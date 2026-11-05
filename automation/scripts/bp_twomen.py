"""What if two men claimed to be Jesus? Believer's POV (owner's choice), our own scenes. Block POV format.
Sources: Matthew 24:24 (false christs will perform great signs to deceive), Matthew 24:26-27 (if they say he is in the desert, do not go;
his coming is like lightning, seen by all), 2 Thessalonians 2:9 (counterfeit signs). Islamic tradition also warns of a false messiah
(al-Masih ad-Dajjal). Our version is set in a fictional seaside city, not Rome."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, OVERCAST, GOLDEN, DUSK  # noqa: E402
from places import street, park  # noqa: E402

s = Story()
ROBE = lambda at, sash, seed, act="idle", face="neutral": [O("block_person", at, 1.25, "#f1ece4", seed=seed, action=act, expression=face, rotate=[0, 180, 0], color2="#f1ece4"),
                                                           O("box", (at[0], at[1] + 1.5, at[2] + 0.12), [0.18, 0.9, 0.05], sash, rotate=[0, 0, 30]),
                                                           O("sphere", (at[0], at[1] + 2.6, at[2] - 0.3), 0.5, "#fff3d0", material="glow", opacity=0.22)]
LEFT = lambda act="idle", face="neutral": ROBE((-1.6, 0.12, -4.6), "#c92a2a", 1301, act, face)
RIGHT = lambda act="idle", face="neutral": ROBE((1.6, 0.12, -5.0), "#1c7ed6", 1302, act, face)
STORM = ["#2a3140", "#6b7480"]
SEASIDE = lambda extra=(), sky=OVERCAST, people=24: env(street(seed=131, people=people, cars=1, extra=[O("box", (0, -0.5, -70), [200, 0.1, 40], "#24485e", material="glossy")] + list(extra)),
                                                       sky, eye=(0, 1.62, 2), amb="wind")
FOL = lambda a, b, alert=False: T("CITY FOLLOWS", value=f"{a}%  |  {b}%", sub="LEFT  ·  RIGHT", alert=alert)

s.B(3.8, "eyes", "", SEASIDE(), tracker=T("HE RETURNS IN", scramble=True, sub="NOBODY KNOWS THE HOUR"), hands={"pose": "idle"}, gaze=(0, 6))
s.B(3.4, "eyes", "At noon, the sun goes dark over your city.", SEASIDE(sky=STORM), hands={"pose": "none"}, gaze=(0, 30), effects=["darken"], sfx=[{"type": "rumble", "at": 0.2, "dur": 3}])
s.B(3.6, "eyes", "A man in white comes down in front of you.", SEASIDE(LEFT("float", "smile"), STORM), hands={"pose": "none"}, gaze=(-10, 12), effects=["rays"])
s.B(3.4, "eyes", "Then a second one. Right next to him.", SEASIDE(LEFT() + RIGHT("float", "smile"), STORM), hands={"pose": "none"}, gaze=(10, 12), effects=["rays"])
s.B(3.6, "eyes", "You hear both say it: \"I am the one.\"", SEASIDE(LEFT("point", "smile") + RIGHT("point", "smile"), STORM), tracker=FOL(0, 0), hands={"pose": "none"}, gaze=(0, 6),
    voices=[("I am the one you've been waiting for.", "am_onyx", 0.3), ("I am the one you've been waiting for.", "bm_george", 1.8)])
s.B(3.6, "eyes", "The right one lifts a hand. Rain hits your face. The drought is over.", SEASIDE(LEFT() + RIGHT("cheer", "smile") + [O("particles", (0, 10, -8), 0.08, "#a5d8ff", count=200, seed=4,
                                                                                                                                spread=[30, 20, 20], animate=[{"type": "drift", "axis": "y", "amount": -1}])],
                                                                                  STORM), tracker=FOL(4, 22), hands={"pose": "none"}, gaze=(12, 10))
s.B(3.6, "eyes", "You watch the left one heal a man in a wheelchair. He walks.", SEASIDE(LEFT("point", "smile") + [guy((-0.6, 0.12, -3.6), "#2f9e44", "#3f4a5a", act="cheer", face="smile", seed=1311, ry=200)],
                                                                                OVERCAST), tracker=FOL(25, 20), hands={"pose": "none"}, gaze=(-14, 2))
s.B(3.6, "eyes", "Gold rises out of the ground at your feet.", SEASIDE(RIGHT("cheer", "smile") + [O("box", (1.0, 0.2, -3.2), [0.3, 0.15, 0.15], "#f2c94c", material="metal", count=40, seed=5,
                                                                                                    spread=[3, 0.3, 2])], GOLDEN), tracker=FOL(21, 43), hands={"pose": "none"}, gaze=(14, -4))
s.B(3.4, "eyes", "Your phone: millions picking sides. Live.", SEASIDE(LEFT() + RIGHT(), GOLDEN), hands={"pose": "phone", "phone_text": "#TeamLeft  #TeamRight  trending", "phone_time": "12:41"},
    gaze=(0, -14), banner={"kicker": "LIVE", "title": "TWO MEN, ONE CLAIM", "subtitle": "CROWDS SPLIT IN THE SQUARE"})
s.B(3.6, "eyes", "A man beside you calls the right one a fake. He drops dead.", SEASIDE(RIGHT("point", "angry") + [guy((0.6, 0.12, -2.4), "#495057", "#212529", act="lie", face="shock", seed=1321, ry=180)],
                                                                             DUSK), tracker=FOL(36, 58, True), hands={"pose": "shield"}, gaze=(10, -6), effects=["shake"])
s.B(3.6, "eyes", "\"False christs will perform great signs. To fool even the faithful.\"", SEASIDE(LEFT() + RIGHT(), DUSK), by="Matthew 24:24", hands={"pose": "none"}, gaze=(0, 4))
s.B(3.6, "eyes", "You remember: Muslims were warned of a false messiah too.", SEASIDE(LEFT() + RIGHT(), DUSK), tracker=FOL(41, 58), hands={"pose": "none"}, gaze=(0, 4))
s.B(3.6, "eyes", "And the real return? You were told: like lightning. Seen by all.", SEASIDE(LEFT() + RIGHT(), DUSK), by="Matthew 24:27", hands={"pose": "none"}, gaze=(0, 24),
    effects=["lightning"])
s.B(3.6, "eyes", "Not two men in your square, asking you to follow.", SEASIDE(LEFT("point") + RIGHT("point"), DUSK), hands={"pose": "none"}, gaze=(0, 6))
s.B(3.8, "eyes", "Now both of them reach for your hand.", SEASIDE(ROBE((-0.9, 0.12, -2.2), "#c92a2a", 1301, "point", "smile") + ROBE((0.9, 0.12, -2.4), "#1c7ed6", 1302, "point", "smile"), DUSK, people=20),
    tracker=T("YOUR CHOICE", value="?", big=True), hands={"pose": "reach"}, gaze=(0, 8), voices=[("Come with me.", "am_onyx", 0.3), ("No. Come with me.", "bm_george", 1.5)])

s.save("bp_twomen", "What if two men claimed to be *Jesus*?",
       "Believer's POV in a seaside city: two robed men descend, both claim to be the one and both perform signs; the crowd splits while you remember the warnings about false christs.",
       "Who would you follow?", accent="#f2c94c", skin="#c68642", sleeve="#3f4a5a", thumb="WHICH ONE IS REAL?", thumb_beat=4)
