# -*- coding: utf-8 -*-
"""
字源数据采集系统
用于从汉典网站采集汉字字源数据和图片

使用方法:
    from scraper import EtymologyCollector

    collector = EtymologyCollector()
    result = collector.collect_single("取")
    collector.close()
"""

from .unicode_utils import UnicodeResolver, char_to_unicode, unicode_to_char
from .zdic_scraper import ZdicScraper, scrape_char
from .image_downloader import ImageDownloader, download_char_images
from .data_storage import DataStorage
from .main import EtymologyCollector

__version__ = "1.0.0"
__all__ = [
    "EtymologyCollector",
    "UnicodeResolver",
    "ZdicScraper",
    "ImageDownloader",
    "DataStorage",
    "char_to_unicode",
    "unicode_to_char",
    "scrape_char",
    "download_char_images",
]
