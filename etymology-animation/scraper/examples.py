# -*- coding: utf-8 -*-
"""
快速使用示例
展示字源数据采集系统的基本用法
"""

from scraper import EtymologyCollector


def example_single_char():
    """示例1: 采集单个汉字"""
    print("=" * 50)
    print("示例1: 采集单个汉字 '取'")
    print("=" * 50)

    collector = EtymologyCollector()
    try:
        result = collector.collect_single("取", download_images=True)

        print(f"\n采集结果:")
        print(f"  汉字: {result['character']}")
        print(f"  Unicode: {result['unicode']}")
        print(f"  成功: {result['success']}")
        print(f"  下载图片数: {len(result['images'])}")

        if result['data']:
            data = result['data']
            print(f"\n基本信息:")
            print(f"  {data.get('basic_info', {})}")

    finally:
        collector.close()


def example_batch_chars():
    """示例2: 批量采集多个汉字"""
    print("\n" + "=" * 50)
    print("示例2: 批量采集多个汉字")
    print("=" * 50)

    # 要采集的汉字列表
    chars = ["日", "月", "山", "水", "取", "采", "休"]

    collector = EtymologyCollector()
    try:
        stats = collector.collect_batch(chars, download_images=True, save_batch=True)

        print(f"\n采集统计:")
        print(f"  总数: {stats['total']}")
        print(f"  成功: {stats['success']}")
        print(f"  失败: {stats['failed']}")
        print(f"  图片总数: {stats['total_images']}")

    finally:
        collector.close()


def example_sample_priority():
    """示例3: 使用论文中建议的优先级采集"""
    print("\n" + "=" * 50)
    print("示例3: 按优先级采集（P0-P2）")
    print("=" * 50)

    # P0: 独体象形字（优先采集）
    p0_chars = ["日", "月", "山", "水", "火", "木", "土", "人", "口", "目"]

    # P1: 会意字
    p1_chars = ["取", "采", "休", "明", "林", "森"]

    # P2: 指事字
    p2_chars = ["上", "下", "本", "末"]

    all_chars = p0_chars + p1_chars + p2_chars

    print(f"计划采集 {len(all_chars)} 个汉字")
    print(f"  P0象形字: {len(p0_chars)} 个")
    print(f"  P1会意字: {len(p1_chars)} 个")
    print(f"  P2指事字: {len(p2_chars)} 个")

    collector = EtymologyCollector()
    try:
        stats = collector.collect_batch(all_chars, download_images=True, save_batch=True)
        print(f"\n完成! 成功 {stats['success']}/{stats['total']}")

    finally:
        collector.close()


if __name__ == "__main__":
    # 运行所有示例
    # example_single_char()  # 先试试单个
    example_batch_chars()
    # example_sample_priority()
