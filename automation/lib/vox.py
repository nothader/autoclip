"""Voxel format helpers (blocky world, live counter card, deadpan humour). See automation/RUNBOOK.md, "Voxel format".

Everything here is seeded: the same seed gives the same world, a new seed gives a new one. Variety comes from
  - ~290 voxel models in the renderer catalog (backend/whatif/web/voxel.js; MODELS below mirrors the names),
  - 40 biomes x random prop picks x 18 pastel skies,
  - seeded people: 15 hair styles x 14 hats x 10 outfits x 10 skins x 6 faces (~126,000 looks),
  - carpets: one model scattered up to 30,000 times in 6 colour variants.

    from vox import Vox, biome, person, crowd, carpet, prop, landmark, SKIES
    v = Vox(seed=7)
    v.B(3.2, "front", biome("beach", 7, extra=[carpet("gummy_bear", 4000)]), counter=v.C(0, 4000, "Gummy bears", "free", "Nobody asked where they came from."))
    v.save("gummy_ocean", "What if the ocean was made of gummy bears?", ...)

A voxel model's scale = its longest side in metres (a person is 1.8, a burger 0.12, the Eiffel Tower 330).
"""
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from props import O  # noqa: E402

_JS = Path(__file__).resolve().parents[2] / "backend" / "whatif" / "web" / "voxel.js"
MODELS = {n: f for n, f in re.findall(r'def\("([a-z0-9_]+)", "([a-z]+)"', _JS.read_text())}
FAMILIES = {}
for _n, _f in MODELS.items():
    FAMILIES.setdefault(_f, []).append(_n)

# Real sizes (longest side, metres) for comparisons: "the pile is now taller than ___".
LANDMARKS = {
    "statue_of_liberty": 93, "big_ben": 96, "leaning_tower": 56, "great_pyramid": 139, "space_needle": 184,
    "eiffel_tower": 330, "empire_state": 443, "burj_khalifa": 828, "cn_tower": 553, "christ_redeemer": 30,
    "colosseum": 189, "taj_mahal": 73, "opera_house": 183, "golden_gate": 2737, "mount_rushmore": 18, "stonehenge": 33,
}
LANDMARK_NAMES = {k: k.replace("_", " ").title().replace("Of", "of") for k in LANDMARKS}

# Typical sizes for everyday models (longest side, metres). Anything missing falls back by family.
SIZE = {"person": 1.8, "car": 4.5, "taxi": 4.5, "police_car": 4.8, "bus": 12, "truck": 9, "pickup": 5.5, "van": 5, "bicycle": 1.8,
        "scooter": 1.2, "motorbike": 2.1, "airplane": 40, "helicopter": 15, "boat": 6, "sailboat": 9, "cruise_ship": 300, "train": 25,
        "rocket": 70, "tractor": 4, "ambulance": 6, "fire_truck": 10, "submarine": 60, "hot_air_balloon": 20, "skateboard_car": 2,
        "whale": 25, "shark": 5, "elephant": 6, "giraffe": 5.5, "horse": 2.4, "cow": 2.4, "dinosaur": 12, "dog": 0.8, "cat": 0.5,
        "house": 10, "cottage": 9, "cabin": 8, "barn": 14, "apartment": 30, "skyscraper": 150, "glass_tower": 120, "stadium": 200,
        "castle": 40, "lighthouse": 25, "windmill": 20, "ferris_wheel": 60, "roller_coaster": 40, "pyramid": 60, "iceberg": 40,
        "volcano": 120, "hill": 60, "palm_tree": 9, "pine_tree": 12, "oak_tree": 10, "birch_tree": 10, "autumn_tree": 9, "cloud": 15}
FAMILY_SIZE = {"food": 0.15, "animal": 1.0, "vehicle": 4.5, "home": 1.2, "item": 0.3, "nature": 1.5, "building": 12,
               "landmark": 100, "toy": 0.4, "street": 1.0}


def size_of(model):
    return SIZE.get(model) or LANDMARKS.get(model) or FAMILY_SIZE.get(MODELS.get(model, ""), 1.0)


# Pastel skies (top, bottom). Pick a new one per video; novelty.py compares them.
SKIES = {
    "cotton": ["#8ec5ff", "#ffe3ec"], "peach": ["#ffb4a2", "#fff1e6"], "mint": ["#7fd8be", "#f1fff8"], "lilac": ["#b8a1ff", "#fdf0ff"],
    "lemon": ["#ffe066", "#fffbe6"], "sky": ["#74c0fc", "#e7f5ff"], "sunset": ["#ff8fab", "#ffd6a5"], "dawn": ["#a5b4fc", "#fde68a"],
    "bubblegum": ["#f783ac", "#fff0f6"], "sea": ["#66d9e8", "#e3fafc"], "dusk": ["#5f3dc4", "#ffa8a8"], "night": ["#1b2559", "#6c5ce7"],
    "storm": ["#748ffc", "#dee2e6"], "golden": ["#f59f00", "#fff3bf"], "arctic": ["#a5d8ff", "#ffffff"], "desert": ["#ffa94d", "#fff4e6"],
    "space": ["#12122b", "#3b2f6b"], "matcha": ["#a9e34b", "#f4fce3"],
}

