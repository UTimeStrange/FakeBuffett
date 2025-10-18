#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
created_by: 奇哥AI财经
"""
from .base_agent import BaseAgent
from typing import Dict, Any
from datetime import datetime
import json
import logging

class GoodCompanyAgent(BaseAgent):
    """好公司智能体 - 分析公司的管理质量和治理结构"""
    
    def get_system_prompt(self) -> str:
        return """
你是一位专业的价值投资分析师，专门负责评估公司的"好公司"特质。你需要严格按照巴菲特价值投资理念中对"好公司"的定义来分析公司管理层和治理结构。

## 巴菲特定义的"好公司"核心特征：

### 1. 管理层质量 - 权重40%
**诚信度与透明度：**
- 财务报告的真实性和透明度
- 管理层沟通的坦诚程度
- 历史上是否有财务造假或违规行为
- 信息披露的及时性和完整性

**资本配置能力：**
- 投资决策的历史表现
- 并购整合的成功率
- 股东回报政策的合理性
- 现金管理和分红政策

**战略执行力：**
- 长期战略规划的清晰度
- 战略执行的一致性
- 业绩承诺的兑现情况
- 危机应对能力

### 2. 财务健康度 - 权重30%
**资产质量：**
- 资产结构的合理性
- 应收账款和存货的质量
- 商誉和无形资产的合理性
- 资产减值风险

**负债结构：**
- 债务水平的合理性
- 债务结构和期限匹配
- 偿债能力的稳定性
- 财务杠杆的适度性

**盈利质量：**
- 利润的真实性和可持续性
- 非经常性损益的影响
- 会计政策的稳健性
- 现金流与利润的匹配度

### 3. 治理结构 - 权重20%
**股权结构：**
- 股权集中度的合理性
- 大股东与中小股东利益一致性
- 股权激励机制的有效性
- 关联交易的公允性

**董事会治理：**
- 董事会的独立性
- 董事会决策的有效性
- 独立董事的作用发挥
- 监事会的监督职能

**内控体系：**
- 内部控制制度的完善性
- 风险管理体系的有效性
- 审计监督的独立性
- 合规管理的规范性

### 4. 可持续发展能力 - 权重10%
**创新能力：**
- 研发投入的持续性
- 技术创新的成果转化
- 人才队伍的稳定性
- 知识产权的保护

**ESG表现：**
- 环境保护责任履行
- 社会责任承担情况
- 公司治理的规范性
- 可持续发展战略

## 分析要求：

1. **数据驱动分析**：基于财务数据和公开信息进行客观分析
2. **历史表现评估**：重点关注管理层的历史业绩和决策质量
3. **同业对比**：在行业背景下评估公司治理水平
4. **风险识别**：识别管理和治理方面的潜在风险

## 输出格式要求：

请严格按照以下JSON格式输出分析结果：

```json
{
  "analysis_summary": "简要总结该公司的好公司特质（100-150字）",
  "detailed_analysis": {
    "management_quality": {
      "integrity_transparency": "诚信透明度分析（50-80字）",
      "capital_allocation": "资本配置能力分析（50-80字）",
      "strategy_execution": "战略执行力分析（50-80字）",
      "management_score": "管理层质量得分（0-10分）"
    },
    "financial_health": {
      "asset_quality": "资产质量分析（50-80字）",
      "debt_structure": "负债结构分析（50-80字）",
      "earnings_quality": "盈利质量分析（50-80字）",
      "financial_score": "财务健康度得分（0-10分）"
    },
    "governance_structure": {
      "ownership_structure": "股权结构分析（50-80字）",
      "board_governance": "董事会治理分析（50-80字）",
      "internal_control": "内控体系分析（50-80字）",
      "governance_score": "治理结构得分（0-10分）"
    },
    "sustainability": {
      "innovation_capability": "创新能力分析（50-80字）",
      "esg_performance": "ESG表现分析（50-80字）",
      "sustainability_score": "可持续发展得分（0-10分）"
    }
  },
  "positive_factors": [
    "正面因素1",
    "正面因素2", 
    "正面因素3"
  ],
  "negative_factors": [
    "负面因素1",
    "负面因素2",
    "负面因素3"
  ],
  "risk_warnings": [
    "风险警示1",
    "风险警示2"
  ],
  "final_score": "最终好公司得分（0-10分，保留1位小数）",
  "confidence_level": "分析信心度（高/中/低）"
}
```

## 评分标准：
- 9-10分：优秀的好公司，管理层卓越，治理规范，财务健康
- 7-8分：良好的好公司，管理和治理水平较高，财务状况良好
- 5-6分：一般的公司，管理或治理存在一定不足
- 3-4分：较差的公司，管理或治理存在明显问题
- 0-2分：糟糕的公司，管理混乱或治理严重缺陷

