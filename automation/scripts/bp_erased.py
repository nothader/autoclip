"""What if Jesus was erased from history? Believer's POV (owner's choice), our own scenes. Block POV format.
Anchors (widely cited): about 2.4 billion Christians; the AD/BC calendar counts years from his birth (Dionysius Exiguus, 525 AD);
Sunday rest, Christmas and Easter, many hospitals, universities and charities trace to Christian origins; the Old Testament stays (it is older)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, DAY, INDOOR, OVERCAST, DUSK, NIGHT  # noqa: E402
from places import church, street, living_room, park  # noqa: E402

s = Story()
GRAN = lambda act="sit", face="smile": guy((-0.8, 0, -5.4), "#7048e8", "#3f4a5a", act=act, face=face, seed=1501, ry=200, look="elder")
BIBLE = O("box", (-0.55, 0.62, -5.2), [0.26, 0.08, 0.34], "#3a2a1e")
PEWS = lambda extra=(), sky=DAY: env(church(seed=15, extra=list(extra)), sky, eye=(0, 1.3, -3.6), amb="room", ambient=1.4)
CONG = crowd(40, 1511, at=(0, 0.1, -10), spread=(8, 0, 6), act="sit", ry=0)
XT = lambda a, b, sub="WORLDWIDE", alert=False: T("CHRISTIANS", count=(a, b), sub=sub, alert=alert)

s.B(3.8, "eyes", "", PEWS([CONG, GRAN(), BIBLE]), tracker=T("CHRISTIANS", value="2,400,000,000", sub="SUNDAY · 10:14 AM"), hands={"pose": "idle"}, gaze=(-12, -4),
    voices=[("Let us stand and sing.", "bm_george", 0.4)])
s.B(3.4, "eyes", "Sunday morning. Church with your grandma. Like every week.", PEWS([CONG, GRAN(), BIBLE]), hands={"pose": "idle"}, gaze=(-14, -4))
s.B(3.4, "eyes", "Then, mid-song, the bells stop.", PEWS([CONG, GRAN("idle", "shock"), BIBLE]), tracker=XT(2_400_000_000, 2_300_000_000, alert=True), hands={"pose": "none"},
    gaze=(0, 10), sfx=[{"type": "drop", "at": 0.3}])
s.B(3.6, "eyes", "Jesus was just erased from history. Every trace.", env(street(seed=151, people=40, cars=2), OVERCAST, eye=(0, 1.62, 2), amb="wind"), tracker=XT(2_300_000_000, 1_900_000_000),
    hands={"pose": "none"}, gaze=(0, 4), effects=["darken"])
s.B(3.6, "eyes", "Your grandma's Bible loses a quarter of its pages.", PEWS([GRAN("think", "sad"), O("box", (-0.55, 0.62, -5.2), [0.26, 0.06, 0.34], "#3a2a1e")]), hands={"pose": "none"},
    gaze=(-14, -10))
s.B(3.4, "eyes", "The Old Testament stays. The New is gone.", PEWS([GRAN("think", "sad")]), tracker=XT(1_900_000_000, 1_400_000_000), hands={"pose": "none"}, gaze=(-14, -6))
s.B(3.6, "eyes", "Your phone: our years counted from his birth. Not anymore.", env(street(seed=152, people=20, cars=2), OVERCAST, eye=(0, 1.62, 2), amb="wind"),
    hands={"pose": "phone", "phone_text": "Year: 2779 (from the founding of Rome)", "phone_time": "10:22"}, gaze=(0, -14))
s.B(3.6, "eyes", "No Christmas. No Easter. Your calendar has holes.", env(living_room(), DUSK, eye=(0, 1.62, 1), amb="room", ambient=1.4),
    hands={"pose": "phone", "phone_text": "Holidays: none in December", "phone_time": "10:30"}, gaze=(0, -14))
s.B(3.6, "eyes", "No Sunday to keep holy. Your boss calls. You work today.", env(street(seed=153, people=30, cars=3), DAY, eye=(0, 1.62, 2), amb="calm"),
    hands={"pose": "phone", "phone_text": "Boss · Incoming call · Sunday", "phone_time": "11:02"}, gaze=(0, -12), tracker=XT(1_400_000_000, 1_000_000_000))
BAR = street(seed=154, people=0, cars=0, extra=[O("plane", (-7.9, 3, -10), [6, 2, 1], "#ff4dd2", material="glow", rotate=[0, 90, 0]),
                                                guy((-0.9, 0, -2.6), "#f59f00", "#3f4a5a", act="cheer", face="smile", seed=1521, ry=180),
                                                guy((0.9, 0, -3.0), "#1c7ed6", "#212529", act="cheer", face="smile", seed=1522, ry=180)])
s.B(3.4, "eyes", "No confession. No guilt. The party never stops.", env(BAR, NIGHT, eye=(0, 1.62, 1), amb="calm"), hands={"pose": "none"}, gaze=(0, 2))
s.B(3.6, "eyes", "Weddings move to city hall. Nobody says 'before God'.", env(street(seed=155, people=10, cars=0, extra=[guy((-0.5, 0, -3), "#f8f9fa", "#f8f9fa", act="idle", face="smile",
                                                                                                                        seed=1531, ry=180), guy((0.5, 0, -3), "#212529", "#212529",
                                                                                                                                                 act="idle", face="smile", seed=1532, ry=180)]),
                                                                            DAY, eye=(0, 1.62, 1), amb="calm"), hands={"pose": "none"}, gaze=(0, 2), tracker=XT(1_000_000_000, 600_000_000))
s.B(3.6, "far", "The cathedrals? Museums now. Or nothing.", env(street(seed=156, people=6, cars=2, extra=[O("box", (0, 10, -40), [14, 20, 10], "#c9b8a0"), O("cone", (-4, 24, -40), [3, 8, 3], "#8a7a64"),
                                                                                                          O("cone", (4, 24, -40), [3, 8, 3], "#8a7a64")]), OVERCAST, focus=(0, 6, -30), zoom=3, amb="wind"))
FUNERAL = park(seed=157, grass="#4f7a3a", people=0, extra=[crowd(14, 1541, at=(0, 0, -5), spread=(6, 0, 3), act="idle", face="sad"), O("box", (0, 0.4, -7), [2.2, 0.8, 0.9], "#5c3a21")])
s.B(3.8, "eyes", "A funeral. Nobody says 'see you again'.", env(FUNERAL, OVERCAST, eye=(0, 1.62, 1), amb="wind"), tracker=XT(600_000_000, 0, "WORLDWIDE"), hands={"pose": "none"}, gaze=(0, -6),
    effects=["darken"])
s.B(3.6, "eyes", "No hell to fear. No heaven to hope for.", env(FUNERAL, NIGHT, eye=(0, 1.62, 1), amb="wind"), tracker=T("CHRISTIANS", value="0", sub="WORLDWIDE", big=True),
    hands={"pose": "none"}, gaze=(0, 18))
s.B(3.6, "eyes", "Your grandma holds her thin Bible. \"Something is missing.\"", PEWS([GRAN("sit", "sad"), BIBLE], DUSK), hands={"pose": "none"}, gaze=(-14, -6),
    voices=[("Something is missing. I just can't remember what.", "af_heart", 0.4)])

s.save("bp_erased", "What if *Jesus* was erased from history?",
       "Believer's POV: mid-hymn on a Sunday, every trace of Jesus vanishes; the New Testament, the calendar, Christmas, Sunday rest, weddings and funerals change, and your grandma feels something missing.",
       "Would the world be better or worse?", accent="#f2c94c", skin="#e0ac69", sleeve="#3f4a5a", thumb="ERASED", thumb_beat=3)
