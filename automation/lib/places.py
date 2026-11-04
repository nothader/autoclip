"""Reusable places for the Block POV format. Every builder returns a list of set objects (stay under 40 per shot with extras).

Conventions: you (camera "eyes") stand near z = +1 looking toward −z. Block people face −z by default, so people who should
face YOU need ry=180. "front" cameras sit at −z looking back toward +z (they see faces of people with ry=0).
Every builder takes seed/colour arguments so the same place never looks identical twice.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from props import O  # noqa: E402
from block import guy, crowd  # noqa: E402

BRICK = ["#9c5b43", "#b3684a", "#8a4f3a", "#c47a5a"]; STONE = ["#c9c1b3", "#d8d0c2", "#b9b2a6"]; GLASS = ["#7d93ad", "#93a8c0", "#6f86a1"]
CONCRETE = ["#9da3aa", "#b5bac0", "#868c94"]


def _r(seed):
    return random.Random(seed * 7919 + 17)


def street(seed=1, length=80, width=10, palette=None, people=14, cars=4, lamps=True, extra=()):
    """A city street running along −z: road, sidewalks, two rows of buildings, street lamps, a few cars and people."""
    r = _r(seed)
    pal = palette or (BRICK + GLASS + CONCRETE)
    o = [O("box", (0, -0.03, -length / 2), [width + 16, 0.04, length + 20], "#5a5d63"),
         O("box", (-(width / 2 + 2), 0.06, -length / 2), [4, 0.12, length + 20], "#a8a49c"),
         O("box", (width / 2 + 2, 0.06, -length / 2), [4, 0.12, length + 20], "#a8a49c"),
         O("box", (0, 0.0, -length / 2), [0.25, 0.01, length], "#e8d36a")]
    z = 4
    while z > -length and len(o) < 26:
        for side in (-1, 1):
            h, w, d = r.choice([9, 12, 15, 20, 26, 34]), r.uniform(7, 10), r.uniform(7, 10)
            o.append(O("box", (side * (width / 2 + 4 + w / 2), h / 2, z - d / 2), [w, h, d], r.choice(pal)))
        z -= r.uniform(9, 12)
    if lamps:
        o.append(O("cylinder", (width / 2 + 0.6, 2.2, -length / 2), [0.12, 4.4, 0.12], "#2b2f36", count=6, seed=seed, spread=[0, 0, length]))
        o.append(O("sphere", (width / 2 + 0.6, 4.5, -length / 2), 0.22, "#ffe9b0", material="glow", count=6, seed=seed, spread=[0, 0, length]))
    if cars:
        o.append(O("box", (1.8, 0.6, -length / 3), [1.9, 1.2, 4.2], r.choice(["#c92a2a", "#1c7ed6", "#f8f9fa", "#212529", "#f59f00"]),
                   count=cars, seed=seed + 3, spread=[5, 0, length / 2]))
    if people:
        o.append(crowd(people, seed + 5, at=(0, 0.12, -length / 3), spread=(width + 6, 0, length / 1.6), act="walk"))
    return o + list(extra)


def terrace(seed=1, lights="#ffe7a8", floor="#b57a52", extra=()):
    """Rooftop restaurant / party terrace: deck, railing, tables with candles, string lights, skyline beyond."""
    r = _r(seed)
    o = [O("box", (0, -0.03, -4), [16, 0.06, 14], floor), O("box", (0, 0.55, -10.5), [16, 1.1, 0.08], "#3a3f46", material="glass", opacity=0.4),
         O("box", (0, 1.1, -10.5), [16, 0.06, 0.08], "#2b2f36")]
    for i in range(4):
        x, z = r.uniform(-5, 5), r.uniform(-8, -1)
        o += [O("cylinder", (x, 0.38, z), [1.0, 0.76, 1.0], "#f1ece4"), O("cylinder", (x, 0.83, z), [0.06, 0.14, 0.06], "#fff3d6", material="glow")]
    o.append(O("sphere", (0, 3.2, -5), 0.08, lights, material="glow", count=24, seed=seed, spread=[14, 0.6, 10]))
    for k in range(7):   # skyline
        h = r.uniform(25, 90)
        o.append(O("box", (r.uniform(-60, 60), h / 2 - 10, r.uniform(-90, -50)), [r.uniform(10, 18), h, 12], r.choice(GLASS + CONCRETE)))
    return o + list(extra)


def hospital_room(seed=1, wall="#dfe6ea", extra=(), you_in_bed=True):
    """Room seen from the bed (you lie at z≈+1 looking toward −z): bed rails, blanket, monitor, window, door."""
    o = [O("box", (0, -0.02, -1.5), [6, 0.04, 7], "#b9a993"), O("box", (0, 1.5, -4.5), [6, 3, 0.1], wall), O("box", (-3, 1.5, -1.5), [0.1, 3, 7], wall),
         O("box", (3, 1.5, -1.5), [0.1, 3, 7], wall), O("box", (0, 3.0, -1.5), [6, 0.05, 7], "#f1f3f5"),
         O("plane", (0, 2.97, -1.5), [1.4, 0.6, 1], "#ffffff", material="glow", rotate=[90, 0, 0]),
         O("plane", (1.2, 1.7, -4.44), [1.8, 1.2, 1], "#a9c8e8", material="glow"),
         O("box", (-1.6, 1.05, -4.42), [0.95, 2.1, 0.05], "#c4b49c"),
         O("box", (2.3, 1.9, -0.6), [0.3, 0.4, 0.5], "#2b2f36"), O("plane", (2.14, 1.92, -0.6), [0.42, 0.3, 1], "#58f08e", material="glow", rotate=[0, -90, 0]),
         O("box", (2.3, 1.0, -0.6), [0.05, 1.8, 0.05], "#adb5bd")]
    if you_in_bed:
        o += [O("box", (0, 0.65, -0.4), [1.2, 0.25, 2.4], "#a5c8e1"), O("box", (-0.65, 0.95, -0.4), [0.05, 0.3, 1.8], "#ced4da"),
              O("box", (0.65, 0.95, -0.4), [0.05, 0.3, 1.8], "#ced4da")]
    return o + list(extra)


def bedroom(seed=1, wall="#4b3f6b", night=True, extra=()):
    """Your bedroom from the bed: blanket, window with city lights, shelf, lamp, string lights."""
    r = _r(seed)
    o = [O("box", (0, -0.02, -1.5), [6, 0.04, 7], "#7a5a43"), O("box", (0, 1.5, -4.0), [6, 3, 0.1], wall), O("box", (-3, 1.5, -1.5), [0.1, 3, 7], wall),
         O("box", (3, 1.5, -1.5), [0.1, 3, 7], wall), O("box", (0, 3.0, -1.5), [6, 0.05, 7], "#d9d2c7"),
         O("plane", (0, 1.7, -3.94), [2.6, 1.6, 1], "#1e2a52" if night else "#a9d1f5", material="glow"),
         O("particles", (0, 1.6, -3.9), 0.06, "#ffd98a", count=40, seed=seed, spread=[2.4, 1.2, 0.05]),
         O("box", (0, 0.45, 0.2), [1.6, 0.4, 2.0], "#c9d6e3"), O("box", (0, 0.68, 0.0), [1.6, 0.08, 1.6], r.choice(["#e9ecef", "#a5d8ff", "#ffd8a8"])),
         O("box", (2.2, 1.6, -3.85), [1.2, 0.05, 0.3], "#6b4f3a"), O("box", (2.0, 1.75, -3.85), [0.2, 0.3, 0.2], "#7048e8"),
         O("sphere", (0, 2.75, -3.9), 0.05, "#ffe7a8", material="glow", count=12, seed=seed + 1, spread=[5, 0.2, 0.05]),
         O("box", (-2.3, 0.3, -3.4), [0.5, 0.6, 0.5], "#5c4a3a"), O("cone", (-2.3, 0.9, -3.4), [0.4, 0.4, 0.4], "#ffe8b0", material="glow")]
    return o + list(extra)


def church(seed=1, pews=True, extra=()):
    """Church interior looking toward the altar (−z): pews, columns, stained-glass window, altar, cross."""
    o = [O("box", (0, -0.02, -8), [12, 0.04, 22], "#a07850"), O("box", (0, 4, -19), [12, 8, 0.2], "#e8dfd0"),
         O("box", (-6, 4, -8), [0.2, 8, 22], "#e8dfd0"), O("box", (6, 4, -8), [0.2, 8, 22], "#e8dfd0"),
         O("cylinder", (-4.5, 3.5, -8), [0.5, 7, 0.5], "#c9b8a0", count=4, seed=seed, spread=[0, 0, 18]),
         O("cylinder", (4.5, 3.5, -8), [0.5, 7, 0.5], "#c9b8a0", count=4, seed=seed + 1, spread=[0, 0, 18]),
         O("plane", (0, 5.2, -18.85), [2.4, 2.4, 1], "#ff9f6b", material="glow"), O("plane", (0, 5.2, -18.8), [1.2, 1.2, 1], "#6b8cff", material="glow"),
         O("box", (0, 0.5, -16.5), [3, 1.0, 1.2], "#f1ece4"), O("box", (0, 3.2, -18.7), [0.25, 2.4, 0.1], "#8a5a3b"),
         O("box", (0, 3.6, -18.7), [1.2, 0.25, 0.1], "#8a5a3b"),
         O("sphere", (0, 6.2, -10), 0.35, "#ffe9b8", material="glow", count=3, seed=seed + 2, spread=[0, 0, 12])]
    if pews:
        o += [O("box", (-2.4, 0.45, -7), [3.2, 0.9, 0.5], "#5c3a21", count=8, seed=seed + 3, spread=[0, 0, 14]),
              O("box", (2.4, 0.45, -7), [3.2, 0.9, 0.5], "#5c3a21", count=8, seed=seed + 4, spread=[0, 0, 14])]
    return o + list(extra)


def mosque(seed=1, extra=()):
    """Mosque exterior across a square: dome, arched door, minaret, courtyard."""
    return [O("box", (0, -0.03, -14), [60, 0.04, 50], "#c9b99a"), O("box", (0, 4, -26), [16, 8, 10], "#e9e4da"),
            O("sphere", (0, 8, -26), [6, 4.5, 6], "#3fa7b5", material="glossy"), O("box", (0, 2.6, -20.95), [3.2, 5.2, 0.1], "#2f5f9e"),
            O("cylinder", (9, 9, -24), [1.0, 18, 1.0], "#e9e4da"), O("cone", (9, 19, -24), [1.4, 2.4, 1.4], "#3fa7b5"),
            O("sphere", (0, 10.8, -26), 0.3, "#f2c94c", material="glossy")] + list(extra)


def office_floor(seed=1, night=False, extra=()):
    """Open-plan office: desks with monitors, ceiling lights, windows on the far wall."""
    o = [O("box", (0, -0.02, -6), [16, 0.04, 18], "#6b7078"), O("box", (0, 3.0, -6), [16, 0.05, 18], "#e9ecef"),
         O("plane", (0, 2.97, -6), [1.2, 0.5, 1], "#ffffff", material="glow", rotate=[90, 0, 0], count=6, seed=seed, spread=[10, 0, 14]),
         O("plane", (0, 1.6, -14.9), [16, 2.6, 1], "#1b2a4a" if night else "#b9d3ee", material="glow"),
         O("box", (-3, 0.38, -6), [1.6, 0.76, 0.8], "#d9cbb4", count=6, seed=seed + 1, spread=[1, 0, 12]),
         O("box", (3, 0.38, -6), [1.6, 0.76, 0.8], "#d9cbb4", count=6, seed=seed + 2, spread=[1, 0, 12]),
         O("plane", (-3, 1.05, -6.2), [0.5, 0.32, 1], "#8fd3ff", material="glow", count=6, seed=seed + 1, spread=[1, 0, 12]),
         O("plane", (3, 1.05, -6.2), [0.5, 0.32, 1], "#8fd3ff", material="glow", count=6, seed=seed + 2, spread=[1, 0, 12])]
    return o + list(extra)


def stairwell(seed=1, steps=12, stripe="#9fe3b8", floor_no=None, extra=()):
    """Emergency stairwell going down toward −z, glow-in-the-dark stripes on each edge, handrail, wall light."""
    o = [O("box", (0, 1.62 - 0.18 * i - 0.09, -0.3 * i), [1.4, 0.18, 0.3], "#8a8f96") for i in range(0, steps, 1)][:12]
    o += [O("box", (0, 1.62 - 0.18 * i + 0.002, -0.3 * i + 0.12), [1.3, 0.01, 0.05], stripe, material="glow") for i in range(0, 12, 2)]
    o += [O("box", (-0.75, 1.2, -2), [0.06, 4.0, 6], "#d9d4cc"), O("box", (0.75, 1.2, -2), [0.06, 4.0, 6], "#d9d4cc"),
          O("box", (0.68, 1.4, -1.8), [0.05, 0.05, 4.4], stripe, rotate=[-31, 0, 0]), O("box", (0, 3.3, -2), [1.5, 0.05, 6], "#cfc9c0"),
          O("plane", (0.72, 2.6, -1.0), [0.3, 0.2, 1], "#fff4dc", material="glow", rotate=[0, -90, 0])]
    return o + list(extra)


def plain(seed=1, ground="#e9e4da", people=80, extra=()):
    """An endless pale plain with rows of people (gatherings, judgment scenes)."""
    return [O("box", (0, -0.03, -40), [400, 0.04, 400], ground), crowd(min(people, 200), seed, at=(0, 0, -18), spread=(40, 0, 30), act="idle", ry=180)] + list(extra)


def living_room(seed=1, wall="#e9dfcf", tv="#2b3a55", extra=()):
    return [O("box", (0, -0.02, -2), [8, 0.04, 8], "#8a6a4f"), O("box", (0, 1.5, -5.5), [8, 3, 0.1], wall), O("box", (-4, 1.5, -2), [0.1, 3, 8], wall),
            O("box", (0, 1.4, -5.4), [2.2, 1.3, 0.08], "#111"), O("plane", (0, 1.4, -5.35), [2.0, 1.1, 1], tv, material="glow"),
            O("box", (0, 0.35, -1.0), [2.6, 0.7, 0.9], "#748ffc"), O("box", (0, 0.4, -4.8), [2.4, 0.8, 0.4], "#5c3d2e"),
            O("box", (-2.8, 0.3, -4.5), [0.5, 0.6, 0.5], "#40c057")] + list(extra)


def park(seed=1, grass="#7aa35a", trees=8, people=10, extra=()):
    return [O("box", (0, -0.03, -20), [120, 0.04, 120], grass), O("box", (0, 0.0, -20), [2.4, 0.02, 80], "#c8b9a0"),
            O("tree", (0, 0, -18), 1.8, "#4f8a3a", count=trees, seed=seed, spread=[40, 0, 30]),
            O("box", (3, 0.25, -6), [1.8, 0.5, 0.5], "#6b4f3a", count=3, seed=seed + 1, spread=[0, 0, 16]),
            crowd(people, seed + 2, at=(0, 0, -14), spread=(20, 0, 16), act="walk")] + list(extra)
