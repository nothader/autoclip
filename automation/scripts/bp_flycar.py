"""What if your car could fly? (trending: Tesla's Roadster demo, Oct 15 2026, hopped off the ground on SpaceX cold-gas thrusters;
Tesla said production starts in 2028). Block POV.
Anchors: Tesla's October 2026 Roadster demo (widely reported); FAA minimum for a private pilot certificate is 40 flight hours;
the average American spends about 54 hours a year stuck in traffic (TTI / INRIX range, rounded: 'about 50 hours')."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd  # noqa: E402

s = Story()
MORNING = ["#7fa9d9", "#f6e3c8"]; HIGH = ["#3f7fc9", "#cfe3f5"]; STORMY = ["#4a5568", "#a3adb8"]; SUNSET = ["#5a4a8c", "#ffb37a"]
CAR_COLS = ["#c92a2a", "#1c7ed6", "#f8f9fa", "#212529", "#f2c94c", "#2f9e44", "#7048e8"]


def car(x, y, z, col, ry=0, fly=False):
    o = [O("box", (x, y + 0.55, z), [1.9, 0.7, 4.2], col, material="glossy", rotate=[0, ry, 0]),
         O("box", (x, y + 1.1, z + 0.2), [1.6, 0.5, 2.0], "#9fc3e6", material="glass", opacity=0.6, rotate=[0, ry, 0])]
    if fly:
        o += [O("flame", (x - 0.7, y - 0.1, z), 0.25, "#7fd3ff"), O("flame", (x + 0.7, y - 0.1, z), 0.25, "#7fd3ff")]
    else:
        o += [O("cylinder", (x, y + 0.3, z), [2.0, 0.6, 0.6], "#212529", rotate=[0, 0, 90])]
    return o


def highway(extra=(), lanes_y=0.0, n=6, fly=False, seed=1):
    o = [O("box", (0, -0.03, -40), [200, 0.04, 200], "#7a9e5a"), O("box", (0, 0.0, -40), [14, 0.02, 200], "#4a4d53"),
         O("box", (0, 0.02, -40), [0.15, 0.02, 200], "#e8d36a"), O("box", (-3.5, 0.02, -40), [0.12, 0.02, 200], "#f1f3f5"),
         O("box", (3.5, 0.02, -40), [0.12, 0.02, 200], "#f1f3f5"),
         O("box", (-60, 20, -120), [20, 40, 20], "#a8b0bb"), O("box", (-30, 30, -140), [18, 60, 18], "#8d97a5"), O("box", (40, 25, -130), [22, 50, 22], "#b7bec7")]
    for k in range(n):
        x = [-5.2, -1.8, 1.8, 5.2][k % 4]
        o += car(x, lanes_y, -8 - k * 7, CAR_COLS[(k + seed) % len(CAR_COLS)], fly=fly)
    return (o + list(extra))[:40]


def cockpit(extra=(), sky_glow="#cfe3f5"):
    """You sit in the driver's seat (eye about (0, 1.25, 0.4)), looking out over the dash and hood."""
    return [O("box", (0, 0.75, -0.55), [1.9, 0.35, 0.6], "#2b2f36"), O("torus", (0.35, 0.95, -0.25), [0.2, 0.2, 0.2], "#15171c", rotate=[70, 0, 0]),
            O("plane", (-0.25, 0.94, -0.52), [0.45, 0.2, 1], "#7fd3ff", material="glow", rotate=[-60, 0, 0]),
            O("box", (0, 0.62, -2.1), [1.9, 0.12, 2.4], "#c92a2a", material="glossy"),
            O("box", (-0.95, 1.25, -0.7), [0.08, 0.9, 0.08], "#212529", rotate=[25, 0, 0]), O("box", (0.95, 1.25, -0.7), [0.08, 0.9, 0.08], "#212529", rotate=[25, 0, 0]),
            ] + list(extra)


EYE = (0.35, 1.25, 0.45)
s.B(3.8, "eyes", "", env(cockpit(highway(n=6)), MORNING, eye=EYE, amb="rumble"), tracker=T("I-35 · MONDAY", clock="7:52:10 AM", sub="SPEED 3 MPH"),
    hands={"pose": "grab"}, gaze=(0, -6), voices=[("Come on, come on...", "am_adam", 0.8)], sfx=[{"type": "beep", "at": 1.6}])
