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


def big_bird(at, color="#4dabf7", belly="#e7f5ff", size=1.0, face_you=True, beak="#ffa94d", crest=None, anim=()):
    """[12] Standing cartoon bird (pigeon/robin/sparrow sized up): round body, googly eyes on the front of the head, beak, flapping wings, orange legs."""
    x, y, z = at
    s, f = size, _f(face_you)
    a = list(anim)
    o = [O("sphere", (x, y + 0.55 * s, z), [0.42 * s, 0.45 * s, 0.4 * s], color, animate=a),
         O("sphere", (x, y + 0.5 * s, z + f * 0.2 * s), [0.3 * s, 0.32 * s, 0.24 * s], belly, animate=a),
         O("sphere", (x, y + 1.08 * s, z + f * 0.04 * s), 0.28 * s, color, animate=a),
         O("cone", (x, y + 1.02 * s, z + f * 0.36 * s), [0.11 * s, 0.24 * s, 0.11 * s], beak, rotate=[f * 90, 0, 0], animate=a),
         O("box", (x - 0.42 * s, y + 0.6 * s, z), [0.08 * s, 0.4 * s, 0.32 * s], color, rotate=[0, 0, 18], animate=a + [{"type": "wobble", "axis": "z", "speed": 4, "amount": 0.25}]),
         O("box", (x + 0.42 * s, y + 0.6 * s, z), [0.08 * s, 0.4 * s, 0.32 * s], color, rotate=[0, 0, -18], animate=a + [{"type": "wobble", "axis": "z", "speed": 4, "amount": 0.25}]),
         O("cone", (x, y + 0.5 * s, z - f * 0.42 * s), [0.3 * s, 0.3 * s, 0.08 * s], color, rotate=[f * -70, 0, 0])]
    o += _pair("cylinder", (x, y + 0.08 * s, z), 0.14 * s, [0.04 * s, 0.18 * s, 0.04 * s], beak)
    o += _pair("box", (x, y + 0.01 * s, z + f * 0.05 * s), 0.14 * s, [0.12 * s, 0.02 * s, 0.16 * s], beak)
    o += _pair("sphere", (x, y + 1.17 * s, z + f * 0.25 * s), 0.11 * s, 0.085 * s, "#ffffff", material="glossy", animate=a)
    o += _pair("sphere", (x, y + 1.17 * s, z + f * 0.33 * s), 0.11 * s, 0.04 * s, "#111111", material="glossy", animate=a + [{"type": "orbit", "speed": 3, "amount": 0.012 * s}])
    if crest:
        o.append(O("cone", (x, y + 1.42 * s, z), [0.1 * s, 0.22 * s, 0.1 * s], crest, rotate=[f * -20, 0, 0], animate=a))
    return o


def bug(at, color="#2f9e44", size=0.35, face_you=True, anim=()):
    """[7] Googly-eyed beetle (round shell, head, antennae). Size 0.35 ≈ a tennis ball; scale up for a monster bug."""
    x, y, z = at
    s, f = size, _f(face_you)
    a = list(anim)
    o = [O("sphere", (x, y + 0.35 * s, z), [0.5 * s, 0.32 * s, 0.6 * s], color, material="glossy", animate=a),
         O("box", (x, y + 0.5 * s, z - f * 0.05 * s), [0.02 * s, 0.14 * s, 1.0 * s], "#111111", animate=a),
         O("sphere", (x, y + 0.36 * s, z + f * 0.55 * s), 0.24 * s, "#212529", animate=a)]
    o += _pair("sphere", (x, y + 0.48 * s, z + f * 0.72 * s), 0.11 * s, 0.1 * s, "#ffffff", material="glossy", animate=a)
    o += _pair("sphere", (x, y + 0.48 * s, z + f * 0.81 * s), 0.11 * s, 0.045 * s, "#111111", material="glossy", animate=a + [{"type": "orbit", "speed": 4, "amount": 0.02 * s}])
    o += [O("cylinder", (x + sx * 0.12 * s, y + 0.72 * s, z + f * 0.62 * s), [0.015 * s, 0.4 * s, 0.015 * s], "#111111", rotate=[f * 30, 0, -sx * 25],
            animate=a + [{"type": "wobble", "speed": 5, "amount": 0.2}]) for sx in (-1, 1)]
    return o


def bug_swarm(at=(0, 0.6, -3), count=40, seed=1, spread=(4, 1.2, 3), color="#343a40"):
    """[1] Cheap swarm of tiny buzzing dots (one object). Mix with a few googly `bug`s up front."""
    return [O("sphere", at, [0.05, 0.035, 0.06], color, count=count, seed=seed, spread=list(spread),
              animate=[{"type": "bob", "amount": 0.15, "speed": 3.5}, {"type": "orbit", "speed": 2.5, "amount": 0.12}])]


def land_shark(at, color="#7b8a9a", belly="#f1f3f5", size=1.0, face_you=True, hammer=False, anim=(), grin=True):
    """[14] Shark that walks on land: upright body on two stubby fin-feet, side fins as arms, dorsal fin, tail on the ground,
    big googly eyes on the FRONT of the head and a toothy grin. hammer=True gives a hammerhead (eyes on the ends). Height ≈ 1.9*size."""
    x, y, z = at
    s, f = size, _f(face_you)
    a = list(anim)
    o = [O("capsule", (x, y + 1.0 * s, z), [0.62 * s, 1.15 * s, 0.55 * s], color, animate=a),                                   # body
         O("capsule", (x, y + 0.95 * s, z + f * 0.17 * s), [0.44 * s, 0.9 * s, 0.3 * s], belly, animate=a),                     # belly
         O("cone", (x, y + 1.25 * s, z - f * 0.3 * s), [0.12 * s, 0.5 * s, 0.38 * s], color, rotate=[f * -25, 0, 0], animate=a),  # dorsal fin
         O("cone", (x, y + 0.28 * s, z - f * 0.5 * s), [0.12 * s, 0.6 * s, 0.4 * s], color, rotate=[f * -110, 0, 0], animate=a),  # tail
         O("box", (x, y + 1.42 * s, z + f * 0.31 * s), [0.34 * s, 0.07 * s, 0.03 * s], "#5c1a1a", animate=a)]                  # mouth
    if grin:
        o.append(O("box", (x, y + 1.44 * s, z + f * 0.33 * s), [0.3 * s, 0.035 * s, 0.02 * s], "#ffffff", animate=a))           # teeth
    o += [O("box", (x + sx * 0.36 * s, y + 1.0 * s, z + f * 0.05 * s), [0.32 * s, 0.07 * s, 0.2 * s], color, rotate=[0, 0, sx * -35],
            animate=a + [{"type": "wobble", "axis": "z", "speed": 2.5, "amount": 0.2}]) for sx in (-1, 1)]                       # arm fins
    o += _pair("capsule", (x, y + 0.14 * s, z + f * 0.05 * s), 0.15 * s, [0.14 * s, 0.26 * s, 0.14 * s], color, animate=a)      # legs
    o += _pair("box", (x, y + 0.03 * s, z + f * 0.12 * s), 0.15 * s, [0.2 * s, 0.05 * s, 0.3 * s], belly, animate=a)          # fin feet
    if hammer:
        o.append(O("capsule", (x, y + 1.62 * s, z), [0.22 * s, 1.2 * s, 0.22 * s], color, rotate=[0, 0, 90], animate=a))
        o += _pair("sphere", (x, y + 1.66 * s, z + f * 0.1 * s), 0.55 * s, 0.1 * s, "#ffffff", material="glossy", animate=a)
        o += _pair("sphere", (x, y + 1.66 * s, z + f * 0.18 * s), 0.55 * s, 0.05 * s, "#111111", material="glossy",
                   animate=a + [{"type": "orbit", "speed": 3, "amount": 0.012 * s}])
    else:
        o += _pair("sphere", (x, y + 1.62 * s, z + f * 0.22 * s), 0.13 * s, 0.1 * s, "#ffffff", material="glossy", animate=a)
        o += _pair("sphere", (x, y + 1.62 * s, z + f * 0.31 * s), 0.13 * s, 0.048 * s, "#111111", material="glossy",
                   animate=a + [{"type": "orbit", "speed": 3, "amount": 0.012 * s}])
    return o


def mini_shark(at, color="#d9b26a", size=0.5, face_you=True, anim=()):
    """[8] Little spotted epaulette shark walking on its fins along the ground (long body lying down, 4 fin-paddles, googly eyes)."""
    x, y, z = at
    s, f = size, _f(face_you)
    a = list(anim)
    o = [O("capsule", (x, y + 0.14 * s, z), [0.3 * s, 1.4 * s, 0.26 * s], color, rotate=[90, 0, 0], animate=a),
         O("cone", (x, y + 0.16 * s, z - f * 0.95 * s), [0.06 * s, 0.4 * s, 0.22 * s], color, rotate=[f * -90, 0, 0], animate=a),
         O("sphere", (x, y + 0.2 * s, z), 0.04 * s, "#5c3a21", count=8, seed=5, spread=[0.18 * s, 0.05 * s, 1.0 * s], animate=a)]
    o += [O("box", (x + sx * 0.2 * s, y + 0.04 * s, z + dz * s), [0.2 * s, 0.03 * s, 0.12 * s], color,
            animate=a + [{"type": "wobble", "axis": "y", "speed": 3, "amount": 0.4}]) for sx in (-1, 1) for dz in (0.3, -0.25)]
    o += _pair("sphere", (x, y + 0.26 * s, z + f * 0.6 * s), 0.07 * s, 0.06 * s, "#ffffff", material="glossy", animate=a)
    o += _pair("sphere", (x, y + 0.27 * s, z + f * 0.65 * s), 0.07 * s, 0.03 * s, "#111111", material="glossy", animate=a)
    return o


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


def picket_sign(at, board="#fff9db", emoji_text="✊", stick="#a0795a", size=1.0, rot=0):
    """[3] Protest sign on a stick with a big emoji on the board (place it beside or above a creature)."""
    x, y, z = at
    s = size
    return [O("cylinder", (x, y + 0.5 * s, z), [0.04 * s, 1.0 * s, 0.04 * s], stick),
            O("box", (x, y + 1.15 * s, z + 0.03), [0.8 * s, 0.55 * s, 0.04 * s], board, rotate=[0, rot, 0]),
            O("emoji", (x, y + 1.15 * s, z + 0.08), 0.38 * s, text=emoji_text)]


