"""DinkCam asset library: creatures, props and places for first-person toy-world videos.
Every builder returns a LIST of object dicts (kind, at, scale, colour, material, animate ...).
Camera default: you stand near z=+1.6 looking toward -z. face_you=True turns creatures toward you (+z).
"""
import random


def O(kind, at, scale=1, color="#d8d8d8", **kw):
    d = {"kind": kind, "at": list(at), "scale": scale if isinstance(scale, (int, float)) else list(scale), "color": color}
    d.update(kw)
    return d


def bean(at, color="#ff8fab", expr="smile", act="idle", ry=0, hat=None, hat_color=None, size=1.0, seed=1, talk=(), color2=None, anim=()):
    """A googly-eyed jelly-bean person. ry=0 faces +z (toward you). talk=[(start, dur)] moves the mouth."""
    o = O("bean", at, 1, color, expr=expr, act=act, rotate=[0, ry, 0], size=size, seed=seed, talk=[list(t) for t in talk], animate=list(anim))
    if hat:
        o["hat"] = hat
    if hat_color:
        o["hatColor"] = hat_color
    if color2:
        o["color2"] = color2
    return o


def crowd(n, seed, at=(0, 0, -8), spread=(12, 0, 6), act="idle", ry=0, color="#ffa8a8"):
    """Many beans (random colours per bean are not supported; use 2-3 crowds of different colours)."""
    return O("bean", at, 1, color, count=min(n, 60), seed=seed, spread=list(spread), act=act, rotate=[0, ry, 0], expr="smile")


def guy(at, top=None, pants=None, act="idle", face="smile", seed=1, ry=0, anim=(), look=""):
    return bean(at, top or "#74c0fc", expr=face, act=act, ry=ry, seed=seed, hat="bun" if look == "elder" else None, anim=anim)


def _r(seed):
    return random.Random(seed * 104729 + 7)


def _pair(kind, at, dx, scale, color, **kw):
    """Two mirrored copies (eyes, ears, wheels): count/spread scatter randomly, so pairs are placed explicitly."""
    x, y, z = at
    return [O(kind, (x - dx, y, z), scale, color, **kw), O(kind, (x + dx, y, z), scale, color, **kw)]


def _quad(kind, at, dx, dz, scale, color, **kw):
    x, y, z = at
    return [O(kind, (x + sx * dx, y, z + sz * dz), scale, color, **kw) for sx in (-1, 1) for sz in (-1, 1)]


def _f(face_you):
    return 1 if face_you else -1


# ───────────────────────── animals ─────────────────────────

def quadruped(at, body="#8a8f98", belly=None, size=1.0, face_you=True, ears="point", tail="bushy", eye="#ffd43b",
              snout=0.22, legs=0.36, neck=0.0, anim=(), belly2=None, tongue=False):
    """Generic four-legged block animal [9-10]. Wolf, dog, fox, cat, bear, deer, lion all come from this."""
    x, y, z = at
    s, f = size, _f(face_you)
    bl = body
    o = [O("box", (x, y + (legs + 0.22) * s, z), [0.46 * s, 0.42 * s, 1.0 * s], bl, animate=list(anim)),          # torso
         O("box", (x, y + (legs + 0.42 + neck) * s, z + f * 0.6 * s), [0.4 * s, 0.38 * s, 0.4 * s], bl, animate=list(anim)),  # head
         O("box", (x, y + (legs + 0.34 + neck) * s, z + f * (0.8 + snout / 2) * s), [0.22 * s, 0.18 * s, snout * s], belly or bl),  # snout
         O("sphere", (x, y + (legs + 0.41 + neck) * s, z + f * (0.8 + snout) * s), [0.05 * s, 0.04 * s, 0.035 * s], "#1b1b1f", material="glossy"),  # nose
         O("box", (x - 0.18 * s, y + legs / 2 * s, z + f * 0.34 * s), [0.12 * s, legs * s, 0.12 * s], bl),
         O("box", (x + 0.18 * s, y + legs / 2 * s, z + f * 0.34 * s), [0.12 * s, legs * s, 0.12 * s], bl),
         O("box", (x, y + legs / 2 * s, z - f * 0.36 * s), [0.48 * s, legs * s, 0.12 * s], bl),                        # back legs (one block)
         ]
    o += _pair("sphere", (x, y + (legs + 0.5 + neck) * s, z + f * 0.8 * s), 0.1 * s, 0.07 * s, "#ffffff", material="glossy")
    o += _pair("sphere", (x, y + (legs + 0.5 + neck) * s, z + f * 0.86 * s), 0.1 * s, 0.035 * s, "#111111", material="glossy",
               animate=[{"type": "orbit", "speed": 3, "amount": 0.012 * s}])
    if ears == "point":
        o += _pair("cone", (x, y + (legs + 0.7 + neck) * s, z + f * 0.55 * s), 0.13 * s, [0.1 * s, 0.2 * s, 0.1 * s], bl)
    elif ears == "flop":
        o += [O("box", (x + sx * 0.23 * s, y + (legs + 0.4 + neck) * s, z + f * 0.58 * s), [0.07 * s, 0.26 * s, 0.16 * s], belly2 or bl,
                rotate=[0, 0, sx * 12], animate=[{"type": "wobble", "speed": 2.5, "amount": 0.12}]) for sx in (-1, 1)]
    elif ears == "round":
        o += _pair("sphere", (x, y + (legs + 0.64 + neck) * s, z + f * 0.55 * s), 0.17 * s, 0.08 * s, bl)
    elif ears == "antlers":
        o += _pair("cylinder", (x, y + (legs + 0.85 + neck) * s, z + f * 0.5 * s), 0.14 * s, [0.04 * s, 0.4 * s, 0.04 * s], "#c8a97e", rotate=[0, 0, 0])
        o += [O("cylinder", (x + sx * 0.24 * s, y + (legs + 0.95 + neck) * s, z + f * 0.5 * s), [0.03 * s, 0.25 * s, 0.03 * s], "#c8a97e",
                rotate=[0, 0, -sx * 50]) for sx in (-1, 1)]
    if tongue:
        o.append(O("box", (x, y + (legs + 0.27 + neck) * s, z + f * (0.78 + snout) * s), [0.08 * s, 0.03 * s, 0.1 * s], "#ff6b8b",
                   rotate=[f * 25, 0, 0], animate=[{"type": "wobble", "axis": "x", "speed": 3, "amount": 0.15}]))
    if tail == "bushy":
        o.append(O("cone", (x, y + (legs + 0.3) * s, z - f * 0.66 * s), [0.14 * s, 0.4 * s, 0.14 * s], belly or bl,
                   rotate=[f * -120, 0, 0], animate=[{"type": "wobble", "speed": 2.0, "axis": "y", "amount": 0.3}]))
    elif tail == "thin":
        o.append(O("box", (x, y + (legs + 0.45) * s, z - f * 0.65 * s), [0.05 * s, 0.05 * s, 0.4 * s], bl, rotate=[f * 35, 0, 0]))
    return o


