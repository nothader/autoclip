"""What if only one gender existed? Two worlds compared: all-women Earth vs all-men Earth (swap recipe, bold).
Facts (rounded, widely cited): ~93% of US prisoners are men (BOP); ~7 in 10 US car-crash deaths are men (IIHS);
women outlive men by ~5 years worldwide (WHO); whiptail lizards: all-female species that reproduce without males."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from hit import *  # noqa: E402,F403

v = Video()
W_BG = ["#c2255c", "#ffdeeb"]; M_BG = ["#1864ab", "#d0ebff"]
women = lambda n=14, seed=4, at=(0, 0, -10), spread=(16, 0, 10), act="walk": O("person", at, 1.0, GIRL, count=n, seed=seed, spread=list(spread), action=act)
men = lambda n=14, seed=9, at=(0, 0, -10), spread=(16, 0, 10), act="walk": O("person", at, 1.0, BOY, count=n, seed=seed, spread=list(spread), action=act)
split = lambda: [O("box", (-15, -0.02, -12), [30, 0.04, 60], "#fcc2d7"), O("box", (15, -0.02, -12), [30, 0.04, 60], "#a5d8ff"),
                  women(14, 4, at=(-3.5, 0, -9), spread=(5, 0, 8)), men(14, 9, at=(3.5, 0, -9), spread=(5, 0, 8)),
                  O("box", (0, 0.05, -12), [0.3, 0.1, 60], "#ffd43b", material="glow")]
WW, MW = "ALL-WOMEN WORLD", "ALL-MEN WORLD"

v.B(4.4, "wide", "In 3 seconds, Earth gets just one gender. But which one wins?", V(city([crowd(24, 3, at=(0, 0, -12), spread=(20, 0, 16))]), SKY,
    focus=(0, 1.4, -12), zoom=1.8), "+0 SEC", "8 BILLION PEOPLE", move="none", sfx=[{"type": "shimmer", "at": 3.0, "gain": 0.8}])
v.B(3.4, "wide", "Planet A: only women. Planet B: only men. Let's compare.", V(split(), GOLD, focus=(0, 1, -10), zoom=1.2), "DAY 1", "TWO WORLDS",
    effects=["flash"])
off = room("#ffdeeb", "#e9ecef", "#ffc9de", w=16, d=12, extra=[O("box", (0, 0.74, -7), [1.6, 0.05, 0.9], "#f8f9fa", count=8, seed=2, spread=[12, 0, 6]),
           women(8, 12, at=(0, 0, -7), spread=(12, 0, 6), act="sit"), O("box", (-6, 1.6, -11.9), [0.5, 0.7, 0.06], "#f8f9fa"),
           O("plane", (-6, 1.65, -11.85), [0.36, 0.25, 1], "#ff8787", material="glow", animate=[{"type": "pulse", "amount": 0.3, "speed": 2}])])
v.B(3.4, "dolly", "In the all-women world, the office thermostat war ends. Forever.", V(off, ["#ffdeeb", "#fcc2d7"], focus=(0, 1.2, -7), zoom=1.1, bounce="#ffdeeb"),
    "DAY 1", WW, transition="whip")
road = city([O("box", (-1.5, 0.65, -14), [2.0, 1.3, 4.4], "#1c7ed6", rotate=[0, 25, 0]), O("box", (1.2, 0.65, -12.5), [2.0, 1.3, 4.4], "#495057", rotate=[0, -40, 0]),
             O("particles", (0, 1, -13), 0.4, "#ced4da", count=12, seed=4, spread=[4, 2, 4], animate=[{"type": "drift", "axis": "y", "amount": 0.3}]),
             men(6, 14, at=(0, 0, -9), spread=(12, 0, 4), act="point")])
v.B(3.4, "follow", "In the all-men world, car insurance spikes. About 7 in 10 US crash deaths are men.", V(road, M_BG, focus=(0, 1.0, -12), zoom=1.2), "DAY 3", MW,
    transition="whip", stat={"value": "7 IN 10", "label": "US CAR-CRASH DEATHS WHO ARE MEN", "count_up": False}, sfx=[{"type": "impact", "at": 0.4, "gain": 0.8}])
jail = [O("box", (0, 0, -4), [10, 0.05, 10], "#adb5bd"), O("box", (0, 1.5, -8), [10, 3, 0.1], "#ffdeeb"),
        O("cylinder", (-4, 1.5, -2), [0.08, 3, 0.08], "#495057", material="metal", count=14, seed=1, spread=[8, 0, 0]),
        O("box", (-1, 0.3, -6), [2, 0.6, 0.9], "#f8f9fa"), O("box", (0, 0.2, -4), [0.6, 0.4, 0.6], "#ffd43b", animate=[{"type": "bob", "amount": 0.05, "speed": 1}])]
v.B(3.4, "follow", "In the all-women world, prisons are almost empty. 93% of US prisoners are men.", V(jail, W_BG, focus=(0, 1.0, -4), zoom=1.0),
    "1 MONTH", WW, stat={"value": "93%", "label": "OF US PRISONERS ARE MEN", "count_up": True})
bath = [O("box", (0, -0.02, -6), [20, 0.04, 20], "#dee2e6"), O("box", (0, 0.4, -6.3), [0.6, 0.8, 0.8], "#f8f9fa"),
        O("box", (0, 0.85, -6.7), [0.6, 0.06, 0.6], "#f8f9fa", rotate=[80, 0, 0], animate=[{"type": "wobble", "amount": 0.3, "speed": 2}]),
        P((1.4, 0, -6), BOY, "point", 2, ry=270), P((-1.6, 0, -6.5), BOY, "idle", 5, ry=90)]
v.B(3.4, "wide", "In the all-men world, the toilet seat debate is over. Nobody puts it down.", V(bath, M_BG, focus=(0, 0.9, -6.2), zoom=0.55),
    "1 MONTH", MW, sfx=[{"type": "crack", "at": 1.2, "gain": 0.4}])
v.B(3.4, "far", "And the all-women world lives longer. Women outlive men by about 5 years.", V(park([women(10, 16, at=(0, 0, -10), spread=(20, 0, 8)),
    P((0, 0, -6), GIRL, "walk", 7, outfit="elder", ry=180)]), W_BG, focus=(0, 1.2, -8), zoom=1.6, amb="forest"), "1 YEAR", WW,
    stat={"value": "+5 YEARS", "label": "WOMEN'S LIFE EXPECTANCY GAP", "count_up": False})
nursery = [O("box", (0, -0.02, -6), [24, 0.04, 20], "#fff3bf"), O("box", (0, 0.5, -6), [1.0, 0.8, 0.6], "#f8f9fa", count=8, seed=3, spread=[9, 0, 4],
           animate=[{"type": "fade_out"}]), P((-3, 0, -4), GIRL, "idle", 3, ry=180), P((3, 0, -4), BOY, "idle", 2, ry=180)]
v.B(3.6, "wide", "Here's the scary part: babies. In both worlds, almost no new babies.", V(nursery, ["#ffd8a8", "#fff3bf"], focus=(0, 0.8, -5.5), zoom=0.8),
    "1 YEAR", "BOTH WORLDS", transition="dip", effects=["darken"], sfx=[{"type": "heartbeat", "at": 0.4, "dur": 2.8, "gain": 0.7}])
lab = room("#e7f5ff", "#dee2e6", w=12, d=10, extra=[O("cylinder", (0, 0.8, -7), [0.9, 1.6, 0.9], "#adb5bd", material="metal", count=6, seed=2, spread=[9, 0, 2]),
           O("particles", (0, 1.8, -7), 0.3, "#e7f5ff", count=20, seed=4, spread=[9, 1, 2], animate=[{"type": "drift", "axis": "y", "amount": 0.2}]),
           P((0, 0, -5), GIRL, "walk", 6, outfit="doctor", ry=90, anim=[{"type": "move", "to": [2, 0, -5]}])])
v.B(3.4, "dolly", "The all-women world has one way out: frozen sperm banks. For a while.", V(lab, W_BG, focus=(0, 1.2, -6), zoom=1.0, bounce="#e7f5ff"), "10 YEARS", WW)
v.B(3.6, "far", "The all-men world has no way to have babies. In 100 years, it is gone.", V(city([men(10, 19, at=(0, 0, -12), spread=(20, 0, 14), act="walk"),
    P((0, 0, -7), BOY, "walk", 5, outfit="elder", ry=180)], ), DUSK, focus=(0, 1.4, -12), zoom=2.0), "100 YEARS", MW, move="pull_out", effects=["darken"])
lizard = lambda at: [O("capsule", at, [0.25, 1.2, 0.25], "#8a9a5b", rotate=[90, 0, 0], animate=[{"type": "wobble", "amount": 0.3, "speed": 4}]),
                     O("cone", (at[0], at[1], at[2] + 0.9), [0.12, 0.8, 0.12], "#8a9a5b", rotate=[90, 0, 0])]
desert = [O("box", (0, -0.02, -6), [60, 0.04, 60], "#e0b97a"), O("rock", (0, 0.3, -8), 0.8, "#b08968", count=8, seed=3, spread=[12, 0, 6])] + \
         lizard((-1, 0.15, -5)) + lizard((0.8, 0.15, -6)) + lizard((2, 0.15, -4.5))
v.B(3.4, "wide", "Nature already tried it. Whiptail lizards are all female. And they still have babies.", V(desert, GOLD, focus=(0.5, 0.4, -5), zoom=0.4),
    "BONUS FACT", "REAL", transition="whip", tooltip={"label": "REAL", "text": "Some whiptail lizard species have no males at all."})
v.B(3.8, "wide", "So which world would last longer? Pick a side.", V(split(), DUSK, focus=(0, 1, -10), zoom=1.3), "THE END", "TWO WORLDS", effects=["glow"])
v.save("onegender", "What if only one gender existed?", "Earth becomes one gender. We compare an all-women world and an all-men world: crime, cars, lifespan and babies.",
       "bold", "SINCE THE CHANGE", ["WHICH WORLD", "LASTS LONGER?"], "ONLY *ONE* GENDER", 1, accent="#ff6b6b", captions=None)
