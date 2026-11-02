"""What if men didn't exist? — retention test: cold open, quick (~40 s), cinematic + big word captions.
Facts (US, widely cited, rounded): ~half of the 8.2 billion people are male; ~9 in 10 airline pilots are men (women ~5-6%);
~97% of electricians are men; ~9 in 10 truck drivers are men; women hold ~28% of seats in Congress; men ~4 in 5 of violent-crime arrests (FBI);
frozen sperm in sperm banks would be the only way to have new babies."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from props import O, S, trees

beats = []
FADE = [{"type": "fade_out"}]


def B(dur, cam, caption, env, **k):
    b = {"duration": dur, "scene": "custom", "camera": cam, "subject": {"type": "none"}, "caption": caption, "env": env}
    b.update(k)
    beats.append(b)


def V(objs, bg, focus=(0, 1.4, -4), zoom=1.6, amb="calm", **k):
    return S(objs, bg, ground="none", focus=focus, zoom=zoom, ambient=k.pop("ambient", 1.4), amb=amb, light=k.pop("light", 2.4))


DAY = ["#4a8fd1", "#cfe3f3"]; GOLD = ["#2f4b7c", "#f2a65a"]; DUSK = ["#2b2d52", "#e07a5f"]; GREY = ["#6c7a89", "#c5cdd6"]
street = [O("box", (0, -0.02, -10), [40, 0.04, 60], "#868e96"), O("box", (0, 0, -10), [6, 0.03, 60], "#495057"),
          O("building", (-18, 0, -26), 6, "#d6cfc4", count=10, seed=3, spread=[2, 0, 30]), O("building", (18, 0, -26), 6, "#c9b8a6", count=10, seed=7, spread=[2, 0, 30]),
          O("box", (2, 0.65, -14), [2.0, 1.3, 4.4], "#e03131"), O("box", (-2, 0.65, -22), [2.0, 1.3, 4.4], "#1c7ed6")]
women = lambda n=14, seed=4: O("person", (0, 0, -8), 1.0, "#e64980", count=n, seed=seed, spread=[14, 0, 14], action="walk")
men = lambda n=14, seed=9, anim=FADE: O("person", (0, 0, -8), 1.0, "#1c7ed6", outfit="suit", count=n, seed=seed, spread=[14, 0, 14], action="walk", animate=list(anim))

# 0 — cold open: half the crowd vanishes on frame 0
B(3.6, "dolly", "Every man on Earth vanishes. All 4 billion of them. Right now.", V(street + [women(), men()], GOLD),
  chapter="Second One", sfx=[{"type": "shimmer", "at": 0.3, "dur": 2.0, "gain": 0.8}])
B(3.4, "wide", "Half of all people, gone. But the scariest part comes later.", V(street + [women(16, 6)], GOLD, zoom=2.2),
  stat={"value": "4 BILLION", "label": "MEN ON EARTH TODAY", "count_up": False})
# planes
air = [O("box", (0, -0.02, -20), [120, 0.04, 120], "#6c757d"), O("box", (0, 0.01, -20), [8, 0.02, 120], "#adb5bd"),
       O("capsule", (-6, 2.2, -20), [2.4, 22, 2.4], "#f8f9fa", material="glossy", rotate=[90, 0, 0]), O("box", (-6, 2.2, -20), [26, 0.3, 4], "#dee2e6"),
       O("capsule", (10, 2.2, -36), [2.4, 22, 2.4], "#f8f9fa", material="glossy", rotate=[90, 0, 0]), O("box", (10, 2.2, -36), [26, 0.3, 4], "#dee2e6"),
       O("person", (2, 0, -10), 1.0, "#f8f9fa", outfit="hivis", count=3, seed=5, spread=[8, 0, 4], action="walk")]
B(3.4, "wide", "Planes stop flying. About 9 out of 10 pilots are men.", V(air, DAY, focus=(2, 2, -26), zoom=2.4), transition="whip", chapter="Day One",
  sfx=[{"type": "drop", "at": 0.4, "gain": 0.5}])
# power
poles = [O("box", (0, -0.02, -20), [120, 0.04, 120], "#5c7a3e"), O("cylinder", (0, 5, -20), [0.3, 10, 0.3], "#6b4f3a", count=6, seed=2, spread=[60, 0, 4]),
         O("box", (0, 9.6, -20), [60, 0.06, 0.06], "#212529"), O("tree", (0, 0, -34), 1.6, "#3f6b3a", count=14, seed=5, spread=[80, 0, 10]),
         O("cylinder", (6, 5, -16), [0.3, 10, 0.3], "#6b4f3a", rotate=[0, 0, 35], animate=[{"type": "wobble", "amount": 0.2, "speed": 2}])]
B(3.4, "wide", "A storm knocks out power. 97% of electricians are men.", V(poles, ["#3d4a5a", "#8a96a3"], focus=(0, 4, -18), zoom=2.4, amb="wind"),
  effects=["lightning"])
# trucks / shelves
store = [O("box", (0, 0, -8), [16, 0.05, 20], "#e9ecef"), O("box", (0, 2.5, -18), [16, 5, 0.1], "#fff3bf"),
         O("box", (-4, 0.9, -9), [0.8, 1.8, 12], "#adb5bd", material="metal"), O("box", (0, 0.9, -9), [0.8, 1.8, 12], "#adb5bd", material="metal"),
         O("box", (4, 0.9, -9), [0.8, 1.8, 12], "#adb5bd", material="metal"), O("box", (0, 1.25, -9), [0.9, 0.25, 1.0], "#fab005", count=4, seed=3, spread=[9, 0, 10]),
         O("person", (0, 0, -10), 1.0, "#e64980", count=5, seed=8, spread=[6, 0, 6], action="walk")]
B(3.4, "dolly", "9 out of 10 truck drivers are men. Store shelves empty in days.", V(store, ["#fff3bf", "#ffe066"], focus=(0, 1.2, -6), zoom=1.2, amb="room"),
  transition="whip")
# congress
dome = [O("box", (0, -0.02, -30), [120, 0.04, 80], "#8ce99a"), O("box", (0, 6, -40), [40, 12, 14], "#f8f9fa"),
        O("sphere", (0, 14, -40), [8, 7, 8], "#f1f3f5"), O("cylinder", (0, 20, -40), [1, 4, 1], "#dee2e6"),
        O("cylinder", (-16, 4, -32.8), [1, 8, 1], "#f1f3f5", count=8, seed=1, spread=[30, 0, 0]),
        O("person", (0, 0, -24), 1.0, "#e64980", count=6, seed=12, spread=[20, 0, 6], action="walk")]
B(3.4, "wide", "In Congress, about 7 in 10 seats go empty overnight.", V(dome, DAY, focus=(0, 6, -36), zoom=3.6), transition="zoom",
  stat={"value": "72%", "label": "OF SEATS IN CONGRESS HELD BY MEN", "count_up": True})
# crime drops
park = [O("box", (0, -0.02, -10), [60, 0.04, 60], "#69a84f"), O("tree", (0, 0, -16), 1.6, "#3f8f3a", count=16, seed=3, spread=[50, 0, 20]),
        O("box", (0, 0.4, -6), [3, 0.15, 0.8], "#8d6e57", count=4, seed=4, spread=[16, 0, 6]), women(10, 2)]
B(3.4, "wide", "But violent crime would crash. 4 in 5 arrests for it are men.", V(park, GOLD, zoom=2), effects=["rays"])
# babies
lab = [O("box", (0, 0, -6), [14, 0.05, 14], "#dee2e6"), O("box", (0, 2.5, -12), [14, 5, 0.1], "#e7f5ff"),
       O("cylinder", (0, 0.8, -8), [0.9, 1.6, 0.9], "#adb5bd", material="metal", count=8, seed=2, spread=[10, 0, 3]),
       O("particles", (0, 1.8, -8), 0.3, "#e7f5ff", count=20, seed=4, spread=[10, 1, 3], animate=[{"type": "drift", "axis": "y", "amount": 0.2}]),
       O("person", (1, 0, -5), 1.0, "#f8f9fa", outfit="doctor", action="walk", seed=6, color2="#c68642")]
B(3.6, "dolly", "Here's the scary part: no new babies. Except from frozen sperm.", V(lab, ["#e7f5ff", "#a5d8ff"], focus=(0, 1.2, -7), zoom=1.2, amb="lab"),
  transition="dip", chapter="The Future", sfx=[{"type": "heartbeat", "at": 0.4, "dur": 2.8, "gain": 0.5}])
B(3.4, "wide", "Sperm banks become the most guarded places on Earth.", V(lab + [O("person", (-3.5, 0, -8.5), 1.0, "#343a40", outfit="police", action="idle", seed=9, color2="#8d5524")],
  ["#e7f5ff", "#a5d8ff"], focus=(-1, 1.2, -7.5), zoom=1.5, amb="lab"))
# 100 years
city2 = street[:3] + [O("tree", (0, 0, -12), 1.3, "#4f7a3a", count=10, seed=5, spread=[16, 0, 30])] + [women(6, 11)]
B(3.6, "far", "Without them, Earth's population could drop by billions within 100 years.", V(city2, DUSK, zoom=2.6), transition="dip",
  chip="+100 YEARS")
B(3.6, "wide", "So would the world be better... or would it fall apart?", V(street + [women(12, 3), men(6, 13, anim=[{"type": "fade_in"}])], DUSK, zoom=2),
  effects=["glow"])

sb = {"format": "story", "title": "What if men didn't exist?",
      "premise": "Every man on Earth vanishes in one second. Planes, power, food, government and the future of humans change overnight.",
      "length": "quick", "intro": {"style": "none", "title": "What if *every man* vanished?"},
      "theme": {"style": "cinematic", "accent": "#ffa94d", "captions": "words", "palette": "warm"},
      "clock": {"mode": "none"},
      "outro": {"chart": False, "question_duration": 3.6, "end": {"kind": "question", "lines": ["BETTER", "OR WORSE?"], "accent_line": 1}},
      "thumbnail": "EVERY *MAN* VANISHED", "thumbnail_beat": 0, "beats": beats}
out = Path(__file__).parent / "men.json"
out.write_text(json.dumps(sb, indent=1, ensure_ascii=False))
print(out, len(beats))
