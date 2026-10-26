"""
电影感：镜头运动、转场、节奏（flow）、调色（palette），以及跟着它们走的音效。

每段的 move / transition 可以在分镜里写死；不写（None）时这里按 flow + 风格 + 段号确定性地挑，
保证相邻两段不重复、整片有起伏。所有选择都是标题 + 段号的纯函数，渲染可复现。

- move：镜头在本段内怎么动（swoop_in 从高远处俯冲进来、arc 绕主体转、whip 甩镜……），渲染端按 frac 缓动
- transition：进入本段的方式（whip 甩镜糊化、flash 白闪、zoom 冲推、dip 黑场、glitch 故障），覆盖本段开头 ~0.3s
- flow：整片节奏（build 越剪越快、punchy 快切重拍、slowburn 先慢后爆、rollercoaster 忽快忽慢、steady 平稳）
- palette：整片调色（warm / cool / teal_orange / vivid / pastel / mono / noir）
"""
from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, List, Optional

MOVES = ["none", "swoop_in", "swoop_out", "crane_up", "crane_down", "arc_left", "arc_right", "push_in", "pull_out",
         "whip", "dutch", "drone_rise", "fly_by", "spiral"]
TRANSITIONS = ["cut", "whip", "flash", "zoom", "dip", "glitch", "blink"]
FLOWS = ["steady", "build", "punchy", "slowburn", "rollercoaster"]
PALETTES = ["natural", "warm", "cool", "teal_orange", "vivid", "pastel", "mono", "noir"]

TR_IN = 0.32      # 转场覆盖本段开头多少秒（原始时间，不随节奏缩）
TR_OUT = 0.12     # 甩镜 / 冲推在上一段末尾的"出"半程

# 每种 flow 偏好的镜头运动和转场（权重）
FLOW_MOVES = {
    "steady": {"arc_left": 3, "arc_right": 3, "push_in": 3, "crane_up": 2, "pull_out": 2, "drone_rise": 1, "none": 1},
    "build": {"push_in": 3, "arc_left": 2, "arc_right": 2, "crane_up": 2, "swoop_in": 2, "fly_by": 2, "whip": 1, "spiral": 1},
    "punchy": {"swoop_in": 3, "whip": 3, "fly_by": 3, "push_in": 3, "spiral": 2, "dutch": 2, "arc_left": 1, "arc_right": 1},
    "slowburn": {"crane_up": 3, "drone_rise": 3, "pull_out": 3, "arc_left": 2, "arc_right": 2, "push_in": 2, "crane_down": 2},
    "rollercoaster": {"swoop_in": 3, "swoop_out": 3, "spiral": 3, "dutch": 2, "fly_by": 2, "crane_down": 2, "arc_left": 1, "arc_right": 1},
}
FLOW_TRANS = {
    "steady": {"cut": 4, "zoom": 2, "whip": 2, "dip": 1},
    "build": {"cut": 3, "whip": 2, "zoom": 2, "flash": 1},
    "punchy": {"flash": 3, "whip": 3, "zoom": 3, "glitch": 1, "cut": 1},
    "slowburn": {"cut": 3, "dip": 3, "zoom": 1},
    "rollercoaster": {"whip": 3, "zoom": 2, "flash": 2, "dip": 1, "glitch": 1, "cut": 1},
}
# 风格对转场的偏好（乘到权重上）
STYLE_TRANS = {
    "retro": {"glitch": 3.0, "dip": 0.3},
    "cinematic": {"dip": 2.0, "glitch": 0.0, "flash": 0.6},
    "calm": {"glitch": 0.0, "flash": 0.5, "dip": 1.5},
    "toon": {"whip": 1.6, "zoom": 1.6, "glitch": 0.3},
    "bold": {"flash": 1.5, "zoom": 1.5},
    "witness": {"whip": 0.0, "zoom": 0.0, "glitch": 0.0, "flash": 0.3, "cut": 3.0, "dip": 1.5},
    "bodycam": {"cut": 3.0, "glitch": 2.0, "whip": 1.2, "zoom": 0.0, "flash": 0.0, "dip": 0.4},   # 实拍感：硬切 + 数字掉帧
}
STYLE_PALETTES = {
    "calm": ["natural", "cool", "pastel", "warm"],
    "bold": ["vivid", "teal_orange", "warm", "natural"],
    "cinematic": ["teal_orange", "warm", "noir", "mono", "cool"],
    "toon": ["vivid", "pastel", "natural", "warm"],
    "retro": ["vivid", "cool", "natural"],
    "witness": ["natural", "cool", "warm"],
    "bodycam": ["natural", "cool"],   # 着色器自己做传感器调色，别再叠重的滤镜
}
# CSS 滤镜（叠在风格自带调色后面）
PALETTE_CSS = {
    "natural": "",
    "warm": "sepia(0.18) saturate(1.12) hue-rotate(-6deg)",
    "cool": "saturate(0.92) hue-rotate(8deg) brightness(1.02)",
    "teal_orange": "sepia(0.12) saturate(1.28) contrast(1.06) hue-rotate(-4deg)",
    "vivid": "saturate(1.4) contrast(1.07)",
    "pastel": "saturate(0.78) brightness(1.07) contrast(0.93)",
    "mono": "grayscale(0.82) contrast(1.12)",
    "noir": "grayscale(1) contrast(1.32) brightness(0.94)",
}


