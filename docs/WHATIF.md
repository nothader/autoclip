# What-if 科普短视频生成器（`autoclip whatif`）

输入一个「如果……会怎样」的题目，输出一条 9:16 竖屏短视频：低多边形 3D 模拟画面 + 小号大写标签 +
每镜一句斜体字幕 + 标题卡 / 结尾卡，配程序化音效（无旁白、无音乐）。

## 版式（format）

| 版式 | 适合 | 画面元素 | 示例 |
|---|---|---|---|
| `escalation` | 数值持续增长（每秒快一倍 / 变高一倍） | 顶部数据 HUD、越过参照值时弹出里程碑、结尾阶梯图表 | `twice_as_fast.json` |
| `timeline` | 发生一次，然后跳时看后果（所有 X 消失 / 太阳熄灭 / 地球停转） | 左中部「+10 SEC → +1 YEAR」时间标签、大号统计数字、信息卡 | `earth_stopped_spinning.json` |
| `countdown` | 短暂事件（摩擦力 / 大气消失 5 秒） | 走动的倒计时 `0:04.821`、每整秒提示音 | `friction_disappeared.json` |
| `story` | 分章节叙事（真实事件复盘 / 灾难推演） | 顶部分段进度条 + 「PART 2 OF 5」+ 章节标题、时间标签、信息框、新闻横幅、地图 | `moon_shattered.json` |
| `survival` | 个人求生（被毒蛇咬了） | 计时器 `0:02:15`、生命体征 / 来电屏幕、医院室内 | （由模型按说明生成） |

场景：`city highway suburb park fields forest desert outback mountains volcano coast ocean sky orbit deep_space globe map interior ancient lab void`；
室内房间 `hospital operating_room classroom nursery office store home lab court hall bunker`；
地球（globe）可设标记（ring/dot/glow/cloud）、晨昏线、断层发光、碎片环、完整/碎裂的月球、冰封、海洋干涸、朝向经纬度；
地图（map）用 SVG 画标签、轨迹（按进度揭示）、危险区。

**自定义布景（`scene: "custom"` + `env.set`，推荐）**：每个题目自己搭场景，而不是套城市/公路/地球模板。
背景（渐变 / 星空 / 纯色）、地面（无 / 平面 / 网格 / 水面 / 镜面）、雾、灯光、镜头焦点与距离，加最多 40 组物体：
基本体（sphere box cylinder cone torus capsule ring plane icosahedron octahedron）和科普道具
（molecule〔按分子式，CPK 配色与单/双/三键〕 atom dna cell blood_cell virus neuron lungs heart hourglass clock gear flame
crystal bubble planet sun moon earth tree rock building arrow bars person particles），每个可设材质
（matte glossy metal glass glow toon）、散布数量、动画（spin bob orbit pulse grow shrink fade_in fade_out move drift wobble）。
示例：`examples/nitrogen_custom_sets.json`。planner 默认按题目设计自定义布景，只有剧情确实发生在城市/室内等地方时才用通用场景。

环境修饰（`env`，同场景内沿用）：时段 `day golden dusk night dawn`、天气 `rain storm snow ash fog dust overcast`、
天象 `red dark meteors`、人群/车流密度、`empty`（人消失）、`lights_off`、`overgrown`（荒废长草）、`damage`（碎片）。
人物：`person`/`cast` 支持服装 `casual hoodie scrubs doctor hivis suit robe soldier child elder ranger police mannequin`（mannequin = 单色无细节人体模型，用于抽象表现） 与姿势
`idle walk run sprint sit kneel lie point phone pray fall float fly handwalk footeat`（handwalk = 倒立用手走，footeat = 坐地上用脚送食物到嘴边；自定义布景里的人会按动作循环动起来）；`vanish` 效果让人逐个消失。

