"""What if it rained forever? One fixed view of your street (witness style) flooding day by day; twist ending.
Facts (rounded, widely cited): all water vapor in the air would cover Earth only ~1 inch (2.5 cm) deep if it fell at once;
Mawsynram, India: ~39 ft (~11.9 m) of rain a year; Carnian Pluvial Episode ~232 million years ago: rain for ~1-2 million years,
followed by the rise of the dinosaurs; mosquitoes breed in standing water."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403
from props import animal  # noqa: E402

v = Video()
RAIN = ["#4a5568", "#a0aec0"]; DARK = ["#2d3748", "#718096"]; GLOOM = ["#1a202c", "#4a5568"]


def street(level=0.0, extra=(), brown=0.0, lights=True):
    """Your street from the porch: houses, cars, trees. level = flood depth in meters."""
    grass = "#4f7a3a" if brown < 0.5 else "#8a7a4a"
    p = [O("box", (0, -0.02, -20), [120, 0.04, 80], grass), O("box", (0, 0, -16), [120, 0.03, 8], "#495057"),
         O("box", (0, 0.02, -10.5), [120, 0.03, 2.4], "#ced4da")]
    p += house((-14, 0, -26), "#ffe8cc", "#7a4a3a") + house((-4, 0, -27), "#dbe4ff", "#495057") + house((6, 0, -26), "#e9dcc9", "#5c3d2e") + house((16, 0, -27), "#fff3bf", "#7a4a3a")
    p += [O("tree", (0, 0, -21), 1.5, "#3f6b3a" if brown < 0.5 else "#6b5a2a", count=8, seed=4, spread=[60, 0, 4]),
          O("box", (-6, 0.65, -15), [4.4, 1.3, 2.0], "#e03131"), O("box", (8, 0.65, -17), [4.4, 1.3, 2.0], "#1c7ed6")]
    if lights:
        p.append(O("box", (0, 1.3, -24.6), [1.0, 0.8, 0.05], "#ffe8a3", material="glow", count=6, seed=3, spread=[34, 0.5, 0]))
    if level > 0:
        p.append(O("box", (0, level / 2, -18), [140, level, 70], "#5b7a99", material="glossy", opacity=0.88,
                   animate=[{"type": "bob", "amount": 0.03, "speed": 0.6}]))
    return p + list(extra)


def W(objs, bg, weather="rain"):
    e = S(objs, bg, ground="none", focus=(0, 0.6, 6), zoom=0.35, ambient=1.3, amb="wind", light=1.8)
    e["weather"] = weather
    return e


def B(dur, cap, env, t, sub="", **k):
    v.B(dur, "witness", cap, env, t, sub, move="none", **k)


kids = [P((-2, 0, -12), "#fab005", "run", 6, outfit="child", s=0.65), P((1, 0, -11.5), "#40c057", "run", 7, outfit="child", s=0.65)]
B(4.4, "In 3 seconds, it starts raining on your street. And it never stops.", W(street(extra=[crowd(5, 3, at=(0, 0, -12), spread=(30, 0, 4))]), SKY, "clear"),
  "+0 SEC", "A SUNNY SATURDAY", sfx=[{"type": "thunder", "at": 3.0, "gain": 0.7}])
B(3.4, "Day 1: kids splash in puddles. Cozy, right? Just wait.", W(street(extra=kids), RAIN), "DAY 1", "IT'S STILL RAINING")
B(3.4, "Day 7: the ground is soaked. Water has nowhere to go.", W(street(0.25), RAIN), "DAY 7", "STILL RAINING")
B(3.4, "Day 14: the street turns into a river. Cars float away.", W(street(0.9, extra=[O("box", (-20, 1.0, -15), [4.4, 1.3, 2.0], "#fab005",
  animate=[{"type": "move", "to": [20, 1.0, -15]}, {"type": "wobble", "amount": 0.2, "speed": 1}])]), DARK), "DAY 14", "STILL RAINING", transition="whip")
B(3.4, "Day 30: no sunshine for a month. The crops rot in the fields.", W(street(1.0, brown=1.0), DARK), "DAY 30", "NO SUN SINCE DAY 1")
B(3.4, "Mosquitoes explode. They breed in standing water.", W(street(1.0, brown=1.0, extra=[O("particles", (0, 3, -14), 0.3, "#111111", count=60, seed=5,
  spread=[40, 4, 12], animate=[{"type": "drift", "axis": "x", "amount": 0.6}])]), DARK), "DAY 45", "BZZZZ", sfx=[{"type": "swell", "at": 0.3, "dur": 2.4, "gain": 0.4}])
boats = [O("box", (-18, 1.25, -14), [3.4, 0.5, 1.4], "#f8f9fa", animate=[{"type": "move", "to": [12, 1.25, -14]}]),
         O("box", (16, 1.25, -17), [3.4, 0.5, 1.4], "#ff922b", animate=[{"type": "move", "to": [-10, 1.25, -17]}])]
B(3.4, "Day 90: you commute to work by boat.", W(street(1.1, brown=1.0, extra=boats), GLOOM), "DAY 90", "STILL RAINING", transition="whip")
B(3.6, "The wettest town on Earth, Mawsynram in India, gets about 39 feet of rain a year.", W(street(1.4, brown=1.0, lights=False), GLOOM, "storm"), "DAY 200",
  "THE POWER IS OUT", stat={"value": "39 FT", "label": "OF RAIN A YEAR IN MAWSYNRAM, INDIA", "count_up": True}, effects=["lightning"])
B(3.6, "Here's the twist: all the water in the sky would cover Earth only about 1 inch deep.", W(street(1.6, brown=1.0, lights=False, extra=[O("box", (14, 1.7, -20), [2.4, 1.8, 2.4], "#8d6e57", rotate=[0, 30, 15],
  animate=[{"type": "move", "to": [-6, 1.7, -18]}, {"type": "wobble", "amount": 0.2, "speed": 0.8}])]), GLOOM, "storm"), "DAY 365",
  "ONE YEAR", stat={"value": "~1 INCH", "label": "ALL THE WATER IN EARTH'S AIR, IF IT FELL AT ONCE", "count_up": False})
B(3.4, "So to rain forever, the oceans must keep feeding the clouds.", W(street(1.5, brown=1.0, lights=False), GLOOM), "DAY 365", "ONE YEAR",
  sfx=[{"type": "rumble", "at": 0.4, "dur": 2.6, "gain": 0.5}])
jungle = [O("box", (0, -0.02, -20), [140, 0.04, 90], "#5c7a2e"), O("tree", (0, 0, -24), 2.6, "#2b8a3e", count=16, seed=6, spread=[80, 0, 14]),
          O("box", (0, 0.1, -14), [140, 0.2, 6], "#3d6b8a", material="glossy")]
B(3.6, "It happened once. About 232 million years ago, it rained for about a million years.", W(jungle, RAIN), "232 MILLION YEARS AGO", "REAL",
  transition="flash", tooltip={"label": "REAL", "text": "Scientists call it the Carnian Pluvial Episode."})
B(3.8, "And when it finally stopped... the dinosaurs took over. Rain forever, or sun forever?",
  W(jungle + animal((-6, 0, -17), 2.6, "#6b8e23", neck=2.6) + animal((7, 0, -20), 2.2, "#7a9a3a", neck=2.4), ["#4a8fd1", "#e6f4d7"], "clear"), "AFTER THE RAIN", "THE AGE OF DINOSAURS", effects=["rays"])
v.save("rain", "What if it rained forever?", "It starts raining on your street and never stops: floods, no sun, boats to work, and the true story of a million-year rain.",
       "witness", "SINCE IT STARTED RAINING", ["RAIN FOREVER", "OR SUN FOREVER?"], "IT NEVER *STOPS* RAINING", 3, accent="#74c0fc", countdown=True)
p = Path(sys.argv[0]).resolve().parent / "rain.json"
d = json.loads(p.read_text()); d["theme"]["anchor"] = "none"; p.write_text(json.dumps(d, indent=1, ensure_ascii=False))
