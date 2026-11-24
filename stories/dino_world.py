"""What if dinosaurs never went extinct? 30 s Short. Structure: cold-open chase -> freeze-frame -> rewind through your day -> back to the chase -> twist.
Real fact: birds are living dinosaurs (they descend from theropods, the T-rex's group)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dink"))
from kit import Story, Set, cam, say, badge, stamp, floaty, label, emoji, meter, DAY, SUNNY, INDOOR, DAWN, MINT  # noqa: E402
from assets import (O, bean, crowd, dino, sauropod, pterodactyl, animate_all, park, bedroom_kid, classroom, cafeteria,  # noqa: E402
                    stadium, supermarket, pizza, gift)

s = Story("dino_world", "What if dinosaurs never went extinct?", accent="#a9e34b",
          hook=["WHAT IF", "DINOSAURS", "NEVER DIED?"], hook_accent=1, skin="#c68642", sleeve="#845ef7", mood="epic")
REX = "#2f9e44"
REXV = "am_onyx"

# 0 — cold open: you're sprinting, looking back at a T-rex. Freeze.
s.beat(3.7, "", Set(park(seed=3, grass="#82c91e") + animate_all(dino((0, 0, 9), REX, size=1.6, face_you=False), [{"type": "move", "to": [0, 0, -2.8], "rel": True}]),
                    sky=SUNNY, ambient=1.5, light=2.6, sun_dir=(3, 9, -6)),
       cam((0, 1.5, 0.5), (0, 2.4, 10), head="run"), hands="run", fx=["shake"],
       freeze={"at": 2.75, "label": "yep. that's you. 🙃"}, sfx=[{"type": "slam", "at": 0.0, "gain": 0.6}])
# 1 — rewind to 7 AM: a tiny raptor is your alarm clock
s.beat(3.0, "let's rewind to *7 AM*", Set(bedroom_kid(seed=4, wall="#ffe066") + dino((-1.4, 0.62, -3.0), "#f76707", size=0.5),
                                          sky=DAWN, ambient=1.5, light=2.2, bounce="#ffe066"),
       cam((0, 1.0, 0.6), (-0.8, 0.9, -3.0)), hands="none", fx=["whip"],
       say=[say("RAWR. (that means get up)", "am_puck", 0.4, who=(-1.4, 1.9, -2.7), name="Alarm", speed=1.1)],
       stickers=[floaty("⏪ 7:00 AM", 0.1, color="#ffffff", y=0.2, size=70)])
# 2 — the school bus has a neck
s.beat(3.2, "the school bus has a *neck*", Set(park(seed=5, grass="#94d82d", trees=3) + sauropod((0.8, 0, -7.5), "#74b816", size=1.2, riders=7, seed=5) +
                                               [O("box", (-2.0, 1.1, -3.5), [0.08, 2.2, 0.08], "#495057"), O("box", (-2.0, 2.3, -3.5), [0.7, 0.45, 0.05], "#fab005")],
                                               sky=DAY, ambient=1.4, light=2.6),
       cam((0, 1.5, 1.5), (0.5, 3.0, -6), head="breathe"), hands="wave", fx=["whip"],
       say=[say("Hop on! Mind the tail.", "am_eric", 0.5, who=(0.8, 6.4, -5.0), name="Driver")],
       stickers=[label("🚌 BUS", who=(0.8, 3.2, -7.5), at=1.6, side="left")])
# 3 — the real fact
s.beat(3.3, "your teacher drops a *fact*", Set(classroom(seed=6, kids=6, extra=[bean((1.6, 0, -5.3), "#748ffc", expr="happy", act="point", ry=0, hat="bun", seed=61, talk=[(0.3, 1.8)])]) +
                                               [O("emoji", (-0.2, 1.6, -6.3), 0.9, text="🐔"), O("emoji", (0.9, 1.6, -6.3), 0.6, text="=")] +
                                               [O("emoji", (1.8, 1.65, -6.3), 0.9, text="🦖")],
                                               sky=INDOOR, ambient=1.6, light=2.0, bounce="#e7dcc6"),
       cam((0, 1.3, 0.4), (0.4, 1.4, -5.5)), hands="idle", fx=["whip"],
       say=[say("Birds ARE dinosaurs. Yes, chickens too.", "af_bella", 0.3, who=(1.6, 1.9, -5.3), name="Ms. Kim")],
       stickers=[badge("Birds are living dinosaurs 🐦", at=1.7, title="REAL FACT")])
# 4 — lunch is a negotiation
s.beat(3.1, "lunch is a *negotiation*", Set(cafeteria(seed=7, extra=[O("box", (0, 0.4, -0.6), [1.8, 0.08, 1.1], "#8d6e57")] + pizza((-0.2, 0.45, -0.4), 0.28)) +
                                            dino((0.1, 0.44, -1.2), "#e64980", size=0.36),
                                            sky=INDOOR, ambient=1.1, light=1.6, bounce="#8d6e57"),
       cam((0, 1.15, 0.5), (0, 0.7, -1.2)), hands="none", fx=["whip"],
       say=[say("This is a pizza tax.", "am_puck", 0.3, who=(0.1, 1.45, -1.0), name="Tiny Rex", speed=1.1)],
       stickers=[floaty("-1 SLICE", 1.5, color="#ff6b6b", y=0.5)])
# 5 — pterodactyl steals the ball
s.beat(3.1, "pterodactyls ruin *every* game", Set(stadium(seed=8) + animate_all(pterodactyl((-1.2, 2.9, -3.2), size=1.5, face_you=True),
                                                                                 [{"type": "move", "to": [2.2, 0.4, -0.6], "rel": True}]) +
                                                  [O("sphere", (-1.2, 2.5, -2.8), 0.22, "#f8f9fa", animate=[{"type": "move", "to": [1.0, 2.9, -3.4]}])],
                                                  sky=DAY, ambient=1.5, light=2.6),
       cam((0, 1.6, 2), (0, 2.8, -3.6)), hands="cheer", fx=["whip"],
       say=[say("HEY! THAT'S OUR BALL!", "am_adam", 0.9, who=(0, 3.0, -9), name="Coach", speed=1.15)],
       stickers=[stamp("FOUL!", 1.9, color="#fab005", rot=-6)])
# 6 — T-rex vs self-checkout
s.beat(3.2, "T-rex tries the *self-checkout*", Set(supermarket(seed=9) + dino((0, 0, -4.2), REX, size=0.95) +
                                                   [O("box", (0.1, 0.5, -2.7), [0.8, 1.0, 0.6], "#495057"), O("plane", (0.1, 1.05, -2.39), [0.5, 0.35, 1], "#74c0fc", material="glow")],
                                                   sky=INDOOR, ambient=1.6, light=2.2, bounce="#e9ecef"),
       cam((0.9, 1.6, 0.4), (0, 1.5, -3.6)), hands="idle", fx=["whip"],
       say=[say("Unexpected item... in bagging area.", "af_sky", 0.2, who=(0.1, 1.3, -2.4), name="Machine", dur=1.5),
            say("My arms. Are. TINY.", REXV, 1.8, who=(0, 2.6, -3.6), name="Rex", dur=1.3)],
       stickers=[emoji("😭", 2.2, x=0.82, y=0.25)])
# 7 — back to now: the chase
s.beat(3.0, "which brings us *back* here", Set(park(seed=3, grass="#82c91e") + animate_all(dino((0, 0, 7.5), REX, size=1.6, face_you=False),
                                                                                         [{"type": "move", "to": [0, 0, -2.3], "rel": True}]),
                                               sky=SUNNY, ambient=1.5, light=2.6, sun_dir=(3, 9, -6)),
       cam((0, 1.5, 0.5), (0, 2.4, 9), to=(0, 1.5, -0.3), head="run"), hands="run", fx=["whip", "shake"],
       stickers=[meter("RUN", 0.4, 1.0, at=0.2, color="#ff6b6b")])
# 8 — twist: he just wanted to return your backpack
s.beat(3.4, "he just wanted to return your *backpack*", Set(park(seed=3, grass="#82c91e") + dino((0, 0, 6.2), REX, size=1.4, face_you=False) +
                                                            gift((0, 1.45, 4.9), "#4c6ef5", "#ffd43b", 0.45),
                                                            sky=SUNNY, ambient=1.6, light=2.6, sun_dir=(3, 9, -6)),
       cam((0, 1.4, -0.4), (0, 2.3, 6.2), fov=66), hands="reach", fx=["punch"],
       say=[say("You dropped this. Rawr.", REXV, 0.3, who=(0, 3.6, 5.3), name="Rex", speed=0.95)],
       stickers=[emoji("🥹", 1.4, x=0.8, y=0.3), badge("Which dinosaur would YOU ride to school? 👇", at=1.9, title="COMMENT BELOW", dur=1.5)])

s.save(tags=["what if dinosaurs never went extinct", "dinosaurs", "t rex", "what if", "pov", "funny", "alternative world", "dink dunk", "animation", "shorts"],
       description="Dinosaurs never died out. Your alarm clock bites, the school bus has a neck, and a T-rex is chasing you. 🦖\n\nWhich dinosaur would YOU ride to school? 👇\n\n#whatif #dinosaurs #funny",
       pinned="Which dinosaur would YOU ride to school? 👇")
