import requests
import time
import execjs


# https://blog.csdn.net/fanmin2000/article/details/112836715


fileTrain = './data/accTrain.csv'
jjTrain = ['004609', '004853', '005524', '005824', '007749']
fileTest = './data/accTest.csv'
jjTest = '007669'

def getUrl(fscode):
    head = 'http://fund.eastmoney.com/pingzhongdata/'
    tail = '.js?v='+ time.strftime("%Y%m%d%H%M%S",time.localtime())
    print(head+fscode+tail)
    return head+fscode+tail

# 根据基金代码获取净值
def getWorth(fscode):
    content = requests.get(getUrl(fscode))
    jsContent = execjs.compile(content.text)
    #单位净值走势
    netWorthTrend = jsContent.eval('Data_netWorthTrend')
    #累计净值走势
    ACWorthTrend = jsContent.eval('Data_ACWorthTrend')
    netWorth = []
    ACWorth = []
    for dayWorth in netWorthTrend[::-1]:
        netWorth.append(dayWorth['y'])
    for dayACWorth in ACWorthTrend[::-1]:
        ACWorth.append(dayACWorth[1])
    return netWorth, ACWorth

ACWorthFile = open(fileTrain, 'w')
for code in jjTrain:
    try:
        _, ACWorth = getWorth(code)
    except:
        continue    
    if len(ACWorth) > 0:
        ACWorthFile.write(",".join(list(map(str, ACWorth))))
        ACWorthFile.write("\n")
        print('{} data downloaded'.format(code))
ACWorthFile.close()

ACWorthTestFile = open(fileTest, 'w')
_, ACWorth = getWorth(jjTest)
if len(ACWorth) > 0:
    ACWorthTestFile.write(",".join(list(map(str, ACWorth))))
    ACWorthTestFile.write("\n")
    print('{} data downloaded'.format(jjTest))
ACWorthTestFile.close()

