"""
程序化声音设计（无人声、无音乐）：环境底噪 + 随速度增强的风声 + 事件音效。

- 环境床：按场景（city / desert / ocean / sky / orbit ...）交叉淡入淡出
- 风：滤波器组（对数分布的若干频带）按每帧强度调增益，频谱随速度上移
- 事件：tick（数值跳一档）/ whoosh（里程碑）/ boom（音爆）/ impact / riser / swell / drop
- 总线：事件过一个简易卷积混响；母带 tanh 软削波 + 响度归一

只用 numpy。所有随机数固定种子，同一个 plan 生成同一段声音。
"""
from __future__ import annotations

import wave
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

SR = 48_000
ATMOSPHERIC = {"city", "highway", "desert", "ocean", "sky", "suburb", "park", "fields", "forest", "mountains",
               "volcano", "coast", "outback", "ancient"}
# 新场景复用哪种环境床
BED_ALIAS = {"suburb": "calm", "park": "calm", "fields": "calm", "forest": "forest", "mountains": "sky",
             "volcano": "volcano", "coast": "ocean", "outback": "desert", "ancient": "desert", "globe": "orbit",
             "map": "void", "interior": "room"}
SCENE_CROWD = {"city": 0.45, "suburb": 0.3, "park": 0.35, "ancient": 0.2, "highway": 0.0}


def _rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def _band(x: np.ndarray, lo: float, hi: float, slope: float = 0.0) -> np.ndarray:
    """FFT 频域带通（软边），slope=每倍频程 dB 的倾斜（负数=偏暗）。"""
    n = len(x)
    size = 1 << max(0, (n - 1).bit_length())   # 2 的幂长度，FFT 快一个数量级
    X = np.fft.rfft(x, size)
    f = np.fft.rfftfreq(size, 1 / SR)
    resp = np.ones_like(f)
    if lo > 0:
        resp *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** 4)
    if hi < SR / 2:
        resp *= 1 / (1 + (f / hi) ** 4)
    if slope:
        resp *= (np.maximum(f, 20) / 1000) ** (slope / 6.02)
    return np.fft.irfft(X * resp, size)[:n]


def _noise(n: int, seed: int) -> np.ndarray:
    return _rng(seed).standard_normal(n)


def _env_from_frames(values: np.ndarray, fps: int, n: int, smooth: float = 0.12) -> np.ndarray:
    """逐帧数值 → 逐样本包络（线性插值 + 平滑）。"""
    t_frames = np.arange(len(values)) / fps
    t = np.arange(n) / SR
    e = np.interp(t, t_frames, values)
    k = max(1, int(smooth * SR))
    if k > 1:  # 滑动平均（累加和实现，O(n)）
        c = np.cumsum(np.pad(e, (k // 2, k - k // 2), mode="edge"))
        c = np.concatenate(([0.0], c))
        e = (c[k:] - c[:-k])[: n] / k
    return e


def _norm(x: np.ndarray) -> np.ndarray:
    m = np.max(np.abs(x)) or 1.0
    return x / m


# --------------------------------------------------------------- beds ---
def _bed(scene: str, n: int, seed: int) -> np.ndarray:
    t = np.arange(n) / SR
    if scene in ("city", "highway"):
        rumble = _norm(_band(_noise(n, seed), 30, 380, slope=-3)) * 0.55
        hiss = _norm(_band(_noise(n, seed + 1), 800, 5000, slope=-4)) * 0.12
        swell = 0.75 + 0.25 * np.sin(2 * np.pi * 0.07 * t + seed)
        return (rumble + hiss) * swell * 0.16
    if scene == "desert":
        wind = _norm(_band(_noise(n, seed), 120, 1600, slope=-5))
        gust = 0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * t + 1.3) * np.sin(2 * np.pi * 0.043 * t)
        return wind * gust * 0.12
    if scene == "ocean":
        surf = _norm(_band(_noise(n, seed), 60, 2500, slope=-3))
        waves = 0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.12 * t)) ** 2
        return surf * waves * 0.16
    if scene == "sky":
        wind = _norm(_band(_noise(n, seed), 200, 3000, slope=-3))
        return wind * (0.7 + 0.3 * np.sin(2 * np.pi * 0.09 * t)) * 0.16
    if scene in ("orbit", "deep_space", "void"):
        drone = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 55.4 * t)
                 + 0.35 * np.sin(2 * np.pi * 82.5 * t + 0.4) + 0.15 * np.sin(2 * np.pi * 220.3 * t))
        air = _norm(_band(_noise(n, seed), 2000, 9000, slope=-6)) * 0.05
        lvl = 0.07 if scene != "void" else 0.05
        return (drone / 2.1 + air) * lvl
    if scene == "lab":
        return _norm(_band(_noise(n, seed), 80, 1200, slope=-6)) * 0.03
    if scene == "calm":
        air = _norm(_band(_noise(n, seed), 150, 2500, slope=-5)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.08 * t))
        return air * 0.06 + _birds(n, seed) * 0.05
    if scene == "forest":
        leaves = _norm(_band(_noise(n, seed), 1500, 7000, slope=-3)) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t) ** 2)
        return leaves * 0.05 + _birds(n, seed + 1, density=1.6) * 0.07
    if scene == "volcano":
        rumble = _norm(_band(_noise(n, seed), 20, 140)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.05 * t))
        return rumble * 0.22 + _norm(_band(_noise(n, seed + 1), 200, 1500, slope=-5)) * 0.05
    if scene == "room":
        hum = np.sin(2 * np.pi * 60 * t) * 0.3 + np.sin(2 * np.pi * 120 * t) * 0.15
        tone = _norm(_band(_noise(n, seed), 60, 900, slope=-6))
        return (tone * 0.04 + hum * 0.02)
    return np.zeros(n)


