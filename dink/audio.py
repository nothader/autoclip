"""DinkCam audio: synthesized comedy SFX, a bouncy generated music bed, Kokoro TTS voices, and the final mix."""
import hashlib
import os
import wave
from pathlib import Path

import numpy as np

SR = 44100
CACHE = Path(os.environ.get("DINK_TTS_CACHE", Path.home() / ".cache" / "dinkcam" / "tts"))
MODEL_DIRS = [CACHE, Path.home() / ".cache" / "autoclip" / "tts"]


def _t(d):
    return np.arange(int(SR * d)) / SR


def _env(n, a=0.005, r=0.1):
    e = np.ones(n)
    na, nr = int(SR * a), int(SR * r)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def _noise(n, seed=0):
    return np.random.default_rng(seed).uniform(-1, 1, n)


def _lp(x, k=0.1):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)):
        acc += k * (x[i] - acc); y[i] = acc
    return y


# ───────── SFX ─────────
def sfx_whoosh(d=0.35):
    n = int(SR * d); x = _noise(n, 1)
    f = np.linspace(0.02, 0.25, n)
    y = np.zeros(n); acc = 0.0
    for i in range(n):
        acc += f[i] * (x[i] - acc); y[i] = acc
    return y * np.sin(np.linspace(0, np.pi, n)) * 0.7


def sfx_pop(d=0.09):
    t = _t(d); return np.sin(2 * np.pi * (900 - 5000 * t) * t) * np.exp(-t * 40) * 0.6


def sfx_boing(d=0.5):
    t = _t(d); f = 180 + 120 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 4)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.6


def sfx_ding(d=0.8):
    t = _t(d); return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1976 * t)) * np.exp(-t * 5) * 0.35


def sfx_achievement(d=0.7):
    out = np.zeros(int(SR * d))
    for i, f in enumerate([784, 988, 1175, 1568]):
        t = _t(0.25); s = int(SR * i * 0.08)
        tone = np.sign(np.sin(2 * np.pi * f * t)) * 0.12 * np.exp(-t * 9)
        out[s:s + len(tone)] += tone[: len(out) - s]
    return out


def sfx_scratch(d=0.45):
    t = _t(d); x = _noise(len(t), 3)
    f = 300 + 1600 * np.abs(np.sin(2 * np.pi * 4 * t))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return (0.5 * x * tone + 0.3 * tone) * _env(len(t), 0.002, 0.08) * 0.6


def sfx_slam(d=0.4):
    t = _t(d); return (np.sin(2 * np.pi * 60 * t) * 1.0 + _noise(len(t), 4) * 0.4 * np.exp(-t * 30)) * np.exp(-t * 9) * 0.9


def sfx_thud(d=0.3):
    t = _t(d); return np.sin(2 * np.pi * (90 - 60 * t) * t) * np.exp(-t * 14) * 0.9


def sfx_sparkle(d=0.6):
    out = np.zeros(int(SR * d)); rng = np.random.default_rng(5)
    for i in range(9):
        f = rng.uniform(2000, 4200); s = int(SR * i * 0.055); t = _t(0.15)
        out[s:s + len(t)] += np.sin(2 * np.pi * f * t) * np.exp(-t * 30) * 0.12
    return out


def sfx_fail(d=1.0):   # sad trombone
    out = np.zeros(int(SR * d))
    for i, f in enumerate([392, 370, 349, 330]):
        dd = 0.22 if i < 3 else 0.5; t = _t(dd); s = int(SR * i * 0.24)
        wob = f * (1 + (0.02 * np.sin(2 * np.pi * 6 * t) if i == 3 else 0))
        tone = np.sin(2 * np.pi * np.cumsum(wob) / SR); tone = np.tanh(2.5 * tone) * _env(len(t), 0.01, 0.06) * 0.25
        out[s:s + len(tone)] += tone[: len(out) - s]
    return out


def sfx_gasp(d=0.6):
    n = int(SR * d); x = _lp(_noise(n, 6), 0.25)
    return x * np.sin(np.linspace(0, np.pi, n)) ** 0.5 * np.linspace(1, 0.3, n) * 0.8


def sfx_crowd(d=1.6):   # cheer / laugh bed
    n = int(SR * d); x = _lp(_noise(n, 7), 0.18); m = 0.6 + 0.4 * np.sin(2 * np.pi * 7 * _t(d))
    return x * m * _env(n, 0.15, 0.5) * 0.7


