"""What if you fell out of a plane? Fresh world: open sky at sunrise, clouds rushing UP past you, the land far below.
Hook type: danger + number (no countdown). Facts (rounded, widely cited): cruise ~35,000 ft, air ~-60 F; belly-down terminal
velocity ~120 mph; falling 35,000 ft takes ~3 min; Vesna Vulovic survived a 33,330 ft fall (1972, Guinness record);
Juliane Koepcke, 17, fell ~2 mi into the Amazon still in her seat row (1971) and walked out ~11 days later."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403

v = Video()
DAWN_HI = ["#1d3c78", "#ff9f68"]; HIGH = ["#2754a3", "#9ec9ff"]; MID = ["#4a8fe0", "#e3f2ff"]; LOW = ["#6aa9e8", "#f1f8ff"]; DUSK = ["#3a2a5c", "#ff9f68"]
ME = dict(outfit="hoodie", seed=11, skin="#c68642")


def me(at=(0, 0, 0), act="float", ry=180, anim=()):
    return P(at, "#2f9e44", act, ME["seed"], outfit=ME["outfit"], ry=ry, anim=anim, skin=ME["skin"])


def clouds_up(y=-30, n=14, seed=3, size=6, col="#ffffff"):   # clouds rushing up past you = falling
    return O("sphere", (0, y, -6), [size, size * 0.35, size], col, opacity=0.85, count=n, seed=seed, spread=[60, 10, 40],
             animate=[{"type": "move", "to": [0, y + 70, -6]}])


def land(depth, extra=()):
    """the ground far below: farmland patches, a lake, a forest, a snowy ridge"""
    g = [O("box", (0, -depth, 0), [4000, 1, 4000], "#6b8e3a"),
         O("box", (-300, -depth + 1, -200), [500, 1, 400], "#a3b85a"), O("box", (35, -depth + 1, 15), [45, 1, 35], "#c9b45a"),
         O("cylinder", (-22, -depth + 1.2, -30), [30, 1, 22], "#2f6fa8", material="glossy"),
         O("tree", (20, -depth, -25), 3, "#2b6b2b", count=30, seed=7, spread=[30, 0, 25]),
         O("cone", (-30, -depth + 10, 20), [40, 22, 30], "#e9f2f7")]
    return g + list(extra)


def plane(at, anim=()):
    x, y, z = at
    a = list(anim)
    return [O("capsule", at, [2.4, 22, 2.4], "#f1f3f5", material="glossy", rotate=[90, 0, 0], animate=a),
            O("box", at, [26, 0.4, 4], "#dee2e6", animate=a), O("box", (x, y + 2.4, z + 9), [0.4, 4, 3], "#e03131", animate=a)]


def SV(objs, bg, focus=(0, 1.0, 0), zoom=1.0, amb="wind"):
    e = V(objs, bg, focus=focus, zoom=zoom, amb=amb)
    e["set"]["sky_detail"] = "none"
    return e


spin = [{"type": "wobble", "axis": "z", "amount": 0.35, "speed": 1.4}]
v.B(4.2, "closeup", "You just fell out of a plane. 35,000 feet up. You have about 3 minutes.",
    SV([me(ry=0, anim=spin), clouds_up(-20), O("particles", (0, 0, 0), 0.2, "#ffffff", count=20, seed=2, spread=[10, 10, 10],
        animate=[{"type": "move", "to": [0, 25, 0]}])] + plane((6, 30, -40), [{"type": "move", "to": [40, 34, -80]}]), DAWN_HI, focus=(0, 1.3, 0), zoom=1.1),
    "35,000 FT", "SUNRISE OVER THE CLOUDS", move="push_in", effects=["shake", "speedlines"],
    sfx=[{"type": "whoosh", "at": 0.1, "dur": 3.5, "gain": 1.0}])
v.B(3.6, "side", "It's 60 below zero up here. But that's not the scary part.", SV([me(act="kneel"), clouds_up(-25, seed=5),
    O("particles", (0, 1, 0), 0.15, "#e7f5ff", count=30, seed=4, spread=[6, 6, 6], animate=[{"type": "move", "to": [0, 15, 0]}])], DAWN_HI, zoom=0.65),
    "34,000 FT", "-60 °F", stat={"value": "-60 °F", "label": "AIR AT CRUISING HEIGHT", "count_up": False}, effects=["speedlines"])
v.B(3.8, "side", "The air is too thin. You black out. Then you wake up lower down.",
    SV([me(act="lie", anim=spin), clouds_up(-30, seed=8)], ["#1b2f5c", "#6f8fc8"], focus=(0, 0.6, 0), zoom=1.0), "28,000 FT", effects=["tunnel", "darken"],
    sfx=[{"type": "heartbeat", "at": 0.2, "dur": 3.4, "gain": 0.8}])
v.B(3.6, "follow", "You hit top speed: about 120 miles per hour.", SV([me(act="fly"), clouds_up(-30, n=18, seed=9, size=8)], HIGH, focus=(0, 0.6, 0), zoom=1.1),
    "20,000 FT", "TERMINAL VELOCITY", stat={"value": "120 MPH", "label": "TOP FALLING SPEED, BELLY DOWN", "count_up": True},
    effects=["speedlines", "motion_blur"], transition="whip")
v.B(3.6, "low_front", "Spread out like a starfish. It slows you a little, and lets you steer.", SV([me(act="fly", anim=[{"type": "spin", "axis": "y", "speed": 0.3}]),
    clouds_up(-30, seed=11, col="#ffe8cc")], ["#2a62b8", "#ffd6a5"], zoom=0.8), "15,000 FT", move="arc_left")
v.B(3.8, "follow", "Now pick your landing spot. Fields. A lake. A forest. Snow on the mountain.", SV([me(act="fly")] + land(60), MID, focus=(0, 1.0, 0), zoom=1.6),
    "8,000 FT", "LOOK DOWN", transition="zoom", move="swoop_in")
v.B(3.6, "follow", "Not the lake. At this speed, water hits almost like concrete.", SV([me(act="fly")] + land(35), MID, focus=(0, 1.0, 0), zoom=1.3),
    "3,000 FT", effects=["shake"])
v.B(3.8, "follow", "Your best bet: thick trees or deep snow. They slow you down before the ground does.", SV([me(act="fly", at=(0, 0, 0))] +
    land(18), LOW, focus=(0, 1.0, 0), zoom=1.1), "1,000 FT", transition="whip")
museum = [O("box", (0, -0.02, -10), [80, 0.04, 60], "#f1f5f9"), O("cone", (0, 0.1, -10), [30, 3, 20], "#e9f2f7"),
          O("tree", (0, 0, -14), 2.2, "#3d6b4a", count=14, seed=21, spread=[50, 0, 20]),
          O("capsule", (6, 1.0, -13), [2.0, 8, 2.0], "#adb5bd", rotate=[90, 30, 12]), O("box", (8.5, 0.6, -12), [6, 0.3, 1.6], "#868e96", rotate=[0, 30, -8]),
          O("particles", (0, 4, -9), 0.3, "#ffffff", count=30, seed=4, spread=[20, 8, 10], animate=[{"type": "drift", "axis": "y", "amount": -0.4}]),
          P((-0.8, 0, -6), "#c92a2a", "kneel", 14, outfit="suit", ry=180, skin="#f1c27d")]
v.B(3.8, "wide", "It has happened. In 1972, flight attendant Vesna Vulović fell 33,000 feet and lived.", SV(museum, ["#8aa2c0", "#e9eef5"], focus=(0.5, 1.0, -7), zoom=1.0),
    "THE RECORD", "GUINNESS WORLD RECORD", transition="flash",
    stat={"value": "33,330 FT", "label": "HIGHEST FALL SURVIVED WITHOUT A PARACHUTE", "count_up": True})
jungle = [O("box", (0, -0.02, -10), [80, 0.04, 60], "#2f5e2a"), O("tree", (0, 0, -12), 3.2, "#2b8a3e", count=22, seed=12, spread=[60, 0, 30]),
          O("box", (0, 0.4, -4), [1.6, 0.8, 0.8], "#495057"), P((2, 0, -4), "#f8f9fa", "walk", 16, outfit="child", s=0.85, ry=270,
          anim=[{"type": "move", "to": [6, 0, -6]}], skin="#f1c27d")]
v.B(3.8, "follow", "A girl, 17, fell into the Amazon in her seat. She walked out 11 days later.", SV(jungle, ["#3d6b3a", "#c9e6a8"], focus=(3, 1.0, -5),
    zoom=1.0, amb="forest"), "1971", "JULIANE KOEPCKE, PERU", sfx=[{"type": "steps", "at": 0.4, "dur": 3.0, "gain": 0.4}])
v.B(4.2, "follow", "Ten seconds left. Do you aim for the trees, or the snow?", SV([me(act="fly", at=(0, 40, 0))] +
    land(-32), DUSK, focus=(0, 40, 0), zoom=1.0), "200 FT", "CHOOSE NOW", move="crane_down",
    effects=["speedlines"])
v.save("planefall", "What if you fell out of a plane?", "You fall from 35,000 feet with about 3 minutes until the ground: the cold, the speed, where to land, and two people who really survived.",
       "film", "FALLING", ["TREES", "OR SNOW?"], "YOU FELL *35,000 FT*", 0, accent="#ff922b")
