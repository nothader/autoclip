"""What if you stood before Allah today? Believer's POV (owner's choice), our own scenes. Block POV format.
Sources: Qur'an 39:68 (the Trumpet is blown), 81:1-3 (the sun wrapped up, stars fall, mountains moved), 101:5 (mountains like carded wool),
39:69 (the earth shines with the light of its Lord), 69:19-25 (record given in the right hand or the left), 80:34-37 (a person flees from
their brother, mother and father). About 117 billion humans have ever lived (Population Reference Bureau estimate)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, DUSK, NIGHT  # noqa: E402
from places import terrace, plain  # noqa: E402

s = Story()
FAMILY = [guy((-0.9, 0, -1.6), "#c2255c", "#3f4a5a", act="sit", face="smile", seed=901, ry=200), guy((0.9, 0, -1.7), "#2b4f7a", "#3f4a5a", act="sit", face="smile", seed=902, ry=160),
          guy((0, 0, -2.6), "#f59f00", "#3f4a5a", act="sit", face="smile", seed=903, ry=180)]
TER = lambda extra=(), sky=DUSK, amb=1.3: env(terrace(seed=9, extra=list(extra)), sky, eye=(0, 1.35, 0.9), amb="calm", ambient=amb, light=1.7, stars=True)
WHITE = ["#8f8a9e", "#e8d9bd"]
DAY_T = T("THE LAST DAY", scramble=True, sub="ONLY ALLAH KNOWS THE HOUR")

s.B(3.8, "eyes", "", TER(FAMILY), tracker=T("TODAY", value="8:41 PM", sub="DINNER WITH FAMILY"), hands={"pose": "idle"}, gaze=(0, -10),
    voices=[("Pass the rice, habibi.", "af_heart", 0.6)])
s.B(3.4, "eyes", "8:41 PM. Dinner on the roof with your family.", TER(FAMILY), hands={"pose": "idle"}, gaze=(-20, -4))
s.B(3.6, "eyes", "One sound. Everywhere on Earth. At once.", TER(FAMILY), tracker=DAY_T, hands={"pose": "shield"}, gaze=(0, 20), effects=["shake"],
    sfx=[{"type": "swell", "at": 0.1, "dur": 3.2, "gain": 1.3}])
s.B(3.6, "eyes", "\"And the Trumpet will be blown.\"", TER(FAMILY), by="Qur'an 39:68", hands={"pose": "none"}, gaze=(0, 26), effects=["shake", "darken"])
STARS = [O("sphere", (0, 30, -80), 0.5, "#fff3d0", material="glow", count=30, seed=4, spread=[120, 40, 20], animate=[{"type": "move", "to": [0, -10, -80]}])]
s.B(3.6, "eyes", "The stars start to fall.", TER(FAMILY + STARS, NIGHT, 1.0), hands={"pose": "none"}, gaze=(0, 30), effects=["shake"])
WOOL = [O("sphere", (0, 20, -90), 8, "#e9e4da", count=8, seed=5, spread=[120, 20, 20], animate=[{"type": "drift", "axis": "y", "amount": 0.6}])]
s.B(3.6, "eyes", "The mountains fly apart like wool.", TER(STARS + WOOL, NIGHT, 1.0), by="Qur'an 101:5", hands={"pose": "none"}, gaze=(0, 16), effects=["shake"])
s.B(3.2, "eyes", "Your mother grabs your hand.", TER([FAMILY[0]], NIGHT, 1.0), hands={"pose": "reach"}, gaze=(-30, -6), voices=[("Hold on to me!", "af_heart", 0.3)])
s.B(3.0, "eyes", "Then nothing.", env([], ["#000000", "#05080c"], eye=(0, 1, 0), amb="none"), hands={"pose": "none"}, effects=["darken"])
s.B(3.6, "eyes", "A second blast. You open your eyes.", env(plain(seed=11, people=0), WHITE, eye=(0, 0.4, 1.0), amb="wind", ambient=1.4), hands={"pose": "none"}, gaze=(0, 10),
    effects=["bloom", "rays"], sfx=[{"type": "swell", "at": 0.2, "dur": 3}])
s.B(3.8, "eyes", "Every human who ever lived. Standing in rows.", env(plain(seed=12, people=200), WHITE, eye=(0, 1.62, 2), amb="wind", ambient=1.4),
    tracker=T("STANDING BEFORE ALLAH", count=(18_000_000_000, 117_000_000_000), sub="EVERY HUMAN WHO EVER LIVED"), hands={"pose": "none"}, gaze=(0, 0), head="walk")
s.B(3.6, "eyes", "Nobody speaks. You only hear footsteps.", env(plain(seed=13, people=200), WHITE, eye=(0, 1.62, 2), amb="wind", ambient=1.4), hands={"pose": "none"},
    head="walk", sfx=[{"type": "steps", "at": 0, "dur": 3.4}])
s.B(3.6, "eyes", "\"The earth shines with the light of its Lord.\"", env(plain(seed=14, people=120), WHITE, eye=(0, 1.62, 2), amb="wind", ambient=1.5), by="Qur'an 39:69",
    hands={"pose": "none"}, gaze=(0, 10), effects=["rays", "bloom"])
s.B(3.6, "eyes", "You see your mother. She looks at you. Then turns away.", env(plain(seed=15, people=60, extra=[guy((-0.8, 0, -1.6), "#c2255c", "#3f4a5a", act="walk", face="sad", seed=901, ry=20)]),
                                                                              WHITE, eye=(0, 1.62, 1), amb="wind", ambient=1.4), hands={"pose": "reach"}, gaze=(-24, 0))
s.B(3.6, "eyes", "On this day, everyone flees even their own family.", env(plain(seed=15, people=60), WHITE, eye=(0, 1.62, 1), amb="wind", ambient=1.4), by="Qur'an 80:34-36",
    hands={"pose": "none"}, gaze=(0, 0))
BOOK = [O("box", (0, 1.3, -0.75), [0.36, 0.05, 0.26], "#5c3a21", animate=[{"type": "move", "to": [0, 1.22, -0.55]}]), O("box", (0, 1.33, -0.75), [0.34, 0.02, 0.24], "#f1ece4",
                                                                                                                    animate=[{"type": "move", "to": [0, 1.25, -0.55]}])]
s.B(3.8, "eyes", "Your book arrives. Everything you ever did.", env(plain(seed=16, people=60, extra=BOOK), WHITE, eye=(0, 1.62, 1), amb="wind", ambient=1.4),
    tracker=T("YOUR RECORD", value="ARRIVING", sub="RIGHT HAND OR LEFT"), hands={"pose": "hold"}, gaze=(0, -24), effects=["bloom"])
s.B(3.6, "eyes", "Every prayer you made. Every one you skipped.", env(plain(seed=16, people=60, extra=BOOK), WHITE, eye=(0, 1.62, 1), amb="wind", ambient=1.4),
    hands={"pose": "hold"}, gaze=(0, -30), effects=["bloom"])

s.save("bp_allah", "What if you stood before *Allah* today?",
       "Believer's POV: a rooftop family dinner, the Trumpet, falling stars and mountains like wool, then every human who ever lived standing in rows, and your record arriving.",
       "Right hand or left hand?", accent="#f2c94c", skin="#8d5524", sleeve="#e9e4da", thumb="RIGHT HAND OR LEFT?", thumb_beat=14)