```bash
pip install -r requirements-whatif.txt
python -m playwright install chromium        # 已有 Playwright Chromium 可跳过

autoclip whatif examples                     # 内置示例分镜
autoclip whatif render backend/whatif/examples/twice_as_fast.json --preview   # 半分辨率，快
autoclip whatif render backend/whatif/examples/twice_as_fast.json -o out.mp4  # 1080x1920 30fps

# 任意题目（用桌面应用里配好的模型，或 --provider/--model/--api-key）
autoclip whatif plan "What if you grew 2x taller every second?" -o tall.json   # 先出分镜，可手改
autoclip whatif render tall.json -o tall.mp4
autoclip whatif make "What if Earth stopped spinning?" --provider openai --model gpt-4o
autoclip whatif make "What if the atmosphere vanished for 5 seconds?" --format countdown
```

## 横屏长视频（YouTube）

分镜顶层写 `"width": 1920, "height": 1080` 即为 16:9 横屏：叠加层换成横屏版式（字幕贴底、章节条在上、统计数字居中、
信息框靠右），总时长上限从 180 s 放宽到 900 s（15 分钟），适合 5–6 分钟的长视频（约 60–80 个分镜、8–10 章，`story` 版式最合适）。
示例：渲 6 分钟 1920x1080 30fps 在 4 核软件渲染下约 1 小时，建议后台跑：

```bash
autoclip whatif render long.json -o long.mp4      # 1920x1080
autoclip whatif render long.json --preview        # 960x540 预览
```

## 旁白（可选，`--narrate`）

参考账号默认无旁白；需要时加 `--narrate`：

```bash
autoclip whatif render story.json --narrate                       # 本地 Kokoro TTS（离线，首次下载模型 ~120 MB）
autoclip whatif render story.json --narrate --voice af_heart      # 换声音：am_michael / af_heart / bf_emma / bm_george …
autoclip whatif make "What if …" --narrate --tts openai --voice onyx   # OpenAI TTS（需 OPENAI_API_KEY 或 AUTOCLIP_TTS_API_KEY）
```

- 默认念：片头标题 → 每段字幕 → 结尾问句；某段想换说法用 `beat.narration`，`""` 表示这段不念
- 画面按语音长度自动拉长（每段至少「0.3 s + 语音 + 0.45 s」），字幕与语音同步
- 单位/符号转成口语（km/h → kilometers per hour、~ → about、CO2 → C O two …）
- 混音：音效总线压到 -22 dBFS，说话时再闪避约 9 dB；人声单独一条总线（约 -16 dBFS）
- 合成结果按文本缓存在 `~/.cache/autoclip/tts`，改画面重渲不重复合成；分镜里也可写 `"narration": {"voice": "...", "speed": 1.0}`

## 画面风格（`theme.style` / `--style`）与分屏（`--layout split`）

| 风格 | 画面 | 字幕 | 适合 |
|---|---|---|---|
| `calm`（默认） | 安静高级、柔和调色 | 斜体衬线一行 | 科普、太空、严肃历史 |
| `bold` | 高饱和、每次切镜推镜冲击 + whoosh、顶部进度条 | 逐词弹出大写粗体，当前词高亮 | 猎奇、身体/金钱类 what-if、快节奏 |
| `cinematic` | 上下黑边、胶片颗粒、暗角、暖调、缓慢推近 | 纪录片式下三分之一 | 历史、灾难、人物 |
| `toon` | 卡通三阶光照 + 黑色描边、平涂高饱和 | 白底黑字贴纸 | 搞笑/荒诞、儿童、动物、食物 |
| `retro` | 8-bit 低分辨率像素 + 扫描线 | 等宽字逐词、绿色高亮 | 游戏、科技、互联网、"模拟世界" |
| `witness` | 固定"目击者"视角（高处阳台，镜头 `witness` 手持微晃）+ 前景咖啡杯 | 带阴影的小号斜体 | 灾难 / 天气 / 城市巨变，在一个真实地点看事情一步步升级 |