def wolf(at, color="#7d838c", face_you=True, size=1.0, eye="#ffd43b"):
    """[10] Gray wolf with glowing gold eyes."""
    return quadruped(at, color, "#c9ced6", size, face_you, "point", "bushy", eye, snout=0.26)


def dog(at, color="#c08a4e", face_you=True, size=0.8):
    """[10] Friendly dog (round ears, wagging tail)."""
    return quadruped(at, color, "#f3e0c6", size, face_you, "flop", "bushy", "#2b2b2b", snout=0.16, legs=0.3, belly2="#8a5a2b", tongue=True)


def cat(at, color="#f08c3c", face_you=True, size=0.55):
    """[10] Cat (pointy ears, thin tail, green eyes)."""
    return quadruped(at, color, "#fff0dc", size, face_you, "point", "thin", "#8ce99a", snout=0.1, legs=0.3)


def bear(at, color="#5b3a26", face_you=True, size=1.6):
    """[10] Bear: big, round ears."""
    return quadruped(at, color, "#8a5a3c", size, face_you, "round", "none", "#111111", snout=0.18, legs=0.4)


def deer(at, color="#a8743f", face_you=True, size=1.1):
    """[10] Deer with antlers."""
    return quadruped(at, color, "#f3e2c8", size, face_you, "antlers", "thin", "#111111", snout=0.18, legs=0.6, neck=0.25)


def lion(at, face_you=True, size=1.3):
    """[11] Lion with a mane."""
    f = _f(face_you)
    x, y, z = at
    return quadruped(at, "#d9a441", "#f2d08a", size, face_you, "round", "thin", "#3b2a10", snout=0.2) + [
        O("box", (x, y + 0.82 * size, z + f * 0.55 * size), [0.62 * size, 0.6 * size, 0.3 * size], "#8a4b14")]


def bird(at, color="#4dabf7", size=0.3, flying=True, seed=1, count=1, spread=(0, 0, 0)):
    """[3] Small bird (body + two wings); count>1 makes a flock."""
    x, y, z = at
    a = [{"type": "bob", "amount": 0.15, "speed": 2.0}] if flying else []
    kw = dict(count=count, seed=seed, spread=list(spread)) if count > 1 else {}
    return [O("capsule", (x, y, z), [0.3 * size, 0.3 * size, 0.6 * size], color, rotate=[90, 0, 0], animate=a, **kw),
            O("box", (x, y + 0.05 * size, z), [1.4 * size, 0.04 * size, 0.35 * size], color, animate=a +
              ([{"type": "wobble", "axis": "z", "speed": 8, "amount": 0.5}] if flying else []), **kw),
            O("cone", (x, y, z + 0.38 * size), [0.08 * size, 0.18 * size, 0.08 * size], "#ffa94d", rotate=[90, 0, 0], **kw)]


def fish(at, color="#ff922b", size=0.4, count=1, seed=1, spread=(0, 0, 0)):
    """[2] Fish (body + tail); count>1 = a school."""
    x, y, z = at
    kw = dict(count=count, seed=seed, spread=list(spread)) if count > 1 else {}
    a = [{"type": "bob", "amount": 0.1, "speed": 1.2}]
    return [O("capsule", (x, y, z), [0.3 * size, 0.4 * size, 0.8 * size], color, rotate=[0, 90, 90], animate=a, **kw),
            O("cone", (x - 0.5 * size, y, z), [0.25 * size, 0.3 * size, 0.1 * size], color, rotate=[0, 0, 90], animate=a, **kw)]


def shark(at, size=2.0, face_you=False):
    """[3] Shark: long gray body, dorsal fin, tail."""
    x, y, z = at
    f = _f(face_you)
    return [O("capsule", (x, y, z), [0.5 * size, 1.6 * size, 0.5 * size], "#6c7a89", rotate=[90, 0, 0], animate=[{"type": "bob", "amount": 0.1}]),
            O("cone", (x, y + 0.35 * size, z), [0.1 * size, 0.4 * size, 0.3 * size], "#5b6876"),
            O("cone", (x, y, z - f * 0.9 * size), [0.1 * size, 0.5 * size, 0.4 * size], "#5b6876", rotate=[90, 0, 0])]


def dino(at, color="#5c940d", size=2.2, face_you=True):
    """[8] T-rex: big head, tiny arms, thick tail."""
    x, y, z = at
    s, f = size, _f(face_you)
    return [O("box", (x, y + 1.3 * s, z), [0.7 * s, 0.8 * s, 1.2 * s], color, rotate=[f * -20, 0, 0], animate=[{"type": "bob", "amount": 0.05}]),
            O("box", (x, y + 2.0 * s, z + f * 0.7 * s), [0.6 * s, 0.55 * s, 0.85 * s], color),
            O("box", (x, y + 1.78 * s, z + f * 1.05 * s), [0.56 * s, 0.08 * s, 0.4 * s], "#f8f9fa"),                    # teeth row
            *_pair("sphere", (x, y + 2.2 * s, z + f * 1.12 * s), 0.2 * s, 0.11 * s, "#ffffff", material="glossy"),
            *_pair("sphere", (x, y + 2.2 * s, z + f * 1.21 * s), 0.2 * s, 0.05 * s, "#111111", material="glossy"),
            O("box", (x, y + 1.95 * s, z + f * 1.13 * s), [0.4 * s, 0.1 * s, 0.03 * s], "#5c1a1a"),
            O("box", (x, y + 1.2 * s, z + f * 0.6 * s), [0.5 * s, 0.08 * s, 0.25 * s], color),                           # tiny arms
            O("box", (x, y + 0.45 * s, z), [0.7 * s, 0.9 * s, 0.3 * s], color),
            O("cone", (x, y + 1.0 * s, z - f * 1.3 * s), [0.35 * s, 1.6 * s, 0.35 * s], color, rotate=[f * -100, 0, 0])]