s.B(3.4, "eyes", "Monday. Stuck again. You're late again.", env(cockpit(highway(n=7, seed=2)), MORNING, eye=EYE, amb="rumble"), hands={"pose": "grab"}, gaze=(-8, -4))
s.B(3.4, "eyes", "But last night, a car update added one new button.", env(cockpit(highway(n=7, seed=2)), MORNING, eye=EYE, amb="rumble"), hands={"pose": "point"}, gaze=(-20, -40),
    screen={"kind": "board", "title": "NEW FEATURE", "subtitle": "SOFTWARE UPDATE 26.11", "rows": [["HOVER MODE", "ON"]]})
s.B(3.4, "eyes", "You press it.", env(cockpit(highway(n=7, seed=2)), MORNING, eye=(0.35, 3.2, 0.45), amb="wind"), head="float", hands={"pose": "grab", "tremble": 0.5},
    gaze=(0, -14), effects=["shake"], sfx=[{"type": "whoosh", "at": 0.2, "dur": 2.4, "gain": 1.1}, {"type": "boom", "at": 0.3, "gain": 0.6}])
s.B(3.6, "eyes", "You rise straight up. Over all of it.", env(cockpit(highway(n=8, seed=3)), HIGH, eye=(0.35, 30, 0.45), amb="wind"), head="float",
    tracker=T("ALTITUDE", count=(0, 300), unit=" FT", sub="ABOVE I-35"), hands={"pose": "grab"}, gaze=(0, -40), effects=["bloom"])
s.B(3.6, "eyes", "In October, a real car hopped into the air on thrusters.", env(cockpit(highway(n=8, seed=3)), HIGH, eye=(0.35, 30, 0.45), amb="wind"), head="float",
    tracker=T("REAL DEMO", value="OCT 2026", sub="PRODUCTION TALK: 2028"), hands={"pose": "grab"}, gaze=(30, -20))
s.B(3.4, "eyes", "Then you look around. Everyone pressed it.", env(cockpit(highway(lanes_y=29.6, n=7, fly=True, seed=4)), HIGH, eye=(0.35, 31.4, 1.2), amb="wind"), head="float",
    hands={"pose": "grab"}, gaze=(0, -12), sfx=[{"type": "whoosh", "at": 0.5}, {"type": "whoosh", "at": 1.6}])
SKYJAM = [O("box", (0, -0.03, -60), [300, 0.04, 300], "#7a9e5a")]
for k in range(30):
    SKYJAM += car(((k * 37) % 60) - 30, 18 + (k * 13) % 30, -10 - (k * 23) % 90, CAR_COLS[k % len(CAR_COLS)], ry=(k * 41) % 360, fly=True)[:2]
s.B(3.6, "far", "Now the traffic jam is in the sky.", env(SKYJAM[:40], HIGH, focus=(0, 30, -30), zoom=2.8, amb="wind"), tracker=T("CARS IN THE SKY", count=(0, 4200), sub="OVER YOUR CITY", alert=True),
    sfx=[{"type": "beep", "at": 0.6}, {"type": "beep", "at": 1.2}])
DRONE = [O("box", (0.4, 30.9, -2.4), [0.8, 0.15, 0.8], "#495057"), O("box", (0.4, 30.6, -2.4), [0.5, 0.5, 0.5], "#c97a40"),
         O("cylinder", (0.4, 31.0, -2.4), [1.4, 0.03, 1.4], "#adb5bd", animate=[{"type": "spin", "axis": "y", "speed": 20}])]
s.B(3.4, "eyes", "A delivery drone hits your windshield. Someone's pizza.", env(cockpit(highway(lanes_y=30, n=4, fly=True, seed=5) + DRONE), HIGH, eye=(0.35, 30.6, 0.45), amb="wind"),
    head="shake", hands={"pose": "shield"}, gaze=(0, 0), effects=["shake"], sfx=[{"type": "impact", "at": 0.3, "gain": 1.2}])
s.B(3.4, "eyes", "Your battery is dropping. Fast.", env(cockpit(highway(lanes_y=30, n=5, fly=True, seed=6)), HIGH, eye=(0.35, 30.6, 0.45), amb="wind"), head="float",
    tracker=T("BATTERY", count=(81, 19), unit="%", sub="HOVERING EATS POWER", alert=True), hands={"pose": "grab", "tremble": 0.4}, gaze=(-20, -40),
    sfx=[{"type": "alarm", "at": 0.4, "dur": 2.4, "gain": 0.5}])
