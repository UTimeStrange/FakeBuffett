import json
import yaml
import os
from typing import Dict, Any
import logging

def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"加载配置文件失败: {e}")
        return {}

def save_json(data: Dict[str, Any], filepath: str) -> None:
    """保存JSON文件"""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"保存JSON文件失败: {e}")

def load_json(filepath: str) -> Dict[str, Any]:
    """加载JSON文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"加载JSON文件失败: {e}")
        return {}

def setup_logging(log_level: str = "INFO") -> None:
    """设置日志"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('fake_buffett.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def calculate_final_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """计算最终得分"""
    total_score = 0
    total_weight = 0
    
    for category, score in scores.items():
        if category in weights:
            total_score += score * weights[category]
            total_weight += weights[category]
    
    return round(total_score / total_weight if total_weight > 0 else 0, 2)