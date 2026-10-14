"""
What-if 视频的分镜（storyboard）结构。

LLM 只负责「写」：选场景、镜头、文案、里程碑；所有数字（速度、距离、倍率、
里程碑出现的时刻）由 model.py 按增长模型算出来，文案里的数字用占位符引用，
保证画面上的数据前后一致、不会编造。

支持多种版式（format），与参考账号的几类视频对应：
- escalation：数值持续增长 + 数据 HUD + 里程碑（"每秒快一倍"）
- timeline：「+10 SEC → +1 HOUR → +100 YEARS」跳时 + 大号统计数字（"如果所有女性消失"）
- countdown：倒计时时钟（"摩擦力消失 5 秒"）
- story：分章节叙事，顶部进度条 + 章节标题 + 时间标签 + 信息框（"TWISTEX"、"月球碎裂"）
- survival：计时器 + 生命体征等屏幕（"被毒蛇咬了"）
"""
from __future__ import annotations

from typing import List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field, field_validator, model_validator

Format = Literal["escalation", "timeline", "countdown", "story", "survival"]
SceneName = Literal[
    "city", "highway", "suburb", "park", "fields", "forest", "desert", "outback", "mountains", "volcano",
    "coast", "ocean", "sky", "orbit", "deep_space", "globe", "map", "interior", "ancient", "lab", "void",
]
CameraName = Literal[
    "follow", "front", "side", "low_front", "wide", "aerial", "orbit", "far", "closeup",
    "establishing", "pov", "top_down", "dolly",
]
SubjectType = Literal["runner", "person", "ball", "car", "cube", "rocket", "none"]
Action = Literal["idle", "walk", "run", "sprint", "float", "fly", "sit", "kneel", "lie", "point", "phone", "pray", "fall"]
Outfit = Literal["casual", "hoodie", "scrubs", "doctor", "hivis", "suit", "robe", "soldier", "child", "elder", "ranger", "police"]
Effect = Literal[
    "motion_blur", "heat", "plasma", "speedlines", "shake", "shockwave",
    "dust", "vapor_cone", "glow", "flash",
    "fire", "smoke", "embers", "earthquake", "vanish", "freeze", "darken",
]
SfxType = Literal[
    "whoosh", "boom", "riser", "impact", "tick", "swell", "drop",
    "rumble", "alarm", "heartbeat", "crack", "ring", "beep", "siren", "thunder",
]
QuantityKind = Literal["speed", "length", "mass", "temperature", "count", "generic"]
TimeOfDay = Literal["day", "golden", "dusk", "night", "dawn"]
Weather = Literal["clear", "overcast", "rain", "storm", "snow", "ash", "fog", "dust"]
SkyEvent = Literal["normal", "red", "dark", "meteors", "aurora"]
Room = Literal["hospital", "operating_room", "classroom", "nursery", "office", "store", "home", "lab", "court", "hall", "bunker"]
Icon = Literal[
    "bars", "people", "person", "earth", "sun", "moon", "volcano", "tornado", "wave", "snake", "bolt",
    "drop", "clock", "flame", "mountain", "building", "heart", "warning", "star", "ice", "rocket", "horse", "none",
]

SCENES: Tuple[str, ...] = SceneName.__args__  # type: ignore[attr-defined]
CAMERAS: Tuple[str, ...] = CameraName.__args__  # type: ignore[attr-defined]
EFFECTS: Tuple[str, ...] = Effect.__args__  # type: ignore[attr-defined]
OUTFITS: Tuple[str, ...] = Outfit.__args__  # type: ignore[attr-defined]
ACTIONS: Tuple[str, ...] = Action.__args__  # type: ignore[attr-defined]
ROOMS: Tuple[str, ...] = Room.__args__  # type: ignore[attr-defined]
ICONS: Tuple[str, ...] = Icon.__args__  # type: ignore[attr-defined]
SFX: Tuple[str, ...] = SfxType.__args__  # type: ignore[attr-defined]


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
    outfit: Outfit = "hoodie"        # runner/person 的服装
    scale: float = 1.0
    scale_with_value: bool = False   # length 类：主体尺寸跟着数值变
    color: str = "#c8322b"


