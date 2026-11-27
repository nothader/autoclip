"""What if you slept through your alarm on exam day? 30 s Short (film look).
Structure: RACE AGAINST A DRAINING "TIME LEFT" METER — every beat a new obstacle on the run from bed to the exam
(alarm clock, calm dad in the kitchen, the street in pyjamas, the school bus leaving, the crossing guard, the hallway sprint,
the classroom door, the teacher). Opens on a close-up of the glowing 7:52 alarm clock (no phone, no stage stamps, no training tape).
Ending: LOOP — the exam is actually TOMORROW; cut to tomorrow morning: the same 7:52 clock and Mom's same shout, so the last
shot leads straight back into the first.
Real fact: the CDC says teens aged 13-18 need 8-10 hours of sleep per 24 hours.
Source: https://www.cdc.gov/sleep/about/index.html (CDC "About Sleep": How much sleep do I need?) and
https://archive.cdc.gov/www_cdc_gov/healthyschools/features/students-sleep.htm
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, meter, INDOOR, DAY, DAWN, SUNNY  # noqa: E402
from assets import (O, SKIN, person, people, screen_ui, text, lamp, room, bedroom, kitchen_home, street, school_hall,  # noqa: E402
                    classroom_real, chair, school_bus, stop_paddle, wall_clock, traffic_light, alarm_clock, table)

ACC = "#ff8787"
s = Story("slept_through_alarm", "What if you slept through your alarm on exam day?", accent=ACC, look="film",
          hook=["WHAT IF YOU", "SLEPT THROUGH", "EXAM DAY?"], hook_accent=1, skin=SKIN["tan"], sleeve="#91a7ff", mood="chill",
          grade={"tint": [1.04, 1.0, 0.96], "sat": 1.08, "contrast": 1.04})
MOM, DAD, JOG, GUARD, TEACH = "af_heart", "am_eric", "am_puck", "am_onyx", "af_nicole"


def left(frm, to, at=0.1):
    return meter("TIME LEFT", frm, to, at=at, color=ACC, y=0.12)


def clock_shot(extra_stickers=(), caption="the exam starts at *8:00*", sfx_extra=()):
    bed_room = bedroom(wall="#4a5563", blanket="#5c7cfa", night=True)
    # replace the stock 6:00 clock with a BIG glowing 7:52 one on the nightstand
    bed_room = [o for o in bed_room if not (o.get("kind") == "text" and o.get("text") == "6:00") and o.get("kind") != "lamp"]
    bed_room += [O("box", (1.3, 0.72, -4.0), [0.46, 0.3, 0.16], "#212529", material="plastic"),
                 text((1.3, 0.72, -3.915), "7:52", 0.4, 0.22, bg="#111111", fg="#ff3b30", lit=2.0),
                 lamp((1.3, 0.9, -3.5), "#ff6b6b", 2, 2.5, hidden=True)]
    return dict(set_=Set(bed_room, sky=INDOOR, sun_dir=(-3, 6, 4), light=1.1, ambient=1.2),
                cam=cam((1.15, 0.95, -2.95), (1.3, 0.72, -4.0), dof=True), caption=caption,
                sfx=[{"type": "alarm", "at": 0.0}, *sfx_extra], stickers=list(extra_stickers))


# 1 — HOOK: the glowing 7:52 alarm clock, Mom yelling off-screen
c = clock_shot()
s.beat(3.4, c["caption"], c["set_"], c["cam"], hands="none",
       say=[dict(say("YOU HAVE AN EXAM IN 8 MINUTES!", MOM, 0.5, name="MOM (downstairs)", speed=1.1, dur=2.4), x=0.5, y=0.73)],
       stickers=[left(1.0, 0.9, 0.2)], sfx=c["sfx"], fx=["punch"])

# 2 — kitchen: Dad is SO calm. you grab toast
dad = person((0.35, 0, -2.4), top="#495057", outfit="sweater", skin="tan", hair="short", hair_color="dark", beard="stubble", glasses=True,
             act="sit_eat", expr="smile", talk=[(0.4, 1.6)], seed=12, hold="emoji:🥣")
s.beat(3.2, "Dad is *way* too calm", Set(kitchen_home(extra=chair((0.35, 0, -2.4), "#6b4f36", ry=0) + [dad]), sky=DAY, sun_dir=(2, 8, 6), light=1.8),
       cam((-0.2, 1.55, 0.2), (0.3, 1.1, -2.3)), hands="thumbsup",
       say=[say("Morning, champ! Big day?", DAD, 0.4, who=(0.35, 1.5, -2.4), name="DAD")],
       stickers=[left(0.9, 0.78), floaty("+1 TOAST 🍞", 2.0, color="#ffd8a8", x=0.3, y=0.45, size=58)],
       sfx=[{"type": "whoosh", "at": 1.9}], fx=["whip"])

# 3 — the street: running... in pyjamas
jogger = person((0.9, 0, -6.2), top="#2f9e44", outfit="tank", bottom="#212529", skin="brown", hair="buzz", hair_color="black", act="run",
                expr="laugh", ry=0, look="you", talk=[(1.0, 1.2)], seed=23,
                anim=[{"type": "move", "to": [0, 0, 2.0], "rel": True}])
s.beat(3.3, "you're still in your *pyjamas*", Set(street(extra=[jogger]), sky=SUNNY, sun_dir=(3, 8, 5), light=2.2),
       cam((1.5, 1.6, 1.0), (0.9, 1.3, -4.5), to=(1.5, 1.6, 0.0), head="run"), hands="run",
       say=[say("Nice pyjamas, bro!", JOG, 1.0, who=(0.9, 2.0, -4.6), name="JOGGER")],
       stickers=[left(0.78, 0.66), label("pyjamas 💀", at=0.3, side="right", x=0.68, y=0.8, dur=1.8)])

# 4 — the school bus leaves without you


def no_parked_car(objs):
    return [o for o in objs if not (-1.2 <= o["at"][0] <= 0.8 and -14.5 <= o["at"][2] <= -9.5)]



s.beat(3.2, "the bus *leaves* without you", Set(no_parked_car(street()) + school_bus((0.2, 0, -3.2), moving=[0, 0, -6]), sky=SUNNY, sun_dir=(3, 8, 5), light=2.2),
       cam((1.0, 1.6, 0.8), (0.2, 1.6, -5.0), head="run"), hands="reach",
       stickers=[left(0.66, 0.55), stamp("MISSED IT", 1.4, color="#ff6b6b", size=150)],
       sfx=[{"type": "whoosh", "at": 0.3}, {"type": "fail", "at": 1.5}])

# 5 — the crossing guard: "walk. don't run."
guard = person((0.2, 0, -2.4), top="#ff922b", outfit="uniform", bottom="#343a40", skin="fair", hair="short", hair_color="grey", age="elder",
               hat="cap", hat_color="#f76707", act="point", expr="neutral", talk=[(0.5, 1.6)], seed=34, belly=True)
s.beat(3.3, "the *slowest* crossing guard alive", Set(street(extra=[guard] + stop_paddle((0.65, 1.75, -2.35), 1.1) + traffic_light((-1.4, 0, -3.2), "red")),
                                                    sky=SUNNY, sun_dir=(3, 8, 5), light=2.2),
       cam((0.2, 1.6, 0.1), (0.3, 1.45, -2.4)), hands="shrug",
       say=[say("Walk. Don't. Run.", GUARD, 0.5, who=(0.2, 2.05, -2.4), name="CROSSING GUARD", speed=0.75)],
       stickers=[left(0.55, 0.42), floaty("-1 MINUTE", 2.1, color="#ff6b6b", x=0.5, y=0.35)],
       sfx=[{"type": "tick", "at": t / 10} for t in range(6, 31, 6)], fx=["slowmo"])

# 6 — hallway sprint. freeze-frame + REAL FACT
kids = [dict(p, act=a, expr="surprised") for p, a in zip(people(3, 45, at=(0, 0, -6.5), spread=(2.6, 0, 3.0), look="you", age="teen"),
                                                        ["point", "laugh", "idle"])]
s.beat(3.6, "you slept *4 hours*. oops.", Set(school_hall(extra=kids), sky=INDOOR, sun_dir=(1, 8, 6), light=1.7, ambient=1.5),
       cam((0, 1.6, 1.0), (0, 1.35, -7.0), to=(0, 1.6, -1.5), head="run"), hands="run",
       stickers=[left(0.42, 0.28), badge("Teens need 8–10 hours of sleep a night 😴", at=1.5, title="REAL FACT · CDC", dur=2.0)],
       freeze={"at": 1.2, "label": "you got 4. 💀"}, fx=["whip"])

# 7 — classroom door, 7:59: the whole class turns around
desks = []
studs = []
looks = [("#e64980", "light", "ponytail", True), ("#1971c2", "deep", "afro", False), ("#2f9e44", "olive", "curly", True),
         ("#f08c00", "fair", "spiky", False), ("#7048e8", "brown", "bun", True), ("#0b7285", "tan", "side", False)]
seats = [(-0.75, -1.0), (0.75, -1.0), (-1.1, -2.9), (0.0, -2.9), (1.1, -2.9)]
for k, (x, z) in enumerate(seats):
    top, sk, hr, fem = looks[k]
    desks += chair((x, 0, z), "#495057", ry=0)
    studs.append(person((x, 0, z), top=top, outfit="hoodie" if k % 2 else "tshirt", skin=sk, hair=hr, feminine=fem, age="teen",
                        act="sit", expr=["shock", "smirk", "surprised", "laugh", "shock"][k], seed=50 + k))
cls = classroom_real(extra=desks + studs + wall_clock((-2.6, 2.3, -6.9), "7:59", 1.2))
s.beat(3.2, "7:59. the whole class *turns*", Set(cls, sky=INDOOR, sun_dir=(1, 8, 6), light=1.7, ambient=1.5),
       cam((0, 1.95, 1.6), (0, 0.85, -2.4)), hands="idle",
       stickers=[left(0.28, 0.12), label("made it!!", at=1.4, side="left", x=0.35, y=0.3, dur=1.6)],
       sfx=[{"type": "gasp", "at": 0.2}, {"type": "scratch", "at": 0.05}], fx=["punch"])

# 8 — the teacher: the exam is TOMORROW
teacher = person((0.2, 0, -2.0), top="#c2255c", outfit="blazer", skin="medium", hair="bob", hair_color="brown", feminine=True, earrings=True,
                 glasses=True, act="talk", expr="smirk", talk=[(0.4, 2.0)], seed=61, hold="clipboard")
board = [text((0, 1.6, -6.86), "MATH EXAM\nFRIDAY", 2.6, 0.9, bg="#ffffff", fg="#c92a2a", font='"Comic Sans MS", cursive', weight=700)]
s.beat(3.6, "plot twist: it's *Thursday*", Set(classroom_real(extra=board + [teacher]), sky=INDOOR, sun_dir=(1, 8, 6), light=1.7, ambient=1.5),
       cam((0, 1.55, 0.6), (0.1, 1.4, -2.4)), hands="shrug",
       say=[say("Sweetie... the exam is TOMORROW.", TEACH, 0.4, who=(0.2, 1.95, -2.0), name="MS. LEE")],
       stickers=[stamp("TOMORROW?!", 2.4, color=ACC, size=140)],
       sfx=[{"type": "fail", "at": 2.5}, {"type": "crowd", "at": 2.6}])

# 9 — LOOP: tomorrow morning, same clock, same shout -> back to beat 1
c = clock_shot(caption="*tomorrow* morning...")
s.beat(3.4, c["caption"], c["set_"], c["cam"], hands="none",
       say=[dict(say("YOU HAVE AN EXAM IN 8 MINUTES!", MOM, 0.6, name="MOM (downstairs)", speed=1.1, dur=2.2), x=0.5, y=0.22)],
       stickers=[stamp("NOT AGAIN 🔁", 2.1, color="#ffffff", y=0.3, rot=-6, size=120)], sfx=c["sfx"], fx=["zoomin"])

s.save(tags=["what if you slept through your alarm", "exam day", "overslept", "what if", "pov", "funny", "alternative world", "dink dunk",
             "animation", "school"],
       description="Your alarm didn't ring. The exam starts in 8 minutes. You're in pyjamas. ⏰😱\n"
                   "Toast, a missed bus, the slowest crossing guard alive... and then the teacher drops the twist.\n\n"
                   "What's YOUR worst oversleeping story? 👇\n\n#school #whatif #funny",
       pinned="What's YOUR worst oversleeping story? 👇 (part 2: tomorrow morning...)")
