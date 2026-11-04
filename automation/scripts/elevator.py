"""What if you got stuck in an elevator? Block POV format (see automation/STYLE_BLOCK_POV.md).
Real anchors (widely reported): in October 1999 Nicholas White was stuck about 41 hours in an express elevator of the McGraw-Hill
Building in New York after stepping out late on a Friday; a security camera showed him but nobody noticed. Elevators are not
airtight; people can survive about 3 days without water; climbing out of a stuck car is the dangerous part (stay put and wait)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, NIGHT, DAWN, DAY, INDOOR, DUSK  # noqa: E402

s = Story()
EYE = (0, 1.62, 0.55)
STEEL, STEEL2 = "#c4c9ce", "#b3b9bf"


def elevator(light="#fff1d0", open_doors=False, extra=()):
    """2 × 2 m car centred on the origin; you stand at the back looking at the doors (−z)."""
    door_anim = (lambda x: [{"type": "move", "to": [x * 2.6, 1.1, -1.0]}]) if open_doors else (lambda x: [])
    o = [O("box", (0, -0.02, 0), [2.0, 0.04, 2.0], "#5a4e44"),
         O("box", (0, 1.3, 1.0), [2.0, 2.6, 0.06], STEEL2, material="glossy"),
         O("box", (-1.0, 1.3, 0), [0.06, 2.6, 2.0], STEEL, material="glossy"), O("box", (1.0, 1.3, 0), [0.06, 2.6, 2.0], STEEL, material="glossy"),
         O("box", (-0.45, 1.1, -1.0), [0.88, 2.2, 0.05], "#d3d7db", material="glossy", animate=door_anim(-1)),
         O("box", (0.45, 1.1, -1.0), [0.88, 2.2, 0.05], "#d3d7db", material="glossy", animate=door_anim(1)),
         O("box", (0, 2.42, -1.0), [2.0, 0.36, 0.06], "#7d838a", material="metal"),
         O("plane", (0, 2.4, -0.96), [0.34, 0.14, 1], "#ff6b5b", material="glow"),
         O("box", (0.96, 1.25, -0.5), [0.04, 0.62, 0.26], "#5f666d", material="metal"),
         O("box", (0.94, 1.12, -0.5), [0.02, 0.05, 0.05], "#ffe8a3", material="glow", count=8, seed=3, spread=[0, 0.4, 0.14]),
         O("box", (0, 0.95, 0.95), [1.8, 0.05, 0.05], "#d0d4d8", material="metal"),
         O("box", (0, 2.62, 0), [2.0, 0.04, 2.0], "#d9dcdf"),
         O("plane", (0, 2.585, -0.1), [1.2, 0.6, 1], light, material="glow", rotate=[90, 0, 0]),
         O("box", (0, 2.595, 0.5), [0.55, 0.01, 0.55], "#6c737a"),
         O("box", (-0.965, 1.25, 0.1), [0.02, 1.7, 1.6], "#8b5e3c"), O("box", (0.965, 1.4, 0.35), [0.02, 1.5, 1.1], "#8b5e3c"),
         O("box", (0, 1.35, 0.965), [1.6, 1.8, 0.02], "#cfd6dc", material="glossy"),
         O("box", (0, 0.002, 0), [0.48, 0.006, 0.48], "#6b5d51", count=6, seed=9, spread=[1.4, 0, 1.4]),
         *([] if open_doors else [O("box", (0, 1.1, -0.972), [0.012, 2.2, 0.01], "#4a4f55")]),
         O("box", (-0.6, 1.6, -0.97), [0.5, 0.25, 0.005], "#d8dde2", material="metal")]
    return o + list(extra)


ELEV = lambda **k: env(elevator(**{a: b for a, b in k.items() if a in ("light", "open_doors", "extra")}), INDOOR, eye=EYE, amb="room",
                       ambient=k.get("ambient", 1.6) + 0.3, light=k.get("lit", 1.6) + 0.5, bounce="#d9cbb5")

# 0. Title only (3.8 s): the last one out of the office on a Friday night.
office = [O("box", (0, -0.02, -4), [14, 0.04, 14], "#4b4f58"), O("plane", (0, 2.2, -9), [14, 4.4, 1], "#1b2a4a", material="glow"),
          O("particles", (0, 2.0, -8.9), 0.12, "#ffd98a", count=90, seed=4, spread=[13, 3.6, 0.1]),
          O("box", (-2.6, 0.38, -3.5), [1.6, 0.76, 0.8], "#d9cbb4", count=4, seed=5, spread=[1, 0, 5]),
          O("box", (2.6, 0.38, -3.5), [1.6, 0.76, 0.8], "#d9cbb4", count=4, seed=6, spread=[1, 0, 5]),
          O("plane", (-2.6, 1.05, -3.7), [0.5, 0.32, 1], "#8fd3ff", material="glow", count=3, seed=7, spread=[1, 0, 5]),
          O("box", (0, 1.3, -7.5), [2.2, 2.6, 0.1], "#9aa1a8", material="metal"),
          O("box", (0, 1.1, -7.44), [1.4, 2.2, 0.04], "#c1c6cc", material="metal"),
          guy((-0.9, 0, -1.6), "#c2255c", "#3f4a5a", act="wave", face="smile", seed=21, ry=180)]
s.B(3.8, "eyes", "", env(office, NIGHT, eye=(0, 1.62, 1.0), amb="room", ambient=1.1, stars=True),
    tracker=T("FRIDAY · NEW YORK", clock="10:58:40 PM", sub="OFFICE TOWER · FLOOR 34"), hands={"pose": "hold", "holding": "cup"},
    head="walk", voices=[("See you Monday!", "af_bella", 1.2)])
s.B(3.4, "eyes", "You're the last one out. You press the button.", env(office, NIGHT, eye=(0, 1.62, -4.4), amb="room", ambient=1.1),
    hands={"pose": "point"}, gaze=(0, -4))
s.B(3.4, "eyes", "The doors close. Floor 34, going down.", ELEV(), tracker=T("FRIDAY · NEW YORK", clock="11:02:14 PM", sub="ELEVATOR 6 · DESCENDING"),
    hands={"pose": "phone", "phone_text": "Mom: home soon?", "phone_time": "11:02"}, gaze=(0, -10))
s.B(3.2, "eyes", "Then a jolt.", ELEV(light="#ffd59a", lit=1.2), tracker=T("FRIDAY · NEW YORK", clock="11:02:31 PM", sub="BETWEEN FLOORS 13 AND 14", alert=True),
    hands={"pose": "shield"}, head="shake", effects=["shake", "darken"], sfx=[{"type": "impact", "at": 0.1, "gain": 1.2}, {"type": "rumble", "at": 0.1, "dur": 1.2}])
s.B(3.4, "eyes", "The lights flicker. You're stuck between floors.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9),
    hands={"pose": "idle"}, gaze=(0, 18), gaze_to=(0, 0), effects=["darken"])
s.B(3.4, "eyes", "You press the alarm. Nothing happens.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9), hands={"pose": "point"}, gaze=(48, -8),
    sfx=[{"type": "beep", "at": 0.5}, {"type": "beep", "at": 1.3}])
s.B(3.2, "eyes", "No signal. Nine percent battery.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9),
    hands={"pose": "phone", "phone_text": "No Service · 9%", "phone_time": "11:09"}, gaze=(0, -14))

desk = [O("box", (0, -0.02, -1), [10, 0.04, 10], "#5a524a"), O("box", (0, 1.6, 1.0), [6, 3.2, 0.1], "#2b3038"),
        O("box", (0, 1.65, 0.9), [3.4, 1.5, 0.08], "#15181d"),
        O("plane", (-1.1, 2.05, 0.85), [0.95, 0.6, 1], "#8fb4ff", material="glow", rotate=[0, 180, 0]),
        O("plane", (0.0, 2.05, 0.85), [0.95, 0.6, 1], "#a5c4ff", material="glow", rotate=[0, 180, 0]),
        O("plane", (1.1, 2.05, 0.85), [0.95, 0.6, 1], "#7ab0ff", material="glow", rotate=[0, 180, 0]),
        O("plane", (-1.1, 1.3, 0.85), [0.95, 0.6, 1], "#b0c8ff", material="glow", rotate=[0, 180, 0]),
        O("plane", (0.0, 1.3, 0.85), [0.95, 0.6, 1], "#3fa34d", material="glow", rotate=[0, 180, 0], animate=[{"type": "pulse", "amount": 0.05}]),
        O("plane", (1.1, 1.3, 0.85), [0.95, 0.6, 1], "#8fb4ff", material="glow", rotate=[0, 180, 0]),
        O("box", (0, 0.4, -1.0), [2.6, 0.8, 0.8], "#6b5641"), O("cylinder", (0.8, 0.86, -1.0), [0.09, 0.12, 0.09], "#f8f9fa"),
        guy((0, 0, -0.2), "#25324a", "#25324a", act="phone", face="smile", seed=33)]
mon = desk[:8] + [O("box", (0.0, 1.3, 0.84), [0.12, 0.2, 0.01], "#1b1e24")]
s.B(3.6, "front", "Down in the lobby, the night guard is watching the game.", env(desk, INDOOR, focus=(0, 1.35, -0.2), zoom=0.62, amb="room", ambient=1.5),
    tracker=T("FRIDAY · NEW YORK", clock="11:20:05 PM", sub="SECURITY DESK · LOBBY"), voices=[("Come on, come on... yes!", "am_eric", 1.0)])
s.B(3.4, "eyes", "\"Hello?! Can anybody hear me?\"", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9), tracker=T("STUCK FOR", value="2 HOURS", sub="FRIDAY NIGHT"),
    hands={"pose": "fists"}, head="shake", voices=[("Hello?! Can anybody hear me?!", "am_adam", 0.3)])
s.B(3.4, "eyes", "Your voice just bounces back.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9), hands={"pose": "idle"}, gaze=(0, 52))
s.B(3.6, "eyes", "You look at the hatch. You think about climbing out.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9), hands={"pose": "reach"}, gaze=(0, 60))
s.B(3.6, "eyes", "Don't. Climbing out is how people get hurt.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9), hands={"pose": "none"}, gaze=(0, 60), gaze_to=(0, -20))
s.B(3.2, "eyes", "So you sit down. And wait.", env(elevator(light="#ffcf8a"), INDOOR, eye=(0, 0.85, 0.5), amb="room", ambient=0.9, light=0.9),
    hands={"pose": "idle"}, head="breathe", gaze=(0, 4))

city = [O("box", (0, -0.05, -40), [300, 0.1, 300], "#6d7480"), O("box", (0, 60, -70), [22, 120, 22], "#8d97a5", material="glossy"),
        O("box", (-34, 40, -90), [18, 80, 18], "#a8b0bb"), O("box", (32, 45, -95), [20, 90, 20], "#7d8794"),
        O("box", (-60, 25, -60), [16, 50, 16], "#b7bec7"), O("box", (60, 30, -60), [18, 60, 18], "#9aa3ae"),
        O("box", (0, 0.4, -20), [3.8, 0.9, 1.8], "#ffd43b", count=6, seed=4, spread=[40, 0, 8]),
        crowd(10, 41, at=(0, 0, -12), spread=(30, 0, 6))]
s.B(3.8, "far", "Saturday morning. The tower is empty.", env(city, DAWN, focus=(0, 50, -80), zoom=6.5, amb="calm"),
    tracker=T("STUCK FOR", count=(8, 9), unit=" HOURS", sub="SATURDAY · 8:14 AM"), move="crane_up")
s.B(3.4, "eyes", "Your phone dies.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9), hands={"pose": "phone", "phone_text": "0%", "phone_time": "8:31"},
    gaze=(0, -14), sfx=[{"type": "drop", "at": 1.2, "gain": 0.6}])
s.B(3.6, "eyes", "You're thirsty. But you won't run out of air.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9), hands={"pose": "idle"}, gaze=(0, 30))
s.B(3.6, "eyes", "Elevators aren't airtight. Air keeps coming in.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9), hands={"pose": "none"}, gaze=(-30, 20))

kitchen = [O("box", (0, -0.02, -3), [8, 0.04, 8], "#b08d6a"), O("box", (0, 0.45, -4.2), [4, 0.9, 0.7], "#e9e1d3"),
           O("box", (1.8, 1.0, -4.3), [0.9, 2.0, 0.7], "#dee2e6"), O("plane", (-0.8, 1.7, -4.58), [1.6, 1.0, 1], "#ffb36b", material="glow"),
           O("cylinder", (-1.2, 0.98, -4.1), [0.12, 0.12, 0.12], "#c92a2a"),
           guy((0, 0, -2.6), "#7048e8", "#3f4a5a", act="phone", face="sad", seed=55)]
s.B(3.8, "front", "Your mom calls. Again. And again.", env(kitchen, DUSK, focus=(0, 1.35, -2.6), zoom=0.55, amb="room", ambient=1.3),
    tracker=T("STUCK FOR", count=(9, 20), unit=" HOURS", sub="SATURDAY · 7:40 PM"),
    voices=[("He's not picking up. That's not like him.", "af_heart", 0.4)])
s.B(3.6, "eyes", "Sunday. You've counted every bolt in the wall.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9),
    tracker=T("STUCK FOR", count=(20, 33), unit=" HOURS", sub="SUNDAY · 8:02 AM"), hands={"pose": "none"}, gaze=(-55, 0), gaze_to=(55, 0))
s.B(3.8, "front", "In 1999, a man in New York was stuck like this. For 41 hours.", env(mon, INDOOR, focus=(0, 1.65, 0.85), zoom=0.42, amb="room", ambient=1.3),
    tracker=T("REAL CASE", value="1999", sub="NEW YORK CITY"), effects=["darken"])
s.B(3.6, "front", "A camera was on him the whole time. Nobody looked.", env(desk, INDOOR, focus=(0, 1.35, -0.2), zoom=0.62, amb="room", ambient=1.3),
    tracker=T("REAL CASE", value="1999", sub="NEW YORK CITY"))
s.B(3.6, "eyes", "Then, a voice.", ELEV(light="#ffcf8a", lit=0.9, ambient=0.9), tracker=T("STUCK FOR", count=(33, 41), unit=" HOURS", sub="SUNDAY · 3:30 PM", alert=True),
    hands={"pose": "idle"}, gaze=(0, 0), voices=[("Hello? Is somebody in there?!", "am_michael", 0.9)], sfx=[{"type": "impact", "at": 0.4, "gain": 0.8}])
rescue = [O("plane", (0, 1.4, -1.9), [3.0, 3.0, 1], "#fff6e0", material="glow"), guy((0.1, 0, -1.7), "#3b3b3b", "#3b3b3b", act="wave", face="smile", seed=71, ry=180)]
s.B(3.8, "eyes", "The doors open. Light.", ELEV(light="#ffcf8a", open_doors=True, extra=rescue, lit=1.3, ambient=1.3),
    tracker=T("STUCK FOR", value="41 HOURS", big=True), hands={"pose": "none"}, gaze=(0, 0), effects=["rays"],
    voices=[("We got you. You're okay.", "am_michael", 1.4)])
stairs = [O("box", (0, 0.09 + 0.18 * i, -0.3 * i), [1.4, 0.18, 0.3], "#8a8f96") for i in range(12)]
stairs += [O("box", (0, 0.185 + 0.18 * i, -0.3 * i + 0.13), [1.2, 0.012, 0.05], "#9fe3b8", material="glow") for i in range(0, 12, 2)]
stairs += [O("box", (-0.75, 1.6, -2), [0.06, 3.6, 6], "#d9d4cc"), O("box", (0.75, 1.6, -2), [0.06, 3.6, 6], "#d9d4cc"),
           O("box", (0.68, 1.0, -1.8), [0.05, 0.05, 4.2], "#9fe3b8", rotate=[31, 0, 0]), O("box", (0, 3.4, -2), [1.5, 0.05, 6], "#cfc9c0"),
           O("plane", (0, 3.37, -1.0), [0.8, 0.3, 1], "#fff4dc", material="glow", rotate=[90, 0, 0])]
s.B(3.8, "eyes", "Monday morning, you take the stairs.", env(stairs, INDOOR, eye=(0, 1.62, 1.2), amb="room", ambient=1.5, light=2.0),
    tracker=T("MONDAY · NEW YORK", clock="8:59:02 AM", sub="STAIRWELL B · FLOOR 1"), hands={"pose": "hold", "holding": "cup"}, head="walk", gaze=(0, 10))

s.save("elevator", "What if you got stuck in an elevator for *41 hours*?",
       "First-person: stuck in an office-tower elevator from Friday night to Sunday afternoon, anchored on the real 41-hour case in New York (1999).",
       "Would you climb out, or wait?", accent="#ff922b", skin="#c68642", thumb="STUCK 41 HOURS", thumb_beat=20)
