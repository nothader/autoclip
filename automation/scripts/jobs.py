"""What if couples had to switch jobs? (swap recipe, toon). Facts (US, rounded): ~9 in 10 registered nurses are women; ~9 in 10 construction
workers are men; nurses often work 12-hour shifts and can walk ~4 miles a shift."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403

v = Video()
home = [O("box", (0, -0.02, -10), [40, 0.04, 40], "#69a84f")] + house((0, 0, -12), "#ffe8cc", "#7a4a3a") + \
       [O("box", (0, 0.01, -6), [3, 0.02, 10], "#ced4da"), O("tree", (0, 0, -16), 1.4, "#3f8f3a", count=6, seed=3, spread=[24, 0, 6])]
HE = lambda act="idle", at=(-0.7, 0, -6), outfit="hivis", ry=180, anim=(): P(at, BOY, act, 2, outfit=outfit, ry=ry, anim=anim)
SHE = lambda act="idle", at=(0.7, 0, -6), outfit="scrubs", ry=180, anim=(): P(at, GIRL, act, 3, outfit=outfit, ry=ry, anim=anim)
v.B(4.4, "follow", "In 3 seconds, every couple on Earth switches jobs.", V(home + [HE(), SHE(), O("sphere", (0, 4, -12), 0.4, "#ffd43b", material="glow", animate=[{"type": "pulse", "amount": 0.3, "speed": 1}])], ["#74a9d8", "#fde2c4"], focus=(0, 1.2, -6), zoom=1.1), "+0 SEC", "6:30 AM",
    move="none", sfx=[{"type": "shimmer", "at": 3.0, "gain": 0.7}])
v.B(3.4, "side", "She's a nurse. He builds houses. But not for the next 30 days.", V(home + [HE(outfit="scrubs", ry=90), SHE(outfit="hivis", ry=270)], ["#74a9d8", "#fde2c4"], focus=(0, 1.2, -6),
    zoom=0.7), "+1 SEC", effects=["confetti"])
site = [O("box", (0, -0.02, -10), [50, 0.04, 40], "#c2a878"), O("box", (0, 3, -14), [8, 0.2, 6], "#adb5bd"), O("cylinder", (-3.6, 1.5, -14), [0.2, 3, 0.2], "#868e96", count=4, seed=1, spread=[8, 0, 6]),
        O("box", (6, 6, -16), [0.4, 12, 0.4], "#fab005"), O("box", (2, 11.8, -16), [8, 0.4, 0.4], "#fab005"),
        O("box", (-1, 9, -16), [1.4, 0.4, 0.4], "#868e96", animate=[{"type": "bob", "amount": 0.6, "speed": 1}]), crowd(5, 4, col="#fab005", at=(0, 0, -10), spread=(10, 0, 6), outfit="hivis")]
v.B(3.4, "wide", "She's on a roof by 7 AM. About 9 in 10 builders are men.", V(site + [P((0, 3.1, -14), GIRL, "point", 3, outfit="hivis", ry=180)], SKY, focus=(0, 2.5, -13), zoom=1.8),
    "+1 HOUR", transition="whip", stat={"value": "9 IN 10", "label": "US CONSTRUCTION WORKERS WHO ARE MEN", "count_up": False})
ward = room("#e7f5ff", "#dee2e6", w=12, d=12, extra=[O("box", (-3, 0.5, -8), [1.2, 0.7, 2.4], "#f8f9fa", count=3, seed=2, spread=[8, 0, 0]),
            P((3, 0, -4), "#40c057", "walk", 8, outfit="scrubs", ry=270, anim=[{"type": "move", "to": [-3, 0, -4]}])])
v.B(3.4, "dolly", "He starts a 12-hour nurse shift. About 9 in 10 nurses are women.", V(ward + [P((0, 0, -5), BOY, "walk", 2, outfit="scrubs", ry=180, anim=[{"type": "move", "to": [0, 0, -3]}])],
    ["#e7f5ff", "#d0ebff"], focus=(0, 1.2, -5), zoom=1.0, bounce="#e7f5ff"), "+2 HOURS", transition="whip")
v.B(3.4, "side", "Nurses can walk 4 miles a shift. His feet quit by lunch.", V(ward + [P((0, 0, -5), BOY, "kneel", 2, outfit="scrubs", ry=90, anim=[{"type": "wobble", "amount": 0.1, "speed": 2}])],
    ["#e7f5ff", "#d0ebff"], focus=(0, 1.0, -5), zoom=0.6, bounce="#e7f5ff"), "+6 HOURS")
fire = city([O("box", (4, 1.4, -16), [2.6, 2.8, 7], "#e03131"), O("box", (4, 3.1, -16), [0.3, 0.3, 6], "#adb5bd", material="metal", rotate=[30, 0, 0]),
             P((0, 0, -12), GIRL, "run", 5, outfit="hivis", ry=180, anim=[{"type": "move", "to": [0, 0, -8]}]),
             O("flame", (-6, 4, -24), 3, "#ff6b00")])
v.B(3.4, "far", "A teacher fights a fire. A firefighter teaches 30 kids.", V(fire, GOLD, focus=(0, 1.6, -14), zoom=1.8), "+1 DAY", transition="whip", effects=["smoke"])
kitch = room("#fff3bf", "#c9a27a", extra=[O("box", (0, 0.45, -9), [8, 0.9, 1], "#868e96"), O("box", (0, 0.92, -9), [8, 0.05, 1.05], "#f1f3f5"),
             O("cylinder", (1, 1.05, -9), [0.5, 0.2, 0.5], "#343a40", material="metal"),
             O("particles", (1, 1.6, -9), 0.3, "#495057", count=16, seed=4, spread=[1, 2, 1], animate=[{"type": "drift", "axis": "y", "amount": 0.5}])])
v.B(3.4, "follow", "At home, someone burns dinner. Nobody says who.", V(kitch + [HE("idle", (0.6, 0, -7.6), "casual", ry=0), SHE("point", (-1, 0, -6), "casual", ry=90)],
    ["#fff3bf", "#ffd8a8"], focus=(0, 1.2, -7.4), zoom=0.8, bounce="#fff3bf"), "+1 WEEK", effects=["smoke"])
v.B(3.4, "wide", "Here's the twist: by day 30, everyone begs to switch back.", V(home + [HE("kneel", outfit="scrubs"), SHE("kneel", outfit="hivis"),
    crowd(8, 19, at=(0, 0, -4), spread=(20, 0, 4), act="walk")], GOLD, focus=(0, 1.2, -6), zoom=1.6), "+30 DAYS", transition="dip")
v.B(3.6, "far", "But nobody ever says \"your job is easy\" again.", V(home + [HE("idle"), SHE("idle")], DUSK, focus=(0, 1.2, -6), zoom=2.0), "+1 YEAR", move="pull_out",
    effects=["glow"])
v.save("jobs", "What if couples had to switch jobs?", "Every couple swaps jobs for 30 days: a nurse on a building site, a builder on a 12-hour hospital shift.",
       "toon", "SINCE THE SWITCH", ["WHOSE JOB", "IS HARDER?"], "COUPLES *SWITCH* JOBS", 2, accent="#40c057", captions=None)
