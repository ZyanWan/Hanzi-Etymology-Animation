# -*- coding: utf-8 -*-
"""
图片下载器模块
支持批量下载图片，带重试机制和进度显示
"""

import requests
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from .config import (
    IMG_URL_TEMPLATES,
    IMG_CDN_BASE,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    USER_AGENT,
    RAW_DIR,
    MAX_CONCURRENT_DOWNLOADS
)
from .unicode_utils import char_to_unicode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageDownloader:
    """图片批量下载器"""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or RAW_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'Referer': 'https://www.zdic.net/',
        })

    def _download_single_image(self, url: str, filepath: Path, char: str = "") -> bool:
        """
        下载单个图片，带重试机制

        Args:
            url: 图片URL
            filepath: 保存路径
            char: 汉字（用于日志）

        Returns:
            是否成功
        """
        for attempt in range(MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()

                # 检查是否是有效图片
                if response.headers.get('content-type', '').startswith('image/'):
                    filepath.write_bytes(response.content)
                    logger.debug(f"✓ 下载成功: {filepath.name}")
                    return True
                else:
                    logger.warning(f"✗ 响应不是图片: {url}")

            except requests.RequestException as e:
                logger.warning(f"下载失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {url} - {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY * (attempt + 1))

        return False

    def generate_standard_urls(self, char: str) -> Dict[str, str]:
        """
        生成标准字体的图片URL（楷书、康熙字典等）

        Args:
            char: 单个汉字

        Returns:
            {书体类型: URL} 的字典
        """
        unicode_hex = char_to_unicode(char)
        urls = {}

        for font_type, template in IMG_URL_TEMPLATES.items():
            urls[font_type] = template.format(unicode=unicode_hex)

        return urls

    def generate_archaic_urls(self, variant_urls: List[Dict]) -> List[Dict]:
        """
        处理古文字变体URL

        Args:
            variant_urls: 从网页提取的古文字URL列表

        Returns:
            处理后的URL列表
        """
        return [
            {
                "url": item["url"],
                "type": item["type"],
                "alt": item.get("alt", ""),
                "filename": self._generate_filename(char="", font_type=item["type"], index=i)
            }
            for i, item in enumerate(variant_urls)
        ]

    def _generate_filename(self, char: str, font_type: str, index: int = 0, extension: str = ".svg") -> str:
        """生成文件名"""
        if index > 0:
            return f"{char}_{font_type}_{index:02d}{extension}"
        return f"{char}_{font_type}{extension}"

    def download_for_char(self, char: str, evolution_images: Dict[str, List] = None,
                          download_standard: bool = True, mode: str = "essential") -> Dict[str, str]:
        """
        下载某个汉字的所有相关图片

        Args:
            char: 单个汉字
            evolution_images: 从网页提取的古文字图片URL
            download_standard: 是否下载标准字体（楷书等）
            mode: 采集模式
                - "full": 完整采集
                - "essential": 关键阶段采集（推荐）
                - "minimal": 最小采集

        Returns:
            {文件名: URL} 的字典，记录下载情况
        """
        from .config import COLLECTION_MODES

        downloaded = {}
        unicode_hex = char_to_unicode(char)
        mode_config = COLLECTION_MODES.get(mode, COLLECTION_MODES["essential"])
        allowed_standard_types = mode_config["standard_types"]

        # 创建该汉字的专属目录
        char_dir = self.output_dir / char
        char_dir.mkdir(exist_ok=True)

        # 1. 下载标准字体（根据模式筛选）
        if download_standard:
            all_standard_urls = self.generate_standard_urls(char)
            for font_type, url in all_standard_urls.items():
                # 只下载模式允许的标准字体
                if font_type in allowed_standard_types:
                    filename = self._generate_filename(char, font_type)
                    filepath = char_dir / filename

                    if self._download_single_image(url, filepath, char):
                        downloaded[filename] = url

                    time.sleep(0.5)  # 避免请求过快

        # 2. 下载古文字变体（根据模式筛选）
        if evolution_images:
            for font_type, images in evolution_images.items():
                # 跳过元数据键
                if font_type.startswith("_"):
                    continue

                for i, img_info in enumerate(images):
                    filename = self._generate_filename(char, font_type, i + 1)
                    filepath = char_dir / filename

                    if self._download_single_image(img_info["url"], filepath, char):
                        downloaded[filename] = img_info["url"]

                    time.sleep(0.5)

        return downloaded

    def batch_download(self, chars: List[str], evolution_data: Dict[str, Dict] = None) -> Dict:
        """
        批量下载多个汉字的图片

        Args:
            chars: 汉字列表
            evolution_data: 可选，包含古文字URL的字典

        Returns:
            下载结果统计
        """
        results = {
            "total": len(chars),
            "success": 0,
            "failed": 0,
            "downloaded_files": []
        }

        for i, char in enumerate(chars):
            logger.info(f"正在下载图片 ({i + 1}/{len(chars)}): '{char}'")

            try:
                evolution_images = None
                if evolution_data and char in evolution_data:
                    evolution_images = evolution_data[char].get("evolution_images", {})

                files = self.download_for_char(char, evolution_images)

                if files:
                    results["success"] += 1
                    results["downloaded_files"].extend(files.keys())
                    logger.info(f"✓ '{char}' 下载完成: {len(files)} 个文件")
                else:
                    results["failed"] += 1
                    logger.warning(f"✗ '{char}' 无文件下载")

                time.sleep(1)  # 批次间隔

            except Exception as e:
                results["failed"] += 1
                logger.error(f"处理 '{char}' 时出错: {e}")

        return results

    def close(self):
        """关闭会话"""
        self.session.close()


def download_char_images(char: str, evolution_images: Dict = None) -> Dict[str, str]:
    """
    便捷函数：下载单个汉字的图片

    Args:
        char: 单个汉字
        evolution_images: 古文字图片URL字典

    Returns:
        下载结果
    """
    downloader = ImageDownloader()
    try:
        return downloader.download_for_char(char, evolution_images)
    finally:
        downloader.close()
