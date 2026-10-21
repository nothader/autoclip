"""what-if 视频生成：数值引擎、文案占位符、语义校验、LLM 分镜修正循环、声音合成。

渲染（Chromium/WebGL）不在单测里跑：需要 playwright + 浏览器，见 test_whatif_render_smoke（缺依赖时跳过）。
"""
import json
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.whatif.model import (  # noqa: E402
    Growth, compile_plan, fmt_distance, fmt_num, fmt_time, hud_for, rate_tag, validate,
)
from backend.whatif.planner import EXAMPLE_PATH, extract_json, plan_storyboard  # noqa: E402
from backend.whatif.schema import GrowthModel, Quantity, Storyboard  # noqa: E402


def _example() -> Storyboard:
    return Storyboard.model_validate_json(EXAMPLE_PATH.read_text(encoding="utf-8"))


def _mini(**over) -> dict:
    d = {
        "title": "t", "premise": "p",
        "quantity": {"kind": "speed", "unit": "m/s",
                     "model": {"type": "exponential", "start": 1, "factor": 2, "step": 1},
                     "milestones": [{"label": "SOUND", "value": 343}]},
        "beats": [
            {"duration": 3, "sim_end": 5, "scene": "city", "caption": "Now at {value}."},
            {"duration": 3, "sim_end": 10, "scene": "desert"},
        ],
        "outro": {"chart_duration": 2, "question_duration": 1},
        "intro": {"duration": 0.5},
    }
    d.update(over)
    return d


# ------------------------------------------------------------------ growth ---
def test_discrete_doubling_matches_second_counter():
    g = Growth(GrowthModel(type="exponential", start=1, factor=2, step=1), 30)
    assert g.value(0) == 1 and g.value(0.99) == 1
    assert g.value(1) == 2 and g.value(5.5) == 32
    # 第 n 秒内的速度是 2^(n-1)：第 6 秒 = 32 m/s
    assert hud_for(Quantity(), g.value(5.5), 5.5).head == "SECOND 6"


def test_distance_is_integral_of_step_speed():
    g = Growth(GrowthModel(type="exponential", start=1, factor=2, step=1), 12)
    # 前 10 秒：1+2+...+512 = 1023 m
    assert g.integral(10) == pytest.approx(1023, rel=2e-3)


def test_linear_and_keyframes():
    lin = Growth(GrowthModel(type="linear", start=10, rate=5, step=1, discrete=False), 10)
    assert lin.value(4) == pytest.approx(30)
    kf = Growth(GrowthModel(type="keyframes", points=[(0, 1), (10, 1e6)], discrete=False), 10)
    assert kf.value(5) == pytest.approx(1000, rel=1e-6)  # 跨数量级按对数插值


def test_crossing_time():
    g = Growth(GrowthModel(type="exponential", start=1, factor=2, step=1), 30)
    assert g.crossing(343) == 9.0          # 2^9 = 512 是第一个 ≥ 343 的值
    assert g.crossing(1e12) is None


# -------------------------------------------------------------- formatting ---
@pytest.mark.parametrize("v,s", [(1, "1"), (32, "32"), (1048576, "1,048,576"), (3.6, "3.6"), (12.25, "12.2"),
                                 (2.5e18, "2.50 × 10¹⁸")])
def test_fmt_num(v, s):
    assert fmt_num(v) == s


def test_misc_formatters():
    assert fmt_distance(59) == "59 m"
    assert fmt_distance(2010) == "2.01 km"
    assert fmt_time(5.9) == "00:05.90"
    assert rate_tag(0.5)[0] == "SLOW MOTION ×2"
    assert rate_tag(1.0)[0] == "REAL TIME"
    assert rate_tag(4)[0] == "TIME-LAPSE ×4"


def test_speed_hud_adds_mach_and_light_fraction():
    h = hud_for(Quantity(), 512, 9.5)
    assert "MACH 1.5" in h.sub and "1,843 km/h" in h.sub
    h2 = hud_for(Quantity(), 1_048_576, 20.5)
    assert "OF LIGHT SPEED" in h2.sub


# ------------------------------------------------------------- validation ---
def test_example_storyboard_is_clean():
    sb = _example()
    assert validate(sb) == []
    plan = compile_plan(sb)
    assert plan["n_frames"] == round(plan["duration"] * plan["fps"])
    assert len(plan["frames"]) == plan["n_frames"]
    titles = [m["title"] for m in plan["milestones"]]
    assert "THE SOUND BARRIER: BROKEN" in titles
    assert plan["chart"]["breach"]["label"].startswith("SECOND 30")


