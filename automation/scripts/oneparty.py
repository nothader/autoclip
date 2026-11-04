"""What if Democrats and Republicans were the same party? Neutral: no side wins or loses; both merge, then the one party splits again.
Hook type: direct to YOU (Thanksgiving table, nobody arguing). Palette: plum dusk + warm cream + sepia; never used on the channel.
Facts (widely cited, rounded): about 4 in 10 Americans call themselves independents (Gallup); about $10 billion went to political
ads in the 2024 cycle (AdImpact); Congress has 535 voting members; the "Era of Good Feelings" (about 1817-1825): one main party
(the Democratic-Republicans), Monroe ran with no real opponent in 1820, then the party split after the 1824 election."""
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403
from props import animal  # noqa: E402

v = Video()
PLUM = ["#3b2a5c", "#f2a65a"]; CREAM = ["#6d8fb3", "#f6e7cf"]; NIGHT = ["#1d2440", "#5b4a7a"]; SEPIA = ["#7a6a55", "#e9d8b4"]
LAV = ["#7c6fb0", "#f3e8ff"]; MINT = ["#4f8f86", "#e6f4ea"]
BLUE, RED, PURPLE = "#2f6fd6", "#d6402f", "#8e5bd8"


def dining(extra=()):
    """Thanksgiving table on an open floor (no walls), warm window glow behind."""
    t = [O("box", (0, -0.02, -3), [16, 0.04, 12], "#a47148"), O("box", (0, 0.75, -2.2), [3.6, 0.08, 1.4], "#fff8ec"),
         O("box", (0, 0.37, -2.2), [3.4, 0.74, 1.2], "#6f4518"),
         O("sphere", (0.3, 0.88, -2.5), [0.17, 0.12, 0.14], "#b5651d", material="glossy"),
         O("cylinder", (0, 0.8, -2.2), [0.25, 0.03, 0.25], "#e9ecef", count=6, seed=2, spread=[3.0, 0, 0.8]),
         O("cylinder", (-1.1, 0.83, -2.0), [0.24, 0.08, 0.24], "#d9480f"), O("cylinder", (1.1, 0.83, -2.4), [0.22, 0.1, 0.22], "#f59f00"),
         O("flame", (-0.5, 1.0, -2.3), 0.12, "#ffa94d"), O("flame", (0.5, 1.0, -2.1), 0.12, "#ffa94d"),
         O("plane", (0, 2.0, 1.2), [4.2, 2.4, 1], "#ffd8a8", material="glow"),
         O("box", (2.8, 0.4, 0.2), [1.2, 0.8, 0.5], "#5c3d2e"), O("cone", (2.8, 1.2, 0.2), [0.5, 0.9, 0.5], "#e8590c")]
    return t + list(extra)


FAMILY = [P((-1.2, 0, -1.4), "#f08c00", "sit", 21, outfit="casual", skin="#c68642"),            # uncle: mustard sweater
          P((0, 0, -1.4), "#5f3dc4", "sit", 22, outfit="elder", skin="#f1c27d"),               # grandma
          P((1.2, 0, -1.4), "#2b8a3e", "sit", 23, outfit="child", skin="#8d5524"),             # kid
          P((-2.2, 0, -2.2), "#c2255c", "sit", 24, outfit="casual", ry=-90, skin="#e0ac69")]   # aunt
v.B(4.2, "front", "Thanksgiving dinner. And for once, nobody at your table is fighting about politics.",
    V(dining(FAMILY), PLUM, focus=(-0.4, 1.15, -1.5), zoom=0.62, amb="room", bounce="#e8c9a0"), "THANKSGIVING", move="push_in",
    sfx=[{"type": "tick", "at": 0.3, "gain": 0.4}])