def animate_all(objs, anim):
    """Give every part of a composite the same animation(s). For moves use RELATIVE offsets: {"type": "move", "to": [dx, dy, dz], "rel": True}
    (an absolute "to" would pull every part to one point)."""
    for o in objs:
        o["animate"] = list(o.get("animate", [])) + list(anim)
    return objs


def sauropod(at, color="#74b816", size=1.0, face_you=True, riders=0, seed=1):
    """[9+] Long-neck dinosaur (doubles as a school bus: riders=N beans sit on its back)."""
    x, y, z = at
    s, f = size, _f(face_you)
    o = [O("capsule", (x, y + 1.9 * s, z), [1.6 * s, 2.2 * s, 1.5 * s], color, rotate=[90, 0, 0]),
         O("capsule", (x, y + 3.3 * s, z + f * 1.6 * s), [0.45 * s, 2.4 * s, 0.45 * s], color, rotate=[f * 35, 0, 0]),
         O("sphere", (x, y + 4.4 * s, z + f * 2.35 * s), [0.4 * s, 0.32 * s, 0.5 * s], color),
         O("cone", (x, y + 1.9 * s, z - f * 2.2 * s), [0.5 * s, 2.4 * s, 0.5 * s], color, rotate=[f * -100, 0, 0],
           animate=[{"type": "wobble", "axis": "y", "speed": 0.8, "amount": 0.15}])]
    o += _quad("cylinder", (x, y + 0.6 * s, z), 0.55 * s, 0.75 * s, [0.42 * s, 1.2 * s, 0.42 * s], color)
    o += _pair("sphere", (x, y + 4.5 * s, z + f * 2.62 * s), 0.16 * s, 0.09 * s, "#ffffff", material="glossy")
    o += _pair("sphere", (x, y + 4.5 * s, z + f * 2.7 * s), 0.16 * s, 0.045 * s, "#111111", material="glossy")
    o.append(O("sphere", (x, y + 2.6 * s, z), 0.12 * s, "#ffd43b", count=5, seed=seed, spread=[1.0 * s, 0, 2.0 * s]))   # spots
    if riders:
        o.append(O("bean", (x, y + 2.75 * s, z), 1, "#ffa8a8", count=riders, seed=seed + 3, spread=[0.6 * s, 0, 2.0 * s],
                   act="cheer", rotate=[0, 0 if face_you else 180, 0], size=0.55))
    return o


def pterodactyl(at, color="#e8590c", size=1.0, face_you=True, flying=True):
    """[7] Pterodactyl: crested head, long beak, flapping leather wings."""
    x, y, z = at
    s, f = size, _f(face_you)
    a = [{"type": "bob", "amount": 0.25, "speed": 1.2}] if flying else []
    flap = [{"type": "wobble", "axis": "z", "speed": 3.5, "amount": 0.45}] if flying else []
    return [O("capsule", (x, y, z), [0.35 * s, 0.6 * s, 0.35 * s], color, rotate=[90, 0, 0], animate=a),
            O("sphere", (x, y + 0.25 * s, z + f * 0.45 * s), 0.18 * s, color, animate=a),
            O("cone", (x, y + 0.22 * s, z + f * 0.8 * s), [0.12 * s, 0.6 * s, 0.12 * s], "#ffd43b", rotate=[f * 90, 0, 0], animate=a),
            O("cone", (x, y + 0.42 * s, z + f * 0.3 * s), [0.08 * s, 0.4 * s, 0.08 * s], color, rotate=[f * -60, 0, 0], animate=a),
            O("box", (x - 0.75 * s, y + 0.05 * s, z), [1.3 * s, 0.03 * s, 0.6 * s], "#ff922b", rotate=[0, 0, 8], animate=a + flap),
            O("box", (x + 0.75 * s, y + 0.05 * s, z), [1.3 * s, 0.03 * s, 0.6 * s], "#ff922b", rotate=[0, 0, -8], animate=a + flap)] + \
        _pair("sphere", (x, y + 0.33 * s, z + f * 0.58 * s), 0.09 * s, 0.05 * s, "#ffffff", material="glossy", animate=a)


def robot(at, color="#ced4da", eye="#4dabf7", size=1.0, face_you=True):
    """[6] Friendly robot: box body, screen face, antenna."""
    x, y, z = at
    s, f = size, _f(face_you)
    return [O("box", (x, y + 0.7 * s, z), [0.7 * s, 0.9 * s, 0.5 * s], color, material="metal"),
            O("box", (x, y + 1.45 * s, z), [0.6 * s, 0.5 * s, 0.5 * s], color, material="metal", animate=[{"type": "bob", "amount": 0.03}]),
            O("plane", (x, y + 1.45 * s, z + f * 0.26 * s), [0.48 * s, 0.34 * s, 1], "#101418", material="glow", rotate=[0, 0 if face_you else 180, 0]),
            *_pair("sphere", (x, y + 1.5 * s, z + f * 0.27 * s), 0.12 * s, 0.05 * s, eye, material="glow"),
            O("cylinder", (x, y + 1.85 * s, z), [0.03 * s, 0.3 * s, 0.03 * s], "#868e96"),
            O("sphere", (x, y + 2.02 * s, z), 0.06 * s, "#ff6b6b", material="glow", animate=[{"type": "pulse", "amount": 0.5}])]


def alien(at, color="#69db7c", size=1.0, face_you=True):
    """[5] Little green alien: big head, huge black eyes, antennae."""
    x, y, z = at
    s, f = size, _f(face_you)
    return [O("capsule", (x, y + 0.5 * s, z), [0.35 * s, 0.7 * s, 0.3 * s], color),
            O("sphere", (x, y + 1.15 * s, z), 0.38 * s, color, animate=[{"type": "bob", "amount": 0.03}]),
            *_pair("sphere", (x, y + 1.18 * s, z + f * 0.3 * s), 0.15 * s, 0.11 * s, "#0b0b0f", material="glossy"),
            *_pair("cylinder", (x, y + 1.6 * s, z), 0.15 * s, [0.02 * s, 0.3 * s, 0.02 * s], color),
            *_pair("sphere", (x, y + 1.76 * s, z), 0.15 * s, 0.05 * s, "#d0bfff", material="glow")]


