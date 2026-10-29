"""
可选旁白：把每段字幕（或 beat.narration）合成为语音，按语音长度拉长画面，生成对齐的人声轨。

引擎：
- kokoro（默认，本地离线）：Kokoro-82M ONNX；首次使用自动下载模型（~120 MB）到 ~/.cache/autoclip/tts
- openai：OpenAI TTS（需要 key：AUTOCLIP_TTS_API_KEY / OPENAI_API_KEY）

合成结果按 (引擎, 声音, 语速, 文本) 缓存，改了画面重渲不会重复合成。
"""
from __future__ import annotations

import hashlib
import io
import logging
import os
import re
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .schema import Narration, Storyboard

logger = logging.getLogger(__name__)

SR = 48_000
LEAD = 0.30          # 段首留白（秒）
TAIL = 0.45          # 句尾留白
MAX_BEAT = 20.0
CACHE = Path(os.getenv("AUTOCLIP_TTS_CACHE", Path.home() / ".cache" / "autoclip" / "tts"))
KOKORO_FILES = {
    "kokoro-v1.0.int8.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}

# 朗读前的文本规整：单位、符号读成英文
_REPL = [
    (r"(\d)\s*km/h", r"\1 kilometers per hour"), (r"(\d)\s*m/s", r"\1 meters per second"),
    (r"(\d)\s*km/s", r"\1 kilometers per second"), (r"(\d)\s*kJ/mol", r"\1 kilojoules per mole"),
    (r"(\d)\s*°C", r"\1 degrees Celsius"), (r"(\d)\s*°F", r"\1 degrees Fahrenheit"),
    (r"(\d)\s*km\b", r"\1 kilometers"), (r"(\d)\s*kg\b", r"\1 kilograms"), (r"(\d)\s*mph\b", r"\1 miles per hour"),
    (r"(\d)\s*%", r"\1 percent"), (r"~\s*", "about "), (r"(\d)\s*×", r"\1 times"), (r"×\s*(\d)", r"times \1"),
    (r"\bCO2\b", "C O two"), (r"\bN2\b", "N two"), (r"\bO2\b", "O two"), (r"\bH2O\b", "H two O"),
    (r"N≡N", "N triple-bond N"), (r"O=O", "O double-bond O"), (r"\s*·\s*", ", "), (r"\s*—\s*", ", "),
]


def speech_text(s: str) -> str:
    s = s.replace("*", "")
    for a, b in _REPL:
        s = re.sub(a, b, s)
    return re.sub(r"\s+", " ", s).strip()


# ------------------------------------------------------------------ engines ---
class KokoroEngine:
    def __init__(self, voice: str, speed: float):
        try:
            from kokoro_onnx import Kokoro
        except ImportError as e:  # noqa: F841
            raise ImportError("kokoro_onnx") from e
        CACHE.mkdir(parents=True, exist_ok=True)
        for name, url in KOKORO_FILES.items():
            path = CACHE / name
            if not path.exists() or path.stat().st_size < 1_000_000:
                logger.info("下载 TTS 模型 %s …", name)
                import urllib.request
                tmp = path.with_suffix(".part")
                urllib.request.urlretrieve(url, tmp)
                tmp.rename(path)
        self.k = Kokoro(str(CACHE / "kokoro-v1.0.int8.onnx"), str(CACHE / "voices-v1.0.bin"))
        if voice not in self.k.get_voices():
            raise ValueError(f"kokoro 没有声音 {voice}；可选：{', '.join(sorted(self.k.get_voices())[:30])} …")
        self.voice, self.speed = voice, speed

    def synth(self, text: str) -> Tuple[np.ndarray, int]:
        lang = {"a": "en-us", "b": "en-gb"}.get(self.voice[:1], "en-us")
        s, sr = self.k.create(text, voice=self.voice, speed=self.speed, lang=lang)
        return np.asarray(s, dtype=np.float32), int(sr)


class OpenAIEngine:
    def __init__(self, voice: str, speed: float):
        from openai import OpenAI
        key = os.getenv("AUTOCLIP_TTS_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("openai TTS 需要 AUTOCLIP_TTS_API_KEY 或 OPENAI_API_KEY")
        self.client = OpenAI(api_key=key, base_url=os.getenv("AUTOCLIP_TTS_BASE_URL") or None)
        self.voice, self.speed = voice, speed

    def synth(self, text: str) -> Tuple[np.ndarray, int]:
        r = self.client.audio.speech.create(model=os.getenv("AUTOCLIP_TTS_MODEL", "gpt-4o-mini-tts"),
                                            voice=self.voice, input=text, speed=self.speed, response_format="wav")
        with wave.open(io.BytesIO(r.read())) as w:
            sr = w.getframerate()
            a = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float32) / 32768
            if w.getnchannels() > 1:
                a = a.reshape(-1, w.getnchannels()).mean(axis=1)
        return a, sr


def make_engine(cfg: Narration):
    return KokoroEngine(cfg.voice, cfg.speed) if cfg.engine == "kokoro" else OpenAIEngine(cfg.voice, cfg.speed)


def _resample(a: np.ndarray, sr: int) -> np.ndarray:
    if sr == SR:
        return a.astype(np.float32)
    n = int(round(len(a) * SR / sr))
    return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)


