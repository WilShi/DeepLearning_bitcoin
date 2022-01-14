# coding: utf-8
# author: Wenbo Shi

import requests
import pandas as pd
import time
import datetime
import json
import sys, re, os
from PIL import Image
import io
import matplotlib.pyplot as plt

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


# https://github.com/dashee87/blogScripts/blob/master/Jupyter/2017-11-20-predicting-cryptocurrency-prices-with-deep-learning.ipynb
    

def get_json(url):
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.get(url)
    json_elements = browser.find_elements_by_tag_name('pre')

    json_file = json_elements[0].text
    json_file = json.loads(json_file)
    return json_file


def mkdir(path):
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)
        print("#"*50)
        print("建立新的文件路径于: {}".format(path))
        print("#"*50)


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
        # date.append(i["time_open"])
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
        mkdir("ft_data")
        data.to_excel(r"ft_data/{}_price_info.xlsx".format(coin),index=0)
        print("已将 {} 的历史数据导出至路径：ft_data/{}_price_info.xlsx，共找到 {} 条数据".format(name, coin, str(len(date))))
        json_file = open(r"ft_data/{}_price_info.json".format(coin), 'w')
        json_file.write(json.dumps(data_d))
        json_file.close()
        print("已将 {} 的历史数据导出至路径：ft_data/{}_price_info.json，共找到 {} 条数据".format(name, coin, str(len(date))))

    return data


def create_graph(bitcoin_market_info, eth_market_info, bitcoin_im, eth_im):
        
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


def run(graph=True):
    # bitcoin_market_info = createTable("bitcoin", False)

    f = open('ft_data/bitcoin_price_info.json', 'r')
    content = f.read()
    bitcoin_market_info = json.loads(content)
    bitcoin_market_info = pd.DataFrame(bitcoin_market_info)
    # bitcoin_market_info = bitcoin_market_info.assign(Date=pd.to_datetime(bitcoin_market_info['Date']))
    f.close()

    f = open('ft_data/ethereum_price_info.json', 'r')
    content = f.read()
    eth_market_info = json.loads(content)
    eth_market_info = pd.DataFrame(eth_market_info)
    # eth_market_info = eth_market_info.assign(Date=pd.to_datetime(eth_market_info['Date']))
    f.close()

    bitcoin_market_info.columns =[bitcoin_market_info.columns[0]]+['bt_'+i for i in bitcoin_market_info.columns[1:]]
    eth_market_info.columns =[eth_market_info.columns[0]]+['eth_'+i for i in eth_market_info.columns[1:]]

    bt_img = requests.get("https://img2.baidu.com/it/u=3702439010,734927277&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=442")
    eth_img = requests.get("https://img1.baidu.com/it/u=4197939871,3401685042&fm=253&fmt=auto&app=138&f=PNG?w=500&h=500")

    image_file = io.BytesIO(bt_img.content)
    bitcoin_im = Image.open(image_file)

    image_file = io.BytesIO(eth_img.content)
    eth_im = Image.open(image_file)
    width_eth_im , height_eth_im  = eth_im.size
    eth_im = eth_im.resize((int(eth_im.size[0]*0.8), int(eth_im.size[1]*0.8)), Image.ANTIALIAS)
     
    if graph:
        create_graph(bitcoin_market_info, eth_market_info, bitcoin_im, eth_im)


    market_info = pd.merge(bitcoin_market_info, eth_market_info, on=['Date'])
    market_info = market_info[market_info['Date']>='2021-01-01']
    for coins in ['bt_', 'eth_']: 
        kwargs = { coins+'day_diff': lambda x: (x[coins+'Close']-x[coins+'Open'])/x[coins+'Open']}
        market_info = market_info.assign(**kwargs)
    market_info.head()

    # print(market_info)
    # print(market_info['Date'])


    split_date = '2021-06-01'

    fig, (ax1, ax2) = plt.subplots(2,1)
    ax1.set_xticks([datetime.date(i,j,1) for i in range(2013,2023) for j in [1,11]])
    ax1.set_xticklabels('')
    ax2.set_xticks([datetime.date(i,j,1) for i in range(2013,2023) for j in [1,11]])
    ax2.set_xticklabels([datetime.date(i,j,1).strftime('%b %Y')  for i in range(2013,2023) for j in [1,11]])
    ax1.plot(market_info[market_info['Date'] < split_date]['Date'],
            market_info[market_info['Date'] < split_date]['bt_Close'], 
            color='#B08FC7', label='Training')
    ax1.plot(market_info[market_info['Date'] >= split_date]['Date'],
            market_info[market_info['Date'] >= split_date]['bt_Close'], 
            color='#8FBAC8', label='Test')
    ax2.plot(market_info[market_info['Date'] < split_date]['Date'],
            market_info[market_info['Date'] < split_date]['eth_Close'], 
            color='#B08FC7')
    ax2.plot(market_info[market_info['Date'] >= split_date]['Date'],
            market_info[market_info['Date'] >= split_date]['eth_Close'], color='#8FBAC8')
    ax1.set_xticklabels('')
    ax1.set_ylabel('Bitcoin Price ($)',fontsize=12)
    ax2.set_ylabel('Ethereum Price ($)',fontsize=12)
    plt.tight_layout()
    ax1.legend(bbox_to_anchor=(0.03, 1), loc=2, borderaxespad=0., prop={'size': 14})
    fig.figimage(bitcoin_im.resize((int(bitcoin_im.size[0]*0.65), int(bitcoin_im.size[1]*0.65)), Image.ANTIALIAS), 
                200, 260, zorder=3,alpha=.5)
    fig.figimage(eth_im.resize((int(eth_im.size[0]*0.65), int(eth_im.size[1]*0.65)), Image.ANTIALIAS), 
                350, 40, zorder=3,alpha=.5)
    plt.show()


    fig, (ax1, ax2) = plt.subplots(2,1)
    ax1.set_xticks([datetime.date(2021,i+1,1) for i in range(12)])
    ax1.set_xticklabels('')
    ax2.set_xticks([datetime.date(2021,i+1,1) for i in range(12)])
    ax2.set_xticklabels([datetime.date(2021,i+1,1).strftime('%b %d %Y')  for i in range(12)])
    ax1.plot(market_info[market_info['Date']>= split_date]['Date'],
            market_info[market_info['Date']>= split_date]['bt_Close'].values, label='Actual')

    ax1.plot(market_info[market_info['Date']>= split_date]['Date'],
            market_info[market_info['Date']>= '2021-05-31']['bt_Close'][1:].values, label='Predicted')

    ax1.set_ylabel('Bitcoin Price ($)',fontsize=12)
    ax1.legend(bbox_to_anchor=(0.1, 1), loc=2, borderaxespad=0., prop={'size': 14})
    ax1.set_title('Simple Lag Model (Test Set)')
    ax2.set_ylabel('Etherum Price ($)',fontsize=12)
    ax2.plot(market_info[market_info['Date']>= split_date]['Date'],
            market_info[market_info['Date']>= split_date]['eth_Close'].values, label='Actual')

    ax2.plot(market_info[market_info['Date']>= split_date]['Date'],
            market_info[market_info['Date']>= '2021-05-31']['eth_Close'][1:].values, label='Predicted')

    fig.tight_layout()
    plt.show()


if __name__ == "__main__":


    createTable("bitcoin")
    createTable("ethereum")

    run(graph=False)

