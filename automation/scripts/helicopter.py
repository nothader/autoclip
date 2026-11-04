"""Why do helicopters crash? Fresh world: rocky coastline at golden hour, a red-and-white helicopter, ocean, cliffs.
Hook type: curiosity close-up (the "Jesus nut") pulling out to reveal. Facts (widely cited): the main rotor's torque would spin the
body the other way, the tail rotor counters it; tail-rotor failure makes the body spin; wire strikes are a classic low-flying
hazard; flying into cloud causes spatial disorientation (inner ear feels level while turning), a leading cause of fatal crashes;
vortex ring state = sinking into your own downwash; autorotation lets a helicopter land after engine failure (like a maple seed)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403

v = Video()
GOLDEN = ["#2b4f7a", "#ffb36b"]; TEAL = ["#1f6f8b", "#bfe9e4"]; STORM = ["#3d4a5c", "#9aa8b5"]; FOG = ["#9aa3ad", "#d8dde2"]; WARM = ["#5a3a6b", "#ffcf8a"]
RED, WHITE = "#d9480f", "#f8f9fa"


def heli(at, rotor=24.0, anim=(), tail=True):
    x, y, z = at
    a = list(anim)
    p = [O("capsule", (x, y, z), [2.6, 3.6, 2.4], RED, material="glossy", rotate=[90, 0, 0], animate=a),
         O("sphere", (x, y + 0.2, z - 1.9), [1.3, 1.1, 1.2], "#a5d8ff", material="glass", opacity=0.55, animate=a),
         O("box", (x, y + 0.2, z + 4.2), [0.35, 0.35, 5.0], WHITE, animate=a),
         O("box", (x, y + 1.6, z), [0.25, 0.9, 0.25], "#495057", material="metal", animate=a),
         O("box", (x, y + 2.05, z), [11, 0.06, 0.45], "#343a40", animate=a + [{"type": "spin", "axis": "y", "speed": rotor}]),
         O("box", (x, y + 2.05, z), [0.45, 0.06, 11], "#343a40", animate=a + [{"type": "spin", "axis": "y", "speed": rotor}]),
         O("box", (x - 0.9, y - 1.5, z), [0.12, 0.12, 4.0], "#495057", animate=a), O("box", (x + 0.9, y - 1.5, z), [0.12, 0.12, 4.0], "#495057", animate=a)]
    if tail:
        p += [O("box", (x + 0.3, y + 0.5, z + 6.6), [0.05, 2.2, 0.25], "#343a40", animate=a + [{"type": "spin", "axis": "x", "speed": rotor * 1.5}]),
              O("box", (x, y + 0.9, z + 6.5), [0.15, 1.2, 0.9], RED, animate=a)]
    return p


def coast(extra=(), sea="#1c6e9c"):
    return [O("box", (0, -0.6, -40), [600, 0.2, 600], sea, material="glossy", animate=[{"type": "bob", "amount": 0.1, "speed": 0.5}]),
            O("box", (-60, 6, -60), [70, 12, 120], "#8a7556"), O("box", (-60, 12.3, -60), [70, 0.6, 120], "#5c7a3e"),
            O("rock", (-24, 2, -40), 5, "#6b5a48", count=10, seed=4, spread=[10, 2, 80]),
            O("box", (40, 0, -10), [60, 0.4, 40], "#e8d4a2")] + list(extra)


def SV(objs, bg, focus=(0, 1.0, 0), zoom=1.0, amb="wind"):
    e = V(objs, bg, focus=focus, zoom=zoom, amb=amb)
    e["set"]["sky_detail"] = "auto"
    return e


PILOT = lambda at, act="sit", ry=0: P(at, "#343a40", act, 17, outfit="police", ry=ry, skin="#8d5524")
nut = [O("cylinder", (0, 0, 0), [0.5, 0.35, 0.5], "#adb5bd", material="metal", animate=[{"type": "spin", "axis": "y", "speed": 4}]),
       O("cylinder", (0, -1.5, 0), [0.3, 2.6, 0.3], "#868e96", material="metal"),
       O("box", (0, 0.05, 0), [9, 0.08, 0.6], "#343a40", animate=[{"type": "spin", "axis": "y", "speed": 4}])]
v.B(4.4, "closeup", "This one nut holds a whole helicopter in the sky. Pilots call it the Jesus nut.", SV(nut, GOLDEN, focus=(0, -0.3, 0), zoom=0.7),
    "THE TOP OF THE ROTOR", move="pull_out", sfx=[{"type": "whoosh", "at": 0.4, "dur": 3.0, "gain": 0.6}])
v.B(3.8, "side", "So why do helicopters crash? It's usually not what you think.", SV(coast(heli((0, 14, -20))), GOLDEN, focus=(0, 14, -20), zoom=5.0, amb="ocean"),
    "THE COAST", move="fly_by", transition="whip")
v.B(3.8, "far", "The big rotor pushes the body to spin. The tiny tail rotor stops it.", SV(coast(heli((0, 12, -20))), TEAL, focus=(0, 12, -20), zoom=1.3,
    amb="ocean"), "HOW IT FLIES", tooltip={"label": "PHYSICS", "text": "Spin one way, and the body wants to spin the other way. That's torque."})
spin = [{"type": "wobble", "axis": "y", "amount": 1.6, "speed": 3}]
v.B(3.8, "side", "Reason #1: the tail rotor fails. Now the whole helicopter starts to spin.", SV(coast(heli((0, 10, -20), anim=spin, tail=False)), TEAL, focus=(0, 10, -20),
    zoom=4.0, amb="ocean"), "TAIL ROTOR FAILURE", move="spiral", effects=["shake", "dizzy"], sfx=[{"type": "alarm", "at": 0.3, "dur": 2.4, "gain": 0.5}])
poles = [O("cylinder", (-14, 9, -24), [0.5, 18, 0.5], "#6b4f3a"), O("cylinder", (14, 9, -24), [0.5, 18, 0.5], "#6b4f3a"),
         O("box", (0, 17.5, -24), [28, 0.06, 0.06], "#212529"), O("box", (0, 16.6, -24), [28, 0.06, 0.06], "#212529")]
v.B(3.8, "low_front", "Reason #2: wires. From the air, power lines are almost invisible.", SV(coast(poles + heli((0, 16, -32), anim=[{"type": "move", "to": [0, 16, -26]}])),
    WARM, focus=(0, 15, -26), zoom=5.0, amb="wind"), "WIRE STRIKE", transition="zoom", effects=["tunnel"])
cloud = [O("sphere", (0, 10, -34), [18, 8, 18], "#e9ecef", opacity=0.3, count=8, seed=5, spread=[40, 6, 10], animate=[{"type": "drift", "axis": "x", "amount": 1}])]
v.B(3.8, "side", "Reason #3, the deadliest: clouds. Inside one, you can't tell up from down.", SV(coast(cloud + heli((0, 10, -20))), FOG, focus=(0, 10, -20), zoom=4.0),
    "FLYING INTO CLOUD", transition="dip", effects=["darken"])
cockpit = [O("box", (0, -0.02, -1), [3, 0.04, 3], "#343a40"), O("box", (0, 0.9, -2.0), [2.4, 0.5, 0.3], "#212529"),
           O("plane", (0, 0.95, -1.84), [0.5, 0.35, 1], "#69db7c", material="glow"), O("plane", (0.7, 0.95, -1.84), [0.5, 0.35, 1], "#4dabf7", material="glow",
           animate=[{"type": "spin", "axis": "z", "speed": 1.2}]), O("sphere", (0, 1.6, -3.5), [4, 2, 1], "#dee2e6", opacity=0.9), PILOT((0, 0, -0.2), "sit", 0)]
v.B(4.0, "closeup", "Your inner ear says you're flying level. But you're turning, and dropping.", SV(cockpit, FOG, focus=(0, 1.2, -0.4), zoom=0.8),
    "INSIDE THE CLOUD", effects=["dizzy", "tunnel"], sfx=[{"type": "heartbeat", "at": 0.3, "dur": 3.4, "gain": 0.8}],
    tooltip={"label": "REAL", "text": "Pilots call it spatial disorientation."})
wash = [O("particles", (0, 4, -20), 0.6, "#e7f5ff", count=40, seed=6, spread=[14, 8, 14], animate=[{"type": "orbit", "amount": 3, "speed": 2}])]
v.B(3.8, "side", "Reason #4: come down too fast, and a helicopter can sink into its own wind.", SV(coast(wash + heli((0, 8, -20), anim=[{"type": "move", "to": [0, 4, -20]}])),
    STORM, focus=(0, 6, -20), zoom=4.5, amb="wind"), "VORTEX RING STATE", effects=["shake"], transition="whip")
v.B(3.6, "front", "Here's the twist: if the engine dies, it's not over.", SV(coast(heli((0, 14, -20), rotor=10)), WARM, focus=(0, 14, -20), zoom=4.0, amb="ocean"),
    "ENGINE FAILURE", sfx=[{"type": "drop", "at": 0.3, "gain": 0.6}])
seed_ = [O("cone", (-4, 12, -14), [0.25, 1.4, 0.1], "#c97a40", rotate=[0, 0, 70], animate=[{"type": "spin", "axis": "y", "speed": 8},
         {"type": "move", "to": [-4, 2, -14]}])]
v.B(4.0, "side", "Air rushing up spins the blades, like a maple seed. It glides down and lands.",
    SV(coast(seed_ + heli((4, 14, -20), rotor=16, anim=[{"type": "move", "to": [12, 2.2, -12]}])), GOLDEN, focus=(8, 8, -16), zoom=5.0, amb="ocean"),
    "AUTOROTATION", stat={"value": "AUTOROTATION", "label": "EVERY PILOT PRACTICES THIS", "count_up": False})
v.B(4.0, "far", "Would you still ride in one?", SV(coast(heli((12, 2.2, -12), rotor=6) + [PILOT((15, 0.2, -10), "point", 270)]), WARM,
    focus=(12, 2, -12), zoom=1.0, amb="ocean"), "SAFE ON THE SAND", move="pull_out", effects=["rays"])
v.save("helicopter", "Why do helicopters crash?", "The real reasons helicopters crash: tail-rotor failure, wires, clouds and vortex ring state, and why an engine failure isn't the end.",
       "film", "", ["WOULD YOU STILL", "RIDE ONE?"], "WHY *HELICOPTERS* FALL", 1, accent="#ff922b")
