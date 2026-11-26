import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, INDOOR
from assets import *
s = Story("_faces", "faces", accent="#4dabf7", look="film")
looks = [("light", "short", "dark", False, None), ("deep", "afro", "black", True, None), ("tan", "long", "auburn", True, None), ("medium", "buzz", "black", False, "full"),
         ("fair", "bun", "blonde", True, None), ("brown", "curly", "dark", False, "stubble")]
for i, e in enumerate(["smile", "happy", "shock", "sad", "angry", "smirk", "neutral", "scared", "tired", "laugh", "confused", "excited"]):
    sk, hs, hc, fem, bd = looks[i % 6]
    s.beat(1.0, e, Set(apartment(extra=[person((0, 0, -1.0), top=["#2f9e44", "#e03131", "#1c7ed6", "#f08c00"][i % 4], skin=sk, hair=hs, hair_color=hc, feminine=fem, beard=bd,
                                              expr=e, seed=i + 1, glasses=i == 4, earrings=fem)])), cam((0, 1.68, 0.0), (0, 1.62, -1.0)), hands="none")
s.save()
