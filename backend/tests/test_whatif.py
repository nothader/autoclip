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
from backend.whatif.schema import GrowthModel, Pov, Quantity, Storyboard, Theme  # noqa: E402


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


def test_every_style_and_split_layout_render(tmp_path):
    """每种风格（含分屏）各渲一帧，防止风格代码让页面脚本出错。"""
    pytest.importorskip("playwright")
    from backend.whatif.render import render_frames
    beats = [{"duration": 1.2, "scene": "custom", "camera": "wide", "subject": {"type": "none"}, "time": "+1", "caption": "Every word pops in here.",
              "env": {"set": {"ground": "plane", "objects": [{"kind": "person", "action": "walk"}, {"kind": "tree", "at": [2, 0, -2]}]}}}]
    for st, lay in [("calm", "full"), ("bold", "split"), ("cinematic", "full"), ("toon", "split"), ("retro", "full"), ("witness", "full")]:
        sb = Storyboard.model_validate({"format": "timeline", "title": "t", "premise": "p", "clock": {"mode": "elapsed"},
                                        "theme": {"style": st, "layout": lay}, "intro": {"style": "title", "title": "x", "duration": 0.4},
                                        "beats": beats, "outro": {"question_duration": 0.5}})
        plan = compile_plan(sb)
        assert plan["theme"]["captions"] == {"calm": "line", "bold": "words", "cinematic": "line", "toon": "box", "retro": "words", "witness": "line"}[st]
        try:
            errs = render_frames(plan, tmp_path / st, width=180, height=320, frames=[int(1.0 * plan["fps"])], workers=1)
        except RuntimeError as e:
            if "playwright install" in str(e) or "Executable doesn't exist" in str(e):
                pytest.skip("chromium 不可用")
            raise
        assert not errs, (st, errs)


def test_witness_pieces_compile():
    """witness：time_label 覆盖时钟标签、默认咖啡杯、overlay 片头、fact 结尾带标题、env.cover 透传。"""
    sb = Storyboard.model_validate({"format": "timeline", "title": "t", "premise": "p", "clock": {"mode": "elapsed", "label": "DEPTH"},
                                    "theme": {"style": "witness"}, "intro": {"style": "overlay", "title": "What if *x*?", "duration": 1.0},
                                    "beats": [{"duration": 2, "scene": "city", "camera": "witness", "subject": {"type": "none"}, "time": "5 CM",
                                               "time_label": "SNOW DEPTH", "caption": "Snow.", "env": {"weather": "snow", "cover": [0.1, 0.4]}}],
                                    "outro": {"chart": False, "question_duration": 2, "end": {"kind": "fact", "lines": ["A FACT."]}}})
    plan = compile_plan(sb)
    assert plan["theme"]["anchor"] == "coffee"
    assert plan["beats"][0]["env"]["cover"] == (0.1, 0.4) or plan["beats"][0]["env"]["cover"] == [0.1, 0.4]
    labels = {f["clock"]["label"] for f in plan["frames"] if f.get("clock")}
    assert "SNOW DEPTH" in labels
    ends = [f["end"] for f in plan["frames"] if f.get("end")]
    assert ends and ends[-1]["kind"] == "fact" and ends[-1]["title"] == "What if *x*?"
    assert any(f.get("intro", {}).get("style") == "overlay" for f in plan["frames"])


# ---------------------------------------------------------------- visual QA + publish pack
def _set_sb(objs, n=4, cam="wide", **kw):
    beat = {"duration": 3, "scene": "custom", "camera": cam, "subject": {"type": "none"}, "caption": "Every person is gone.",
            "env": {"set": {"ground": "plane", "objects": objs}}}
    d = {"format": "timeline", "title": "What if every *cat* vanished?", "premise": "p", "clock": {"mode": "elapsed"},
         "intro": {"style": "title", "title": "What if every *cat* vanished?"}, "beats": [dict(beat) for _ in range(n)],
         "outro": {"chart": False, "question_duration": 3}}
    d.update(kw)
    return Storyboard.model_validate(d)


