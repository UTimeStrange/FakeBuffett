#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
created_by: 奇哥AI财经
"""
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import sys
import os

# 添加utils目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.data_utils import process_financial_data

class DataProvider:
    """A股数据提供者，基于Tushare接口"""
    
    def __init__(self, token: str):
        """
        初始化数据提供者
        
        Args:
            token: Tushare API token
        """
        self.token = token
        ts.set_token(token)
        self.pro = ts.pro_api()
        
    def get_stock_basic_info(self, ts_code: str) -> Dict:
        """获取股票基本信息"""
        try:
            # 基本信息
            basic_info = self.pro.stock_basic(ts_code=ts_code, fields='ts_code,symbol,name,area,industry,market,list_date')
            if basic_info.empty:
                return {}
                
            info = basic_info.iloc[0].to_dict()
            
            # 计算上市年限
            list_date = datetime.strptime(info['list_date'], '%Y%m%d')
            listing_years = (datetime.now() - list_date).days / 365.25
            info['listing_years'] = round(listing_years, 1)
            
            return info
        except Exception as e:
            logging.error(f"获取股票基本信息失败 {ts_code}: {e}")
            return {}
    
    def get_financial_data(self, ts_code: str, years: int = 5) -> Dict:
        """获取财务数据（用于好生意和好公司分析）"""
        try:
            # 获取当前年份，确保获取最新的完整年报数据
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            # 如果当前时间在4月30日之前，最新年报可能还没有发布，往前推一年
            if current_month < 5:  # 年报通常在4月30日前发布
                latest_year = current_year - 1
            else:
                latest_year = current_year
                
            end_date = f"{latest_year}1231"  # 最新年报的结束日期
            start_date = f"{latest_year - years + 1}0101"  # 往前推years年的开始日期
            
            logging.info(f"获取财务数据时间范围: {start_date} 到 {end_date}")
            
            # 利润表数据
            income = self.pro.income(ts_code=ts_code, start_date=start_date, end_date=end_date, fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,total_revenue,revenue,int_income,prem_earned,comm_income,n_commis_income,n_oth_income,n_oth_b_income,prem_income,out_prem,une_prem_reser,reins_income,n_sec_tb_income,n_sec_uw_income,n_asset_mg_income,oth_b_income,fv_value_chg_gain,invest_income,ass_invest_income,forex_gain,total_cogs,oper_cost,int_exp,comm_exp,biz_tax_surchg,sell_exp,admin_exp,fin_exp,assets_impair_loss,prem_refund,compens_payout,reser_insur_liab,div_payt,reins_exp,oper_exp,compens_payout_refu,insur_reser_refu,reins_cost_refund,other_bus_cost,operate_profit,non_oper_income,non_oper_exp,nca_disploss,total_profit,income_tax,n_income,n_income_attr_p,minority_gain,oth_compr_income,t_compr_income,compr_inc_attr_p,compr_inc_attr_m_s,ebit,ebitda,insurance_exp,undist_profit,distable_profit,rd_exp,fin_exp_int_exp,fin_exp_int_inc,transfer_surplus_rese,transfer_housing_imprest,transfer_oth,adj_lossgain,withdra_legal_surplus,withdra_legal_publi,withdra_biz_devfund,withdra_rese_fund,withdra_oth_ersu,workers_welfare,distr_profit_shrhder,prfshare_payable_dvd,comshare_payable_dvd,capit_comstock_div,continued_net_profit,end_net_profit')
            
            # 资产负债表数据
            balancesheet = self.pro.balancesheet(ts_code=ts_code, start_date=start_date, end_date=end_date, fields='ts_code,ann_date,f_ann_date,end_date,report_type,comp_type,total_share,cap_rese,undistr_porfit,surplus_rese,special_rese,money_cap,trad_asset,notes_receiv,accounts_receiv,oth_receiv,prepayment,div_receiv,int_receiv,inventories,amor_exp,nca_within_1y,sett_rsrv,loanto_oth_bank_fi,premium_receiv,reinsur_receiv,reinsur_res_receiv,pur_resale_fa,oth_cur_assets,total_cur_assets,fa_avail_for_sale,htm_invest,lt_eqt_invest,invest_real_estate,time_deposits,oth_assets,lt_rec,fix_assets,cip,const_materials,fixed_assets_disp,produc_bio_assets,oil_and_gas_assets,intan_assets,r_and_d,goodwill,lt_amor_exp,defer_tax_assets,decr_in_disbur,oth_nca,total_nca,cash_reser_cb,depos_in_oth_bfi,prec_metals,deriv_assets,rr_reinsur_une_prem,rr_reinsur_outstd_cla,rr_reinsur_lins_liab,rr_reinsur_lthins_liab,refund_depos,ph_pledge_loans,receiv_invest,receiv_cap_contrib,insurance_cont_reserves,banking_rf,sf_execu,traded_fa,note_accounts_receiv,cash_in_cb,total_assets,shortterm_loan,trad_liab,notes_payable,acct_payable,adv_receipts,sold_for_repur_fa,comm_payable,payroll_payable,taxes_payable,int_payable,div_payable,oth_payable,acc_exp,deferred_inc,st_bonds_payable,payable_to_reinsurer,rsrv_insur_cont,acting_trading_sec,acting_uw_sec,non_cur_liab_due_1y,oth_cur_liab,total_cur_liab,bond_payable,lt_payable,specific_payables,estimated_liab,defer_tax_liab,defer_inc_non_cur_liab,oth_ncl,total_ncl,depos_oth_bfi,deriv_liab,depos,agency_bus_liab,oth_liab,prem_receiv_adva,depos_received,ph_invest,reser_une_prem,reser_outstd_claims,reser_lins_liab,reser_lthins_liab,indept_acc_liab,pledge_borr,indem_payable,policy_div_payable,total_liab,treasury_share,ordin_risk_reser,forex_differ,invest_loss_unconf,minority_int,total_hldr_eqy_exc_min_int,total_hldr_eqy_inc_min_int,total_liab_hldr_eqy,lt_payroll_payable,oth_comp_income,oth_eqt_tools,oth_eqt_tools_p_shr,lending_funds,acc_receivable,st_fin_payable,payables,hfs_assets,hfs_sales')
            
            # 现金流量表数据
            cashflow = self.pro.cashflow(ts_code=ts_code, start_date=start_date, end_date=end_date, fields='ts_code,ann_date,f_ann_date,end_date,comp_type,report_type,net_profit,finan_exp,c_fr_sale_sg,recp_tax_rends,n_depos_incr_fi,n_incr_loans_cb,n_inc_borr_oth_fi,prem_fr_orig_contr,n_incr_insured_dep,n_reinsur_prem,n_incr_disp_tfa,ifc_cash_incr,n_incr_disp_faas,n_incr_loans_oth_bank,n_cap_incr_repur,c_fr_oth_operate_a,c_inf_fr_operate_a,c_paid_goods_s,c_paid_to_for_empl,c_paid_for_taxes,n_decr_insured_dep,n_decr_loans_cb,c_paid_claim,n_decr_fin_depos,c_paid_int_comm,c_paid_depr_charb_insur_reserves,c_paid_policy_div,c_paid_oth_operate_a,c_outf_fr_operate_a,n_cashflow_act,oth_recp_ral_inv_act,c_disp_withdrwl_invest,c_recp_return_invest,n_recp_disp_fiolta,n_recp_disp_sobu,stot_inflows_inv_act,c_paid_acq_const_fiolta,c_paid_invest,n_disp_subs_oth_biz,oth_pay_ral_inv_act,n_incr_pledge_loan,stot_out_inv_act,n_cashflow_inv_act,c_recp_borrow,proc_issue_bonds,oth_cash_recp_ral_fnc_act,stot_cash_in_fnc_act,free_cashflow,c_prepay_amt_borr,c_pay_dist_dpcp_int_exp,incl_dvd_profit_paid_sc_ms,oth_cashpay_ral_fnc_act,stot_cashout_fnc_act,n_cash_flows_fnc_act,eff_fx_flu_cash,n_incr_cash_cash_equ,c_cash_equ_beg_period,c_cash_equ_end_period,c_recp_cap_contrib,incl_cash_rec_saims,uncon_invest_loss,prov_depr_assets,depr_fa_coga_dpba,amort_intang_assets,lt_amort_deferred_exp,decr_deferred_exp,incr_acc_exp,loss_disp_fiolta,loss_scr_fa,loss_fv_chg,invest_loss,decr_def_inc_tax_assets,incr_def_inc_tax_liab,decr_inventories,decr_oper_payable,incr_oper_payable,others,im_net_cashflow_oper_act,conv_debt_into_cap,conv_copbonds_due_within_1y,fa_fnc_leases,end_bal_cash,beg_bal_cash,end_bal_cash_equ,beg_bal_cash_equ,im_n_incr_cash_equ')
            
            # 财务指标数据
            fina_indicator = self.pro.fina_indicator(ts_code=ts_code, start_date=start_date, end_date=end_date, fields='ts_code,ann_date,end_date,eps,dt_eps,total_revenue_ps,revenue_ps,capital_rese_ps,surplus_rese_ps,undist_profit_ps,extra_item,profit_dedt,gross_margin,current_ratio,quick_ratio,cash_ratio,invturn_days,arturn_days,inv_turn,ar_turn,ca_turn,fa_turn,assets_turn,op_income,valuechange_income,interst_income,daa,ebit,ebitda,fcff,fcfe,current_exint,noncurrent_exint,interestdebt,netdebt,tangible_asset,working_capital,networking_capital,invest_capital,retained_earnings,diluted2_eps,bps,ocfps,retainedps,cfps,ebit_ps,fcff_ps,fcfe_ps,netprofit_margin,grossprofit_margin,cogs_of_sales,expense_of_sales,profit_to_gr,saleexp_to_gr,adminexp_of_gr,finaexp_of_gr,impai_ttm,gc_of_gr,op_of_gr,ebit_of_gr,roe,roe_waa,roe_dt,roa,npta,roic,roe_yearly,roa_yearly,roe_avg,opincome_of_ebt,investincome_of_ebt,n_op_profit_of_ebt,tax_to_ebt,dtprofit_to_profit,salescash_to_or,ocf_to_or,ocf_to_opincome,capitalized_to_da,debt_to_assets,assets_to_eqt,dp_assets_to_eqt,ca_to_assets,nca_to_assets,tbassets_to_totalassets,int_to_talcap,eqt_to_talcapital,currentdebt_to_debt,longdeb_to_debt,ocf_to_shortdebt,debt_to_eqt,eqt_to_debt,eqt_to_interestdebt,tangibleasset_to_debt,tangasset_to_intdebt,tangibleasset_to_netdebt,ocf_to_debt,ocf_to_interestdebt,ocf_to_netdebt,ebit_to_interest,longdebt_to_workingcapital,ebitda_to_debt,turn_days,roa_yearly,roa_dp,fixed_assets,profit_prefin_exp,non_op_profit,op_to_ebt,nop_to_ebt,ocf_to_profit,cash_to_liqdebt,cash_to_liqdebt_withinterest,op_to_liqdebt,op_to_debt,roic_yearly,total_fa_trun,profit_to_op,q_opincome,q_investincome,q_dtprofit,q_eps,q_netprofit_margin,q_gsprofit_margin,q_exp_to_sales,q_profit_to_gr,q_saleexp_to_gr,q_adminexp_to_gr,q_finaexp_to_gr,q_impair_to_gr_ttm,q_gc_to_gr,q_op_to_gr,q_roe,q_dt_roe,q_npta,q_opincome_to_ebt,q_investincome_to_ebt,q_dtprofit_to_profit,q_salescash_to_or,q_ocf_to_sales,q_ocf_to_or,basic_eps_yoy,dt_eps_yoy,cfps_yoy,op_yoy,ebt_yoy,netprofit_yoy,dt_netprofit_yoy,ocf_yoy,roe_yoy,bps_yoy,assets_yoy,eqt_yoy,tr_yoy,or_yoy,q_gr_yoy,q_gr_qoq,q_sales_yoy,q_sales_qoq,q_op_yoy,q_op_qoq,q_profit_yoy,q_profit_qoq,q_netprofit_yoy,q_netprofit_qoq,equity_yoy,rd_exp,rd_exp_ttm')
            
            # 处理重复列名问题
            def clean_dataframe(df):
                if df.empty:
                    return df
                # 删除重复的列
                df = df.loc[:, ~df.columns.duplicated()]
                return df
            
            income = clean_dataframe(income)
            balancesheet = clean_dataframe(balancesheet)
            cashflow = clean_dataframe(cashflow)
            fina_indicator = clean_dataframe(fina_indicator)
            
            # 转换为字典并进行数据清理
            raw_data = {
                'income': income.to_dict('records') if not income.empty else [],
                'balancesheet': balancesheet.to_dict('records') if not balancesheet.empty else [],
                'cashflow': cashflow.to_dict('records') if not cashflow.empty else [],
                'fina_indicator': fina_indicator.to_dict('records') if not fina_indicator.empty else []
            }
            
            # 使用安全的数据处理函数
            processed_data = process_financial_data(raw_data)
            
            # 添加数据质量检查和日志
            self._log_data_quality(ts_code, processed_data, start_date, end_date)
            
            return processed_data
        except Exception as e:
            logging.error(f"获取财务数据失败 {ts_code}: {e}")
            return {'income': [], 'balancesheet': [], 'cashflow': [], 'fina_indicator': []}
    
    def get_market_data(self, ts_code: str) -> Dict:
        """获取市场数据（用于好价格分析）"""
        try:
            # 当前股价和市值
            daily = self.pro.daily(ts_code=ts_code, trade_date='', fields='ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount')
            if daily.empty:
                return {}
            
            latest_data = daily.iloc[0].to_dict()
            
            # 获取市值数据
            daily_basic = self.pro.daily_basic(ts_code=ts_code, trade_date='', fields='ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_share,float_share,free_share,total_mv,circ_mv')
            if not daily_basic.empty:
                market_data = daily_basic.iloc[0].to_dict()
                latest_data.update(market_data)
            
            # 获取历史PE、PB数据用于估值分析
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=365*3)).strftime('%Y%m%d')
            
            hist_valuation = self.pro.daily_basic(ts_code=ts_code, start_date=start_date, end_date=end_date, fields='ts_code,trade_date,pe,pe_ttm,pb')
            latest_data['historical_valuation'] = hist_valuation.to_dict('records') if not hist_valuation.empty else []
            
            return latest_data
        except Exception as e:
            logging.error(f"获取市场数据失败 {ts_code}: {e}")
            return {}
    
    def get_top_companies_by_market_cap(self, min_listing_years: int = 20, top_n: int = 100) -> List[str]:
        """获取上市时长超过指定年限且市值排名前N的公司"""
        try:
            logging.info(f"开始筛选上市时长≥{min_listing_years}年且市值排名前{top_n}的公司")
            
            # 获取所有A股基本信息
            stock_basic = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,market,list_date')
            
            if stock_basic.empty:
                logging.error("无法获取股票基本信息")
                return []
            
            logging.info(f"获取到{len(stock_basic)}只A股基本信息")
            
            # 计算上市年限
            current_date = datetime.now()
            stock_basic['list_date'] = pd.to_datetime(stock_basic['list_date'], format='%Y%m%d', errors='coerce')
            stock_basic = stock_basic.dropna(subset=['list_date'])  # 删除无效日期
            stock_basic['listing_years'] = (current_date - stock_basic['list_date']).dt.days / 365.25
            
            # 筛选上市时长超过指定年限的公司
            qualified_stocks_df = stock_basic[stock_basic['listing_years'] >= min_listing_years]
            qualified_stocks = qualified_stocks_df['ts_code'].tolist()
            
            logging.info(f"符合上市时长≥{min_listing_years}年条件的公司：{len(qualified_stocks)}家")
            
            if not qualified_stocks:
                logging.warning(f"没有找到上市时长≥{min_listing_years}年的公司")
                return []
            
            # 获取最近交易日
            current_date_str = current_date.strftime('%Y%m%d')
            start_date_str = (current_date - timedelta(days=10)).strftime('%Y%m%d')
            
            trade_cal = self.pro.trade_cal(exchange='', start_date=start_date_str, end_date=current_date_str)
            
            if trade_cal.empty:
                logging.error("无法获取交易日历")
                return qualified_stocks[:top_n]
            
            # 获取最近的交易日
            recent_trade_dates = trade_cal[trade_cal['is_open'] == 1]['cal_date'].tolist()
            if not recent_trade_dates:
                logging.error("没有找到最近的交易日")
                return qualified_stocks[:top_n]
            
            latest_trade_date = recent_trade_dates[-1]
            logging.info(f"使用交易日期：{latest_trade_date}")
            
            # 获取市值数据
            try:
                market_data = self.pro.daily_basic(trade_date=latest_trade_date, fields='ts_code,total_mv')
                
                if market_data.empty:
                    logging.warning(f"交易日{latest_trade_date}没有市值数据")
                    return qualified_stocks[:top_n]
                
                logging.info(f"获取到{len(market_data)}条市值数据")
                
                # 筛选符合条件的股票
                qualified_market_data = market_data[market_data['ts_code'].isin(qualified_stocks)].copy()
                logging.info(f"符合上市年限条件且有市值数据的公司：{len(qualified_market_data)}家")
                
                if qualified_market_data.empty:
                    logging.warning("符合上市年限条件的公司都没有市值数据")
                    return qualified_stocks[:top_n]
                
                # 数据清理：处理total_mv列的数据类型问题
                original_count = len(qualified_market_data)
                
                # 将total_mv转换为数值类型，无法转换的设为NaN
                qualified_market_data['total_mv'] = pd.to_numeric(qualified_market_data['total_mv'], errors='coerce')
                
                # 删除total_mv为NaN或0的记录
                qualified_market_data = qualified_market_data.dropna(subset=['total_mv'])
                qualified_market_data = qualified_market_data[qualified_market_data['total_mv'] > 0]
                
                valid_count = len(qualified_market_data)
                logging.info(f"数据清理：原始{original_count}条 -> 有效{valid_count}条市值数据")
                
                if qualified_market_data.empty:
                    logging.warning("清理后没有有效的市值数据")
                    return qualified_stocks[:top_n]
                
                # 按市值排序并取前N名
                actual_top_n = min(top_n, len(qualified_market_data))
                top_companies = qualified_market_data.nlargest(actual_top_n, 'total_mv')['ts_code'].tolist()
                
                logging.info(f"成功获取市值排名前{len(top_companies)}家公司")
                
                # 输出前几名的市值信息用于调试
                top_5 = qualified_market_data.nlargest(5, 'total_mv')[['ts_code', 'total_mv']]
                logging.info(f"市值前5名：\n{top_5.to_string()}")
                
                return top_companies
                
            except Exception as e:
                logging.error(f"获取市值数据失败: {e}")
                logging.info(f"使用备选方案：返回前{min(top_n, len(qualified_stocks))}个符合上市年限的公司")
                return qualified_stocks[:top_n]
            
        except Exception as e:
            logging.error(f"获取top公司列表失败: {e}")
            import traceback
            logging.error(f"详细错误信息: {traceback.format_exc()}")
            return []
    
    def _log_data_quality(self, ts_code: str, processed_data: Dict, start_date: str, end_date: str):
        """记录数据质量信息"""
        try:
            logging.info(f"=== {ts_code} 数据质量报告 ===")
            logging.info(f"数据获取时间范围: {start_date} 到 {end_date}")
            
            for category, records in processed_data.items():
                if isinstance(records, list) and records:
                    # 筛选年报数据
                    annual_records = [r for r in records 
                                    if r.get('report_type') == '1' or 
                                    (isinstance(r.get('end_date'), str) and r.get('end_date', '').endswith('1231'))]
                    
                    if annual_records:
                        # 按时间排序
                        annual_records.sort(key=lambda x: x.get('end_date', '19700101'))
                        latest_record = annual_records[-1]
                        earliest_record = annual_records[0]
                        
                        logging.info(f"{category}: 共{len(annual_records)}条年报记录")
                        logging.info(f"  最早年报: {earliest_record.get('end_date', 'N/A')}")
                        logging.info(f"  最新年报: {latest_record.get('end_date', 'N/A')}")
                        
                        # 检查最新数据的时效性
                        latest_year = latest_record.get('end_date', '')[:4]
                        current_year = datetime.now().year
                        if latest_year and latest_year.isdigit():
                            year_diff = current_year - int(latest_year)
                            if year_diff > 1:
                                logging.warning(f"  警告: 最新{category}数据为{latest_year}年，距今{year_diff}年")
                            else:
                                logging.info(f"  数据时效性良好: 最新数据为{latest_year}年")
                    else:
                        logging.warning(f"{category}: 未找到年报数据，共{len(records)}条记录")
                else:
                    logging.warning(f"{category}: 无数据")
                    
        except Exception as e:
            logging.error(f"数据质量检查失败: {e}")