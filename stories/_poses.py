import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, INDOOR
from assets import *
part = int(sys.argv[1]) if len(sys.argv) > 1 else 0   # 0 or 1: first/second half of ACTS
s = Story(f"_poses{part}", "poses", accent="#4dabf7", look="film", skin=SKIN["fair"], sleeve="#495057")
acts = ACTS[part * 24:(part + 1) * 24]
for i, a in enumerate(acts):
    objs = room(6, 6, 2.8, -3.5, panels=1) + (chair((0, 0, -1.5), ry=0) if a.startswith("sit") else []) + \
        [person((0, 0, -1.5), top="#e03131", outfit="tshirt", hair="short", act=a, expr="smile", seed=3, talk=[(0, 1)] if a == "talk" else ())]
    s.beat(1.0, a, Set(objs, sky=INDOOR), cam((0.9, 1.3, 1.3), (0, 0.95, -1.5)), hands="none")
s.save()
