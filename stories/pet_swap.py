"""What if you swapped bodies with your dog for a day? 30 s Short.
Structure: VERSUS — a running scoreboard (NOODLE vs YOU), one "round" per venue; you're stuck in the dog's body (low camera, furry paws),
Noodle is in yours. Ending: comment bait (final score + "who wins?" badge), no twist.
Real fact: adult dogs sleep about 12-14 hours a day (Sleep Foundation, "How Much Do Dogs Sleep?").
Source: https://www.sleepfoundation.org/animals/how-much-do-dogs-sleep
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, DAY, SUNNY, INDOOR, DUSK  # noqa: E402
from assets import (O, bean, dog, kitchen, classroom, park, supermarket, hospital_hall, living_room, bedroom_kid,  # noqa: E402
                    dog_bowl, fire_hydrant, cone_of_shame, animate_all, phone)

ACC = "#3bc9db"
s = Story("pet_swap", "What if you swapped bodies with your dog?", accent=ACC,
          hook=["WHAT IF YOU", "SWAPPED BODIES", "WITH YOUR DOG?"], hook_accent=1, skin="#d9a066", sleeve="#b07a45", mood="epic")
NOODLE = "am_puck"      # Noodle (the dog) talking out of YOUR body
YOU = "am_eric"         # you, talking out of the dog
HOODIE = "#4c6ef5"      # your body = a blue bean in your hoodie
FUR = "#d9a066"
DOGCAM = 0.62           # you're dog height now
LIT = dict(sun_dir=(1, 7, 9))


def me(at, expr="happy", act="idle", ry=0, talk=(), size=1.0, anim=()):
    """Your body, now driven by Noodle: blue bean with your messy hair."""
    return bean(at, HOODIE, expr=expr, act=act, ry=ry, hat="hair", hat_color="#5c3a21", seed=11, talk=talk, size=size, anim=anim)


def score(n, y, at=0.15, dur=None):
    return stamp(f"NOODLE {n} – {y} YOU", at, color=ACC, x=0.5, y=0.2, rot=0, size=74, dur=dur or 2.9)


def top(x, z, size=1.0):   # bubble anchor above a bean
    return (x, 1.95 * size, z + 0.1)


# 0 — hook: low angle, looking UP at "you" happily eating out of the dog bowl
s.beat(3.3, "", Set(kitchen(seed=1, wall="#e3fafc") + [me((0, 0, -1.5), expr="love", act="idle", talk=[(0.3, 1.4)])] +
                    dog_bowl((0.05, 0.5, -1.05), size=1.2) +
                    [O("sphere", (0.1, 0.7, -0.95), 0.03, "#a0522d", count=6, seed=3, spread=[0.4, 0.2, 0.2], animate=[{"type": "fall", "floor": 0.02}])],
                    sky=SUNNY, ambient=1.6, light=2.3, bounce="#e3fafc", **LIT),
       cam((0, DOGCAM, 0.4), (0, 1.15, -1.5)), hands="idle", fx=["punch"],
       say=[say("Mmm! BEST cereal EVER!", NOODLE, 0.3, who=top(0, -1.5), name="You??", speed=1.15, dur=1.6)],
       sfx=[{"type": "boing", "at": 0.25}])
# 1 — the open loop: the mirror reveal + the bet
s.beat(3.4, "you woke up as *Noodle*", Set([O("box", (0, -0.02, -1), [6, 0.04, 6], "#c8b597"), O("box", (0, 1.5, -2.2), [6, 3, 0.1], "#d0ebff"),
                                            O("box", (0, 0.9, -2.12), [1.3, 1.8, 0.05], "#a0795a"), O("plane", (0, 0.9, -2.08), [1.15, 1.65, 1], "#e7f5ff", material="glossy", opacity=0.35)] +
                                           dog((0, 0, -2.6), FUR, face_you=True, size=0.9),
                                           sky=INDOOR, ambient=1.7, light=2.2, bounce="#d0ebff", sun_dir=(0, 6, 9)),
       cam((0, DOGCAM, 0.3), (0, 0.55, -2.4)), hands="shrug", fx=["whip"],
       say=[say("Why am I... FLUFFY?!", YOU, 0.2, who=(0, 1.2, -2.0), name="You", dur=1.2),
            say("First to ask for a swap back LOSES.", NOODLE, 1.55, who=(0.9, 1.5, -1.0), name="Noodle", dur=1.7)],
       stickers=[label("you. 🐶", who=(0.1, 0.75, -2.0), at=0.4, side="right", dur=1.3)])
# 2 — round 1: Noodle goes to YOUR school
s.beat(3.2, "round 1: Noodle does *your* school day", Set(classroom(seed=2, kids=6, wall="#fff3bf", extra=[me((0.3, 0, -1.9), expr="happy", act="cheer", ry=0, talk=[(0.3, 1.5)])]),
                                                          sky=INDOOR, ambient=1.7, light=2.1, bounce="#fff3bf", sun_dir=(1, 8, 9)),
       cam((-0.1, DOGCAM + 0.1, 0.6), (0.3, 0.9, -1.9)), hands="none", fx=["whip"],
       say=[say("I ate the homework. Legally.", NOODLE, 0.3, who=top(0.3, -1.9), name="Noodle", speed=1.15)],
       stickers=[score(1, 0, at=1.8, dur=1.4), floaty("+1 NOODLE", 1.9, color=ACC, y=0.62)])
# 3 — round 2: the dog park greeting (you refuse)
s.beat(3.1, "round 2: the dog park *greeting*", Set(park(seed=3, grass="#82c91e", trees=7) + fire_hydrant((0.9, 0, -1.6)) +
                                                    dog((-0.35, 0, -2.4), "#495057", face_you=True, size=0.95) + dog((1.8, 0, -3.4), "#f8f9fa", face_you=True, size=0.7),
                                                    sky=DAY, ambient=1.5, light=2.5, **LIT),
       cam((0, DOGCAM, 0.3), (0.0, 0.5, -2.2)), hands="idle", fx=["whip"],
       say=[say("Hey. Butt sniff?", "am_onyx", 0.25, who=(-0.35, 1.05, -1.8), name="Big Dave", dur=1.2),
            say("ABSOLUTELY not.", YOU, 1.45, who=(0.3, 1.15, -1.0), name="You", dur=1.0)],
       stickers=[stamp("AWKWARD", 2.0, color="#ffd43b", rot=-8, y=0.36, size=130, dur=1.0), score(2, 0, at=2.0, dur=1.0)])
# 4 — round 3 (you WIN): the nap. The real fact.
s.beat(3.4, "round 3: the *nap*", Set(bedroom_kid(seed=4, wall="#ffe8cc") +
                                      [O("cylinder", (0, 0.08, -0.9), [1.3, 0.16, 1.1], "#ffa8a8"), O("torus", (0, 0.16, -0.9), [0.62, 0.55, 0.6], "#ff8787", rotate=[90, 0, 0]),
                                       O("plane", (0.6, 0.2, -1.6), [1.4, 2.4, 1], "#fff3bf", material="glow", opacity=0.35, rotate=[-90, 0, 20]),
                                       O("emoji", (0.6, 1.0, -1.6), 0.3, text="💤", animate=[{"type": "bob", "amount": 0.08}]), O("emoji", (-0.5, 1.7, -4.6), 0.8, text="🕑")] +
                                      [me((1.1, 0, -3.3), expr="sad", act="facepalm")],
                                      sky=DAY, ambient=1.6, light=2.4, bounce="#ffe8cc", sun_dir=(3, 6, 6)),
       cam((0, 0.42, 0.1), (0.3, 0.6, -2.2)), hands="idle", fx=["slowmo"], tint="rgba(255,200,120,0.10)",
       stickers=[badge("Dogs sleep 12–14 hours a day 😴", at=0.5, title="REAL FACT", dur=1.7), floaty("+1 YOU (14 HRS!)", 2.0, color="#69db7c", y=0.5), score(2, 1, at=2.4, dur=1.0)])
# 5 — round 4: Noodle at the supermarket with YOUR card (you ride in the cart)
s.beat(3.1, "round 4: Noodle finds your *card*", Set(supermarket(seed=5) + [me((0, 0, -2.5), expr="love", act="cheer", talk=[(0.3, 1.5)])] +
                                                     [O("sphere", (0, 0.66, -0.75), 0.04, "#c0eb75", count=18, seed=6, spread=[0.6, 0.12, 0.4]),
                                                      O("box", (0, 0.6, -0.75), [0.9, 0.4, 0.8], "#adb5bd", material="metal", opacity=0.6)],
                                                     sky=INDOOR, ambient=1.7, light=2.2, bounce="#e9ecef", sun_dir=(0, 8, 8)),
       cam((0, 1.05, -0.2), (0, 0.95, -2.0), head="walk"), hands="idle", fx=["whip"],
       say=[say("ALL the tennis balls. ALL of them!", NOODLE, 0.3, who=top(0, -2.5), name="Noodle", speed=1.2)],
       stickers=[floaty("-$212 🎾", 1.6, color="#ff6b6b", x=0.7, y=0.55), score(3, 1, at=2.1, dur=1.0)])
# 6 — round 5: the vet — you're inside the cone of shame
VETPOS = (0, DOGCAM, 0.4)
s.beat(3.3, "round 5: Noodle books *your* vet visit", Set(hospital_hall(seed=6) + cone_of_shame(VETPOS) +
                                                          [bean((0.2, 0, -1.9), "#f8f9fa", expr="smirk", act="point", hat="hair", hat_color="#868e96", seed=21, talk=[(0.2, 1.4)]),
                                                           O("cylinder", (0.55, 1.05, -1.7), [0.05, 0.25, 0.05], "#a5d8ff", material="glossy", rotate=[0, 0, 60]),
                                                           me((-0.9, 0, -3.2), expr="happy", act="wave")],
                                                          sky=INDOOR, ambient=1.8, light=2.2, bounce="#e3f2ef", sun_dir=(0, 6, 9)),
       cam(VETPOS, (0.1, 0.95, -1.9)), hands="none", fx=["dutch", "punch"],
       say=[say("Just a tiny little shot!", "af_nicole", 0.25, who=top(0.2, -1.9), name="Dr. Pat")],
       stickers=[stamp("BETRAYED", 1.7, color="#ff6b6b", rot=8, y=0.34, size=130, dur=0.9), score(4, 1, at=2.4, dur=0.9)])
# 7 — round 6: Noodle finally catches the mailman (slow-mo, you watch from the window)
s.beat(3.2, "round 6: *6 years* of training pay off", Set(park(seed=7, grass="#69b34c", trees=6) +
                                                          [O("box", (0, -0.01, -4), [3, 0.03, 30], "#adb5bd"),
                                                           bean((1.3, 0, -4.4), "#1c7ed6", expr="scared", act="run", hat="cap", hat_color="#1864ab", seed=31,
                                                                anim=[{"type": "move", "to": [-0.4, 0, -1.6], "rel": True}]),
                                                           O("box", (1.55, 0.75, -4.25), [0.35, 0.25, 0.12], "#f8f9fa", animate=[{"type": "move", "to": [-0.4, 0, -1.6], "rel": True}]),
                                                           me((-0.4, 0, -2.2), expr="happy", act="run", anim=[{"type": "move", "to": [0.3, 0, -1.6], "rel": True}])],
                                                          sky=DAY, ambient=1.5, light=2.5, sun_dir=(0, 7, -2)),
       cam((0, 1.0, 1.2), (0.3, 1.0, -4.5)), hands="none", fx=["slowmo"],
       say=[say("COME BACK, MAIL GUY!", NOODLE, 0.3, who=(-0.2, 1.9, -3.0), name="Noodle", speed=1.2, dur=1.4)],
       stickers=[emoji("📬", 1.4, x=0.8, y=0.3, size=160), score(5, 1, at=2.2, dur=1.0)])
# 8 — the ending: sofa, sunset, Noodle won't give your body back. Comment bait.
s.beat(3.5, "and now he wants to keep *the thumbs*", Set(living_room(seed=8, wall="#fff4e6", sofa="#e8590c") +
                                                         [me((0.3, 0.4, -4.1), expr="smirk", act="sit", talk=[(0.3, 1.6)])] + phone((0.62, 0.95, -3.9), rot=(-20, 0, 0)),
                                                         sky=DUSK, ambient=1.6, light=2.0, bounce="#ffc078", sun_dir=(1, 6, 9), sun_color="#ffd8a8"),
       cam((0, DOGCAM, -1.4), (0.2, 0.95, -4.1)), hands="reach", fx=["zoomin"],
       say=[say("Thumbs are AMAZING. Not swapping.", NOODLE, 0.3, who=(0.3, 2.3, -4.0), name="Noodle", dur=1.7)],
       stickers=[score(5, 1, at=0.1, dur=2.0), badge("Should you ask to swap back? 👇", at=2.1, title="WHO WINS?", dur=1.4)])

s.save(tags=["what if you swapped bodies with your dog", "body swap", "what if", "pov", "funny", "funny dogs", "alternative world", "dink dunk", "animation", "dog pov", "shorts"],
       description="You wake up as your dog. Your dog wakes up as YOU... and he's winning. 🐶🔄\n\nScore's 5–1. Would YOU beg to swap back? 👇\n\n#whatif #dogs #funny",
       pinned="Final score 5–1 for Noodle. Would YOU beg to swap back? 👇")