def _h(*parts: Any) -> float:
    """确定性伪随机 [0,1)。"""
    d = hashlib.sha1("|".join(str(p) for p in parts).encode()).digest()
    return int.from_bytes(d[:6], "big") / float(1 << 48)


def _pick(weights: Dict[str, float], u: float, avoid: Optional[str] = None) -> str:
    items = [(k, w) for k, w in weights.items() if w > 0 and k != avoid] or [(k, w) for k, w in weights.items() if w > 0]
    total = sum(w for _, w in items)
    acc = 0.0
    for k, w in items:
        acc += w / total
        if u < acc:
            return k
    return items[-1][0]


def resolve_flow(sb) -> str:
    f = sb.theme.flow
    return f if f in FLOWS else FLOWS[int(_h(sb.title, "flow") * len(FLOWS))]


def resolve_palette(sb) -> str:
    p = sb.theme.palette
    if p in PALETTES:
        return p
    opts = STYLE_PALETTES.get(sb.theme.style, PALETTES)
    return opts[int(_h(sb.title, "palette") * len(opts))]


def flow_factor(flow: str, i: int, n: int) -> float:
    """节奏：每段时长乘的系数（只在 pace≠1 时用，见 model.apply_pace）。"""
    x = i / max(1, n - 1)
    if flow == "build":
        return 1.25 - 0.5 * x
    if flow == "punchy":
        return 1.3 if i % 5 == 4 else 0.82
    if flow == "slowburn":
        return 1.3 if x < 0.4 else 0.85
    if flow == "rollercoaster":
        return 1.0 + 0.3 * math.sin(i * 1.3)
    return 1.0


