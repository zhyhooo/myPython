import akshare as ak
import pandas as pd
import numpy as np



def get_allfund_info():
    fund_info = ak.fund_name_em()
    print(fund_info.info())
    print(fund_info)
    fund_info.to_csv("fund_info.csv")


def find_fund():
    days = 30
    fund_info = ak.fund_name_em()
    fund_info = fund_info[fund_info['基金简称'].str.contains('科创')]
    for code in fund_info['基金代码']:
        try:
            fund_cumulative_nav = ak.fund_open_fund_info_em(symbol=code, indicator="累计净值走势")
            fund_cumulative_nav_test = fund_cumulative_nav[-days * 3:-days * 3 + 1]

            if not fund_cumulative_nav_test.empty:  # 3月前的记录需要存在
                fund_name = fund_info[fund_info['基金代码'] == code]['基金简称'].values[0]
                # 计算最近3月的收益率
                fund_cumulative_nav3 = fund_cumulative_nav[-days * 3:]
                cumulative_nav_returns3 = fund_cumulative_nav3.iloc[-1]['累计净值'] / fund_cumulative_nav3.iloc[0]['累计净值'] - 1
                # 计算最近2月的收益率
                fund_cumulative_nav2 = fund_cumulative_nav[-days * 2:]
                cumulative_nav_returns2 = fund_cumulative_nav2.iloc[-1]['累计净值'] / fund_cumulative_nav2.iloc[0]['累计净值'] - 1
                # 计算最近1月的收益率
                fund_cumulative_nav1 = fund_cumulative_nav[-days * 1:]
                cumulative_nav_returns1 = fund_cumulative_nav1.iloc[-1]['累计净值'] / fund_cumulative_nav1.iloc[0]['累计净值'] - 1
              
                print(f"{fund_name}({code}): 近3月收益率：{cumulative_nav_returns3:.2%}, {cumulative_nav_returns2:.2%}, {cumulative_nav_returns1:.2%}")
        except :
            print(f"{code} 基金信息获取失败")



if __name__ == '__main__':
    find_fund()
    print("OK")
