"""LONG-FORM (YouTube 16:9, narrated): What if men and women swapped bodies for a day?
Follows Alex and Maya hour by hour. A halo shows whose MIND is in a body: blue = Alex, pink = Maya.
Facts (rounded / hedged, widely cited):
- ~8.2 billion people, roughly half men and half women (~4 billion each)
- US average height: men ~5'9", women ~5'4" (CDC) -> about 5 inches
- typical speaking pitch: men ~85-155 Hz, women ~165-255 Hz -> roughly an octave
- by 50, most men have noticeable hair loss (~85%, American Hair Loss Association)
- men average ~40% more upper-body muscle (Janssen et al., 2000)
- many office thermostats follow a 1960s comfort formula based on an average 40-year-old man (Kingma & van Marken Lichtenbelt, Nature Climate Change, 2015)
- adult calorie needs (USDA): men ~2,200-3,000, women ~1,600-2,400 -> several hundred more
- red-green colorblindness: ~1 in 12 men, ~1 in 200 women
- on any given day, 300+ million people are menstruating (World Bank)
- surveys (e.g. Gallup) find women feel much less safe walking alone at night than men
- ~40% of men vs ~24% of women snore habitually (Sleep Foundation)"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from props import O, S, trees, house

BLUE, PINK = "#1c7ed6", "#e64980"          # bodies: Alex's body is blue, Maya's body is pink
HALO_A, HALO_M = "#4dabf7", "#f783ac"      # minds
SEED_A, SEED_M = 2, 3
SKIN_A, SKIN_M = "#c68642", "#e0ac69"
beats = []


def B(cam, narr, env, chip=None, cap=None, **k):
    """narr = what the narrator says (also the subtitle unless cap is given)."""
    b = {"duration": 4.0, "scene": "custom", "camera": cam, "subject": {"type": "none"}, "caption": cap or narr, "env": env}
    if cap:
        b["narration"] = narr
    if chip:
        b["chip"] = chip
    b.update(k)
    beats.append(b)


def halo(at, col, h=2.02, anim=()):
    x, y, z = at
    return O("torus", (x, y + h, z), [0.22, 0.22, 0.05], col, material="glow", rotate=[90, 0, 0],
             animate=list(anim) + [{"type": "bob", "amount": 0.04, "speed": 1.5}])


def body(who_body, at, act="idle", ry=0, anim=()):
    col, seed, skin = (BLUE, SEED_A, SKIN_A) if who_body == "A" else (PINK, SEED_M, SKIN_M)
    return O("person", at, 1.0, col, outfit="casual", action=act, seed=seed, color2=skin, rotate=[0, ry, 0], animate=list(anim))


def mind(mind_of, at, act="idle", ry=0, swapped=True, anim=(), h=None):
    """mind_of 'A' (Alex) or 'M' (Maya). swapped=True puts that mind in the OTHER body."""
    b = ("M" if mind_of == "A" else "A") if swapped else mind_of
    hh = h if h is not None else (1.45 if act in ("sit", "kneel") else 0.95 if act == "lie" else 2.02)
    mv = [a for a in anim if a.get("type") == "move"]
    halo_anim = [{"type": "move", "to": [a["to"][0], a["to"][1], a["to"][2]]} for a in mv]
    return [body(b, at, act, ry, anim), halo(at, HALO_A if mind_of == "A" else HALO_M, hh, halo_anim)]


def crowd(n, seed, at=(0, 0, -10), spread=(20, 0, 12), act="walk", col=None):
    return O("person", at, 1.0, col or "#d8d8d8", count=n, seed=seed, spread=list(spread), action=act)


def mixed(n, seed, at=(0, 0, -12), spread=(30, 0, 14), act="walk", halos=False):
    """a crowd of swapped people: blue bodies with pink halos and pink bodies with blue halos (as scatter groups)."""
    out = [O("person", at, 1.0, BLUE, count=n, seed=seed, spread=list(spread), action=act),
           O("person", at, 1.0, PINK, count=n, seed=seed + 50, spread=list(spread), action=act)]
    if halos:
        out += [O("torus", (at[0], 2.02, at[2]), [0.22, 0.22, 0.05], HALO_M, material="glow", rotate=[90, 0, 0], count=n, seed=seed, spread=list(spread)),
                O("torus", (at[0], 2.02, at[2]), [0.22, 0.22, 0.05], HALO_A, material="glow", rotate=[90, 0, 0], count=n, seed=seed + 50, spread=list(spread))]
    return out


def V(objs, bg, focus=(0, 1.2, -5), zoom=1.2, amb="calm", bounce=None, **k):
    e = S(objs, bg, ground="none", focus=focus, zoom=zoom, ambient=k.pop("ambient", 1.5), amb=amb, light=k.pop("light", 2.3))
    if bounce:
        e["set"]["bounce"] = bounce
    return e


def room(wall, floor, win=None, w=14, d=12, extra=()):
    p = [O("box", (0, 0, -d / 2), [w, 0.05, d], floor), O("box", (0, 1.6, -d), [w, 3.2, 0.1], wall),
         O("box", (-w / 2, 1.6, -d / 2), [0.1, 3.2, d], wall), O("box", (w / 2, 1.6, -d / 2), [0.1, 3.2, d], wall)]
    if win:
        p += [O("plane", (w / 4, 1.8, -d + 0.07), [2.6, 1.5, 1], win, material="glow"), O("box", (w / 4, 1.8, -d + 0.08), [2.7, 0.06, 0.04], "#f8f9fa")]
    return p + list(extra)


# ---------------------------------------------------------------- locations
NIGHT_IN = ["#1b2440", "#3b4a6b"]; DAWN = ["#5d86ad", "#ffd8a8"]; MORNING = ["#74a9d8", "#fde2c4"]; DAY = ["#4a8fd1", "#cfe3f3"]
GOLD = ["#2f4b7c", "#f4a259"]; DUSK = ["#2b2d52", "#e07a5f"]; NIGHT = ["#141c2e", "#3b3a6b"]; WARM = ["#3b2a6b", "#c08a5a"]


def bedroom(win="#ffd8a8", lamp=False, extra=()):
    p = room("#e9dcc9", "#b08968", win, extra=[O("box", (0, 0.3, -7.5), [3.2, 0.55, 3.8], "#f1f3f5"), O("box", (0, 0.65, -9.2), [3.2, 0.5, 0.5], "#a5d8ff"),
                                                O("box", (0, 0.9, -9.6), [3.4, 1.4, 0.15], "#8d6e57"),
                                                O("box", (-2.4, 0.35, -9.2), [0.8, 0.7, 0.6], "#8d6e57"), O("box", (2.4, 0.35, -9.2), [0.8, 0.7, 0.6], "#8d6e57"),
                                                O("box", (5.5, 1.2, -6), [0.1, 2.0, 1.0], "#dee2e6", material="metal")])
    if lamp:
        p += [O("cylinder", (-2.4, 0.95, -9.2), [0.15, 0.4, 0.15], "#ffd43b", material="glow")]
    return p + list(extra)


def bathroom(extra=()):
    return room("#e7f5ff", "#dee2e6", None, w=10, d=8, extra=[O("box", (0, 1.7, -7.9), [3.4, 1.4, 0.05], "#dee2e6", material="metal"),
                                                              O("box", (0, 0.45, -7.4), [3.6, 0.9, 0.9], "#f8f9fa"), O("cylinder", (-0.8, 0.95, -7.4), [0.4, 0.1, 0.3], "#ced4da"),
                                                              O("cylinder", (0.8, 0.95, -7.4), [0.4, 0.1, 0.3], "#ced4da")] + list(extra))


def kitchen(extra=()):
    return room("#fff3bf", "#c9a27a", "#a5d8ff", extra=[O("box", (0, 0.45, -11), [12, 0.9, 1.1], "#5c677d"), O("box", (0, 0.92, -11), [12, 0.05, 1.15], "#f1f3f5"),
                                                         O("box", (-3, 2.3, -11.6), [4, 0.06, 0.6], "#8d6e57"), O("cylinder", (-3.6, 2.42, -11.6), [0.12, 0.18, 0.12], "#f783ac", count=4, seed=3, spread=[3, 0, 0.1]),
                                                         O("box", (0, 0.75, -7), [2.2, 0.06, 1.2], "#8d6e57"), O("cylinder", (0, 0.37, -7), [0.12, 0.74, 0.12], "#6b4f3a")] + list(extra))


def closet(extra=()):
    return room("#f3d9fa", "#c9a27a", None, w=10, d=8, extra=[O("box", (0, 2.2, -7.5), [8, 0.05, 0.05], "#868e96", material="metal"),
                                                              O("box", (0, 1.5, -7.4), [0.5, 1.2, 0.08], "#e64980", count=8, seed=2, spread=[7, 0, 0.1]),
                                                              O("box", (0, 1.5, -7.3), [0.5, 1.2, 0.08], "#1c7ed6", count=8, seed=5, spread=[7, 0, 0.1]),
                                                              O("box", (3.6, 0.15, -5), [0.4, 0.15, 0.25], "#343a40", count=6, seed=4, spread=[1.4, 0, 2])] + list(extra))


def street(extra=(), lit=False):
    p = [O("box", (0, -0.06, -20), [600, 0.04, 600], "#7d8a6a"), O("box", (0, -0.02, -20), [120, 0.04, 100], "#868e96"), O("box", (0, 0, -16), [120, 0.03, 8], "#495057"), O("box", (0, 0.04, -16), [120, 0.01, 0.15], "#ffd43b"),
         O("building", (0, 0, -34), 3, "#e8d5b7", count=10, seed=3, spread=[80, 0, 8]), O("building", (0, 0, -30), 2.4, "#a5b4c4", count=8, seed=13, spread=[80, 0, 6]), O("tree", (0, 0, -9), 1.3, "#4f7a3a", count=8, seed=4, spread=[60, 0, 2]),
         O("box", (-8, 0.65, -15), [4.4, 1.3, 2.0], "#e03131", animate=[{"type": "move", "to": [30, 0.65, -15]}]),
         O("box", (12, 0.65, -17.5), [4.4, 1.3, 2.0], "#fab005", animate=[{"type": "move", "to": [-30, 0.65, -17.5]}])]
    if lit:
        p += [O("cylinder", (0, 2.5, -11.5), [0.1, 5, 0.1], "#495057", count=5, seed=2, spread=[40, 0, 0]),
              O("sphere", (0, 5.1, -11.5), 0.25, "#ffe066", material="glow", count=5, seed=2, spread=[40, 0, 0]),
              O("box", (0, 8, -26.9), [1.0, 0.8, 0.05], "#ffe8a3", material="glow", count=16, seed=5, spread=[70, 10, 0])]
    return p + list(extra)


def office(thermo=True, extra=()):
    p = room("#e9ecef", "#adb5bd", "#a5d8ff", w=18, d=14, extra=[O("box", (0, 0.74, -8), [1.6, 0.05, 0.9], "#f8f9fa", count=10, seed=2, spread=[14, 0, 8]),
                                                                 O("box", (0, 1.0, -8), [0.6, 0.4, 0.05], "#212529", count=10, seed=2, spread=[14, 0, 8])])
    if thermo:
        p += [O("box", (-6, 1.6, -13.9), [0.5, 0.7, 0.06], "#f8f9fa"), O("plane", (-6, 1.65, -13.85), [0.36, 0.25, 1], "#4dabf7", material="glow")]
    return p + list(extra)


def cafe(extra=()):
    return room("#ffe8cc", "#8d6e57", "#ffd8a8", w=16, d=12, extra=[O("box", (0, 0.75, -7), [1.2, 0.06, 1.2], "#f8f9fa", count=6, seed=3, spread=[12, 0, 6]),
                                                                    O("box", (-6, 0.6, -11), [4, 1.2, 1], "#6b4f3a")] + list(extra))


def restaurant(extra=()):
    return room("#3b2a6b", "#5c3d2e", "#1b2440", w=16, d=12, extra=[O("box", (0, 0.75, -7), [1.2, 0.06, 0.8], "#f8f9fa"), O("cylinder", (0, 0.37, -7), [0.1, 0.74, 0.1], "#495057"),
                                                                    O("flame", (0, 0.9, -7), 0.08, "#ffa94d"), O("box", (0, 0.75, -7), [1.2, 0.06, 0.8], "#f8f9fa", count=5, seed=8, spread=[12, 0, 5]),
                                                                    O("sphere", (0, 2.9, -7), 0.12, "#ffe066", material="glow", count=12, seed=4, spread=[14, 0.2, 10]),
                                                                    O("person", (0, 0, -9), 1.0, count=8, seed=11, spread=[12, 0, 4], action="sit")] + list(extra))


def plaza(extra=(), bg_build="#d6cfc4"):
    return [O("box", (0, -0.06, -20), [600, 0.04, 600], "#7d8a6a"), O("box", (0, -0.02, -20), [160, 0.04, 120], "#ced4da"), O("building", (0, 0, -52), 4, bg_build, count=16, seed=9, spread=[140, 0, 16]), O("building", (0, 0, -46), 3, "#b5c7d6", count=12, seed=19, spread=[140, 0, 10]),
            O("tree", (0, 0, -36), 1.6, "#4f7a3a", count=14, seed=6, spread=[120, 0, 6]),
            O("cylinder", (0, 0.4, -18), [3, 0.8, 3], "#adb5bd"), O("particles", (0, 2, -18), 0.3, "#a5d8ff", count=10, seed=3, spread=[2, 3, 2],
                                                                    animate=[{"type": "drift", "axis": "y", "amount": 0.5}])] + list(extra)


# ======================================================================= HOOK
B("follow", "Tomorrow at 6 AM, every man and every woman on Earth will wake up in each other's body.",
  V(bedroom("#1b2440", lamp=True, extra=[body("A", (-0.6, 0.62, -7.3), "lie", 0), body("M", (0.6, 0.62, -7.3), "lie", 0),
                                          halo((-0.6, 0.62, -7.3), HALO_A, 0.6), halo((0.6, 0.62, -7.3), HALO_M, 0.6)]), NIGHT_IN, focus=(0, 0.8, -7.5), zoom=1.0, bounce="#3b4a6b"),
  "5:59 AM", chapter="The Swap", move="none", sfx=[{"type": "tick", "at": 0.5, "gain": 0.5}, {"type": "tick", "at": 1.5, "gain": 0.5}, {"type": "tick", "at": 2.5, "gain": 0.5}])
B("wide", "Four billion men. Four billion women. Twenty-four hours. No warning.",
  V(plaza(mixed(30, 4, at=(0, 0, -16), spread=(60, 0, 20))), DAWN, focus=(0, 1.5, -16), zoom=3.2), "6:00 AM",
  effects=["flash"], stat={"value": "8 BILLION", "label": "PEOPLE WAKE UP IN THE WRONG BODY", "count_up": True}, sfx=[{"type": "shimmer", "at": 0.1, "gain": 0.9}])
B("dolly", "By 9 AM, millions of men will be freezing at their desks. And there's a real reason why.",
  V(office(extra=mixed(6, 21, at=(0, 0, -8), spread=(14, 0, 8), act="sit")), ["#e9ecef", "#a5d8ff"], focus=(0, 1.2, -7), zoom=1.4, bounce="#e9ecef"),
  "COMING UP", transition="whip")
B("wide", "By 2 PM, around 300 million men will be dealing with something they've never felt before.",
  V(street(mixed(10, 31, at=(0, 0, -10), spread=(40, 0, 6))), GOLD, focus=(0, 1.3, -12), zoom=2.4), "COMING UP", transition="whip")
B("far", "And at the very end, both sides will admit something nobody expects. Stay for that one.",
  V(street(lit=True, extra=mind("M", (-0.6, 0, -9), "walk", 180) + mind("A", (0.6, 0, -9), "walk", 180)), NIGHT, focus=(0, 1.3, -9), zoom=2.0), "COMING UP",
  transition="dip", effects=["glow"])
B("orbit", "Meet Alex and Maya. The blue light shows where Alex's mind is. The pink light shows Maya's. Let's follow them, hour by hour.",
  V(bedroom(DAWN[1], extra=mind("A", (-0.6, 0, -5), "idle", 180, swapped=False) + mind("M", (0.6, 0, -5), "idle", 180, swapped=False)), DAWN, focus=(0, 1.2, -5),
    zoom=0.8, bounce="#e9dcc9"), "THE NIGHT BEFORE", cap="Meet Alex (blue light) and Maya (pink light).")

# ======================================================================= 6 AM — THE MIRROR
B("follow", "6 AM. Alex wakes up first. Something feels... off.",
  V(bedroom("#ffd8a8", extra=[body("M", (-0.6, 0.62, -7.3), "lie"), halo((-0.6, 0.62, -7.3), HALO_A, 0.6), body("A", (0.6, 0.62, -7.3), "lie"),
                              halo((0.6, 0.62, -7.3), HALO_M, 0.6)]), DAWN, focus=(0, 0.8, -7.5), zoom=0.9, bounce="#e9dcc9"), "6:00 AM", chapter="6 AM: The Mirror",
  transition="dip")
B("side", "He sits up, and long hair falls right into his face.",
  V(bedroom("#ffd8a8", extra=mind("A", (-0.6, 0.45, -7.3), "sit", 270, anim=[{"type": "wobble", "amount": 0.1, "speed": 2}])), DAWN, focus=(-0.6, 1.2, -7.3), zoom=0.5,
    bounce="#e9dcc9"), "6:01 AM")
B("side", "Next to him, Maya wakes up in his body. With a full day's worth of stubble.",
  V(bedroom("#ffd8a8", extra=mind("M", (0.6, 0.45, -7.3), "sit", 90)), DAWN, focus=(0.6, 1.2, -7.3), zoom=0.5, bounce="#e9dcc9"), "6:01 AM")
B("follow", "They both run to the mirror. And they both scream. At the exact same time.",
  V(bathroom(mind("A", (-0.6, 0, -6.4), "idle", 0) + mind("M", (0.6, 0, -6.4), "idle", 0)), ["#e7f5ff", "#d0ebff"], focus=(0, 1.5, -6.6), zoom=0.8, bounce="#e7f5ff"),
  "6:02 AM", effects=["shake"], sfx=[{"type": "swell", "at": 0.6, "dur": 1.6, "gain": 0.7}])
B("side", "Alex's scream comes out way higher than he expected. Men's voices are usually about an octave lower than women's.",
  V(bathroom(mind("A", (-0.6, 0, -6.4), "point", 90) + mind("M", (0.6, 0, -6.4), "idle", 270)), ["#e7f5ff", "#d0ebff"], focus=(0, 1.5, -6.4), zoom=0.6, bounce="#e7f5ff"),
  "6:02 AM", cap="His scream comes out way higher than he expected.", tooltip={"label": "FACT", "text": "Men's voices are usually about an octave lower than women's."})
B("wide", "In the kitchen, Maya grabs a mug from the top shelf. Easily. For the first time in her life.",
  V(kitchen(mind("M", (-3, 0, -10.6), "point", 0) + mind("A", (1.5, 0, -8), "idle", 270)), MORNING, focus=(-1, 1.4, -9), zoom=1.2, bounce="#fff3bf"), "6:15 AM",
  stat={"value": "~5 INCHES", "label": "AVERAGE US HEIGHT GAP: 5'9\" VS 5'4\"", "count_up": False})
B("follow", "Alex, now about five inches shorter, has to climb on a chair to reach the same shelf.",
  V(kitchen([O("box", (-3, 0.45, -10.4), [0.6, 0.9, 0.6], "#8d6e57")] + mind("A", (-3, 0.9, -10.4), "point", 0) + mind("M", (1.5, 0, -8), "idle", 270)), MORNING,
    focus=(-2, 1.6, -10), zoom=0.9, bounce="#fff3bf"), "6:16 AM")
B("establishing", "Quick question before we go on: who do you think adapts faster, the men or the women? Put your answer in the comments now. We'll see if you're right.",
  V(plaza(mixed(24, 41, at=(0, 0, -16), spread=(60, 0, 20), act="idle")), MORNING, focus=(0, 1.5, -18), zoom=3.6), "6:30 AM",
  cap="Who adapts faster: men or women? Comment now.", effects=["rays"])

# ======================================================================= 7 AM — GETTING READY
B("dolly", "7 AM. Getting dressed. And nothing in the closet fits right.",
  V(closet(mind("A", (-1.2, 0, -5.5), "idle", 0) + mind("M", (1.2, 0, -5.5), "idle", 0)), ["#f3d9fa", "#e5dbff"], focus=(0, 1.3, -6), zoom=0.9, bounce="#f3d9fa"),
  "7:00 AM", chapter="7 AM: Getting Ready", transition="whip")
B("side", "Maya's shirts are suddenly too tight across the shoulders. Alex's jeans keep sliding down.",
  V(closet(mind("M", (1.2, 0, -5.5), "walk", 270, anim=[{"type": "wobble", "amount": 0.15, "speed": 3}]) + mind("A", (-1.2, 0, -5.5), "idle", 90)),
    ["#f3d9fa", "#e5dbff"], focus=(0, 1.2, -5.5), zoom=0.7, bounce="#f3d9fa"), "7:05 AM")
B("follow", "Alex has never put on a bra in his life. It takes him four tries. And a tutorial.",
  V(closet(mind("A", (-0.6, 0, -6), "idle", 0, anim=[{"type": "wobble", "amount": 0.25, "speed": 3}])), ["#f3d9fa", "#e5dbff"], focus=(-0.6, 1.3, -6), zoom=0.6,
    bounce="#f3d9fa"), "7:10 AM", sfx=[{"type": "pop", "at": 1.0, "gain": 0.4}, {"type": "pop", "at": 2.2, "gain": 0.4}])
B("side", "Maya, meanwhile, learns that this face needs shaving. Every. Single. Morning.",
  V(bathroom(mind("M", (0, 0, -6.6), "point", 0)), ["#e7f5ff", "#d0ebff"], focus=(0, 1.5, -6.8), zoom=0.55, bounce="#e7f5ff"), "7:15 AM")
B("wide", "And across the world, a lot of women wake up with way less hair. By age 50, most men have noticeable hair loss.",
  V(street(mixed(10, 51, at=(0, 0, -10), spread=(40, 0, 6))), MORNING, focus=(0, 1.3, -12), zoom=2.2), "7:30 AM",
  cap="A lot of women wake up with way less hair.", tooltip={"label": "FACT", "text": "By age 50, most men have noticeable hair loss."})
B("follow", "And the men find out exactly how long a quick morning routine really takes. Ladies, how long does yours take? Tell the guys in the comments.",
  V(bathroom(mind("A", (-0.6, 0, -6.6), "idle", 0) + [O("cylinder", (0.6, 1.0, -7.4), [0.06, 0.18, 0.06], c, count=1) for c in ("#f783ac", "#ffd43b", "#74c0fc")]),
    ["#e7f5ff", "#d0ebff"], focus=(0, 1.4, -6.8), zoom=0.8, bounce="#e7f5ff"), "7:55 AM", cap="Ladies: how long does your routine take? Tell the guys below.")

# ======================================================================= 8 AM — THE COMMUTE
car_in = [O("box", (0, 0.6, -6), [2.2, 1.2, 4.6], "#adb5bd", material="metal"), O("box", (0, 1.4, -6.4), [2.0, 0.6, 2.4], "#a5d8ff", material="glass", opacity=0.5)]
B("side", "8 AM. In the car, every single person has to move the seat and fix every mirror.",
  V(street(car_in + mind("M", (0.4, 0.6, -6), "sit", 0)), MORNING, focus=(0, 1.2, -6), zoom=1.2), "8:00 AM", chapter="8 AM: The Commute", transition="whip",
  sfx=[{"type": "whoosh", "at": 0.8, "gain": 0.4}])
B("dolly", "On the sidewalk, the men are shorter now. Suddenly, a crowd feels like a wall of shoulders.",
  V(street(mixed(14, 61, at=(0, 0, -10), spread=(16, 0, 6)) + mind("A", (0, 0, -8), "walk", 180, anim=[{"type": "move", "to": [0, 0, -5]}])), MORNING,
    focus=(0, 1.4, -8), zoom=1.0), "8:15 AM")
bags = lambda x: [O("box", (x - 0.35, 0.9, -6), [0.3, 0.4, 0.25], "#c97a40", animate=[{"type": "bob", "amount": 0.03, "speed": 3}]),
                  O("box", (x + 0.35, 0.9, -6), [0.3, 0.4, 0.25], "#c97a40", animate=[{"type": "bob", "amount": 0.03, "speed": 3}])]
B("follow", "At the store, Maya picks up all the heavy bags without even thinking. On average, men's bodies carry about 40 percent more upper-body muscle.",
  V(street(mind("M", (0.8, 0, -6), "walk", 180) + bags(0.8) + mind("A", (-0.8, 0, -6), "walk", 180)), MORNING, focus=(0, 1.2, -6), zoom=0.9), "8:30 AM",
  cap="Maya grabs all the heavy bags without thinking.", stat={"value": "+40%", "label": "UPPER-BODY MUSCLE, MEN VS WOMEN (AVERAGE)", "count_up": True})
B("side", "Alex can't open the pickle jar. He has never felt so personally offended.",
  V(kitchen(mind("A", (0, 0, -6.4), "kneel", 90, anim=[{"type": "wobble", "amount": 0.2, "speed": 4}]) +
            [O("cylinder", (0.3, 1.1, -6.4), [0.12, 0.2, 0.12], "#94d82d", animate=[{"type": "spin", "speed": 2}])]), MORNING, focus=(0, 1.0, -6.4), zoom=0.5,
    bounce="#fff3bf"), "8:40 AM", sfx=[{"type": "crack", "at": 2.2, "gain": 0.3}])

# ======================================================================= 9 AM — THE OFFICE
B("wide", "9 AM. The office.",
  V(office(extra=mixed(7, 71, at=(0, 0, -8), spread=(14, 0, 8), act="sit") + [crowd(3, 72, at=(0, 0, -11), spread=(14, 0, 2))]), ["#e9ecef", "#a5d8ff"], focus=(0, 1.2, -8), zoom=1.0, bounce="#e9ecef"), "9:00 AM",
  chapter="9 AM: The Office", transition="dip")
B("dolly", "Within an hour, men all over the world are reaching for a sweater.",
  V(office(extra=mind("A", (-1, 0, -7), "sit", 180) + mind("M", (1.4, 0, -7), "sit", 180) +
           [O("particles", (-1, 1.6, -7), 0.15, "#e7f5ff", count=10, seed=3, spread=[0.6, 0.6, 0.6], animate=[{"type": "drift", "axis": "y", "amount": 0.2}])]),
    ["#e9ecef", "#a5d8ff"], focus=(0, 1.2, -7), zoom=1.0, bounce="#e9ecef"), "9:50 AM", sfx=[{"type": "breath", "at": 0.5, "dur": 1.6, "gain": 0.4}])
B("follow", "Here's the real reason. Many office thermostats still follow a comfort formula from the 1960s. It was based on the body of an average 40-year-old man.",
  V(office(extra=[O("plane", (-6, 1.65, -13.84), [0.36, 0.25, 1], "#74c0fc", material="glow", animate=[{"type": "pulse", "amount": 0.3, "speed": 2}])] +
           mind("A", (-6, 0, -12.8), "point", 0)), ["#e9ecef", "#a5d8ff"], focus=(-6, 1.5, -13), zoom=0.6, bounce="#e9ecef"), "10:00 AM",
  cap="Many thermostats use a 1960s formula based on an average man.", tooltip={"label": "REAL STUDY", "text": "Nature Climate Change, 2015"})
B("side", "Women's bodies tend to burn energy more slowly, so many women feel colder in those offices. Today, the men feel it instead.",
  V(office(extra=mind("A", (0, 0, -7), "sit", 90, anim=[{"type": "wobble", "amount": 0.08, "speed": 6}])), ["#e9ecef", "#a5d8ff"], focus=(0, 1.2, -7), zoom=0.6,
    bounce="#e9ecef"), "10:05 AM", cap="Today, the men are the ones freezing.")
B("wide", "So be honest. Are you team always-cold, or team always-hot? Drop it below.",
  V(office(extra=mixed(7, 81, at=(0, 0, -8), spread=(14, 0, 8), act="sit") + [crowd(3, 82, at=(0, 0, -11), spread=(14, 0, 2))]), ["#e9ecef", "#a5d8ff"], focus=(0, 1.2, -8), zoom=1.0, bounce="#e9ecef"), "10:10 AM",
  cap="Team always-cold or team always-hot? Comment.")
meet = [O("box", (0, 0.74, -8), [5, 0.06, 1.8], "#8d6e57")]
B("orbit", "At the 10:30 meeting, things get interesting.",
  V(office(thermo=False, extra=meet + mind("A", (-1.6, 0, -7), "sit", 180) + mind("M", (1.6, 0, -9), "sit", 0) + [crowd(4, 91, at=(0, 0, -8), spread=(4, 0, 2), act="sit")]),
    ["#e9ecef", "#a5d8ff"], focus=(0, 1.2, -8), zoom=1.0, bounce="#e9ecef"), "10:30 AM")
B("side", "Many women say they get talked over in meetings. Today, a lot of men get to find out what that's like. From the other chair.",
  V(office(thermo=False, extra=meet + mind("A", (-1.6, 0, -7), "point", 180) + mind("M", (1.6, 0, -9), "point", 0)), ["#e9ecef", "#a5d8ff"], focus=(0, 1.2, -8), zoom=0.8,
    bounce="#e9ecef"), "10:35 AM", cap="Today, men see meetings from the other chair.")

# ======================================================================= NOON — LUNCH
B("dolly", "Noon. Lunch. And the women, now in men's bodies, are starving.",
  V(cafe(mind("M", (0, 0, -6), "sit", 180) + mind("A", (0, 0, -8), "sit", 0) + [crowd(6, 101, at=(0, 0, -7), spread=(12, 0, 6), act="sit")]), ["#ffe8cc", "#ffd8a8"],
    focus=(0, 1.0, -7), zoom=1.0, bounce="#ffe8cc"), "12:00 PM", chapter="Noon: Lunch", transition="whip")
B("side", "Men's bodies usually need several hundred more calories a day. So Maya orders two burgers. Alex can only finish half a sandwich.",
  V(cafe(mind("M", (0, 0, -6), "sit", 180) + mind("A", (0, 0, -8), "sit", 0) + [O("cylinder", (0, 0.86, -6.5), [0.25, 0.14, 0.25], "#d9480f", count=2, seed=2, spread=[0.6, 0, 0.1])]),
    ["#ffe8cc", "#ffd8a8"], focus=(0, 1.0, -7), zoom=0.6, bounce="#ffe8cc"), "12:10 PM", cap="Maya orders two burgers. Alex can't finish half a sandwich.",
  tooltip={"label": "FACT", "text": "Men's bodies usually need several hundred more calories a day."})
B("wide", "And then, something nobody saw coming. About 1 in 12 men is colorblind. For women, it's about 1 in 200.",
  V((park_like := [O("box", (0, -0.02, -14), [80, 0.04, 60], "#69a84f"), O("tree", (0, 0, -20), 1.6, "#3f8f3a", count=12, seed=3, spread=[50, 0, 16])]) +
    mind("A", (0, 0, -8), "idle", 180), DAY, focus=(0, 1.2, -9), zoom=1.6), "12:30 PM", cap="About 1 in 12 men is colorblind. For women: 1 in 200.",
  stat={"value": "1 IN 12", "label": "MEN WHO ARE COLORBLIND", "count_up": False})
flowers = [O("sphere", (0, 0.4, -10), 0.25, c, count=10, seed=i + 3, spread=[30, 0, 14]) for i, c in enumerate(["#e03131", "#fab005", "#40c057", "#7048e8", "#f783ac"])]
B("closeup", "Alex is one of them. Today, for the first time in his life, he sees red and green the way everyone else does.",
  V(park_like + flowers + mind("A", (0, 0, -8), "idle", 0), DAY, focus=(0, 1.6, -8), zoom=0.7), "12:31 PM", effects=["rays", "bloom"],
  cap="Alex sees red and green for the first time.", sfx=[{"type": "sparkle", "at": 0.6, "gain": 0.6}, {"type": "swell", "at": 0.8, "dur": 2.5, "gain": 0.5}])
B("wide", "He just stands there, staring at the flowers for ten minutes. Meanwhile, millions of women find out what it's like to mix them up.",
  V(park_like + flowers + mind("A", (0, 0, -8), "idle", 180) + mind("M", (2, 0, -7), "walk", 270, anim=[{"type": "move", "to": [0.8, 0, -7.2]}]), DAY,
    focus=(0, 1.2, -8), zoom=1.2), "12:40 PM", cap="Millions of women find out what it's like to mix up red and green.")

# ======================================================================= 2 PM — THE PERIOD
B("establishing", "2 PM. And now, the moment the men have been dreading.",
  V(plaza(mixed(20, 111, at=(0, 0, -16), spread=(50, 0, 18))), GOLD, focus=(0, 1.5, -18), zoom=3.0), "2:00 PM", chapter="2 PM: The Hour Men Dread", transition="dip",
  sfx=[{"type": "heartbeat", "at": 0.5, "dur": 2.6, "gain": 0.6}])
B("wide", "On any given day, more than 300 million people are on their period. Today, every one of those bodies has a man inside it.",
  V(plaza(mixed(24, 121, at=(0, 0, -16), spread=(60, 0, 20), act="kneel")), GOLD, focus=(0, 1.5, -18), zoom=3.4), "2:05 PM", cap="300+ million people are on their period on any given day.",
  stat={"value": "300 MILLION", "label": "ON THEIR PERIOD TODAY (WORLD BANK)", "count_up": True})
B("side", "Alex feels the first cramp at his desk. He is honestly convinced something is seriously wrong.",
  V(office(thermo=False, extra=mind("A", (0, 0, -7), "kneel", 90, anim=[{"type": "wobble", "amount": 0.15, "speed": 3}])), ["#e9ecef", "#a5d8ff"], focus=(0, 1.0, -7), zoom=0.6,
    bounce="#e9ecef"), "2:10 PM", effects=["tunnel"])
B("follow", "He calls Maya, panicking. She doesn't even look up. She just says: heating pad, painkiller, chocolate. In that order.",
  V(office(thermo=False, extra=mind("M", (0, 0, -7), "point", 180) + [O("box", (0.4, 0.8, -6.6), [0.1, 0.2, 0.02], "#212529")]), ["#e9ecef", "#a5d8ff"], focus=(0, 1.2, -7),
    zoom=0.7, bounce="#e9ecef"), "2:12 PM", cap="Maya: \"Heating pad. Painkiller. Chocolate. In that order.\"")
B("dolly", "By 4 PM, pharmacies would probably be sold out of painkillers. And chocolate.",
  V(room("#fff3bf", "#e9ecef", w=14, d=12, extra=[O("box", (-3, 0.9, -7), [0.8, 1.8, 8], "#adb5bd", material="metal"), O("box", (3, 0.9, -7), [0.8, 1.8, 8], "#adb5bd", material="metal"),
         O("box", (-3, 1.3, -7), [0.9, 0.2, 0.3], "#e03131", count=6, seed=4, spread=[0, 0, 7], animate=[{"type": "shrink"}])] + mixed(6, 131, at=(0, 0, -6), spread=(3, 0, 8), act="run")),
    ["#fff3bf", "#ffe066"], focus=(0, 1.2, -6), zoom=1.0, bounce="#fff3bf"), "4:00 PM")
B("wide", "Men, be honest in the comments: would you have made it through the whole day without calling in sick?",
  V(office(thermo=False, extra=mixed(6, 141, at=(0, 0, -8), spread=(14, 0, 8), act="kneel") + [crowd(3, 142, at=(0, 0, -11), spread=(14, 0, 2))]), ["#e9ecef", "#a5d8ff"], focus=(0, 1.2, -8), zoom=1.0, bounce="#e9ecef"),
  "4:30 PM", cap="Men: would you have made it through the day? Be honest.")

# ======================================================================= 6 PM — WALKING HOME
B("follow", "6 PM. It's getting dark. Maya walks home alone.",
  V(street(lit=True, extra=mind("M", (0, 0, -9), "walk", 180, anim=[{"type": "move", "to": [0, 0, -5]}])), DUSK, focus=(0, 1.3, -8), zoom=1.0), "6:00 PM",
  chapter="6 PM: Walking Home", transition="dip")
B("side", "And for the first time in years, she doesn't hold her keys between her fingers.",
  V(street(lit=True, extra=mind("M", (0, 0, -7), "walk", 270, anim=[{"type": "move", "to": [-3, 0, -7]}])), DUSK, focus=(-1, 1.2, -7), zoom=0.7), "6:05 PM")
B("wide", "Surveys keep finding the same thing: women feel far less safe walking alone at night than men do.",
  V(street(lit=True, extra=mixed(6, 151, at=(0, 0, -10), spread=(40, 0, 4))), DUSK, focus=(0, 1.3, -11), zoom=2.2), "6:10 PM",
  tooltip={"label": "SURVEYS", "text": "Women report feeling much less safe walking alone at night."})
B("follow", "Alex walks the same street ten minutes later. And for the first time, he notices every single footstep behind him.",
  V(street(lit=True, extra=mind("A", (0, 0, -8), "walk", 180, anim=[{"type": "move", "to": [0, 0, -5]}]) +
           [O("person", (0, 0, -14), 1.0, "#495057", action="walk", seed=17, color2="#8d5524", rotate=[0, 180, 0], animate=[{"type": "move", "to": [0, 0, -10]}])]),
    NIGHT, focus=(0, 1.3, -8), zoom=1.0), "6:15 PM", effects=["tunnel"], sfx=[{"type": "steps", "at": 0.3, "dur": 3.4, "gain": 0.6}])
B("far", "Same street. Same night. A completely different walk.",
  V(street(lit=True, extra=mind("A", (-1, 0, -9), "walk", 180) + mind("M", (1, 0, -9), "walk", 180)), NIGHT, focus=(0, 1.3, -9), zoom=2.4), "6:20 PM", move="pull_out")

# ======================================================================= 8 PM — DATE NIGHT
B("dolly", "8 PM. Date night. In each other's bodies.",
  V(restaurant(mind("A", (0, 0, -6.2), "sit", 180) + mind("M", (0, 0, -7.8), "sit", 0)), WARM, focus=(0, 1.0, -7), zoom=1.0, bounce="#5f3dc4"), "8:00 PM",
  chapter="8 PM: Date Night", transition="whip")
B("side", "The check arrives. And here's the question: who pays? The body, or the brain? Tell me in the comments.",
  V(restaurant(mind("A", (0, 0, -6.2), "point", 180) + mind("M", (0, 0, -7.8), "point", 0) + [O("box", (0, 0.8, -7), [0.2, 0.02, 0.3], "#212529")]), WARM,
    focus=(0, 1.0, -7), zoom=0.6, bounce="#5f3dc4"), "8:45 PM", cap="Who pays: the body or the brain? Comment.")
B("orbit", "Then they try to dance. Neither of them has any idea who's supposed to lead.",
  V(restaurant(mind("A", (-0.4, 0, -4), "walk", 90, anim=[{"type": "orbit", "amount": 0.4, "speed": 1.2}]) +
               mind("M", (0.4, 0, -4), "walk", 270, anim=[{"type": "orbit", "amount": 0.4, "speed": 1.2}])), WARM, focus=(0, 1.2, -4), zoom=0.8, bounce="#5f3dc4"),
  "9:15 PM", sfx=[{"type": "shimmer", "at": 0.5, "gain": 0.4}])
B("wide", "They step on each other's feet so many times that the whole restaurant starts laughing. And then, so do they.",
  V(restaurant(mind("A", (-0.4, 0, -4), "idle", 90) + mind("M", (0.4, 0, -4), "idle", 270)), WARM, focus=(0, 1.2, -5), zoom=1.4, bounce="#5f3dc4"), "9:20 PM",
  effects=["confetti"])

# ======================================================================= 11 PM — THE NIGHT
B("follow", "11 PM. Bedtime. One last surprise.",
  V(bedroom("#1b2440", lamp=True, extra=[body("M", (-0.6, 0.62, -7.3), "lie"), halo((-0.6, 0.62, -7.3), HALO_A, 0.6), body("A", (0.6, 0.62, -7.3), "lie"),
                                          halo((0.6, 0.62, -7.3), HALO_M, 0.6)]), NIGHT_IN, focus=(0, 0.8, -7.5), zoom=1.0, bounce="#3b4a6b"), "11:00 PM",
  chapter="11 PM: Lights Out", transition="dip")
B("side", "About 4 in 10 men snore regularly, compared to about 1 in 4 women.",
  V(bedroom("#1b2440", lamp=True, extra=[body("A", (0.6, 0.62, -7.3), "lie", anim=[{"type": "bob", "amount": 0.03, "speed": 0.8}]), halo((0.6, 0.62, -7.3), HALO_M, 0.6)]),
    NIGHT_IN, focus=(0.6, 0.8, -7.3), zoom=0.6, bounce="#3b4a6b"), "11:30 PM", stat={"value": "40% VS 24%", "label": "MEN VS WOMEN WHO SNORE REGULARLY", "count_up": False},
  sfx=[{"type": "breath", "at": 0.3, "dur": 3.0, "gain": 0.8}])
B("follow", "So tonight, Maya finally finds out who's been snoring all these years. It's her. Well, it's his body. Alex lies there, wide awake.",
  V(bedroom("#1b2440", lamp=True, extra=[body("M", (-0.6, 0.62, -7.3), "lie"), halo((-0.6, 0.62, -7.3), HALO_A, 0.6), body("A", (0.6, 0.62, -7.3), "lie",
         anim=[{"type": "bob", "amount": 0.03, "speed": 0.8}]), halo((0.6, 0.62, -7.3), HALO_M, 0.6)]), NIGHT_IN, focus=(0, 0.8, -7.5), zoom=0.8, bounce="#3b4a6b"),
  "1:00 AM", cap="Maya finds out who's been snoring all these years.", sfx=[{"type": "breath", "at": 0.3, "dur": 3.4, "gain": 0.8}])

# ======================================================================= 5:59 AM — THE SWITCH BACK
B("wide", "5:59 AM. One minute left.",
  V(bedroom("#ffd8a8", extra=mind("A", (-0.6, 0.45, -7.3), "sit", 180) + mind("M", (0.6, 0.45, -7.3), "sit", 180)), DAWN, focus=(0, 1.0, -7.3), zoom=1.0, bounce="#e9dcc9"),
  "5:59 AM", chapter="5:59 AM: The Switch Back", transition="dip", sfx=[{"type": "tick", "at": 0.4, "gain": 0.6}, {"type": "tick", "at": 1.4, "gain": 0.6}])
B("follow", "Before it ends, they ask each other one question. What will you miss?",
  V(bedroom("#ffd8a8", extra=mind("A", (-0.6, 0.45, -7.3), "sit", 90) + mind("M", (0.6, 0.45, -7.3), "sit", 270)), DAWN, focus=(0, 1.1, -7.3), zoom=0.7, bounce="#e9dcc9"),
  "5:59 AM")
B("side", "Maya says: walking home at night without looking over my shoulder.",
  V(bedroom("#ffd8a8", extra=mind("M", (0.6, 0.45, -7.3), "sit", 270)), DAWN, focus=(0.6, 1.2, -7.3), zoom=0.45, bounce="#e9dcc9"), "5:59 AM",
  effects=["glow"])
B("side", "Alex thinks for a long time. Then he says: the colors. I'm going to miss the colors.",
  V(bedroom("#ffd8a8", extra=mind("A", (-0.6, 0.45, -7.3), "sit", 90)), DAWN, focus=(-0.6, 1.2, -7.3), zoom=0.45, bounce="#e9dcc9"), "5:59 AM",
  effects=["glow"], sfx=[{"type": "swell", "at": 0.5, "dur": 3.0, "gain": 0.5}])
B("wide", "6 AM. Everyone, everywhere, snaps back.",
  V(plaza(mixed(24, 161, at=(0, 0, -16), spread=(60, 0, 20), act="idle", halos=False) +
          [O("person", (0, 0, -16), 1.0, BLUE, count=1, seed=1)]), DAWN, focus=(0, 1.5, -18), zoom=3.4), "6:00 AM", effects=["flash"],
  sfx=[{"type": "shimmer", "at": 0.1, "gain": 0.9}])
B("orbit", "The world looks exactly the same. But nobody sees it quite the same way anymore.",
  V(bedroom("#ffd8a8", extra=mind("A", (-0.6, 0, -5), "idle", 180, swapped=False) + mind("M", (0.6, 0, -5), "idle", 180, swapped=False)), MORNING, focus=(0, 1.2, -5),
    zoom=0.8, bounce="#e9dcc9"), "6:01 AM", effects=["rays"])
B("far", "Maybe that's the point. Spend one day in someone else's body, and maybe we'd argue a little less.",
  V(street(mixed(10, 171, at=(0, 0, -10), spread=(40, 0, 6), halos=False) + mind("A", (-0.6, 0, -8), "walk", 180, swapped=False) +
           mind("M", (0.6, 0, -8), "walk", 180, swapped=False)), GOLD, focus=(0, 1.3, -9), zoom=2.2), "THE NEXT DAY", move="pull_out")
B("wide", "So, who had the harder day: the men or the women? And what would you miss? Tell me in the comments. I read every one.",
  V(plaza(mixed(20, 181, at=(0, 0, -16), spread=(50, 0, 18), act="idle", halos=False)), GOLD, focus=(0, 1.5, -18), zoom=3.0), "THE NEXT DAY",
  cap="Who had the harder day? And what would you miss?", hud=False)

# short on-screen subtitles for long narrated lines (the narrator still says the full line)
SHORT = {
    "Tomorrow at 6 AM": "At 6 AM, every man and woman wakes up in the other's body.",
    "Four billion men.": "4 billion men. 4 billion women. But no warning.",
    "By 9 AM, millions": "By 9 AM, men are freezing. Here's the weird reason why.",
    "Alex has never put on a bra": "Alex's first bra: four tries and a tutorial.",
    "On the sidewalk, the men": "Now shorter, men see a wall of shoulders.",
    "By 4 PM, pharmacies": "By 4 PM, stores run out of pain pills. And chocolate.",
    "Surveys keep finding": "Women feel far less safe walking alone at night.",
    "Alex walks the same street": "Alex hears every footstep behind him.",
    "They step on each other's feet": "The whole place laughs. Then so do they.",
    "Alex thinks for a long time": "Alex: \"I'm going to miss the colors.\"",
    "In the kitchen, Maya grabs": "Maya reaches the top shelf. Easily. For the first time.",
    "Alex, now about five inches": "Alex, 5 inches shorter, needs a chair.",
    "Maybe that's the point.": "One day in their body, and we might argue less.",
    "By 2 PM, around 300 million": "By 2 PM, 300 million men feel something brand new.",
    "And at the very end": "At the end, both sides admit something. Stay for it.",
    "Here's the real reason.": "Here's why: a 1960s thermostat formula based on an average man.",
}
for b in beats:
    for k, short in SHORT.items():
        if b["caption"].startswith(k) and "narration" not in b:
            b["narration"], b["caption"] = b["caption"], short

sb = {"format": "story", "title": "What if men and women swapped bodies for a day?",
      "premise": "For 24 hours, every man and woman on Earth wakes up in each other's body. Follow Alex and Maya hour by hour, with real facts about height, strength, "
                 "temperature, color vision, periods, safety and sleep.",
      "width": 1920, "height": 1080,
      "narration": {"enabled": True, "engine": "kokoro", "voice": "am_michael", "speed": 1.05, "read_title": False, "read_end": False},
      "intro": {"style": "none", "title": "What if men and women *swapped bodies* for a day?"},
      "theme": {"style": "calm", "accent": "#f06595"},
      "clock": {"mode": "none", "intro_label": "THE SWAP HAPPENS IN", "intro_from": 3},
      "outro": {"chart": False, "question_duration": 5.0, "end": {"kind": "question", "lines": ["WHO HAD THE", "HARDER DAY?"], "accent_line": 1}},
      "thumbnail": "24 HOURS IN *THEIR* BODY", "thumbnail_beat": 10, "beats": beats}
out = Path(__file__).parent / "swap24.json"
out.write_text(json.dumps(sb, indent=1, ensure_ascii=False))
print(out, len(beats))
