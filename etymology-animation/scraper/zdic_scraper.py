# -*- coding: utf-8 -*-
"""
汉典网站爬虫模块
从汉典网站提取字源数据和图片URL
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Dict, List, Optional
from pathlib import Path

from .config import (
    ZDIC_BASE_URL,
    ZDIC_SEARCH_URL,
    IMG_CDN_BASE,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    USER_AGENT,
    ARCHAIC_TYPES
)
from .unicode_utils import char_to_unicode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ZdicScraper:
    """汉典网站数据爬虫"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.unicode_resolver = char_to_unicode

    def _fetch_page(self, url: str) -> Optional[str]:
        """
        获取网页内容，带重试机制

        Args:
            url: 目标URL

        Returns:
            网页HTML内容，失败返回None
        """
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                response.encoding = 'utf-8'
                return response.text
            except requests.RequestException as e:
                logger.warning(f"获取页面失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {url} - {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))
        return None

    def get_char_page_url(self, char: str) -> str:
        """获取汉字的汉典页面URL"""
        return ZDIC_SEARCH_URL.format(char=char)

    def scrape_char_info(self, char: str, mode: str = "essential") -> Dict:
        """
        爬取汉字的详细信息

        Args:
            char: 单个汉字
            mode: 采集模式
                - "full": 完整采集
                - "essential": 关键阶段采集（推荐）
                - "minimal": 最小采集

        Returns:
            包含字源信息的字典
        """
        url = self.get_char_page_url(char)
        html = self._fetch_page(url)

        if not html:
            logger.error(f"无法获取汉字 '{char}' 的页面")
            return {}

        soup = BeautifulSoup(html, 'html.parser')
        info = {
            "character": char,
            "unicode": self.unicode_resolver(char),
            "basic_info": self._extract_basic_info(soup),
            "meanings": self._extract_meanings(soup),
            "citations": self._extract_citations(soup),
            "evolution_images": self._extract_evolution_images(soup, mode),
            "structure_analysis": self._extract_structure(soup),
        }

        return info

    def _extract_basic_info(self, soup: BeautifulSoup) -> Dict:
        """提取基本信息（拼音、部首、笔画等）"""
        info = {}
        
        page_layout = soup.find('div', {'class': 'page-layout'})
        search_area = page_layout if page_layout else soup
        
        page_text = search_area.get_text()
        
        # 查找拼音
        pinyin_elem = search_area.find('a', {'href': lambda x: x and 'pinyin' in str(x)})
        if pinyin_elem:
            info['pinyin'] = pinyin_elem.get_text(strip=True)
        
        # 查找部首
        radical_elem = search_area.find('a', {'href': lambda x: x and 'bushou' in str(x)})
        if radical_elem:
            info['radical'] = radical_elem.get_text(strip=True)
        
        # 查找笔画数
        stroke_match = re.search(r'总笔画[：:]\s*(\d+)', page_text)
        if stroke_match:
            info['total_strokes'] = int(stroke_match.group(1))
        
        # 查找结构
        structure_match = re.search(r'字形结构[：:]\s*([^\s\n]+)', page_text)
        if structure_match:
            info['structure'] = structure_match.group(1)
        
        # 查找字形分析
        analysis_match = re.search(r'字形分析[：:]\s*([^<\n]+)', page_text)
        if analysis_match:
            info['analysis'] = analysis_match.group(1).strip()
        
        return info

    def _extract_meanings(self, soup: BeautifulSoup) -> List[Dict]:
        """提取字义解释（本义、引申义等）"""
        meanings = []
        
        # 方法1：从详细解释区域提取（id="xxjs"）
        xxjs_section = soup.find('section', {'id': 'xxjs'})
        if not xxjs_section:
            xxjs_section = soup.find('div', {'class': 'xxjs-section'})
        
        if xxjs_section:
            # 提取本义定义
            benyi_def = xxjs_section.find('div', {'class': 'xxjs-item__def'})
            if benyi_def:
                text = benyi_def.get_text(strip=True)
                if '本义' in text or '会意' in text or '象形' in text:
                    meanings.append({
                        "type": "本义",
                        "text": text,
                        "description": ""
                    })
            
            # 提取字义说明
            pos_section = xxjs_section.find('div', {'class': 'xxjs-pos-section'})
            if pos_section:
                all_text = pos_section.get_text()
                
                # 提取本义
                benyi_pattern = re.search(r'\((?:会意|象形|指事|形声)[^)]+\)', all_text)
                if benyi_pattern and not meanings:
                    meanings.append({
                        "type": "本义",
                        "text": benyi_pattern.group(0).strip(),
                        "description": ""
                    })
        
        # 方法2：从页面文本提取
        if not meanings:
            page_text = soup.get_text()
            
            # 提取本义
            benyi_match = re.search(r'本义[：:]\s*[\(（]?([^）\)。]+)', page_text)
            if benyi_match:
                meanings.append({
                    "type": "本义",
                    "text": benyi_match.group(1).strip(),
                    "description": ""
                })
            
            # 提取引申义
            fansheng_match = re.search(r'引申义[：:]\s*([^。]+)', page_text)
            if fansheng_match:
                meanings.append({
                    "type": "引申义",
                    "text": fansheng_match.group(1).strip()[:200],
                    "description": ""
                })
        
        return meanings

    def _extract_citations(self, soup: BeautifulSoup) -> List[Dict]:
        """提取古籍引用（说文解字、康熙字典等）"""
        citations = []
        
        # 方法1：从说文解字区域提取（id="swjz"）
        swjz_section = soup.find('section', {'id': 'swjz'})
        if not swjz_section:
            swjz_section = soup.find('div', {'class': 'dict-section'})
        
        if swjz_section:
            section_text = swjz_section.get_text()
            
            # 提取说文原文
            swjz_pattern = re.search(r'捕取也[^{]*(?:《[^》]+》[^}])*', section_text)
            if swjz_pattern:
                text = swjz_pattern.group(0).strip()
                if len(text) > 5:
                    citations.append({
                        "source": "《说文解字》",
                        "text": text[:200],
                        "description": ""
                    })
        
        # 方法2：从页面文本提取
        if not citations:
            full_text = soup.get_text()
            
            # 提取《说文解字》引用
            swjz_patterns = [
                r'《说文解字》[》]?\s*[""\']([^""\']+)[""\']',
                r'《说文解字》[：:]\s*([^。\n]+)',
                r'说文[解字]?[：:]\s*([^。\n]+)',
            ]
            for pattern in swjz_patterns:
                swjz_match = re.search(pattern, full_text)
                if swjz_match:
                    text = swjz_match.group(1).strip()
                    if len(text) > 5 and len(text) < 200:
                        citations.append({
                            "source": "《说文解字》",
                            "text": text,
                            "description": ""
                        })
                        break
            
            # 提取《康熙字典》引用
            kxzd_patterns = [
                r'《康熙字典》[》]?\s*[""\']([^""\']+)[""\']',
                r'《康熙字典》[：:]\s*([^。\n]+)',
            ]
            for pattern in kxzd_patterns:
                kxzd_match = re.search(pattern, full_text)
                if kxzd_match:
                    text = kxzd_match.group(1).strip()
                    if len(text) > 5 and len(text) < 200:
                        citations.append({
                            "source": "《康熙字典》",
                            "text": text,
                            "description": ""
                        })
                        break
        
        return citations

    def _extract_evolution_images(self, soup: BeautifulSoup, mode: str = "essential") -> Dict[str, List[str]]:
        """
        提取字形演变图片URL

        Args:
            soup: BeautifulSoup解析后的页面对象
            mode: 采集模式
                - "full": 完整采集（所有阶段，每个阶段多个变体）
                - "essential": 关键阶段采集（推荐，只采4个阶段）
                - "minimal": 最小采集（只采3个核心阶段）

        Returns:
            {阶段类型: [图片信息列表]}
        """
        from .config import COLLECTION_MODES

        mode_config = COLLECTION_MODES.get(mode, COLLECTION_MODES["essential"])
        allowed_types = mode_config["archaic_types"]
        max_variants = mode_config["max_variants"]

        images = {type_name: [] for type_name in allowed_types}

        # 查找所有图片
        img_tags = soup.find_all('img')

        for img in img_tags:
            src = img.get('src', '')
            alt = img.get('alt', '')

            # 修复URL：添加协议前缀
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://www.zdic.net' + src

            # 检查是否是字源演变图片
            if 'img.zdic.net' in src:
                for type_name in allowed_types:
                    if type_name in src:
                        # 根据模式限制变体数量
                        if len(images[type_name]) < max_variants:
                            images[type_name].append({
                                "url": src,
                                "alt": alt,
                                "type": type_name
                            })
                        break

        # 过滤空列表
        filtered_images = {k: v for k, v in images.items() if v}

        # 记录采集模式
        if filtered_images:
            filtered_images["_collection_mode"] = mode
            filtered_images["_stage_info"] = {
                stage: mode_config.get(stage, {}).get("name", stage)
                for stage in filtered_images.keys() if not stage.startswith("_")
            }

        return filtered_images

    def _extract_structure(self, soup: BeautifulSoup) -> Optional[str]:
        """提取字形结构分析"""
        text = soup.get_text()

        # 查找"会意"、"象形"等构字说明
        structure_match = re.search(r'字形分析[：:]\s*([^<\n]+)', text)
        if structure_match:
            return structure_match.group(1).strip()

        return None

    def batch_scrape(self, chars: List[str], delay: float = 1.0, mode: str = "essential") -> Dict[str, Dict]:
        """
        批量爬取多个汉字的数据

        Args:
            chars: 汉字列表
            delay: 请求间隔（秒）
            mode: 采集模式
                - "full": 完整采集
                - "essential": 关键阶段采集（推荐）
                - "minimal": 最小采集

        Returns:
            以汉字为键的字典，包含每个汉字的数据
        """
        results = {}

        for i, char in enumerate(chars):
            logger.info(f"正在爬取 ({i + 1}/{len(chars)}): '{char}' (模式: {mode})")

            try:
                info = self.scrape_char_info(char, mode)
                if info:
                    results[char] = info
                    logger.info(f"✓ 成功获取 '{char}' 的数据")
                else:
                    logger.warning(f"✗ 无法获取 '{char}' 的数据")

                # 请求间隔，避免被封
                if i < len(chars) - 1:
                    time.sleep(delay)

            except Exception as e:
                logger.error(f"处理 '{char}' 时出错: {e}")
                continue

        return results

    def close(self):
        """关闭会话"""
        self.session.close()


def scrape_char(char: str, mode: str = "essential") -> Dict:
    """
    便捷函数：爬取单个汉字的数据

    Args:
        char: 单个汉字
        mode: 采集模式
            - "full": 完整采集
            - "essential": 关键阶段采集（推荐）
            - "minimal": 最小采集

    Returns:
        字源数据字典
    """
    scraper = ZdicScraper()
    try:
        return scraper.scrape_char_info(char, mode)
    finally:
        scraper.close()
