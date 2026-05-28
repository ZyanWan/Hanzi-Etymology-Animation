# -*- coding: utf-8 -*-
"""
字形演变Prompt生成器

重要说明：
    这个模板是给"中间人"（AI Agent）参考的，
    不是完全依赖脚本生成的。
    
    中间人应该：
    1. 读取字义数据（metadata中的meanings字段）
    2. 根据本义场景适当调整Prompt
    3. 融合字义场景和字形变化
    4. 生成适合特定汉字的Prompt
"""

from typing import Dict, List, Optional
import json
from pathlib import Path


class PromptGenerator:
    """字形演变Prompt生成器"""
    
    # 场景演绎Prompt模板（参考用，中间人需根据字义调整）
    TEMPLATE_SCENE = """[本义场景描述]，
[汉字]字从[本义场景]逐渐过渡为甲骨文字形，
保持字形完整不变形，
书法风格，画面稳定，[DURATION]秒"""
    
    # 字形演变Prompt模板
    TEMPLATE_EVOLUTION = """白底黑字的[START_STYLE][CHAR]字，
[FIRST_FEATURES]，
笔画平滑过渡变化为[END_STYLE][CHAR]字，
[END_FEATURES]，
保持字形完整不变形，无笔画扭曲或断裂，
书法风格，画面稳定，[DURATION]秒"""
    
    # 英文模板（Sora/Runway用）
    TEMPLATE_EN = """White background, black Chinese character "[CHAR]".
[START_STYLE_EN] inscription showing [FIRST_FEATURES_EN].
Smooth stroke transition transforming to [END_STYLE_EN] style.
[END_FEATURES_EN].
Maintain complete character shape without distortion or stroke breaking.
Calligraphy aesthetic, stable camera, [DURATION] seconds."""
    
    # 阶段名称映射
    STAGE_NAMES = {
        "jiaguwen": {
            "name": "商朝甲骨文",
            "name_en": "Shang dynasty Oracle Bone Script",
            "features": "象形性强，笔画稚拙，线条不均匀",
            "features_en": "highly pictographic, primitive strokes, uneven lines"
        },
        "jinwen": {
            "name": "西周金文",
            "name_en": "Western Zhou Bronze Script",
            "features": "笔画开始规整，线条圆润厚重",
            "features_en": "strokes beginning to regularize, rounded and thick lines"
        },
        "xiaozhuan": {
            "name": "秦朝小篆",
            "name_en": "Qin dynasty Small Seal Script",
            "features": "线条完全统一，圆润流畅，结构修长",
            "features_en": "unified stroke width, smooth curves, elongated structure"
        },
        "lishu": {
            "name": "汉朝隶书",
            "name_en": "Han dynasty Clerical Script",
            "features": "波磔特征明显，方折代替圆转",
            "features_en": "distinctive stroke waves, angular turns replacing curves"
        },
        "kaishu_cn": {
            "name": "现代楷书",
            "name_en": "modern Regular Script",
            "features": "横平竖直，方块字形，标准规范",
            "features_en": "horizontal and vertical strokes, square character form, standardized"
        }
    }
    
    def __init__(self):
        pass
    
    def generate_scene_prompt(
        self,
        char: str,
        meaning_text: str,
        duration: int = 3
    ) -> str:
        """
        生成场景演绎Prompt
        
        注意：这是参考模板，中间人应根据字义数据适当调整。
        
        Args:
            char: 目标汉字
            meaning_text: 字义文本（本义描述）
            duration: 时长（秒）
        
        Returns:
            场景演绎Prompt
        """
        # 从字义文本中提取场景描述
        # 格式如："(会意。从又，从耳。甲骨文字形...本义:[捕获到野兽或战俘时]割下左耳)"
        
        scene_desc = self._extract_scene_description(meaning_text, char)
        
        prompt = self.TEMPLATE_SCENE
        prompt = prompt.replace("[本义场景描述]", scene_desc)
        prompt = prompt.replace("[汉字]", char)
        prompt = prompt.replace("[本义场景]", scene_desc.split("。")[0] if "。" in scene_desc else scene_desc)
        prompt = prompt.replace("[DURATION]", str(duration))
        
        return prompt
    
    def _extract_scene_description(self, meaning_text: str, char: str) -> str:
        """
        从字义文本中提取场景描述
        
        Args:
            meaning_text: 字义文本
            char: 汉字
        
        Returns:
            简化的场景描述
        """
        if not meaning_text:
            return f"{char}字的原始含义"
        
        # 尝试提取本义部分
        if "本义" in meaning_text:
            benyi_match = meaning_text.split("本义")[-1]
            # 清理括号内容
            benyi_match = benyi_match.strip("：[:(").split("）")[0].split(")")[0]
            if len(benyi_match) > 50:
                benyi_match = benyi_match[:50] + "..."
            return benyi_match
        
        # 如果没有明确的本义标签，截取前100字
        if len(meaning_text) > 100:
            return meaning_text[:100] + "..."
        
        return meaning_text
    
    def generate_prompt(
        self,
        char: str,
        start_stage: str,
        end_stage: str,
        duration: int = 2,
        language: str = "zh"
    ) -> str:
        """
        生成单段Prompt
        
        Args:
            char: 目标汉字
            start_stage: 起始阶段（如 "jiaguwen"）
            end_stage: 目标阶段（如 "jinwen"）
            duration: 时长（秒）
            language: 语言（"zh" 或 "en"）
        
        Returns:
            生成的Prompt
        """
        if language == "zh":
            return self._generate_zh(char, start_stage, end_stage, duration)
        else:
            return self._generate_en(char, start_stage, end_stage, duration)
    
    def _generate_zh(
        self,
        char: str,
        start_stage: str,
        end_stage: str,
        duration: int
    ) -> str:
        """生成中文Prompt"""
        start_info = self.STAGE_NAMES.get(start_stage, {"name": start_stage, "features": ""})
        end_info = self.STAGE_NAMES.get(end_stage, {"name": end_stage, "features": ""})
        
        prompt = self.TEMPLATE_EVOLUTION
        prompt = prompt.replace("[CHAR]", char)
        prompt = prompt.replace("[START_STYLE]", start_info["name"])
        prompt = prompt.replace("[END_STYLE]", end_info["name"])
        prompt = prompt.replace("[FIRST_FEATURES]", start_info["features"])
        prompt = prompt.replace("[END_FEATURES]", end_info["features"])
        prompt = prompt.replace("[DURATION]", str(duration))
        
        return prompt
    
    def _generate_en(
        self,
        char: str,
        start_stage: str,
        end_stage: str,
        duration: int
    ) -> str:
        """生成英文Prompt"""
        start_info = self.STAGE_NAMES.get(start_stage, {"name_en": start_stage, "features_en": ""})
        end_info = self.STAGE_NAMES.get(end_stage, {"name_en": end_stage, "features_en": ""})
        
        prompt = self.TEMPLATE_EN
        prompt = prompt.replace("[CHAR]", char)
        prompt = prompt.replace("[START_STYLE_EN]", start_info["name_en"])
        prompt = prompt.replace("[END_STYLE_EN]", end_info["name_en"])
        prompt = prompt.replace("[FIRST_FEATURES_EN]", start_info["features_en"])
        prompt = prompt.replace("[END_FEATURES_EN]", end_info["features_en"])
        prompt = prompt.replace("[DURATION]", str(duration))
        
        return prompt
    
    def generate_full_evolution_prompts(
        self,
        char: str,
        stages: List[str],
        duration: int = 2
    ) -> List[Dict[str, str]]:
        """
        生成完整演变过程的多个Prompt
        
        Args:
            char: 目标汉字
            stages: 演变阶段列表（如 ["jiaguwen", "jinwen", "xiaozhuan", "kaishu_cn"]）
            duration: 每段时长（秒）
        
        Returns:
            [{stage_from, stage_to, prompt_zh, prompt_en, duration}]
        """
        prompts = []
        
        for i in range(len(stages) - 1):
            start = stages[i]
            end = stages[i + 1]
            
            prompts.append({
                "stage_from": start,
                "stage_to": end,
                "prompt_zh": self._generate_zh(char, start, end, duration),
                "prompt_en": self._generate_en(char, start, end, duration),
                "duration": duration,
                "order": i + 1
            })
        
        return prompts
    
    @staticmethod
    def save_prompts(prompts: List[Dict], output_path: Path):
        """保存Prompt到JSON文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)


def generate_prompts_for_char(
    char: str,
    stages: Optional[List[str]] = None
) -> List[Dict[str, str]]:
    """
    便捷函数：为汉字生成Prompt
    
    Args:
        char: 目标汉字
        stages: 演变阶段列表（默认使用标准5阶段）
    
    Returns:
        Prompt列表
    """
    generator = PromptGenerator()
    
    if stages is None:
        stages = ["jiaguwen", "jinwen", "xiaozhuan", "lishu", "kaishu_cn"]
    
    return generator.generate_full_evolution_prompts(char, stages)
