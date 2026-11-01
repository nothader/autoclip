"""剪辑表 → MP4。

每个镜头单独一次 ffmpeg（变速曲线 → 恒定帧率 → 铺满裁切 → 推镜 → 调色 → 闪白），按精确帧数输出，
再用 concat 无损拼接，最后和 numpy 混好的音轨（音乐 + 素材原声 + 合成音效）封装。
帧数在剪辑表里就定死了，所以每一刀都精确落在拍点那一帧上，不会越剪越漂。
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np

from backend.beatcut.audio import decode_audio
from backend.beatcut.plan import EditPlan, ShotPlan
from backend.utils.ffmpeg_utils import get_ffmpeg_path

AUDIO_SR = 48000
PUNCH_SECONDS = 0.25
FLASH_SECONDS = 0.18

GRADES: Dict[str, str] = {
    "none": "",
    "clean": "eq=contrast=1.05:saturation=1.06,unsharp=5:5:0.35:5:5:0",
    "warm": "colorbalance=rs=0.03:bs=-0.04:rm=0.03:bm=-0.03:rh=0.02:bh=-0.02,eq=contrast=1.06:saturation=1.08",
    "moody": "eq=contrast=1.14:brightness=-0.035:saturation=0.82:gamma=0.95,"
             "colorbalance=bs=0.04:gs=0.01:rh=0.03:bh=-0.02,vignette=angle=PI/5",
    "mono": "hue=s=0,eq=contrast=1.18:brightness=-0.01",
    "punchy": "eq=contrast=1.12:saturation=1.22,unsharp=5:5:0.5:5:5:0",
}
HDR_TONEMAP = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
               "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv")

Progress = Optional[Callable[[str, int, int], None]]


@lru_cache(maxsize=1)
def _has_filter(name: str) -> bool:
    try:
        out = subprocess.run([get_ffmpeg_path(), "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    except OSError:
        return False
    return any(line.split()[1:2] == [name] for line in out.splitlines() if len(line.split()) > 1)


@lru_cache(maxsize=256)
def _is_hdr(path: str) -> bool:
    from backend.beatcut.footage import probe
    try:
        return probe(Path(path)).hdr
    except Exception:  # noqa: BLE001
        return False


def _escape_filter_path(p: str) -> str:
    return p.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def speed_expr(shot: ShotPlan, fps: int) -> str:
    """分段变速 → setpts 表达式（输入时间 T 秒 → 输出时间）。恒速返回 PTS/speed。"""
    const = shot.constant_speed
    if const is not None:
        return "PTS" if abs(const - 1) < 1e-9 else f"PTS/{const:.6f}"
    out = shot.frames / fps
    src_edge, out_edge = 0.0, 0.0
    pieces = []
    for frac, sp in shot.speed:
        pieces.append((src_edge, out_edge, sp))
        src_edge += frac * out * sp
        out_edge += frac * out
    s_last, o_last, sp_last = pieces[-1]
    expr = f"{o_last:.6f}+(T-{s_last:.6f})/{sp_last:.6f}"
    for k in range(len(pieces) - 2, -1, -1):
        s0, o0, sp = pieces[k]
        expr = f"if(lt(T\\,{pieces[k + 1][0]:.6f})\\,{o0:.6f}+(T-{s0:.6f})/{sp:.6f}\\,{expr})"
    return f"({expr})/TB"


def shot_filter(shot: ShotPlan, plan: EditPlan, W: int, H: int) -> str:
    chain: List[str] = []
    if _is_hdr(shot.source) and _has_filter("zscale"):
        chain.append(HDR_TONEMAP)
    chain += ["setpts=PTS-STARTPTS", f"setpts='{speed_expr(shot, plan.fps)}'" if shot.constant_speed is None
              else f"setpts={speed_expr(shot, plan.fps)}", f"fps={plan.fps}"]
    chain.append(f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H}")
    if shot.punch > 0:
        z = f"(1+{shot.punch:.4f}*pow(max(0\\,1-t/{PUNCH_SECONDS})\\,2))"
        chain.append(f"scale=w='trunc({W}*{z}/2)*2':h='trunc({H}*{z}/2)*2':eval=frame:flags=bicubic,crop={W}:{H}")
    grade = GRADES.get(plan.grade, "")
    if grade:
        chain.append(grade)
    if plan.lut:
        chain.append(f"lut3d=file='{_escape_filter_path(str(Path(plan.lut).expanduser()))}'")
    if shot.flash:
        chain.append(f"fade=t=in:st=0:d={FLASH_SECONDS}:color=white")
    chain += ["setsar=1", "format=yuv420p", "tpad=stop_mode=clone:stop_duration=3"]
    return ",".join(chain)


def _render_shot(shot: ShotPlan, plan: EditPlan, W: int, H: int, out: Path, preview: bool) -> None:
    src_len = shot.src_seconds(plan.fps)
    cmd = [get_ffmpeg_path(), "-v", "error", "-nostdin", "-y",
           "-ss", f"{shot.src_start:.4f}", "-t", f"{src_len + 0.4:.4f}", "-i", shot.source,
           "-an", "-vf", shot_filter(shot, plan, W, H), "-frames:v", str(shot.frames),
           "-c:v", "libx264", "-preset", "ultrafast" if preview else "medium", "-crf", "23" if preview else "18",
           "-g", str(plan.fps), "-r", str(plan.fps), "-video_track_timescale", str(plan.fps * 1000), str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not out.exists():
        raise RuntimeError(f"镜头渲染失败（{Path(shot.source).name} @{shot.src_start:.2f}s）：{proc.stderr[-600:]}")


# ------------------------------------------------------------------ audio ---
def _fade(a: np.ndarray, fin: float, fout: float) -> np.ndarray:
    n = len(a)
    if n == 0:
        return a
    i, o = min(n, int(fin * AUDIO_SR)), min(n, int(fout * AUDIO_SR))
    if i:
        a[:i] *= np.linspace(0, 1, i, dtype=np.float32)[:, None]
    if o:
        a[n - o:] *= np.linspace(1, 0, o, dtype=np.float32)[:, None]
    return a


def whoosh(seconds: float = 0.42, seed: int = 0) -> np.ndarray:
    """带通噪声，起得慢、收得快，左右扫过。"""
    rng = np.random.default_rng(seed)
    n = int(seconds * AUDIO_SR)
    noise = rng.standard_normal(n).astype(np.float32)
    spec = np.fft.rfft(noise)
    f = np.fft.rfftfreq(n, 1 / AUDIO_SR)
    spec *= np.exp(-0.5 * (np.log2(np.maximum(f, 1) / 1800) / 1.1) ** 2)
    x = np.fft.irfft(spec, n).astype(np.float32)
    t = np.linspace(0, 1, n, dtype=np.float32)
    env = np.where(t < 0.75, (t / 0.75) ** 2.2, np.exp(-(t - 0.75) * 14))
    x = x * env
    x /= np.abs(x).max() + 1e-9
    pan = t
    return np.stack([x * np.cos(pan * np.pi / 2), x * np.sin(pan * np.pi / 2)], axis=1) * 0.7


def impact(seconds: float = 0.45) -> np.ndarray:
    """低频下滑的一声「咚」，垫在闪白下面。"""
    n = int(seconds * AUDIO_SR)
    t = np.arange(n, dtype=np.float32) / AUDIO_SR
    freq = 38 + 70 * np.exp(-t * 22)
    phase = 2 * np.pi * np.cumsum(freq) / AUDIO_SR
    x = np.sin(phase) * np.exp(-t * 9)
    x[: int(0.002 * AUDIO_SR)] *= np.linspace(0, 1, int(0.002 * AUDIO_SR))
    return np.stack([x, x], axis=1).astype(np.float32)


def _place(bus: np.ndarray, clip: np.ndarray, at: int, gain: float = 1.0) -> None:
    if at >= len(bus):
        return
    if at < 0:
        clip, at = clip[-at:], 0
    m = min(len(clip), len(bus) - at)
    bus[at:at + m] += clip[:m] * gain


def mix_audio(plan: EditPlan) -> np.ndarray:
    total = plan.total_frames / plan.fps
    n = int(round(total * AUDIO_SR))
    music = np.zeros((n, 2), dtype=np.float32)
    if plan.music:
        m = decode_audio(Path(plan.music.path), AUDIO_SR, 2, plan.music.start, total)
        _place(music, m, 0)
        music = _fade(music, 0.01, 0.12 if plan.loop else 0.35)

    foley = np.zeros((n, 2), dtype=np.float32)
    sfx = np.zeros((n, 2), dtype=np.float32)
    f0 = 0
    for i, s in enumerate(plan.shots):
        at = int(round(f0 / plan.fps * AUDIO_SR))
        out = s.frames / plan.fps
        if plan.foley > 0 and s.foley and s.constant_speed is not None and abs(s.constant_speed - 1) < 1e-6:
            a = decode_audio(Path(s.source), AUDIO_SR, 2, s.src_start, out)
            if a.size:
                _place(foley, _fade(a.copy(), 0.008, 0.012), at)
        if plan.sfx and s.constant_speed is None:  # 变速镜头：进镜前起 whoosh，峰值落在切点
            w = whoosh(seed=i)
            _place(sfx, w, at - int(0.75 * len(w)), 0.32)
        if plan.sfx and s.flash:
            _place(sfx, impact(), at, 0.45)
        f0 += s.frames

    # 素材原声手机收音差异大：先把整条原声轨归一到 -24 dBFS RMS，再乘用户音量
    live = np.abs(foley).max(axis=1) > 1e-4
    if live.any():
        rms = float(np.sqrt((foley[live] ** 2).mean()))
        if rms > 1e-6:
            foley *= (10 ** (-24 / 20)) / rms
    mix = music * 0.9 + foley * plan.foley * (1.6 if not plan.music else 1.0) + sfx
    # 峰值归一到 -1 dBFS（偏小的最多提 12 dB），手机外放不至于比别的视频小一截
    peak = float(np.abs(mix).max()) if mix.size else 0.0
    if peak > 1e-4:
        mix *= min(0.89 / peak, 10 ** (12 / 20))
    return mix.astype(np.float32)


# ------------------------------------------------------------------ main ---
def render_plan(plan: EditPlan, out: Path, *, preview: bool = False, workers: int = 0,
                progress: Progress = None) -> dict:
    t_start = time.time()
    out = Path(out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    for s in plan.shots:
        if not Path(s.source).exists():
            raise FileNotFoundError(f"剪辑表里的素材不存在：{s.source}")
    if plan.lut and not Path(plan.lut).expanduser().exists():
        raise FileNotFoundError(f"LUT 文件不存在：{plan.lut}")
    if plan.grade not in GRADES:
        raise ValueError(f"未知调色 {plan.grade}，可选：{' '.join(GRADES)}")
    W, H = plan.width, plan.height
    if preview:
        W, H = (W // 2) // 2 * 2, (H // 2) // 2 * 2

    tmp = Path(tempfile.mkdtemp(prefix=".beatcut-", dir=out.parent))
    try:
        parts = [tmp / f"shot_{i:03d}.mp4" for i in range(len(plan.shots))]
        n_workers = workers or min(4, os.cpu_count() or 2)
        done = 0
        with ThreadPoolExecutor(max_workers=n_workers) as ex:
            futs = [ex.submit(_render_shot, s, plan, W, H, p, preview) for s, p in zip(plan.shots, parts, strict=True)]
            for f in futs:
                f.result()
                done += 1
                if progress:
                    progress("shots", done, len(parts))
        listing = tmp / "list.txt"
        listing.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
        video = tmp / "video.mp4"
        proc = subprocess.run([get_ffmpeg_path(), "-v", "error", "-nostdin", "-y", "-f", "concat", "-safe", "0",
                               "-i", str(listing), "-c", "copy", str(video)], capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"拼接失败：{proc.stderr[-500:]}")

        if progress:
            progress("audio", 0, 1)
        audio = mix_audio(plan)
        cmd = [get_ffmpeg_path(), "-v", "error", "-nostdin", "-y", "-i", str(video),
               "-f", "f32le", "-ar", str(AUDIO_SR), "-ac", "2", "-i", "pipe:0",
               "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
               "-shortest", "-movflags", "+faststart", str(out)]
        proc = subprocess.run(cmd, input=audio.tobytes(), capture_output=True)
        if proc.returncode != 0:
            raise RuntimeError(f"封装失败：{proc.stderr.decode('utf-8', 'replace')[-500:]}")
        if progress:
            progress("audio", 1, 1)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    return {
        "path": str(out), "duration": round(plan.duration, 3), "width": W, "height": H, "fps": plan.fps,
        "shots": len(plan.shots), "frames": plan.total_frames, "seconds": round(time.time() - t_start, 1),
    }
