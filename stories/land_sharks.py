"""What if sharks could walk on land? 30 s Short.
Structure: MOCKUMENTARY — you're the wildlife cameraman (camcorder in hand), a hushed British narrator, species labels on every shark.
Ending: soft twist — a shark film crew is making a documentary about YOU (freeze-frame).
Real fact: epaulette sharks really "walk" on their fins across reef flats and can survive out of water for up to ~2 hours
(Smithsonian Magazine 2022; Wikipedia "Epaulette shark").
Sources: https://www.smithsonianmag.com/smart-news/this-shark-can-walk-on-land-to-survive-its-extreme-habitat-180980667/
         https://en.wikipedia.org/wiki/Epaulette_shark
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, SUNNY, DAY, INDOOR, NIGHT, DUSK  # noqa: E402
from assets import (O, bean, crowd, land_shark, mini_shark, fish, beach, supermarket, park, bedroom_kid, bus,  # noqa: E402
                    lifeguard_tower, camcorder, animate_all)

s = Story("land_sharks", "What if sharks could walk on land?", accent="#20c997",
          hook=["WHAT IF", "SHARKS", "COULD WALK?"], hook_accent=1, skin="#c68642", sleeve="#9c8455", mood="sneaky")
NARR = "bf_emma"
WHITE = "am_adam"
HAMMER = "am_michael"
GREY, HGREY = "#7b8a9a", "#8f9db0"
LIT = dict(sun_dir=(1, 7, 9))       # sharks face you -> light from the camera side
CAM = [dict(o, at=[o["at"][0] * 0.55 + 0.16, o["at"][1] * 0.55 - 0.1, o["at"][2] * 0.55 + 0.05],
            scale=[v * 0.55 for v in o["scale"]] if isinstance(o["scale"], list) else o["scale"] * 0.55) for o in camcorder()]


def head(x, z, size=1.0):
    return (x, 2.05 * size, z + 0.2)


def tag(text, x, z, size=1.0, at=0.5, side="right", dur=2.0):
    return label(text, who=(x, 1.7 * size, z), at=at, side=side, dur=dur, color="#c3fae8")


def street(extra=()):
    return [O("box", (0, -0.03, -6), [30, 0.04, 30], "#868e96"), O("box", (0, 0.0, -2.4), [30, 0.05, 3.6], "#ced4da"),
            O("box", (0, 2.5, -5.2), [14, 5, 0.2], "#d0ebff"),
            O("plane", (-2.6, 2.6, -5.09), [1.2, 1.4, 1], "#ffe066", material="glow"), O("plane", (2.6, 2.6, -5.09), [1.2, 1.4, 1], "#a5d8ff", material="glossy"),
            O("box", (0, 0.03, -3.6), [0.5, 0.02, 2.0], "#f8f9fa", count=1)] + list(extra)


# 0 — hook: you're on a beach towel; a shark walks OUT of the sea toward you
s.beat(3.3, "", Set(beach(seed=2) + [O("box", (0, 0.0, 0.0), [1.0, 0.02, 1.8], "#ff8787"), O("box", (0, 0.01, 0.0), [1.0, 0.01, 0.2], "#fff3bf")] +
                    animate_all(land_shark((0.2, 0, -4.4), GREY, anim=[{"type": "hop", "amount": 0.05, "speed": 1.4}]),
                                [{"type": "move", "to": [0, 0, 1.8], "rel": True}]),
                    sky=SUNNY, ambient=1.5, light=2.5, **LIT),
       cam((0, 1.0, 0.6), (0.1, 1.2, -3.0)), hands="idle", fx=["punch"],
       say=[say("Is this spot taken?", WHITE, 1.85, who=(0.2, 2.3, -2.4), name="Steve", dur=1.4)],
       sfx=[{"type": "thud", "at": 0.3}, {"type": "thud", "at": 0.8}, {"type": "thud", "at": 1.3}])
# 1 — narrator intro: the land shark, commuting
s.beat(3.3, "a nature documentary *nobody* asked for", Set(street(animate_all(land_shark((-1.3, 0, -2.6), GREY) + [O("box", (-0.7, 0.75, -2.5), [0.4, 0.3, 0.1], "#5c3a21")],
                                                                              [{"type": "move", "to": [1.6, 0, 0], "rel": True}, {"type": "hop", "amount": 0.04, "speed": 1.6}])),
                                                         sky=DAY, ambient=1.6, light=2.4, **LIT),
       cam((0, 1.5, 0.7), (0, 1.3, -2.6), head="walk"), hands="hold", hold=CAM, fx=["whip"],
       say=[say("Here we observe... the land shark.", NARR, 0.25, who=None, name="Narrator", speed=0.95, dur=1.9)],
       stickers=[tag("Great White · late for work", 0.3, -2.6, at=1.4, side="left", dur=1.8), label("🔴 REC", x=0.15, y=0.12, at=0.1, side="left", color="#ff6b6b", dur=3.2)])
# 2 — the supermarket fish counter (awkward)
s.beat(3.1, "it shops for *groceries*", Set(supermarket(seed=3) +
                                            [O("box", (0, 0.5, -1.3), [1.8, 1.0, 0.7], "#e9ecef", material="glossy"), O("box", (0, 1.02, -1.3), [1.8, 0.04, 0.7], "#d0ebff", material="glossy")] +
                                            fish((-0.4, 1.12, -1.2), "#ff922b", size=0.35) + fish((0.35, 1.12, -1.35), "#74c0fc", size=0.35) +
                                            land_shark((0, 0, -2.6), GREY, grin=False),
                                            sky=INDOOR, ambient=1.8, light=2.2, bounce="#e9ecef", sun_dir=(0, 8, 9)),
       cam((0, 1.45, 0.5), (0, 1.3, -2.4)), hands="hold", hold=CAM, fx=["dutch"],
       say=[say("...Uncle Kevin?!", WHITE, 0.4, who=head(0, -2.6), name="Steve", speed=0.9, dur=1.3)],
       stickers=[emoji("😬", 1.8, x=0.8, y=0.3, size=170)])
# 3 — the hammerhead vs the bus door
s.beat(3.2, "the hammerhead tries *public transport*", Set(street(bus((-2.6, 0, -5.0)) + land_shark((0.2, 0, -2.8), HGREY, hammer=True)),
                                                           sky=DAY, ambient=1.6, light=2.4, **LIT),
       cam((0.4, 1.5, 0.8), (0, 1.4, -2.8)), hands="hold", hold=CAM, fx=["whip"],
       say=[say("I'm not wide. The DOOR is narrow.", HAMMER, 0.3, who=head(0.2, -2.8), name="Hank")],
       stickers=[tag("Hammerhead · 9th bus missed", 0.2, -2.8, at=0.2, side="right", dur=1.6), stamp("TOO WIDE", 2.1, color="#ff6b6b", rot=-6, y=0.62, size=130, dur=1.0)])
# 4 — the real fact: a tide pool; a little epaulette shark walks toward you
s.beat(3.4, "but one shark was *already* doing it", Set([O("box", (0, -0.03, -6), [40, 0.04, 40], "#d9c08f"),
                                                         O("cylinder", (0, -0.01, -1.6), [3.0, 0.02, 2.4], "#66d9e8", material="glossy", opacity=0.8),
                                                         O("rock", (-1.2, 0.1, -2.2), 0.6, "#868e96"), O("rock", (1.3, 0.1, -1.8), 0.5, "#adb5bd"),
                                                         O("box", (0, -0.1, -30), [200, 0.1, 40], "#1c8fb5", material="glossy")] +
                                                        animate_all(mini_shark((0, 0, -2.2), "#d9b26a", size=0.9), [{"type": "move", "to": [0, 0, 0.4], "rel": True}]),
                                                        sky=SUNNY, ambient=1.6, light=2.6, **LIT),
       cam((0, 0.75, 0.4), (0, 0.2, -2.0)), hands="hold", hold=CAM, fx=["whip"],
       say=[say("The epaulette shark. Always been a walker.", NARR, 0.2, name="Narrator", speed=0.95, dur=2.0)],
       stickers=[badge("Epaulette sharks walk on their fins & last ~2 h out of water 🦈", at=1.0, title="REAL FACT", dur=2.2)])
# 5 — lifeguard duty (nobody dares to swim)
s.beat(3.1, "it gets a *summer job*", Set(beach(seed=5) + lifeguard_tower((0, 0, -3.4)) + land_shark((0, 1.66, -3.3), GREY, size=0.55),
                                          sky=SUNNY, ambient=1.6, light=2.6, **LIT),
       cam((0, 1.4, 0.6), (0, 2.4, -3.3)), hands="hold", hold=CAM, fx=["whip"],
       say=[say("Zero swimmers. Zero problems.", WHITE, 0.3, who=(0, 2.95, -3.0), name="Steve")],
       stickers=[floaty("🏆 SAFEST BEACH 2026", 1.9, color="#ffd43b", y=0.6, size=56)])
# 6 — the mako goes jogging (slow-mo)
s.beat(3.1, "it *never* stops moving", Set(park(seed=6, grass="#8ce99a", trees=8) +
                                           animate_all(land_shark((-1.4, 0, -3.0), "#4c6ef5", belly="#e7f5ff", anim=[{"type": "hop", "amount": 0.1, "speed": 2.2}]) +
                                                       [O("torus", (-1.4, 1.83, -3.0), [0.6, 0.6, 0.5], "#ff6b6b", rotate=[90, 0, 0])],
                                                       [{"type": "move", "to": [2.4, 0, 0], "rel": True}]),
                                           sky=DAY, ambient=1.5, light=2.5, **LIT),
       cam((0, 1.4, 0.6), (0, 1.2, -3.0)), hands="hold", hold=CAM, fx=["slowmo"],
       say=[say("Lap forty. Feeling GREAT.", "am_puck", 0.4, who=(0, 2.3, -2.8), name="Mako", speed=1.1, dur=1.4)],
       stickers=[tag("Mako · cardio addict", -0.2, -3.0, at=1.6, side="right", dur=1.4)])
# 7 — night: a dorsal fin glides across your bedroom floor
s.beat(3.2, "and bedtime got *complicated*", Set(bedroom_kid(seed=7, wall="#364fc7") +
                                                 [O("cylinder", (0, 0.01, -2.4), [3.6, 0.02, 2.8], "#1c7ed6", material="glossy", opacity=0.9),
                                                  *animate_all([O("cone", (-1.0, 0.4, -2.8), [0.3, 0.8, 0.7], "#495057", rotate=[0, 0, -15]),
                                                    O("sphere", (-1.0, 0.05, -2.5), [0.12, 0.09, 0.08], "#ffffff", material="glossy"),
                                                    O("sphere", (-0.82, 0.05, -2.5), [0.12, 0.09, 0.08], "#ffffff", material="glossy"),
                                                    O("sphere", (-1.0, 0.06, -2.43), 0.04, "#111111", material="glossy"),
                                                    O("sphere", (-0.82, 0.06, -2.43), 0.04, "#111111", material="glossy")],
                                                   [{"type": "move", "to": [1.6, 0, 0.2], "rel": True}]),
                                                  O("emoji", (1.6, 2.2, -4.6), 0.5, text="🌙")],
                                                 sky=NIGHT, ambient=1.4, light=1.8, bounce="#5f5fa0", sun_color="#d0d8ff", sun_dir=(0, 6, 9)),
       cam((0, 1.2, 0.3), (0, 0.3, -2.2)), hands="hold", hold=CAM, fx=["shake"],
       say=[say("Do not. Put a foot. Down.", NARR, 0.3, name="Narrator", speed=0.85, dur=1.8)],
       stickers=[emoji("😱", 1.9, x=0.8, y=0.3, size=170)])
# 8 — twist: you turn around... a shark film crew is filming YOU
s.beat(3.6, "plot twist: the *documentary*", Set(street(land_shark((0, 0, -3.0), "#495057", size=1.0) + land_shark((1.3, 0, -3.2), HGREY, size=0.85, hammer=True) +
                                                       [O("box", (0.3, 1.35, -2.55), [0.3, 0.26, 0.45], "#212529", material="glossy"),
                                                        O("cylinder", (0.3, 1.35, -2.3), [0.16, 0.14, 0.16], "#111111", rotate=[90, 0, 0]),
                                                        O("cylinder", (0, 2.02, -3.0), [0.7, 0.04, 0.7], "#c8a97e"), O("sphere", (0, 2.08, -3.0), [0.24, 0.14, 0.24], "#c8a97e"),
                                                        O("cylinder", (1.6, 2.7, -3.0), [0.05, 1.2, 0.05], "#495057", rotate=[0, 0, -30]),
                                                        O("capsule", (1.95, 3.25, -3.0), [0.18, 0.4, 0.18], "#343a40", rotate=[0, 0, 90])]),
                                                 sky=DUSK, ambient=1.7, light=2.3, bounce="#ffc078", sun_dir=(1, 6, 9), sun_color="#ffd8a8"),
       cam((0, 1.5, 0.5), (0.3, 1.4, -3.0)), hands="shrug", fx=["zoomin"],
       say=[say("And here... the rare human. In its natural habitat.", "bm_george", 0.3, who=head(0, -3.0), name="Sir Finnegan", speed=0.9, dur=2.2)],
       freeze={"at": 2.6, "label": "wait. it's about US?"})

s.save(tags=["what if sharks could walk on land", "walking sharks", "what if", "pov", "funny", "sharks", "alternative world", "dink dunk", "animation", "epaulette shark", "shorts"],
       description="Sharks can walk now. One's late for work, one can't fit on the bus, and one is the lifeguard. 🦈🚶\n\nWhich shark would YOU want as a neighbour? 👇\n\n#whatif #sharks #funny",
       pinned="Which shark would YOU want as a neighbour: Steve, Hank or the Mako? 👇")
