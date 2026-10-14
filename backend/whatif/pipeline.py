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
from .schema import Storyboard


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
               progress: Optional[Callable[[str, int, int], None]] = None) -> Dict[str, Any]:
    from .audio import render_audio
    from .render import render_video

    t0 = time.time()
    plan = compile_plan(sb)
    tmp = Path(tempfile.mkdtemp(prefix="whatif-"))
    try:
        if progress:
            progress("audio", 0, 1)
        wav = render_audio(plan, tmp / "audio.wav")
        if progress:
            progress("audio", 1, 1)
        res = render_video(plan, out, preview=preview, workers=workers, audio=wav,
                           progress=(lambda d, n: progress("frames", d, n)) if progress else None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    out.with_suffix(".storyboard.json").write_text(
        json.dumps(sb.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    res.update({"title": sb.title, "seconds": round(time.time() - t0, 1),
                "milestones": [{"t": round(m["t0"], 2), "title": m["title"]} for m in plan["milestones"]]})
    return res
