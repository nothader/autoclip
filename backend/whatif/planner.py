"""
任意 what-if 题目 → Storyboard（LLM 写分镜，代码算数字并校验）。

流程：提示词（规则 + 结构说明 + 示例）→ LLM → 解析 JSON → pydantic 结构校验 + model.validate 语义校验
→ 有问题就把错误列表回传给 LLM 修（最多 max_repairs 轮）。
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from pydantic import ValidationError

from .model import PLACEHOLDERS, validate
from .schema import CAMERAS, EFFECTS, SCENES, Storyboard

logger = logging.getLogger(__name__)

EXAMPLE_PATH = Path(__file__).parent / "examples" / "twice_as_fast.json"

RULES = f"""You are the writer-director of a short vertical "what if" science video (TikTok / Reels / Shorts, 60-95 seconds).
Style: a calm, cinematic 3D simulation. A low-poly character (or object) in a real-world setting, a data HUD at the top,
milestone call-outs that pop up when a real-world reference value is crossed, one short italic caption per shot,
no narration, no music (sound effects only), and a step chart + question card at the end.

Your job: turn the PREMISE into a storyboard JSON. You write the words and choose the shots.
The renderer COMPUTES every number from your growth model, so:

NUMBERS
- Pick quantity.kind from: speed (unit m/s), length (m), mass (kg), temperature (°C), count, generic.
- Describe the growth with quantity.model: exponential (start, factor, step seconds), linear (start, rate), or keyframes [[sim_seconds, value], ...].
- NEVER hard-code a computed number in a caption. Use placeholders, which are filled from the model at the END of that beat:
  {', '.join('{' + p + '}' for p in PLACEHOLDERS)}.
  ({{kmh}}, {{mach}}, {{light_pct}}, {{distance}} only make sense for speed.) Small counting words like "four seconds in" are fine
  only if they are true for that beat.
- Milestones are real, well-known reference values (with the value in the same unit as quantity.unit). They pop up automatically at the
  exact moment the value crosses them, so do NOT repeat them in captions. Only use values you are confident are correct and commonly cited;
  write the detail line as "ITS TOP SPEED: ABOUT 100 km/h" style, approximate wording ("about", "~") when appropriate.
  Every milestone must actually be crossed during the simulated time. 6-10 milestones, spread across the video.
- Use quantity.limit for a hard physical limit if one exists (e.g. speed of light, 299792458 m/s).

TIMING
- Each beat has a video duration (2.5-5 s) and sim_end: the simulated time reached at the end of that beat. Simulated time must never go backwards.
  sim progressing slower than video time shows "SLOW MOTION ×N" in the HUD; faster shows "TIME-LAPSE ×N". Most beats should be slow motion.
- 14-20 beats. Total beats duration 55-80 s. Outro: chart 6-8 s with 1-2 short chart_captions, question card 3 s.

SHOTS
- scene: one of {', '.join(SCENES)}. Progress through settings that fit the escalation (e.g. city → highway → desert → sky → orbit → deep_space).
- camera: one of {', '.join(CAMERAS)}. Vary them; start wide, then front/closeup to introduce the subject.
- subject: {{"type": runner|ball|car|cube|rocket|none, "action": idle|walk|run|sprint|float|fly, "scale": 1, "scale_with_value": false, "color": "#c8322b"}}.
  Only set it when it changes. For a growing-size premise use kind=length and scale_with_value=true.
- effects (only when physically motivated): {', '.join(EFFECTS)}.
- sfx (optional): [{{"type": "riser"|"whoosh"|"boom"|"impact"|"swell"|"tick", "at": seconds_from_beat_start}}]. Booms are added automatically for
  shockwave / vapor_cone, impacts for flash, swells for cards, whooshes for milestones, ticks for HUD steps. Add a riser ~2.4 s before a big moment.
- callout (optional, for non-numeric notes such as "SIMULATION — BODY MADE INDESTRUCTIBLE"). card (optional, at most 1-2): a boxed panel such as
  "PHYSICS BREAKDOWN" with rows [[label, value]]; values may use placeholders; tone "warning" for impossibility.

WRITING
- English only. Captions: one sentence, <= 110 characters, plain and genuine. No hype, no clickbait, no false claims.
- If the premise becomes physically impossible or fatal, say so plainly and, if you continue, label it a simulation.
- Intro card lines: 4 short ALL-CAPS lines like ["WHAT IF", "YOU GOT", "2× FASTER", "EVERY SECOND?"], accent = index of the key line.
- End question: an engaging, honest question in ALL CAPS (<= 40 chars).

Return ONLY the JSON object, no prose, no markdown fences."""


def build_prompt(premise: str, notes: str = "") -> str:
    example = EXAMPLE_PATH.read_text(encoding="utf-8")
    return (f"{RULES}\n\nEXAMPLE (premise: \"What if you got 2x faster every second?\"):\n{example}\n\n"
            f"PREMISE: {premise.strip()}\n" + (f"EXTRA NOTES: {notes.strip()}\n" if notes.strip() else "")
            + "\nStoryboard JSON:")


def extract_json(text: str) -> Dict[str, Any]:
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", t, re.S)
    if m:
        t = m.group(1).strip()
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("回复里没有 JSON 对象")
    return json.loads(t[start:end + 1])


def check(data: Dict[str, Any]) -> tuple[Optional[Storyboard], List[str]]:
    try:
        sb = Storyboard.model_validate(data)
    except ValidationError as e:
        errs = []
        for er in e.errors()[:25]:
            loc = ".".join(str(x) for x in er["loc"])
            errs.append(f"{loc}: {er['msg']}")
        return None, errs
    return sb, validate(sb)


def plan_storyboard(premise: str, *, notes: str = "", max_repairs: int = 2,
                    call: Optional[Callable[[str], str]] = None) -> Storyboard:
    """call(prompt) -> 文本；默认用 AutoClip 当前配置的 LLM。"""
    if call is None:
        from backend.core.llm_manager import get_llm_manager
        mgr = get_llm_manager()
        call = lambda p: mgr.call_with_retry(p)  # noqa: E731

    prompt = build_prompt(premise, notes)
    reply = call(prompt)
    for attempt in range(max_repairs + 1):
        try:
            data = extract_json(reply)
        except (ValueError, json.JSONDecodeError) as e:
            problems = [f"invalid JSON: {e}"]
            data = None
        else:
            sb, problems = check(data)
            if sb is not None and not problems:
                return sb
        if attempt == max_repairs:
            raise ValueError("分镜校验没通过：\n- " + "\n- ".join(problems))
        logger.info("分镜第 %d 次修正：%s", attempt + 1, problems[:5])
        repair = (f"{prompt}\n\nYour previous storyboard:\n{json.dumps(data, ensure_ascii=False) if data else reply[:6000]}\n\n"
                  "It has these problems. Fix ALL of them and return the full corrected JSON only:\n- " + "\n- ".join(problems))
        reply = call(repair)
    raise AssertionError("unreachable")
