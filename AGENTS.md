# AGENTS.md — 字形演变动画制作

**版本**: 2.5.1 | **更新日期**: 2026-05-28  
**Root**: `D:\Desktop\Hanzi`  
**Main code**: `etymology-animation/`

---

## 项目概述

**任务**：为汉字制作字形演变动画，用于对外汉语教学。
**产出**：完整教学视频，展示汉字从甲骨文到楷书的演变。
**核心理念**：让学生理解"这个字为什么长这样"。理解本义，就能理解引申义。

---

## 核心原则（必须遵守）

### 原则1：字形离不开字义

```
字义（为什么变） + 字形（怎么变） = 完整的教学叙事
```

- ✅ **必须**：第1段是场景演绎，让学生先理解字的本义
- ❌ **禁止**：只做干巴巴的字形变形动画

### 原则2：演变是连续流畅的

❌ **错误做法**：每段用首尾帧独立生成（甲骨文→金文、金文→小篆...），然后拼接——这是PPT式切换
✅ **正确做法**：用首帧 + 一段完整prompt描述整个演变过程，让模型生成连续流畅的变化

### 原则3：Prompt由你（中间人）生成

你是Prompt的设计者，不是模板套用机器。

- ✅ **必须**：读取字义数据，融合场景和字形，生成有针对性的Prompt
- ✅ **必须**：根据具体汉字的本义，手动调整Prompt措辞
- ❌ **禁止**：完全依赖脚本模板生成Prompt

### 原则4：场景描述适度

- ✅ **必须**：中等长度，简洁描述本义场景，重点在字形变化
- ❌ **禁止**：大段场景描述，喧宾夺主

---

## Quick Start

```bash
cd D:\Desktop\Hanzi\etymology-animation

# 1. 采集
python -m scraper.main 取 --mode essential

# 2. 转换PNG
python -m processors.svg_converter 取

# 3. 查看元数据，理解字义
# 编辑 data/metadata/char_取_53D6.json

# 4. 生成Prompt（由你根据字义生成，描述完整演变过程）

# 5. 生成视频 — 一段视频展示完整演变（不是分段PPT式！）
python -m processors.wan_video \
    --first data/png/取/jiaguwen.png \
    --prompt "白底黑字的取字，从甲骨文象形笔画开始，笔画稚拙线条不均匀，像一只手抓着一只耳朵，逐渐笔画变规整变圆润演变为金文，再逐渐线条统一圆润演变为小篆，最后横平竖直演变为楷书取字，整个过程是同一个字在不同朝代的字形之间自然流畅地连续变化，保持字形完整不变形，书法风格" \
    --resolution 720P --duration 10 \
    -o data/video/取/取_完整演变.mp4

# 6. 生成TTS旁白
python -m processors.tts --text "取字的本意是割取敌人耳朵" --output data/audio/取/scene_1.wav

# 7. 后期拼接（视频+音频+字幕）
```

---

## 工作流程

### 步骤1：采集数据

```bash
python -m scraper.main 取 --mode essential
```

**采集内容**：SVG图片（甲骨文→金文→小篆→隶书→楷书）+ JSON元数据（字义、本义、说文解字引用）

**验证**：检查 `data/metadata/[汉字].json` 的 `meanings` 字段，不完整则用Playwright分析网页补充。

### 步骤2：转换PNG

```bash
python -m processors.svg_converter 取
```

输出：`data/png/[汉字]/`，尺寸 1024x1024。

### 步骤3：分析分段策略

| 字形类型 | 第1段 | 后续段 |
|----------|-------|--------|
| 象形字 | 场景演绎（3秒） | 2段演变（各2秒） |
| 会意字 | 场景演绎（3秒） | 4段演变（各2秒） |
| 指事字 | 场景演绎（3秒） | 3段演变（各2秒） |

判断方法：读取JSON元数据 `basic_info.analysis` 字段。"会意"→会意字 | "象形"→象形字 | "指事"→指事字

### 步骤4：生成Prompt

**场景演绎Prompt模板**：
```
[简洁的本义场景描述]，
[汉字]字从[场景]逐渐过渡为甲骨文字形，
保持字形完整不变形，
书法风格，画面稳定，3秒
```

