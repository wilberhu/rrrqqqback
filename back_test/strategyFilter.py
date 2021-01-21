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
    ans={}
    tmp=[]
    result={"activities":[]}
    for date in result_g:
        res={}
        tradeData=[i for i in result_g[date] if i['share']!=0]
        if tradeData!=[]:
            if tradeData!=tmp:
                ans[date]=tradeData
                tmp=tradeData
                res['companies']=tradeData
                res['timestamp']=date
                result['activities'].append(res)
        elif tradeData==[]:
            if tradeData!=tmp:
                ans[date]=tradeData
                tmp=tradeData
                res['companies']=tradeData
                res['timestamp']=date
                result['activities'].append(res)
    return result


# 定义一个计算执行时间的函数作装饰器，传入参数为装饰的函数或方法
def dailyHold(func):
    # 定义嵌套函数，用来打印出装饰的函数的执行时间
    def wrapper(self, *args, **kwargs):
        global result_g
        res = func(self, *args, **kwargs)
        date_time=str(self.data.datetime.date())
        result_g[date_time]=[]
        for data in self.datas:
            tmp={}
            pos = self.getposition(data).size
            tmp['ts_code']=data._name
            tmp['share']=pos
            result_g[date_time].append(tmp)
        return res
    return wrapper


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

    print(result_g)

    return outFormat(result_g)

