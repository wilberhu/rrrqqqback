import pandas as pd
import os
import sys
import json
import datetime

data_path=r'./tushare_data/data/hist_data'

#自动计算截止日期
def closeDate():
    df=pd.read_csv(data_path+'\\000001.SZ.csv')
    date=str(df.loc[len(df)-1]['trade_date'])
    return '-'.join([date[0:4],date[4:6],date[6:]])

#自动日期生成
def dateRange(start, end, step=1, format="%Y-%m-%d"):
    strptime, strftime=datetime.datetime.strptime, datetime.datetime.strftime
    days=(strptime(end, format)-strptime(start, format)).days
    return [strftime(strptime(start, format) + datetime.timedelta(i), format) for i in range(0, days, step)]

#自动计算某日资金
def calValues(stockNums,date,df): 
    result=[]
    for stock in stockNums:
        ans={}
        price=stockValues(stock,date,df)
        ans['name']=stock
        ans['value']=price*stockNums[stock]
        ans['share']=stockNums[stock]
        ans['close']=price
        result.append(ans)
    return result

#自动股票日期价值定位
def stockValues(code,date,df):
    try:
        date=int(date.replace('-',''))
        value=df.loc[date][code]
    except:
        value=None
    return value

#转换输入格式
def changeForm(stocks):
    temp={}
    for stock in stocks:
        temp[stock['name']]=stock['share']
    return temp

#获取交易信息，计算剩余金额
def stockTrader(date,stockNums,trades,freeCash,df):
    temp=changeForm(trades)
    tradeLog={}
    for stock in stockNums:
        if stock in temp:
            tradeLog[stock]=stockNums[stock]-temp[stock]
            temp.pop(stock)
        else:
            tradeLog[stock]=stockNums[stock]
    for stock in temp:
        tradeLog[stock]=-temp[stock]
    rest=freeCash
    #需要修改，考虑资金不足的情况
    for stock in tradeLog:
        rest+=tradeLog[stock]*stockValues(stock,date,df)
    return rest

#合并多张CSV的收盘价
def mixValue(index):
    df=pd.DataFrame()
    for ticket in index:
        temp=pd.read_csv(data_path+'\\'+ticket+'.csv',usecols=['trade_date','close'],index_col=0)
        df[ticket]=temp['close']
    return df

#主方法
def mainfunc(composition):
    '''
    freeCash金额
    buyDate生成至今日期
    stockNums股票持仓数
    
    '''
    freeCash=composition['stock']
    buyDate=[i for i in composition]
    buyDate.pop(0)
    start=buyDate[0]
    end=closeDate()
    dates=dateRange(start,end)
    index=[]
    for date in buyDate:
        for company in composition[date]:
            if company["name"] not in index:
                index.append(company["name"])
    df=mixValue(index)
    stockNums={}
    res=[]
    for date in dates:
        if date in buyDate:
            temp={}
            freeCash=stockTrader(date,stockNums,composition[date],freeCash,df)
            stockNums=changeForm(composition[date])
            temp['companies']=calValues(stockNums,date,df)
            temp['timestamp']=date
            temp['freecash']=freeCash
            res.append(temp)
        else:
            if stockValues('000001.SZ',date,df) == None:
                continue
            else:
                temp={}
                temp['companies']=calValues(stockNums,date,df)
                temp['timestamp']=date
                temp['freecash']=freeCash
                res.append(temp)
    return res

if __name__=="__main__":
    composition={'stock':10000,
             '2020-04-13':[{ 'name': '000001.SZ', 'share': 50 },{'name': '000004.SZ', 'share': 50 }],
             '2020-04-15':[{ "name": '000001.SZ', "share": 100 },{"name": '000002.SZ', "share": 50 },{ "name": '000004.SZ', "share": 25 }],
             '2020-04-20':[{ "name": '000001.SZ', "share": 75 },{"name": '000002.SZ', "share": 50 },{ "name": '000004.SZ', "share": 100 },{ "name": '000005.SZ', "share": 150 }]
            }
    result=mainfunc(composition)
    print(result)