def test_milestones_pop_when_crossed_and_never_overlap():
    plan = compile_plan(_example())
    pops = plan["milestones"]
    for a, b in zip(pops, pops[1:]):
        assert b["t0"] >= a["t1"] - 1e-9
    snd = next(m for m in pops if m["title"].startswith("THE SOUND"))
    fr = plan["frames"][int(snd["t0"] * plan["fps"]) + 3]
    assert fr["callout"]["title"] == snd["title"]
    # 弹出那一刻 HUD 上的速度确实已经越过音速
    assert float(fr["hud"]["value"].replace(",", "")) >= 343


def test_captions_get_computed_numbers():
    plan = compile_plan(Storyboard.model_validate(_mini()))
    assert plan["beats"][0]["caption"] == "Now at 16 m/s."   # sim_end=5 → 2^4


def test_validate_flags_hardcoded_numbers_unknown_placeholders_and_uncrossed_milestones():
    d = _mini()
    d["beats"][0]["caption"] = "You hit 1,000,000 m/s at {speed}."
    d["quantity"]["milestones"].append({"label": "LIGHT", "value": 3e8})
    problems = validate(Storyboard.model_validate(d))
    text = "\n".join(problems)
    assert "写死的数字" in text and "{speed}" in text and "LIGHT" in text


def test_sim_time_cannot_go_backwards():
    d = _mini()
    d["beats"][1]["sim_end"] = 2
    with pytest.raises(Exception):
        Storyboard.model_validate(d)


def test_frames_are_pure_functions_of_index():
    a = compile_plan(_example())["frames"]
    b = compile_plan(_example())["frames"]
    assert a[1234] == b[1234]
    # 场景切换时位移清零，同一场景内单调递增
    zs = [f["z"] for f in a if f.get("b") in (3, 4)]
    assert all(y >= x for x, y in zip(zs, zs[1:]))


# ---------------------------------------------------------------- planner ---
def test_extract_json_handles_fences():
    assert extract_json('Sure!\n```json\n{"a": 1}\n```') == {"a": 1}


def test_planner_repairs_invalid_storyboard():
    good = _mini()
    bad = json.loads(json.dumps(good))
    bad["beats"][0]["caption"] = "At {speed}."
    calls = []

    def fake_llm(prompt: str) -> str:
        calls.append(prompt)
        return json.dumps(bad if len(calls) == 1 else good)

    sb = plan_storyboard("What if?", call=fake_llm, hooks=False)
    assert sb.beats[0].caption == "Now at {value}."
    assert len(calls) == 2 and "{speed}" in calls[1]   # 第二轮把错误回传给了模型


def test_planner_gives_up_after_max_repairs():
    with pytest.raises(ValueError):
        plan_storyboard("x", call=lambda p: "not json", max_repairs=1)


# ------------------------------------------------------------------ audio ---
def test_audio_synthesis_levels_and_length():
    np = pytest.importorskip("numpy")
    from backend.whatif.audio import SR, synthesize
    d = _mini()
    d["beats"][1]["effects"] = ["shockwave"]
    d["beats"][0]["sfx"] = [{"type": "riser", "at": 0.5}]
    plan = compile_plan(Storyboard.model_validate(d))
    x = synthesize(plan)
    assert x.shape == (int(round(plan["duration"] * SR)), 2)
    assert np.max(np.abs(x)) <= 0.8 and np.sqrt(np.mean(x ** 2)) > 0.03
    assert np.isfinite(x).all()


def test_whatif_render_smoke(tmp_path):
    pytest.importorskip("playwright")
    from backend.whatif.render import render_stills
    plan = compile_plan(Storyboard.model_validate(_mini()))
    try:
        paths = render_stills(plan, tmp_path, [10, 120], preview=True)
    except Exception as e:  # 没装浏览器的环境
        pytest.skip(f"chromium 不可用: {e}")
    assert all(p.exists() and p.stat().st_size > 10_000 for p in paths)


# ---------------------------------------------------------- 多版式（v2） ---
from backend.whatif.model import count_up, fmt_clock, lightning, lightning_times  # noqa: E402
from backend.whatif.planner import EXAMPLES_DIR, FORMAT_EXAMPLES, build_prompt  # noqa: E402


