"""What if you had 12 minutes to get out? (fictional high-rise fire; our reworked version of the 16-minutes video). Block POV.
Anchors (fire-safety basics, widely cited): smoke, not flames, causes most fire deaths; never use an elevator in a fire; stay low where
the air is cleaner; in real fires many people delay leaving to finish tasks or grab belongings."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, DAY, INDOOR, OVERCAST  # noqa: E402
from places import office_floor, stairwell, street  # noqa: E402

s = Story()
SMOKE = lambda n=60, y=2.4, z=-6, c="#8d9096": O("particles", (0, y, z), 0.35, c, count=n, seed=7, spread=[12, 1.2, 14])
BOSS = guy((-1.1, 0, -1.8), "#25324a", "#25324a", act="idle", face="smile", seed=301, ry=180)
COWORKER = guy((1.2, 0, -2.4), "#e64980", "#3f4a5a", act="phone", face="neutral", seed=302, ry=200)
OFFICE = lambda extra=(), amb=1.4: env(office_floor(seed=5, extra=extra), DAY, eye=(0, 1.62, 1.2), amb="room", ambient=amb, light=2.2)

s.B(3.8, "eyes", "", OFFICE([BOSS, COWORKER]), tracker=T("HARBOR TOWER", clock="2:14:03 PM", sub="TUESDAY · FLOOR 51"), hands={"pose": "hold", "holding": "cup"},
    gaze=(0, -6), voices=[("Great work on the deck today!", "am_michael", 0.6)])
s.B(3.4, "eyes", "A fire alarm. Everyone groans.", OFFICE([BOSS, COWORKER]), hands={"pose": "hold", "holding": "cup"}, gaze=(0, 16),
    voices=[("Ugh. Probably another drill.", "af_nicole", 0.9)], sfx=[{"type": "alarm", "at": 0.1, "dur": 3.0, "gain": 0.6}])
s.B(3.2, "eyes", "But you smell smoke.", OFFICE([BOSS, COWORKER, SMOKE(30, 2.8)]), hands={"pose": "idle"}, gaze=(0, 28), sfx=[{"type": "alarm", "at": 0, "dur": 3.0, "gain": 0.5}])
s.B(3.6, "eyes", "\"Everyone stay put. Wait for the announcement.\"", OFFICE([BOSS, COWORKER, SMOKE(30, 2.8)]), by="Your manager", hands={"pose": "idle"},
    gaze=(-26, 0), voices=[("Everyone stay put. Wait for the announcement.", "am_michael", 0.3)])
s.B(3.4, "eyes", "Most people wait. They finish an email. They grab a bag.", OFFICE([COWORKER, SMOKE(40, 2.6)], amb=1.2), hands={"pose": "idle"}, gaze=(30, -14))
s.B(3.2, "eyes", "You don't. You leave everything and go.", OFFICE([SMOKE(40, 2.6)], amb=1.2), head="walk", hands={"pose": "idle"}, gaze=(0, 0))
LIFT = [O("box", (0, -0.02, -2), [6, 0.04, 6], "#6b7078"), O("box", (0, 1.5, -3.4), [6, 3, 0.1], "#cfd4d9"),
        O("box", (-0.8, 1.1, -3.33), [1.3, 2.2, 0.05], "#a9b0b8", material="glossy"), O("box", (1.4, 1.1, -3.33), [1.3, 2.2, 0.05], "#a9b0b8", material="glossy"),
        O("plane", (0.3, 1.5, -3.32), [0.5, 0.4, 1], "#e03131", material="glow"), SMOKE(30, 2.6, -2)]
s.B(3.4, "eyes", "The elevator is right there. You reach for it.", env(LIFT, INDOOR, eye=(0, 1.62, 0.8), amb="room", ambient=1.3), hands={"pose": "point"}, gaze=(-10, -4))
s.B(3.6, "eyes", "Never take it in a fire. The shaft fills with smoke.", env(LIFT, INDOOR, eye=(0.3, 1.62, -1.6), amb="room", ambient=1.3), hands={"pose": "none"},
    gaze=(0, 0), screen={"kind": "board", "title": "IN CASE OF FIRE", "subtitle": "DO NOT USE ELEVATORS · USE EXIT STAIRS"})
s.B(3.4, "eyes", "You take Stairwell C. Fifty-one floors down.", env(stairwell(seed=1), INDOOR, eye=(0, 1.62, 1.2), amb="room", ambient=1.5, light=1.8),
    tracker=T("HARBOR TOWER", clock="2:16:40 PM", sub="STAIRWELL C · FLOOR 51"), head="walk", hands={"pose": "grab"}, gaze=(0, -22))
PACK = [crowd(8, 311, at=(0, -1.2, -2.4), spread=(0.8, 0, 2.6), act="walk", ry=0)]
s.B(3.4, "eyes", "It's packed. You can only shuffle.", env(stairwell(seed=2, extra=PACK), INDOOR, eye=(0, 1.62, 1.2), amb="room", ambient=1.4, light=1.7),
    tracker=T("HARBOR TOWER", clock="2:19:05 PM", sub="STAIRWELL C · FLOOR 44"), head="walk", hands={"pose": "grab"}, gaze=(0, -26),
    voices=[("Keep moving! Keep to the right!", "am_adam", 1.0)])
s.B(3.4, "eyes", "Floor 38. The air around you turns gray.", env(stairwell(seed=3, extra=[SMOKE(110, 2.4, -2, "#6b6e73")] + PACK), INDOOR, eye=(0, 1.62, 1.2), amb="room",
                                                  ambient=1.0, light=1.2, fog=["#55585d", 1, 7]),
    tracker=T("HARBOR TOWER", clock="2:20:31 PM", sub="STAIRWELL C · FLOOR 38", alert=True), head="walk", hands={"pose": "grab"}, gaze=(0, -24), effects=["darken"])
s.B(3.6, "eyes", "In fires, smoke kills more people than flames do.", env(stairwell(seed=3, extra=[SMOKE(120, 2.0, -2, "#5d6065")]), INDOOR, eye=(0, 1.62, 1.2),
                                                                       amb="room", ambient=0.9, light=1.0, fog=["#4d5055", 0.8, 5]),
    tracker=T("FIRE DEATHS", value="MOSTLY SMOKE", sub="NOT FLAMES", alert=True), hands={"pose": "idle", "tremble": 0.6}, gaze=(0, -20))
s.B(3.4, "eyes", "So you stay low. You breathe through your sleeve.", env(stairwell(seed=4, extra=[SMOKE(110, 2.6, -2, "#5d6065")]), INDOOR, eye=(0, 1.3, 1.2),
                                                                         amb="room", ambient=0.9, light=1.0, fog=["#4d5055", 1.2, 6]),
    tracker=T("HARBOR TOWER", clock="2:22:10 PM", sub="STAIRWELL C · FLOOR 29", alert=True), head="walk", hands={"pose": "idle", "tremble": 0.6}, gaze=(0, -30))
FF = [guy((0.25, -0.35, -1.0), "#3d3d3d", "#3d3d3d", act="run", face="angry", seed=321, ry=180), O("box", (0.25, 1.42, -1.0), [0.42, 0.18, 0.42], "#f59f00")]
s.B(3.2, "eyes", "A firefighter pushes past you. Going up.", env(stairwell(seed=5, extra=FF + [SMOKE(60, 2.6, -2, "#6b6e73")]), INDOOR, eye=(0, 1.62, 1.2), amb="room",
                                                                   ambient=1.1, light=1.3), hands={"pose": "shield"}, gaze=(0, -10),
    voices=[("Keep going down! Don't stop!", "am_onyx", 0.3)], effects=["shake"])
s.B(3.4, "eyes", "Floor 12. Your legs are shaking.", env(stairwell(seed=6), INDOOR, eye=(0, 1.62, 1.2), amb="room", ambient=1.4, light=1.7),
    tracker=T("HARBOR TOWER", clock="2:24:47 PM", sub="STAIRWELL C · FLOOR 12"), head="stumble", hands={"pose": "grab", "tremble": 0.8}, gaze=(0, -26))
LOBBY = [O("box", (0, -0.02, -6), [14, 0.04, 16], "#d9d4cc"), O("plane", (0, 2.2, -13.9), [12, 4.4, 1], "#fff7e6", material="glow"),
         O("box", (-6, 2.5, -6), [0.2, 5, 16], "#bfc4c9"), O("box", (6, 2.5, -6), [0.2, 5, 16], "#bfc4c9"),
         crowd(16, 331, at=(0, 0, -11), spread=(10, 0, 5), act="run", face="shock", ry=0)]
s.B(3.4, "eyes", "The lobby. Daylight.", env(LOBBY, DAY, eye=(0, 1.62, 1.2), amb="room", ambient=1.7, light=2.3), tracker=T("HARBOR TOWER", clock="2:25:52 PM", sub="LOBBY · EXIT B"),
    head="run", hands={"pose": "idle"}, effects=["bloom", "rays"])
TOWER = [O("box", (0, 60, -70), [24, 120, 24], "#8d97a5", material="glossy"), O("flame", (0, 104, -57.8), 9, "#ff7a1a"),
         O("particles", (0, 125, -62), 3.0, "#5d6065", count=90, seed=9, spread=[40, 40, 20], animate=[{"type": "drift", "axis": "y", "amount": 0.3}]),
         O("box", (-5, 1.4, -24), [3, 2.8, 9], "#c92a2a", count=3, seed=4, spread=[16, 0, 6]),
         O("sphere", (-5, 3.0, -24), 0.25, "#4dabf7", material="glow", count=3, seed=4, spread=[16, 0, 6], animate=[{"type": "pulse", "amount": 0.6}])]
s.B(3.6, "far", "You look up. Your floor is gone in smoke.", env(street(seed=21, people=30, cars=0, extra=TOWER), OVERCAST, focus=(0, 70, -70), zoom=4.5, amb="wind", ambient=1.3),
    tracker=T("HARBOR TOWER", clock="2:26:03 PM", sub="OUTSIDE · HARBOR ST"), sfx=[{"type": "siren", "at": 0.2, "dur": 3.2, "gain": 0.6}])
s.B(3.8, "eyes", "Twelve minutes. That's all you had.", env(street(seed=21, people=30, cars=0, extra=TOWER), OVERCAST, eye=(0, 1.62, 0), amb="wind", ambient=1.3),
    tracker=T("TIME TO GET OUT", value="12:00", sub="FROM ALARM TO STREET", big=True), hands={"pose": "none"}, gaze=(0, 30))
s.B(3.6, "eyes", "The ones who waited for the announcement are still in the stairwell.", env(street(seed=22, people=40, cars=0, extra=TOWER), OVERCAST, eye=(2, 1.62, -4),
                                                                                         amb="wind", ambient=1.3), hands={"pose": "none"}, gaze=(-20, 8))

s.save("bp_tower", "What if you had *12 minutes* to get out?",
       "First-person high-rise fire in a fictional tower: an ignored alarm, a manager who says wait, the elevator trap, 51 floors of smoky stairs and 12 minutes to reach the street.",
       "Would you have waited for the announcement?", accent="#ff922b", skin="#c68642", sleeve="#25324a", thumb="12 MINUTES", thumb_beat=11)
