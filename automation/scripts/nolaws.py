"""What if no laws existed? — retention format: cold open, quick, witness style (one fixed street-corner view) + big word captions.
Facts: Montreal police strike, 7 Oct 1969 (~16 hours): bank robberies and looting, army called in; before the 1906 Pure Food and Drug Act
some US milk was preserved with formaldehyde ("embalmed milk"); disaster research: most people cooperate and help each other."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from props import O, S, trees

beats = []


def B(dur, caption, env, t, sub="", **k):
    b = {"duration": dur, "scene": "custom", "camera": "witness", "subject": {"type": "none"}, "caption": caption, "env": env,
         "time": t, "time_sub": sub, "move": "none"}
    b.update(k)
    beats.append(b)


def light(x, z, col):
    return [O("cylinder", (x, 2.5, z), [0.12, 5, 0.12], "#343a40", material="metal"), O("box", (x, 5.2, z), [0.5, 1.2, 0.4], "#212529"),
            O("sphere", (x, 5.5 if col == "#ff4d4d" else 4.9, z + 0.22), 0.16, col, material="glow" if col != "#495057" else "matte")]


def corner(lights="#40c057", cars=(), people=(), store=(), extra=(), lit=True, mess=0.0, clean=False):
    p = [O("box", (0, -0.02, -24), [120, 0.04, 80], "#868e96"),
         O("box", (0, 0, -24), [120, 0.03, 9], "#495057"), O("box", (0, 0.001, -24), [9, 0.032, 80], "#495057"),
         O("box", (0, 0.04, -19.2), [9, 0.01, 0.6], "#f8f9fa", count=1),
         O("building", (-16, 0, -40), 5, "#d6cfc4", count=6, seed=3, spread=[14, 0, 12]), O("building", (16, 0, -40), 5, "#c9b8a6", count=6, seed=7, spread=[14, 0, 12]),
         O("box", (-14, 3, -14), [12, 6, 8], "#e9dcc9"), O("box", (-14, 1.4, -9.95), [8, 2.2, 0.06], "#a5d8ff" if not mess else "#495057", material="glass"),
         O("box", (-14, 4.2, -9.9), [6, 0.8, 0.06], "#e03131"),
         O("box", (14, 3, -14), [12, 6, 8], "#dbe4ff"), O("tree", (0, 0, -6), 1.2, "#4f7a3a", count=4, seed=4, spread=[40, 0, 2])]
    p += light(-5, -19.5, lights) + light(5, -28.5, lights)
    if lit:
        p.append(O("box", (0, 8, -35.8), [1.0, 0.8, 0.05], "#ffe8a3", material="glow", count=10, seed=5, spread=[40, 10, 0]))
    if mess:
        p.append(O("box", (0, 0.2, -16), [0.8, 0.4, 0.6], "#8d6e57", count=int(16 * mess), seed=9, spread=[30, 0, 20]))
    if clean:
        p.append(O("box", (0, 0.2, -16), [0.8, 0.4, 0.6], "#8d6e57", count=4, seed=9, spread=[30, 0, 20], animate=[{"type": "shrink"}]))
    return p + list(cars) + list(people) + list(store) + list(extra)


def car(x, z, to, col, ry=0):
    return O("box", (x, 0.65, z), [2.0, 1.3, 4.2], col, rotate=[0, ry, 0], animate=[{"type": "move", "to": list(to)}])


crowd = lambda n=14, seed=3, act="walk", col=None, at=(0, 0, -12), spread=(30, 0, 10), anim=(): O("person", at, 1.0, col or "#d8d8d8", count=n, seed=seed,
                                                                                                    spread=list(spread), action=act, animate=list(anim))
DAY = ["#4a8fd1", "#cfe3f3"]; HAZE = ["#7b8794", "#d9c49a"]; SMOKE = ["#3d3533", "#b5651d"]; DUSK = ["#2b2d52", "#e07a5f"]; DAWN = ["#5d86ad", "#ffd8a8"]


def V(objs, bg=DAY, weather="clear", amb="calm"):
    e = S(objs, bg, ground="none", focus=(0, 0.6, 6), zoom=0.35, ambient=1.4, amb=amb, light=2.2)
    e["weather"] = weather
    return e


police = [O("box", (3, 0.7, -24), [2.0, 1.4, 4.4], "#1c3d6e", rotate=[0, 90, 0], animate=[{"type": "move", "to": [60, 0.7, -24]}]),
          O("box", (3, 1.5, -24), [0.4, 0.2, 0.8], "#e03131", material="glow", rotate=[0, 90, 0], animate=[{"type": "move", "to": [60, 1.5, -24]}])]
# 0 — cold open: the last police car drives away
B(3.6, "At noon today, every law on Earth disappears.", V(corner(cars=police + [car(-2, -10, (-2, 0.65, -60), "#e03131")], people=[crowd(12, 3)])),
  "12:00 PM", "DAY 1", time_label="NO LAWS", sfx=[{"type": "siren", "at": 0.2, "dur": 2.6, "gain": 0.4}])
B(3.4, "No police. No courts. No rules. So what happens first?", V(corner(people=[crowd(16, 5, "idle")])), "12:01 PM", "DAY 1")
crash = [car(-40, -22, (-1, 0.65, -22), "#fab005", ry=90), car(2, 10, (1.5, 0.65, -20), "#1c7ed6"),
         O("particles", (0, 1, -21), 0.4, "#ced4da", count=12, seed=4, spread=[4, 2, 4], animate=[{"type": "drift", "axis": "y", "amount": 0.3}])]
B(3.4, "Red lights mean nothing now. Drivers just floor it.", V(corner(lights="#ff4d4d", cars=crash, people=[crowd(8, 7, "point", at=(0, 0, -6), spread=(30, 0, 4))])),
  "12:05 PM", "DAY 1", effects=["shake"], sfx=[{"type": "impact", "at": 2.2, "gain": 1.0}, {"type": "crack", "at": 2.3, "gain": 0.6}])
B(3.4, "There's no driving age anymore. A 12-year-old takes Dad's car.", V(corner(lights="#495057", cars=[car(-2, 6, (-2, 0.65, -70), "#40c057"),
  O("person", (-2.3, 1.0, 5.6), 0.55, "#fab005", outfit="child", action="sit", seed=6, color2="#e0ac69", animate=[{"type": "move", "to": [-2.3, 1.0, -70.4]}])])),
  "12:40 PM", "DAY 1", sfx=[{"type": "whoosh", "at": 0.6, "gain": 0.7}])
loot = [O("person", (-14, 0, -9), 1.0, count=8, seed=11, spread=[8, 0, 2], action="run", animate=[{"type": "move", "to": [-4, 0, -4]}]),
        O("box", (-14, 1.0, -9), [0.6, 0.5, 0.5], "#c97a40", count=6, seed=12, spread=[8, 0, 2], animate=[{"type": "move", "to": [-4, 1.0, -4]}])]
B(3.4, "Some stores get emptied in minutes.", V(corner(lights="#495057", store=loot, mess=0.4), HAZE), "2:00 PM", "DAY 1", effects=["shake"],
  sfx=[{"type": "debris", "at": 0.4, "gain": 0.7}])
B(3.6, "It's happened before. In 1969, Montreal's police went on strike for 16 hours.", V(corner(lights="#495057", mess=0.6, people=[crowd(10, 13, "run")]), HAZE),
  "4:00 PM", "DAY 1", stat={"value": "16 HOURS", "label": "MONTREAL POLICE STRIKE, 1969", "count_up": False})
fires = [O("flame", (14, 6, -14), 3, "#ff6b00"), O("particles", (14, 14, -14), 3, "#3d3533", count=20, seed=6, spread=[8, 16, 8], animate=[{"type": "drift", "axis": "y", "amount": 2}])]
B(3.4, "Banks got robbed. Stores got looted. The army had to come in.", V(corner(lights="#495057", mess=0.8, extra=fires, lit=False,
  people=[O("person", (0, 0, -30), 1.0, "#5c7a3e", outfit="soldier", count=8, seed=14, spread=[10, 0, 2], action="walk", animate=[{"type": "move", "to": [0, 0, -18]}])]),
  SMOKE, "ash"), "11:00 PM", "DAY 1", effects=["smoke"])
milk = [O("box", (-14, 1.4, -9.9), [1.2, 0.4, 0.4], "#f8f9fa", count=4, seed=3, spread=[6, 1, 0])]
B(3.6, "Day 3: no food safety laws. Before 1906, some US milk had formaldehyde in it.", V(corner(lights="#495057", mess=0.8, lit=False, store=milk,
  people=[crowd(6, 15, "idle", at=(-12, 0, -7), spread=(8, 0, 2))]), HAZE), "DAY 3", "", stat={"value": "1906", "label": "FIRST US FOOD SAFETY LAW", "count_up": False})
B(3.4, "Your house is only yours if you can keep it.", V(corner(lights="#495057", mess=1.0, lit=False, extra=[O("box", (14, 1.0, -9.9), [3, 2.0, 0.3], "#8d6e57")],
  people=[crowd(4, 16, "idle", at=(14, 0, -8), spread=(6, 0, 1))]), DUSK), "DAY 5", "", effects=["darken"])
help_ = [crowd(14, 17, "walk", col="#fab005", at=(0, 0, -16), spread=(30, 0, 14))]
B(3.6, "But here's the twist: in real disasters, most people help each other.", V(corner(lights="#495057", lit=False, clean=True, people=help_), DAWN),
  "DAY 7", "", transition="dip", effects=["rays"])
B(3.6, "Neighbors make their own rules. That's how laws started in the first place.", V(corner(lights="#40c057", people=help_ + [crowd(8, 18, "idle", at=(0, 0, -6), spread=(20, 0, 3))]),
  DAY), "DAY 30", "", hud=False)

sb = {"format": "timeline", "title": "What if no laws existed?",
      "premise": "Every law on Earth disappears at noon. One street corner, watched from the first minute to day 30. Based on what really happened in 1969 Montreal.",
      "length": "quick", "intro": {"style": "none", "title": "What if *every law* disappeared?"},
      "theme": {"style": "witness", "accent": "#ffa94d", "captions": "words", "anchor": "none"},
      "clock": {"mode": "elapsed", "label": "NO LAWS"},
      "outro": {"chart": False, "question_duration": 3.4, "end": {"kind": "question", "lines": ["WHAT WOULD", "YOU DO FIRST?"], "accent_line": 1}},
      "thumbnail": "NO *LAWS*. 30 DAYS.", "thumbnail_beat": 6, "beats": beats}
out = Path(__file__).parent / "nolaws.json"
out.write_text(json.dumps(sb, indent=1, ensure_ascii=False))
print(out, len(beats))
