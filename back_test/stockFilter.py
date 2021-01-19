import pandas as pd
import os
import sys
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.types import CHAR,INT
from sqlalchemy.orm import sessionmaker
import time
 
connect_info = 'mysql+pymysql://root:87654321@localhost:3306/stock_api?charset=utf8'
engine = create_engine(connect_info) #use sqlalchemy to build link-engine

def paramsFormat(params):
    result={}
    for indi in params["filterList"]:
        if indi['table'] not in result:
            result[indi['table']]=[] 
        for item in result[indi['table']]:
            if item['key']==indi['key']:
                item[indi['filterConditionList'][0]['key']]=indi['filterConditionList'][0]['value']
                break
        else:
            tmp={}
            tmp['key']=indi['key']
            tmp['match']=indi['match']
            tmp[indi['filterConditionList'][0]['key']]=indi['filterConditionList'][0]['value']
            result[indi['table']].append(tmp)
    return result

def sqlGenrate(table,indicators,start,end):
    sql="select end_date,ts_code from "+table+" where end_date>='"+start+"' and end_date<='"+end+"' "
    for indi in indicators:
        tmp=helper(indi)
        sql+=tmp
    return sql    

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

def stockValue(code,date):
    try:
        sql_date="select cal_date,is_open,pretrade_date from trade_cal where cal_date='"+date+"';"
        df_date=pd.read_sql(sql_date,engine)
        if df_date['is_open'][0]==1:
            trade_date=date
        else:
            trade_date=df_date['pretrade_date'][0]
        sql_open="select ts_code,open from hist_data where ts_code='"+code+"' and trade_date='"+trade_date+"';"
        df_open=pd.read_sql(sql_open,engine)
        value=df_open['open'][0]
    except:
        value=0
    return value

#股票名字典
def stockName(df):
    data=df
    codeList=set(data['ts_code'])
    stock_dict={}
    sql="select ts_code,name from companies_company"
    df=pd.read_sql(sql,engine)
    for code in codeList:
        index=df.loc[df['ts_code'].isin([code])].index
        stock_dict[code]=df.loc[index[0]]['name']
    data['name']=''
    for i in range(len(data)):
        data.loc[i,'name']=stock_dict[data.loc[i]['ts_code']]
    return data

#计算可交易股票数量
def countNums(df,index):
    nums=0
    for i in range(index,index+len(df)):
        if stockValue(df.loc[i,'ts_code'],df.loc[i,'end_date'])!=0:
            nums+=1
    return nums

def readSql(params):
    #日期确定
    if "startTime" not in params:
         start='2010-01-03'
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
        df=pd.read_sql(sql,engine)
        res.append(df)
    
    if len(res)==1:
        return res[0]

def mainfunc(params):
    df=readSql(params)
    df=stockName(df)
    group_data=df.groupby(df['end_date'])
    result={}
    result["activities"]=[]
    allfund=params['allfund']
    comm=params['commission']
    cnt=0
    for date,group in group_data:
        start=cnt #计算开始结尾的index位置
        end=start+len(group)
        cnt=end
        nums=countNums(group,start)#计算group中可交易股票数量
        group_by_date={}#根据季度日期调仓
        group_by_date['companies']=[]
        precodes=[]#上季度持有股票
        realCash=allfund*(1-comm)//nums#去除手续费，每支股票实际可用金额
        stockfund=0#计算股票总值
        for i in range(start,end):
            tmp={}
            code=group.loc[i]['ts_code']
            name=group.loc[i]['name']
            value=stockValue(code,date)
            if value==0:
                continue
            else:
                tmp["name"]=name
                tmp["open"]=value
                tmp["share"]=realCash//value
                precodes.append([code,tmp['share']])
                stockfund+=value*tmp['share']*(1+comm)#股票成本核算加入手续费
                #print(len(group),name,value,tmp['share'],stockfund)
                tmp["ts_code"]=code
                tmp["ts_code_name"]=code+'-'+name
                group_by_date['companies'].append(tmp)
        allfund= allfund if result["activities"]==[] else result['activities'][-1]['freecash']+sum(list(map(lambda x:stockValue(x[0],date)*x[1]*(1-comm),precodes)))
        group_by_date['allfund']=allfund
        group_by_date['freecash']=allfund-stockfund
        group_by_date['timestamp']=date[:4]+'-'+date[4:6]+'-'+date[6:]
        result["activities"].append(group_by_date)
    return result


if __name__=="__main__":
    params={'startTime': '2019-01-01',
     'endTime': '2020-01-01',
     'allfund':100000,
     'commission':0.0001,
     'filterList': [{'method': 'query',
       'key': 'roe',
       'table': 'fina_indicators',
       'match': 'and',
       'filterConditionList': [{'key': 'gt', 'value': 30}]},
      {'method': 'query',
       'key': 'roe',
       'table': 'fina_indicators',
       'match': 'and',
       'filterConditionList': [{'key': 'lt', 'value': 50}]},
      {'method': 'query',
       'key': 'ocfps',
       'table': 'fina_indicators',
       'match': 'and',
       'filterConditionList': [{'key': 'gt', 'value': 0}]},
      {'method': 'query',
       'key': 'ocfps',
       'table': 'fina_indicators',
       'match': 'and',
       'filterConditionList': [{'key': 'lt', 'value': 10}]}]}
    res=mainfunc(params)
    print(res)