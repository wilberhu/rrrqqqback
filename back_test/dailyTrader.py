import pandas as pd
from math import isnan
import numpy as np
import os
import json
import datetime
from decimal import *
import pymysql
from django.db import connection
from sqlalchemy import create_engine

data_path=r'./tushare_data/data/hist_data'

#自动日期生成
def dateRange(start='2010-01-04',end=datetime.datetime.now().strftime('%Y-%m-%d')):
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

#自动计算某日资金
def calValues(code,stockNums,date,df):
    price=stockValues(code,date,df)
    if code in stockNums and price!=None:
        stockFund=float(Decimal(str(price))*Decimal(str(stockNums[code])))
    else:
        stockFund=0
    return stockFund

#格式转换
def changeForm(stocks):
    temp={}
    for stock in stocks:
        temp[stock['ts_code']]=stock['share']
    return temp

#trades为[]，返回的rest为allfund，也即freecash
def stockTrader(date,stockNums,trades,freeCash,comm,df):
    temp=changeForm(trades)
    rest=freeCash
    if temp=={}:
        for stock in stockNums:
            rest+=stockNums[stock]*stockValues(stock,date,df)*(1-comm)
        return rest
    tradeLog={}
    for stock in stockNums:
        if stock in temp:
            tradeLog[stock]=stockNums[stock]-temp[stock]
            temp.pop(stock)
        else:
            tradeLog[stock]=stockNums[stock]
    for stock in temp:
        tradeLog[stock]=-int(temp[stock])
    #需要修改，考虑资金不足的情况
    for stock in tradeLog:
        #rest+=tradeLog[stock]*stockValues(stock,date,df)-abs(tradeLog[stock])*stockValues(stock,date,df)*comm
        rest+=(tradeLog[stock]-abs(tradeLog[stock])*comm)*stockValues(stock,date,df)
    return rest

#合并多张CSV的开盘价，提取日线数据
def mixValue(index):
    df=pd.DataFrame()
    for ticket in index:
        temp=pd.read_csv(data_path+'/'+ticket+'.csv',usecols=['trade_date','open'],index_col=0)
        df[ticket]=temp['open']
    return df

#自动股票日期价值定位
def stockValues(code,date,df):
    try:
        date=int(date.replace('-',''))
        value=df.loc[date][code]
        if isnan(value):
            dates=list(df.index)
            index=dates.index(date)
            values=list(df[code])
            for i in range(index,-1,-1):
                if not isnan(values[i]):
                    value=values[i]
                    break
    except:
        value=None
    return value

def emptyValue(stock,end):
    res=[]
    free=stock
    dateList=dateRange('2010-01-03',end)
    n=len(dateList)
    return {
        'timestamp':dateList,
        'codeList':['allfund','freecash'],
        'data':[[free]*n,[free]*n]
    }

def mainfunc(composition):
    
    freeCash=composition['allfund']
    comm=composition['commission']
    tradeDate=[i for i in composition]
    tradeDate.pop(0)
    tradeDate.pop(0)
    tradeDate.sort()
    
    end=datetime.datetime.now().strftime('%Y-%m-%d')
    if tradeDate==[]:
        return emptyValue(freeCash,end)
    start=tradeDate[0]
    dates=dateRange(start,end)
    
    codeList=[]
    for date in tradeDate:
        for company in composition[date]:
            if company["ts_code"] not in codeList:
                codeList.append(company["ts_code"])
    df=mixValue(codeList)
    
    stockNums={}
    data=[[] for i in range(len(codeList))]
    data_freecash=[]
    data_allfund=[]
    
    for date in dates:
        if date in tradeDate:
            #print(stockNums)
            freeCash=stockTrader(date,stockNums,composition[date],freeCash,comm,df)
            stockNums=changeForm(composition[date])
        ans=0
        for index, item in enumerate(codeList):
            stockFund = calValues(item,stockNums,date,df)
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



if __name__=="__main__":
    composition={'stock':100000,
		     'commission':0.001,
		     '2019-03-11': [{'ts_code': '000002.SZ', 'share': 300}],
		     '2019-03-18': [],
		     '2019-03-25': [{'ts_code': '000001.SZ', 'share': 700}],
		     '2019-03-26': [{'ts_code': '000001.SZ', 'share': 700},
		      {'ts_code': '000002.SZ', 'share': 300}],
		     '2019-03-28': [{'ts_code': '000001.SZ', 'share': 700}],
		     '2019-04-01': [],
		     '2019-04-19': [{'ts_code': '000002.SZ', 'share': 200}],
		     '2019-04-22': [],
		     '2019-04-23': [{'ts_code': '000002.SZ', 'share': 300}],
		     '2019-04-24': [{'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-04-25': [{'ts_code': '000002.SZ', 'share': 300}],
		     '2019-04-29': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000002.SZ', 'share': 300}],
		     '2019-04-30': [{'ts_code': '000002.SZ', 'share': 300}],
		     '2019-05-06': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000002.SZ', 'share': 300}],
		     '2019-05-14': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-05-28': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000002.SZ', 'share': 300}],
		     '2019-05-31': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-06-04': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000002.SZ', 'share': 300}],
		     '2019-06-05': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-06-11': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-06-13': [],
		     '2019-06-18': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-06-24': [],
		     '2019-07-01': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-07-02': [],
		     '2019-07-04': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-07-18': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-07-22': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-07-24': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-07-25': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-07-30': [{'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-07-31': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-08-01': [{'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-08-05': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-08-09': [{'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-08-16': [{'ts_code': '000002.SZ', 'share': 300}],
		     '2019-08-23': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000002.SZ', 'share': 300}],
		     '2019-08-26': [{'ts_code': '000002.SZ', 'share': 300}],
		     '2019-08-27': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000002.SZ', 'share': 300}],
		     '2019-09-06': [],
		     '2019-09-09': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-09-10': [],
		     '2019-09-11': [{'ts_code': '000001.SZ', 'share': 600}],
		     '2019-09-12': [],
		     '2019-09-16': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-09-17': [{'ts_code': '000001.SZ', 'share': 600}],
		     '2019-09-19': [{'ts_code': '000001.SZ', 'share': 600},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-09-20': [],
		     '2019-09-24': [{'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-10-10': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-10-11': [{'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-10-14': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-10-25': [{'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-10-28': [{'ts_code': '000004.SZ', 'share': 400}],
		     '2019-10-30': [{'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-10-31': [{'ts_code': '000001.SZ', 'share': 500},
		      {'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-11-04': [{'ts_code': '000002.SZ', 'share': 300}],
		     '2019-11-11': [{'ts_code': '000001.SZ', 'share': 500},
		      {'ts_code': '000002.SZ', 'share': 300}],
		     '2019-11-12': [{'ts_code': '000001.SZ', 'share': 500},
		      {'ts_code': '000002.SZ', 'share': 300},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-11-20': [{'ts_code': '000001.SZ', 'share': 500}],
		     '2019-11-25': [{'ts_code': '000001.SZ', 'share': 500},
		      {'ts_code': '000004.SZ', 'share': 400}],
		     '2019-11-29': [{'ts_code': '000001.SZ', 'share': 500}],
		     '2019-12-16': []
		    }
    result=mainfunc(composition)
    print(result)