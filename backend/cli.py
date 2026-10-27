#!/usr/bin/env python3
"""
autoclip — 命令行出片。

    autoclip run video.mp4                         # 用桌面应用里配好的模型
    autoclip run video.mp4 --provider ollama       # 本地 Ollama（默认 qwen2.5:7b，无需 key）
    autoclip run video.mp4 --provider lmstudio --model qwen2.5-7b-instruct
    autoclip run video.mp4 --provider openai --base-url https://api.deepseek.com/v1 --model deepseek-chat --api-key sk-...
    autoclip run video.mp4 --srt video.srt --min-score 0.6 --json
    autoclip list / show <project_id> / providers / doctor

产物与桌面应用共用同一个数据目录（mac: ~/Library/Application Support/AutoClip），
跑完在桌面应用首页就能看到。用 --data-dir 或 AUTOCLIP_DATA_DIR 可以换目录。

不装包也能用：`python -m backend.cli ...`；`pip install -e .` 之后有 `autoclip` 命令。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# 只 import 不触发数据库 / 模型初始化的东西；重活放在子命令里、configure_environment 之后
from backend.services.local_runner import (
    PROVIDER_CHOICES,
    LLMOverride,
    RunRequest,
    configure_environment,
    setup_logging,
)

STAGE_NAMES = {
    "INGEST": "准备", "SUBTITLE": "字幕", "ANALYZE": "分析",
    "HIGHLIGHT": "选段", "EXPORT": "导出", "DONE": "完成",
}
_TTY = sys.stderr.isatty()


def _c(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if _TTY else s


def _dim(s: str) -> str:
    return _c("2", s)


def _bold(s: str) -> str:
    return _c("1", s)


def _err(msg: str) -> None:
    print(_c("31", "error: ") + msg, file=sys.stderr)


def _add_llm_args(p: argparse.ArgumentParser) -> None:
    g = p.add_argument_group("模型（不填则用桌面应用设置页里的配置）")
    g.add_argument("--provider", choices=PROVIDER_CHOICES, help="dashscope / openai / gemini / siliconflow，或本地预设 ollama / lmstudio")
    g.add_argument("--model", help="模型名，如 qwen-plus、gpt-4o-mini、qwen2.5:7b")
    g.add_argument("--base-url", help="OpenAI 兼容接口地址（provider=openai 时用；ollama/lmstudio 有默认值）")
    g.add_argument("--api-key", help="API Key（本地模型可不填）。也可用环境变量 AUTOCLIP_API_KEY")


def _llm_override(args: argparse.Namespace) -> LLMOverride:
    return LLMOverride(
        provider=getattr(args, "provider", None),
        model=getattr(args, "model", None),
        base_url=getattr(args, "base_url", None),
        api_key=getattr(args, "api_key", None) or os.getenv("AUTOCLIP_API_KEY"),
    )


# ---------------------------------------------------------------- run ---
def cmd_run(args: argparse.Namespace) -> int:
    from backend.services.local_runner import configure_llm, prepare_project, run_pipeline, summarize_project

    t0 = time.time()
    try:
        info = configure_llm(_llm_override(args))
    except Exception as e:  # noqa: BLE001
        _err(str(e))
        return 2

    req = RunRequest(
        video=Path(args.video),
        srt=Path(args.srt) if args.srt else None,
        name=args.name,
        category=args.category,
        min_score=args.min_score,
        register_db=not args.no_db,
    )
    try:
        video_in_raw = prepare_project(req, link=not args.copy)
    except FileNotFoundError as e:
        _err(str(e))
        return 2

    if not args.json:
        model_desc = f"{info.get('provider')} · {info.get('model')}"
        if info.get("base_url"):
            model_desc += f" · {info['base_url']}"
        print(_bold(req.name or req.video.stem) + _dim(f"  {req.project_id}"), file=sys.stderr)
        print(_dim(f"模型 {model_desc}"), file=sys.stderr)
        if not req.srt:
            print(_dim("没有字幕文件，将用本地 Whisper 转写（首次会下载模型）"), file=sys.stderr)

    last = {"line": ""}

    def on_progress(p: Dict[str, Any]) -> None:
        if args.json:
            return
        stage = STAGE_NAMES.get(p.get("stage", ""), p.get("stage", ""))
        line = f"[{p.get('percent', 0):3d}%] {stage:<3} {p.get('message', '')}"
        if line != last["line"]:
            print(line, file=sys.stderr)
            last["line"] = line

    result = run_pipeline(req, video_in_raw, on_progress=on_progress)
    elapsed = time.time() - t0

    if result.get("status") != "succeeded":
        if args.json:
            print(json.dumps({"ok": False, "project_id": req.project_id, "error": result.get("error")}, ensure_ascii=False))
        else:
            _err(result.get("error") or "处理失败")
            print(_dim(f"日志：{os.getenv('LOG_FILE')}"), file=sys.stderr)
        return 1

    summary = summarize_project(req.project_id)
    summary["elapsed_sec"] = round(elapsed, 1)
    summary["llm"] = {k: info.get(k) for k in ("provider", "model", "base_url") if info.get(k)}
    if args.json:
        print(json.dumps({"ok": True, **summary}, ensure_ascii=False, indent=2))
        return 0

    print(file=sys.stderr)
    n_clips, n_cols = summary["counts"]["clips"], summary["counts"]["collections"]
    print(_bold(f"完成  {n_clips} 切片 · {n_cols} 合集 · {elapsed:.0f}s"), file=sys.stderr)
    for c in summary["clips"]:
        score = str(c["score_100"]) if c.get("score_100") is not None else "-"
        print(f"  {score:>4}  {c['start_time']} → {c['end_time']}  {c['title']}", file=sys.stderr)
    if n_clips == 0:
        print(_dim("  没有片段达到评分阈值，可以试试 --min-score 0.5"), file=sys.stderr)
    print(_dim(f"输出目录 {summary['clips_dir']}"), file=sys.stderr)
    # stdout 只放项目 id，方便 shell 里接管道
    print(req.project_id)
    return 0


# ---------------------------------------------------------------- list / show ---
def cmd_list(args: argparse.Namespace) -> int:
    from backend.services.local_runner import list_projects

    items = list_projects(limit=args.limit)
    if args.json:
        print(json.dumps(items, ensure_ascii=False, indent=2))
        return 0
    if not items:
        print(_dim("还没有项目。autoclip run <video> 开始。"))
        return 0
    for it in items:
        print(f"{it['project_id']}  {it['status']:<9} {it['clips']:>3} 切片  {it['updated_at'][:16]}  {it['name']}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    from backend.services.local_runner import summarize_project

    try:
        s = summarize_project(args.project_id)
    except FileNotFoundError as e:
        _err(str(e))
        return 2
    if args.json:
        print(json.dumps(s, ensure_ascii=False, indent=2))
        return 0
    print(_bold(s["name"]) + _dim(f"  {s['project_id']}"))
    print(_dim(f"{s['counts']['clips']} 切片 · {s['counts']['collections']} 合集 · {s['project_dir']}"))
    for c in s["clips"]:
        score = str(c["score_100"]) if c.get("score_100") is not None else "-"
        print(f"  {score:>4}  {c['start_time']} → {c['end_time']}  {c['title']}")
        if c.get("file"):
            print(_dim(f"        {c['file']}"))
    for col in s["collections"]:
        print(f"  合集  {col['title']}  {_dim('切片 ' + ', '.join(col['clip_ids']))}")
        if col.get("file"):
            print(_dim(f"        {col['file']}"))
    return 0


# ---------------------------------------------------------------- providers / doctor ---
def cmd_providers(args: argparse.Namespace) -> int:
    from backend.core.local_presets import LOCAL_PRESETS
    from backend.core.llm_manager import get_llm_manager

    rows = [
        ("dashscope", "阿里通义千问", "需要 key；国内直连，qwen-plus 性价比高"),
        ("openai", "OpenAI / 兼容接口", "需要 key；--base-url 可指向 DeepSeek / 智谱 / OpenRouter / vLLM"),
        ("gemini", "Google Gemini", "需要 key"),
        ("siliconflow", "硅基流动", "需要 key；DeepSeek / Qwen 开源模型"),
    ] + [
        (p.key, p.display_name, f"无需 key；默认 {p.base_url}" + (f"，默认模型 {p.default_model}" if p.default_model else ""))
        for p in LOCAL_PRESETS.values()
    ]
    info = get_llm_manager().get_current_provider_info()
    if args.json:
        print(json.dumps({"current": info, "providers": [dict(zip(("key", "name", "note"), r)) for r in rows]}, ensure_ascii=False, indent=2))
        return 0
    for key, name, note in rows:
        mark = "●" if key == info.get("provider") else " "
        print(f"{mark} {key:<12} {name:<18} {_dim(note)}")
    cur = f"{info.get('provider')} · {info.get('model')}" + (f" · {info['base_url']}" if info.get("base_url") else "")
    print(_dim(f"\n当前：{cur}  ({'可用' if info.get('available') else '未配置 key'})"))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    from backend.services.local_runner import configure_llm, environment_report

    try:
        configure_llm(_llm_override(args))
    except Exception as e:  # noqa: BLE001
        _err(str(e))
    rep = environment_report()
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return 0 if rep["ffmpeg"]["ok"] and rep["llm"]["ok"] else 1

    def line(ok: Optional[bool], label: str, detail: str) -> None:
        mark = _c("32", "✓") if ok else _c("31", "✗")
        print(f"{mark} {label:<8} {detail}")

    print(_dim(f"数据目录 {rep['data_dir']} · Python {rep['python']}"))
    line(rep["ffmpeg"]["ok"], "ffmpeg", rep["ffmpeg"].get("path") or rep["ffmpeg"].get("error", ""))
    w = rep["whisper"]
    line(w["ok"], "whisper", ("faster-whisper 已安装" if w["ok"] else "未安装（无字幕的视频需要；桌面应用 设置 → 转写 一键安装）"))
    llm = rep["llm"]
    llm_desc = f"{llm.get('provider')} · {llm.get('model')}" + (f" · {llm['base_url']}" if llm.get("base_url") else "")
    line(llm["ok"], "模型", llm_desc + ("" if llm["ok"] else f"  {_dim(llm.get('error') or '')}"))
    return 0 if rep["ffmpeg"]["ok"] and llm["ok"] else 1


# ---------------------------------------------------------------- export ---
def cmd_export(args: argparse.Namespace) -> int:
    from backend.services.publish_export import ExportRequest, export_clip, list_presets, load_clip_meta
    from backend.services.local_runner import summarize_project

    if args.list_presets:
        rows = list_presets()
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
        else:
            for p in rows:
                print(f"{p['key']:<14} {p['label']:<16} {p.get('w') or '-'}x{p.get('h') or '-'}  {p.get('layout')}")
        return 0

    clip_ids = list(args.clip or [])
    if not clip_ids:
        try:
            summary = summarize_project(args.project_id)
        except FileNotFoundError as e:
            _err(str(e))
            return 2
        clip_ids = [c["id"] for c in summary["clips"]]
        if not clip_ids:
            _err("这个项目没有切片")
            return 2

    results = []
    for cid in clip_ids:
        try:
            load_clip_meta(args.project_id, cid)
            r = export_clip(ExportRequest(
                project_id=args.project_id, clip_id=cid, preset=args.preset,
                subtitles=not args.no_subtitles, title_card=not args.no_title,
            ))
            results.append(r)
            if not args.json:
                print(f"{'cached' if r.get('cached') else 'ok':<8} {cid}  {r.get('path')}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            results.append({"ok": False, "clip_id": cid, "error": str(e)[:400]})
            _err(f"{cid}: {e}")

    if args.json:
        print(json.dumps({"ok": all(r.get("ok") for r in results), "exports": results}, ensure_ascii=False, indent=2))
    return 0 if all(r.get("ok") for r in results) else 1


# ---------------------------------------------------------------- mcp ---
def cmd_mcp(args: argparse.Namespace) -> int:
    from backend.mcp_server import main as mcp_main

    return mcp_main()


# ---------------------------------------------------------------- whatif ---
def _whatif_out(args: argparse.Namespace, title: str) -> Path:
    if getattr(args, "output", None):
        return Path(args.output).expanduser().resolve()
    from backend.core.path_utils import get_data_directory
    from backend.whatif.pipeline import slugify
    return get_data_directory() / "whatif" / f"{slugify(title)}.mp4"


def _whatif_progress(as_json: bool):
    last = {"k": None}

    def cb(stage: str, done: int, total: int) -> None:
        if as_json:
            return
        key = (stage, done * 20 // max(1, total))
        if key == last["k"]:
            return
        last["k"] = key
        label = {"audio": "声音", "frames": "画面", "voice": "旁白"}.get(stage, stage)
        print(_dim(f"  {label} {done}/{total}"), file=sys.stderr)
    return cb


def _whatif_plan(args: argparse.Namespace):
    from backend.services.local_runner import configure_llm
    from backend.whatif.planner import plan_storyboard
    info = configure_llm(_llm_override(args))
    if not args.json:
        print(_dim(f"写分镜：{info.get('provider')} · {info.get('model')}"), file=sys.stderr)
    from backend.whatif.cinema import load_history, recent
    styles = recent(load_history(), "style", 2)
    notes = (args.notes or "") + (f"\nRecent videos used the styles {', '.join(styles)}: pick a different style unless the user asked for one."
                                  if styles else "")
    return plan_storyboard(args.premise, notes=notes.strip(), fmt=getattr(args, "format", None))


def _whatif_pack(args: argparse.Namespace, out: Path) -> dict:
    """成片之外：封面、标题/简介/标签、横屏长视频再自动剪一支 1 分钟竖屏短版（含它自己的封面和文案）。"""
    from backend.whatif import publish
    from backend.whatif.pipeline import make_video
    from backend.whatif.schema import Storyboard
    final = Storyboard.model_validate_json(out.with_suffix(".storyboard.json").read_text(encoding="utf-8"))
    pack = {}
    if not args.json:
        print(_dim("发布包：封面 + 文案" + (" + 竖屏短版" if final.width > final.height else "")), file=sys.stderr)
    pack["thumbnail"] = str(publish.thumbnail(final, out.with_name(out.stem + "_thumb.jpg")))
    meta_path = out.with_name(out.stem + "_youtube.txt")
    meta_path.write_text(publish.metadata_text(publish.metadata(final)), encoding="utf-8")
    pack["metadata"] = str(meta_path)
    if final.width > final.height and not getattr(args, "no_short", False):
        short = publish.make_short(final)
        s_out = out.with_name(out.stem + "_short.mp4")
        make_video(short, s_out, preview=args.preview, workers=args.workers, progress=_whatif_progress(args.json))
        pack["short"] = str(s_out)
        pack["short_thumbnail"] = str(publish.thumbnail(short, s_out.with_name(s_out.stem + "_thumb.jpg")))
        s_meta = s_out.with_name(s_out.stem + "_tiktok.txt")
        s_meta.write_text(publish.metadata_text(publish.metadata(short)), encoding="utf-8")
        pack["short_metadata"] = str(s_meta)
    return pack


def cmd_whatif(args: argparse.Namespace) -> int:
    from backend.whatif.model import PlanError
    from backend.whatif.pipeline import load_storyboard, make_video, slugify

    try:
        if args.whatif_cmd == "plan":
            sb = _whatif_plan(args)
            out = Path(args.output) if args.output else _whatif_out(args, sb.title).with_suffix(".json")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(sb.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({"ok": True, "storyboard": str(out), "title": sb.title}, ensure_ascii=False) if args.json
                  else f"分镜已写入 {out}\n下一步：autoclip whatif render {out}")
            return 0

        if args.whatif_cmd == "check":
            from backend.whatif.hooks import hook_report, hook_score
            from backend.whatif.model import validate
            from backend.whatif.quality import quality_report
            sb = load_storyboard(Path(args.storyboard))
            rep = hook_report(sb) + quality_report(sb)
            if args.json:
                print(json.dumps({"ok": True, "score": hook_score(sb, rep), "problems": validate(sb),
                                  "findings": [x.__dict__ for x in rep]}, ensure_ascii=False, indent=2))
            else:
                print(_bold(sb.title) + f"  score {hook_score(sb, rep)}/100 (hooks + visuals)")
                for p in validate(sb):
                    print(f"  [error] {p}")
                for x in rep:
                    print(f"  {x}")
                if not rep:
                    print("  All hook and visual rules pass.")
            return 0

        if args.whatif_cmd in ("thumb", "meta", "short"):
            from backend.whatif import publish
            sb = load_storyboard(Path(args.storyboard))
            stem = Path(args.storyboard).with_suffix("")
            stem = stem.with_name(stem.name.replace(".storyboard", ""))
            if args.whatif_cmd == "thumb":
                land = True if args.landscape else (False if args.vertical else None)
                out = Path(args.output) if args.output else stem.with_name(stem.name + "_thumb.jpg")
                publish.thumbnail(sb, out, text=args.text, landscape=land, arrow=args.arrow, beat=args.beat)
                print(json.dumps({"ok": True, "thumbnail": str(out)}) if args.json else f"封面：{out}")
                return 0
            if args.whatif_cmd == "meta":
                meta = publish.metadata(sb)
                out = Path(args.output) if args.output else stem.with_name(stem.name + "_youtube.txt")
                out.write_text(publish.metadata_text(meta), encoding="utf-8")
                print(json.dumps({"ok": True, "path": str(out), **meta}, ensure_ascii=False, indent=2) if args.json
                      else publish.metadata_text(meta) + _dim(f"\n已写入 {out}"))
                return 0
            short = publish.make_short(sb, target=args.target)
            out = Path(args.output) if args.output else stem.with_name(stem.name + "_short.json")
            out.write_text(json.dumps(short.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps({"ok": True, "storyboard": str(out), "beats": len(short.beats)}) if args.json
                  else f"短版分镜（{len(short.beats)} 段）：{out}\n下一步：autoclip whatif render {out} --pack")
            return 0

        if args.whatif_cmd == "examples":
            from backend.whatif.planner import EXAMPLE_PATH
            for p in sorted(EXAMPLE_PATH.parent.glob("*.json")):
                print(p)
            return 0

        if args.whatif_cmd == "render":
            sb = load_storyboard(Path(args.storyboard))
        else:  # make
            sb = _whatif_plan(args)
        if sb.pace is None or args.pace is not None:
            from backend.whatif.model import DEFAULT_PACE
            sb = sb.model_copy(update={"pace": args.pace if args.pace is not None else DEFAULT_PACE})
        theme_up = {k: v for k, v in (("style", args.style), ("layout", args.layout), ("captions", args.captions),
                                      ("flow", args.flow), ("palette", args.palette)) if v}
        if theme_up:
            sb = sb.model_copy(update={"theme": sb.theme.model_copy(update=theme_up)})
        from backend.whatif.cinema import load_history, resolve_variety
        sb = resolve_variety(sb, load_history())   # flow / palette 自动轮换，不和最近的视频撞
        out = _whatif_out(args, sb.title)
        if args.preview and not args.output:
            out = out.with_name(out.stem + "-preview.mp4")
        if not args.json:
            print(_bold(sb.title) + _dim(f"  → {out}"), file=sys.stderr)
            from backend.whatif.hooks import hook_report, hook_score
            from backend.whatif.quality import quality_report
            rep = hook_report(sb) + quality_report(sb)
            fixes = [x for x in rep if x.level == "fix"]
            print(_dim(f"score {hook_score(sb, rep)}/100 (hooks + visuals)" + (f" · {len(fixes)} to fix (autoclip whatif check for details)" if fixes else "")), file=sys.stderr)
        narr = None
        if getattr(args, "narrate", False):
            from backend.whatif.schema import Narration
            base = sb.narration or Narration()
            narr = base.model_copy(update={k: v for k, v in (("voice", args.voice), ("engine", args.tts), ("speed", args.speed)) if v})
            narr.enabled = True
        res = make_video(sb, out, preview=args.preview, workers=args.workers, narration=narr,
                         frames_dir=Path(args.frames_dir) if getattr(args, "frames_dir", None) else None,
                         progress=_whatif_progress(args.json))
    except ImportError as e:
        _err(f"缺少 what-if 依赖（{e.name}）：pip install -r requirements-whatif.txt && python -m playwright install chromium"
             + ("（旁白需要 kokoro-onnx）" if e.name == "kokoro_onnx" else ""))
        return 2
    except (PlanError, ValueError, RuntimeError) as e:
        _err(str(e))
        return 1
    if getattr(args, "pack", False):
        try:
            res["pack"] = _whatif_pack(args, out)
        except Exception as e:  # noqa: BLE001  发布包失败不影响成片
            _err(f"发布包没做完：{e}")
    if args.json:
        print(json.dumps({"ok": True, **res}, ensure_ascii=False, indent=2))
    else:
        for k, v in (res.get("pack") or {}).items():
            print(_dim(f"  {k}: {v}"))
        print(f"完成：{res['path']}  ({res['duration']:.1f}s, {res['width']}x{res['height']}, 用时 {res['seconds']}s)")
        if res.get("page_errors"):
            print(_dim(f"页面警告：{res['page_errors'][:3]}"), file=sys.stderr)
    return 0


# ---------------------------------------------------------------- parser ---
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="autoclip",
        description="AutoClip 命令行：一条命令把长视频切成高光片段。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("\n\n", 1)[1] if __doc__ else None,
    )
    p.add_argument("--data-dir", help="数据目录（默认与桌面应用共用；也可用 AUTOCLIP_DATA_DIR）")
    p.add_argument("-v", "--verbose", action="store_true", help="在终端输出后端日志")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="处理一条视频，输出切片与合集")
    r.add_argument("video", help="视频文件路径")
    r.add_argument("--srt", help="已有字幕文件（没有则本地 Whisper 转写）")
    r.add_argument("--name", help="项目名（默认取文件名）")
    r.add_argument("--category", default="default",
                   choices=["default", "knowledge", "business", "opinion", "experience", "speech", "content_review", "entertainment"],
                   help="内容类型，影响提示词")
    r.add_argument("--min-score", type=float, help="最低评分阈值 0–1（默认 0.7；切片为 0 时调低）")
    r.add_argument("--copy", action="store_true", help="把视频复制进项目目录（默认硬链接，不占双份空间）")
    r.add_argument("--no-db", action="store_true", help="不写 SQLite（桌面应用里就看不到这个项目）")
    r.add_argument("--json", action="store_true", help="以 JSON 输出结果（给脚本 / agent 用）")
    _add_llm_args(r)
    r.set_defaults(func=cmd_run)

    l = sub.add_parser("list", help="列出项目")
    l.add_argument("--limit", type=int, default=30)
    l.add_argument("--json", action="store_true")
    l.set_defaults(func=cmd_list)

    s = sub.add_parser("show", help="查看一个项目的切片与文件路径")
    s.add_argument("project_id")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_show)

    pr = sub.add_parser("providers", help="列出可用的模型提供商与本地预设")
    pr.add_argument("--json", action="store_true")
    pr.set_defaults(func=cmd_providers)

    d = sub.add_parser("doctor", help="检查 ffmpeg / Whisper / 模型连接")
    d.add_argument("--json", action="store_true")
    _add_llm_args(d)
    d.set_defaults(func=cmd_doctor)

    m = sub.add_parser("mcp", help="以 MCP server（stdio）方式运行，供 Cursor / Claude 调用")
    m.set_defaults(func=cmd_mcp)

    e = sub.add_parser("export", help="把切片渲成可发布成片（9:16 / 烧字幕 / 标题卡）")
    e.add_argument("project_id")
    e.add_argument("--preset", default="douyin", choices=["douyin", "xiaohongshu", "shorts", "bilibili", "original"])
    e.add_argument("--clip", action="append", help="切片 id，可重复；不填则导出全部")
    e.add_argument("--no-subtitles", action="store_true")
    e.add_argument("--no-title", action="store_true")
    e.add_argument("--list-presets", action="store_true")
    e.add_argument("--json", action="store_true")
    e.set_defaults(func=cmd_export)

    w = sub.add_parser("whatif", help="生成 what-if 科普短视频（3D 模拟 + 数据 HUD + 音效，9:16）")
    wsub = w.add_subparsers(dest="whatif_cmd", required=True)
    wp = wsub.add_parser("plan", help="题目 → 分镜 JSON（用 LLM；可手改后再 render）")
    wp.add_argument("premise", help='题目，如 "What if you got 2x faster every second?"')
    wp.add_argument("--notes", help="给编剧的额外要求")
    wp.add_argument("--format", choices=["escalation", "timeline", "countdown", "story", "survival", "pov"], help="指定版式（默认让模型按题目选）")
    wp.add_argument("-o", "--output", help="分镜 JSON 输出路径")
    wp.add_argument("--json", action="store_true")
    _add_llm_args(wp)
    wr = wsub.add_parser("render", help="分镜 JSON → MP4")
    wr.add_argument("storyboard", help="分镜 JSON 路径（示例见 `autoclip whatif examples`）")
    wm = wsub.add_parser("make", help="题目 → 分镜 → MP4 一步到位")
    wm.add_argument("premise")
    wm.add_argument("--notes")
    wm.add_argument("--format", choices=["escalation", "timeline", "countdown", "story", "survival", "pov"], help="指定版式（默认让模型按题目选）")
    _add_llm_args(wm)
    for x in (wr, wm):
        x.add_argument("-o", "--output", help="MP4 输出路径（默认 数据目录/whatif/<标题>.mp4）")
        x.add_argument("--preview", action="store_true", help="半分辨率（540x960），快 ~3 倍")
        x.add_argument("--workers", type=int, default=0, help="并行渲染进程数（默认 = CPU 核数，最多 4）")
        x.add_argument("--frames-dir", help="帧放在这个目录并保留；重跑同一命令时跳过已渲好的帧（长片 / 容器可能重启时用）")
        x.add_argument("--json", action="store_true")
        x.add_argument("--narrate", action="store_true", help="加旁白（默认念字幕；本地 Kokoro TTS，首次自动下载模型 ~120 MB）")
        x.add_argument("--voice", help="旁白声音（kokoro: am_michael / af_heart / bf_emma / bm_george …；openai: onyx / nova …）")
        x.add_argument("--tts", choices=["kokoro", "openai"], help="TTS 引擎（默认 kokoro，离线）")
        x.add_argument("--speed", type=float, help="语速 0.6–1.6（默认 1.0）")
        x.add_argument("--style", choices=["calm", "bold", "cinematic", "toon", "retro", "witness", "bodycam"],
                       help="Visual style: calm (quiet, premium) / bold (viral word-by-word captions, punch zooms) / "
                            "cinematic (letterbox, grain, grade) / toon (cel-shaded, outlines, sticker captions) / retro (8-bit pixels, scanlines) / witness (fixed eyewitness view, coffee-cup anchor, escalating metric) / bodycam (found footage: fisheye, REC + timestamp, handheld shake, sensor noise, night vision)")
        x.add_argument("--flow", choices=["steady", "build", "punchy", "slowburn", "rollercoaster"],
                       help="Edit rhythm (default: auto, rotated so consecutive videos differ): build = cuts speed up, punchy = fast cuts "
                            "with hits, slowburn = slow start then fast, rollercoaster = alternating, steady = even")
        x.add_argument("--palette", choices=["natural", "warm", "cool", "teal_orange", "vivid", "pastel", "mono", "noir"],
                       help="Colour grade (default: auto per style, rotated)")
        x.add_argument("--layout", choices=["full", "split"], help="split = story on top, satisfying loop below (vertical only)")
        x.add_argument("--captions", choices=["line", "words", "box"], help="Caption mode (default follows the style)")
        x.add_argument("--pack", action=argparse.BooleanOptionalAction, default=(x is wm),
                       help="Also write a thumbnail, title/description/tags text and (for landscape long-form) a 1-minute "
                            "vertical short with its own thumbnail. On by default for make.")
        x.add_argument("--no-short", action="store_true", help="With --pack: skip the automatic vertical short")
        x.add_argument("--pace", type=float, default=None,
                       help="Edit pace multiplier (default 1.2): shots 1.2x shorter, motion 1.2x faster; captions stay readable. "
                            "A storyboard's own \"pace\" wins. Use 1.0 for the original timing.")
    wc = wsub.add_parser("check", help="Check a storyboard against the hook/retention rules (specific, grade-3 reading level, 3-second hook, open loop, no fluff)")
    wc.add_argument("storyboard")
    wc.add_argument("--json", action="store_true")
    wt = wsub.add_parser("thumb", help="Thumbnail: renders the most dramatic shot and adds big bait text")
    wt.add_argument("storyboard")
    wt.add_argument("-o", "--output", help="JPG path (default <storyboard>_thumb.jpg)")
    wt.add_argument("--text", help='Big text, *word* = yellow highlight (default: storyboard.thumbnail or from the title)')
    wt.add_argument("--beat", type=int, help="Use this beat's shot (default: auto-pick)")
    wt.add_argument("--arrow", action="store_true", help="Add a red arrow")
    g = wt.add_mutually_exclusive_group()
    g.add_argument("--landscape", action="store_true", help="1280x720 (default follows the video)")
    g.add_argument("--vertical", action="store_true", help="1080x1920")
    wt.add_argument("--json", action="store_true")
    wmeta = wsub.add_parser("meta", help="Title, description, chapters, tags and a pinned comment for YouTube/TikTok")
    wmeta.add_argument("storyboard")
    wmeta.add_argument("-o", "--output", help="TXT path (default <storyboard>_youtube.txt)")
    wmeta.add_argument("--json", action="store_true")
    wsh = wsub.add_parser("short", help="Cut a long-form storyboard into a ~1-minute vertical short storyboard")
    wsh.add_argument("storyboard")
    wsh.add_argument("-o", "--output", help="JSON path (default <storyboard>_short.json)")
    wsh.add_argument("--target", type=float, default=62.0, help="Target length in seconds after pacing (default 62)")
    wsh.add_argument("--json", action="store_true")
    wsub.add_parser("examples", help="列出内置示例分镜")
    w.set_defaults(func=cmd_whatif)
    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_environment(Path(args.data_dir) if args.data_dir else None)
    setup_logging(verbose=args.verbose)
    try:
        return int(args.func(args) or 0)
    except KeyboardInterrupt:
        print(file=sys.stderr)
        _err("已中断")
        return 130


if __name__ == "__main__":
    sys.exit(main())
