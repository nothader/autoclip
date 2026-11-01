"""剪辑决策：音乐拍点 + 打过分的镜头 → 剪辑表（EditPlan，JSON 可手改后再渲）。

规则（产品 UGC / 无脸卡点）：
- 每一刀都落在拍点上；能量高的段落切得更密（半拍 / 一拍），安静段落两拍、四拍一切
- 第一镜（hook）用全片最好的画面，不放闪白，不放慢，开门见山
- 强拍（drop、重鼓）上闪白；小节第一拍上轻推镜（punch-in）
- 有运动的镜头做变速：先快后慢，慢下来正好落在下一拍（speed ramp）
- 高帧率素材（≥50fps）在安静段落直接放慢 0.5×
- 结尾接回开头：最后一镜取 hook 镜头之前的那几帧，播完无缝回到第一帧（loop）
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from backend.beatcut.audio import MusicAnalysis, pick_window
from backend.beatcut.footage import Shot

ASPECTS: Dict[str, Tuple[int, int]] = {
    "9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080), "16:9": (1920, 1080),
}
Pace = Literal["calm", "normal", "hype"]
GRADES = ("none", "clean", "warm", "moody", "mono", "punchy")
RAMP = [[0.4, 2.6], [0.6, 0.65]]       # 前 40% 时长 2.6×，后 60% 0.65×（落拍时慢下来）
SLOWMO = [[1.0, 0.5]]


class _M(BaseModel):
    model_config = ConfigDict(extra="forbid")


class MusicRef(_M):
    path: str
    start: float = Field(ge=0, description="从音乐第几秒开始用")
    bpm: float = 0


class ShotPlan(_M):
    source: str
    src_start: float = Field(ge=0)
    frames: int = Field(gt=0, description="成片里占多少帧")
    speed: List[List[float]] = Field(default_factory=lambda: [[1.0, 1.0]],
                                     description="[[占本镜时长比例, 速度], ...]，比例之和 = 1")
    punch: float = Field(0.0, ge=0, le=0.5, description="推镜幅度：开头放大到 1+punch，0.25 s 内回到 1")
    flash: bool = False
    foley: bool = True
    text: str = Field("", description="这一镜上叠的文案（同一句跨多个镜头时每镜都写同一句）")
    text_in: bool = Field(False, description="这一句从这一镜开始（淡入）")
    note: str = ""

    def src_seconds(self, fps: float) -> float:
        out = self.frames / fps
        return sum(frac * out * sp for frac, sp in self.speed)

    @property
    def constant_speed(self) -> Optional[float]:
        sp = {round(s, 4) for _, s in self.speed}
        return self.speed[0][1] if len(sp) == 1 else None


class EditPlan(_M):
    version: int = 1
    title: str = "beatcut"
    width: int = 1080
    height: int = 1920
    fps: int = 30
    music: Optional[MusicRef] = None
    grade: str = "clean"
    lut: Optional[str] = None
    foley: float = Field(0.35, ge=0, le=1.5, description="素材原声（敲击、开合、倒水）混音音量")
    sfx: bool = True
    loop: bool = True
    dim: float = Field(0.0, ge=0, le=0.8, description="低曝光遮罩：整体压暗的比例（0 = 不压，0.3 ≈ 30% 黑色遮罩）")
    text_style: str = "serif-italic"
    text_pos: str = "center"
    text_size: float = Field(1.0, gt=0.2, le=3)
    font: Optional[str] = None
    beats: List[float] = Field(default_factory=list, description="成片内的拍点（秒），仅供参考")
    shots: List[ShotPlan]

    @property
    def total_frames(self) -> int:
        return sum(s.frames for s in self.shots)

    @property
    def duration(self) -> float:
        return self.total_frames / self.fps


class PlanOptions(_M):
    duration: float = Field(15.0, gt=1, le=180)
    pace: Pace = "normal"
    aspect: str = "9:16"
    fps: int = 30
    grade: str = "clean"
    lut: Optional[str] = None
    loop: bool = True
    ramps: bool = True
    punch: bool = True
    flash: bool = True
    foley: float = 0.35
    sfx: bool = True
    variant: int = Field(0, ge=0, description="第几个版本：换 hook 镜头和特效分布")
    music_start: Optional[float] = None
    title: str = "beatcut"
    text: List[str] = Field(default_factory=list, description="文案，每句占一段，换句落在切点上")
    dim: Optional[float] = Field(None, ge=0, le=0.8, description="低曝光遮罩；默认有文案时 0.3，否则 0")
    text_style: str = "serif-italic"
    text_pos: str = "center"
    text_size: float = 1.0
    font: Optional[str] = None


# ------------------------------------------------------------------ slots ---
def _slots(beats: np.ndarray, energy: np.ndarray, strength: np.ndarray, downbeats: np.ndarray,
           end: float, pace: str) -> List[dict]:
    """把 [0, end] 按拍点切成若干格。返回 [{t0, t1, energy, strength, downbeat}]。"""
    if beats.size < 2:
        n = max(1, int(round(end / 0.8)))
        return [{"t0": i * end / n, "t1": (i + 1) * end / n, "energy": 0.5, "strength": 0.5, "downbeat": i % 4 == 0}
                for i in range(n)]
    period = float(np.median(np.diff(beats)))
    base = {"calm": 2.0, "normal": 1.0, "hype": 1.0}[pace]
    while base * period < {"calm": 0.9, "normal": 0.42, "hype": 0.32}[pace]:
        base *= 2
    # 半拍网格（hype 的高能量段落用）
    half = np.sort(np.concatenate([beats, (beats[:-1] + beats[1:]) / 2]))
    slots: List[dict] = []
    t = 0.0
    while t < end - 1e-6:
        i = int(np.argmin(np.abs(beats - t)))
        e = float(energy[i]) if i < energy.size else 0.5
        step = base
        if e < 0.35:
            step = base * 2
        elif e > 0.7 and pace != "calm":
            step = base / 2 if (base / 2) * period >= {"normal": 0.38, "hype": 0.24}[pace] else base
        grid = half if step < 1 else beats
        target = t + step * period
        j = int(np.argmin(np.abs(grid - target)))
        t1 = float(grid[j])
        if t1 <= t + 0.2:
            later = grid[grid > t + 0.2]
            t1 = float(later[0]) if later.size else end
        if end - t1 < 0.3:  # 别留一个极短的尾巴
            t1 = end
        t1 = min(t1, end)
        k = int(np.argmin(np.abs(beats - t)))
        slots.append({
            "t0": t, "t1": t1, "energy": e,
            "strength": float(strength[k]) if k < strength.size else 0.5,
            "downbeat": bool(downbeats.size and np.min(np.abs(downbeats - t)) < 0.03),
        })
        t = t1
    return slots


# ------------------------------------------------------------------ plan ---
def plan_edit(shots: List[Shot], music: MusicAnalysis, opts: PlanOptions,
              music_path: Optional[str] = None) -> Tuple[EditPlan, List[str]]:
    """返回 (剪辑表, 提示信息)。"""
    warnings: List[str] = []
    fps = opts.fps
    W, H = ASPECTS.get(opts.aspect, ASPECTS["9:16"])
    rng = np.random.default_rng(1000 + opts.variant)

    # 1) 选音乐段：起点在重拍，终点吸附到最近的拍点
    w0 = pick_window(music, opts.duration, opts.music_start) if music_path else 0.0
    all_beats = np.array(music.beats)
    rel = all_beats - w0
    in_win = (rel >= -1e-6) & (rel <= opts.duration + 60.0 / max(music.bpm, 1) * 0.5)
    beats = rel[in_win]
    energy = np.array(music.beat_energy)[in_win] if music.beat_energy else np.zeros(beats.size)
    strength = np.array(music.beat_strength)[in_win] if music.beat_strength else np.zeros(beats.size)
    downbeats = np.array(music.downbeats) - w0
    if beats.size:
        end = float(beats[int(np.argmin(np.abs(beats - opts.duration)))])
        if end < opts.duration * 0.6:
            end = opts.duration
    else:
        end = opts.duration
    if music_path and music.duration - w0 < end - 0.05:
        end = max(1.0, music.duration - w0)
        warnings.append(f"音乐只剩 {end:.1f}s，成片缩短")
    keep = beats <= end + 1e-6
    beats, energy, strength = beats[keep], energy[keep], strength[keep]

    slots = _slots(beats, energy, strength, downbeats, end, opts.pace)

    # 2) 帧边界（累计取整，不漂移）
    bounds = [int(round(s["t0"] * fps)) for s in slots] + [int(round(end * fps))]
    for s, a, b in zip(slots, bounds[:-1], bounds[1:], strict=True):
        s["frames"] = max(1, b - a)

    # 3) 特效分布
    n = len(slots)
    strong = sorted(range(1, n), key=lambda i: -slots[i]["strength"])
    flash_min = 0.8 if opts.pace == "calm" else 0.55  # calm 只在真正的重音上闪白
    flash_set = {i for i in strong[: max(1, n // 6)] if slots[i]["strength"] > flash_min} if opts.flash else set()
    ramp_phase = int(rng.integers(0, 3))
    for i, s in enumerate(slots):
        dur = s["frames"] / fps
        s["flash"] = i in flash_set
        s["punch"] = 0.12 if (opts.punch and i > 0 and s["downbeat"] and not s["flash"]
                              and (opts.pace != "calm" or s["strength"] > 0.6)) else 0.0
        s["ramp"] = bool(opts.ramps and opts.pace != "calm" and 0 < i < n - 1 and dur >= 0.5
                         and (i + ramp_phase) % 3 == 0)
        s["slowmo_ok"] = (opts.pace == "calm" or s["energy"] < 0.4) and i > 0 and not s["ramp"]

    loop_tail = opts.loop and n >= 3
    tail_len = slots[-1]["frames"] / fps if loop_tail else 0.0

    # 4) 分配镜头
    motions = np.array([float(sh.motion.mean()) if sh.motion.size else 0.0 for sh in shots])
    mnorm = motions / (motions.max() + 1e-9)
    used: Dict[int, List[Tuple[float, float]]] = {sh.id: [] for sh in shots}
    protected: Dict[int, List[Tuple[float, float]]] = {sh.id: [] for sh in shots}  # hook + 循环尾巴，任何时候都不复用
    usage = {sh.id: 0 for sh in shots}
    plans: List[ShotPlan] = []
    prev_id, prev_src = -1, ""
    hook = None

    def speed_for(s: dict, sh: Shot) -> List[List[float]]:
        if s["ramp"]:
            return [list(x) for x in RAMP]
        if s["slowmo_ok"] and sh.source.fps >= 50:
            return [list(x) for x in SLOWMO]
        return [[1.0, 1.0]]

    for i, s in enumerate(slots):
        out = s["frames"] / fps
        if loop_tail and i == n - 1 and hook is not None:
            sh, start = hook
            plans.append(ShotPlan(source=sh.source.path, src_start=round(max(0.0, start - out), 4), frames=s["frames"],
                                  foley=sh.source.has_audio, note="loop → 接回第一镜"))
            continue
        cands = []
        for sh in shots:
            sp = speed_for(s, sh)
            need = sum(f * out * v for f, v in sp)
            margin = 0.15
            avoid = [(a - margin, b + margin) for a, b in used[sh.id]] + protected[sh.id]
            min_start = sh.start + (tail_len if (i == 0 and loop_tail) else 0.0)
            win = sh.best_window(need, min_start=min_start, avoid=avoid)
            if win is None:
                continue
            st, sc = win
            score = sc - 0.22 * usage[sh.id]
            if sh.id == prev_id or (loop_tail and i == n - 2 and hook is not None and sh.id == hook[0].id):
                score -= 0.6
            elif sh.source.path == prev_src and len(shots) > 2:
                score -= 0.1
            if s["ramp"]:
                score += 0.25 * mnorm[sh.id]
            cands.append((score, sh, st, sp))
        if not cands:  # 素材不够：放开「不重复」，再不行就放慢最长的镜头填满
            for sh in shots:
                sp = speed_for(s, sh)
                need = sum(f * out * v for f, v in sp)
                win = sh.best_window(need, avoid=protected[sh.id])
                if win:
                    clash = sh.id == prev_id or (loop_tail and i == n - 2 and hook is not None and sh.id == hook[0].id)
                    cands.append((win[1] - 0.3 * usage[sh.id] - (0.6 if clash else 0), sh, win[0], sp))
        if not cands:
            sh = max(shots, key=lambda x: x.duration)
            factor = max(0.25, sh.duration / out)
            cands.append((0.0, sh, sh.start, [[1.0, round(factor, 3)]]))
            warnings.append(f"素材不够长：第 {i + 1} 镜把 {sh.duration:.1f}s 放慢到 {out:.1f}s")
        cands.sort(key=lambda c: -c[0])
        pick = cands[0]
        if i == 0:
            # 不同版本用不同的 hook 镜头
            distinct, seen = [], set()
            for c in cands:
                if c[1].id not in seen:
                    seen.add(c[1].id)
                    distinct.append(c)
            pick = distinct[opts.variant % len(distinct)]
        score, sh, st, sp = pick
        need = sum(f * out * v for f, v in sp)
        used[sh.id].append((st, st + need))
        usage[sh.id] += 1
        if i == 0:
            hook = (sh, st)
            protected[sh.id].append((st - (tail_len if loop_tail else 0.0) - 0.05, st + need + 0.05))
        notes = []
        if i == 0:
            notes.append("hook")
        if sp == RAMP:
            notes.append("ramp")
        elif sp == SLOWMO:
            notes.append("slowmo")
        if s["flash"]:
            notes.append("flash")
        if s["punch"]:
            notes.append("punch")
        plans.append(ShotPlan(
            source=sh.source.path, src_start=round(st, 4), frames=s["frames"], speed=sp,
            punch=s["punch"], flash=s["flash"],
            foley=bool(sh.source.has_audio and all(abs(v - 1) < 1e-6 for _, v in sp)),
            note=" ".join(notes),
        ))
        prev_id, prev_src = sh.id, sh.source.path

    if loop_tail and hook is not None and hook[1] - tail_len < hook[0].start - 1e-6:
        warnings.append("hook 镜头前面素材不够，结尾不是严格无缝循环")

    plan = EditPlan(
        title=opts.title, width=W, height=H, fps=fps,
        music=MusicRef(path=music_path, start=round(w0, 4), bpm=round(music.bpm, 2)) if music_path else None,
        grade=opts.grade, lut=opts.lut, foley=opts.foley, sfx=opts.sfx, loop=loop_tail,
        dim=opts.dim if opts.dim is not None else (0.3 if opts.text else 0.0),
        text_style=opts.text_style, text_pos=opts.text_pos, text_size=opts.text_size, font=opts.font,
        beats=[round(float(b), 4) for b in beats], shots=plans,
    )
    if opts.text:
        from backend.beatcut.text import assign_lines
        for sp, (line, first) in zip(plans, assign_lines([p.frames for p in plans], opts.text), strict=True):
            sp.text, sp.text_in = line, first
        from backend.beatcut.text import has_cjk
        if not opts.font and any(has_cjk(x) for x in opts.text):
            from backend.services.publish_export import resolve_cjk_font
            if resolve_cjk_font() is None:
                warnings.append("文案里有中日韩文字但系统里没找到 CJK 字体，会显示成方框：用 --font 指定一个 .ttf/.otf")
    footage_total = sum(sh.duration for sh in shots)
    if footage_total < end:
        warnings.append(f"素材总长 {footage_total:.1f}s 少于成片 {end:.1f}s，部分画面会重复出现")
    if len({p.source for p in plans}) == 1 and len(shots) == 1:
        warnings.append("只有一个镜头：多拍几个角度（微距、俯拍、手部动作）效果会好很多")
    return plan, warnings


def describe(plan: EditPlan) -> List[str]:
    """人能读的剪辑表。"""
    lines = []
    t = 0
    for i, s in enumerate(plan.shots, 1):
        a = t / plan.fps
        t += s.frames
        lines.append(f"{i:>2}  {a:6.2f}–{t / plan.fps:6.2f}s  {_short_name(s.source):<28} @{s.src_start:7.2f}s  {s.note}")
    return lines


def _short_name(p: str) -> str:
    name = Path(p).name
    return name if len(name) <= 28 else name[:25] + "…"
