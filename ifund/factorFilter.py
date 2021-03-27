import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_api.settings")
from django.db import connection

import time

default_start = "2010-01-04"

#params格式化
def paramsFormat(params):
    result={}
    for indi in params["filterList"]:
        if indi['table'] not in result:
            result[indi['table']]=[]
        
        tmp={'key':indi['key'],'match':indi['match']}
        for item in indi['filterConditionList']:
            tmp[item['key']]=item['value']
        result[indi['table']].append(tmp)
    return result 

#交易日期检查
def dateCheck(dates):
    if len(dates) == 0:
        return {}
    date=','.join(dates)
    sql="SELECT * FROM tush_trade_cal WHERE cal_date IN ("+date+");"

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有
    df = pd.DataFrame(rows, columns=['exchange', 'cal_date', 'is_open', 'pretrade_date'])
    cursor.close()

    result={}
    for i in range(len(df)):
        if int(df.at[i,'is_open'])==1:
            result[df.at[i,'cal_date'][:8]]=df.at[i,'cal_date'][:8]
        else:
            result[df.at[i,'cal_date'][:8]]=df.at[i,'pretrade_date'][:8]
    return result

#拼接生成SQL语句
def sqlGenrate(table,indicators,start,end):
    sql="select end_date,ts_code from "+table+" where end_date>='"+start.replace('-', '')+"' and end_date<='"+end.replace('-', '')+"' "
    for indi in indicators:
        tmp=helper(indi)
        sql+=tmp
    
    print(sql)
    return sql    

#SQL生成辅助函数
def helper(indi):
    d={'gt':'>','lt':'<','eq':'=','gte':'>=','lte':'<='}
    key=indi['key']
    del indi['key']
    match=indi['match']
    del indi['match']
    if len(indi)>1:
        func=[i for i in indi]
        sql='and ('+key+d[func[0]]+str(indi[func[0]])+' '+match+' '+key+d[func[1]]+str(indi[func[1]])+') '
    else:
        func=[i for i in indi]
        sql='and '+key+d[func[0]]+str(indi[func[0]])+' '
    return sql 

#记录全部股票的开盘价
def mixValue(df):
    group_data = df.groupby(df['end_date'])
    conditions = []
    for date,group in group_data:
        conditions.append(" (trade_date=" + str(date) + " and ts_code in " + "('"+"','".join(group['ts_code'])+"')) ")
    condition_str = " or ".join(conditions)
    sql="select ts_code,open,trade_date from tush_hist_data where " + condition_str + ";"

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()  # 读取所有
    df = pd.DataFrame(rows, columns=['ts_code', 'open', 'trade_date'])
    cursor.close()

    result={}
    for i in range(len(df)):
        date=str(df.at[i,'trade_date'])[:10].replace('-','')
        if date not in result:
            result[date]={}
        symbol=df.at[i,'ts_code']
        value=df.at[i,'open']
        result[date][symbol]=value
    return result

#读取数据库
def readSql(params):
    #日期确定
    if "startTime" not in params:
         start=default_start
    else:
        start=params['startTime']
    if "endTime" not in params:
        end=time.strftime("%Y-%m-%d")
    else:
        end=params['endTime']
    #参数格式化
    param=paramsFormat(params)

    tables=[i for i in param]
    res=[]
    
    for table in tables:
        sql=sqlGenrate(table,param[table],start,end)

        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()  # 读取所有
        df = pd.DataFrame(rows, columns=['end_date', 'ts_code'])
        cursor.close()

        res.append(df)
    
    if len(res)==1:
        return res[0]
    else:
        return pd.DataFrame()
def calculateShare(df, params):
    if df.empty:
        return {
            'activities': []
        }

    dates=sorted(list(set(df['end_date'])))

    dates = dateCheck(dates)
    for index in range(len(df)):
        df.at[index,'end_date']=dates[df.at[index,'end_date']]

    stockValues=mixValue(df)

    group_data=df.groupby(df['end_date'])
    res={}
    res["activities"]=[]
    allfund=params['allfund']
    comm=params['commission']
    cnt=0
    for date,group in group_data:
        start=cnt #计算开始结尾的index位置
        end=start+len(group)
        cnt=end

        nums=len(stockValues[df.at[start,'end_date']]) if df.at[start, 'end_date'] in stockValues else 0#计算group中可交易股票数量

        if nums == 0:
            continue

        group_by_date={}#根据季度日期调仓
        group_by_date['companies']=[]
        precodes=[]#上季度持有股票
        realCash=allfund*(1-comm)//nums#去除手续费，每支股票实际可用金额
        stockfund=0#计算股票总值
        for i in range(start,end):
            tmp={}
            code=group.at[i,'ts_code']
            value=stockValues[date][code] if code in stockValues[date] else 0
            if value==0:
                continue
            else:
                tmp["open"]=value
                tmp["share"]=realCash//value
                precodes.append([code,tmp['share']])
                stockfund+=value*tmp['share']*(1+comm)#股票成本核算加入手续费
                tmp["ts_code"]=code
                group_by_date['companies'].append(tmp)
        allfund = allfund if res["activities"]==[] else res['activities'][-1]['freecash']+sum(list(map(lambda x:stockValues[date][x[0]]*x[1]*(1-comm),precodes)))
        group_by_date['allfund']=allfund
        group_by_date['freecash']=allfund-stockfund
        group_by_date['timestamp']=date[:4]+'-'+date[4:6]+'-'+date[6:]
        res["activities"].append(group_by_date)
    return res


#filter主函数
def mainfunc(params):

    df=readSql(params)
    return calculateShare(df, params)



if __name__ == '__main__':
    params = {
        'allfund': 100000,
        'commission': 0.0,
        'startTime': '2020-02-11',
        'filterListString': ['q_roe'],
        'filterList': [
            {
                'url': 'http://localhost:8000/filter_options/1/',
                'id': 1,
                'owner': 'admin',
                'key': 'q_roe',
                'label': '单季度净资产收益率（q_roe）',
                'table': 'tush_fina_indicators',
                'method': 'query',
                'match': 'and',
                'filterConditionListString':
                    [
                        'gt',
                        'lt'
                    ],
                'filterConditionList':
                    [
                        {
                            'key': 'gt',
                            'label': 'greater than',
                            'symbol': '>',
                            'value': '20'
                        },
                        {
                            'key': 'lt',
                            'label': 'less than',
                            'symbol': '<',
                            'value': '22'
                        }
                    ],
                'visible': False
            }
        ]
    }
    result = mainfunc(params)
    print(result)