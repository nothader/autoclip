"""What if you accidentally hit reply-all to the whole company? 30 s Short (film look).
Structure: THE 5 STAGES OF REPLY-ALL GRIEF — a stage stamp per beat (denial, bargaining, hiding, the elevator, acceptance),
each in a new place (your desk, coworker's stare, IT department, bathroom stall, elevator with the boss, office-wide storm,
all-hands, back at your desk). Opens on the monitor with the cursor on REPLY ALL (no hook phone, no countdown).
Ending: soft twist — the CEO replies-all "Agreed. No more Friday meetings." and the office cheers you (no freeze, no cliffhanger).
Real fact: in January 2019 a reply-all storm caught 11,543 Microsoft employees in one email thread.
Source: https://www.cbsnews.com/news/more-than-11000-at-microsoft-said-ensnared-in-reply-all-email-loop
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, meter, INDOOR, DAY  # noqa: E402
from assets import (O, SKIN, person, people, screen_ui, screen_panel, text, lamp, room, office, desk, monitor, office_chair,  # noqa: E402
                    elevator, meeting_room, server_rack, bathroom_stall, plant)

ACC = "#4dabf7"
s = Story("reply_all", "What if you accidentally hit reply-all to the whole company?", accent=ACC, look="film",
          hook=["WHAT IF YOU HIT", "REPLY ALL", "BY ACCIDENT?"], hook_accent=1, skin=SKIN["porcelain"], sleeve="#5f3dc4", mood="sneaky",
          grade={"tint": [0.97, 1.0, 1.05], "sat": 1.05})
BRO, IT, BOSS, CEO = "am_eric", "am_adam", "bm_george", "af_bella"


def stage(n, word, at=0.15):
    return stamp(f"STAGE {n}: {word}", at, color="#ffffff", y=0.2, rot=-4, size=96, dur=2.2)


EMAIL = screen_ui(app="✉️  To: ALL STAFF (11,543)", lines=["Subject: this meeting 💀", "", "could've been an email lol.", "boss talks like a podcast 🎙️"],
                  button="REPLY ALL ▸ SEND", bg="#1e2530", fg="#f1f3f5", accent="#e03131")
SENT = screen_ui(app="✉️  Sent", big="11,543", sub="people received your email", lines=["(including the boss)"], bg="#1e2530", fg="#f1f3f5", big_color="#ff6b6b")


def my_desk(screen, extra=()):
    return room(7, 7, 2.9, -3.0, "#b8c4d0", "#4a5563", "carpet", "paint", panels=2) + desk((0, 0, -1.2), 1.5, 0.75, screen=screen, clutter=True) + plant((1.6, 0, -2.6)) + list(extra)


# 1 — the monitor: cursor on REPLY ALL
s.beat(3.2, "you meant to send it to *one* friend", Set(my_desk(EMAIL), sky=INDOOR, sun_dir=(1, 8, 7), light=1.7),
       cam((0, 1.22, 0.05), (0, 1.08, -1.35)), hands="none",
       stickers=[label("not your friend", who=(0.1, 1.27, -1.35), at=1.0, side="right", dur=1.6)],
       sfx=[{"type": "tick", "at": 2.4}, {"type": "whoosh", "at": 2.6}], fx=["zoomin"])
# 2 — STAGE 1: DENIAL — the coworker slowly turns
bro = person((0.95, 0, -2.3), top="#0b7285", outfit="hoodie", skin="deep", hair="afro", hair_color="black", act="sit_type", ry=-70, look="you",
             expr="shock", talk=[(1.1, 1.3)], seed=21, lanyard=True)
s.beat(3.4, "it's *fine*. nobody reads email.", Set(my_desk(SENT, office_chair((0.95, 0, -2.3), ry=-70)[:3] + [bro]), sky=INDOOR, sun_dir=(1, 8, 7), light=1.7),
       cam((-0.1, 1.35, 0.4), (0.55, 1.1, -2.1)), hands="none",
       say=[say("Bro... I got your email.", BRO, 1.1, who=(0.95, 1.55, -2.3), name="DEV")],
       stickers=[stage(1, "DENIAL")], fx=["dutch"])
# 3 — STAGE 2: BARGAINING — IT department
it_guy = person((0, 0, -2.3), top="#343a40", outfit="tshirt", skin="tan", hair="long", hair_color="dark", beard="full", hat="headphones",
                hat_color="#212529", act="cross", expr="bored", talk=[(1.2, 1.6)], seed=31, glasses=True)
it_room = (room(6, 6, 2.8, -3.4, "#1d2b36", "#343a40", "concrete", "paint", panels=1)
           + server_rack((-1.5, 0, -2.9)) + server_rack((1.5, 0, -2.9)) + [text((0, 2.25, -3.3), "IT HELP DESK", 1.6, 0.32, bg="#0b7285", fg="#ffffff", lit=1.1),
                                                                            lamp((0, 2.0, -1.4), "#a5d8ff", 4, 5, hidden=True), it_guy])
s.beat(3.4, "can you *unsend* it?", Set(it_room, sky=INDOOR, sun_dir=(1, 8, 7), light=1.9, ambient=1.5),
       cam((0, 1.55, 0.2), (0, 1.35, -2.3)), hands="money",
       say=[say("Sir, this isn't a text.", IT, 1.2, who=(0, 1.95, -2.3), name="IT GUY", speed=0.9)],
       stickers=[stage(2, "BARGAINING")])
# 4 — STAGE 3: HIDING — bathroom stall, phone exploding
s.beat(3.3, "the phone *won't stop*", Set(bathroom_stall(), sky=INDOOR, sun_dir=(1, 8, 7), light=2.0),
       cam((0, 1.25, 0.2), (0, 1.15, -1.2)), hands="phone",
       screen=screen_ui(app="Outlook", big="482", sub="new replies 😳", lines=["RE: this meeting 💀", "RE: RE: this meeting 💀", "RE: who is this??"],
                        accent="#e03131", big_color="#ff6b6b", time="10:14", bg="#1e2530", fg="#f1f3f5"),
       stickers=[stage(3, "HIDING"), floaty("+97", 1.0, color="#ff6b6b", x=0.72, y=0.45), floaty("+212", 1.8, color="#ff6b6b", x=0.3, y=0.4)],
       sfx=[{"type": "notify", "at": t / 10} for t in range(4, 31, 3)], fx=["shake"])
# 5 — STAGE 4: THE ELEVATOR — with the boss
boss = person((0.55, 0, -0.9), top="#212529", outfit="suit", skin="fair", hair="side", hair_color="grey", tie="#c92a2a", act="idle", ry=-35,
              look="you", expr="smirk", talk=[(0.9, 1.5)], seed=41, watch=True)
s.beat(3.6, "and then the *elevator*", Set(elevator(extra=[boss]), sky=INDOOR, sun_dir=(1, 8, 7), light=2.0, ambient=1.5),
       cam((-0.45, 1.6, 0.4), (0.4, 1.55, -0.9)), hands="none",
       say=[say("So... a podcast, huh?", BOSS, 0.9, who=(0.55, 1.95, -0.9), name="THE BOSS", speed=0.9)],
       stickers=[stage(4, "THE ELEVATOR"), meter("AWKWARD", 0.3, 1.0, at=0.5, color="#ff922b", y=0.32)],
       sfx=[{"type": "tick", "at": t / 10} for t in range(5, 34, 6)])
# 6 — the storm: everyone replies all. REAL FACT
storm = [dict(p, act=a, expr="angry") for p, a in zip(people(7, 52, at=(0, 0, -4.2), spread=(4.0, 0, 3.0), look="you"),
                                                     ["angry", "point", "angry", "facepalm", "angry", "shake_head", "point"])]
s.beat(3.4, "then *everyone* replies all", Set(office(extra=storm), sky=INDOOR, sun_dir=(1, 8, 7), light=1.7),
       cam((0, 1.65, 1.0), (0, 1.3, -4.0)), hands="shrug",
       say=[say("STOP REPLYING ALL!!", BRO, 0.3, who=(-0.6, 2.0, -3.5), name="EVERYONE", speed=1.15, dur=1.2)],
       stickers=[badge("11,543 Microsoft workers, ONE reply-all storm", at=1.2, title="REAL FACT · 2019", dur=2.1)],
       sfx=[{"type": "crowd", "at": 0.2}], fx=["whip"])
# 7 — all-hands: your email is buried
allhands = screen_ui(app="ALL-HANDS · URGENT", lines=["RE: RE: RE: please remove me", "RE: RE: unsubscribe", "RE: STOP REPLYING ALL", "RE: me too"],
                     bg="#1e2530", fg="#f1f3f5", accent="#ff6b6b")
ceo = person((0, 0, -4.6), top="#e9ecef", outfit="blazer", skin="medium", hair="bob", hair_color="dark", feminine=True, earrings=True, act="talk",
             expr="neutral", talk=[(0.3, 2.0)], seed=51)
seated = [person((x, 0, z), top=c, skin=sk, hair=h, act="sit", ry=90 if x < 0 else -90, look="ahead", expr="bored", seed=60 + k)
          for k, (x, z, c, sk, h) in enumerate([(-0.95, -1.6, "#1971c2", "light", "short"), (0.95, -1.6, "#e64980", "tan", "ponytail"),
                                                (-0.95, -2.6, "#2f9e44", "brown", "curly"), (0.95, -2.6, "#f08c00", "fair", "bun"),
                                                (-0.95, -3.6, "#495057", "olive", "buzz"), (0.95, -3.6, "#ae3ec9", "deep", "afro")])]
s.beat(3.4, "your email is now *one of 11,543*", Set(meeting_room(wall="#c5ccd4", screen=allhands, extra=seated + [ceo]), sky=INDOOR, sun_dir=(1, 8, 7), light=1.6),
       cam((0, 1.65, -0.6), (0, 1.55, -4.6)), hands="none",
       say=[say("Who started this?!", CEO, 0.4, who=(0, 2.1, -4.6), name="CEO", dur=1.5)],
       stickers=[label("nobody remembers you", who=(0, 2.1, -4.6), at=1.9, side="left", dur=1.4)], fx=["punch"])
# 8 — STAGE 5: ACCEPTANCE — the CEO's reply. Soft twist
ceo_mail = screen_ui(app="✉️  From: CEO → ALL STAFF", lines=["RE: this meeting 💀", "", "Agreed.", "No more Friday meetings."], bg="#1e2530",
                     fg="#f1f3f5", accent="#51cf66")
cheer = [dict(p, act=a, expr="happy") for p, a in zip(people(5, 66, at=(0.2, 0, -3.2), spread=(2.6, 0, 1.2), look="you"),
                                                     ["cheer", "clap", "cheer", "finger_guns", "clap"])]
s.beat(3.6, "stage 5: *legend*", Set(my_desk(ceo_mail, cheer), sky=INDOOR, sun_dir=(1, 8, 7), light=1.7),
       cam((0, 1.5, 0.7), (0, 1.3, -2.2)), hands="none",
       stickers=[badge("No more Friday meetings 🎉", at=0.7, title="ACHIEVEMENT UNLOCKED", dur=2.2)],
       sfx=[{"type": "achievement", "at": 0.7}, {"type": "crowd", "at": 0.9}])

s.save(tags=["what if you hit reply all", "reply all", "office humor", "what if", "pov", "funny", "alternative world", "dink dunk",
             "animation", "work email"],
       description="You meant to send it to ONE friend. It went to all 11,543 people. Including the boss. 📧💀\n"
                   "Five stages of grief, one bathroom stall, and a very long elevator ride.\n\nWhat's the WORST email you've ever sent? 👇\n\n#replyall #whatif #funny",
       pinned="What's the WORST email you've ever sent? 👇")
