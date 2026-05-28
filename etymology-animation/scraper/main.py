# -*- coding: utf-8 -*-
"""
字源数据采集系统 - 主程序
一键采集汉字字源数据和图片，生成Prompt
"""

import sys
import json
import logging
from pathlib import Path
from typing import List, Dict
import argparse

from .config import DATA_DIR, LOG_FILE, PROCESSED_DIR
from .unicode_utils import UnicodeResolver
from .zdic_scraper import ZdicScraper
from .image_downloader import ImageDownloader
from .data_storage import DataStorage
from processors import PromptGenerator, SegmentAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class EtymologyCollector:
    """字源数据采集器"""

    def __init__(self):
        self.scraper = ZdicScraper()
        self.downloader = ImageDownloader()
        self.storage = DataStorage()
        self.unicode_resolver = UnicodeResolver()

    def collect_single(self, char: str, download_images: bool = True, mode: str = "essential") -> Dict:
        """
        采集单个汉字的完整数据

        Args:
            char: 单个汉字
            download_images: 是否下载图片
            mode: 采集模式
                - "full": 完整采集
                - "essential": 关键阶段采集（推荐）
                - "minimal": 最小采集

        Returns:
            采集结果
        """
        logger.info(f"=" * 50)
        logger.info(f"开始采集: '{char}' (模式: {mode})")
        logger.info(f"=" * 50)

        result = {
            "character": char,
            "unicode": self.unicode_resolver.char_to_unicode(char),
            "success": False,
            "data": None,
            "images": {},
            "collection_mode": mode
        }

        # 1. 爬取数据
        try:
            logger.info("步骤 1/2: 爬取字源数据...")
            char_data = self.scraper.scrape_char_info(char, mode)

            if char_data:
                result["data"] = char_data
                logger.info(f"✓ 数据爬取成功")
            else:
                logger.error(f"✗ 数据爬取失败")
                return result

        except Exception as e:
            logger.error(f"✗ 爬取数据时出错: {e}")
            return result

        # 2. 下载图片
        if download_images:
            try:
                logger.info("步骤 2/2: 下载字源图片...")
                evolution_images = char_data.get("evolution_images", {})
                downloaded = self.downloader.download_for_char(char, evolution_images, mode=mode)

                result["images"] = downloaded
                logger.info(f"✓ 下载了 {len(downloaded)} 个图片文件")

            except Exception as e:
                logger.error(f"✗ 下载图片时出错: {e}")

        # 3. 保存数据
        try:
            logger.info("保存数据...")
            self.storage.save_char_data(char, char_data)
        except Exception as e:
            logger.error(f"✗ 保存数据时出错: {e}")

        result["success"] = True
        logger.info(f"完成!")
        return result

    def collect_batch(self, chars: List[str], download_images: bool = True,
                     save_batch: bool = True, mode: str = "essential") -> Dict:
        """
        批量采集多个汉字

        Args:
            chars: 汉字列表
            download_images: 是否下载图片
            save_batch: 是否保存批量数据文件
            mode: 采集模式
                - "full": 完整采集
                - "essential": 关键阶段采集（推荐）
                - "minimal": 最小采集

        Returns:
            采集统计
        """
        logger.info(f"=" * 50)
        logger.info(f"开始批量采集: {len(chars)} 个汉字 (模式: {mode})")
        logger.info(f"=" * 50)

        results = {}
        stats = {
            "total": len(chars),
            "success": 0,
            "failed": 0,
            "total_images": 0,
            "collection_mode": mode
        }

        for i, char in enumerate(chars):
            logger.info(f"\n[{i + 1}/{len(chars)}] 正在处理: '{char}'")

            result = self.collect_single(char, download_images, mode)
            results[char] = result

            if result["success"]:
                stats["success"] += 1
                stats["total_images"] += len(result["images"])
            else:
                stats["failed"] += 1

        # 保存批量数据
        if save_batch and results:
            logger.info("\n保存批量数据...")
            self.storage.save_batch_data(results)

            # 导出为训练格式
            self.storage.export_to_training_format(results)

        # 打印统计
        logger.info(f"\n" + "=" * 50)
        logger.info(f"采集完成!")
        logger.info(f"成功: {stats['success']}/{stats['total']}")
        logger.info(f"失败: {stats['failed']}/{stats['total']}")
        logger.info(f"下载图片总数: {stats['total_images']}")
        logger.info(f"=" * 50)

        return stats

    def close(self):
        """关闭所有资源"""
        self.scraper.close()
        self.downloader.close()


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description="汉典字源数据采集工具")
    parser.add_argument("chars", nargs="*", help="要采集的汉字列表")
    parser.add_argument("-f", "--file", type=str, help="包含汉字列表的文件路径")
    parser.add_argument("-s", "--sample", action="store_true", help="使用样例汉字（P0-P2优先级）")
    parser.add_argument("--no-images", action="store_true", help="只爬取数据，不下载图片")
    parser.add_argument("--batch", action="store_true", help="保存为批量数据文件")
    parser.add_argument("--mode", type=str, default="essential",
                        choices=["full", "essential", "minimal"],
                        help="采集模式: full(完整采集), essential(关键阶段-推荐), minimal(最小采集)")
    parser.add_argument("--prompt", action="store_true", help="生成Prompt（需要先采集数据）")
    parser.add_argument("--analyze", action="store_true", help="分析分段策略（需要先采集数据）")
    parser.add_argument("--lang", type=str, default="zh", choices=["zh", "en"],
                        help="Prompt语言: zh(中文), en(英文)")

    args = parser.parse_args()

    # 确定要采集的汉字
    chars = []

    if args.file:
        # 从文件读取
        filepath = Path(args.file)
        if filepath.exists():
            chars = [line.strip() for line in filepath.read_text(encoding='utf-8').splitlines() if line.strip()]
            logger.info(f"从文件读取到 {len(chars)} 个汉字")

    if args.sample:
        # 样例汉字（论文中提到的P0-P2）
        sample_chars = [
            # P0: 独体象形字
            "日", "月", "山", "水", "火", "木", "土", "人", "口", "目",
            # P1: 会意字
            "取", "采", "休", "明", "林", "森", "从", "众", "武", "信",
            # P2: 指事字
            "上", "下", "本", "末", "中", "旦", "刃", "寸", "曰", "甘"
        ]
        chars.extend(sample_chars)

    if args.chars:
        chars.extend(args.chars)

    # 去重
    chars = list(dict.fromkeys(chars))

    if not chars:
        logger.error("请提供要采集的汉字！")
        logger.info("使用方法:")
        logger.info("  python -m scraper.main 取")
        logger.info("  python -m scraper.main 日 月 山 水")
        logger.info("  python -m scraper.main -s  # 使用样例")
        logger.info("  python -m scraper.main -f chars.txt  # 从文件读取")
        logger.info("")
        logger.info("采集模式选项:")
        logger.info("  --mode essential  # 关键阶段采集（默认，推荐）")
        logger.info("  --mode full       # 完整采集（所有变体）")
        logger.info("  --mode minimal    # 最小采集（仅3个阶段）")
        return

    # 显示采集模式信息
    from .config import COLLECTION_MODES
    mode_info = COLLECTION_MODES.get(args.mode, COLLECTION_MODES["essential"])
    logger.info(f"采集模式: {mode_info['name']}")
    logger.info(f"模式说明: {mode_info['description']}")

    # 执行采集
    collector = EtymologyCollector()
    try:
        if len(chars) == 1:
            result = collector.collect_single(chars[0], download_images=not args.no_images, mode=args.mode)
            
            # 分析分段
            if args.analyze and result["success"]:
                analyzer = SegmentAnalyzer()
                char_data = result["data"]
                priority = "P1" if "会意" in str(char_data.get("structure_analysis", "")) else "P0"
                analysis = analyzer.analyze_and_decide_segments(char_data, priority)
                report = analyzer.generate_segment_report(char_data, priority)
                print("\n" + "=" * 50)
                print(report)
                print("=" * 50)
            
            # 生成Prompt
            if args.prompt and result["success"]:
                generator = PromptGenerator()
                char_data = result["data"]
                analysis = analyzer.analyze_and_decide_segments(char_data, "P0") if args.analyze else None
                
                # 获取分段
                if analysis:
                    stages = [seg["from"] for seg in analysis["recommended_segments"]] + [analysis["recommended_segments"][-1]["to"]]
                else:
                    stages = ["jiaguwen", "jinwen", "xiaozhuan", "lishu", "kaishu_cn"]
                
                prompts = generator.generate_full_evolution_prompts(chars[0], stages)
                
                print("\n" + "=" * 50)
                print(f"生成的Prompt ({args.lang.upper()}):")
                print("=" * 50)
                for p in prompts:
                    lang_key = f"prompt_{args.lang}"
                    print(f"\n第{p['order']}段: {p['stage_from']} → {p['stage_to']}")
                    print(p[lang_key])
                print("=" * 50)
                
                # 保存Prompt
                prompt_file = DATA_DIR / "prompts" / f"{chars[0]}_prompts.json"
                prompt_file.parent.mkdir(exist_ok=True)
                generator.save_prompts(prompts, prompt_file)
                logger.info(f"Prompt已保存至: {prompt_file}")
        
        else:
            results = collector.collect_batch(chars, download_images=not args.no_images, save_batch=args.batch, mode=args.mode)
            
            # 批量生成Prompt
            if args.prompt:
                generator = PromptGenerator()
                analyzer = SegmentAnalyzer()
                
                print("\n" + "=" * 50)
                print("批量Prompt生成:")
                print("=" * 50)
                
                for char in chars:
                    char_data_path = DATA_DIR / "metadata" / f"char_{char}_{hex(ord(char)).upper()[2:]}.json"
                    if char_data_path.exists():
                        with open(char_data_path, 'r', encoding='utf-8') as f:
                            char_data = json.load(f)
                        
                        analysis = analyzer.analyze_and_decide_segments(char_data, "P0")
                        stages = [seg["from"] for seg in analysis["recommended_segments"]] + [analysis["recommended_segments"][-1]["to"]]
                        prompts = generator.generate_full_evolution_prompts(char, stages)
                        
                        print(f"\n{char}: {len(prompts)}段")
                        
                        # 保存
                        prompt_file = DATA_DIR / "prompts" / f"{char}_prompts.json"
                        prompt_file.parent.mkdir(exist_ok=True)
                        generator.save_prompts(prompts, prompt_file)
                
                logger.info(f"所有Prompt已保存至: {DATA_DIR / 'prompts'}")
                print("=" * 50)
    
    finally:
        collector.close()


if __name__ == "__main__":
    main()
