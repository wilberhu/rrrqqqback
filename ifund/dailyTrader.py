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

data_path=r'./tushare_data/data/tush_hist_data'

default_start = "2010-01-04"

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
    cursor.close()

    df_open = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    df_open['trade_date'] = df_open['trade_date'].dt.strftime('%Y%m%d')

    res = pd.concat([df.set_index(['trade_date', 'ts_code']), df_open.set_index(['trade_date', 'ts_code'])],
                   axis=1)
    return res.reset_index()

#合并多张CSV的开盘价，提取日线数据
def getStockValue(indexes):
    df=pd.DataFrame()
    for ticket in indexes:
        temp=pd.read_csv(os.path.join(data_path, ticket+'.csv'),usecols=['trade_date','open'],index_col=0)
        df[ticket]=temp['open']
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
        'timestamp':dateList,
        'codeList':['allfund','freecash'],
        'data':[[free]*n,[free]*n]
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

    end = datetime.datetime.now().strftime('%Y%m%d')
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
    if len(codeList) * len(dates) < 10000:
        data = [[] for i in range(len(codeList))]
        ifAddCompaniesDate = True
    else:
        data = []
        ifAddCompaniesDate = False

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
            if ifAddCompaniesDate:
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
# 计算持仓detail
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

        if datetime.datetime.strptime(tmp_activity["timestamp"], "%Y%m%d") < datetime.datetime.strptime(activity["timestamp"], "%Y%m%d"):
            tmp_composition['activities'].append(tmp_activity)
            activity_added = True
            break
        elif datetime.datetime.strptime(tmp_activity["timestamp"], "%Y%m%d") == datetime.datetime.strptime(activity["timestamp"], "%Y%m%d"):
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
        "activities":[
            {
                "timestamp":"20200901",
                "companies":[
                    {
                        "ts_code":"300829.SZ",
                        "share":29100,
                        "open":110.02
                    },
                    {
                        "ts_code":"603661.SH",
                        "share":32200,
                        "open":88.36
                    },
                    {
                        "ts_code":"603353.SH",
                        "share":38900,
                        "open":73.59
                    },
                    {
                        "ts_code":"601012.SH",
                        "share":36200,
                        "open":63.3
                    },
                    {
                        "ts_code":"002810.SZ",
                        "share":59100,
                        "open":38.15
                    },
                    {
                        "ts_code":"603187.SH",
                        "share":39800,
                        "open":56.71
                    },
                    {
                        "ts_code":"002982.SZ",
                        "share":18300,
                        "open":122.3
                    },
                    {
                        "ts_code":"688202.SH",
                        "share":12600,
                        "open":168.93
                    },
                    {
                        "ts_code":"002706.SZ",
                        "share":85100,
                        "open":25.15
                    },
                    {
                        "ts_code":"688139.SH",
                        "share":30000,
                        "open":67.5
                    },
                    {
                        "ts_code":"300487.SZ",
                        "share":40200,
                        "open":47.3
                    },
                    {
                        "ts_code":"300759.SZ",
                        "share":17400,
                        "open":111.28
                    },
                    {
                        "ts_code":"000858.SZ",
                        "share":8100,
                        "open":237.48
                    },
                    {
                        "ts_code":"300801.SZ",
                        "share":54500,
                        "open":34.05
                    },
                    {
                        "ts_code":"300019.SZ",
                        "share":119900,
                        "open":15.7
                    },
                    {
                        "ts_code":"300443.SZ",
                        "share":67100,
                        "open":25.89
                    },
                    {
                        "ts_code":"000739.SZ",
                        "share":62300,
                        "open":28.32
                    },
                    {
                        "ts_code":"688089.SH",
                        "share":28900,
                        "open":60.01
                    },
                    {
                        "ts_code":"002979.SZ",
                        "share":38500,
                        "open":41
                    },
                    {
                        "ts_code":"300702.SZ",
                        "share":13600,
                        "open":126.8
                    },
                    {
                        "ts_code":"300763.SZ",
                        "share":16100,
                        "open":96
                    },
                    {
                        "ts_code":"300033.SZ",
                        "share":9200,
                        "open":168
                    },
                    {
                        "ts_code":"603258.SH",
                        "share":33500,
                        "open":47.98
                    },
                    {
                        "ts_code":"603699.SH",
                        "share":91000,
                        "open":16.37
                    },
                    {
                        "ts_code":"688181.SH",
                        "share":20700,
                        "open":71.9
                    },
                    {
                        "ts_code":"688169.SH",
                        "share":3000,
                        "open":479
                    },
                    {
                        "ts_code":"603786.SH",
                        "share":18800,
                        "open":75.69
                    },
                    {
                        "ts_code":"688111.SH",
                        "share":4200,
                        "open":329.25
                    },
                    {
                        "ts_code":"002139.SZ",
                        "share":198900,
                        "open":7.01
                    },
                    {
                        "ts_code":"603338.SH",
                        "share":12900,
                        "open":106.16
                    },
                    {
                        "ts_code":"300748.SZ",
                        "share":32400,
                        "open":41.65
                    },
                    {
                        "ts_code":"688369.SH",
                        "share":16700,
                        "open":79
                    },
                    {
                        "ts_code":"002475.SZ",
                        "share":23400,
                        "open":54.89
                    },
                    {
                        "ts_code":"603893.SH",
                        "share":16700,
                        "open":77.21
                    },
                    {
                        "ts_code":"002020.SZ",
                        "share":106300,
                        "open":12.33
                    },
                    {
                        "ts_code":"688019.SH",
                        "share":3800,
                        "open":329.4
                    },
                    {
                        "ts_code":"688100.SH",
                        "share":44200,
                        "open":27.57
                    },
                    {
                        "ts_code":"688166.SH",
                        "share":22600,
                        "open":56.38
                    },
                    {
                        "ts_code":"000672.SZ",
                        "share":43200,
                        "open":28.2
                    },
                    {
                        "ts_code":"603127.SH",
                        "share":11400,
                        "open":102.52
                    },
                    {
                        "ts_code":"002972.SZ",
                        "share":45000,
                        "open":25.58
                    },
                    {
                        "ts_code":"300827.SZ",
                        "share":21100,
                        "open":51.62
                    },
                    {
                        "ts_code":"300788.SZ",
                        "share":24500,
                        "open":46.23
                    },
                    {
                        "ts_code":"688299.SH",
                        "share":44100,
                        "open":26.35
                    },
                    {
                        "ts_code":"002968.SZ",
                        "share":19200,
                        "open":60.31
                    },
                    {
                        "ts_code":"688023.SH",
                        "share":4300,
                        "open":269.67
                    },
                    {
                        "ts_code":"603326.SH",
                        "share":65200,
                        "open":16.45
                    },
                    {
                        "ts_code":"603218.SH",
                        "share":51800,
                        "open":20.43
                    },
                    {
                        "ts_code":"688228.SH",
                        "share":15300,
                        "open":68.53
                    },
                    {
                        "ts_code":"603986.SH",
                        "share":5000,
                        "open":200.05
                    },
                    {
                        "ts_code":"688058.SH",
                        "share":8200,
                        "open":120.34
                    },
                    {
                        "ts_code":"688358.SH",
                        "share":15100,
                        "open":64.8
                    },
                    {
                        "ts_code":"688123.SH",
                        "share":14000,
                        "open":67.35
                    },
                    {
                        "ts_code":"688258.SH",
                        "share":10500,
                        "open":88.51
                    },
                    {
                        "ts_code":"300661.SZ",
                        "share":3300,
                        "open":285
                    },
                    {
                        "ts_code":"688020.SH",
                        "share":9600,
                        "open":100.4
                    },
                    {
                        "ts_code":"002832.SZ",
                        "share":50900,
                        "open":16.61
                    },
                    {
                        "ts_code":"002463.SZ",
                        "share":39300,
                        "open":21.04
                    },
                    {
                        "ts_code":"603160.SH",
                        "share":4600,
                        "open":178
                    },
                    {
                        "ts_code":"002975.SZ",
                        "share":9100,
                        "open":85.44
                    },
                    {
                        "ts_code":"300735.SZ",
                        "share":40000,
                        "open":18.29
                    },
                    {
                        "ts_code":"300782.SZ",
                        "share":1800,
                        "open":389
                    },
                    {
                        "ts_code":"300792.SZ",
                        "share":4200,
                        "open":160.1
                    }
                ]
            },
            {
                "timestamp":"20201102",
                "companies":[
                    {
                        "ts_code":"688169.SH",
                        "share":2100,
                        "open":801.01
                    },
                    {
                        "ts_code":"605008.SH",
                        "share":59400,
                        "open":27.6
                    },
                    {
                        "ts_code":"300850.SZ",
                        "share":15700,
                        "open":92.5
                    },
                    {
                        "ts_code":"300763.SZ",
                        "share":10100,
                        "open":122.4
                    },
                    {
                        "ts_code":"300840.SZ",
                        "share":51200,
                        "open":22.94
                    },
                    {
                        "ts_code":"002139.SZ",
                        "share":142300,
                        "open":8.61
                    },
                    {
                        "ts_code":"002975.SZ",
                        "share":11800,
                        "open":101.01
                    },
                    {
                        "ts_code":"600702.SH",
                        "share":25900,
                        "open":43.61
                    },
                    {
                        "ts_code":"605168.SH",
                        "share":4600,
                        "open":255.88
                    },
                    {
                        "ts_code":"688356.SH",
                        "share":9500,
                        "open":113.33
                    },
                    {
                        "ts_code":"603218.SH",
                        "share":48300,
                        "open":24.2
                    },
                    {
                        "ts_code":"300782.SZ",
                        "share":2600,
                        "open":441.66
                    },
                    {
                        "ts_code":"300443.SZ",
                        "share":36500,
                        "open":30.62
                    },
                    {
                        "ts_code":"603416.SH",
                        "share":11900,
                        "open":89.31
                    },
                    {
                        "ts_code":"601012.SH",
                        "share":15000,
                        "open":70.51
                    },
                    {
                        "ts_code":"300827.SZ",
                        "share":18100,
                        "open":59.34
                    },
                    {
                        "ts_code":"688166.SH",
                        "share":18600,
                        "open":59.49
                    },
                    {
                        "ts_code":"002832.SZ",
                        "share":59800,
                        "open":17.59
                    },
                    {
                        "ts_code":"688299.SH",
                        "share":37900,
                        "open":26.9
                    },
                    {
                        "ts_code":"688202.SH",
                        "share":5900,
                        "open":173.45
                    },
                    {
                        "ts_code":"000858.SZ",
                        "share":4200,
                        "open":247.07
                    },
                    {
                        "ts_code":"603986.SH",
                        "share":5000,
                        "open":197
                    },
                    {
                        "ts_code":"300661.SZ",
                        "share":3500,
                        "open":271
                    },
                    {
                        "ts_code":"300788.SZ",
                        "share":21000,
                        "open":45.67
                    },
                    {
                        "ts_code":"600167.SH",
                        "share":74600,
                        "open":13.2
                    },
                    {
                        "ts_code":"002979.SZ",
                        "share":23000,
                        "open":40.38
                    },
                    {
                        "ts_code":"002475.SZ",
                        "share":17500,
                        "open":54.9
                    },
                    {
                        "ts_code":"688139.SH",
                        "share":14400,
                        "open":67.87
                    },
                    {
                        "ts_code":"603893.SH",
                        "share":12700,
                        "open":76
                    },
                    {
                        "ts_code":"300865.SZ",
                        "share":18800,
                        "open":49.58
                    },
                    {
                        "ts_code":"688358.SH",
                        "share":15500,
                        "open":61.59
                    },
                    {
                        "ts_code":"688023.SH",
                        "share":3900,
                        "open":250
                    },
                    {
                        "ts_code":"688157.SH",
                        "share":8900,
                        "open":103.31
                    },
                    {
                        "ts_code":"300019.SZ",
                        "share":63500,
                        "open":14.68
                    },
                    {
                        "ts_code":"300860.SZ",
                        "share":6200,
                        "open":149.61
                    },
                    {
                        "ts_code":"688393.SH",
                        "share":19800,
                        "open":46.68
                    },
                    {
                        "ts_code":"603127.SH",
                        "share":9500,
                        "open":98.52
                    },
                    {
                        "ts_code":"603187.SH",
                        "share":17700,
                        "open":49.5
                    },
                    {
                        "ts_code":"002987.SZ",
                        "share":16200,
                        "open":56.6
                    },
                    {
                        "ts_code":"603087.SH",
                        "share":7500,
                        "open":119.03
                    },
                    {
                        "ts_code":"688181.SH",
                        "share":14100,
                        "open":64.47
                    },
                    {
                        "ts_code":"688019.SH",
                        "share":3000,
                        "open":307.89
                    },
                    {
                        "ts_code":"603661.SH",
                        "share":11800,
                        "open":72.08
                    },
                    {
                        "ts_code":"002968.SZ",
                        "share":16700,
                        "open":54.67
                    },
                    {
                        "ts_code":"688123.SH",
                        "share":14700,
                        "open":61.02
                    },
                    {
                        "ts_code":"603392.SH",
                        "share":4600,
                        "open":192.96
                    },
                    {
                        "ts_code":"002959.SZ",
                        "share":7200,
                        "open":117.87
                    },
                    {
                        "ts_code":"603338.SH",
                        "share":9300,
                        "open":91.08
                    },
                    {
                        "ts_code":"603950.SH",
                        "share":33100,
                        "open":26.84
                    },
                    {
                        "ts_code":"002993.SZ",
                        "share":10900,
                        "open":76.61
                    },
                    {
                        "ts_code":"300841.SZ",
                        "share":1900,
                        "open":460
                    },
                    {
                        "ts_code":"002463.SZ",
                        "share":47000,
                        "open":18.46
                    },
                    {
                        "ts_code":"603638.SH",
                        "share":15500,
                        "open":51.06
                    },
                    {
                        "ts_code":"688228.SH",
                        "share":14500,
                        "open":56.09
                    },
                    {
                        "ts_code":"300033.SZ",
                        "share":5900,
                        "open":136.61
                    },
                    {
                        "ts_code":"002972.SZ",
                        "share":38400,
                        "open":20.95
                    },
                    {
                        "ts_code":"300837.SZ",
                        "share":14400,
                        "open":55.1
                    },
                    {
                        "ts_code":"688528.SH",
                        "share":39700,
                        "open":20.25
                    },
                    {
                        "ts_code":"603326.SH",
                        "share":60100,
                        "open":12.6
                    },
                    {
                        "ts_code":"603258.SH",
                        "share":21700,
                        "open":39.57
                    },
                    {
                        "ts_code":"300702.SZ",
                        "share":8200,
                        "open":93.99
                    },
                    {
                        "ts_code":"000672.SZ",
                        "share":35600,
                        "open":21.93
                    },
                    {
                        "ts_code":"002991.SZ",
                        "share":7300,
                        "open":100.22
                    },
                    {
                        "ts_code":"688466.SH",
                        "share":23800,
                        "open":31.4
                    },
                    {
                        "ts_code":"688069.SH",
                        "share":8400,
                        "open":86.1
                    },
                    {
                        "ts_code":"300856.SZ",
                        "share":10300,
                        "open":62.4
                    },
                    {
                        "ts_code":"603353.SH",
                        "share":14100,
                        "open":48.92
                    },
                    {
                        "ts_code":"605388.SH",
                        "share":36900,
                        "open":17.57
                    },
                    {
                        "ts_code":"688580.SH",
                        "share":5400,
                        "open":117.5
                    },
                    {
                        "ts_code":"002982.SZ",
                        "share":8300,
                        "open":69.99
                    }
                ]
            }
        ]
    }
    df = dict2dataframe(params['activities'])
    activities = dataframe2dict(df)

    composition = {
        'allfund': 100000000,
        'commission': 0.0001,
        'activities': activities
    }

    chart_data = composition_calculate(composition)
    print(chart_data)

    # tmp_activity = activities[1].copy()
    # tmp_activity['timestamp'] = '2020-10-30'
    # composition = activity_calculate(composition, tmp_activity, 0)
    # print(composition)