"""What if Christianity was proven true? Believer's POV (owner's choice), our own scenes and words. Block POV format.
Anchors: about 2.4 billion Christians worldwide (widely cited); 3 PM is traditionally the hour Jesus died (Luke 23:44-46);
the parable of the lost son (Luke 15) for the reconciliation beats."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, DAY, INDOOR, OVERCAST, GOLDEN, DUSK  # noqa: E402
from places import street, church, living_room, park  # noqa: E402

s = Story()
BELL = lambda: [O("box", (14, 18, -40), [6, 36, 6], "#c9b8a0"), O("cone", (14, 39, -40), [5, 8, 5], "#6b4f3a"),
                O("cylinder", (14, 30, -36.9), [1.4, 1.6, 1.4], "#d4a72c", material="metal", animate=[{"type": "wobble", "amount": 0.4, "speed": 2}])]
DARK = ["#3a3f52", "#8a8fa0"]; GLOW = ["#5a6fa8", "#ffe6b0"]
FRIEND = guy((-1.0, 0, -2.0), "#2f9e44", "#3f4a5a", act="phone", face="neutral", seed=701, ry=180)
PLAZA = lambda extra=(), sky=DAY, people=30: env(street(seed=71, people=people, cars=2, extra=list(extra) + BELL()), sky, eye=(0, 1.62, 2), amb="calm")
XT = lambda a, b, sub="DAY 1", big=False: T("CHRISTIANS", count=(a, b), sub=sub, big=big)

s.B(3.8, "eyes", "", PLAZA([FRIEND]), tracker=T("CHRISTIANS", value="2,400,000,000", sub="DAY 1 · 2:59 PM"), hands={"pose": "hold", "holding": "cup"}, gaze=(0, 4),
    voices=[("So then I told him, no way, man.", "am_eric", 0.5)])
s.B(3.6, "eyes", "3:00 PM. Every church bell on Earth starts ringing.", PLAZA([FRIEND]), hands={"pose": "hold", "holding": "cup"}, gaze=(28, 20),
    sfx=[{"type": "ring", "at": 0.2, "gain": 0.8}, {"type": "ring", "at": 1.2, "gain": 0.8}, {"type": "ring", "at": 2.2, "gain": 0.8}])
s.B(3.4, "eyes", "You run inside. Nobody is pulling the ropes.", env(church(seed=2, pews=True), INDOOR, eye=(0, 1.62, -2), amb="room", ambient=1.3), hands={"pose": "none"}, gaze=(0, 10),
    sfx=[{"type": "ring", "at": 0.4, "gain": 0.9}])
s.B(3.6, "eyes", "Above you, the sky goes dark. At 3 in the afternoon.", PLAZA([FRIEND], DARK), tracker=XT(2_400_000_000, 2_430_000_000, "DAY 1 · 3:01 PM"),
    hands={"pose": "none"}, gaze=(0, 30), effects=["darken"], sfx=[{"type": "rumble", "at": 0.2, "dur": 3.0}])
s.B(3.6, "eyes", "Then light breaks through over you. Every city. Same second.", PLAZA([FRIEND, O("cone", (0, 30, -60), [30, 60, 30], "#fff3d0", material="glow", opacity=0.35)], GLOW),
    hands={"pose": "none"}, gaze=(0, 30), effects=["rays", "bloom"], sfx=[{"type": "swell", "at": 0.2, "dur": 3}])
s.B(3.4, "eyes", "Your friend, who never believed, just stares.", PLAZA([guy((-0.6, 0, -1.4), "#2f9e44", "#3f4a5a", act="idle", face="shock", seed=701, ry=170)], GLOW),
    hands={"pose": "none"}, gaze=(-18, 6), voices=[("Bro... are you seeing this?", "am_eric", 0.5)])
s.B(3.6, "eyes", "Your phone: the same thing, live from every country.", PLAZA([], GLOW), hands={"pose": "phone", "phone_text": "Mom: are you seeing this??", "phone_time": "3:02"},
    gaze=(0, -14), banner={"kicker": "BREAKING NEWS", "title": "BELLS RING WORLDWIDE · SKY LIGHTS UP", "subtitle": "NO EXPLANATION"})
s.B(3.6, "far", "By night, your church can't hold everyone.", env(church(seed=3, extra=[crowd(60, 711, at=(0, 0, -8), spread=(9, 0, 12), act="pray", ry=0)]), INDOOR,
                                                                   focus=(0, 2, -9), zoom=1.6, amb="room", ambient=1.4), tracker=XT(2_430_000_000, 3_100_000_000, "DAY 1 · 9:40 PM"))
s.B(3.6, "eyes", "You call your dad. You haven't talked in three years.", env(living_room(), DUSK, eye=(0, 1.62, 1.0), amb="room", ambient=1.4),
    hands={"pose": "phone", "phone_text": "Calling Dad…", "phone_time": "10:12"}, gaze=(0, -14), voices=[("...Hello? Son?", "bm_george", 1.4)])
s.B(3.4, "eyes", "\"I'm sorry.\" That's all you say. He starts crying.", env(living_room(), DUSK, eye=(0, 1.62, 1.0), amb="room", ambient=1.4),
    hands={"pose": "phone", "phone_text": "Dad · 14:08", "phone_time": "10:26"}, gaze=(0, -10), voices=[("I'm sorry, Dad.", "am_adam", 0.4)])
s.B(3.6, "eyes", "Day 3. You pay back money you swore you'd forget.", PLAZA([guy((0.6, 0, -1.5), "#e8590c", "#3f4a5a", act="idle", face="shock", seed=721, ry=190)], DAY),
    tracker=XT(3_100_000_000, 3_900_000_000, "DAY 3"), hands={"pose": "reach"}, gaze=(8, -6))
BAR = street(seed=73, people=0, cars=0, extra=[O("plane", (-7.9, 3, -10), [6, 2, 1], "#ff4dd2", material="glow", rotate=[0, 90, 0])])
s.B(3.4, "eyes", "Saturday night. You walk past empty clubs.", env(BAR, ["#140f2a", "#3a2a5a"], eye=(0, 1.62, 2), amb="wind"), hands={"pose": "none"}, gaze=(-24, 0))
s.B(3.4, "eyes", "The line is outside the church now.", env(street(seed=74, people=60, cars=0, extra=[O("box", (0, 4, -24), [12, 8, 8], "#e8dfd0"), O("cone", (0, 10, -24), [4, 5, 4], "#6b4f3a")]),
                                                         ["#140f2a", "#3a2a5a"], eye=(0, 1.62, 2), amb="calm"), hands={"pose": "none"}, gaze=(0, 4),
    tracker=XT(3_900_000_000, 4_800_000_000, "DAY 6"))
s.B(3.6, "eyes", "Day 40. The bells still ring at 3 PM. Every day.", PLAZA([], GOLDEN), tracker=XT(4_800_000_000, 6_000_000_000, "DAY 40"), hands={"pose": "none"}, gaze=(28, 18),
    sfx=[{"type": "ring", "at": 0.4, "gain": 0.8}])
s.B(3.8, "eyes", "Six billion people believe now. You're one of them.", PLAZA([], GOLDEN, people=60), tracker=T("CHRISTIANS", value="6,000,000,000", sub="DAY 40", big=True), hands={"pose": "none"},
    gaze=(0, 8), effects=["rays"])
s.B(3.6, "eyes", "And two billion still say it's a trick.", PLAZA([], GOLDEN, people=60), tracker=T("STILL DOUBTING", value="2,000,000,000", sub="DAY 40"), hands={"pose": "none"},
    gaze=(-30, 0))

s.save("bp_christian", "What if *Christianity* was proven true?",
       "Believer's POV: at 3 PM every church bell rings by itself, the sky darkens and lights up over every city; people reconcile, repay debts and fill the churches while the count of believers climbs.",
       "Would one sign be enough for you?", accent="#f2c94c", skin="#e0ac69", sleeve="#3f4a5a", thumb="EVERY BELL ON EARTH", thumb_beat=4)