flags = [O("box", (0, -0.02, -16), [90, 0.04, 60], "#7a9e5a"),
         O("plane", (-9, 7, -18), [8, 5, 1], BLUE, animate=[{"type": "move", "to": [-1.2, 7, -18]}, {"type": "fade_out"}]),
         O("plane", (9, 7, -18.1), [8, 5, 1], RED, animate=[{"type": "move", "to": [1.2, 7, -18.1]}, {"type": "fade_out"}]),
         O("plane", (0, 7, -17.9), [9, 5.5, 1], PURPLE, animate=[{"type": "fade_in"}, {"type": "grow", "amount": 1.15}]),
         O("cylinder", (0, 4.5, -18.3), [0.25, 9, 0.25], "#dee2e6", material="metal"),
         crowd(28, 5, "#d8d8d8", at=(0, 0, -11), spread=(22, 0, 6), act="walk")]
v.B(4.0, "wide", "Because overnight, Democrats and Republicans merge into one big party. But wait until month two.",
    V(flags, LAV, focus=(0, 4, -14), zoom=1.4, amb="wind"), "ONE PARTY", transition="whip", effects=["rays"],
    sfx=[{"type": "boom", "at": 1.6, "gain": 0.6}])

booths = [O("box", (0, -0.02, -6), [24, 0.04, 16], "#ced4da")]
for i, x in enumerate((-4.5, -1.5, 1.5, 4.5)):
    booths += [O("box", (x, 1.0, -7), [1.6, 2.0, 0.1], "#495057"), O("box", (x, 1.4, -6.3), [1.6, 1.2, 0.05], "#e6e1f5", opacity=0.9)]
booths += [O("plane", (0.55, 1.2, -4.6), [0.4, 0.55, 1], "#ffffff", rotate=[0, 180, 0]),
           P((0, 0, -4.8), "#0b7285", "point", 31, outfit="hoodie", ry=180, skin="#5c3a21"),
           crowd(6, 33, "#d8d8d8", at=(0, 0, -10), spread=(10, 0, 2), act="walk")]
v.B(3.6, "follow", "Day one: you go to vote, and every ballot has just one name.",
    V(booths, CREAM, focus=(0, 1.3, -4.5), zoom=0.9, amb="room"), "ELECTION DAY", transition="zoom")

ind = [O("box", (0, -0.02, -8), [40, 0.04, 30], "#b2d8a8"), crowd(10, 41, "#868e96", at=(-3, 0, -8), spread=(6, 0, 4), act="walk"),
       crowd(14, 42, PURPLE, at=(3, 0, -8), spread=(7, 0, 4), act="idle"),
       O("tree", (0, 0, -18), 1.4, "#c0841a", count=8, seed=6, spread=[30, 0, 6])]
v.B(3.8, "aerial", "About 4 in 10 Americans say they're in no party. Now there's no other side to pick.",
    V(ind, MINT, focus=(0, 0, -6), zoom=0.9, amb="calm"), "INDEPENDENTS", tooltip={"label": "REAL", "text": "About 40% call themselves independent."})

lounge = [O("box", (0, -0.02, -3), [10, 0.04, 8], "#3d2b1f"), O("box", (0, 0.35, -1.6), [2.6, 0.7, 0.9], "#748ffc"),
          O("box", (0, 0.9, -1.2), [2.6, 0.7, 0.25], "#748ffc"), O("box", (0, 1.4, -5.2), [2.2, 1.3, 0.1], "#111"),
          O("plane", (0, 1.4, -5.14), [2.0, 1.1, 1], "#2b2f3a", material="glow", rotate=[0, 180, 0]),
          O("box", (0, 0.4, -5.1), [2.4, 0.8, 0.4], "#5c3d2e"),
          P((0, 0.1, -1.7), "#e64980", "sit", 51, outfit="hoodie", ry=180, skin="#f1c27d")]
v.B(3.6, "side", "No more attack ads. About 10 billion dollars of yelling, just gone. TV feels so quiet.",
    V(lounge, NIGHT, focus=(0, 1.0, -2.6), zoom=1.4, amb="room", bounce="#3b3355"), "NIGHT TV",
    stat={"value": "$10,000,000,000", "label": "SPENT ON POLITICAL ADS IN 2024"}, effects=["darken"])

