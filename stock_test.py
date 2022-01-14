
import akshare as ak
import requests
import pandas as pd

# 接口教程：https://cloud.tencent.com/developer/article/1866258

fund_em_open_fund_daily_df = ak.fund_em_open_fund_daily()
fund_em_open_fund_daily_df.to_csv("基金数据.csv", index=0, encoding='utf-8_sig')