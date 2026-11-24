"""What if your cat was secretly the boss of the house? 30 s Short.
Structure: a family meeting run by the cat, told as a numbered AGENDA (items 1-5), each item in a new room. Ending: cliffhanger (part 2?).
Real fact: cats recognise their owner's voice but often choose not to respond (Saito & Shinozuka, Animal Cognition 2013, Univ. of Tokyo).
Source: https://pubmed.ncbi.nlm.nih.gov/23525707/
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, meter, DAY, SUNNY, NIGHT, INDOOR, DUSK  # noqa: E402
from assets import (O, bean, cat, dog, gavel, cat_tower, living_room, bedroom_kid, kitchen, supermarket, classroom,  # noqa: E402
                    park, gift, full_moon, stars_field)

s = Story("cat_boss", "What if your cat was secretly the boss of the house?", accent="#e599f7",
          hook=["WHAT IF YOUR", "CAT", "WAS THE BOSS?"], hook_accent=1, skin="#8d5524", sleeve="#20c997", mood="sneaky")
FUR = "#f08c3c"
CATV = "bm_george"
NAME = "Lady Mittens"


def crown(at, size=0.13):   # gold band + 5 points (no gems; reads better at cat scale)
    x, y, z = at
    import math
    return [O("cylinder", (x, y, z), [size * 1.6, size * 0.6, size * 1.6], "#fcc419", material="metal")] + [
        O("cone", (x + math.sin(i / 5 * 6.283) * size * 0.65, y + size * 0.5, z + math.cos(i / 5 * 6.283) * size * 0.65), [size * 0.35, size * 0.6, size * 0.35],
          "#fcc419", material="metal") for i in range(5)]


def head(x, y, z, sz):   # bubble anchor just above the cat's head (cat faces you)
    return (x, y + 1.2 * sz, z + 0.55 * sz)


def boss(x, y, z, sz=0.9, face_you=True):
    c = cat((x, y, z), FUR, face_you=face_you, size=sz)
    return c + crown((x, y + 0.92 * sz, z + (0.55 if face_you else -0.55) * sz), 0.13 * sz / 0.9)


def agenda(n, at=0.15):
    return floaty(f"AGENDA ITEM {n}", at, color="#e599f7", y=0.62, size=58, dur=1.6)


# 0 — hook: the cat bangs a gavel on the coffee table, the whole family on the sofa
s.beat(3.4, "", Set(living_room(seed=1, wall="#ffe8cc", sofa="#5c7cfa") +
                    [O("box", (0, 0.22, -1.9), [1.4, 0.44, 0.8], "#8d6e57")] + boss(0, 0.44, -1.9) + gavel((0.42, 0.44, -1.6), banging=True) +
                    [bean((-0.9, 0.7, -4.1), "#ffa8a8", expr="scared", act="sit", hat="bun", seed=2, size=0.9),
                     bean((0.0, 0.7, -4.1), "#74c0fc", expr="shock", act="sit", hat="cap", hat_color="#1c7ed6", seed=3, size=0.9),
                     bean((0.9, 0.7, -4.1), "#ffe066", expr="neutral", act="sit", seed=4, size=0.7)],
                    sky=INDOOR, ambient=1.6, light=2.2, bounce="#ffe8cc", sun_dir=(2, 8, 8)),
       cam((0, 1.35, 0.6), (0, 0.95, -2.4)), hands="idle", fx=["punch"],
       say=[say("Order! This family meeting is now in session.", CATV, 2.35, who=head(0, 0.44, -1.9, 0.9), name=NAME, dur=1.0)],
       sfx=[{"type": "slam", "at": 0.25, "gain": 0.5}, {"type": "slam", "at": 0.6, "gain": 0.5}])
# 1 — item 1: breakfast is at 4 AM (you wake up, cat on your chest)
s.beat(3.2, "item 1: breakfast is now at *4 AM*", Set(bedroom_kid(seed=2, wall="#3b3b6b") + boss(0, 0.2, -1.3, 0.75) +
                                                      [O("box", (0, 0.1, -0.6), [1.6, 0.2, 2.2], "#f783ac"), O("emoji", (1.4, 2.2, -4.6), 0.5, text="🌙")],
                                                      sky=NIGHT, ambient=1.1, light=1.4, bounce="#5f5fa0", sun_color="#c5d0ff", sun_dir=(1, 6, 6)),
       cam((0, 0.85, 0.5), (0, 0.6, -1.3), fov=62), hands="shield", fx=["whip"],
       say=[say("It's four. I'm starving. RISE.", CATV, 0.4, who=head(0, 0.2, -1.3, 0.75), name=NAME, dur=1.6)],
       stickers=[agenda(1), label("⏰ 4:00 AM", x=0.25, y=0.3, at=0.3, side="left", dur=2.4), floaty("-3 HOURS SLEEP", 2.0, color="#ff6b6b", y=0.6)])
# 2 — item 2: the box stays (the fancy bed gets denied)
s.beat(3.2, "item 2: the $80 bed is *rejected*", Set(kitchen(seed=3, wall="#fff4e6") +
                                                    [O("box", (-0.35, 0.25, -1.8), [0.8, 0.5, 0.7], "#c8a27a"), O("box", (-0.35, 0.505, -1.8), [0.82, 0.01, 0.72], "#b08960")] +
                                                    boss(-0.35, 0.3, -1.75, 0.7) +
                                                    [O("cylinder", (0.75, 0.12, -1.4), [0.7, 0.24, 0.7], "#d0bfff"), O("cylinder", (0.75, 0.2, -1.4), [0.6, 0.1, 0.6], "#f3f0ff")],
                                                    sky=SUNNY, ambient=1.6, light=2.4, bounce="#fff4e6", sun_dir=(2, 8, 7)),
       cam((0.0, 1.3, 0.6), (-0.1, 0.65, -1.7)), hands="shrug", fx=["whip"],
       say=[say("The bed is decor. The box is my office.", CATV, 0.3, who=head(-0.35, 0.3, -1.75, 0.7), name=NAME)],
       stickers=[agenda(2), stamp("DENIED", 1.9, color="#ff6b6b", x=0.68, y=0.6, rot=8, size=140)])
# 3 — item 3: the laptop is a heated bed
s.beat(3.1, "item 3: your laptop is a *heated bed*", Set([O("box", (0, -0.02, -2), [8, 0.04, 8], "#a68a6d"), O("box", (0, 1.6, -3.4), [8, 3.2, 0.1], "#d3f9d8"),
                                                         O("box", (0, 0.72, -1.4), [1.8, 0.06, 0.9], "#e9ecef"), *[O("box", (sx * 0.8, 0.36, -1.4), [0.06, 0.72, 0.8], "#868e96") for sx in (-1, 1)],
                                                         O("box", (0, 0.76, -1.3), [0.7, 0.02, 0.45], "#343a40"), O("plane", (0, 0.98, -1.55), [0.66, 0.42, 1], "#74c0fc", material="glow", rotate=[-12, 0, 0]),
                                                         O("emoji", (-0.6, 1.1, -1.6), 0.25, text="☕"), O("plane", (1.6, 2.0, -3.34), [1.1, 0.8, 1], "#ffe066", material="glow")] +
                                                        cat((0.0, 0.66, -1.25), FUR, face_you=True, size=0.55) + crown((0, 1.16, -0.95), 0.08),
                                                        sky=DAY, ambient=1.6, light=2.2, bounce="#d3f9d8", sun_dir=(1, 8, 8)),
       cam((0, 1.45, 0.25), (0, 0.85, -1.3)), hands="shrug", fx=["whip"],
       say=[say("Your 9 AM call can wait. My nap can't.", CATV, 0.3, who=(0, 1.35, -0.95), name=NAME)],
       stickers=[agenda(3), label("your boss, muted", x=0.5, y=0.36, at=1.6, side="right", dur=1.4)])
# 4 — the real fact (a scientist with a chart)
s.beat(3.4, "Tokyo scientists *tested* this", Set(classroom(seed=4, kids=0, wall="#e3fafc", board="#1d3b4f",
                                                           extra=[bean((1.4, 0, -4.6), "#f8f9fa", expr="smirk", act="point", hat="hair", hat_color="#495057", seed=41, talk=[(0.2, 1.8)])]) +
                                                 [O("emoji", (-0.5, 1.7, -6.3), 0.8, text="🗣️"), O("emoji", (0.5, 1.7, -6.3), 0.5, text="➡️"), O("emoji", (1.3, 1.7, -6.3), 0.8, text="🙉")] +
                                                 cat((-1.2, 0, -4.0), "#adb5bd", face_you=True, size=0.7),
                                                 sky=INDOOR, ambient=1.7, light=2.0, bounce="#e3fafc", sun_dir=(1, 8, 8)),
       cam((0, 1.4, 0.2), (0.1, 1.2, -5.0)), hands="idle", fx=["whip"],
       say=[say("They know your voice. They just don't care.", "af_nicole", 0.25, who=(1.4, 1.95, -4.6), name="Dr. Purrcell")],
       stickers=[badge("Cats recognise YOUR voice... and ignore it 🐈 (2013 study)", at=1.7, title="REAL FACT", dur=1.6)])
# 5 — proof: you call her at dusk, she doesn't turn. Freeze.
s.beat(3.2, "so you test it *yourself*", Set(park(seed=5, grass="#5c940d", trees=6) + [O("box", (0, 0.5, -2.4), [6, 1.0, 0.12], "#e8d5b7")] +
                                             cat((0, 1.0, -2.3), FUR, face_you=False, size=0.95) + crown((0, 1.88, -2.82), 0.12),
                                             sky=DUSK, ambient=1.8, light=2.2, bounce="#ffc078", sun_dir=(0, 5, 9), sun_color="#ffd8a8"),
       cam((0, 1.5, 0.6), (0, 1.75, -2.3)), hands="wave", fx=["whip"],
       say=[say("Mittens! Dinner time!", "am_eric", 0.2, who=(0, 1.9, -1.0), name="You", dur=1.1)],
       freeze={"at": 1.7, "label": "she heard you. 100%."})
# 6 — item 4: tributes (she rides the cart and picks the salmon)
s.beat(3.1, "item 4: weekly *tributes*", Set(supermarket(seed=6) +
                                             [O("box", (0, 0.75, -0.9), [0.8, 0.5, 0.9], "#adb5bd", material="metal", opacity=0.75),
                                              *[O("cylinder", (sx * 0.3, 0.15, -0.9 + dz), [0.1, 0.08, 0.1], "#212529", rotate=[0, 0, 90]) for sx in (-1, 1) for dz in (-0.35, 0.35)],
                                              O("box", (0, 0.35, -0.9), [0.06, 0.5, 0.06], "#868e96"),
                                              O("emoji", (-0.2, 1.1, -1.1), 0.3, text="🐟"), O("emoji", (0.15, 1.1, -1.15), 0.3, text="🍣")] +
                                             boss(0, 0.95, -0.85, 0.55),
                                             sky=INDOOR, ambient=1.7, light=2.2, bounce="#e9ecef", sun_dir=(0, 8, 8)),
       cam((0, 1.6, 0.35), (0, 1.0, -1.1), head="walk"), hands="reach", fx=["whip"],
       say=[say("The FANCY salmon, peasant.", CATV, 0.3, who=head(0, 0.95, -0.85, 0.55), name=NAME)],
       stickers=[agenda(4), floaty("-$47.99", 1.8, color="#ff6b6b", x=0.7, y=0.55)])
# 7 — item 5: the vote (everyone votes no, motion passes anyway)
s.beat(3.2, "item 5: a *vote*", Set(living_room(seed=7, wall="#fff0f6", sofa="#4c6ef5") +
                                    [O("box", (0, 0.22, -1.9), [1.4, 0.44, 0.8], "#8d6e57")] + boss(0, 0.44, -1.9) + gavel((0.42, 0.44, -1.6)) +
                                    [bean((-0.9, 0.7, -4.1), "#ffa8a8", expr="angry", act="point", hat="bun", seed=2, size=0.9),
                                     bean((0.0, 0.7, -4.1), "#74c0fc", expr="angry", act="point", hat="cap", hat_color="#1c7ed6", seed=3, size=0.9),
                                     bean((0.9, 0.7, -4.1), "#ffe066", expr="sad", act="point", seed=4, size=0.7)] +
                                    dog((1.6, 0, -2.6), "#c08a4e", size=0.75),
                                    sky=INDOOR, ambient=1.6, light=2.2, bounce="#fff0f6", sun_dir=(2, 8, 8)),
       cam((0, 1.35, 0.6), (0, 0.95, -2.4)), hands="point", fx=["dutch"],
       say=[say("All against? Five. All for? Me. Motion passes.", CATV, 0.25, who=head(0, 0.44, -1.9, 0.9), name=NAME, dur=2.0)],
       stickers=[stamp("APPROVED", 2.3, color="#40c057", rot=-8, size=150)])
# 8 — cliffhanger: at the window, a SECOND crowned cat on the neighbour's fence
s.beat(3.5, "and then she looks *next door*", Set([O("box", (0, -0.02, -1), [6, 0.04, 4], "#b98b5e"), O("box", (-1.9, 1.6, -2.0), [1.6, 3.2, 0.1], "#ffe8cc"),
                                                    O("box", (1.9, 1.6, -2.0), [1.6, 3.2, 0.1], "#ffe8cc"), O("box", (0, 0.4, -2.0), [2.2, 0.8, 0.1], "#ffe8cc"),
                                                    O("box", (0, 2.9, -2.0), [2.2, 0.6, 0.1], "#ffe8cc"), O("box", (0, 0.85, -1.85), [2.3, 0.08, 0.4], "#f8f9fa"),
                                                    O("box", (0, -0.02, -9), [40, 0.04, 14], "#2b8a3e"), O("box", (0, 0.8, -8.5), [14, 1.6, 0.12], "#a0795a")] +
                                                   cat((0.5, 1.6, -7.6), "#495057", face_you=True, size=1.4) + crown((0.5, 2.9, -6.83), 0.18) +
                                                   boss(-0.3, 0.89, -1.8, 0.6, face_you=False) + full_moon((-6, 9, -40), 2.0) + stars_field(80, 4),
                                                   sky=NIGHT, ambient=1.3, light=1.6, bounce="#5f5fa0", sun_color="#c5d0ff", sun_dir=(0, 6, 9)),
       cam((0, 1.5, 0.6), (0, 1.25, -5)), hands="none", fx=["zoomin", "slowmo"],
       say=[say("Next meeting: we annex the neighbours.", CATV, 0.4, who=(-0.3, 1.85, -1.6), name=NAME, speed=0.9, dur=1.9)],
       stickers=[emoji("😼", 1.2, x=0.78, y=0.3, size=170), stamp("PART 2?", 2.5, color="#e599f7", rot=-6, y=0.55)])

s.save(tags=["what if your cat was the boss", "cat boss", "what if", "pov", "funny", "funny cats", "alternative world", "dink dunk", "animation", "cat logic", "shorts"],
       description="Your cat calls a family meeting. Breakfast is now at 4 AM, the box stays, and the vote is 5 against 1... motion passes. 😼\n\nWhat rule would YOUR cat add first? 👇\n\n#whatif #cats #funny",
       pinned="What rule would YOUR cat add first? 👇")
