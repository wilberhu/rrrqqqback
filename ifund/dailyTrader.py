import copy

import pandas as pd
import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_api.settings")
import datetime
from django.db import connection
from decimal import *

default_start = "2010-01-04"


# 返回空结果
def emptyValue(allfund, end):
    freecash=allfund
    dateList=dateRange(default_start,end)
    n=len(dateList)
    return {
        'time_line':dateList,
        'ts_code_list':['allfund','freecash'],
        'name_list':['',''],
        'close_data':[[allfund]*n,[freecash]*n]
    }


# 自动日期生成
def dateRange(start, end):
    sql = "SELECT cal_date FROM tush_trade_cal WHERE cal_date BETWEEN cast('{}' as date) AND cast('{}' as date) AND is_open=1;".format(start, end)

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有
    df = pd.DataFrame(rows, columns=['cal_date'])
    cursor.close()

    result = list(map(lambda x: x.strftime('%Y%m%d'), list(df['cal_date'])))
    return result


# 获取多个股票的收盘价，合并为dataframe
def getStockValue(ts_code_list, start, end):
    cursor = connection.cursor()
    sql = "select ts_code, DATE_FORMAT(trade_date,'%Y%m%d') as trade_date, close from tush_companydaily where ts_code in({}) and trade_date between cast('{}' as datetime) and cast('{}' as datetime)"

    sql = sql.format(",".join(["'" + ts_code + "'" for ts_code in ts_code_list]), start, end)

    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有
    cursor.close()

    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])
    group_data = df.groupby(['ts_code'])
    groups = [group[['trade_date', 'close']].set_index('trade_date').rename(columns={'close': ts_code}) for ts_code, group in group_data]

    if len(groups) == 0:
        df = pd.DataFrame()
    else:
        df = pd.concat(groups, axis=1, join='outer', ignore_index=False,
              keys=None, levels=None, names=None, verify_integrity=False,
              copy=True)
        df = df.sort_index(ascending=True)
    return df


# 根据ts_code获取index
def getCompanyIndexByTsCode(companies, ts_code):
    for i in range(len(companies)):
        if companies[i]['ts_code'] == ts_code:
            return i
    return -1


# 根据交易详情计算调仓日现有持仓
def getHoldingStates(composition, commission):
    holding_states = []
    for index, activity in enumerate(composition['activities']):
        holdings_cur = copy.deepcopy(composition['activities'][index - 1]['holdings_cur'] if index > 0 else [])
        freecash_cur = composition['activities'][index - 1]['freecash_cur'] if index > 0 else composition['allfund']

        for companyOp in composition['activities'][index]['companyOps']:
            company_index = getCompanyIndexByTsCode(holdings_cur, companyOp['ts_code'])
            operationSign = -1 if companyOp['operation'] == 'buy' else 1
            if company_index != -1:
                holdings_cur[company_index]['share'] -= operationSign * float(companyOp['share'])
                holdings_cur[company_index]['cost'] -= operationSign * float(companyOp['share']) * float(
                    companyOp['price'])
                if holdings_cur[company_index]['share'] == 0:
                    holdings_cur.pop(company_index)
            else:
                holdings_cur.append({
                    'ts_code': companyOp['ts_code'],
                    'name': companyOp['name'],
                    'share': -operationSign * float(companyOp['share']),
                    'cost': -operationSign * float(companyOp['share']) * float(companyOp['price'])
                })

            freecash_cur += operationSign * float(companyOp['share']) * float(companyOp['price'])

        holding_states.append({
            'holdings_cur': copy.deepcopy(holdings_cur),
            'freecash_cur': freecash_cur,
            'timestamp': composition['activities'][index]['timestamp']
        })
    return holding_states


# 获取股票收盘价
def get_df_close_data(df, ts_code, timestamp):
    return df[ts_code].loc[timestamp] if ts_code in df and timestamp in df[ts_code].index else 0


# 计算持仓收益曲线
def get_chart_data(holding_states, dates, df_close, all_ts_code_list):
    tradeDate = [i['timestamp'] for i in holding_states]

    chart_data = np.zeros((len(all_ts_code_list), len(dates)))

    trade_date_index = 0
    for date_index, date in enumerate(dates):
        if date in tradeDate:
            trade_date_index = tradeDate.index(date)

        for company in holding_states[trade_date_index]['holdings_cur']:
            close_data = get_df_close_data(df_close, company['ts_code'], date) or '' # 取收盘价
            company_index = all_ts_code_list.index(company['ts_code'])
            total_value = float(str(close_data)) * float(str(company['share'])) if close_data != '' else chart_data[company_index, date_index-1]
            chart_data[company_index, date_index] = total_value

        chart_data[all_ts_code_list.index('freecash'), date_index] = holding_states[trade_date_index]['freecash_cur']
        chart_data[all_ts_code_list.index('allfund'), date_index] = sum(chart_data[:, date_index])

    return chart_data.tolist()


