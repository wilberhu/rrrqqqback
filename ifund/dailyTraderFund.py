import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_api.settings")
import datetime
from dateutil import parser
from django.db import connection
from math import isnan
from decimal import *

data_path=r'./tushare_data/data/tush_fund_nav_data'

default_start = "2010-01-04"

#记录全部股票的开盘价
def mixValue(df):
    group_data = df.groupby(df['end_date'])
    conditions = []
    for date,group in group_data:
        conditions.append(" (end_date='" + date.replace('-', '') + "' and ts_code in " + "('"+"','".join(group['ts_code'])+"')) ")
    condition_str = " or ".join(conditions)
    sql="select ts_code,adj_nav,end_date from tush_fund_nav where " + condition_str + ";"

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有
    cursor.close()

    df_adj_nav = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    # df_adj_nav['end_date'] = df_adj_nav['end_date'].dt.strftime('%Y%m%d')
    for index, item in df_adj_nav.iterrows():
        df_adj_nav['end_date'].iloc[index] = item['end_date'].strftime('%Y%m%d')

    res = pd.concat([df.set_index(['end_date', 'ts_code']), df_adj_nav.set_index(['end_date', 'ts_code'])],
                   axis=1)
    return res.reset_index()

#合并多张CSV的开盘价，提取日线数据
def getStockValue(indexes):
    df=pd.DataFrame()
    for ticket in indexes:
        temp=pd.read_csv(os.path.join(data_path, ticket+'.csv'),usecols=['end_date','adj_nav'],index_col=0)
        df[ticket]=temp['adj_nav']
    return df

# 自动日期生成
def dateRange(start=default_start, end=datetime.datetime.now().strftime('%Y-%m-%d')):
    start = str(start).replace('-', '')
    end = str(end).replace('-', '')
    sql = "SELECT cal_date FROM tush_trade_cal WHERE cal_date>=" + start + " AND cal_date<=" + end + " AND is_open=1"

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有
    df = pd.DataFrame(rows, columns=['cal_date'])
    cursor.close()

    result = list(map(lambda x: x.strftime('%Y%m%d'), list(df['cal_date'])))

    return result

def emptyValue(stock,end):
    res=[]
    free=stock
    dateList=dateRange(default_start,end)
    n=len(dateList)
    return {
        'time_line':dateList,
        'ts_code_list':['allfund','freecash'],
        'close_data':[[free]*n,[free]*n]
    }

#格式转换
def changeForm(stocks):
    temp={}
    for stock in stocks:
        temp[stock['ts_code']]=int(stock['share']) if stock['share'] and not isnan(int(stock['share'])) else 0
    return temp

#trades为[]，返回的rest为allfund，也即freecash
def stockTrader(date,stocks_dict_pre,stocks,freeCash,comm,df):
    stocks_dict_cur = changeForm(stocks)
    rest=freeCash
    if stocks_dict_cur=={}:
        for stock in stocks_dict_pre:
            rest+=stocks_dict_pre[stock]*stockValues(stock,date,df)*(1-comm)
        return rest
    tradeLog={}
    for stock in stocks_dict_pre:
        if stock in stocks_dict_cur:
            tradeLog[stock]=stocks_dict_pre[stock]-stocks_dict_cur[stock]
            stocks_dict_cur.pop(stock)
        else:
            tradeLog[stock]=stocks_dict_pre[stock]
    for stock in stocks_dict_cur:
        tradeLog[stock]=-int(stocks_dict_cur[stock])

    #需要修改，考虑资金不足的情况
    for stock in tradeLog:
        #rest+=tradeLog[stock]*stockValues(stock,date,df)-abs(tradeLog[stock])*stockValues(stock,date,df)*comm
        rest+=(tradeLog[stock]-abs(tradeLog[stock])*comm)*stockValues(stock,date,df)
    return rest