def _birds(n: int, seed: int, density: float = 1.0) -> np.ndarray:
    """稀疏的鸟鸣：短促的高频调频音。"""
    r = _rng(seed)
    out = np.zeros(n)
    k = int(n / SR * 0.7 * density)
    for _ in range(k):
        start = int(r.uniform(0, n - SR // 2))
        m = int(r.uniform(0.05, 0.16) * SR)
        tt = np.arange(m) / SR
        f0 = r.uniform(2200, 4200)
        f = f0 * (1 + 0.25 * np.sin(2 * np.pi * r.uniform(15, 35) * tt))
        ph = 2 * np.pi * np.cumsum(f) / SR
        out[start:start + m] += np.sin(ph) * np.sin(np.pi * tt / tt[-1]) * r.uniform(0.3, 1)
    return out


def _babble(n: int, seed: int) -> np.ndarray:
    """人群嘈杂：多条带通噪声以音节速率调幅。"""
    t = np.arange(n) / SR
    r = _rng(seed)
    out = np.zeros(n)
    for i in range(6):
        b = _norm(_band(_noise(n, seed + i), 250 + 80 * i, 1100 + 150 * i, slope=-3))
        am = 0.5 + 0.5 * np.sin(2 * np.pi * r.uniform(3, 6) * t + r.uniform(0, 6)) * np.sin(2 * np.pi * r.uniform(0.2, 0.6) * t)
        out += b * np.clip(am, 0, 1)
    return _norm(out)


def _rain(n: int, seed: int) -> np.ndarray:
    hiss = _norm(_band(_noise(n, seed), 400, 9000, slope=-2))
    r = _rng(seed + 1)
    drops = np.zeros(n)
    idx = r.integers(0, n, size=int(n / SR * 120))
    drops[idx] = r.uniform(0.3, 1, size=idx.size)
    drops = _band(drops, 1500, 8000)
    return hiss * 0.7 + _norm(drops) * 0.3


def _crackle(n: int, seed: int) -> np.ndarray:
    r = _rng(seed)
    pops = np.zeros(n)
    idx = r.integers(0, n, size=int(n / SR * 25))
    pops[idx] = r.uniform(0.2, 1, size=idx.size) * r.choice([-1, 1], size=idx.size)
    roar = _norm(_band(_noise(n, seed + 3), 80, 900, slope=-4))
    return _norm(_band(pops, 800, 6000)) * 0.6 + roar * 0.4


def _crickets(n: int, seed: int) -> np.ndarray:
    t = np.arange(n) / SR
    chirp = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 28 * t) > 0.3) * (np.sin(2 * np.pi * 0.9 * t) > -0.2)
    chirp2 = np.sin(2 * np.pi * 3900 * t + 1) * (np.sin(2 * np.pi * 31 * t + 2) > 0.4) * (np.sin(2 * np.pi * 0.7 * t + 1) > 0)
    return chirp * 0.5 + chirp2 * 0.4