def _timeline(**over) -> dict:
    d = {
        "format": "timeline", "title": "t", "premise": "p",
        "clock": {"mode": "elapsed", "label": "WITHOUT X", "intro_label": "X VANISHES IN", "intro_from": 5},
        "intro": {"style": "title", "title": "What if all *x* disappeared?", "duration": 1.0},
        "beats": [
            {"duration": 2, "scene": "city", "camera": "wide"},
            {"duration": 2, "scene": "interior", "env": {"room": "hospital"}, "time": "+10 SEC",
             "stat": {"value": "90%", "label": "OF NURSES"}, "caption": "Hospitals lose most nurses."},
            {"duration": 2, "scene": "city", "time": "+1 HOUR", "chapter": "After"},
        ],
        "outro": {"question_duration": 1, "end": {"kind": "tagline", "lines": ["A", "B"], "accent_line": 1}},
    }
    d.update(over)
    return d


@pytest.mark.parametrize("name", sorted(p.name for p in EXAMPLES_DIR.glob("*.json")))
def test_every_example_validates_and_compiles(name):
    sb = Storyboard.model_validate_json((EXAMPLES_DIR / name).read_text(encoding="utf-8"))
    assert validate(sb) == []
    plan = compile_plan(sb)
    assert len(plan["frames"]) == plan["n_frames"] > 0
    assert plan["frames"][-1].get("end") or plan["frames"][-1].get("chart")


def test_examples_cover_every_prompted_format():
    for fmt, name in FORMAT_EXAMPLES.items():
        sb = Storyboard.model_validate_json((EXAMPLES_DIR / name).read_text(encoding="utf-8"))
        assert sb.format == fmt


def test_count_up_and_clock_format():
    assert count_up("90%", 1) == "90%"
    assert count_up("90%", 0) == "0%"
    assert count_up("~100,000", 0.5).startswith("~") and "," in count_up("~100,000", 0.5)
    assert count_up("~2/3", 0.3) == "~0/3" or count_up("~2/3", 0.3).startswith("~")
    assert count_up("BACK", 0.2) == "BACK"
    assert fmt_clock(4.821, "countdown") == "0:04.821"
    assert fmt_clock(3725, "stopwatch") == "1:02:05"


def test_timeline_frames_have_clock_stat_and_intro_countdown():
    plan = compile_plan(Storyboard.model_validate(_timeline()))
    f_intro = plan["frames"][5]
    assert f_intro["intro"]["style"] == "title"
    assert f_intro["clock"]["label"] == "X VANISHES IN" and f_intro["clock"]["value"].startswith("0:04")
    f_stat = plan["frames"][int(3.5 * plan["fps"])]
    assert f_stat["clock"]["value"] == "+10 SEC" and f_stat["stat"]["value"] == "90%"
    assert plan["beats"][1]["env"]["room"] == "hospital"
    assert plan["frames"][-1]["end"]["kind"] == "tagline"
    assert plan["chapters"] == ["After"]
    assert "hud" not in f_stat                                   # 没有 quantity 就没有数据 HUD


def test_countdown_runs_down_and_beeps_each_second():
    d = _timeline(format="countdown", clock={"mode": "countdown", "label": "BACK IN"})
    d["beats"][1]["time"] = [3.0, 1.0]
    d["beats"][2]["time"] = "BACK"
    plan = compile_plan(Storyboard.model_validate(d))
    vals = [f["clock"]["value"] for f in plan["frames"] if f.get("b") == 1 and "clock" in f]
    assert vals[0] == "0:03.000" and vals[-1] < vals[0]
    assert sum(1 for e in plan["audio"] if e["type"] == "beep") >= 1   # 跨整秒（3→2）时响一声


def test_semantic_checks_for_formats():
    d = _timeline(format="countdown", clock={"mode": "countdown"})
    d["beats"][1]["time"] = [1.0, 3.0]                             # 倒计时却在增加
    assert any("递减" in p for p in validate(Storyboard.model_validate(d)))
    d2 = _timeline(format="story", clock=None)
    for b in d2["beats"]:
        b.pop("chapter", None)
    assert any("chapter" in p for p in validate(Storyboard.model_validate(d2)))
    d3 = _timeline()
    d3["beats"][1]["caption"] = "At {value}."                   # 无 quantity 不能用占位符
    assert any("占位符" in p for p in validate(Storyboard.model_validate(d3)))


