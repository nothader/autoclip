"""What if your dad joined your online game squad? 30 s Short (film look).
Structure: ESCALATING LIST OF DAD MOVES — one new embarrassing "dad move" per beat, each in a new place (your RGB battle station,
the monitor chat, the kitchen sink, the couch with an upside-down controller, the front lawn "flank", the school hallway,
the front door pizza delivery, the victory screen). Opens on Dad leaning into your gaming setup in a giant green headset
(no clock, no meter, no stage stamps, no training tape).
Ending: soft twist + comment bait — Dad carried the match, the squad votes and kicks YOU, Dad keeps your spot ("Gamer Dad will return").
Real fact: Pew Research Center (May 2024) — 85% of U.S. teens say they play video games (41% daily).
Source: https://www.pewresearch.org/internet/2024/05/09/teens-and-video-games-today/
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, meter, INDOOR, DAY, SUNNY  # noqa: E402
from assets import (O, SKIN, person, people, screen_ui, text, lamp, room, kitchen_home, apartment, street, school_hall,  # noqa: E402
                    front_door, gaming_desk, pizza_box, screen_panel)

ACC = "#a9e34b"
RGB = "#20c997"
s = Story("gamer_dad", "What if your dad joined your online game squad?", accent=ACC, look="film",
          hook=["WHAT IF YOUR", "DAD", "JOINED YOUR SQUAD?"], hook_accent=1, skin=SKIN["brown"], sleeve="#ffa94d", mood="bouncy",
          grade={"tint": [0.98, 1.02, 1.0], "sat": 1.1, "contrast": 1.05})
DAD, JAY, MAYA, PIZZA = "am_adam", "am_puck", "af_sky", "bm_george"

DAD_KW = dict(top="#c92a2a", bottom="#364fc7", outfit="sweater", skin="brown", hair="short", hair_color="dark", beard="stubble",
              glasses=True, belly=True, hat="headphones", hat_color=RGB, seed=7)


def dad(at, **kw):
    d = dict(DAD_KW)
    d.update(kw)
    return person(at, **d)


def battle_room(screen, extra=()):
    return (room(6, 6, 2.7, -2.4, "#2b3040", "#3b3f4a", "carpet", "paint", panels=1, panel_color="#c5f6fa")
            + gaming_desk((0, 0, -1.4), screen, rgb=RGB, chair=False)
            + [text((-1.6, 1.9, -2.32), "GG ONLY", 0.9, 0.3, bg="#111111", fg=ACC, lit=1.3), lamp((0, 2.2, -0.4), "#e3fafc", 3, 5, hidden=True)]
            + list(extra))


def game(app, big=None, sub=None, lines=(), messages=(), big_color=None):
    return screen_ui(app=app, big=big, sub=sub, lines=lines, messages=messages, bg="#0d1117", fg="#e9ecef", accent=RGB, big_color=big_color)


ROOM_LIGHT = dict(sky=INDOOR, sun_dir=(1, 8, 7), light=1.4, ambient=1.5)

# 1 — HOOK: Dad leans into your setup in a giant green headset
JOIN = game("🎮 SQUAD 4/4", big="DAD_1974", sub="has joined the squad", big_color=ACC)
s.beat(3.4, "Dad *joined* your squad", Set(battle_room(JOIN, [dad((0.75, 0, -1.25), act="wave", expr="excited", ry=-25, talk=[(0.35, 1.9)])]), **ROOM_LIGHT),
       cam((-0.45, 1.4, 1.5), (0.15, 1.25, -1.3)), hands="none",
       say=[dict(say("Hey team! Dad's in the game!", DAD, 0.35, name="DAD"), x=0.5, y=0.43)],
       stickers=[emoji("💀", 2.4, x=0.2, y=0.32, size=170)], sfx=[{"type": "notify", "at": 0.1}], fx=["punch"])

# 2 — the monitor: your squad heard EVERYTHING
CHAT = game("💬 SQUAD CHAT", big="👀", lines=["JAYDEN: who is DAD_1974 💀", "MAYA: is that your DAD??", "YOU: no", "DAD_1974: hi kids!! 👋"])
s.beat(3.2, "your squad heard *everything*", Set(battle_room(CHAT), **ROOM_LIGHT),
       cam((0, 1.25, 0.75), (0, 1.14, -1.6)), hands="type",
       say=[dict(say("Bro... is that your DAD?", JAY, 0.5, name="JAYDEN (squad)"), x=0.5, y=0.22)],
       sfx=[{"type": "notify", "at": 0.3}, {"type": "notify", "at": 1.1}], fx=["zoomin"])

# 3 — kitchen sink: voice chat for chores
sink_dad = dad((-0.5, 0, -3.3), act="talk", expr="smirk", ry=15, talk=[(0.4, 2.2)])
s.beat(3.4, "he uses voice chat for *chores*", Set(kitchen_home(extra=[sink_dad]), sky=DAY, sun_dir=(2, 8, 6), light=1.7),
       cam((0.1, 1.55, -0.4), (-0.45, 1.4, -3.2)), hands="shrug",
       say=[say("Team, quick update: who left a bowl in the sink?", DAD, 0.4, who=(-0.5, 2.1, -3.3), name="DAD")],
       stickers=[floaty("-100 AURA", 2.4, color="#ff6b6b", x=0.62, y=0.36)])

# 4 — couch: holding the controller upside down
couch_dad = dad((0, 0, -3.85), act="sit", expr="confused", hold="emoji:🎮", talk=[(0.5, 1.6)], look="you")
s.beat(3.2, "he holds it *upside down*", Set(apartment(extra=[couch_dad]), sky=DAY, sun_dir=(2, 8, 6), light=1.7),
       cam((0.4, 1.45, -0.6), (0, 0.95, -3.8)), hands="shrug",
       say=[say("Which one is jump? The triangle?", DAD, 0.5, who=(0, 1.75, -3.85), name="DAD")],
       stickers=[label("upside down 🙃", who=(0.15, 1.0, -3.6), at=1.4, side="right", dur=1.7)], fx=["dutch"])

# 5 — front lawn: "flank left" means OUTSIDE
lawn_dad = dad((1.3, 0, -3.6), act="run", expr="excited", ry=-80, look="ahead", talk=[(0.2, 1.6)],
               anim=[{"type": "move", "to": [-2.2, 0, 0], "rel": True}])
neighbor = person((-0.9, 0, -5.6), top="#e8d5b5", outfit="shirt", skin="light", hair="bald", age="elder", act="idle", expr="shock", seed=44)
s.beat(3.3, "he thinks 'flank' means *outside*", Set(street(extra=[lawn_dad, neighbor]), sky=SUNNY, sun_dir=(3, 8, 5), light=2.1),
       cam((0.3, 1.6, 0.8), (0.1, 1.2, -4.0)), hands="shrug",
       say=[say("I'M FLANKING LEFT!", DAD, 0.2, who=(0.2, 2.2, -3.6), name="DAD", speed=1.15)],
       stickers=[label("the neighbor", who=(-0.9, 1.8, -5.6), at=1.8, side="right", dur=1.4)],
       sfx=[{"type": "whoosh", "at": 0.1}], fx=["whip"])

# 6 — school hallway next day: the clip is everywhere + REAL FACT
kids = [dict(p, act=a, expr=e) for p, a, e in zip(people(4, 61, at=(0, 0, -4.8), spread=(2.8, 0, 2.4), look="you", age="teen"),
                                                  ["phone", "laugh", "point", "selfie"], ["laugh", "laugh", "grin", "excited"])]
s.beat(3.6, "the clip is *all over school*", Set(school_hall(extra=kids), sky=INDOOR, sun_dir=(1, 8, 6), light=1.7, ambient=1.5),
       cam((0, 1.6, 0.8), (0, 1.35, -5.0), to=(0, 1.6, 0.0), head="walk"), hands="idle",
       say=[say("FLANKING LEFT!", JAY, 0.4, who=(0.3, 1.9, -4.4), name="JAYDEN", speed=1.1)],
       stickers=[badge("85% of US teens play video games 🎮", at=1.3, title="REAL FACT · PEW 2024", dur=2.1)],
       sfx=[{"type": "crowd", "at": 0.3}])

# 7 — front door: he ordered pizza for the whole lobby
driver = person((0, 0, -2.85), top="#e03131", outfit="uniform", bottom="#343a40", skin="olive", hair="curly", hair_color="black", hat="cap",
                hat_color="#e03131", act="idle", expr="bored", hold="box", talk=[(0.4, 1.9)], seed=73)
s.beat(3.3, "he ordered pizza for *the whole lobby*", Set(front_door() + [driver] + pizza_box((0.55, 0, -2.5), 12) + pizza_box((-0.55, 0, -2.5), 10),
                                                         sky=DAY, sun_dir=(2, 8, 6), light=1.8),
       cam((0, 1.6, 0.6), (0, 1.15, -2.8)), hands="none",
       say=[say("Pizza for... xX_DadBod_Xx?", PIZZA, 0.4, who=(0, 2.0, -2.85), name="DELIVERY")],
       stickers=[floaty("-$84 🍕", 2.2, color="#ff6b6b", x=0.5, y=0.33, size=80)], sfx=[{"type": "doorbell", "at": 0.05}])

# 8 — plot twist: Dad is REALLY good
WIN = game("🏆 VICTORY", big="#1", sub="MVP: DAD_1974 · 23 eliminations", lines=["", "you: 0 eliminations 💀"], big_color="#ffd43b")
s.beat(3.3, "plot twist: he's *really good*", Set(battle_room(WIN), **ROOM_LIGHT),
       cam((0, 1.25, 0.75), (0, 1.14, -1.6)), hands="type",
       say=[dict(say("Your dad is a LEGEND!", MAYA, 0.6, name="MAYA (squad)"), x=0.5, y=0.22)],
       stickers=[stamp("CARRIED 🏆", 1.7, color="#ffd43b", y=0.62, size=140)], sfx=[{"type": "achievement", "at": 0.2}], fx=["punch"])

# 9 — the squad votes... you're out. Dad keeps your spot.
KICK = game("🗳️ SQUAD VOTE", big="KICK YOU", sub="squad vote: ✅ 3   ❌ 0", lines=["", "DAD_1974 stays 🎮"], big_color="#ff6b6b")
s.beat(3.4, "your squad *picked Dad*", Set(battle_room(KICK, [dad((0.75, 0, -1.25), act="shrug", expr="grin", ry=-25, talk=[(0.4, 1.7)])]), **ROOM_LIGHT),
       cam((-0.45, 1.4, 1.5), (0.15, 1.25, -1.3)), hands="none",
       say=[say("Sorry, champ. Dishes first.", DAD, 0.4, who=(0.75, 2.0, -1.25), name="DAD")],
       stickers=[stamp("KICKED 😭", 1.9, color=ACC, y=0.3, rot=-8, size=150), label("Gamer Dad will return 🎮", at=2.3, x=0.5, y=0.8, dur=1.1)],
       sfx=[{"type": "fail", "at": 1.9}])

s.save(tags=["what if your dad joined your game squad", "gamer dad", "what if", "pov", "funny", "alternative world", "dink dunk",
             "animation", "gaming", "dad"],
       description="Your dad joined your online squad. On voice chat. With a giant green headset. 🎮💀\n"
                   "Chores over the mic, pizza for the whole lobby... and then the squad votes.\n\n"
                   "Would YOU let your dad join your squad? 👇\n\n#gaming #whatif #funny",
       pinned="Would YOU let your dad join your squad? 👇 (Gamer Dad will return...)")
