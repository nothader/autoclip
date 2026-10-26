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
from .schema import ACTIONS, CAMERAS, EFFECTS, ICONS, OUTFITS, ROOMS, SCENES, SET_KINDS, SFX, Storyboard

logger = logging.getLogger(__name__)

EXAMPLES_DIR = Path(__file__).parent / "examples"
EXAMPLE_PATH = EXAMPLES_DIR / "twice_as_fast.json"
FORMAT_EXAMPLES = {
    "escalation": "twice_as_fast.json",
    "timeline": "nitrogen_custom_sets.json",
    "countdown": "friction_disappeared.json",
    "story": "moon_shattered.json",
    "pov": "pov_gravity_gone.json",
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
  `time` = [from, to] seconds counting UP; use `screen` (vitals / phone_call) and interiors (hospital).
- pov: "POV: you ..." first-person video; the VIEWER is the character. `pov.text` is the hook pinned at the top from
  frame 0 (it types out while your eyes are still closed, then they open): lower-case, 10 words max, specific
  ("you wake up and gravity is gone", "you're the last person on Earth"). No intro card. Use camera "eyes" on nearly
  every beat; in a custom set, env.set.focus IS your eye position (about 1.6 m up when standing, 0.5 lying down).
  Per beat: `gaze` [yaw, pitch] degrees (+yaw = look right, +pitch = look up) and `gaze_to` to turn your head during
  the beat; `head`: steady / breathe / walk / run (you move forward) / stumble / fall / float / shake (fear);
  `hands`: {pose: idle / reach / phone / shield / grab / cover / fists / point / wave / hold / float / none,
  holding: phone / flashlight / cup, phone_text: "MOM: where are you??", tremble: 0-1}. Captions talk to the viewer in
  short present tense ("You grab the bed. Your phone floats away."). Transitions: blink (eyes close and open) is the
  signature cut. Effects: tunnel (tunnel vision + heartbeat) and dizzy. End on a cliffhanger, then a question card."""

RULES = f"""You are the writer-director of a short vertical "what if" science video (TikTok / Reels / Shorts, 40-95 seconds).
Look: low-poly 3D simulation in one of several visual styles (below); one short caption per shot; NO narration and NO
music unless asked (sound effects only, generated automatically); a title card at the start and an end card.
Default deliverable: a vertical short of 1 minute or more at 1.2x pace.

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
- Videos render at 1.2x pace by default (shots are shortened, never below caption reading time), so write MORE, shorter
  beats with short captions: ~16-22 beats for a 1-minute video. Prefer lively places, crowds and motion over abstract props.
- Each beat 2.5-5 s before pacing; the paced video must run 60-95 s (checked automatically). First beat is under the
  title card (intro.duration ~2.5 s), so keep it captionless and visually strong (establishing / wide).
- Long-form landscape (YouTube): only when asked for a long or landscape/16:9 video, set "width": 1920, "height": 1080 and
  write 60-80 beats (5-6 minutes, up to 15 minutes) in 8-10 chapters, usually the story format.
- escalation: each beat has sim_end (simulated seconds reached at the end of the beat, never decreasing).

SETS: DESIGN YOUR OWN FOR EVERY VIDEO (MOST IMPORTANT VISUAL RULE)
- Prefer scene="custom" with a bespoke env.set built for THIS topic, so every video has its own visual world
  (molecules and lungs for a breathing video, hourglasses and clocks for aging, cells for biology, planets for space).
  Use the generic places (city, suburb, interior ...) only when the story literally happens there.
- NEVER use globes or Earth seen from space: no scene "globe" or "orbit", and no "earth" object in sets.
  For geography use scene "map" or show the actual place (a city, coast, desert, street).
  Vary sets shot to shot: different background colors, object arrangements, materials and camera moves.
- env.set = {{"background": ["#top", "#bottom"] | "stars" | "black" | "white", "ground": none|plane|grid|water|mirror,
  "ground_color", "fog": [color, near, far] (optional), "light": "#color", "light_intensity" (~2), "ambient" (~0.8),
  "focus": [x, y, z] (what the camera looks at), "zoom" (camera distance multiplier, 0.5-2.5),
  "ambience": none|space|room|calm|forest|ocean|wind|lab|rumble, "objects": [...] (<= 40 entries)}}
- object = {{"kind", "at": [x,y,z], "scale": number | [x,y,z], "rotate": [deg,deg,deg], "color", "color2",
  "material": matte|glossy|metal|glass|glow|toon, "opacity", "count" (scatter copies within "spread": [x,y,z]), "seed",
  "animate": [{{"type": spin|bob|orbit|pulse|grow|shrink|fade_in|fade_out|move|drift|wobble, "axis", "speed", "amount", "to"}}]}}
  kinds: {', '.join(k for k in SET_KINDS if k != "earth")}.
  molecule uses "formula" (N2 O2 H2 CO2 H2O CH4 NH3 O3 NaCl CO, real CPK colors); bars uses "values"; person uses
  "outfit"/"action"; particles = a drifting point cloud (count x 20 points). Units are meters; keep objects within ~8 m
  of focus. Use grow/fade/move/shrink to make each beat's set change while its caption plays.

SHOTS
- scene: {', '.join(x for x in SCENES if x not in ("globe", "orbit"))}.
  interior uses env.room: {', '.join(ROOMS)}. map uses env.map (labels/path points with x,y in 0..1 and
  text, keep y between 0.05 and 0.65 so captions stay clear; zone + zone_radius; style dark|satellite|paper).
- env (carries over to the next beats in the same scene; reset when the scene changes): time day|golden|dusk|night|dawn,
  weather clear|overcast|rain|storm|snow|ash|fog|dust, sky normal|red|dark|meteors|aurora, crowd 0..1, traffic 0..1,
  empty (people gone), lights_off, overgrown 0..1, damage 0..1.
- camera: {', '.join(CAMERAS)} (establishing/wide/aerial/top_down for places, pov/dolly to move through a space,
  front/closeup/side/follow for a subject).
- subject: {{"type": runner|person|ball|car|cube|rocket|none, "action": ..., "outfit": ...}} only when it changes;
  type none for pure places. cast: groups of people [{{"outfit", "count" (<=40), "action", "layout" around|line|row|scatter|seated|crowd, "distance"}}].
  outfits: {', '.join(OUTFITS)}. actions: {', '.join(ACTIONS)}.
- effects (only when motivated): {', '.join(EFFECTS)}. "vanish" makes people disappear during that beat.
- sfx (optional, auto-added for most events): {', '.join(SFX)} with "at" seconds from beat start.
- overlays per beat (optional): stat, card (rows), tooltip, banner, screen (phone_call | vitals | board), callout, chip,
  chapter, caption_ref, time, time_sub.
- narration (optional per beat): when the video is narrated, the caption is read aloud by default. Set "narration" only
  when the spoken wording should differ (e.g. a fuller sentence), or "" to keep a beat silent. Captions must read well aloud.

VISUAL STYLE (theme.style; pick the one that fits the topic and vary it between videos, never default to the same look)
- calm: quiet, premium, serif captions. Science explainers, space, serious history.
- bold: viral TikTok look: huge word-by-word captions with a highlighted word, punch-in zoom and whoosh on every cut,
  progress bar. Shock/curiosity topics, body and money "what ifs", fast lists.
- cinematic: documentary: letterbox bars, film grain, warm grade, slow push-ins. History, disasters, people's stories.
- toon: cartoon: cel shading, black outlines, white sticker captions. Funny/absurd premises, kids, animals, food.
- retro: 8-bit pixels and scanlines, green word highlights. Games, tech, internet, "simulation" topics.
- witness: one fixed eyewitness view of a REAL named place (a balcony over a city, a harbour, a café terrace) that
  watches a disaster or change escalate. Use camera "witness" on most beats (it drifts like a handheld shot), set
  theme.anchor ("coffee" default / "drink" / "none") for a cup in the foreground that reacts (steam, frost/ash cap,
  shaking). Drive tension with ONE escalating metric: clock + beat.time_label (small caps label that changes per
  section, e.g. "WIND SPEED" → "STORM SURGE"), beat.time (big number) and beat.time_sub (tiny reference line, e.g.
  "A CAT 5 IS 157 MPH"). Use intro.style "overlay" (title over the first shot, no icon) and end kind "fact"
  (title + one short monospace caps fact line). Small italic-feel captions, few words. Weather/sky/lighting
  changes carry the story; aim for 80-95s.
- theme.layout "split" (vertical only): story on top, a satisfying ball-run loop below, captions on the seam. Good for
  bold/retro storytime-style videos. theme.captions (line|words|box) overrides the style's caption mode.

CINEMATOGRAPHY (make it feel like a film, never a slideshow)
- Every beat gets an automatic camera move and transition chosen by theme.flow, so you only override when the story
  needs a specific one. beat.move: swoop_in (dive in from high and far), swoop_out, crane_up, crane_down, arc_left,
  arc_right, push_in, pull_out, whip, dutch (tilted, uneasy), drone_rise, fly_by, spiral, none.
  beat.transition (into this beat): cut, whip (motion-blur pan), flash (white hit), zoom (punch-in blur), dip (from
  black: big time jumps, sad moments), glitch (digital, tech topics).
- Use the big effects at the story's peaks, not everywhere: explosion, sparks, confetti (celebrations), lightning,
  rays (hope, revelation), glitch (systems failing), bloom (dreamy, warm), plus the older ones (shockwave, fire, smoke,
  shake, earthquake, flash, darken, vanish, freeze ...). Every effect, move and transition gets matching sound.
- theme.flow sets the rhythm: build (cuts speed up toward the climax), punchy (fast cuts with hits), slowburn (slow,
  tense start, then fast), rollercoaster (alternating), steady. theme.palette sets the grade: natural, warm, cool,
  teal_orange, vivid, pastel, mono, noir. Leave both "auto" unless the topic clearly wants one: the tool rotates them
  so consecutive videos never look or move the same.

PRODUCTION LESSONS (learned from earlier videos; visual rules are checked automatically and sent back to you)
- Never boring: every cut must look clearly different (new place, camera, time of day, weather or set). No more than
  2 shots in a row with the same scene and camera (witness style excepted). Something must move in every shot
  (walking people, animate, particles, effects, an orbit/dolly camera).
- Real places and lively scenes beat abstract props: streets, homes, crowds, kitchens, beaches, offices with people
  doing the thing the premise changes. Show the consequence on people, not a text card about it.
- People in custom sets: give every person a different seed and/or outfit/color, or they look like identical clones.
  person color2 = skin color; vary skin tones in crowds unless the premise says otherwise. Use cast for big crowds.
- Faces: with camera "wide" or "closeup", rotate y 0 faces the camera; camera "front" looks from the other side, so
  use rotate y ~180 there when faces matter.
  Do not stand people behind houses, trees or big props; keep the subject inside ~4 m of env.set.focus.
- Higher env.set.focus.y moves objects LOWER in frame. Vertical frames are narrow: keep the action within about
  x = -3..3 m and z = -8..1 m of focus, and use zoom 1.6-1.8 (zoom 1.0 is too close in vertical; ~1.0 suits landscape).
  "dolly" pushes forward about 1 m per second, so nothing should stand between the camera and focus (z > 1).
  Good default for custom sets: camera "dolly" (people at rotate 0 face it), or "wide" for an elevated overview.
- Avoid crossfading two similar silhouettes (young/old versions of a person): put them side by side instead.
- Use time / time_label / chip to show progress ("+1 DAY", "DAY 30") so viewers feel the story move forward.
- thumbnail: 2-5 punchy ALL-CAPS words for the cover with one *highlight* word ("SNOW IN *DUBAI*?",
  "NO MORE *ANIMALS*?"); thumbnail_beat: index of the most dramatic shot (optional).

HOOKS AND RETENTION (checked automatically; violations are sent back to you)
- Be specific and direct: use names, numbers or emotional triggers the viewer relates to ("8 billion people",
  "every", "never", "gone", "Elon Musk"), not vague wording. Put one in the title.
- 3rd-grade reading level: short everyday words, one idea per caption, about 6-12 words. Avoid long words
  (no "reproduction", "disoriented", "populations"; say "make babies", "lost", "groups").
- The most interesting detail goes in the first 3 seconds: the title card and the first caption.
- Cut fluff ("basically", "actually", "in this video", "fun fact", "in conclusion").
- Open a loop early and don't give away the payoff: within the first 3 captions ask a question or tease what's coming
  ("But that's not the worst part.", "Until day 3...") and only answer it near the end. End on a question card.

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
    from .quality import auto_style
    parts.append(f"SUGGESTED STYLE: {auto_style(premise)} (use it unless another style clearly fits this premise better)")
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
