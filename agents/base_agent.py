from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime
import openai
import requests
import json
import logging

class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化智能体
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.llm_config = config.get('llm_config', {})
        self.setup_llm()
        
    def setup_llm(self):
        """设置大语言模型"""
        provider = self.llm_config.get('provider', 'openai')
        
        if provider == 'openai':
            openai.api_key = self.config['api_keys']['openai_api_key']
            self.client = openai.OpenAI(api_key=self.config['api_keys']['openai_api_key'])
        else:
            # 可以扩展其他模型提供商
            raise ValueError(f"不支持的模型提供商: {provider}")
    
    def call_llm(self, messages: list) -> str:
        """调用大语言模型"""
        provider = self.llm_config.get('provider', 'openai')
        
        try:
            if provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.llm_config.get('model', 'gpt-4'),
                    messages=messages,
                    temperature=self.llm_config.get('temperature', 0.1),
                    max_tokens=self.llm_config.get('max_tokens', 2000)
                )
                return self._clean_response(response.choices[0].message.content)
            
            elif provider == 'hunyuan':
                return self._clean_response(self._call_hunyuan(messages))
            
            else:
                raise ValueError(f"不支持的模型提供商: {provider}")
                
        except Exception as e:
            logging.error(f"调用LLM失败: {e}")
            return ""
    
    def _clean_response(self, response: str) -> str:
        """清理响应内容，移除markdown代码块标记"""
        if not response:
            return response
        
        # 移除markdown代码块标记
        response = response.strip()
        
        # 如果响应被包裹在```json...```中，提取JSON内容
        if response.startswith('```json') and response.endswith('```'):
            # 移除开头的```json和结尾的```
            response = response[7:-3].strip()
        elif response.startswith('```') and response.endswith('```'):
            # 移除开头和结尾的```
            lines = response.split('\n')
            if len(lines) > 2:
                response = '\n'.join(lines[1:-1]).strip()
        
        return response
    
    def _call_hunyuan(self, messages: list) -> str:
        """调用混元模型"""
        try:
            # 构建请求头
            headers = {
                "Authorization": self.hunyuan_key,
                "Content-Type": "application/json"
            }
            
            # 构建请求数据
            data = {
                "model": self.llm_config.get('model', 'hunyuan'),
                "messages": messages,
                "enable_enhancement": self.hunyuan_config.get('enable_enhancement', False),
                "sensitive_business": self.hunyuan_config.get('sensitive_business', True),
            }
            
            # 发送请求
            response = requests.post(self.hunyuan_url, headers=headers, data=json.dumps(data))
            response.raise_for_status()  # 检查HTTP错误
            
            # 解析响应
            result = response.json()
            return result['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            logging.error(f"混元API请求失败: {e}")
            return ""
        except KeyError as e:
            logging.error(f"混元API响应格式错误: {e}")
            return ""
        except Exception as e:
            logging.error(f"调用混元模型失败: {e}")
            return ""
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass
    
    @abstractmethod
    def analyze(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析公司数据"""
        pass
    
    def format_financial_data(self, financial_data: Dict[str, Any]) -> str:
        """格式化财务数据为可读文本"""
        formatted_text = ""
        
        def filter_annual_reports(records):
            """筛选年报数据并按时间排序"""
            if not records:
                return []
            
            # 筛选年报数据 (report_type='1' 或 end_date以1231结尾)
            annual_records = []
            for record in records:
                end_date = record.get('end_date', '')
                report_type = record.get('report_type', '')
                
                # 优先使用report_type='1'（年报），其次使用end_date以1231结尾的记录
                if report_type == '1' or (isinstance(end_date, str) and end_date.endswith('1231')):
                    annual_records.append(record)
            
            # 如果没有明确的年报数据，则使用所有数据
            if not annual_records:
                annual_records = records
            
            # 按end_date排序（最新的在后面）
            try:
                annual_records.sort(key=lambda x: x.get('end_date', '19700101'), reverse=False)
            except:
                pass
            
            # 返回最近5年的数据
            return annual_records[-5:]
        
        # 格式化利润表数据
        if financial_data.get('income'):
            formatted_text += "=== 利润表数据（年报）===\n"
            annual_income = filter_annual_reports(financial_data['income'])
            for record in annual_income:
                end_date = record.get('end_date', 'N/A')
                year = end_date[:4] if len(str(end_date)) >= 4 else 'N/A'
                formatted_text += f"报告期: {end_date} ({year}年年报)\n"
                formatted_text += f"营业收入: {record.get('total_revenue', 'N/A')} 万元\n"
                formatted_text += f"净利润: {record.get('n_income', 'N/A')} 万元\n"
                formatted_text += f"研发费用: {record.get('rd_exp', 'N/A')} 万元\n"
                formatted_text += "---\n"
        
        # 格式化资产负债表数据
        if financial_data.get('balancesheet'):
            formatted_text += "\n=== 资产负债表数据（年报）===\n"
            annual_balance = filter_annual_reports(financial_data['balancesheet'])
            for record in annual_balance:
                end_date = record.get('end_date', 'N/A')
                year = end_date[:4] if len(str(end_date)) >= 4 else 'N/A'
                formatted_text += f"报告期: {end_date} ({year}年年报)\n"
                formatted_text += f"总资产: {record.get('total_assets', 'N/A')} 万元\n"
                formatted_text += f"总负债: {record.get('total_liab', 'N/A')} 万元\n"
                formatted_text += f"股东权益: {record.get('total_hldr_eqy_exc_min_int', 'N/A')} 万元\n"
                formatted_text += "---\n"
        
        # 格式化现金流量表数据
        if financial_data.get('cashflow'):
            formatted_text += "\n=== 现金流量表数据（年报）===\n"
            annual_cashflow = filter_annual_reports(financial_data['cashflow'])
            for record in annual_cashflow:
                end_date = record.get('end_date', 'N/A')
                year = end_date[:4] if len(str(end_date)) >= 4 else 'N/A'
                formatted_text += f"报告期: {end_date} ({year}年年报)\n"
                formatted_text += f"经营活动现金流: {record.get('n_cashflow_act', 'N/A')} 万元\n"
                formatted_text += f"投资活动现金流: {record.get('n_cashflow_inv_act', 'N/A')} 万元\n"
                formatted_text += f"筹资活动现金流: {record.get('n_cash_flows_fnc_act', 'N/A')} 万元\n"
                formatted_text += "---\n"
        
        # 格式化财务指标数据
        if financial_data.get('fina_indicator'):
            formatted_text += "\n=== 财务指标数据（年报）===\n"
            annual_indicators = filter_annual_reports(financial_data['fina_indicator'])
            for record in annual_indicators:
                end_date = record.get('end_date', 'N/A')
                year = end_date[:4] if len(str(end_date)) >= 4 else 'N/A'
                formatted_text += f"报告期: {end_date} ({year}年年报)\n"
                formatted_text += f"ROE: {record.get('roe', 'N/A')}%\n"
                formatted_text += f"ROA: {record.get('roa', 'N/A')}%\n"
                formatted_text += f"毛利率: {record.get('grossprofit_margin', 'N/A')}%\n"
                formatted_text += f"净利率: {record.get('netprofit_margin', 'N/A')}%\n"
                formatted_text += f"资产负债率: {record.get('debt_to_assets', 'N/A')}%\n"
                formatted_text += "---\n"
        
        # 添加数据时效性说明
        formatted_text += f"\n=== 数据说明 ===\n"
        formatted_text += f"数据获取时间: {datetime.now().strftime('%Y-%m-%d')}\n"
        formatted_text += f"注意: 以上数据为最近5年的年报数据，按时间顺序排列\n"
        
        return formatted_text