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
from .schema import ACTIONS, CAMERAS, EFFECTS, ICONS, OUTFITS, ROOMS, SCENES, SFX, Storyboard

logger = logging.getLogger(__name__)

EXAMPLES_DIR = Path(__file__).parent / "examples"
EXAMPLE_PATH = EXAMPLES_DIR / "twice_as_fast.json"
FORMAT_EXAMPLES = {
    "escalation": "twice_as_fast.json",
    "timeline": "earth_stopped_spinning.json",
    "countdown": "friction_disappeared.json",
    "story": "moon_shattered.json",
}

FORMATS_GUIDE = """FORMATS (pick the one that fits the premise best, unless told otherwise):
- escalation: a single quantity keeps growing (2x faster / taller / hotter every second). Needs `quantity` (growth model,
  milestones, optional limit). Data HUD at the top, milestones pop up when crossed, step chart + question at the end.
- timeline: something happens once, then we jump forward in time ("+10 SEC", "+1 HOUR", "+1 YEAR", "+100 YEARS") to
  show consequences (what if all X disappeared / the Sun went out / Earth stopped spinning). clock.mode="elapsed",
  each beat sets `time` to a short label. Use `stat` for big, well-known facts ("90%" / "OF THE WORLD'S NURSES ARE WOMEN").
- countdown: a short event with a ticking clock (what if friction / the atmosphere / gravity vanished for 5 seconds).
  clock.mode="countdown", each beat sets `time` to [from_seconds, to_seconds] going DOWN; a final beat can use a word
  ("BACK"). Video time is much longer than clock time (slow motion).
- story: a narrative in 4-6 chapters (a real event reconstruction, a disaster unfolding, a hypothetical sequence).
  Beats set `chapter` when a new chapter starts, `chip` for time/date labels ("6:03 PM", "5 DAYS LATER"), `tooltip`
  for sourced facts ("REAL EVENT: ..."), `banner` for a news headline, scene="map" with env.map for maps.
- survival: a personal survival scenario timed from an event ("TIME SINCE BITE"). clock.mode="stopwatch",
  `time` = [from, to] seconds counting UP; use `screen` (vitals / phone_call) and interiors (hospital)."""

RULES = f"""You are the writer-director of a short vertical "what if" science video (TikTok / Reels / Shorts, 40-95 seconds).
Style: calm, cinematic low-poly 3D simulation; small caps labels; one short italic caption per shot; NO narration and NO
music (sound effects only, generated automatically); a title card at the start and an end card.

{FORMATS_GUIDE}

YOUR OUTPUT is a storyboard JSON (same shape as the examples). You write the words and choose the shots; the renderer
draws everything and computes every number that comes from a growth model.

NUMBERS AND FACTS
- Only state facts that are well established and commonly cited. Prefer "about"/"~" for rounded figures. Never invent
  statistics, dates, names or quotes. If unsure, leave the number out.
- Speculative consequences must be framed as hypothetical ("would", "could"); label simulations as simulations.
- escalation only: NEVER hard-code computed numbers in captions; use placeholders {', '.join('{' + p + '}' for p in PLACEHOLDERS)}
  (filled at the end of each beat). Milestones are real reference values in quantity.unit; they must be crossed.
- No political statements or endorsements. For religious or historical narratives, attribute events to their source
  (use caption_ref such as "LUKE 22:42") rather than presenting them as established fact.

TIMING
- 10-20 beats, each 2.5-5 s. Total 40-90 s plus the end card (3 s). First beat is under the title card (intro.duration
  ~2.5 s), so keep it captionless and visually strong (establishing / wide).
- escalation: each beat has sim_end (simulated seconds reached at the end of the beat, never decreasing).

SHOTS
- scene: {', '.join(SCENES)}.
  interior uses env.room: {', '.join(ROOMS)}. globe uses env.globe (night_side, markers [lat, lon, kind ring|dot|glow|cloud,
  radius], faults, ring, moon none|whole|shattered, frozen, dry_oceans, spin, focus [lat, lon]). map uses env.map
  (labels/path points with x,y in 0..1 and text, zone + zone_radius, style dark|satellite|paper).
- env (carries over to the next beats in the same scene; reset when the scene changes): time day|golden|dusk|night|dawn,
  weather clear|overcast|rain|storm|snow|ash|fog|dust, sky normal|red|dark|meteors|aurora, crowd 0..1, traffic 0..1,
  empty (people gone), lights_off, overgrown 0..1, damage 0..1.
- camera: {', '.join(CAMERAS)} (establishing/wide/aerial/top_down for places, pov/dolly to move through a space,
  front/closeup/side/follow for a subject; on globe: wide/front/closeup/orbit).
- subject: {{"type": runner|person|ball|car|cube|rocket|none, "action": ..., "outfit": ...}} only when it changes;
  type none for pure places. cast: groups of people [{{"outfit", "count" (<=40), "action", "layout" around|line|row|scatter|seated|crowd, "distance"}}].
  outfits: {', '.join(OUTFITS)}. actions: {', '.join(ACTIONS)}.
- effects (only when motivated): {', '.join(EFFECTS)}. "vanish" makes people disappear during that beat.
- sfx (optional, auto-added for most events): {', '.join(SFX)} with "at" seconds from beat start.
- overlays per beat (optional): stat, card (rows), tooltip, banner, screen (phone_call | vitals | board), callout, chip,
  chapter, caption_ref, time, time_sub.
- narration (optional per beat): when the video is narrated, the caption is read aloud by default. Set "narration" only
  when the spoken wording should differ (e.g. a fuller sentence), or "" to keep a beat silent. Captions must read well aloud.

WRITING
- English only. Captions: one sentence, <= 110 characters, plain, genuine, no hype or clickbait.
- intro: style "title" with the key word wrapped in *asterisks* ("What if all *women* disappeared?"), an icon from
  {', '.join(ICONS)}, optional small subtitle. theme.accent: one restrained color that fits the topic.
- outro.end: kind question|title|tagline|memorial|continued with short ALL-CAPS lines; set outro.chart false unless escalation.

Return ONLY the JSON object, no prose, no markdown fences."""


def _example_text(name: str) -> str:
    return json.dumps(json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8")), ensure_ascii=False, separators=(",", ":"))


def build_prompt(premise: str, notes: str = "", fmt: Optional[str] = None) -> str:
    parts = [RULES, ""]
    names = list(FORMAT_EXAMPLES.items())
    if fmt in FORMAT_EXAMPLES:  # 指定版式时它的示例放最后（离题目最近）
        names.sort(key=lambda kv: kv[0] == fmt)
    for f, name in names:
        parts.append(f"EXAMPLE ({f}):\n{_example_text(name)}\n")
    parts.append(f"PREMISE: {premise.strip()}")
    if fmt:
        parts.append(f"FORMAT: {fmt} (required)")
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
                    call: Optional[Callable[[str], str]] = None) -> Storyboard:
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
            if sb is not None and not problems:
                return sb
        if attempt == max_repairs:
            raise ValueError("分镜校验没通过：\n- " + "\n- ".join(problems))
        logger.info("分镜第 %d 次修正：%s", attempt + 1, problems[:5])
        repair = (f"{prompt}\n\nYour previous storyboard:\n{json.dumps(data, ensure_ascii=False) if data else reply[:6000]}\n\n"
                  "It has these problems. Fix ALL of them and return the full corrected JSON only:\n- " + "\n- ".join(problems))
        reply = call(repair)
    raise AssertionError("unreachable")
