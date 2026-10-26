"""
开头钩子与可读性检查（短视频留存规则）。

规则（来自运营要求）：
1. 具体、直接：用观众熟悉的名字、数字或情绪触发词，不要空泛表述。
2. 词汇简单到小学三年级能读懂；最有意思的细节放在前 3 秒。
3. 删掉无关的废话；不要太早揭晓答案；用"开放式悬念"让人看到最后。

hook_report() 返回逐条发现（fix = 必须改，tip = 建议）；planner 把 fix 级问题回传给 LLM 修，
`autoclip whatif check` 打印完整报告。只做启发式文本检查，不调用模型。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from .schema import Storyboard

READING_GRADE_MAX = 9.0      # 单条字幕 Flesch-Kincaid 上限（短句上 FK 噪声大，只拦明显难的）
READING_GRADE_FIX = 6.5      # 全片字幕合起来算的年级超过这个 = 必须改
READING_GRADE_TARGET = 4.5   # 全片超过这个给建议（目标 ~3 年级）
MAX_WORDS = 16               # 单条字幕词数上限
HOOK_SECONDS = 3.0           # 最有意思的细节必须在这之前出现
LOOP_WINDOW = 3              # 前几条字幕里必须有一个悬念

TRIGGERS = {
    "never", "every", "everyone", "nobody", "all", "only", "first", "last", "gone", "vanish", "vanished", "die", "dies",
    "dead", "death", "kill", "kills", "danger", "deadly", "secret", "impossible", "instantly", "overnight", "forever",
    "suddenly", "worst", "biggest", "fastest", "shock", "scary", "insane", "disappear", "disappears", "disappeared",
    "explode", "explodes", "collapse", "collapses", "starve", "survive", "end", "ends", "fail", "failed", "broke",
    "billion", "million", "trillion", "thousand", "hundred", "half", "zero", "double", "twice",
}
NUMBER_WORDS = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "twelve", "twenty",
                "hundred", "thousand", "million", "billion", "trillion", "half", "double", "twice"}
LOOP_PATTERNS = [r"\?", r"\bbut\b", r"\buntil\b", r"\bwait\b", r"\bhere'?s\b", r"\bworst\b", r"\bwhat happens\b",
                 r"\bby the end\b", r"\bsoon\b", r"\bthen\b", r"\bnext\b", r"\bstill\b", r"\bnot yet\b", r"\bthe catch\b",
                 r"\bnobody\b", r"\bwatch\b", r"\bguess\b"]
FLUFF = ["basically", "actually", "interestingly", "it's worth noting", "it is worth noting", "needless to say",
         "in conclusion", "to sum up", "as we all know", "let's dive", "let's take a look", "without further ado",
         "in this video", "fun fact", "believe it or not", "so, ", "you know", "kind of", "sort of", "very very"]
PAYOFF_EARLY = ["in conclusion", "to sum up", "the answer is", "in the end", "the final", "so the answer"]


@dataclass
class Finding:
    level: str      # "fix" | "tip"
    rule: str       # specific | reading | first3s | fluff | open_loop | payoff
    where: str      # "intro.title" / "beats[3].caption" / "storyboard"
    msg: str

    def __str__(self) -> str:
        return f"[{self.level}] {self.where}: {self.msg}"


# ------------------------------------------------------------------ 文本工具
_WORD = re.compile(r"[A-Za-z']+")


def words(text: str) -> List[str]:
    return _WORD.findall(text.replace("*", ""))


def syllables(word: str) -> int:
    w = word.lower().strip("'")
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r"(?:[^laeiouy]es|[^laeiouy]ed|[^laeiouy]e)$", "", w)
    w = re.sub(r"^y", "", w)
    return max(1, len(re.findall(r"[aeiouy]{1,2}", w)))


def reading_grade(text: str) -> float:
    """Flesch-Kincaid 年级。数字不计入难词（"8 billion" 对小朋友也好懂）。"""
    ws = words(text)
    if not ws:
        return 0.0
    sentences = max(1, len(re.findall(r"[.!?]+", text)) or 1)
    syl = sum(syllables(w) for w in ws)
    return 0.39 * (len(ws) / sentences) + 11.8 * (syl / len(ws)) - 15.59


def hard_words(text: str, proper: bool = False) -> List[str]:
    """三个音节以上、且不是专有名词（大写开头，句首除外）的词。"""
    out = []
    for i, w in enumerate(words(text)):
        if syllables(w) >= 4 or (syllables(w) == 3 and len(w) >= 10):
            if not proper and w[0].isupper() and i > 0:
                continue
            out.append(w)
    return out


def is_specific(text: str) -> bool:
    """有数字 / 数量词 / 专有名词 / 情绪触发词。"""
    t = text.replace("*", "")
    if re.search(r"\d", t):
        return True
    ws = words(t)
    low = {w.lower() for w in ws}
    if low & NUMBER_WORDS or low & TRIGGERS:
        return True
    # 句中大写词 = 名字（Elon Musk / Pretoria / WHO）
    return any(w[0].isupper() for w in ws[1:] if w.lower() not in {"i", "what", "if"})


def has_loop(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in LOOP_PATTERNS)


# ------------------------------------------------------------------ 检查
POV_HOOK_WORDS = 10      # 顶部 POV 钩子最多几个词
POV_YOU_SHARE = 0.6      # pov 字幕里至少多少比例对"你"说话


def hook_report(sb: Storyboard) -> List[Finding]:
    f: List[Finding] = []
    pov = sb.format == "pov" and sb.pov is not None
    # pov：顶部 "POV: …" 从第 0 帧就在（闭着眼时就打字出来），它就是开头钩子；没有片头卡
    title = ("POV: " + sb.pov.text) if pov else sb.intro.title if sb.intro and sb.intro.style != "none" else ""
    caps = [(i, b.caption) for i, b in enumerate(sb.beats) if b.caption]

    # 规则 2b：最有意思的细节在前 3 秒——标题卡从 0 秒开始，且标题本身要够具体
    if not title:
        f.append(Finding("fix", "first3s", "intro", "No title card, so there is no hook in the first 3 seconds. Add intro.title."))
    else:
        if not pov and sb.intro.duration > HOOK_SECONDS + 0.3:
            f.append(Finding("tip", "first3s", "intro.duration", f"Title card lasts {sb.intro.duration:.1f}s (over {HOOK_SECONDS:.0f}s). Shorten it so the first shot lands sooner."))
        if not is_specific(title):
            f.append(Finding("fix", "specific", "intro.title",
                             f"Title \"{title}\" is not specific. Add a number, a name or an emotional trigger (every / never / 8 billion / gone)."))
    if caps and not is_specific(caps[0][1]) and not has_loop(caps[0][1]):
        f.append(Finding("fix", "first3s", f"beats[{caps[0][0]}].caption",
                         "First caption is flat. Put the most interesting detail or number of the whole video here."))

    if pov:
        if len(words(sb.pov.text)) > POV_HOOK_WORDS:
            f.append(Finding("fix", "first3s", "pov.text", f"POV hook has {len(words(sb.pov.text))} words; keep it to {POV_HOOK_WORDS} or fewer so it types out in about a second."))
        you = sum(1 for _, c in caps if re.search(r"\b(you|your|you're|yourself)\b", c.lower())) / max(1, len(caps))
        if caps and you < POV_YOU_SHARE:
            f.append(Finding("fix", "pov", "storyboard", f"Only {you:.0%} of captions talk to \"you\". POV videos happen to the viewer: "
                             "\"You grab the bed.\" \"Your phone floats away.\" (aim for most captions)."))

    # 规则 1：具体
    if caps:
        spec = sum(1 for _, c in caps if is_specific(c)) / len(caps)
        if spec < 0.4:
            f.append(Finding("tip", "specific", "storyboard", f"Only {spec:.0%} of captions have a number, name or emotional trigger (aim for 40%+)."))

    # 规则 2a：三年级阅读水平
    for i, c in caps:
        g = reading_grade(c)
        hw = hard_words(c)
        if g > READING_GRADE_MAX or len(hw) >= 2 or len(words(c)) > MAX_WORDS:
            f.append(Finding("fix", "reading", f"beats[{i}].caption",
                             f"Too hard to read (about grade {max(g, 0):.0f})" + (f"; hard words: {', '.join(hw)}" if hw else "") + ". Use short words and short sentences."))
    if caps:
        whole = reading_grade(" ".join(c if c.rstrip()[-1:] in ".!?" else c + "." for _, c in caps))
        if whole > READING_GRADE_FIX:
            f.append(Finding("fix", "reading", "storyboard", f"Script reads at about grade {whole:.1f}; rewrite with shorter words and sentences (aim for grade 3)."))
        elif whole > READING_GRADE_TARGET:
            f.append(Finding("tip", "reading", "storyboard", f"Script reads at about grade {whole:.1f}; aim for grade 3."))

    # 规则 3a：废话
    for i, c in caps:
        low = c.lower()
        hit = [w for w in FLUFF if w in low]
        if hit:
            f.append(Finding("fix", "fluff", f"beats[{i}].caption", f"Cut the fluff: {', '.join(hit)}."))

    # 规则 3b：不要太早揭晓
    half = (len(caps) + 1) // 2
    for i, c in caps[:half]:
        if any(p in c.lower() for p in PAYOFF_EARLY):
            f.append(Finding("fix", "payoff", f"beats[{i}].caption", "Gives away the payoff in the first half. Save the answer for the end."))

    # 规则 3c：开放式悬念
    early = [c for _, c in caps[:LOOP_WINDOW]]   # 标题本身总是问句，不算悬念
    if caps and not any(has_loop(c) for c in early):
        f.append(Finding("fix", "open_loop", "storyboard",
                         f"No open loop in the first {LOOP_WINDOW} captions. Ask a question, or tease with \"but... / until... / here's the worst part\", and only answer it at the end."))
    end = sb.outro.end if sb.outro else None
    if not end or end.kind != "question":
        f.append(Finding("tip", "open_loop", "outro.end", "End on a question card (kind=question) to drive comments."))
    return f


def hook_problems(sb: Storyboard) -> List[str]:
    """fix 级问题，格式化给 LLM 修正。"""
    return [f"hook rule ({x.rule}) at {x.where}: {x.msg}" for x in hook_report(sb) if x.level == "fix"]


def hook_score(sb: Storyboard, report: Optional[List[Finding]] = None) -> int:
    r = hook_report(sb) if report is None else report
    return max(0, 100 - 12 * sum(x.level == "fix" for x in r) - 4 * sum(x.level == "tip" for x in r))