hall = [O("box", (0, -0.02, -8), [40, 0.04, 30], "#8c6d4f"), O("sphere", (0, 0, -12), [16, 11, 10], "#e9e2d0", opacity=0.25)]
for k in range(14):
    a = math.pi * (0.1 + 0.8 * k / 13)
    hall.append(O("box", (round(math.cos(a) * 7, 2), 0.45, round(-4 - math.sin(a) * 5, 2)), [0.9, 0.9, 0.5], "#5c3d2e", rotate=[0, round(90 - math.degrees(a)), 0]))
hall += [crowd(40, 61, PURPLE, at=(0, 0, -7), spread=(12, 0, 5), act="idle"), O("box", (0, 0.8, -2), [2, 1.6, 0.8], "#3d2b1f"),
         O("particles", (0, 3, -6), 0.5, "#ffd43b", count=60, seed=7, spread=[14, 4, 8])]
v.B(3.8, "establishing", "Congress votes yes on everything. Laws that took years now pass in a day.",
    V(hall, LAV, focus=(0, 1, -7), zoom=0.9, amb="room", bounce="#e9e2d0"), "CONGRESS", move="crane_down",
    stat={"value": "535", "label": "MEMBERS. ONE PARTY."}, effects=["confetti"], sfx=[{"type": "pop", "at": 0.6}, {"type": "pop", "at": 1.3}])

podium = [O("box", (0, -0.02, -4), [16, 0.04, 12], "#2b2d42"), O("box", (0, 0.6, -2), [1.2, 1.2, 0.6], PURPLE),
          P((0, 0, -1.4), "#212529", "point", 71, outfit="suit", skin="#e0ac69"),
          O("box", (0, 0.25, -6), [0.6, 0.5, 0.6], "#495057", count=12, seed=4, spread=[8, 0, 3]),
          O("cone", (0, 6, -1.6), [2.4, 5, 2.4], "#fff3bf", material="glow", opacity=0.18, animate=[{"type": "pulse", "amount": 0.1}])]
v.B(3.8, "low_front", "Here's the scary part. With no other side, nobody asks the hard questions.",
    V(podium, NIGHT, focus=(0, 1.3, -1.6), zoom=0.9, amb="room", bounce="#2b2d42"), "THE PRESS ROOM", transition="dip",
    sfx=[{"type": "heartbeat", "at": 0.2, "dur": 3.0, "gain": 0.7}])

split = [O("box", (0, -0.02, -10), [60, 0.04, 40], "#a9c46c"),
         O("person", (0, 0, -9), 1.0, "#1098ad", outfit="casual", count=24, seed=81, spread=[8, 0, 5], action="walk",
           rotate=[0, 90, 0], animate=[{"type": "move", "to": [-9, 0, -9]}]),
         O("person", (0, 0, -9.4), 1.0, "#a8862a", outfit="ranger", count=24, seed=82, spread=[8, 0, 5], action="walk",
           rotate=[0, -90, 0], animate=[{"type": "move", "to": [9, 0, -9.4]}]),
         O("building", (-22, 0, -26), 4, "#adb5bd", count=6, seed=3, spread=[10, 0, 6]), O("tree", (20, 0, -24), 1.8, "#5c940d", count=8, seed=4, spread=[12, 0, 8])]
v.B(4.0, "far", "But by month two, the one party starts to crack. City against farm. Young against old.",
    V(split, MINT, focus=(0, 1, -9), zoom=1.1, amb="wind"), "MONTH TWO", transition="whip", effects=["shake"],
    sfx=[{"type": "crack", "at": 0.5}])