def ghost(at, size=1.0):
    """[3] Floating sheet ghost."""
    x, y, z = at
    return [O("capsule", (x, y + 1.2 * size, z), [0.6 * size, 1.1 * size, 0.6 * size], "#f1f3f5", material="glow",
              animate=[{"type": "bob", "amount": 0.15, "speed": 0.8}]),
            *_pair("sphere", (x, y + 1.5 * size, z + 0.29 * size), 0.11 * size, 0.06 * size, "#111"),
            O("sphere", (x, y + 1.32 * size, z + 0.3 * size), 0.07 * size, "#111")]


# ───────────────────────── food & props ─────────────────────────

def pizza(at, size=0.4):
    """[3] Pizza on a plate with pepperoni."""
    x, y, z = at
    return [O("cylinder", (x, y, z), [size, 0.02, size], "#f8f9fa"), O("cylinder", (x, y + 0.02, z), [size * 0.85, 0.03, size * 0.85], "#f2a541"),
            O("cylinder", (x, y + 0.04, z), [size * 0.12, 0.01, size * 0.12], "#c92a2a", count=7, seed=3, spread=[size * 1.1, 0, size * 1.1])]


def burger(at, size=0.25):
    """[5] Stacked burger."""
    x, y, z = at
    st = [("#e0a458", 0.08), ("#2f9e44", 0.03), ("#c92a2a", 0.03), ("#5c3a21", 0.07), ("#e0a458", 0.1)]
    out, h = [], y
    for c, t in st:
        out.append(O("cylinder", (x, h + t * size * 4 / 2, z), [size, t * size * 4, size], c))
        h += t * size * 4
    return out


def cake(at, candles=5, size=0.35):
    """[4] Birthday cake with lit candles."""
    x, y, z = at
    return [O("cylinder", (x, y + 0.12 * size * 3, z), [size, 0.24 * size * 3, size], "#ffdeeb"),
            O("cylinder", (x, y + 0.26 * size * 3, z), [size * 1.02, 0.04 * size * 3, size * 1.02], "#f783ac"),
            O("cylinder", (x, y + 0.36 * size * 3, z), [0.015, 0.12, 0.015], "#4dabf7", count=candles, seed=2, spread=[size, 0, size]),
            O("flame", (x, y + 0.46 * size * 3, z), 0.05, "#ffd43b", count=candles, seed=2, spread=[size, 0, size])]


def coffee(at, color="#f8f9fa"):
    """[2] Mug with steam."""
    x, y, z = at
    return [O("cylinder", (x, y + 0.06, z), [0.06, 0.12, 0.06], color),
            O("particles", (x, y + 0.2, z), 0.01, "#ffffff", count=10, seed=1, spread=[0.05, 0.15, 0.05])]


def phone(at, screen="#74c0fc", rot=(-70, 0, 0)):
    """[2] Phone lying or held, glowing screen."""
    x, y, z = at
    return [O("box", (x, y, z), [0.08, 0.16, 0.01], "#212529", rotate=list(rot)),
            O("plane", (x, y + 0.006, z), [0.07, 0.14, 1], screen, material="glow", rotate=list(rot), animate=[{"type": "pulse", "amount": 0.2}])]


def money(at, count=30, spread=(2, 0.02, 2), seed=1):
    """[1] Scattered dollar bills."""
    return [O("box", at, [0.16, 0.005, 0.07], "#69a85c", count=count, seed=seed, spread=list(spread))]


def money_rain(at=(0, 3, -2), count=80, seed=2):
    """[1] Bills falling from the sky."""
    return [O("box", at, [0.16, 0.005, 0.07], "#69a85c", count=count, seed=seed, spread=[6, 3, 4],
              animate=[{"type": "move", "to": [at[0], -0.5, at[2]]}, {"type": "spin", "speed": 2}])]


def gold_bars(at, count=12, seed=1):
    """[1] Pile of gold bars."""
    return [O("box", at, [0.25, 0.08, 0.12], "#ffd43b", material="metal", count=count, seed=seed, spread=[0.8, 0.3, 0.6])]


def trophy(at, size=0.4):
    """[3] Gold trophy."""
    x, y, z = at
    return [O("box", (x, y + 0.05 * size, z), [0.3 * size, 0.1 * size, 0.3 * size], "#343a40"),
            O("cylinder", (x, y + 0.3 * size, z), [0.05 * size, 0.4 * size, 0.05 * size], "#fcc419", material="metal"),
            O("cone", (x, y + 0.75 * size, z), [0.25 * size, 0.5 * size, 0.25 * size], "#fcc419", material="metal", rotate=[180, 0, 0])]


def gift(at, color="#e64980", ribbon="#ffd43b", size=0.4):
    """[3] Wrapped present."""
    x, y, z = at
    return [O("box", (x, y + size / 2, z), [size, size, size], color),
            O("box", (x, y + size / 2, z), [size * 1.02, size * 1.02, size * 0.15], ribbon),
            O("box", (x, y + size / 2, z), [size * 0.15, size * 1.02, size * 1.02], ribbon)]


def crown(at, size=0.3):
    """[2] Gold crown with gems."""
    x, y, z = at
    return [O("cylinder", (x, y, z), [size, size * 0.5, size], "#fcc419", material="metal"),
            O("sphere", (x, y + 0.05, z + size * 0.9), 0.03, "#e03131", material="glow", count=3, seed=2, spread=[size, 0, 0])]


def tv(at, screen="#4dabf7", size=1.0, rot=0):
    """[3] TV on a stand, glowing screen (news broadcast look)."""
    x, y, z = at
    return [O("box", (x, y + 1.0 * size, z), [1.6 * size, 0.95 * size, 0.08], "#111", rotate=[0, rot, 0]),
            O("plane", (x, y + 1.0 * size, z + 0.05), [1.5 * size, 0.85 * size, 1], screen, material="glow", rotate=[0, rot, 0],
              animate=[{"type": "pulse", "amount": 0.15}]),
            O("box", (x, y + 0.3 * size, z), [1.2 * size, 0.6 * size, 0.4 * size], "#5c3d2e")]


