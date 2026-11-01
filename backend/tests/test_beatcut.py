"""beatcut 卡点剪辑：拍点跟踪精度、选段、剪辑表不变量、镜头拆分、端到端渲染（切点对齐成片自身的拍点）。

渲染相关用例需要 ffmpeg，缺失时跳过；numpy 是 beatcut 的可选依赖（pip install numpy）。
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

np = pytest.importorskip("numpy")

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.beatcut.audio import SR, analyze_signal, decode_audio, grid_analysis, pick_window  # noqa: E402
from backend.beatcut.footage import Shot, SourceInfo, analyze_footage, split_shots  # noqa: E402
from backend.beatcut.plan import RAMP, EditPlan, PlanOptions, ShotPlan, plan_edit  # noqa: E402
from backend.beatcut.render import speed_expr  # noqa: E402

HAS_FFMPEG = shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None
needs_ffmpeg = pytest.mark.skipif(not HAS_FFMPEG, reason="需要 ffmpeg")


def click_track(bpm: float, dur: float, offset: float = 0.3, quiet_until: float = 0.0, seed: int = 0) -> np.ndarray:
    """4/4 点击音轨：重拍低频 kick，其余高频 click；quiet_until 之前音量压低（模拟前奏 → drop）。"""
    rng = np.random.default_rng(seed)
    y = 0.02 * rng.standard_normal(int(dur * SR)).astype(np.float32)
    p = 60 / bpm
    t, i = offset, 0
    while t < dur - 0.2:
        n = int(t * SR)
        k = np.arange(int(0.06 * SR))
        loud = 0.25 if t < quiet_until else 1.0
        amp = loud * (1.0 if i % 4 == 0 else 0.5)
        freq = 60 if i % 4 == 0 else 2000
        seg = amp * np.sin(2 * np.pi * freq * k / SR) * np.exp(-k / (0.015 * SR))
        y[n:n + len(seg)] += seg[: len(y) - n]
        t += p
        i += 1
    return y


# ---------------------------------------------------------------- audio ---
@pytest.mark.parametrize("bpm", [85, 100, 124, 140, 174])
def test_beat_tracking_accuracy(bpm):
    m = analyze_signal(click_track(bpm, 30))
    assert abs(m.bpm - bpm) < 0.5
    expected = 0.3 + np.arange(200) * 60 / bpm
    err = np.array([np.min(np.abs(expected - b)) for b in m.beats])
    assert err.max() < 0.03, "拍点误差应小于 1 帧（30fps）"
    assert len(m.beats) >= int(28 * bpm / 60) - 2
    # 重拍落在 kick 上
    assert min(np.min(np.abs(expected[::4] - d)) for d in m.downbeats[:3]) < 0.03


def test_pick_window_prefers_the_drop():
    m = analyze_signal(click_track(120, 40, quiet_until=16))
    start = pick_window(m, 10)
    assert start >= 15.5, "应跳过安静的前奏，从能量高的段落开始"
    assert np.min(np.abs(np.array(m.downbeats) - start)) < 1e-6, "起点在重拍上"
    forced = pick_window(m, 10, start=3.33)
    assert np.min(np.abs(np.array(m.beats) - forced)) < 1e-6


# ---------------------------------------------------------------- planning ---
def _fake_shots(n=4, dur=6.0, fps=30.0, has_audio=True):
    shots = []
    for i in range(n):
        src = SourceInfo(f"/footage/{i}.mp4", dur, fps, 1920, 1080, has_audio)
        k = int(dur * 10)
        rng = np.random.default_rng(i)
        shots.append(Shot(i, src, 0.0, dur, rng.uniform(0.3, 0.9, k), rng.uniform(2, 20, k)))
    return shots


def _cuts(plan: EditPlan):
    return np.cumsum([s.frames for s in plan.shots])[:-1] / plan.fps


def test_plan_cuts_land_on_beats_and_frames_add_up():
    m = grid_analysis(120, 20)
    plan, _ = plan_edit(_fake_shots(), m, PlanOptions(duration=12, fps=30))
    assert plan.total_frames == round(12 * 30)
    beats = np.array(m.beats)
    for c in _cuts(plan):
        assert np.min(np.abs(beats - c)) <= 0.5 / 30 + 1e-9


def test_plan_loop_tail_and_hook_protected():
    plan, _ = plan_edit(_fake_shots(), grid_analysis(120, 20), PlanOptions(duration=10))
    hook, tail = plan.shots[0], plan.shots[-1]
    assert plan.loop and "loop" in tail.note
    assert tail.source == hook.source
    assert abs(tail.src_start + tail.frames / plan.fps - hook.src_start) < 1e-3, "最后一镜正好接到第一镜开头"
    a0, a1 = tail.src_start, hook.src_start + hook.src_seconds(plan.fps)
    for s in plan.shots[1:-1]:
        if s.source == hook.source:
            b0, b1 = s.src_start, s.src_start + s.src_seconds(plan.fps)
            assert b1 <= a0 + 1e-6 or b0 >= a1 - 1e-6, "中间镜头不复用 hook / 循环尾巴的画面"
    assert plan.shots[-2].source != hook.source or len({s.source for s in plan.shots}) == 1


def test_plan_effects_and_pace():
    shots = _fake_shots()
    normal, _ = plan_edit(shots, grid_analysis(120, 20), PlanOptions(duration=12, pace="normal"))
    calm, _ = plan_edit(shots, grid_analysis(120, 20), PlanOptions(duration=12, pace="calm"))
    hype, _ = plan_edit(shots, grid_analysis(120, 20), PlanOptions(duration=12, pace="hype"))
    assert len(calm.shots) < len(normal.shots) <= len(hype.shots)
    assert not any(s.speed == RAMP for s in calm.shots), "calm 不做变速"
    assert any(s.speed == RAMP for s in normal.shots)
    first = normal.shots[0]
    assert "hook" in first.note and not first.flash and first.speed == [[1.0, 1.0]]
    for s in normal.shots:
        if s.speed == RAMP:
            assert not s.foley, "变速镜头不混原声"
    off, _ = plan_edit(shots, grid_analysis(120, 20),
                       PlanOptions(duration=12, ramps=False, punch=False, flash=False, loop=False))
    assert not any(s.flash or s.punch or s.speed != [[1.0, 1.0]] for s in off.shots)
    assert not off.loop


def test_variants_change_the_hook():
    shots = _fake_shots()
    hooks = {(plan_edit(shots, grid_analysis(120, 20), PlanOptions(duration=8, variant=v))[0].shots[0].source)
             for v in range(3)}
    assert len(hooks) == 3


def test_short_footage_warns_and_still_fills():
    shots = _fake_shots(n=1, dur=2.0)
    plan, warnings = plan_edit(shots, grid_analysis(120, 20), PlanOptions(duration=10))
    assert plan.total_frames == 300
    assert any("素材" in w for w in warnings)


def test_slowmo_only_for_high_fps():
    m = grid_analysis(120, 30)
    lo, _ = plan_edit(_fake_shots(fps=30), m, PlanOptions(duration=12, pace="calm"))
    hi, _ = plan_edit(_fake_shots(fps=60), m, PlanOptions(duration=12, pace="calm"))
    assert not any("slowmo" in s.note for s in lo.shots)
    assert any("slowmo" in s.note for s in hi.shots)


def test_plan_json_roundtrip():
    plan, _ = plan_edit(_fake_shots(), grid_analysis(120, 20), PlanOptions(duration=6))
    again = EditPlan.model_validate_json(plan.model_dump_json())
    assert again == plan
    with pytest.raises(ValidationError):
        EditPlan.model_validate({**plan.model_dump(), "bogus": 1})


def test_speed_expr_piecewise_is_continuous():
    s = ShotPlan(source="x", src_start=0, frames=30, speed=RAMP)
    expr = speed_expr(s, 30)
    assert expr.startswith("(if(lt(T") and expr.endswith(")/TB")
    # 源长度 = 0.4*1s*2.6 + 0.6*1s*0.65
    assert abs(s.src_seconds(30) - (0.4 * 2.6 + 0.6 * 0.65)) < 1e-9
    assert speed_expr(ShotPlan(source="x", src_start=0, frames=30), 30) == "PTS"


def test_split_shots_needs_both_signals():
    motion = np.full(40, 3.0)
    cut = np.zeros(40)
    cut[20], motion[20] = 0.8, 60.0      # 真切换
    cut[30] = 0.8                         # 只有直方图跳（比如灯闪），不算
    assert split_shots(cut, motion) == [0, 20, 40]


# ---------------------------------------------------------------- render (ffmpeg) ---
def _ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


@pytest.fixture(scope="module")
def media(tmp_path_factory):
    if not HAS_FFMPEG:
        pytest.skip("需要 ffmpeg")
    d = tmp_path_factory.mktemp("beatcut")
    foot = d / "footage"
    foot.mkdir()
    _ff("-f", "lavfi", "-i", "testsrc2=s=320x180:r=60:d=3", "-f", "lavfi", "-i", "sine=f=880:d=3:beep_factor=4",
        "-shortest", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", str(foot / "a.mp4"))
    _ff("-f", "lavfi", "-i", "mandelbrot=s=320x180:r=30", "-t", "3", "-c:v", "libx264", "-preset", "ultrafast",
        str(foot / "b.mp4"))
    # 一条「一镜到底」素材，中间硬切换场景 → 应拆成两个镜头
    _ff("-f", "lavfi", "-i", "color=c=#203040:s=320x180:r=30:d=2,drawbox=x='mod(t*200\\,300)':y=40:w=40:h=80:c=white:t=fill",
        "-f", "lavfi", "-i", "testsrc=s=320x180:r=30:d=2",
        "-filter_complex", "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]", "-c:v", "libx264", "-preset", "ultrafast",
        str(foot / "c_raw.mp4"))
    music = d / "music.wav"
    y = click_track(124, 20, quiet_until=6)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", str(music)],
                   input=y.astype(np.float32).tobytes(), check=True)
    return d


@needs_ffmpeg
def test_footage_analysis_splits_raw_take(media):
    from backend.beatcut.footage import collect_sources
    shots = analyze_footage(collect_sources([media / "footage"]))
    per_file = {}
    for s in shots:
        per_file.setdefault(Path(s.source.path).name, []).append(s)
    assert len(per_file["c_raw.mp4"]) == 2
    assert per_file["a.mp4"][0].source.fps == pytest.approx(60, abs=0.5)
    assert per_file["a.mp4"][0].source.has_audio and not per_file["b.mp4"][0].source.has_audio


@needs_ffmpeg
def test_render_end_to_end_cuts_on_beats(media, tmp_path):
    from backend.beatcut.pipeline import load_plan, make_videos
    out = tmp_path / "edit.mp4"
    res = make_videos([media / "footage"], media / "music.wav", out,
                      PlanOptions(duration=6, grade="warm"), preview=True, variants=2)
    assert len(res["videos"]) == 2
    v = res["videos"][0]
    path = Path(v["path"])
    assert path.exists() and path.name == "edit-v1.mp4"
    plan = load_plan(Path(v["plan"]))

    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,nb_frames",
                            "-of", "compact", str(path)], capture_output=True, text=True).stdout
    assert "codec_type=audio" in probe
    assert f"nb_frames={plan.total_frames}" in probe
    assert "width=540|height=960" in probe

    # 用成片自己的音轨重新找拍点：每一刀都在 1 帧以内
    m = analyze_signal(decode_audio(path))
    beats = np.array(m.beats)
    cuts = [c for c in _cuts(plan) if beats.min() - 0.05 < c < beats.max() + 0.05]
    assert cuts
    assert max(np.min(np.abs(beats - c)) for c in cuts) < 1 / plan.fps

    # 每个切点都是可见的画面跳变
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-vf", "scale=48:48,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(-1, 48, 48).astype(float)
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    jumps = set((np.where(d > np.median(d) * 3)[0] + 1).tolist())
    planned = set(np.round(_cuts(plan) * plan.fps).astype(int).tolist())
    assert len(planned & jumps) >= 0.8 * len(planned)


@needs_ffmpeg
def test_render_without_music_and_rerender_plan(media, tmp_path):
    from backend.beatcut.pipeline import load_plan, make_videos
    from backend.beatcut.render import render_plan
    res = make_videos([media / "footage" / "a.mp4"], None, tmp_path / "solo.mp4",
                      PlanOptions(duration=3, aspect="1:1", grade="mono"), bpm=100, preview=True)
    plan = load_plan(Path(res["videos"][0]["plan"]))
    assert plan.music is None and plan.width == plan.height
    plan.shots[0].flash = True
    again = render_plan(plan, tmp_path / "solo2.mp4", preview=True)
    assert Path(again["path"]).exists() and again["frames"] == plan.total_frames


def test_cli_parses_beatcut():
    from backend.cli import build_parser
    a = build_parser().parse_args(["beatcut", "make", "dir", "clip.mov", "-m", "s.mp3", "-d", "12", "--pace", "hype",
                                   "--variants", "3", "--grade", "moody", "--no-loop"])
    assert a.footage == ["dir", "clip.mov"] and a.duration == 12 and a.variants == 3 and a.no_loop
    assert build_parser().parse_args(["beatcut", "render", "p.json", "--preview"]).preview
    assert build_parser().parse_args(["beatcut", "beats", "s.mp3"]).beatcut_cmd == "beats"
