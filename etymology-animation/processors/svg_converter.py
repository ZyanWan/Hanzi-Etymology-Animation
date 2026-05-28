# -*- coding: utf-8 -*-
"""
SVG转PNG转换器
将SVG字形图片转换为PNG格式，供AI视频工具使用
"""

import os
import cairosvg
from pathlib import Path
from typing import Optional, List, Dict
import json


class SVGConverter:
    """SVG转PNG转换器"""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        初始化转换器

        Args:
            output_dir: 输出目录，默认使用 data/png/
        """
        if output_dir is None:
            self.output_dir = Path(__file__).parent.parent / "data" / "png"
        else:
            self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def convert_single(
        self,
        svg_path: Path,
        output_size: int = 1024,
        background_color: str = "white",
        output_name: Optional[str] = None
    ) -> Path:
        """
        转换单个SVG文件

        Args:
            svg_path: SVG文件路径
            output_size: 输出尺寸（正方形，边长）
            background_color: 背景颜色
            output_name: 输出文件名（不含扩展名）

        Returns:
            输出的PNG文件路径
        """
        svg_path = Path(svg_path)

        if not svg_path.exists():
            raise FileNotFoundError(f"SVG文件不存在: {svg_path}")

        if output_name is None:
            output_name = svg_path.stem

        output_path = self.output_dir / f"{output_name}.png"

        cairosvg.svg2png(
            url=str(svg_path.resolve()),
            write_to=str(output_path),
            output_width=output_size,
            output_height=output_size
        )

        return output_path

    def convert_character(
        self,
        char_dir: Path,
        output_size: int = 1024,
        keep_structure: bool = True
    ) -> Dict[str, Path]:
        """
        转换单个汉字的所有SVG文件

        Args:
            char_dir: 汉字目录（如 data/raw/取/）
            output_size: 输出尺寸
            keep_structure: 是否保持目录结构

        Returns:
            {阶段名: PNG路径}
        """
        char_dir = Path(char_dir)
        char_name = char_dir.name

        if keep_structure:
            char_output_dir = self.output_dir / char_name
            char_output_dir.mkdir(parents=True, exist_ok=True)
        else:
            char_output_dir = self.output_dir

        results = {}

        for svg_file in char_dir.glob("*.svg"):
            stage_name = self._extract_stage_name(svg_file.name)

            output_path = char_output_dir / f"{stage_name}.png"

            cairosvg.svg2png(
                url=str(svg_file.resolve()),
                write_to=str(output_path),
                output_width=output_size,
                output_height=output_size
            )

            results[stage_name] = output_path

        return results

    def convert_batch(
        self,
        raw_dir: Path,
        chars: Optional[List[str]] = None,
        output_size: int = 1024
    ) -> Dict[str, Dict[str, Path]]:
        """
        批量转换多个汉字的SVG文件

        Args:
            raw_dir: 原始数据目录（如 data/raw/）
            chars: 要转换的汉字列表（None表示全部）
            output_size: 输出尺寸

        Returns:
            {汉字: {阶段名: PNG路径}}
        """
        raw_dir = Path(raw_dir)
        results = {}

        target_chars = chars if chars else [d.name for d in raw_dir.iterdir() if d.is_dir()]

        for char in target_chars:
            char_dir = raw_dir / char
            if char_dir.exists():
                results[char] = self.convert_character(char_dir, output_size)

        return results

    def _extract_stage_name(self, filename: str) -> str:
        """从文件名提取阶段名"""
        stage_map = {
            "jiaguwen": "jiaguwen",
            "jinwen": "jinwen",
            "xiaozhuan": "xiaozhuan",
            "lishu": "lishu",
            "kaishu_cn": "kaishu_cn",
        }

        for key in stage_map:
            if key in filename:
                return key

        return "unknown"

    def get_output_info(self) -> Dict:
        """获取转换输出信息"""
        if not self.output_dir.exists():
            return {"exists": False, "dir": str(self.output_dir)}

        png_files = list(self.output_dir.rglob("*.png"))

        return {
            "exists": True,
            "dir": str(self.output_dir),
            "total_files": len(png_files),
            "chars": list(set(f.parent.name for f in png_files))
        }


def convert_character(char: str, size: int = 1024) -> Dict[str, Path]:
    """
    便捷函数：转换单个汉字

    Args:
        char: 汉字
        size: 输出尺寸

    Returns:
        {阶段名: PNG路径}
    """
    converter = SVGConverter()
    char_dir = converter.output_dir.parent / "raw" / char

    if not char_dir.exists():
        char_dir = converter.output_dir.parent.parent / "raw" / char

    return converter.convert_character(char_dir, size)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="SVG转PNG转换器")
    parser.add_argument("char", nargs="?", help="要转换的汉字")
    parser.add_argument("-a", "--all", action="store_true", help="转换所有汉字")
    parser.add_argument("-s", "--size", type=int, default=1024, help="输出尺寸（默认1024）")

    args = parser.parse_args()

    converter = SVGConverter()

    if args.all:
        raw_dir = Path(__file__).parent.parent / "data" / "raw"
        results = converter.convert_batch(raw_dir, output_size=args.size)

        print(f"\n转换完成！共转换 {len(results)} 个汉字")
        for char, stages in results.items():
            print(f"  {char}: {len(stages)} 个文件")

    elif args.char:
        char_dir = converter.output_dir.parent / "raw" / args.char
        if not char_dir.exists():
            char_dir = converter.output_dir.parent.parent / "raw" / args.char

        if not char_dir.exists():
            print(f"错误：找不到汉字 '{args.char}' 的数据")
            return

        results = converter.convert_character(char_dir, output_size=args.size)

        print(f"\n转换完成！{args.char}:")
        for stage, path in results.items():
            print(f"  {stage}: {path}")

    else:
        print("请指定要转换的汉字，或使用 -a 转换全部")
        print("示例：")
        print("  python -m processors.svg_converter 取")
        print("  python -m processors.svg_converter -a")


if __name__ == "__main__":
    main()
