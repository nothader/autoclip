"""What if Islam was proven true? Believer's POV (owner's choice), our own scenes and words. Block POV format.
Source: hadith (Sahih al-Bukhari): the Hour will not come until the sun rises from the west; when people see it they will all believe,
but belief that begins then will not benefit a soul (cf. Qur'an 6:158). About 2 billion Muslims worldwide (widely cited)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from block import Story, O, T, env, guy, crowd, NIGHT, DAWN, INDOOR  # noqa: E402
from places import mosque, street  # noqa: E402

s = Story()
PRE = ["#1a2240", "#5a5a7a"]; WEST = ["#3a3a66", "#ffb37a"]
SEA = [O("box", (0, -0.6, -40), [300, 0.1, 300], "#20304a", material="glossy", animate=[{"type": "bob", "amount": 0.05, "speed": 0.5}]),
       O("box", (0, 0.0, 0), [3, 0.12, 30], "#7a5a3c"), O("box", (-1.45, 0.55, 0), [0.08, 1.0, 30], "#5c4430"), O("box", (1.45, 0.55, 0), [0.08, 1.0, 30], "#5c4430"),
       O("box", (40, 6, 60), [40, 12, 16], "#5b6476"), O("box", (-40, 9, 70), [30, 18, 16], "#6b7486"), O("cylinder", (-30, 14, 66), [1.2, 28, 1.2], "#d8d0c2")]
SUNW = O("sphere", (0, 7, 140), 9, "#ffd18a", material="glow")
DAD = guy((0.8, 0.06, -1.6), "#2b4f7a", "#3f4a5a", act="idle", face="neutral", seed=601, ry=200)
PIER = lambda extra=(), sky=PRE: env(SEA + list(extra), sky, eye=(0, 1.68, 1.5), amb="ocean", ambient=1.1, light=1.6, stars=sky is PRE)

s.B(3.8, "eyes", "", PIER([DAD]), tracker=T("SUNRISE", value="6:12 AM", sub="EXPECTED · EAST"), hands={"pose": "hold", "holding": "cup"}, gaze=(0, -2))
s.B(3.4, "eyes", "6:10 AM. You and your dad are waiting for the sunrise.", PIER([DAD]), hands={"pose": "hold", "holding": "cup"}, gaze=(20, 0),
    voices=[("Watch the east. Any second now.", "am_onyx", 0.4)])
s.B(3.2, "eyes", "But the east stays dark.", PIER([DAD]), tracker=T("SUNRISE", clock="6:12:40 AM", sub="EAST · NOTHING"), hands={"pose": "hold", "holding": "cup"}, gaze=(0, 4))
s.B(3.4, "eyes", "Behind you, the sky is turning gold.", PIER([DAD, SUNW], WEST), hands={"pose": "hold", "holding": "cup"}, gaze=(150, 6), effects=["rays"])
s.B(3.8, "eyes", "The sun is rising in the west.", PIER([DAD, SUNW], WEST), tracker=T("SUNRISE", value="WEST", sub="6:13 AM", alert=True), hands={"pose": "none"},
    gaze=(178, 8), effects=["rays", "bloom"], sfx=[{"type": "swell", "at": 0.2, "dur": 3.0}])
s.B(3.4, "eyes", "Your dad drops his cup. His hands are shaking.", PIER([DAD, SUNW], WEST), hands={"pose": "none"}, gaze=(140, -2),
    voices=[("SubhanAllah... it's the sign.", "am_onyx", 0.5)])
s.B(3.8, "eyes", "This sign was described 1,400 years ago.", PIER([SUNW], WEST), tracker=T("FORETOLD", value="1,400 YEARS AGO", sub="7TH CENTURY"),
    hands={"pose": "none"}, gaze=(178, 6), effects=["rays"])
s.B(3.8, "eyes", "\"When people see it, they will all believe.\"", PIER([SUNW], WEST), by="Sahih al-Bukhari", hands={"pose": "none"}, gaze=(178, 10), effects=["rays"])
s.B(3.4, "eyes", "Your phone explodes. Every screen shows the same sky.", PIER([SUNW], WEST), hands={"pose": "phone", "phone_text": "SUN RISING IN THE WEST — LIVE", "phone_time": "6:14"},
    gaze=(178, -14), banner={"kicker": "LIVE", "title": "SUN RISES IN THE WEST", "subtitle": "SEEN IN EVERY COUNTRY"})
KNEEL = [crowd(14, 611, at=(0, 0.06, -6), spread=(2.4, 0, 10), act="pray", face="sad", ry=180), SUNW]
s.B(3.4, "eyes", "Along the pier, strangers fall to their knees.", PIER(KNEEL, WEST), hands={"pose": "none"}, gaze=(0, -10), effects=["rays"])
CITY = street(seed=61, people=50, cars=1, extra=[O("sphere", (0, 14, 90), 10, "#ffd18a", material="glow")])
s.B(3.4, "far", "In the city, millions run into the streets.", env(CITY, WEST, focus=(0, 2, -18), zoom=3.0, amb="wind"),
    tracker=T("PEOPLE WATCHING", count=(1_000_000_000, 8_100_000_000), sub="EVERY TIME ZONE"))
s.B(3.8, "eyes", "But the door of repentance closed with that sunrise.", PIER([SUNW], WEST), tracker=T("REPENTANCE", value="CLOSED", sub="SINCE SUNRISE", alert=True),
    hands={"pose": "none"}, gaze=(178, 4), effects=["darken"], sfx=[{"type": "drop", "at": 0.4}])
s.B(3.6, "eyes", "Faith that begins today... no longer counts.", PIER([SUNW], WEST), by="Qur'an 6:158", hands={"pose": "none"}, gaze=(178, 0), effects=["darken"])
MOSQ = mosque(seed=2, extra=[crowd(60, 621, at=(0, 0, -16), spread=(18, 0, 8), act="pray", ry=0), O("sphere", (0, 12, 70), 9, "#ffd18a", material="glow")])
s.B(3.6, "far", "Your local mosque overflows into the street.", env(MOSQ, WEST, focus=(0, 3, -20), zoom=2.6, amb="calm"),
    tracker=T("REPENTANCE", value="CLOSED", sub="SINCE SUNRISE", alert=True), voices=[("Allahu akbar...", "am_onyx", 0.6)])
s.B(3.6, "eyes", "You think about every prayer you said you'd start.", PIER([SUNW], WEST), hands={"pose": "idle", "tremble": 0.5}, gaze=(178, -20))
s.B(3.6, "eyes", "\"Tomorrow,\" you always said.", PIER([SUNW], WEST), tracker=T("TOMORROW", value="NEVER CAME", big=True), hands={"pose": "phone", "phone_text": "Reminder: start praying (snoozed 214×)",
                                                                                                                     "phone_time": "6:21"}, gaze=(178, -14))

s.save("bp_islam", "What if *Islam* was proven true?",
       "Believer's POV: at dawn on a pier the sun rises in the west, the sign described in the hadith; the world believes at once, but the door of repentance has closed.",
       "Would you be ready?", accent="#f2c94c", skin="#a0522d", sleeve="#3f4a5a", thumb="SUN RISES IN THE WEST", thumb_beat=4)
