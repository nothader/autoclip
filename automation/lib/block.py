"""Block POV format helpers (the @weirdsecret_ style). See automation/STYLE_BLOCK_POV.md.

    from block import Story, O, env, guy, crowd, T
    s = Story()
    s.B(3.4, "eyes", "The doors close. Floor 34.", env(objs, NIGHT, eye=(0, 1.62, 0.6)), tracker=T("FRIDAY · NEW YORK", clock="11:02:14 PM"),
        hands={"pose": "idle"}, voices=[("See you Monday!", "af_bella")])
    s.save("elevator", "What if you got stuck in an *elevator*?", "...", "Would you climb out, or wait?")

Rules the format lives by: no narrator (people in the scene talk instead), second-person italic captions of 3-9 words,
a left tracker that ticks (clock / count / day), a title only in the first 3.5 s, a black end card with a gold question.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from props import O  # noqa: E402,F401

# Skies (top, bottom): pick per scene, keep them believable (this format is cinematic, not pastel).
NIGHT = ["#0b1020", "#26324a"]; DUSK = ["#2c2a4a", "#e08a5f"]; DAWN = ["#5c6f9e", "#f4c9a0"]; DAY = ["#5d86ad", "#d7e3ea"]
OVERCAST = ["#6f7a86", "#c4cad0"]; GOLDEN = ["#3c4f7a", "#f2b066"]; INDOOR = ["#1c1f26", "#3a3f48"]
SKINS = ["#f1c27d", "#e0ac69", "#c68642", "#8d5524", "#5c3a21", "#ffdbac", "#d4a373", "#a0522d"]


def T(label="", value="", sub="", clock=None, rate=1.0, count=None, unit="", decimals=0, alert=False, big=False, scramble=False, prefix=""):
    """Tracker. clock="11:02:14 PM" ticks (rate = sim seconds per real second); count=(from, to) eases; value = fixed text."""
    t = {"label": label, "value": value, "sub": sub, "alert": alert, "big": big, "scramble": scramble}
    if clock:
        t["clock"], t["clock_rate"] = clock, rate
    if count is not None:
        t["count_from"], t["count_to"], t["unit"], t["decimals"], t["prefix"] = count[0], count[1], unit, decimals, prefix
    return t


def guy(at, top=None, pants=None, act="idle", face="auto", seed=1, ry=0, anim=()):
    """A block person (drawn face). Faces −z by default; ry=180 faces +z (toward wide/follow cameras)."""
    o = O("block_person", at, 1.0, top or "#d8d8d8", seed=seed, action=act, expression=face, rotate=[0, ry, 0], animate=list(anim))
    if pants:
        o["color2"] = pants
    return o


def crowd(n, seed, at=(0, 0, -8), spread=(12, 0, 6), act="walk", face="auto", ry=0):
    return O("block_person", at, 1.0, "#d8d8d8", seed=seed, count=min(n, 200), spread=list(spread), action=act, expression=face,
             rotate=[0, ry, 0])


def env(objs, sky, focus=(0, 1.5, -3), zoom=1.0, eye=None, amb="room", light=2.3, ambient=1.3, bounce="#cfc6b8", fog=None, stars=False):
    """eye=(x, y, z): for camera "eyes" the set's focus is YOUR eye position (you look toward −z). stars=True only for open night skies."""
    s = {"background": list(sky), "sky_detail": "auto" if stars else "none", "ground": "none", "focus": list(eye or focus), "zoom": zoom, "ambience": amb,
         "light_intensity": light, "ambient": ambient, "bounce": bounce, "objects": list(objs)[:40]}
    if fog:
        s["fog"] = list(fog)
    return {"set": s}


class Story:
    def __init__(self):
        self.beats = []

    def B(self, dur, cam, caption, env_, tracker=None, voices=(), by="", hands=None, head=None, gaze=None, gaze_to=None, **k):
        b = {"duration": dur, "scene": "custom", "camera": cam, "subject": {"type": "none"}, "caption": caption, "env": env_}
        if tracker:
            b["tracker"] = tracker
        if by:
            b["caption_by"] = by
        vl = []
        for v in voices:   # ("text", "voice") or ("text", "voice", at)
            vl.append({"text": v[0], "voice": v[1] if len(v) > 1 else "am_michael", "at": v[2] if len(v) > 2 else 0.3})
        if vl:
            b["voices"] = vl
        if cam == "eyes":
            b["hands"] = hands or {"pose": "none"}
            b["head"] = head or "breathe"
        if gaze is not None:
            b["gaze"] = list(gaze)
        if gaze_to is not None:
            b["gaze_to"] = list(gaze_to)
        b.update(k)
        self.beats.append(b)

    def save(self, name, title, premise, question, skin="#e0ac69", sleeve="#2b2f36", accent="#ff922b", music="tender",
             thumb="", thumb_beat=0):
        """title: mark the key word with *stars* ("What if you got stuck in an *elevator*?")."""
        plain = title.replace("*", "")
        sb = {"format": "pov", "title": plain, "premise": premise, "length": "standard",
              "intro": {"style": "none", "title": title},
              "pov": {"text": "", "skin": skin, "sleeve": sleeve, "hand_style": "block", "open_eyes": False},
              "theme": {"style": "block", "accent": accent, "music": music},
              "outro": {"chart": False, "question_duration": 4.0, "end": {"kind": "question", "lines": [question]}},
              "thumbnail": thumb or plain.upper(), "thumbnail_beat": thumb_beat, "beats": self.beats}
        out = Path(sys.argv[0]).resolve().parent / f"{name}.json"
        out.write_text(json.dumps(sb, indent=1, ensure_ascii=False))
        print(out, len(self.beats), round(sum(b["duration"] for b in self.beats), 1), "s")
