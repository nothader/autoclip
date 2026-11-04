"""What if the ocean was made of gummy bears? (voxel format sample: counter card on every beat, deadpan lines, callback ending)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from vox import Vox, biome, carpet, person, crowd, prop, landmark, env, ambience  # noqa: E402
from props import O  # noqa: E402

v = Vox(seed=11)
C = v.C
SEA = lambda n=6000, z=-16, h=0.5, size=0.34, seed=3: carpet("gummy_bear", n, at=(0, 0, z), spread=(60 * max(1, size * 3), h, 22 * max(1, size * 3)), size=size, seed=seed)
KID = dict(seed=41, top="#ffd43b", pants="#3f5a85")
CLOSE = dict(focus=(0, 1.3, -3), zoom=0.75)          # our main character: yellow tee, the callback at the end

# 1. Cold open: the ocean is gummies. The narrator reads the title over this.
v.B(3.6, "wide", env(biome("beach", 11, extra=[SEA(), crowd(9, 5, at=(0, 0, -6), spread=(10, 0, 4), act="cheer")], n_props=8), "cotton",
                     focus=(0, 1.0, -6), zoom=1.6, amb="ocean"),
    counter=C(0, 600, "Gummy bears in the ocean", "quintillion", "Roughly. Nobody counted."), move="swoop_in",
    sfx=[{"type": "pop", "at": 0.4}, {"type": "sparkle", "at": 1.2}])
# 2. First bite.
v.B(3.2, "front", env([O("box", (0, -0.05, -3), [20, 0.1, 20], "#f3d9a4"), SEA(3000, z=-9),
                         person((0, 0, -3), act="idle", face="smile", **KID), prop("gummy_bear", (-0.45, 1.05, -3.2), 0.22, color="#ff6b6b", anim=[{"type": "bob", "amount": 0.04}])],
                        "peach", focus=(0, 1.3, -3), zoom=0.75, amb="ocean"),
    counter=C(0, 1, "Bites taken", "delicious", "Day one is great."), sfx=[{"type": "pop", "at": 1.0}])
# 3. Everyone shows up.
v.B(3.4, "aerial", env(biome("beach", 12, extra=[SEA(8000, z=-14), crowd(60, 9, at=(0, 0, -3), spread=(26, 0, 8), act="walk"),
                                                    prop("sign", (5, 0, 1), 2.4)], n_props=10), "lemon", focus=(0, 0, -4), zoom=2.2, amb="ocean"),
    counter=C(0, 48000, "People at one beach", "record", "Lifeguards relax. You can't drown in candy."), sfx=[{"type": "steps", "at": 0.2, "dur": 2.5}])
# 4. You can't drown. You just get stuck.
v.B(3.4, "front", env([O("box", (0, -0.05, -4), [30, 0.1, 30], "#f3d9a4"), carpet("gummy_bear", 7000, at=(0, 0, -2.5), spread=(30, 1.0, 7), size=0.28, seed=6),
                       person((-1.4, 0.3, -4), seed=77, act="swim", face="shock", ry=90), person((1.3, 0.3, -4.6), seed=78, act="scared", face="shock"),
                       person((0.2, 0.4, -6), seed=79, act="swim", face="sad", ry=-90)], "mint", focus=(0, 1.0, -4.8), zoom=1.5, amb="ocean"),
    counter=C(2, 0.1, "Swim speed", "too slow", unit="m/s", line="You just get stuck. Politely.", decimals=1, tag_color="#1c7ed6"), move="push_in")
# 5. Noon: it melts into one gummy.
v.B(3.4, "front", env([O("box", (0, -0.05, -10), [80, 0.1, 60], "#f3d9a4"), O("box", (0, 0.15, -18), [80, 0.3, 26], "#ff8787", material="glossy"),
                      prop("palm_tree", (-5, 0, -12), 8), prop("palm_tree", (4, 0, -15), 9), prop("umbrella", (1.6, 0, -4), 2.2),
                      person((0, 0, -5), seed=88, act="think", face="sad")], "golden", focus=(0, 1.2, -5), zoom=1.1, amb="ocean"),
    counter=C(24, 38, "Beach temperature", "melting", unit="°C", line="By noon, the ocean is one gummy.", tag_color="#f76707"), effects=["heat"], move="crane_up")
# 6. Sharks are fine.
v.B(3.2, "side", env([O("box", (0, -0.05, -4), [30, 0.1, 30], "#ff8787"), carpet("gummy_bear", 3000, at=(0, 0, -4), spread=(9, 1.2, 9), size=0.3, seed=8),
                      prop("shark", (0, 0.6, -4), 4.5, ry=90, anim=[{"type": "bob", "amount": 0.2}]), prop("fish", (-2.5, 0.5, -3), 0.9, count=6, spread=(5, 1, 3), seed=5)],
                     "sea", focus=(0, 1.4, -4), zoom=2.2, amb="ocean"),
    counter=C(0, 3.5, "Fish complaining", "trillion", "Sharks are fine. They just chew more.", decimals=1, tag_color="#7048e8"), move="arc_left")
# 7. Ships stuck.
v.B(3.2, "wide", env([O("box", (0, -0.05, -40), [400, 0.1, 300], "#ff8fab"), SEA(9000, z=-40, h=0.8, size=0.9, seed=12),
                     prop("cruise_ship", (0, 0, -60), 90, ry=90, anim=[{"type": "wobble", "amount": 0.03}]),
                     prop("boat", (-22, 0, -38), 9, ry=40), prop("sailboat", (24, 0, -44), 12, ry=-30), prop("boat", (10, 0, -30), 7, ry=200),
                     prop("crate", (-8, 0, -30), 2.5, count=6, spread=(14, 0, 6), seed=4)],
                    "sky", focus=(0, 8, -60), zoom=7, amb="ocean"),
    counter=C(0, 50000, "Cargo ships stuck", "at sea", line="Your new shoes are stuck at sea. For good.", tag_color="#0ca678"), move="pull_out")
# 8. Ants.
v.B(3.2, "low_front", env(biome("park", 31, extra=[carpet("gummy_bear", 400, at=(0, 0, -4), spread=(6, 0.2, 3), size=0.3, seed=4),
                                                      O("particles", (0, 0.05, -4), 0.3, "#212529", count=160, seed=5, spread=(8, 0.1, 5)),
                                                      person((-1.2, 0, -2.5), seed=93, act="scared", face="shock")], n_props=7),
                          "matcha", focus=(0, 0.7, -4.5), zoom=1.0, amb="forest"),
    counter=C(0, 20, "Ants arriving", "quadrillion", "Every ant on Earth got the same text.", tag_color="#e8590c"))
# 9. Sticky rain.
v.B(3.2, "wide", env(biome("city", 41, extra=[crowd(16, 14, at=(0, 0, -6), spread=(14, 0, 6), act="run", face="shock"),
                                                 prop("umbrella", (0, 0, -4), 2.2, count=8, spread=(12, 0, 5), seed=7),
                                                 O("particles", (0, 8, -8), 0.18, "#ff8fab", count=180, seed=9, spread=(30, 16, 20))], n_props=9),
                     "storm", focus=(0, 2, -6), zoom=1.8, amb="wind"),
    counter=C(0, 100, "Sugar in the rain", "sticky", unit="%", line="It's raining syrup. Umbrellas sell out.", tag_color="#d6336c"), sfx=[{"type": "thunder", "at": 0.3}])
# 10. The gummy wave: Statue of Liberty for scale.
WAVE = lambda h, z: carpet("gummy_bear", 9000, at=(0, 0, z), spread=(320, h, 30), size=4.0, seed=21,
                           anim=[{"type": "move", "to": [0, 0, z + 60]}])
v.B(3.6, "far", env([O("box", (0, -0.05, -150), [800, 0.1, 600], "#f3d9a4"), WAVE(93, -260), landmark("statue_of_liberty", (0, 0, -130)),
                     prop("skyscraper", (-110, 0, -150), 150), crowd(30, 22, at=(0, 0, -40), spread=(60, 0, 10), act="run", face="shock")],
                    "dusk", focus=(0, 50, -170), zoom=9, amb="rumble"),
    counter=C(0, 93, "Gummy wave height", unit="m", line="It's adorable. It is also a wave.", tag="≈ Statue of Liberty", tag_color="#0ca678"),
    effects=["shake"], sfx=[{"type": "rumble", "at": 0, "dur": 3.4}])
# 11. Eiffel Tower.
v.B(3.6, "far", env([O("box", (0, -0.05, -150), [900, 0.1, 700], "#ffc9c9"), WAVE(330, -300), landmark("eiffel_tower", (0, 0, -150)),
                     prop("apartment", (-60, 0, -130), 30, count=6, spread=(80, 0, 30), seed=3)],
                    "sunset", focus=(0, 150, -220), zoom=20, amb="rumble"),
    counter=C(None, 330, "Gummy wave height", unit="m", line="Still growing. Somehow cuter.", tag="≈ Eiffel Tower", tag_color="#1c7ed6"),
    effects=["shake"], move="crane_up", sfx=[{"type": "boom", "at": 2.6}])
# 12. The only winner.
v.B(3.4, "front", env(biome("hospital", 51, extra=[person((0, 0, -4), seed=104, act="cheer", face="smile", top="#f8f9fa"),
                                                      prop("money_stack", (-1.4, 0, -4.4), 0.6, count=5, spread=(1, 0, 1)), prop("toothbrush", (1.3, 1, -4.2), 0.5)], n_props=6),
                      "arctic", focus=(0, 1.2, -4.2), zoom=0.9, amb="room"),
    counter=C(0, 1, "Happy dentists", "all of them", "One industry wins.", tag_color="#0ca678"), effects=["confetti"], sfx=[{"type": "sparkle", "at": 0.5}])
# 13. Callback: the kid from beat 2.
v.B(3.6, "front", env([O("box", (0, -0.05, -3), [20, 0.1, 20], "#ffc9c9"), O("box", (0, 0.15, -9), [40, 0.3, 10], "#ff8787", material="glossy"),
                         person((0, 0, -3), act="idle", face="sad", **KID), prop("gummy_bear", (-0.45, 1.05, -3.2), 0.22, color="#ff6b6b", anim=[{"type": "bob", "amount": 0.04}])],
                        "lilac", focus=(0, 1.3, -3), zoom=0.75, amb="ocean"),
    counter=C(1, 2, "Bites taken", "regret", line="Day two. Still delicious. Never again."))

v.save("gummy_ocean", "What if the ocean was made of gummy bears?",
       "The entire ocean is replaced by gummy bears. Funny escalation from first bite to a 330 m gummy wave, with a counter on every beat.",
       ["WOULD YOU", "SWIM IN IT?", "YES OR NO"], "GUMMY OCEAN", thumb_beat=9)