def _trim(a: np.ndarray, thr: float = 0.006) -> np.ndarray:
    idx = np.where(np.abs(a) > thr)[0]
    if not len(idx):
        return a[:0]
    pad = int(0.03 * SR)
    return a[max(0, idx[0] - pad): idx[-1] + pad]


class Speaker:
    """带缓存的合成器（48 kHz 单声道 float32）。"""

    def __init__(self, cfg: Narration):
        self.cfg = cfg
        self._engine = None

    def say(self, text: str) -> np.ndarray:
        key = hashlib.sha1(f"{self.cfg.engine}|{self.cfg.voice}|{self.cfg.speed}|{text}".encode()).hexdigest()[:20]
        path = CACHE / "lines" / f"{key}.npy"
        if path.exists():
            return np.load(path)
        if self._engine is None:
            self._engine = make_engine(self.cfg)
        a, sr = self._engine.synth(text)
        a = _trim(_resample(a, sr))
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, a)
        return a


# ------------------------------------------------------------------- 流程 ---
@dataclass
class Line:
    kind: str            # title / beat / end
    index: int           # beat 序号（title/end 为 -1）
    text: str
    audio: np.ndarray

    @property
    def seconds(self) -> float:
        return len(self.audio) / SR


def plan_lines(sb: Storyboard, cfg: Narration) -> List[Tuple[str, int, str]]:
    """(kind, index, 文本)。字幕里的占位符先由 compile_plan 填好。"""
    from .model import compile_plan
    plan = compile_plan(sb)
    out: List[Tuple[str, int, str]] = []
    if cfg.read_title and sb.intro.style != "none":
        t = sb.intro.title or " ".join(sb.intro.lines)
        if t.strip():
            out.append(("title", -1, t))
    for b in plan["beats"]:
        text = b["narration"] if b["narration"] is not None else b["caption"]
        if text and text.strip():
            out.append(("beat", b["i"], text))
    if cfg.read_end:
        e = sb.outro.end
        lines = (e.lines if e else [sb.outro.question]) if (e or sb.outro.question) else []
        t = " ".join(l for l in lines if l)
        if e and e.kind == "title" and not t:
            t = sb.intro.title
        if t.strip():
            out.append(("end", -1, t.capitalize() if t.isupper() else t))
    return out


def narrate(sb: Storyboard, cfg: Optional[Narration] = None) -> Tuple[Storyboard, List[Line]]:
    """合成全部台词，并返回拉长后的分镜（每段至少容纳 LEAD + 语音 + TAIL）。"""
    cfg = cfg or sb.narration or Narration()
    spk = Speaker(cfg)
    lines = [Line(k, i, t, spk.say(speech_text(t))) for k, i, t in plan_lines(sb, cfg)]
    sb2 = sb.model_copy(deep=True)
    for ln in lines:
        need = LEAD + ln.seconds + TAIL
        if ln.kind == "beat":
            b = sb2.beats[ln.index]
            if ln.index == 0:   # 首段被片头卡占用（字幕也在片头后才出现）：台词排在片头之后
                need += max(0.0, sb2.intro.duration)
            if b.duration < need:
                b.duration = min(MAX_BEAT, round(need, 2))
        elif ln.kind == "title":
            # 片头标题念在首段里；片头卡至少要盖住标题朗读
            sb2.intro.duration = max(sb2.intro.duration, round(LEAD + ln.seconds + 0.2, 2))
            if sb2.beats[0].duration < sb2.intro.duration + 0.4:
                sb2.beats[0].duration = min(MAX_BEAT, round(sb2.intro.duration + 0.4, 2))
        elif ln.kind == "end":
            sb2.outro.question_duration = max(sb2.outro.question_duration, round(LEAD + ln.seconds + 0.8, 2))
    return sb2, lines


def voice_track(plan: Dict[str, Any], lines: List[Line]) -> np.ndarray:
    """按最终时间轴摆放台词，返回整段人声（单声道，48 kHz）。"""
    n = int(round(plan["duration"] * SR))
    out = np.zeros(n, dtype=np.float32)
    starts = {b["i"]: b["start"] for b in plan["beats"]}
    intro_d = plan.get("intro_duration", 0.0)
    end_start = plan.get("end_start")
    for ln in lines:
        if ln.kind == "title":
            t0 = LEAD
        elif ln.kind == "end":
            if end_start is None:
                continue
            t0 = end_start + LEAD
        else:
            t0 = starts[ln.index] + LEAD + (intro_d if ln.index == 0 else 0.0)
        i0 = int(t0 * SR)
        seg = ln.audio[: max(0, n - i0)]
        out[i0: i0 + len(seg)] += seg
    return out