def test_env_carries_over_within_scene_and_resets_on_change():
    d = _timeline()
    d["beats"][0]["env"] = {"time": "night"}
    d["beats"].insert(1, {"duration": 2, "scene": "city", "time": "+1 SEC"})
    plan = compile_plan(Storyboard.model_validate(d))
    assert plan["beats"][1]["env"]["time"] == "night"            # 同场景沿用
    assert plan["beats"][2]["env"]["time"] == "day"              # 换场景重置


def test_storm_lightning_is_deterministic_and_has_thunder():
    assert lightning_times(3, 10) == lightning_times(3, 10)
    t0 = lightning_times(3, 10)[0]
    assert lightning(3, t0 + 0.01) > 0 and lightning(3, t0 + 0.5) == 0
    d = _timeline()
    d["beats"][0]["env"] = {"weather": "storm"}
    d["beats"][0]["duration"] = 6
    plan = compile_plan(Storyboard.model_validate(d))
    assert any(e["type"] == "thunder" for e in plan["audio"])
    assert any(f.get("lightning") for f in plan["frames"])


def test_prompt_contains_all_format_examples_and_forced_format():
    p = build_prompt("What if the ice melted?", fmt="timeline")
    for fmt in FORMAT_EXAMPLES:
        assert f"EXAMPLE ({fmt})" in p
    assert p.rindex("EXAMPLE (timeline)") > p.rindex("EXAMPLE (story)")
    assert "FORMAT: timeline (required)" in p


def test_planner_enforces_requested_format():
    good = _timeline()
    wrong = json.loads(json.dumps(good))
    wrong["format"] = "story"
    wrong["beats"][2]["chapter"] = "X"
    replies = [json.dumps(wrong), json.dumps(good)]
    sb = plan_storyboard("x", fmt="timeline", call=lambda p: replies.pop(0), hooks=False)
    assert sb.format == "timeline"


def test_audio_layers_for_new_scenes():
    np = pytest.importorskip("numpy")
    from backend.whatif.audio import synthesize
    d = _timeline()
    d["beats"][0]["env"] = {"weather": "rain", "crowd": 0.8}
    d["beats"][2]["effects"] = ["fire", "earthquake"]
    d["beats"][1]["screen"] = {"kind": "vitals", "rows": [["HR", "80"]]}
    x = synthesize(compile_plan(Storyboard.model_validate(d)))
    assert np.isfinite(x).all() and np.max(np.abs(x)) <= 0.8


@pytest.mark.parametrize("name", sorted(p.name for p in EXAMPLES_DIR.glob("*.json")))
def test_every_example_beat_renders_without_page_errors(name, tmp_path):
    """每个示例的每一段各渲一帧（缩小尺寸）：页面脚本报错会让 worker 退出 → 这里失败。"""
    pytest.importorskip("playwright")
    from backend.whatif.render import render_frames
    plan = compile_plan(Storyboard.model_validate_json((EXAMPLES_DIR / name).read_text(encoding="utf-8")))
    frames = [int((b["start"] + b["duration"] * 0.5) * plan["fps"]) for b in plan["beats"]] + [plan["n_frames"] - 1]
    try:
        errs = render_frames(plan, tmp_path, width=270, height=480, frames=frames, workers=2, fmt="jpg")
    except RuntimeError as e:
        if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
            pytest.skip("chromium 不可用")
        raise
    assert not errs, errs


# ------------------------------------------------------------------ 旁白 ---
def test_speech_text_reads_units_and_symbols():
    from backend.whatif.narration import speech_text
    assert speech_text("about 1,670 km/h") == "about 1,670 kilometers per hour"
    assert speech_text("~20% of CO2") == "about 20 percent of C O two"
    assert speech_text("What if all *women* disappeared?") == "What if all women disappeared?"


