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
ATMOSPHERIC = {"city", "highway", "desert", "ocean", "sky"}


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
    return np.zeros(n)


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


EVENT_FUNCS = {"tick": _tick, "whoosh": _whoosh, "boom": _boom, "impact": _impact,
               "riser": _riser, "swell": _swell, "drop": _drop}


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
def synthesize(plan: Dict[str, Any]) -> np.ndarray:
    """返回 (n, 2) float32，范围 [-1, 1]。"""
    fps = plan["fps"]
    frames = plan["frames"]
    n = int(round(plan["duration"] * SR))
    out = np.zeros((n, 2))

    scenes = [f.get("scene", "void") for f in frames]
    # 1) 环境床：每个场景一条，按逐帧"是否当前场景"做交叉淡化
    for k, name in enumerate(sorted(set(scenes))):
        mask = np.array([1.0 if s == name else 0.0 for s in scenes])
        env = _env_from_frames(mask, fps, n, smooth=0.25)
        if env.max() <= 0:
            continue
        bed = _bed(name, n, seed=100 + k)
        out[:, 0] += bed * env
        out[:, 1] += np.roll(bed, 211) * env

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

    # 3) 事件（+ 混响送一路）
    fx = np.zeros((n, 2))
    for i, ev in enumerate(plan.get("audio", [])):
        fn = EVENT_FUNCS.get(ev["type"])
        if not fn:
            continue
        s = fn(1000 + i)
        start = int(ev["t"] * SR)
        if start >= n:
            continue
        end = min(n, start + len(s))
        seg = s[: end - start] * ev.get("gain", 1.0)
        pan = 0.0 if ev["type"] != "whoosh" else (0.35 if i % 2 else -0.35)
        fx[start:end, 0] += seg * (1 - pan) / 1.0
        fx[start:end, 1] += seg * (1 + pan) / 1.0
    wet = np.stack([_reverb(fx[:, 0], seed=5), _reverb(fx[:, 1], seed=6)], axis=1)
    out += fx + wet * 0.28

    # 4) 结尾问句段：除 drop 外压低，留出安静
    q_frames = np.array([1.0 if f.get("sec") == "question" else 0.0 for f in frames])
    duck = 1 - 0.7 * _env_from_frames(q_frames, fps, n, smooth=0.4)
    out *= duck[:, None]

    # 5) 母带：淡入淡出 + 软削波 + 响度归一（RMS ≈ -18 dBFS，峰值 ≤ -2 dBFS（给 AAC 编码留余量））
    fade = int(0.04 * SR)
    out[:fade] *= np.linspace(0, 1, fade)[:, None]
    tail = int(0.6 * SR)
    out[-tail:] *= np.linspace(1, 0, tail)[:, None]
    rms = np.sqrt(np.mean(out ** 2)) or 1.0
    out *= 10 ** (-18 / 20) / rms
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


def render_audio(plan: Dict[str, Any], path: Path) -> Path:
    return write_wav(synthesize(plan), path)