# -------------------------------------------------------------- events ---
def _adsr(n: int, a: float, d: float) -> np.ndarray:
    t = np.arange(n) / SR
    env = np.minimum(1.0, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / max(d, 1e-4))
    return env


def _tick(seed: int) -> np.ndarray:
    n = int(0.09 * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * 2350 * t) * 0.6 + np.sin(2 * np.pi * 3520 * t) * 0.25
    click = _band(_noise(n, seed), 3000, 12000) * np.exp(-t / 0.004) * 0.6
    return (tone * _adsr(n, 0.002, 0.018) + click) * 0.22


def _whoosh(seed: int, dur: float = 1.1) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = _noise(n, seed)
    bands = [(150, 400), (400, 900), (900, 2000), (2000, 4500), (4500, 9000)]
    out = np.zeros(n)
    peak = 0.45 * dur
    for k, (lo, hi) in enumerate(bands):
        b = _norm(_band(x, lo, hi))
        center = peak + (k - 2) * 0.05 * dur  # 高频略晚到 → 有"划过"感
        env = np.exp(-((t - center) / (0.18 * dur)) ** 2)
        out += b * env * (1.0 - 0.12 * k)
    return out * 0.32


def _boom(seed: int) -> np.ndarray:
    n = int(3.2 * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    # N 波：两声尖锐爆裂，间隔 ~0.11s
    for i, t0 in enumerate((0.0, 0.11)):
        idx = int(t0 * SR)
        m = int(0.03 * SR)
        crack = _band(_noise(m, seed + i), 80, 9000) * np.exp(-np.arange(m) / SR / 0.006)
        out[idx: idx + m] += crack * 1.2
    sub = np.sin(2 * np.pi * (48 * t - 6 * t * t)) * np.exp(-t / 0.7) * 0.9
    rumble = _norm(_band(_noise(n, seed + 9), 25, 220)) * np.exp(-t / 1.1) * 0.6
    return (out + sub + rumble) * 0.6


def _impact(seed: int) -> np.ndarray:
    n = int(1.6 * SR)
    t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * (70 * t - 18 * t * t)) * np.exp(-t / 0.35)
    burst = _band(_noise(n, seed), 200, 6000) * np.exp(-t / 0.08) * 0.5
    return (thump + burst) * 0.55


def _riser(seed: int, dur: float = 2.4) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 180 * (2 ** (2.2 * t / dur))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)) / 1.75
    air = _norm(_band(_noise(n, seed), 1500, 8000)) * 0.3
    env = (t / dur) ** 2.2
    return (tone * 0.6 + air) * env * 0.32


def _swell(seed: int, dur: float = 3.0) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    pad = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((110, 110.6, 164.8, 220.2)))
    env = np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 1.4)
    return pad / 4 * env * 0.22


def _drop(seed: int) -> np.ndarray:
    n = int(3.0 * SR)
    t = np.arange(n) / SR
    f = 30 + 70 * np.exp(-t / 0.35)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t / 1.1) * 0.7


def _rumble(seed: int, dur: float = 3.0) -> np.ndarray:
    n = int(max(0.5, dur) * SR)
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.8)
    body = _norm(_band(_noise(n, seed), 18, 160)) * (0.75 + 0.25 * np.sin(2 * np.pi * 7 * t))
    rattle = _norm(_band(_noise(n, seed + 1), 300, 2500)) * (np.abs(np.sin(2 * np.pi * 11 * t)) ** 4) * 0.3
    return (body + rattle) * env * 0.7


def _alarm(seed: int, dur: float = 2.0) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = np.where((t * 2.5) % 1 < 0.5, 880, 660)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sq = np.tanh(3 * np.sin(ph))
    return sq * np.minimum(1, (dur - t) / 0.1) * 0.18


