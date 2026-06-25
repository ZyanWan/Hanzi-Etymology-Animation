# 汉字词源动画工具

一款用于创建汉字演变动画视频的工具，展示汉字从甲骨文到现代楷书的演变历程。专为对外汉语教学设计——帮助学生理解汉字为何呈现如今的面貌。

## 为什么这很重要

每个汉字都是一个微型视觉故事。通过动画展示演变过程，学生可以直观地理解：

- **为什么这个字长这样**——它的象形起源
- **为什么它表示这个意思**——原始含义与现代用法之间的联系
- **如何记住它**——通过字形变化进行视觉锚定

> 示例："取"字最初描绘的是一只手抓住敌人的耳朵——这是古代割取敌人首级或耳朵作为战利品的做法。动画展示这个象形字如何逐渐演变成现代汉字。

## 功能特点

- **自动化数据采集**——从汉典网抓取汉字词源数据（SVG字形 + 元数据）
- **SVG转PNG转换**——为AI视频生成准备图像素材
- **AI视频生成**——使用阿里云Wan2.7模型创建流畅的演变动画
- **TTS语音解说**——生成讲解汉字含义的语音旁白（火山引擎）
- **连续演变**——单次提示词即可生成贯穿所有历史阶段的流畅变形动画

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/your-username/Hanzi.git
cd Hanzi/etymology-animation

# 安装依赖
pip install -r requirements.txt

# 1. 采集字符数据（以"取"字为例）
python -m scraper.main qu --mode essential

# 2. 将SVG转换为PNG
python -m processors.svg_converter qu

# 3. 生成演变视频（单次连续动画）
python -m processors.wan_video \
    --first data/png/qu/jiaguwen.png \
    --prompt "白色背景上呈现黑色书法字形取，从笔画粗细不均、字形类似手抓耳朵的甲骨文，逐渐演变为更加规整圆润的金文，随后笔画统一流畅的小篆，最后成为方正的楷书，整个过程展示同一汉字在不同朝代间自然流畅地变形转化，同时保持结构完整性，书风遒劲有力" \
    --resolution 720P --duration 10 \
    -o data/video/qu/qu_evolution.mp4

# 4. 生成TTS语音解说
python -m processors.tts --text "取的本义是割取敌人的耳朵" --output data/audio/qu/narration.wav
```

> **注意**：上述中文提示词是视频生成模型的必需输入——必须使用中文才能产生正确的汉字动画效果。该模型对中文书法描述的理解优于英文。

## 安装配置

### API密钥

本项目需要两个API服务，需分别注册获取密钥。

#### 1. 阿里云DashScope（视频生成）

用途：Wan2.7 AI视频生成（汉字演变动画）

**步骤：**
1. 访问[阿里云DashScope](https://dashscope.console.aliyun.com/)
2. 使用阿里云账号注册/登录
3. 在左侧导航栏打开**API-KEY管理**
4. 点击**创建API-KEY**并复制生成的密钥
5. 新用户享有免费试用额度（请查看当前优惠）

**价格：** 约0.24元/5秒视频（720P）

#### 2. 火山引擎（TTS语音合成）

用途：文本转语音旁白（讲解汉字含义）

**步骤：**
1. 访问[火山引擎控制台](https://console.volcengine.com/)
2. 注册/登录
3. 在产品控制台搜索"语音合成"
4. 创建应用以获取**AppID**
5. 进入**访问密钥**管理获取**Access Key ID**

**价格：** 基础用量免费

#### 配置密钥

复制示例文件并填写密钥：

```bash
cd etymology-animation
cp .env.example .env
```

编辑`.env`填入你的密钥：

```env
# 阿里云DashScope（Wan2.7视频生成）
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# 火山引擎（TTS语音合成）
VOLC_APPID=1234567890
VOLC_ACCESS_KEY_ID=your_access_key_id_here
```

> **安全性**：`.env`已在`.gitignore`中，不会被提交到Git。

### 依赖安装

```bash
pip install requests cairosvg pillow websockets python-dotenv
```

网页抓取所需：
```bash
pip install playwright
playwright install chromium
```

## 工作流程

```
1. 采集    →  从汉典网收集SVG字形 + 词源元数据
2. 转换    →  将SVG转换为1024x1024的PNG图片
3. 撰写提示词 →  根据汉字含义设计演变叙事
4. 生成    →  使用Wan2.7创建连续动画
5. 配音    →  添加讲解汉字含义的TTS语音旁白
6. 合成    →  合并视频 + 音频 + 字幕
```

## 项目结构

```
├── etymology-animation/
│   ├── scraper/               # 从汉典网采集数据
│   │   ├── main.py            # 入口文件
│   │   └── zdic_scraper.py    # 网页抓取器
│   ├── processors/            # 数据处理模块
│   │   ├── wan_video.py       # 阿里云Wan2.7视频生成
│   │   ├── tts.py             # 火山引擎TTS
│   │   ├── svg_converter.py   # SVG转PNG
│   │   ├── prompt_generator.py # 提示词模板（参考）
│   │   └── segment_analyzer.py # 字符类型分析
│   ├── data/
│   │   ├── raw/[char]/        # 原始SVG文件
│   │   ├── png/[char]/        # 转换后的PNG文件
│   │   ├── metadata/[char].json # 词源元数据
│   │   ├── audio/[char]/      # TTS音频文件
│   │   └── video/[char]/      # 生成的视频文件
│   └── docs/                  # 工作流程文档
├── AGENTS.md                  # AI智能体说明
└── README.md
```

## 汉字类型

工具针对不同类型的汉字采用相应的动画策略：

| 类型 | 说明 | 示例 | 动画价值 |
|------|------|------|----------|
| 象形字 | 事物的直接图画 | 日、月、山、水 | 最为直观 |
| 会意字 | 两个象形字组合 | 取、休、明、森 | 故事性强 |
| 指事字 | 象形字 + 抽象标记 | 上、下、本、刃 | 巧妙精妙 |
| 形声字 | 义符 + 声符组合 | 江、湖、糊 | 价值较低 |

**建议**：优先选择象形字和会意字，效果最佳。

## 质量检查清单

- [ ] 场景描述简洁（不冗长）
- [ ] 汉字特征具体（朝代 + 特征）
- [ ] 包含结构完整性指令
- [ ] 融入含义讲解，而非单纯字形变形
- [ ] 背景为白色，汉字为黑色
- [ ] 动画流畅连续

## 文档

详见[`docs/`](etymology-animation/docs/)中的详细指南：

- [方法论与汉字选择](etymology-animation/docs/01_methodology.md)
- [数据采集](etymology-animation/docs/02_data_collection.md)
- [AI视频生成](etymology-animation/docs/04_video_generation.md)
- [提示词设计](etymology-animation/docs/05_prompt_design.md)
- [后期制作](etymology-animation/docs/06_post_production.md)

## 开源许可

MIT
