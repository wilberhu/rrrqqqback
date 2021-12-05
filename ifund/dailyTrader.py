import copy
import math

import pandas as pd
import numpy as np
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_api.settings")
import datetime
from django.db import connection
from decimal import *
from ifund.cal_indicator import get_max_drawdown, cal_indicators

default_start = "2010-01-04"


# 返回空结果
def emptyValue(allfund, end):
    freecash=allfund
    dateList=dateRange(default_start,end)
    n=len(dateList)
    return {
        'lineChartData': {
            'time_line': dateList,
            'ts_code_list': ['allfund', 'freecash'],
            'name_list': ['总资产', '空闲资金'],
            'close_data': [[allfund] * n, [freecash] * n]
        }
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
def getStockValue(ts_code_list, date_list, type):
    cursor = connection.cursor()
    sql = ''
    if type == 'fund':
        sql = "select ts_code, DATE_FORMAT(nav_date,'%Y%m%d') as nav_date, unit_nav, (adj_nav / unit_nav) as adj_factor from tush_fundnav where ts_code in({}) and nav_date in({})"
    elif type == 'company':
        sql = "select ts_code, DATE_FORMAT(trade_date,'%Y%m%d') as trade_date, close, adj_factor from tush_companydaily where ts_code in({}) and trade_date in({})"
        # sql = "select ts_code, DATE_FORMAT(trade_date,'%Y%m%d') as trade_date, close from tush_companydaily where ts_code in({}) and trade_date between cast('{}' as datetime) and cast('{}' as datetime)"

    sql = sql.format(",".join(["'" + ts_code + "'" for ts_code in ts_code_list]), ",".join(["'" + ts_code + "'" for ts_code in date_list]))

    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有
    cursor.close()

    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])
    group_data = df.groupby(['ts_code'])
    if type == 'fund':
        groups = [group[['nav_date', 'unit_nav']].set_index('nav_date').rename(columns={'unit_nav': ts_code}) for ts_code, group in group_data]
        adj_factors = [group[['nav_date', 'adj_factor']].set_index('nav_date').rename(columns={'adj_factor': ts_code}) for ts_code, group in group_data]
    elif type == 'company':
        groups = [group[['trade_date', 'close']].set_index('trade_date').rename(columns={'close': ts_code}) for ts_code, group in group_data]
        adj_factors = [group[['trade_date', 'adj_factor']].set_index('trade_date').rename(columns={'adj_factor': ts_code}) for ts_code, group in group_data]
    if len(groups) == 0:
        return pd.DataFrame(), pd.DataFrame()
    df = pd.concat(groups, axis=1, join='outer', ignore_index=False,
              keys=None, levels=None, names=None, verify_integrity=False,
              copy=True)

    df_adj = pd.concat(adj_factors, axis=1, join='outer', ignore_index=False,
              keys=None, levels=None, names=None, verify_integrity=False,
              copy=True)
    df = df.sort_index(ascending=True)
    df_adj = df_adj.sort_index(ascending=True)
    return df, df_adj
    # return df.mul(df_adj) # !!!!!!!!!!!!!!!!!!!!!!!!!

# 获取多个股票的收盘价，合并为dataframe
def getStockInfo(ts_code_list, timeline, type):
    cursor = connection.cursor()
    sql = ''
    if type == 'fund':
        sql = "select ts_code, DATE_FORMAT(nav_date,'%Y%m%d') as nav_date, unit_nav from tush_fundnav where ts_code in ({}) and nav_date in ({})"
    elif type == 'company':
        sql = "select ts_code, DATE_FORMAT(trade_date,'%Y%m%d') as trade_date, open, close, high, low from tush_companydaily where ts_code in({}) and trade_date in ({})"

    sql = sql.format(",".join(["'" + ts_code + "'" for ts_code in ts_code_list]), ",".join(timeline))
    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有
    cursor.close()

    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])
    if type == 'company':
        df = df.set_index(['trade_date', 'ts_code'])
    return df


