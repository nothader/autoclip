"""素材 + 音乐 → 剪辑表 → 成片。CLI 和 MCP 共用。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, List, Optional, Sequence

from backend.beatcut.audio import MusicAnalysis, analyze_music, grid_analysis
from backend.beatcut.footage import analyze_footage, collect_sources
from backend.beatcut.plan import EditPlan, PlanOptions, describe, plan_edit
from backend.beatcut.render import render_plan

Progress = Optional[Callable[[str, int, int], None]]


def analyze(music: Optional[str | Path], bpm: Optional[float], duration: float) -> MusicAnalysis:
    if music:
        return analyze_music(Path(music).expanduser(), bpm_hint=bpm)
    return grid_analysis(bpm or 120.0, duration)


def make_plans(footage: Sequence[str | Path], music: Optional[str | Path], opts: PlanOptions,
               *, variants: int = 1, bpm: Optional[float] = None, progress: Progress = None) -> dict:
    """分析一次，出 variants 个剪辑表。返回 {plans, warnings, music, shots}。"""
    sources = collect_sources(footage)
    shots = analyze_footage(sources, progress=progress)
    m = analyze(music, bpm, opts.duration)
    music_path = str(Path(music).expanduser().resolve()) if music else None
    plans: List[EditPlan] = []
    warnings: List[str] = []
    for v in range(max(1, variants)):
        o = opts.model_copy(update={"variant": opts.variant + v})
        p, w = plan_edit(shots, m, o, music_path)
        plans.append(p)
        warnings += [x for x in w if x not in warnings]
    return {
        "plans": plans, "warnings": warnings,
        "music": {"bpm": round(m.bpm, 1), "beats": len(m.beats), "duration": round(m.duration, 2), "path": music_path},
        "footage": {"files": len(sources), "shots": len(shots)},
    }


def save_plan(plan: EditPlan, path: Path) -> Path:
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_plan(path: Path) -> EditPlan:
    return EditPlan.model_validate_json(Path(path).expanduser().read_text(encoding="utf-8"))


def variant_path(out: Path, i: int, n: int) -> Path:
    return out if n <= 1 else out.with_name(f"{out.stem}-v{i + 1}{out.suffix}")


def make_videos(footage: Sequence[str | Path], music: Optional[str | Path], out: Path, opts: PlanOptions,
                *, variants: int = 1, bpm: Optional[float] = None, preview: bool = False,
                workers: int = 0, keep_plan: bool = True, progress: Progress = None) -> dict:
    res = make_plans(footage, music, opts, variants=variants, bpm=bpm, progress=progress)
    out = Path(out).expanduser().resolve()
    videos = []
    for i, plan in enumerate(res["plans"]):
        target = variant_path(out, i, len(res["plans"]))
        r = render_plan(plan, target, preview=preview, workers=workers, progress=progress)
        if keep_plan:
            r["plan"] = str(save_plan(plan, target.with_suffix(".json")))
        r["edl"] = describe(plan)
        videos.append(r)
    return {"videos": videos, "warnings": res["warnings"], "music": res["music"], "footage": res["footage"]}
