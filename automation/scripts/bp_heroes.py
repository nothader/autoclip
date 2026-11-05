"""What if superheroes were real? (our own heroes: Volta, Bastion, Skylark — no existing characters). Block POV.
Anchors (widely cited): a lightning bolt is about 5 times hotter than the surface of the Sun; most home-insurance policies exclude damage
from war and similar events, so a 'super battle' claim would likely be denied."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, DAY, OVERCAST, GOLDEN, DUSK  # noqa: E402
from places import street  # noqa: E402

s = Story()
VOLTA = lambda at, act="fly": [guy(at, "#f2c94c", "#1c3d7a", act=act, face="angry", seed=401, ry=180),
                               O("sphere", (at[0], at[1] + 1.0, at[2]), 1.1, "#7fd3ff", material="glow", opacity=0.35)]
BASTION = lambda at, act="idle": [O("block_person", at, 2.6, "#2f9e44", seed=402, action=act, expression="angry", rotate=[0, 180, 0], color2="#1e3a2a"),
                                  O("box", (at[0] + 1.2, at[1] + 2.4, at[2] + 0.6), [2.2, 2.8, 0.25], "#adb5bd", material="metal")]
SKYLARK = lambda at: [guy(at, "#e03131", "#212529", act="fly", face="smile", seed=403, ry=180), O("plane", (at[0], at[1] + 0.9, at[2] - 0.35), [0.9, 1.4, 1], "#c92a2a")]
BOLT = lambda x=0, z=-20: O("box", (x, 25, z), [0.6, 50, 0.6], "#e7f5ff", material="glow", animate=[{"type": "pulse", "amount": 0.8}])
RIFT = [O("plane", (0, 38, -60), [10, 26, 1], "#b197fc", material="glow", rotate=[0, 0, 12], animate=[{"type": "pulse", "amount": 0.2}]),
        O("box", (0, 34, -55), [1.2, 0.6, 1.2], "#343a40", count=24, seed=6, spread=[30, 16, 10], animate=[{"type": "drift", "axis": "y", "amount": -0.3}])]
CITY = lambda seed=31, extra=(), people=20, cars=5: street(seed=seed, people=people, cars=cars, extra=extra)
DMG = lambda a, b, sub="YOUR STREET", alert=False, big=False: T("DAMAGE", count=(a, b), prefix="$", sub=sub, alert=alert, big=big)

s.B(3.8, "eyes", "", env(CITY(), DAY, eye=(0, 1.62, 2), amb="calm"), tracker=T("DAMAGE", value="$0", sub="YOUR STREET · 4:02 PM"),
    hands={"pose": "phone", "phone_text": "Is that... a person flying??", "phone_time": "4:02"}, gaze=(0, 12))
s.B(3.4, "eyes", "Your phone films a woman flying over traffic.", env(CITY(extra=VOLTA((1.5, 6, -9))), DAY, eye=(0, 1.62, 2), amb="calm"),
    hands={"pose": "phone", "phone_text": "REC 00:04", "phone_time": "4:02"}, gaze=(4, 22))
s.B(3.6, "eyes", "Her name is Volta. She fires real lightning.", env(CITY(extra=VOLTA((0.5, 5.5, -8)) + [BOLT(4, -22)]), DAY, eye=(0, 1.62, 2), amb="calm"),
    tracker=DMG(0, 1200), hands={"pose": "none"}, gaze=(0, 18), effects=["lightning", "shake"], sfx=[{"type": "thunder", "at": 0.6}])
s.B(3.4, "eyes", "Each bolt is about five times hotter than the Sun's surface.", env(CITY(extra=VOLTA((0.5, 5.5, -8)) + [BOLT(-3, -18)]), OVERCAST, eye=(0, 1.62, 2), amb="wind"),
    tracker=T("BOLT TEMPERATURE", value="≈ 30,000 °C", sub="SUN'S SURFACE ≈ 5,500 °C", alert=True), hands={"pose": "none"}, gaze=(0, 16), effects=["lightning"])
s.B(3.4, "eyes", "Across from you, a giant stops a bus with his shield.", env(CITY(extra=BASTION((-3, 0, -12)) + [O("box", (-3, 1.6, -15.5), [3, 3.2, 10], "#f08c00")]), DAY,
                                                                       eye=(0, 1.62, 2), amb="calm"), tracker=DMG(1200, 48000), hands={"pose": "none"}, gaze=(-12, 6),
    sfx=[{"type": "impact", "at": 0.5, "gain": 1.2}], effects=["shake"])
s.B(3.2, "eyes", "The bus is fine. The road isn't.", env(CITY(extra=BASTION((-3, 0, -12)) + [O("rock", (-2, 0.3, -9), 0.6, "#5a5d63", count=10, seed=4, spread=[6, 0.4, 4])]),
                                                       DAY, eye=(0, 1.62, 2), amb="calm"), tracker=DMG(48000, 410000), hands={"pose": "none"}, gaze=(-10, -6))
s.B(3.6, "eyes", "Then the sky above your street splits open.", env(CITY(extra=RIFT), DUSK, eye=(0, 1.62, 2), amb="rumble"), tracker=DMG(410000, 2_900_000, alert=True),
    hands={"pose": "none"}, gaze=(0, 34), effects=["shake", "darken"], sfx=[{"type": "rumble", "at": 0, "dur": 3.4}])
s.B(3.4, "eyes", "Machines pour through. Thousands of them, right over you.", env(CITY(extra=RIFT, people=40), DUSK, eye=(0, 1.62, 2), amb="rumble"), tracker=DMG(2_900_000, 40_000_000, alert=True),
    hands={"pose": "none"}, gaze=(0, 30), banner={"kicker": "BREAKING NEWS", "title": "SKY TORN OPEN DOWNTOWN", "subtitle": "STAY INDOORS"})
s.B(3.4, "far", "Every hero you've seen online shows up at once.", env(CITY(extra=VOLTA((0, 18, -30)) + BASTION((-4, 0, -24)) + SKYLARK((6, 16, -26)) + RIFT, people=10), DUSK,
                                                                focus=(0, 10, -30), zoom=4.5, amb="rumble"), tracker=DMG(40_000_000, 900_000_000, alert=True),
    banner={"kicker": "BREAKING NEWS", "title": "HEROES ASSEMBLE ON 5TH STREET", "subtitle": "YOUR STREET"})
s.B(3.4, "eyes", "Bastion throws a machine. It lands on your car.", env(CITY(extra=BASTION((-2, 0, -12)) + [O("box", (2.2, 0.9, -6), [2, 1.8, 4.4], "#495057", rotate=[0, 30, 18])]),
                                                                          DUSK, eye=(0, 1.62, 2), amb="rumble"), tracker=DMG(900_000_000, 6_000_000_000, alert=True),
    hands={"pose": "none"}, gaze=(14, -10), effects=["shake"], sfx=[{"type": "boom", "at": 0.4}])
s.B(3.4, "eyes", "Skylark grabs you before a wall comes down.", env(CITY(extra=SKYLARK((0.2, 4.4, 0.3)), people=0, cars=0), DUSK, eye=(0, 6, 2), amb="wind"), head="float",
    hands={"pose": "reach"}, gaze=(0, -30), voices=[("I got you! Hold on!", "af_sky", 0.3)])
s.B(3.6, "far", "Twenty minutes later, you look up. The rift is closed.", env(CITY(seed=32, people=30, cars=2), GOLDEN, focus=(0, 8, -30), zoom=4, amb="calm"),
    tracker=DMG(6_000_000_000, 160_000_000_000, big=True), effects=["rays"])
s.B(3.4, "eyes", "Your street is gone. Your car is a pancake.", env(CITY(seed=33, people=6, cars=0, extra=[O("rock", (0, 0.4, -8), 0.9, "#6c6f75", count=16, seed=7, spread=[12, 0.6, 12])]),
                                                                  GOLDEN, eye=(0, 1.62, 2), amb="wind"), tracker=T("DAMAGE", value="$160,000,000,000", sub="ONE AFTERNOON"),
    hands={"pose": "none"}, gaze=(0, -10))
s.B(3.6, "eyes", "You call your insurance.", env(CITY(seed=33, people=4, cars=0), GOLDEN, eye=(0, 1.62, 2), amb="wind"),
    hands={"pose": "phone", "phone_text": "Claim #48-2271: DENIED", "phone_time": "6:41"}, gaze=(0, -14),
    voices=[("I'm sorry, superhuman combat isn't covered under your policy.", "af_bella", 0.4)])
s.B(3.6, "eyes", "Most policies don't cover war. A super battle counts.", env(CITY(seed=33, people=4, cars=0), GOLDEN, eye=(0, 1.62, 2), amb="wind"),
    tracker=T("YOUR CLAIM", value="DENIED", sub="EXCLUSION: ACTS OF WAR", alert=True), hands={"pose": "phone", "phone_text": "Claim #48-2271: DENIED", "phone_time": "6:42"},
    gaze=(0, -14))
s.B(3.6, "eyes", "That night, the heroes are on every screen. Smiling.", env(CITY(seed=34, people=30, cars=0, extra=[O("plane", (0, 8, -30), [12, 7, 1], "#ffd8a8", material="glow")]),
                                                                           DUSK, eye=(0, 1.62, 2), amb="calm"),
    banner={"kicker": "LIVE", "title": "WHO PAYS FOR THIS?", "subtitle": "CITY ASKS HEROES TO REGISTER"}, hands={"pose": "none"}, gaze=(0, 10))
s.B(3.6, "eyes", "Nobody can arrest them. Nobody can make them pay.", env(CITY(seed=34, people=30, cars=0), NIGHT if False else DUSK, eye=(0, 1.62, 2), amb="calm"),
    tracker=T("WHO CAN STOP THEM", value="NOBODY", sub="NO LAW COVERS THIS"), hands={"pose": "none"}, gaze=(0, 22))

s.save("bp_heroes", "What if *superheroes* were real?",
       "First-person: three original heroes fight over your street; a live damage counter climbs to $160 billion and your insurance claim gets denied.",
       "Would you trust them?", accent="#ffd43b", skin="#c68642", sleeve="#3b5bdb", thumb="$160 BILLION", thumb_beat=11)
