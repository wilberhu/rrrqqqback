import datetime
#import pymysql
import pandas as pd

import backtrader as bt
#import backtrader.feeds as btfeeds
#import backtrader.indicators as btind
#import backtrader.analyzers as btanalyzers

from sqlalchemy import create_engine
from sqlalchemy.types import CHAR,INT
from sqlalchemy.orm import sessionmaker
import time

con_info='mysql+pymysql://root:87654321@localhost:3306/stock_api?charset=utf8'
test_engine = create_engine(con_info) #use sqlalchemy to build link-engine

def get_data(start,end,code):
    sql = "select * from hist_data where ts_code = '"+code+ "' and trade_date >= '"+start+ "' and trade_date<= '"+end+"';"
    df = pd.read_sql(sql,test_engine)
    data = df[['trade_date','open','high','low','close','vol']]
    data=data.rename(columns={'vol':'volume'})
    data=data.set_index('trade_date')
    data['openinterest']=0
    data['datetime']=data.index
    data=data[['datetime','open','high','low','close','volume','openinterest']]
    return data

def calShare(data):
    ans = 0
    for i in data:
        ans += i['share']
    return ans

def outFormat(result_g):
    flag = 0
    result = {}
    tmp = {}
    for data in result_g:
        if calShare(result_g[data]) != 0 and flag == 0:
            result[data] = result_g[data]
            tmp = result_g[data]
            flag = 1
        elif calShare(result_g[data]) != 0 and flag == 1:
            if result_g[data] != tmp:
                result[data] = result_g[data]
                tmp = result_g[data]
        elif calShare(result_g[data]) == 0 and flag == 1:
            if result_g[data] != tmp:
                result[data] = result_g[data]
                tmp = result_g[data]
    return result

def mainfunc(strategy_import, strategy,ts_code_list,startTime='2010-01-04',endTime=datetime.datetime.now().strftime('%Y-%m-%d'),allfund=100000,commission=0):
    print(strategy_import)
    print(strategy)
    print(ts_code_list)
    print(startTime.replace("-", ""))
    print(endTime.replace("-", ""))
    print(allfund)
    print(commission)

    exec(strategy_import)

    global result_g
    result_g={}


    cerebro=bt.Cerebro()
    for code in ts_code_list:
        feed = bt.feeds.PandasData(dataname = get_data(startTime.replace("-", ""),endTime.replace("-", ""),code))
        cerebro.adddata(feed, name = code)
    startcash=allfund
    cerebro.broker.setcash(startcash)
    cerebro.broker.setcommission(commission=commission)
    cerebro.addstrategy(eval(strategy))
    cerebro.run()
    portvalue=cerebro.broker.getvalue()
    pnl=portvalue-startcash
    print(f'总资金: {round(portvalue,2)}')
    print(f'净收益: {round(pnl,2)}')

    return outFormat(result_g)