`witness` 的几个配套件：
- `theme.anchor`：`coffee`（默认）/ `drink` / `none`——镜头前景的杯子：热时冒气，下雪 / 落灰的段数越多杯口积得越厚，`storm` / `earthquake` / `shake` 时会抖。
- 递增指标：`clock` + 每段 `time_label`（覆盖时钟标签，如 "SNOW DEPTH" → "POWER"）、`time`（大号数字）、`time_sub`（一行等宽参照小字）。
- `intro.style: "overlay"`：标题直接压在第一个镜头上；`outro.end.kind: "fact"`：纯黑底，标题 + 等宽大写史实一行。
- `env.cover`（0..1 或 `[起, 止]`，任何风格都能用）：积雪覆盖，朝上的面（路面、车顶、屋顶、树冠）逐渐变白；`weather: "ash"` 时为灰。自定义布景也会下雪 / 落灰。

`theme.captions`（`line`/`words`/`box`）可单独覆盖字幕样式。`theme.layout: "split"`（仅竖屏）：上半故事、下半解压循环
（小球在彩虹台阶上弹跳），字幕压在接缝上。

```bash
autoclip whatif render story.json --style bold --layout split
autoclip whatif render story.json --style cinematic
```

## 节奏（`--pace`，默认 1.8）

渲染默认 1.8 倍节奏：每个镜头时长 ÷ 1.8（但不短于字幕可读下限 0.8 s + 0.028 s/字符），画面里的动作（自转、走路、抖动）
同步快 1.8 倍；模拟数字和里程碑不变；有旁白时改为加快语速（上限 1.6）。分镜里写 `"pace": 1.0` 可恢复原速，
或 `autoclip whatif render story.json --pace 1.0`。

## 开头钩子与留存规则（`autoclip whatif check`）

`backend/whatif/hooks.py` 按以下规则给分镜打分（0–100），planner 写分镜时会把不合格项回传给模型修（修不完不报错），
`render` 开始时打印分数：

1. **具体、直接**：标题和第一句字幕要有数字、名字或情绪词（every / never / 8 billion / gone）
2. **三年级阅读水平**：短词短句，每条字幕约 6–12 词；整片 Flesch-Kincaid 年级 > 6.5 必须改，> 4.5 给建议
3. **最抓人的细节在前 3 秒**：标题卡 ≤ 3 s，第一句字幕放全片最有意思的点
4. **删废话**：basically / actually / in this video / fun fact / in conclusion …
5. **不提前揭晓 + 开放式悬念**：前 3 句里要有问句或 "But… / Here's the worst part…"，结论留到最后，结尾卡用问句

```bash
autoclip whatif check story.json          # 打印分数和逐条问题
autoclip whatif check story.json --json
```

## 画面质量检查（同样在 `autoclip whatif check` 里）

`backend/whatif/quality.py` 把之前每支视频踩过的坑写成规则，fix 级问题和钩子问题一起回传给 planner：

- **克隆人**：同一布景里两个人 outfit + seed + 颜色完全一样
- **单调**：连续 3 段同场景同机位（witness 除外）、连续 2 段完全相同的自定义布景 + 机位；某个机位占比 > 55% 给建议
- **静止 / 空镜**：自定义布景里什么都不动、或者什么都没有
- **时长**：竖屏按 1.8x 节奏压完后 < 58 s（短视频要 1 分钟以上）；横屏长视频 < 4 分钟给建议
- **风格配套**：witness 风格必须有递增指标（clock + time）

planner 还会拿到一个按题目关键词推荐的风格（`SUGGESTED STYLE`：灾难 / 天气 → witness，游戏 / 科技 → retro，
动物 / 食物 / 荒诞 → toon，历史 / 人物 → cinematic，金钱 / 身体 / 社会 → bold，其余 calm）。

## 发布包（`--pack`，`make` 默认开）

成片之外一起产出：

| 文件 | 内容 |
|---|---|
| `<名字>_thumb.jpg` | 封面：自动挑最有冲击力的一段（特效、天象、损毁、人多、靠近高潮），去掉字幕 / HUD 单独渲一帧，压上 2–5 个词的大字（`*星号*` 词黄色高亮）。横屏 1280×720，竖屏 1080×1920 |
| `<名字>_youtube.txt` | 标题、简介（钩子句 + 悬念句 + 免责声明）、横屏的章节时间戳、标签、hashtag、置顶评论（结尾问题） |
| `<名字>_short.mp4` | 仅横屏长视频：自动剪的 ~1 分钟竖屏短版（保留开头结尾，中间按信息量挑段，去旁白），附自己的封面和 `_tiktok.txt` |