###############################################
# 主函数
###############################################
def composition_calculate(composition):
    commission = composition['commission']
    today = datetime.datetime.now().strftime('%Y%m%d')

    if len(composition['activities']) == 0:
        return emptyValue(composition['allfund'], today)

    composition['activities'].sort(key=lambda item : item['timestamp'])

    start = composition['activities'][0]['timestamp']
    end = today


    ts_code_list = []
    name_list = []
    for activity in composition['activities']:
        for companyOp in activity['companyOps']:
            if companyOp["ts_code"] not in ts_code_list:
                ts_code_list.append(companyOp["ts_code"])
                name_list.append(companyOp["name"])
    df_close = getStockValue(ts_code_list, start, end)

    # holding_states = getHoldingStates(composition, commission)

    all_ts_code_list = ['allfund', 'freecash'] + ts_code_list
    all_name_list = ['总资产', '空闲资金'] + name_list

    dates = dateRange(start, end)
    chart_data = get_chart_data(composition['activities'], dates, df_close, all_ts_code_list)

    return {
        'time_line': dates,
        'ts_code_list': all_ts_code_list,
        'name_list': all_name_list,
        'close_data': chart_data
    }


if __name__ == '__main__':
    composition = {
        "name":"composition",
        "allfund":100000000,
        "commission":0.0001,
        "activities":[
            {
                "companyOps":[
                    {
                        "operation":"buy",
                        "ts_code":"000001.SZ",
                        "ts_code_temp":"000001.SZ",
                        "name":"平安银行",
                        "share":"1000000",
                        "info":{
                            "date":"20210802",
                            "open":17.64,
                            "close":18.01,
                            "high":18.14,
                            "low":17.18
                        },
                        "price":"18"
                    },
                    {
                        "operation":"buy",
                        "ts_code":"000002.SZ",
                        "ts_code_temp":"000002.SZ",
                        "name":"万科A",
                        "share":"1000000",
                        "info":{
                            "date":"20210802",
                            "open":20.6,
                            "close":20.9,
                            "high":21.18,
                            "low":20.1
                        },
                        "price":"21"
                    }
                ],
                "timestamp_temp":"20210802",
                "timestamp":"20210802",
                "freecash_pre":100000000,
                "freecash_cur":61000000,
                "holdings_pre":[

                ],
                "holdings_cur":[
                    {
                        "ts_code":"000001.SZ",
                        "name":"平安银行",
                        "share":1000000,
                        "cost":18000000
                    },
                    {
                        "ts_code":"000002.SZ",
                        "name":"万科A",
                        "share":1000000,
                        "cost":21000000
                    }
                ]
            },
            {
                "companyOps":[
                    {
                        "operation":"buy",
                        "ts_code":"002594.SZ",
                        "ts_code_temp":"002594.SZ",
                        "name":"比亚迪",
                        "share":"20000",
                        "info":{
                            "date":"20210806",
                            "open":313,
                            "close":303.48,
                            "high":317.3,
                            "low":298.5
                        },
                        "price":"310"
                    },
                    {
                        "operation":"sell",
                        "ts_code":"000002.SZ",
                        "ts_code_temp":"000002.SZ",
                        "name":"万科A",
                        "share":"500000",
                        "info":{
                            "date":"20210806",
                            "open":20.73,
                            "close":21.1,
                            "high":21.16,
                            "low":20.33
                        },
                        "price":"20.5"
                    }
                ],
                "timestamp_temp":"20210806",
                "timestamp":"20210806",
                "freecash_pre":61000000,
                "freecash_cur":65050000,
                "holdings_pre":[
                    {
                        "ts_code":"000001.SZ",
                        "name":"平安银行",
                        "share":1000000,
                        "cost":18000000
                    },
                    {
                        "ts_code":"000002.SZ",
                        "name":"万科A",
                        "share":1000000,
                        "cost":21000000
                    }
                ],
                "holdings_cur":[
                    {
                        "ts_code":"000001.SZ",
                        "name":"平安银行",
                        "share":1000000,
                        "cost":18000000
                    },
                    {
                        "ts_code":"000002.SZ",
                        "name":"万科A",
                        "share":500000,
                        "cost":10750000
                    },
                    {
                        "ts_code":"002594.SZ",
                        "name":"比亚迪",
                        "share":20000,
                        "cost":6200000
                    }
                ]
            }
        ]
    }
    chart_data = composition_calculate(composition)
    print(chart_data)