#自动股票日期价值定位
def stockValues(code,date,df):
    value = 0
    try:
        date=int(date.replace('-',''))
        value=df.at[date,code]
        if isnan(value):
            dates=list(df.index)
            index=dates.index(date)
            values=list(df[code])
            for i in range(index,-1,-1):
                if not isnan(values[i]):
                    value=values[i]
                    break
    except:
        for i in list(df[code])[::-1]:
            if not isnan(i):
                value=i
                break
    return value


#自动计算某日资金
def calValues(code,stocks_dict,date,df):
    price=stockValues(code,date,df)
    if code in stocks_dict and price!=None:
        stockFund=float(Decimal(str(price))*Decimal(str(stocks_dict[code])))
        # print(date, code, price, stocks_dict[code])
    else:
        stockFund=0
    return stockFund


###############################################
# 计算持仓收益曲线
###############################################
def composition_calculate(composition):
    freeCash = composition['allfund']
    comm = composition['commission']

    tradeDate = [i['timestamp'] for i in composition['activities']]
    tradeDate.sort()

    end = datetime.datetime.now().strftime('%Y%m%d')
    if len(tradeDate) == 0:
        return emptyValue(freeCash, end)
    start = tradeDate[0]

    dates = dateRange(start, end)
    # dates = tradeDate

    ts_code_list = []
    for activity in composition['activities']:
        for company in activity['companies']:
            if company["ts_code"] not in ts_code_list:
                ts_code_list.append(company["ts_code"])
    df = getStockValue(ts_code_list)

    activities_dict = {}
    for activity in composition['activities']:
        activities_dict[activity['timestamp']] = activity['companies']

    stocks_dict = {}
    if len(ts_code_list) * len(dates) < 10000:
        data = [[] for i in range(len(ts_code_list))]
        whetherAddCompaniesData = True
    else:
        data = []
        whetherAddCompaniesData = False

    data_freecash = []
    data_allfund = []

    for date in dates:
        if date in tradeDate:
            freeCash = stockTrader(date, stocks_dict, activities_dict[date], freeCash, comm, df)
            stocks_dict = changeForm(activities_dict[date])
        holdFund = 0
        for index, item in enumerate(ts_code_list):
            stockFund = calValues(item, stocks_dict, date, df)
            holdFund += stockFund if stockFund != None else 0
            if whetherAddCompaniesData:
                data[index].append(stockFund)
        data_freecash.append(freeCash)
        data_allfund.append(freeCash + holdFund)
    if whetherAddCompaniesData:
        ts_code_list.insert(0, "freecash")
        data.insert(0, data_freecash)
    ts_code_list.insert(0, "allfund")
    data.insert(0, data_allfund)
    if not whetherAddCompaniesData:
        ts_code_list = ["allfund"]
    return {
        'time_line': dates,
        'ts_code_list': ts_code_list,
        'close_data': data
    }

def calculate_fund_share(ts_code_list, timestamp, allfund, commission):
    df = pd.DataFrame()
    for ts_code in ts_code_list:
        df = df.append([{'end_date': timestamp, 'ts_code': ts_code}], ignore_index=True)
    df = mixValue(df)

    activities = []
    group_data = df.groupby(df['end_date'])
    for date, group in group_data:
        adj_nav_list = [x for x in group['adj_nav'].to_list() if x > 0]
        if len(adj_nav_list) == 0:
            return []
        eachfund = allfund * ( 1 - commission ) / len(adj_nav_list)
        companies = []
        for index, company in group.iterrows():
            companies.append(
                {
                    'ts_code': company['ts_code'],
                    'adj_nav': company['adj_nav'],
                    'share': eachfund // company['adj_nav'] if company['adj_nav'] > 0 else 0
                }
            )
        activities.append(
            {
                'timestamp': date,
                'companies': companies
            }
        )
    return activities

if __name__ == '__main__':
    ts_code_list = ['009010.OF', '009014.OF']
    timestamp = '20200701'
    allfund = 100000000
    commission = 0.0001
    res = calculate_fund_share(ts_code_list, timestamp, allfund, commission)
    print(res)