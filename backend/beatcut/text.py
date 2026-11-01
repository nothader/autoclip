"""文字叠加：「低曝光遮罩 + 白字」的无脸 aesthetic 版式。

每句文案占成片的一段，换句只发生在切点（拍点）上；每句出现时 0.2 s 淡入。
默认字体是仓库自带的 Source Serif 4 斜体（OFL），中日韩文字自动换成系统 CJK 字体。
"""
from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

FONT_DIR = Path(__file__).resolve().parents[1] / "whatif" / "web" / "fonts"
TEXT_STYLES = ("serif-italic", "serif", "sans")
TEXT_POSITIONS = ("center", "lower", "upper")
FADE_IN = 0.2
_CJK = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af\uff00-\uffef]")

_SANS_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/SFNS.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def has_cjk(s: str) -> bool:
    return bool(_CJK.search(s))


def resolve_font(style: str, text: str = "", override: Optional[str] = None) -> Path:
    if override:
        p = Path(override).expanduser()
        if not p.exists():
            raise FileNotFoundError(f"字体不存在：{p}")
        return p
    if has_cjk(text):
        from backend.services.publish_export import resolve_cjk_font
        cjk = resolve_cjk_font()
        if cjk:
            return cjk
    if style == "sans":
        for c in _SANS_CANDIDATES:
            if Path(c).exists():
                return Path(c)
    name = "SourceSerif4-Italic.ttf" if style == "serif-italic" else "SourceSerif4.ttf"
    return FONT_DIR / name


def wrap(text: str, width_px: int, font_px: int) -> List[str]:
    """按画面宽度折行（留 16% 边距）。CJK 按字数，拉丁文按单词。显式 \\n 保留。"""
    out: List[str] = []
    for para in text.replace("\\n", "\n").split("\n"):
        para = para.strip()
        if not para:
            continue
        if has_cjk(para):
            per = max(4, int(width_px * 0.84 / font_px))
            out += [para[i:i + per] for i in range(0, len(para), per)]
        else:
            per = max(8, int(width_px * 0.84 / (font_px * 0.5)))
            out += textwrap.wrap(para, per) or [para]
    return out


def assign_lines(frames: Sequence[int], lines: Sequence[str]) -> List[Tuple[str, bool]]:
    """把文案分给镜头：每句占约 1/N 时长，边界吸附到最近的切点。返回每个镜头的 (文案, 是否这句的第一镜)。"""
    lines = [x for x in lines if x and x.strip()]
    n = len(frames)
    if not lines or n == 0:
        return [("", False)] * n
    starts = [0]
    for f in frames[:-1]:
        starts.append(starts[-1] + f)
    total = starts[-1] + frames[-1]
    k = min(len(lines), n)
    if len(lines) > n:  # 句子比镜头多：多出来的并到最后一句
        lines = list(lines[: n - 1]) + [" / ".join(lines[n - 1:])]
    first_shot = [0]
    for i in range(1, k):
        target = total * i / k
        j = min(range(n), key=lambda s: abs(starts[s] - target))
        j = max(j, first_shot[-1] + 1)
        first_shot.append(min(j, n - (k - i)))
    out: List[Tuple[str, bool]] = []
    li = 0
    for s in range(n):
        while li + 1 < k and s >= first_shot[li + 1]:
            li += 1
        out.append((lines[li], s == first_shot[li]))
    return out


def _escape(p: Path) -> str:
    return str(p.resolve()).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")


def drawtext_chain(text: str, *, W: int, H: int, style: str, pos: str, size: float, fade_in: bool,
                   workdir: Path, key: str, font: Optional[str] = None) -> List[str]:
    """一句文案 → 若干 drawtext（每行一个，各自居中）。文字写进 textfile，避开 ffmpeg 转义。"""
    if not text.strip():
        return []
    font_px = max(12, int(round(W * 0.058 * size)))
    lines = wrap(text, W, font_px)
    if not lines:
        return []
    fontfile = resolve_font(style, text, font)
    line_h = int(font_px * 1.32)
    block = line_h * len(lines)
    top = {"center": (H - block) / 2, "upper": H * 0.16, "lower": H * 0.74 - block}.get(pos, (H - block) / 2)
    alpha = f":alpha='min(1\\,t/{FADE_IN})'" if fade_in else ""
    shadow = max(1, font_px // 24)
    out = []
    for i, line in enumerate(lines):
        tf = workdir / f"text_{key}_{i}.txt"
        tf.write_text(line, encoding="utf-8")
        out.append(
            f"drawtext=fontfile='{_escape(fontfile)}':textfile='{_escape(tf)}':reload=0"
            f":fontsize={font_px}:fontcolor=white:x=(w-text_w)/2:y={int(top + i * line_h)}"
            f":shadowcolor=black@0.35:shadowx=0:shadowy={shadow}{alpha}"
        )
    return out