def get_name_dict(ts_code_list, type):
    cursor = connection.cursor()
    sql = ''
    if type == 'fund':
        sql = "select ts_code, name from tush_fundbasic where ts_code in({})"
    elif type == 'company':
        sql = "select ts_code, name from tush_company where ts_code in({})"

    sql = sql.format(",".join(["'" + ts_code + "'" for ts_code in ts_code_list]))
    cursor.execute(sql)

    name_dict = {}
    for row in cursor.fetchall():
        name_dict[row[0]] = row[1]
    cursor.close()

    return name_dict


# 根据ts_code获取index
def getCompanyIndexByTsCode(companies, ts_code):
    for i in range(len(companies)):
        if companies[i]['ts_code'] == ts_code:
            return i
    return -1


# 根据调仓日交易计算现有持仓
def getHoldingStates(composition, type, df_info=None, name_dict=None):

    ts_code_list, name_list, timeline = get_all_ts_code(composition)
    df_close, df_adj = getStockValue(ts_code_list, timeline, type)

    activities = []
    for index, activity in enumerate(composition['activities']):
        holdings_cur = copy.deepcopy(activities[index - 1]['holdings_cur'] if index > 0 else [])
        freecash_cur = activities[index - 1]['freecash_cur'] if index > 0 else composition['allfund']

        for index_h, holding in enumerate(holdings_cur):
            if index >= 1:
                holdings_cur[index_h]['share'] = holding['share'] * (df_adj.loc[activity['timestamp']][holding['ts_code']] / df_adj.loc[activities[index - 1]['timestamp']][holding['ts_code']])
                holdings_cur[index_h]['cost'] = holding['cost'] * (df_adj.loc[activity['timestamp']][holding['ts_code']] / df_adj.loc[activities[index - 1]['timestamp']][holding['ts_code']])

        for companyOp in composition['activities'][index]['companyOps']:
            company_index = getCompanyIndexByTsCode(holdings_cur, companyOp['ts_code'])
            operationSign = -1 if companyOp['operation'] == 'buy' else 1
            if company_index != -1:
                holdings_cur[company_index]['share'] -= operationSign * float(companyOp['share'])
                holdings_cur[company_index]['cost'] -= operationSign * float(companyOp['share']) * float(companyOp['price'])
                if abs(holdings_cur[company_index]['share']) < 1:
                    holdings_cur.pop(company_index)
            else:
                holdings_cur.append({
                    'ts_code': companyOp['ts_code'],
                    'name': companyOp['name'] if name_dict == None else name_dict[companyOp['ts_code']],
                    'share': -operationSign * float(companyOp['share']),
                    'cost': -operationSign * float(companyOp['share']) * float(companyOp['price'])
                })
            if name_dict is not None:
                companyOp['name'] = name_dict[companyOp['ts_code']]
            if df_info is not None:
                companyOp['info'] = {
                    'open': df_info.loc[activity['timestamp'], companyOp['ts_code']]['open'],
                    'close': df_info.loc[activity['timestamp'], companyOp['ts_code']]['close'],
                    'high': df_info.loc[activity['timestamp'], companyOp['ts_code']]['high'],
                    'low': df_info.loc[activity['timestamp'], companyOp['ts_code']]['low']
                }

            freecash_cur += operationSign * float(companyOp['share']) * float(companyOp['price'])
        if df_info is not None:
            for holding in holdings_cur:
                holding['close'] = df_info.loc[activity['timestamp'], holding['ts_code']]['close']

        activities.append({
            'holdings_cur': copy.deepcopy(holdings_cur),
            'freecash_cur': freecash_cur,
            'companyOps': copy.deepcopy(composition['activities'][index]['companyOps']),
            'timestamp': composition['activities'][index]['timestamp']
        })

    ret = {
        'id': composition.get('id'),
        'name': composition.get('name'),
        'description': composition.get('description'),
        'allfund': composition.get('allfund'),
        'commission': composition.get('commission'),
        'activities': activities
    }
    return ret


# 获取股票收盘价
def get_df_close_data(df, ts_code, timestamp):
    return df[ts_code].loc[timestamp] if ts_code in df and timestamp in df[ts_code].index else math.nan


