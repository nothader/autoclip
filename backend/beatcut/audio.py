"""音乐分析：解码 → 起音包络 → 速度（BPM）→ 拍点 / 重拍 → 每拍能量 → 选出最适合的一段。

只依赖 numpy + ffmpeg。拍点跟踪用 Ellis (2007) 动态规划：在「落在强起音上」和「拍间隔接近估计周期」之间求最优。
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import numpy as np

from backend.utils.ffmpeg_utils import get_ffmpeg_path

SR = 22050
HOP = 512
N_FFT = 2048
FRAME_RATE = SR / HOP  # 起音包络帧率 ≈ 43 Hz
# 能量在起音前半个窗就开始上升，拍点系统性偏早 ~15 ms（合成点击音轨实测），统一补偿
ONSET_LAG = 0.015


def decode_audio(path: Path, sr: int = SR, channels: int = 1, start: float = 0.0,
                 duration: Optional[float] = None) -> np.ndarray:
    """ffmpeg 解码成 float32。channels=1 → shape (n,)；channels=2 → shape (n, 2)。无音轨返回空数组。"""
    cmd = [get_ffmpeg_path(), "-v", "error", "-nostdin"]
    if start > 0:
        cmd += ["-ss", f"{start:.4f}"]
    cmd += ["-i", str(path)]
    if duration is not None:
        cmd += ["-t", f"{duration:.4f}"]
    cmd += ["-vn", "-ac", str(channels), "-ar", str(sr), "-f", "f32le", "-"]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        msg = proc.stderr.decode("utf-8", "replace")
        if "does not contain any stream" in msg or "Output file #0 does not contain" in msg or "matches no streams" in msg:
            return np.zeros((0, channels) if channels > 1 else 0, dtype=np.float32)
        raise RuntimeError(f"音频解码失败：{path}\n{msg[-400:]}")
    a = np.frombuffer(proc.stdout, dtype=np.float32).copy()
    if channels > 1:
        a = a[: len(a) // channels * channels].reshape(-1, channels)
    return a


def _stft_mag(y: np.ndarray) -> np.ndarray:
    # 居中分帧：第 t 帧以 t*HOP 为中心，拍点时间不带半窗延迟
    y = np.pad(y, (N_FFT // 2, N_FFT // 2))
    if len(y) < N_FFT:
        y = np.pad(y, (0, N_FFT - len(y)))
    n_frames = 1 + (len(y) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n_frames)[:, None]
    frames = y[idx] * np.hanning(N_FFT)[None, :].astype(np.float32)
    return np.abs(np.fft.rfft(frames, axis=1)).astype(np.float32)  # (frames, bins)


def onset_envelope(mag: np.ndarray, lo_hz: float = 0, hi_hz: float = SR / 2) -> np.ndarray:
    """对数幅度谱的正向差分（spectral flux），减去局部均值，半波整流。"""
    freqs = np.fft.rfftfreq(N_FFT, 1 / SR)
    band = (freqs >= lo_hz) & (freqs <= hi_hz)
    logm = np.log1p(100.0 * mag[:, band])
    flux = np.maximum(0.0, np.diff(logm, axis=0)).sum(axis=1)
    flux = np.concatenate([[0.0], flux])
    w = int(FRAME_RATE * 0.5) | 1
    local = np.convolve(flux, np.ones(w) / w, mode="same")
    env = np.maximum(0.0, flux - local)
    peak = np.percentile(env, 99) if env.size else 0
    return (env / peak).astype(np.float32) if peak > 0 else env.astype(np.float32)


def estimate_tempo(env: np.ndarray, lo_bpm: float = 60, hi_bpm: float = 200, prior_bpm: float = 120) -> float:
    """起音包络自相关 + 以 prior_bpm 为中心的对数高斯先验。"""
    if env.size < FRAME_RATE * 4:
        return prior_bpm
    e = env - env.mean()
    ac = np.correlate(e, e, mode="full")[len(e) - 1:]
    ac = ac / (ac[0] + 1e-9)
    lags = np.arange(len(ac))
    min_lag = int(FRAME_RATE * 60 / hi_bpm)
    max_lag = min(len(ac) - 2, int(FRAME_RATE * 60 / lo_bpm))
    if max_lag <= min_lag + 2:
        return prior_bpm
    lag_f = lags[min_lag:max_lag + 1].astype(float)
    bpm = 60 * FRAME_RATE / lag_f
    weight = np.exp(-0.5 * (np.log2(bpm / prior_bpm) / 0.6) ** 2)
    # 加上二倍周期的自相关，抑制半拍误判
    acl = ac[min_lag:max_lag + 1]
    ac2 = np.array([ac[min(len(ac) - 1, int(2 * x))] for x in lag_f])
    score = (acl + 0.5 * ac2) * weight
    i = int(np.argmax(score))
    # 抛物线插值细化
    if 0 < i < len(score) - 1:
        a, b, c = score[i - 1], score[i], score[i + 1]
        denom = a - 2 * b + c
        off = 0.5 * (a - c) / denom if denom != 0 else 0.0
    else:
        off = 0.0
    lag = lag_f[i] + off
    return float(60 * FRAME_RATE / lag)


def track_beats(env: np.ndarray, bpm: float, tightness: float = 100.0) -> np.ndarray:
    """Ellis 动态规划拍点跟踪，返回拍点所在的包络帧号。"""
    n = env.size
    if n == 0:
        return np.zeros(0, dtype=int)
    period = 60 * FRAME_RATE / bpm
    # 轻度平滑：以拍长为尺度的高斯窗
    w = np.exp(-0.5 * (np.arange(-int(period), int(period) + 1) * 32.0 / period) ** 2)
    local = np.convolve(env, w, mode="same")
    score = local.copy()
    back = -np.ones(n, dtype=int)
    lo, hi = int(round(period / 2)), int(round(period * 2))
    offsets = np.arange(-hi, -lo + 1)
    penalty = -tightness * np.log(-offsets / period) ** 2
    for t in range(n):
        prev = t + offsets
        ok = prev >= 0
        if not ok.any():
            continue
        cand = score[prev[ok]] + penalty[ok]
        j = int(np.argmax(cand))
        if cand[j] > 0:
            score[t] = local[t] + cand[j]
            back[t] = prev[ok][j]
    # 从结尾一个拍长内的最高分往回追
    tail = max(0, n - int(period))
    t = tail + int(np.argmax(score[tail:]))
    beats = [t]
    while back[t] >= 0:
        t = back[t]
        beats.append(t)
    beats = np.array(beats[::-1], dtype=int)
    # 去掉开头/结尾弱的拍（静音段）
    thr = 0.5 * np.median(local[beats]) if beats.size else 0
    keep = np.where(local[beats] > thr)[0]
    if keep.size:
        beats = beats[keep[0]: keep[-1] + 1]
    return beats


@dataclass
class MusicAnalysis:
    path: Optional[str]
    duration: float
    bpm: float
    beats: List[float]                       # 秒
    downbeats: List[float]                   # 每小节第一拍（秒）
    beat_energy: List[float]                 # 每拍 RMS 能量（0–1，相对整首）
    beat_strength: List[float]               # 每拍起音强度（0–1）
    meta: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "path": self.path, "duration": round(self.duration, 3), "bpm": round(self.bpm, 2),
            "beats": [round(b, 4) for b in self.beats],
            "downbeats": [round(b, 4) for b in self.downbeats],
            "beat_energy": [round(x, 3) for x in self.beat_energy],
            "beat_strength": [round(x, 3) for x in self.beat_strength],
        }


def _norm(x: np.ndarray) -> np.ndarray:
    if x.size == 0:
        return x
    lo, hi = np.percentile(x, 5), np.percentile(x, 98)
    return np.clip((x - lo) / (hi - lo + 1e-9), 0, 1)


def analyze_signal(y: np.ndarray, path: Optional[str] = None, bpm_hint: Optional[float] = None) -> MusicAnalysis:
    duration = len(y) / SR
    mag = _stft_mag(y)
    env = onset_envelope(mag)
    bpm = float(bpm_hint) if bpm_hint else estimate_tempo(env)
    bf = track_beats(env, bpm)
    beats = bf * HOP / SR + ONSET_LAG
    if beats.size >= 4:  # 用跟踪到的拍点线性回归修正 BPM（比相邻间隔中位数精确，后者被量化到包络帧）
        idx = np.arange(beats.size)
        slope = float(np.polyfit(idx, beats, 1)[0])
        if slope > 0:
            bpm = 60.0 / slope

    # 每拍能量 / 起音强度
    rms = np.sqrt((mag ** 2).mean(axis=1))
    edges = np.concatenate([bf, [len(rms)]])
    energy = np.array([rms[a:max(a + 1, b)].mean() for a, b in zip(edges[:-1], edges[1:], strict=True)]) if bf.size else np.zeros(0)
    strength = env[bf] if bf.size else np.zeros(0)

    # 重拍：低频（kick）起音在哪个相位上最强（4/4 假设）
    kick = onset_envelope(mag, 0, 160)
    downbeats: List[float] = []
    if bf.size >= 8:
        phase_score = [kick[bf[p::4]].mean() + 0.5 * env[bf[p::4]].mean() for p in range(4)]
        p = int(np.argmax(phase_score))
        downbeats = list(beats[p::4])
    elif beats.size:
        downbeats = list(beats[::4])

    return MusicAnalysis(
        path=path, duration=duration, bpm=bpm, beats=list(map(float, beats)), downbeats=list(map(float, downbeats)),
        beat_energy=list(map(float, _norm(energy))), beat_strength=list(map(float, np.clip(strength, 0, 1))),
    )


def analyze_music(path: Path, bpm_hint: Optional[float] = None) -> MusicAnalysis:
    y = decode_audio(path)
    if y.size < SR:
        raise ValueError(f"音乐太短或无音轨：{path}")
    return analyze_signal(y, str(path), bpm_hint)


def grid_analysis(bpm: float, duration: float) -> MusicAnalysis:
    """没给音乐时：固定速度的拍点网格。"""
    period = 60.0 / bpm
    beats = list(np.arange(0, duration + period, period))
    return MusicAnalysis(path=None, duration=duration + period, bpm=bpm, beats=beats, downbeats=beats[::4],
                         beat_energy=[0.6] * len(beats), beat_strength=[0.5] * len(beats))


def pick_window(m: MusicAnalysis, duration: float, start: Optional[float] = None) -> float:
    """选一段 duration 秒的音乐：从重拍开始、平均能量最高、开头有强拍（drop）。返回起点（秒）。

    start 给定时对齐到最近的拍点。
    """
    beats = np.array(m.beats)
    if beats.size == 0:
        return 0.0
    if start is not None:
        return float(beats[int(np.argmin(np.abs(beats - start)))])
    latest = m.duration - duration
    cands = [b for b in (m.downbeats or m.beats) if b <= latest] or [float(beats[0])]
    energy = np.array(m.beat_energy)
    strength = np.array(m.beat_strength)
    best, best_s = cands[0], -1e9
    for c in cands:
        sel = (beats >= c) & (beats < c + duration)
        if not sel.any():
            continue
        i0 = int(np.argmax(sel))
        s = energy[sel].mean() + 0.35 * strength[i0] + 0.15 * (energy[i0] - (energy[i0 - 1] if i0 > 0 else 0))
        s -= 0.02 * (c / max(1.0, m.duration))  # 同分偏好靠前
        if s > best_s:
            best, best_s = c, s
    return float(best)
