import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_api.settings")
import datetime
from django.db import connection
from math import isnan
from decimal import *

data_path=r'./tushare_data/data/tush_hist_data'

#记录全部股票的开盘价
def mixValue(df):
    group_data = df.groupby(df['trade_date'])
    conditions = []
    for date,group in group_data:
        conditions.append(" (trade_date='" + date.replace('-', '') + "' and ts_code in " + "('"+"','".join(group['ts_code'])+"')) ")
    condition_str = " or ".join(conditions)
    sql="select ts_code,open,trade_date from tush_hist_data where " + condition_str + ";"

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有

    df_open = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])
    df_open['trade_date'] = df_open['trade_date'].dt.strftime('%Y-%m-%d')

    res = pd.concat([df.set_index(['trade_date', 'ts_code']), df_open.set_index(['trade_date', 'ts_code'])],
                   axis=1)
    return res.reset_index()

#合并多张CSV的开盘价，提取日线数据
def getStockValue(indexes):
    df=pd.DataFrame()
    for ticket in indexes:
        temp=pd.read_csv(data_path+'/'+ticket+'.csv',usecols=['trade_date','open'],index_col=0)
        df[ticket]=temp['open']
    return df

# 自动日期生成
def dateRange(start='2010-01-04', end=datetime.datetime.now().strftime('%Y-%m-%d')):
    start = start.replace('-', '')
    end = end.replace('-', '')
    sql = "SELECT cal_date FROM tush_trade_cal WHERE cal_date>=" + start + " AND cal_date<=" + end + " AND is_open=1"

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有
    df = pd.DataFrame(rows, columns=['cal_date'])
    cursor.close()

    result = list(map(lambda x: x[:4] + '-' + x[4:6] + '-' + x[6:], list(df['cal_date'])))
    return result

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

#格式转换
def changeForm(stocks):
    temp={}
    for stock in stocks:
        temp[stock['ts_code']]=int(stock['share']) if stock['share'] else 0
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
    else:
        stockFund=0
    return stockFund


###############################################
# 将activities转成dataframe
###############################################
def dict2dataframe(activities):
    fields = ['trade_date', 'ts_code', 'share']
    df = pd.DataFrame(columns=fields)
    for activity in activities:
        timestamp = activity['timestamp']
        for company in activity['companies']:
            df = df.append(pd.DataFrame([[timestamp, company['ts_code'], company['share']]], columns=fields), ignore_index=True)
    # 添加open数据
    if not df.empty:
        df = mixValue(df)
    return df


###############################################
# 将dataframe转成activities
###############################################
def dataframe2dict(df):
    group_data = df.groupby(df['trade_date'])
    activities = []
    for date,group in group_data:
        activity = {
            'companies': [],
            'timestamp': date
        }
        for index, row in group.iterrows():
            activity['companies'].append({
                'open': row['open'],
                'share': row['share'],
                'ts_code': row['ts_code']
            })
        activities.append(activity)
    return activities


###############################################
# 计算持仓收益曲线
###############################################
def composition_calculate(composition):
    freeCash = composition['allfund']
    comm = composition['commission']

    tradeDate = [i['timestamp'] for i in composition['activities']]
    tradeDate.sort()

    end = datetime.datetime.now().strftime('%Y-%m-%d')
    if len(tradeDate) == 0:
        return emptyValue(freeCash, end)
    start = tradeDate[0]

    dates = dateRange(start, end)
    # dates = tradeDate

    codeList = []
    for activity in composition['activities']:
        for company in activity['companies']:
            if company["ts_code"] not in codeList:
                codeList.append(company["ts_code"])
    df = getStockValue(codeList)

    activities_dict = {}
    for activity in composition['activities']:
        activities_dict[activity['timestamp']] = activity['companies']

    stocks_dict = {}
    data = [[] for i in range(len(codeList))]
    data_freecash = []
    data_allfund = []

    for date in dates:
        if date in tradeDate:
            freeCash = stockTrader(date, stocks_dict, activities_dict[date], freeCash, comm, df)
            stocks_dict = changeForm(activities_dict[date])
        holdFund = 0
        for index, item in enumerate(codeList):
            stockFund = calValues(item, stocks_dict, date, df)
            holdFund += stockFund if stockFund != None else 0
            data[index].append(stockFund)
        data_freecash.append(freeCash)
        data_allfund.append(freeCash + holdFund)
    codeList.insert(0, "freecash")
    data.insert(0, data_freecash)
    codeList.insert(0, "allfund")
    data.insert(0, data_allfund)
    return {
        'timestamp': dates,
        'codeList': codeList,
        'data': data
    }


