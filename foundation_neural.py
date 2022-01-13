import numpy as np
import pandas as pd
import csv
from keras.models import Sequential
from keras.layers import Dense
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif']='SimHei'
plt.rcParams['axes.unicode_minus']=False

batch_size = 16
epochs = 100
look_back = 5 #窗口天数
showdays = 60 #最后画图观察的天数，必须大于look_back（小于窗口天数无法预测）

X_train = []
y_train = []
X_validation = []
y_validation = []
testset = [] #用来保存测试基金的近期净值
test_mean = [] #用来保存测试基金的近期净值的look_back日均线
y_mean = [] #用来保存测试基金近期涨跌幅的look_back日均线

def create_dataset(dataset):
    dataX, dataY = [], []
    print('len of dataset: {}'.format(len(dataset)))
    for i in range(len(dataset) - look_back):
        x = dataset[i: i + look_back]
        dataX.append(x)
        y = dataset[i + look_back]
        dataY.append(y)
    return np.array(dataX), np.array(dataY)

def build_model():
    model = Sequential()
    model.add(Dense(units=32, input_dim=look_back, activation='relu'))
    model.add(Dense(units=8, activation='relu'))
    model.add(Dense(units=1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    return model

# 导入数据
with open(fileTrain) as f:
    row = csv.reader(f, delimiter=',')
    for r in row:
        dataset = []
        r = [x for x in r if x != 'None']
        days = len(r) - 1
        #有效天数小于窗口天数，忽略
        if days <= look_back:
            continue
        for i in range(days):
            f2 = float(r[days - i])
            f1 = float(r[days - i -1])
            if f1 == 0 or f2 ==0:
                dataset = []
                break
            #把数据放大100倍，相当于以百分比为单位
            f1 = (f1 - f2) / f2 * 100
            if f1 > 10 or f1 < -10:
                dataset = []
                break
            dataset.append(f1)
        if len(dataset) > look_back:
            X_1, y_1 = create_dataset(dataset)
            X_train = np.append(X_train, X_1)
            y_train = np.append(y_train, y_1)

with open(fileTest) as f:
    row = csv.reader(f, delimiter=',')
    #写成了循环，但实际只有1条验证数据
    for r in row:
        dataset = []
        #去掉记录为None的数据（当天数据缺失）
        r = [x for x in r if x != 'None']
        #只需要最后画图观察天数的数据
        if len(r) > showdays + 1:
            r = r[:showdays + 1]
        days = len(r) - 1
        #有效天数小于窗口天数，忽略
        if days <= look_back:
            continue
        for i in range(days):
            f2 = float(r[days - i])
            f1 = float(r[days - i -1])
            if f1 == 0 or f2 ==0:
                dataset = []
                break
            #把数据放大100倍，相当于以百分比为单位
            f1 = (f1 - f2) / f2 * 100
            if f1 > 10 or f1 < -10:
                dataset = []
                break
            dataset.append(f1)
            testset.append(f2)
        #保存look_back日均线，以备之后画图所用
        y_mean = pd.Series(dataset).rolling(window=look_back).mean()
        #预测明天，需先假定明天涨跌为0，增加入dataset
        dataset.append(0)
        f2=float(r[0])
        testset.append(f2)
        #保存look_back日均线，以备之后画图所用
        test_mean = pd.Series(testset).rolling(window=look_back).mean()
        if len(dataset) > look_back:
            X_validation, y_validation = create_dataset(dataset)

#之前append改变了维数，需要重新改回窗口大小
X_train = X_train.reshape(-1, look_back)

print('num of X_train: {}\tnum of y_train: {}'.format(len(X_train), len(y_train)))
print('num of X_validation: {}\tnum of y_validation: {}'.format(len(X_validation), len(y_validation)))

# 训练模型
model = build_model()
model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1, validation_split=0.2, shuffle=True)

# 评估模型
train_score = model.evaluate(X_train, y_train, verbose=0)
print('Train Set Score: %.2f' % (train_score))
validation_score = model.evaluate(X_validation, y_validation, verbose=0)
print('Test Set Score: %.2f' % (validation_score))

#设置测试集明天数值为NAN
testset.append(np.nan)
testset = np.array(testset).reshape(-1, 1)

#将之前假定的明天涨跌由0改为NAN
y_validation[showdays-look_back] = np.nan
y_validation = np.array(y_validation).reshape(-1, 1)

#去掉前(look_back-1)个NAN，注意这是预测均线（实际均线右移1天）
y_mean = y_mean[look_back-1:]
y_mean = np.array(y_mean).reshape(-1, 1)

# 图表查看预测趋势
predict_validation = model.predict(X_validation)

# 图表显示
fig=plt.figure(figsize=(15,6))
plt.plot(y_validation, color='blue', label='基金每日涨幅')
plt.plot(y_mean, color='yellow', label='之前日均涨幅')
plt.plot(predict_validation, color='red', label='预测每日涨幅')
plt.legend(loc='upper left')
plt.show()