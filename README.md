# Hanzi Etymology Animation

A tool for creating animated videos showing the evolution of Chinese characters from oracle bone script (甲骨文) to modern regular script (楷书). Designed for teaching Chinese as a foreign language — helping students understand *why* a character looks the way it does.

## Why This Matters

Every Chinese character is a mini visual story. By animating the evolution, students can intuitively grasp:

- **Why the character looks like this** — its pictographic origin
- **Why it means what it means** — the link between original meaning and modern usage
- **How to remember it** — visual anchoring through shape transformation

> Example: 取 (qǔ, "to take") originally depicted a hand grabbing an enemy's ear — an ancient war trophy practice. The animation shows this pictograph gradually transforming into the modern character.

## Features

- **Automated data scraping** — pulls character etymology data (SVG glyphs + metadata) from zdic.net
- **SVG-to-PNG conversion** — prepares images for AI video generation
- **AI video generation** — uses Alibaba Cloud's Wan2.7 model to create smooth evolution animations
- **TTS narration** — generates voiceover explaining character meaning (Volcano Engine)
- **Continuous evolution** — single prompt generates fluid transformation across all historical stages

## Quick Start

```bash
# Clone the repo
git clone https://github.com/your-username/Hanzi.git
cd Hanzi/etymology-animation

# Install dependencies
pip install -r requirements.txt

# 1. Scrape character data
python -m scraper.main 取 --mode essential

# 2. Convert SVG to PNG
python -m processors.svg_converter 取

# 3. Generate evolution video (one continuous animation)
python -m processors.wan_video \
    --first data/png/取/jiaguwen.png \
    --prompt "白底黑字的取字，从甲骨文象形笔画开始，笔画稚拙线条不均匀，像一只手抓着一只耳朵，逐渐笔画变规整变圆润演变为金文，再逐渐线条统一圆润演变为小篆，最后横平竖直演变为楷书取字，整个过程是同一个字在不同朝代的字形之间自然流畅地连续变化，保持字形完整不变形，书法风格" \
    --resolution 720P --duration 10 \
    -o data/video/取/取_完整演变.mp4

# 4. Generate TTS narration
python -m processors.tts --text "取字的本意是割取敌人耳朵" --output data/audio/取/scene_1.wav
```

## Setup

### API Keys

Create `etymology-animation/.env`:

```env
# Alibaba Cloud DashScope (Wan2.7 video generation)
DASHSCOPE_API_KEY=your_dashscope_key

# Volcano Engine (TTS voice synthesis)
VOLC_APPID=your_app_id
VOLC_ACCESS_KEY_ID=your_access_key
```

### Dependencies

```bash
pip install requests cairosvg pillow websockets python-dotenv
```

For web scraping:
```bash
pip install playwright
playwright install chromium
```

## Workflow

```
1. Scrape    →  Collect SVG glyphs + etymology metadata from zdic.net
2. Convert   →  Transform SVGs to 1024x1024 PNGs
3. Prompt    →  Design evolution narrative based on character meaning
4. Generate  →  Create continuous animation with Wan2.7
5. Narrate   →  Add TTS voiceover explaining the character
6. Assemble  →  Combine video + audio + subtitles
```

## Project Structure

```
├── etymology-animation/
│   ├── scraper/               # Data collection from zdic.net
│   │   ├── main.py            # Entry point
│   │   └── zdic_scraper.py    # Web scraper
│   ├── processors/            # Data processing modules
│   │   ├── wan_video.py       # Alibaba Cloud Wan2.7 video gen
│   │   ├── tts.py             # Volcano Engine TTS
│   │   ├── svg_converter.py   # SVG to PNG conversion
│   │   ├── prompt_generator.py # Prompt templates (reference)
│   │   └── segment_analyzer.py # Character type analysis
│   ├── data/
│   │   ├── raw/[char]/        # Original SVGs
│   │   ├── png/[char]/        # Converted PNGs
│   │   ├── metadata/[char].json # Etymology metadata
│   │   ├── audio/[char]/      # TTS audio files
│   │   └── video/[char]/      # Generated videos
│   └── docs/                  # Workflow documentation
├── AGENTS.md                  # AI agent instructions
└── README.md
```

## Character Types

The tool handles different character types with appropriate animation strategies:

| Type | Description | Example | Animation Value |
|------|-------------|---------|-----------------|
| Pictograph (象形) | Direct drawing of an object | 日, 月, 山, 水 | ★★★ Most intuitive |
| Compound ideograph (会意) | Two pictographs combined | 取, 休, 明, 森 | ★★★ Story-rich |
| Simple indicative (指事) | Pictograph + abstract marker | 上, 下, 本, 刃 | ★★ Clever |
| Phono-semantic (形声) | Meaning + sound component | 江, 河, 湖 | ★ Low value |

**Recommendation**: Start with P0 (pictographs) and P1 (compound ideographs).

## Quality Checklist

- [ ] Scene description is concise (not verbose)
- [ ] Character features are specific (dynasty + characteristics)
- [ ] "保持字形完整不变形" (maintain shape integrity) is included
- [ ] Meaning is integrated, not just shape morphing
- [ ] Background is white, character is black
- [ ] Animation is smooth and continuous

## Documentation

See [`docs/`](etymology-animation/docs/) for detailed guides:

- [Methodology & Character Selection](etymology-animation/docs/01_方法论与选字.md)
- [Data Collection](etymology-animation/docs/02_字源采集.md)
- [AI Video Generation](etymology-animation/docs/04_AI视频生成.md)
- [Prompt Design](etymology-animation/docs/05_Prompt集.md)
- [Post-Production](etymology-animation/docs/06_后期制作.md)

## License

MIT
