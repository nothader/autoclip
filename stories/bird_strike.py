"""What if birds went on strike? 30 s Short.
Structure: LIVE news report (you're the field reporter holding a mic) with a DAY 1 -> DAY 7 counter. Ending: callback twist (the union boss is back with a new demand).
Real fact: a single barn swallow can eat about 60 insects an hour / ~850 a day (BirdNote, "Swallows Swallow").
Source: https://birdnote.org/node/11338
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, meter, DAY, SUNNY, NIGHT, INDOOR, MINT  # noqa: E402
from assets import (O, bean, bird, big_bird, bug, bug_swarm, picket_sign, picnic, beach, bedroom_kid, courtroom, park,  # noqa: E402
                    animate_all)

s = Story("bird_strike", "What if birds went on strike?", accent="#ffa94d",
          hook=["WHAT IF", "BIRDS", "WENT ON STRIKE?"], hook_accent=1, skin="#ffdbac", sleeve="#fab005", mood="chill")
GARY = "am_adam"
YOU = "am_michael"
PIGEON, PBELLY = "#868e96", "#dee2e6"
MIC = [O("cylinder", (0.13, -0.02, 0), [0.022, 0.13, 0.022], "#212529", rotate=[20, 0, 0]), O("sphere", (0.13, 0.055, -0.025), 0.03, "#adb5bd", material="metal")]
LIT = dict(sun_dir=(1, 7, 9))   # light the birds from the camera side


def street(extra=()):
    return [O("box", (0, -0.03, -6), [30, 0.04, 30], "#868e96"), O("box", (0, 0.0, -2.6), [30, 0.05, 4], "#ced4da"),
            O("box", (0, 2.5, -5.2), [14, 5, 0.2], "#ffc9c9"),
            O("plane", (-3, 2.8, -5.09), [0.9, 1.1, 1], "#a5d8ff", material="glossy"), O("plane", (3, 2.8, -5.09), [0.9, 1.1, 1], "#a5d8ff", material="glossy"),
            O("plane", (0, 3.8, -5.09), [5, 0.5, 1], "#ffa94d", material="glow"),
            O("cylinder", (-2.6, 1.6, -3.6), [0.08, 3.2, 0.08], "#495057"), O("sphere", (-2.6, 3.25, -3.6), 0.2, "#fff3bf", material="glow")] + list(extra)


def bubble_at(x, y, z, sz):
    return (x, y + 1.55 * sz, z + 0.1 * sz)


# 0 — hook: picket line, the union boss yells straight at you
s.beat(3.4, "", Set(street(big_bird((0, 0, -2.2), PIGEON, PBELLY, size=1.15, anim=[{"type": "bob", "amount": 0.06, "speed": 3}]) +
                           picket_sign((-0.8, 0.3, -2.0), emoji_text="✊", size=1.1) +
                           big_bird((-1.5, 0, -3.4), "#ff8787", "#ffe3e3", size=0.9, crest="#e03131") + picket_sign((-2.1, 0.3, -3.3), emoji_text="🚫", size=0.9) +
                           big_bird((1.7, 0, -3.6), "#4dabf7", "#e7f5ff", size=0.85)),
                    sky=SUNNY, ambient=1.5, light=2.4, **LIT),
       cam((0, 1.45, 0.9), (0, 1.15, -2.4)), hands="hold", hold=MIC, fx=["punch"],
       say=[say("NO WORMS, NO WORK!", GARY, 0.35, who=bubble_at(0, 0, -2.2, 1.15), name="Gary", speed=1.1, dur=1.6)],
       sfx=[{"type": "boing", "at": 0.3}])
# 1 — you're live: the interview, his demands
s.beat(3.3, "*BREAKING:* every bird quit today", Set(street(big_bird((0, 0, -1.6), PIGEON, PBELLY, size=1.0) + picket_sign((-0.7, 0.3, -1.45), emoji_text="✊", size=1.0) +
                                                           bird((-2.0, 2.6, -4.5), "#ff8787", size=0.35, count=6, seed=3, spread=(3, 0.6, 1))),
                                                    sky=SUNNY, ambient=1.5, light=2.4, **LIT),
       cam((0.2, 1.35, 0.5), (0, 1.0, -1.6)), hands="hold", hold=MIC, fx=["whip"],
       say=[say("We want dental. And bread. GOOD bread.", GARY, 0.3, who=bubble_at(0, 0, -1.6, 1.0), name="Gary, union boss")],
       stickers=[label("🔴 LIVE", x=0.16, y=0.12, at=0.1, side="left", color="#ff6b6b", dur=3.0)])
# 2 — DAY 1: the picnic gets taken over
s.beat(3.2, "*DAY 1:* the bugs notice", Set(picnic(seed=4, blanket="#4dabf7") + bug_swarm((0, 0.9, -2.6), 40, seed=5, spread=(3.5, 1.4, 2.5)) +
                                            bug((-0.3, 0.12, -1.3), "#2f9e44", size=0.42) + bug((0.4, 0.02, -1.15), "#e8590c", size=0.34) +
                                            bug((0.7, 0.4, -2.0), "#7048e8", size=0.25),
                                            sky=DAY, ambient=1.5, light=2.5, sun_dir=(1, 7, 8)),
       cam((0, 1.0, 0.2), (0, 0.3, -1.6)), hands="none", fx=["whip"],
       say=[say("Thanks for lunch!", "am_puck", 0.4, who=(-0.3, 0.45, -1.3), name="Bug", speed=1.25, dur=1.2)],
       stickers=[meter("BUG LEVEL", 0.3, 0.85, at=0.2, color="#69db7c"), floaty("-1 SANDWICH", 2.1, color="#ff6b6b", y=0.55)])
# 3 — DAY 2: the rooster refuses to crow (farmyard)
s.beat(3.2, "*DAY 2:* no alarm clock", Set([O("box", (0, -0.03, -10), [60, 0.04, 60], "#a9e34b"), O("box", (1.8, 1.6, -6), [3.4, 3.2, 2.6], "#e03131"),
                                            O("cone", (1.8, 3.9, -6), [3.2, 1.6, 2.8], "#c92a2a", rotate=[0, 45, 0]), O("box", (1.8, 0.9, -4.68), [1.2, 1.8, 0.05], "#f8f9fa"),
                                            O("box", (-0.8, 0.5, -2.6), [2.0, 0.08, 0.08], "#a0795a"), O("box", (-0.8, 0.25, -2.6), [0.08, 0.5, 0.08], "#a0795a"),
                                            O("sphere", (-5, 12, -40), 2.0, "#ffd43b", material="glow")] +
                                           big_bird((-0.8, 0.54, -2.6), "#f8f9fa", "#fff4e6", size=0.75, crest="#fa5252", beak="#fab005") +
                                           [O("emoji", (-0.2, 1.7, -2.6), 0.35, text="💤")],
                                           sky=SUNNY, ambient=1.5, light=2.5, sun_dir=(1, 7, 9)),
       cam((0, 1.4, 0.5), (-0.4, 1.0, -2.6)), hands="shrug", fx=["whip"],
       say=[say("Set your own alarm, Kevin.", "am_onyx", 0.3, who=(-0.8, 1.9, -2.5), name="Rooster", speed=0.9)],
       stickers=[floaty("😴 OVERSLEPT 4 HOURS", 1.9, color="#ffd43b", y=0.58, size=54)])
# 4 — the real fact on the beach: the swallow on a lifeguard tower doing nothing
s.beat(3.4, "turns out birds did a *lot*", Set(beach(seed=5) + [O("box", (0, 0.9, -2.6), [0.12, 1.8, 0.12], "#f8f9fa"), O("box", (0, 1.85, -2.6), [1.0, 0.1, 0.8], "#e03131")] +
                                               big_bird((0, 1.9, -2.6), "#1c3f94", "#ffd8a8", size=0.6, beak="#212529") +
                                               [O("emoji", (0.55, 2.55, -2.5), 0.3, text="🕶️")] + bug_swarm((0, 1.6, -3.2), 30, seed=8, spread=(4, 1.4, 2)),
                                               sky=SUNNY, ambient=1.5, light=2.6, sun_dir=(1, 7, 9)),
       cam((0, 1.5, 0.6), (0, 2.0, -2.6)), hands="idle", fx=["whip"],
       say=[say("I ate 850 bugs a day. For FREE.", "af_sky", 0.2, who=(0, 2.95, -2.5), name="Swallow")],
       stickers=[badge("One swallow can eat ~850 insects a day 🐦", at=1.7, title="REAL FACT", dur=1.6)])
# 5 — DAY 5: a giant mosquito-bug is your new roommate
s.beat(3.1, "*DAY 5:* you get a roommate", Set(bedroom_kid(seed=6, wall="#2f3b6b") + bug((-0.9, 0.6, -3.3), "#5c940d", size=1.4) +
                                               [O("emoji", (1.2, 2.3, -4.6), 0.5, text="🌙")],
                                               sky=NIGHT, ambient=1.3, light=1.7, bounce="#5f5fa0", sun_color="#d0d8ff", sun_dir=(0, 6, 9)),
       cam((0, 1.15, 0.4), (-0.8, 1.0, -3.2)), hands="shield", fx=["whip", "shake"],
       say=[say("Hi roomie. I'm on the left side.", "am_puck", 0.3, who=(-0.9, 1.9, -2.5), name="Doug", speed=1.1)],
       stickers=[emoji("😰", 2.0, x=0.8, y=0.32)])
# 6 — DAY 6: negotiations in court
s.beat(3.2, "*DAY 6:* the city gives in", Set(courtroom(seed=7) + [O("box", (0, 0.4, -2.0), [2.6, 0.08, 0.9], "#5c3a21")] +
                                              big_bird((0, 0.45, -2.6), PIGEON, PBELLY, size=0.95) + [O("emoji", (0.55, 0.52, -1.75), 0.3, text="📜")],
                                              sky=INDOOR, ambient=1.7, light=2.2, bounce="#d8c3a5", sun_dir=(1, 8, 9)),
       cam((0, 1.45, 0.3), (0, 1.15, -2.6)), hands="point", fx=["dutch"],
       say=[say("Fine! What do you want?", YOU, 0.15, who=(0, 2.7, -1.6), name="You", dur=1.1),
            say("Heated bird baths. Each.", GARY, 1.4, who=bubble_at(0, 0.45, -2.6, 0.95), name="Gary", dur=1.5)],
       stickers=[stamp("DEAL", 2.5, color="#40c057", rot=-7)])
# 7 — DAY 7: the flock returns, bugs vanish (slow-mo)
s.beat(3.2, "*DAY 7:* they're back", Set(park(seed=8, grass="#82c91e") +
                                         animate_all(bird((-3, 3.2, -5), "#4dabf7", size=0.5, count=14, seed=9, spread=(5, 1.5, 3)), [{"type": "move", "to": [4, 0.6, 1], "rel": True}]) +
                                         animate_all(bird((3, 2.2, -4), "#ff8787", size=0.45, count=8, seed=10, spread=(4, 1.0, 2)), [{"type": "move", "to": [-4, 0.8, 0.5], "rel": True}]) +
                                         bug_swarm((0, 1.4, -3), 25, seed=11, spread=(5, 1.5, 2)),
                                         sky=DAY, ambient=1.5, light=2.6, sun_dir=(1, 7, 8)),
       cam((0, 1.3, 0.6), (0, 2.6, -4.5)), hands="cheer", fx=["slowmo"],
       stickers=[floaty("BUGS: 0 ✅", 1.6, color="#69db7c", y=0.5, size=70)])
# 8 — callback: Gary is back at your picnic with a NEW sign
s.beat(3.5, "and then Gary *comes back*", Set(picnic(seed=4, blanket="#4dabf7") + big_bird((0.3, 0, -2.7), PIGEON, PBELLY, size=1.0) +
                                              picket_sign((-0.55, 0.3, -2.5), board="#d3f9d8", emoji_text="🍟", size=1.0),
                                              sky=DAY, ambient=1.5, light=2.5, sun_dir=(1, 7, 9)),
       cam((0, 1.35, 0.5), (0, 1.0, -2.6)), hands="hold", hold=MIC, fx=["zoomin"],
       say=[say("New strike. Fries are a human right.", GARY, 0.35, who=bubble_at(0.3, 0, -2.7, 1.0), name="Gary", dur=1.8)],
       stickers=[emoji("🍟", 2.2, x=0.78, y=0.3, size=170), label("he's not leaving", x=0.5, y=0.6, at=2.4, side="right", dur=1.0)])

s.save(tags=["what if birds went on strike", "birds on strike", "what if", "pov", "funny", "funny birds", "alternative world", "dink dunk", "animation", "pigeon", "shorts"],
       description="Every bird on Earth quits. Day 1 the bugs take your picnic. Day 5 one moves into your room. 🐦✊\n\nWhat would YOUR local birds demand? 👇\n\n#whatif #birds #funny",
       pinned="What would YOUR local birds demand? 👇")
