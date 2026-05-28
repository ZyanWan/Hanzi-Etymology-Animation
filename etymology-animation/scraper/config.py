# -*- coding: utf-8 -*-
"""
汉典字源数据采集系统 - 配置文件
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# 确保目录存在
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# 汉典网站配置
ZDIC_BASE_URL = "https://www.zdic.net"
ZDIC_SEARCH_URL = "https://www.zdic.net/hans/{char}"

# 图片CDN配置
IMG_CDN_BASE = "https://img.zdic.net"

# 图片URL模板（通过Unicode可直接访问）
IMG_URL_TEMPLATES = {
    "kaishu_cn": "https://img.zdic.net/kai/cn/{unicode}.svg",
    "kaishu_hk": "https://img.zdic.net/kai/hk/{unicode}.svg",
    "kaishu_tw": "https://img.zdic.net/kai/tw/{unicode}.svg",
    "kaishu_jp": "https://img.zdic.net/kai/jp/{unicode}.svg",
    "kaishu_kr": "https://img.zdic.net/kai/kr/{unicode}.svg",
    "kxzd": "https://img.zdic.net/kxzd/{unicode}.svg",
    "swxz": "https://img.zdic.net/swxz/{unicode}.svg",
}

# 古文字URL模式（需要从页面提取）
ARCHAIC_TYPES = ["jiaguwen", "jinwen", "chuwenzi", "xiaozhuan", "qinwenzi", "lishu", "chuanchao"]

# 采集模式配置
COLLECTION_MODES = {
    "full": {
        "name": "完整采集",
        "description": "采集所有演变阶段的图片（每个阶段多个变体）",
        "archaic_types": ARCHAIC_TYPES,
        "standard_types": ["kaishu_cn", "kaishu_hk", "kaishu_tw", "kaishu_jp", "kaishu_kr", "kxzd", "swxz"],
        "max_variants": 10,  # 每个阶段最多采集的变体数
    },
    "essential": {
        "name": "关键阶段采集（推荐）",
        "description": "只采集变化最显著的4个阶段，适合AI视频生成",
        "archaic_types": ["jiaguwen", "jinwen", "xiaozhuan", "lishu"],
        "standard_types": ["kaishu_cn"],
        "max_variants": 1,  # 每个阶段只取1个代表性字形
    },
    "minimal": {
        "name": "最小采集",
        "description": "只采集3个核心阶段：甲骨文、小篆、楷书",
        "archaic_types": ["jiaguwen", "xiaozhuan"],
        "standard_types": ["kaishu_cn"],
        "max_variants": 1,
    }
}

# 关键演变阶段说明（用于教学和Prompt生成）
EVOLUTION_STAGES = {
    "jiaguwen": {
        "name": "甲骨文",
        "period": "商代",
        "feature": "象形性强，最接近原始图画",
        "teaching_value": "帮助学生建立'字来自画'的认知"
    },
    "jinwen": {
        "name": "金文",
        "period": "西周",
        "feature": "笔画开始规整化，青铜器铭文",
        "teaching_value": "体现从图画到符号的过渡"
    },
    "xiaozhuan": {
        "name": "小篆",
        "period": "秦代",
        "feature": "线条完全统一，曲线圆润",
        "teaching_value": "汉字规范化的里程碑"
    },
    "lishu": {
        "name": "隶书",
        "period": "汉代",
        "feature": "波磔特征明显，方折代替圆转",
        "teaching_value": "古今字形差异最大"
    },
    "kaishu_cn": {
        "name": "楷书",
        "period": "现代",
        "feature": "标准方块字，横平竖直",
        "teaching_value": "对接学习者的日常使用场景"
    }
}

# 推荐采集组合（用于AI视频生成）
RECOMMENDED_COMBINATIONS = {
    "best": ["jiaguwen", "xiaozhuan", "kaishu_cn"],  # 最佳：3阶段
    "good": ["jiaguwen", "jinwen", "xiaozhuan", "lishu", "kaishu_cn"],  # 完整：5阶段
    "minimal": ["jiaguwen", "xiaozhuan", "kaishu_cn"],  # 最简：3阶段
}

# 请求配置
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
RETRY_DELAY = 2

# 下载配置
MAX_CONCURRENT_DOWNLOADS = 5
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 采集优先级配置
PRIORITY_CONFIG = {
    "P0": {"types": ["独体象形字"], "weight": 1.0},
    "P1": {"types": ["会意字"], "weight": 0.8},
    "P2": {"types": ["指事字"], "weight": 0.6},
    "P3": {"types": ["形声字"], "weight": 0.3},
}

# 日志配置
LOG_FILE = DATA_DIR / "scraper.log"