def test_narration_stretches_beats_and_places_lines(monkeypatch):
    np = pytest.importorskip("numpy")
    from backend.whatif import narration as N
    from backend.whatif.schema import Narration
    # 假引擎：每个字符 0.08 秒，不需要模型
    monkeypatch.setattr(N.Speaker, "say", lambda self, text: np.ones(int(len(text) * 0.08 * N.SR), dtype=np.float32) * 0.2)
    d = _timeline()
    d["beats"][2]["caption"] = "A much longer line that will not fit inside a two second shot at all."
    d["beats"][2]["narration"] = None
    d["beats"][1]["narration"] = ""                      # 这段不念
    sb = Storyboard.model_validate(d)
    sb2, lines = N.narrate(sb, Narration())
    kinds = [(l.kind, l.index) for l in lines]
    assert ("title", -1) in kinds and ("beat", 2) in kinds and ("beat", 1) not in kinds and ("end", -1) in kinds
    long_line = next(l for l in lines if l.index == 2)
    assert sb2.beats[2].duration >= N.LEAD + long_line.seconds + N.TAIL - 1e-6
    assert sb.beats[2].duration == 2                     # 原分镜不被修改
    plan = compile_plan(sb2)
    v = N.voice_track(plan, lines)
    start = plan["beats"][2]["start"] + N.LEAD
    assert v[int(start * N.SR) + 10] > 0 and v[int((start - 0.1) * N.SR)] == 0
    from backend.whatif.audio import synthesize
    x = synthesize(plan, v)
    assert np.isfinite(x).all() and np.max(np.abs(x)) <= 0.8


# ------------------------------------------------------------- 自定义布景 ---
def test_custom_scene_requires_a_set_and_limits_objects():
    d = _timeline()
    d["beats"][1] = {"duration": 2, "scene": "custom", "time": "+1 SEC"}
    assert any("env.set" in p for p in validate(Storyboard.model_validate(d)))
    d["beats"][1]["env"] = {"set": {"objects": [{"kind": "molecule", "formula": "N2", "count": 200},
                                                {"kind": "cell", "count": 100}]}}
    assert any("太多" in p for p in validate(Storyboard.model_validate(d)))
    d["beats"][1]["env"] = {"set": {"background": "stars", "objects": [{"kind": "hourglass", "animate": [{"type": "spin"}]}]}}
    sb = Storyboard.model_validate(d)
    assert validate(sb) == []
    assert compile_plan(sb)["beats"][1]["env"]["set"]["objects"][0]["kind"] == "hourglass"


def test_prompt_pushes_bespoke_sets():
    p = build_prompt("What if trees could walk?")
    assert "DESIGN YOUR OWN FOR EVERY VIDEO" in p and "molecule" in p and '"scene":"custom"' in p


