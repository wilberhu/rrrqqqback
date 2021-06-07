import pandas as pd
from rest_framework.reverse import reverse
import re

from tush.models import Company

column_dict = {
    "roic": "资本回报率",
    "roe": "净资产收益率",
    "roa": "资产收益率",
    "npm": "净利润率",
    "qgr_yoy": "单季营收同比",
    "qpf_yoy": "单季净利润同比",
    "qpf_qoq": "单季净利润环比",
    "total_share": "股本",
    "total_mv": "市值",
    "pe": "静态市盈率",
    "pe_ttm": "滚动市盈率",
    "peg": "市盈增长比率",
    "tr_yoy": "营收同比增长率",
    "np_yoy": "净利润同比增长率",
    "dnp_yoy": "扣非净利润同比增长率",
    "p_tr_yoy": "预测营收同比",
    "p_np_yoy": "预测净利润同比",
    "total_pf": "总利润",
    "otp": "经营现金流/总利润",
}

def getColumnDict(columns):
    res = {}
    for item in columns:
        if re.sub("\d*$", "", item) in column_dict:
            tmp = column_dict[re.sub("\d*$", "", item)]
        else:
            tmp = re.sub("\d*$", "", item)
        res[item] = re.sub("\d*$", "", item) + " " + tmp + " " + re.findall(r"\d*$", item)[0]
    return res

def getCompanyDict():
    res = {}
    queryset = Company.objects.all().only('ts_code', 'name')
    for e in queryset:
        res[e.ts_code] = [e.name, e.industry]
    return res

company_dict = getCompanyDict()

def formatResult2CN(result):
    res = {
        'df': None,
        'group_data': {},
        'path': '',
        'columns': [],
        'activities': []
    }

    df = result['df']
    df = df.rename(columns={"date": "end_date"})
    df["end_date"] = df["end_date"].apply(lambda x: str(x))

    columns = df.columns.tolist()
    if "end_date" in columns:
        columns.remove("end_date")
    if "ts_code" in columns:
        columns.remove("ts_code")
    if "name" in columns:
        columns.remove("name")
    if "industry" in columns:
        columns.remove("industry")

    columns_pre = ['end_date', 'ts_code', 'name', 'industry']
    df_pre = pd.DataFrame(columns=columns_pre)

    for index, row in df.iterrows():
        my_series = pd.Series(data=[row['end_date'], row['ts_code'], company_dict[row['ts_code']][0], company_dict[row['ts_code']][1]], index=columns_pre)
        df_pre = df_pre.append(my_series, ignore_index=True)
    df = pd.concat([df_pre, df[columns]], axis=1)

    df = df.rename(columns=getColumnDict(columns))

    path = result['path'].replace(".csv", '_cn.csv')
    df.to_csv(path)


    group_data = df.groupby(df['end_date'])
    for date, group in group_data:
        group['index'] = group.index
        res['group_data'][date] = {
            'results': group.to_dict('records'),
            'count': group.shape[0]
        }

    res['df'] = df
    res['columns'] = df.columns
    res['path'] = path
    return res

def formatResult(result):
    res = {
        'df': None,
        'group_data': {},
        'path': '',
        'columns': [],
        'activities': []
    }

    df = pd.read_csv(result['path']).fillna('')

    group_data = df.groupby(df['end_date'])
    for date, group in group_data:
        group['index'] = group.index
        res['group_data'][date] = {
            'results': group.to_dict('records'),
            'count': group.shape[0]
        }

    res['df'] = df
    res['columns'] = df.columns
    res['path'] = result['path']
    res['activities'] = result['activities']
    return res