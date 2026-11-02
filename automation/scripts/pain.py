"""What if men and women felt each other's pain? (swap recipe, bold). Facts kept soft: UCL's John Guillebaud said period cramps can be
'almost as bad as having a heart attack'; childbirth is widely ranked among the most painful human experiences."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403

v = Video()
HE, SHE = (lambda act="idle", anim=(): P((-0.7, 0, -6), BOY, act, 2, ry=180, anim=anim)), (lambda act="idle", anim=(): P((0.7, 0, -6), GIRL, act, 3, ry=180, anim=anim))
pk = lambda extra=(): park([crowd(10, 4, at=(0, 0, -14), spread=(30, 0, 10))] + list(extra))
v.B(4.4, "follow", "In 3 seconds, every man and woman starts feeling each other's pain.", V(pk([HE("walk"), SHE("walk")]), SKY, focus=(0, 1.2, -6), zoom=1.2),
    "+0 SEC", "EVERY COUPLE ON EARTH", move="none", sfx=[{"type": "shimmer", "at": 3.0, "gain": 0.7}])
v.B(3.2, "side", "He stubs his toe. She screams too.", V(pk([HE("kneel"), SHE("kneel"), O("box", (-0.4, 0.15, -6.4), [0.4, 0.3, 0.4], "#8d6e57")]), SKY, focus=(0, 0.9, -6), zoom=0.8),
    "+1 MIN", effects=["shake"], sfx=[{"type": "impact", "at": 0.3, "gain": 0.9}])
bed = room("#ffdeeb", "#c9a27a", extra=[O("box", (-2, 0.35, -6), [2.4, 0.5, 3], "#f8f9fa"), O("box", (2.6, 0.75, -7), [1.4, 0.06, 0.8], "#8d6e57")])
v.B(3.4, "follow", "Then her period starts. He feels every cramp.",
    V(bed + [P((-2, 0.6, -6), BOY, "lie", 2, ry=90, anim=[{"type": "wobble", "amount": 0.2, "speed": 3}]), P((1, 0, -5), GIRL, "point", 3, ry=180)],
      ["#ffdeeb", "#fcc2d7"], focus=(0, 1.0, -5.5), zoom=1.0, bounce="#ffdeeb"), "+3 DAYS", effects=["shake"])
v.B(3.4, "side", "One doctor said cramps can hurt almost like a heart attack.",
    V(bed + [P((-2, 0.6, -6), BOY, "lie", 2, ry=90, anim=[{"type": "wobble", "amount": 0.25, "speed": 4}])],
      ["#ffdeeb", "#fcc2d7"], focus=(-2, 0.9, -6), zoom=0.4, bounce="#ffdeeb"), "+3 DAYS", sfx=[{"type": "heartbeat", "at": 0.3, "dur": 2.6, "gain": 0.6}])
v.B(3.2, "follow", "Grown men call in sick for cramps. Every month.", V(city([crowd(14, 9, at=(0, 0, -14), spread=(20, 0, 20), act="kneel", col=BOY), crowd(6, 16, at=(0, 0, -10), spread=(10, 0, 10), col=GIRL)]), GOLD,
    focus=(0, 1.2, -12), zoom=1.8), "+1 MONTH", transition="whip")
store = room("#fff3bf", "#e9ecef", w=12, d=12, extra=[O("box", (-3, 0.9, -7), [0.8, 1.8, 8], "#adb5bd", material="metal"), O("box", (3, 0.9, -7), [0.8, 1.8, 8], "#adb5bd", material="metal"),
             O("box", (-3, 1.3, -7), [0.9, 0.2, 0.3], "#e03131", count=6, seed=4, spread=[0, 0, 7], animate=[{"type": "shrink"}]),
             crowd(8, 14, at=(0, 0, -6), spread=(4, 0, 8), act="run", col=BOY)])
v.B(3.2, "dolly", "Pain pills sell out in every store.", V(store, ["#fff3bf", "#ffe066"], focus=(0, 1.2, -6), zoom=1.0, bounce="#fff3bf"), "+1 MONTH")
hosp = room("#e7f5ff", "#dee2e6", extra=[O("box", (0, 0.5, -6), [1.4, 0.7, 2.6], "#f8f9fa"), O("box", (2.6, 1.2, -8), [0.8, 1.6, 0.5], "#adb5bd", material="metal"),
            P((2, 0, -5), "#40c057", "walk", 8, outfit="scrubs", ry=270, anim=[{"type": "move", "to": [1, 0, -5]}])])
v.B(3.6, "follow", "Here's the scary part: then the baby comes. And Dad feels all of it.", V(hosp + [P((0, 0.85, -6), GIRL, "lie", 3), P((-1.6, 0, -5.2), BOY, "kneel", 2, ry=90,
    anim=[{"type": "wobble", "amount": 0.15, "speed": 4}])], ["#e7f5ff", "#d0ebff"], focus=(0, 1.0, -5.6), zoom=1.0, bounce="#e7f5ff"), "+9 MONTHS", transition="dip",
    stat={"value": "TOP 3", "label": "CHILDBIRTH: AMONG THE MOST PAINFUL THINGS A PERSON FEELS", "count_up": False}, sfx=[{"type": "heartbeat", "at": 0.3, "dur": 3.0, "gain": 0.7}])
v.B(3.2, "closeup", "The whole hospital hears him yell.", V(hosp + [P((-1.6, 0, -5.2), BOY, "kneel", 2, ry=0, anim=[{"type": "wobble", "amount": 0.2, "speed": 5}])],
    ["#e7f5ff", "#d0ebff"], focus=(-1.6, 1.0, -5.2), zoom=0.7), "+9 MONTHS", effects=["shake"], sfx=[{"type": "swell", "at": 0.2, "dur": 2.4, "gain": 0.6}])
field = [O("box", (0, -0.02, -14), [60, 0.04, 60], "#2f9e44")] + [O("box", (0, 0.01, -14 + i * 4), [40, 0.02, 0.15], "#f8f9fa") for i in range(-3, 4)] + \
        [P((-1, 0, -12), "#e03131", "run", 4, anim=[{"type": "move", "to": [-0.2, 0, -10]}]), P((1, 0, -8), "#1c7ed6", "run", 5, ry=180, anim=[{"type": "move", "to": [0.2, 0, -10]}]),
         crowd(16, 15, at=(-24, 0, -14), spread=(2, 0, 30), act="idle")]
v.B(3.2, "wide", "Football gets VERY gentle. Every tackle hurts someone at home.", V(field, SKY, focus=(0, 1.0, -10), zoom=0.8), "+1 YEAR", transition="whip",
    sfx=[{"type": "impact", "at": 1.8, "gain": 0.8}])
v.B(3.6, "far", "Couples stop fighting fast. Hurting them... hurts you.", V(pk([HE("idle"), SHE("idle")]), DUSK, focus=(0, 1.2, -6), zoom=1.8), "+1 YEAR", move="pull_out",
    effects=["glow"])
v.save("pain", "What if men and women felt each other's pain?", "Every couple on Earth feels each other's pain: stubbed toes, cramps, even childbirth.",
       "bold", "SINCE THE LINK", ["WHO WOULD", "CRY FIRST?"], "HE FEELS *HER* PAIN", 2, accent="#ff6b6b", captions=None)
