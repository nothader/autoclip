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

    sb = plan_storyboard("What if?", call=fake_llm)
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
