import pandas as pd
import datetime
from decimal import *
from django.db import connection
data_path = r'./tushare_data/data/hist_data'

# 自动日期生成
def dateRange(start,end):
    start=start.replace('-','')
    end=end.replace('-','')
    sql="SELECT cal_date FROM trade_cal WHERE cal_date>="+start+" AND cal_date<="+end+" AND is_open=1" 

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有
    df = pd.DataFrame(rows, columns=['cal_date'])
    cursor.close()

    result=list(map(lambda x:x[:4]+'-'+x[4:6]+'-'+x[6:],list(df['cal_date'])))
    return result


# 自动计算某日资金
def calValues(code, stockNums, date, df):
    price = stockValues(code, date, df)
    if code in stockNums and price != None:
        stockFund = float(Decimal(str(price)) * Decimal(str(stockNums[code])))
    else:
        stockFund = 0
    return stockFund


# 自动股票日期价值定位
def stockValues(code, date, df):
    try:
        date = int(date.replace('-', ''))
        value = df.loc[date][code]
    except:
        value = None
    return value


# 格式转换
def changeForm(stocks):
    temp = {}
    for stock in stocks:
        temp[stock['ts_code']] = stock['share']
    return temp


# 获取交易信息，计算剩余金额
def stockTrader(date, stockNums, trades, freeCash, df):
    temp = changeForm(trades)
    tradeLog = {}
    for stock in stockNums:
        if stock in temp:
            tradeLog[stock] = int(stockNums[stock]) - int(temp[stock])
            temp.pop(stock)
        else:
            tradeLog[stock] = int(stockNums[stock])
    for stock in temp:
        tradeLog[stock] = -int(temp[stock])
    rest = freeCash
    # 需要修改，考虑资金不足的情况
    for stock in tradeLog:
        rest += tradeLog[stock] * stockValues(stock, date, df)
    return rest


# 合并多张CSV的收盘价
def mixValue(index):
    df = pd.DataFrame()
    for ticket in index:
        temp = pd.read_csv(data_path + '/' + ticket + '.csv', usecols=['trade_date', 'close'], index_col=0)
        df[ticket] = temp['close']
    return df


# 处理activities空值
def emptyValue(stock, end):
    res = []
    free = stock
    dateList = dateRange('2010-01-03', end)
    n = len(dateList)
    return {
        'timestamp': dateList,
        'codeList': ['allfund', 'freecash'],
        'data': [[free] * n, [free] * n]
    }


# 主方法
def mainfunc(composition):
    freeCash = composition['stock']
    buyDate = [i for i in composition]
    buyDate.pop(0)
    buyDate.sort()

    end = datetime.datetime.now().strftime('%Y-%m-%d')
    if buyDate == []:
        return emptyValue(freeCash, end)
    start = buyDate[0]
    dates = dateRange(start, end)

    codeList = []
    for date in buyDate:
        for company in composition[date]:
            if company["ts_code"] not in codeList:
                codeList.append(company["ts_code"])
    df = mixValue(codeList)

    stockNums = {}
    data = [[] for i in range(len(codeList))]
    data_freecash = []
    data_allfund = []

    for date in dates:
        if date in buyDate:
            freeCash = stockTrader(date, stockNums, composition[date], freeCash, df)
            stockNums = changeForm(composition[date])
        ans = 0
        for index, item in enumerate(codeList):
            stockFund = calValues(item, stockNums, date, df)
            ans += stockFund if stockFund != None else 0
            data[index].append(stockFund)
        data_freecash.append(freeCash)
        data_allfund.append(freeCash + ans)
    codeList.insert(0, "freecash")
    data.insert(0, data_freecash)
    codeList.insert(0, "allfund")
    data.insert(0, data_allfund)
    return {
        'timestamp': dates,
        'codeList': codeList,
        'data': data
    }
