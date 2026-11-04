"""What if you could leave your body? (our own version of the astral-projection POV). Block POV format.
Anchor (widely cited): about 1 in 10 people say they have had at least one out-of-body experience. Everything else is the fantasy."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, NIGHT, DAY, INDOOR, DUSK, GOLDEN  # noqa: E402
from places import bedroom, living_room, street  # noqa: E402

s = Story()
GHOST = {"pose": "float"}
ME = guy((0, 0.45, 0.9), "#3b5bdb", "#25324a", act="lie", face="neutral", seed=201, ry=0)

s.B(3.8, "eyes", "", env(bedroom(seed=3), NIGHT, eye=(0, 1.0, 1.4), amb="room", ambient=1.1), tracker=T("HOME", clock="3:30:02 AM", sub="YOUR BEDROOM"),
    hands={"pose": "idle"}, gaze=(0, -6))
s.B(3.4, "eyes", "3:30 AM. You can't move. But you're awake.", env(bedroom(seed=3), NIGHT, eye=(0, 1.0, 1.4), amb="room", ambient=1.0),
    hands={"pose": "none"}, gaze=(0, 10), effects=["darken"], sfx=[{"type": "heartbeat", "at": 0.2, "dur": 3.0, "gain": 0.7}])
s.B(3.4, "eyes", "Then you start to float.", env(bedroom(seed=3, extra=[ME]), NIGHT, eye=(0, 2.75, 2.6), amb="room", ambient=1.2), head="float",
    hands=GHOST, gaze=(0, -42), effects=["bloom"], sfx=[{"type": "shimmer", "at": 0.3}])
s.B(3.4, "eyes", "Below you, your body is still sleeping.", env(bedroom(seed=3, extra=[ME]), NIGHT, eye=(0, 2.8, 2.3), amb="room", ambient=1.2),
    hands=GHOST, gaze=(0, -48), effects=["bloom"])
NEIGH = living_room(wall="#3d2f5c", tv="#5ad1ff", extra=[guy((0, 0.1, -1.0), "#e03131", "#212529", act="sit", face="smile", seed=202, ry=0),
                                                         O("box", (2.5, 0.4, -4.6), [0.6, 0.8, 0.6], "#212529")])
s.B(3.6, "eyes", "Walls don't stop you anymore.", env(NEIGH, NIGHT, eye=(0, 1.8, 1.2), amb="room", ambient=1.2), tracker=T("NEXT DOOR", clock="3:31:10 AM", sub="APARTMENT 4B"),
    hands=GHOST, gaze=(0, -14), head="float", effects=["bloom"])
s.B(3.2, "eyes", "Your neighbor is still gaming. He has no idea.", env(NEIGH, NIGHT, eye=(1.2, 1.6, 0.4), amb="room", ambient=1.2), hands=GHOST, gaze=(30, -20),
    voices=[("Come on, come on, one more round...", "am_eric", 0.3)])
s.B(3.4, "eyes", "You think of somewhere far away.", env([], ["#0b1020", "#1c2b52"], eye=(0, 1.6, 0), amb="wind"), hands=GHOST, effects=["tunnel", "bloom"],
    sfx=[{"type": "whoosh", "at": 0.2, "dur": 2.4}])
NEON = [O("plane", (-7.8, 6, -14), [3, 6, 1], c, material="glow", rotate=[0, 90, 0]) for c in ("#ff4d9a",)] + \
       [O("plane", (7.8, 7, -22), [3, 5, 1], "#4dd2ff", material="glow", rotate=[0, -90, 0]),
        O("box", (0, 0.02, -12), [10, 0.02, 0.6], "#f1f3f5", count=7, seed=2, spread=[0, 0, 8])]
s.B(3.6, "eyes", "And you're there. Instantly.", env(street(seed=11, people=60, cars=2, extra=NEON), DUSK, eye=(0, 4.5, 2), amb="calm"),
    tracker=T("TOKYO", clock="5:32:40 PM", sub="SHIBUYA CROSSING"), hands=GHOST, gaze=(0, -24), head="float", effects=["bloom"])
s.B(3.4, "eyes", "Three thousand people cross at once. Nobody sees you.", env(street(seed=11, people=90, cars=0, extra=NEON), DUSK, eye=(0, 1.8, -8), amb="calm"),
    hands=GHOST, gaze=(0, -6), head="float")
GALLERY = [O("box", (0, -0.02, -8), [10, 0.04, 22], "#8a6e52"), O("box", (-4, 2.5, -8), [0.1, 5, 22], "#e9e0d0"), O("box", (4, 2.5, -8), [0.1, 5, 22], "#e9e0d0"),
           O("box", (0, 5, -8), [8, 0.05, 22], "#d8cfbf"),
           O("plane", (-3.93, 2.0, -5), [1.4, 1.8, 1], "#c99a4f", material="glow", rotate=[0, 90, 0], count=4, seed=3, spread=[0, 0, 16]),
           O("plane", (3.93, 2.0, -7), [1.6, 1.2, 1], "#6f8fbf", material="glow", rotate=[0, -90, 0], count=4, seed=4, spread=[0, 0, 16]),
           O("box", (0, 0.25, -9), [2.0, 0.5, 0.6], "#5c4a3a"), O("box", (0, 1.0, -16), [0.8, 2.0, 0.8], "#f1ece4"),
           guy((2.4, 0, -12), "#25324a", "#25324a", act="walk", face="neutral", seed=203, ry=180)]
s.B(3.6, "eyes", "A famous museum, hours after closing.", env(GALLERY, INDOOR, eye=(0, 1.7, 1.0), amb="room", ambient=1.0, light=1.4),
    tracker=T("PARIS", clock="10:34:05 AM" if False else "11:34:05 PM", sub="THE GALLERY · CLOSED"), hands=GHOST, head="float", gaze=(0, -4))
s.B(3.4, "eyes", "The guard walks right through you.", env(GALLERY, INDOOR, eye=(2.2, 1.7, -9.5), amb="room", ambient=1.0, light=1.4), hands=GHOST, gaze=(0, -8),
    effects=["bloom"])
TOMB = [O("box", (0, -0.02, -6), [3, 0.04, 14], "#a1824f"), O("box", (-1.5, 2, -6), [0.2, 4, 14], "#b3925c"), O("box", (1.5, 2, -6), [0.2, 4, 14], "#b3925c"),
        O("box", (0, 3.0, -6), [3, 0.2, 14], "#9c7d4a", rotate=[0, 0, 0]), O("box", (0, 0.6, -11), [1.2, 1.2, 2.4], "#7a6040"),
        O("flame", (1.2, 1.6, -9), 0.25, "#ffb85c")]
s.B(3.6, "eyes", "The middle of the Great Pyramid. Total silence.", env(TOMB, ["#3a2a18", "#6b4f2c"], eye=(0, 1.6, 0.5), amb="wind", ambient=0.9, light=1.0),
    tracker=T("GIZA", clock="6:34:20 AM", sub="KING'S CHAMBER"), hands=GHOST, head="float", gaze=(0, -6))
ICE = [O("box", (0, -0.05, -30), [300, 0.1, 300], "#eef4fb"), O("box", (-6, 1.5, -18), [8, 3, 5], "#e8590c"), O("box", (6, 1.2, -24), [6, 2.4, 4], "#1c7ed6"),
       O("plane", (0, 40, -160), [200, 26, 1], "#4cf2a6", material="glow", opacity=0.22, animate=[{"type": "wobble", "amount": 0.05}]),
       O("plane", (30, 48, -170), [150, 18, 1], "#7c5cff", material="glow", opacity=0.18),
       guy((-3, 0, -14), "#e8590c", "#25324a", act="walk", face="neutral", seed=204, ry=180)]
s.B(3.6, "eyes", "Antarctica. Minus 60 degrees. You feel nothing.", env(ICE, ["#060b1c", "#1d2f55"], eye=(0, 3, 2), amb="wind", ambient=1.1, stars=True),
    tracker=T("ANTARCTICA", clock="4:34:41 PM", sub="RESEARCH STATION"), hands=GHOST, head="float", gaze=(0, -6))
DEEP = [O("box", (0, -0.05, -20), [200, 0.1, 200], "#2b3b45"), O("box", (2, 3, -16), [5, 4, 16], "#3d4a4f", rotate=[0, 25, 12]),
        O("cylinder", (2, 8, -14), [0.4, 6, 0.4], "#3d4a4f", rotate=[10, 0, 12]),
        O("particles", (0, 3, -10), 0.06, "#bfe9ff", count=120, seed=6, spread=[20, 8, 20]),
        O("sphere", (-4, 4, -12), [0.5, 0.2, 0.2], "#ffd43b", count=12, seed=7, spread=[8, 3, 6], animate=[{"type": "drift", "axis": "x", "amount": 0.4}])]
s.B(3.6, "eyes", "The bottom of the ocean. A ship nobody has found.", env(DEEP, ["#020a14", "#0a2f4a"], eye=(0, 3, 2), amb="ocean", ambient=0.8, light=0.8,
                                                                            fog=["#0a2f4a", 6, 40]),
    tracker=T("ATLANTIC", value="3,800 M DOWN", sub="NO LIGHT · NO SOUND"), hands=GHOST, head="float", gaze=(0, -10))
STATION = [O("box", (0, 1.5, -2), [3, 3, 6], "#d8dde2"), O("plane", (0, 1.6, -4.95), [1.4, 1.4, 1], "#0b1430", material="glow"),
           O("particles", (0, 1.6, -4.9), 0.03, "#ffffff", count=80, seed=8, spread=[1.3, 1.3, 0.02]),
           O("box", (-1.3, 1.8, -3), [0.3, 0.5, 2], "#868e96"), O("box", (1.3, 1.2, -2.5), [0.3, 0.9, 1.4], "#495057"),
           guy((0.4, 1.0, -3.2), "#3b5bdb", "#3b5bdb", act="float", face="smile", seed=205, ry=200)]
s.B(3.6, "eyes", "400 km up. An astronaut floats right past you.", env(STATION, INDOOR, eye=(0, 1.6, 0.6), amb="lab", ambient=1.5),
    tracker=T("ORBIT", value="408 KM", sub="SPACE STATION · 17,500 MPH"), hands=GHOST, head="float", gaze=(0, -4), effects=["bloom"])
s.B(3.4, "eyes", "About 1 in 10 people say this has happened to them.", env([], ["#0b1020", "#1c2b52"], eye=(0, 1.6, 0), amb="wind"),
    tracker=T("OUT-OF-BODY", value="1 IN 10", sub="PEOPLE SAY THEY'VE FELT IT"), hands=GHOST, effects=["tunnel"])
s.B(3.4, "eyes", "Then you think about your body. Alone in that bed.", env(bedroom(seed=3, extra=[ME]), NIGHT, eye=(0, 2.7, 2.5), amb="room", ambient=1.1),
    tracker=T("HOME", clock="3:31:58 AM", sub="YOUR BEDROOM"), hands=GHOST, gaze=(0, -44), effects=["bloom"])
s.B(3.6, "eyes", "And you wake up. 3:31. Two minutes passed.", env(bedroom(seed=3), NIGHT, eye=(0, 1.0, 1.4), amb="room", ambient=1.1),
    hands={"pose": "idle"}, gaze=(0, -6), sfx=[{"type": "breath", "at": 0.2}])

s.save("bp_astral", "What if you could *leave your body*?",
       "First-person out-of-body night: float out of bed, through the wall, to Tokyo, a closed museum, the Great Pyramid, Antarctica, a shipwreck and the space station, then wake up two minutes later.",
       "Where would you go first?", accent="#7fd3ff", skin="#bfe3ff", sleeve="#8fc3ff", thumb="I LEFT MY BODY", thumb_beat=3)
