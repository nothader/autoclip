# What-if 科普短视频生成器（`autoclip whatif`）

输入一个「如果……会怎样」的题目，输出一条 9:16 竖屏短视频：低多边形 3D 模拟画面 + 顶部数据 HUD +
越过真实参照值时弹出的里程碑标注 + 每镜一句斜体字幕 + 结尾阶梯图表和问句卡，配程序化音效（无旁白、无音乐）。

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
| `backend/whatif/web/` | three.js 场景（`world.js` 环境、`actors.js` 主体与特效）+ HTML 叠加层（`overlay.js`） |
| `backend/whatif/render.py` | 多个 headless Chromium 子进程并行渲帧 → ffmpeg 合成 |
| `backend/whatif/audio.py` | numpy 程序化音效：场景环境床、随速度变亮的风、tick/whoosh/boom/riser/swell/drop、混响、响度归一 |
| `backend/whatif/examples/twice_as_fast.json` | 示例：「每秒快一倍」 |

可选值：场景 `city highway desert ocean sky orbit deep_space lab void`；镜头 `follow front closeup low_front side wide aerial far orbit`；
主体 `runner ball car cube rocket none`（动作 `idle walk run sprint float fly`）；特效 `dust speedlines heat plasma vapor_cone shockwave glow shake flash motion_blur`。

## 性能

软件 WebGL（SwiftShader）下 1080x1920 约 0.4–0.6 s/帧/进程；4 核约 8–12 分钟出 80 秒成片。`--preview` 半分辨率快约 3 倍。
网页是帧号的纯函数，所以可以任意切分帧区间并行。

## 已知限制

- 画面是程序生成的低多边形风格；人物、城市细节比手工建模的参考视频简单
- 新题目若需要新的场景/主体（比如「海底」「恐龙」），要在 `world.js` / `actors.js` 里加构建函数并登记到 schema
- 里程碑的真实数值由 LLM 提供，代码只能保证「越过的时刻」正确；发布前请人工核对参照值本身
