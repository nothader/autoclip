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

from .model import validate
from .schema import ACTIONS, CAMERAS, EFFECTS, SET_KINDS, SFX, Storyboard

logger = logging.getLogger(__name__)

EXAMPLES_DIR = Path(__file__).parent / "examples"
EXAMPLE_PATH = EXAMPLES_DIR / "elevator_41h.json"
EXAMPLE_FILES = ["coma.json", "elevator_41h.json"]

RULES = f"""You are the writer-director of a first-person "Block POV" what-if video (TikTok / Reels / Shorts, 60-100 seconds),
in the style of the blocky 3D "what if" channels: a smooth block-people world seen through YOUR eyes, with your blocky hands
in frame. The viewer IS the main character.

YOUR OUTPUT is a storyboard JSON (same shape as the examples). Every beat: scene "custom", env.set built for that place.

STRUCTURE (60-100 s, 16-26 beats of 2.8-4 s):
1. Beat 0: caption "" (the title shows over it for 3.5 s). A normal, specific moment (party dare, train to work, dinner).
2. The event lands in 2-3 short beats. Then time jumps forward; each jump is a new place or angle.
3. One real-world anchor per video, stated flatly (a real number, case or source line in caption_by: "Matthew 24:27").
4. People around you get it wrong; you choose differently. Climax: tracker turns red (alert) or huge (big), shake.
5. A quiet emotional resolution. End card: one gold question to YOU (outro.end.lines = ["Would you be ready?"]).

TEXT:
- intro.title: "What if ... *key word* ...?" (one word in *stars* gets the accent colour). intro.style "none".
- Captions: italic serif, second person, present tense, 3-9 words, grade-3 words ("You jump. Not far enough.").
  Dialogue in quotes with caption_by = who said it. At least 40% of captions say "you"/"your".
- tracker on most beats (inherits to the next beats when omitted): label (tiny caps), and ONE of clock ("11:02:14 PM",
  ticks live), count_from/count_to (+unit, prefix "$"), value ("DAY 3", "CLOSED"), scramble (unknown countdown); sub line.
- banner: {{"kicker": "BREAKING NEWS", "title": "...", "subtitle": "..."}} for world-wide moments; screen: vitals / board.

SOUND: no narrator (narration off). People in the scene talk: beat.voices [{{"text","voice","at"}}] with Kokoro voices
(am_michael, am_adam, am_eric, am_onyx, am_puck, af_heart, af_bella, af_nicole, af_sky, bf_emma, bm_george). theme.music "tender".

CAMERA: mostly camera "eyes" (env.set.focus = your eye position, you look toward -z) with hands
(pose: {", ".join(["none", "idle", "reach", "phone", "shield", "grab", "fists", "point", "hold", "float"])};
holding phone/cup; phone_text + phone_time) and head (breathe/walk/run/stumble/fall/float/shake), gaze [yaw, pitch].
Cut away 1-3 times to "front"/"far" (faces, wide shots). Cameras: {", ".join(CAMERAS)}.

WORLD: env.set.objects from kinds {", ".join(SET_KINDS)} (max 40 objects). People are kind "block_person"
(color = top, color2 = trousers, seed = look, action = {", ".join(ACTIONS)}, expression smile/shock/sad/angry/smirk,
outfit "elder" = grey-haired grandparent; rotate [0,180,0] faces you). Build detailed, believable places (rooms with
walls, window light, furniture; streets with buildings). Keep faces above the caption line (about 58% down).
Effects: {", ".join(EFFECTS)}. Sfx: {", ".join(SFX)}.

Topics: believer's POV is allowed for religious topics. Never set a story inside a real attack with real victims (use a
fictional place). No gore.

Return ONLY the JSON object, no prose, no markdown fences."""


def _example_text(name: str) -> str:
    return json.dumps(json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8")), ensure_ascii=False, separators=(",", ":"))


def build_prompt(premise: str, notes: str = "", fmt: Optional[str] = None) -> str:
    parts = [RULES, ""]
    for name in EXAMPLE_FILES:
        parts.append(f"EXAMPLE:\n{_example_text(name)}\n")
    parts.append(f"PREMISE: {premise.strip()}")
    if notes.strip():
        parts.append(f"EXTRA NOTES: {notes.strip()}")
    parts.append("\nStoryboard JSON:")
    return "\n".join(parts)


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


def plan_storyboard(premise: str, *, notes: str = "", fmt: Optional[str] = None, max_repairs: int = 2,
                    call: Optional[Callable[[str], str]] = None, hooks: bool = True) -> Storyboard:
    """call(prompt) -> 文本；默认用 AutoClip 当前配置的 LLM。"""
    if call is None:
        from backend.core.llm_manager import get_llm_manager
        mgr = get_llm_manager()
        call = lambda p: mgr.call_with_retry(p)  # noqa: E731

    prompt = build_prompt(premise, notes, fmt)
    reply = call(prompt)
    for attempt in range(max_repairs + 1):
        try:
            data = extract_json(reply)
        except (ValueError, json.JSONDecodeError) as e:
            problems = [f"invalid JSON: {e}"]
            data = None
        else:
            sb, problems = check(data)
            if sb is not None and fmt and sb.format != fmt:
                problems.append(f"format must be {fmt}, got {sb.format}")
            if sb is not None and not problems and hooks:
                from .hooks import hook_problems
                from .quality import quality_problems
                problems = hook_problems(sb) + quality_problems(sb)
                if problems and attempt == max_repairs:   # 钩子规则只是建议性的：修不完也不报错
                    logger.info("钩子规则仍有 %d 条未满足：%s", len(problems), problems[:3])
                    return sb
            if sb is not None and not problems:
                return sb
        if attempt == max_repairs:
            raise ValueError("分镜校验没通过：\n- " + "\n- ".join(problems))
        logger.info("分镜第 %d 次修正：%s", attempt + 1, problems[:5])
        repair = (f"{prompt}\n\nYour previous storyboard:\n{json.dumps(data, ensure_ascii=False) if data else reply[:6000]}\n\n"
                  "It has these problems. Fix ALL of them and return the full corrected JSON only:\n- " + "\n- ".join(problems))
        reply = call(repair)
    raise AssertionError("unreachable")
