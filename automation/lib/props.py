import json
def O(kind, at, scale=1, color="#d8d8d8", **kw):
    d = {"kind": kind, "at": list(at), "scale": scale if isinstance(scale, (int, float)) else list(scale), "color": color}
    d.update(kw); return d
def add(a, b): return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]
FADE = [{"type": "fade_out"}]
def S(objs, bg, ground="plane", gc="#3c4a32", focus=(0,1.5,0), zoom=1.6, amb="forest", light=2.6, ambient=1.0, fog=None):
    assert len(objs) <= 40, len(objs)
    s = {"background": bg, "ground": ground, "ground_color": gc, "focus": list(focus), "zoom": zoom, "ambience": amb,
         "light_intensity": light, "ambient": ambient, "objects": objs}
    if fog: s["fog"] = fog
    return {"set": s}
# ---------- palettes
DAY = ["#5d86ad", "#c9d8e2"]; GOLDEN = ["#2c3e5c", "#e0a46a"]; DUSK = ["#141c2e", "#6b5068"]; NIGHT = ["#0b1220", "#263650"]
OVERCAST = ["#59636d", "#a9b1b8"]; SEA = ["#0d2a3f", "#2f6f8f"]; DEEP = ["#03121e", "#0b3550"]; LAB = ["#161b22", "#2d3644"]
GRASS = "#4f6b3a"; DRY = "#8a7a4a"; SOIL = "#4a3626"
# ---------- props
def animal(at, s=1.0, col="#8d6e57", head=None, neck=0.0, ry=0, anim=()):
    a = list(anim); leg = 0.7*s
    p = [O("box", add(at,(0, leg+0.35*s, 0)), [1.6*s, 0.75*s, 0.7*s], col, rotate=[0,ry,0], animate=a)]
    for x in (-0.6, 0.6):
        for z in (-0.25, 0.25):
            p.append(O("cylinder", add(at,(x*s, leg/2, z*s)), [0.18*s, leg, 0.18*s], col, animate=a))
    hy = leg + 0.6*s + neck*s
    if neck:
        p.append(O("cylinder", add(at,(0.8*s, leg+0.4*s+neck*s/2, 0)), [0.22*s, neck*s, 0.22*s], col, animate=a))
    p.append(O("box", add(at,(0.95*s if not neck else 0.95*s, hy, 0)), [0.55*s, 0.4*s, 0.4*s], head or col, animate=a))
    return p
def elephant(at, anim=()):
    a = list(anim); return animal(at, 1.9, "#8c8f94", anim=a) + [O("cylinder", add(at,(2.15,1.4,0)), [0.22,1.2,0.22], "#8c8f94", rotate=[0,0,-12], animate=a)]
def giraffe(at, anim=()): return animal(at, 1.1, "#d9a94e", neck=1.9, anim=anim)
def zebra(at, anim=()): return animal(at, 1.0, "#e9ecef", head="#343a40", anim=anim)
def cow(at, anim=()): return animal(at, 1.15, "#f1f3f5", head="#3d2b1f", anim=anim)
def dog(at, anim=(), col="#c08552"): return animal(at, 0.45, col, anim=anim)
def birds(at, n=24, spread=(14,4,8), seed=2, anim=FADE, col="#2b2f36"):
    return O("cone", at, [0.14,0.45,0.14], col, rotate=[0,0,90], count=n, seed=seed, spread=list(spread),
             animate=[{"type":"drift","axis":"x","amount":0.25}] + list(anim))
def insects(at, n=6, spread=(8,3,6), seed=3, anim=FADE, col="#2b2f36"):
    return O("particles", at, 0.35, col, count=n, seed=seed, spread=list(spread), animate=[{"type":"drift","axis":"y","amount":0.05}] + list(anim))
def fish(at, n=30, spread=(14,5,8), seed=4, col="#ffa94d", anim=FADE):
    return O("cone", at, [0.3,0.9,0.22], col, material="glossy", rotate=[0,0,90], count=n, seed=seed, spread=list(spread),
             animate=[{"type":"drift","axis":"x","amount":0.3}] + list(anim))
def whale(at, anim=()):
    a = list(anim)
    return [O("capsule", at, [3,6,3], "#46576b", material="glossy", rotate=[0,0,90], animate=a+[{"type":"bob","amount":0.3,"speed":0.3}]),
            O("cone", add(at,(-4.4,0.2,0)), [2.6,1.4,0.4], "#46576b", rotate=[0,0,90], animate=a+[{"type":"bob","amount":0.3,"speed":0.3}])]
def trees(at=(0,0,-6), n=14, spread=(26,0,14), seed=5, s=1.2, col="#3f6b3a", anim=()):
    return O("tree", at, s, col, count=n, seed=seed, spread=list(spread), animate=list(anim))
def flower(at, col="#f783ac", s=1.0, anim=()):
    a = list(anim)
    return [O("cylinder", add(at,(0,0.5*s,0)), [0.06*s,1.0*s,0.06*s], "#4f8a3a", animate=a),
            O("sphere", add(at,(0,1.05*s,0)), 0.14*s, "#ffd43b", animate=a),
            O("torus", add(at,(0,1.05*s,0)), [0.28*s,0.28*s,0.6*s], col, rotate=[90,0,0], animate=a)]