def test_quality_flags_clones_monotony_and_short_length():
    from backend.whatif.quality import quality_report
    twins = [{"kind": "person", "at": [0, 0, 0]}, {"kind": "person", "at": [1, 0, 0]}]
    rules = {(x.level, x.rule) for x in quality_report(_set_sb(twins))}
    assert ("fix", "clones") in rules and ("fix", "monotony") in rules and ("fix", "length") in rules
    varied = [{"kind": "person", "at": [0, 0, 0], "seed": 1, "action": "walk"}, {"kind": "person", "at": [1, 0, 0], "seed": 2}]
    sb = _set_sb(varied, n=1)
    assert not any(x.rule in ("clones", "static") for x in quality_report(sb))


def test_auto_style_picks_by_topic():
    from backend.whatif.quality import auto_style
    assert auto_style("What if a hurricane hit London?") == "witness"
    assert auto_style("What if video games were real?") == "retro"
    assert auto_style("What if Rome never fell? An empire story") == "cinematic"
    assert auto_style("What if everyone was rich?") == "bold"
    assert auto_style("What if dogs could talk?") == "toon"
    assert auto_style("What if the Moon was closer?") == "calm"


def test_planner_prompt_suggests_style_and_repairs_visual_problems():
    from backend.whatif.planner import build_prompt
    assert "SUGGESTED STYLE: witness" in build_prompt("What if a volcano erupted in Naples?")
    good = _cine_sb(4).model_dump()   # 只有 4 段，不够 1 分钟 → 会被要求修一次，最后一次照样返回
    good["pace"] = None
    good["clock"] = {"mode": "elapsed"}
    for k, b in enumerate(good["beats"]):
        b["time"] = f"+{k + 1} DAY"
    calls = []

    def fake(prompt):
        calls.append(prompt)
        return json.dumps(good)
    plan_storyboard("x", call=fake, max_repairs=1)
    assert len(calls) == 2 and "visual rule (length)" in calls[1]


def test_thumb_text_metadata_and_short():
    from backend.whatif import publish
    sb = _set_sb([{"kind": "person", "seed": 3, "action": "walk"}], n=3)
    assert publish.thumb_text(sb) == "EVERY *CAT* VANISHED?"
    assert publish.thumb_text(sb.model_copy(update={"thumbnail": "no more *cats*?"})) == "NO MORE *CATS*?"
    m = publish.metadata(sb)
    assert m["title"] == "What if every cat vanished?" and "#shorts" in m["hashtags"] and "#cat" in m["hashtags"]
    assert "TITLE" in publish.metadata_text(m)
    nums = publish.metadata(sb.model_copy(update={"thumbnail": "*900 MILLION* WILD DOGS?"}))   # 数字不当标签（曾出 #900 #million）
    filler = publish.metadata(sb.model_copy(update={"title": "What if everything around you got bigger except you?", "thumbnail": ""}))
    assert not {"#except", "#everything", "#around"} & set(filler["hashtags"]) and "bigger" in filler["tags"]
    assert "#900" not in nums["hashtags"] and "#million" not in nums["hashtags"] and "wild" in nums["tags"]
    beats = [{"duration": 4, "scene": "city", "camera": c, "subject": {"type": "none"}, "caption": f"Line {i}.", "chapter": f"C{i // 10}"}
             for i, c in zip(range(60), ["wide", "aerial", "establishing", "dolly"] * 15)]
    long = Storyboard.model_validate({"format": "story", "title": "t", "premise": "p", "width": 1920, "height": 1080, "pace": 1.0,
                                      "beats": beats, "outro": {"chart": False}, "narration": {"enabled": True}})
    assert [c["title"] for c in publish.metadata(long)["chapters"]] == [f"C{i}" for i in range(6)]
    short = publish.make_short(long)
    assert (short.width, short.height) == (1080, 1920) and short.narration is None
    assert short.pace == publish.SHORT_PACE   # 长视频是 1x 也一样：短版按 1.8x
    for b in short.beats:   # 年份 / 章节按原片补齐
        k = next(i for i, x in enumerate(long.beats) if x.caption == b.caption) if b.caption else 0
        assert b.chapter == f"C{k // 10}"
    assert 10 <= len(short.beats) < 60 and short.beats[0].caption == ""
    assert compile_plan(short)["duration"] >= publish.SHORT_TARGET


