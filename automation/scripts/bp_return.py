"""What if Jesus came back today? Believer's POV (owner's choice), our own scenes and words. Block POV format.
Sources: Matthew 24:27 (like lightning from east to west), 24:30 (every eye will see), 24:36 (no one knows the day or hour),
24:40 (one taken, one left); 1 Thessalonians 4:16-17 (trumpet; the dead in Christ rise first). World population about 8.2 billion."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, DAWN, DAY, GOLDEN, OVERCAST  # noqa: E402
from places import street  # noqa: E402

s = Story()
SKY = ["#5d86ad", "#e9dcc5"]; BRIGHT = ["#c9d8ff", "#fff6e0"]


def train(extra=(), window="#bcd3ea"):
    """Commuter train car: you sit at the back looking down the aisle (−z); seats both sides, windows glowing."""
    o = [O("box", (0, -0.02, -6), [3, 0.04, 16], "#6b6f78"), O("box", (0, 2.4, -6), [3, 0.05, 16], "#e9ecef"),
         O("box", (-1.5, 1.2, -6), [0.06, 2.4, 16], "#c9ced4"), O("box", (1.5, 1.2, -6), [0.06, 2.4, 16], "#c9ced4"),
         O("plane", (-1.46, 1.5, -6), [14, 0.8, 1], window, material="glow", rotate=[0, 90, 0]), O("plane", (1.46, 1.5, -6), [14, 0.8, 1], window, material="glow", rotate=[0, -90, 0]),
         O("box", (-1.05, 0.45, -6), [0.8, 0.9, 0.5], "#2f5f9e", count=8, seed=2, spread=[0, 0, 13]), O("box", (1.05, 0.45, -6), [0.8, 0.9, 0.5], "#2f5f9e", count=8, seed=3, spread=[0, 0, 13]),
         O("cylinder", (0, 1.2, -6), [0.04, 2.4, 0.04], "#d0d4d8", material="metal", count=4, seed=4, spread=[0, 0, 12]),
         O("plane", (0, 2.37, -6), [0.6, 0.3, 1], "#ffffff", material="glow", rotate=[90, 0, 0], count=5, seed=5, spread=[0, 0, 14])]
    return o + list(extra)


RIDERS = [guy((-1.05, 0.1, -1.6), "#e64980", "#3f4a5a", act="sit", face="neutral", seed=801, ry=90),
          guy((1.05, 0.1, -2.4), "#495057", "#212529", act="phone", face="neutral", seed=802, ry=-90),
          guy((-1.05, 0.1, -3.6), "#f59f00", "#3f4a5a", act="sit", face="neutral", seed=803, ry=90),
          guy((1.05, 0.1, -4.6), "#2f9e44", "#3f4a5a", act="sit", face="neutral", seed=804, ry=-90)]
SEATMATE = lambda act="sit", anim=(): guy((0.75, 0.1, -0.9), "#7048e8", "#3f4a5a", act=act, face="smile", seed=805, ry=210, anim=anim)
CAR = lambda extra=(), w="#bcd3ea", amb=1.4: env(train(list(extra), w), SKY, eye=(-0.4, 1.3, 1.9), amb="rumble", ambient=amb, light=1.8)
RETURNS = lambda sub="NOBODY KNOWS THE HOUR": T("HE RETURNS IN", scramble=True, sub=sub)

s.B(3.8, "eyes", "", CAR(RIDERS + [SEATMATE()]), tracker=RETURNS(), hands={"pose": "phone", "phone_text": "Running late again 🙄", "phone_time": "7:51"}, gaze=(0, -10))
s.B(3.4, "eyes", "7:52 AM. The train to work. Everyone's on their phone.", CAR(RIDERS + [SEATMATE()]), hands={"pose": "phone", "phone_text": "Running late again", "phone_time": "7:52"},
    gaze=(0, -2))
s.B(3.4, "eyes", "Across from you, a woman reads a small book. Smiling.", CAR(RIDERS + [SEATMATE()]), hands={"pose": "none"}, gaze=(28, -8))
s.B(3.6, "eyes", "Then a flash crosses your window. East to west.", CAR(RIDERS + [SEATMATE()], w="#ffffff", amb=1.9), tracker=T("HE RETURNS IN", value="00:00:00", sub="7:52 AM", alert=True),
    hands={"pose": "shield"}, gaze=(80, 6), effects=["flash", "shake"], sfx=[{"type": "thunder", "at": 0.2}])
s.B(3.6, "eyes", "\"As lightning comes from the east and shines to the west...\"", CAR(RIDERS + [SEATMATE()], w="#fff4d6", amb=1.8), by="Matthew 24:27", hands={"pose": "none"},
    gaze=(80, 8), effects=["bloom"])
LIGHT = [O("sphere", (0, 40, -90), 8, "#fffbe8", material="glow"), O("cone", (0, 40, -90), [40, 4, 40], "#fff3d0", material="glow", opacity=0.3)]
s.B(3.8, "eyes", "The train stops. Everyone looks up. Every eye on Earth.", env(street(seed=81, people=60, cars=3, extra=LIGHT), BRIGHT, eye=(0, 1.62, 2), amb="wind"),
    tracker=T("RIGHT NOW", value="8.2 BILLION", sub="PEOPLE SEE THE SAME THING"), hands={"pose": "none"}, gaze=(0, 34), effects=["rays", "bloom"])
s.B(3.6, "eyes", "A trumpet. You don't hear it with your ears. You feel it.", env(street(seed=81, people=60, cars=3, extra=LIGHT), BRIGHT, eye=(0, 1.62, 2), amb="wind"),
    hands={"pose": "none"}, gaze=(0, 26), effects=["shake", "rays"], sfx=[{"type": "swell", "at": 0.1, "dur": 3.2, "gain": 1.2}])
s.B(3.6, "eyes", "Around you, some fall to their knees. Some keep filming.", env(street(seed=82, people=0, cars=3, extra=LIGHT + [crowd(30, 821, at=(0, 0.12, -10), spread=(10, 0, 10), act="pray", ry=180),
                                                                                                           crowd(16, 822, at=(0, 0.12, -6), spread=(10, 0, 6), act="phone", ry=180)]),
                                                                       BRIGHT, eye=(0, 1.62, 2), amb="wind"), hands={"pose": "none"}, gaze=(0, -4))
UP = lambda x, z, seed, h: guy((x, 0.1, z), "#d8d8d8", None, act="float", face="smile", seed=seed, ry=180, anim=[{"type": "move", "to": [x, h, z]}])
s.B(3.6, "eyes", "Then the woman across from you starts to rise.", CAR(RIDERS + [SEATMATE("float", [{"type": "move", "to": [0.75, 1.6, -0.9]}])], w="#fff4d6", amb=1.8),
    tracker=T("RISING", count=(0, 2), unit=" m", decimals=1), hands={"pose": "reach"}, gaze=(28, 18), effects=["bloom"])
s.B(3.8, "eyes", "Outside your window, thousands are rising into the light.", env(street(seed=83, people=10, cars=2, extra=LIGHT + [UP(-4, -10, 831, 14), UP(3, -14, 832, 20), UP(-1, -22, 833, 26),
                                                                                                          UP(6, -8, 834, 9), UP(-6, -18, 835, 22)]), BRIGHT, eye=(0, 1.62, 2), amb="wind"),
    tracker=T("RISING", count=(2, 30), unit=" m"), hands={"pose": "none"}, gaze=(0, 30), effects=["rays"])
s.B(3.6, "eyes", "\"The dead in Christ will rise first.\"", env([O("box", (0, -0.03, -14), [80, 0.04, 60], "#5c8a3a"),
                                                                    O("box", (0, 0.4, -14), [0.8, 0.8, 0.2], "#adb5bd", count=24, seed=9, spread=[20, 0, 20]),
                                                                    O("box", (0, 10, -16), [0.18, 20, 0.18], "#fff3d0", material="glow", count=12, seed=9, spread=[20, 0, 20])] + LIGHT,
                                                                   BRIGHT, eye=(0, 4, 4), amb="wind"), by="1 Thessalonians 4:16", hands={"pose": "none"}, gaze=(0, -14), effects=["rays"])
s.B(3.6, "eyes", "Your phone: half your contacts stop answering.", CAR(RIDERS[1:2], w="#fff4d6", amb=1.7), hands={"pose": "phone", "phone_text": "Mom · No answer (6)", "phone_time": "7:58"},
    gaze=(0, -14), tracker=T("CALLS", count=(1, 6), sub="NO ANSWER"))
s.B(3.6, "eyes", "\"One will be taken. The other left.\"", CAR(RIDERS[1:2], w="#fff4d6", amb=1.6), by="Matthew 24:40", hands={"pose": "none"}, gaze=(28, -6))
s.B(3.6, "eyes", "Her book is still on the seat across from you.", CAR([O("box", (0.9, 0.94, -0.6), [0.18, 0.04, 0.24], "#7a1f1f")] + RIDERS[1:2], w="#fff4d6", amb=1.6),
    hands={"pose": "reach"}, gaze=(26, -22))
s.B(3.8, "eyes", "Nobody knew the day or the hour. Not even you.", CAR([] + RIDERS[1:2], w="#fff4d6", amb=1.5), tracker=T("HE RETURNED AT", value="7:52 AM", sub="A NORMAL TUESDAY", big=True),
    by="Matthew 24:36", hands={"pose": "none"}, gaze=(0, -4))

s.save("bp_return", "What if *Jesus* came back today?",
       "Believer's POV on a morning commuter train: lightning from east to west, every eye sees, a trumpet, people rising, one taken and one left, on a normal Tuesday.",
       "Which one would you be?", accent="#f2c94c", skin="#e0ac69", sleeve="#25324a", thumb="ONE TAKEN. ONE LEFT.", thumb_beat=8)
