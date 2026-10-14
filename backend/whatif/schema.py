"""
What-if 视频的分镜（storyboard）结构。

LLM 只负责「写」：选场景、镜头、文案、里程碑；所有数字（速度、距离、倍率、
里程碑出现的时刻）由 model.py 按增长模型算出来，文案里的数字用占位符引用，
保证画面上的数据前后一致、不会编造。
"""
from __future__ import annotations

from typing import List, Literal, Optional, Tuple

from pydantic import BaseModel, Field, field_validator, model_validator

SceneName = Literal["city", "highway", "desert", "ocean", "sky", "orbit", "deep_space", "lab", "void"]
CameraName = Literal["follow", "front", "side", "low_front", "wide", "aerial", "orbit", "far", "closeup"]
SubjectType = Literal["runner", "ball", "car", "cube", "rocket", "none"]
Action = Literal["idle", "walk", "run", "sprint", "float", "fly"]
Effect = Literal[
    "motion_blur", "heat", "plasma", "speedlines", "shake", "shockwave",
    "dust", "vapor_cone", "glow", "flash",
]
SfxType = Literal["whoosh", "boom", "riser", "impact", "tick", "swell", "drop"]
QuantityKind = Literal["speed", "length", "mass", "temperature", "count", "generic"]

SCENES: Tuple[str, ...] = SceneName.__args__  # type: ignore[attr-defined]
CAMERAS: Tuple[str, ...] = CameraName.__args__  # type: ignore[attr-defined]
EFFECTS: Tuple[str, ...] = Effect.__args__  # type: ignore[attr-defined]


class _Strict(BaseModel):
    model_config = {"extra": "forbid"}


class GrowthModel(_Strict):
    """数值随「模拟时间」（秒）怎么变。"""
    type: Literal["exponential", "linear", "keyframes"] = "exponential"
    start: float = 1.0
    factor: float = 2.0          # exponential：每 step 秒乘以 factor
    rate: float = 0.0            # linear：每秒增加 rate
    step: float = 1.0            # 增长步长（秒）
    discrete: bool = True        # True：每 step 秒跳一次（"第 N 秒"）；False：连续
    points: List[Tuple[float, float]] = Field(default_factory=list)  # keyframes: (sim 秒, 值)

    @model_validator(mode="after")
    def _check(self) -> "GrowthModel":
        if self.type == "keyframes" and len(self.points) < 2:
            raise ValueError("keyframes 至少需要 2 个点")
        if self.step <= 0:
            raise ValueError("step 必须 > 0")
        return self


class Milestone(_Strict):
    """一个真实世界的参照值。数值越过它的那一刻，画面自动弹出标注。"""
    label: str                   # FASTER THAN A CHEETAH
    detail: str = ""             # ITS TOP SPEED: ABOUT 100 km/h
    value: float                 # 阈值（与 quantity.unit 同单位）
    chart: bool = True           # 结尾图表里画成参考线
    chart_label: Optional[str] = None  # 图表参考线的短标签（默认用 label）


class Quantity(_Strict):
    kind: QuantityKind = "speed"
    label: str = "SPEED"
    unit: str = "m/s"            # speed: m/s；length: m；mass: kg；temperature: °C；其它自定
    model: GrowthModel = Field(default_factory=GrowthModel)
    limit: Optional[Milestone] = None       # 物理上限（如光速）：HUD 进度条 + 越过时报警
    milestones: List[Milestone] = Field(default_factory=list)


class Subject(_Strict):
    type: SubjectType = "runner"
    action: Action = "run"
    scale: float = 1.0
    scale_with_value: bool = False   # length 类：主体尺寸跟着数值变
    color: str = "#c8322b"


class Callout(_Strict):
    title: str
    subtitle: str = ""


class Card(_Strict):
    title: str
    rows: List[Tuple[str, str]] = Field(default_factory=list)
    tone: Literal["neutral", "warning"] = "neutral"


class Sfx(_Strict):
    type: SfxType
    at: float = 0.0              # 相对本段开始的秒数
    gain: float = 1.0


class Beat(_Strict):
    duration: float = Field(gt=0.3, le=20)
    sim_end: Optional[float] = None  # 本段结束时的模拟时间；省略=实时推进（sim 增量=duration）
    scene: SceneName = "city"
    camera: CameraName = "follow"
    subject: Optional[Subject] = None   # 省略=沿用上一段
    effects: List[Effect] = Field(default_factory=list)
    caption: str = ""
    callout: Optional[Callout] = None
    card: Optional[Card] = None
    sfx: List[Sfx] = Field(default_factory=list)
    hud: bool = True
    altitude: Optional[Tuple[float, float]] = None  # 可选：本段起止海拔（米），HUD 显示

    @field_validator("caption")
    @classmethod
    def _caption_len(cls, v: str) -> str:
        if len(v) > 160:
            raise ValueError("caption 太长（>160 字符），拆成多段")
        return v


class Intro(_Strict):
    lines: List[str] = Field(default_factory=lambda: ["WHAT IF", "YOU GOT", "2× FASTER", "EVERY SECOND?"])
    accent: int = 2              # 哪一行用强调色、放大
    duration: float = 2.0


class Outro(_Strict):
    chart: bool = True
    chart_title: str = "YOUR SPEED, SECOND BY SECOND"
    chart_subtitle: str = "EACH STEP UP: TWICE AS FAST"
    chart_captions: List[str] = Field(default_factory=list)
    chart_duration: float = 7.0
    question: str = "HOW MANY SECONDS WOULD YOU SURVIVE?"
    question_duration: float = 3.0


class Storyboard(_Strict):
    version: int = 1
    title: str
    premise: str
    quantity: Quantity
    intro: Intro = Field(default_factory=Intro)
    beats: List[Beat] = Field(min_length=1)
    outro: Outro = Field(default_factory=Outro)
    fps: int = 30
    width: int = 1080
    height: int = 1920

    @model_validator(mode="after")
    def _check(self) -> "Storyboard":
        if self.beats[0].subject is None:
            self.beats[0].subject = Subject()
        last = 0.0
        sim = 0.0
        for i, b in enumerate(self.beats):
            end = b.sim_end if b.sim_end is not None else sim + b.duration
            if end < sim - 1e-9:
                raise ValueError(f"beats[{i}].sim_end={end} 比上一段 {sim} 还小（模拟时间不能倒流）")
            sim = end
            last = end
        if last <= 0:
            raise ValueError("总模拟时间为 0")
        return self
