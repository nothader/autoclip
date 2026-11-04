"""What if you fell into a coma? (our own version: a summer-camp night dive). Block POV format.
Anchors (widely cited): the Glasgow Coma Scale runs from 3 (deepest) to 15; a 2006 study (Owen, Science) showed a patient who seemed
unresponsive could follow commands in a brain scanner by imagining playing tennis or walking through her home; about 1 in 4 people who
can't move or speak show hidden awareness on scans (NEJM, 2024); older studies found about 4 in 10 'vegetative' diagnoses were wrong."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, NIGHT, DAY, INDOOR, DAWN  # noqa: E402
from places import hospital_room, living_room  # noqa: E402

s = Story()
LAKE = [O("box", (0, -0.4, -20), [200, 0.1, 200], "#12334f", material="glossy", animate=[{"type": "bob", "amount": 0.03, "speed": 0.6}]),
        O("box", (0, 0.05, 2.5), [2.2, 0.1, 8], "#7a5a3c"), O("cylinder", (-1.0, -0.2, -1.2), [0.18, 0.8, 0.18], "#5c4430", count=4, seed=2, spread=[0, 0, 6]),
        O("tree", (0, 0, -60), 3.0, "#1f3b2c", count=14, seed=4, spread=[140, 0, 10]), O("flame", (-6, 0.1, 6), 0.6, "#ffa94d"),
        O("sphere", (0, 0.05, -9), 0.06, "#ffe7a8", material="glow", count=10, seed=5, spread=[20, 0, 2])]
FRIENDS = [guy((-0.85, 0.1, -2.0), "#2f9e44", "#3f4a5a", act="cheer", face="smile", seed=101, ry=200),
           guy((0.9, 0.1, -2.3), "#f76707", "#25324a", act="cheer", face="smile", seed=102, ry=160),
           O("sphere", (14, 9, -60), 2.2, "#fff3d6", material="glow"),
           O("sphere", (0, 0.4, -45), 0.12, "#ffd98a", material="glow", count=14, seed=8, spread=[80, 0.5, 4])]
LAKESKY = ["#1b2650", "#55688f"]
ROOM = lambda extra=(), light=1.0: env(hospital_room(extra=extra), INDOOR, eye=(0, 1.15, 1.25), amb="room", ambient=1.3 * light, light=1.8 * light, bounce="#e7ecef")
MOM = guy((-0.85, 0, -1.3), "#c2255c", "#3f4a5a", act="idle", face="sad", seed=111, ry=165)
DOC = guy((1.1, 0, -1.6), "#f8f9fa", "#495057", act="idle", face="neutral", seed=112, ry=200)

s.B(3.8, "eyes", "", env(LAKE + FRIENDS, LAKESKY, eye=(0, 1.72, 0.4), amb="ocean", ambient=1.0, stars=True),
    tracker=T("CAMP WILLOW LAKE", clock="11:16:05 PM", sub="LAST NIGHT OF SUMMER"), hands={"pose": "idle"}, gaze=(0, -14),
    voices=[("Dive! Dive! Dive!", "am_puck", 0.4), ("Do it!", "af_nicole", 2.2)])
s.B(3.2, "eyes", "Your friends dare you to dive. In the dark.", env(LAKE + FRIENDS, LAKESKY, eye=(0, 1.72, -0.6), amb="ocean", ambient=1.0, stars=True),
    hands={"pose": "reach"}, gaze=(0, -30))
s.B(2.8, "eyes", "The water is shallower than it looks.", env(LAKE, LAKESKY, eye=(0, 0.6, -2.5), amb="ocean", ambient=0.9, stars=True), head="fall",
    hands={"pose": "shield"}, gaze=(0, -55), effects=["shake"], sfx=[{"type": "impact", "at": 1.4, "gain": 1.3}])
s.B(3.0, "eyes", "Your head hits a rock.", env([O("box", (0, -1, -1), [8, 0.1, 8], "#0b2236"), O("rock", (0.2, -0.6, -1.4), 0.6, "#3d4a40"),
                                                O("particles", (0, -0.2, -1), 0.05, "#bfe3ff", count=60, seed=3, spread=[3, 2, 3])], ["#0a2a40", "#1d5a7a"],
                                               eye=(0, 0.2, 0), amb="ocean", ambient=0.8), hands={"pose": "none"}, gaze=(0, -40), effects=["darken", "dizzy"])
s.B(3.0, "eyes", "Then nothing.", env([], ["#000000", "#05080c"], eye=(0, 1, 0), amb="none"), tracker=T("IN A COMA", value="DAY 1", sub="ST. MARY'S · ICU 4"),
    hands={"pose": "none"}, effects=["darken"])
s.B(3.6, "eyes", "Doctors score you a 3 out of 15. The lowest there is.", ROOM([DOC]), hands={"pose": "none"}, gaze=(8, -6),
    voices=[("No eye opening. No response to voice. GCS three.", "am_michael", 0.3)], screen={"kind": "vitals", "title": "GCS 3/15", "rows": [["HR", "62"], ["SpO2", "97"]]})
s.B(3.6, "eyes", "Your mom hasn't left the chair.", ROOM([MOM]), tracker=T("IN A COMA", value="DAY 4", sub="ST. MARY'S · ICU 4"), hands={"pose": "none"},
    gaze=(-22, 6), voices=[("Hey baby. It's Mom. I'm right here.", "af_heart", 0.4)])
s.B(3.4, "eyes", "You can hear her. You can't answer.", ROOM([MOM]), hands={"pose": "none"}, gaze=(-22, 6), effects=["darken"])
s.B(3.4, "eyes", "Your phone keeps lighting up. Nobody reads it.",
    ROOM([O("box", (-1.3, 0.7, 0.4), [0.5, 0.05, 0.5], "#c4b49c"), O("plane", (-1.3, 0.73, 0.4), [0.12, 0.22, 1], "#9fd3ff", material="glow", rotate=[-90, 0, 0],
            animate=[{"type": "pulse", "amount": 0.3}])]), tracker=T("IN A COMA", value="WEEK 2", sub="47 UNREAD MESSAGES"), hands={"pose": "none"}, gaze=(-38, -40))
s.B(3.6, "eyes", "\"There may be no one in there anymore.\"", ROOM([DOC, MOM]), by="Your doctor", tracker=T("IN A COMA", value="WEEK 5", sub="ST. MARY'S · ICU 4"),
    hands={"pose": "none"}, gaze=(14, -6), voices=[("I'm sorry. There may be no one in there anymore.", "am_michael", 0.3)])
s.B(3.4, "eyes", "\"She's in there. I know she is.\"", ROOM([DOC, MOM]), by="Your mom", hands={"pose": "none"}, gaze=(-24, -6),
    voices=[("No. She's in there. I know she is.", "af_heart", 0.3)])
s.B(3.6, "eyes", "But about 4 in 10 times, that call is wrong.", ROOM([DOC, MOM], light=0.8), tracker=T("MISDIAGNOSED", value="ABOUT 40%", sub="OF 'NO AWARENESS' CASES", alert=True),
    hands={"pose": "none"}, gaze=(0, 0))
MRI = [O("box", (0, -0.02, -1), [6, 0.04, 6], "#c9ced4"), O("torus", (0, 1.2, -0.4), [1.4, 1.4, 2.4], "#eef1f4", material="glossy", rotate=[0, 0, 0]),
       O("box", (0, 0.6, 0.6), [0.9, 0.2, 3.2], "#dfe4e8"), O("plane", (0, 2.95, -1), [1.2, 0.6, 1], "#ffffff", material="glow", rotate=[90, 0, 0]),
       O("box", (2.5, 1.5, -2.5), [0.1, 3, 5], "#dfe6ea")]
s.B(3.6, "eyes", "Week 7. They slide you into a brain scanner.", env(MRI, INDOOR, eye=(0, 1.2, 1.1), amb="lab", ambient=1.5, light=2.0),
    tracker=T("IN A COMA", value="WEEK 7", sub="fMRI · ROOM B"), hands={"pose": "none"}, gaze=(0, 0), sfx=[{"type": "rumble", "at": 0.3, "dur": 3.0, "gain": 0.6}])
s.B(3.6, "eyes", "A voice says: \"Imagine walking through your home.\"", env(MRI, INDOOR, eye=(0, 1.2, 0.6), amb="lab", ambient=1.3, light=1.8),
    hands={"pose": "none"}, voices=[("If you can hear me... imagine walking through your home.", "bf_emma", 0.3)])
s.B(3.6, "eyes", "So you do. Every room. Every door.", env(living_room(extra=[O("cat", (1, 0, -3), 0.5, "#8d6e57")] if False else ()), DAWN,
                                                              eye=(0, 1.62, 1.0), amb="room", ambient=1.7, light=2.4), head="walk", hands={"pose": "idle"},
    effects=["bloom"], tracker=T("IN A COMA", value="WEEK 7", sub="fMRI · ROOM B"))
s.B(3.4, "eyes", "Your kitchen. Your bedroom. The squeaky stair.", env(living_room(wall="#f3e6d2", tv="#ffd8a8"), DAWN, eye=(1, 1.62, -1.0), amb="room", ambient=1.7, light=2.4),
    head="walk", hands={"pose": "reach"}, gaze=(-40, 0), effects=["bloom"])
SCAN = [O("box", (0, -0.02, -1), [8, 0.04, 8], "#5a6068"), O("box", (0, 1.6, 1.0), [3.4, 1.9, 0.1], "#15181d"),
        O("plane", (-0.8, 1.6, 0.94), [1.4, 1.4, 1], "#f08c00", material="glow", rotate=[0, 180, 0], animate=[{"type": "pulse", "amount": 0.25}]),
        O("plane", (0.8, 1.6, 0.94), [1.4, 1.4, 1], "#e8590c", material="glow", rotate=[0, 180, 0], animate=[{"type": "pulse", "amount": 0.25}]),
        guy((0.75, 0, -0.4), "#f8f9fa", "#495057", act="point", face="shock", seed=112),
        guy((-0.75, 0, -0.5), "#7048e8", "#3f4a5a", act="cheer", face="smile", seed=113)]
s.B(3.6, "front", "On the screen, your brain lights up.", env(SCAN, INDOOR, focus=(0, 1.45, -0.4), zoom=0.7, amb="lab", ambient=1.4),
    tracker=T("RESPONSE", value="DETECTED", sub="fMRI · ROOM B"), voices=[("Wait. Look at this. She's doing it.", "am_michael", 0.4)], effects=["rays"])
s.B(3.6, "front", "About 1 in 4 people who can't move can do this.", env(SCAN, INDOOR, focus=(0, 1.6, 0.4), zoom=0.6, amb="lab", ambient=1.4),
    tracker=T("HIDDEN AWARENESS", value="1 IN 4", sub="OF PATIENTS WHO CAN'T RESPOND"))
s.B(3.8, "eyes", "You still can't move. But now they know you're there.", ROOM([MOM], light=1.2), hands={"pose": "none"}, gaze=(-22, 6),
    voices=[("We know you're in there. We're not going anywhere.", "af_heart", 0.5)], tracker=T("IN A COMA", value="WEEK 7", sub="ST. MARY'S · ICU 4"))
s.B(3.6, "eyes", "And for the first time in weeks, someone talks to you. Not about you.", ROOM([MOM], light=1.3), hands={"pose": "none"}, gaze=(-30, -2),
    effects=["bloom"])

s.save("bp_coma", "What if you fell into a *coma*?",
       "First-person coma story: a night dive at summer camp, ICU weeks, a doctor ready to give up, and a brain scan that proves you're still there.",
       "Would you want them to keep trying?", accent="#4fd1c5", skin="#c68642", thumb="STILL IN THERE", thumb_beat=16)
