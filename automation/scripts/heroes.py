"""What if superheroes were real? — retention format: cold open, quick, toon + big word captions. Generic powers, no brands.
Facts: 8.2 billion / 1 million ≈ 8,000 people; heaviest deadlift ever 501 kg ≈ 1,104 lb (2020); a car ≈ 4,000 lb;
speed of sound ≈ 767 mph at sea level (sonic booms can break windows); air at airliner cruise height ≈ -60 °F;
an invisible eye can't absorb light, so an invisible person would be blind."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from props import O, S, trees

beats = []


def B(dur, cam, caption, env, **k):
    b = {"duration": dur, "scene": "custom", "camera": cam, "subject": {"type": "none"}, "caption": caption, "env": env}
    b.update(k)
    beats.append(b)


def V(objs, bg, focus=(0, 1.4, -4), zoom=1.6, amb="calm", **k):
    return S(objs, bg, ground="none", focus=focus, zoom=zoom, ambient=k.pop("ambient", 1.5), amb=amb, light=k.pop("light", 2.4))


GOLD = ["#2f4b7c", "#f4a259"]; SKY = ["#3a8ee6", "#cfe8ff"]; HIGH = ["#0b2a5a", "#5b8fd1"]; STORM = ["#2b1b3a", "#c2412d"]


def hero(at, col="#e03131", act="fly", seed=4, to=None, ry=0, s=1.0):
    a = [{"type": "move", "to": list(to)}] if to else []
    a.append({"type": "bob", "amount": 0.15, "speed": 1.2})
    x, y, z = at
    cape_to = [to[0], to[1] + 0.9 * s, to[2] + 0.35 * s] if to else None
    cape_a = ([{"type": "move", "to": cape_to}] if cape_to else []) + [{"type": "wobble", "amount": 0.3, "speed": 4}]
    return [O("person", at, s, col, outfit="casual", action=act, seed=seed, color2="#e0ac69", rotate=[0, ry, 0], animate=a),
            O("box", (x, y + 0.9 * s, z + 0.35 * s), [0.7 * s, 1.2 * s, 0.05], "#ffd43b" if col != "#ffd43b" else "#1c7ed6", rotate=[20, ry, 0], animate=cape_a)]


city = [O("box", (0, -0.02, -40), [300, 0.04, 300], "#868e96"), O("building", (0, 0, -60), 4, "#adb5bd", count=40, seed=3, spread=[200, 0, 120]),
        O("building", (0, 0, -30), 3, "#ced4da", count=16, seed=8, spread=[120, 0, 30]), O("box", (0, 0.01, -10), [300, 0.02, 10], "#495057")]
street = [O("box", (0, -0.02, -10), [60, 0.04, 80], "#868e96"), O("box", (0, 0, -10), [8, 0.03, 80], "#495057"),
          O("building", (-16, 0, -24), 6, "#d6cfc4", count=8, seed=3, spread=[2, 0, 40]), O("building", (16, 0, -24), 6, "#c9b8a6", count=8, seed=7, spread=[2, 0, 40]),
          O("person", (0, 0, -8), 1.0, count=10, seed=5, spread=[20, 0, 14], action="point")]

# 0 — cold open: a hero streaks over the city at sunset
B(3.6, "front", "Tomorrow, 1 in a million people wake up with superpowers.", V(city + hero((0, 49.4, 0), to=(0, 50, -5), s=1.0), GOLD, focus=(0, 50, -6), zoom=0.8),
  move="none", sfx=[{"type": "whoosh", "at": 0.4, "dur": 2.0, "gain": 0.9}])
B(3.4, "aerial", "That's about 8,000 superheroes. But here's the catch.", V(city + hero((-20, 50, -40), to=(10, 54, -50), ry=90, seed=2, col="#1c7ed6", s=3.0) +
  hero((20, 44, -30), to=(-6, 48, -36), ry=-90, seed=7, col="#40c057", s=3.0) + hero((0, 40, -60), to=(4, 46, -70), seed=4, s=3.0), GOLD, focus=(0, 40, -45), zoom=4),
  stat={"value": "~8,000", "label": "PEOPLE WITH POWERS", "count_up": True})
# strength
car = lambda at, anim=(): [O("box", at, [2.0, 1.3, 4.4], "#1c7ed6", animate=list(anim)), O("box", (at[0], at[1] + 0.9, at[2] + 0.3), [1.8, 0.6, 2.2], "#1864ab", animate=list(anim))]
B(3.6, "low_front", "Super strength? The heaviest deadlift ever is about 1,100 lb. A car is 4,000.", V(street + hero((0, 0, -6), act="idle", seed=3) +
  car((0, 3.0, -6.3), anim=[{"type": "bob", "amount": 0.1, "speed": 2}]), SKY, focus=(0, 2, -6), zoom=1.4), transition="whip",
  stat={"value": "1,104 LB", "label": "HEAVIEST DEADLIFT EVER (2020)", "count_up": True})
B(3.4, "side", "Grab a car by the bumper, and the bumper just rips off.", V(street + hero((-1.5, 0, -6), act="idle", seed=3) + car((1.5, 0.65, -6)) +
  [O("box", (-0.6, 1.2, -6), [1.9, 0.3, 0.3], "#adb5bd", material="metal", animate=[{"type": "move", "to": [-1.6, 2.0, -6]}, {"type": "spin", "axis": "z", "speed": 3}])],
  SKY, focus=(0, 1.2, -6), zoom=1.2), effects=["shake"], sfx=[{"type": "crack", "at": 0.8, "gain": 0.8}])
# speed
B(3.4, "follow", "Super speed? Pass 767 mph and you break the sound barrier.", V(street + [O("person", (0, 0, 0), 1.0, "#ffd43b", action="sprint", seed=6, color2="#8d5524",
  rotate=[0, 0, 0], animate=[{"type": "move", "to": [0, 0, -60]}])], SKY, focus=(0, 1.2, -10), zoom=1.6), transition="zoom",
  effects=["speedlines", "shockwave", "vapor_cone"], sfx=[{"type": "boom", "at": 1.6, "gain": 1.0}])
B(3.4, "wide", "Every window on the street would shatter.", V(street + [O("box", (0, 6, -20), [1.0, 1.0, 0.1], "#a5d8ff", material="glass", count=40, seed=4,
  spread=[30, 10, 30], animate=[{"type": "move", "to": [0, 0, -18]}, {"type": "spin", "axis": "x", "speed": 4}])], SKY, focus=(0, 2, -12), zoom=2.2),
  effects=["shake", "dust"], sfx=[{"type": "debris", "at": 0.2, "gain": 0.9}])
# flight
B(3.4, "closeup", "Flying? Up where jets fly, the air is about 60 below zero.", V([O("sphere", (0, -40, -60), [200, 20, 200], "#f8f9fa", opacity=0.9, count=8, seed=2,
  spread=[400, 10, 300])] + hero((0, 0, 0), seed=2, col="#1c7ed6", ry=180), HIGH, focus=(0, 1.2, 0), zoom=1.0, amb="wind"), transition="whip",
  stat={"value": "-60 °F", "label": "AT JET CRUISING HEIGHT", "count_up": False}, effects=["glow"])
# invisibility
park = [O("box", (0, -0.02, -10), [60, 0.04, 60], "#69a84f"), O("tree", (0, 0, -16), 1.6, "#3f8f3a", count=12, seed=3, spread=[40, 0, 16]),
        O("box", (0, 0.4, -12), [3, 0.15, 0.8], "#8d6e57", count=3, seed=4, spread=[14, 0, 4]),
        O("person", (0, 0, -5), 1.0, "#7048e8", action="walk", seed=9, color2="#c68642", opacity=0.25, animate=[{"type": "fade_out"}])]
B(3.6, "front", "Invisible? Light would pass right through your eyes. So you'd be blind.", V(park, SKY, focus=(0, 1.4, -5), zoom=1.3), transition="dip",
  effects=["darken"])
# damage + villains
ruin = city[:1] + [O("building", (0, 0, -40), 8, "#868e96", count=20, seed=5, spread=[120, 0, 60], animate=[{"type": "wobble", "amount": 0.1, "speed": 1}]),
                   O("box", (0, 2, -30), [6, 3, 6], "#6c757d", count=14, seed=7, spread=[80, 2, 30]),
                   O("particles", (0, 20, -40), 6, "#a39274", count=30, seed=9, spread=[120, 40, 60], animate=[{"type": "drift", "axis": "y", "amount": 2}])]
B(3.4, "establishing", "One big hero fight could wreck a city. Who pays for that?", V(ruin + hero((-20, 18, -40), act="fly", seed=2, col="#1c7ed6", s=3.0), GOLD, focus=(0, 10, -40), zoom=4),
  effects=["smoke", "shake"], sfx=[{"type": "boom", "at": 0.5, "gain": 0.8}])
B(3.6, "follow", "And the scary part? Not all 8,000 would be good.", V(ruin + [O("person", (0, 0, -8), 1.6, "#212529", outfit="suit", action="idle", seed=11, color2="#8d5524", rotate=[0, 180, 0]),
  O("sphere", (-0.09, 2.9, -7.7), 0.05, "#ff0000", material="glow"), O("sphere", (0.09, 2.9, -7.7), 0.05, "#ff0000", material="glow")], STORM, focus=(0, 2.0, -8), zoom=1.0),
  effects=["lightning", "darken"], sfx=[{"type": "thunder", "at": 0.3, "gain": 0.9}])

sb = {"format": "story", "title": "What if superheroes were real?",
      "premise": "One in a million people wake up with superpowers. Real physics checks strength, speed, flight, invisibility and the damage.",
      "length": "quick", "intro": {"style": "none", "title": "What if *superheroes* were real?"},
      "theme": {"style": "toon", "accent": "#e03131", "captions": "words"},
      "outro": {"chart": False, "question_duration": 3.4, "end": {"kind": "question", "lines": ["WHICH POWER", "WOULD YOU PICK?"], "accent_line": 1}},
      "thumbnail": "SUPERHEROES ARE *REAL*", "thumbnail_beat": 0, "beats": beats}
for i, ch in ((0, "Day One"), (2, "The Powers"), (8, "The Problem")):
    beats[i]["chapter"] = ch
out = Path(__file__).parent / "heroes.json"
out.write_text(json.dumps(sb, indent=1, ensure_ascii=False))
print(out, len(beats))