newflags = [O("box", (0, -0.02, -14), [70, 0.04, 50], "#c9b48a"),
            O("plane", (-5, 6, -16), [6, 4, 1], "#2f9e44", animate=[{"type": "grow", "amount": 1.3}]),
            O("plane", (5, 6, -16), [6, 4, 1], "#f76707", animate=[{"type": "grow", "amount": 1.3}]),
            O("cylinder", (-5, 4, -16.2), [0.2, 8, 0.2], "#dee2e6"), O("cylinder", (5, 4, -16.2), [0.2, 8, 0.2], "#dee2e6"),
            crowd(18, 91, "#2f9e44", at=(-6, 0, -10), spread=(7, 0, 4), act="idle"), crowd(18, 92, "#f76707", at=(6, 0, -10), spread=(7, 0, 4), act="idle")]
v.B(3.6, "orbit", "Soon there are two sides again. Same fights. New names.",
    V(newflags, PLUM, focus=(0, 3, -12), zoom=3.0, amb="wind"), "MONTH SIX", effects=["rays"])

town = [O("box", (0, -0.02, -10), [60, 0.04, 40], "#b08d5b"), O("box", (0, 0.01, -10), [4, 0.02, 40], "#8a6a45")]
for i, (x, z) in enumerate([(-6, -8), (-6, -14), (6, -9), (6, -15), (-6, -20), (6, -21)]):
    town += [O("box", (x, 1.5, z), [4, 3, 4], ["#8b5e3c", "#a47148", "#6f4518"][i % 3]), O("cone", (x, 3.9, z), [3.4, 1.8, 3.4], "#5c3d2e")]
town += animal((3, 0, -6), 1.1, "#7a5230", anim=[{"type": "bob", "amount": 0.03}])
town += [P((0, 0, -5), "#343a40", "point", 101, outfit="suit", ry=180, skin="#f1c27d"), crowd(12, 102, "#d8d8d8", at=(0, 0, -12), spread=(6, 0, 8), act="walk"),
         O("cylinder", (-2.5, 3, -5), [0.15, 6, 0.15], "#dee2e6"), O("plane", (-1.5, 5.4, -5), [2, 1.2, 1], "#adb5bd")]
v.B(4.2, "dolly", "And here's the twist. This really happened. Around 1820, America had just one main party.",
    V(town, SEPIA, focus=(0, 1.3, -6), zoom=1.1, amb="wind", bounce="#c9a77a"), "AROUND 1820", transition="dip", effects=["freeze"],
    tooltip={"label": "REAL", "text": "Historians call it the Era of Good Feelings."})

town2 = town[:-4] + [crowd(10, 111, "#495057", at=(-3, 0, -9), spread=(4, 0, 4), act="point"), crowd(10, 112, "#7a5230", at=(3, 0, -9), spread=(4, 0, 4), act="point")]
v.B(3.8, "front", "It lasted about 8 years. Then it split, and two new parties were born.",
    V(town2, SEPIA, focus=(0, 1.2, -9), zoom=1.5, amb="wind", bounce="#c9a77a"), "ABOUT 1825", effects=["freeze", "shake"],
    stat={"value": "8 YEARS", "label": "HOW LONG ONE PARTY LASTED", "count_up": False})

FAMILY2 = [P((-1.2, 0, -1.4), "#f08c00", "point", 21, outfit="casual", skin="#c68642"), FAMILY[1], FAMILY[2],
           P((-2.2, 0, -2.2), "#c2255c", "point", 24, outfit="casual", ry=-90, skin="#e0ac69")]
v.B(4.0, "closeup", "So by next Thanksgiving, your uncle is yelling again. Just about a brand new party.",
    V(dining(FAMILY2), PLUM, focus=(-1.2, 1.25, -1.4), zoom=0.8, amb="room", bounce="#e8c9a0"), "NEXT THANKSGIVING", move="pull_out",
    transition="whip", effects=["shake"])

v.save("oneparty", "What if Democrats and Republicans were the same party?",
       "Both US parties merge into one. Ballots with one name, quiet TV, Congress passes everything, then the party splits again, just like the one-party era around 1820.",
       "film", "", ["ONE PARTY", "OR TWO?"], "ONE *PARTY*", 1, accent="#b197fc")
