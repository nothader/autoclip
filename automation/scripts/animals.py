"""What if animals were as smart as humans? — retention test: cold open, quick, bold.
Facts: crows recognize human faces and remember them for years (UW study); octopuses ~500 million neurons, most in their arms;
chimps share ~99% of our DNA (98.8%); dolphins use signature whistles like names; ~20 quadrillion ants (2022 estimate) ≈ 2.5 million per person."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from props import O, S, dog, cow, birds, trees, animal, house, fence

beats = []


def B(dur, cam, caption, env, **k):
    b = {"duration": dur, "scene": "custom", "camera": cam, "subject": {"type": "none"}, "caption": caption, "env": env}
    b.update(k)
    beats.append(b)


def V(objs, bg, focus=(0, 1.0, -3), zoom=1.4, amb="calm", **k):
    e = S(objs, bg, ground="none", focus=focus, zoom=zoom, ambient=k.pop("ambient", 1.5), amb=amb, light=k.pop("light", 2.4))
    if "bounce" in k:
        e["set"]["bounce"] = k["bounce"]
    return e


SKY = ["#4dabf7", "#d0ebff"]; GOLD = ["#2f4b7c", "#f2a65a"]; SEA = ["#0b3d5c", "#3aa0c8"]
kitchen = [O("box", (0, 0, -2), [8, 0.05, 8], "#c9a27a"), O("box", (0, 1.5, -5), [8, 3, 0.1], "#fff3bf"), O("box", (-4, 1.5, -2), [0.1, 3, 8], "#ffe8cc"),
           O("box", (0, 0.75, -2.6), [1.8, 0.06, 1.1], "#8d6e57"), O("cylinder", (0, 0.37, -2.6), [0.12, 0.74, 0.12], "#6b4f3a"),
           O("box", (0.2, 0.8, -2.5), [0.5, 0.03, 0.35], "#f8f9fa"), O("plane", (1.6, 1.8, -4.93), [1.6, 1.0, 1], "#a5d8ff", material="glow")]
smartdog = dog((-0.2, 0.55, -2.0), anim=[{"type": "bob", "amount": 0.03, "speed": 1}], col="#c08552")

# 0 — cold open: your dog at the table, talking back
B(3.4, "side", "One morning, every animal on Earth wakes up as smart as you.", V(kitchen + smartdog, ["#fff3bf", "#ffd8a8"], focus=(0, 0.9, -2.4), zoom=0.9,
  amb="room", bounce="#e9dcc9"), sfx=[{"type": "sparkle", "at": 0.3, "gain": 0.7}])
B(3.4, "side", "Your dog reads the news. Then asks why it only gets one walk a day.", V(kitchen + smartdog, ["#fff3bf", "#ffd8a8"], focus=(0, 1.0, -2.2), zoom=0.5,
  amb="room", bounce="#e9dcc9"))
# crows
wires = [O("box", (0, -0.02, -10), [60, 0.04, 60], "#868e96"), O("cylinder", (-8, 4, -8), [0.25, 8, 0.25], "#6b4f3a"), O("cylinder", (8, 4, -8), [0.25, 8, 0.25], "#6b4f3a"),
         O("box", (0, 7.6, -8), [16, 0.04, 0.04], "#212529"), O("cone", (0, 7.85, -8), [0.25, 0.5, 0.25], "#212529", rotate=[0, 0, 90], count=14, seed=3, spread=[14, 0, 0]),
         O("person", (0, 0, -6), 1.0, "#1c7ed6", action="walk", seed=4, color2="#e0ac69", animate=[{"type": "move", "to": [4, 0, -6]}])] + \
        house((-8, 0, -18), "#ced4da", "#5c3d2e") + house((6, 0, -20), "#ffe8cc", "#7a4a3a")
B(3.4, "low_front", "But crows already remember human faces for years. Now they hold grudges.", V(wires, SKY, focus=(0, 5, -8), zoom=2.0), transition="whip",
  sfx=[{"type": "swell", "at": 0.5, "dur": 2.0, "gain": 0.3}])
B(3.2, "wide", "If you ever chased one away... they remember.", V(wires + [birds((0, 9, -8), n=20, spread=(16, 3, 6), anim=[])], ["#3b4a63", "#9aa7b8"],
  focus=(0, 4, -7), zoom=2.4, amb="wind"), effects=["shake"])
# octopus
def octo(at=(0, 1.5, -5)):
    x, y, z = at
    return [O("sphere", at, [1.0, 1.3, 1.0], "#e8590c", material="glossy", animate=[{"type": "bob", "amount": 0.2, "speed": 0.7}])] + \
           [O("cone", (x + 0.9 * c, y - 1.2, z + 0.9 * s), [0.25, 1.8, 0.25], "#e8590c", rotate=[180 + 25 * s, 0, -25 * c],
              animate=[{"type": "wobble", "amount": 0.3, "speed": 1.4}]) for c, s in ((1, 0), (-1, 0), (0, 1), (0, -1), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7), (-0.7, -0.7))]
reef = [O("box", (0, -0.02, -6), [40, 0.04, 40], "#c2a878"), O("rock", (0, 0.5, -9), 1.2, "#6c757d", count=10, seed=4, spread=[20, 0, 8]),
        O("cylinder", (0, 0.8, -8), [0.3, 1.6, 0.3], "#f783ac", count=8, seed=6, spread=[16, 0, 6]),
        O("box", (3, 0.6, -6), [1.2, 1.2, 1.2], "#adb5bd", material="metal", animate=[{"type": "spin", "speed": 0.4}]),
        O("particles", (0, 3, -6), 0.4, "#e7f5ff", count=20, seed=3, spread=[16, 6, 10], animate=[{"type": "drift", "axis": "y", "amount": 0.4}])]
B(3.4, "front", "Octopuses have 500 million neurons. Now they're building machines.", V(reef + octo(), SEA, focus=(0, 1.4, -5), zoom=1.3, amb="ocean"), transition="whip",
  stat={"value": "500 MILLION", "label": "NEURONS IN AN OCTOPUS", "count_up": True})
# chimps
ape = lambda at, act="walk", seed=1: O("person", at, 0.85, "#5c3d2e", outfit="mannequin", action=act, seed=seed, color2="#5c3d2e")
city = [O("box", (0, -0.02, -10), [40, 0.04, 60], "#868e96"), O("building", (-10, 0, -18), 6, "#d6cfc4", count=8, seed=3, spread=[3, 0, 30]),
        O("building", (10, 0, -18), 6, "#c9b8a6", count=8, seed=7, spread=[3, 0, 30]), ape((-1, 0, -6), seed=2), ape((1.4, 0, -8), seed=5), ape((0, 0, -11), "point", seed=8)]
B(3.4, "dolly", "Chimps share about 99% of our DNA. They move into the city.", V(city, GOLD, focus=(0, 1.2, -8), zoom=1.4), chapter=None)
# dolphins
dolphin = lambda at, seed: O("capsule", at, [0.6, 2.2, 0.6], "#868e96", material="glossy", rotate=[0, 0, 90],
                             animate=[{"type": "bob", "amount": 0.6, "speed": 1.2 + seed * 0.1}, {"type": "drift", "axis": "x", "amount": 0.6}])
sea = [O("box", (0, -0.02, -14), [200, 0.04, 200], "#1c7ed6", material="glossy"), dolphin((-3, 0.3, -8), 1), dolphin((1, 0.3, -10), 2), dolphin((4, 0.3, -7), 3),
       O("box", (0, 0.8, -24), [6, 1.6, 2], "#f8f9fa")]
B(3.4, "side", "Dolphins already call each other by name. Now they want their ocean back.", V(sea, SKY, focus=(0, 0.2, -8.5), zoom=1.5, amb="ocean"), transition="zoom")
# cows on strike
farm = [O("box", (0, -0.02, -10), [60, 0.04, 60], "#69a84f")] + fence(-3) + cow((-3, 0, -6)) + cow((2, 0, -8)) + cow((5, 0, -5)) + \
       [O("box", (0, 1.6, -4.4), [2.2, 1.0, 0.06], "#f8f9fa", animate=[{"type": "bob", "amount": 0.1, "speed": 2}]),
        O("box", (0, 1.6, -4.36), [1.8, 0.2, 0.02], "#e03131"), O("cylinder", (0, 0.8, -4.4), [0.06, 1.6, 0.06], "#8d6e57")] + \
       [O("box", (-14, 1.5, -20), [6, 3, 5], "#9c3b2f"), trees((0, 0, -28), n=12, spread=(60, 0, 6))]
B(3.4, "wide", "Cows go on strike. No more milk. No more burgers.", V(farm, SKY, focus=(0, 1.2, -6), zoom=1.6), effects=["shake"],
  sfx=[{"type": "boom", "at": 0.6, "gain": 0.4}])
# ants
anthill = [O("box", (0, -0.02, -4), [30, 0.04, 30], "#8a6d3b"), O("cone", (0, 0.8, -5), [3, 1.6, 3], "#a68a5b"),
           O("sphere", (0, 0.05, -3), 0.05, "#212529", count=200, seed=5, spread=[10, 0, 8], animate=[{"type": "drift", "axis": "x", "amount": 0.3}])]
B(3.6, "follow", "Here's the scary part: there are 2.5 million ants for every one of us.", V(anthill, GOLD, focus=(0, 0.3, -3.5), zoom=0.45),
  transition="dip", stat={"value": "20 QUADRILLION", "label": "ANTS ON EARTH", "count_up": True}, sfx=[{"type": "steps", "at": 0.2, "dur": 3.0, "gain": 0.5}])
B(3.6, "aerial", "And if animals ever held a vote... humans would lose.", V(anthill + [O("person", (0, 0, 0), 1.0, "#1c7ed6", action="idle", seed=4, color2="#e0ac69")],
  ["#2b2d52", "#e07a5f"], focus=(0, 0.6, -2), zoom=1.6), effects=["glow"])

sb = {"format": "story", "title": "What if animals were as smart as humans?",
      "premise": "Every animal on Earth wakes up with human-level intelligence: dogs, crows, octopuses, chimps, dolphins, cows and ants.",
      "length": "quick", "intro": {"style": "none", "title": "What if *every animal* got as smart as you?"},
      "theme": {"style": "bold", "accent": "#40c057"},
      "outro": {"chart": False, "question_duration": 3.4, "end": {"kind": "question", "lines": ["WHICH ANIMAL", "WINS?"], "accent_line": 1}},
      "thumbnail": "ANIMALS GET *SMART*", "thumbnail_beat": 4, "beats": beats}
for i, ch in ((0, "Wake Up"), (4, "The Smart Ones"), (8, "The Vote")):
    beats[i]["chapter"] = ch
for b in beats:
    if b.get("chapter", "x") is None:
        del b["chapter"]
out = Path(__file__).parent / "animals.json"
out.write_text(json.dumps(sb, indent=1, ensure_ascii=False))
print(out, len(beats))
