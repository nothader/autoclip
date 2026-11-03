"""What if kids made the rules for a day? (swap recipe, retro). Fact: ~2.4 billion children under 18 on Earth (UNICEF)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403

v = Video()
KID = lambda at, col="#fab005", act="idle", seed=6, ry=180, anim=(): P(at, col, act, seed, outfit="child", ry=ry, s=0.65, anim=anim)
kids = lambda n=10, seed=4, at=(0, 0, -6), spread=(10, 0, 8), act="walk": O("person", at, 0.65, "#fab005", outfit="child", count=n, seed=seed, spread=list(spread), action=act)
cls = room("#e7f5ff", "#d9c49a", w=12, d=12, extra=[O("box", (0, 0.72, -6), [0.9, 0.05, 0.6], "#8d6e57", count=8, seed=2, spread=[8, 0, 6]),
                                                    O("box", (0, 1.8, -11.9), [5, 1.6, 0.05], "#2b8a3e")])
v.B(4.4, "follow", "In 3 seconds, kids make every rule on Earth. For one whole day.", V(cls + [KID((0, 0.75, -6), act="point", anim=[{"type": "bob", "amount": 0.1, "speed": 2}]), kids(8, 4, act="idle"),
    P((0, 0, -10.5), "#868e96", "idle", 8, outfit="suit")], ["#e7f5ff", "#d0ebff"], focus=(0, 1.0, -7), zoom=1.0, bounce="#e7f5ff"), "+0 SEC", "7:00 AM",
    move="none", sfx=[{"type": "shimmer", "at": 3.0, "gain": 0.7}])
v.B(3.4, "wide", "There are 2.4 billion kids. But wait until you see rule 6.", V(park([kids(30, 7, at=(0, 0, -10), spread=(30, 0, 16), act="run")]), SKY, focus=(0, 1, -10), zoom=2.0),
    "+1 MIN", stat={"value": "2.4 BILLION", "label": "KIDS ON EARTH", "count_up": True}, effects=["confetti"])
kit = room("#fff3bf", "#c9a27a", extra=[O("box", (0, 0.75, -6), [2, 0.06, 1.2], "#8d6e57"),
           O("cone", (-0.4, 1.0, -6), [0.18, 0.4, 0.18], "#d9a066", rotate=[180, 0, 0]), O("sphere", (-0.4, 1.25, -6), 0.16, "#f783ac"),
           O("cone", (0.4, 1.0, -6), [0.18, 0.4, 0.18], "#d9a066", rotate=[180, 0, 0]), O("sphere", (0.4, 1.25, -6), 0.16, "#74c0fc")])
v.B(3.2, "follow", "Rule 1: ice cream for breakfast.", V(kit + [KID((-0.5, 0, -5.2), act="idle", ry=180), KID((0.6, 0, -5.2), "#e64980", "point", 9, ry=180, anim=[{"type": "bob", "amount": 0.08, "speed": 2.5}])],
    ["#fff3bf", "#ffd8a8"], focus=(0, 0.9, -5.6), zoom=0.7, bounce="#fff3bf"), "+7 AM", transition="whip")
v.B(3.2, "wide", "Rule 2: no more homework. Ever.", V(cls + [kids(8, 11, at=(0, 0, -6), spread=(8, 0, 6), act="run"),
    O("box", (0, 2, -6), [0.3, 0.02, 0.4], "#f8f9fa", count=14, seed=5, spread=[8, 2, 6], animate=[{"type": "drift", "axis": "y", "amount": 0.4}, {"type": "spin", "axis": "x", "speed": 3}])],
    ["#e7f5ff", "#d0ebff"], focus=(0, 1.0, -6), zoom=1.0, bounce="#e7f5ff"), "+8 AM", effects=["confetti"])
play = park([O("box", (-4, 1.2, -10), [0.2, 2.4, 0.2], "#e03131"), O("box", (-4, 2.4, -10), [3, 0.2, 0.2], "#e03131"),
             O("box", (4, 0.8, -12), [3, 0.1, 1], "#fab005", rotate=[0, 0, 25]), kids(16, 13, at=(0, 0, -10), spread=(16, 0, 10), act="run")])
v.B(3.2, "wide", "Rule 3: recess lasts all day.", V(play, SKY, focus=(0, 1, -10), zoom=1.6), "+10 AM", transition="whip")
corner = room("#ffe8cc", "#c9a27a", extra=[P((-3.5, 0, -9), "#868e96", "sit", 8, outfit="suit", ry=0), P((3.5, 0, -9), "#495057", "sit", 9, outfit="doctor", ry=0),
              KID((0, 0, -5), "#e64980", "walk", 9, ry=90, anim=[{"type": "move", "to": [2, 0, -5]}])])
v.B(3.4, "follow", "Grown-ups go to time-out. Including your boss.", V(corner, ["#ffe8cc", "#ffd8a8"], focus=(0, 1.0, -7), zoom=1.0, bounce="#ffe8cc"), "+12 PM")
dogs = [O("box", (x, 0.45, -6 + x * 0.3), [0.9, 0.5, 0.4], c, animate=[{"type": "bob", "amount": 0.08, "speed": 3}]) for x, c in ((-2, "#c08552"), (0, "#343a40"), (2, "#e9ecef"))]
v.B(3.2, "wide", "Rule 4: dogs come to school. Every dog.", V(cls + dogs + [kids(8, 15, at=(0, 0, -6), spread=(8, 0, 6), act="idle")], ["#e7f5ff", "#d0ebff"], focus=(0, 0.6, -6),
    zoom=0.7, bounce="#e7f5ff"), "+1 PM")
night = city([kids(14, 17, at=(0, 0, -14), spread=(10, 0, 14), act="run"), O("sphere", (0, 8, -20), 0.3, "#ffd43b", material="glow", count=16, seed=4, spread=[30, 6, 20])])
pj = city([crowd(12, 21, col="#9775fa", at=(0, 0, -14), spread=(10, 0, 14), outfit="robe"), kids(4, 22, at=(0, 0, -10), spread=(8, 0, 4))])
v.B(3.2, "wide", "Rule 5: grown-ups wear pajamas to work.", V(pj, GOLD, focus=(0, 1.4, -12), zoom=1.8), "+3 PM", transition="whip")
v.B(3.4, "far", "Here's the catch: Rule 6, bedtime is cancelled.", V(night, ["#1b2a5c", "#6c4ed6"], focus=(0, 1.4, -14), zoom=1.8), "+11 PM", transition="dip", effects=["confetti"])
couch = room("#3b2a6b", "#5c3d2e", win="#0b1d3a", extra=[O("box", (0, 0.4, -7), [4, 0.8, 1.2], "#7048e8"),
             O("person", (0, 0.6, -7), 0.65, "#fab005", outfit="child", count=4, seed=19, spread=[3, 0, 0.4], action="lie", animate=[{"type": "bob", "amount": 0.02, "speed": 0.6}])])
v.B(3.6, "follow", "By 2 AM, every kid falls asleep anyway. Rules are hard.", V(couch, ["#1b2a5c", "#6c4ed6"], focus=(0, 0.8, -7), zoom=0.9, bounce="#3b2a6b"), "+2 AM",
    sfx=[{"type": "breath", "at": 0.5, "dur": 2.6, "gain": 0.5}])
v.save("kids", "What if kids made the rules for a day?", "For one day, every rule on Earth is made by kids: ice cream breakfasts, no homework, recess all day.",
       "retro", "KIDS IN CHARGE", ["WHAT'S YOUR", "FIRST RULE?"], "KIDS MAKE *THE RULES*", 2, accent="#ffd43b", captions=None, countdown=True)