def cat_tower(at, color="#c5a880", pad="#868e96", size=1.0):
    """[6] Carpeted cat tower: post with three round platforms (the cat's throne)."""
    x, y, z = at
    s = size
    return [O("cylinder", (x, y + 0.8 * s, z), [0.16 * s, 1.6 * s, 0.16 * s], color),
            O("cylinder", (x, y + 0.04 * s, z), [0.9 * s, 0.08 * s, 0.9 * s], pad),
            O("cylinder", (x, y + 0.7 * s, z), [0.7 * s, 0.07 * s, 0.7 * s], pad),
            O("cylinder", (x, y + 1.6 * s, z), [0.8 * s, 0.08 * s, 0.8 * s], pad),
            O("sphere", (x + 0.3 * s, y + 0.5 * s, z + 0.2 * s), 0.07 * s, "#ff6b6b", animate=[{"type": "wobble", "speed": 2, "amount": 0.3}]),
            O("cylinder", (x + 0.3 * s, y + 0.62 * s, z + 0.2 * s), [0.008, 0.16 * s, 0.008], "#f8f9fa")]


def gavel(at, color="#7a4b2a", size=1.0, banging=False):
    """[3] Judge's gavel + sound block (set banging=True to bob it)."""
    x, y, z = at
    s = size
    a = [{"type": "bob", "amount": 0.05 * s, "speed": 6}] if banging else []
    return [O("cylinder", (x, y + 0.03 * s, z), [0.2 * s, 0.06 * s, 0.2 * s], "#5c3a21"),
            O("cylinder", (x, y + 0.16 * s, z), [0.09 * s, 0.24 * s, 0.09 * s], color, rotate=[0, 0, 90], animate=a),
            O("cylinder", (x + 0.16 * s, y + 0.16 * s, z + 0.08 * s), [0.03 * s, 0.32 * s, 0.03 * s], color, rotate=[60, 0, 0], animate=a)]


def dog_bowl(at, color="#e03131", food="#a0522d", size=1.0):
    """[3] Dog bowl with a pile of kibble (put on the floor or hold it)."""
    x, y, z = at
    s = size
    return [O("cylinder", (x, y + 0.05 * s, z), [0.34 * s, 0.1 * s, 0.34 * s], color, material="glossy"),
            O("torus", (x, y + 0.1 * s, z), [0.33 * s, 0.33 * s, 0.3 * s], color, material="glossy", rotate=[90, 0, 0]),
            O("sphere", (x, y + 0.12 * s, z), 0.025 * s, food, count=22, seed=4, spread=[0.24 * s, 0.03 * s, 0.24 * s])]


def fire_hydrant(at, color="#e03131", size=1.0):
    """[5] Red fire hydrant (dog-park landmark)."""
    x, y, z = at
    s = size
    return [O("cylinder", (x, y + 0.3 * s, z), [0.22 * s, 0.6 * s, 0.22 * s], color, material="glossy"),
            O("sphere", (x, y + 0.62 * s, z), [0.13 * s, 0.1 * s, 0.13 * s], color, material="glossy"),
            O("cylinder", (x, y + 0.04 * s, z), [0.3 * s, 0.08 * s, 0.3 * s], color),
            *_pair("cylinder", (x, y + 0.4 * s, z), 0.14 * s, [0.08 * s, 0.1 * s, 0.08 * s], "#fcc419", rotate=[0, 0, 90])]


def cone_of_shame(cam_at=(0, 0.6, 0.5), color="#e7f5ff", opacity=0.3):
    """[2] The vet cone, seen from INSIDE: a big translucent funnel whose tip sits behind the camera, so its rim frames the view.
    Pass the camera position (cam pos); the camera must look roughly toward −z."""
    x, y, z = cam_at
    return [O("cone", (x, y, z - 0.05), [1.5, 0.9, 1.5], color, rotate=[-90, 0, 0], opacity=opacity),
            O("torus", (x, y, z - 0.5), [1.5, 1.5, 0.2], "#a5d8ff", opacity=0.7)]


def lifeguard_tower(at, color="#f8f9fa", roof="#e03131", size=1.0):
    """[8] Lifeguard tower on stilts: platform at y≈1.6*size, little hut, red roof, ladder (seat something on top at y+1.65*size)."""
    x, y, z = at
    s = size
    o = _quad("box", (x, y + 0.8 * s, z), 0.55 * s, 0.45 * s, [0.08 * s, 1.6 * s, 0.08 * s], color)
    o += [O("box", (x, y + 1.62 * s, z), [1.4 * s, 0.08 * s, 1.2 * s], color),
          O("box", (x, y + 2.15 * s, z - 0.5 * s), [1.4 * s, 1.0 * s, 0.06 * s], "#ffd43b"),
          O("box", (x, y + 2.75 * s, z), [1.7 * s, 0.1 * s, 1.5 * s], roof),
          *_pair("box", (x, y + 2.15 * s, z + 0.6 * s), 0.68 * s, [0.06 * s, 1.1 * s, 0.06 * s], color),
          O("box", (x, y + 0.8 * s, z + 0.75 * s), [0.5 * s, 1.6 * s, 0.04 * s], "#ced4da", rotate=[20, 0, 0])]
    return o


def camcorder(color="#343a40"):
    """[4] Handheld documentary camera (use as hold=camcorder()); lens points away from you."""
    return [O("box", (0, 0.02, -0.05), [0.12, 0.1, 0.22], color, material="glossy"),
            O("cylinder", (0, 0.02, -0.19), [0.07, 0.08, 0.07], "#111111", rotate=[90, 0, 0]),
            O("sphere", (0.05, 0.08, 0.02), 0.012, "#ff3b30", material="glow", animate=[{"type": "pulse", "amount": 0.6}]),
            O("box", (-0.075, 0.03, 0.0), [0.02, 0.07, 0.1], "#495057")]


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


def living_room(seed=1, wall="#ffe8cc", sofa="#5c7cfa", rug="#e64980", window="#a5d8ff", extra=()):
    """[10+] Living room: sofa against the back wall, rug, window, lamp, plant. You stand near z=+0.6 facing the sofa (−z)."""
    return [O("box", (0, -0.02, -2), [9, 0.04, 9], "#b98b5e"), O("box", (0, 1.6, -5.2), [9, 3.2, 0.1], wall),
            O("box", (-4.5, 1.6, -2), [0.1, 3.2, 9], wall), O("cylinder", (0, 0.01, -2.4), [2.6, 0.02, 1.8], rug),
            O("box", (0, 0.35, -4.2), [2.8, 0.7, 1.0], sofa), O("box", (0, 0.85, -4.65), [2.8, 0.8, 0.3], sofa),
            *_pair("box", (0, 0.55, -4.2), 1.45, [0.25, 0.5, 1.0], sofa),
            O("plane", (2.6, 1.9, -5.13), [1.2, 1.3, 1], window, material="glow"),
            O("cylinder", (-2.9, 0.75, -4.4), [0.05, 1.5, 0.05], "#495057"), O("cone", (-2.9, 1.6, -4.4), [0.5, 0.4, 0.5], "#fff3bf", material="glow"),
            O("cylinder", (3.6, 0.3, -4.4), [0.5, 0.6, 0.5], "#e8590c"), O("sphere", (3.6, 0.9, -4.4), 0.45, "#40c057")] + list(extra)


def picnic(seed=1, blanket="#ff6b6b", grass="#74b816", extra=()):
    """[8+] Picnic in the park: checked blanket at (0,0,-1.6), basket, sandwich, juice, trees behind."""
    return park(seed=seed, grass=grass, trees=7) + [
        O("box", (0, 0.01, -1.6), [2.2, 0.02, 1.8], "#f8f9fa"),
        O("box", (0, 0.02, -1.6), [0.36, 0.005, 0.36], blanket, count=12, seed=seed + 5, spread=[1.8, 0, 1.4]),
        O("box", (0.7, 0.2, -2.1), [0.5, 0.36, 0.34], "#c08a4e"), O("torus", (0.7, 0.42, -2.1), [0.36, 0.3, 0.3], "#8d6e4f", rotate=[0, 90, 0]),
        O("box", (-0.3, 0.06, -1.3), [0.3, 0.08, 0.22], "#f2c27a"), O("box", (-0.3, 0.1, -1.3), [0.31, 0.02, 0.23], "#69db7c"),
        O("cylinder", (0.1, 0.12, -1.2), [0.07, 0.22, 0.07], "#ffa94d")] + list(extra)


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


ALL_ANIMALS = [wolf, dog, cat, bear, deer, lion, bird, big_bird, bug, bug_swarm, land_shark, mini_shark, fish, shark, dino, sauropod, pterodactyl, robot, alien, ghost]
ALL_PROPS = [pizza, burger, cake, coffee, phone, money, money_rain, gold_bars, trophy, gift, crown, tv, car, bus, rocket, ufo,
             balloon_cluster, confetti, fire_pit, full_moon, stars_field, snow, rain, fireflies, portal, sign, desk_row, picket_sign, cat_tower, gavel, dog_bowl, fire_hydrant, cone_of_shame, lifeguard_tower, camcorder]
ALL_PLACES = [forest, den, classroom, cafeteria, kitchen, supermarket, plane_cabin, beach, snowfield, desert, space_station,
              city_night, stadium, park, picnic, living_room, bedroom_kid, courtroom, wedding, hospital_hall, underwater]


# ═════════════════════════ v2: HUMANS & REAL LIFE (use with Story(..., look="film")) ═════════════════════════
# person() = a real-looking stylised human (jointed arms/legs, eyes that blink, hair, outfits, lip-sync).
# Sets below are built from textured surfaces (tex=planks|tiles|bricks|asphalt|grass|carpet|concrete|marble|stripes|
# wallpaper|sidewalk|paint) and real light sources (O("lamp")), so they read like real places.

SKIN = {"porcelain": "#f6d9c4", "light": "#efc8a8", "fair": "#e5b48f", "medium": "#d29c74", "olive": "#c08a5e",
        "tan": "#a8704a", "brown": "#8a5a3b", "deep": "#5e3b26", "ebony": "#46291b"}
