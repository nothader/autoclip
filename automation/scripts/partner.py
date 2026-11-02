"""What if you could hear your partner's thoughts? (swap recipe, calm). Fact: one 2020 Queen's University study estimated ~6,000 thoughts a day."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403

v = Video()
T = lambda text: {"label": "THEIR THOUGHTS", "text": text}
YOU, THEM = BOY, GIRL
lounge = room("#ffe8cc", "#b08968", win="#ffd8a8", w=12, d=12, extra=[O("box", (0, 0.35, -8), [3.6, 0.7, 1.2], "#4c6ef5"), O("box", (0, 0.9, -8.6), [3.6, 0.8, 0.3], "#4263eb"),
                                                                      O("box", (3.6, 0.6, -10), [1.6, 1.2, 0.3], "#212529"), O("plane", (3.6, 0.65, -9.84), [1.4, 0.9, 1], "#74c0fc", material="glow")])
couch = lambda: [P((-0.7, 0.35, -8), YOU, "sit", 2, ry=180), P((0.7, 0.35, -8), THEM, "sit", 3, ry=180),
                 O("particles", (3.6, 1, -9.6), 0.2, "#a5d8ff", count=8, seed=3, spread=[1.4, 1, 0.2], animate=[{"type": "drift", "axis": "y", "amount": 0.2}])]
v.B(4.4, "follow", "In 3 seconds, you'll hear your partner's thoughts. Every single one.", V(lounge + couch() + [O("particles", (3.6, 1, -9.6), 0.2, "#a5d8ff", count=8, seed=3,
    spread=[1.4, 1, 0.2], animate=[{"type": "drift", "axis": "y", "amount": 0.2}])], ["#ffe8cc", "#ffd8a8"], focus=(0, 1.0, -8), zoom=0.8, bounce="#ffe8cc"),
    "+0 SEC", "A NORMAL SUNDAY", move="none", sfx=[{"type": "shimmer", "at": 3.0, "gain": 0.6}])
kit = room("#fff3bf", "#c9a27a", extra=[O("box", (0, 0.45, -9), [8, 0.9, 1], "#868e96"), O("box", (0, 0.92, -9), [8, 0.05, 1.05], "#f1f3f5"),
           O("cylinder", (-1, 1.0, -8.8), [0.12, 0.16, 0.12], "#f8f9fa", count=2, seed=4, spread=[1, 0, 0.2]),
           O("particles", (-1, 1.3, -8.8), 0.1, "#f1f3f5", count=6, seed=5, spread=[1, 0.6, 0.2], animate=[{"type": "drift", "axis": "y", "amount": 0.2}])])
v.B(3.4, "side", "Morning coffee. And then you hear it.", V(kit + [P((-0.5, 0, -7.6), YOU, "idle", 2, ry=90), P((0.5, 0, -7.6), THEM, "idle", 3, ry=270)],
    ["#fff3bf", "#ffd8a8"], focus=(0, 1.3, -7.6), zoom=0.5, bounce="#fff3bf"), "+1 HOUR", tooltip=T("They look so cute when they're sleepy."))
v.B(3.4, "follow", "They still get nervous around you. But wait until dinner.", V(kit + [P((0.5, 0, -7.6), THEM, "idle", 3, ry=180), P((-0.6, 0, -6.4), YOU, "walk", 2, ry=0)],
    ["#fff3bf", "#ffd8a8"], focus=(0.3, 1.3, -7.4), zoom=0.7, bounce="#fff3bf"), "+1 HOUR", tooltip=T("Does my hair look weird? It looks weird."))
v.B(3.4, "side", "You tell them a long story. You hear what they think.", V(lounge + [P((-0.7, 0.35, -8), YOU, "point", 2, ry=90, anim=[{"type": "bob", "amount": 0.04, "speed": 3}]), P((0.7, 0.35, -8), THEM, "sit", 3, ry=270)],
    ["#ffe8cc", "#ffd8a8"], focus=(0, 1.0, -8), zoom=0.5, bounce="#ffe8cc"), "+3 HRS", tooltip=T("I love them. But this story is SO long."), transition="whip")
v.B(3.6, "wide", "But here's the problem: you hear everyone. About 6,000 thoughts a day each.", V(city([crowd(22, 7, at=(0, 0, -14), spread=(12, 0, 16)),
    P((-0.5, 0, -8), YOU, "walk", 2, ry=180), P((0.5, 0, -8), THEM, "walk", 3, ry=180)]), GOLD, focus=(0, 1.3, -11), zoom=1.4), "+5 HRS",
    tooltip={"label": "EVERYONE ELSE", "text": "Do dogs know they're dogs?"}, stat={"value": "6,000", "label": "THOUGHTS PER PERSON PER DAY (ONE STUDY)", "count_up": True},
    effects=["dizzy"])
diner = room("#3b2a6b", "#5c3d2e", win="#0b1d3a", w=12, d=12, extra=[O("box", (0, 0.75, -7), [1.2, 0.06, 0.8], "#f8f9fa"), O("cylinder", (0, 0.37, -7), [0.1, 0.74, 0.1], "#495057"),
             O("cylinder", (0, 0.95, -7), [0.04, 0.3, 0.04], "#fff3bf"), O("flame", (0, 1.15, -7), 0.08, "#ffa94d"),
             O("sphere", (0, 2.9, -7), 0.12, "#ffe066", material="glow", count=10, seed=4, spread=[10, 0.2, 10])])
v.B(3.6, "follow", "At dinner, you hear the one thought you didn't want to.", V(diner + [P((0, 0, -7.8), THEM, "sit", 3, ry=180), P((0, 0, -6.2), YOU, "sit", 2)],
    ["#3b2a6b", "#9775fa"], focus=(0, 1.0, -7.4), zoom=0.7, bounce="#5f3dc4"), "+10 HRS", tooltip=T("Should I tell them I ate their leftovers?"), transition="dip",
    effects=["tunnel"], sfx=[{"type": "heartbeat", "at": 0.6, "dur": 2.6, "gain": 0.7}])
v.B(3.4, "side", "Mystery solved. Your leftovers were never safe.", V(diner + [P((0, 0, -7.8), THEM, "sit", 3, ry=270), P((0, 0, -6.2), YOU, "point", 2, ry=90)],
    ["#3b2a6b", "#9775fa"], focus=(0, 1.0, -7), zoom=0.6, bounce="#5f3dc4"), "+10 HRS", effects=["confetti"])
v.B(3.4, "follow", "No more \"What's wrong?\" \"Nothing.\" Now you can hear the truth.", V(lounge + couch(), ["#ffe8cc", "#ffd8a8"], focus=(0, 1.0, -8), zoom=0.7, bounce="#ffe8cc"),
    "+1 DAY", tooltip=T("I'm not mad. I'm just hungry."))
v.B(3.4, "side", "But they could never surprise you again. Ever.", V(park([P((-0.5, 0, -6), YOU, "idle", 2, ry=90), P((0.5, 0, -6), THEM, "point", 3, ry=270),
    O("box", (0.2, 1.1, -6), [0.3, 0.3, 0.3], "#e03131", rotate=[0, 30, 0], animate=[{"type": "bob", "amount": 0.05, "speed": 2}]), crowd(4, 21, at=(0, 0, -14), spread=(20, 0, 4))]),
    GOLD, focus=(0, 1.2, -6), zoom=0.8), "+1 WEEK", tooltip=T("I got them a gift. Don't think about it. DON'T."))
v.B(3.8, "far", "And if they could hear yours... what would they hear right now?", V(park([P((-0.4, 0, -6), YOU, "idle", 2, ry=90), P((0.4, 0, -6), THEM, "idle", 3, ry=270)]),
    DUSK, focus=(0, 1.2, -6), zoom=1.6), "+1 MONTH", move="pull_out", effects=["glow"])
v.save("partner", "What if you could hear your partner's thoughts?", "You can suddenly hear every thought your partner has, and everyone else's too.", "calm",
       "SINCE YOU HEARD IT", ["WOULD YOU", "WANT TO KNOW?"], "HEARING MY *PARTNER'S* THOUGHTS", 1, accent="#f06595", captions="words")
