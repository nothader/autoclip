"""What if hell was real? Believer's POV (owner's choice), our own scenes. Block POV format.
Sources: Mark 9:48 (the fire is not quenched), Revelation 20:14-15 (the lake of fire), Luke 16:24 (the rich man begs for a drop of water),
Luke 16:26 (a great chasm fixed between), Matthew 25:41 (prepared for the devil and his angels), Revelation 14:11 (no rest day or night).
Kept non-graphic: fire, crowds, distance; no gore."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, NIGHT  # noqa: E402
from places import street  # noqa: E402

s = Story()
FIRE_SKY = ["#2a0a04", "#ff6a1a"]
CONCERT = street(seed=91, people=80, cars=0, extra=[O("sphere", (0, 6, -20), 0.15, c, material="glow", count=30, seed=k, spread=[20, 2, 30])
                                                    for k, c in ((1, "#ff4dd2"), (2, "#4dd2ff"), (3, "#ffe066"))])
FRIEND = guy((0.8, 0, -1.6), "#e8590c", "#212529", act="cheer", face="smile", seed=1001, ry=190)
LAKE = lambda n=200, extra=(): [O("box", (0, -0.05, -40), [400, 0.1, 400], "#3a1206"),
                                O("flame", (0, 0, -34), 1.4, "#ff7a1a", count=40, seed=11, spread=[70, 0, 40]),
                                O("particles", (0, 6, -20), 0.12, "#ffb347", count=200, seed=12, spread=[60, 12, 50], animate=[{"type": "drift", "axis": "y", "amount": 0.5}])] + \
                               ([crowd(min(n, 200), 13, at=(0, 0, -16), spread=(30, 0, 24), act="scared", face="shock", ry=180)] if n else []) + list(extra)
SINCE = lambda a, b: T("SINCE YOUR LAST HEARTBEAT", count=(a, b), unit=" s")
FOREVER = T("TIME LEFT", value="FOREVER", sub="YEARS PASSED: 0")

s.B(3.8, "eyes", "", env(CONCERT + [FRIEND], NIGHT, eye=(0, 1.62, 2), amb="calm", stars=True), tracker=T("FRIDAY", value="11:58 PM", sub="STREET FESTIVAL"),
    hands={"pose": "idle"}, gaze=(0, 6), voices=[("Let's go! One more song!", "am_puck", 0.5)])
s.B(3.4, "eyes", "One bang. In the middle of the party.", env(CONCERT + [FRIEND], NIGHT, eye=(0, 1.62, 2), amb="calm", stars=True), hands={"pose": "shield"}, gaze=(0, 0),
    effects=["flash", "shake"], sfx=[{"type": "boom", "at": 0.3}])
s.B(3.4, "eyes", "You see yourself lying on the street.", env(CONCERT + [guy((0, 0.1, -1), "#3b5bdb", "#25324a", act="lie", face="neutral", seed=1002)], NIGHT,
                                                            eye=(0, 4.5, 2.5), amb="wind", stars=True), tracker=SINCE(0, 4), hands={"pose": "none"}, gaze=(0, -55), head="float")
s.B(3.2, "eyes", "But you don't go up. You fall.", env([], ["#000000", "#1a0a04"], eye=(0, 1.6, 0), amb="rumble"), tracker=SINCE(4, 9), hands={"pose": "none"},
    head="fall", effects=["tunnel", "darken"], sfx=[{"type": "whoosh", "at": 0.1, "dur": 3}])
s.B(3.2, "eyes", "Deeper. It gets hotter every second.", env([O("particles", (0, 0, -6), 0.15, "#ff7a1a", count=150, seed=3, spread=[8, 30, 8], animate=[{"type": "drift", "axis": "y", "amount": 2}])],
                                                           FIRE_SKY, eye=(0, 1.6, 0), amb="rumble"), tracker=SINCE(9, 15), hands={"pose": "shield"}, head="fall", effects=["tunnel", "heat"])
s.B(3.8, "eyes", "A lake of fire. As far as you can see.", env(LAKE(0), FIRE_SKY, eye=(0, 12, 6), amb="rumble", ambient=1.2), by="Revelation 20:15", tracker=SINCE(15, 21),
    hands={"pose": "none"}, gaze=(0, -24), effects=["heat"])
s.B(3.6, "eyes", "Millions of people. Screaming.", env(LAKE(200), FIRE_SKY, eye=(0, 4, 4), amb="rumble", ambient=1.2), tracker=FOREVER, hands={"pose": "none"}, gaze=(0, -14),
    effects=["heat"])
s.B(3.6, "eyes", "\"The fire is never put out.\"", env(LAKE(120), FIRE_SKY, eye=(0, 1.62, 2), amb="rumble", ambient=1.2), by="Mark 9:48", hands={"pose": "shield"}, gaze=(0, 0),
    effects=["heat"])
s.B(3.6, "eyes", "You remember it all. Every chance you had.", env(LAKE(80), FIRE_SKY, eye=(0, 1.62, 2), amb="rumble", ambient=1.1), hands={"pose": "idle", "tremble": 0.8},
    gaze=(0, -20), effects=["heat"])
s.B(3.4, "eyes", "You beg for one drop of water.", env(LAKE(60), FIRE_SKY, eye=(0, 1.3, 2), amb="rumble", ambient=1.1), by="Luke 16:24", hands={"pose": "reach"}, gaze=(0, 20),
    effects=["heat"])
HEAVEN = [O("sphere", (0, 40, -260), 18, "#fff6dc", material="glow"), O("box", (0, -10, -120), [400, 0.1, 40], "#000000")]
s.B(3.6, "eyes", "Far away, you see heaven. Light. Music.", env(LAKE(40, HEAVEN), FIRE_SKY, eye=(0, 3, 2), amb="rumble", ambient=1.1), hands={"pose": "reach"}, gaze=(0, 6),
    effects=["bloom"])
s.B(3.6, "eyes", "A gap no one can cross.", env(LAKE(0, HEAVEN), FIRE_SKY, eye=(0, 3, 2), amb="rumble", ambient=1.1), by="Luke 16:26", hands={"pose": "none"}, gaze=(0, 0))
s.B(3.6, "eyes", "No rest. Day or night.", env(LAKE(150), FIRE_SKY, eye=(0, 1.62, 2), amb="rumble", ambient=1.1), by="Revelation 14:11",
    tracker=T("TIME LEFT", value="FOREVER", sub="YEARS PASSED: 1,000,000"), hands={"pose": "none"}, effects=["heat"])
s.B(3.6, "eyes", "It was made for the devil. Not for you.", env(LAKE(100), FIRE_SKY, eye=(0, 1.62, 2), amb="rumble", ambient=1.1), by="Matthew 25:41", hands={"pose": "none"},
    gaze=(0, 10), effects=["heat"])
s.B(3.8, "eyes", "And it never ends.", env(LAKE(200), FIRE_SKY, eye=(0, 6, 4), amb="rumble", ambient=1.1), tracker=T("TIME LEFT", value="FOREVER", big=True), hands={"pose": "none"},
    gaze=(0, -18), effects=["heat"])

s.save("bp_hell", "What if *hell* was real?",
       "Believer's POV: a street party, one bang, falling instead of rising; the lake of fire, begging for a drop of water and seeing heaven across a gap no one can cross.",
       "Do you believe it's real?", accent="#ff4b2b", skin="#c68642", sleeve="#212529", thumb="IT NEVER ENDS", thumb_beat=5)