def _heartbeat(seed: int, dur: float = 2.4) -> np.ndarray:
    n = int(dur * SR)
    out = np.zeros(n)
    for beat in np.arange(0, dur - 0.3, 0.85):
        for off, g in ((0.0, 1.0), (0.18, 0.7)):
            i = int((beat + off) * SR)
            m = int(0.16 * SR)
            tt = np.arange(m) / SR
            thump = np.sin(2 * np.pi * (55 - 60 * tt) * tt) * np.exp(-tt / 0.045) * g
            out[i:i + m] += thump[: max(0, min(m, n - i))]
    return out * 0.8


def _crack(seed: int) -> np.ndarray:
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    snap = _band(_noise(n, seed), 1000, 12000) * np.exp(-t / 0.012)
    tail = _norm(_band(_noise(n, seed + 1), 60, 600)) * np.exp(-t / 0.35) * 0.4
    return (snap * 1.2 + tail) * 0.6


def _ring(seed: int) -> np.ndarray:
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    gate = ((t % 0.1) < 0.05) * (t < 0.9)
    tone = np.sin(2 * np.pi * 1400 * t) * 0.6 + np.sin(2 * np.pi * 1750 * t) * 0.4
    return tone * gate * 0.2


def _beep(seed: int) -> np.ndarray:
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1000 * t) * _adsr(n, 0.004, 0.05) * 0.25


def _siren(seed: int, dur: float = 3.0) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 700 + 400 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.6 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.minimum(1, t / 0.3) * np.minimum(1, (dur - t) / 0.5) * 0.15


def _thunder(seed: int) -> np.ndarray:
    n = int(4.0 * SR)
    t = np.arange(n) / SR
    crack = _band(_noise(n, seed), 600, 8000) * np.exp(-t / 0.05) * 0.7
    roll = _norm(_band(_noise(n, seed + 1), 25, 300)) * np.exp(-t / 1.2) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.7 * t) ** 2)
    return (crack + roll) * 0.8


def _debris(seed: int) -> np.ndarray:
    """爆炸后碎石落地：一串随机的小撞击 + 沙沙声。"""
    n = int(2.4 * SR)
    r = _rng(seed)
    out = np.zeros(n)
    for k in range(28):
        t0 = int(r.uniform(0.0, 1.9) ** 1.4 * SR)
        m = int(0.06 * SR)
        hit = _band(_noise(m, seed + k), 300, 5000) * np.exp(-np.arange(m) / SR / 0.012) * r.uniform(0.2, 0.9)
        out[t0: t0 + m] += hit[: max(0, min(m, n - t0))]
    t = np.arange(n) / SR
    hiss = _norm(_band(_noise(n, seed + 99), 2000, 9000)) * np.exp(-t / 0.8) * 0.15
    return (out + hiss) * 0.7


def _sparkle(seed: int, dur: float = 2.5) -> np.ndarray:
    """电焊 / 火花：密集的高频噼啪。"""
    n = int(dur * SR)
    r = _rng(seed)
    pops = np.zeros(n)
    idx = r.integers(0, n, size=int(dur * 140))
    pops[idx] = r.uniform(0.2, 1, size=idx.size) * r.choice([-1, 1], size=idx.size)
    t = np.arange(n) / SR
    env = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.3)
    buzz = _norm(_band(_noise(n, seed + 1), 3000, 9000)) * 0.25
    return (_norm(_band(pops, 2500, 11000)) * 0.75 + buzz) * env * 0.5


def _pop(seed: int) -> np.ndarray:
    """彩带炮 / 气泡：短促的"啵" + 一点纸屑沙沙。"""
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (420 * t - 900 * t * t)) * np.exp(-t / 0.03)
    snap = _band(_noise(n, seed), 1500, 9000) * np.exp(-t / 0.01)
    rustle = _norm(_band(_noise(n, seed + 2), 3000, 10000)) * np.exp(-t / 0.35) * 0.18
    return (body * 0.7 + snap * 0.6 + rustle) * 0.6


