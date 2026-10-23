"""
画面质量检查：把之前每支视频踩过的坑变成规则（和 hooks.py 一样只做启发式检查，不调模型）。

- 克隆人：同一布景里两个 person 的 outfit + seed + 颜色完全一样 → 长得一模一样
- 单调：连续好几段同一个场景 + 同一个机位 / 同一套布景（"no sex" 那支"无聊"的原因）
- 静止：自定义布景里没有任何动的东西（没有 animate、人不走、没有特效）
- 空镜：自定义布景没有物体也没有地面
- 时长：竖屏短视频按 1.8x 节奏压完后不到 1 分钟；横屏长视频不到 4 分钟
- 风格配套：witness 风格却不用 witness 机位 / 没有递增指标

quality_report() 返回 hooks.Finding 列表；fix 级问题会和钩子问题一起回传给 planner 修。
"""
from __future__ import annotations

import json
import re
from collections import Counter
from typing import List, Optional

from .hooks import Finding
from .schema import Storyboard

SHORT_MIN_SECONDS = 61.0       # 竖屏短视频（按节奏压缩后）至少这么长：1 分钟以上，留 1 秒余量
LONG_MIN_SECONDS = 240.0       # 横屏长视频
SAME_SHOT_RUN = 3              # 连续多少段同场景同机位算单调（witness 风格除外）
SAME_SET_RUN = 2               # 连续多少段完全相同的自定义布景算单调
CAMERA_SHARE_TIP = 0.55        # 某个机位占比超过这个给建议
NO_EARTH_SCENES = ("globe", "orbit")   # 用户要求：视频里不要地球仪 / 太空里的地球（deep_space 已不画地球）
NO_EARTH_KINDS = ("earth",)
MOVING_ACTIONS = {"walk", "run", "sprint", "fly", "float", "fall", "handwalk", "footeat"}

# 题目关键词 → 推荐风格（planner 没明确选风格时用；也写进提示里当建议）
STYLE_HINTS = [
    ("witness", r"hurricane|tornado|storm|snow|blizzard|volcano|erupt|tsunami|flood|earthquake|asteroid|meteor|heat ?wave|"
                r"ice age|colder|hotter|rain(ed|s)? (for|forever)|sun (went|goes) out|sky|weather|nuke|nuclear|wildfire"),
    ("retro", r"\b(game|games|gaming|video ?games?|minecraft|internet|robots?|ai|matrix|wifi|hackers?|8-bit|pixel)\b"),
    ("toon", r"\b(animal|animals|dog|cat|food|fruit|pizza|candy|baby|babies|kids?|feet|hands|naked|clothes|talk|tiny|giant)\b"),
    ("cinematic", r"\b(war|empire|rome|roman|egypt|history|historical|never existed|died|death|king|queen|ancient|jesus|"
                  r"president|world war|titanic|plague)\b"),
    ("bold", r"\b(rich|money|billion|million|sex|body|bbl|surgery|men|women|race|black|white|swap|everyone|nobody)\b"),
]


def auto_style(premise: str) -> str:
    """按题目挑一个风格（没有命中关键词 = calm）。"""
    p = premise.lower()
    for style, pat in STYLE_HINTS:
        if re.search(pat, p):
            return style
    return "calm"


def _paced_seconds(sb: Storyboard) -> float:
    from .model import compile_plan
    return float(compile_plan(sb.model_copy(update={"pace": sb.pace or 1.8}))["duration"])


def _set_key(b) -> Optional[str]:
    if b.scene != "custom" or not b.env or not b.env.set:
        return None
    return json.dumps(b.env.set.model_dump(), sort_keys=True)