HAIR = {"black": "#141110", "dark": "#2b1d14", "brown": "#5a3a22", "auburn": "#7b3a1e", "ginger": "#b8582a",
        "blonde": "#d9b26a", "platinum": "#e8e0c8", "grey": "#a9a9a9", "white": "#e9e9e9", "pink": "#f783ac", "blue": "#4c6ef5"}
ACTS = ("idle talk walk run wave point point_side cheer clap facepalm cry shrug think cross hips angry scared dance jump sit "
        "sit_type sit_phone sit_talk sit_eat sit_sad type phone text selfie call drink eat carry push bow laugh stretch yawn lie "
        "sleep kneel lean mic finger_guns thumbs_up flex beg panic shake_head nod").split()
EXPRS = ("smile happy grin shock surprised sad angry smirk neutral love scared tired cringe laugh sleep confused proud bored "
         "worried disgust excited").split()
OUTFITS = "tshirt shirt hoodie suit blazer jacket coat sweater dress apron scrubs tank uniform shorts".split()
HAIRS = "short side spiky ponytail bun buzz bob long pigtails curly afro bald mohawk".split()


def person(at, top="#4c6ef5", bottom="#3b4a5a", skin="medium", hair="short", hair_color="dark", outfit="tshirt", age="adult",
           expr="smile", act="idle", ry=0, talk=(), seed=1, look="you", shoes="#2b2b2b", glasses=None, sunglasses=False, hat=None,
           hat_color=None, beard=None, hold=None, hold2=None, tie=None, feminine=False, build=1.0, height=1.0, eye_color=None,
           chest=None, lanyard=False, watch=False, belly=False, earrings=False, lips=None, apron=False, size=1.0, anim=(), **kw):
    """[1 object] A human. Faces +z (you) at ry=0. age: kid|teen|adult|elder. look: "you" (head follows the camera), "ahead", or [x,y,z].
    act: see ACTS (e.g. talk, walk, sit_type, phone, call, facepalm, cheer...). expr: see EXPRS. outfit: see OUTFITS. hair: see HAIRS.
    hold/hold2 (right/left hand): phone cup coffee paper book bag briefcase card mic money box clipboard keys bottle or "emoji:🍔".
    talk=[(start, dur)] animates the mouth (match your say() lines). beard: full|stubble|mustache. hat: cap beanie hardhat chef
    headphones party crown grad santa. skin/hair_color accept SKIN/HAIR names or hex. Feet at y=at[1] (sitting acts sit at seat height ~0.47)."""
    o = O("person", at, 1, SKIN.get(skin, skin), skin=SKIN.get(skin, skin), top=top, bottom=bottom, hair=hair,
          hair_color=HAIR.get(hair_color, hair_color), outfit=outfit, age=age, expr=expr, act=act, rotate=[0, ry, 0],
          talk=[list(t) for t in talk], seed=seed, look=look if isinstance(look, str) else list(look), shoes=shoes, feminine=feminine,
          build=build, height=height, size=size, animate=list(anim))
    for k, v in dict(glasses=glasses, sunglasses=sunglasses, hat=hat, hat_color=hat_color, beard=beard, hold=hold, hold2=hold2, tie=tie,
                     eye_color=eye_color, chest=chest, lanyard=lanyard, watch=watch, belly=belly, earrings=earrings, lips=lips, apron=apron).items():
        if v:
            o[k] = v
    if sunglasses and not glasses:
        o["glasses"] = "#111111"
    o.update(kw)
    return o


_TOPS = ["#4c6ef5", "#e03131", "#2f9e44", "#f08c00", "#ae3ec9", "#1098ad", "#495057", "#f1f3f5", "#c2255c", "#364fc7", "#d9480f", "#5c940d", "#343a40", "#e8d5b5"]
_BOTTOMS = ["#2b3a55", "#343a40", "#495057", "#5c4033", "#1f2a44", "#7a6a55", "#212529"]


def people(n, seed, at=(0, 0, -6), spread=(8, 0, 4), act="idle", ry=0, look="ahead", acts=None, age=None, expr=None, outfits=None, ry_jitter=0):
    """[n objects] A varied, deterministic crowd of humans (different skin, hair, clothes). acts: optional list to cycle through."""
    r = random.Random(seed * 7919 + 13)
    skins, hairs, hcols = list(SKIN), ["short", "side", "bob", "long", "ponytail", "curly", "buzz", "bun", "afro", "spiky", "bald"], list(HAIR)[:7]
    out = []
    for i in range(n):
        fem = r.random() < 0.5
        hs = r.choice(["bob", "long", "ponytail", "bun", "curly", "pigtails"] if fem else ["short", "side", "buzz", "curly", "spiky", "bald", "afro"])
        a = acts[i % len(acts)] if acts else act
        p = (at[0] + (r.random() - 0.5) * spread[0], at[1] + (r.random() - 0.5) * spread[1], at[2] + (r.random() - 0.5) * spread[2])
        ag = age or r.choice(["adult"] * 6 + ["teen", "elder"])
        out.append(person(p, top=r.choice(_TOPS), bottom=r.choice(_BOTTOMS), skin=r.choice(skins), hair=hs, hair_color=r.choice(hcols),
                          outfit=r.choice(outfits or ["tshirt", "tshirt", "shirt", "hoodie", "jacket", "sweater"] + (["dress"] if fem else [])),
                          age=ag, act=a, ry=ry + (r.random() - 0.5) * ry_jitter, seed=seed * 100 + i, look=look, feminine=fem,
                          expr=expr or r.choice(["smile", "neutral", "smile", "happy"]), glasses=r.random() < 0.2,
                          beard=(r.choice([None, None, "stubble", "full"]) if not fem and ag != "teen" else None), build=0.9 + r.random() * 0.25))
    return out


def screen_ui(app=None, big=None, sub=None, messages=(), lines=(), button=None, bg="#ffffff", fg="#111111", accent="#228be6", time="9:41", big_color=None):
    """Spec for phone/TV/laptop screens: Story.beat(hands="phone", screen=screen_ui(...)) or screen_panel(...).
    messages=[("them", "u up?"), ("me", "no")]; big="$3.12" (balance, score, timer); lines=["Step 1", ...]; button="Pay now"."""
    d = {"bg": bg, "fg": fg, "accent": accent, "time": time, "messages": [list(m) for m in messages], "lines": list(lines)}
    for k, v in (("app", app), ("big", big), ("sub", sub), ("button", button), ("bigColor", big_color)):
        if v:
            d[k] = v
    return d


def screen_panel(at, w, h, spec, rot=(0, 0, 0)):
    """[1] A glowing UI screen (TV, monitor, billboard, airport board) showing screen_ui(...) content."""
    return O("screen", at, [w, h, 1], "#ffffff", screen=spec, rotate=list(rot))


def text(at, words, w=1.6, h=0.5, bg="#ffffff", fg="#111111", rot=(0, 0, 0), lit=False, border=None, font=None, weight=900):
    """[1] A flat sign with real words ("OPEN", "EXIT", store names, menus). Use \\n for lines. lit=True glows."""
    o = O("text", at, [w, h, 1], bg, text=words, bg=bg, fg=fg, rotate=list(rot), weight=weight)
    if lit:
        o["lit"] = lit
    if border:
        o["border"] = border
    if font:
        o["font"] = font
    return o


def lamp(at, color="#ffe8c2", intensity=6, range_=8, hidden=False):
    """[1] A real point light (+ visible bulb unless hidden). Max ~3 per shot."""
    return O("lamp", at, 1, color, intensity=intensity, range=range_, hidden=hidden)


def spotlight(at, target, color="#fff4e0", intensity=40, angle=22, shadow=False):
    """[1] A spotlight from `at` aimed at `target` (stage, interrogation, flashlight)."""
    return O("spot", at, 1, color, target=list(target), intensity=intensity, angle=angle, shadow=shadow)


def room(w=8, d=9, h=2.8, z_back=-5.5, wall="#efe6da", floor="#b48a60", floor_tex="planks", wall_tex="paint", ceiling="#f8f6f2",
         side_walls=True, panels=2, panel_color="#fff8ec", x=0):
    """[6-9] Shell of an interior: textured floor, back + side walls, ceiling with light panels. Open toward +z (camera side)."""
    zc = z_back + d / 2
    # walls + ceiling don't cast shadows, so the "sun" acts as the room's key light (people still cast floor shadows)
    o = [O("box", (x, -0.05, zc), [w, 0.1, d], floor, tex=floor_tex, texRep=[w, d]),
         O("box", (x, h / 2, z_back), [w, h, 0.12], wall, tex=wall_tex, texRep=[w, h], cast=False),
         O("box", (x, h + 0.05, zc), [w, 0.1, d], ceiling, cast=False),
         O("box", (x, 0.06, z_back + 0.07), [w, 0.12, 0.03], "#ffffff", material="paint", cast=False)]
    if side_walls:
        o += [O("box", (x - w / 2, h / 2, zc), [0.12, h, d], wall, tex=wall_tex, texRep=[d, h], cast=False),
              O("box", (x + w / 2, h / 2, zc), [0.12, h, d], wall, tex=wall_tex, texRep=[d, h], cast=False)]
    for i in range(panels):
        o.append(O("box", (x, h - 0.01, z_back + d * (i + 0.6) / (panels + 0.4)), [1.2, 0.03, 0.6], panel_color, material="emit"))
    return o


# ── real-life props ──
def table(at, w=1.4, d=0.8, h=0.75, color="#8b6a4a", legs="#3b3b3b", tex="planks"):
    """[5] Table (top at y=h)."""
    x, y, z = at
    return [O("box", (x, y + h - 0.02, z), [w, 0.04, d], color, tex=tex, texRep=[w, d])] + _quad("box", (x, y + (h - 0.04) / 2, z), w / 2 - 0.06, d / 2 - 0.06, [0.05, h - 0.04, 0.05], legs, material="metal")


def chair(at, color="#495057", ry=0, seat=0.46):
    """[3] Simple chair facing +z at ry=0 (seat at 0.46 m: use person(act="sit") at the same spot)."""
    import math
    x, y, z = at
    bx, bz = -math.sin(math.radians(ry)) * 0.22, -math.cos(math.radians(ry)) * 0.22
    return [O("box", (x, y + seat, z), [0.46, 0.05, 0.44], color, rotate=[0, ry, 0]), O("box", (x + bx, y + seat + 0.3, z + bz), [0.46, 0.55, 0.05], color, rotate=[0, ry, 0]),
            O("cylinder", (x, y + seat / 2, z), [0.05, seat, 0.05], "#212529", material="metal")]