def test_custom_set_grounds_and_props_render(tmp_path):
    """每种地面 + 一批道具各渲一帧，防止某个组合让页面脚本崩溃。"""
    pytest.importorskip("playwright")
    from backend.whatif.render import render_frames
    from backend.whatif.schema import SET_KINDS
    kinds = [k for k in SET_KINDS if k not in ("particles",)]
    beats = []
    for gi, ground in enumerate(("none", "plane", "grid", "water", "mirror")):
        objs = [{"kind": k, "at": [(j % 5 - 2) * 2.2, 1, -(j // 5) * 2.2], "scale": 0.6, "formula": "CO2", "values": [1, 2],
                 "animate": [{"type": "spin"}, {"type": "grow"}]} for j, k in enumerate(kinds[gi::5])]
        objs.append({"kind": "particles", "count": 10})
        beats.append({"duration": 1.0, "scene": "custom", "camera": "wide", "subject": {"type": "none"},
                      "env": {"set": {"ground": ground, "objects": objs}}})
    sb = Storyboard.model_validate({"format": "timeline", "title": "t", "premise": "p", "clock": {"mode": "elapsed"},
                                    "intro": {"style": "title", "title": "x", "duration": 0.4},
                                    "beats": [dict(b, time=f"+{i}") for i, b in enumerate(beats)],
                                    "outro": {"question_duration": 0.5}})
    plan = compile_plan(sb)
    try:
        errs = render_frames(plan, tmp_path, width=180, height=320,
                             frames=[int((b["start"] + 0.5) * plan["fps"]) for b in plan["beats"]], workers=2)
    except RuntimeError as e:
        if "playwright install" in str(e) or "Executable doesn't exist" in str(e):
            pytest.skip("chromium 不可用")
        raise
    assert not errs, errs


def test_landscape_allows_long_form_but_portrait_does_not():
    """横屏 1920x1080 = YouTube 长视频，总时长上限 900s；竖屏仍是 180s。"""
    beats = [{"duration": 5.0, "scene": "custom", "camera": "wide", "subject": {"type": "none"}, "chapter": "c" if i == 0 else None,
              "env": {"set": {"objects": [{"kind": "tree"}]}}} for i in range(60)]
    base = {"format": "story", "title": "t", "premise": "p", "beats": beats}
    land = Storyboard.model_validate(dict(base, width=1920, height=1080))
    assert not [p for p in validate(land) if "总时长" in p]
    assert compile_plan(land)["width"] == 1920
    port = Storyboard.model_validate(base)
    assert [p for p in validate(port) if "总时长" in p]


def test_hook_rules_flag_hard_vague_and_loopless_storyboards():
    from backend.whatif.hooks import hook_report, hook_score, reading_grade
    assert reading_grade("Every baby can talk.") + 5 < reading_grade(
        "Sexual reproduction fundamentally transformed evolutionary diversification across populations.")
    beats = [{"duration": 3, "scene": "custom", "camera": "wide", "subject": {"type": "none"}, "time": f"+{i}",
              "env": {"set": {"objects": [{"kind": "tree"}]}}, "caption": c} for i, c in enumerate([
                  "Basically, the situation would gradually become considerably more complicated for populations.",
                  "In conclusion, things change.",
                  "Interestingly, scientists would investigate the consequences."])]
    bad = Storyboard.model_validate({"format": "timeline", "title": "t", "premise": "p", "clock": {"mode": "elapsed"},
                                     "intro": {"style": "title", "title": "What if things changed?"}, "beats": beats})
    rules = {x.rule for x in hook_report(bad) if x.level == "fix"}
    assert {"specific", "reading", "fluff", "open_loop", "payoff", "first3s"} <= rules
    good_caps = ["Every baby on Earth can talk. 130 million of them.", "But that is not the strangest part.",
                 "They remember being born.", "And they want answers."]
    good = Storyboard.model_validate({"format": "timeline", "title": "t", "premise": "p", "clock": {"mode": "elapsed"},
                                      "intro": {"style": "title", "title": "What if every baby could talk?"},
                                      "outro": {"end": {"kind": "question", "lines": ["WHAT WOULD YOU SAY?"]}},
                                      "beats": [dict(b, caption=c) for b, c in zip(beats + beats[:1], good_caps)]})
    assert not [x for x in hook_report(good) if x.level == "fix"]
    assert hook_score(good) > hook_score(bad)


def test_planner_sends_hook_problems_back_but_never_fails_on_them():
    good = json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))
    good["beats"][1]["caption"] = "Basically, the velocity increases considerably."   # 废话 + 难词
    calls = []
    def fake(p):
        calls.append(p)
        return json.dumps(good)
    sb = plan_storyboard("x", call=fake, max_repairs=1)
    assert sb.title and len(calls) == 2 and "hook rule" in calls[1]


def test_pace_shortens_shots_keeps_sim_and_readability():
    from backend.whatif.model import readable_seconds
    sb = Storyboard.model_validate(json.loads(EXAMPLE_PATH.read_text(encoding="utf-8")))
    base = compile_plan(sb)
    fast = compile_plan(sb.model_copy(update={"pace": 1.8}))
    assert fast["pace"] == 1.8 and fast["duration"] < base["duration"] * 0.8
    for b0, b1, src in zip(base["beats"], fast["beats"], sb.beats):
        assert b1["duration"] >= readable_seconds(src.caption) - 1e-6
        assert abs(b1["sim1"] - b0["sim1"]) < 1e-6            # 模拟时间不变
    assert [m["title"] for m in fast["milestones"]] == [m["title"] for m in base["milestones"]]


def test_narrated_pace_compresses_shots_before_voice_stretch(monkeypatch):
    """有旁白时：先按 pace 压缩镜头（语速加快），再由语音拉长——不能退回原始长度。"""
    import backend.whatif.pipeline as pl
    from backend.whatif.schema import Narration
    sb = Storyboard.model_validate(json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))).model_copy(update={"pace": 1.8})
    seen = {}
    def fake_narrate(s, cfg):
        seen["dur"] = sum(b.duration for b in s.beats); seen["speed"] = cfg.speed; seen["pace"] = s.pace
        raise RuntimeError("stop")
    monkeypatch.setattr("backend.whatif.narration.narrate", fake_narrate)
    with pytest.raises(RuntimeError):
        pl.make_video(sb, Path("/tmp/x.mp4"), narration=Narration(enabled=True))
    assert seen["pace"] == 1.0 and seen["speed"] > 1.0
    assert seen["dur"] < sum(b.duration for b in sb.beats) * 0.8
