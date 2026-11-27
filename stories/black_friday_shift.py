"""What if you worked retail on Black Friday? 30 s Short (film look).
Structure: TRAINING TAPE vs REALITY — every beat a cheerful "LESSON" from the 1998 training video, immediately disproved
(doors, stampede, TV aisle, endless checkout line, returns desk, stockroom, parking lot, break room). Cold open at the glass doors.
Ending: cliffhanger — the manager texts "same time tomorrow? 🙂" -> "PART 2?" stamp (not a freeze-frame callback like Thanksgiving).
Real fact: NRF — a record 202.9 million people shopped over Thanksgiving weekend 2025 (Thanksgiving Day through Cyber Monday).
Source: https://nrf.com/media-center/press-releases/thanksgiving-holiday-weekend-draws-a-record-203-million-shoppers
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, meter, INDOOR, DUSK, NIGHT  # noqa: E402
from assets import (O, person, people, screen_ui, screen_panel, text, lamp, room, grocery, counter, roast_turkey,  # noqa: E402
                    glass_doors, tv_wall, box_stack, parking_lot, car_real, apartment, table, chair)

ACC = "#fcc419"
s = Story("black_friday_shift", "What if you worked retail on Black Friday?", accent=ACC, look="film",
          hook=["WHAT IF YOU", "WORKED", "BLACK FRIDAY?"], hook_accent=2, skin="brown", sleeve="#c92a2a", mood="epic",
          grade={"tint": [1.0, 0.98, 1.04], "sat": 1.08, "contrast": 1.06})
from assets import SKIN  # noqa: E402
s.you["skin"] = SKIN["brown"]
CROWD, GRAN1, GRAN2, CUST, BOSS = "am_onyx", "bf_emma", "af_nicole", "am_puck", "af_sky"


def lesson(n, t, at=0.25):
    return badge(t, at=at, title=f"📼 TRAINING TAPE · LESSON {n}", dur=1.5)


# 1 — 4:59 AM, cold open: the crowd pressed against the glass
outside = people(9, 11, at=(0, 0, -3.5), spread=(3.0, 0, 0.9), acts=["angry", "point", "angry", "cheer", "panic", "angry", "point", "angry", "cheer"],
                 look="you", expr="angry")
s.beat(3.3, "4:59 AM. your *first* Black Friday", Set(glass_doors((0, 0, -2.6)) + outside, sky=NIGHT, sun_dir=(0, 6, 8), light=1.6, env=0.6, fill=1.2),
       cam((0, 1.6, 1.3), (0, 1.3, -3.3)), hands="idle",
       say=[say("OPEN THE DOOOORS!", CROWD, 1.4, who=(0.2, 2.1, -3.4), name="SOMEONE'S DAD", speed=1.1)],
       sfx=[{"type": "crowd", "at": 0.0}, {"type": "bonk", "at": 1.0}, {"type": "bonk", "at": 1.3}], fx=["shake"])
# 2 — 5:00 AM: doors open, stampede. LESSON 1
run_in = [dict(p, act="run", expr="excited", anim=[{"type": "move", "to": [0, 0, 3.0], "rel": True}]) for p in people(8, 12, at=(0, 0, -3.6), spread=(2.6, 0, 1.0), look="you")]
for p in run_in:
    p["animate"] = [{"type": "move", "to": [0, 0, 3.0], "rel": True}]
s.beat(3.2, "lesson 1: *greet* every guest", Set(glass_doors((0, 0, -2.6), open_=1.0) + run_in, sky=NIGHT, sun_dir=(0, 6, 8), light=1.6, env=0.6, fill=1.2),
       cam((0, 1.6, 1.0), (0, 1.3, -3.0), to=(0, 1.6, 1.5)), hands="none",
       stickers=[lesson(1, "Greet every guest with a smile 😊"), stamp("RUN.", 1.9, color="#ff6b6b", size=190)],
       sfx=[{"type": "whoosh", "at": 0.2}, {"type": "crowd", "at": 0.3}], fx=["slowmo", "shake"])
# 3 — electronics: one TV left, two grandmas
g1 = person((-0.55, 0, -2.3), top="#862e9c", outfit="coat", skin="fair", hair="bun", hair_color="white", feminine=True, age="elder", glasses=True,
            act="angry", expr="angry", ry=35, look=[0.55, 1.5, -2.3], talk=[(0.4, 1.0)], seed=61)
g2 = person((0.55, 0, -2.3), top="#2b8a3e", outfit="sweater", skin="deep", hair="curly", hair_color="grey", feminine=True, age="elder", earrings=True,
            act="point", expr="angry", ry=-35, look=[-0.55, 1.5, -2.3], talk=[(1.55, 1.1)], seed=62)
last_tv = [O("box", (0, 0.45, -2.75), [1.2, 0.9, 0.18], "#c8a27a"), text((0, 0.55, -2.65), "75\" TV\n$99", 0.9, 0.5, bg="#ffffff", fg="#c92a2a")]
s.beat(3.4, "*one* TV left. *two* grandmas.", Set(room(8, 8, 3.2, -3.6, "#e9ecef", "#ced4da", "tiles", "paint", panels=2)
                                                   + tv_wall((0, 0, -3.5), empty=[(0, 0), (1, 0), (2, 0), (3, 0), (1, 1), (2, 1)]) + last_tv + [g1, g2],
                                                   sky=INDOOR, sun_dir=(1, 8, 7), light=2.0),
       cam((0, 1.55, 0.6), (0, 1.2, -2.4)), hands="none",
       say=[say("I SAW IT FIRST!", GRAN1, 0.35, who=(-0.55, 1.95, -2.3), name="GRANDMA 1", dur=1.1),
            say("I SAW IT FIRSTER!", GRAN2, 1.5, who=(0.55, 1.95, -2.3), name="GRANDMA 2", dur=1.3)],
       stickers=[label("last one", who=(0, 0.95, -2.7), at=0.2, side="right", dur=1.0)], fx=["dutch"])
# 4 — checkout: the line goes forever. REAL FACT
line = [dict(p, act=a) for p, a in zip(people(10, 14, at=(-0.2, 0, -8.0), spread=(0.5, 0, 11.0), look="you"),
                                       ["idle", "phone", "cross", "idle", "hips", "phone", "idle", "cross", "idle", "phone"])]
s.beat(3.6, "the line goes to *Ohio*", Set(grocery(extra=line + [person((-0.2, 0, -2.4), top="#1971c2", outfit="hoodie", skin="olive", hair="side",
                                                                       act="hips", expr="bored", seed=71, hold="emoji:🧺")]), sky=INDOOR, sun_dir=(1, 8, 6), light=2.0),
       cam((1.3, 1.75, -0.2), (-0.3, 1.2, -8.0)), hands="none",
       stickers=[badge("202.9 million people shopped Thanksgiving weekend 2025", at=0.9, title="REAL FACT · NRF", dur=2.4),
                 label("Ohio →", who=(-0.3, 1.9, -13), at=0.3, side="left", dur=1.2)])
# 5 — returns desk: a turkey
ret = (room(7, 7, 3.0, -3.8, "#e7f5ff", "#ced4da", "tiles", "paint", panels=2)
       + counter((0, 0, -1.6), 2.4, 0.6, "#495057", "#dee2e6") + roast_turkey((0.15, 0.95, -1.6), 0.9)
       + [text((0, 2.3, -3.7), "RETURNS", 2.2, 0.5, bg="#1971c2", fg="#ffffff", lit=0.6),
          person((0.1, 0, -2.5), top="#e8590c", outfit="jacket", skin="light", hair="spiky", hair_color="ginger", beard="stubble", act="talk",
                 expr="smile", talk=[(0.3, 1.9)], seed=81)])
s.beat(3.2, "returns desk: a *turkey*", Set(ret, sky=INDOOR, sun_dir=(1, 8, 6), light=2.1),
       cam((-0.15, 1.6, 0.5), (0.05, 1.3, -2.2)), hands="none",
       say=[say("Hi! It's from yesterday. No receipt.", CUST, 0.3, who=(0.1, 1.95, -2.5), name="CUSTOMER", dur=1.9)],
       stickers=[stamp("NO.", 2.2, color="#ff6b6b", size=200)], sfx=[{"type": "boing", "at": 2.2}], fx=["punch"])
# 6 — stockroom: lunch break, 4 minutes
stock = (room(6, 6, 3.0, -3.2, "#adb5bd", "#868e96", "concrete", "concrete", panels=1) + box_stack((0, 0, -2.4), n=9, seed=3, color="#d9b38c")
         + [O("emoji", (0.15, 0.78, -0.4), 0.2, text="🥪"), lamp((0, 2.4, -1.4), "#fff3bf", 4, 5, hidden=True)])
s.beat(3.2, "lunch break: *4 minutes*", Set(stock, sky=INDOOR, sun_dir=(1, 8, 6), light=2.4, ambient=1.6),
       cam((0, 1.05, 0.9), (0, 0.85, -2.4), head="breathe"), hands="hold", hold=[O("emoji", (0, 0.05, 0), 0.16, text="🥪")],
       stickers=[floaty("⏱ 0:04", 0.2, color=ACC, y=0.16, size=72, dur=2.6), emoji("😭", 1.6, x=0.78, y=0.3, size=170)],
       sfx=[{"type": "tick", "at": t / 10} for t in range(4, 30, 5)])
# 7 — parking lot: the TV on a tiny car
roof_tv = [O("box", (0.8, 1.75, -4.6), [1.95, 1.15, 0.22], "#c8a27a", rotate=[90, 0, 0]),
           text((0.8, 1.88, -4.6), "75\"", 0.7, 0.35, bg="#c8a27a", fg="#212529", rot=(-90, 0, 0))]
s.beat(3.2, "lesson 7: *it's fun!*", Set(parking_lot(extra=car_real((0.8, 0, -4.6), "#f08c00", ry=0)[:6] + roof_tv
                                                     + [person((-0.6, 0, -3.4), top="#5c940d", outfit="hoodie", skin="tan", hair="buzz", act="cheer",
                                                               expr="excited", seed=91)]),
                                         sky=DUSK, sun_dir=(-5, 4, 6), light=2.0, sun_color="#ffc9a0", env=0.55, fill=1.1),
       cam((0.2, 1.7, 1.6), (0.75, 1.2, -4.4)), hands="none",
       stickers=[lesson(7, "Black Friday is FUN! 🎉", at=0.1), label("a 75\" TV", who=(0.8, 1.9, -4.6), at=1.4, side="right", dur=1.6),
                 label("a 2009 Honda", who=(0.8, 0.8, -4.0), at=1.9, side="left", dur=1.2)])
# 8 — break room, 11 PM: you collapse, the tape keeps playing
brk = (room(6, 6, 2.8, -3.2, "#d3c7b3", "#9c8f7f", "tiles", "paint", panels=1)
       + table((0, 0, -1.4), 1.2, 0.8, 0.75, "#adb5bd", tex=None)
       + [O("box", (0.9, 1.65, -3.0), [1.0, 0.75, 0.5], "#343a40", material="plastic"),
          screen_panel((0.9, 1.65, -2.74), 0.9, 0.64, screen_ui(app="📼 MEGAMART 1998", big="LESSON 8", sub="Smile! It's only 6 more weeks 😊", bg="#1864ab", fg="#ffffff")),
          O("emoji", (-0.2, 0.86, -1.3), 0.2, text="☕"), O("emoji", (0.25, 0.86, -1.5), 0.2, text="☕"), O("emoji", (0.0, 0.86, -1.2), 0.2, text="☕")])
s.beat(3.3, "11 PM. *it's over.*", Set(brk, sky=INDOOR, sun_dir=(1, 8, 6), light=1.6),
       cam((-0.3, 1.25, 0.4), (0.6, 1.45, -2.8), head="breathe"), hands="none",
       stickers=[meter("ENERGY", 0.25, 0.01, at=0.3, color="#ff6b6b", y=0.2, dur=2.6)], grade={"tint": [1.0, 0.95, 1.08], "sat": 0.85})
# 9 — cliffhanger: the manager texts
s.beat(3.3, "...right?", Set(brk, sky=INDOOR, sun_dir=(1, 8, 6), light=1.6),
       cam((-0.3, 1.25, 0.4), (0.4, 1.2, -2.8)), hands="phone",
       screen=screen_ui(app="Manager Deb", messages=[("them", "GREAT job today!!"), ("them", "Same time tomorrow? 🙂"), ("them", "and Cyber Monday 🙂🙂")],
                        time="11:02", accent="#c92a2a"),
       say=[dict(say("Same time tomorrow?", BOSS, 0.45, name="MANAGER DEB 📱", dur=1.6), x=0.5, y=0.56)],
       stickers=[stamp("PART 2?", 2.1, color=ACC, size=170)],
       sfx=[{"type": "notify", "at": 0.2}, {"type": "notify", "at": 1.0}], fx=["zoomin"])

s.save(tags=["what if you worked black friday", "black friday", "retail worker", "what if", "pov", "funny", "alternative world", "dink dunk",
             "animation", "retail"],
       description="Your first Black Friday shift. The training tape said smile. The grandmas said WAR. 🛒📺\n"
                   "Someone returned a turkey and your lunch break lasted 4 minutes.\n\nWhat's the WILDEST thing you've seen on Black Friday? 👇\n\n#blackfriday #whatif #funny",
       pinned="What's the WILDEST thing you've seen on Black Friday? 👇")
