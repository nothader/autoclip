"""What if your dog could talk for one day? 30 s Short. Real anchor: dogs know about 89 words/phrases on average (Reeve & Jacques, 2021)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, meter, DAY, SUNNY, NIGHT, INDOOR, DUSK  # noqa: E402
from assets import O, bean, dog, kitchen, park, supermarket, bedroom_kid, tv, coffee, money  # noqa: E402

s = Story("talking_dog", "What if your dog could talk for one day?", accent="#ffd43b",
          hook=["WHAT IF YOUR", "DOG", "COULD TALK?"], hook_accent=1, skin="#e0ac69", sleeve="#ff6b6b", mood="bouncy")
BUD = "#c08a4e"
DOGV = "am_onyx"
HEAD = lambda x, z, s=0.9, base=0.0: (x, base + 1.0 * s, z + 0.6 * s)   # bubble anchor above the dog's head


def living_room(extra=()):
    return [O("box", (0, -0.02, -2), [9, 0.04, 9], "#b98b5e"), O("box", (0, 1.6, -5.2), [9, 3.2, 0.1], "#ffe8cc"),
            O("box", (-4.5, 1.6, -2), [0.1, 3.2, 9], "#ffd8a8"), O("box", (0, 0.35, -3.4), [2.8, 0.7, 1.0], "#5c7cfa"),
            O("box", (0, 0.75, -3.85), [2.8, 0.8, 0.3], "#4c6ef5"), O("box", (2.6, 1.9, -5.1), [1.0, 1.4, 0.05], "#ffa94d"),
            O("cylinder", (-2.8, 0.6, -4.2), [0.5, 1.2, 0.5], "#69db7c"), O("sphere", (-2.8, 1.4, -4.2), 0.45, "#40c057")] + list(extra)


def vet_room(extra=()):
    return [O("box", (0, -0.02, -2), [8, 0.04, 8], "#dbe4ff"), O("box", (0, 1.6, -4.6), [8, 3.2, 0.1], "#e7f5ff"),
            O("box", (-4, 1.6, -2), [0.1, 3.2, 8], "#d0ebff"), O("box", (0, 0.45, -1.4), [1.8, 0.9, 1.0], "#ced4da", material="metal"),
            O("plane", (1.4, 2.0, -4.54), [1.2, 0.8, 1], "#a5d8ff", material="glow"),
            O("emoji", (-1.6, 2.2, -4.4), 0.7, text="🦴"), O("emoji", (1.6, 2.6, -4.4), 0.5, text="💉")] + list(extra)


# 0 — kitchen, 7 AM: the dog is staring. Hook, then the first words.
s.beat(3.4, "", Set(kitchen(seed=2, wall="#fff4e6") + dog((0, 0, -1.0), BUD, size=0.9) + coffee((0.9, 0.95, -4.0)) +
                    [O("emoji", (-1.6, 2.2, -4.3), 0.5, text="☀️")], sky=SUNNY, ambient=1.5, light=2.6),
       cam((0, 1.6, 1.4), (0, 0.6, -1.0)), hands="idle",
       say=[say("We need to talk.", DOGV, 2.65, who=HEAD(0, -1.0, 0.9), name="Biscuit", dur=1.0)], fx=["punch"])
# 1 — first complaint
s.beat(3.2, "his first words? a *complaint*", Set(kitchen(seed=3, wall="#fff4e6") + dog((0.3, 0, -1.2), BUD, size=0.9) +
                                                 [O("cylinder", (-0.4, 0.05, -0.9), [0.35, 0.1, 0.35], "#e03131"),
                                                  O("sphere", (-0.4, 0.1, -0.9), 0.05, "#8d6e4f", count=6, seed=4, spread=[0.18, 0.02, 0.18])],
                                                 sky=SUNNY, ambient=1.5, light=2.6),
       cam((0, 1.45, 1.2), (0, 0.5, -1.2)), hands="idle",
       say=[say("Dry food? AGAIN? I'm calling my lawyer.", DOGV, 0.2, who=HEAD(0.3, -1.2, 0.9), name="Biscuit")],
       stickers=[emoji("😐", 1.6, x=0.82, y=0.42)], fx=["whip"])
# 2 — park: he narrates every squirrel (you get dragged)
s.beat(3.2, "he narrates *every* squirrel", Set(park(seed=5, people=0) + dog((0, 0, -1.6), BUD, face_you=False, size=0.9) +
                                                [O("emoji", (1.8, 1.6, -5), 0.6, text="🐿️", animate=[{"type": "hop", "amount": 0.4, "speed": 1.4}]),
                                                 O("emoji", (-2.4, 2.4, -7), 0.6, text="🐿️", animate=[{"type": "hop", "amount": 0.3, "speed": 1.1}])],
                                                sky=DAY, ambient=1.4, light=2.6),
       cam((0, 1.55, 1.2), (0, 0.8, -4), to=(0, 1.55, -0.4), look_to=(0.4, 0.9, -6), head="run"), hands="reach",
       hold=[O("cylinder", (0.1, 0.0, 0.0), [0.05, 0.16, 0.05], "#e03131")],
       say=[say("SQUIRREL. Squirrel. That one owes me money.", DOGV, 0.2, who=(0.2, 1.5, -2.4), name="Biscuit", speed=1.15)],
       stickers=[meter("SQUIRREL RAGE", 0.2, 1.0, at=0.3, color="#ff6b6b")], fx=["whip"])
# 3 — vet: he lies
s.beat(3.2, "at the vet, he *lies*", Set(vet_room([bean((1.0, 0, -2.5), "#ffffff", expr="neutral", act="idle", hat="cap", hat_color="#4dabf7", seed=31, size=1.45,
                                                       talk=[(1.9, 0.9)])]) + dog((-0.2, 0.9, -1.4), BUD, size=0.75) +
                                     [O("box", (-0.05, 1.32, -0.85), [0.12, 0.06, 0.08], "#f8f9fa", rotate=[0, 0, 20])],
                                     sky=INDOOR, ambient=1.6, light=2.0, bounce="#dbe4ff"),
       cam((0, 1.6, 1.0), (0, 1.15, -1.6)), hands="idle",
       say=[say("I have never eaten a sock.", DOGV, 0.15, who=HEAD(-0.2, -1.4, 0.75, 0.9), name="Biscuit", dur=1.6),
            say("...there's a sock in your mouth.", "af_bella", 1.85, who=(1.0, 1.9, -2.5), name="Vet", dur=1.3, color="#d0ebff")],
       stickers=[label("🧦 THE SOCK", who=(-0.05, 1.32, -0.85), at=1.9, side="left"), stamp("LIAR", 2.4, rot=8, y=0.36)], fx=["whip"])
# 4 — supermarket: the real anchor
s.beat(3.3, "dogs really know about *89* words", Set(supermarket(seed=7) + dog((0, 0.55, -0.9), BUD, size=0.7) +
                                                    [O("box", (0, 0.42, -0.9), [0.9, 0.06, 0.7], "#adb5bd", material="metal"),
                                                     O("box", (0, 0.8, -1.25), [0.9, 0.7, 0.04], "#adb5bd", material="metal", opacity=0.6)],
                                                    sky=INDOOR, ambient=1.6, light=2.2, bounce="#e9ecef"),
       cam((0, 1.6, 0.9), (0, 0.9, -1.4), head="walk"), hands="reach",
       say=[say("Eighty of them mean snack.", DOGV, 0.9, who=HEAD(0, -0.9, 0.7, 0.55), name="Biscuit")],
       stickers=[badge("2021 study: ~89 words 🐶", at=0.2, title="REAL FACT")], fx=["whip"])
# 5 — living room: the outfit roast
s.beat(3.1, "he *roasts* your outfit", Set(living_room() + dog((0, 0.72, -3.1), BUD, size=0.8) + tv((2.6, 0, -4.3), "#74c0fc", 0.8) +
                                           [O("box", (0, 0.05, 0.2), [0.5, 0.02, 0.6], "#e64980")],
                                           sky=DUSK, ambient=1.4, light=2.2, bounce="#ffd8a8"),
       cam((0, 1.6, 0.6), (0, 1.0, -3.0)), hands="shrug",
       say=[say("Bold choice. Wrong. But bold.", DOGV, 0.2, who=HEAD(0, -3.1, 0.8, 0.72), name="Biscuit")],
       stickers=[emoji("💀", 1.6, x=0.8, y=0.28), floaty("-200 AURA", 1.2, color="#ff6b6b", y=0.58)], fx=["whip"])
# 6 — bedroom: he takes your bed
s.beat(3.1, "then he takes your *bed*", Set(bedroom_kid(seed=8, wall="#3b3b6b") + dog((-2.1, 0.62, -3.3), BUD, size=0.8) +
                                            [O("emoji", (1.0, 2.3, -4.6), 0.5, text="🌙")],
                                            sky=NIGHT, ambient=0.9, light=1.2, bounce="#3b3b6b", sun_color="#a5b4fc"),
       cam((-0.6, 0.55, -0.9), (-1.9, 0.9, -3.3)), hands="none",
       say=[say("Rent is due Friday.", DOGV, 0.3, who=HEAD(-2.1, -3.3, 0.8, 0.62), name="Biscuit")],
       stickers=[stamp("EVICTED", 1.6, color="#ff922b", rot=-8)], fx=["whip"])
# 7 — 11:59 PM: the soft twist
s.beat(3.4, "at *11:59* he says one more thing", Set(kitchen(seed=9, wall="#2b2d42") + dog((0, 0.46, -1.5), BUD, size=0.8) +
                                                     [O("plane", (0, 2.0, -4.43), [1.6, 1.0, 1], "#0b1430", material="glow"),
                                                      O("sphere", (0.3, 2.1, -4.38), 0.25, "#fff8e1", material="glow")],
                                                     sky=NIGHT, ambient=0.8, light=1.0, bounce="#2b2d42", sun_color="#ffd8a8"),
       cam((0, 1.25, 0.6), (0, 0.7, -1.9), fov=55), hands="reach",
       say=[say("Thanks for picking me. Out of all of them.", DOGV, 0.3, who=HEAD(0, -1.5, 0.8, 0.46), name="Biscuit", speed=0.9)],
       stickers=[emoji("🥺", 2.2, x=0.78, y=0.3)], fx=["zoomin"], tint="rgba(255,170,80,0.08)")
# 8 — midnight: woof. comment bait.
s.beat(3.2, "12:00. and then... *woof*.", Set(kitchen(seed=10, wall="#2b2d42") + dog((0, 0.46, -1.5), BUD, size=0.8) +
                                             [O("emoji", (0, 1.5, -2.4), 0.35, text="❤️", animate=[{"type": "bob", "amount": 0.06}])],
                                             sky=NIGHT, ambient=0.9, light=1.1, bounce="#2b2d42", sun_color="#ffd8a8"),
       cam((0, 1.25, 0.6), (0, 0.7, -1.9), fov=55), hands="reach",
       say=[say("Woof.", DOGV, 0.5, who=HEAD(0, -1.5, 0.8, 0.46), dur=1.0)],
       stickers=[floaty("+1000 GOOD BOY", 1.0, y=0.45), badge("What would YOUR dog say first? 👇", at=1.7, title="COMMENT BELOW", dur=1.5)])

s.save(tags=["what if your dog could talk", "talking dog", "what if", "pov", "funny dog", "dog thoughts", "alternative world", "dink dunk", "animation", "shorts"],
       description="Your dog gets ONE day to talk. He uses it to complain, lie at the vet and steal your bed. 🐶\n\nWhat would YOUR dog say first? 👇\n\n#whatif #dogs #funny",
       pinned="What would YOUR dog say first? 👇")
