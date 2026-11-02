"""What if we lived on Mars and Earth was empty? (swap recipe: countdown cold open, ~35 s, pick-a-side end).
Facts: Mars gravity 0.38 g; air <1% as thick as Earth's, mostly CO2; average ~ -80 F; sol = 24 h 37 min; year = 687 Earth days;
radio/light delay 3-22 min; without people, power grids fail within days (fuel/maintenance); Chernobyl zone: wolves, elk, boar returned."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403
from props import dog, animal

v = Video()
MARS = ["#7a2e12", "#e8a87c"]; MARS_DUSK = ["#2b1630", "#c0603a"]; MARS_NIGHT = "stars"
red = lambda extra=(): [O("box", (0, -0.03, -20), [400, 0.04, 400], "#b5522b"),
                        O("rock", (0, 0.5, -30), 2.5, "#8a3b1e", count=14, seed=3, spread=[120, 0, 40]),
                        O("cone", (-60, 12, -120), [70, 24, 40], "#9c4a28"), O("cone", (70, 16, -140), [90, 32, 50], "#8a3b1e")] + list(extra)
dome = lambda extra=(): red([O("sphere", (0, 0, -14), [16, 9, 16], "#ffe8cc", material="glass", opacity=0.25),
                             O("box", (0, 0.02, -14), [28, 0.04, 28], "#ced4da"),
                             O("building", (0, 0, -18), 1.6, "#dee2e6", count=8, seed=4, spread=[16, 0, 8]),
                             O("tree", (0, 0, -12), 0.9, "#40c057", count=6, seed=5, spread=[16, 0, 6])] + list(extra))
def suit(at, act="walk", anim=(), seed=4, helmet=False):
    x, y, z = at
    a = list(anim)
    p = [O("person", at, 1.0, "#f8f9fa", action=act, seed=seed, color2="#e0ac69", animate=a)]
    if helmet:
        p.append(O("sphere", (x, y + 1.62, z), 0.24, "#a5d8ff", material="glass", opacity=0.55, animate=a))
    return p
empty_city = lambda grow=0.0, extra=(): city([O("box", (-4, 0.65, -14), [4.4, 1.3, 2.0], "#e03131"), O("box", (6, 0.65, -18), [4.4, 1.3, 2.0], "#1c7ed6")] +
    ([O("cone", (0, 0.3, -16), [0.5, 0.8 + grow, 0.5], "#5c940d", count=int(50 * grow), seed=4, spread=[40, 0, 30]),
      O("tree", (0, 0, -16), 1.0 + grow, "#3f6b3a", count=int(16 * grow), seed=7, spread=[30, 0, 30])] if grow else []) + list(extra))

v.B(4.4, "wide", "In 3 seconds, all 8 billion of us move to Mars. Earth is left totally empty.",
    V(dome([crowd(24, 3, at=(0, 0, -12), spread=(18, 0, 10)), O("cone", (14, 3, -30), [2, 6, 2], "#f8f9fa", animate=[{"type": "move", "to": [14, 40, -30]}]),
      O("particles", (14, 1, -30), 1.0, "#ffa94d", count=20, seed=2, spread=[3, 3, 3], animate=[{"type": "move", "to": [14, 36, -30]}])]), MARS, focus=(0, 2, -14), zoom=1.8, amb="wind"), "+0 SEC", "MOVING DAY",
    move="none", sfx=[{"type": "shimmer", "at": 3.0, "gain": 0.7}])
v.B(3.4, "low_front", "Mars gravity is only 38% of Earth's. You can jump like a superhero.",
    V(dome(suit((0, 1.5, -6), "float", [{"type": "bob", "amount": 1.4, "speed": 0.8}])), MARS, focus=(0, 2.2, -6), zoom=1.2, amb="wind"), "DAY 1",
    stat={"value": "0.38 G", "label": "GRAVITY ON MARS", "count_up": False})
v.B(3.4, "side", "But step outside. The air is less than 1% as thick as Earth's.",
    V(red(suit((0, 0, -6), "walk", [{"type": "move", "to": [3, 0, -6]}]) + [O("particles", (0, 2, -8), 0.5, "#e8a87c", count=30, seed=4, spread=[30, 4, 10],
      animate=[{"type": "drift", "axis": "x", "amount": 2}])]), MARS, focus=(1, 1.3, -6), zoom=1.0, amb="wind"), "DAY 1", effects=["dust"], transition="whip")
v.B(3.4, "closeup", "Without a suit, you'd pass out in seconds. And it's about 80 below zero.",
    V(red(suit((0, 0, -6), "kneel", helmet=True)), MARS_DUSK, focus=(0, 1.2, -6), zoom=0.7, amb="wind"), "DAY 2", stat={"value": "-80 °F", "label": "AVERAGE MARS TEMPERATURE", "count_up": False},
    effects=["tunnel"], sfx=[{"type": "breath", "at": 0.3, "dur": 2.8, "gain": 0.9}])
v.B(3.4, "far", "Meanwhile, back on Earth... the lights go out within days.",
    V(empty_city(extra=[O("box", (0, 8, -29.9), [1.0, 0.8, 0.05], "#ffe8a3", material="glow", count=12, seed=5, spread=[60, 10, 0], animate=[{"type": "fade_out"}])]),
      DUSK, focus=(0, 3, -22), zoom=1.4), "DAY 3", transition="dip")
pack = (animal((-1.6, 0, -15), 0.8, "#c08552", anim=[{"type": "bob", "amount": 0.05, "speed": 3}]) + animal((0.4, 0, -16.5), 0.8, "#343a40", anim=[{"type": "bob", "amount": 0.05, "speed": 3}]) +
        animal((2.2, 0, -15.5), 0.8, "#e9ecef", anim=[{"type": "bob", "amount": 0.05, "speed": 3}]))
v.B(3.4, "far", "Dogs and cats take over the empty streets.", V(empty_city(extra=pack), GOLD, focus=(0.4, 0.7, -13.5), zoom=0.42), "1 MONTH")
v.B(3.4, "wide", "In 20 years, trees burst through the roads.",
    V(empty_city(1.2), SKY, focus=(0, 2, -14), zoom=2.0, amb="forest"), "20 YEARS", transition="whip")
wolves = [O("box", (0, 0, 0), 1, "#000000")][:0]
for x, z, c in ((-2, -10, "#868e96"), (0.5, -12, "#adb5bd"), (3, -9, "#6c757d")):
    wolves += animal((x, 0, z), 1.0, c, anim=[{"type": "bob", "amount": 0.05, "speed": 2}])
v.B(3.6, "far", "Wolves move back into the cities. It already happened near Chernobyl.",
    V(empty_city(0.7, wolves), ["#3b5b3a", "#c9d8a6"], focus=(1, 0.7, -8), zoom=0.45, amb="forest"), "50 YEARS",
    tooltip={"label": "REAL", "text": "Wolves, elk and boar returned to the empty Chernobyl zone."})
v.B(3.4, "far", "On Mars, a day lasts 37 minutes longer. And a year is 687 days.",
    V(dome([crowd(12, 9, at=(0, 0, -12), spread=(14, 0, 8), act="idle"), O("sphere", (0, 3, -14), 0.2, "#ffd43b", material="glow", count=12, seed=3,
      spread=[14, 2, 10], animate=[{"type": "pulse", "amount": 0.4, "speed": 2}])]), MARS_DUSK, focus=(0, 3, -14), zoom=1.6), "1 YEAR", effects=["confetti"],
    stat={"value": "687 DAYS", "label": "ONE YEAR ON MARS", "count_up": True})
v.B(3.4, "follow", "Texting Grandma's old house on Earth? It takes up to 20 minutes to arrive.",
    V(dome(suit((0, 0, -6), "phone")), MARS, focus=(0, 1.4, -6), zoom=0.8), "1 YEAR")
v.B(3.8, "low_front", "At night, Earth is just a bright blue star in the Martian sky.",
    V(red(suit((0, 0, -6), "point") + [O("sphere", (1.5, 7, 14), 0.35, "#74c0fc", material="glow", animate=[{"type": "pulse", "amount": 0.3, "speed": 1}])]),
      MARS_NIGHT, focus=(0, 2.4, -6), zoom=1.2, amb="space"), "NIGHT", transition="dip", effects=["glow"])
v.B(3.8, "far", "Here's the real question: if Earth healed, would you ever go back?",
    V(empty_city(2.0, [O("person", (0, 0, -8), 1.0, "#f8f9fa", action="walk", seed=4, color2="#e0ac69", animate=[{"type": "move", "to": [0, 0, -4]}])]),
      ["#4a8fd1", "#e6f4d7"], focus=(0, 1.6, -12), zoom=2.2, amb="forest"), "100 YEARS", move="pull_out", effects=["rays"])
v.save("mars", "What if we lived on Mars and Earth was empty?", "All 8 billion people move to Mars and Earth is left empty. Life on Mars vs. nature taking Earth back.",
       "cinematic", "SINCE THE MOVE", ["MARS OR", "EMPTY EARTH?"], "WE LEFT *EARTH*", 1, accent="#ff922b", palette="warm")
