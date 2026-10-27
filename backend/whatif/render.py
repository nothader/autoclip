"""
逐帧渲染：多个 headless Chromium 进程各渲一段帧，写 JPEG，最后 ffmpeg 合成。

网页（web/）是帧号的纯函数：WHATIF.frame(i) 只依赖 plan.json 里第 i 帧的数据，
所以可以把帧区间切给多个 worker 并行渲染。
"""
from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

WEB_DIR = Path(__file__).parent / "web"
ORIGIN = "http://whatif.local/"
CHROMIUM_ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
                 "--disable-background-timer-throttling", "--disable-renderer-backgrounding"]
_MIME = {".html": "text/html", ".js": "text/javascript", ".json": "application/json",
         ".ttf": "font/ttf", ".css": "text/css", ".jpg": "image/jpeg", ".png": "image/png"}


def _open_page(pw, plan_path: Path, width: int, height: int):
    browser = pw.chromium.launch(args=CHROMIUM_ARGS)
    page = browser.new_page(viewport={"width": width, "height": height})
    errors: List[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

    def route(r):
        rel = r.request.url[len(ORIGIN):].split("?", 1)[0] or "index.html"
        f = plan_path if rel == "plan.json" else (WEB_DIR / rel).resolve()
        if rel != "plan.json" and (WEB_DIR.resolve() not in f.parents or not f.is_file()):
            r.fulfill(status=404, body="not found")
            return
        r.fulfill(path=str(f), headers={"Content-Type": _MIME.get(f.suffix, "application/octet-stream")})

    page.route(f"{ORIGIN}**", route)
    page.goto(f"{ORIGIN}index.html?w={width}&h={height}")
    try:
        page.wait_for_function("window.WHATIF_READY || window.WHATIF_ERROR", timeout=120_000)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"页面加载超时；页面报错: {errors[:5]}") from e
    err = page.evaluate("window.WHATIF_ERROR || null")
    if err:
        raise RuntimeError(f"页面加载失败: {err}")
    return browser, page, errors


def _render_part(plan_path: Path, out: Path, width: int, height: int, frames: List[int],
                 fmt: str, quality: int) -> Dict[str, Any]:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser, page, errors = _open_page(pw, plan_path, width, height)
        try:
            for i in frames:
                page.evaluate(f"WHATIF.frame({i})")
                path = out / f"{i:06d}.{fmt}"
                tmp = out / f".{i:06d}.{fmt}"   # 写完再改名，进度按完成的文件数算
                if fmt == "jpg":
                    page.screenshot(path=str(tmp), type="jpeg", quality=quality)
                else:
                    page.screenshot(path=str(tmp), type="png")
                tmp.rename(path)
        finally:
            browser.close()
    return {"frames": len(frames), "errors": errors[:20]}


