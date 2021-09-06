import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_api.settings")
import datetime
from django.db import connection
from decimal import *
import numpy as np

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
        return pd.DataFrame()
    df = pd.concat(groups, axis=1, join='outer', ignore_index=False,
              keys=None, levels=None, names=None, verify_integrity=False,
              copy=True)
    df = df.sort_index(ascending=True)
    return df


def get_name_dict(ts_code_list):
    cursor = connection.cursor()
    sql = "select ts_code, name from tush_company where ts_code in({})"
    sql = sql.format(",".join(["'" + ts_code + "'" for ts_code in ts_code_list]))
    cursor.execute(sql)
    cursor.close()

    name_dict = {}
    for row in cursor.fetchall():
        name_dict[row[0]] = row[1]
    return name_dict


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
            close_data = get_df_close_data(df_close, company['ts_code'], date) # 取基金净值
            company_index = all_ts_code_list.index(company['ts_code'])
            total_value = float(Decimal(str(close_data)) * Decimal(str(company['share'])))
            chart_data[company_index, date_index] = total_value if total_value > 0 else (chart_data[company_index, date_index-1] if date_index-1 >= 0 else 0)

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
        for company in activity['holdings_cur']:
            if company["ts_code"] not in ts_code_list:
                ts_code_list.append(company["ts_code"])
                name_list.append(company["name"])
    df_close = getStockValue(ts_code_list, start, end)

    ###################################################

    all_ts_code_list = ['allfund', 'freecash'] + ts_code_list
    all_name_list = ['', ''] + name_list

    dates = dateRange(start, end)
    chart_data = get_chart_data(composition['activities'], dates, df_close, all_ts_code_list)

    return {
        'time_line': dates,
        'ts_code_list': all_ts_code_list,
        'name_list': all_name_list,
        'close_data': chart_data
    }


def calculate_fund_share(ts_code_list, timestamp, allfund, commission):

    df = getStockValue(ts_code_list, timestamp, timestamp)

    name_dict = get_name_dict(ts_code_list)

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
                    'ts_code': j,
                    'name': name_dict[j],
                    'close': value,
                    'share': each_fund_amount // value if value > 0 else 0
                }
            )
        activities.append(
            {
                'timestamp': i,
                'holdings_cur': funds,
                'freecash_cur': allfund - each_fund_amount * len(fund_in_timestamp_list)
            }
        )
    return activities


if __name__ == '__main__':
    ts_code_list = ['000001.SZ', '000002.SZ']
    timestamp = '20200701'
    allfund = 100000000
    commission = 0.0001
    res = calculate_fund_share(ts_code_list, timestamp, allfund, commission)
    print(res)