###############################################
# 计算持仓收益曲线
###############################################
def activity_calculate(composition, tmp_activity, index=None):
    freeCash = composition['allfund']
    comm = composition['commission']

    codeList = []
    tmp_composition = {
        "allfund": freeCash,
        "commission": comm,
        "activities": []
    }
    activity_added = False
    for company in tmp_activity['companies']:
        if company["ts_code"] not in codeList:
            codeList.append(company["ts_code"])
    for activity in composition['activities']:
        for company in activity['companies']:
            if company["ts_code"] not in codeList:
                codeList.append(company["ts_code"])

        if datetime.date.fromisoformat(tmp_activity["timestamp"]) < datetime.date.fromisoformat(activity["timestamp"]):
            tmp_composition['activities'].append(tmp_activity)
            activity_added = True
            break
        elif datetime.date.fromisoformat(tmp_activity["timestamp"]) == datetime.date.fromisoformat(activity["timestamp"]):
            tmp_composition['activities'].append(tmp_activity)
            activity_added = True
            break
        else:
            tmp_composition['activities'].append(activity)
    if not activity_added:
        tmp_composition['activities'].append(tmp_activity)

    df = getStockValue(codeList)

    composition = tmp_composition.copy()

    activities_dict = {}
    for activity in composition['activities']:
        activities_dict[activity['timestamp']] = activity['companies']

    stocks_dict = {}

    for index_j, activity in enumerate(composition['activities']):
        date = activity['timestamp']
        freeCash = stockTrader(date, stocks_dict, activities_dict[date], freeCash, comm, df)
        stocks_dict = changeForm(activities_dict[date])

        holdFund = 0
        for index, item in enumerate(activity['companies']):
            stockFund = calValues(item['ts_code'], stocks_dict, date, df)
            holdFund += stockFund if stockFund != None else 0
            composition['activities'][index_j]['companies'][index]["allfund"] = stockFund
            composition['activities'][index_j]['companies'][index]["open"] = stockValues(item['ts_code'],date,df)
        composition['activities'][index_j]['freecash'] = freeCash
        composition['activities'][index_j]['allfund'] = freeCash + holdFund
    return composition['activities'][-1]


if __name__ == '__main__':
    params = {
        'activities': [
            {
                'companies': [
                    {'open': 78.11, 'share': 640.0, 'ts_code': '002714.SZ'},
                    {'open': 88.94, 'share': 562.0, 'ts_code': '603882.SH'}
                ],
                'allfund': 100000,
                'freecash': 25.320000000006985,
                'timestamp': '2020-06-30'
            },
            {
                'companies': [
                    {'open': 16.5, 'share': 1515.0, 'ts_code': '002124.SZ'},
                    {'open': 18.4, 'share': 1358.0, 'ts_code': '002157.SZ'},
                    {'open': 21.19, 'share': 1179.0, 'ts_code': '300461.SZ'},
                    {'open': 242.3, 'share': 103.0, 'ts_code': '688399.SH'}
                ],
                'allfund': 99949.93,
                'freecash': 25.320000000006985,
                'timestamp': '2020-09-30'
            }
        ]
    }
    df = dict2dataframe(params['activities'])
    df = mixValue(df)
    activities = dataframe2dict(df)

    composition = {
        'allfund': 100000,
        'commission': 0.0001,
        'activities': activities
    }
    chart_data = composition_calculate(composition)

    tmp_activity = activities[1].copy()
    tmp_activity['timestamp'] = '2020-10-30'
    composition = activity_calculate(composition, tmp_activity, 0)
    print(composition)