def assign(sb) -> List[Dict[str, Any]]:
    """每段的 {"move", "tr", "mk"}（mk = 运动幅度 0.5–1）。分镜里写了就用写的。"""
    flow = resolve_flow(sb)
    style = sb.theme.style
    n = len(sb.beats)
    out = []
    prev_move = prev_tr = None
    chapter = None
    for i, b in enumerate(sb.beats):
        x = i / max(1, n - 1)
        # 镜头运动
        if b.move:
            move = b.move
        elif b.camera in ("witness", "eyes") or b.scene == "map":   # 目击者 / 第一人称视角由自己的头部运动驱动；地图不用运镜
            move = "none"
        else:
            w = dict(FLOW_MOVES[flow])
            if flow == "build":   # 越往后越猛
                for k in ("swoop_in", "fly_by", "whip", "spiral"):
                    w[k] = w.get(k, 0) * (0.3 + 2.2 * x)
            if b.scene == "globe":
                w = {k: v for k, v in w.items() if k in ("swoop_in", "swoop_out", "arc_left", "arc_right", "push_in", "pull_out", "spiral", "none")}
            move = _pick(w, _h(sb.title, i, "move"), avoid=prev_move)
        # 转场（第一段在标题下，不转场）
        new_ch = b.chapter is not None and b.chapter != chapter
        chapter = b.chapter or chapter
        if b.transition:
            tr = b.transition
        elif i == 0:
            tr = "cut"
        else:
            w = dict(FLOW_TRANS[flow])
            for k, m in STYLE_TRANS.get(style, {}).items():
                w[k] = w.get(k, 0) * m if k in w else (1.0 * m if m > 1 else 0)
            if flow == "build":
                w["cut"] = w.get("cut", 0) * (1.6 - 1.3 * x)
            if sb.format == "pov":   # 第一人称：眨眼、转头（甩）、黑场；不用闪白 / 冲推
                w = {"blink": 4, "cut": 3, "whip": 2, "dip": 1, "glitch": 0.5 if style != "calm" else 0}
            if new_ch:   # 新章节：更重的转场
                w = {"flash": 2, "dip": 2, "zoom": 1} if style not in ("witness",) else {"dip": 1}
            tr = _pick(w, _h(sb.title, i, "tr"), avoid=prev_tr if prev_tr != "cut" else None)
            if sb.format == "pov" and not new_ch and i >= 3 and "blink" not in [o["tr"] for o in out[-2:]]:
                tr = "blink"   # 眨眼是 pov 的标志：至少每三刀一次
        mk = 0.55 + 0.45 * _h(sb.title, i, "mk")
        if flow in ("punchy", "rollercoaster"):
            mk = min(1.0, mk + 0.2)
        if flow == "slowburn" and x < 0.4:
            mk *= 0.6
        out.append({"move": move, "tr": tr, "mk": round(mk, 3)})
        prev_move, prev_tr = move, tr
    return out


def transition_frame(tr: str, lt: float) -> Optional[Dict[str, Any]]:
    """本段开头 lt 秒处的转场状态 {k, p}（p: 0→1 进度）；过了 TR_IN 返回 None。"""
    if tr in (None, "cut") or lt >= TR_IN:
        return None
    return {"k": tr, "p": round(lt / TR_IN, 3)}


def transition_out(next_tr: Optional[str], left: float) -> Optional[Dict[str, Any]]:
    """上一段最后 left 秒（到下一段开始的剩余时间）的"出"半程：甩镜 / 冲推 / 故障先起势。"""
    if next_tr not in ("whip", "zoom", "glitch", "blink") or left >= TR_OUT:
        return None
    return {"k": next_tr, "p": round(1 - left / TR_OUT, 3), "out": True}


# ------------------------------------------------------------------ 声音
MOVE_SFX = {
    "swoop_in": [("whoosh", 0.0, 0.5, 1.4)], "swoop_out": [("whoosh", 0.1, 0.4, 1.5)], "fly_by": [("whoosh", 0.15, 0.5, 1.0)],
    "whip": [("whoosh", 0.0, 0.45, 0.6)], "spiral": [("whoosh", 0.1, 0.35, 1.6)],
    "drone_rise": [("riser", 0.0, 0.22, 2.0)], "crane_up": [("riser", 0.0, 0.15, 1.6)],
    "push_in": [("whoosh", 0.0, 0.18, 0.7)], "pull_out": [("whoosh", 0.0, 0.15, 0.9)],
}
TRANS_SFX = {
    "whip": [("whoosh", -0.12, 0.55, 0.55)], "flash": [("impact", 0.0, 0.7, None), ("boom", 0.0, 0.25, None)],
    "zoom": [("whoosh", -0.1, 0.35, 0.45)], "dip": [("drop", 0.0, 0.3, None)], "glitch": [("glitch", -0.05, 0.6, None)],
}
EFFECT_SFX = {
    "explosion": [("boom", 0.05, 1.0, None), ("debris", 0.25, 0.7, None)],
    "sparks": [("sparkle", 0.0, 0.45, "beat")],
    "confetti": [("pop", 0.0, 0.7, None), ("pop", 0.18, 0.5, None), ("swell", 0.0, 0.5, None)],
    "lightning": [("crack", 0.0, 0.9, None), ("thunder", 0.2, 0.9, None)],
    "rays": [("shimmer", 0.0, 0.5, None)],
    "glitch": [("glitch", 0.1, 0.6, None), ("glitch", 0.9, 0.4, None)],
    "bloom": [("shimmer", 0.0, 0.35, None)],
}


