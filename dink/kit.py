"""Story kit: write a DinkCam video as Python.

    s = Story("wolves", accent="#ffd43b", hook=["WHAT IF YOU WERE", "RAISED BY", "WOLVES?"], hook_accent=2)
    s.beat(3.0, "your mom has *four* legs", Set(objs, sky=NIGHT), cam=cam((0, 1.0, 1.4), (0, 0.8, -2)), hands="reach",
           say=[say("Eat your rabbit, sweetie", "af_heart", 0.4, who=(0, 1.2, -2), name="Mom")],
           stickers=[badge("Raised by wolves", at=1.0)], fx=["punch"])
    s.save()
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# skies (top, bottom)
DAY = ["#5aa9ff", "#d8efff"]; SUNNY = ["#3d8bfd", "#fff1c1"]; DUSK = ["#3a2d6b", "#ff9a6b"]; NIGHT = ["#0b1230", "#2b3b6b"]
DAWN = ["#6b7fd6", "#ffd1a8"]; INDOOR = ["#2a2433", "#4a3f55"]; MINT = ["#7ee8c8", "#effff9"]; CANDY = ["#ff8fc7", "#ffe3f1"]
STORM = ["#3b4252", "#8a94a6"]; SPACE = ["#05030f", "#1b1440"]; DEEP = ["#03243b", "#0a6c8f"]; SNOWY = ["#9fb7d1", "#f3f7fb"]


def Set(objects, sky=DAY, ambient=1.3, light=2.4, bounce="#8a7a6a", sun_dir=(4, 9, 5), fog=None, sun_color="#fff3df", sky_light="#ffffff"):
    objs = [o for o in objects if o]
    if len(objs) > 60:
        raise ValueError(f"too many objects in one shot: {len(objs)} (max 60)")
    d = {"objects": objs, "sky": list(sky), "ambient": ambient, "light": light, "bounce": bounce, "sunDir": list(sun_dir),
         "sunColor": sun_color, "skyLight": sky_light}
    if fog:
        d["fog"] = list(fog)
    return d


def cam(pos=(0, 1.55, 1.6), look=(0, 1.2, -3), to=None, look_to=None, head="breathe", fov=None):
    c = {"pos": list(pos), "look": list(look), "head": head}
    if to:
        c["to"] = list(to)
    if look_to:
        c["lookTo"] = list(look_to)
    if fov:
        c["fov"] = fov
    return c


def say(text, voice="am_michael", at=0.3, who=None, name="", speed=1.0, dur=None, color=None):
    """A spoken line: a speech bubble (anchored at world point `who`) + a TTS voice."""
    b = {"text": text, "at": at, "dur": dur or max(1.4, 0.36 + 0.065 * len(text)), "voice": voice, "speed": speed}
    if who is not None:
        b["who"] = list(who)
    if name:
        b["name"] = name
    if color:
        b["color"] = color
    return b


def badge(text, at=0.6, title="ACHIEVEMENT UNLOCKED", dur=1.8):
    return {"kind": "badge", "text": text, "title": title, "at": at, "dur": dur}


def stamp(text, at=0.8, color="#ff3b5c", x=0.5, y=0.42, rot=-10, size=170, dur=1.4):
    return {"kind": "stamp", "text": text, "at": at, "color": color, "x": x, "y": y, "rot": rot, "size": size, "dur": dur}


def floaty(text, at=0.5, color="#69db7c", x=0.5, y=0.4, size=64, dur=1.4):
    return {"kind": "float", "text": text, "at": at, "color": color, "x": x, "y": y, "size": size, "dur": dur}


def label(text, who=None, at=0.4, side="right", color="#ffffff", x=0.5, y=0.5, dur=2.0):
    d = {"kind": "label", "text": text, "at": at, "side": side, "color": color, "x": x, "y": y, "dur": dur}
    if who is not None:
        d["who"] = list(who)
    return d


def emoji(ch, at=0.5, x=0.8, y=0.3, size=200, dur=1.6):
    return {"kind": "emoji", "text": ch, "at": at, "x": x, "y": y, "size": size, "dur": dur}


def meter(text, frm=0.0, to=1.0, at=0.2, color=None, y=0.13, dur=None):
    d = {"kind": "meter", "text": text, "from": frm, "to": to, "at": at, "y": y}
    if color:
        d["color"] = color
    if dur:
        d["dur"] = dur
    return d


class Story:
    def __init__(self, slug, title="", accent="#ffd43b", hook=(), hook_accent=-1, hook_dur=2.6, skin="#f1c27d", sleeve="#4c6ef5",
                 landscape=False, music_seed=None, mood="bouncy"):
        self.slug, self.title, self.accent = slug, title, accent
        self.hook = {"lines": list(hook), "accent": hook_accent} if hook else None
        self.hook_dur = hook_dur
        self.you = {"skin": skin, "sleeve": sleeve}
        self.w, self.h = (1920, 1080) if landscape else (1080, 1920)
        self.beats = []
        self.music_seed = music_seed if music_seed is not None else (sum(map(ord, slug)) % 997)
        self.mood = mood
        self.meta = {}

    def beat(self, dur, caption, set_, cam=None, hands="idle", hold=None, say=(), stickers=(), sfx=(), fx=(), freeze=None, tint=None):
        b = {"dur": dur, "caption": caption, "set": set_, "cam": cam or {}, "hands": hands, "bubbles": list(say),
             "stickers": list(stickers), "sfx": list(sfx), "fx": list(fx)}
        if hold:
            b["hold"] = hold
        if freeze:
            b["freeze"] = freeze
        if tint:
            b["tint"] = tint
        self.beats.append(b)
        return b

    def save(self, out_dir=None, **meta):
        t = 0.0
        for b in self.beats:
            b["t0"] = round(t, 4)
            t += b["dur"]
        self.meta.update(meta)
        d = {"slug": self.slug, "title": self.title, "accent": self.accent, "hook": self.hook, "hookDur": self.hook_dur,
             "you": self.you, "width": self.w, "height": self.h, "duration": round(t, 4), "beats": self.beats,
             "music": {"seed": self.music_seed, "mood": self.mood}, "meta": self.meta}
        out = Path(out_dir or ROOT / "stories") / f"{self.slug}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(d, indent=1, ensure_ascii=False))
        print(out, len(self.beats), "beats", round(t, 1), "s")
        return out
