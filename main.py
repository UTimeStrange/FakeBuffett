#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
巴菲特价值投资多智能体协作系统
主程序入口
created_by: 奇哥AI财经
"""

import os
import sys
from typing import Dict, Any
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.helpers import load_config, save_json, setup_logging, calculate_final_score
from data.data_provider import DataProvider
from agents.good_business_agent import GoodBusinessAgent
from agents.good_company_agent import GoodCompanyAgent
from agents.good_price_agent import GoodPriceAgent
from agents.final_decision_agent import FinalDecisionAgent
from main_helper import get_company_data_helper, create_failed_analysis_helper

class BuffettInvestmentSystem:
    """巴菲特价值投资多智能体系统"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化系统"""
        self.config = load_config(config_path)
        if not self.config:
            raise ValueError("配置文件加载失败")
        
        # 设置日志
        setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 初始化数据提供者
        tushare_token = self.config['api_keys']['tushare_token']
        if not tushare_token or tushare_token == "your_tushare_token_here":
            raise ValueError("请在配置文件中设置正确的Tushare API Token")
        
        self.data_provider = DataProvider(tushare_token)
        
        # 初始化智能体
        self.good_business_agent = GoodBusinessAgent(self.config)
        self.good_company_agent = GoodCompanyAgent(self.config)
        self.good_price_agent = GoodPriceAgent(self.config)
        self.final_decision_agent = FinalDecisionAgent(self.config)
        
        # 创建结果目录
        self.results_dir = self.config['output_config']['results_dir']
        os.makedirs(self.results_dir, exist_ok=True)
        
        self.logger.info("巴菲特价值投资系统初始化完成")
    
    def analyze_company(self, ts_code: str) -> Dict[str, Any]:
        """分析单个公司"""
        self.logger.info(f"开始分析公司: {ts_code}")
        
        try:
            # 获取公司数据
            company_data = self._get_company_data(ts_code)
            if not company_data['basic_info']:
                self.logger.error(f"无法获取公司基本信息: {ts_code}")
                return self._create_failed_analysis(ts_code, "数据获取失败")
            
            # 并行执行三个智能体分析
            with ThreadPoolExecutor(max_workers=3) as executor:
                # 提交任务
                business_future = executor.submit(self.good_business_agent.analyze, company_data)
                company_future = executor.submit(self.good_company_agent.analyze, company_data)
                price_future = executor.submit(self.good_price_agent.analyze, company_data)
                
                # 收集结果
                agent_results = []
                futures = {
                    'business': business_future,
                    'company': company_future,
                    'price': price_future
                }
                
                for name, future in futures.items():
                    try:
                        result = future.result(timeout=120)  # 2分钟超时
                        
                        # 检查结果是否有效（不是错误响应）
                        final_score = result.get('final_score', 0)
                        try:
                            final_score = float(final_score) if final_score is not None else 0
                        except (ValueError, TypeError):
                            final_score = 0
                            
                        if final_score > 0 or not result.get('error'):
                            agent_results.append(result)
                            self.logger.info(f"{name}智能体分析完成: {ts_code}, 得分: {final_score}")
                        else:
                            self.logger.warning(f"{name}智能体返回了错误结果: {ts_code}")
                            agent_results.append(result)
                            
                    except Exception as e:
                        self.logger.error(f"{name}智能体分析失败: {ts_code}, 错误: {e}")
                        # 创建错误结果
                        error_result = {
                            'agent_type': name,
                            'company_code': ts_code,
                            'final_score': 0.0,
                            'error': str(e)
                        }
                        agent_results.append(error_result)
            
            # 最终决策分析
            if len(agent_results) == 3:
                final_result = self.final_decision_agent.analyze(agent_results)
                self.logger.info(f"最终决策分析完成: {ts_code}")
            else:
                self.logger.error(f"智能体分析不完整: {ts_code}")
                final_result = self._create_failed_analysis(ts_code, "智能体分析不完整")
            
            # 创建股票代码专用文件夹
            stock_result_dir = os.path.join(self.results_dir, ts_code)
            os.makedirs(stock_result_dir, exist_ok=True)
            
            # 添加每个智能体的详细结果到最终结果中
            final_result['individual_agent_results'] = {
                'business_agent': next((r for r in agent_results if r.get('agent_type') == 'business'), None),
                'company_agent': next((r for r in agent_results if r.get('agent_type') == 'company'), None),
                'price_agent': next((r for r in agent_results if r.get('agent_type') == 'price'), None)
            }
            
            # 保存最终综合分析结果
            final_result_file = os.path.join(stock_result_dir, "final_analysis.json")
            save_json(final_result, final_result_file)
            
            # 单独保存每个智能体的详细结果
            for result in agent_results:
                agent_type = result.get('agent_type', 'unknown')
                agent_file = os.path.join(stock_result_dir, f"{agent_type}_analysis.json")
                save_json(result, agent_file)
            
            # 生成简化的摘要报告
            summary_report = self._create_summary_report(final_result, agent_results)
            summary_file = os.path.join(stock_result_dir, "summary_report.json")
            save_json(summary_report, summary_file)
            
            self.logger.info(f"公司分析完成: {ts_code}, 最终得分: {final_result.get('final_score', 0)}")
            return final_result
            
        except Exception as e:
            self.logger.error(f"分析公司失败: {ts_code}, 错误: {e}")
            return self._create_failed_analysis(ts_code, str(e))
    
    def _get_company_data(self, ts_code: str) -> Dict[str, Any]:
        """获取公司完整数据"""
        return get_company_data_helper(self.data_provider, ts_code)
    
    def _create_failed_analysis(self, ts_code: str, error_msg: str) -> Dict[str, Any]:
        """创建失败的分析结果"""
        return create_failed_analysis_helper(ts_code, error_msg)
    
    def _create_summary_report(self, final_result: Dict[str, Any], agent_results: list) -> Dict[str, Any]:
        """创建简化的摘要报告"""
        return {
            "stock_code": final_result.get('company_code', 'N/A'),
            "company_name": final_result.get('company_name', 'N/A'),
            "final_score": final_result.get('final_score', 0),
            "investment_recommendation": final_result.get('investment_recommendation', {}).get('recommendation', 'N/A'),
            "confidence_level": final_result.get('investment_recommendation', {}).get('confidence_level', 'N/A'),
            "key_summary": final_result.get('analysis_summary', 'N/A'),
            "agent_scores": {
                "business_score": next((r.get('final_score', 0) for r in agent_results if r.get('agent_type') == 'good_business'), 0),
                "company_score": next((r.get('final_score', 0) for r in agent_results if r.get('agent_type') == 'good_company'), 0),
                "price_score": next((r.get('final_score', 0) for r in agent_results if r.get('agent_type') == 'good_price'), 0)
            },
            "key_strengths": final_result.get('detailed_analysis', {}).get('strength_analysis', {}).get('key_strengths', []),
            "major_risks": final_result.get('detailed_analysis', {}).get('risk_analysis', {}).get('major_risks', []),
            "position_sizing": final_result.get('investment_recommendation', {}).get('position_sizing', 'N/A')
        }

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python main.py <股票代码>")
        print("示例: python main.py 600519.SH")
        sys.exit(1)
    
    ts_code = sys.argv[1]
    
    try:
        # 初始化系统
        system = BuffettInvestmentSystem()
        
        # 分析公司
        result = system.analyze_company(ts_code)
        
        # 输出结果摘要
        print(f"\n=== {result.get('company_name', ts_code)} 投资分析报告 ===")
        print(f"股票代码: {result.get('company_code', ts_code)}")
        print(f"最终得分: {result.get('final_score', 0)}/10")
        print(f"投资建议: {result.get('investment_recommendation', {}).get('recommendation', 'N/A')}")
        print(f"分析摘要: {result.get('analysis_summary', 'N/A')}")
        print(f"\n详细报告已保存到: results/{ts_code}/")
        print(f"- 最终分析: results/{ts_code}/final_analysis.json")
        print(f"- 摘要报告: results/{ts_code}/summary_report.json")
        print(f"- 各智能体详细分析: results/{ts_code}/[agent_type]_analysis.json")
        
    except Exception as e:
        print(f"系统运行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()