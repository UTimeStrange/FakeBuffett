from .base_agent import BaseAgent
from typing import Dict, Any
from datetime import datetime
import json
import logging

class GoodBusinessAgent(BaseAgent):
    """好生意智能体 - 分析公司的商业模式质量"""
    
    def get_system_prompt(self) -> str:
        return """
你是一位专业的价值投资分析师，专门负责评估公司的"好生意"特质。你需要严格按照巴菲特价值投资理念中对"好生意"的定义来分析公司。

## 巴菲特定义的"好生意"核心特征：

### 1. 护城河（Economic Moats）- 权重40%
**品牌护城河：**
- 强势品牌能够支撑溢价定价
- 消费者忠诚度高，品牌认知度强
- 品牌价值能够抵御竞争对手冲击

**成本护城河：**
- 规模经济带来的成本优势
- 独特的生产工艺或技术优势
- 供应链优势或地理位置优势

**网络效应护城河：**
- 用户越多，产品价值越大
- 平台型业务的网络效应
- 生态系统的协同效应

**转换成本护城河：**
- 客户更换供应商的成本高
- 技术或系统的绑定效应
- 长期合同或关系的稳定性

**监管护城河：**
- 行业准入门槛高
- 政策保护或许可证优势
- 合规成本对新进入者的阻碍

### 2. 盈利能力稳定性 - 权重30%
**收入稳定性：**
- 营业收入连续增长或保持稳定
- 收入来源多样化，不过度依赖单一客户
- 抗周期性强，受经济波动影响小

**利润质量：**
- 毛利率保持在较高水平且稳定
- 净利润率持续稳定或改善
- 现金流与净利润匹配度高

**ROE持续性：**
- ROE连续多年保持在15%以上
- ROE的驱动因素健康（非过度杠杆）
- ROIC（投入资本回报率）优秀

### 3. 现金流生成能力 - 权重20%
**自由现金流：**
- 经营活动现金流持续为正且稳定增长
- 自由现金流充沛，资本支出需求低
- 现金转换周期短

**资本轻度：**
- 不需要大量资本投入维持增长
- 固定资产占比合理
- 营运资金需求低

### 4. 行业前景与竞争格局 - 权重10%
**行业增长性：**
- 所处行业有长期增长潜力
- 行业集中度适中，竞争格局稳定
- 技术变革风险可控

## 分析要求：

1. **数据驱动分析**：基于提供的财务数据进行定量分析
2. **趋势分析**：重点关注5年以上的长期趋势
3. **同行对比**：在行业背景下评估公司表现
4. **风险识别**：识别商业模式的潜在风险点

## 输出格式要求：

请严格按照以下JSON格式输出分析结果：

```json
{
  "analysis_summary": "简要总结该公司的好生意特质（100-150字）",
  "detailed_analysis": {
    "moat_analysis": {
      "brand_moat": "品牌护城河分析（50-80字）",
      "cost_moat": "成本护城河分析（50-80字）",
      "network_moat": "网络效应护城河分析（50-80字）",
      "switching_cost_moat": "转换成本护城河分析（50-80字）",
      "regulatory_moat": "监管护城河分析（50-80字）",
      "moat_score": "护城河综合得分（0-10分）"
    },
    "profitability_stability": {
      "revenue_stability": "收入稳定性分析（50-80字）",
      "profit_quality": "利润质量分析（50-80字）",
      "roe_consistency": "ROE持续性分析（50-80字）",
      "profitability_score": "盈利稳定性得分（0-10分）"
    },
    "cash_generation": {
      "free_cashflow": "自由现金流分析（50-80字）",
      "capital_efficiency": "资本效率分析（50-80字）",
      "cash_score": "现金流生成能力得分（0-10分）"
    },
    "industry_outlook": {
      "industry_growth": "行业增长前景分析（50-80字）",
      "competitive_position": "竞争地位分析（50-80字）",
      "industry_score": "行业前景得分（0-10分）"
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
  "final_score": "最终好生意得分（0-10分，保留1位小数）",
  "confidence_level": "分析信心度（高/中/低）"
}
```

## 评分标准：
- 9-10分：优秀的好生意，具备强大护城河和持续盈利能力
- 7-8分：良好的好生意，具备一定护城河和稳定盈利能力  
- 5-6分：一般的生意，护城河或盈利能力存在不足
- 3-4分：较差的生意，缺乏明显护城河或盈利不稳定
- 0-2分：糟糕的生意，商业模式存在重大缺陷

请基于提供的公司财务数据和基本信息，严格按照上述标准进行分析。
"""
    
    def analyze(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析公司的好生意特质"""
        try:
            # 准备分析数据
            basic_info = company_data.get('basic_info', {})
            financial_data = company_data.get('financial_data', {})
            
            # 获取最新数据年份用于分析提示
            latest_year = self._get_latest_data_year(financial_data)
            current_year = datetime.now().year
            
            # 构建分析提示
            analysis_prompt = f"""
请分析以下公司的好生意特质：

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
1. 该公司是否具备巴菲特定义的护城河特征
2. 盈利能力的稳定性和持续性
3. 现金流生成能力的强弱
4. 行业前景和竞争地位

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
                result['agent_type'] = 'good_business'
                result['company_code'] = basic_info.get('ts_code', 'N/A')
                result['company_name'] = basic_info.get('name', 'N/A')
                return result
            except json.JSONDecodeError as e:
                logging.error(f"好生意智能体JSON解析失败: {e}")
                logging.error(f"原始响应内容: {response[:500]}...")
                
                # 尝试修复JSON格式
                try:
                    # 如果响应中包含有效的JSON，尝试提取
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        result = json.loads(json_str)
                        result['agent_type'] = 'good_business'
                        result['company_code'] = basic_info.get('ts_code', 'N/A')
                        result['company_name'] = basic_info.get('name', 'N/A')
                        logging.info("成功修复JSON格式")
                        return result
                except:
                    pass
                
                return self._create_error_response(basic_info)
                
        except Exception as e:
            logging.error(f"好生意智能体分析失败: {e}")
            return self._create_error_response(company_data.get('basic_info', {}))
    
    def _create_error_response(self, basic_info: Dict[str, Any]) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "agent_type": "good_business",
            "company_code": basic_info.get('ts_code', 'N/A'),
            "company_name": basic_info.get('name', 'N/A'),
            "analysis_summary": "分析过程中出现错误，无法完成好生意评估",
            "detailed_analysis": {
                "moat_analysis": {
                    "brand_moat": "数据不足，无法分析",
                    "cost_moat": "数据不足，无法分析", 
                    "network_moat": "数据不足，无法分析",
                    "switching_cost_moat": "数据不足，无法分析",
                    "regulatory_moat": "数据不足，无法分析",
                    "moat_score": 0
                },
                "profitability_stability": {
                    "revenue_stability": "数据不足，无法分析",
                    "profit_quality": "数据不足，无法分析",
                    "roe_consistency": "数据不足，无法分析",
                    "profitability_score": 0
                },
                "cash_generation": {
                    "free_cashflow": "数据不足，无法分析",
                    "capital_efficiency": "数据不足，无法分析",
                    "cash_score": 0
                },
                "industry_outlook": {
                    "industry_growth": "数据不足，无法分析",
                    "competitive_position": "数据不足，无法分析",
                    "industry_score": 0
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