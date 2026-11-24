"""Render a DinkCam story JSON to MP4.

    python -m dink.render stories/wolves.json [-o out/wolves.mp4] [--sheet] [--workers 2] [--fps 30]
--sheet renders one still per beat (at 60% of the beat) into out/<slug>_sheet.jpg for a quick look.
"""
import argparse
import base64
import functools
import http.server
import json
import multiprocessing as mp
import os
import shutil
import socketserver
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME_ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--no-sandbox"]


def chrome_path():
    for p in (os.environ.get("DINK_CHROME"), "/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"):
        if p and os.path.exists(p):
            return p
    return None


def serve(port):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    handler.log_message = lambda *a: None
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def _worker(args):
    story_rel, times, frames_dir, port, w, h = args
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        exe = chrome_path()
        br = pw.chromium.launch(args=CHROME_ARGS, executable_path=exe) if exe else pw.chromium.launch(args=CHROME_ARGS)
        pg = br.new_page(viewport={"width": 800, "height": 800})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(f"http://127.0.0.1:{port}/web/index.html?story=/{story_rel}")
        try:
            pg.wait_for_function("window.READY === true", timeout=60000)
        except Exception:
            raise RuntimeError("engine failed to load: " + "; ".join(errs))
        for idx, t in times:
            out = Path(frames_dir) / f"{idx:05d}.jpg"
            if out.exists():
                continue
            data = pg.evaluate(f"renderFrame({t})")
            out.write_bytes(base64.b64decode(data.split(",", 1)[1]))
        br.close()
    return len(times)


def render(story_path, out_mp4=None, fps=30, workers=2, sheet=False, frames_dir=None):
    story_path = Path(story_path).resolve()
    st = json.loads(story_path.read_text())
    slug = st["slug"]
    rel = story_path.relative_to(ROOT).as_posix()
    port = 8700 + os.getpid() % 200
    httpd = serve(port)
    try:
        if sheet:
            fd = Path(f"/tmp/dink_sheet_{slug}"); shutil.rmtree(fd, ignore_errors=True); fd.mkdir(parents=True)
            times = [(i, b["t0"] + b["dur"] * (0.75 if i == 0 else 0.6)) for i, b in enumerate(st["beats"])]
            _worker((rel, times, str(fd), port, st["width"], st["height"]))
            cols = min(len(times), 6 if st["height"] > st["width"] else 4)
            rows = (len(times) + cols - 1) // cols
            out = ROOT / "out" / f"{slug}_sheet.jpg"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "1", "-i", str(fd / "%05d.jpg"),
                            "-vf", f"scale={360 if st['height'] > st['width'] else 480}:-1,tile={cols}x{rows}:padding=6:color=black",
                            "-frames:v", "1", str(out)], check=True)
            print(out)
            return out
        T = st["duration"]; n = int(round(T * fps))
        fd = Path(frames_dir or f"/tmp/dink_frames_{slug}"); fd.mkdir(parents=True, exist_ok=True)
        allt = [(i, i / fps) for i in range(n)]
        chunk = (n + workers - 1) // workers
        jobs = [(rel, allt[k * chunk:(k + 1) * chunk], str(fd), port, st["width"], st["height"]) for k in range(workers)]
        t0 = time.time()
        stop = threading.Event()

        def progress():
            while not stop.wait(20):
                done = len(list(fd.glob("*.jpg")))
                print(f"  frames {done}/{n}  ({time.time() - t0:.0f}s)", flush=True)
        threading.Thread(target=progress, daemon=True).start()
        with mp.get_context("spawn").Pool(workers) as pool:
            pool.map(_worker, jobs)
        stop.set()
        from .audio import mix
        wav = fd / "audio.wav"
        mix(st, wav)
        out = Path(out_mp4 or ROOT / "out" / f"{slug}.mp4"); out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(fd / "%05d.jpg"), "-i", str(wav),
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                        "-movflags", "+faststart", "-shortest", str(out)], check=True)
        print(f"done: {out}  ({T:.1f}s, {st['width']}x{st['height']}, {time.time() - t0:.0f}s)", flush=True)
        return out
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("story"); ap.add_argument("-o", "--out"); ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=2); ap.add_argument("--sheet", action="store_true"); ap.add_argument("--frames-dir")
    a = ap.parse_args()
    render(a.story, a.out, a.fps, a.workers, a.sheet, a.frames_dir)