def car(at, color="#1c7ed6", rot=0, moving=False, seed=1):
    """[5] Block car with wheels and headlights."""
    x, y, z = at
    a = [{"type": "move", "to": [x, y, z + 20]}] if moving else []
    return [O("box", (x, y + 0.55, z), [1.8, 0.6, 4.0], color, material="glossy", rotate=[0, rot, 0], animate=a),
            O("box", (x, y + 1.05, z - 0.2), [1.6, 0.5, 2.0], "#a5d8ff", material="glossy", rotate=[0, rot, 0], animate=a),
            *_quad("cylinder", (x, y + 0.3, z), 0.9, 1.3, [0.32, 0.25, 0.32], "#212529", rotate=[0, 0, 90], animate=a),
            *_pair("sphere", (x, y + 0.6, z + 2.0), 0.65, 0.1, "#fff3bf", material="glow", animate=a),
            *_pair("sphere", (x, y + 0.6, z - 2.0), 0.65, 0.09, "#ff6b6b", material="glow", animate=a)]


def bus(at, color="#fab005", rot=0):
    """[4] School bus."""
    x, y, z = at
    return [O("box", (x, y + 1.2, z), [2.4, 2.0, 9.0], color, rotate=[0, rot, 0]),
            O("plane", (x + 1.21, y + 1.6, z), [7.0, 0.6, 1], "#a5d8ff", material="glossy", rotate=[0, 90, 0]),
            *_quad("cylinder", (x, y + 0.4, z), 1.2, 3.0, [0.45, 0.3, 0.45], "#212529", rotate=[0, 0, 90]),
            *_pair("sphere", (x, y + 0.8, z + 4.5), 0.9, 0.14, "#fff3bf", material="glow")]


def rocket(at, size=1.0, launching=False):
    """[5] Rocket with fins and exhaust flame."""
    x, y, z = at
    s = size
    a = [{"type": "move", "to": [x, y + 40, z]}] if launching else []
    return [O("cylinder", (x, y + 3 * s, z), [0.7 * s, 5 * s, 0.7 * s], "#f1f3f5", animate=a),
            O("cone", (x, y + 6.2 * s, z), [0.7 * s, 1.4 * s, 0.7 * s], "#e03131", animate=a),
            O("cone", (x, y + 0.8 * s, z), [0.3 * s, 1.0 * s, 0.1 * s], "#e03131", count=3, seed=2, spread=[1.4 * s, 0, 1.4 * s], animate=a),
            O("flame", (x, y + 0.1, z), 1.0 * s, "#ff922b", animate=a),
            O("particles", (x, y, z), 0.2, "#dee2e6", count=40, seed=3, spread=[4, 1, 4])]


def ufo(at, size=1.0, beam=True):
    """[4] Flying saucer with a tractor beam."""
    x, y, z = at
    s = size
    o = [O("cylinder", (x, y, z), [2.2 * s, 0.25 * s, 2.2 * s], "#adb5bd", material="metal", animate=[{"type": "spin", "speed": 0.5}, {"type": "bob", "amount": 0.2}]),
         O("sphere", (x, y + 0.25 * s, z), 0.7 * s, "#99e9f2", material="glossy"),
         O("sphere", (x, y - 0.05, z), 0.1 * s, "#ffe066", material="glow", count=8, seed=4, spread=[3.6 * s, 0, 3.6 * s])]
    if beam:
        o.append(O("cone", (x, y - 2.5 * s, z), [1.4 * s, 5 * s, 1.4 * s], "#c3fae8", material="glow", animate=[{"type": "pulse", "amount": 0.3}]))
    return o


def balloon_cluster(at, count=10, seed=1):
    """[2] Bunch of party balloons on strings."""
    return [O("sphere", at, 0.18, "#ff6b6b", material="glossy", count=count, seed=seed, spread=[1.0, 0.6, 0.5],
              animate=[{"type": "bob", "amount": 0.08, "speed": 0.7}]),
            O("cylinder", (at[0], at[1] - 0.6, at[2]), [0.005, 1.0, 0.005], "#f8f9fa", count=count, seed=seed, spread=[1.0, 0, 0.5])]


def confetti(at=(0, 2.5, -2), count=120, seed=7):
    """[1] Falling confetti."""
    return [O("box", at, [0.04, 0.005, 0.04], "#f783ac", count=count, seed=seed, spread=[5, 2.5, 4],
              animate=[{"type": "move", "to": [at[0], 0, at[2]]}, {"type": "spin", "speed": 3}])]


def fire_pit(at, size=0.6):
    """[3] Campfire: logs, flame, sparks."""
    x, y, z = at
    return [O("cylinder", (x, y + 0.08, z), [0.08, 0.7 * size, 0.08], "#5c3d2e", rotate=[90, 0, 0], count=3, seed=3, spread=[0.3, 0, 0.3]),
            O("flame", (x, y + 0.1, z), size, "#ff922b"),
            O("particles", (x, y + 0.8, z), 0.02, "#ffd43b", count=30, seed=2, spread=[0.5, 1.2, 0.5])]


def full_moon(at=(10, 14, -60), size=3.0):
    """[2] Big glowing moon with a halo."""
    return [O("sphere", at, size, "#fff8e1", material="glow"),
            O("sphere", at, size * 1.5, "#fff3bf", material="glow", opacity=0.12)]


def stars_field(count=120, seed=3):
    """[1] Extra stars (for skies where stars=True isn't enough)."""
    return [O("sphere", (0, 30, -80), 0.08, "#ffffff", material="glow", count=count, seed=seed, spread=[160, 40, 20])]


def snow(count=160, seed=4):
    """[1] Falling snow."""
    return [O("particles", (0, 3, -4), 0.02, "#ffffff", count=count, seed=seed, spread=[10, 4, 10])]


def rain(count=180, seed=5):
    """[1] Rain streaks."""
    return [O("box", (0, 4, -4), [0.01, 0.3, 0.01], "#a5d8ff", count=count, seed=seed, spread=[10, 4, 10],
              animate=[{"type": "move", "to": [0, -0.5, -4]}])]


def fireflies(count=30, seed=6, at=(0, 1.2, -6)):
    """[1] Floating glow dots."""
    return [O("sphere", at, 0.03, "#d8f5a2", material="glow", count=count, seed=seed, spread=[10, 2, 8], animate=[{"type": "bob", "amount": 0.2}])]