def test_compose_thumbnail(tmp_path):
    from PIL import Image
    from backend.whatif.publish import compose_thumbnail
    still = tmp_path / "s.png"
    Image.new("RGB", (1920, 1080), (90, 120, 160)).save(still)
    out = compose_thumbnail(still, tmp_path / "t.jpg", "SNOW IN *DUBAI*?", arrow=True)
    im = Image.open(out)
    assert im.size == (1280, 720)
    px = [im.getpixel((x, y)) for x in range(0, 700, 7) for y in range(200, 520, 7)]
    assert any(r > 230 and g > 190 and b < 120 for r, g, b in px)   # 黄色高亮词画上去了


def test_captions_stay_on_screen_in_every_style_and_orientation(tmp_path):
    """横屏 cinematic 曾经把字幕推到 top:1300px（画面外）；每种风格 × 横竖屏都检查字幕框在画面内。"""
    pytest.importorskip("playwright")
    from playwright.sync_api import sync_playwright
    from backend.whatif.render import _open_page
    beat = {"duration": 2.0, "scene": "void", "camera": "wide", "subject": {"type": "none"}, "caption": "Every caption must be seen."}
    with sync_playwright() as pw:
        for st in ("calm", "bold", "cinematic", "toon", "retro", "witness"):
            for w, h in ((1080, 1920), (1920, 1080)):
                sb = Storyboard.model_validate({"format": "timeline", "title": "t", "premise": "p", "clock": {"mode": "none"}, "width": w, "height": h,
                                                "theme": {"style": st}, "intro": {"style": "title", "title": "x", "duration": 0.3},
                                                "beats": [beat], "outro": {"chart": False, "question_duration": 0.5}, "pace": 1.0})
                p = tmp_path / f"{st}{w}.json"
                p.write_text(json.dumps(compile_plan(sb)))
                try:
                    browser, page, _ = _open_page(pw, p, w // 4, h // 4)
                except Exception as e:  # noqa: BLE001
                    if "Executable doesn't exist" in str(e) or "playwright install" in str(e):
                        pytest.skip("chromium 不可用")
                    raise
                try:
                    page.evaluate("WHATIF.frame(36)")
                    r = page.evaluate("(() => { const c = document.querySelector('#cap'), b = c.getBoundingClientRect(), o = document.querySelector('#ov').getBoundingClientRect();"
                                      " return {top: b.top - o.top, bottom: b.bottom - o.top, h: o.height, text: c.textContent, shown: getComputedStyle(c).display !== 'none'}; })()")
                finally:
                    browser.close()
                assert r["shown"] and "caption" in r["text"], (st, w, r)
                assert 0 <= r["top"] and r["bottom"] <= r["h"] + 1, (st, w, r)


def test_toon_keeps_shader_skies_and_survives_scene_switch(tmp_path):
    """toon 曾把天空的 ShaderMaterial 换成卡通材质：自定义天空变暗，之后切到城市场景时报错。"""
    pytest.importorskip("playwright")
    from backend.whatif.render import render_frames
    beats = [{"duration": 1.0, "scene": "custom", "camera": "wide", "subject": {"type": "none"},
              "env": {"set": {"background": ["#5d86ad", "#c9d8e2"], "ground": "plane", "objects": [{"kind": "box"}]}}},
             {"duration": 1.0, "scene": "city", "camera": "aerial", "subject": {"type": "none"}}]
    sb = Storyboard.model_validate({"format": "timeline", "title": "t", "premise": "p", "clock": {"mode": "none"}, "pace": 1.0,
                                    "theme": {"style": "toon"}, "intro": {"style": "title", "title": "x", "duration": 0.3},
                                    "beats": beats, "outro": {"chart": False, "question_duration": 0.5}})
    plan = compile_plan(sb)
    try:
        errs = render_frames(plan, tmp_path / "f", width=180, height=320, frames=[15, 45], workers=1, fmt="png")
    except RuntimeError as e:
        if "playwright install" in str(e) or "Executable doesn't exist" in str(e):
            pytest.skip("chromium 不可用")
        raise
    assert not errs, errs
    from PIL import Image
    top = Image.open(tmp_path / "f" / "000015.png").convert("RGB").getpixel((90, 8))
    assert sum(top) > 300, top   # 天空保持浅蓝渐变，而不是被卡通材质染暗


# ---------------------------------------------------------------- cinema: moves, transitions, flows, sound
def _cine_sb(n=12, **theme):
    beats = [{"duration": 3, "scene": "custom", "camera": "dolly", "subject": {"type": "none"}, "caption": f"Beat {i} is here.",
              "env": {"set": {"ground": "plane", "objects": [{"kind": "box"}]}}} for i in range(n)]
    return Storyboard.model_validate({"format": "timeline", "title": "cine test", "premise": "p", "clock": {"mode": "none"},
                                      "theme": theme, "beats": beats, "outro": {"chart": False}, "pace": 1.8})


def test_cinema_assigns_varied_moves_and_transitions_deterministically():
    from backend.whatif.cinema import assign, MOVES, TRANSITIONS
    sb = _cine_sb(16, flow="punchy")
    a, b = assign(sb), assign(sb)
    assert a == b                                            # 纯函数，可复现
    assert all(x["move"] in MOVES and x["tr"] in TRANSITIONS for x in a)
    assert a[0]["tr"] == "cut"                               # 第一镜在标题下
    assert all(a[i]["move"] != a[i + 1]["move"] for i in range(len(a) - 1))   # 相邻不重复
    assert len({x["move"] for x in a}) >= 4 and len({x["tr"] for x in a}) >= 3
    sb2 = sb.model_copy(update={"beats": [sb.beats[0].model_copy(update={"move": "dutch", "transition": "glitch"})] + sb.beats[1:]})
    assert assign(sb2)[0]["move"] == "dutch"                 # 写死的优先
    w = _cine_sb(6, style="witness")
    w = w.model_copy(update={"beats": [b.model_copy(update={"camera": "witness"}) for b in w.beats]})
    assert {x["move"] for x in assign(w)} == {"none"}        # 目击者视角固定


def test_flow_shapes_rhythm_and_plan_carries_cinema():
    from backend.whatif.model import apply_pace
    build = [b.duration for b in apply_pace(_cine_sb(12, flow="build")).beats]
    steady = [b.duration for b in apply_pace(_cine_sb(12, flow="steady")).beats]
    assert build[0] > build[-1] and len(set(steady)) == 1   # build：越剪越快；steady：平稳
    plan = compile_plan(_cine_sb(10, flow="punchy", palette="noir"))
    assert plan["theme"]["flow"] == "punchy" and "grayscale" in plan["theme"]["palette_css"]
    assert all("move" in b and "tr" in b for b in plan["beats"])
    trs = [f["tr"] for f in plan["frames"] if f.get("tr")]
    assert trs and all(0 <= t["p"] <= 1 for t in trs)
    kinds = {e["type"] for e in plan["audio"]}
    assert "whoosh" in kinds and ({"impact", "glitch"} & kinds)   # 转场 / 运镜自动配声


def test_new_effects_get_matching_sounds():
    sb = _cine_sb(4)
    beats = [b.model_copy(update={"effects": [fx]}) for b, fx in zip(sb.beats, ["explosion", "sparks", "confetti", "lightning"])]
    plan = compile_plan(sb.model_copy(update={"beats": beats}))
    kinds = {e["type"] for e in plan["audio"]}
    assert {"boom", "debris", "sparkle", "pop", "thunder"} <= kinds
    assert any(f.get("lightning") for f in plan["frames"])


def test_variety_rotates_flow_and_palette_against_history():
    from backend.whatif.cinema import resolve_variety
    sb = _cine_sb(3, style="cinematic")
    hist = [{"flow": "build", "palette": "noir"}, {"flow": "punchy", "palette": "teal_orange"}]
    got = resolve_variety(sb, hist).theme
    assert got.flow not in ("build", "punchy") and got.palette not in ("noir", "teal_orange")
    fixed = resolve_variety(sb.model_copy(update={"theme": sb.theme.model_copy(update={"flow": "build"})}), hist).theme
    assert fixed.flow == "build"                             # 用户指定的不改


def test_audio_synthesizes_new_events():
    from backend.whatif import audio as A
    for k in ("debris", "sparkle", "pop", "glitch", "shimmer"):
        x = A.EVENT_FUNCS[k](3)
        assert len(x) > 1000 and 0.05 < float(abs(x).max()) < 1.0
    assert len(A._whoosh(1, 0.5)) == int(0.5 * A.SR)


def test_cinema_effects_and_moves_render(tmp_path):
    """每种新特效 + 运镜 + 转场都渲一帧（含转场中途），页面不报错。"""
    pytest.importorskip("playwright")
    from backend.whatif.render import render_frames
    fxs = ["explosion", "sparks", "confetti", "lightning", "rays", "glitch", "bloom"]
    moves = ["swoop_in", "spiral", "fly_by", "dutch", "whip", "drone_rise", "arc_left"]
    trs = ["cut", "whip", "flash", "zoom", "dip", "glitch", "whip"]
    sb = _cine_sb(7, style="bold")
    beats = [b.model_copy(update={"effects": [f], "move": m, "transition": t, "duration": 1.0}) for b, f, m, t in zip(sb.beats, fxs, moves, trs)]
    beats.append(beats[0].model_copy(update={"scene": "globe", "env": None, "move": "swoop_in", "transition": "flash"}))
    plan = compile_plan(sb.model_copy(update={"beats": beats, "pace": 1.0}))
    frames = [int((b["start"] + d) * plan["fps"]) for b in plan["beats"] for d in (0.1, 0.6)]
    try:
        errs = render_frames(plan, tmp_path / "f", width=180, height=320, frames=frames, workers=1, fmt="png")
    except RuntimeError as e:
        if "playwright install" in str(e) or "Executable doesn't exist" in str(e):
            pytest.skip("chromium 不可用")
        raise
    assert not errs, errs


def test_no_globes_rule_and_prompt():
    """用户要求：视频里不要地球仪 / 太空地球。检查器拦下，planner 提示里也不再提供。"""
    from backend.whatif.quality import quality_report
    from backend.whatif.planner import build_prompt
    sb = _cine_sb(3)
    for scene, env in (("globe", None), ("orbit", None)):
        bad = sb.model_copy(update={"beats": [sb.beats[0].model_copy(update={"scene": scene, "env": env})] + sb.beats[1:]})
        assert any(x.rule == "no_globe" and x.level == "fix" for x in quality_report(bad)), scene
    d = sb.model_dump()
    d["beats"][0]["env"] = {"set": {"ground": "plane", "objects": [{"kind": "earth"}]}}
    assert any(x.rule == "no_globe" for x in quality_report(Storyboard.model_validate(d)))
    assert not any(x.rule == "no_globe" for x in quality_report(sb))
    p = build_prompt("What if the oceans dried up?")
    assert "NEVER use globes" in p and '"scene": "globe"' not in p and "globe uses env.globe" not in p


# ---------------------------------------------------------------- pov: first person
def _pov_sb(n=6, **kw):
    beats = [{"duration": 3, "scene": "custom", "camera": "eyes", "subject": {"type": "none"}, "caption": f"You see thing {i}. Your hands shake.",
              "env": {"set": {"ground": "plane", "focus": [0, 1.6, 0], "objects": [{"kind": "box", "at": [0, 1, -3]}]}}} for i in range(n)]
    beats[0]["hands"] = {"pose": "phone", "phone_text": "MOM: where are you??"}
    beats[0]["head"] = "walk"
    if n > 2:
        beats[2]["hands"] = {"pose": "shield", "tremble": 0.5}
        beats[2]["head"] = "run"
    sb = {"format": "pov", "title": "t", "premise": "p", "pov": {"text": "you wake up and gravity is gone"}, "beats": beats,
          "outro": {"chart": False, "end": {"kind": "question", "lines": ["WHAT DO", "YOU DO?"]}}, "pace": 1.0}
    sb.update(kw)
    return Storyboard.model_validate(sb)


def test_pov_needs_hook_text():
    with pytest.raises(Exception):
        Storyboard.model_validate({"format": "pov", "title": "t", "premise": "p", "beats": [{"duration": 2, "camera": "eyes"}]})


def test_pov_plan_opens_eyes_inherits_hands_and_types():
    plan = compile_plan(_pov_sb())
    assert plan["pov"]["text"] == "you wake up and gravity is gone" and plan["theme"]["captions"] == "typed"
    f0, f_open = plan["frames"][0], plan["frames"][int(1.6 * plan["fps"])]
    assert f0["pov"]["lid"] > 0.95 and f_open["pov"]["lid"] == 0 and f0["pov"]["k"] < 0.1 and f_open["pov"]["k"] == 1
    assert "intro" not in f0 and f0.get("cap")          # 没有片头卡；字幕从第一帧就打字
    hands = [b["hands"]["pose"] for b in plan["beats"]]
    assert hands == ["phone", "phone", "shield", "shield", "shield", "shield"]   # 没写就沿用上一段
    assert [b["head"] for b in plan["beats"]][:4] == ["walk", "walk", "run", "run"]
    assert all(b["move"] == "none" for b in plan["beats"])   # 第一人称不叠加电影运镜
    types = {e["type"] for e in plan["audio"]}
    assert {"steps", "run_steps", "breath"} <= types      # 走路 / 跑步自动配脚步和喘气
    # blink 转场：上一段末尾闭眼，本段开头睁开
    blink = [b["i"] for b in plan["beats"] if b["tr"] == "blink"]
    assert blink
    s = plan["beats"][blink[0]]["start"]
    near = [f for f in plan["frames"] if abs(f["t"] - s) < 0.05 and f.get("pov")]
    assert max(f["pov"]["lid"] for f in near) > 0.6


def test_pov_hook_and_quality_rules():
    from backend.whatif.hooks import hook_report
    from backend.whatif.quality import quality_report
    good = _pov_sb()
    assert not [x for x in hook_report(good) if x.rule in ("pov", "first3s") and x.level == "fix"]
    from backend.whatif.publish import metadata
    m = metadata(good.model_copy(update={"title": "POV: you wake up and gravity is gone"}))
    assert m["title"] == "POV: you wake up and gravity is gone" and "#pov" in m["hashtags"]
    third = good.model_copy(update={"beats": [b.model_copy(update={"caption": f"The city is quiet at {i}."}) for i, b in enumerate(good.beats)]})
    assert any(x.rule == "pov" for x in hook_report(third))
    long_hook = good.model_copy(update={"pov": good.pov.model_copy(update={"text": "you wake up one day and find out that every single thing floats away"})})
    assert any(x.rule == "first3s" and x.where == "pov.text" for x in hook_report(long_hook))
    wide = good.model_copy(update={"beats": [b.model_copy(update={"camera": "wide"}) for b in good.beats]})
    assert any(x.rule == "pov" and x.level == "fix" for x in quality_report(wide))


def test_pov_renders_closed_eyes_then_hands(tmp_path):
    pytest.importorskip("playwright")
    from PIL import Image
    from backend.whatif.render import render_frames
    plan = compile_plan(_pov_sb(3))
    try:
        errs = render_frames(plan, tmp_path / "f", width=270, height=480, frames=[0, 75], workers=1, fmt="png")
    except RuntimeError as e:
        if "playwright install" in str(e) or "Executable doesn't exist" in str(e):
            pytest.skip("chromium 不可用")
        raise
    assert not errs, errs
    closed = Image.open(tmp_path / "f" / "000000.png").convert("RGB")
    assert sum(closed.getpixel((135, 300))) < 60            # 开头闭着眼：画面中下部是眼皮
    opened = Image.open(tmp_path / "f" / "000075.png").convert("RGB")
    assert sum(opened.getpixel((135, 300))) > 60
    # 画面下半部有手机屏幕（深色）+ 手（肤色）：找到偏暖的肤色像素
    px = [opened.getpixel((x, y)) for x in range(40, 230, 4) for y in range(300, 470, 4)]
    assert any(r > 150 and r > b + 35 and g > 90 for r, g, b in px)


# ---------------------------------------------------------------- bodycam style
def test_bodycam_plan_audio_and_auto_style():
    from backend.whatif.quality import auto_style
    from backend.whatif.audio import synthesize
    sb = _pov_sb(4).model_copy(update={"theme": Theme(style="bodycam", rec="2026-10-26 03:12:40")})
    plan = compile_plan(sb)
    assert plan["theme"]["rec"] == "2026-10-26 03:12:40" and plan["theme"]["palette"] in ("natural", "cool")
    thumps = [e for e in plan["audio"] if e["type"] == "impact" and e["gain"] == 0.22]
    assert len(thumps) == 3                                   # 每刀一下话筒闷响
    assert not any(b["tr"] in ("flash", "zoom") for b in plan["beats"])   # 实拍感：不闪白、不冲推
    assert synthesize(plan).shape[1] == 2
    assert compile_plan(_pov_sb(4))["theme"]["rec"]           # 没写就用当天日期
    assert auto_style("POV: you explore a haunted hospital") == "bodycam"


def test_bodycam_renders_rec_hud_and_fisheye(tmp_path):
    pytest.importorskip("playwright")
    from PIL import Image
    from backend.whatif.render import render_frames
    sb = _pov_sb(2).model_copy(update={"theme": Theme(style="bodycam"), "pov": Pov(text="you wake up and gravity is gone", open_eyes=False)})
    sb.beats[1].effects = ["nightvision"]
    sb.beats[1].env.set.background = ("#d0d4d8", "#f1f3f5")   # 亮场景里才看得出夜视的绿
    plan = compile_plan(sb)
    try:
        errs = render_frames(plan, tmp_path / "f", width=270, height=480, frames=[10, 120], workers=1, fmt="png")
    except RuntimeError as e:
        if "playwright install" in str(e) or "Executable doesn't exist" in str(e):
            pytest.skip("chromium 不可用")
        raise
    assert not errs, errs
    im = Image.open(tmp_path / "f" / "000010.png").convert("RGB")
    rec = [im.getpixel((x, y)) for x in range(8, 40) for y in range(10, 30)]
    assert any(r > 180 and g < 110 and b < 110 for r, g, b in rec)     # 红色 REC 点
    corner, centre = sum(im.getpixel((3, 470))), sum(im.getpixel((135, 300)))
    assert corner < centre                                               # 鱼眼暗角
    from PIL import ImageStat
    nv = ImageStat.Stat(Image.open(tmp_path / "f" / "000120.png").convert("RGB").crop((20, 120, 250, 460))).mean   # 第 4 秒 = 第二段
    assert nv[1] > nv[0] * 1.6 and nv[1] > nv[2] * 1.4                   # 夜视：整体偏绿


def test_speed_in_mph_keeps_physics_in_ms():
    from backend.whatif.model import hud_for, MPH
    from backend.whatif.schema import Quantity
    q = Quantity.model_validate({"kind": "speed", "unit": "mph", "model": {"type": "exponential", "start": 2, "factor": 2},
                                 "milestones": [{"label": "HIGHWAY", "value": 31.3}]})
    h = hud_for(q, 31.3, 4)
    assert h.unit == "mph" and h.value == "70" and "km/h" in h.sub
    sb = Storyboard.model_validate({"format": "escalation", "title": "t", "premise": "p", "quantity": q.model_dump(), "pace": 1.0,
                                    "beats": [{"duration": 3, "sim_end": 6, "caption": "Now {mph} mph."}]})
    plan = compile_plan(sb)
    assert plan["beats"][0]["caption"] == "Now 143 mph."      # 段末 2·2^5 = 64 m/s ≈ 143 mph
    assert abs(plan["chart"]["refs"][0]["value"] - 31.3 * MPH) < 1e-6


def test_length_in_feet_shows_feet_then_miles():
    from backend.whatif.model import hud_for, FT
    from backend.whatif.schema import Quantity
    q = Quantity.model_validate({"kind": "length", "unit": "ft", "model": {"type": "exponential", "start": 1.7, "factor": 2},
                                 "milestones": [{"label": "HOOP", "value": 3.05}]})
    h = hud_for(q, 3.4, 1)
    assert (h.value, h.unit, h.sub) == ("11", "ft", "3.4 m")
    assert hud_for(q, 14000, 13).unit == "mi" and hud_for(q, 14000, 13).value == "8.7"
    sb = Storyboard.model_validate({"format": "escalation", "title": "t", "premise": "p", "quantity": q.model_dump(), "pace": 1.0,
                                    "beats": [{"duration": 3, "sim_end": 3, "caption": "You're {ft} tall."}]})
    plan = compile_plan(sb)
    assert plan["beats"][0]["caption"] == "You're 22 ft tall."      # 段末仍在第 3 秒：1.7·2^2 = 6.8 m
    assert abs(plan["chart"]["refs"][0]["value"] - 3.05 * FT) < 1e-6


def test_usa_region_map_fields_reach_the_frame():
    beats = [{"duration": 2, "scene": "map", "camera": "wide", "subject": {"type": "none"}, "chapter": "A",
              "env": {"map": {"region": "usa", "zone": {"x": 0.25, "y": 0.2, "text": "YELLOWSTONE"}, "grow": True, "zone_stretch": 1.8}}}]
    sb = Storyboard.model_validate({"format": "story", "title": "t", "premise": "p", "beats": beats, "outro": {"chart": False}, "pace": 1.0})
    m = next(f["map"] for f in compile_plan(sb)["frames"] if f.get("map"))
    assert m["region"] == "usa" and m["grow"] and m["zone_stretch"] == 1.8


def test_render_frames_resumes_and_skips_existing(tmp_path, monkeypatch):
    from backend.whatif import render
    calls = []

    class FakeProc:
        def __init__(self, cmd, **kw):
            job = json.loads(Path(cmd[-2]).read_text())
            calls.append(job["frames"])
            for i in job["frames"]:
                (Path(job["out"]) / f"{i:06d}.jpg").write_bytes(b"x")
            Path(cmd[-1]).write_text(json.dumps({"errors": []}))
            self.stderr = None
            self.returncode = 0

        def poll(self):
            return 0

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(render.subprocess, "Popen", FakeProc)
    plan = {"n_frames": 10, "fps": 30}
    out = tmp_path / "frames"
    out.mkdir()
    for i in range(6):                                   # 前 6 帧上次已经渲好了
        (out / f"{i:06d}.jpg").write_bytes(b"x")
    render.render_frames(plan, out, width=10, height=10, workers=2)
    assert sorted(i for part in calls for i in part) == [6, 7, 8, 9]
    calls.clear()
    assert render.render_frames(plan, out, width=10, height=10) == [] and not calls


def test_series_end_card_title_and_thumbnail_badge(tmp_path):
    from PIL import Image
    from backend.whatif import publish
    sb = _set_sb([{"kind": "box"}], n=3).model_copy(update={"series": {"name": "EVERY PLANET", "part": 2, "next": "Football on Jupiter?"}})
    sb = Storyboard.model_validate(sb.model_dump())
    end = next(f["end"] for f in compile_plan(sb)["frames"] if f.get("end"))
    assert end["series"]["part"] == 2 and end["series"]["next"] == "Football on Jupiter?"
    m = publish.metadata(sb)
    assert m["title"].endswith("(Part 2)") and "#EveryPlanet" in m["hashtags"] and "Part 2 of the Every Planet series. Next: Football on Jupiter? Follow" in m["description"]
    sb2 = Storyboard.model_validate({**sb.model_dump(), "series": {"name": "POV", "part": 5, "next": "Zombies, day 1"}})
    assert "Part 5 of the POV series. Next: Zombies, day 1. Follow" in publish.metadata(sb2)["description"]
    still = tmp_path / "s.png"
    Image.new("RGB", (1080, 1920), (90, 120, 160)).save(still)
    im = Image.open(publish.compose_thumbnail(still, tmp_path / "t.jpg", "X", size=(1080, 1920), badge="PART 2")).convert("RGB")
    px = [im.getpixel((x, y)) for x in range(50, 260, 6) for y in range(55, 140, 6)]
    assert any(r > 200 and g < 80 and b < 80 for r, g, b in px)        # 红色 PART 角标


def test_cold_open_starts_on_the_first_caption_and_quick_length_rule():
    from backend.whatif.quality import quality_report
    from backend.whatif.hooks import hook_report
    sb = _set_sb([{"kind": "box", "animate": [{"type": "spin"}]}], n=4, intro={"style": "none"}, length="quick")
    plan = compile_plan(sb)
    f0 = plan["frames"][0]
    assert plan["intro_duration"] == 0 and "intro" not in f0 and f0["cap"]["text"] == "Every person is gone."
    assert not any(x.where == "intro" for x in hook_report(sb))                      # 冷开场不要求片头卡
    flashy = Storyboard.model_validate({**sb.model_dump(), "beats": [{**sb.beats[0].model_dump(), "effects": ["flash"]}] + [b.model_dump() for b in sb.beats[1:]]})
    assert any(x.where == "beats[0].effects" for x in hook_report(flashy))            # 冷开场第一帧不能是白闪
    lens = [x for x in quality_report(sb) if x.rule == "length"]
    assert lens and "quick shorts" in lens[0].msg                                    # 4 段 ≈ 10 秒：太短
    sb12 = _set_sb([{"kind": "box", "animate": [{"type": "spin"}]}], n=12, intro={"style": "none"}, length="quick")
    assert not any(x.rule == "length" for x in quality_report(sb12))                     # 12 段 ≈ 30 秒：刚好