COP = [O("box", (1.8, 30.4, -3.0), [1.9, 0.7, 4.2], "#f8f9fa", material="glossy"), O("box", (1.8, 31.0, -3.0), [1.4, 0.15, 0.3], "#1c7ed6", material="glow",
                                                                                                         animate=[{"type": "pulse", "amount": 0.9}]),
       O("box", (1.8, 31.0, -2.6), [1.4, 0.15, 0.3], "#e03131", material="glow", animate=[{"type": "pulse", "amount": 0.9}]),
       guy((1.6, 30.75, -2.4), "#25324a", "#25324a", act="point", face="angry", seed=1701, ry=200)]
s.B(3.6, "eyes", "Lights behind you. A flying cop.", env(cockpit(highway(lanes_y=0, n=4, seed=7) + COP), HIGH, eye=(0.35, 30.6, 0.45), amb="wind"), head="float",
    hands={"pose": "grab"}, gaze=(40, 0), voices=[("Pull over. Well... down.", "am_onyx", 0.4)], sfx=[{"type": "siren", "at": 0.1, "dur": 3.0, "gain": 0.6}])
s.B(3.6, "eyes", "\"License? Pilots need 40 hours of flight time.\"", env(cockpit(highway(lanes_y=0, n=4, seed=7) + COP), HIGH, eye=(0.35, 30.6, 0.45), amb="wind"), head="float",
    by="FAA minimum", tracker=T("YOUR FLIGHT HOURS", value="0", sub="REQUIRED: 40", alert=True), hands={"pose": "phone", "phone_text": "Driver's license ✓  Pilot's license ✗",
                                                                                                     "phone_time": "8:03"}, gaze=(10, -14))
s.B(3.4, "eyes", "Then the wind picks up.", env(cockpit(highway(lanes_y=0, n=4, seed=8)), STORMY, eye=(0.35, 30.6, 0.45), amb="wind"), head="shake",
    hands={"pose": "grab", "tremble": 0.9}, gaze=(0, -10), effects=["shake", "darken"], sfx=[{"type": "rumble", "at": 0.2, "dur": 3.0}])
s.B(3.4, "eyes", "Cars on the road just stop. Up here, you drop.", env(cockpit(highway(lanes_y=0, n=6, seed=9)), STORMY, eye=(0.35, 12, 0.45), amb="wind"), head="fall",
    tracker=T("ALTITUDE", count=(300, 40), unit=" FT", alert=True), hands={"pose": "grab", "tremble": 1.0}, gaze=(0, -45), effects=["shake"])
ROOF = [O("box", (0, -0.03, -10), [60, 0.04, 60], "#6f9a4e"), O("box", (0, 2.5, -6), [9, 5, 8], "#e9dcc5"), O("box", (0, 5.1, -6), [9.4, 0.3, 8.4], "#8a4f3a"),
        guy((-1.0, 5.2, -6.5), "#7048e8", "#3f4a5a", act="wave", face="shock", seed=1702, ry=180)]
s.B(3.6, "eyes", "You land on your own roof. Your neighbor just stares.", env(cockpit(ROOF), SUNSET, eye=(0.35, 6.6, -2.5), amb="calm"), head="breathe",
    tracker=T("MONDAY", clock="8:41:02 AM", sub="49 MINUTES LATE"), hands={"pose": "none"}, gaze=(-12, -10), voices=[("Is that... your car?", "af_nicole", 0.6)])
s.B(3.8, "eyes", "Tomorrow, the road will be slow. But it stays on the ground.", env(cockpit(highway(n=6, seed=10)), SUNSET, eye=EYE, amb="rumble"),
    tracker=T("TUESDAY", clock="7:52:10 AM", sub="SPEED 3 MPH"), hands={"pose": "grab"}, gaze=(0, -6))

s.save("bp_flycar", "What if your car could *fly*?",
       "First-person: a software update adds hover mode, you lift over a Monday traffic jam, then everyone does; sky traffic, a drone hit, a dying battery, a flying cop asking for a pilot's license, wind, and a landing on your roof.",
       "Would you fly to work, or stay on the road?", accent="#7fd3ff", skin="#a0522d", sleeve="#2b2f36", thumb="TRAFFIC IN THE SKY", thumb_beat=7)
