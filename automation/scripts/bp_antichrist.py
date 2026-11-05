"""What if the Antichrist appeared? Believer's POV (owner's choice), our own scenes. Block POV format.
Sources: 1 Thessalonians 5:3 ('peace and safety', then destruction), Revelation 13:3 (a fatal wound healed), 13:13 (fire from heaven),
13:15 (the image given breath to speak), 13:16-17 (no one could buy or sell without the mark), 2 Thessalonians 2:4 (proclaims himself God).
Islamic tradition warns of the Dajjal, who offers fire that is really paradise and paradise that is really fire. Leader is fictional."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, NIGHT, INDOOR, DUSK  # noqa: E402
from places import street, church, living_room  # noqa: E402

s = Story()
LEADER = lambda at=(0, 0.12, -6.5), act="idle", face="smile", s_=1.8: [O("block_person", at, s_, "#15171c", seed=1401, action=act, expression=face, rotate=[0, 180, 0], color2="#15171c"),
                                                                      O("sphere", (at[0], at[1] + 1.8 * s_, at[2] - 1.2), 1.0, "#ffcf8a", material="glow", opacity=0.15)]
SQUARE = lambda extra=(), sky=NIGHT, people=36: env(street(seed=141, people=people, cars=0, extra=[O("plane", (-7.9, 8, -16), [10, 6, 1], "#ffcf8a", material="glow", rotate=[0, 90, 0]),
                                                                                                O("plane", (7.9, 9, -24), [10, 6, 1], "#ffcf8a", material="glow", rotate=[0, -90, 0])]
                                                                       + list(extra)), sky, eye=(0, 1.62, 2), amb="calm", stars=True, ambient=2.0, light=2.6)
MARK = lambda a, b, alert=False: T("WITH HIS MARK", count=(a, b), sub="PEOPLE", alert=alert)

s.B(3.8, "eyes", "", SQUARE(LEADER()), tracker=T("WITH HIS MARK", value="0", sub="NOT YET"), hands={"pose": "idle"}, gaze=(0, 6), voices=[("Peace! Peace!", "af_nicole", 0.6)])
s.B(3.6, "eyes", "One man ends every war on Earth. In one night.", SQUARE(LEADER(act="cheer")), hands={"pose": "idle"}, gaze=(0, 10), banner={"kicker": "BREAKING NEWS", "title": "ALL WARS END TONIGHT",
                                                                                                                                          "subtitle": "193 NATIONS SIGN"})
s.B(3.6, "eyes", "He doesn't come with horns. He comes with peace.", SQUARE(LEADER((0, 0.12, -4.2), face="smile", s_=1.7), people=40), by="1 Thessalonians 5:3", hands={"pose": "none"}, gaze=(0, 12))
s.B(3.4, "eyes", "Then the signs begin.", SQUARE(LEADER(act="point") + [O("sphere", (0, 30, -40), 3, "#ff7a1a", material="glow", animate=[{"type": "move", "to": [0, 2, -16]}])], DUSK),
    hands={"pose": "shield"}, gaze=(0, 26), effects=["shake"], sfx=[{"type": "boom", "at": 2.4}])
s.B(3.6, "eyes", "Fire falls from the sky. In front of everyone.", SQUARE(LEADER(act="point") + [O("flame", (0, 0, -18), 3, "#ff7a1a")], DUSK), by="Revelation 13:13", tracker=MARK(0, 0),
    hands={"pose": "shield"}, gaze=(0, 6), effects=["heat"])
s.B(3.4, "eyes", "Someone attacks him. A wound no one survives.", SQUARE(LEADER(act="lie", face="shock"), DUSK), hands={"pose": "none"}, gaze=(0, -6), effects=["darken", "shake"])
s.B(3.6, "eyes", "Three days later, he stands back up.", SQUARE(LEADER(act="cheer", face="smile"), NIGHT), by="Revelation 13:3", hands={"pose": "none"}, gaze=(0, 10), effects=["rays"])
s.B(3.6, "eyes", "The whole world kneels. Except you.", SQUARE(LEADER() + [crowd(60, 1411, at=(0, 0.12, -9), spread=(10, 0, 6), act="pray", ry=180)], NIGHT, people=0),
    tracker=MARK(0, 38_000_000), hands={"pose": "none"}, gaze=(0, -4))
STATUE = [O("block_person", (0, 0.12, -20), 7, "#e9ecef", seed=1402, action="cheer", expression="smile", rotate=[0, 180, 0], color2="#e9ecef")]
s.B(3.6, "eyes", "His statue starts to speak.", SQUARE(STATUE, NIGHT), by="Revelation 13:15", hands={"pose": "none"}, gaze=(0, 24), voices=[("I am your god.", "am_onyx", 0.5)],
    effects=["rays"])
s.B(3.6, "eyes", "\"Get your mark. Three seconds. Right hand.\"", env(living_room(), NIGHT, eye=(0, 1.62, 1), amb="room", ambient=1.3),
    hands={"pose": "phone", "phone_text": "GET YOUR MARK · 3 SECONDS · RIGHT HAND", "phone_time": "9:12"}, gaze=(0, -14), tracker=MARK(38_000_000, 1_100_000_000))
CHURCH = church(seed=14, pews=False, extra=[O("box", (0, 1.6, -18.6), [2.4, 3.2, 0.1], "#495057"), O("box", (0, 1.6, -18.5), [0.6, 0.6, 0.06], "#c92a2a")])
s.B(3.4, "eyes", "Your church is locked. By order.", env(CHURCH, NIGHT, eye=(0, 1.62, -12), amb="room", ambient=1.0), hands={"pose": "reach"}, gaze=(0, 4),
    tracker=MARK(1_100_000_000, 3_900_000_000))
CELLAR = [O("box", (0, -0.02, -2), [6, 0.04, 6], "#3a3530"), O("box", (0, 1.4, -4), [6, 2.8, 0.1], "#4b4238"), O("flame", (0, 0.4, -2.2), 0.25, "#ffb85c"),
          crowd(6, 1421, at=(0, 0, -3.6), spread=(3.4, 0, 0.6), act="pray", ry=0)]
s.B(3.4, "eyes", "Believers pray in secret. In basements.", env(CELLAR, INDOOR, eye=(0, 1.5, 1.4), amb="room", ambient=0.9, light=1.0), hands={"pose": "idle"}, gaze=(0, -10))
s.B(3.6, "eyes", "Muslims were warned too. His fire is paradise. His paradise is fire.", env(CELLAR, INDOOR, eye=(0, 1.5, 1.4), amb="room", ambient=0.9, light=1.0), hands={"pose": "none"},
    gaze=(0, -14), tracker=MARK(3_900_000_000, 5_600_000_000))
STORE = [O("box", (0, -0.02, -2), [8, 0.04, 8], "#d9d4cc"), O("box", (0, 0.5, -1.6), [1.6, 1.0, 0.7], "#495057"), O("box", (0, 1.2, -1.9), [0.6, 0.5, 0.05], "#212529"),
         O("plane", (0, 1.2, -1.87), [0.5, 0.4, 1], "#4dabf7", material="glow"), O("plane", (0, 1.02, -1.24), [0.5, 0.3, 1], "#ff6b6b", material="glow", rotate=[-90, 0, 0])]
s.B(3.6, "eyes", "Without his mark, you can't even buy bread.", env(STORE, INDOOR, eye=(0, 1.62, 0.6), amb="room", ambient=1.4), by="Revelation 13:17", hands={"pose": "reach"}, gaze=(0, -28),
    tracker=T("TOTAL", value="$2.49", sub="SCAN HAND TO PAY", alert=True), voices=[("Scan your hand, please.", "af_bella", 0.4)])
s.B(3.6, "eyes", "Your best friend already has it. He looks... peaceful.", env(street(seed=142, people=10, cars=0, extra=[guy((0.4, 0, -1.4), "#c92a2a", "#212529", act="wave", face="smile",
                                                                                                                          seed=1431, ry=180)]), DUSK, eye=(0, 1.62, 1), amb="calm"),
    tracker=MARK(5_600_000_000, 7_900_000_000, True), hands={"pose": "none"}, gaze=(0, 0), voices=[("Just do it, man. It doesn't even hurt.", "am_eric", 0.5)])
s.B(3.8, "eyes", "The scanner is glowing. Everyone is watching you.", env(STORE, INDOOR, eye=(0, 1.62, 0.6), amb="room", ambient=1.2), tracker=T("WITH HIS MARK", value="7,900,000,000", sub="AND YOU?", big=True),
    hands={"pose": "reach", "tremble": 0.6}, gaze=(0, -30))

s.save("bp_antichrist", "What if the *Antichrist* appeared?",
       "Believer's POV: a fictional leader ends every war, survives a fatal wound, makes a statue speak, and soon nobody can buy bread without his mark.",
       "Would you recognize him?", accent="#ff4b2b", skin="#a0522d", sleeve="#25324a", thumb="HE COMES WITH PEACE", thumb_beat=2)
