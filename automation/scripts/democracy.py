"""What if we didn't have democracy? — retention test with NARRATION: cold open, quick, toon (big box captions).
Neutral civics: Athens ~508 BC (about 2,500 years ago); for most of history kings/emperors ruled; rulers often for life,
power passed to their children; Magna Carta 1215 first limited an English king; in a democracy adults vote (US: age 18)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from props import O, S, house, trees

beats = []


def B(dur, cam, caption, env, **k):
    b = {"duration": dur, "scene": "custom", "camera": cam, "subject": {"type": "none"}, "caption": caption, "env": env}
    b.update(k)
    beats.append(b)


def V(objs, bg, focus=(0, 1.4, -4), zoom=1.6, amb="calm", **k):
    return S(objs, bg, ground="none", focus=focus, zoom=zoom, ambient=k.pop("ambient", 1.5), amb=amb, light=k.pop("light", 2.4))


GOLD = "#fab005"; ROYAL = "#7048e8"
king = lambda at=(0, 0.9, -6), act="point": [O("person", at, 1.1, ROYAL, outfit="robe", action=act, seed=5, color2="#e0ac69", rotate=[0, 180, 0]),
                                              O("cone", (at[0], at[1] + 2.15, at[2]), [0.32, 0.3, 0.32], GOLD, material="metal",
                                                animate=[{"type": "spin", "speed": 0.6}])]
throne_room = [O("box", (0, 0, -6), [14, 0.05, 16], "#8d6e57"), O("box", (0, 3.5, -12), [14, 7, 0.1], "#c92a2a"),
               O("box", (0, 0.03, -4), [2.4, 0.03, 12], "#e03131"), O("box", (0, 0.45, -6), [1.6, 0.9, 1.2], GOLD, material="metal"),
               O("box", (0, 1.6, -6.6), [1.6, 2.2, 0.2], GOLD, material="metal"), O("flame", (-5, 2.6, -11.6), 0.5, "#ff922b"), O("flame", (5, 2.6, -11.6), 0.5, "#ff922b")]
bowing = O("person", (0, 0, -1), 1.0, "#868e96", count=10, seed=3, spread=[9, 0, 4], action="kneel")
town = [O("box", (0, -0.02, -10), [50, 0.04, 50], "#c2a878"), O("tree", (0, 0, -24), 1.5, "#4f7a3a", count=10, seed=4, spread=[50, 0, 8])] + \
       house((-8, 0, -16), "#e9dcc9", "#7a4a3a") + house((8, 0, -16), "#ffe8cc", "#5c3d2e") + house((0, 0, -20), "#dbe4ff", "#495057")
crowd = lambda act="idle", n=16, seed=6: O("person", (0, 0, -6), 1.0, count=n, seed=seed, spread=[14, 0, 8], action=act)
SKY = ["#4dabf7", "#d0ebff"]; WARM = ["#ff922b", "#ffe8cc"]; INSIDE = ["#5f3dc4", "#9775fa"]

# 0 — cold open: one man on a throne, everyone kneeling
B(3.6, "follow", "Imagine one person ruling your country. Forever. And you can't vote.", V(throne_room + king(act="point") + [bowing], INSIDE, focus=(0, 1.6, -6), zoom=1.3, amb="room"),
  effects=["rays"], sfx=[{"type": "boom", "at": 0.2, "gain": 0.6}])
B(3.4, "wide", "That was normal for most of history. But one city changed it.", V(throne_room + king(act="idle") + [bowing], INSIDE, zoom=2.2, amb="room"))
# Athens
temple = [O("box", (0, -0.02, -10), [50, 0.04, 50], "#e9dcc9"), O("box", (0, 0.5, -14), [16, 1, 8], "#f1f3f5"),
          O("cylinder", (-6, 3.5, -11), [0.6, 5, 0.6], "#f8f9fa", count=7, seed=1, spread=[12, 0, 0]), O("box", (0, 6.3, -14), [16, 0.8, 8], "#f1f3f5"),
          O("cone", (0, 7.4, -14), [11, 1.6, 6], "#f8f9fa", rotate=[0, 45, 0]), crowd("point", 14, 2),
          O("cylinder", (0, 0.5, -4), [0.5, 1, 0.5], "#c97a40", animate=[{"type": "pulse", "amount": 0.2, "speed": 1.5}])]
B(3.6, "establishing", "2,500 years ago, Athens tried something new: voting.", V(temple, SKY, focus=(0, 3, -10), zoom=2.6), transition="whip",
  chapter="The Big Idea", stat={"value": "~508 BC", "label": "DEMOCRACY STARTS IN ATHENS", "count_up": False})
# without it
B(3.4, "wide", "But what if that idea never spread? No elections. Ever.", V(town + [crowd("idle", 12, 8), O("box", (0, 0.6, -2), [0.8, 1.2, 0.8], "#495057",
  animate=[{"type": "shrink"}])], WARM, focus=(0, 1.2, -3), zoom=1.4), chapter="No Democracy", transition="dip")
B(3.4, "dolly", "The ruler stays in charge for life. Then their kid takes over.", V(throne_room + king((-0.8, 0.9, -6), "idle") +
  [O("person", (1.2, 0, -5), 0.7, ROYAL, outfit="child", action="point", seed=7, color2="#e0ac69", rotate=[0, 180, 0])], INSIDE, focus=(0, 1.4, -6), zoom=1.2, amb="room"))
herald = [O("person", (0, 1.2, -9), 1.0, "#c92a2a", outfit="robe", action="point", seed=4, color2="#c68642"), O("box", (0, 0.6, -9), [3, 1.2, 2], "#8d6e57"),
          O("box", (0.6, 2.3, -8.6), [0.6, 0.8, 0.05], "#fff3bf", animate=[{"type": "wobble", "amount": 0.2, "speed": 2}])]
B(3.4, "wide", "New laws? One person decides. Nobody asks you.", V(town + herald + [crowd("idle", 14, 9)], WARM, zoom=2), transition="whip",
  banner={"kicker": "ROYAL ORDER", "title": "NEW TAX: DOUBLED", "subtitle": "BY ORDER OF THE KING"})
jail = [O("box", (0, 0, -4), [8, 0.05, 8], "#495057"), O("box", (0, 1.5, -7), [8, 3, 0.1], "#868e96"),
        O("cylinder", (-3, 1.5, -1), [0.08, 3, 0.08], "#343a40", material="metal", count=12, seed=1, spread=[6, 0, 0]),
        O("person", (0, 0, -4), 1.0, "#adb5bd", action="sit", seed=8, color2="#c68642")]
B(3.4, "follow", "Complain about the king? In many kingdoms, that meant jail.", V(jail, ["#343a40", "#868e96"], focus=(0, 1.2, -3), zoom=1.1, amb="room"),
  effects=["darken"], sfx=[{"type": "impact", "at": 0.4, "gain": 0.8}])
# Magna Carta → today
B(3.4, "follow", "The twist: in 1215, nobles made England's king obey the law.", V(throne_room + king((0, 0.9, -6), "idle") +
  [O("box", (0.8, 1.4, -5.2), [0.6, 0.8, 0.04], "#fff3bf", rotate=[0, -20, 0])], INSIDE, focus=(0, 1.8, -6), zoom=0.8, amb="room"), chapter="The Twist",
  stat={"value": "1215", "label": "THE MAGNA CARTA", "count_up": False})
booth = [O("box", (0, 0, -6), [16, 0.05, 14], "#dee2e6"), O("box", (0, 2.5, -12), [16, 5, 0.1], "#e7f5ff"),
         O("box", (-4, 1.0, -9), [1.4, 2.0, 1.4], "#4dabf7", count=4, seed=2, spread=[10, 0, 0]),
         O("box", (2, 0.55, -4), [1.0, 1.1, 1.0], "#f8f9fa"), O("box", (2, 1.12, -4), [0.5, 0.03, 0.06], "#212529"),
         O("box", (2, 1.6, -4), [0.4, 0.5, 0.02], "#ffffff", animate=[{"type": "move", "to": [2, 1.14, -4]}]),
         O("person", (0, 0, -7), 1.0, count=8, seed=11, spread=[10, 0, 4], action="walk")]
B(3.6, "dolly", "That idea grew. Today, in a democracy, you get a vote at 18.", V(booth, ["#e7f5ff", "#a5d8ff"], focus=(1, 1.2, -5), zoom=1.2, amb="room"),
  effects=["confetti"])
B(3.6, "wide", "Without it, you'd get zero votes. For your whole life.", V(throne_room + king(act="point") + [bowing], INSIDE, zoom=2.4, amb="room"),
  transition="dip", effects=["darken"])

sb = {"format": "story", "title": "What if democracy never existed?",
      "premise": "A neutral history explainer: kings and emperors ruled most of history; what life looks like with no voting at all.",
      "length": "quick", "intro": {"style": "none", "title": "What if *democracy* never existed?"},
      "narration": {"enabled": True, "engine": "kokoro", "voice": "am_michael", "speed": 1.2, "read_end": True},
      "theme": {"style": "toon", "accent": "#7048e8"},
      "outro": {"chart": False, "question_duration": 3.4, "end": {"kind": "question", "lines": ["WOULD YOU", "WANT A KING?"], "accent_line": 1}},
      "thumbnail": "NO *VOTES*. EVER.", "thumbnail_beat": 0, "beats": beats}
out = Path(__file__).parent / "democracy.json"
out.write_text(json.dumps(sb, indent=1, ensure_ascii=False))
print(out, len(beats))