def portal(at, color="#9775fa", size=1.4):
    """[3] Swirling portal."""
    x, y, z = at
    return [O("torus", (x, y, z), [size, size, 0.2], color, material="glow", animate=[{"type": "spin", "axis": "z", "speed": 1.5}]),
            O("plane", (x, y, z), [size * 1.6, size * 1.6, 1], "#e5dbff", material="glow", animate=[{"type": "pulse", "amount": 0.4}]),
            O("particles", (x, y, z), 0.03, "#d0bfff", count=40, seed=8, spread=[size * 2, size * 2, 0.5])]


def sign(at, color="#2b8a3e", text_color="#f8f9fa", w=1.6, h=0.6, rot=0):
    """[3] Road / shop sign on a pole (no readable text; the caption carries words)."""
    x, y, z = at
    return [O("cylinder", (x, y + 1.2, z), [0.05, 2.4, 0.05], "#495057"),
            O("box", (x, y + 2.6, z), [w, h, 0.05], color, rotate=[0, rot, 0]),
            O("box", (x, y + 2.6, z + 0.03), [w * 0.7, h * 0.15, 0.01], text_color, rotate=[0, rot, 0])]


def desk_row(at=(0, 0, -3), rows=3, cols=3, color="#d9b98c", seed=1):
    """[2] School desks in a grid."""
    return [O("box", (at[0], 0.38, at[2]), [0.9, 0.06, 0.6], color, count=rows * cols, seed=seed, spread=[cols * 1.5, 0, rows * 1.3]),
            O("box", (at[0], 0.2, at[2]), [0.06, 0.4, 0.06], "#495057", count=rows * cols, seed=seed, spread=[cols * 1.5, 0, rows * 1.3])]


# ───────────────────────── places (full sets) ─────────────────────────

def forest(seed=1, ground="#3b5e3a", trees=14, night=True, extra=()):
    """[5+] Pine forest floor with rocks, trees and fireflies at night."""
    o = [O("box", (0, -0.03, -20), [140, 0.04, 140], ground),
         O("tree", (0, 0, -16), 2.6, "#2b4a33", count=trees, seed=seed, spread=[36, 0, 26]),
         O("tree", (0, 0, -45), 3.4, "#1f3b2c", count=trees, seed=seed + 1, spread=[90, 0, 20]),
         O("rock", (0, 0.1, -6), 0.5, "#6b6f63", count=5, seed=seed + 2, spread=[10, 0, 6])]
    if night:
        o += fireflies(seed=seed + 3)
    return o + list(extra)


def den(seed=1, extra=()):
    """[5+] Rocky cave mouth / wolf den (you look out from inside)."""
    return [O("box", (0, -0.03, -4), [20, 0.04, 20], "#4a3f35"),
            O("rock", (-2.4, 0.8, -2), 1.8, "#5a5048"), O("rock", (2.5, 0.9, -2.2), 2.0, "#544a42"),
            O("box", (0, 3.0, -1.5), [8, 0.6, 5], "#463d36"),
            O("particles", (0, 0.05, -2), 0.04, "#d8c9a8", count=20, seed=seed, spread=[3, 0, 3])] + list(extra)


def classroom(seed=1, wall="#e7dcc6", board="#2f4f3a", kids=6, extra=()):
    """[8+] Classroom: board, desks, kids facing the board (−z)."""
    o = [O("box", (0, -0.02, -3), [9, 0.04, 9], "#b08a63"), O("box", (0, 1.5, -6.5), [9, 3, 0.1], wall),
         O("box", (-4.5, 1.5, -3), [0.1, 3, 9], wall), O("box", (0, 1.6, -6.4), [3.6, 1.3, 0.05], board),
         O("box", (3.6, 1.7, -6.4), [1.4, 1.0, 0.05], "#a5d8ff", material="glow")] + desk_row((0, 0, -2.8), seed=seed)
    if kids:
        o.append(crowd(kids, seed + 3, at=(0, 0, -2.6), spread=(4.5, 0, 3.2), act="sit", ry=180))
    return o + list(extra)


def cafeteria(seed=1, extra=()):
    """[6+] School cafeteria: long tables, trays, kids eating."""
    return [O("box", (0, -0.02, -4), [12, 0.04, 12], "#d0d4d8"), O("box", (0, 1.6, -9), [12, 3.2, 0.1], "#f1e3c8"),
            O("box", (0, 0.4, -2.5), [3.6, 0.08, 0.9], "#e9ecef", count=3, seed=seed, spread=[0, 0, 6]),
            O("box", (0, 0.46, -2.5), [0.4, 0.03, 0.3], "#74c0fc", count=9, seed=seed + 1, spread=[3, 0, 6]),
            crowd(10, seed + 2, at=(0, 0, -3.5), spread=(4, 0, 6), act="sit", ry=0),
            O("plane", (0, 3.1, -4), [1.4, 0.5, 1], "#ffffff", material="glow", rotate=[90, 0, 0], count=4, seed=seed, spread=[8, 0, 8])] + list(extra)


def kitchen(seed=1, wall="#f4ede0", extra=()):
    """[7+] Home kitchen: counters, fridge, stove glow, table."""
    return [O("box", (0, -0.02, -2), [8, 0.04, 8], "#c8b597"), O("box", (0, 1.5, -4.5), [8, 3, 0.1], wall),
            O("box", (-1.5, 0.45, -4.1), [4.0, 0.9, 0.7], "#5f7a8a"), O("box", (-1.5, 0.92, -4.1), [4.0, 0.05, 0.75], "#e9ecef"),
            O("box", (2.3, 1.0, -4.1), [1.0, 2.0, 0.8], "#e9ecef", material="glossy"),
            O("box", (0, 0.4, -1.4), [1.8, 0.06, 1.0], "#a0795a"), O("plane", (-2.5, 0.96, -4.0), [0.5, 0.5, 1], "#ff6b3d", material="glow", rotate=[-90, 0, 0])] + list(extra)


