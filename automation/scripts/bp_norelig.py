"""What if religion just disappeared? Our own scenes. Block POV format.
Anchors (widely cited): about 6 in 7 people in the world identify with a religion (Pew); 'In God We Trust' is on US money;
most hospitals and many charities worldwide were founded by religious groups; studies link religious attendance with lower depression rates."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, DAY, INDOOR, GOLDEN, DUSK, OVERCAST  # noqa: E402
from places import church, mosque, street, living_room, park  # noqa: E402

s = Story()
BEL = lambda a, b, sub="WORLDWIDE": T("BELIEVERS", count=(a, b), sub=sub)
GRAN = guy((-0.7, 0, -5.4), "#7048e8", "#3f4a5a", act="sit", face="smile", seed=1101, ry=200, look="elder")
PEWS = lambda extra=(), sky=DAY: env(church(seed=11, extra=list(extra)), sky, eye=(0, 1.3, -4), amb="room", ambient=1.4)
CONG = crowd(40, 1111, at=(0, 0.1, -9), spread=(8, 0, 8), act="sit", ry=0)

s.B(3.8, "eyes", "", PEWS([CONG, GRAN]), tracker=T("BELIEVERS", value="6,900,000,000", sub="SUNDAY · 10:02 AM"), hands={"pose": "idle"}, gaze=(0, 0),
    voices=[("Let us pray.", "bm_george", 0.4)])
s.B(3.4, "eyes", "Sunday morning. Your grandma's church. Like every week.", PEWS([CONG, GRAN]), hands={"pose": "idle"}, gaze=(-26, -6))
s.B(3.6, "eyes", "Then, mid-prayer, the words just... leave everyone.", PEWS([CONG, GRAN]), tracker=BEL(6_900_000_000, 0), hands={"pose": "none"}, gaze=(0, 0),
    effects=["darken"], sfx=[{"type": "drop", "at": 0.4}])
s.B(3.4, "eyes", "Your grandma looks at the cross like she's never seen one.", PEWS([guy((-0.7, 0, -5.4), "#7048e8", "#3f4a5a", act="think", face="neutral", seed=1101, ry=200, look="elder")]),
    hands={"pose": "none"}, gaze=(-26, -2), voices=[("Why... are we here?", "af_heart", 0.5)])
s.B(3.6, "far", "Every church, mosque and temple. Empty in a minute.", env(mosque(seed=3, extra=[crowd(30, 1121, at=(0, 0, -10), spread=(20, 0, 8), act="walk", ry=180)]),
                                                                        GOLDEN, focus=(0, 3, -18), zoom=2.6, amb="calm"), tracker=T("BELIEVERS", value="0", sub="WORLDWIDE"))
s.B(3.6, "eyes", "You check your wallet. 'In God We Trust'. Just words now.", env(living_room(), DAY, eye=(0, 1.62, 1), amb="room", ambient=1.5),
    hands={"pose": "phone", "phone_text": "IN GOD WE TRUST · ONE DOLLAR", "phone_time": "10:30"}, gaze=(0, -16))
s.B(3.6, "eyes", "Your phone: 'No more Christmas'. 'No more Ramadan'. 'No more Diwali'.", env(living_room(), DAY, eye=(0, 1.62, 1), amb="room", ambient=1.5),
    hands={"pose": "phone", "phone_text": "Holidays: 0 upcoming", "phone_time": "10:31"}, gaze=(0, -14))
s.B(3.6, "eyes", "Your best friend scores a goal. He doesn't look up anymore.", env(park(seed=12, people=20, extra=[guy((0, 0, -4), "#e03131", "#f8f9fa", act="cheer", face="smile", seed=1131, ry=180),
                                                                                   O("box", (0, 1.1, -12), [7, 2.2, 0.1], "#f8f9fa")]), DAY, eye=(0, 1.62, 2), amb="calm"),
    hands={"pose": "none"}, gaze=(0, 4))
SHELF = [O("box", (0, -0.02, -2), [8, 0.04, 8], "#3a3530"), O("box", (0, 1.4, -4), [4, 2.8, 0.6], "#5c4a3a"),
         O("box", (0, 1.4, -3.7), [0.15, 0.25, 0.2], "#c92a2a", count=30, seed=7, spread=[3.6, 2.2, 0]), guy((0.6, 0, -2.4), "#495057", "#212529", act="think", face="neutral", seed=1141)]
s.B(3.6, "front", "Studies link faith to less crime and less depression.", env(SHELF, INDOOR, focus=(0.6, 1.4, -2.4), zoom=0.65, amb="room", ambient=1.3),
    tracker=T("STUDIES", value="LESS CRIME", sub="LESS DEPRESSION · MORE GIVING"))
s.B(3.6, "eyes", "Without it, who runs the food banks? The shelters?", env(street(seed=13, people=20, cars=2, extra=[O("box", (-6, 2, -10), [6, 4, 6], "#e9ecef"),
                                                                                                   O("plane", (-2.95, 3.4, -10), [4, 0.6, 1], "#2f9e44", material="glow", rotate=[0, 90, 0])]),
                                                                       OVERCAST, eye=(0, 1.62, 2), amb="wind"), hands={"pose": "none"}, gaze=(-30, 0),
    tracker=T("CHARITIES", value="HALF CLOSING", sub="FAITH-BASED · WORLDWIDE", alert=True))
s.B(3.6, "eyes", "But you notice: fewer people fight over whose god is right.", env(street(seed=14, people=40, cars=2), DAY, eye=(0, 1.62, 2), amb="calm"), hands={"pose": "none"},
    gaze=(0, 2))
s.B(3.6, "eyes", "Wars over holy land? Nobody remembers why they started.", env(street(seed=16, people=30, cars=0, extra=[O("box", (0, 1.2, -14), [12, 2.4, 0.4], "#9c8f7a")]),
                                                                           GOLDEN, eye=(0, 1.62, 2), amb="calm"), hands={"pose": "none"}, gaze=(0, 0),
    tracker=T("RELIGIOUS CONFLICTS", value="STOPPED", sub="NO ONE LEFT TO FIGHT FOR"))
s.B(3.8, "eyes", "At a funeral, nobody says 'see you again'.", env(park(seed=15, grass="#4f7a3a", people=0, extra=[crowd(14, 1151, at=(0, 0, -5), spread=(6, 0, 3), act="idle", face="sad"),
                                                                                                    O("box", (0, 0.4, -7), [2.2, 0.8, 0.9], "#5c3a21")]),
                                                                   OVERCAST, eye=(0, 1.62, 1), amb="wind"), hands={"pose": "none"}, gaze=(0, -6), effects=["darken"])
s.B(3.6, "eyes", "Your grandma sits on the steps. She doesn't know where to go on Sundays.", env(church(seed=11, pews=False, extra=[GRAN]), DUSK, eye=(0, 1.3, -4), amb="room", ambient=1.2),
    tracker=T("BELIEVERS", value="0", sub="SUNDAY · ONE WEEK LATER"), hands={"pose": "none"}, gaze=(-26, -6))
s.B(3.8, "eyes", "Then she asks you: \"What do you believe in now?\"", env(church(seed=11, pews=False, extra=[guy((-0.7, 0, -5.4), "#7048e8", "#3f4a5a", act="sit", face="sad", seed=1101, ry=200, look="elder")]),
                                                                     DUSK, eye=(0, 1.3, -4), amb="room", ambient=1.2), tracker=T("YOUR ANSWER", value="?", big=True),
    hands={"pose": "none"}, gaze=(-26, -2), voices=[("So... what do you believe in now?", "af_heart", 0.4)])

s.save("bp_norelig", "What if *religion* just disappeared?",
       "First-person: mid-prayer on a Sunday, every belief on Earth vanishes; holidays, charities, funerals and your grandma's Sundays change overnight.",
       "What would you believe in?", accent="#f2c94c", skin="#e0ac69", sleeve="#3f4a5a", thumb="0 BELIEVERS", thumb_beat=2)