def sfx_tick(d=0.05):
    t = _t(d); return np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 120) * 0.4


def sfx_bonk(d=0.25):
    t = _t(d); return (np.sin(2 * np.pi * 520 * t) + 0.6 * np.sin(2 * np.pi * 780 * t)) * np.exp(-t * 22) * 0.5


def sfx_howl(d=1.8):
    t = _t(d); f = 420 + 260 * np.sin(np.pi * t / d) + 8 * np.sin(2 * np.pi * 5 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) * 0.25


def sfx_riser(d=1.2):
    t = _t(d); f = 200 * (8 ** (t / d))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + _lp(_noise(len(t), 8), 0.3) * 0.25) * (t / d)


def sfx_alarm(d=1.2):   # smoke-alarm beeps
    t = _t(d); gate = (np.floor(t * 6) % 2 == 0).astype(float)
    return np.sign(np.sin(2 * np.pi * 3100 * t)) * gate * 0.12


def sfx_doorbell(d=1.2):   # ding-dong
    t = _t(d); a = np.sin(2 * np.pi * 659 * t) * np.exp(-t * 3) * (t < 0.6)
    t2 = np.clip(t - 0.45, 0, None); b2 = np.sin(2 * np.pi * 523 * t2) * np.exp(-t2 * 3) * (t >= 0.45)
    return (a + b2) * 0.35


def sfx_notify(d=0.3):   # phone message ping
    t = _t(d); return (np.sin(2 * np.pi * 1320 * t) * (t < 0.12) + np.sin(2 * np.pi * 1760 * t) * (t >= 0.12)) * np.exp(-t * 9) * 0.35


SFX = {k[4:]: v for k, v in globals().items() if k.startswith("sfx_")}


# ───────── music ─────────
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)


def _pluck(f, d, seed=0, damp=0.996):
    n = int(SR * d); p = max(2, int(SR / f))
    buf = np.random.default_rng(seed).uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = damp * 0.5 * (buf[i % p] + buf[(i + 1) % p])
    return out


def music(duration, seed=1, mood="bouncy"):
    rng = np.random.default_rng(seed)
    bpm = {"bouncy": 118, "chill": 92, "sneaky": 100, "epic": 128}.get(mood, 112) + int(rng.integers(-6, 7))
    beat = 60 / bpm
    key = 57 + int(rng.integers(0, 7))
    progs = {"bouncy": [[0, 4, 7], [7, 11, 14], [9, 12, 16], [5, 9, 12]], "chill": [[0, 4, 7, 11], [5, 9, 12, 16], [2, 5, 9, 12], [7, 11, 14, 17]],
             "sneaky": [[0, 3, 7], [0, 3, 7], [5, 8, 12], [7, 10, 14]], "epic": [[0, 4, 7], [9, 12, 16], [5, 9, 12], [7, 11, 14]]}
    prog = progs.get(mood, progs["bouncy"])
    n = int(SR * (duration + 1)); out = np.zeros(n)
    bar = beat * 4; t = 0.0; bi = 0
    while t < duration + 0.5:
        ch = prog[bi % len(prog)]
        # arpeggio pluck (8ths)
        for k in range(8):
            m = key + ch[(k * (1 if mood != "sneaky" else 2)) % len(ch)] + (12 if k % 4 == 3 else 0)
            s = int(SR * (t + k * beat / 2))
            if s >= n:
                break
            p = _pluck(NOTE(m), beat * 0.9, seed=bi * 8 + k) * (0.16 if k % 2 == 0 else 0.11)
            out[s:s + len(p)] += p[: n - s]
        # bass on beats 1 and 3
        for k in (0, 2):
            s = int(SR * (t + k * beat))
            if s >= n:
                break
            tt = _t(beat * 0.95); b = np.sin(2 * np.pi * NOTE(key - 24 + ch[0]) * tt) * np.exp(-tt * 3) * 0.28
            out[s:s + len(b)] += b[: n - s]
        # light percussion: shaker on 8ths, clap on 2 and 4
        for k in range(8):
            s = int(SR * (t + k * beat / 2))
            if s >= n:
                break
            sh = _noise(int(SR * 0.04), bi * 8 + k) * np.exp(-_t(0.04) * 90) * 0.05
            out[s:s + len(sh)] += sh[: n - s]
        for k in (1, 3):
            s = int(SR * (t + k * beat))
            if s >= n:
                break
            cl = _lp(_noise(int(SR * 0.12), k + bi), 0.5) * np.exp(-_t(0.12) * 35) * 0.18
            out[s:s + len(cl)] += cl[: n - s]
        t += bar; bi += 1
    fade = int(SR * 1.2)
    out[-fade:] *= np.linspace(1, 0, fade)
    return out[: int(SR * duration)]