def supermarket(seed=1, extra=()):
    """[7+] Supermarket aisle running along −z, colourful shelves."""
    return [O("box", (0, -0.02, -10), [8, 0.04, 30], "#e9ecef"),
            O("box", (-1.8, 1.0, -10), [0.6, 2.0, 24], "#ced4da"), O("box", (1.8, 1.0, -10), [0.6, 2.0, 24], "#ced4da"),
            O("box", (-1.5, 1.0, -10), [0.15, 0.2, 0.15], "#ff6b6b", count=60, seed=seed, spread=[0.05, 1.6, 22]),
            O("box", (1.5, 1.0, -10), [0.15, 0.2, 0.15], "#4dabf7", count=60, seed=seed + 1, spread=[0.05, 1.6, 22]),
            O("plane", (0, 3.0, -10), [0.4, 6, 1], "#ffffff", material="glow", rotate=[90, 0, 0], count=3, seed=seed, spread=[0, 0, 20]),
            crowd(5, seed + 2, at=(0, 0, -12), spread=(1.6, 0, 14), act="walk")] + list(extra)


def plane_cabin(seed=1, night=False, empty=False, extra=()):
    """[7+] Airplane cabin aisle looking forward (−z): seat rows, windows, overhead bins."""
    o = [O("box", (0, -0.02, -8), [3.6, 0.04, 20], "#3b4a6b"),
         O("box", (-1.1, 0.55, -8), [1.0, 1.1, 0.5], "#2f3a56", count=12, seed=seed, spread=[0, 0, 16]),
         O("box", (1.1, 0.55, -8), [1.0, 1.1, 0.5], "#2f3a56", count=12, seed=seed + 1, spread=[0, 0, 16]),
         O("box", (0, 2.25, -8), [3.6, 0.1, 20], "#e9ecef"),
         O("box", (-1.4, 1.95, -8), [0.8, 0.4, 20], "#dee2e6"), O("box", (1.4, 1.95, -8), [0.8, 0.4, 20], "#dee2e6"),
         O("plane", (-1.78, 1.25, -8), [0.25, 0.35, 1], "#1b2a4a" if night else "#a5d8ff", material="glow", rotate=[0, 90, 0], count=10, seed=seed, spread=[0, 0, 16])]
    if not empty:
        o.append(crowd(14, seed + 3, at=(0, 0.3, -8), spread=(2.6, 0, 14), act="sit"))
    return o + list(extra)


def beach(seed=1, sand="#e9d3a5", sea="#1c8fb5", extra=()):
    """[6+] Beach: sand, sea with waves, palm-ish trees, sun umbrellas."""
    return [O("box", (0, -0.03, -5), [80, 0.04, 30], sand),
            O("box", (0, -0.1, -40), [200, 0.1, 50], sea, material="glossy", animate=[{"type": "bob", "amount": 0.04, "speed": 0.6}]),
            O("cylinder", (-6, 2, -10), [0.15, 4, 0.15], "#8d6e4f", count=3, seed=seed, spread=[14, 0, 6]),
            O("sphere", (-6, 4.1, -10), 1.0, "#2f9e44", count=3, seed=seed, spread=[14, 0, 6]),
            O("cone", (2, 1.8, -6), [1.2, 0.4, 1.2], "#ff6b6b", count=3, seed=seed + 1, spread=[10, 0, 4]),
            crowd(8, seed + 2, at=(0, 0, -8), spread=(18, 0, 6), act="walk")] + list(extra)


def snowfield(seed=1, extra=()):
    """[5+] Snowy mountains, pines, falling snow."""
    return [O("box", (0, -0.03, -20), [160, 0.04, 160], "#eef2f6"),
            O("cone", (0, 10, -80), [26, 22, 26], "#dfe6ee", count=4, seed=seed, spread=[160, 6, 20]),
            O("tree", (0, 0, -18), 2.4, "#2b4a3a", count=10, seed=seed + 1, spread=[40, 0, 20])] + snow(seed=seed) + list(extra)


def desert(seed=1, extra=()):
    """[4+] Dunes, cacti, heat shimmer."""
    return [O("box", (0, -0.03, -20), [200, 0.04, 200], "#e3b778"),
            O("sphere", (0, -6, -40), 12, "#d9a35f", count=5, seed=seed, spread=[120, 0, 40]),
            O("cylinder", (4, 1.2, -10), [0.3, 2.4, 0.3], "#4f8a3a", count=4, seed=seed + 1, spread=[24, 0, 16]),
            O("particles", (0, 0.3, -6), 0.02, "#fff1d6", count=40, seed=seed + 2, spread=[12, 0.6, 8])] + list(extra)


def space_station(seed=1, extra=()):
    """[7+] Inside a space station module: padded walls, screens, floating stuff."""
    return [O("cylinder", (0, 1.3, -4), [2.6, 10, 2.6], "#e9ecef", rotate=[90, 0, 0]),
            O("box", (0, 0.1, -4), [1.6, 0.05, 9], "#adb5bd"),
            O("plane", (-1.1, 1.6, -3), [0.6, 0.4, 1], "#4dabf7", material="glow", rotate=[0, 90, 0], count=4, seed=seed, spread=[0, 0.6, 6]),
            O("sphere", (0, 1.4, -3), 0.05, "#ffd43b", material="glow", count=10, seed=seed + 1, spread=[1.6, 1.2, 6]),
            O("box", (0, 1.5, -3), [0.2, 0.08, 0.14], "#ff8787", count=6, seed=seed + 2, spread=[1.4, 1.2, 5],
              animate=[{"type": "spin", "speed": 0.4}, {"type": "bob", "amount": 0.1}]),
            O("plane", (0, 1.3, -8.9), [1.4, 1.4, 1], "#0b1020", material="glow")] + list(extra)


def city_night(seed=1, extra=()):
    """[6+] Skyline at night seen from a rooftop: lit windows, a moon, a rail in front."""
    return [O("box", (0, -0.03, -2), [10, 0.04, 6], "#5c5f66"), O("box", (0, 0.5, -3.6), [10, 0.08, 0.08], "#adb5bd", material="metal"),
            O("box", (0, 10, -60), [8, 20, 8], "#1f2a44", count=14, seed=seed, spread=[140, 14, 30]),
            O("plane", (0, 10, -55), [0.6, 0.8, 1], "#ffe8a3", material="glow", count=60, seed=seed + 1, spread=[140, 18, 2]),
            ] + full_moon((18, 22, -90), 4) + list(extra)


