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

环境修饰（`env`，同场景内沿用）：时段 `day golden dusk night dawn`、天气 `rain storm snow ash fog dust overcast`、
天象 `red dark meteors`、人群/车流密度、`empty`（人消失）、`lights_off`、`overgrown`（荒废长草）、`damage`（碎片）。
人物：`person`/`cast` 支持服装 `casual hoodie scrubs doctor hivis suit robe soldier child ranger police` 与姿势
`idle walk run sprint sit kneel lie point phone pray fall float fly`；`vanish` 效果让人逐个消失。

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
| `backend/whatif/web/` | three.js 场景（`world.js`/`envs.js` 环境与时段天气、`people.js` 人物与人群、`actors.js` 道具与特效）+ HTML/SVG 叠加层（`overlay.js`、`icons.js`） |
| `backend/whatif/render.py` | 多个 headless Chromium 子进程并行渲帧 → ffmpeg 合成 |
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