class CastGroup(_Strict):
    """场景里的一群人（路人、医护、学生……）。位置由渲染端按 layout 确定性生成。"""
    outfit: Outfit = "casual"
    count: int = Field(default=8, ge=1, le=80)
    action: Action = "idle"
    layout: Literal["around", "line", "row", "scatter", "seated", "crowd"] = "scatter"
    distance: float = 6.0            # 离镜头焦点的大致距离（米）


class Marker(_Strict):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    label: str = ""
    kind: Literal["ring", "dot", "glow", "cloud"] = "ring"
    radius: float = 6.0              # 度


class GlobeOpts(_Strict):
    night_side: bool = False         # 晨昏线（一半黑夜）
    markers: List[Marker] = Field(default_factory=list)
    faults: bool = False             # 板块断层发光
    ring: bool = False               # 碎片环
    moon: Literal["none", "whole", "shattered"] = "none"
    frozen: bool = False             # 冰封地球
    dry_oceans: bool = False         # 海洋消失
    spin: float = 0.05               # 自转速度（弧度/秒，视觉）
    focus: Optional[Tuple[float, float]] = None  # 朝向镜头的经纬度


class MapPoint(_Strict):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    text: str = ""


class MapOpts(_Strict):
    labels: List[MapPoint] = Field(default_factory=list)
    path: List[MapPoint] = Field(default_factory=list)  # 移动轨迹（按本段进度揭示）
    zone: Optional[MapPoint] = None                     # 危险区（圆）
    zone_radius: float = 0.12
    style: Literal["dark", "satellite", "paper"] = "dark"


class Env(_Strict):
    """场景修饰：时段、天气、天象、人群密度、荒废程度、室内类型、地球/地图选项。"""
    time: TimeOfDay = "day"
    weather: Weather = "clear"
    sky: SkyEvent = "normal"
    crowd: Optional[float] = Field(default=None, ge=0, le=1)    # 行人密度；None = 场景默认
    traffic: Optional[float] = Field(default=None, ge=0, le=1)  # 车辆密度；None = 场景默认
    empty: bool = False              # 人消失了（车、物还在）
    lights_off: bool = False         # 断电：夜里窗户不亮
    overgrown: float = Field(default=0.0, ge=0, le=1)  # 荒废 / 植物覆盖
    damage: float = Field(default=0.0, ge=0, le=1)     # 碎片、倒塌
    room: Room = "office"            # scene=interior 时的房间类型
    globe: Optional[GlobeOpts] = None
    map: Optional[MapOpts] = None


class Stat(_Strict):
    """画面上方的大号数字（"90%" / "OF THE WORLD'S NURSES ARE WOMEN"）。是事实陈述：须可查证。"""
    value: str
    label: str = ""
    count_up: bool = True


class Tooltip(_Strict):
    label: str = "FACT"
    text: str


class Banner(_Strict):
    kicker: str = "BREAKING NEWS"
    title: str
    subtitle: str = ""


class Screen(_Strict):
    """手机来电 / 生命体征监护 / 信息屏。"""
    kind: Literal["phone_call", "vitals", "board"] = "board"
    title: str = ""
    subtitle: str = ""
    badge: str = ""
    rows: List[Tuple[str, str]] = Field(default_factory=list)

class Callout(_Strict):
    title: str
    subtitle: str = ""


class Card(_Strict):
    title: str
    rows: List[Tuple[str, str]] = Field(default_factory=list)
    tone: Literal["neutral", "warning"] = "neutral"


