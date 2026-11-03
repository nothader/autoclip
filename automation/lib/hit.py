"""The 'swap' recipe (41K-view hit) for every video: everyone watching is in the story, a 3-2-1 countdown cold open,
everyday funny details, ~30-35 s, big word captions, and an end question people argue about."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from props import O, S, trees, house  # noqa: F401

SKY = ["#4a8fd1", "#cfe3f3"]; GOLD = ["#2f4b7c", "#f4a259"]; DUSK = ["#2b2d52", "#e07a5f"]; PINK = ["#9c36b5", "#ffc9de"]
BOY, GIRL = "#1c7ed6", "#e64980"


class Video:
    def __init__(self):
        self.beats = []

    def B(self, dur, cam, caption, env, t, sub="", **k):
        b = {"duration": dur, "scene": "custom", "camera": cam, "subject": {"type": "none"}, "caption": caption, "env": env, "time": t, "time_sub": sub}
        b.update(k)
        self.beats.append(b)

    def save(self, name, title, premise, style, label, end, thumb, thumb_beat=1, accent="#ffa94d", palette=None, captions="words",
             narrate=True, music="dark", voice="am_onyx"):
        theme = {"style": style, "accent": accent, "music": music}   # outlier formula: dark music bed ~10-15% under the voice
        if captions:
            theme["captions"] = captions
        if palette:
            theme["palette"] = palette
        sb = {"format": "timeline", "title": title, "premise": premise, "length": "quick",
              "intro": {"style": "none", "title": title.replace("What if ", "What if *", 1).rstrip("?") + "*?"},
              "theme": theme, "clock": {"mode": "elapsed", "label": label, "intro_label": "IT HAPPENS IN", "intro_from": 3},
              "outro": {"chart": False, "question_duration": 3.4, "end": {"kind": "question", "lines": end, "accent_line": 1}},
              "thumbnail": thumb, "thumbnail_beat": thumb_beat, "beats": self.beats}
        if narrate:   # outlier formula: deep, serious narrator talking to "you"
            sb["narration"] = {"enabled": True, "engine": "kokoro", "voice": voice, "speed": 1.0, "read_title": False, "read_end": True}
        out = Path(sys.argv[0]).resolve().parent / f"{name}.json"   # 写在调用脚本旁边
        out.write_text(json.dumps(sb, indent=1, ensure_ascii=False))
        print(out, len(self.beats))


def V(objs, bg, focus=(0, 1.3, -4), zoom=1.4, amb="calm", bounce=None, **k):
    e = S(objs, bg, ground="none", focus=focus, zoom=zoom, ambient=k.pop("ambient", 1.5), amb=amb, light=k.pop("light", 2.4))
    if bounce:
        e["set"]["bounce"] = bounce
    return e


def P(at, col, act="idle", seed=1, outfit="casual", ry=0, s=1.0, anim=(), skin=None):
    return O("person", at, s, col, outfit=outfit, action=act, seed=seed, color2=skin or ["#8d5524", "#c68642", "#e0ac69", "#f1c27d", "#5c3a21"][seed % 5],
             rotate=[0, ry, 0], animate=list(anim))


def crowd(n, seed, col=None, at=(0, 0, -8), spread=(16, 0, 10), act="walk", outfit="casual"):
    return O("person", at, 1.0, col or "#d8d8d8", outfit=outfit, count=n, seed=seed, spread=list(spread), action=act)


def room(wall="#fff3bf", floor="#c9a27a", win="#a5d8ff", w=10, d=10, extra=()):
    return [O("box", (0, 0, -d / 2), [w, 0.05, d], floor), O("box", (0, 1.6, -d), [w, 3.2, 0.1], wall),
            O("box", (-w / 2, 1.6, -d / 2), [0.1, 3.2, d], wall), O("box", (w / 2, 1.6, -d / 2), [0.1, 3.2, d], wall),
            O("plane", (w / 4, 1.8, -d + 0.07), [2.2, 1.3, 1], win, material="glow")] + list(extra)


def school(extra=()):
    return [O("box", (0, -0.02, -14), [60, 0.04, 50], "#ced4da"), O("box", (0, 0.01, -10), [4, 0.02, 40], "#f1f3f5"),
            O("box", (-6, 1.6, -12), [0.3, 3.2, 30], "#74c0fc"), O("box", (-5.8, 1.1, -12), [0.5, 2.0, 0.6], "#4dabf7", count=14, seed=3, spread=[0, 0, 26]),
            O("box", (6, 1.6, -12), [0.3, 3.2, 30], "#ffd8a8"),
            O("box", (0, 3.18, -12), [0.6, 0.03, 1.2], "#ffffff", material="glow", count=8, seed=4, spread=[0, 0, 26])] + list(extra)


def park(extra=()):
    return [O("box", (0, -0.02, -14), [80, 0.04, 60], "#69a84f"), O("box", (0, 0, -10), [4, 0.03, 60], "#c2a878"),
            O("tree", (0, 0, -20), 1.6, "#3f8f3a", count=14, seed=3, spread=[50, 0, 20])] + list(extra)


def city(extra=()):
    return [O("box", (0, -0.02, -20), [120, 0.04, 100], "#868e96"), O("box", (0, 0, -16), [8, 0.03, 100], "#495057"),
            O("building", (-18, 0, -30), 5, "#d6cfc4", count=10, seed=3, spread=[4, 0, 40]), O("building", (18, 0, -30), 5, "#c9b8a6", count=10, seed=7, spread=[4, 0, 40])] + list(extra)