**阶段特征参考**：

| 阶段 | 朝代 | 特征描述 |
|------|------|----------|
| 甲骨文 | 商朝 | 象形性强，笔画稚拙，线条不均匀 |
| 金文 | 西周 | 笔画开始规整，线条圆润厚重 |
| 小篆 | 秦朝 | 线条完全统一，圆润流畅，结构修长 |
| 隶书 | 汉朝 | 波磔特征明显，方折代替圆转 |
| 楷书 | 现代 | 横平竖直，方块字形，标准规范 |

### 步骤5：调用Wan2.7生成视频

**参数**：模型 `wan2.7-i2v-2026-04-25`，时长 10-15秒，分辨率 720P
**输入**：首帧（甲骨文PNG）+ 完整演变prompt，**不要用 --last**

```bash
python -m processors.wan_video \
    --first data/png/取/jiaguwen.png \
    --prompt "白底黑字的取字，从甲骨文象形笔画开始..." \
    --resolution 720P --duration 10 \
    -o data/video/取/取_完整演变.mp4
```

### 步骤6：生成TTS旁白

```bash
python -m processors.tts --text "取字的本意是割取敌人耳朵" --output data/audio/取/scene_1.wav
```

**语音类型**：`BV700_V2_streaming`（标准女声，推荐）

### 步骤7：拼接成品

后期处理：视频拼接 → 字幕叠加 → MP4/GIF成品

---

## 项目结构

```
etymology-animation/
├── scraper/              # 数据采集工具
│   ├── main.py           # 主入口
│   └── zdic_scraper.py
├── processors/           # 数据处理模块
│   ├── prompt_generator.py   # Prompt生成（参考模板）
│   ├── segment_analyzer.py   # 分段分析
│   ├── svg_converter.py      # SVG转PNG
│   ├── wan_video.py          # 阿里云Wan2.7视频生成
│   ├── tts.py                # 火山引擎TTS配音
│   ├── protocols.py          # TTS协议定义
│   └── __init__.py           # 环境变量加载
├── data/
│   ├── raw/[汉字]/           # SVG原始图片
│   ├── png/[汉字]/           # PNG转换图片
│   ├── metadata/[汉字].json  # 元数据（含字义）
│   ├── prompts/[汉字].json   # 生成的Prompt
│   ├── audio/[汉字]/         # TTS音频文件
│   └── video/[汉字]/         # 生成的视频文件
└── docs/                     # 工作流文档（参考用）
```

---

## API Keys（从 .env 加载）

- `VOLC_APPID` / `VOLC_ACCESS_KEY_ID`：火山引擎TTS
- `DASHSCOPE_API_KEY`：阿里云百炼 Wan2.7 视频生成

---

## 数据结构

### 元数据JSON

```json
{
  "character": "取",
  "basic_info": { "analysis": "会意；从耳、从又" },
  "meanings": [{ "type": "本义", "text": "割取敌人的耳朵（古代战争中割耳计功）" }],
  "citations": [{ "source": "《说文解字》", "text": "捕取也。从又从耳。" }]
}
```

---

## 质量检查清单

- [ ] 场景描述简洁（中度），不冗长
- [ ] 字形特征描述具体（朝代+特征）
- [ ] 明确指出"保持字形完整不变形"
- [ ] 融入字义，不只是干巴巴的字形变化
- [ ] 字形结构保持完整，笔画过渡自然流畅
- [ ] 背景白色，字形黑色，画面稳定

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 字义数据不完整 | 用Playwright分析网页，找出正确的数据位置 |
| 场景描述太长 | 精简到50字以内 |
| 字形变形 | 降低运动幅度/创意度参数 |
| 采集失败 | 检查网络，用Playwright验证页面结构 |
| SVG转换错误 | `pip install cairosvg pillow` |
| TTS错误 | 检查 `.env` 中 `VOLC_APPID` 和 `VOLC_ACCESS_KEY_ID` |
| 视频生成错误 | 检查 `.env` 中 `DASHSCOPE_API_KEY`；视频URL 24小时过期 |
