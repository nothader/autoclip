"""What-if 视频：分镜 → 渲染计划 → 画面 + 声音 → MP4。"""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .model import PlanError, compile_plan, validate
from .schema import Narration, Storyboard


def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return (s[:60] or "whatif")


def load_storyboard(path: Path) -> Storyboard:
    sb = Storyboard.model_validate_json(Path(path).read_text(encoding="utf-8"))
    problems = validate(sb)
    if problems:
        raise PlanError("分镜有问题：\n- " + "\n- ".join(problems))
    return sb


def make_video(sb: Storyboard, out: Path, *, preview: bool = False, workers: int = 0,
               narration: Optional["Narration"] = None,
               progress: Optional[Callable[[str, int, int], None]] = None) -> Dict[str, Any]:
    """narration：开启旁白（覆盖分镜里的 narration 设置）；None 时按分镜里的 narration.enabled。"""
    from .audio import render_audio
    from .render import render_video

    t0 = time.time()
    cfg = narration or (sb.narration if sb.narration and sb.narration.enabled else None)
    voice = None
    lines = []
    if cfg is not None:
        from .narration import narrate, voice_track
        if progress:
            progress("voice", 0, 1)
        pace = sb.pace or 1.0
        if pace != 1.0:   # 有旁白时：节奏体现在语速上（上限 1.6），镜头按语音长度排，不再压缩
            cfg = cfg.model_copy(update={"speed": round(min(1.6, max(cfg.speed, cfg.speed * pace ** 0.5)), 2)})
            sb = sb.model_copy(update={"pace": 1.0})
        sb, lines = narrate(sb, cfg)
        if progress:
            progress("voice", 1, 1)
    plan = compile_plan(sb)
    if cfg is not None:
        voice = voice_track(plan, lines)
    tmp = Path(tempfile.mkdtemp(prefix="whatif-"))
    try:
        if progress:
            progress("audio", 0, 1)
        wav = render_audio(plan, tmp / "audio.wav", voice=voice)
        if progress:
            progress("audio", 1, 1)
        res = render_video(plan, out, preview=preview, workers=workers, audio=wav,
                           progress=(lambda d, n: progress("frames", d, n)) if progress else None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out.with_suffix(".storyboard.json").write_text(
        json.dumps(sb.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    res.update({"title": sb.title, "seconds": round(time.time() - t0, 1),
                "narration": [{"kind": ln.kind, "beat": ln.index, "text": ln.text, "sec": round(ln.seconds, 2)} for ln in lines],
                "milestones": [{"t": round(m["t0"], 2), "title": m["title"]} for m in plan["milestones"]]})
    return res
