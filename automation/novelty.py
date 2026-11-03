"""Novelty check: is this video visually and structurally different from the recent ones?

    ./venv/bin/python automation/novelty.py automation/scripts/<topic>.json [--recent 10]

Compares the new storyboard with the most recent other storyboards in automation/scripts/ on:
  - props    : the set of (object kind, colour) pairs used across all shots
  - skies    : background gradients
  - cameras  : the sequence of camera angles
  - opening  : first caption's first three words (e.g. "in 3 seconds")
  - style    : theme.style
  - ending   : end-card lines
Exits 1 with a list of overlaps if it is too similar to any recent video; fix the script, re-run.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "scripts"
PROPS_MAX = 0.45      # Jaccard similarity of (kind, colour) sets above this = too similar
SKIES_MAX = 0.5
CAMS_MAX = 0.7


def fingerprint(d):
    props, skies, cams = set(), set(), []
    for b in d.get("beats", []):
        cams.append(b.get("camera", ""))
        st = ((b.get("env") or {}).get("set") or {})
        bg = st.get("background")
        if isinstance(bg, list):
            skies.add(tuple(c.lower() for c in bg))
        for o in st.get("objects", []):
            props.add((o.get("kind"), str(o.get("color", "")).lower()))
    caps = [b.get("caption", "") for b in d.get("beats", []) if b.get("caption")]
    opening = " ".join(caps[0].lower().replace(",", "").split()[:3]) if caps else ""
    end = tuple(((d.get("outro") or {}).get("end") or {}).get("lines") or [])
    return {"props": props, "skies": skies, "cams": cams, "opening": opening,
            "style": (d.get("theme") or {}).get("style"), "end": end}


def jac(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 0.0


def seq_sim(a, b):
    n = min(len(a), len(b))
    return sum(x == y for x, y in zip(a, b)) / n if n else 0.0


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    recent = int(sys.argv[sys.argv.index("--recent") + 1]) if "--recent" in sys.argv else 10
    new = Path(args[0]).resolve()
    me = fingerprint(json.loads(new.read_text()))
    others = sorted((p for p in ROOT.glob("*.json") if p.resolve() != new and not p.name.endswith(".sheet.json")),
                    key=lambda p: p.stat().st_mtime, reverse=True)[:recent]
    problems = []
    for p in others:
        o = fingerprint(json.loads(p.read_text()))
        hits = []
        if jac(me["props"], o["props"]) > PROPS_MAX:
            hits.append(f"props {jac(me['props'], o['props']):.0%} the same")
        if me["skies"] and jac(me["skies"], o["skies"]) > SKIES_MAX:
            hits.append(f"skies {jac(me['skies'], o['skies']):.0%} the same")
        if seq_sim(me["cams"], o["cams"]) > CAMS_MAX:
            hits.append(f"camera sequence {seq_sim(me['cams'], o['cams']):.0%} the same")
        if me["opening"] and me["opening"] == o["opening"]:
            hits.append(f'same opening words "{me["opening"]}"')
        if me["end"] and me["end"] == o["end"]:
            hits.append("same end card")
        if hits:
            problems.append(f"{p.stem}: " + "; ".join(hits))
    if len(others) >= 2 and me["style"] and all(fingerprint(json.loads(p.read_text()))["style"] == me["style"] for p in others[:2]):
        problems.append(f'style "{me["style"]}" was used by the last two videos too (film is the house look; vary palette, sky and set instead)')
    if problems:
        print("TOO SIMILAR to recent videos:")
        for x in problems:
            print("  - " + x)
        return 1
    print(f"Novel enough vs the last {len(others)} videos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