def quality_report(sb: Storyboard) -> List[Finding]:
    f: List[Finding] = []
    style = sb.theme.style
    beats = sb.beats

    # 不要地球（用户明确要求）：globe / orbit / deep_space 场景、自定义布景里的 earth 物体
    for i, b in enumerate(beats):
        kinds = {o.kind for o in b.env.set.objects} if (b.scene == "custom" and b.env and b.env.set) else set()
        if b.scene in NO_EARTH_SCENES or kinds & set(NO_EARTH_KINDS):
            f.append(Finding("fix", "no_globe", f"beats[{i}]", "No globes or Earth-from-space shots. Show the place itself instead "
                             "(a city, street, desert, coast, map, or a custom set)."))

    # 克隆人
    for i, b in enumerate(beats):
        if b.scene != "custom" or not b.env or not b.env.set:
            continue
        seen = Counter((o.outfit, o.seed, o.color, o.color2) for o in b.env.set.objects if o.kind == "person" and o.count == 1)
        dup = [k for k, n in seen.items() if n > 1]
        if dup:
            f.append(Finding("fix", "clones", f"beats[{i}].env.set", f"{sum(seen[k] for k in dup)} people share outfit+seed+colors, so they "
                             "look like identical clones. Give each person a different seed, outfit or color."))

    # 单调：同场景同机位 / 同一套布景连续出现
    run = 1
    for i in range(1, len(beats)):
        a, b = beats[i - 1], beats[i]
        same = a.scene == b.scene and a.camera == b.camera and a.scene != "custom"
        run = run + 1 if same else 1
        if run == SAME_SHOT_RUN and style != "witness":
            f.append(Finding("fix", "monotony", f"beats[{i - SAME_SHOT_RUN + 1}..{i}]",
                             f"{SAME_SHOT_RUN} shots in a row with scene={b.scene} and camera={b.camera}. Change the camera, scene, "
                             "time of day or weather so every cut looks different."))
    run = 1
    for i in range(1, len(beats)):
        k0, k1 = _set_key(beats[i - 1]), _set_key(beats[i])
        run = run + 1 if (k0 is not None and k0 == k1 and beats[i - 1].camera == beats[i].camera) else 1
        if run == SAME_SET_RUN:
            f.append(Finding("fix", "monotony", f"beats[{i - 1}..{i}]", "The same custom set with the same camera twice in a row. "
                             "Change the camera, rearrange the set or add an animation so the cut is visible."))
    if style != "witness" and len(beats) >= 6:
        cam, n = Counter(b.camera for b in beats).most_common(1)[0]
        if n / len(beats) > CAMERA_SHARE_TIP:
            f.append(Finding("tip", "variety", "storyboard", f"camera \"{cam}\" is used for {n}/{len(beats)} shots; mix in other angles."))

    # 静止 / 空镜
    for i, b in enumerate(beats):
        if b.scene != "custom" or not b.env or not b.env.set:
            continue
        objs = b.env.set.objects
        if not objs and b.env.set.ground == "none":
            f.append(Finding("fix", "empty", f"beats[{i}].env.set", "Empty set: no objects and no ground. Build something to look at."))
            continue
        moving = (any(o.animate for o in objs) or any(o.kind == "person" and o.action in MOVING_ACTIONS for o in objs)
                  or any(o.kind in ("particles", "flame") for o in objs) or b.effects or b.camera in ("orbit", "dolly", "pov"))
        if not moving and b.duration >= 3.0:
            f.append(Finding("tip", "static", f"beats[{i}].env.set", "Nothing moves in this shot. Add an animate (grow/move/spin/bob), "
                             "a walking person, particles or an effect."))

    # 时长
    secs = _paced_seconds(sb)
    vertical = sb.height > sb.width
    if vertical and secs < SHORT_MIN_SECONDS:
        f.append(Finding("fix", "length", "storyboard", f"About {secs:.0f}s at the 1.8x pace; vertical shorts should run 1 minute or more. "
                         "Add more beats (more events, more places), not longer ones."))
    if not vertical and secs < LONG_MIN_SECONDS:
        f.append(Finding("tip", "length", "storyboard", f"About {secs:.0f}s; long-form landscape videos work best at 5-6 minutes."))

    # 风格配套
    if style == "witness":
        if sum(b.camera == "witness" for b in beats) < len(beats) / 2:
            f.append(Finding("tip", "style", "storyboard", "witness style: use camera \"witness\" on most beats (one fixed eyewitness view)."))
        if not sb.clock or not any(b.time for b in beats):
            f.append(Finding("fix", "style", "storyboard", "witness style needs an escalating metric: clock + beat.time (+ time_label / time_sub)."))
    return f


def quality_problems(sb: Storyboard) -> List[str]:
    return [f"visual rule ({x.rule}) at {x.where}: {x.msg}" for x in quality_report(sb) if x.level == "fix"]
