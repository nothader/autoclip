"""What if women ran every country? (swap recipe, cinematic warm, neutral). Facts: ~27 of 193 UN members led by women in 2025 (~1 in 7);
women hold ~27% of parliament seats worldwide (about 3 in 4 are men); 193 UN member states."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403

v = Video()
hall = [O("box", (0, 0, -10), [40, 0.05, 30], "#8d6e57"), O("box", (0, 6, -24), [40, 12, 0.2], "#1864ab"),
        O("cylinder", (0, 6, -23.8), [3, 0.1, 3], "#f8f9fa", rotate=[90, 0, 0]),
        O("box", (0, 0.6, -14), [24, 0.1, 1.2], "#adb5bd", count=1)]
flags = [O("box", (-18 + i * 3, 4.5, -23.6), [1.6, 1.0, 0.05], c) for i, c in enumerate(["#e03131", "#fab005", "#2b8a3e", "#1c7ed6", "#f8f9fa", "#7048e8", "#e8590c", "#0ca678",
                                                                                        "#c2255c", "#495057", "#ffd43b", "#1971c2", "#d9480f"])]
leaders = lambda col=GIRL, n=24, act="sit", seed=3, anim=(): O("person", (0, 0, -10), 1.0, col, outfit="suit", count=n, seed=seed, spread=[30, 0, 12], action=act, animate=list(anim))
WARM = ["#2b1d3a", "#e8875c"]
v.B(4.4, "wide", "In 3 seconds, every country on Earth gets a woman as its leader.", V(hall + flags + [leaders(BOY, act="sit", seed=3, anim=[{"type": "fade_out"}]), leaders(GIRL, act="sit", seed=3, anim=[{"type": "fade_in"}])], WARM, focus=(0, 1.4, -12), zoom=1.5,
    amb="room"), "+0 SEC", "THE UNITED NATIONS", move="none", sfx=[{"type": "shimmer", "at": 3.0, "gain": 0.7}])
v.B(3.4, "wide", "Today, only about 1 in 7 countries is led by a woman.", V(hall + flags + [leaders(GIRL, act="sit", seed=3), P((-6, 0.7, -14), GIRL, "walk", 3, outfit="suit", ry=270, anim=[{"type": "move", "to": [0, 0.7, -14]}])],
    WARM, focus=(0, 2, -12), zoom=2.0, amb="room"), "+1 SEC", stat={"value": "~1 IN 7", "label": "COUNTRIES LED BY A WOMAN TODAY", "count_up": False})
v.B(3.4, "dolly", "Day one: 193 women walk into the UN. But the real test comes later.", V(hall + flags + [crowd(14, 6, col=GIRL, at=(0, 0, -4), spread=(8, 0, 6), act="walk", outfit="suit")],
    WARM, focus=(0, 1.4, -8), zoom=1.4, amb="room"), "+1 DAY", transition="whip")
parl = [O("box", (0, 0, -10), [40, 0.05, 30], "#2b8a3e"), O("box", (0, 6, -24), [40, 12, 0.2], "#e9dcc9"),
        O("box", (0, 0.15, -10), [0.7, 0.3, 0.6], "#5c940d", count=40, seed=4, spread=[30, 0, 14])]
v.B(3.4, "wide", "Parliaments flip too. Right now, about 3 in 4 seats belong to men.", V(parl + [leaders(GIRL, 30, "sit", 8), P((-8, 0, -6), "#868e96", "walk", 9, outfit="suit", ry=270, anim=[{"type": "move", "to": [8, 0, -6]}])], SKY, focus=(0, 2, -10), zoom=2.0, amb="room"),
    "+1 MONTH", stat={"value": "73%", "label": "OF PARLIAMENT SEATS HELD BY MEN TODAY", "count_up": True})
v.B(3.4, "follow", "Would wars stop? Honestly, nobody knows. Leaders face the same hard choices.", V(hall + flags + [P((0, 0, -12), GIRL, "point", 3, outfit="suit", ry=180)],
    ["#1b2440", "#8a5a6a"], focus=(0, 1.6, -12), zoom=1.0, amb="room"), "+6 MONTHS", effects=["darken"])
v.B(3.4, "follow", "Paid leave and childcare would likely get way more attention.", V(park([crowd(8, 11, at=(0, 0, -8), spread=(14, 0, 8)), P((0, 0, -5), GIRL, "walk", 4),
    P((0.8, 0, -5), "#fab005", "walk", 7, outfit="child", s=0.6)]), SKY, focus=(0, 1.0, -5), zoom=1.2), "+1 YEAR", transition="whip")
protest = city([crowd(16, 13, col=BOY, at=(0, 0, -16), spread=(10, 0, 12), act="walk"),
                O("box", (0, 2.6, -16), [1.0, 0.6, 0.05], "#f8f9fa", count=8, seed=13, spread=[10, 0, 12], animate=[{"type": "bob", "amount": 0.1, "speed": 2}])])
v.B(3.4, "wide", "And some men would ask: when is it our turn again?", V(protest, GOLD, focus=(0, 1.6, -14), zoom=1.8), "+2 YEARS")
booth = room("#e7f5ff", "#dee2e6", w=14, d=12, extra=[O("box", (-4, 1.0, -9), [1.4, 2.0, 1.4], "#4dabf7", count=4, seed=2, spread=[10, 0, 0]),
                                                       crowd(10, 17, at=(0, 0, -6), spread=(10, 0, 6), act="walk")])
v.B(3.4, "dolly", "Then the next election comes. Everyone gets to vote.", V(booth, ["#e7f5ff", "#a5d8ff"], focus=(0, 1.2, -6), zoom=1.2, amb="room", bounce="#e7f5ff"),
    "+4 YEARS", transition="dip")
v.B(3.6, "far", "Here's the real question: would people vote to keep it?", V(hall + flags + [leaders(GIRL, act="sit", seed=3)], WARM, focus=(0, 2, -12), zoom=3.0, amb="room"),
    "+4 YEARS", move="pull_out", effects=["glow"])
v.save("leaders", "What if women ran every country?", "Every country on Earth gets a woman as its leader overnight. A neutral look at what could change.",
       "cinematic", "SINCE THE CHANGE", ["WOULD THE WORLD", "BE BETTER?"], "WOMEN RUN *EVERY* COUNTRY", 1, accent="#f4a259", palette="warm", countdown=True)
