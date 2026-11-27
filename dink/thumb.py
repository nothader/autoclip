"""Custom thumbnail for a rendered DinkCam video (mainly long-form; Shorts ignore custom thumbnails on mobile).

    python -m dink.thumb out/<slug>.mp4 --at 42.5 --text "YOU HOSTED|THANKSGIVING|ALONE?" --accent 1 [--color "#ffd43b"]

Grabs the frame at --at seconds (pick one with a face reacting, big and well lit, no caption on it), darkens the
left side and writes 2–3 huge Anton lines (one in the accent colour). Output: out/<slug>_thumb.jpg (1280x720, or
720x1280 for vertical sources), < 2 MB as YouTube requires. Keep the text to 2–4 words per line, max 3 lines.
"""
import argparse
import base64
import html
import subprocess
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

from dink.render import chrome_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--at", type=float, default=5.0)
    ap.add_argument("--text", required=True, help="lines separated by |")
    ap.add_argument("--accent", type=int, default=1, help="index of the accent line")
    ap.add_argument("--color", default="#ffd43b")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    v = Path(a.video)
    out = Path(a.out or v.with_name(v.stem + "_thumb.jpg"))
    with tempfile.TemporaryDirectory() as td:
        frame = Path(td) / "f.jpg"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(a.at), "-i", str(v), "-frames:v", "1", "-q:v", "2", str(frame)], check=True)
        dims = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=p=0", str(v)],
                              capture_output=True, text=True, check=True).stdout.strip().split(",")
        vertical = int(dims[1]) > int(dims[0])
        W, H = (720, 1280) if vertical else (1280, 720)
        img = base64.b64encode(frame.read_bytes()).decode()
        lines = [html.escape(t.strip()) for t in a.text.split("|")][:3]
        fs = 120 if not vertical else 110
        spans = "".join(f'<div class="l{" acc" if i == a.accent else ""}">{t}</div>' for i, t in enumerate(lines))
        page = f"""<html><head><style>
body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;font-family:"Anton",Impact,sans-serif}}
.bg{{position:absolute;inset:0;background:url(data:image/jpeg;base64,{img}) center/cover}}
.sh{{position:absolute;inset:0;background:linear-gradient({'180deg' if vertical else '90deg'},rgba(0,0,0,.72) 0%,rgba(0,0,0,.35) 45%,rgba(0,0,0,0) 70%)}}
.t{{position:absolute;{'left:40px;right:40px;top:60px' if vertical else 'left:56px;top:50%;transform:translateY(-50%);width:62%'}}}
.l{{font-size:{fs}px;line-height:1.02;color:#fff;text-transform:uppercase;-webkit-text-stroke:6px #111;paint-order:stroke fill;
   text-shadow:0 8px 24px rgba(0,0,0,.6)}}
.acc{{color:{a.color}}}
</style></head><body><div class="bg"></div><div class="sh"></div><div class="t">{spans}</div></body></html>"""
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=chrome_path(), args=["--no-sandbox"])
            pg = b.new_page(viewport={"width": W, "height": H})
            pg.set_content(page)
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(out), type="jpeg", quality=88)
            b.close()
    print(out, out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
