#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主程序辅助函数
"""

from typing import Dict, Any
import logging

def get_company_data_helper(data_provider, ts_code: str) -> Dict[str, Any]:
    """获取公司完整数据的辅助函数"""
    company_data = {
        'basic_info': {},
        'financial_data': {},
        'market_data': {}
    }
    
    try:
        # 获取基本信息
        company_data['basic_info'] = data_provider.get_stock_basic_info(ts_code)
        
        # 获取财务数据（好生意和好公司智能体需要）
        company_data['financial_data'] = data_provider.get_financial_data(ts_code)
        
        # 获取市场数据（好价格智能体需要）
        company_data['market_data'] = data_provider.get_market_data(ts_code)
        
    except Exception as e:
        logging.error(f"获取公司数据失败: {ts_code}, 错误: {e}")
    
    return company_data

def create_failed_analysis_helper(ts_code: str, error_msg: str) -> Dict[str, Any]:
    """创建失败的分析结果"""
    return {
        "agent_type": "final_decision",
        "company_code": ts_code,
        "company_name": "未知",
        "analysis_summary": f"分析失败: {error_msg}",
        "detailed_analysis": {
            "score_synthesis": {
                "business_score": 0,
                "company_score": 0,
                "price_score": 0,
                "weighted_score": 0,
                "score_analysis": "分析失败，无法计算得分"
            },
            "strength_analysis": {
                "key_strengths": ["分析失败"],
                "competitive_advantages": "无法分析"
            },
            "risk_analysis": {
                "major_risks": ["分析失败风险"],
                "risk_mitigation": "建议重新分析"
            },
            "investment_logic": {
                "investment_thesis": "分析失败，无法形成投资逻辑",
                "catalyst_factors": ["无法识别"],
                "time_horizon": "N/A"
            }
        },
        "investment_recommendation": {
            "recommendation": "不推荐",
            "confidence_level": "低",
            "position_sizing": "0%",
            "entry_strategy": "分析失败，建议重新分析",
            "exit_strategy": "N/A"
        },
        "monitoring_points": ["重新进行分析"],
        "final_score": 0.0,
        "decision_rationale": f"由于{error_msg}，无法做出投资决策",
        "error": error_msg
    }