def office_chair(at, color="#212529", ry=0):
    """[4] Swivel office chair."""
    import math
    x, y, z = at
    bx, bz = -math.sin(math.radians(ry)) * 0.25, -math.cos(math.radians(ry)) * 0.25
    return [O("box", (x, y + 0.48, z), [0.52, 0.09, 0.5], color, material="fabric", rotate=[0, ry, 0]),
            O("box", (x + bx, y + 0.86, z + bz), [0.48, 0.66, 0.08], color, material="fabric", rotate=[0, ry, 0]),
            O("cylinder", (x, y + 0.24, z), [0.05, 0.45, 0.05], "#adb5bd", material="chrome"), O("cylinder", (x, y + 0.04, z), [0.6, 0.04, 0.6], "#343a40", material="plastic")]


def laptop(at, ry=0, screen=None, color="#ced4da"):
    """[3] Open laptop (screen faces +z at ry=0). screen=screen_ui(...) to show content."""
    import math
    x, y, z = at
    sx, sz = -math.sin(math.radians(ry)) * 0.13, -math.cos(math.radians(ry)) * 0.13
    o = [O("box", (x, y + 0.01, z), [0.34, 0.02, 0.24], color, material="metal", rotate=[0, ry, 0]),
         O("box", (x + sx, y + 0.13, z + sz), [0.34, 0.23, 0.012], color, material="metal", rotate=[-12, ry, 0])]
    spec = screen or screen_ui(app="Docs", lines=["Q3 report", "......", "....."], bg="#f8f9fa")
    o.append(screen_panel((x + sx * 0.92, y + 0.13, z + sz * 0.92), 0.31, 0.2, spec, rot=(-12, ry, 0)))
    return o


def monitor(at, ry=0, screen=None, w=0.6):
    """[3] Desk monitor on a stand."""
    x, y, z = at
    return [O("box", (x, y + 0.36, z - 0.02), [w, w * 0.6, 0.03], "#212529", material="plastic", rotate=[0, ry, 0]),
            screen_panel((x, y + 0.36, z), w * 0.94, w * 0.55, screen or screen_ui(app="Inbox (4,281)", lines=["RE: RE: RE: urgent", "Meeting moved", "Quick sync?"], bg="#ffffff"), rot=(0, ry, 0)),
            O("box", (x, y + 0.1, z - 0.04), [0.06, 0.2, 0.04], "#343a40", material="metal"), O("box", (x, y + 0.01, z - 0.04), [0.25, 0.02, 0.18], "#343a40", material="metal")]


def desk(at, w=1.4, d=0.7, ry=0, color="#d8c3a5", screen=None, with_monitor=True, clutter=True):
    """[8-12] Office desk: top, legs, monitor, keyboard, mug, papers."""
    x, y, z = at
    o = table(at, w, d, 0.74, color, "#495057", tex="planks")
    if with_monitor:
        o += monitor((x, y + 0.75, z - 0.15), ry, screen)
    o += [O("box", (x, y + 0.765, z + 0.12), [0.42, 0.02, 0.14], "#343a40", material="plastic")]
    if clutter:
        o += [O("cylinder", (x + 0.45, y + 0.81, z + 0.05), [0.08, 0.1, 0.08], "#f1f3f5", material="ceramic"),
              O("box", (x - 0.45, y + 0.765, z + 0.05), [0.22, 0.02, 0.3], "#ffffff", rotate=[0, 12, 0])]
    return o


def plant(at, size=1.0, pot="#d9480f", leaves="#2f9e44"):
    """[4] Potted plant."""
    x, y, z = at
    s = size
    return [O("cylinder", (x, y + 0.2 * s, z), [0.35 * s, 0.4 * s, 0.35 * s], pot, material="ceramic"),
            O("sphere", (x, y + 0.65 * s, z), [0.32 * s, 0.4 * s, 0.32 * s], leaves),
            O("sphere", (x - 0.15 * s, y + 0.85 * s, z + 0.05), [0.2 * s, 0.28 * s, 0.2 * s], "#37b24d"),
            O("sphere", (x + 0.17 * s, y + 0.8 * s, z - 0.05), [0.18 * s, 0.25 * s, 0.18 * s], "#2b8a3e")]


def window(at, w=1.6, h=1.4, view="#a5d8ff", frame="#f8f9fa", rot=(0, 0, 0), night=False):
    """[3] Window with a bright outside view (emits light)."""
    x, y, z = at
    return [O("box", (x, y, z), [w + 0.12, h + 0.12, 0.08], frame, rotate=list(rot)),
            O("plane", (x, y, z + 0.05), [w, h, 1], "#1b2a4a" if night else view, material="emit" if not night else "glow", rotate=list(rot)),
            O("box", (x, y, z + 0.06), [0.04, h, 0.03], frame, rotate=list(rot))]


def door(at, color="#f1f3f5", w=0.95, h=2.1, rot=(0, 0, 0), sign=None):
    """[3-4] Interior door with handle (optional sign text)."""
    x, y, z = at
    o = [O("box", (x, y + h / 2, z), [w, h, 0.05], color, material="paint", rotate=list(rot)),
         O("box", (x, y + h / 2, z - 0.01), [w + 0.1, h + 0.06, 0.04], "#dee2e6", rotate=list(rot)),
         O("sphere", (x + w * 0.38, y + 1.0, z + 0.05), 0.035, "#adb5bd", material="chrome")]
    if sign:
        o.append(text((x, y + 1.6, z + 0.03), sign, 0.5, 0.18, rot=rot))
    return o


def bookshelf(at, w=1.2, h=1.9, color="#6b4f36", seed=1):
    """[4+] Shelf with books."""
    x, y, z = at
    r = random.Random(seed)
    o = [O("box", (x, y + h / 2, z), [w, h, 0.32], color, tex="planks")]
    for k in range(4):
        yy = y + 0.25 + k * (h - 0.3) / 4
        o.append(O("box", (x - w * 0.2, yy, z + 0.03), [w * 0.5, 0.26, 0.24], r.choice(["#c92a2a", "#1864ab", "#2b8a3e", "#e67700", "#5f3dc4"])))
        o.append(O("box", (x + w * 0.25, yy, z + 0.03), [w * 0.35, 0.22, 0.24], r.choice(["#f1f3f5", "#495057", "#a61e4d", "#0b7285"])))
    return o


def fridge(at, color="#e9ecef", ry=0):
    """[3] Fridge."""
    x, y, z = at
    return [O("box", (x, y + 0.95, z), [0.8, 1.9, 0.75], color, material="glossy", rotate=[0, ry, 0]),
            O("box", (x + 0.3, y + 1.3, z + 0.39), [0.03, 0.4, 0.03], "#adb5bd", material="chrome"), O("box", (x, y + 1.18, z + 0.38), [0.8, 0.01, 0.01], "#adb5bd")]


def counter(at, w=3.0, d=0.65, color="#e9ecef", top="#f8f9fa", top_tex="marble"):
    """[3] Kitchen/shop counter (top at 0.92)."""
    x, y, z = at
    return [O("box", (x, y + 0.45, z), [w, 0.9, d], color, material="paint"), O("box", (x, y + 0.92, z), [w + 0.04, 0.05, d + 0.04], top, tex=top_tex, texRep=[w, d]),
            O("box", (x, y + 0.04, z + d / 2 - 0.04), [w, 0.08, 0.02], "#343a40")]


def bed(at, w=1.6, l=2.1, sheets="#e7f5ff", frame="#6b4f36", blanket="#4c6ef5", ry=0):
    """[5] Adult bed (head toward −z at ry=0)."""
    x, y, z = at
    return [O("box", (x, y + 0.2, z), [w + 0.1, 0.4, l + 0.1], frame, rotate=[0, ry, 0]), O("box", (x, y + 0.48, z), [w, 0.18, l], sheets, material="fabric", rotate=[0, ry, 0]),
            O("box", (x, y + 0.59, z + 0.25), [w + 0.02, 0.06, l * 0.65], blanket, material="fabric", tex="fabric", texRep=[w, l], rotate=[0, ry, 0]),
            O("box", (x, y + 0.62, z - l / 2 + 0.3), [w * 0.8, 0.15, 0.4], "#ffffff", material="fabric", rotate=[0, ry, 0]),
            O("box", (x, y + 0.75, z - l / 2 - 0.05), [w + 0.1, 1.1, 0.08], frame, rotate=[0, ry, 0])]


def alarm_clock(at, time="6:00", color="#e03131"):
    """[2] Bedside alarm clock with glowing digits."""
    x, y, z = at
    return [O("box", (x, y + 0.06, z), [0.18, 0.12, 0.08], "#212529", material="plastic"), text((x, y + 0.06, z + 0.042), time, 0.15, 0.08, bg="#111111", fg=color, lit=1.6)]


def steering_wheel(at=(0, 1.08, 0.95)):
    """[3] Steering wheel in front of you (for car_inside)."""
    x, y, z = at
    return [O("torus", (x, y, z), [0.42, 0.42, 0.5], "#212529", material="leather", rotate=[62, 0, 0]),
            O("box", (x, y - 0.04, z + 0.02), [0.32, 0.05, 0.03], "#212529", rotate=[62, 0, 0]),
            O("cylinder", (x, y - 0.03, z + 0.02), [0.12, 0.05, 0.12], "#343a40", material="plastic", rotate=[62, 0, 0])]


def shopping_cart(at, ry=0, full=True, seed=1):
    """[6+] Supermarket trolley."""
    x, y, z = at
    o = [O("box", (x, y + 0.75, z), [0.55, 0.45, 0.85], "#adb5bd", material="chrome", opacity=0.55, rotate=[0, ry, 0]),
         O("cylinder", (x, y + 1.0, z + 0.5), [0.04, 0.6, 0.04], "#e03131", material="plastic", rotate=[0, ry, 90])] + _quad("sphere", (x, y + 0.07, z), 0.22, 0.35, 0.07, "#212529")
    if full:
        o += [O("box", (x, y + 0.85, z), [0.12, 0.18, 0.12], "#f59f00", count=6, seed=seed, spread=[0.35, 0.15, 0.6]),
              O("box", (x, y + 0.85, z), [0.12, 0.2, 0.12], "#40c057", count=5, seed=seed + 1, spread=[0.35, 0.15, 0.6])]
    return o


