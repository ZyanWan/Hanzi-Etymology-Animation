# -*- coding: utf-8 -*-
"""
字形演变分段分析器
分析字义数据，决定分段策略
"""

from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path


class SegmentAnalyzer:
    """字形演变分段分析器"""
    
    # 标准演变阶段（从古到今）
    STANDARD_STAGES = ["jiaguwen", "jinwen", "xiaozhuan", "lishu", "kaishu_cn"]
    
    # 最小分段（适合简单字形）
    MINIMAL_STAGES = ["jiaguwen", "xiaozhuan", "kaishu_cn"]
    
    # 会意字专用（两个部件组合）
    COMPOUND_STAGES = ["jiaguwen", "jinwen", "xiaozhuan", "lishu", "kaishu_cn"]
    
    def __init__(self):
        pass
    
    def analyze_and_decide_segments(
        self,
        char_data: Dict,
        priority: str = "P0"
    ) -> Dict:
        """
        分析字形数据，决定分段策略
        
        Args:
            char_data: 包含字形和字义的数据
            priority: 字优先级（P0-P3）
        
        Returns:
            分析结果和建议
        """
        result = {
            "character": char_data.get("character", ""),
            "priority": priority,
            "structure": self._analyze_structure(char_data),
            "recommended_segments": self._decide_segments(char_data, priority),
            "total_duration": 0,
            "segments_detail": []
        }
        
        # 计算总时长
        result["total_duration"] = len(result["recommended_segments"]) * 2
        
        return result
    
    def _analyze_structure(self, char_data: Dict) -> Dict:
        """分析字形结构"""
        basic_info = char_data.get("basic_info", {})
        structure_analysis = char_data.get("structure_analysis", "")
        
        return {
            "type": basic_info.get("analysis", structure_analysis or ""),
            "pinyin": basic_info.get("pinyin", ""),
            "radical": basic_info.get("radical", ""),
            "strokes": basic_info.get("total_strokes", 0)
        }
    
    def _decide_segments(
        self,
        char_data: Dict,
        priority: str
    ) -> List[Dict]:
        """
        根据字形类型和字义决定分段
        
        分段策略：
        - 第1段：场景演绎（从本义生成场景动画）
        - 第2段起：字形演变（按阶段过渡）
        
        Returns:
            分段列表，每个包含from、to、reason、segment_type
        """
        segments = []
        structure = char_data.get("basic_info", {}).get("analysis", "")
        
        # 判断字形类型
        is_pictographic = "象形" in structure
        is_compound = "会意" in structure
        is_indicative = "指事" in structure
        
        # 第1段：场景演绎（必须）
        segments.append({
            "order": 1,
            "segment_type": "scene",
            "stage_from": "本义",
            "stage_to": "甲骨文",
            "description": "演绎本义场景",
            "reason": "让学生理解字的本义，引申义由本义展开"
        })
        
        # 第2段起：字形演变
        base_order = 2
        
        # 根据类型决定演变阶段
        if is_pictographic:
            stages = self.MINIMAL_STAGES
            reason = "象形字字形直观，3阶段足以展示核心变化"
        elif is_compound:
            stages = self.COMPOUND_STAGES
            reason = "会意字由部件组合，5阶段展示完整的演变故事"
        elif is_indicative:
            stages = ["jiaguwen", "xiaozhuan", "lishu", "kaishu_cn"]
            reason = "指事字有抽象标记，4阶段平衡叙事与变化"
        else:
            stages = self.STANDARD_STAGES
            reason = "默认采用标准5阶段演变"
        
        # 构建字形演变分段
        for i in range(len(stages) - 1):
            segments.append({
                "order": base_order + i,
                "segment_type": "evolution",
                "stage_from": stages[i],
                "stage_to": stages[i + 1],
                "description": "",
                "reason": reason
            })
        
        return segments
    
    def generate_segment_report(
        self,
        char_data: Dict,
        priority: str = "P0"
    ) -> str:
        """
        生成完整的分段报告（供AI和人类阅读）
        
        Returns:
            分段报告文本
        """
        analysis = self.analyze_and_decide_segments(char_data, priority)
        
        report = f"""# 字形演变分析报告：{analysis['character']}

## 基本信息
- **优先级**: {analysis['priority']}
- **拼音**: {analysis['structure']['pinyin']}
- **部首**: {analysis['structure']['radical']}
- **笔画**: {analysis['structure']['strokes']}
- **结构**: {analysis['structure']['type']}

## 分段策略
共 {len(analysis['recommended_segments'])} 段，预计总时长 {analysis['total_duration']} 秒

### 详细分段
"""
        
        for seg in analysis['recommended_segments']:
            seg_type = seg.get('segment_type', 'evolution')
            if seg_type == 'scene':
                report += f"""
#### 第{seg['order']}段：场景演绎
- 类型：场景演绎
- 内容：演绎本义场景
- 理由：{seg['reason']}
"""
            else:
                from_name = self._get_stage_name(seg['stage_from'])
                to_name = self._get_stage_name(seg['stage_to'])
                report += f"""
#### 第{seg['order']}段：{from_name} → {to_name}
- 起点：{from_name}
- 终点：{to_name}
- 理由：{seg['reason']}
"""
        
        return report
    
    def _get_stage_name(self, stage_code: str) -> str:
        """获取阶段中文名称"""
        names = {
            "jiaguwen": "甲骨文",
            "jinwen": "金文",
            "xiaozhuan": "小篆",
            "lishu": "隶书",
            "kaishu_cn": "楷书"
        }
        return names.get(stage_code, stage_code)


def analyze_character(char_data: Dict, priority: str = "P0") -> Dict:
    """
    便捷函数：分析单个汉字
    
    Args:
        char_data: 字形和字义数据
        priority: 优先级
    
    Returns:
        分析结果
    """
    analyzer = SegmentAnalyzer()
    return analyzer.analyze_and_decide_segments(char_data, priority)