def _glitch(seed: int) -> np.ndarray:
    """数字故障：方波碎片 + 位压缩噪声的断续。"""
    n = int(0.55 * SR)
    r = _rng(seed)
    t = np.arange(n) / SR
    out = np.zeros(n)
    pos = 0
    while pos < n:
        m = int(r.uniform(0.015, 0.07) * SR)
        f = r.choice([180, 340, 720, 1450, 2900])
        seg = np.sign(np.sin(2 * np.pi * f * np.arange(m) / SR)) * r.uniform(0.3, 1.0)
        if r.random() < 0.4:
            seg = np.round(_noise(m, int(r.integers(1, 1 << 30))) * 3) / 3
        if r.random() < 0.25:
            seg *= 0
        out[pos: pos + m] += seg[: max(0, min(m, n - pos))]
        pos += m
    return out * np.minimum(1, (0.55 - t) / 0.05) * 0.22


def _shimmer(seed: int, dur: float = 2.6) -> np.ndarray:
    """光束 / 辉光：高处的泛音铃声慢慢铺开。"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    tones = sum(np.sin(2 * np.pi * f * t + k) * (0.6 ** k) for k, f in enumerate((880, 1318.5, 1760, 2637)))
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * 5.5 * t)
    env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 1.2)
    return tones * trem * env * 0.07


def _breath(seed: int, dur: float = 3.0) -> np.ndarray:
    """第一人称呼吸：滤波噪声的吸 / 呼循环（吸气更亮、更短）。"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = _noise(n, seed)
    inhale, exhale = _norm(_band(x, 900, 4200)), _norm(_band(x, 350, 1800))
    period = 1.7
    ph = (t % period) / period
    env_in = np.where(ph < 0.38, np.sin(np.pi * ph / 0.38), 0.0) ** 2
    env_out = np.where(ph >= 0.42, np.sin(np.pi * (ph - 0.42) / 0.58), 0.0) ** 1.5
    fade = np.minimum(1, t / 0.3) * np.minimum(1, (dur - t) / 0.3)
    return (inhale * env_in * 0.55 + exhale * env_out * 0.7) * fade * 0.16


def _footsteps(seed: int, dur: float, step: float, hard: float) -> np.ndarray:
    n = int(dur * SR)
    out = np.zeros(n)
    rng = _rng(seed)
    m = int(0.14 * SR)
    tt = np.arange(m) / SR
    k = 0
    for t0 in np.arange(0.12, dur - 0.1, step):
        i = int((t0 + rng.uniform(-0.015, 0.015)) * SR)
        thump = np.sin(2 * np.pi * (95 - 120 * tt) * tt) * np.exp(-tt / 0.03)
        scuff = _band(_noise(m, seed + k), 800, 5000) * np.exp(-tt / 0.02) * 0.35 * hard
        g = 0.85 + 0.15 * ((k % 2) * 2 - 1)   # 左右脚轻重不同
        seg = (thump + scuff) * g
        out[i:i + m] += seg[: max(0, min(m, n - i))]
        k += 1
    return out * 0.5


def _steps(seed: int, dur: float = 3.0) -> np.ndarray:
    return _footsteps(seed, dur, 0.55, 0.6)


def _run_steps(seed: int, dur: float = 3.0) -> np.ndarray:
    return _footsteps(seed, dur, 0.31, 1.0) * 1.15


EVENT_FUNCS = {"tick": _tick, "whoosh": _whoosh, "boom": _boom, "impact": _impact,
               "rumble": _rumble, "alarm": _alarm, "heartbeat": _heartbeat, "crack": _crack, "ring": _ring,
               "beep": _beep, "siren": _siren, "thunder": _thunder,
               "riser": _riser, "swell": _swell, "drop": _drop,
               "debris": _debris, "sparkle": _sparkle, "pop": _pop, "glitch": _glitch, "shimmer": _shimmer,
               "breath": _breath, "steps": _steps, "run_steps": _run_steps}
TIMED = {"rumble", "alarm", "siren", "heartbeat", "whoosh", "riser", "swell", "sparkle", "shimmer", "breath", "steps", "run_steps"}   # 接受 dur 的事件


def _reverb(x: np.ndarray, seconds: float = 2.2, seed: int = 99) -> np.ndarray:
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = _band(_noise(n, seed), 200, 7000) * np.exp(-t / (seconds / 5))
    ir /= np.sqrt(np.sum(ir ** 2)) or 1
    L = len(x) + n - 1
    size = 1 << (L - 1).bit_length()
    y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    return y


