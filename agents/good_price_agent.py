from .base_agent import BaseAgent
from typing import Dict, Any
from datetime import datetime
import json
import logging

class GoodPriceAgent(BaseAgent):
    """好价格智能体 - 分析公司的估值水平和投资时机"""
    
    def get_system_prompt(self) -> str:
        return """
你是一位专业的价值投资分析师，专门负责评估公司的"好价格"特质。你需要严格按照巴菲特价值投资理念中对"好价格"的定义来分析公司的估值水平。

## 巴菲特定义的"好价格"核心特征：

### 1. 绝对估值分析 - 权重40%
**内在价值评估：**
- 基于自由现金流的DCF估值
- 考虑永续增长率的合理性
- 折现率的选择和风险调整
- 估值的敏感性分析

**资产价值评估：**
- 净资产价值和账面价值分析
- 有形资产和无形资产的合理性
- 重置成本和清算价值
- 资产的真实价值评估

**盈利能力估值：**
- 基于PE的历史估值区间
- 合理PE倍数的确定
- 盈利增长的可持续性
- 周期性调整后的估值

### 2. 相对估值分析 - 权重30%
**同行业对比：**
- 与同行业公司的PE、PB对比
- 行业平均估值水平分析
- 相对估值的合理性
- 行业估值溢价或折价

**历史估值对比：**
- 公司历史PE、PB区间分析
- 当前估值在历史区间的位置
- 估值均值回归的可能性
- 历史估值的驱动因素变化

**市场估值对比：**
- 与市场整体估值水平对比
- 市场情绪和风险偏好影响
- 相对于无风险收益率的吸引力
- 风险调整后的相对价值

### 3. 安全边际评估 - 权重20%
**估值折扣：**
- 当前价格相对内在价值的折扣
- 安全边际的充分性
- 下跌风险的评估
- 最坏情况下的价值保护

**风险调整：**
- 业务风险对估值的影响
- 财务风险的估值调整
- 行业风险和系统性风险
- 流动性风险的考虑

### 4. 投资时机分析 - 权重10%
**市场周期：**
- 当前市场周期位置
- 行业周期对估值的影响
- 宏观经济环境的影响
- 政策环境的变化

**催化剂识别：**
- 潜在的价值重估催化剂
- 业绩改善的预期
- 市场认知的可能变化
- 估值修复的时间预期

## 分析要求：

1. **数据驱动分析**：基于实际市场数据和财务数据进行估值
2. **多维度估值**：结合绝对估值和相对估值方法
3. **风险考虑**：充分考虑各种风险因素对估值的影响
4. **保守原则**：遵循价值投资的保守估值原则

## 输出格式要求：

请严格按照以下JSON格式输出分析结果：

```json
{
  "analysis_summary": "简要总结该公司的好价格特质（100-150字）",
  "detailed_analysis": {
    "absolute_valuation": {
      "dcf_valuation": "DCF估值分析（50-80字）",
      "asset_valuation": "资产价值分析（50-80字）",
      "earnings_valuation": "盈利能力估值分析（50-80字）",
      "intrinsic_value_estimate": "内在价值估计区间（元/股）",
      "absolute_score": "绝对估值得分（0-10分）"
    },
    "relative_valuation": {
      "peer_comparison": "同行业对比分析（50-80字）",
      "historical_comparison": "历史估值对比分析（50-80字）",
      "market_comparison": "市场估值对比分析（50-80字）",
      "relative_score": "相对估值得分（0-10分）"
    },
    "safety_margin": {
      "valuation_discount": "估值折扣分析（50-80字）",
      "risk_adjustment": "风险调整分析（50-80字）",
      "downside_protection": "下跌保护分析（50-80字）",
      "safety_score": "安全边际得分（0-10分）"
    },
    "investment_timing": {
      "market_cycle": "市场周期分析（50-80字）",
      "catalysts": "价值催化剂分析（50-80字）",
      "timing_score": "投资时机得分（0-10分）"
    }
  },
  "valuation_metrics": {
    "current_pe": "当前PE倍数",
    "current_pb": "当前PB倍数",
    "current_price": "当前股价（元）",
    "target_price_range": "目标价格区间（元）",
    "upside_potential": "上涨空间（%）",
    "downside_risk": "下跌风险（%）"
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
  "final_score": "最终好价格得分（0-10分，保留1位小数）",
  "confidence_level": "分析信心度（高/中/低）"
}
```

## 评分标准：
- 9-10分：极具吸引力的价格，大幅低于内在价值，安全边际充足
- 7-8分：有吸引力的价格，低于内在价值，安全边际合理
- 5-6分：合理的价格，接近内在价值，安全边际一般
- 3-4分：偏高的价格，高于内在价值，安全边际不足
- 0-2分：过高的价格，严重高估，存在较大下跌风险

请基于提供的公司市场数据和财务数据，严格按照上述标准进行分析。
"""
    
    def analyze(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析公司的好价格特质"""
        try:
            # 准备分析数据
            basic_info = company_data.get('basic_info', {})
            financial_data = company_data.get('financial_data', {})
            market_data = company_data.get('market_data', {})
            
            # 格式化市场数据
            market_info = self._format_market_data(market_data)
            
            # 获取最新数据年份用于分析提示
            latest_year = self._get_latest_data_year(financial_data)
            current_year = datetime.now().year
            
            # 构建分析提示
            analysis_prompt = f"""
请分析以下公司的好价格特质：

## 公司基本信息
- 公司名称：{basic_info.get('name', 'N/A')}
- 股票代码：{basic_info.get('ts_code', 'N/A')}
- 所属行业：{basic_info.get('industry', 'N/A')}
- 上市年限：{basic_info.get('listing_years', 'N/A')}年

## 数据时效性说明
- 分析基准时间：{current_year}年
- 最新财务数据：{latest_year}年年报
- 数据覆盖范围：最近5年年报数据

## 当前市场数据
{market_info}

## 财务数据分析
{self.format_financial_data(financial_data)}

请严格按照系统提示中的JSON格式要求输出分析结果。重点关注：
1. 基于财务数据计算公司的内在价值
2. 当前股价相对于内在价值的估值水平
3. 与同行业和历史估值的对比分析
4. 投资的安全边际和风险收益比

估值分析要点：
- 绝对估值：使用DCF模型、资产价值法、盈利倍数法等
- 相对估值：PE、PB等指标的行业对比和历史对比
- 安全边际：当前价格的折扣幅度和风险保护
- 投资时机：市场环境和价值催化剂

**重要提示：**
- 分析必须基于实际市场数据和财务数据，提供具体的估值区间和投资建议
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
                result['agent_type'] = 'good_price'
                result['company_code'] = basic_info.get('ts_code', 'N/A')
                result['company_name'] = basic_info.get('name', 'N/A')
                return result
            except json.JSONDecodeError as e:
                logging.error(f"好价格智能体JSON解析失败: {e}")
                logging.error(f"原始响应内容: {response[:500]}...")
                
                # 尝试修复JSON格式
                try:
                    # 如果响应中包含有效的JSON，尝试提取
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        result = json.loads(json_str)
                        result['agent_type'] = 'good_price'
                        result['company_code'] = basic_info.get('ts_code', 'N/A')
                        result['company_name'] = basic_info.get('name', 'N/A')
                        logging.info("成功修复JSON格式")
                        return result
                except:
                    pass
                
                return self._create_error_response(basic_info)
                
        except Exception as e:
            logging.error(f"好价格智能体分析失败: {e}")
            return self._create_error_response(company_data.get('basic_info', {}))
    
    def _format_market_data(self, market_data: Dict[str, Any]) -> str:
        """格式化市场数据"""
        if not market_data:
            return "市场数据不可用"
        
        formatted_text = "=== 当前市场数据 ===\n"
        formatted_text += f"当前股价: {market_data.get('close', 'N/A')} 元\n"
        formatted_text += f"市盈率(PE): {market_data.get('pe', 'N/A')}\n"
        formatted_text += f"市净率(PB): {market_data.get('pb', 'N/A')}\n"
        formatted_text += f"市销率(PS): {market_data.get('ps', 'N/A')}\n"
        formatted_text += f"总市值: {market_data.get('total_mv', 'N/A')} 万元\n"
        formatted_text += f"流通市值: {market_data.get('circ_mv', 'N/A')} 万元\n"
        
        # 历史估值数据
        if market_data.get('historical_valuation'):
            formatted_text += "\n=== 历史估值数据（近3年） ===\n"
            for record in market_data['historical_valuation'][-10:]:  # 最近10个交易日
                formatted_text += f"日期: {record.get('trade_date', 'N/A')}, PE: {record.get('pe', 'N/A')}, PB: {record.get('pb', 'N/A')}\n"
        
        return formatted_text
    
    def _create_error_response(self, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "agent_type": "good_price",
            "company_code": basic_info.get('ts_code', 'N/A'),
            "company_name": basic_info.get('name', 'N/A'),
            "analysis_summary": "分析过程中出现错误，无法完成好价格评估",
            "detailed_analysis": {
                "absolute_valuation": {
                    "dcf_valuation": "数据不足，无法分析",
                    "asset_valuation": "数据不足，无法分析",
                    "earnings_valuation": "数据不足，无法分析",
                    "intrinsic_value_estimate": "无法估算",
                    "absolute_score": 0
                },
                "relative_valuation": {
                    "peer_comparison": "数据不足，无法分析",
                    "historical_comparison": "数据不足，无法分析",
                    "market_comparison": "数据不足，无法分析",
                    "relative_score": 0
                },
                "safety_margin": {
                    "valuation_discount": "数据不足，无法分析",
                    "risk_adjustment": "数据不足，无法分析",
                    "downside_protection": "数据不足，无法分析",
                    "safety_score": 0
                },
                "investment_timing": {
                    "market_cycle": "数据不足，无法分析",
                    "catalysts": "数据不足，无法分析",
                    "timing_score": 0
                }
            },
            "valuation_metrics": {
                "current_pe": "N/A",
                "current_pb": "N/A", 
                "current_price": "N/A",
                "target_price_range": "N/A",
                "upside_potential": "N/A",
                "downside_risk": "N/A"
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