def get_all_ts_code(composition):
    ts_code_list = []
    name_list = []
    timeline = []
    for activity in composition['activities']:
        for companyOp in activity['companyOps']:
            if companyOp["ts_code"] not in ts_code_list:
                ts_code_list.append(companyOp.get("ts_code"))
                name_list.append(companyOp.get("name"))
        timeline.append(activity['timestamp'])
    return ts_code_list, name_list, timeline


# 计算持仓收益曲线
def get_chart_data(composition, dates, df_close, df_adj, all_ts_code_list, timeline):

    chart_data = np.zeros((len(all_ts_code_list), len(dates)))

    for date_index, date in enumerate(dates):
        if date in timeline:
            trade_date_index = timeline.index(date)

            adj_trade_dict = {}
            for company in composition['activities'][trade_date_index]['holdings_cur']:
                adj_trade_dict[company['ts_code']] = get_df_close_data(df_adj, company['ts_code'], date)

        for company in composition['activities'][trade_date_index]['holdings_cur']:
            close_data = get_df_close_data(df_close, company['ts_code'], date) # 取收盘价

            rate = get_df_close_data(df_adj, company['ts_code'], date) / adj_trade_dict[company['ts_code']]

            company_index = all_ts_code_list.index(company['ts_code'])
            chart_data[company_index, date_index] = rate * float(str(close_data)) * float(str(company['share'])) if not math.isnan(close_data) else chart_data[company_index, date_index - 1]


        chart_data[all_ts_code_list.index('freecash'), date_index] = composition['activities'][trade_date_index]['freecash_cur']
        chart_data[all_ts_code_list.index('allfund'), date_index] = sum(chart_data[:, date_index])

    return chart_data.tolist()

def get_composition_info(composition, type):
    if type == 'company':
        ts_code_list, name_list, timeline = get_all_ts_code(composition)
        name_dict = get_name_dict(ts_code_list, type)

        df_info = getStockInfo(ts_code_list, timeline, type)
        return getHoldingStates(composition, type, df_info, name_dict)


###############################################
# 主函数
###############################################
def composition_calculate(composition, type):
    commission = composition['commission']
    today = datetime.datetime.now().strftime('%Y%m%d')

    if len(composition['activities']) == 0:
        return emptyValue(composition['allfund'], today)

    composition['activities'].sort(key=lambda item : item['timestamp'])

    start = composition['activities'][0]['timestamp']
    end = today
    dates = dateRange(start, end)

    ts_code_list, name_list, timeline = get_all_ts_code(composition)
    df_close, df_adj = getStockValue(ts_code_list, dates, type)


    all_ts_code_list = ['allfund', 'freecash'] + ts_code_list
    all_name_list = ['总资产', '空闲资金'] + name_list

    chart_data = get_chart_data(composition, dates, df_close, df_adj, all_ts_code_list, timeline)

    df = pd.DataFrame({
        'trade_date': dates,
        'value': [int(i) for i in chart_data[0]]
    })
    indicators = cal_indicators(df)

    return {
        'lineChartData': {
            'time_line': dates,
            'ts_code_list': all_ts_code_list,
            'name_list': all_name_list,
            'close_data': chart_data
        },
        'indicators': indicators
    }


def calculate_fund_share(ts_code_list, timestamp, allfund, commission, type):

    df, df_adj = getStockValue(ts_code_list, [timestamp], type)

    name_dict = get_name_dict(ts_code_list, type)

    activities = []
    for i, row in df.iterrows():
        fund_in_timestamp_list = [x for x in row.to_list() if x > 0]
        if len(fund_in_timestamp_list) == 0:
            return []
        each_fund_amount = allfund / len(fund_in_timestamp_list)
        funds = []
        for j, value in row.iteritems():
            funds.append(
                {
                    'operation': 'buy',
                    'ts_code': j,
                    'name': name_dict[j],
                    'price': value,
                    'share': each_fund_amount // value if value > 0 else 0
                }
            )
        activities.append(
            {
                'timestamp': i,
                'companyOps': funds,
                'freecash_cur': allfund - each_fund_amount * len(fund_in_timestamp_list)
            }
        )
    composition = {
        'allfund': allfund,
        'commission': commission,
        'activities': activities
    }

    composition = getHoldingStates(composition, type)
    return composition
