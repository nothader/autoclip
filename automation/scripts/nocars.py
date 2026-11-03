"""What if every car disappeared? (film house style, narrated, dark music). Facts (rounded, widely cited):
~1.5 billion cars worldwide; ~9 in 10 US households own a car; average US one-way commute ~27 min; walking ~3 mph (20 mi ~ 7 h);
WHO: ~1.2 million road-crash deaths a year; 2020 lockdowns: city NO2 smog fell within weeks."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403

v = Video()
FADE = [{"type": "fade_out"}]
car = lambda x, z, col, ry=0, anim=FADE: O("box", (x, 0.65, z), [2.0, 1.3, 4.4], col, rotate=[0, ry, 0], animate=list(anim))
road = lambda extra=(), cars=(): [O("box", (0, -0.02, -14), [140, 0.04, 80], "#7da35a"), O("box", (0, 0, -12), [140, 0.03, 10], "#495057"),
                                  O("box", (0, 0.04, -12), [140, 0.01, 0.15], "#ffd43b"), O("box", (0, 0.02, -5.5), [140, 0.03, 2.4], "#ced4da"),
                                  O("tree", (0, 0, -22), 1.5, "#4f7a3a", count=10, seed=4, spread=[70, 0, 6])] + \
    house((-12, 0, -24), "#ffe8cc", "#7a4a3a") + house((0, 0, -25), "#dbe4ff", "#495057") + house((12, 0, -24), "#e9dcc9", "#5c3d2e") + list(cars) + list(extra)
bike = lambda x, z, col="#e03131": [O("torus", (x - 0.5, 0.35, z), [0.33, 0.33, 0.04], "#212529", rotate=[0, 90, 0]),
                                    O("torus", (x + 0.5, 0.35, z), [0.33, 0.33, 0.04], "#212529", rotate=[0, 90, 0]),
                                    O("box", (x, 0.6, z), [1.0, 0.06, 0.06], col, rotate=[0, 0, 12])]
YOU = lambda act="sit", at=(0, 0.55, -10.5), ry=0, anim=(): P(at, BOY, act, 2, ry=ry, anim=anim)

# 0 — cold open: you're driving
v.B(4.4, "front", "In 3 seconds, every car on Earth vanishes. All 1.5 billion. Even the one you're in.",
    V(road(cars=[O("box", (0, 0.3, -10.5), [2.0, 0.6, 4.4], "#e03131"), O("box", (0, 0.75, -11.6), [1.8, 0.5, 0.08], "#a5d8ff", material="glass", opacity=0.5), car(-9, -13.5, "#1c7ed6", 90, [{"type": "move", "to": [9, 0.65, -13.5]}]),
                 car(9, -13.5, "#fab005", 90, [{"type": "move", "to": [-9, 0.65, -13.5]}])], extra=[YOU("sit", (0, 0.2, -10.3))]), SKY, focus=(0, 1.3, -10.5), zoom=0.7),
    "+0 SEC", "YOUR MORNING DRIVE", move="none", stat={"value": "1.5 BILLION", "label": "CARS ON EARTH", "count_up": True})
v.B(3.6, "front", "Poof. You drop onto the road, still holding the steering wheel.", V(road(extra=[YOU("kneel", (0, 0, -10.5)),
    O("torus", (0.25, 0.75, -10.9), [0.18, 0.18, 0.03], "#212529", rotate=[70, 0, 0])]), SKY, focus=(0, 0.8, -10.5), zoom=0.75),
    "+1 SEC", effects=["shake"], sfx=[{"type": "impact", "at": 0.3, "gain": 0.8}])
v.B(3.6, "wide", "Every highway goes silent. No horns. No engines. Just birds.", V(road(extra=[crowd(8, 4, at=(0, 0, -12), spread=(40, 0, 6), act="idle"),
    O("cone", (0, 9, -20), [0.14, 0.45, 0.14], "#2b2f36", rotate=[0, 0, 90], count=10, seed=2, spread=[30, 3, 8], animate=[{"type": "drift", "axis": "x", "amount": 0.3}])]),
    SKY, focus=(0, 1.5, -12), zoom=1.6), "+1 MIN")
v.B(3.6, "follow", "But your job is 20 miles away. On foot, that's about 7 hours. Each way.", V(road(extra=[YOU("walk", (0, 0, -6), 180,
    [{"type": "move", "to": [0, 0, -2]}])]), GOLD, focus=(0, 1.2, -5), zoom=0.8), "+1 HOUR", "THE NEW COMMUTE",
    stat={"value": "7 HOURS", "label": "WALKING 20 MILES", "count_up": False}, transition="whip")
shop = room("#fff3bf", "#e9ecef", "#a5d8ff", w=14, d=12, extra=[crowd(14, 6, at=(0, 0, -6), spread=(10, 0, 6), act="run")] +
            sum([bike(x, -10, c) for x, c in ((-4, "#e03131"), (-1.5, "#1c7ed6"), (1, "#40c057"), (3.5, "#fab005"))], []))
v.B(3.4, "wide", "Bike shops sell out by lunch.", V(shop, ["#fff3bf", "#ffd8a8"], focus=(0, 1.0, -7), zoom=1.2, bounce="#fff3bf"), "+4 HOURS", transition="whip",
    sfx=[{"type": "pop", "at": 0.6, "gain": 0.4}, {"type": "pop", "at": 1.4, "gain": 0.4}])
v.B(3.6, "follow", "The suburbs get hit hardest. About 9 in 10 American homes own a car.", V(road(extra=[P((-2, 0, -6), GIRL, "walk", 3, ry=180,
    anim=[{"type": "move", "to": [-2, 0, -2]}]), O("box", (-1.6, 0.9, -6), [0.35, 0.45, 0.3], "#c97a40", animate=[{"type": "move", "to": [-1.6, 0.9, -2]}])]), GOLD,
    focus=(-2, 1.2, -5), zoom=0.8), "+1 DAY", "GROCERIES: 3 MILES AWAY", stat={"value": "9 IN 10", "label": "US HOMES WITH A CAR", "count_up": False})
v.B(3.4, "front", "Pizza delivery now comes by bike. It arrives cold. Every time.", V(road(extra=[P((0, 0, -7.5), "#e03131", "point", 6, ry=0)] + bike(1.4, -7.8) +
    [O("box", (0.4, 1.0, -7.2), [0.5, 0.06, 0.5], "#f4a259")]), GOLD, focus=(0.4, 1.2, -7.5), zoom=0.85), "+2 DAYS", sfx=[{"type": "pop", "at": 1.2, "gain": 0.3}])
v.B(3.6, "side", "Here's the scary part: ambulances vanish too. Help comes on foot.", V(road(extra=[P((0, 0, -9), "#40c057", "run", 8, outfit="scrubs", ry=90,
    anim=[{"type": "move", "to": [6, 0, -9]}]), P((7, 0.3, -9.5), "#868e96", "lie", 9)]), DUSK, focus=(3, 1.0, -9), zoom=1.0), "+3 DAYS", transition="dip",
    effects=["tunnel"], sfx=[{"type": "siren", "at": 0.2, "dur": 2.4, "gain": 0.3}, {"type": "heartbeat", "at": 0.6, "dur": 2.6, "gain": 0.6}])
v.B(3.6, "far", "But the air gets cleaner, fast. In the 2020 lockdowns, city smog dropped within weeks.", V(city([crowd(14, 9, at=(0, 0, -14), spread=(16, 0, 14))]),
    ["#339af0", "#e3fafc"], focus=(0, 2.5, -20), zoom=1.2), "+1 MONTH", effects=["rays"])
v.B(3.8, "front", "And about 1.2 million people die in road crashes every year. That number drops to almost zero.",
    V(park([P((-0.6, 0, -6), GIRL, "point", 3), P((0.6, 0, -6), BOY, "point", 2), crowd(8, 11, at=(0, 0, -12), spread=(20, 0, 6))]), SKY,
      focus=(0, 1.4, -6), zoom=0.7), "+1 YEAR", stat={"value": "1.2 MILLION", "label": "ROAD DEATHS A YEAR (WHO)", "count_up": True})
lot = [O("box", (0, -0.02, -14), [100, 0.04, 70], "#868e96")] + [O("box", (-12 + i * 3, 0.01, -12), [0.12, 0.02, 4], "#f8f9fa") for i in range(9)] + \
      [O("tree", (0, 0, -12), 1.3, "#40c057", count=10, seed=5, spread=[24, 0, 8], animate=[{"type": "grow"}]),
       O("box", (0, 0.02, -12), [26, 0.03, 10], "#69a84f", opacity=0.9, animate=[{"type": "fade_in"}])]
v.B(3.6, "aerial", "Parking lots turn into parks.", V(lot, SKY, focus=(0, 0.6, -10), zoom=1.2), "+2 YEARS", transition="whip", effects=["confetti"])
v.B(3.6, "follow", "And kids play in the middle of the street again.", V(road(extra=[P((-1.5, 0, -12), "#fab005", "run", 6, outfit="child", s=0.65,
    anim=[{"type": "move", "to": [1.5, 0, -12]}]), P((1.5, 0, -11), "#40c057", "run", 7, outfit="child", s=0.65, anim=[{"type": "move", "to": [-1.5, 0, -11]}]),
    O("sphere", (0, 0.3, -11.5), 0.25, "#e03131", animate=[{"type": "bob", "amount": 0.4, "speed": 2}])]), GOLD, focus=(0, 0.9, -11.5), zoom=0.8), "+5 YEARS")
v.B(4.0, "far", "So be honest: a better world, or total chaos?", V(road(extra=[YOU("idle", (0, 0, -9), 180), crowd(10, 13, at=(0, 0, -12), spread=(30, 0, 6))]),
    DUSK, focus=(0, 1.2, -10), zoom=1.8), "+5 YEARS", move="pull_out", effects=["glow"])
v.save("nocars", "What if every car disappeared?", "All 1.5 billion cars on Earth vanish at once: walking commutes, sold-out bikes, cold pizza, cleaner air and safer streets.",
       "film", "SINCE THE CARS VANISHED", ["BETTER WORLD", "OR TOTAL CHAOS?"], "EVERY *CAR* IS GONE", 1, accent="#ffd43b")
