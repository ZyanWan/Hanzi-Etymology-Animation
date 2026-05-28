# Hanzi Etymology Animation

A tool for creating animated videos showing the evolution of Chinese characters from oracle bone script to modern regular script. Designed for teaching Chinese as a foreign language — helping students understand *why* a character looks the way it does.

## Why This Matters

Every Chinese character is a mini visual story. By animating the evolution, students can intuitively grasp:

- **Why the character looks like this** — its pictographic origin
- **Why it means what it means** — the link between original meaning and modern usage
- **How to remember it** — visual anchoring through shape transformation

> Example: The character "qu" originally depicted a hand grabbing an enemy's ear — an ancient war trophy practice. The animation shows this pictograph gradually transforming into the modern character.

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

# 1. Scrape character data (example: "qu" character)
python -m scraper.main qu --mode essential

# 2. Convert SVG to PNG
python -m processors.svg_converter qu

# 3. Generate evolution video (one continuous animation)
python -m processors.wan_video \
    --first data/png/qu/jiaguwen.png \
    --prompt "A white background with black calligraphy of the character qu, starting from oracle bone script with crude uneven strokes resembling a hand grabbing an ear, gradually becoming more regular and rounded as it evolves into bronze inscriptions, then lines becoming uniform and flowing as it becomes small seal script, finally becoming straight and squared as it becomes regular script, the entire process showing the same character naturally and smoothly transforming across different dynasties while maintaining structural integrity, calligraphy style" \
    --resolution 720P --duration 10 \
    -o data/video/qu/qu_evolution.mp4

# 4. Generate TTS narration
python -m processors.tts --text "The original meaning of qu is to cut off enemy ears" --output data/audio/qu/narration.wav
```

> **Note:** The Chinese prompt above is required by the video generation model — it must be in Chinese to produce correct character animations. The model understands Chinese calligraphy descriptions better than English.

## Setup

### API Keys

This project requires two API services. You need to register and obtain keys from each.

#### 1. Alibaba Cloud DashScope (Video Generation)

Used for: Wan2.7 AI video generation (character evolution animations)

**Steps:**
1. Go to [Alibaba Cloud DashScope](https://dashscope.console.aliyun.com/)
2. Register / log in with your Alibaba Cloud account
3. Open **API Key Management** from the left sidebar
4. Click **Create API Key** and copy the generated key
5. New users get free trial credits (check the console for current offer)

**Pricing:** ~0.24 CNY per 5-second video at 720P

#### 2. Volcano Engine (TTS Voice Synthesis)

Used for: Text-to-speech narration (explaining character meaning)

**Steps:**
1. Go to [Volcano Engine Console](https://console.volcengine.com/)
2. Register / log in
3. Search for "Speech Synthesis" (语音合成) in the product console
4. Create an application to get your **AppID**
5. Go to **Access Key** management to get your **Access Key ID**

**Pricing:** Free tier available for basic usage

#### Configure Keys

Copy the example file and fill in your keys:

```bash
cd etymology-animation
cp .env.example .env
```

Edit `.env` with your keys:

```env
# Alibaba Cloud DashScope (Wan2.7 video generation)
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# Volcano Engine (TTS voice synthesis)
VOLC_APPID=1234567890
VOLC_ACCESS_KEY_ID=your_access_key_id_here
```

> **Security:** `.env` is already in `.gitignore` and will not be committed to Git.

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
| Pictograph | Direct drawing of an object | ri, yue, shan, shui | Most intuitive |
| Compound ideograph | Two pictographs combined | qu, xiu, ming, sen | Story-rich |
| Simple indicative | Pictograph + abstract marker | shang, xia, ben, ren | Clever |
| Phono-semantic | Meaning + sound component | jiang, hu, hu | Low value |

**Recommendation**: Start with pictographs and compound ideographs for best results.

## Quality Checklist

- [ ] Scene description is concise (not verbose)
- [ ] Character features are specific (dynasty + characteristics)
- [ ] Shape integrity instruction is included
- [ ] Meaning is integrated, not just shape morphing
- [ ] Background is white, character is black
- [ ] Animation is smooth and continuous

## Documentation

See [`docs/`](etymology-animation/docs/) for detailed guides:

- [Methodology & Character Selection](etymology-animation/docs/01_methodology.md)
- [Data Collection](etymology-animation/docs/02_data_collection.md)
- [AI Video Generation](etymology-animation/docs/04_video_generation.md)
- [Prompt Design](etymology-animation/docs/05_prompt_design.md)
- [Post-Production](etymology-animation/docs/06_post_production.md)

## License

MIT