def car_real(at, color="#1c7ed6", ry=0, moving=None):
    """[9] A car with real proportions (cabin glass, wheels, lights). moving=[dx,dy,dz] slides it."""
    x, y, z = at
    a = [{"type": "move", "to": list(moving), "rel": True}] if moving else []
    o = [O("box", (x, y + 0.55, z), [1.8, 0.62, 4.3], color, material="glossy", rotate=[0, ry, 0]),
         O("box", (x, y + 1.08, z - 0.25), [1.62, 0.55, 2.2], "#1d2733", material="glass", opacity=0.9, rotate=[0, ry, 0]),
         O("box", (x, y + 1.36, z - 0.25), [1.6, 0.04, 2.0], color, material="glossy", rotate=[0, ry, 0]),
         *_quad("cylinder", (x, y + 0.33, z), 0.88, 1.35, [0.66, 0.24, 0.66], "#1b1b1b", material="rubber", rotate=[0, 0, 90]),
         *_pair("box", (x, y + 0.66, z + 2.15), 0.62, [0.3, 0.12, 0.04], "#fff9e6", material="emit"),
         O("box", (x, y + 0.45, z + 2.17), [0.7, 0.18, 0.03], "#212529")]
    for d in o:
        if a:
            d["animate"] = list(a)
    return o


def traffic_light(at, state="red"):
    """[4] Traffic light pole."""
    x, y, z = at
    cols = {"red": "#ff3b30", "yellow": "#ffcc00", "green": "#34c759"}
    o = [O("cylinder", (x, y + 1.6, z), [0.12, 3.2, 0.12], "#343a40", material="metal"), O("box", (x, y + 3.4, z), [0.35, 0.9, 0.3], "#212529")]
    for i, k in enumerate(("red", "yellow", "green")):
        o.append(O("sphere", (x, y + 3.68 - i * 0.28, z + 0.16), 0.09, cols[k] if k == state else "#3b3b3b", material="emit" if k == state else "matte"))
    return o


def street_lamp(at, on=False):
    """[3] Street lamp."""
    x, y, z = at
    o = [O("cylinder", (x, y + 2.2, z), [0.1, 4.4, 0.1], "#343a40", material="metal"), O("box", (x, y + 4.4, z + 0.35), [0.25, 0.1, 0.8], "#343a40")]
    o.append(O("box", (x, y + 4.34, z + 0.55), [0.18, 0.03, 0.4], "#fff3bf", material="emit" if on else "matte"))
    return o


def building(at, w=8, h=14, d=6, color="#c9b8a0", window_color="#9cc3e6", tex="bricks", sign=None, shop=None, seed=1):
    """[4-6] A city building front facing +z: textured facade, window grid, optional shop front + sign."""
    x, y, z = at
    o = [O("box", (x, y + h / 2, z), [w, h, d], color, tex=tex, texRep=[w, h]),
         O("plane", (x, y + h * 0.55, z + d / 2 + 0.02), [w * 0.85, h * 0.75, 1], window_color, material="glossy", tex="stripes", texRep=[w * 0.85, h * 0.75], opacity=0.92)]
    if shop:
        o += [O("plane", (x, y + 1.4, z + d / 2 + 0.03), [w * 0.8, 2.4, 1], shop, material="emit")]
    if sign:
        o.append(text((x, y + 3.1, z + d / 2 + 0.05), sign, min(w * 0.7, 5), 0.8, bg="#212529", fg="#ffffff", lit=0.9))
    return o


def bench(at, ry=0, color="#8b5e3c"):
    """[3] Park/bus bench."""
    x, y, z = at
    return [O("box", (x, y + 0.45, z), [1.6, 0.06, 0.45], color, tex="planks", rotate=[0, ry, 0]), O("box", (x, y + 0.75, z - 0.2), [1.6, 0.4, 0.05], color, tex="planks", rotate=[0, ry, 0]),
            *_pair("box", (x, y + 0.22, z), 0.7, [0.06, 0.44, 0.4], "#343a40", material="metal")]


def locker_row(at, n=8, color="#4263eb", rot=0):
    """[n+1] School/gym lockers along x."""
    x, y, z = at
    o = [O("box", (x + (i - (n - 1) / 2) * 0.42, y + 0.95, z), [0.4, 1.9, 0.5], color, material="metal", rotate=[0, rot, 0]) for i in range(n)]
    o += [O("box", (x + (i - (n - 1) / 2) * 0.42 + 0.12, y + 1.05, z + 0.26), [0.03, 0.12, 0.02], "#dee2e6", material="chrome") for i in range(0, n, 2)]
    return o


def dumbbell(at, color="#343a40"):
    """[3] Dumbbell."""
    x, y, z = at
    return [O("cylinder", (x, y + 0.08, z), [0.04, 0.4, 0.04], "#adb5bd", material="chrome", rotate=[0, 0, 90]),
            *_pair("cylinder", (x, y + 0.08, z), 0.16, [0.17, 0.08, 0.17], color, material="rubber", rotate=[0, 0, 90])]


def treadmill(at, ry=0):
    """[3] Treadmill."""
    x, y, z = at
    return [O("box", (x, y + 0.12, z), [0.8, 0.22, 1.9], "#212529", rotate=[0, ry, 0]), O("box", (x, y + 0.24, z), [0.62, 0.02, 1.7], "#343a40", material="rubber", rotate=[0, ry, 0]),
            O("box", (x, y + 1.25, z - 0.85), [0.8, 0.25, 0.12], "#212529", rotate=[-25, ry, 0])]


def coffee_machine(at):
    """[3] Café espresso machine."""
    x, y, z = at
    return [O("box", (x, y + 0.25, z), [0.7, 0.5, 0.45], "#adb5bd", material="chrome"), O("box", (x, y + 0.52, z), [0.72, 0.06, 0.47], "#343a40"),
            O("cylinder", (x - 0.15, y + 0.15, z + 0.25), [0.06, 0.08, 0.06], "#212529", material="metal")]


def menu_board(at, items=("LATTE  $6", "FLAT WHITE  $5", "CROISSANT  $4"), w=2.2, h=1.1):
    """[1] Dark café menu board with real words."""
    return text(at, "MENU\n" + "\n".join(items), w, h, bg="#1f2421", fg="#f1f3f5", weight=700)


def cash_register(at, total="$47.99"):
    """[3] Checkout register with a customer display."""
    x, y, z = at
    return [O("box", (x, y + 0.08, z), [0.4, 0.16, 0.35], "#343a40", material="plastic"),
            O("box", (x, y + 0.3, z - 0.1), [0.3, 0.2, 0.03], "#212529", rotate=[-15, 0, 0]),
            text((x, y + 0.3, z - 0.08), total, 0.27, 0.16, bg="#0b3d2e", fg="#69db7c", rot=(-15, 0, 0), lit=1.2)]


def elevator_doors(at, open_=False):
    """[4] Steel elevator doors with floor display."""
    x, y, z = at
    g = 0.5 if open_ else 0
    return [O("box", (x - 0.5 - g, y + 1.05, z), [1.0, 2.1, 0.05], "#ced4da", material="chrome"), O("box", (x + 0.5 + g, y + 1.05, z), [1.0, 2.1, 0.05], "#ced4da", material="chrome"),
            O("box", (x, y + 1.1, z - 0.03), [2.3, 2.3, 0.04], "#868e96", material="metal"), text((x, y + 2.35, z + 0.03), "▲ 12", 0.4, 0.15, bg="#111111", fg="#ff6b6b", lit=1.4)]


# ── real-life places (each is a full set; add people with person()/people() via extra=[...]) ──
def apartment(seed=1, wall="#ede4d6", sofa="#55657a", rug="#c9b79c", extra=()):
    """[~30] Modern living room: sofa on the back wall, coffee table, TV on the left wall, window, plant, warm lamp. You stand at z≈+1 facing −z."""
    return (room(8, 9, 2.8, -4.6, wall, "#a77b52", "planks", "paint", panels=1)
            + [O("box", (0, 0.01, -2.2), [3.0, 0.02, 2.0], rug, tex="carpet", texRep=[3, 2]),
               O("box", (0, 0.3, -3.9), [2.6, 0.45, 0.95], sofa, material="fabric", tex="fabric", texRep=[2.6, 1]),
               O("box", (0, 0.72, -4.32), [2.6, 0.6, 0.25], sofa, material="fabric"),
               *_pair("box", (0, 0.5, -3.9), 1.38, [0.22, 0.5, 0.95], sofa, material="fabric"),
               O("box", (-0.8, 0.62, -3.75), [0.42, 0.38, 0.14], "#e8d5b5", material="fabric", rotate=[-10, 10, 0]),
               O("box", (0, 0.38, -2.3), [1.1, 0.06, 0.6], "#3b2a1a", tex="planks"), O("box", (0, 0.18, -2.3), [1.0, 0.34, 0.5], "#2b1d14"),
               O("box", (-3.9, 1.35, -2.0), [0.06, 0.85, 1.5], "#111111", material="glossy")]
            + window((2.4, 1.6, -4.52), 1.6, 1.5) + plant((3.3, 0, -4.0), 1.1)
            + [O("cylinder", (-2.4, 0.8, -4.1), [0.04, 1.6, 0.04], "#343a40", material="metal"), O("cone", (-2.4, 1.65, -4.1), [0.45, 0.35, 0.45], "#fff3d6", material="emit"),
               lamp((-2.4, 1.5, -3.8), "#ffd8a8", 4, 6)] + list(extra))