# 40 biomes: ground colour, prop pool (models), ambience. biome() picks a seeded subset and scatters it.
BIOMES = {
    "beach": ("#f3d9a4", ["palm_tree", "beach_ball", "surfboard", "shell", "starfish", "sand_castle", "umbrella", "crab", "bucket", "shovel", "juice_box", "boat"], "ocean"),
    "city": ("#adb5bd", ["skyscraper", "glass_tower", "apartment", "taxi", "bus", "street_lamp", "traffic_light", "fire_hydrant", "bench", "mailbox", "shop", "car"], "calm"),
    "suburb": ("#8ce99a", ["house", "cottage", "oak_tree", "mailbox", "fence", "car", "bicycle", "dog", "trash_can", "basketball_hoop", "flower", "bush"], "calm"),
    "desert": ("#ffd8a8", ["cactus", "rock", "boulder", "pyramid", "snake", "tent", "pickup", "hill", "barrel", "sign"], "wind"),
    "snow": ("#f8f9fa", ["pine_tree", "snowman", "igloo", "penguin", "cabin", "iceberg", "lantern", "sign", "rock", "pine_tree"], "wind"),
    "forest": ("#69db7c", ["pine_tree", "oak_tree", "birch_tree", "mushroom_tree", "stump", "log", "fox", "bear", "owl", "rabbit", "mushroom", "bush"], "forest"),
    "autumn": ("#ffc078", ["autumn_tree", "autumn_tree", "stump", "log", "pumpkin" if "pumpkin" in MODELS else "orange", "rake" if "rake" in MODELS else "shovel", "bench", "squirrel" if "squirrel" in MODELS else "fox", "lantern", "bush"], "forest"),
    "kitchen": ("#fff4e6", ["fridge", "oven", "microwave", "toaster", "table", "chair", "coffee_cup", "pancakes", "toast", "fried_egg", "cereal_box", "trash_can"], "room"),
    "bedroom": ("#e5dbff", ["bed", "lamp", "bookshelf", "desk", "laptop", "rug", "teddy_bear", "wall_clock", "plant_pot", "sock", "mirror", "controller"], "room"),
    "living_room": ("#ffe8cc", ["sofa", "tv", "rug", "lamp", "plant_pot", "controller", "popcorn", "speaker", "bookshelf", "cat", "dog", "table"], "room"),
    "bathroom": ("#e3fafc", ["toilet", "bathtub", "mirror", "toothbrush", "toilet_paper", "rubber_duck", "plant_pot", "trash_can", "washing_machine"], "room"),
    "classroom": ("#ffec99", ["desk", "chair", "book", "pencil", "backpack", "wall_clock", "computer", "globe" if "globe" in MODELS else "trophy", "scissors", "trash_can", "apple"], "room"),
    "office": ("#dee2e6", ["desk", "computer", "laptop", "chair", "coffee_cup", "plant_pot", "keyboard", "wall_clock", "trash_can", "vending_machine"], "room"),
    "stadium": ("#51cf66", ["stadium", "soccer_goal", "soccer_ball", "football", "basketball_hoop", "trophy", "bench", "hot_dog", "soda_can", "speaker"], "calm"),
    "farm": ("#a9e34b", ["barn", "silo", "tractor", "cow", "pig", "sheep", "chicken", "horse", "fence", "windmill", "corn", "hut"], "forest"),
    "jungle": ("#2f9e44", ["palm_tree", "bamboo", "monkey", "parrot", "snake", "frog", "bush", "boulder", "hut", "pineapple", "banana", "treehouse"], "forest"),
    "island": ("#ffe3a3", ["palm_tree", "hut", "boat", "sailboat", "coral", "shell", "crab", "turtle", "pineapple", "lighthouse"], "ocean"),
    "underwater": ("#3bc9db", ["coral", "seaweed", "fish", "shark", "whale", "octopus", "jellyfish", "turtle", "submarine", "shell", "starfish", "dolphin"], "ocean"),
    "mall": ("#f1f3f5", ["shop", "vending_machine", "bench", "plant_pot", "bubble_tea", "sneaker", "backpack", "sunglasses", "smartphone", "headphones", "gift"], "room"),
    "subway": ("#868e96", ["train", "bench", "sign", "trash_can", "vending_machine", "street_lamp", "backpack", "smartphone", "coffee_cup"], "rumble"),
    "space_station": ("#495057", ["rocket", "robot", "drone", "computer", "battery", "light_bulb", "noodle_cup", "camera", "keyboard"], "space"),
    "moon": ("#ced4da", ["rocket", "rock", "boulder", "crystal_rock", "robot", "sign", "camera", "flag" if "flag" in MODELS else "sign"], "space"),
    "candyland": ("#ffdeeb", ["lollipop", "candy_cane", "cupcake", "donut", "cotton_candy", "gummy_bear", "ice_cream", "cake", "chocolate_bar", "cookie"], "calm"),
    "playground": ("#b2f2bb", ["trampoline", "basketball_hoop", "soccer_ball", "kite", "bench", "skateboard", "yoyo", "beach_ball", "oak_tree", "ice_cream"], "calm"),
    "park": ("#8ce99a", ["oak_tree", "bench", "flower", "tulip", "dog", "bicycle", "kite", "street_lamp", "trash_can", "ice_cream", "lily_pad"], "forest"),
    "river": ("#74c0fc", ["lily_pad", "frog", "duck", "boat", "bridge", "log", "rock", "fish", "bamboo", "bush"], "ocean"),
    "volcano": ("#5c3a21", ["volcano", "boulder", "rock", "crystal_rock", "dinosaur", "hill", "stump", "sign"], "rumble"),
    "arctic": ("#e7f5ff", ["iceberg", "penguin", "igloo", "snowman", "whale", "boat", "lantern", "rock"], "wind"),
    "gas_station": ("#ced4da", ["gas_station", "car", "pickup", "truck", "vending_machine", "trash_can", "street_lamp", "sign", "soda_can", "traffic_cone"], "calm"),
    "parking_lot": ("#868e96", ["car", "taxi", "van", "pickup", "police_car", "traffic_cone", "parking_meter", "street_lamp", "shopping_cart" if "shopping_cart" in MODELS else "dumpster"], "calm"),
    "airport": ("#dee2e6", ["airplane", "helicopter", "suitcase", "backpack", "sign", "bus", "traffic_cone", "coffee_cup", "vending_machine"], "rumble"),
    "harbor": ("#a5d8ff", ["cruise_ship", "boat", "sailboat", "crate", "barrel", "lighthouse", "fish", "truck", "ladder"], "ocean"),
    "castle": ("#94d82d", ["castle", "crown", "horse", "tent", "lantern", "barrel", "fence", "oak_tree", "chess_king"], "wind"),
    "ancient": ("#ffe8a1", ["pyramid", "temple", "great_pyramid", "colosseum", "boulder", "hut", "sign", "cactus", "gold_bar"], "wind"),
    "festival": ("#c0eb75", ["ferris_wheel", "roller_coaster", "tent", "balloon", "cotton_candy", "popcorn", "hot_dog", "speaker", "lantern", "gift"], "calm"),
    "bank": ("#f8f0fc", ["money_stack", "gold_bar", "coin", "gem", "crown", "trophy", "key", "desk", "computer"], "room"),
    "gym": ("#fff0f6", ["basketball", "trampoline", "bench", "sneaker", "juice_box", "speaker", "tennis_racket", "bowling_pin", "golf_ball"], "room"),
    "hospital": ("#e6fcf5", ["hospital", "ambulance", "bed", "computer", "plant_pot", "wall_clock", "vending_machine", "chair", "trash_can"], "room"),
    "rooftop": ("#adb5bd", ["water_tower", "hot_tub", "drone", "plant_pot", "chair", "speaker", "antenna" if "antenna" in MODELS else "street_lamp", "skyscraper", "glass_tower"], "wind"),
    "toy_room": ("#d0ebff", ["lego_brick", "rubiks_cube", "teddy_bear", "dice", "puzzle_piece", "robot", "rubber_duck", "fidget_spinner", "slime", "chess_king", "yoyo"], "room"),
}
BIOMES = {k: (g, [m for m in pool if m in MODELS], amb) for k, (g, pool, amb) in BIOMES.items()}


