"""
数值引擎：把 Storyboard 编译成逐帧的渲染计划（plan）。

- 增长模型 → 任意模拟时刻的数值、积分（速度 → 距离）
- 里程碑越过的时刻 → 自动弹出标注 + 结尾图表参考线
- 每帧的 HUD 文本、字幕、卡片、透明度，全部在这里算好；网页端只负责画
- 声音事件（tick / whoosh / boom ...）与每帧的环境强度，供 audio.py 合成

所有画面上的数字都出自这里，文案里的数字通过占位符引用这里的结果。
"""
from __future__ import annotations

import bisect
import math
import re
import string
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .schema import STYLE_CAPTIONS, Beat, GrowthModel, Milestone, Quantity, Storyboard, Subject

SPEED_OF_SOUND = 343.0          # m/s，海平面 20°C
SPEED_OF_LIGHT = 299_792_458.0  # m/s

ACTION_SPEED = {"idle": 0.0, "walk": 1.4, "run": 4.0, "sprint": 8.0, "float": 0.6, "fly": 14.0}
ACTION_STRIDE = {"idle": 0.0, "walk": 1.0, "run": 1.5, "sprint": 2.0, "float": 0.25, "fly": 0.0}

MILESTONE_HOLD = 2.6   # 里程碑标注至少停留多少秒（视频时间）
FADE = 0.22


# ------------------------------------------------------------------ growth ---
class Growth:
    """数值曲线 + 累积积分表。"""

    def __init__(self, m: GrowthModel, sim_max: float):
        self.m = m
        self.sim_max = max(sim_max, m.step)
        self.dt = m.step / max(200, math.ceil(m.step / 0.005))
        n = int(math.ceil(self.sim_max / self.dt)) + 2
        self._cum = [0.0] * n
        acc = 0.0
        for i in range(1, n):
            # 中点法：网格对齐增长步长，阶梯函数积分是精确的
            acc += self.value((i - 0.5) * self.dt) * self.dt
            self._cum[i] = acc

    def value(self, t: float) -> float:
        m = self.m
        t = max(0.0, t)
        if m.type == "keyframes":
            pts = sorted(m.points)
            if t <= pts[0][0]:
                return pts[0][1]
            for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
                if t <= t1:
                    if m.discrete:
                        return v0
                    f = (t - t0) / (t1 - t0) if t1 > t0 else 1.0
                    if v0 > 0 and v1 > 0 and max(v0, v1) / min(v0, v1) > 50:
                        return v0 * (v1 / v0) ** f  # 跨数量级的关键帧按对数插值
                    return v0 + (v1 - v0) * f
            return pts[-1][1]
        steps = math.floor(t / m.step + 1e-9) if m.discrete else t / m.step
        if m.type == "exponential":
            try:
                return m.start * m.factor ** steps
            except OverflowError:
                return float("inf")
        return m.start + m.rate * m.step * steps

    def integral(self, t: float) -> float:
        t = min(max(0.0, t), self.sim_max)
        x = t / self.dt
        i = int(x)
        if i + 1 >= len(self._cum):
            return self._cum[-1]
        return self._cum[i] + (self._cum[i + 1] - self._cum[i]) * (x - i)

    def crossing(self, threshold: float) -> Optional[float]:
        """数值第一次 >= threshold 的模拟时刻；在 sim_max 内没越过返回 None。"""
        if self.value(0) >= threshold:
            return 0.0
        m = self.m
        if m.discrete and m.type in ("exponential", "linear"):
            k = 0
            while k * m.step <= self.sim_max + 1e-9:
                if self.value(k * m.step + 1e-9) >= threshold:
                    return k * m.step
                k += 1
            return None
        lo, hi = 0.0, self.sim_max
        if self.value(hi) < threshold:
            return None
        for _ in range(60):
            mid = (lo + hi) / 2
            if self.value(mid) >= threshold:
                hi = mid
            else:
                lo = mid
        return hi


# -------------------------------------------------------------- formatting ---
_SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")


def fmt_num(v: float, max_dec: int = 2) -> str:
    if v is None or math.isnan(v):
        return "—"
    if math.isinf(v):
        return "∞"
    a = abs(v)
    if a >= 1e15:
        e = int(math.floor(math.log10(a)))
        mant = v / 10 ** e
        return f"{mant:.2f} × 10{str(e).translate(_SUP)}"
    if a >= 100 or float(v).is_integer():
        return f"{v:,.0f}"
    if a >= 10:
        return f"{v:,.1f}".rstrip("0").rstrip(".")
    if a == 0:
        return "0"
    dec = max_dec if a >= 0.01 else 4
    return f"{v:.{dec}f}".rstrip("0").rstrip(".")