def bedroom(seed=1, wall="#dfe7ee", blanket="#4c6ef5", night=False, extra=()):
    """[~25] Adult bedroom: bed along −z, nightstand + alarm clock, window, wardrobe. Lie-in POV: cam((0,0.9,-2.6),(0,1.2,0))."""
    o = (room(7, 8, 2.7, -4.6, wall, "#b08a66", "planks", "paint", panels=0 if night else 1)
         + bed((0, 0, -3.3), blanket=blanket) + [O("box", (1.3, 0.28, -4.1), [0.5, 0.56, 0.45], "#6b4f36", tex="planks")]
         + alarm_clock((1.3, 0.56, -4.0), "6:00") + window((-2.2, 1.6, -4.52), 1.4, 1.3, night=night)
         + [O("box", (3.0, 1.0, -2.4), [0.6, 2.0, 1.6], "#e9ecef", material="paint")])
    if night:
        o.append(lamp((1.3, 0.85, -4.0), "#ffb86b", 2.5, 4))
    return o + list(extra)


def kitchen_home(seed=1, wall="#f1ece3", cabinets="#5f7a8a", extra=()):
    """[~28] Home kitchen: counter + upper cabinets on the back wall, fridge, island/table with stools, window over the sink."""
    return (room(8, 8, 2.8, -4.4, wall, "#d9d4cc", "tiles", "paint", panels=2)
            + counter((-0.8, 0, -4.0), 4.2, 0.65, cabinets) + [O("box", (-0.8, 2.05, -4.15), [4.2, 0.8, 0.4], cabinets, material="paint")]
            + fridge((2.4, 0, -3.95)) + window((-0.8, 1.55, -4.32), 1.3, 0.8)
            + [O("box", (-2.1, 0.96, -3.95), [0.6, 0.03, 0.45], "#212529", material="glossy"), O("cylinder", (0.2, 1.05, -4.05), [0.18, 0.22, 0.18], "#adb5bd", material="chrome")]
            + table((0, 0, -1.8), 1.6, 0.9, 0.9, "#c9a77c") + list(extra))


def office(seed=1, wall="#e9ecef", carpet="#6c7a89", extra=()):
    """[~45] Open-plan office: desks with monitors in rows going away (−z), glass meeting room, plants, ceiling panels. Aisle at x=0."""
    o = room(12, 14, 3.0, -10, wall, carpet, "carpet", "paint", panels=4)
    for i, z in enumerate((-2.2, -5.0)):
        o += desk((-1.7, 0, z), 1.5, 0.75, screen=screen_ui(app="Slack", messages=[("them", "quick call?"), ("them", "??")]) if i == 0 else None, clutter=i == 0)
        o += desk((1.7, 0, z), 1.5, 0.75, clutter=False)
        o += office_chair((-1.7, 0, z + 0.6), ry=180) if i else []
    o += plant((-5.2, 0, -8.5), 1.3) + plant((5.2, 0, -3.5), 1.2)
    o += [O("box", (3.5, 1.4, -8.5), [4.5, 2.8, 0.05], "#a5d8ff", material="glass"), text((3.5, 2.2, -8.45), "MEETING ROOM", 1.6, 0.22, bg="#ffffff", fg="#495057", weight=700)]
    return o + list(extra)


def meeting_room(seed=1, wall="#eef1f4", screen=None, extra=()):
    """[~20] Meeting room: long table pointing away (−z), chairs, big screen on the back wall. Put coworkers at x=±0.9 seated (act="sit_talk")."""
    o = room(7, 8, 2.8, -5.4, wall, "#7b8794", "carpet", "paint", panels=2) + table((0, 0, -2.6), 1.2, 3.4, 0.75, "#f1f3f5", tex="marble")
    for z in (-1.6, -2.6, -3.6):
        o += chair((-0.95, 0, z), "#343a40", ry=90)[:2] + chair((0.95, 0, z), "#343a40", ry=-90)[:2]
    o.append(screen_panel((0, 1.55, -5.32), 2.6, 1.45, screen or screen_ui(app="Q4 PLANNING", big="📉", sub="revenue (vibes)", bg="#ffffff")))
    return o + list(extra)


def cafe(seed=1, wall="#e8dccb", extra=()):
    """[~35] Coffee shop: counter with espresso machine + barista spot at (0.6,0,-3.6), menu board, small tables, pendant lights."""
    o = (room(9, 9, 3.0, -5.0, wall, "#8a6a4f", "planks", "bricks", panels=0)
         + counter((0.4, 0, -3.1), 4.0, 0.7, "#3b2f2a", "#e9ecef") + coffee_machine((1.4, 0.95, -3.2))
         + [menu_board((0.4, 2.1, -4.92)), O("box", (-1.0, 1.0, -3.1), [0.4, 0.15, 0.3], "#f2c27a"), O("box", (-0.6, 1.0, -3.1), [0.35, 0.12, 0.3], "#c08a4e")]
         + table((-2.6, 0, -1.0), 0.8, 0.8, 0.75, "#c9a77c") + chair((-2.6, 0, -0.4), "#3b2f2a", ry=180)
         + table((2.8, 0, -0.9), 0.8, 0.8, 0.75, "#c9a77c") + plant((-3.8, 0, -4.2), 1.2))
    for x in (-1.2, 0.4, 2.0):
        o += [O("cylinder", (x, 2.6, -3.1), [0.01, 0.8, 0.01], "#212529"), O("cone", (x, 2.15, -3.1), [0.32, 0.22, 0.32], "#212529", material="metal")]
    o += [lamp((0.4, 2.0, -3.0), "#ffc078", 7, 7), lamp((-2.6, 2.2, -1.0), "#ffc078", 3, 5, hidden=True)]
    return o + list(extra)


def street(seed=1, night=False, extra=()):
    """[~40] City street: road along −z, sidewalks, building fronts both sides with shops, lamps, traffic light, parked car. You stand on the right sidewalk (x≈1.5)."""
    o = [O("box", (0, -0.05, -20), [60, 0.1, 80], "#3a3d42", tex="asphalt", texRep=[60, 80]),
         O("box", (-6.5, 0.05, -20), [4, 0.2, 80], "#b7b2a8", tex="sidewalk", texRep=[4, 80]), O("box", (3.2, 0.05, -20), [4, 0.2, 80], "#b7b2a8", tex="sidewalk", texRep=[4, 80]),
         O("box", (-1.6, 0.003, -20), [0.15, 0.01, 80], "#f8f9fa", material="paint", tex="stripes", texRep=[0.15, 80])]
    o += [O("box", (-1.6 + dx, 0.004, -6), [0.5, 0.01, 3.0], "#f1f3f5", material="paint") for dx in (-2.4, -1.2, 0, 1.2, 2.4)]
    o += building((9.2, 0, -6), 8, 14, 8, "#b8a48e", sign="PHARMACY", shop="#fff4d6", seed=seed)
    o += building((9.2, 0, -16), 8, 22, 8, "#8d99ae", tex="concrete", seed=seed + 1)
    o += building((-12.5, 0, -8), 8, 16, 8, "#a26b4f", sign="DINER", shop="#ffe3c2", seed=seed + 2)
    o += building((-12.5, 0, -19), 8, 26, 8, "#ced4da", tex="concrete", seed=seed + 3)
    o += [O("box", (0, 6, -45), [60, 18, 2], "#9aa7b8", tex="concrete", texRep=[60, 18])]
    o += street_lamp((4.6, 0, -4), on=night) + street_lamp((4.6, 0, -16), on=night) + traffic_light((4.6, 0, -9.5), "red")
    o += car_real((-0.2, 0, -12), "#c92a2a") + bench((4.4, 0, -1.5), ry=-90)
    return o + list(extra)


def car_inside(seed=1, outside="street", night=False, speed="62 mph", extra=()):
    """[~25] Driver's seat POV. Use cam((0, 1.2, 1.6), (0, 1.05, -8)) and hands="wheel". Dashboard top sits below the horizon so the road shows."""
    o = [O("box", (0, 0.72, 0.72), [1.9, 0.42, 0.62], "#262a30", material="plastic", cast=False),
         O("box", (0, 0.94, 0.5), [1.9, 0.04, 0.3], "#1b1e22", material="plastic", cast=False),
         O("box", (0, 0.9, 0.78), [0.26, 0.1, 0.04], "#111111", material="glossy", rotate=[-20, 0, 0], cast=False),
         text((0, 0.9, 0.805), speed, 0.22, 0.075, bg="#06121f", fg="#4dabf7", lit=1.3, rot=(-20, 0, 0)),
         O("box", (0, 1.9, 0.9), [1.9, 0.06, 1.5], "#3a3f47", cast=False),
         O("box", (0.0, 1.78, 0.32), [0.28, 0.08, 0.02], "#1b1b1b", cast=False),
         O("box", (0.0, 1.78, 0.335), [0.26, 0.065, 0.005], "#cfe3f0", material="chrome", cast=False),
         *_pair("box", (0, 1.4, 0.45), 0.98, [0.1, 1.05, 0.1], "#2b2f36", rotate=[-30, 0, 0], cast=False)]
    # wheel: rim + spokes, faces you, tilted back
    o += [O("torus", (0, 0.86, 1.17), [0.36, 0.36, 0.55], "#1b1b1b", material="leather", rotate=[-25, 0, 0], cast=False),
          O("cylinder", (0, 0.85, 1.19), [0.1, 0.05, 0.1], "#2b2f36", material="plastic", rotate=[65, 0, 0], cast=False),
          O("box", (0, 0.85, 1.18), [0.33, 0.035, 0.02], "#2b2f36", rotate=[-25, 0, 0], cast=False)]
    if outside == "street":
        o += street(seed)[:16]
    elif outside == "highway":
        o += [O("box", (0, -0.05, -40), [80, 0.1, 120], "#3a3d42", tex="asphalt", texRep=[80, 120]), O("box", (-14, 0.02, -40), [20, 0.04, 120], "#6a8f4e", tex="grass", texRep=[20, 120]),
              O("box", (-1.8, 0.003, -30), [0.15, 0.01, 3], "#f8f9fa", material="paint", count=6, seed=seed, spread=[0, 0, 60])]
    return o + list(extra)


def gym(seed=1, wall="#2b2f36", extra=()):
    """[~30] Gym: rubber floor, mirror wall at the back, dumbbell rack, treadmills, motivational sign."""
    o = (room(10, 10, 3.2, -6, wall, "#2c2c2c", "concrete", "concrete", panels=3)
         + [O("box", (0, 1.4, -5.9), [9.6, 2.4, 0.03], "#cfe3f0", material="chrome"), text((0, 2.9, -5.85), "NO PAIN NO GAIN", 3.6, 0.35, bg="#e03131", fg="#ffffff")]
         + treadmill((-3.0, 0, -3.5)) + treadmill((-1.8, 0, -3.5)) + [O("box", (2.8, 0.45, -4.8), [2.6, 0.1, 0.5], "#495057", material="metal")]
         + dumbbell((2.0, 0.5, -4.8)) + dumbbell((2.8, 0.5, -4.8), "#e03131") + dumbbell((3.6, 0.5, -4.8), "#1c7ed6"))
    return o + list(extra)