def prop(model, at=(0, 0, -4), size=None, color="#d8d8d8", seed=1, ry=0, anim=(), count=1, spread=(0, 0, 0)):
    """One voxel model; size = longest side in metres (defaults to its real size)."""
    assert model in MODELS, f"unknown voxel model {model!r}"
    return O("voxel", at, size or size_of(model), color, model=model, seed=seed, rotate=[0, ry, 0], animate=list(anim),
             count=count, spread=list(spread))


def landmark(name, at=(0, 0, -400), ry=0, anim=()):
    return prop(name, at, LANDMARKS[name], ry=ry, anim=anim)


def carpet(model, n=3000, at=(0, 0, -6), spread=(30, 0.4, 24), size=None, seed=3, color="#d8d8d8", anim=()):
    """Thousands of one model (6 colour variants). size = each item's size; default is its real size x2 so it reads on screen."""
    return O("carpet", at, size or max(0.12, size_of(model) * 2), color, model=model, n=n, spread=list(spread), seed=seed, animate=list(anim))


def person(at=(0, 0, -3), seed=1, act="idle", face="auto", ry=0, top=None, pants=None, size=1.8, anim=()):
    """A seeded voxel person (look comes from the seed; top/pants override clothes). ry=180 faces wide/follow cameras."""
    o = O("voxel_person", at, size / 1.8, top or "#d8d8d8", seed=seed, action=act, expression=face, rotate=[0, ry, 0], animate=list(anim))
    if pants:
        o["color2"] = pants
    return o