# ───────── TTS ─────────
_kok = None


def _kokoro():
    global _kok
    if _kok is None:
        from kokoro_onnx import Kokoro
        for d in MODEL_DIRS:
            m, v = d / "kokoro-v1.0.int8.onnx", d / "voices-v1.0.bin"
            if m.exists() and v.exists():
                _kok = Kokoro(str(m), str(v))
                break
        else:
            raise RuntimeError(f"Kokoro model not found in {MODEL_DIRS}. Download kokoro-v1.0.int8.onnx and voices-v1.0.bin from "
                               "https://github.com/thewh1teagle/kokoro-onnx/releases into " + str(CACHE))
    return _kok


def tts(text, voice="am_michael", speed=1.0):
    key = hashlib.sha1(f"{text}|{voice}|{speed}".encode()).hexdigest()[:16]
    f = CACHE / "lines" / f"{key}.npy"
    if f.exists():
        return np.load(f)
    samples, sr = _kokoro().create(text, voice=voice, speed=speed, lang="en-us")
    x = np.interp(np.arange(int(len(samples) * SR / sr)) * sr / SR, np.arange(len(samples)), samples).astype(np.float32)
    f.parent.mkdir(parents=True, exist_ok=True)
    np.save(f, x)
    return x


# ───────── mix ─────────
def mix(story, out_wav):
    T = story["duration"]; n = int(SR * (T + 0.5))
    fx = np.zeros(n); vox = np.zeros(n)

    def add(buf, x, at, g=1.0):
        s = int(SR * max(at, 0))
        if s >= n:
            return
        e = min(n, s + len(x)); buf[s:e] += x[: e - s] * g

    for i, b in enumerate(story["beats"]):
        t0 = b["t0"]
        if "whip" in b.get("fx", []) or (i > 0 and b.get("transition", "whoosh") == "whoosh"):
            add(fx, sfx_whoosh(), t0 - 0.12, 0.6)
        if "punch" in b.get("fx", []):
            add(fx, sfx_thud(), t0, 0.7)
        if "flash" in b.get("fx", []):
            add(fx, sfx_slam(), t0, 0.6)
        for bb in b.get("bubbles", []):
            add(fx, sfx_pop(), t0 + bb["at"], 0.6)
            if bb.get("voice"):
                add(vox, tts(bb["text"].replace("*", ""), bb["voice"], bb.get("speed", 1.0)), t0 + bb["at"] + 0.05, 1.0)
        for st in b.get("stickers", []):
            k = st["kind"]; at = t0 + st["at"]
            add(fx, {"badge": sfx_achievement, "stamp": sfx_slam, "float": sfx_sparkle, "label": sfx_pop, "emoji": sfx_boing,
                     "meter": sfx_riser}[k](), at, 0.7)
        if b.get("freeze"):
            add(fx, sfx_scratch(), t0 + b["freeze"]["at"], 0.8)
        for s in b.get("sfx", []):
            add(fx, SFX[s["type"]](), t0 + s.get("at", 0), s.get("gain", 1.0))
        if i == 0 and story.get("hook"):
            for k in range(len(story["hook"]["lines"])):
                add(fx, sfx_pop(), k * 0.18, 0.5)
    mus = np.zeros(n); m = music(T + 0.4, story["music"]["seed"], story["music"]["mood"]); mus[: len(m)] = m[:n]
    # duck music under voices
    env = np.abs(vox); win = int(SR * 0.15)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    duck = 1 - 0.6 * np.clip(env * 12, 0, 1)
    y = vox * 1.0 + fx * 0.8 + mus * 0.55 * duck
    y = np.tanh(y * 1.1) * 0.92
    y16 = (np.clip(y, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(out_wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y16.tobytes())
    return out_wav
