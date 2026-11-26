import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, INDOOR
from assets import *
s = Story("_hands", "hands", accent="#4dabf7", look="film", skin=SKIN["medium"], sleeve="#1c7ed6", watch=True)
for h in "idle point reach hold wave shrug facepalm shield run cheer thumbsup fist peace stop offer phone wheel type grab count money".split():
    s.beat(1.0, h, Set(room(6, 6, 2.8, -3.5, panels=1), sky=INDOOR), cam((0, 1.5, 1.3), (0, 1.3, -3)), hands=h,
           screen=screen_ui(app="Bank", big="$3.12", sub="available balance") if h == "phone" else None)
s.save()
