# -*- coding: utf-8 -*-
"""
数据存储模块
将爬取的数据保存为JSON格式，便于后续使用
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging

from .config import DATA_DIR, PROCESSED_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataStorage:
    """数据存储管理器"""

    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or DATA_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
        (self.base_dir / "metadata").mkdir(exist_ok=True, parents=True)

    def save_char_data(self, char: str, data: Dict, filename: str = None) -> Path:
        """
        保存单个汉字的数据为JSON

        Args:
            char: 汉字
            data: 数据字典
            filename: 可选的自定义文件名

        Returns:
            保存的文件路径
        """
        if filename is None:
            filename = f"char_{char}_{data.get('unicode', '')}.json"

        filepath = self.base_dir / "metadata" / filename

        # 添加元数据
        data["_metadata"] = {
            "scraped_at": datetime.now().isoformat(),
            "source": "汉典 zdic.net",
            "character": char
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ 数据已保存: {filepath.name}")
        return filepath

    def save_batch_data(self, chars_data: Dict[str, Dict], filename: str = "batch_data.json") -> Path:
        """
        批量保存汉字数据

        Args:
            chars_data: {汉字: 数据} 的字典
            filename: 保存文件名

        Returns:
            保存的文件路径
        """
        filepath = self.base_dir / "metadata" / filename

        # 添加批次元数据
        batch_data = {
            "_batch_metadata": {
                "scraped_at": datetime.now().isoformat(),
                "total_chars": len(chars_data),
                "characters": list(chars_data.keys()),
                "source": "汉典 zdic.net"
            },
            "data": chars_data
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, ensure_ascii=False, indent=2)

        logger.info(f"✓ 批量数据已保存: {filepath.name} ({len(chars_data)} 个汉字)")
        return filepath

    def load_char_data(self, char: str, unicode_hex: str = None) -> Dict:
        """
        加载单个汉字的数据

        Args:
            char: 汉字
            unicode_hex: Unicode编码（可选）

        Returns:
            数据字典，不存在返回空字典
        """
        if unicode_hex:
            filename = f"char_{char}_{unicode_hex}.json"
        else:
            filename = f"char_{char}_*.json"

        # 查找匹配的文件
        metadata_dir = self.base_dir / "metadata"
        for filepath in metadata_dir.glob(filename):
            if filepath.is_file():
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)

        return {}

    def load_batch_data(self, filename: str = "batch_data.json") -> Dict:
        """
        加载批量数据

        Args:
            filename: 文件名

        Returns:
            数据字典
        """
        filepath = self.base_dir / "metadata" / filename

        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {}

    def generate_image_manifest(self, chars: List[str]) -> List[Dict]:
        """
        生成图片清单，用于后续处理

        Args:
            chars: 汉字列表

        Returns:
            图片清单列表
        """
        manifest = []

        for char in chars:
            char_dir = self.base_dir.parent / "data" / "raw" / char

            if char_dir.exists():
                for img_file in char_dir.glob("*.svg"):
                    manifest.append({
                        "character": char,
                        "filename": img_file.name,
                        "filepath": str(img_file.relative_to(self.base_dir.parent)),
                        "type": self._infer_image_type(img_file.name),
                        "size_bytes": img_file.stat().st_size
                    })

        return manifest

    def _infer_image_type(self, filename: str) -> str:
        """从文件名推断图片类型"""
        name_lower = filename.lower()

        if "kaishu" in name_lower or "kai" in name_lower:
            return "楷书"
        elif "jiaguwen" in name_lower or "jia" in name_lower:
            return "甲骨文"
        elif "jinwen" in name_lower or "jin" in name_lower:
            return "金文"
        elif "xiaozhuan" in name_lower or "zhuan" in name_lower:
            return "小篆"
        elif "lishu" in name_lower or "li" in name_lower:
            return "隶书"
        elif "chuwenzi" in name_lower or "chu" in name_lower:
            return "楚系简帛"
        elif "kxzd" in name_lower:
            return "康熙字典"
        elif "swxz" in name_lower:
            return "说文解字"
        else:
            return "其他"

    def export_to_training_format(self, chars_data: Dict, output_file: str = "training_data.jsonl") -> Path:
        """
        导出为AI训练格式（JSONL）

        Args:
            chars_data: 汉字数据字典
            output_file: 输出文件名

        Returns:
            输出文件路径
        """
        filepath = self.base_dir / "metadata" / output_file

        with open(filepath, 'w', encoding='utf-8') as f:
            for char, data in chars_data.items():
                # 转换为训练友好的格式
                training_item = {
                    "character": char,
                    "unicode": data.get("unicode", ""),
                    "prompt": self._generate_prompt(char, data),
                    "images": self._collect_image_paths(char, data)
                }
                f.write(json.dumps(training_item, ensure_ascii=False) + '\n')

        logger.info(f"✓ 训练数据已导出: {filepath.name}")
        return filepath

    def _generate_prompt(self, char: str, data: Dict) -> str:
        """为AI视频生成提示词"""
        basic_info = data.get("basic_info", {})
        meanings = data.get("meanings", [])

        prompt_parts = [f"汉字'{char}'"]

        if basic_info.get("pinyin"):
            prompt_parts.append(f"读音：{basic_info['pinyin']}")

        if basic_info.get("analysis"):
            prompt_parts.append(f"构字：{basic_info['analysis']}")

        if meanings:
            prompt_parts.append(f"本义：{meanings[0].get('text', '')[:50]}")

        return "，".join(prompt_parts)

    def _collect_image_paths(self, char: str, data: Dict) -> Dict[str, str]:
        """收集该汉字的所有图片路径"""
        evolution = data.get("evolution_images", {})
        paths = {}

        for font_type, images in evolution.items():
            if images:
                paths[font_type] = [img["url"] for img in images]

        return paths

    def get_statistics(self) -> Dict:
        """获取数据统计"""
        metadata_dir = self.base_dir / "metadata"

        stats = {
            "total_files": 0,
            "total_chars": 0,
            "files_by_type": {},
            "total_size_mb": 0
        }

        json_files = list(metadata_dir.glob("char_*.json"))
        batch_files = list(metadata_dir.glob("batch_*.json"))
        jsonl_files = list(metadata_dir.glob("*.jsonl"))

        stats["total_files"] = len(json_files) + len(batch_files) + len(jsonl_files)

        # 计算总大小
        for filepath in metadata_dir.rglob("*"):
            if filepath.is_file():
                stats["total_size_mb"] += filepath.stat().st_size / (1024 * 1024)

        return stats