def fmt_sig(v: float, sig: int = 2) -> str:
    if v == 0:
        return "0"
    d = max(0, sig - int(math.floor(math.log10(abs(v)))) - 1)
    return f"{v:,.{d}f}"


def fmt_distance(m: float) -> str:
    if m < 1000:
        return f"{m:,.0f} m"
    km = m / 1000
    if km < 10:
        return f"{km:.2f} km"
    if km < 100:
        return f"{km:.1f} km"
    return f"{fmt_num(round(km))} km"


def fmt_length(m: float) -> Tuple[str, str]:
    if m < 0.01:
        return fmt_num(m * 1000), "mm"
    if m < 1:
        return fmt_num(m * 100), "cm"
    if m < 1000:
        return fmt_num(m), "m"
    return fmt_num(m / 1000), "km"


def fmt_time(sim: float) -> str:
    sim = max(0.0, sim)
    mm = int(sim // 60)
    ss = sim - mm * 60
    return f"{mm:02d}:{ss:05.2f}"


def rate_tag(rate: float) -> Tuple[str, str]:
    """(文字, 样式)；rate = 模拟时间 / 视频时间。"""
    if rate <= 0.001:
        return "TIME FROZEN", "slow"
    if rate < 0.93:
        f = 1 / rate
        return f"SLOW MOTION ×{fmt_num(round(f, 1) if f < 10 else round(f))}", "slow"
    if rate > 1.08:
        return f"TIME-LAPSE ×{fmt_num(round(rate, 1) if rate < 10 else round(rate))}", "fast"
    return "REAL TIME", "real"


@dataclass
class HudText:
    head: str
    value: str
    unit: str
    sub: str
    over_limit: bool = False


def hud_for(q: Quantity, v: float, sim: float) -> HudText:
    step_no = int(math.floor(sim / q.model.step + 1e-9)) + 1 if q.model.discrete else None
    head = f"SECOND {step_no}" if (step_no and q.model.step == 1.0) else (
        f"STEP {step_no}" if step_no else q.label)
    over = bool(q.limit and v > q.limit.value)
    if q.kind == "speed":
        parts = [f"{fmt_num(round(v * 3.6) if v * 3.6 >= 10 else v * 3.6)} km/h"]
        mach = v / SPEED_OF_SOUND
        if mach >= 0.3:
            parts.append(f"MACH {fmt_num(round(mach, 1) if mach < 10 else round(mach))}")
        frac = v / SPEED_OF_LIGHT
        if frac >= 1e-3:
            pct = frac * 100
            parts.append(f"{fmt_sig(pct, 2)}% OF LIGHT SPEED" + (" · IMPOSSIBLE" if v > SPEED_OF_LIGHT else ""))
        return HudText(head, fmt_num(v), q.unit, " · ".join(parts), over)
    if q.kind == "length":
        val, unit = fmt_length(v)
        ft = v * 3.28084
        return HudText(head, val, unit, f"{fmt_num(round(ft) if ft >= 10 else ft)} ft", over)
    if q.kind == "mass":
        if v >= 1000:
            return HudText(head, fmt_num(v / 1000), "t", f"{fmt_num(round(v * 2.20462))} lb", over)
        return HudText(head, fmt_num(v), "kg", f"{fmt_num(round(v * 2.20462, 1))} lb", over)
    if q.kind == "temperature":
        f = v * 9 / 5 + 32
        return HudText(head, fmt_num(v), q.unit or "°C", f"{fmt_num(round(f))} °F", over)
    scale = v / q.model.start if q.model.start else 0
    return HudText(head, fmt_num(v), q.unit, f"×{fmt_num(scale)} THE START" if scale >= 2 else "", over)


# ----------------------------------------------------------- placeholders ---
PLACEHOLDERS = ("value", "value_start", "sim_end", "kmh", "mach", "light_pct", "distance", "scale", "unit")


def placeholder_values(q: Quantity, g: Growth, sim0: float, sim1: float) -> Dict[str, str]:
    v1, v0 = g.value(sim1 - 1e-6 if sim1 > sim0 else sim1), g.value(sim0)
    h1, h0 = hud_for(q, v1, sim1), hud_for(q, v0, sim0)
    d = {
        "value": f"{h1.value} {h1.unit}".strip(),
        "value_start": f"{h0.value} {h0.unit}".strip(),
        "sim_end": fmt_num(round(sim1, 2)),
        "unit": q.unit,
        "scale": fmt_num(v1 / q.model.start) if q.model.start else "—",
        "kmh": fmt_num(round(v1 * 3.6)),
        "mach": fmt_num(round(v1 / SPEED_OF_SOUND, 1)),
        "light_pct": fmt_sig(v1 / SPEED_OF_LIGHT * 100, 2),
        "distance": fmt_distance(g.integral(sim1)),
    }
    return d


def placeholders_in(text: str) -> List[str]:
    return [f for _, f, _, _ in string.Formatter().parse(text) if f]


def fill(text: str, values: Dict[str, str]) -> str:
    if not text or "{" not in text:
        return text
    return text.format_map(values)


# ----------------------------------------------------------------- compile ---
@dataclass
class Section:
    kind: str           # beat / chart / question
    start: float
    duration: float
    beat: Optional[Beat] = None
    index: int = -1
    sim0: float = 0.0
    sim1: float = 0.0
    subject: Optional[Subject] = None


class PlanError(ValueError):
    pass


def _sections(sb: Storyboard) -> List[Section]:
    out: List[Section] = []
    t = 0.0
    sim = 0.0
    subj = sb.beats[0].subject
    for i, b in enumerate(sb.beats):
        end = b.sim_end if b.sim_end is not None else sim + b.duration
        subj = b.subject or subj
        out.append(Section("beat", t, b.duration, b, i, sim, end, subj))
        t += b.duration
        sim = end
    if sb.outro.chart:
        out.append(Section("chart", t, sb.outro.chart_duration, sim0=sim, sim1=sim))
        t += sb.outro.chart_duration
    if sb.outro.question or sb.outro.end:
        out.append(Section("question", t, sb.outro.question_duration, sim0=sim, sim1=sim))
    return out


def _no_quantity() -> Quantity:
    return Quantity(kind="generic", label="", unit="",
                    model=GrowthModel(type="linear", start=0, rate=0, step=1, discrete=False))


FORMAT_CLOCK = {"timeline": "elapsed", "countdown": "countdown", "survival": "stopwatch", "story": "time_of_day"}


def validate(sb: Storyboard) -> List[str]:
    """语义检查（结构检查由 pydantic 完成）。返回问题列表，空 = 通过。"""
    problems: List[str] = []
    q = sb.quantity
    for i, b in enumerate(sb.beats):
        texts = [("caption", b.caption)]
        if b.card:
            texts += [("card", b.card.title)] + [("card", x) for row in b.card.rows for x in row]
        for field, text in texts:
            for ph in placeholders_in(text):
                if q is None:
                    problems.append(f"beats[{i}].{field} 用了占位符 {{{ph}}}，但这个分镜没有 quantity；直接写文字")
                elif ph not in PLACEHOLDERS:
                    problems.append(f"beats[{i}].{field} 用了未知占位符 {{{ph}}}；可用：{', '.join(PLACEHOLDERS)}")
        if q is not None and re.search(r"\d", b.caption) and q.kind == "speed":
            # 文案里的计算型数字必须走占位符；允许"seconds"之类的小整数叙述
            nums = [n for n in re.findall(r"\d[\d,\.]*", re.sub(r"\{[^}]*\}", "", b.caption))]
            big = [n for n in nums if float(n.replace(",", "") or 0) >= 100]
            if big:
                problems.append(f"beats[{i}].caption 里有写死的数字 {big}；请用 {{value}}/{{kmh}}/{{distance}} 等占位符")
        mode = sb.clock.mode if sb.clock else None
        if mode in ("countdown", "stopwatch") and b.time is not None and isinstance(b.time, str) is False:
            a, z = b.time
            if mode == "countdown" and z > a + 1e-9:
                problems.append(f"beats[{i}].time 倒计时应递减（{a} → {z}）")
            if mode == "stopwatch" and z < a - 1e-9:
                problems.append(f"beats[{i}].time 秒表应递增（{a} → {z}）")
        if mode in ("elapsed", "time_of_day") and b.time is not None and not isinstance(b.time, str):
            problems.append(f"beats[{i}].time 在 clock.mode={mode} 下应是文字标签（如 \"+1 HOUR\"）")
        if b.scene == "globe" and b.env and b.env.map:
            problems.append(f"beats[{i}] scene=globe 不用 env.map")
        if b.scene == "custom" and not (b.env and b.env.set):
            problems.append(f"beats[{i}] scene=custom 需要 env.set（背景 / 地面 / objects）")
        if b.env and b.env.set:
            n_obj = sum(o.count for o in b.env.set.objects if o.kind != "particles")
            if n_obj > 260:
                problems.append(f"beats[{i}] 自定义布景物体太多（{n_obj} > 260），会拖慢渲染")
        if b.scene == "map" and not (b.env and b.env.map):
            problems.append(f"beats[{i}] scene=map 需要 env.map（labels/path/zone）")
    if sb.format in ("timeline", "countdown", "survival") and (sb.clock is None or sb.clock.mode == "none"):
        problems.append(f"format={sb.format} 需要 clock（mode 建议 {FORMAT_CLOCK[sb.format]}）")
    if sb.format in ("timeline", "countdown", "survival") and sb.beats[0].time is None and len(sb.beats) > 1 \
            and all(b.time is None for b in sb.beats):
        problems.append("每段都没有 time；时钟会是空的")
    if sb.format == "story" and not any(b.chapter for b in sb.beats):
        problems.append("format=story 需要用 chapter 给段落分章")
    total = sum(b.duration for b in sb.beats) + (sb.outro.chart_duration if sb.outro.chart else 0) + (
        sb.outro.question_duration if (sb.outro.question or sb.outro.end) else 0)
    limit = 900 if sb.width > sb.height else 180   # 横屏 = YouTube 长视频
    if total > limit:
        problems.append(f"总时长 {total:.0f}s 太长（上限 {limit}s）")
    if q is not None:
        g = Growth(q.model, max(s.sim1 for s in _sections(sb)))
        for m in q.milestones:
            if g.crossing(m.value) is None:
                problems.append(f"里程碑「{m.label}」({m.value}) 在模拟时间内不会被越过；删掉它或延长模拟")
    return problems


_NUM_RE = re.compile(r"^(?P<pre>[^\d]*)(?P<num>\d[\d,]*(?:\.\d+)?)(?P<post>.*)$")


def count_up(value: str, k: float) -> str:
    """"90%" → 在 k∈[0,1] 时显示 "0%"…"90%"；不含数字的原样返回。保留千分位与小数位数。"""
    m = _NUM_RE.match(value.strip())
    if not m or k >= 1:
        return value
    raw = m.group("num")
    target = float(raw.replace(",", ""))
    dec = len(raw.split(".")[1]) if "." in raw else 0
    cur = target * (1 - (1 - k) ** 3)
    body = f"{cur:,.{dec}f}" if "," in raw else f"{cur:.{dec}f}"
    return f"{m.group('pre')}{body}{m.group('post')}"


def fmt_clock(sec: float, mode: str) -> str:
    sec = max(0.0, sec)
    if mode == "countdown":
        mm = int(sec // 60)
        return f"{mm}:{sec - mm * 60:06.3f}"
    h = int(sec // 3600)
    mm = int((sec - h * 3600) // 60)
    ss = int(sec - h * 3600 - mm * 60)
    return f"{h}:{mm:02d}:{ss:02d}"


def lightning_times(beat_index: int, duration: float) -> List[float]:
    """风暴段内闪电的时刻（确定性：画面闪光与雷声同源）。"""
    out, t = [], 0.6 + (beat_index * 0.37) % 1.0
    while t < duration - 0.3:
        out.append(round(t, 3))
        t += 1.7 + ((beat_index * 7 + len(out) * 3) % 5) * 0.35
    return out


def lightning(beat_index: int, lt: float) -> float:
    for t0 in lightning_times(beat_index, lt + 1):
        d = lt - t0
        if 0 <= d < 0.25:
            return (1 - d / 0.25) * (1 if d < 0.06 or 0.1 < d < 0.14 else 0.4)
    return 0.0


def _style_sfx(sb: Storyboard, secs) -> List[Dict[str, Any]]:
    """风格附带的转场音效：bold / retro 每次切镜一个 whoosh。"""
    if sb.theme.style not in ("bold", "retro"):
        return []
    gain = 0.45 if sb.theme.style == "bold" else 0.3
    return [{"type": "whoosh", "t": s.start, "gain": gain} for s in secs if s.kind == "beat" and s.start > 0.5]


def readable_seconds(caption: Optional[str]) -> float:
    """字幕至少要停留这么久才读得完（快节奏下的下限）。"""
    return 1.2 if not caption else 0.8 + 0.028 * len(caption)


def apply_pace(sb: Storyboard) -> Storyboard:
    """按 sb.pace 压缩时长：每镜 ÷ pace，但不短于字幕可读下限；片头 ÷ pace（≥1.6s），结尾卡保持可读。"""
    pace = sb.pace or 1.0
    if abs(pace - 1.0) < 1e-6:
        return sb
    out = sb.model_copy(deep=True)
    sim = 0.0
    for b in out.beats:
        sim = b.sim_end if b.sim_end is not None else sim + b.duration
        b.sim_end = sim          # 模拟时间不随节奏变（数字、里程碑保持原样），只是放得更快
        b.duration = round(max(b.duration / pace, readable_seconds(b.caption), 0.8), 3)
    out.intro.duration = round(max(1.6, out.intro.duration / pace), 3)
    out.outro.question_duration = round(max(2.2, out.outro.question_duration / max(1.0, pace * 0.75)), 3)
    return out


def compile_plan(sb: Storyboard) -> Dict[str, Any]:
    from .schema import Env
    pace = sb.pace or 1.0
    sb = apply_pace(sb)
    has_q = sb.quantity is not None
    q = sb.quantity or _no_quantity()
    secs = _sections(sb)
    sim_total = max(s.sim1 for s in secs)
    g = Growth(q.model, sim_total + q.model.step)
    total = secs[-1].start + secs[-1].duration
    fps = sb.fps
    n_frames = int(round(total * fps))
    beat_secs = [s for s in secs if s.kind == "beat"]
    clock = sb.clock if (sb.clock and sb.clock.mode != "none") else None

    def sim_to_video(sim: float) -> Optional[float]:
        for s in beat_secs:
            if s.sim0 - 1e-9 <= sim <= s.sim1 + 1e-9:
                if s.sim1 - s.sim0 < 1e-9:
                    return s.start
                return s.start + (sim - s.sim0) / (s.sim1 - s.sim0) * s.duration
        return None

    # 里程碑弹出时间表（排队，不重叠）
    pops: List[Dict[str, Any]] = []
    t_free = sb.intro.duration
    for m in sorted(q.milestones, key=lambda m: m.value):
        c = g.crossing(m.value)
        if c is None:
            continue
        tv = sim_to_video(c)
        if tv is None:
            continue
        t0 = max(tv, t_free)
        if t0 >= beat_secs[-1].start + beat_secs[-1].duration:
            continue
        pops.append({"t0": t0, "t1": t0 + MILESTONE_HOLD, "title": m.label, "sub": m.detail, "sim": c})
        t_free = t0 + MILESTONE_HOLD

    # 章节：按首次出现顺序编号，未写 chapter 的段沿用上一段
    chapters: List[str] = []
    beat_chapter: List[Optional[int]] = []
    cur_ch: Optional[int] = None
    for s in beat_secs:
        if s.beat.chapter:
            if not chapters or chapters[-1] != s.beat.chapter:
                chapters.append(s.beat.chapter)
            cur_ch = len(chapters) - 1
        beat_chapter.append(cur_ch)

    beats_out = []
    env = Env()
    prev_scene_b = None
    clock_val: Any = None
    chip = ""
    for s in beat_secs:
        b = s.beat
        ph = placeholder_values(q, g, s.sim0, s.sim1) if has_q else {}
        try:
            caption = fill(b.caption, ph)
        except (KeyError, IndexError, ValueError) as e:
            raise PlanError(f"beats[{s.index}].caption 占位符错误: {e}") from e
        subj = s.subject or Subject()
        if b.env is not None:
            env = b.env
        elif b.scene != prev_scene_b:
            env = Env()
        prev_scene_b = b.scene
        # 时钟值：没写就沿用上一段的结束值
        if b.time is not None:
            clock_val = b.time
        elif isinstance(clock_val, (list, tuple)):
            clock_val = (clock_val[1], clock_val[1])
        ch_i = beat_chapter[s.index]
        if b.chip:
            chip = b.chip
        elif b.chapter:
            chip = ""
        beats_out.append({
            "i": s.index, "start": s.start, "duration": s.duration,
            "scene": b.scene, "camera": b.camera, "effects": list(b.effects),
            "subject": subj.model_dump(), "caption": caption, "caption_ref": b.caption_ref,
            "callout": b.callout.model_dump() if b.callout else None,
            "card": ({"title": fill(b.card.title, ph), "rows": [[fill(k, ph), fill(v, ph)] for k, v in b.card.rows],
                      "tone": b.card.tone} if b.card else None),
            "hud": b.hud, "sim0": s.sim0, "sim1": s.sim1,
            "env": env.model_dump(), "cast": [c.model_dump() for c in b.cast],
            "time": list(clock_val) if isinstance(clock_val, (list, tuple)) else clock_val,
            "time_sub": b.time_sub, "stat": b.stat.model_dump() if b.stat else None,
            "chapter": ch_i, "chip": chip,
            "tooltip": b.tooltip.model_dump() if b.tooltip else None,
            "banner": b.banner.model_dump() if b.banner else None,
            "screen": b.screen.model_dump() if b.screen else None,
            "narration": fill(b.narration, ph) if b.narration is not None else None,
        })

    frames: List[Dict[str, Any]] = []
    audio_events: List[Dict[str, Any]] = []
    z = 0.0
    phase = 0.0
    prev_scene = None
    prev_step = None
    prev_clock_int = None
    sec_starts = [s.start for s in secs]
    intro = sb.intro
    for fi in range(n_frames):
        t = fi / fps
        si = max(0, bisect.bisect_right(sec_starts, t) - 1)
        s = secs[si]
        lt = t - s.start
        fr: Dict[str, Any] = {"t": round(t, 4), "sec": s.kind}
        if s.kind == "beat":
            b = s.beat
            bo = beats_out[s.index]
            subj = s.subject or Subject()
            frac = lt / s.duration
            sim = s.sim0 + (s.sim1 - s.sim0) * frac
            v = g.value(sim)
            if b.scene != prev_scene:
                z = 0.0
                prev_scene = b.scene
            if subj.type == "none":
                vis = 0.0
            elif has_q and q.kind == "speed" and subj.action not in ("idle", "float"):
                vv = max(v, 0.0)
                vis = vv * 1.4 if vv <= 6 else 8.4 + 22 * math.log10(vv / 6)
                vis = min(vis, 160.0)
            else:
                vis = ACTION_SPEED.get(subj.action, 0.0)
            z += vis / fps
            stride = ACTION_STRIDE.get(subj.action, 0.0) * (1 + min(2.0, vis / 40))
            phase += 2 * math.pi * 1.55 * stride / fps
            scale = subj.scale
            if has_q and subj.scale_with_value and q.model.start:
                scale = subj.scale * (v / 1.75 if q.kind == "length" else v / q.model.start)
            in_intro = t < intro.duration
            fr.update({
                "b": s.index, "lt": round(lt, 4), "frac": round(frac, 5), "sim": round(sim, 5),
                "z": round(z, 4), "vis": round(vis, 3), "scale": scale,
                "stride": round(stride, 4), "ph": round(phase, 4),
            })
            if has_q and b.hud and not in_intro:
                rate = (s.sim1 - s.sim0) / s.duration
                tag, tag_style = rate_tag(rate)
                h = hud_for(q, v, sim)
                right = [["TIME", fmt_time(sim)]]
                if q.kind == "speed":
                    right.append(["DISTANCE", fmt_distance(g.integral(sim))])
                if b.altitude:
                    a0, a1 = b.altitude
                    right.append(["ALTITUDE", fmt_distance(a0 + (a1 - a0) * frac)])
                hud = {"head": h.head, "value": h.value, "unit": h.unit, "sub": h.sub,
                       "over": h.over_limit, "right": right, "tag": tag, "tag_style": tag_style}
                if q.limit and v >= q.limit.value * 1e-3:
                    hud["bar"] = {"label": f"{q.limit.label}: {fmt_num(q.limit.value)} {q.unit}",
                                  "frac": min(1.0, v / q.limit.value)}
                fr["hud"] = hud
                # 每跨一个增长步，HUD 跳一下 → tick
                step_no = math.floor(sim / q.model.step + 1e-9)
                if prev_step is not None and step_no != prev_step:
                    audio_events.append({"type": "tick", "t": t, "gain": 0.5})
                prev_step = step_no
            fr["intensity"] = round(min(1.0, vis / 120.0), 4)
            fr["scene"] = b.scene
            fade = max(0.0, min(1.0, lt / FADE, (s.duration - lt) / FADE))

            # 片头
            if in_intro:
                a = 1.0 if t < intro.duration - 0.4 else max(0.0, (intro.duration - t) / 0.4)
                fr["intro"] = {"style": intro.style, "lines": intro.lines, "accent": intro.accent,
                               "title": intro.title, "kicker": intro.kicker, "subtitle": intro.subtitle,
                               "icon": intro.icon, "a": round(a, 3)}
            # 时钟
            if clock and b.hud:
                if in_intro and clock.intro_from is not None:
                    left = clock.intro_from - t
                    fr["clock"] = {"label": clock.intro_label, "value": fmt_clock(left, "countdown"), "sub": "", "a": 1.0}
                    ci = int(math.ceil(left))
                    if prev_clock_int is not None and ci != prev_clock_int:
                        audio_events.append({"type": "beep", "t": t, "gain": 0.35})
                    prev_clock_int = ci
                elif not in_intro and bo["time"] is not None:
                    tv = bo["time"]
                    if isinstance(tv, list):
                        cur = tv[0] + (tv[1] - tv[0]) * frac
                        val = fmt_clock(cur, clock.mode if clock.mode in ("countdown", "stopwatch") else "stopwatch")
                        if clock.mode == "countdown":
                            ci = int(math.ceil(cur - 1e-9))
                            if prev_clock_int is not None and ci != prev_clock_int:
                                audio_events.append({"type": "beep", "t": t, "gain": 0.35})
                            prev_clock_int = ci
                    else:
                        val = str(tv)
                    prev_b = beats_out[s.index - 1] if s.index > 0 else None
                    changed = prev_b is None or prev_b["time"] != tv or isinstance(tv, list)
                    ca = 1.0 if not changed or isinstance(tv, list) else min(1.0, lt / 0.3)
                    fr["clock"] = {"label": clock.label, "value": val, "sub": b.time_sub, "a": round(ca, 3)}
            # 统计大字
            if bo["stat"] and not in_intro:
                st = bo["stat"]
                k = min(1.0, max(0.0, (lt - 0.15) / 0.9))
                val = count_up(st["value"], k) if st.get("count_up", True) else st["value"]
                fr["stat"] = {"value": val, "label": st["label"], "a": round(min(1.0, lt / 0.3, (s.duration - lt) / FADE), 3)}
            # 章节
            if chapters and bo["chapter"] is not None and not in_intro:
                ci = bo["chapter"]
                fr["chapter"] = {"i": ci, "n": len(chapters), "title": chapters[ci]}
                if bo["chip"]:
                    fr["chip"] = bo["chip"]
            elif bo["chip"] and not in_intro:
                fr["chip"] = bo["chip"]
            if bo["tooltip"] and not in_intro:
                ta = max(0.0, min(1.0, (lt - 0.4) / 0.3, (s.duration - lt) / FADE))
                fr["tooltip"] = {**bo["tooltip"], "a": round(ta, 3)}
            if bo["banner"] and not in_intro:
                fr["banner"] = {**bo["banner"], "a": round(min(1.0, lt / 0.25, (s.duration - lt) / FADE), 3),
                                "slide": round(min(1.0, lt / 0.35), 3)}
            if bo["screen"] and not in_intro:
                fr["screen"] = {**bo["screen"], "a": round(min(1.0, lt / 0.3, (s.duration - lt) / FADE), 3), "lt": round(lt, 3)}

            cap = bo["caption"]
            if cap and not in_intro:
                # k：逐词字幕的显示进度（前 ~65% 时间里逐词出现，之后整句停留）
                fr["cap"] = {"text": cap, "a": round(fade, 3), "ref": bo["caption_ref"],
                             "k": round(min(1.0, lt / max(0.6, s.duration * 0.65)), 4)}
            pop = next((p for p in pops if p["t0"] <= t < p["t1"]), None)
            if pop:
                pa = min(1.0, (t - pop["t0"]) / FADE, (pop["t1"] - t) / FADE)
                fr["callout"] = {"title": pop["title"], "sub": pop["sub"], "a": round(max(0, pa), 3), "kind": "milestone"}
            elif b.callout and not in_intro:
                fr["callout"] = {"title": b.callout.title, "sub": b.callout.subtitle, "a": round(fade, 3), "kind": "note"}
            if b.card:
                card = bo["card"]
                fr["card"] = {**card,
                              "a": round(min(1.0, lt / 0.35, (s.duration - lt) / FADE), 3)}
            if "flash" in b.effects and lt < 0.5:
                fr["flash"] = round(1 - lt / 0.5, 3)
            if "darken" in b.effects:
                fr["darken"] = round(min(1.0, max(0.0, (frac - 0.4) / 0.6)), 3)
            env_d = bo["env"]
            if env_d.get("weather") == "storm":
                li = lightning(s.index, lt)
                if li > 0:
                    fr["lightning"] = round(li, 3)
            if b.scene == "map" and env_d.get("map"):
                fr["map"] = {**env_d["map"], "p": round(frac, 4), "t": round(lt, 3)}
        elif s.kind == "chart":
            prog = min(1.0, lt / max(0.1, s.duration * 0.75))
            fr["chart"] = {"p": round(prog, 4), "a": round(min(1.0, lt / 0.4), 3)}
            caps = sb.outro.chart_captions
            if caps:
                k = min(len(caps) - 1, int(lt / (s.duration / len(caps))))
                seg = s.duration / len(caps)
                ll = lt - k * seg
                fr["cap"] = {"text": caps[k], "a": round(max(0.0, min(1.0, ll / FADE, (seg - ll) / FADE)), 3)}
            fr["scene"] = "void"
            fr["intensity"] = 0.0
        else:
            a = round(min(1.0, lt / 0.5), 3)
            end = sb.outro.end
            if end is None:
                fr["end"] = {"kind": "question", "kicker": "", "lines": [sb.outro.question], "accent_line": -1,
                             "sub": "", "a": a, "icon": intro.icon}
            else:
                fr["end"] = {**end.model_dump(), "a": a, "icon": intro.icon,
                             "title": intro.title if end.kind == "title" else ""}
            fr["scene"] = "void"
            fr["intensity"] = 0.0
        frames.append(fr)

    # 声音事件：段落 sfx + 效果/界面自动配声 + 里程碑 whoosh
    prev_ch = None
    for s in beat_secs:
        b = s.beat
        bo = beats_out[s.index]
        for x in b.sfx:
            audio_events.append({"type": x.type, "t": s.start + x.at, "gain": x.gain})
        if "shockwave" in b.effects or "vapor_cone" in b.effects:
            audio_events.append({"type": "boom", "t": s.start + 0.05, "gain": 1.0})
        if "flash" in b.effects:
            audio_events.append({"type": "impact", "t": s.start, "gain": 0.8})
        if "earthquake" in b.effects:
            audio_events.append({"type": "rumble", "t": s.start, "gain": 0.9, "dur": s.duration})
        if b.card:
            audio_events.append({"type": "swell", "t": s.start, "gain": 0.7})
        if b.stat:
            audio_events.append({"type": "whoosh", "t": s.start + 0.1, "gain": 0.3})
        if b.banner:
            audio_events.append({"type": "impact", "t": s.start, "gain": 0.5})
        if b.screen and b.screen.kind == "phone_call":
            for k in range(int(s.duration / 1.6) + 1):
                audio_events.append({"type": "ring", "t": s.start + 0.2 + k * 1.6, "gain": 0.6})
        if b.screen and b.screen.kind == "vitals":
            for k in range(int(s.duration / 0.55)):
                audio_events.append({"type": "beep", "t": s.start + 0.1 + k * 0.55, "gain": 0.25})
        if bo["chapter"] is not None and bo["chapter"] != prev_ch and s.index > 0:
            audio_events.append({"type": "whoosh", "t": s.start, "gain": 0.4})
        prev_ch = bo["chapter"]
        if clock and clock.mode == "elapsed" and isinstance(bo["time"], str) and s.index > 0 \
                and beats_out[s.index - 1]["time"] != bo["time"]:
            audio_events.append({"type": "tick", "t": s.start, "gain": 0.45})
        if bo["env"].get("weather") == "storm":
            for k0 in lightning_times(s.index, s.duration):
                audio_events.append({"type": "thunder", "t": s.start + k0 + 0.35, "gain": 0.8})
    for p in pops:
        audio_events.append({"type": "whoosh", "t": p["t0"], "gain": 0.55})
    if sb.outro.question or sb.outro.end:
        audio_events.append({"type": "drop", "t": secs[-1].start, "gain": 0.9})

    chart = None
    if sb.outro.chart and has_q:
        steps = []
        k = 0
        while k * q.model.step <= sim_total + 1e-9 and k < 400:
            val = g.value(k * q.model.step + 1e-9)
            steps.append([k * q.model.step, val])
            k += 1
        refs = [{"label": (m.chart_label or m.label), "value": m.value} for m in q.milestones if m.chart]
        if q.limit:
            refs.append({"label": q.limit.chart_label or q.limit.label, "value": q.limit.value, "limit": True})
        breach = None
        if q.limit:
            c = g.crossing(q.limit.value * (1 + 1e-12))
            if c is not None and c <= sim_total:
                n = int(math.floor(c / q.model.step + 1e-9)) + 1
                breach = {"sim": c, "label": f"SECOND {n}: {q.limit.label} EXCEEDED"
                          if q.model.step == 1 else f"{q.limit.label} EXCEEDED"}
        chart = {"title": sb.outro.chart_title, "subtitle": sb.outro.chart_subtitle,
                 "steps": steps, "refs": refs, "breach": breach, "unit": q.unit}

    return {
        "version": 2, "title": sb.title, "format": sb.format, "fps": fps, "width": sb.width, "height": sb.height, "pace": pace,
        "duration": n_frames / fps, "n_frames": n_frames, "kind": q.kind if has_q else None,
        "theme": {**sb.theme.model_dump(), "captions": sb.theme.captions or STYLE_CAPTIONS[sb.theme.style]}, "chapters": chapters,
        "intro_duration": intro.duration,
        "end_start": secs[-1].start if secs[-1].kind == "question" else None,
        "layout": {"cap_top": 1090 if sb.format == "escalation" else 1290},
        "beats": beats_out, "frames": frames, "audio": sorted(audio_events + _style_sfx(sb, secs), key=lambda e: e["t"]),
        "chart": chart, "milestones": pops,
    }