# ------------------------------------------------------------ 合成主函数 ---
def synthesize(plan: Dict[str, Any], voice: "np.ndarray | None" = None) -> np.ndarray:
    """返回 (n, 2) float32，范围 [-1, 1]。voice：可选旁白人声（单声道 48 kHz），自动压低底噪/音效。"""
    fps = plan["fps"]
    frames = plan["frames"]
    n = int(round(plan["duration"] * SR))
    out = np.zeros((n, 2))

    beats = plan.get("beats", [])
    AMB = {"space": "orbit", "room": "room", "calm": "calm", "forest": "forest", "ocean": "ocean", "wind": "sky",
           "lab": "room", "rumble": "volcano", "none": "none"}

    def bed_name(f):
        sc = f.get("scene", "void")
        if sc == "custom" and "b" in f and f["b"] < len(beats):
            st = (beats[f["b"]].get("env") or {}).get("set") or {}
            return AMB.get(st.get("ambience", "space"), "orbit")
        return BED_ALIAS.get(sc, sc)

    scenes = [bed_name(f) for f in frames]
    # 1) 环境床：每个场景一条，按逐帧"是否当前场景"做交叉淡化
    for k, name in enumerate(sorted(set(scenes))):
        mask = np.array([1.0 if s == name else 0.0 for s in scenes])
        env = _env_from_frames(mask, fps, n, smooth=0.25)
        if env.max() <= 0:
            continue
        bed = _bed(name, n, seed=100 + k)
        out[:, 0] += bed * env
        out[:, 1] += np.roll(bed, 211) * env

    # 1b) 场景层：人群嘈杂、雨、火、夜虫（由每段的 env / cast / effects 决定）
    def beat_of(f):
        return beats[f["b"]] if "b" in f and f["b"] < len(beats) else None

    crowd_l, rain_l, fire_l, night_l = [], [], [], []
    for f in frames:
        b = beat_of(f)
        envd = (b or {}).get("env") or {}
        scene = f.get("scene", "void")
        crowd = 0.0
        if b is not None:
            base = envd.get("crowd")
            crowd = SCENE_CROWD.get(scene, 0.0) if base is None else base
            if envd.get("empty"):
                crowd = 0.0
            cast_n = sum(c.get("count", 0) for c in b.get("cast", []))
            crowd = max(crowd, min(1.0, cast_n / 25))
            if "vanish" in b.get("effects", []):
                crowd *= max(0.0, 1 - (f.get("frac", 0) * 1.4))
        crowd_l.append(crowd)
        w = envd.get("weather")
        rain_l.append(1.0 if w == "storm" else 0.7 if w == "rain" else 0.0)
        fire_l.append(1.0 if b is not None and "fire" in b.get("effects", []) else 0.0)
        night_l.append(1.0 if envd.get("time") == "night" and scene in ATMOSPHERIC and scene != "city" else 0.0)
    for k, (vals, fn, gain) in enumerate(((crowd_l, _babble, 0.09), (rain_l, _rain, 0.14),
                                          (fire_l, _crackle, 0.16), (night_l, _crickets, 0.025))):
        arr = np.array(vals)
        if arr.max() <= 0:
            continue
        envl = _env_from_frames(arr, fps, n, smooth=0.3)
        layer = fn(n, 500 + k)
        out[:, 0] += layer * envl * gain
        out[:, 1] += np.roll(layer, 331) * envl * gain

    # 2) 风：强度驱动的滤波器组，只在有空气的场景
    inten = np.array([f.get("intensity", 0.0) if f.get("scene") in ATMOSPHERIC else 0.0 for f in frames])
    ienv = _env_from_frames(inten, fps, n, smooth=0.3)
    if ienv.max() > 0.01:
        base = _noise(n, 7)
        bands = [(90, 220), (220, 480), (480, 1000), (1000, 2100), (2100, 4400), (4400, 9000)]
        wind = np.zeros(n)
        for b, (lo, hi) in enumerate(bands):
            nb = _norm(_band(base, lo, hi))
            # 低频带先起来，高频带在高速时才打开 → 音色随速度变亮
            thresh = b / len(bands) * 0.75
            g = np.clip((ienv - thresh) / 0.35, 0, 1) * (0.9 - 0.08 * b)
            wind += nb * g
        gust = 1 + 0.18 * np.sin(2 * np.pi * 0.6 * np.arange(n) / SR) * np.sin(2 * np.pi * 0.23 * np.arange(n) / SR)
        wind *= gust * 0.2 * (ienv ** 0.7)
        out[:, 0] += wind
        out[:, 1] += np.roll(wind, 97)

    # 2b) bodycam：机身话筒的底噪 + 偶尔的风噪（一直在，像真实录像）
    if (plan.get("theme") or {}).get("style") == "bodycam":
        hiss = _norm(_band(_noise(n, 77), 2500, 9000)) * 0.012
        rumble = _norm(_band(_noise(n, 78), 40, 160))
        gust = np.clip(np.sin(2 * np.pi * 0.13 * np.arange(n) / SR) * np.sin(2 * np.pi * 0.047 * np.arange(n) / SR), 0, 1) ** 2
        mic = hiss + rumble * gust * 0.05
        out[:, 0] += mic
        out[:, 1] += np.roll(mic, 53)

    # 3) 事件（+ 混响送一路）
    fx = np.zeros((n, 2))
    for i, ev in enumerate(plan.get("audio", [])):
        fn = EVENT_FUNCS.get(ev["type"])
        if not fn:
            continue
        s = fn(1000 + i, max(0.25, float(ev["dur"]))) if "dur" in ev and ev["type"] in TIMED else fn(1000 + i)
        start = int(ev["t"] * SR)
        if start >= n:
            continue
        end = min(n, start + len(s))
        seg = s[: end - start] * ev.get("gain", 1.0)
        pan = 0.0 if ev["type"] not in ("whoosh", "thunder", "debris", "sparkle", "glitch") else (0.35 if i % 2 else -0.35)
        fx[start:end, 0] += seg * (1 - pan) / 1.0
        fx[start:end, 1] += seg * (1 + pan) / 1.0
    wet = np.stack([_reverb(fx[:, 0], seed=5), _reverb(fx[:, 1], seed=6)], axis=1)
    out += fx + wet * 0.28

    # 4) 结尾问句段：除 drop 外压低，留出安静
    q_frames = np.array([1.0 if f.get("sec") == "question" else 0.0 for f in frames])
    duck = 1 - 0.7 * _env_from_frames(q_frames, fps, n, smooth=0.4)
    out *= duck[:, None]

    # 5) 母带：淡入淡出 + 软削波 + 响度归一（RMS ≈ -18 dBFS，峰值 ≤ -2 dBFS（给 AAC 编码留余量））
    #    有旁白时：音效总线压到 -22 dBFS，说话处再闪避 ~9 dB；人声单独一条总线（有声部分 RMS ≈ -16 dBFS）
    fade = int(0.04 * SR)
    out[:fade] *= np.linspace(0, 1, fade)[:, None]
    tail = int(0.6 * SR)
    out[-tail:] *= np.linspace(1, 0, tail)[:, None]
    rms = np.sqrt(np.mean(out ** 2)) or 1.0
    has_voice = voice is not None and np.any(voice)
    out *= 10 ** ((-22 if has_voice else -18) / 20) / rms
    if has_voice:
        v = np.zeros(n, dtype=np.float64)
        v[: min(n, len(voice))] = voice[:n]
        active = np.abs(v) > 0.01
        venv = _env_from_frames(active[:: SR // 100].astype(float), 100, n, smooth=0.25)
        venv = np.clip(venv * 3, 0, 1)
        out *= (1 - 0.65 * venv)[:, None]
        vr = np.sqrt(np.mean(v[active] ** 2)) if active.any() else 1.0
        v *= 10 ** (-16 / 20) / (vr or 1.0)
        out[:, 0] += v
        out[:, 1] += v
    out = np.tanh(out * 1.2) / np.tanh(1.2)
    peak = np.max(np.abs(out)) or 1.0
    if peak > 0.79:
        out *= 0.79 / peak
    return out.astype(np.float32)


def write_wav(samples: np.ndarray, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(samples, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


def render_audio(plan: Dict[str, Any], path: Path, voice: "np.ndarray | None" = None) -> Path:
    return write_wav(synthesize(plan, voice), path)
