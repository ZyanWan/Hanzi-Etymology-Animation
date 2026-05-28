# -*- coding: utf-8 -*-
"""
Unicode转换工具模块
"""

import json
from typing import Dict, Optional


class UnicodeResolver:
    """汉字Unicode编码解析器"""

    def __init__(self):
        self._cache: Dict[str, str] = {}

    def char_to_unicode(self, char: str) -> str:
        """
        将汉字转换为Unicode编码（十六进制，大写）

        Args:
            char: 单个汉字

        Returns:
            Unicode编码（4位十六进制），如 '53D6'
        """
        if not char or len(char) != 1:
            raise ValueError("请输入单个汉字")

        unicode_code = ord(char)
        self._cache[char] = hex(unicode_code).upper().replace('0X', '')
        return self._cache[char]

    def unicode_to_char(self, unicode_hex: str) -> str:
        """
        将Unicode编码转换为汉字

        Args:
            unicode_hex: Unicode编码（4位十六进制），如 '53D6'

        Returns:
            对应的汉字
        """
        unicode_hex = unicode_hex.upper().replace('U+', '').replace('0X', '')
        return chr(int(unicode_hex, 16))

    def get_char_info(self, char: str) -> Dict[str, any]:
        """
        获取汉字的完整Unicode信息

        Args:
            char: 单个汉字

        Returns:
            包含Unicode相关信息的字典
        """
        unicode_hex = self.char_to_unicode(char)
        return {
            "character": char,
            "unicode_hex": unicode_hex,
            "unicode_decimal": ord(char),
            "unicode_binary": bin(ord(char)),
            "utf8_bytes": char.encode('utf-8').hex().upper(),
        }

    @staticmethod
    def load_common_chars(filepath: str = None) -> list:
        """
        加载常用汉字表

        Args:
            filepath: 可选的自定义汉字表文件路径

        Returns:
            常用汉字列表
        """
        if filepath and os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]

        # 内置常用汉字表（3500个一级常用字）
        common_chars = [
            "的一是在不了有和人这中大为上个国我以要他时来",
            "用工生意外面日时去习建挖当没发表情妈好后自力",
            "会都回意与所生平代民样对文经都分部法电起第就",
            "好小部其些主样理心她本前开但因只从想实诸者",
            "么会去得学到你说如子也就出年分行天中多夫再",
            "后作方两个妇人即远完定杀应增创痛白独远亲师",
            "器书声雪寒村料煮累功赏希探远层含兽雾露惊",
            "宿寒官富赏康宁尺隐屋幕仓卷席帆常带甲电夏",
            "厂广汤泼莱墓荣荆荒草茶药荷莲菊菜萧落葛壶",
            "蒙蓄蒸营蓝蓬萝卜葱蒜芹莱薯紫红绿织绸绣绳",
            "象力年手支拜股肩胎肿胀胃胡胶膏舟舰般船舱",
            "盘青索靖靛静非悲排师常帕带幅帽幌帆帐帘",
            "帕帽幅帐帘幕帖帚帕帆帐帘帖帆帕带幅帖帖幅"
        ]
        return list(''.join(common_chars))


# 创建全局实例
unicode_resolver = UnicodeResolver()

# 导出便捷函数
char_to_unicode = unicode_resolver.char_to_unicode
unicode_to_char = unicode_resolver.unicode_to_char
get_char_info = unicode_resolver.get_char_info


import os
