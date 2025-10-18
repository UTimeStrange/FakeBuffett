#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据处理工具函数
created_by: 奇哥AI财经
"""

from typing import Any, Union
import logging

def safe_float_convert(value: Any, default: float = 0.0) -> float:
    """安全地将值转换为浮点数"""
    if value is None:
        return default
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # 处理空字符串
        if not value.strip():
            return default
        
        # 处理百分号
        if value.endswith('%'):
            try:
                return float(value[:-1]) / 100.0
            except ValueError:
                return default
        
        # 尝试直接转换
        try:
            return float(value)
        except ValueError:
            return default
    
    return default

def safe_int_convert(value: Any, default: int = 0) -> int:
    """安全地将值转换为整数"""
    if value is None:
        return default
    
    if isinstance(value, int):
        return value
    
    if isinstance(value, float):
        return int(value)
    
    if isinstance(value, str):
        if not value.strip():
            return default
        
        try:
            return int(float(value))
        except ValueError:
            return default
    
    return default

def safe_percentage_convert(value: Any, default: float = 0.0) -> float:
    """安全地将值转换为百分比（0-1之间的小数）"""
    converted = safe_float_convert(value, default)
    
    # 如果值大于1，假设它是百分比形式（如15表示15%）
    if converted > 1:
        return converted / 100.0
    
    return converted

def clean_financial_record(record: dict) -> dict:
    """清理财务记录中的数据类型"""
    cleaned = {}
    
    for key, value in record.items():
        if key in ['end_date', 'ann_date', 'f_ann_date', 'trade_date', 'ts_code', 'report_type', 'comp_type']:
            # 保持字符串类型的字段
            cleaned[key] = str(value) if value is not None else 'N/A'
        elif 'ratio' in key.lower() or 'rate' in key.lower() or 'margin' in key.lower() or key in ['roe', 'roa', 'pe', 'pb', 'ps']:
            # 比率、利率、边际等字段转换为百分比
            cleaned[key] = safe_percentage_convert(value)
        elif 'yoy' in key.lower() or 'qoq' in key.lower():
            # 同比、环比增长率
            cleaned[key] = safe_percentage_convert(value)
        else:
            # 其他数值字段
            cleaned[key] = safe_float_convert(value)
    
    return cleaned

def process_financial_data(financial_data: dict) -> dict:
    """处理整个财务数据字典"""
    processed_data = {}
    
    for category, records in financial_data.items():
        if isinstance(records, list):
            processed_data[category] = [clean_financial_record(record) for record in records]
        else:
            processed_data[category] = records
    
    return processed_data