def render_frames(plan: Dict[str, Any], out_dir: Path, *, width: int, height: int,
                  frames: Optional[Sequence[int]] = None, workers: int = 0, fmt: str = "jpg",
                  quality: int = 94, progress: Optional[Callable[[int, int], None]] = None) -> List[str]:
    """每个 worker 是独立的 Python 子进程（不依赖调用方的 __main__ 保护）。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = list(frames if frames is not None else range(plan["n_frames"]))
    frames = [i for i in frames if not (out_dir / f"{i:06d}.{fmt}").exists()]   # 续渲：已经写好的帧跳过
    if not frames:
        return []
    if not workers:
        workers = max(1, min(4, os.cpu_count() or 2))
    workers = max(1, min(workers, len(frames)))
    plan_path = out_dir / "plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    # 连续区间切块：块内顺序渲染，场景分块复用率高
    per = (len(frames) + workers - 1) // workers
    parts = [p for p in (frames[k * per:(k + 1) * per] for k in range(workers)) if p]
    t0 = time.time()
    procs = []
    for k, part in enumerate(parts):
        job = out_dir / f"job{k}.json"
        job.write_text(json.dumps({"plan": str(plan_path), "out": str(out_dir), "width": width, "height": height,
                                   "frames": part, "fmt": fmt, "quality": quality}), encoding="utf-8")
        res = out_dir / f"job{k}.result.json"
        cmd = [sys.executable, "-m", "backend.whatif.render", str(job), str(res)]
        procs.append((subprocess.Popen(cmd, cwd=str(Path(__file__).resolve().parents[2]),
                                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True), res))
    try:
        while any(p.poll() is None for p, _ in procs):
            time.sleep(1.0)
            if progress:
                progress(sum(1 for _ in out_dir.glob(f"[0-9]*.{fmt}")), len(frames))
    finally:
        # 中断 / 出错时不留孤儿进程（否则它们会继续占 CPU、往目录里写帧）
        for p, _ in procs:
            if p.poll() is None:
                p.terminate()
        for p, _ in procs:
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()
    missing = [i for i in frames if not (out_dir / f"{i:06d}.{fmt}").exists()]
    errors: List[str] = []
    for p, res in procs:
        stderr = p.stderr.read() if p.stderr else ""
        if p.returncode != 0 or not res.exists():
            raise RuntimeError(f"渲染进程失败（exit {p.returncode}）: {stderr[-1500:]}")
        errors.extend(json.loads(res.read_text(encoding="utf-8")).get("errors", []))
    if missing:
        raise RuntimeError(f"缺 {len(missing)} 帧（如 {missing[:5]}），不合成")
    if progress:
        progress(len(frames), len(frames))
    logger.info("渲染 %d 帧用时 %.1fs（%d 进程）", len(frames), time.time() - t0, len(parts))
    return errors


def encode(frames_dir: Path, fps: int, audio: Optional[Path], out: Path, crf: int = 18) -> None:
    from backend.utils.ffmpeg_utils import get_ffmpeg_path
    cmd = [get_ffmpeg_path(), "-hide_banner", "-loglevel", "error", "-y",
           "-framerate", str(fps), "-i", str(frames_dir / "%06d.jpg")]
    if audio:
        cmd += ["-i", str(audio)]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-profile:v", "high", "-movflags", "+faststart"]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += [str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg 合成失败: {proc.stderr[-800:]}")


def render_video(plan: Dict[str, Any], out: Path, *, preview: bool = False, workers: int = 0,
                 audio: Optional[Path] = None, keep_frames: bool = False, frames_dir: Optional[Path] = None,
                 progress: Optional[Callable[[int, int], None]] = None) -> Dict[str, Any]:
    """frames_dir：帧放在固定目录并保留；已经渲好的帧会跳过——容器重启 / 进程被杀后用同一个目录重跑就能续上。"""
    width, height = plan["width"], plan["height"]
    if preview:
        width, height = width // 2, height // 2
    if frames_dir is not None:
        frames_dir.mkdir(parents=True, exist_ok=True)
        keep_frames = True
    tmp = frames_dir or Path(tempfile.mkdtemp(prefix="whatif-frames-"))
    try:
        errors = render_frames(plan, tmp, width=width, height=height, workers=workers, progress=progress)
        out.parent.mkdir(parents=True, exist_ok=True)
        encode(tmp, plan["fps"], audio, out)
        return {"path": str(out), "width": width, "height": height, "frames": plan["n_frames"],
                "duration": plan["duration"], "page_errors": errors}
    finally:
        if not keep_frames:
            shutil.rmtree(tmp, ignore_errors=True)


def render_stills(plan: Dict[str, Any], out_dir: Path, frames: Iterable[int], *, preview: bool = True) -> List[Path]:
    width, height = plan["width"], plan["height"]
    if preview:
        width, height = width // 2, height // 2
    frames = list(frames)
    errs = render_frames(plan, out_dir, width=width, height=height, frames=frames, workers=1, fmt="png")
    if errs:
        logger.warning("页面报错: %s", errs[:5])
    return [out_dir / f"{i:06d}.png" for i in frames]


def _main(argv: List[str]) -> int:
    job = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    res = _render_part(Path(job["plan"]), Path(job["out"]), job["width"], job["height"],
                       job["frames"], job["fmt"], job["quality"])
    Path(argv[2]).write_text(json.dumps(res, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
