"""LONG-FORM (16:9): What if the power went out for a week in the coldest week of winter? Block POV, fictional town (Cedar Falls).
Trend link: winter cold snaps + the 2026 fight over grid demand and AI data centers.
Anchors (widely reported): Feb 2021 Texas winter storm left about 4 million customers without power; Texas health officials counted
246 storm-related deaths, most from hypothermia; generators and grills must never run indoors (carbon monoxide);
running a little water keeps pipes from freezing; data centers are a fast-growing share of US power demand (IEA / EIA)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd  # noqa: E402
from places import street, church  # noqa: E402

s = Story()
SNOWSKY = ["#5d6f8c", "#cfd8e3"]; NIGHTSNOW = ["#0e1424", "#2e3b55"]; GREYDAY = ["#7d8896", "#dfe4ea"]; DAWNCOLD = ["#6a7fb0", "#f2d2c0"]
INSIDE = ["#1c1f26", "#3a3f48"]
SNOW = {"weather": "snow", "cover": 0.8}

def E(objs, sky, eye=None, focus=(0, 1.5, -3), zoom=1.0, amb="room", light=2.0, ambient=1.3, snow=False, bounce="#d8d0c4"):
    e = env(objs, sky, eye=eye, focus=focus, zoom=zoom, amb=amb, light=light, ambient=ambient, bounce=bounce)
    if snow:
        e.update(SNOW)
    return e


def room(lit=True, extra=(), wall="#e6d6bf", warm=True):
    """Your living room: couch, TV, window to the snowy street, lamp. You stand near z=+1 looking toward -z."""
    win = "#ffd8a8" if lit and warm else "#3a4a66"
    o = [O("box", (0, -0.02, -2), [9, 0.04, 9], "#8a6a4f"), O("box", (0, 1.6, -5.5), [9, 3.2, 0.1], wall),
         O("box", (-4.5, 1.6, -2), [0.1, 3.2, 9], wall), O("box", (4.5, 1.6, -2), [0.1, 3.2, 9], wall), O("box", (0, 3.2, -2), [9, 0.05, 9], "#efe7dc"),
         O("plane", (2.4, 1.8, -5.43), [2.2, 1.4, 1], "#8fa6c8" if lit else "#1e2a44", material="glow"),
         O("particles", (2.4, 1.8, -5.4), 0.05, "#ffffff", count=40, seed=3, spread=[2, 1.3, 0.02], animate=[{"type": "drift", "axis": "y", "amount": -0.3}]),
         O("box", (-1.2, 0.35, -3.6), [2.6, 0.7, 0.9], "#5c7a99"), O("box", (-1.2, 0.85, -4.0), [2.6, 0.6, 0.25], "#5c7a99"),
         O("box", (0.2, 1.3, -5.4), [1.6, 0.9, 0.06], "#111"), O("plane", (0.2, 1.3, -5.36), [1.5, 0.8, 1], "#2f6fd6" if lit else "#0b0d12", material="glow"),
         O("box", (-3.6, 0.6, -4.6), [0.4, 1.2, 0.4], "#6b4f3a"), O("cone", (-3.6, 1.4, -4.6), [0.6, 0.5, 0.6], win, material="glow" if lit else "matte"),
         O("box", (1.4, 0.25, -2.4), [1.4, 0.5, 0.8], "#6b4f3a")]
    return o + list(extra)


def kitchen(extra=(), lit=True):
    return [O("box", (0, -0.02, -2), [8, 0.04, 8], "#cbbba3"), O("box", (0, 1.6, -5), [8, 3.2, 0.1], "#dfe6ea"),
            O("box", (-4, 1.6, -2), [0.1, 3.2, 8], "#dfe6ea"), O("box", (4, 1.6, -2), [0.1, 3.2, 8], "#dfe6ea"),
            O("box", (0, 0.45, -4.5), [6, 0.9, 0.8], "#7a8a99"), O("box", (2.6, 1.0, -4.5), [1.0, 2.0, 0.8], "#e9ecef"),
            O("cylinder", (-1.0, 1.0, -4.3), [0.08, 0.3, 0.08], "#adb5bd", material="metal"),
            O("plane", (-1.6, 2.0, -4.94), [1.6, 1.0, 1], "#8fa6c8" if lit else "#2b3a55", material="glow")] + list(extra)


MOM = lambda act="idle", face="neutral", at=(-1.3, 0, -2.6), ry=150: guy(at, "#c2255c", "#3f4a5a", act=act, face=face, seed=1801, ry=ry)
DAD = lambda act="idle", face="neutral", at=(1.4, 0, -2.8), ry=210: guy(at, "#2f6fd6", "#25324a", act=act, face=face, seed=1802, ry=ry)
KID = lambda act="idle", face="smile", at=(0.1, 0, -2.2), ry=180: guy(at, "#f59f00", "#3f4a5a", act=act, face=face, seed=1803, ry=ry, look="child")
GRAN = lambda act="sit", face="sad", at=(0, 0, -3.0), ry=180: guy(at, "#7048e8", "#3f4a5a", act=act, face=face, seed=1804, ry=ry, look="elder")
EYE = (0, 1.62, 1.6)
TEMP = lambda a, b, sub="INSIDE YOUR HOUSE", alert=False: T("INDOOR TEMP", count=(a, b), unit="°F", sub=sub, alert=alert)
OUT = lambda v, sub: T("WITHOUT POWER", value=v, sub=sub, alert=True)

# ---------------- Night 0 ----------------
s.B(3.8, "eyes", "", E(room(extra=[MOM("sit", "smile", (-1.3, 0.1, -3.4)), KID("sit", "smile", (-0.6, 0.1, -3.5))]), INSIDE, eye=EYE, ambient=1.5),
    tracker=T("CEDAR FALLS", clock="8:12:40 PM", sub="OUTSIDE: 4°F · SNOWING"), hands={"pose": "hold", "holding": "cup"}, gaze=(-10, -6),
    voices=[("Mom, can we watch one more?", "af_sky", 0.6)])
s.B(3.4, "eyes", "The coldest night in 30 years. You're warm on the couch.", E(room(extra=[MOM("sit", "smile", (-1.3, 0.1, -3.4)), KID("sit", "smile", (-0.6, 0.1, -3.5))]), INSIDE, eye=EYE, ambient=1.5),
    hands={"pose": "hold", "holding": "cup"}, gaze=(14, -2))
s.B(3.6, "eyes", "Your phone buzzes. Then everyone's does.", E(room(), INSIDE, eye=EYE, ambient=1.5),
    hands={"pose": "phone", "phone_text": "EMERGENCY ALERT: Extreme cold. Conserve power now.", "phone_time": "8:21"}, gaze=(0, -14),
    sfx=[{"type": "alarm", "at": 0.3, "dur": 1.6, "gain": 0.6}])
s.B(3.6, "eyes", "On TV: the grid is running out of power to send.", E(room(), INSIDE, eye=(0, 1.5, -2.6), ambient=1.5),
    banner={"kicker": "BREAKING NEWS", "title": "GRID OPERATOR: ROLLING BLACKOUTS POSSIBLE", "subtitle": "DEMAND AT RECORD HIGH"}, hands={"pose": "none"}, gaze=(0, -4))
s.B(3.2, "eyes", "The lights flicker once.", E(room(), INSIDE, eye=EYE, ambient=1.1, light=1.2), hands={"pose": "none"}, gaze=(0, 18), effects=["darken"],
    sfx=[{"type": "glitch", "at": 0.4}])
s.B(3.4, "eyes", "Then everything goes dark.", E(room(lit=False), NIGHTSNOW, eye=EYE, ambient=0.35, light=0.3), tracker=T("WITHOUT POWER", clock="8:34:02 PM", sub="HOUR 0", alert=True),
    hands={"pose": "none"}, gaze=(0, 0), effects=["darken"], sfx=[{"type": "drop", "at": 0.1, "gain": 1.0}], voices=[("Mom?!", "af_sky", 1.2)])
s.B(3.6, "eyes", "The fridge stops humming. The heat stops too.", E(kitchen(lit=False), NIGHTSNOW, eye=(0, 1.62, 1.2), ambient=0.45, light=0.4),
    hands={"pose": "hold", "holding": "flashlight"}, gaze=(20, -6))
s.B(3.6, "eyes", "\"It'll be back in an hour. It always is.\"", E(room(lit=False, extra=[DAD("idle", "smile", (0.9, 0, -2.0), 200)]), NIGHTSNOW, eye=EYE, ambient=0.5, light=0.5),
    by="Your dad", hands={"pose": "hold", "holding": "flashlight"}, gaze=(14, -4), voices=[("Relax. It'll be back in an hour.", "am_michael", 0.4)])

# ---------------- Hour 1-6 ----------------
DARKST = street(seed=181, people=8, cars=3, lamps=False)
s.B(3.6, "eyes", "You step outside. The whole street is dark.", E(DARKST, NIGHTSNOW, eye=(0, 1.62, 3), amb="wind", ambient=0.6, light=0.5, snow=True),
    tracker=T("WITHOUT POWER", value="HOUR 2", sub="OUTSIDE: 2°F", alert=True), hands={"pose": "hold", "holding": "flashlight"}, head="walk", gaze=(0, -4),
    sfx=[{"type": "steps", "at": 0.2, "dur": 3.0}])
s.B(3.4, "eyes", "No streetlights. No windows. Just snow.", E(DARKST, NIGHTSNOW, eye=(0, 1.62, -6), amb="wind", ambient=0.55, light=0.5, snow=True),
    hands={"pose": "hold", "holding": "flashlight"}, gaze=(-40, 6))
s.B(3.6, "eyes", "Your neighbors are out with flashlights too.", E(street(seed=182, people=0, cars=3, lamps=False, extra=[crowd(10, 1821, at=(0, 0.12, -10), spread=(10, 0, 8), act="idle", face="shock", ry=180)]),
                                                                  NIGHTSNOW, eye=(0, 1.62, 2), amb="wind", ambient=0.6, light=0.5, snow=True),
    hands={"pose": "hold", "holding": "flashlight"}, gaze=(0, -2), voices=[("Is it the whole city?", "am_eric", 0.6)])
s.B(3.6, "eyes", "It's not just your street. It's half the state.", E(DARKST, NIGHTSNOW, eye=(0, 1.62, 3), amb="wind", ambient=0.55, light=0.5, snow=True),
    hands={"pose": "phone", "phone_text": "1.9 million homes without power", "phone_time": "11:48"}, gaze=(0, -14),
    tracker=T("HOMES IN THE DARK", count=(200000, 1900000), sub="ACROSS THE STATE", alert=True))
s.B(3.6, "eyes", "Midnight. Your family sleeps in coats.", E(room(lit=False, extra=[MOM("lie", "sad", (-1.2, 0.75, -3.6), 90), KID("lie", "sad", (-0.2, 0.75, -3.6), 90)]),
                                                                NIGHTSNOW, eye=EYE, ambient=0.45, light=0.4), tracker=TEMP(68, 58, "MIDNIGHT"), hands={"pose": "none"}, gaze=(-10, -10))

# ---------------- Day 1 ----------------
s.B(3.6, "eyes", "Morning. You can see your breath. Inside.", E(room(lit=False), GREYDAY, eye=EYE, ambient=0.9, light=1.0), tracker=TEMP(58, 51, "DAY 1 · 7:30 AM"),
    hands={"pose": "idle", "tremble": 0.6}, gaze=(0, 4), sfx=[{"type": "breath", "at": 0.3}])
s.B(3.4, "eyes", "Your phone is at 22%. You turn off everything.", E(room(lit=False), GREYDAY, eye=EYE, ambient=0.9, light=1.0), hands={"pose": "phone", "phone_text": "22% · Low Power Mode", "phone_time": "7:41"},
    gaze=(0, -14))
STORE = [O("box", (0, -0.02, -6), [14, 0.04, 16], "#c9c3b5"), O("box", (-3, 1.1, -7), [1.0, 2.2, 10], "#d8d0c2"), O("box", (3, 1.1, -7), [1.0, 2.2, 10], "#d8d0c2"),
         O("box", (-2.5, 0.6, -7), [0.05, 0.05, 9.5], "#868e96"), O("box", (2.5, 0.6, -7), [0.05, 0.05, 9.5], "#868e96"),
         O("box", (-2.6, 1.5, -9), [0.3, 0.3, 0.3], "#e8590c", count=3, seed=2, spread=[0, 0.2, 4]),
         crowd(6, 1831, at=(0, 0.12, -10.5), spread=(2.4, 0, 2.5), act="walk", ry=180)]
s.B(3.6, "eyes", "The store is open on a generator. The shelves are empty.", E(STORE, INSIDE, eye=(0, 1.62, 2), ambient=1.0, light=1.0), head="walk",
    tracker=T("WITHOUT POWER", value="DAY 1", sub="FRESH MART · BACKUP POWER", alert=True), hands={"pose": "none"}, gaze=(-20, -6))
s.B(3.6, "eyes", "Bread: gone. Batteries: gone. Water: gone.", E(STORE, INSIDE, eye=(0, 1.62, -3), ambient=1.0, light=1.0), hands={"pose": "reach"}, gaze=(-40, -6),
    voices=[("Sorry, we're out of everything.", "af_bella", 0.6)])
GAS = [O("box", (0, -0.03, -14), [80, 0.04, 60], "#d8dde2"), O("box", (0, -0.01, -4), [9, 0.04, 40], "#4a5056"),
       O("box", (-5, 0.4, -4), [1.2, 0.8, 40], "#f1f3f5"), O("box", (5, 0.4, -4), [1.2, 0.8, 40], "#f1f3f5"), O("box", (0, 3.5, -16), [12, 0.4, 6], "#c92a2a"), O("box", (-3, 1.6, -16), [0.4, 3.2, 0.4], "#adb5bd"),
       O("box", (3, 1.6, -16), [0.4, 3.2, 0.4], "#adb5bd")]
for k in range(8):
    x, z, c = -2 + (k % 2) * 4, -10 + k * 2.5, ["#c92a2a", "#1c7ed6", "#868e96", "#212529", "#f2c94c"][k % 5]
    GAS += [O("box", (x, 0.55, z), [1.9, 0.7, 4.0], c, material="glossy"), O("box", (x, 1.15, z + 0.3), [1.6, 0.55, 2.0], "#2b3440", material="glossy"),
            O("box", (x, 1.45, z + 0.3), [1.6, 0.06, 2.0], "#ffffff")]
GAS += [O("particles", (0, 6, -4), 0.06, "#ffffff", count=200, seed=9, spread=[16, 10, 30], animate=[{"type": "drift", "axis": "y", "amount": -1}])]
s.B(3.6, "eyes", "The gas line wraps around the block.", E(GAS, GREYDAY, eye=(0, 1.9, 13), amb="wind", ambient=1.0, light=1.0), hands={"pose": "none"}, gaze=(0, -4), tracker=T("GAS LINE", value="2 HOURS", sub="ONE STATION OPEN"))
s.B(3.4, "eyes", "You charge your phone in the car. Engine running. Outside.", E(street(seed=183, people=2, cars=1, lamps=False), GREYDAY, eye=(0.35, 1.25, 0.45), amb="rumble", snow=True),
    hands={"pose": "phone", "phone_text": "Charging… 31%", "phone_time": "2:10"}, gaze=(0, -14))

# ---------------- Day 2 ----------------
s.B(3.6, "eyes", "Day 2. The house keeps losing heat.", E(room(lit=False), GREYDAY, eye=EYE, ambient=0.85, light=0.9), tracker=TEMP(51, 41, "DAY 2", True), hands={"pose": "idle", "tremble": 0.8},
    gaze=(0, 0))
TENT = room(lit=False, extra=[O("cone", (-0.6, 1.0, -3.0), [2.6, 2.0, 2.6], "#e8590c"), MOM("sit", "sad", (-1.6, 0, -2.2), 160), KID("sit", "neutral", (0.5, 0, -2.3), 200)])
s.B(3.6, "eyes", "You build a blanket tent in one room. Everyone sleeps inside.", E(TENT, GREYDAY, eye=EYE, ambient=0.85, light=0.9), hands={"pose": "none"}, gaze=(-8, -10))
s.B(3.6, "eyes", "Your neighbor drags a generator into his garage.", E(street(seed=184, people=0, cars=2, lamps=False, extra=[guy((2, 0.12, -5), "#495057", "#212529", act="walk", face="neutral", seed=1841, ry=180),
                                                                                                              O("box", (2.8, 0.4, -5), [0.8, 0.6, 0.5], "#f2c94c")]),
                                                                       GREYDAY, eye=(0, 1.62, 2), amb="wind", snow=True), hands={"pose": "none"}, gaze=(10, -4))
s.B(3.6, "eyes", "You stop him. Generators and grills never go indoors.", E(street(seed=184, people=0, cars=2, lamps=False, extra=[guy((0.6, 0.12, -1.6), "#495057", "#212529", act="idle", face="shock", seed=1841, ry=180)]),
                                                                           GREYDAY, eye=(0, 1.62, 1), amb="wind", snow=True), hands={"pose": "shield"}, gaze=(4, -2),
    voices=[("Hey! Not in the garage! The fumes!", "am_adam", 0.3)], tracker=T("CARBON MONOXIDE", value="NO SMELL", sub="NO COLOR · KILLS IN HOURS", alert=True))
s.B(3.6, "eyes", "You check on the old woman next door.", E(street(seed=185, people=0, cars=1, lamps=False), GREYDAY, eye=(0, 1.62, 2), amb="wind", snow=True), head="walk",
    hands={"pose": "none"}, gaze=(-20, 0), sfx=[{"type": "steps", "at": 0.2, "dur": 3.0}])
s.B(3.8, "eyes", "She's been alone in the dark for two days.", E(room(lit=False, wall="#d9cbb5", extra=[GRAN("sit", "sad", (0, 0.1, -3.0), 180)]), GREYDAY, eye=EYE, ambient=0.8, light=0.8),
    tracker=TEMP(44, 38, "MRS. ALVAREZ'S HOUSE", True), hands={"pose": "reach"}, gaze=(0, -8), voices=[("Oh, honey. I didn't want to bother anyone.", "af_heart", 0.6)])

# ---------------- Day 3 ----------------
PIPE = kitchen(lit=False, extra=[O("cylinder", (-2.6, 2.6, -4.6), [0.12, 2.4, 0.12], "#868e96", rotate=[0, 0, 90]),
                                 O("particles", (-2.0, 2.4, -4.5), 0.06, "#a5d8ff", count=80, seed=7, spread=[0.4, 2.4, 0.4], animate=[{"type": "drift", "axis": "y", "amount": -1.2}])])
s.B(3.6, "eyes", "Day 3. A pipe bursts in the ceiling.", E(PIPE, GREYDAY, eye=(0, 1.62, 1.2), ambient=0.9, light=0.9), tracker=OUT("DAY 3", "YOUR KITCHEN"), hands={"pose": "shield"}, gaze=(-20, 20),
    effects=["shake"], sfx=[{"type": "crack", "at": 0.2}])
s.B(3.6, "eyes", "Frozen water expands. Pipes split. A dripping tap could have saved it.", E(PIPE, GREYDAY, eye=(0, 1.62, 1.2), ambient=0.9, light=0.9), hands={"pose": "none"}, gaze=(-20, 10),
    tracker=T("FROZEN PIPES", value="+9%", sub="WATER EXPANDS WHEN IT FREEZES"))
s.B(3.6, "eyes", "Now the city water is down too. Boil it, if you can.", E(kitchen(lit=False), GREYDAY, eye=(0, 1.62, 1.2), ambient=0.9, light=0.9),
    hands={"pose": "phone", "phone_text": "BOIL WATER NOTICE · Cedar Falls", "phone_time": "10:02"}, gaze=(0, -14))
s.B(3.8, "eyes", "This isn't made up. In 2021, about 4 million Texas homes lost power.", E(street(seed=186, people=0, cars=2, lamps=False), NIGHTSNOW, eye=(0, 1.62, 3), amb="wind", ambient=0.5, light=0.5, snow=True),
    tracker=T("TEXAS · FEB 2021", count=(0, 4000000), sub="CUSTOMERS WITHOUT POWER"), hands={"pose": "none"}, gaze=(0, 6), by="ERCOT / news reports")
s.B(3.8, "eyes", "Officially, 246 people died. Most from the cold.", E(street(seed=186, people=0, cars=2, lamps=False), NIGHTSNOW, eye=(0, 1.62, -2), amb="wind", ambient=0.5, light=0.5, snow=True),
    tracker=T("TEXAS · FEB 2021", value="246", sub="OFFICIAL DEATHS · MOSTLY HYPOTHERMIA"), hands={"pose": "none"}, gaze=(0, 0), by="Texas Dept. of State Health Services", effects=["darken"])

# ---------------- Day 4-5 ----------------
WARM = church(seed=19, pews=False, extra=[crowd(40, 1901, at=(0, 0.1, -9), spread=(9, 0, 10), act="sit", face="smile", ry=180),
                                          O("box", (0, 0.5, -4), [3, 1.0, 1.2], "#f1ece4"), O("cylinder", (-0.8, 1.2, -4), [0.4, 0.4, 0.4], "#adb5bd", material="metal")])
s.B(3.6, "eyes", "Day 4. A church across town has a generator.", E(WARM, INSIDE, eye=(0, 1.62, 2), ambient=1.6, light=1.8), tracker=T("WARMING CENTER", value="OPEN", sub="ST. LUKE'S · 300 COTS"),
    hands={"pose": "none"}, head="walk", gaze=(0, -4), effects=["bloom"])
s.B(3.6, "eyes", "Warm air hits your face. You almost cry.", E(WARM, INSIDE, eye=(0, 1.62, 0), ambient=1.6, light=1.8), tracker=TEMP(38, 66, "WARMING CENTER"),
    hands={"pose": "idle"}, gaze=(0, 8), effects=["bloom"])
s.B(3.6, "eyes", "Strangers share soup. Phone chargers. Blankets.", E(WARM, INSIDE, eye=(1.5, 1.62, -3), ambient=1.6, light=1.8), hands={"pose": "hold", "holding": "cup"}, gaze=(-30, -10),
    voices=[("Here. It's still hot.", "af_nicole", 0.5)])
s.B(3.6, "eyes", "Mrs. Alvarez gets a cot by the heater.", E(church(seed=19, pews=False, extra=[GRAN("lie", "smile", (0, 0.5, -3), 90), O("box", (0, 0.25, -3), [1.0, 0.4, 2.2], "#2f6fd6")]),
                                                         INSIDE, eye=(0, 1.62, 0), ambient=1.6, light=1.8), hands={"pose": "none"}, gaze=(0, -20))
s.B(3.6, "eyes", "Day 5. Line crews come in from three states.", E(street(seed=191, people=0, cars=0, lamps=False, extra=[O("box", (-2, 1.4, -8), [2.4, 2.8, 6], "#f2c94c", count=3, seed=4, spread=[8, 0, 10]),
                                                                                                                     crowd(8, 1911, at=(0, 0.12, -6), spread=(8, 0, 4), act="walk", ry=180)]),
                                                                       DAWNCOLD, eye=(0, 1.62, 2), amb="rumble", snow=True), tracker=OUT("DAY 5", "CREWS ON YOUR STREET"),
    hands={"pose": "none"}, gaze=(0, 4), voices=[("We'll get you back on, ma'am.", "am_onyx", 0.6)])

# ---------------- Day 6-7 ----------------
s.B(3.6, "eyes", "Day 6. You go home to grab clothes.", E(room(lit=False), DAWNCOLD, eye=EYE, ambient=0.9, light=0.9), tracker=TEMP(36, 33, "DAY 6 · YOUR HOUSE", True),
    hands={"pose": "none"}, gaze=(0, 0))
s.B(3.4, "eyes", "Then a click.", E(room(lit=False), DAWNCOLD, eye=EYE, ambient=0.9, light=0.9), hands={"pose": "none"}, gaze=(-20, 10), sfx=[{"type": "tick", "at": 0.8, "gain": 1.0}])
s.B(3.6, "eyes", "The furnace roars. The lights come on.", E(room(lit=True), DAWNCOLD, eye=EYE, ambient=1.6, light=2.0), tracker=T("POWER", value="BACK ON", sub="AFTER 6 DAYS, 14 HOURS", big=True),
    hands={"pose": "none"}, gaze=(0, 12), effects=["bloom", "rays"], sfx=[{"type": "swell", "at": 0.2, "dur": 2.8}])
s.B(3.6, "eyes", "Your whole street cheers.", E(street(seed=192, people=0, cars=3, extra=[crowd(14, 1921, at=(0, 0.12, -8), spread=(10, 0, 8), act="cheer", face="smile", ry=180)]),
                                                 DAWNCOLD, eye=(0, 1.62, 2), amb="calm", snow=True), hands={"pose": "none"}, gaze=(0, 0),
    voices=[("Woooo!", "am_puck", 0.3), ("It's back!", "af_bella", 1.0)])
s.B(3.6, "eyes", "On the news: demand is growing faster than the grid.", E(room(lit=True), DAWNCOLD, eye=(0, 1.5, -2.6), ambient=1.6, light=2.0),
    banner={"kicker": "LIVE", "title": "WHY THE GRID FAILED", "subtitle": "RECORD COLD · RECORD DEMAND"}, hands={"pose": "none"}, gaze=(0, -4))
s.B(3.6, "eyes", "Heaters. Electric cars. And now, AI data centers.", E(room(lit=True), DAWNCOLD, eye=(0, 1.5, -2.6), ambient=1.6, light=2.0),
    tracker=T("ONE AI DATA CENTER", count=(0, 100000), unit=" HOMES", sub="SAME POWER USE"), by="IEA, 2025", hands={"pose": "none"}, gaze=(0, -4))
s.B(3.8, "eyes", "That night, your family sleeps in their own beds.", E(room(lit=True, extra=[MOM("sit", "smile", (-1.3, 0.1, -3.4)), KID("sit", "smile", (-0.6, 0.1, -3.5)),
                                                                                             DAD("sit", "smile", (0.2, 0.1, -3.4), 180)]), NIGHTSNOW, eye=EYE, ambient=1.5),
    tracker=T("CEDAR FALLS", clock="9:30:00 PM", sub="OUTSIDE: 11°F · 72° INSIDE"), hands={"pose": "hold", "holding": "cup"}, gaze=(-10, -6))
s.B(3.8, "eyes", "And you fill the closet. Water. Batteries. Blankets. Just in case.", E(room(lit=True, extra=[O("box", (3.6, 0.5, -3), [0.6, 1.0, 1.4], "#a5d8ff", count=3, seed=5, spread=[0.2, 0, 1]),
                                                                                                                 O("box", (3.6, 1.2, -3), [0.4, 0.3, 0.4], "#f2c94c", count=3, seed=6, spread=[0.2, 0, 1])]),
                                                                                       NIGHTSNOW, eye=EYE, ambient=1.5), hands={"pose": "reach"}, gaze=(40, -14))

s.save("lf_blackout", "What if the power went out for a *week* in the coldest week of winter?",
       "First-person long-form: a fictional town loses power on the coldest night in 30 years; a family lives through a week of dropping indoor temperatures, empty stores, a burst pipe, a generator mistake avoided, a warming center, and the lights coming back; anchored on the 2021 Texas freeze.",
       "Would your house last a week?", accent="#7fd3ff", skin="#e0ac69", sleeve="#3f4a5a", thumb="NO POWER. 4°F.", thumb_beat=5)
import json  # noqa: E402
p = Path(__file__).resolve().parent / "lf_blackout.json"
d = json.loads(p.read_text())
d["width"], d["height"] = 1920, 1080
p.write_text(json.dumps(d, indent=1, ensure_ascii=False))
