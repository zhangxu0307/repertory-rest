#encoding=utf-8
import sklearn as sk
import numpy as np
from sklearn.svm import SVR
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error,mean_squared_error
import pandas as pd


def create_dataset(dataset, look_back=1, forehead=1): # 分割数据
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-forehead-1):
        a = dataset[i:(i+look_back)]
        b = dataset[(i+look_back):(i+look_back+forehead)]
        dataX.append(a)
        dataY.append(b)
    return np.array(dataX), np.array(dataY)


def forecasting(data,look_back,foreNum): # AR模型时间序列预测

    X, Y = create_dataset(data, look_back=look_back, forehead=foreNum)

    clf = LinearRegression()
    clf.fit(X, Y)
    return clf.predict(X[-1,:]).tolist() # 利用最后一组数据向前预测


def evaluate(dataset, look_back, foreNum): # 多步预测直接估计误差

    trainData = dataset[:-foreNum]
    testY = dataset[-foreNum:]
    ans = forecasting(trainData, look_back, foreNum)
    ans = np.array(ans).transpose(1, 0)

    error = (testY- ans[:, 0])
    accList = (1.0 - np.abs(error / testY)) * 100
    accMean = round(np.mean(np.abs(accList)), 4)

    # emp = np.empty((trainData.shape[0], 1))
    # emp[:] = np.nan
    # ans = np.vstack((emp, ans))
    # plt.plot(dataset, 'r')
    # plt.plot(ans, 'b')
    # plt.show()

    return testY, ans.flatten().tolist(), accList.tolist(), accMean


def evaluate_onestep(dataset,look_back,foreNum): # 单步预测估计误差

    dataX, dataY = [], []
    for i in range(len(dataset) - look_back):
        a = dataset[i:(i + look_back)]
        dataX.append(a)
        dataY.append(dataset[i + look_back])
    dataX = np.array(dataX)
    dataY = np.array(dataY)

    trainNum = len(dataX)-foreNum
    trainX = dataX[:trainNum]
    trainY = dataY[:trainNum]
    testX = dataX[trainNum:]
    testY = dataY[trainNum:]

    clf = LinearRegression()
    #clf = MLPRegressor()
    clf.fit(trainX,trainY)
    ans = clf.predict(testX)
    accList = (1.0-np.abs((testY- ans) / testY))*100
    accMean = round(np.mean(np.abs(accList)), 4)

    # plt.plot(testY, 'r')
    # plt.plot(ans, 'b')
    # plt.show()

    return testY, ans.tolist(),accList.tolist(), accMean


if __name__ == "__main__":

    df = pd.read_csv('./data/true_data.csv', encoding='utf-8', index_col='date',skip_footer=0)
    d = df.to_dict()
    #print d['x']
    df.index = pd.to_datetime(df.index)
    #dataDcit = castingData(df)
    #print dataDcit
    dataset1 = df['x'].values
    dataset1 = dataset1.astype('float32')
    evalans,accList,accMean = evaluate_onestep(dataset1, 6, 6)
    print (evalans)
    print (accList)
    print (accMean)

    evalans, accList, accMean = evaluate(dataset1, 6, 6)
    print (evalans)
    print (accList)
    print (accMean)

    ans = forecasting(dataset1, 6, 6)
    print (ans[0])