def elevator(seed=1, extra=()):
    """[~10] Inside a small lift, facing the closed doors (−z). Fits 2-3 people beside you."""
    return [O("box", (0, -0.05, -0.6), [2.2, 0.1, 2.6], "#6b6e73", tex="tiles", texRep=[2.2, 2.6]),
            O("box", (0, 1.25, -1.9), [2.2, 2.5, 0.05], "#ced4da", material="chrome"), O("box", (0, 1.25, -1.88), [0.02, 2.2, 0.02], "#495057"),
            O("box", (-1.1, 1.25, -0.6), [0.05, 2.5, 2.6], "#b8bec6", material="metal"), O("box", (1.1, 1.25, -0.6), [0.05, 2.5, 2.6], "#b8bec6", material="metal"),
            O("box", (0, 2.5, -0.6), [2.2, 0.05, 2.6], "#e9ecef"), O("box", (0, 2.47, -0.6), [1.2, 0.02, 1.2], "#fff8ec", material="emit"),
            O("box", (0.95, 1.2, -1.5), [0.12, 0.5, 0.05], "#212529"), text((0, 2.25, -1.86), "▲ 12", 0.42, 0.16, bg="#111111", fg="#ff6b6b", lit=1.4)] + list(extra)


def school_hall(seed=1, extra=()):
    """[~30] School corridor: lockers both sides running away (−z), tiled floor, posters, clock."""
    o = room(5, 18, 3.0, -14, "#e6e1d3", "#c8c3b5", "tiles", "paint", panels=4)
    o += locker_row((-2.25, 0, -6), 10, "#4263eb", rot=90) + locker_row((2.25, 0, -8), 10, "#e8590c", rot=-90)
    o += [text((0, 2.35, -13.9), "BE KIND", 1.6, 0.4, bg="#ffd43b", fg="#212529"), O("cylinder", (0, 2.6, -13.92), [0.4, 0.03, 0.4], "#ffffff", rotate=[90, 0, 0])]
    return o + list(extra)


def grocery(seed=1, extra=()):
    """[~30] Supermarket checkout: conveyor counter in front of you, cashier spot at (0.9,0,-2.0), register, aisles behind."""
    o = (room(12, 14, 3.4, -10, "#f1f3f5", "#e9ecef", "tiles", "paint", panels=4)
         + counter((0, 0, -1.4), 0.7, 2.6, "#495057", "#212529", None)
         + cash_register((0.55, 0.95, -2.0))
         + [O("box", (-4, 1.0, -7), [0.6, 2.0, 6], "#ced4da"), O("box", (-3.7, 1.0, -7), [0.15, 0.2, 0.15], "#ff6b6b", count=24, seed=seed, spread=[0.05, 1.6, 5.5]),
            O("box", (4, 1.0, -7), [0.6, 2.0, 6], "#ced4da"), O("box", (3.7, 1.0, -7), [0.15, 0.2, 0.15], "#ffd43b", count=24, seed=seed + 1, spread=[0.05, 1.6, 5.5]),
            text((0, 2.9, -9.9), "FRESH • LOCAL • CHEAP-ISH", 5, 0.5, bg="#2b8a3e", fg="#ffffff")])
    return o + list(extra)


def restaurant(seed=1, wall="#3b2f2a", extra=()):
    """[~30] Fancy restaurant: dim warm light, round table with white cloth in front of you, candles, other diners behind."""
    o = (room(10, 10, 3.2, -6, wall, "#5a3e2b", "planks", "wallpaper", panels=0)
         + [O("cylinder", (0, 0.74, -1.2), [1.2, 0.04, 1.2], "#f8f9fa", material="fabric"), O("cylinder", (0, 0.38, -1.2), [0.12, 0.74, 0.12], "#212529"),
            O("cylinder", (0, 0.78, -0.75), [0.36, 0.02, 0.36], "#ffffff", material="ceramic"), O("cylinder", (0.15, 0.85, -1.4), [0.04, 0.16, 0.04], "#f8f9fa"),
            O("cylinder", (0.15, 0.95, -1.4), [0.02, 0.05, 0.02], "#ffb347", material="glow")]
         + table((-2.8, 0, -4), 1.0, 1.0, 0.75, "#f8f9fa", tex=None) + table((2.8, 0, -4.2), 1.0, 1.0, 0.75, "#f8f9fa", tex=None)
         + [lamp((0, 1.1, -1.4), "#ffb347", 3, 3.5), lamp((0, 2.6, -3.5), "#ffd8a8", 6, 9)])
    return o + list(extra)


def airport_gate(seed=1, extra=()):
    """[~30] Airport gate: rows of seats, big window with a plane outside, departures board, gate sign."""
    o = (room(14, 12, 4.0, -8, "#e9ecef", "#8d99ae", "carpet", "paint", panels=4, side_walls=False)
         + [O("plane", (0, 2.0, -7.9), [13, 3.6, 1], "#bfe0ff", material="emit"), O("box", (0, 0.2, -12), [80, 0.1, 60], "#6c757d", tex="concrete"),
            O("box", (2, 2.2, -16), [3, 2.6, 18], "#f1f3f5", material="glossy", rotate=[0, 70, 0]), O("box", (2, 2.4, -16), [18, 0.3, 3], "#f1f3f5", material="glossy", rotate=[0, 70, 0]),
            screen_panel((-4.0, 2.9, -7.6), 2.4, 0.9, screen_ui(app="DEPARTURES", lines=["NYC  DELAYED", "LAX  DELAYED", "MIA  CANCELLED"], bg="#0b1a33", fg="#ffd43b")),
            text((4.5, 3.2, -7.6), "GATE B12", 1.6, 0.5, bg="#ffd43b", fg="#111111")])
    for z in (-2.0, -3.6):
        o += [O("box", (-2.2, 0.42, z), [3.2, 0.08, 0.5], "#343a40", material="plastic"), O("box", (-2.2, 0.7, z - 0.25), [3.2, 0.5, 0.06], "#343a40", material="plastic"),
              O("box", (2.2, 0.42, z), [3.2, 0.08, 0.5], "#343a40", material="plastic"), O("box", (2.2, 0.7, z - 0.25), [3.2, 0.5, 0.06], "#343a40", material="plastic")]
    return o + list(extra)


def classroom_real(seed=1, wall="#ece6d6", extra=()):
    """[~35] Real classroom from a student desk: whiteboard with words, teacher's desk, other students' desks + backs."""
    o = room(9, 10, 3.0, -7, wall, "#c4a27c", "tiles", "paint", panels=3)
    o += [O("box", (0, 1.55, -6.92), [3.6, 1.2, 0.04], "#ffffff", material="glossy"), text((0, 1.6, -6.88), "QUIZ TODAY", 2.4, 0.45, bg="#ffffff", fg="#1c7ed6", font='"Comic Sans MS", cursive', weight=700)]
    o += table((2.4, 0, -5.6), 1.4, 0.7, 0.76, "#8b6a4a")
    o += table((0, 0, 0.55), 0.7, 0.5, 0.72, "#d9b98c", tex="planks")   # your desk
    for x in (-1.5, 0, 1.5):
        for z in (-1.4, -3.2):
            o += table((x, 0, z), 0.7, 0.5, 0.72, "#d9b98c")[:1]
    return o + list(extra)


# ── holiday / home props (added with the Thanksgiving Short) ──
def roast_turkey(at, size=1.0, frozen=False, platter=True):
    """[5-7] Roast turkey on a platter (frozen=True: pale, icy, rock-hard)."""
    x, y, z = at
    s = size
    c = "#e8eef3" if frozen else "#b8652a"
    m = "glossy" if frozen else "glossy"
    o = [O("sphere", (x, y + 0.12 * s, z), [0.22 * s, 0.13 * s, 0.17 * s], c, material=m),
         *_pair("sphere", (x, y + 0.1 * s, z + 0.12 * s), 0.12 * s, [0.07 * s, 0.06 * s, 0.11 * s], c, material=m),
         *_pair("cylinder", (x, y + 0.12 * s, z + 0.25 * s), 0.12 * s, [0.025 * s, 0.07 * s, 0.025 * s], "#f8f9fa", rotate=[70, 0, 0])]
    if platter:
        o.insert(0, O("cylinder", (x, y + 0.01, z), [0.62 * s, 0.025, 0.46 * s], "#f8f9fa", material="ceramic"))
    if frozen:
        o.append(O("particles", (x, y + 0.3 * s, z), 0.012, "#e7f5ff", count=12, seed=3, spread=[0.4 * s, 0.25 * s, 0.3 * s]))
    return o


def oven(at, on=False, smoke=False, ry=0):
    """[4-6] Kitchen oven (glowing window when on, smoke pouring out when smoke=True)."""
    x, y, z = at
    o = [O("box", (x, y + 0.45, z), [0.76, 0.9, 0.65], "#ced4da", material="metal", rotate=[0, ry, 0]),
         O("box", (x, y + 0.42, z + 0.33), [0.56, 0.36, 0.02], "#ff8c2b" if on else "#212529", material="emit" if on else "glossy", rotate=[0, ry, 0]),
         O("box", (x, y + 0.7, z + 0.36), [0.6, 0.03, 0.03], "#adb5bd", material="chrome"),
         O("box", (x, y + 0.86, z + 0.3), [0.7, 0.08, 0.05], "#343a40")]
    if smoke:
        o += smoke_cloud((x, y + 1.0, z + 0.4))
    return o


def smoke_cloud(at, count=26, seed=5, color="#868e96"):
    """[1] Rising grey smoke puffs."""
    x, y, z = at
    return [O("sphere", (x, y + 0.5, z), 0.18, color, count=count, seed=seed, spread=[1.0, 1.0, 0.8], opacity=0.55,
              animate=[{"type": "move", "to": [0, 0.8, 0.3], "rel": True}, {"type": "pulse", "amount": 0.3}])]