def cinema_sfx(assigned: List[Dict[str, Any]], beats_secs, effects_of) -> List[Dict[str, Any]]:
    """镜头运动 / 转场 / 新特效自动配声。beats_secs: [(start, duration)]；effects_of(i) -> 该段特效列表。"""
    ev: List[Dict[str, Any]] = []

    def add(kind, t, gain, dur):
        e = {"type": kind, "t": round(max(0.0, t), 3), "gain": gain}
        if dur is not None:
            e["dur"] = dur
        ev.append(e)

    for i, (a, (start, dur)) in enumerate(zip(assigned, beats_secs)):
        for kind, at, gain, d in TRANS_SFX.get(a["tr"], []) if i > 0 else []:
            add(kind, start + at, gain, d)
        for kind, at, gain, d in MOVE_SFX.get(a["move"], []):
            add(kind, start + at, gain * (0.6 + 0.4 * a["mk"]), min(d, dur) if d else None)
        for fx in effects_of(i):
            for kind, at, gain, d in EFFECT_SFX.get(fx, []):
                add(kind, start + at, gain, dur if d == "beat" else d)
    return ev


# ------------------------------------------------------------------ 多样性：近期历史
HISTORY_KEEP = 30


def history_path():
    from backend.core.path_utils import get_data_directory
    return get_data_directory() / "whatif" / "history.json"


def load_history() -> List[Dict[str, Any]]:
    import json
    try:
        return json.loads(history_path().read_text(encoding="utf-8"))[-HISTORY_KEEP:]
    except Exception:  # noqa: BLE001  没有历史 / 坏文件 = 从头来
        return []


def record_history(sb, plan_theme: Dict[str, Any]) -> None:
    import json
    import time
    h = load_history() + [{"title": sb.title, "style": plan_theme.get("style"), "flow": plan_theme.get("flow"),
                           "palette": plan_theme.get("palette"), "vertical": sb.height > sb.width, "t": int(time.time())}]
    p = history_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(h[-HISTORY_KEEP:], ensure_ascii=False, indent=1), encoding="utf-8")


def recent(history: List[Dict[str, Any]], key: str, n: int = 2) -> List[str]:
    return [h.get(key) for h in history[-n:] if h.get(key)]


def resolve_variety(sb, history: List[Dict[str, Any]]):
    """flow / palette 为 auto 时，挑一个和最近几支视频都不一样的（按标题哈希排序，确定性）。"""
    theme = sb.theme
    up = {}
    if theme.flow not in FLOWS:
        avoid = set(recent(history, "flow", 2))
        order = sorted(FLOWS, key=lambda f: _h(sb.title, "flow", f))
        up["flow"] = next((f for f in order if f not in avoid), order[0])
    if theme.palette not in PALETTES:
        avoid = set(recent(history, "palette", 3))
        opts = STYLE_PALETTES.get(theme.style, PALETTES)
        order = sorted(opts, key=lambda p: _h(sb.title, "palette", p))
        up["palette"] = next((p for p in order if p not in avoid), order[0])
    return sb.model_copy(update={"theme": theme.model_copy(update=up)}) if up else sb