class Clock(_Strict):
    """左侧中部的时间块。elapsed: "+10 SEC" 标签；countdown/stopwatch：连续走动的数字时钟；time_of_day："6:03 PM"。"""
    mode: Literal["elapsed", "countdown", "stopwatch", "time_of_day", "none"] = "elapsed"
    label: str = ""                  # 例 "WITHOUT WOMEN" / "FRICTION RETURNS IN" / "TIME SINCE BITE"
    intro_label: str = ""            # 片头倒计时的标签，例 "WOMEN VANISH IN"
    intro_from: Optional[float] = None  # 片头倒计时起点（秒）；None = 片头不显示时钟


class Theme(_Strict):
    accent: str = "#f0883e"          # 主题强调色（女性=粉、地球=蓝、太阳=黄……）

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
    # --- 多版式 ---
    env: Optional[Env] = None        # 省略=沿用上一段（换场景时重置为默认）
    cast: List[CastGroup] = Field(default_factory=list)
    time: Optional[Union[str, Tuple[float, float]]] = None  # "+1 HOUR" 或 [起, 止] 秒（倒计时/秒表）
    time_sub: str = ""               # 时钟下面的一行小字
    stat: Optional[Stat] = None
    chapter: Optional[str] = None    # 章节标题；省略=沿用上一段
    chip: str = ""                   # 右上角时间标签（"6:20 PM" / "5 DAYS LATER"）
    tooltip: Optional[Tooltip] = None
    caption_ref: str = ""            # 字幕下的出处（"LUKE 22:42"）
    banner: Optional[Banner] = None
    screen: Optional[Screen] = None
    @field_validator("caption")
    @classmethod
    def _caption_len(cls, v: str) -> str:
        if len(v) > 160:
            raise ValueError("caption 太长（>160 字符），拆成多段")
        return v


class Intro(_Strict):
    style: Literal["stack", "title", "chapter"] = "stack"
    lines: List[str] = Field(default_factory=lambda: ["WHAT IF", "YOU GOT", "2× FASTER", "EVERY SECOND?"])
    accent: int = 2              # stack：哪一行用强调色、放大
    title: str = ""              # title/chapter：用 *星号* 标出强调词，例 "What if all *women* disappeared?"
    kicker: str = ""             # 标题上方小字（"PART 1"）
    subtitle: str = ""           # 标题下方小字（"A HYPOTHETICAL SIMULATION"）
    icon: Icon = "bars"
    duration: float = 2.0


class EndCard(_Strict):
    kind: Literal["question", "title", "tagline", "memorial", "continued"] = "question"
    kicker: str = ""             # 小字（"IN MEMORY OF" / "PART 2"）
    lines: List[str] = Field(default_factory=list)
    accent_line: int = -1        # 哪一行用强调色
    sub: str = ""

class Outro(_Strict):
    chart: bool = True
    chart_title: str = "YOUR SPEED, SECOND BY SECOND"
    chart_subtitle: str = "EACH STEP UP: TWICE AS FAST"
    chart_captions: List[str] = Field(default_factory=list)
    chart_duration: float = 7.0
    question: str = "HOW MANY SECONDS WOULD YOU SURVIVE?"
    question_duration: float = 3.0
    end: Optional[EndCard] = None    # 设置后替代 question 的样式

class Storyboard(_Strict):
    version: int = 1
    format: Format = "escalation"
    title: str
    premise: str
    theme: Theme = Field(default_factory=Theme)
    quantity: Optional[Quantity] = None   # escalation 必填；其它版式可省略
    clock: Optional[Clock] = None
    intro: Intro = Field(default_factory=Intro)
    beats: List[Beat] = Field(min_length=1)
    outro: Outro = Field(default_factory=Outro)
    fps: int = 30
    width: int = 1080
    height: int = 1920

    @model_validator(mode="after")
    def _check(self) -> "Storyboard":
        if self.beats[0].subject is None:
            self.beats[0].subject = Subject() if self.format == "escalation" else Subject(type="none")
        if self.format == "escalation" and self.quantity is None:
            raise ValueError("format=escalation 需要 quantity")
        if self.quantity is None and self.outro.chart:
            self.outro.chart = False
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
