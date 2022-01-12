# coding: utf-8
# author: Wenbo Shi

import requests
import pandas as pd
import time
import datetime
import json
import sys
from PIL import Image
import io
import matplotlib.pyplot as plt

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
    

def get_json(url):
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(url)
    json_elements = browser.find_elements_by_tag_name('pre')

    json_file = json_elements[0].text
    json_file = json.loads(json_file)
    return json_file


def createTable(coin, table=True):
    url = "https://web-api.coinmarketcap.com/v1/cryptocurrency/ohlcv/historical?convert=USD&slug={}&time_end={}&time_start=1367107200".format(coin, str(int(time.time())))

    print(url)
    js = get_json(url)

    name = js.get("data").get("name")
    symbol = js.get("data").get("symbol")

    print("正在查看 {} 代号 {} 的历史数据".format(name, symbol))

    date = []
    open_ = []
    high = []
    low = []
    close = []
    volume = []
    market_cap = []

    for i in js.get("data").get("quotes"):
        tm = i["time_open"]
        tm = tm[:tm.find("T")]
        date.append(tm)
        open_.append(i["quote"]["USD"]["open"])
        high.append(i["quote"]["USD"]["high"])
        low.append(i["quote"]["USD"]["low"])
        close.append(i["quote"]["USD"]["close"])
        volume.append(i["quote"]["USD"]["volume"])
        market_cap.append(i["quote"]["USD"]["market_cap"])

    data_d = {
        "Date": date, "Open": open_, "High": high, "Low": low, "Close": close, "Volume": volume, "Market Cap": market_cap
    }

    data = pd.DataFrame(data_d)

    if table:
        data.to_excel(r"{}_price_info.xlsx".format(coin),index=0)
        print("已将 {} 的历史数据导出至路径：{}_price_info.xlsx，共找到 {} 条数据".format(name, coin, str(len(date))))
        json_file = open(r"{}_price_info.json".format(coin), 'w')
        json_file.write(json.dumps(data_d))
        json_file.close()
        print("已将 {} 的历史数据导出至路径：{}_price_info.json，共找到 {} 条数据".format(name, coin, str(len(date))))

    return data


def create_graph(grapg=True):
    # bitcoin_market_info = createTable("bitcoin", False)

    f = open('bitcoin_price_info.json', 'r')
    content = f.read()
    bitcoin_market_info = json.loads(content)
    bitcoin_market_info = pd.DataFrame(bitcoin_market_info)
    f.close()

    f = open('ethereum_price_info.json', 'r')
    content = f.read()
    eth_market_info = json.loads(content)
    eth_market_info = pd.DataFrame(eth_market_info)
    f.close()
     


    bt_img = requests.get("https://gimg2.baidu.com/image_search/src=http%3A%2F%2Fpic.51yuansu.com%2Fpic3%2Fcover%2F02%2F32%2F51%2F59c0db6901095_610.jpg&refer=http%3A%2F%2Fpic.51yuansu.com&app=2002&size=f9999,10000&q=a80&n=0&g=0n&fmt=jpeg?sec=1644564673&t=61978fbd68a86a5710ce99140845634b")
    eth_img = requests.get("https://img1.baidu.com/it/u=4197939871,3401685042&fm=253&fmt=auto&app=138&f=PNG?w=500&h=500")

    image_file = io.BytesIO(bt_img.content)
    bitcoin_im = Image.open(image_file)

    image_file = io.BytesIO(eth_img.content)
    eth_im = Image.open(image_file)
    width_eth_im , height_eth_im  = eth_im.size
    eth_im = eth_im.resize((int(eth_im.size[0]*0.8), int(eth_im.size[1]*0.8)), Image.ANTIALIAS)

    bitcoin_market_info.columns =[bitcoin_market_info.columns[0]]+['bt_'+i for i in bitcoin_market_info.columns[1:]]
    eth_market_info.columns =[eth_market_info.columns[0]]+['eth_'+i for i in eth_market_info.columns[1:]]

    if grapg:
        fig, (ax1, ax2) = plt.subplots(2,1, gridspec_kw = {'height_ratios':[3, 1]})
        ax1.set_ylabel('Closing Price ($)',fontsize=12)
        ax2.set_ylabel('Volume ($ bn)',fontsize=12)
        ax2.set_yticks([int('%d000000000'%i) for i in range(20)])
        ax2.set_yticklabels(range(20))
        ax1.set_xticks([datetime.date(i,j,1) for i in range(2013,2023) for j in [1,11]])
        ax1.set_xticklabels('')
        ax2.set_xticks([datetime.date(i,j,1) for i in range(2013,2023) for j in [1,11]])
        ax2.set_xticklabels([datetime.date(i,j,1).strftime('%b %Y')  for i in range(2013,2023) for j in [1,11]])
        ax1.plot(bitcoin_market_info['Date'],bitcoin_market_info['bt_Open'])
        ax2.bar(bitcoin_market_info['Date'], bitcoin_market_info['bt_Volume'])
        fig.tight_layout()
        fig.figimage(bitcoin_im, 100, 120, zorder=3,alpha=.5)
        plt.show()


        fig, (ax1, ax2) = plt.subplots(2,1, gridspec_kw = {'height_ratios':[3, 1]})
        #ax1.set_yscale('log')
        ax1.set_ylabel('Closing Price ($)',fontsize=12)
        ax2.set_ylabel('Volume ($ bn)',fontsize=12)
        ax2.set_yticks([int('%d000000000'%i) for i in range(20)])
        ax2.set_yticklabels(range(20))
        ax1.set_xticks([datetime.date(i,j,1) for i in range(2013,2023) for j in [1,11]])
        ax1.set_xticklabels('')
        ax2.set_xticks([datetime.date(i,j,1) for i in range(2013,2023) for j in [1,11]])
        ax2.set_xticklabels([datetime.date(i,j,1).strftime('%b %Y')  for i in range(2013,2023) for j in [1,11]])
        ax1.plot(eth_market_info['Date'], eth_market_info['eth_Open'])
        ax2.bar(eth_market_info['Date'], eth_market_info['eth_Volume'])
        fig.tight_layout()
        fig.figimage(eth_im, 300, 180, zorder=3, alpha=.6)
        plt.show()


    market_info = pd.merge(bitcoin_market_info, eth_market_info, on=['Date'])
    market_info = market_info[market_info['Date']>='2021-01-01']
    for coins in ['bt_', 'eth_']: 
        kwargs = { coins+'day_diff': lambda x: (x[coins+'Close']-x[coins+'Open'])/x[coins+'Open']}
        market_info = market_info.assign(**kwargs)
    market_info.head()
    print(market_info)




if __name__ == "__main__":


    # createTable("bitcoin")
    # createTable("ethereum")

    create_graph(False)