def stadium(seed=1, extra=()):
    """[6+] Stadium: pitch, stands full of crowd, floodlights."""
    return [O("box", (0, -0.03, -14), [40, 0.04, 30], "#2f9e44"), O("box", (0, 0.0, -14), [0.2, 0.02, 30], "#f8f9fa"),
            O("box", (0, 4, -32), [60, 8, 6], "#495057", rotate=[-25, 0, 0]),
            crowd(150, seed, at=(0, 4, -31), spread=(56, 6, 3), act="cheer", ry=0),
            O("sphere", (0, 16, -30), 0.8, "#ffffff", material="glow", count=4, seed=seed + 1, spread=[56, 0, 0]),
            O("box", (0, 0.05, -4), [0.6, 0.6, 0.6], "#f8f9fa")] + list(extra)


def bedroom_kid(seed=1, wall="#a5d8ff", extra=()):
    """[7+] Kid's bedroom: bed, posters, toy shelf, night lamp."""
    return [O("box", (0, -0.02, -2), [7, 0.04, 7], "#c8a27a"), O("box", (0, 1.5, -4.8), [7, 3, 0.1], wall), O("box", (-3.5, 1.5, -2), [0.1, 3, 7], wall),
            O("box", (-2.2, 0.3, -3.4), [1.6, 0.6, 2.4], "#f783ac"), O("box", (-2.2, 0.65, -4.3), [1.5, 0.2, 0.5], "#ffffff"),
            O("plane", (1, 1.9, -4.74), [0.8, 1.1, 1], "#ffd43b", material="glow", count=3, seed=seed, spread=[3, 0.4, 0]),
            O("box", (2.6, 0.9, -4.5), [1.2, 1.8, 0.4], "#845ef7"),
            O("sphere", (2.6, 1.3, -4.3), 0.12, "#ff922b", count=6, seed=seed, spread=[1.0, 1.2, 0])] + list(extra)


def courtroom(seed=1, extra=()):
    """[6+] Courtroom: judge's bench, flags, benches."""
    return [O("box", (0, -0.02, -4), [12, 0.04, 12], "#6e4a32"), O("box", (0, 1.8, -9), [12, 3.6, 0.1], "#d8c3a5"),
            O("box", (0, 0.7, -7.5), [4.0, 1.4, 1.0], "#5c3a21"), O("box", (0, 1.5, -8.9), [1.0, 1.0, 0.05], "#fcc419", material="metal"),
            O("box", (0, 0.4, -3), [3.6, 0.8, 0.4], "#7a5236", count=3, seed=seed, spread=[0, 0, 3]),
            guy((0, 0.6, -7.9), "#212529", "#212529", act="idle", face="angry", seed=seed + 9, ry=0)] + list(extra)


def wedding(seed=1, extra=()):
    """[6+] Outdoor wedding: arch with flowers, chairs, guests."""
    return [O("box", (0, -0.03, -8), [40, 0.04, 40], "#8ac06a"),
            O("torus", (0, 1.4, -6), [1.6, 1.6, 0.15], "#f8f9fa"), O("sphere", (0, 2.2, -6), 0.14, "#f783ac", count=14, seed=seed, spread=[3, 1.6, 0.2]),
            O("box", (0, 0.25, -3), [0.4, 0.5, 0.4], "#f8f9fa", count=16, seed=seed + 1, spread=[5, 0, 3]),
            crowd(12, seed + 2, at=(0, 0, -3), spread=(5, 0, 3), act="sit", ry=180)] + list(extra)


def hospital_hall(seed=1, extra=()):
    """[5+] Long hospital corridor with ceiling lights and a gurney."""
    return [O("box", (0, -0.02, -10), [3, 0.04, 26], "#cfd8dc"), O("box", (-1.5, 1.4, -10), [0.06, 2.8, 26], "#e3f2ef"),
            O("box", (1.5, 1.4, -10), [0.06, 2.8, 26], "#e3f2ef"),
            O("plane", (0, 2.78, -10), [0.8, 0.4, 1], "#ffffff", material="glow", rotate=[90, 0, 0], count=6, seed=seed, spread=[0, 0, 22]),
            O("box", (0.8, 0.5, -5), [0.7, 0.1, 1.9], "#f8f9fa")] + list(extra)


def underwater(seed=1, extra=()):
    """[5+] Deep blue underwater: sand floor, kelp, fish school, light rays."""
    return [O("box", (0, -0.03, -10), [80, 0.04, 80], "#c9b48a"),
            O("cylinder", (0, 1.5, -8), [0.08, 3.0, 0.08], "#2b8a3e", count=10, seed=seed, spread=[14, 0, 8], animate=[{"type": "bob", "amount": 0.1}]),
            O("particles", (0, 2, -5), 0.02, "#e3fafc", count=50, seed=seed + 1, spread=[10, 4, 8])] + fish((0, 1.6, -6), count=14, seed=seed + 2, spread=(8, 2, 6)) + list(extra)


def park(seed=1, grass="#69b34c", trees=9, people=0, extra=()):
    """[6+] Sunny park: path, round trees, benches, flowers."""
    o = [O("box", (0, -0.03, -20), [120, 0.04, 120], grass), O("box", (0, 0.0, -20), [2.6, 0.02, 80], "#e9d8b4"),
         O("blob_tree", (0, 0, -14), 2.2, "#51cf66", count=trees, seed=seed, spread=[30, 0, 22]),
         O("blob_tree", (0, 0, -40), 3.2, "#2f9e44", count=trees, seed=seed + 1, spread=[80, 0, 20]),
         O("box", (2.4, 0.3, -6), [1.8, 0.12, 0.6], "#a0522d", count=3, seed=seed + 2, spread=[0, 0, 14]),
         O("sphere", (0, 0.08, -8), 0.08, "#ff8787", count=24, seed=seed + 3, spread=[12, 0, 14])]
    if people:
        o.append(crowd(people, seed + 4, at=(0, 0, -12), spread=(14, 0, 12), act="walk", color="#a5d8ff"))
    return o + list(extra)


ALL_ANIMALS = [wolf, dog, cat, bear, deer, lion, bird, fish, shark, dino, sauropod, pterodactyl, robot, alien, ghost]
ALL_PROPS = [pizza, burger, cake, coffee, phone, money, money_rain, gold_bars, trophy, gift, crown, tv, car, bus, rocket, ufo,
             balloon_cluster, confetti, fire_pit, full_moon, stars_field, snow, rain, fireflies, portal, sign, desk_row]
ALL_PLACES = [forest, den, classroom, cafeteria, kitchen, supermarket, plane_cabin, beach, snowfield, desert, space_station,
              city_night, stadium, park, bedroom_kid, courtroom, wedding, hospital_hall, underwater]