def bee(at, anim=()):
    a = list(anim)
    return [O("sphere", at, [0.22,0.15,0.15], "#fab005", material="glossy", animate=a),
            O("box", add(at,(0,0,0)), [0.07,0.31,0.31], "#212529", animate=a),
            O("sphere", add(at,(0,0.15,0)), [0.12,0.03,0.2], "#e7f5ff", material="glass", opacity=0.6, animate=a)]
def blossom_tree(at, col="#ffdeeb", s=1.0, fruit=None, anim=()):
    a = list(anim)
    p = [O("cylinder", add(at,(0,1.0*s,0)), [0.3*s,2.0*s,0.3*s], "#6b4f3a"),
         O("sphere", add(at,(0,2.6*s,0)), [1.5*s,1.2*s,1.5*s], col, animate=a)]
    if fruit:
        p.append(O("sphere", add(at,(0,2.6*s,0)), 0.16*s, fruit, material="glossy", count=10, seed=int(at[0]*7+11)%97+1, spread=[2.4*s,1.8*s,2.4*s], animate=a))
    return p
def barn(at):
    return [O("box", add(at,(0,1.5,0)), [4,3,3], "#9c3b2f"), O("cone", add(at,(0,3.8,0)), [5.2,1.6,4.0], "#5b2a22")]
def fence(z, x0=-10, x1=10):
    return [O("box", ((x0+x1)/2, 0.8, z), [x1-x0, 0.1, 0.1], "#8d6e57"), O("box", ((x0+x1)/2, 0.4, z), [x1-x0, 0.1, 0.1], "#8d6e57")]
def house(at, col="#ced4da", roof="#7a4a3a"):
    return [O("box", add(at,(0,1.1,0)), [2.6,2.2,2.4], col), O("cone", add(at,(0,2.9,0)), [3.6,1.4,3.4], roof)]
def worms(n=8, anim=FADE, at=(0,-1.2,-0.25)):
    return O("capsule", at, [0.14,0.7,0.14], "#e8a0a0", material="glossy", rotate=[0,0,70], count=n, seed=9, spread=[8,2,0.1], animate=list(anim))
def mushroom(at, s=1.0, col="#e9d8c4"):
    return [O("cylinder", add(at,(0,0.25*s,0)), [0.15*s,0.5*s,0.15*s], "#f1f3f5"), O("sphere", add(at,(0,0.52*s,0)), [0.42*s,0.2*s,0.42*s], col)]
def coral(at, n=10, seed=6, anim=()):
    cols = ["#ff8787", "#ffa94d", "#f783ac", "#da77f2", "#ffd43b"]
    return [O("cylinder", at, [0.3,1.4,0.3], cols[i % 5], count=n, seed=seed+i, spread=[10,0.5,6], animate=list(anim)) for i in range(3)] + \
           [O("sphere", at, 0.6, cols[(i+2) % 5], count=n, seed=seed+10+i, spread=[10,0.4,6], animate=list(anim)) for i in range(2)]
def bleached(at, n=10, seed=6, anim=()):
    return [O("cylinder", at, [0.3,1.4,0.3], "#e9ecef", count=n, seed=seed+i, spread=[10,0.5,6], animate=list(anim)) for i in range(3)] + \
           [O("sphere", at, 0.6, "#dee2e6", count=n, seed=seed+10+i, spread=[10,0.4,6], animate=list(anim)) for i in range(2)]
def crowd(at=(0,0,2), n=14, spread=(10,0,6), seed=3, outfit="casual", action="idle", anim=()):
    return O("person", at, 1.0, outfit=outfit, action=action, count=n, seed=seed, spread=list(spread), animate=list(anim))
def drone(at, anim=()):
    a = list(anim)
    p = [O("box", at, [0.5,0.15,0.5], "#343a40", material="metal", animate=a)]
    for x, z in [(-0.35,-0.35),(0.35,-0.35),(-0.35,0.35),(0.35,0.35)]:
        p.append(O("cylinder", add(at,(x,0.1,z)), [0.4,0.02,0.4], "#adb5bd", material="glass", opacity=0.6, animate=a+[{"type":"spin","speed":20}]))
    return p
def shelf_row(x, z, cols, anim_idx=(), h=3):
    p = [O("box", (x, h/2, z), [3, h, 0.7], "#adb5bd", material="metal")]
    for j, c in enumerate(cols):
        an = [{"type": "shrink"}] if j in anim_idx else []
        p.append(O("box", (x, 0.5 + j*0.9, z-0.42), [2.6, 0.5, 0.25], c, animate=an))
    return p
savanna = lambda anim=(): elephant((-6,0,-4), anim) + giraffe((2,0,-7), anim) + zebra((5,0,-2), anim) + zebra((7,0,-4), anim) + zebra((-1,0,-1), anim)
acacia = [O("cylinder", (x,1.5,z), [0.3,3,0.3], "#6b4f3a") for x, z in [(-10,-10),(9,-12)]] + \
         [O("cylinder", (x,3.2,z), [4.5,0.6,4.5], "#5f7a3a") for x, z in [(-10,-10),(9,-12)]]

