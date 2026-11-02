"""Contact sheet: one still from the middle of every beat, tiled into one PNG (look at it before rendering).

    ./venv/bin/python automation/sheet.py automation/scripts/mars.json [out.png] [--frac 0.6]
"""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from PIL import Image  # noqa: E402
from backend.whatif.schema import Storyboard  # noqa: E402
from backend.whatif.model import compile_plan  # noqa: E402
from backend.whatif.render import render_stills  # noqa: E402


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    frac = float(sys.argv[sys.argv.index("--frac") + 1]) if "--frac" in sys.argv else 0.6
    src = Path(args[0])
    out = Path(args[1]) if len(args) > 1 and args[1].endswith(".png") else src.with_suffix(".sheet.png")
    sb = Storyboard.model_validate(json.loads(src.read_text()))
    plan = compile_plan(sb.model_copy(update={"pace": 1.8}))
    frames = [int((b["start"] + b["duration"] * frac) * plan["fps"]) for b in plan["beats"]]
    stills = render_stills(plan, Path(tempfile.mkdtemp(prefix="sheet-")), frames)
    land = sb.width > sb.height
    w, h = (320, 180) if land else (216, 384)
    cols = 6 if land else 7
    rows = (len(stills) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h))
    for i, p in enumerate(stills):
        sheet.paste(Image.open(p).convert("RGB").resize((w, h)), ((i % cols) * w, (i // cols) * h))
    sheet.save(out)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