def crowd(n, seed, at=(0, 0, -8), spread=(14, 0, 8), act="walk", face="auto"):
    """n different-looking people (each one gets its own seed)."""
    return O("voxel_person", at, 1.0, "#d8d8d8", seed=seed, count=min(n, 200), spread=list(spread), action=act, expression=face)


def biome(name, seed, extra=(), n_props=10, area=(26, 18), center=(0, 0, -10), ground=None, keep_clear=3.0):
    """A seeded scene: ground + n_props picked from the biome's pool, scattered around center, leaving the front clear."""
    g, pool, _ = BIOMES[name]
    r = random.Random(seed * 1013 + len(name))
    objs = [O("box", (center[0], -0.05, center[2]), [area[0] * 3, 0.1, area[1] * 3], ground or g)]
    pool = [m for m in pool if size_of(m) <= 60] or pool   # giants (cruise ships, landmarks) only when added on purpose
    for i in range(n_props):
        m = r.choice(pool)
        for _ in range(20):
            x, z = (r.random() - 0.5) * area[0], center[2] - r.random() * area[1] / 2 - keep_clear
            if abs(x) > keep_clear or z < center[2] - keep_clear:
                break
        sz = size_of(m) * (0.8 + r.random() * 0.5)
        if sz > 20:   # big buildings go to the back
            z -= 10 + sz
        objs.append(prop(m, (round(x, 2), 0, round(z, 2)), round(sz, 3), seed=r.randint(2, 7), ry=r.randint(0, 359)))
    objs += list(extra)
    return objs[:40]


def ambience(name):
    return BIOMES[name][2] if name in BIOMES else "calm"


def env(objs, sky, focus=(0, 1.2, -4), zoom=1.4, amb="calm", light=2.5, ambient=1.7, fog=None):
    s = {"background": list(SKIES.get(sky, sky)) if isinstance(sky, str) else list(sky), "ground": "none", "focus": list(focus),
         "zoom": zoom, "ambience": amb, "light_intensity": light, "ambient": ambient, "bounce": "#f1e4d8", "objects": objs[:40]}
    if fog:
        s["fog"] = list(fog)
    return {"set": s}


class Vox:
    def __init__(self, seed=1):
        self.beats, self.seed = [], seed

    @staticmethod
    def C(frm, to, label, tag="", line="", unit="", tag_color="#e64980", decimals=0):
        """Counter card: the number counts from frm (None = previous beat's value) to to."""
        c = {"to": to, "label": label, "tag": tag, "line": line, "unit": unit, "tag_color": tag_color, "decimals": decimals}
        if frm is not None:
            c["from"] = frm
        return c

    def B(self, dur, cam, env_, caption="", counter=None, sfx=None, **k):
        b = {"duration": dur, "scene": "custom", "camera": cam, "subject": {"type": "none"}, "caption": caption or (counter or {}).get("line", ""),
             "env": env_}
        if counter:
            b["counter"] = counter
        if sfx:
            b["sfx"] = sfx
        b.update(k)
        self.beats.append(b)

    def save(self, name, title, premise, end, thumb, thumb_beat=1, accent="#e64980", voice="am_michael", speak_end=False):
        """Voxel defaults: voxel style, playful music, the narrator reads only the title (the cards carry the jokes)."""
        beats = [dict(b) for b in self.beats]
        for i, b in enumerate(beats):
            b["narration"] = title if i == 0 else ""
        sb = {"format": "timeline", "title": title, "premise": premise, "length": "quick",
              "intro": {"style": "none", "title": title}, "theme": {"style": "voxel", "accent": accent, "music": "playful", "captions": "line"},
              "outro": {"chart": False, "question_duration": 3.4, "end": {"kind": "question", "lines": end, "accent_line": 1}},
              "thumbnail": thumb, "thumbnail_beat": thumb_beat, "beats": beats,
              "narration": {"enabled": True, "engine": "kokoro", "voice": voice, "speed": 1.0, "read_title": False, "read_end": speak_end}}
        out = Path(sys.argv[0]).resolve().parent / f"{name}.json"
        out.write_text(json.dumps(sb, indent=1, ensure_ascii=False))
        print(out, len(beats))
