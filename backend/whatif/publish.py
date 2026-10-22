"""
发布包：成片之外的东西——封面、标题 / 简介 / 标签 / 章节、长视频自动剪 1 分钟竖屏短版。

- hero_beat()：挑画面最有冲击力的一段（特效、天象、损毁、人多、靠近高潮）当封面
- thumbnail()：把那一段单独渲一帧（去掉字幕 / HUD），压上 2-5 个词的大字（*星号* 词黄色高亮）
- metadata()：YouTube / TikTok 用的标题、简介、章节时间戳、标签、置顶评论（结尾问题）
- make_short()：横屏长视频 → 竖屏 ~1 分钟短版（挑信息量最大的段落，按 1.8x 节奏凑够时长，去掉旁白）

全部是确定性的模板 / 启发式，不调模型；planner 写的 storyboard.thumbnail 优先。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .hooks import is_specific
from .schema import Storyboard

FONT_DIR = Path(__file__).parent / "web" / "fonts"
THUMB_FONT = FONT_DIR / "InterDisplay-Black.otf"
HIGHLIGHT = (255, 212, 59)       # 封面高亮词（平台封面惯例的亮黄，只用于封面，不用于 App UI）
SHORT_TARGET = 62.0              # 短版目标时长（秒，按节奏压缩后）
LEAD_WORDS = {"it", "the", "a", "an", "we", "you", "there", "our", "your", "i"}
TRAIL_WORDS = {"and", "or", "of", "in", "the", "a", "an", "to", "with", "for", "on", "at", "instead"}
STOP = LEAD_WORDS | TRAIL_WORDS | {"what", "if", "was", "were", "is", "are", "be", "been", "had", "has", "have", "could",
                                  "would", "did", "do", "does", "never", "every", "all", "only", "no", "not", "suddenly",
                                  "became", "become", "started", "start", "from", "into", "than", "this", "that", "its"}


# ------------------------------------------------------------------ 选段
def effective(sb: Storyboard, i: int):
    """第 i 段实际生效的 env / subject（省略 = 沿用同场景上一段）。"""
    from .schema import Env, Subject
    env, subj = None, None
    for j, b in enumerate(sb.beats[: i + 1]):
        if j and b.scene != sb.beats[j - 1].scene:
            env = None
        env = b.env or env
        subj = b.subject or subj
    return env or Env(), subj or Subject(type="none")


def beat_score(sb: Storyboard, i: int) -> float:
    b = sb.beats[i]
    env, _ = effective(sb, i)
    s = 2.0 * len(b.effects) + (1.5 if b.stat else 0) + (1.0 if b.caption and is_specific(b.caption) else 0)
    s += {"storm": 2.0, "snow": 1.5, "ash": 2.0, "rain": 1.0, "dust": 1.0}.get(env.weather, 0)
    s += {"red": 2.5, "meteors": 2.5, "aurora": 2.0, "dark": 0.5}.get(env.sky, 0)
    s += 2.0 * env.damage + 1.0 * env.overgrown + (1.0 if env.time in ("dusk", "golden", "night") else 0)
    if b.scene == "custom" and env.set:
        objs = env.set.objects
        s += min(2.0, len(objs) / 8) + min(2.0, sum(o.kind == "person" for o in objs) / 3)
    s += 1.0 * len(b.cast)
    n = len(sb.beats)
    s += 1.5 - abs(i / max(1, n - 1) - 0.72) * 3   # 越靠近高潮（~72% 处）越好
    return s


def hero_beat(sb: Storyboard) -> int:
    if sb.thumbnail_beat is not None and 0 <= sb.thumbnail_beat < len(sb.beats):
        return sb.thumbnail_beat
    cands = range(1, len(sb.beats)) if len(sb.beats) > 1 else range(1)
    return max(cands, key=lambda i: beat_score(sb, i))


# ------------------------------------------------------------------ 封面
def clean(text: str) -> str:
    return text.replace("*", "").strip()


def thumb_text(sb: Storyboard) -> str:
    """封面大字：planner 写的 thumbnail 优先；否则从标题里取 2-4 个词（保留 *高亮*）。"""
    if sb.thumbnail.strip():
        return sb.thumbnail.strip().upper()
    src = (sb.intro.title or sb.title).strip()
    src = re.sub(r"^\s*what\s+if\s+", "", src, flags=re.I).rstrip("?!. ")
    words = src.split()
    while words and clean(words[0]).lower() in LEAD_WORDS:
        words.pop(0)
    words = words[:4]
    while len(words) > 1 and clean(words[-1]).lower() in TRAIL_WORDS:
        words.pop()
    text = " ".join(words).upper()
    if "*" not in text and words:   # 没标高亮：最长的实词高亮
        key = max((w for w in words if clean(w).lower() not in STOP), key=len, default=words[-1])
        text = text.replace(key.upper(), f"*{key.upper()}*", 1)
    return text + "?"


def _wrap(draw, words, font, max_w):
    lines, cur = [], []
    for w in words:
        trial = cur + [w]
        if cur and draw.textlength(" ".join(clean(x) for x in trial), font=font) > max_w:
            lines.append(cur)
            cur = [w]
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def compose_thumbnail(still: Path, out: Path, text: str, *, size=(1280, 720), arrow: bool = False) -> Path:
    from PIL import Image, ImageDraw, ImageFont
    W, H = size
    img = Image.open(still).convert("RGB")
    s = max(W / img.width, H / img.height)   # cover 裁切
    img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    img = img.crop(((img.width - W) // 2, (img.height - H) // 2, (img.width - W) // 2 + W, (img.height - H) // 2 + H))
    land = W > H
    # 文字一侧压暗，保证可读
    g = Image.linear_gradient("L").point(lambda v: int(190 * (v / 255) ** 1.4))   # 上=0 → 下=190
    if land:
        g = g.rotate(-90, expand=True).resize((int(W * 0.62), H))   # 左深右浅
    else:
        g = g.transpose(Image.FLIP_TOP_BOTTOM).resize((W, int(H * 0.45)))   # 上深下浅
    shade = Image.new("L", (W, H), 0)
    shade.paste(g, (0, 0))
    img = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), img, shade)
    draw = ImageDraw.Draw(img)
    words = text.split()
    box_w = W * (0.56 if land else 0.88)
    size_px = int(H * (0.2 if land else 0.085))
    while True:   # 字号自适应：最多 3 行
        font = ImageFont.truetype(str(THUMB_FONT), size_px)
        lines = _wrap(draw, words, font, box_w)
        if len(lines) <= 3 or size_px < 40:
            break
        size_px = int(size_px * 0.9)
    lh = int(size_px * 1.02)
    stroke = max(4, size_px // 14)
    x0 = int(W * 0.05)
    y = int(H * 0.5 - lh * len(lines) / 2) if land else int(H * 0.1)
    for ln in lines:
        lw = draw.textlength(" ".join(clean(w) for w in ln), font=font)
        x = x0 if land else int((W - lw) / 2)
        for w in ln:
            hi = w.startswith("*") or w.rstrip("?!.,").endswith("*")
            t = clean(w)
            draw.text((x, y), t, font=font, fill=HIGHLIGHT if hi else (255, 255, 255), stroke_width=stroke, stroke_fill=(0, 0, 0))
            x += draw.textlength(t + " ", font=font)
        y += lh
    if arrow:   # 红色粗箭头指向画面主体
        ax, ay = (int(W * 0.6), int(H * 0.72)) if land else (int(W * 0.3), int(H * 0.38))
        bx, by = (int(W * 0.74), int(H * 0.5)) if land else (int(W * 0.48), int(H * 0.55))
        draw.line([(ax, ay), (bx, by)], fill=(230, 40, 40), width=max(10, W // 70))
        import math
        ang = math.atan2(by - ay, bx - ax)
        L = W // 22
        pts = [(bx + math.cos(ang) * L * 0.6, by + math.sin(ang) * L * 0.6),
               (bx + math.cos(ang + 2.4) * L, by + math.sin(ang + 2.4) * L),
               (bx + math.cos(ang - 2.4) * L, by + math.sin(ang - 2.4) * L)]
        draw.polygon(pts, fill=(230, 40, 40))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=92)
    return out


def thumbnail_storyboard(sb: Storyboard, i: int, *, landscape: bool) -> Storyboard:
    """只含第 i 段画面的单镜分镜：去掉字幕、HUD 和所有叠加层。"""
    env, subj = effective(sb, i)
    b = sb.beats[i].model_copy(update={
        "caption": "", "stat": None, "card": None, "tooltip": None, "banner": None, "screen": None, "callout": None,
        "chip": "", "chapter": None, "time": None, "time_sub": "", "time_label": "", "hud": False, "caption_ref": "",
        "env": env, "subject": subj, "duration": 3.0, "sim_end": None})
    if b.scene == "custom" and env.set and landscape != (sb.width > sb.height):
        zm = env.set.zoom * (0.8 if landscape else 1.35)
        b.env = env.model_copy(update={"set": env.set.model_copy(update={"zoom": round(zm, 2)})})
    fmt = "timeline" if sb.format in ("escalation", "story") else sb.format
    return Storyboard.model_validate({
        "format": fmt, "title": sb.title, "premise": sb.premise, "theme": {**sb.theme.model_dump(), "anchor": "none"},
        "clock": {"mode": "none"}, "intro": {"style": "title", "title": "x", "duration": 0.4},
        "outro": {"chart": False, "question_duration": 0.5}, "beats": [b.model_dump()], "pace": 1.0,
        "width": 1920 if landscape else 1080, "height": 1080 if landscape else 1920})


def thumbnail(sb: Storyboard, out: Path, *, text: Optional[str] = None, landscape: Optional[bool] = None,
              arrow: bool = False, beat: Optional[int] = None) -> Path:
    from .model import compile_plan
    from .render import render_stills
    import shutil
    import tempfile
    land = (sb.width > sb.height) if landscape is None else landscape
    i = hero_beat(sb) if beat is None else beat
    plan = compile_plan(thumbnail_storyboard(sb, i, landscape=land))
    tmp = Path(tempfile.mkdtemp(prefix="whatif-thumb-"))
    try:
        fr = int((plan["beats"][0]["start"] + 1.4) * plan["fps"])
        still = render_stills(plan, tmp, [fr], preview=False)[0]
        return compose_thumbnail(still, out, text or thumb_text(sb), size=(1280, 720) if land else (1080, 1920), arrow=arrow)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ------------------------------------------------------------------ 文案
def _ts(sec: float) -> str:
    sec = int(round(sec))
    return f"{sec // 60}:{sec % 60:02d}" if sec < 3600 else f"{sec // 3600}:{sec // 60 % 60:02d}:{sec % 60:02d}"


def tags_for(sb: Storyboard, n: int = 10) -> List[str]:
    """高亮词（*星号*）和专有名词排前面，其余实词在后。"""
    src = sb.intro.title + " " + sb.title + " " + sb.thumbnail
    star = re.findall(r"\*([^*]+)\*", src)
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", clean(src))
    proper = [w for i, w in enumerate(words) if w[0].isupper() and i and w.lower() not in STOP]
    seen, out = set(), []
    for w in [x for s0 in star for x in s0.split()] + proper + words:
        k = w.lower().strip("'")
        if k in STOP or len(k) < 3 or k in seen:
            continue
        seen.add(k)
        out.append(k)
    base = ["what if", "hypothetical", "simulation", "3d animation"]
    return (out + base)[:n]


def _sentence(text: str, sb: Storyboard) -> str:
    """ALL-CAPS 结尾问题 → 句子大小写，标题里大写的词（USA / Dubai）保持原样。"""
    if not text:
        return ""
    keep = {w.lower(): w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", clean(sb.title)) if w[0].isupper()}
    words = [keep.get(w.lower(), w.lower()) for w in text.split()]
    out = " ".join(words)
    return out[0].upper() + out[1:]


def metadata(sb: Storyboard, plan: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    from .model import compile_plan
    plan = plan or compile_plan(sb)
    vertical = sb.height > sb.width
    title = clean(sb.title)
    if not title.endswith("?"):
        title = title.rstrip(".!") + "?"
    caps = [b.caption for b in sb.beats if b.caption]
    hook = caps[0] if caps else ""
    tease = next((c for c in caps[1:4] if "?" in c or re.search(r"\b(but|until|worst|then)\b", c, re.I)), "")
    chapters = []
    if not vertical:
        last = None
        for pb, b in zip(plan["beats"], sb.beats):
            if b.chapter and b.chapter != last:
                chapters.append((0.0 if not chapters else pb["start"], b.chapter))
                last = b.chapter
    end = sb.outro.end
    if end and end.kind == "question" and end.lines:
        question = " ".join(end.lines)
    elif end is None or end.kind == "question":
        question = sb.outro.question
    else:
        question = "What would you do first if this really happened?"
    tags = tags_for(sb)
    hashtags = ["#whatif"] + [f"#{t.replace(' ', '')}" for t in tags[:2] if t not in ("what if",)] + ["#simulation"] + (["#shorts"] if vertical else [])
    desc = [hook + (" " + tease if tease else "")]
    desc.append("")
    desc.append(clean(sb.premise) if len(sb.premise) < 400 else clean(sb.premise)[:397] + "...")
    desc.append("")
    desc.append("A hypothetical 3D simulation. Facts on screen are widely cited; the consequences are speculative.")
    if chapters:
        desc += ["", "CHAPTERS"] + [f"{_ts(t)} {c}" for t, c in chapters]
    desc += ["", " ".join(dict.fromkeys(hashtags))]
    return {"title": title[:100], "description": "\n".join(desc).strip(), "tags": tags, "hashtags": list(dict.fromkeys(hashtags)),
            "chapters": [{"t": round(t, 1), "title": c} for t, c in chapters], "pinned_comment": _sentence(question, sb),
            "duration": round(plan["duration"], 1)}


def metadata_text(meta: Dict[str, Any]) -> str:
    parts = ["TITLE", meta["title"], "", "DESCRIPTION", meta["description"], "", "TAGS", ", ".join(meta["tags"])]
    if meta.get("pinned_comment"):
        parts += ["", "PINNED COMMENT", meta["pinned_comment"]]
    return "\n".join(parts) + "\n"


# ------------------------------------------------------------------ 短版
def make_short(sb: Storyboard, *, target: float = SHORT_TARGET) -> Storyboard:
    """横屏长视频 → 竖屏短版：保留开头和结尾，中间按信息量挑段，按节奏压缩后凑够 target 秒。"""
    from .model import compile_plan
    pace = sb.pace or 1.8
    n = len(sb.beats)
    must = {0, max(i for i, b in enumerate(sb.beats) if b.caption) if any(b.caption for b in sb.beats) else n - 1}
    order = sorted((i for i in range(n) if i not in must), key=lambda i: -beat_score(sb, i))
    chosen = set(must)

    def build(ids) -> Storyboard:
        beats = []
        for i in sorted(ids):
            env, subj = effective(sb, i)
            b = sb.beats[i].model_copy(update={"env": env, "subject": subj, "narration": None, "sim_end": None})
            if b.scene == "custom" and env.set and sb.width > sb.height:
                b.env = env.model_copy(update={"set": env.set.model_copy(update={"zoom": round(env.set.zoom * 1.35, 2)})})
            beats.append(b.model_dump())
        if beats and beats[0].get("caption") and len(beats) > 1:
            beats[0]["caption"] = ""   # 第一镜压在标题下，不放字幕
        d = sb.model_dump()
        d.update({"beats": beats, "width": 1080, "height": 1920, "narration": None, "pace": pace})
        d["intro"]["duration"] = min(d["intro"]["duration"], 2.6)
        if d["format"] == "escalation":
            sims, sim = [], 0.0
            for i in sorted(ids):   # 增长型：保留原模拟时间
                b0 = sb.beats[i]
                sim = b0.sim_end if b0.sim_end is not None else sim + b0.duration
                sims.append(sim)
            for b, s in zip(d["beats"], sims):
                b["sim_end"] = s
        return Storyboard.model_validate(d)

    cur = build(chosen)
    for i in order:
        if compile_plan(cur)["duration"] >= target:
            break
        chosen.add(i)
        cur = build(chosen)
    return cur