def front_door(at=(0, 0, -2.2), color="#7b2d26", wall="#e9e2d6", night=False):
    """[~8] Front door seen from inside the hallway, open onto the porch (put the guest at (0,0,at_z-0.6))."""
    x, y, z = at
    return [O("box", (x, -0.05, z + 1.5), [4, 0.1, 5], "#a77b52", tex="planks", texRep=[4, 5]),
            O("box", (x - 1.35, 1.4, z), [1.8, 2.8, 0.15], wall, tex="paint", cast=False), O("box", (x + 1.35, 1.4, z), [1.8, 2.8, 0.15], wall, tex="paint", cast=False),
            O("box", (x, 2.6, z), [0.9, 0.4, 0.15], wall, cast=False),
            O("box", (x + 0.75, 1.05, z + 0.4), [0.06, 2.1, 0.9], color, material="paint", rotate=[0, 0, 0]),
            O("box", (x, -0.03, z - 2), [12, 0.06, 4], "#8d99ae", tex="concrete"),
            O("box", (x, 3, z - 9), [30, 6, 1], "#9ac0e0" if not night else "#1b2a4a", material="emit" if not night else "matte"),
            O("blob_tree", (x - 3, 0, z - 6), 1.6, "#5c940d")]


def dining_table(at=(0, 0, -1.8), length=2.6, cloth="#f1e3c8", food=True):
    """[~12] Long dinner table with tablecloth, plates, glasses (runs along −z)."""
    x, y, z = at
    o = table(at, 1.1, length, 0.76, "#6b4f36") + [O("box", (x, y + 0.775, z), [1.16, 0.01, length + 0.06], cloth, material="fabric", tex="fabric", texRep=[1.2, length])]
    for k in range(3):
        zz = z - length / 2 + 0.45 + k * (length - 0.9) / 2
        o += [O("cylinder", (x - 0.35, y + 0.79, zz), [0.26, 0.015, 0.26], "#ffffff", material="ceramic"), O("cylinder", (x + 0.35, y + 0.79, zz), [0.26, 0.015, 0.26], "#ffffff", material="ceramic")]
    if food:
        o += [O("cylinder", (x, y + 0.82, z - 0.3), [0.22, 0.08, 0.22], "#f08c00", material="ceramic"), O("cylinder", (x, y + 0.82, z + 0.35), [0.2, 0.06, 0.2], "#2f9e44", material="ceramic")]
    return o


# ── retail props/places (added with the Black Friday Short) ──
def glass_doors(at=(0, 0, -2.6), sign="DOORBUSTER 5 AM", open_=0.0, night=True):
    """[~9] Store entrance seen from inside: two sliding glass doors in a glass front, red sale banner above, dark car park outside.
    open_=0..1 slides the doors apart over the beat (crowd outside at z≈at_z-0.6)."""
    x, y, z = at
    mv = lambda dx: [{"type": "move", "to": [dx, 0, 0], "rel": True, "delay": 0.15, "dur": 0.9}] if open_ else []
    o = [O("box", (x, -0.05, z + 2.0), [8, 0.1, 5], "#d6d3cc", tex="tiles", texRep=[8, 5]),
         O("box", (x, -0.04, z - 4.0), [30, 0.08, 8], "#2f3237", tex="asphalt", texRep=[30, 8]),
         O("box", (x - 2.6, 1.4, z), [3.2, 2.8, 0.06], "#cfe3f0", material="glass", opacity=0.12, cast=False),
         O("box", (x + 2.6, 1.4, z), [3.2, 2.8, 0.06], "#cfe3f0", material="glass", opacity=0.12, cast=False),
         O("box", (x - 0.5, 1.15, z + 0.05), [1.0, 2.3, 0.04], "#cfe3f0", material="glass", opacity=0.1, cast=False, animate=mv(-0.95 * open_)),
         O("box", (x + 0.5, 1.15, z + 0.05), [1.0, 2.3, 0.04], "#cfe3f0", material="glass", opacity=0.1, cast=False, animate=mv(0.95 * open_)),
         O("box", (x, 2.55, z + 0.02), [8, 0.5, 0.14], "#343a40", material="metal"),
         text((x, 2.55, z + 0.11), sign, 2.6, 0.42, bg="#e03131", fg="#ffffff", lit=1.2),
         O("box", (x, 3, z - 12), [40, 6, 1], "#16203a" if night else "#9ac0e0", material="matte" if night else "emit")]
    if night:
        o.append(lamp((x, 2.2, z - 1.6), "#ffd8a8", 5, 6, hidden=True))
    return o


def tv_wall(at=(0, 0, -3.4), cols=4, rows=2, empty=None, seed=1):
    """[~12] Electronics-aisle display wall: grid of glowing TVs on a dark wall. empty=[(c, r), ...] leaves gaps (sold out)."""
    x, y, z = at
    r = random.Random(seed)
    o = [O("box", (x, 1.5, z - 0.05), [cols * 1.15 + 0.4, 3.0, 0.1], "#212529", material="paint")]
    pics = [("📺", "#1c7ed6"), ("⚽", "#2b8a3e"), ("🦖", "#e8590c"), ("🎮", "#7048e8"), ("🌋", "#c92a2a"), ("🐧", "#1098ad")]
    for c in range(cols):
        for rw in range(rows):
            if empty and (c, rw) in empty:
                o.append(text((x + (c - (cols - 1) / 2) * 1.15, 0.95 + rw * 0.75, z + 0.01), "SOLD OUT", 0.8, 0.2, bg="#fff3bf", fg="#c92a2a"))
                continue
            em, col = pics[r.randrange(len(pics))]
            o.append(screen_panel((x + (c - (cols - 1) / 2) * 1.15, 0.95 + rw * 0.75, z + 0.01), 1.0, 0.58, screen_ui(big=em, bg=col, fg="#ffffff")))
    return o


def box_stack(at, n=6, seed=1, color="#c8a27a"):
    """[n+1] Stockroom pile of cardboard boxes (deterministic) + a metal shelf behind."""
    x, y, z = at
    r = random.Random(seed * 31 + 5)
    o = [O("box", (x, 1.1, z - 0.45), [2.2, 2.2, 0.08], "#868e96", material="metal")]
    for i in range(n):
        w, h = 0.45 + r.random() * 0.3, 0.32 + r.random() * 0.2
        col, row = i % 3, i // 3
        o.append(O("box", (x + (col - 1) * 0.72 + (r.random() - 0.5) * 0.08, y + h / 2 + row * 0.55, z + (r.random() - 0.5) * 0.15), [w, h, 0.5], color,
                   material="matte", rotate=[0, (r.random() - 0.5) * 14, 0]))
    return o


def parking_lot(seed=1, extra=()):
    """[~40] Store car park at dusk: striped bays, parked cars, stray shopping carts, store front with a lit sign behind (−z)."""
    o = [O("box", (0, -0.05, -10), [40, 0.1, 40], "#3a3d42", tex="asphalt", texRep=[40, 40])]
    o += [O("box", (x, 0.004, -5.5), [0.12, 0.01, 4.5], "#f8f9fa", material="paint") for x in (-4.5, -2.0, 0.5, 3.0, 5.5)]
    o += building((0, 0, -17), 22, 7, 6, "#d8d0c2", tex="concrete", shop="#fff4d6", seed=seed)
    o += [text((0, 5.2, -13.9), "MEGAMART", 5.0, 1.1, bg="#c92a2a", fg="#ffffff", lit=1.5)]
    o += car_real((-3.25, 0, -6), "#adb5bd") + car_real((4.25, 0, -6.5), "#1c7ed6")
    o += shopping_cart((1.8, 0, -2.6), ry=35, full=False) + shopping_cart((-1.6, 0, -9.5), ry=-60, full=False)
    o += street_lamp((-6, 0, -3), on=True)
    return o + list(extra)


# ── office extras (added with the reply-all Short) ──
def server_rack(at, ry=0, units=8):
    """[~units+2] IT-department server rack with blinking green/blue LEDs."""
    x, y, z = at
    o = [O("box", (x, y + 1.0, z), [0.65, 2.0, 0.8], "#1b1e22", material="metal", rotate=[0, ry, 0])]
    for i in range(units):
        o.append(O("box", (x, y + 0.25 + i * 0.22, z + 0.41), [0.56, 0.16, 0.02], "#343a40", material="plastic", rotate=[0, ry, 0]))
        o.append(O("sphere", (x + 0.2, y + 0.25 + i * 0.22, z + 0.43), 0.018, "#51cf66" if i % 3 else "#4dabf7", material="emit",
                   animate=[{"type": "pulse", "amount": 0.6, "speed": 3 + i}]))
    return o


def bathroom_stall(extra=()):
    """[~12] Inside an office bathroom stall, facing the closed door (−z): tiled floor/walls, toilet-roll holder, coat hook, a door sign."""
    return [O("box", (0, -0.05, -0.4), [1.6, 0.1, 2.4], "#dee2e6", tex="tiles", texRep=[1.6, 2.4]),
            O("box", (0, 1.05, -1.25), [1.05, 1.9, 0.04], "#748ffc", material="paint"),
            O("box", (-0.72, 1.05, -0.5), [0.04, 1.9, 1.6], "#748ffc", material="paint"),
            O("box", (0.72, 1.05, -0.5), [0.04, 1.9, 1.6], "#748ffc", material="paint"),
            O("box", (0, 1.4, -1.6), [3, 2.8, 0.05], "#f1f3f5", tex="tiles", texRep=[3, 2.8], cast=False),
            O("box", (0.38, 1.0, -1.22), [0.06, 0.12, 0.04], "#adb5bd", material="chrome"),
            O("cylinder", (0, 1.75, -1.2), [0.03, 0.08, 0.03], "#adb5bd", material="chrome", rotate=[90, 0, 0]),
            O("cylinder", (0.66, 0.75, -0.6), [0.12, 0.11, 0.12], "#ffffff", rotate=[0, 0, 90]),
            text((0, 1.45, -1.22), "PLEASE DO NOT\nHIDE IN HERE ALL DAY", 0.7, 0.3, bg="#ffffff", fg="#212529", weight=700),
            O("box", (0, 2.6, -0.5), [1.6, 0.04, 2.4], "#f8f9fa", material="emit")] + list(extra)
