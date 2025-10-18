from .base_agent import BaseAgent
from typing import Dict, Any, List
import json
import logging

class FinalDecisionAgent(BaseAgent):
    """最终决策智能体 - 综合分析三个智能体的结果并做出最终投资决策"""
    
    def get_system_prompt(self) -> str:
        return """
你是一位资深的价值投资决策专家，负责综合分析好生意智能体、好公司智能体和好价格智能体的分析结果，并做出最终的投资决策建议。

## 决策框架：

### 1. 综合评分体系 - 权重分配
**好生意评分权重：35%**
- 护城河的强度和可持续性
- 盈利能力的稳定性
- 现金流生成能力
- 行业前景和竞争地位

**好公司评分权重：35%**
- 管理层质量和诚信度
- 财务健康度和透明度
- 治理结构的规范性
- 可持续发展能力

**好价格评分权重：30%**
- 估值的合理性和吸引力
- 安全边际的充分性
- 投资时机的把握
- 风险收益比的评估

### 2. 决策逻辑
**投资决策矩阵：**
- 三高（好生意≥7，好公司≥7，好价格≥7）：强烈推荐
- 两高一中（两项≥7，一项5-6.9）：推荐
- 一高两中（一项≥7，两项5-6.9）：谨慎推荐
- 其他情况：不推荐或观察

**风险控制原则：**
- 任何一项评分低于3分：直接否决
- 好价格评分低于5分：需要更高的安全边际
- 好公司评分低于5分：需要谨慎考虑治理风险
- 好生意评分低于5分：需要评估商业模式风险

### 3. 投资建议分类
**强烈推荐（8.5-10分）：**
- 三项评分均优秀，符合巴菲特投资标准
- 建议重点配置，长期持有

**推荐（7.0-8.4分）：**
- 整体质量良好，具备投资价值
- 建议适度配置，关注风险点

**谨慎推荐（5.5-6.9分）：**
- 存在一定不足，但仍有投资机会
- 建议小仓位试探，密切跟踪

**不推荐（0-5.4分）：**
- 不符合价值投资标准
- 建议回避或等待更好时机

## 分析要求：

1. **客观综合**：客观分析三个智能体的结论，避免主观偏见
2. **风险识别**：重点识别和评估各种投资风险
3. **决策逻辑**：清晰阐述投资决策的逻辑和依据
4. **实操建议**：提供具体的投资操作建议

## 输出格式要求：

请严格按照以下JSON格式输出分析结果：

```json
{
  "analysis_summary": "综合分析总结，包含投资决策建议（150-200字）",
  "detailed_analysis": {
    "score_synthesis": {
      "business_score": "好生意得分",
      "company_score": "好公司得分", 
      "price_score": "好价格得分",
      "weighted_score": "加权综合得分",
      "score_analysis": "得分分析说明（80-120字）"
    },
    "strength_analysis": {
      "key_strengths": [
        "核心优势1",
        "核心优势2",
        "核心优势3"
      ],
      "competitive_advantages": "竞争优势分析（80-120字）"
    },
    "risk_analysis": {
      "major_risks": [
        "主要风险1",
        "主要风险2", 
        "主要风险3"
      ],
      "risk_mitigation": "风险缓解措施建议（80-120字）"
    },
    "investment_logic": {
      "investment_thesis": "投资逻辑阐述（100-150字）",
      "catalyst_factors": [
        "催化因素1",
        "催化因素2"
      ],
      "time_horizon": "建议投资期限"
    }
  },
  "investment_recommendation": {
    "recommendation": "投资建议（强烈推荐/推荐/谨慎推荐/不推荐）",
    "confidence_level": "决策信心度（高/中/低）",
    "position_sizing": "建议仓位比例",
    "entry_strategy": "入场策略建议（80-100字）",
    "exit_strategy": "退出策略建议（80-100字）"
  },
  "monitoring_points": [
    "关键监控指标1",
    "关键监控指标2",
    "关键监控指标3"
  ],
  "final_score": "最终综合得分（0-10分，保留1位小数）",
  "decision_rationale": "决策理由总结（100-150字）"
}
```

## 决策原则：
- 遵循巴菲特价值投资理念
- 坚持安全边际原则
- 重视长期价值创造
- 关注风险控制

请基于三个智能体的分析结果，严格按照上述框架进行综合决策分析。
"""
    
    def analyze(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """综合分析三个智能体的结果并做出最终决策"""
        try:
            # 提取各智能体的分析结果
            business_result = None
            company_result = None
            price_result = None
            
            for result in agent_results:
                agent_type = result.get('agent_type')
                if agent_type == 'good_business':
                    business_result = result
                elif agent_type == 'good_company':
                    company_result = result
                elif agent_type == 'good_price':
                    price_result = result
            
            # 检查是否所有智能体都有结果
            if not all([business_result, company_result, price_result]):
                return self._create_error_response("缺少必要的智能体分析结果")
            
            # 检查智能体结果是否有效（不是错误响应）
            valid_results = []
            for result in [business_result, company_result, price_result]:
                if result.get('error') or result.get('final_score', 0) == 0:
                    # 如果是错误响应，尝试从日志中提取实际得分
                    if hasattr(result, 'get') and result.get('final_score') != 0:
                        valid_results.append(result)
                    else:
                        # 创建默认评分以避免完全失败
                        logging.warning(f"智能体 {result.get('agent_type')} 返回错误结果，使用默认评分")
                else:
                    valid_results.append(result)
            
            # 如果所有结果都无效，但实际上智能体可能成功了（从日志看），尝试使用原始结果
            if len(valid_results) == 0:
                logging.info("尝试使用原始智能体结果进行分析")
                valid_results = [business_result, company_result, price_result]
            
            # 提取基本信息
            company_code = business_result.get('company_code', 'N/A')
            company_name = business_result.get('company_name', 'N/A')
            
            # 构建综合分析提示
            analysis_prompt = f"""
请基于以下三个智能体的分析结果，做出最终的投资决策：

## 公司基本信息
- 公司名称：{company_name}
- 股票代码：{company_code}

## 好生意智能体分析结果
{json.dumps(business_result, ensure_ascii=False, indent=2)}

## 好公司智能体分析结果  
{json.dumps(company_result, ensure_ascii=False, indent=2)}

## 好价格智能体分析结果
{json.dumps(price_result, ensure_ascii=False, indent=2)}

请严格按照系统提示中的JSON格式要求输出最终决策分析。重点关注：
1. 综合三个维度的评分，计算加权综合得分
2. 识别公司的核心投资亮点和主要风险点
3. 基于巴菲特价值投资理念给出明确的投资建议
4. 提供具体的投资策略和风险控制措施

决策要点：
- 权重分配：好生意35%，好公司35%，好价格30%
- 风险控制：任何维度低于3分需要特别关注
- 投资逻辑：必须符合价值投资的核心原则
- 实操建议：提供可执行的投资策略

注意：决策必须客观理性，基于数据分析，避免情绪化判断。
"""
            
            # 调用LLM进行综合分析
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = self.call_llm(messages)
            
            # 解析JSON响应
            try:
                result = json.loads(response)
                result['agent_type'] = 'final_decision'
                result['company_code'] = company_code
                result['company_name'] = company_name
                
                # 添加原始智能体结果的引用
                result['source_analysis'] = {
                    'good_business': business_result,
                    'good_company': company_result,
                    'good_price': price_result
                }
                
                return result
            except json.JSONDecodeError as e:
                logging.error(f"最终决策智能体JSON解析失败: {e}")
                logging.error(f"原始响应内容: {response[:500]}...")
                
                # 尝试修复JSON格式
                try:
                    # 如果响应中包含有效的JSON，尝试提取
                    import re
                    json_match = re.search(r'\{.*\}', response, re.DOTALL)
                    if json_match:
                        json_str = json_match.group()
                        result = json.loads(json_str)
                        result['agent_type'] = 'final_decision'
                        result['company_code'] = company_code
                        result['company_name'] = company_name
                        
                        # 添加原始智能体结果的引用
                        result['source_analysis'] = {
                            'good_business': business_result,
                            'good_company': company_result,
                            'good_price': price_result
                        }
                        
                        logging.info("成功修复JSON格式")
                        return result
                except:
                    pass
                
                return self._create_error_response("JSON解析失败")
                
        except Exception as e:
            logging.error(f"最终决策智能体分析失败: {e}")
            return self._create_error_response(f"分析过程出错: {str(e)}")
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "agent_type": "final_decision",
            "company_code": "N/A",
            "company_name": "N/A",
            "analysis_summary": f"最终决策分析失败：{error_msg}",
            "detailed_analysis": {
                "score_synthesis": {
                    "business_score": 0,
                    "company_score": 0,
                    "price_score": 0,
                    "weighted_score": 0,
                    "score_analysis": "分析失败，无法计算得分"
                },
                "strength_analysis": {
                    "key_strengths": ["无法识别"],
                    "competitive_advantages": "分析失败，无法识别优势"
                },
                "risk_analysis": {
                    "major_risks": ["分析失败风险"],
                    "risk_mitigation": "建议重新进行完整分析"
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
                "entry_strategy": "建议重新分析后再做决策",
                "exit_strategy": "N/A"
            },
            "monitoring_points": ["重新进行完整分析"],
            "final_score": 0.0,
            "decision_rationale": f"由于{error_msg}，无法做出可靠的投资决策建议"
        }