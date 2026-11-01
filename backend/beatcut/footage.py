"""素材分析：探测 → 低分辨率抽帧 → 每帧清晰度 / 运动量 / 曝光 → 按镜头切换拆成 shot → 打分。

一条长的原始素材（一镜到底拍了很多角度）和一文件夹短片段都能用：长素材按画面突变自动拆分。
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

from backend.utils.ffmpeg_utils import get_ffmpeg_path, get_ffprobe_path

VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi", ".mts", ".hevc"}
SAMPLE_FPS = 10.0
SAMPLE_W, SAMPLE_H = 96, 96
MIN_SHOT = 0.4  # 秒；短于这个的镜头片段不用


@dataclass
class SourceInfo:
    path: str
    duration: float
    fps: float
    width: int
    height: int
    has_audio: bool
    hdr: bool = False


@dataclass
class Shot:
    """一段连续画面（同一机位 / 角度）。scores 按 SAMPLE_FPS 采样，对应 [start, end)。"""
    id: int
    source: SourceInfo
    start: float
    end: float
    scores: np.ndarray = field(repr=False)
    motion: np.ndarray = field(repr=False)

    @property
    def duration(self) -> float:
        return self.end - self.start

    @property
    def quality(self) -> float:
        return float(np.percentile(self.scores, 75)) if self.scores.size else 0.0

    def best_window(self, length: float, *, min_start: float = 0.0,
                    avoid: Sequence[Tuple[float, float]] = ()) -> Optional[Tuple[float, float]]:
        """在镜头内找长度 length 的最佳窗口（平均分最高），避开已用区间。返回 (起点秒, 平均分)。"""
        lo = max(self.start, min_start)
        if self.end - lo < length - 1e-6:
            return None
        n = max(1, int(round(length * SAMPLE_FPS)))
        sc = self.scores
        if sc.size < n:
            ok = not any(a < lo + length and lo < b for a, b in avoid)
            return (lo, float(sc.mean()) if sc.size else 0.0) if ok else None
        csum = np.concatenate([[0.0], np.cumsum(sc)])
        means = (csum[n:] - csum[:-n]) / n
        starts = self.start + np.arange(means.size) / SAMPLE_FPS
        best, best_s = None, -1e9
        for s0, m in zip(starts, means, strict=True):
            if s0 < lo - 1e-6 or s0 + length > self.end + 1e-6:
                continue
            if any(a < s0 + length and s0 < b for a, b in avoid):
                continue
            if m > best_s:
                best, best_s = float(s0), float(m)
        return (best, best_s) if best is not None else None

    def motion_at(self, t0: float, t1: float) -> float:
        i0 = int((t0 - self.start) * SAMPLE_FPS)
        i1 = max(i0 + 1, int((t1 - self.start) * SAMPLE_FPS))
        seg = self.motion[max(0, i0):i1]
        return float(seg.mean()) if seg.size else 0.0


def collect_sources(inputs: Iterable[str | Path]) -> List[Path]:
    out: List[Path] = []
    for raw in inputs:
        p = Path(raw).expanduser()
        if p.is_dir():
            out += sorted(x for x in p.iterdir() if x.suffix.lower() in VIDEO_EXTS and not x.name.startswith("."))
        elif p.is_file():
            out.append(p)
        else:
            raise FileNotFoundError(f"素材不存在：{p}")
    if not out:
        raise ValueError("没有找到视频素材（支持 " + " ".join(sorted(VIDEO_EXTS)) + "）")
    return [x.resolve() for x in out]


def probe(path: Path) -> SourceInfo:
    cmd = [get_ffprobe_path(), "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"无法读取素材：{path}\n{proc.stderr[-300:]}")
    info = json.loads(proc.stdout or "{}")
    streams = info.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    if v is None:
        raise ValueError(f"不是视频文件：{path}")
    num, _, den = (v.get("avg_frame_rate") or v.get("r_frame_rate") or "30/1").partition("/")
    try:
        fps = float(num) / float(den or 1)
    except (ValueError, ZeroDivisionError):
        fps = 30.0
    if not (1 <= fps <= 1000):
        fps = 30.0
    w, h = int(v.get("width", 0)), int(v.get("height", 0))
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    if "rotate" in (v.get("tags") or {}):
        rot = int(v["tags"]["rotate"])
    if abs(rot) % 180 == 90:
        w, h = h, w
    dur = float(v.get("duration") or info.get("format", {}).get("duration") or 0)
    hdr = v.get("color_transfer") in ("arib-std-b67", "smpte2084")
    return SourceInfo(str(path), dur, fps, w, h, any(s.get("codec_type") == "audio" for s in streams), hdr)


def sample_frames(src: SourceInfo) -> np.ndarray:
    """按 SAMPLE_FPS 抽成 96x96 灰度帧，shape (n, H, W) uint8。"""
    cmd = [get_ffmpeg_path(), "-v", "error", "-nostdin", "-i", src.path, "-an",
           "-vf", f"fps={SAMPLE_FPS},scale={SAMPLE_W}:{SAMPLE_H}:flags=area,format=gray",
           "-f", "rawvideo", "-"]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(f"抽帧失败：{src.path}\n{proc.stderr.decode('utf-8', 'replace')[-300:]}")
    buf = np.frombuffer(proc.stdout, dtype=np.uint8)
    n = buf.size // (SAMPLE_W * SAMPLE_H)
    return buf[: n * SAMPLE_W * SAMPLE_H].reshape(n, SAMPLE_H, SAMPLE_W)


def frame_metrics(frames: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """返回 (sharpness, motion, brightness, cut_signal)。"""
    f = frames.astype(np.float32)
    lap = (-4 * f[:, 1:-1, 1:-1] + f[:, :-2, 1:-1] + f[:, 2:, 1:-1] + f[:, 1:-1, :-2] + f[:, 1:-1, 2:])
    sharp = lap.reshape(len(f), -1).var(axis=1)
    bright = f.reshape(len(f), -1).mean(axis=1)
    if len(f) > 1:
        d = np.abs(np.diff(f, axis=0)).reshape(len(f) - 1, -1).mean(axis=1)
        motion = np.concatenate([[d[0]], d])
        # 镜头切换：直方图距离（比像素差对运动更不敏感）
        hists = np.stack([np.histogram(x, bins=32, range=(0, 255))[0] for x in frames]).astype(np.float32)
        hists /= hists.sum(axis=1, keepdims=True) + 1e-9
        hd = 0.5 * np.abs(np.diff(hists, axis=0)).sum(axis=1)
        cut = np.concatenate([[0.0], hd])
    else:
        motion = np.zeros(len(f), dtype=np.float32)
        cut = np.zeros(len(f), dtype=np.float32)
    return sharp, motion, bright, cut


def split_shots(cut: np.ndarray, motion: np.ndarray) -> List[int]:
    """返回镜头边界（采样帧号，含 0 和 n）。直方图突变 + 像素突变同时成立才算切换。"""
    n = cut.size
    if n < 3:
        return [0, n]
    med = float(np.median(motion)) + 1e-6
    bounds = [0]
    for i in range(1, n):
        if cut[i] > 0.35 and motion[i] > max(18.0, 3.5 * med) and i - bounds[-1] >= MIN_SHOT * SAMPLE_FPS:
            bounds.append(i)
    bounds.append(n)
    return bounds


def score_frames(sharp: np.ndarray, motion: np.ndarray, bright: np.ndarray, sharp_ref: Tuple[float, float]) -> np.ndarray:
    """0–1 分：清晰（主要）+ 适度运动（手部动作、转台）− 欠曝 / 过曝 − 剧烈晃动。"""
    lo, hi = sharp_ref
    s = np.clip((np.log1p(sharp) - lo) / (hi - lo + 1e-9), 0, 1)
    # 运动：0 → 0.3（静止画面也能用），8–20 最好，> 40 视为甩镜 / 晃动
    m = np.interp(motion, [0, 4, 8, 20, 40, 70], [0.3, 0.7, 1.0, 1.0, 0.4, 0.0])
    b = np.interp(bright, [0, 25, 50, 200, 235, 255], [0.0, 0.3, 1.0, 1.0, 0.5, 0.2])
    return (0.55 * s + 0.25 * m + 0.20 * b) * (0.5 + 0.5 * b)


def analyze_footage(paths: Sequence[Path], progress=None) -> List[Shot]:
    raw = []
    for i, p in enumerate(paths):
        src = probe(p)
        frames = sample_frames(src)
        if len(frames) == 0:
            continue
        raw.append((src, *frame_metrics(frames)))
        if progress:
            progress("footage", i + 1, len(paths))
    if not raw:
        raise ValueError("素材都读不出画面")
    all_sharp = np.log1p(np.concatenate([r[1] for r in raw]))
    ref = (float(np.percentile(all_sharp, 10)), float(np.percentile(all_sharp, 95)))

    shots: List[Shot] = []
    for src, sharp, motion, bright, cut in raw:
        scores = score_frames(sharp, motion, bright, ref)
        bounds = split_shots(cut, motion)
        for a, b in zip(bounds[:-1], bounds[1:], strict=True):
            # 镜头两端各让出一个采样帧，避开切换处的过渡帧
            a2 = a + (1 if a > 0 else 0)
            b2 = b - (1 if b < len(scores) else 0)
            start = a2 / SAMPLE_FPS
            end = min(src.duration, b2 / SAMPLE_FPS) if src.duration else b2 / SAMPLE_FPS
            if end - start < MIN_SHOT:
                continue
            shots.append(Shot(len(shots), src, start, end, scores[a2:b2], motion[a2:b2]))
    if not shots:
        raise ValueError("素材太短：每个镜头至少要 0.4 秒")
    return shots
