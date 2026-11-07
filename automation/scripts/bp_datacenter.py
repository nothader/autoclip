"""What if an AI data center was built next to your house? (trending: Nov 3, 2026 local votes against data centers). Block POV.
Neutral: shows both the bills/hum and the jobs/tax money; the viewer casts the deciding vote.
Anchors: a typical AI-focused data center uses about as much electricity as 100,000 households (IEA, Energy and AI, 2025);
in an August 2026 poll about 3 in 4 people opposed a new data center near their home; on Nov 3, 2026 voters in about 10 states
turned down most local data-center measures (widely reported, e.g. Route Fifty, States Newsroom)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, NIGHT, INDOOR  # noqa: E402
GOLDEN = ["#4a5a8c", "#f7b87a"]; OVERCAST = ["#7d8896", "#d6dbe0"]; DUSK = ["#3b2f5c", "#f08a6a"]; DAY = ["#4f8fd6", "#e3eef7"]

s = Story()
LAWN, ROAD = "#6f9a4e", "#55585e"


def house(x, z, wall, roof, ry=0):
    return [O("box", (x, 1.4, z), [5, 2.8, 4.4], wall, rotate=[0, ry, 0]), O("cone", (x, 3.6, z), [4.2, 1.6, 4.2], roof, rotate=[0, 45 + ry, 0]),
            O("plane", (x - 1.2, 1.5, z + 2.22), [0.9, 0.8, 1], "#ffe2a8", material="glow"), O("box", (x + 1.0, 0.9, z + 2.21), [0.8, 1.8, 0.05], "#6b4f3a")]


def street(dc=False, dusk=False, extra=()):
    o = [O("box", (0, -0.03, -14), [90, 0.04, 70], LAWN), O("box", (0, -0.01, -6), [90, 0.02, 4], ROAD),
         O("box", (0, 0.01, -6), [0.15, 0.01, 90], "#e8d36a", rotate=[0, 90, 0])]
    o += house(-11, -14, "#e9dcc5", "#8a4f3a") + house(-2, -15, "#c9d8e6", "#3d4a5c") + house(9, -14, "#f1e2c2", "#6b3a2e")
    o += [O("tree", (-13, 0, -3), 1.6, "#4f8a3a"), O("tree", (13, 0, -2), 1.5, "#5c9442"), O("box", (4, 0.5, -1.5), [2.6, 0.9, 1.2], "#c92a2a")]
    if dc:   # the data center behind the houses: grey wall, roof units, blinking lights
        o += [O("box", (0, 7, -46), [80, 14, 22], "#b8bcc2"), O("box", (0, 14.6, -46), [70, 1.2, 18], "#9aa0a7"),
              O("cylinder", (-25, 16.5, -42), [3, 3.6, 3], "#8b9198", count=6, seed=4, spread=[50, 0, 4]),
              O("sphere", (0, 12, -34.9), 0.25, "#ff4d4d", material="glow", count=10, seed=5, spread=[70, 3, 0], animate=[{"type": "pulse", "amount": 0.8}]),
              O("box", (0, 1.4, -32), [86, 2.8, 0.15], "#d8dde2"),
              O("box", (0, 9, -34.9), [76, 1.6, 0.1], "#2b3038"), O("plane", (18, 11.5, -34.8), [12, 2.2, 1], "#4dabf7", material="glow"),
              O("box", (-20, 4, -34.85), [1.4, 6, 0.1], "#8b9198", count=8, seed=9, spread=[40, 0, 0])]
    return o + list(extra)


ME_EYE = (0, 1.62, 3.5)
MOM = lambda act="idle", face="neutral", ry=200: guy((-1.0, 0, -0.6), "#c2255c", "#3f4a5a", act=act, face=face, seed=1601, ry=ry, look="elder")
FRIEND = lambda act="idle", face="smile", top="#f59f00", ry=160: guy((1.1, 0, -0.8), top, "#3f4a5a", act=act, face=face, seed=1602, ry=ry)

s.B(3.8, "eyes", "", env(street(extra=[guy((6, 0, -3), "#1c7ed6", "#212529", act="wave", face="smile", seed=1603, ry=200), O("flame", (6, 0.9, -4), 0.3, "#ff922b")]),
                         GOLDEN, eye=ME_EYE, amb="calm"), tracker=T("MAPLE CREEK, OHIO", value="QUIET", sub="POPULATION 2,400"),
    hands={"pose": "hold", "holding": "cup"}, gaze=(14, -4), voices=[("Burgers in five!", "am_eric", 0.6)])
s.B(3.4, "eyes", "A letter shows up in your mailbox.", env(street(), GOLDEN, eye=ME_EYE, amb="calm"), hands={"pose": "reach"}, gaze=(0, -16),
    screen={"kind": "board", "title": "NOTICE OF CONSTRUCTION", "subtitle": "AI DATA CENTER · BEHIND ELM STREET",
            "rows": [["Size", "1.2 million sq ft"], ["Opens", "Next spring"]]})
s.B(3.6, "eyes", "Something huge is going up behind your house.", env(street(dc=True), OVERCAST, eye=(0, 1.62, 6), amb="rumble"),
    tracker=T("SIZE", count=(0, 21), unit=" FOOTBALL FIELDS", sub="BEHIND ELM STREET"), hands={"pose": "none"}, gaze=(0, 14),
    sfx=[{"type": "rumble", "at": 0.2, "dur": 3.0, "gain": 0.6}])
RACKS = [O("box", (0, -0.02, -6), [12, 0.04, 20], "#2b2f36"), O("box", (0, 3.2, -6), [12, 0.05, 20], "#3a3f48"),
         O("box", (-2.2, 1.1, -7), [1.2, 2.2, 14], "#1e2228"), O("box", (2.2, 1.1, -7), [1.2, 2.2, 14], "#1e2228"),
         O("sphere", (-1.58, 1.1, -7), 0.05, "#4dabf7", material="glow", count=60, seed=6, spread=[0, 1.8, 13], animate=[{"type": "pulse", "amount": 0.7}]),
         O("sphere", (1.58, 1.1, -7), 0.05, "#69db7c", material="glow", count=60, seed=7, spread=[0, 1.8, 13], animate=[{"type": "pulse", "amount": 0.7}]),
         O("plane", (0, 3.15, -6), [1.2, 0.3, 1], "#e7f5ff", material="glow", rotate=[90, 0, 0], count=6, seed=8, spread=[0, 0, 16])]
s.B(3.6, "eyes", "Inside: rows and rows of AI chips. Running all day.", env(RACKS, INDOOR, eye=(0, 1.62, 2), amb="lab", ambient=1.2), head="walk",
    tracker=T("OPEN", value="24/7", sub="DATA HALL 3"), hands={"pose": "none"}, gaze=(0, -2))
s.B(3.4, "eyes", "Every time you ask an AI something, a place like this answers.", env(street(dc=True), DUSK, eye=ME_EYE, amb="calm"),
    hands={"pose": "phone", "phone_text": "Ask AI anything…", "phone_time": "7:12"}, gaze=(0, -14))
BED = [O("box", (0, -0.02, -1.5), [6, 0.04, 7], "#6b5241"), O("box", (0, 1.5, -4.0), [6, 3, 0.1], "#3d4a6b"), O("box", (-3, 1.5, -1.5), [0.1, 3, 7], "#3d4a6b"),
       O("box", (3, 1.5, -1.5), [0.1, 3, 7], "#3d4a6b"), O("box", (0, 3.0, -1.5), [6, 0.05, 7], "#d9d2c7"),
       O("plane", (0, 1.7, -3.94), [2.6, 1.6, 1], "#1e2a52", material="glow"),
       O("sphere", (0, 1.4, -3.92), 0.05, "#ff4d4d", material="glow", count=8, seed=5, spread=[2.2, 0.2, 0.02], animate=[{"type": "pulse", "amount": 0.8}]),
       O("box", (0, 0.45, 0.6), [1.6, 0.4, 2.0], "#c9d6e3"), O("box", (0, 0.68, 0.4), [1.6, 0.08, 1.6], "#a5d8ff")]
s.B(3.6, "eyes", "Then you hear it. A low hum. All night.", env(BED, NIGHT, eye=(0, 1.0, 1.4), amb="rumble", ambient=1.0), tracker=T("THE HUM", clock="2:14:06 AM", sub="EVERY NIGHT"),
    hands={"pose": "none"}, gaze=(0, -4), sfx=[{"type": "rumble", "at": 0, "dur": 3.4, "gain": 0.5}])
s.B(3.6, "front", "\"I haven't slept right in weeks.\"", env(street(dc=True, extra=[MOM("think", "sad", ry=15)]), OVERCAST, focus=(-1.0, 1.4, -0.6), zoom=0.7, amb="rumble"),
    by="Your mom", voices=[("I haven't slept right in weeks.", "af_heart", 0.3)])
s.B(3.8, "eyes", "A data center like this uses as much power as 100,000 homes.", env(street(dc=True), DUSK, eye=(0, 4, 6), amb="rumble"),
    tracker=T("POWER USE", count=(0, 100000), unit=" HOMES", sub="ONE AI DATA CENTER"), hands={"pose": "none"}, gaze=(0, 0), by="IEA, 2025")
s.B(3.4, "eyes", "Your electric bill comes in. Higher.", env(street(dc=True), DUSK, eye=ME_EYE, amb="calm"),
    hands={"pose": "phone", "phone_text": "Electric bill: $212 (+$38)", "phone_time": "8:02"}, gaze=(0, -14),
    tracker=T("YOUR BILL", count=(174, 212), prefix="$", sub="THIS MONTH", alert=True))
SCHOOL = [O("box", (0, -0.03, -14), [80, 0.04, 60], "#7aa35a"), O("box", (0, 3, -18), [24, 6, 10], "#c47a5a"), O("box", (0, 6.2, -18), [25, 0.4, 11], "#8a4f3a"),
          O("plane", (0, 3.4, -12.95), [10, 1.2, 1], "#f8f9fa", material="glow"),
          O("plane", (-6, 2.2, -12.95), [3, 2, 1], "#a5d8ff", material="glow", count=3, seed=2, spread=[14, 0, 0]),
          crowd(14, 1611, at=(0, 0, -9), spread=(14, 0, 4), act="cheer", face="smile", ry=180)]
s.B(3.6, "eyes", "But the town gets millions in new taxes. A new school gym.", env(SCHOOL, DAY, eye=(0, 1.62, 2), amb="calm"),
    tracker=T("NEW TAX MONEY", count=(0, 12000000), prefix="$", sub="PER YEAR"), hands={"pose": "none"}, gaze=(0, 6), effects=["rays"])
SITE = [O("box", (0, -0.03, -14), [80, 0.04, 60], "#b08d5b"), O("box", (-6, 1.5, -18), [5, 3, 3], "#f08c00"), O("box", (-6, 4, -18), [0.4, 6, 0.4], "#f2c94c"),
        O("box", (-3, 7, -18), [6, 0.4, 0.4], "#f2c94c"), crowd(12, 1621, at=(0, 0, -10), spread=(14, 0, 6), act="walk", ry=180),
        O("box", (0, 2.3, -10), [0.5, 0.25, 0.5], "#ffd43b", count=12, seed=1621, spread=[14, 0, 6])]
s.B(3.4, "eyes", "And 300 people get jobs building it.", env(SITE, DAY, eye=(0, 1.62, 2), amb="rumble"), tracker=T("NEW JOBS", count=(0, 300), sub="CONSTRUCTION"),
    hands={"pose": "none"}, gaze=(0, 2))
s.B(3.6, "front", "Your best friend is one of them.", env(street(dc=True, extra=[FRIEND("cheer", "smile", "#f2c94c", ry=-15)]), DAY, focus=(1.1, 1.4, -0.8), zoom=0.7, amb="calm"),
    voices=[("Bro, I'm finally hired!", "am_puck", 0.4)])
HALL = [O("box", (0, -0.02, -6), [16, 0.04, 16], "#8c6d4f"), O("box", (0, 2.5, -13), [16, 5, 0.2], "#e9e0d0"),
        O("plane", (0, 3.4, -12.85), [6, 1, 1], "#2f6fd6", material="glow"),
        crowd(40, 1631, at=(0, 0, -7), spread=(12, 0, 7), act="idle", ry=180), O("box", (0, 0.6, -11), [3, 1.2, 1], "#5c3d2e")]
s.B(3.6, "eyes", "Election night. Your town votes on a second one.", env(HALL, NIGHT, eye=(0, 1.62, 2), amb="room", ambient=1.4), tracker=T("SECOND DATA CENTER", value="VOTE", sub="NOV 3"),
    hands={"pose": "none"}, gaze=(0, 0), banner={"kicker": "LIVE", "title": "VOTERS IN 10 STATES SAY NO TO DATA CENTERS", "subtitle": "ELECTION NIGHT"})
s.B(3.6, "eyes", "In one poll, 3 in 4 people didn't want one near their home.", env(HALL, NIGHT, eye=(0, 1.62, -1), amb="room", ambient=1.4),
    tracker=T("OPPOSED", value="3 IN 4", sub="AUG 2026 POLL"), hands={"pose": "none"}, gaze=(-20, 0))
SPLIT = street(dc=True, extra=[MOM("point", "angry", ry=20), FRIEND("point", "smile", "#f2c94c", ry=-20)])
s.B(3.6, "front", "Your mom votes no. Your best friend votes yes.", env(SPLIT, DUSK, focus=(0, 1.55, -0.7), zoom=1.15, amb="calm"),
    voices=[("No more humming.", "af_heart", 0.3), ("No more jobs, then?", "am_puck", 1.8)])
s.B(3.8, "eyes", "The count comes in. It's a tie.", env(HALL, NIGHT, eye=(0, 1.62, 2), amb="room", ambient=1.4), tracker=T("YES · NO", value="1,203 · 1,203", sub="ONE BALLOT LEFT", alert=True),
    hands={"pose": "none"}, gaze=(0, 4), sfx=[{"type": "heartbeat", "at": 0.2, "dur": 3.2, "gain": 0.7}])
BOOTH = [O("box", (0, -0.02, -1), [4, 0.04, 4], "#ced4da"), O("box", (0, 1.0, -1.2), [1.6, 2.0, 0.06], "#495057"),
         O("box", (-0.8, 1.0, -0.6), [0.06, 2.0, 1.2], "#495057"), O("box", (0.8, 1.0, -0.6), [0.06, 2.0, 1.2], "#495057"),
         O("box", (0, 1.05, -0.8), [1.0, 0.05, 0.6], "#f1f3f5"), O("plane", (0, 1.08, -0.8), [0.45, 0.55, 1], "#ffffff", rotate=[-90, 0, 0])]
s.B(3.8, "eyes", "The last ballot is yours.", env(BOOTH, INDOOR, eye=(0, 1.62, 0.6), amb="room", ambient=1.5), tracker=T("DECIDING VOTE", value="YOU", big=True),
    hands={"pose": "point"}, gaze=(0, -38))

s.save("bp_datacenter", "What if an *AI data center* was built next to your house?",
       "First-person: an AI data center goes up behind your street; a night hum and a higher power bill against new school money and 300 jobs, until the town vote is tied and the last ballot is yours.",
       "Yes or no: would you vote for it?", accent="#4dabf7", skin="#e0ac69", sleeve="#495057", thumb="THE LAST VOTE IS YOURS", thumb_beat=2)