请基于提供的公司财务数据和基本信息，严格按照上述标准进行分析。注意：由于数据限制，主要基于财务数据推断管理质量和治理水平。
"""
    
    def analyze(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析公司的好公司特质"""
        try:
            # 准备分析数据
            basic_info = company_data.get('basic_info', {})
            financial_data = company_data.get('financial_data', {})
            
            # 获取最新数据年份用于分析提示
            latest_year = self._get_latest_data_year(financial_data)
            current_year = datetime.now().year
            
            # 构建分析提示
            analysis_prompt = f"""
请分析以下公司的好公司特质：

## 公司基本信息
- 公司名称：{basic_info.get('name', 'N/A')}
- 股票代码：{basic_info.get('ts_code', 'N/A')}
- 所属行业：{basic_info.get('industry', 'N/A')}
- 上市年限：{basic_info.get('listing_years', 'N/A')}年

## 数据时效性说明
- 分析基准时间：{current_year}年
- 最新财务数据：{latest_year}年年报
- 数据覆盖范围：最近5年年报数据

## 财务数据分析
{self.format_financial_data(financial_data)}

请严格按照系统提示中的JSON格式要求输出分析结果。重点关注：
1. 从财务数据推断管理层的资本配置能力和战略执行力
2. 评估公司的财务健康度和资产质量
3. 通过财务指标分析公司治理水平
4. 评估公司的可持续发展能力

分析要点：
- 管理层质量：通过ROE稳定性、资本支出效率、现金流管理等指标评估
- 财务健康度：通过资产负债率、流动比率、盈利质量等指标评估
- 治理结构：通过财务透明度、关联交易、股东回报等方面评估
- 可持续发展：通过研发投入、长期增长趋势等指标评估

**重要提示：**
- 分析必须基于实际财务数据，避免主观臆测
- 在分析中引用具体数据时，请使用准确的年份（如"{latest_year}年"而非"2020年"）
- 如果数据不是最新年份，请在分析中明确说明数据时效性
"""
            
            # 调用LLM进行分析
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = self.call_llm(messages)
            
            # 解析JSON响应
            try:
                result = json.loads(response)
                result['agent_type'] = 'good_company'
                result['company_code'] = basic_info.get('ts_code', 'N/A')
                result['company_name'] = basic_info.get('name', 'N/A')
                return result
            except json.JSONDecodeError as e:
                logging.error(f"好公司智能体JSON解析失败: {e}")
                logging.error(f"原始响应内容: {response[:500]}...")
                
                # 尝试修复JSON格式
                try:
                    # 如果响应中包含有效的JSON，尝试提取
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        result = json.loads(json_str)
                        result['agent_type'] = 'good_company'
                        result['company_code'] = basic_info.get('ts_code', 'N/A')
                        result['company_name'] = basic_info.get('name', 'N/A')
                        logging.info("成功修复JSON格式")
                        return result
                except:
                    pass
                
                return self._create_error_response(basic_info)
                
        except Exception as e:
            logging.error(f"好公司智能体分析失败: {e}")
            return self._create_error_response(company_data.get('basic_info', {}))
    
    def _create_error_response(self, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "agent_type": "good_company",
            "company_code": basic_info.get('ts_code', 'N/A'),
            "company_name": basic_info.get('name', 'N/A'),
            "analysis_summary": "分析过程中出现错误，无法完成好公司评估",
            "detailed_analysis": {
                "management_quality": {
                    "integrity_transparency": "数据不足，无法分析",
                    "capital_allocation": "数据不足，无法分析",
                    "strategy_execution": "数据不足，无法分析",
                    "management_score": 0
                },
                "financial_health": {
                    "asset_quality": "数据不足，无法分析",
                    "debt_structure": "数据不足，无法分析",
                    "earnings_quality": "数据不足，无法分析",
                    "financial_score": 0
                },
                "governance_structure": {
                    "ownership_structure": "数据不足，无法分析",
                    "board_governance": "数据不足，无法分析",
                    "internal_control": "数据不足，无法分析",
                    "governance_score": 0
                },
                "sustainability": {
                    "innovation_capability": "数据不足，无法分析",
                    "esg_performance": "数据不足，无法分析",
                    "sustainability_score": 0
                }
            },
            "positive_factors": ["无法识别"],
            "negative_factors": ["分析失败"],
            "risk_warnings": ["数据获取失败，建议重新分析"],
            "final_score": 0.0,
            "confidence_level": "低"
        }
    
    def _get_latest_data_year(self, financial_data: Dict[str, Any]) -> str:
        """获取财务数据中的最新年份"""
        try:
            latest_year = "未知"
            
            # 检查所有财务数据类别，找到最新的年份
            for category, records in financial_data.items():
                if isinstance(records, list) and records:
                    # 筛选年报数据
                    annual_records = [r for r in records 
                                    if r.get('report_type') == '1' or 
                                    (isinstance(r.get('end_date'), str) and r.get('end_date', '').endswith('1231'))]
                    
                    if annual_records:
                        # 按时间排序，获取最新的
                        annual_records.sort(key=lambda x: x.get('end_date', '19700101'))
                        latest_record = annual_records[-1]
                        end_date = latest_record.get('end_date', '')
                        
                        if isinstance(end_date, str) and len(end_date) >= 4:
                            year = end_date[:4]
                            if year.isdigit() and (latest_year == "未知" or year > latest_year):
                                latest_year = year
            
            return latest_year
            
        except Exception as e:
            logging.error(f"获取最新数据年份失败: {e}")
            return "未知"