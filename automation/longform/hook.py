"""8-second DANGER HOOK cold open for the swap long-form (from the reference video's playbook):
start mid-story at the most dangerous moment (Alex, in Maya's body, wobbling on a chair), then glitch-rewind to the night before."""
from pathlib import Path
here = Path(__file__).parent
src = (here / "swap24.py").read_text().split("# ======================================================================= HOOK")[0]
exec(src)

chair_wobble = [{"type": "wobble", "axis": "z", "amount": 0.55, "speed": 2.6}]
scene = kitchen([O("box", (-3, 0.45, -10.4), [0.6, 0.9, 0.6], "#8d6e57", animate=chair_wobble)] +
                [body("M", (-3, 0.9, -10.4), "point", 0, anim=chair_wobble), halo((-3, 0.9, -10.4), HALO_A, 2.02, anim=chair_wobble)] +
                mind("M", (1.5, 0, -8), "point", 270))
B("follow", "This is Alex. He's about to fall off a chair. And he's in his wife's body.",
  V(scene, MORNING, focus=(-2.4, 1.7, -10), zoom=0.75, bounce="#fff3bf"), "6:16 AM", chapter="Cold Open",
  cap="This is Alex. He's about to fall... in his WIFE'S body.", move="push_in", effects=["shake", "tunnel"],
  sfx=[{"type": "crack", "at": 0.6, "gain": 0.7}, {"type": "crack", "at": 1.9, "gain": 0.8}, {"type": "heartbeat", "at": 0.2, "dur": 3.2, "gain": 0.7}])
B("closeup", "How did he end up in there? Let's go back to the night before.",
  V(scene, MORNING, focus=(-3, 2.2, -10.4), zoom=0.55, bounce="#fff3bf"), "REWIND", transition="glitch", effects=["glitch"],
  cap="How did he end up in there? Rewind.", sfx=[{"type": "glitch", "at": 0.1, "gain": 0.9}, {"type": "whoosh", "at": 0.3, "dur": 1.6, "gain": 0.8}])

sb = {"format": "story", "title": "What if men and women swapped bodies for a day? (hook)", "premise": "Cold open.",
      "width": 1920, "height": 1080,
      "narration": {"enabled": True, "engine": "kokoro", "voice": "am_michael", "speed": 1.05, "read_title": False, "read_end": False},
      "intro": {"style": "none", "title": "What if men and women *swapped bodies* for a day?"},
      "theme": {"style": "calm", "accent": "#f06595"}, "clock": {"mode": "none"},
      "outro": {"chart": False, "question_duration": 2.0, "end": {"kind": "question", "lines": ["X", "Y"], "accent_line": 1}},
      "beats": beats}
out = here / "hook.json"
out.write_text(json.dumps(sb, indent=1, ensure_ascii=False))
print(out, len(beats))