分镜里可写 `"thumbnail": "SNOW IN *DUBAI*?"`、`"thumbnail_beat": 12` 指定封面字和画面。也可以单独跑：

```bash
autoclip whatif make "What if it snowed in Dubai and never stopped?"       # 成片 + 封面 + 文案
autoclip whatif render story.json --pack                                   # 已有分镜
autoclip whatif thumb story.json --text "SNOW IN *DUBAI*?" --arrow         # 只做封面
autoclip whatif meta story.json                                            # 只出标题 / 简介 / 标签
autoclip whatif short long.json && autoclip whatif render long_short.json  # 长视频 → 1 分钟竖屏短版
```

## 设计原则：文字归 LLM，数字归代码

LLM 只写分镜：增长模型、场景、镜头、文案、里程碑（真实参照值）。画面上出现的每个数字都由 `model.py`
按增长模型算出来：

- HUD 每帧的数值、km/h、马赫、光速百分比、累计距离、慢放倍率
- 里程碑在数值**真正越过**参照值的那一帧弹出（排队，不重叠）
- 文案里的计算型数字必须写成占位符：`{value}` `{kmh}` `{mach}` `{light_pct}` `{distance}` `{scale}` …，渲染时按该镜结束时刻填入
- `validate()` 拦截：写死的大数字、未知占位符、模拟时间内不会被越过的里程碑、时长超限；planner 把问题回传给 LLM 修，最多 2 轮

## 结构

| 文件 | 作用 |
|---|---|
| `backend/whatif/schema.py` | 分镜结构（pydantic，`extra=forbid`） |
| `backend/whatif/model.py` | 增长模型、积分、里程碑时刻、格式化 → 逐帧渲染计划 `plan` |
| `backend/whatif/planner.py` | 题目 → 分镜（提示词 + 示例 + 校验修正循环） |
| `backend/whatif/web/` | three.js 场景（`sets.js` 自定义布景与道具库、`world.js`/`envs.js` 通用环境与时段天气、`people.js` 人物与人群、`actors.js` 道具与特效）+ HTML/SVG 叠加层（`overlay.js`、`icons.js`） |
| `backend/whatif/render.py` | 多个 headless Chromium 子进程并行渲帧 → ffmpeg 合成 |
| `backend/whatif/narration.py` | 可选旁白：Kokoro / OpenAI TTS、文本口语化、按语音拉长分镜、人声轨对齐与缓存 |
| `backend/whatif/audio.py` | numpy 程序化音效：场景环境床、随速度变亮的风、tick/whoosh/boom/riser/swell/drop、混响、响度归一 |
| `backend/whatif/examples/twice_as_fast.json` | 示例：「每秒快一倍」 |

可选值：场景 `city highway desert ocean sky orbit deep_space lab void`；镜头 `follow front closeup low_front side wide aerial far orbit`；
主体 `runner ball car cube rocket none`（动作 `idle walk run sprint float fly`）；特效 `dust speedlines heat plasma vapor_cone shockwave glow shake flash motion_blur`。

## 性能

软件 WebGL（SwiftShader）下 1080x1920 约 0.4–0.6 s/帧/进程；4 核约 15–20 分钟出 80 秒成片。`--preview` 半分辨率快约 3 倍。
网页是帧号的纯函数，所以可以任意切分帧区间并行。

## 已知限制

- 画面是程序生成的低多边形风格；人物、城市细节比手工建模的参考视频简单
- 新题目若需要现有场景之外的东西（比如「海底」「恐龙」「人体内部」），要在 `envs.js` / `people.js` 里加构建函数并登记到 schema
- 统计数字、信息框、新闻横幅里的事实由 LLM 提供（提示词要求只用公认数据），代码无法核实，发布前请人工核对
- 里程碑的真实数值由 LLM 提供，代码只能保证「越过的时刻」正确；发布前请人工核对参照值本身
