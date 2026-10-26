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
- pov：第一人称"你"的视角（"POV: 你醒来发现重力消失了"）：眼睛机位 + 画面里你自己的手、眨眼转场、顶部固定 POV 钩子、打字字幕
"""
from __future__ import annotations

from typing import List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field, field_validator, model_validator

Format = Literal["escalation", "timeline", "countdown", "story", "survival", "pov"]
SceneName = Literal[
    "city", "highway", "suburb", "park", "fields", "forest", "desert", "outback", "mountains", "volcano",
    "coast", "ocean", "sky", "orbit", "deep_space", "globe", "map", "interior", "ancient", "lab", "void", "custom",
]
CameraName = Literal[
    "follow", "front", "side", "low_front", "wide", "aerial", "orbit", "far", "closeup",
    "establishing", "pov", "top_down", "dolly", "witness", "eyes",
]
SubjectType = Literal["runner", "person", "ball", "car", "cube", "rocket", "none"]
Action = Literal["idle", "walk", "run", "sprint", "float", "fly", "sit", "kneel", "lie", "point", "phone", "pray", "fall", "handwalk", "footeat"]
Outfit = Literal["casual", "hoodie", "scrubs", "doctor", "hivis", "suit", "robe", "soldier", "child", "elder", "ranger", "police", "mannequin"]
Effect = Literal[
    "motion_blur", "heat", "plasma", "speedlines", "shake", "shockwave",
    "dust", "vapor_cone", "glow", "flash",
    "fire", "smoke", "embers", "earthquake", "vanish", "freeze", "darken",
    "explosion", "sparks", "confetti", "lightning", "rays", "glitch", "bloom",
    "tunnel", "dizzy", "nightvision",
]
Move = Literal["none", "swoop_in", "swoop_out", "crane_up", "crane_down", "arc_left", "arc_right", "push_in", "pull_out",
               "whip", "dutch", "drone_rise", "fly_by", "spiral"]
Transition = Literal["cut", "whip", "flash", "zoom", "dip", "glitch", "blink"]
SfxType = Literal[
    "whoosh", "boom", "riser", "impact", "tick", "swell", "drop",
    "rumble", "alarm", "heartbeat", "crack", "ring", "beep", "siren", "thunder",
    "debris", "sparkle", "pop", "glitch", "shimmer",
    "breath", "steps", "run_steps",
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


SetKind = Literal[
    # 基本体
    "sphere", "box", "cylinder", "cone", "torus", "capsule", "ring", "plane", "icosahedron", "octahedron",
    # 科普道具
    "molecule", "atom", "dna", "cell", "blood_cell", "virus", "neuron", "lungs", "heart", "hourglass", "clock",
    "gear", "flame", "crystal", "bubble", "planet", "sun", "moon", "earth", "tree", "rock", "building", "arrow",
    "bars", "person", "particles",
]
SET_KINDS: Tuple[str, ...] = SetKind.__args__  # type: ignore[attr-defined]


class Anim(_Strict):
    type: Literal["spin", "bob", "orbit", "pulse", "grow", "shrink", "fade_in", "fade_out", "move", "drift", "wobble"]
    axis: Literal["x", "y", "z"] = "y"
    speed: float = 1.0               # 每秒（弧度 / 周期 / 米，视类型而定）
    amount: float = 0.3              # 幅度（bob / pulse / wobble / orbit 半径）
    to: Optional[Tuple[float, float, float]] = None  # move：本段内从 at 移动到 to


class SetObject(_Strict):
    """自定义布景里的一个物体（或一组：count > 1 时在 spread 范围内随机散布）。"""
    kind: SetKind
    at: Tuple[float, float, float] = (0, 0, 0)
    scale: Union[float, Tuple[float, float, float]] = 1.0
    rotate: Tuple[float, float, float] = (0, 0, 0)   # 度
    color: str = "#d8d8d8"
    color2: Optional[str] = None     # 次要颜色（细胞核、沙子、钟面、DNA 第二条链 …；person = 肤色）
    material: Literal["matte", "glossy", "metal", "glass", "glow", "toon"] = "matte"
    opacity: float = Field(default=1.0, ge=0.05, le=1)
    count: int = Field(default=1, ge=1, le=200)
    spread: Tuple[float, float, float] = (0, 0, 0)
    seed: int = 1
    formula: str = ""                # molecule："N2" "O2" "CO2" "H2O" "CH4" "NH3" ……
    values: List[float] = Field(default_factory=list)   # bars：柱高
    outfit: Outfit = "casual"        # person
    action: Action = "idle"
    animate: List[Anim] = Field(default_factory=list)


class SetSpec(_Strict):
    """完全自定义的布景：按题目设计，而不是套用城市 / 公路 / 地球模板。"""
    background: Union[Literal["stars", "black", "white"], Tuple[str, str]] = ("#0d1622", "#2a3b52")  # (顶, 底) 渐变
    ground: Literal["none", "plane", "grid", "water", "mirror"] = "none"
    ground_color: str = "#1a2230"
    fog: Optional[Tuple[str, float, float]] = None   # (颜色, 近, 远)
    light: str = "#ffffff"
    light_intensity: float = 2.2
    ambient: float = 0.8
    bounce: str = "#30343c"          # 环境光的"地面反射"色（朝下的面拿到的光）；室内用接近墙面的浅色，天花板才不会发黑
    focus: Tuple[float, float, float] = (0, 1, 0)    # 镜头围绕的点
    zoom: float = 1.0                                 # 镜头距离倍数
    ambience: Literal["none", "space", "room", "calm", "forest", "ocean", "wind", "lab", "rumble"] = "space"
    objects: List[SetObject] = Field(default_factory=list, max_length=40)


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
    cover: Union[float, Tuple[float, float]] = 0.0     # 积雪 / 落灰（weather=ash 时为灰）覆盖程度 0..1；[起, 止] = 本段内逐渐盖上
    room: Room = "office"            # scene=interior 时的房间类型
    globe: Optional[GlobeOpts] = None
    map: Optional[MapOpts] = None
    set: Optional[SetSpec] = None    # scene=custom 时的布景


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


class Narration(_Strict):
    """可选旁白（参考账号默认无旁白）。开启后每段读字幕或 beat.narration，画面按语音长度自动拉长。"""
    enabled: bool = True
    engine: Literal["kokoro", "openai"] = "kokoro"
    voice: str = "am_michael"        # kokoro: am_michael / af_heart / bf_emma …；openai: alloy / onyx / nova …
    speed: float = Field(default=1.0, ge=0.6, le=1.6)
    read_title: bool = True          # 片头念标题
    read_end: bool = True            # 结尾念问句 / 结尾卡


VideoStyle = Literal["calm", "bold", "cinematic", "toon", "retro", "witness", "bodycam"]
CaptionMode = Literal["line", "words", "box", "typed"]
STYLE_CAPTIONS = {"calm": "line", "bold": "words", "cinematic": "line", "toon": "box", "retro": "words", "witness": "line", "bodycam": "box"}


class Theme(_Strict):
    accent: str = "#f0883e"          # 主题强调色（女性=粉、地球=蓝、太阳=黄……）
    # 画面风格：calm 安静高级（默认）/ bold 爆款快剪（逐词大字幕、推镜、闪切）/ cinematic 纪录片（黑边、颗粒、调色）
    #          / toon 卡通（描边、平涂、贴纸字幕）/ retro 8-bit 像素（低分辨率、扫描线）
    style: VideoStyle = "calm"
    captions: Optional[CaptionMode] = None   # None = 跟随风格
    layout: Literal["full", "split"] = "full"   # split = 上半故事、下半解压循环画面（竖屏）
    # 前景"锚点"小物：固定在镜头下方，随剧情变化（冒热气 / 结霜 / 落灰 / 抖动）。witness 风格默认 coffee
    anchor: Optional[Literal["none", "coffee", "drink"]] = None
    flow: Literal["auto", "steady", "build", "punchy", "slowburn", "rollercoaster"] = "auto"   # 整片节奏；auto = 按标题 / 近期历史挑
    rec: str = ""                    # bodycam：右上角时间戳的起点（"2026-10-26 07:42:13"）；空 = 渲染当天 07:42:13
    palette: Literal["auto", "natural", "warm", "cool", "teal_orange", "vivid", "pastel", "mono", "noir"] = "auto"

class Sfx(_Strict):
    type: SfxType
    at: float = 0.0              # 相对本段开始的秒数
    gain: float = 1.0
    dur: Optional[float] = Field(default=None, gt=0, le=20)   # 可选：持续时长（whoosh / riser / rumble / heartbeat / alarm … 适用）


HandPose = Literal["none", "idle", "reach", "phone", "shield", "grab", "cover", "fists", "point", "wave", "hold", "float"]
HeadMotion = Literal["steady", "breathe", "walk", "run", "stumble", "fall", "float", "shake"]
HAND_POSES: Tuple[str, ...] = HandPose.__args__  # type: ignore[attr-defined]
HEAD_MOTIONS: Tuple[str, ...] = HeadMotion.__args__  # type: ignore[attr-defined]


class Hands(_Strict):
    """pov：画面下方你自己的手（镜头坐标系里的一对手臂）。"""
    pose: HandPose = "idle"
    holding: Literal["none", "phone", "cup", "flashlight"] = "none"   # 右手拿着的东西（phone 姿势默认拿手机）
    phone_text: str = ""             # 手机屏幕上的字（"NO SIGNAL" / "MOM: where are you??"）
    tremble: float = Field(default=0.0, ge=0, le=1)   # 手抖（害怕 / 冷）


class Pov(_Strict):
    """pov 版式：顶部固定的 POV 钩子 + 你的手的样子。"""
    text: str                        # "you wake up and gravity is gone"（显示为 "POV: …"，整片固定在顶部）
    skin: str = "#d6a07c"
    sleeve: str = "#343a40"
    open_eyes: bool = True           # 开头从闭眼到睁眼（像刚醒来）


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
    time_label: str = ""             # 本段时钟上方的标签（覆盖 clock.label，如 "COLUMN HEIGHT" / "WIND" / "THE FLOW"）
    stat: Optional[Stat] = None
    chapter: Optional[str] = None    # 章节标题；省略=沿用上一段
    chip: str = ""                   # 右上角时间标签（"6:20 PM" / "5 DAYS LATER"）
    tooltip: Optional[Tooltip] = None
    caption_ref: str = ""            # 字幕下的出处（"LUKE 22:42"）
    banner: Optional[Banner] = None
    screen: Optional[Screen] = None
    narration: Optional[str] = None  # 旁白文本；None = 读字幕（开启旁白时），"" = 这段不念
    move: Optional[Move] = None      # 本段镜头运动；None = 按 flow 自动挑
    transition: Optional[Transition] = None   # 进入本段的转场；None = 自动
    roll: float = 0.0                # 镜头横滚角（度）：180 = 整个世界倒过来（地面在头顶、天空在脚下）
    roll_to: Optional[float] = None  # 本段结束时的横滚角；设了就在本段内缓动转过去（如 0 → 180 把世界翻过来）
    # --- pov（camera="eyes"）---
    hands: Optional[Hands] = None    # 省略 = 沿用上一段（pov 版式第一段默认 idle）
    head: Optional[HeadMotion] = None   # 头部运动：walk / run 会往前走；fall 往下掉；省略 = 沿用上一段
    gaze: Tuple[float, float] = (0.0, 0.0)   # 视线（偏航, 俯仰）度：偏航 + = 向右看，俯仰 + = 抬头
    gaze_to: Optional[Tuple[float, float]] = None   # 本段结束时的视线；设了就在本段内转头过去
    @field_validator("caption")
    @classmethod
    def _caption_len(cls, v: str) -> str:
        if len(v) > 160:
            raise ValueError("caption 太长（>160 字符），拆成多段")
        return v


class Intro(_Strict):
    style: Literal["stack", "title", "chapter", "overlay"] = "stack"   # overlay = 标题直接压在第一个镜头上（无图标、小号衬线）
    lines: List[str] = Field(default_factory=lambda: ["WHAT IF", "YOU GOT", "2× FASTER", "EVERY SECOND?"])
    accent: int = 2              # stack：哪一行用强调色、放大
    title: str = ""              # title/chapter：用 *星号* 标出强调词，例 "What if all *women* disappeared?"
    kicker: str = ""             # 标题上方小字（"PART 1"）
    subtitle: str = ""           # 标题下方小字（"A HYPOTHETICAL SIMULATION"）
    icon: Icon = "bars"
    duration: float = 2.0


class EndCard(_Strict):
    kind: Literal["question", "title", "tagline", "memorial", "continued", "fact"] = "question"   # fact = 标题 + 一行等宽小字史实
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
    narration: Optional[Narration] = None
    intro: Intro = Field(default_factory=Intro)
    beats: List[Beat] = Field(min_length=1)
    outro: Outro = Field(default_factory=Outro)
    fps: int = 30
    width: int = 1080
    height: int = 1920
    thumbnail: str = ""          # 封面大字（2-5 个词，*星号* 标出高亮词，如 "SNOW IN *DUBAI*?"）；空 = 从标题推
    thumbnail_beat: Optional[int] = None   # 封面用哪一段的画面；None = 自动挑最有冲击力的一段
    pov: Optional[Pov] = None    # format=pov 必填
    pace: Optional[float] = Field(default=None, ge=0.5, le=3.0)   # 节奏倍数：1.2 = 镜头短 1.2 倍、画面动作快 1.2 倍；None = 用渲染参数（默认 1.2）

    @model_validator(mode="after")
    def _check(self) -> "Storyboard":
        if self.beats[0].subject is None:
            self.beats[0].subject = Subject() if self.format == "escalation" else Subject(type="none")
        if self.format == "pov" and self.pov is None:
            raise ValueError("format=pov 需要 pov（顶部钩子文字，如 {\"text\": \"you wake up and gravity is gone\"}）")
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
