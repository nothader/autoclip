"""What if every nurse walked out tomorrow? (our neutral rework of the 'everyone in one group leaves' video). Block POV.
Anchors (widely cited): nurses are the largest group of health-care workers; the US has about 3 million working registered nurses;
when emergency rooms are overwhelmed, hospitals go on 'ambulance diversion' and send ambulances elsewhere."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, DAY, INDOOR, DAWN, DUSK, OVERCAST  # noqa: E402
from places import hospital_room, street  # noqa: E402

s = Story()
ROOM = lambda extra=(), light=1.0: env(hospital_room(seed=4, wall="#e3ebe6", extra=extra), DAWN, eye=(0, 1.15, 1.25), amb="room", ambient=1.3 * light,
                                       light=1.8 * light, bounce="#e7ecef")
CALL = O("sphere", (1.2, 1.2, 0.6), 0.06, "#ff6b6b", material="glow", animate=[{"type": "pulse", "amount": 0.8}])
HALL = [O("box", (0, -0.02, -8), [4, 0.04, 20], "#c9d1cc"), O("box", (-2, 1.5, -8), [0.1, 3, 20], "#e3ebe6"), O("box", (2, 1.5, -8), [0.1, 3, 20], "#e3ebe6"),
        O("box", (0, 3.0, -8), [4, 0.05, 20], "#f1f3f5"), O("plane", (0, 2.97, -8), [0.8, 0.4, 1], "#ffffff", material="glow", rotate=[90, 0, 0], count=5, seed=2, spread=[0, 0, 16]),
        O("sphere", (-1.95, 2.3, -8), 0.07, "#ff6b6b", material="glow", count=8, seed=3, spread=[0, 0, 16], animate=[{"type": "pulse", "amount": 0.8}]),
        O("sphere", (1.95, 2.3, -8), 0.07, "#ff6b6b", material="glow", count=8, seed=4, spread=[0, 0, 16], animate=[{"type": "pulse", "amount": 0.8}]),
        O("box", (1.2, 0.5, -5), [0.8, 1.0, 1.6], "#adb5bd")]
DOC = lambda at=(0.9, 0, -1.4), act="run": guy(at, "#f8f9fa", "#495057", act=act, face="shock", seed=501, ry=200)

s.B(3.8, "eyes", "", ROOM([CALL]), tracker=T("ST. LUKE'S · WARD 6", clock="6:58:30 AM", sub="DAY AFTER YOUR SURGERY"), hands={"pose": "idle"}, gaze=(0, -6))
s.B(3.4, "eyes", "You wake up after surgery. Shift change is at 7.", ROOM([CALL]), hands={"pose": "idle"}, gaze=(0, 4))
s.B(3.4, "eyes", "7:00. Nobody comes in.", ROOM([CALL]), tracker=T("ST. LUKE'S · WARD 6", clock="7:00:02 AM", sub="SHIFT CHANGE"), hands={"pose": "point"}, gaze=(30, -10),
    sfx=[{"type": "beep", "at": 0.4}, {"type": "beep", "at": 1.6}])
s.B(3.6, "eyes", "You find out every nurse in the country walked out.", env(HALL, INDOOR, eye=(0, 1.62, 1.0), amb="room", ambient=1.4),
    tracker=T("NURSES ON SHIFT", count=(3_000_000, 0), sub="UNITED STATES", alert=True), hands={"pose": "grab"}, head="walk",
    banner={"kicker": "BREAKING NEWS", "title": "NURSES WALK OUT NATIONWIDE", "subtitle": "HOSPITALS SCRAMBLE"})
s.B(3.4, "eyes", "Down the hall, every call light is blinking.", env(HALL, INDOOR, eye=(0, 1.62, 1.0), amb="room", ambient=1.3), hands={"pose": "grab"}, gaze=(0, 4),
    tracker=T("CALL LIGHTS", count=(3, 41), sub="WARD 6 · UNANSWERED", alert=True))
s.B(3.4, "eyes", "A doctor runs past you. Alone.", env(HALL + [DOC((0.4, 0, -2.2))], INDOOR, eye=(0, 1.62, 1.0), amb="room", ambient=1.3), hands={"pose": "grab"},
    voices=[("I need someone in room twelve! Anyone!", "am_michael", 0.3)])
s.B(3.6, "eyes", "You never knew: nurses are the biggest group in health care.", env(HALL, INDOOR, eye=(0, 1.62, -4), amb="room", ambient=1.2),
    tracker=T("HEALTH-CARE WORKERS", value="#1", sub="NURSES · LARGEST GROUP"), hands={"pose": "none"}, gaze=(0, 0))
s.B(3.4, "eyes", "Your 8 AM pain meds don't arrive.", ROOM([CALL], light=0.9), tracker=T("ST. LUKE'S · WARD 6", clock="8:12:40 AM", sub="MEDS: NOT GIVEN", alert=True),
    hands={"pose": "idle", "tremble": 0.5}, gaze=(-20, -10))
s.B(3.4, "eyes", "Nobody checks your stitches. Nobody checks anyone.", ROOM([CALL], light=0.9), hands={"pose": "none"}, gaze=(0, -30))
ER = street(seed=51, people=40, cars=0, extra=[O("box", (0, 2.5, -14), [16, 5, 6], "#e9ecef"), O("plane", (0, 4.2, -10.95), [8, 1.2, 1], "#c92a2a", material="glow"),
                                                O("box", (-3, 1.3, -9), [2.4, 2.6, 6], "#f8f9fa", count=4, seed=5, spread=[10, 0, 4]),
                                                O("sphere", (-3, 2.8, -9), 0.2, "#ff6b6b", material="glow", count=4, seed=5, spread=[10, 0, 4], animate=[{"type": "pulse", "amount": 0.7}])])
s.B(3.6, "far", "Outside your window, the ER line wraps around the block.", env(ER, OVERCAST, focus=(0, 2, -10), zoom=2.6, amb="wind"),
    tracker=T("ER WAIT", count=(2, 14), unit=" HOURS", sub="ST. LUKE'S · ENTRANCE B", alert=True))
s.B(3.6, "eyes", "You watch the ambulances get sent away. No room.", env(ER, OVERCAST, eye=(0, 1.62, 2), amb="wind"), hands={"pose": "none"}, gaze=(-10, 2),
    sfx=[{"type": "siren", "at": 0.2, "dur": 3.2, "gain": 0.6}], banner={"kicker": "LIVE", "title": "EVERY HOSPITAL IN THE CITY ON DIVERSION", "subtitle": "AMBULANCES REROUTED"})
NICU = [O("box", (0, -0.02, -3), [8, 0.04, 8], "#dfe7e3"), O("box", (0, 1.5, -6), [8, 3, 0.1], "#e8f0ec"),
        O("box", (-1.6, 0.9, -3.4), [0.9, 0.5, 0.6], "#bfe3ff", material="glass", opacity=0.5, count=3, seed=6, spread=[4, 0, 0]),
        O("sphere", (-1.6, 1.25, -3.4), 0.08, "#58f08e", material="glow", count=3, seed=6, spread=[4, 0, 0], animate=[{"type": "pulse", "amount": 0.6}]),
        guy((0.4, 0, -1.8), "#7048e8", "#3f4a5a", act="think", face="sad", seed=511)]
s.B(3.6, "front", "Upstairs, new parents like you try machines they never touched.", env(NICU, INDOOR, focus=(0, 1.4, -1.8), zoom=0.7, amb="room", ambient=1.4),
    tracker=T("NEWBORN ICU", value="0 NURSES", sub="14 BABIES", alert=True), voices=[("Which one is the alarm? Which button?!", "am_eric", 0.5)])
s.B(3.4, "eyes", "By noon, a doctor is emptying your bedpan.", ROOM([DOC((0.9, 0, -1.4), act="kneel")]), tracker=T("ST. LUKE'S · WARD 6", clock="12:04:10 PM", sub="DOCTORS ON NURSE DUTY"),
    hands={"pose": "none"}, gaze=(20, -8))
s.B(3.4, "eyes", "You finally understand who was keeping you alive.", ROOM([CALL], light=0.8), hands={"pose": "none"}, gaze=(0, 0), effects=["darken"])
NURSE = guy((-0.8, 0, -1.1), "#4dabf7", "#4dabf7", act="wave", face="smile", seed=521, ry=165)
s.B(3.6, "eyes", "Next morning, 7 AM. Your door opens.", ROOM([NURSE], light=1.2), tracker=T("ST. LUKE'S · WARD 6", clock="7:00:05 AM", sub="DAY 2 · SHIFT CHANGE"),
    hands={"pose": "idle"}, gaze=(-18, 4), effects=["rays"], voices=[("Good morning. Sorry I'm late. Let's look at those stitches.", "af_heart", 0.5)])
s.B(3.6, "eyes", "One day. That's all it took for everyone to notice.", ROOM([NURSE], light=1.2), tracker=T("NURSES ON SHIFT", value="3,000,000", sub="BACK AT WORK", big=True),
    hands={"pose": "idle"}, gaze=(-18, 4))

s.save("bp_nurses", "What if every *nurse* walked out tomorrow?",
       "First-person from a hospital bed: every nurse leaves at 7 AM; call lights, missed meds, an ER line around the block, ambulance diversion, and one day that shows who keeps hospitals running.",
       "Would your hospital last one day?", accent="#4dabf7", skin="#c68642", sleeve="#a5c8e1", thumb="0 NURSES", thumb_beat=3)
