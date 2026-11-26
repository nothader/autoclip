"""What if you hosted Thanksgiving for the first time? 30 s Short (film look: real people, real places).
Structure: COUNTDOWN CLOCK through the day (6:00 AM -> 5:00 PM), one disaster per hour, each in a new place
(kitchen, frozen turkey close-up, couch, front door, living room, smoking oven, closed street, 24/7 diner).
Ending: callback twist — Mom's first text comes back: "same time next year?" -> freeze-frame "you're hosting again."
Real fact: USDA says thaw a turkey in the fridge for about 24 hours per 4–5 lb, so a 22 lb bird needs ~5 days.
Source: https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/poultry/turkey-basics-safe-thawing
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, meter, DAY, INDOOR, DUSK  # noqa: E402
from assets import (O, SKIN, person, people, screen_ui, text, lamp, room, kitchen_home, apartment, street, chair,  # noqa: E402
                    roast_turkey, oven, front_door, dining_table, menu_board, counter, window, plant)

ACC = "#ff922b"
s = Story("first_thanksgiving", "What if you hosted Thanksgiving for the first time?", accent=ACC, look="film",
          hook=["WHAT IF YOU", "HOSTED", "THANKSGIVING?"], hook_accent=1, skin=SKIN["olive"], sleeve="#2b8a3e", mood="bouncy",
          grade={"tint": [1.05, 1.0, 0.93], "sat": 1.1}, watch=True)
MOM, UNCLE, DAD, WAIT = "af_bella", "am_onyx", "am_michael", "af_nicole"


def clock(t, at=0.15):
    return floaty(t, at, color="#ffd8a8", x=0.5, y=0.12, size=60, dur=2.6)


# 1 — 6:00 AM, kitchen: Mom texts
s.beat(3.4, "your *first* time hosting", Set(kitchen_home(), sky=DAY, sun_dir=(2, 8, 6), light=2.2),
       cam((0.3, 1.6, 0.4), (-0.5, 1.1, -3.8)), hands="phone",
       screen=screen_ui(app="Mom ❤️", messages=[("them", "How big is the turkey?"), ("me", "22 lb 💪"), ("them", "Did you thaw it??")], time="6:00"),
       say=[dict(say("You thawed the turkey... right?", MOM, 0.45, name="MOM 📱", dur=2.6), x=0.5, y=0.56)],
       sfx=[{"type": "notify", "at": 0.2}, {"type": "notify", "at": 0.9}])
# 2 — frozen turkey close-up
s.beat(3.0, "the turkey is a *rock*", Set(kitchen_home(extra=roast_turkey((-0.8, 0.95, -3.85), 1.1, frozen=True)), sky=DAY, sun_dir=(1, 7, 8)),
       cam((-0.75, 1.5, -2.7), (-0.8, 1.0, -3.85), dof=True), hands="fist",
       stickers=[clock("6:01 AM", 0.1), stamp("FROZEN SOLID", 1.2, color="#74c0fc", y=0.36, size=130)],
       sfx=[{"type": "bonk", "at": 0.55}, {"type": "bonk", "at": 0.85}, {"type": "bonk", "at": 1.15}], fx=["punch"])
# 3 — couch, googling. REAL FACT
s.beat(3.4, "google says *five days*", Set(apartment(), sky=DAY, sun_dir=(3, 8, 6)),
       cam((0.3, 1.2, -3.5), (-3.9, 1.3, -2.0)), hands="phone",
       screen=screen_ui(app="🔍 thaw turkey fast", big="5 DAYS", sub="22 lb turkey, in the fridge", lines=["(it's Thursday)"], accent="#e03131"),
       stickers=[clock("8:00 AM", 0.05), badge("Fridge thaw: 1 day per 4–5 lb 🦃", at=1.2, title="REAL FACT · USDA", dur=2.0)])
# 4 — front door: uncle arrives 3 hours early
s.beat(3.3, "uncle Ray is *three hours* early", Set(front_door() + [
           person((0, 0, -2.9), top="#a61e4d", outfit="jacket", shirt="#e9ecef", skin="tan", hair="buzz", hair_color="grey", beard="full", beard_color="#868e96",
                  act="wave", expr="excited", hold2="emoji:🥧", talk=[(0.7, 1.7)], seed=21, build=1.25, belly=True)], sky=DAY, sun_dir=(-2, 6, 8), light=2.6),
       cam((0, 1.6, -0.6), (0, 1.5, -2.9)), hands="none",
       say=[say("I'm early! Where's the turkey?", UNCLE, 0.65, who=(0, 2.05, -2.9), name="UNCLE RAY")],
       stickers=[clock("11:00 AM", 0.05)], sfx=[{"type": "doorbell", "at": 0.0}])
# 5 — living room: everyone staring
fam = people(9, 77, at=(0, 0, -3.0), spread=(3.6, 0, 1.4), acts=["idle", "cross", "hips", "idle", "phone", "cross", "idle", "hips", "idle"], look="you", expr="neutral")
s.beat(3.2, "13 hungry relatives. *0* turkey.", Set(apartment(extra=fam), sky=DAY, sun_dir=(2, 8, 7)),
       cam((0, 1.62, 0.6), (0, 1.25, -3.0), to=(0, 1.62, 0.1)), hands="shrug",
       stickers=[clock("1:00 PM", 0.05), meter("HANGER LEVEL", 0.35, 0.97, at=0.6, color="#e03131", y=0.2)],
       sfx=[{"type": "tick", "at": t / 10} for t in range(8, 30, 3)])
# 6 — plan B: cook it frozen -> smoke alarm
s.beat(3.2, "plan B: cook it *frozen*", Set(kitchen_home(extra=oven((-0.45, 0, -3.1), on=True, smoke=True) + [
           person((0.5, 0, -2.5), top="#1864ab", outfit="sweater", skin="light", hair="side", hair_color="brown", glasses=True, act="panic", expr="scared", seed=31),
           lamp((-0.45, 0.6, -2.6), "#ff6b3d", 5, 4, hidden=True)]), sky=DAY, sun_dir=(2, 8, 7)),
       cam((0.05, 1.6, -0.9), (0.0, 1.15, -2.8), head="shake"), hands="point", fx=["shake"],
       say=[say("WHY IS IT SMOKING?!", DAD, 0.5, who=(0.5, 2.0, -2.5), name="DAD", speed=1.15)],
       stickers=[clock("2:00 PM", 0.05), stamp("NOPE", 1.8, color="#ff6b6b", x=0.33, y=0.4)], sfx=[{"type": "alarm", "at": 0.1}, {"type": "alarm", "at": 1.4}],
       grade={"tint": [1.12, 0.94, 0.9]})
# 7 — every store closed
closed = [text((3.7, 0.75, -3.6), "CLOSED", 0.9, 0.45, bg="#e03131", fg="#ffffff", rot=(0, -20, 0)),
          text((2.3, 0.75, -7.2), "CLOSED", 0.9, 0.45, bg="#e03131", fg="#ffffff", rot=(0, -10, 0)),
          text((-5.2, 1.4, -9.5), "DINER\nOPEN 24/7", 1.8, 0.9, bg="#212529", fg="#ffd43b", lit=1.4, rot=(0, 30, 0))]
s.beat(3.2, "every store: *closed*", Set(street(extra=closed), sky=DUSK, sun_dir=(-6, 4, -4), light=1.8, sun_color="#ffb38a", env=0.45),
       cam((3.2, 1.6, 1.0), (2.8, 1.1, -8), look_to=(-2.6, 1.4, -9)), hands="shrug",
       stickers=[clock("3:00 PM", 0.05), label("closed", who=(3.7, 1.0, -3.6), at=0.4, side="left", dur=1.2),
                 label("ALSO closed", who=(2.3, 1.0, -7.2), at=0.9, side="left", dur=1.2), label("...wait 👀", who=(-5.2, 1.6, -9.5), at=2.0, side="right", dur=1.2)])
# 8 — the diner saves Thanksgiving
diner = (room(8, 8, 3.0, -5.0, "#f3e9dc", "#e9ecef", "tiles", "paint", panels=2)
         + dining_table((0, 0, -2.4), 3.0, cloth="#ffffff")
         + [menu_board((0, 2.1, -4.92), items=("TURKEY PLATE  $12", "PANCAKES  $8", "PIE (ALL OF IT)  $6"), w=2.6, h=1.2),
            text((2.8, 2.2, -4.9), "OPEN 24/7", 1.4, 0.4, bg="#212529", fg="#ff6b9d", lit=1.6), lamp((0, 2.2, -2.4), "#ffe3bf", 5, 6, hidden=True)]
         + [O("emoji", (x, 0.92, z), 0.22, text=e) for x, z, e in ((-0.35, -1.55, "🥞"), (0.35, -2.3, "🦃"), (-0.35, -3.05, "🥧"), (0.35, -1.55, "🍟"))])
seated = [person((x * 0.82, 0, z), top=c, skin=sk, hair=h, hair_color=hc, feminine=f, act="sit_eat" if k % 2 else "cheer", ry=90 if x < 0 else -90,
                 look="you", expr="happy", seed=40 + k, age=a)
          for k, (x, z, c, sk, h, hc, f, a) in enumerate([(-1, -1.55, "#e64980", "fair", "bob", "blonde", True, "adult"), (1, -1.55, "#a61e4d", "tan", "buzz", "grey", False, "adult"),
                                                           (-1, -2.3, "#f08c00", "deep", "curly", "black", False, "teen"), (1, -2.3, "#1864ab", "light", "side", "brown", False, "adult"),
                                                           (-1, -3.05, "#5c940d", "brown", "ponytail", "dark", True, "kid"), (1, -3.05, "#862e9c", "medium", "bun", "grey", True, "elder")])]
s.beat(3.3, "Thanksgiving at the *diner*", Set(diner + seated, sky=INDOOR, sun_dir=(2, 8, 6), light=2.0),
       cam((0, 1.75, 1.8), (0, 1.0, -2.4)), hands="thumbsup",
       stickers=[clock("4:30 PM", 0.05), badge("Everyone got fed 🙌", at=1.0, title="ACHIEVEMENT UNLOCKED")], sfx=[{"type": "crowd", "at": 0.3}])
# 9 — callback twist: Mom
mom = person((0.55, 0, -1.25), top="#c2255c", outfit="sweater", skin="olive", hair="bob", hair_color="dark", feminine=True, earrings=True,
             act="sit_talk", ry=-90, expr="happy", talk=[(0.3, 1.9)], seed=51)
s.beat(3.3, "", Set(diner + seated[1:] + [mom] + chair((0.82, 0, -1.25), "#343a40", ry=-90)[:2], sky=INDOOR, sun_dir=(2, 8, 6), light=2.0),
       cam((-0.1, 1.45, -0.3), (0.55, 1.35, -1.25), dof=True), hands="idle",
       say=[say("Great job, honey! Same time next year?", MOM, 0.3, who=(0.55, 1.6, -1.25), name="MOM", dur=2.0)],
       freeze={"at": 2.3, "label": "you're hosting again."})

s.save(tags=["what if you hosted thanksgiving", "thanksgiving", "first thanksgiving", "what if", "pov", "funny", "alternative world", "dink dunk", "animation", "family"],
       description="Your first Thanksgiving as host. The turkey is a rock, Uncle Ray is 3 hours early and the oven is on fire.\n"
                   "Plan Z: the 24/7 diner. 🦃\n\nWho ALWAYS ruins Thanksgiving in your family? 👇\n\n#whatif #thanksgiving #funny",
       pinned="Who ALWAYS ruins Thanksgiving in your family? 👇")
