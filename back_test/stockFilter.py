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

#区域行业信息筛选(暂不使用)
def area_companies_company_in(area):
    sql='select ts_code, area  from companies_company where area='+num
    df=pd.read_sql(sql=sql,con=test_engine)
    return df

def industry_companies_company_in(industry):
    sql='select ts_code, area  from fina_indicators where industry='+num
    df=pd.read_sql(sql=sql,con=test_engine)
    return df



#roe参数筛选
def roe_fina_indicators_gt(start,end,num):
    sql="SELECT end_date,ts_code,roe FROM fina_indicators WHERE roe >'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def roe_fina_indicators_lt(start,end,num):
    sql="SELECT end_date,ts_code,roe FROM fina_indicators WHERE roe <'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def roe_fina_indicators_eq(start,end,num):
    sql="SELECT end_date,ts_code,roe FROM fina_indicators WHERE roe ='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def roe_fina_indicators_gte(start,end,num):
    sql="SELECT end_date,ts_code,roe FROM fina_indicators WHERE roe >='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def roe_fina_indicators_lte(start,end,num):
    sql="SELECT end_date,ts_code,roe FROM fina_indicators WHERE roe <='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

#经营性现金流（每股）参数筛选
def ocfps_fina_indicators_gt(start,end,num):
    sql="SELECT end_date,ts_code,ocfps FROM fina_indicators WHERE ocfps >'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def ocfps_fina_indicators_lt(start,end,num):
    sql="SELECT end_date,ts_code,ocfps FROM fina_indicators WHERE ocfps <'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def ocfps_fina_indicators_eq(start,end,num):
    sql="SELECT end_date,ts_code,ocfps FROM fina_indicators WHERE ocfps ='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def ocfps_fina_indicators_gt(start,end,num):
    sql="SELECT end_date,ts_code,ocfps FROM fina_indicators WHERE ocfps >='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def ocfps_fina_indicators_lt(start,end,num):
    sql="SELECT end_date,ts_code,ocfps FROM fina_indicators WHERE ocfps <='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

#净利润同比增长率参数筛选
def q_profit_yoy_fina_indicators_gt(start,end,num):
    sql="SELECT end_date,ts_code,q_profit_yoy FROM fina_indicators WHERE q_profit_yoy >'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_profit_yoy_fina_indicators_lt(start,end,num):
    sql="SELECT end_date,ts_code,q_profit_yoy FROM fina_indicators WHERE q_profit_yoy <'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df
    
def q_profit_yoy_fina_indicators_eq(start,end,num):
    sql="SELECT end_date,ts_code,q_profit_yoy FROM fina_indicators WHERE q_profit_yoy ='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_profit_yoy_fina_indicators_gte(start,end,num):
    sql="SELECT end_date,ts_code,q_profit_yoy FROM fina_indicators WHERE q_profit_yoy >='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_profit_yoy_fina_indicators_lte(start,end,num):
    sql="SELECT end_date,ts_code,q_profit_yoy FROM fina_indicators WHERE q_profit_yoy <='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

#净利润环比增长率参数筛选
def q_profit_qoq_fina_indicators_gt(start,end,num):
    sql="SELECT end_date,ts_code,q_profit_qoq FROM fina_indicators WHERE q_profit_qoq >'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_profit_qoq_fina_indicators_lt( start,end,num):    
    sql="SELECT end_date,ts_code,q_profit_qoq FROM fina_indicators WHERE q_profit_qoq <'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_profit_qoq_fina_indicators_eq(start,end,num):
    sql="SELECT end_date,ts_code,q_profit_qoq FROM fina_indicators WHERE q_profit_qoq ='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_profit_qoq_fina_indicators_gte(start,end,num):
    sql="SELECT end_date,ts_code,q_profit_qoq FROM fina_indicators WHERE q_profit_qoq >='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_profit_qoq_fina_indicators_lte( start,end,num):    
    sql="SELECT end_date,ts_code,q_profit_qoq FROM fina_indicators WHERE q_profit_qoq <='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

#同比营收增长率参数筛选
def q_gr_yoy_fina_indicators_gt(start,end,num):
    sql="SELECT end_date,ts_code,q_gr_yoy FROM fina_indicators WHERE q_gr_yoy >'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_gr_yoy_fina_indicators_lt(start,end,num):
    sql="SELECT end_date,ts_code,q_gr_yoy FROM fina_indicators WHERE q_gr_yoy <'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_gr_yoy_fina_indicators_eq(start,end,num):
    sql="SELECT end_date,ts_code,q_gr_yoy FROM fina_indicators WHERE q_gr_yoy ='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_gr_yoy_fina_indicators_gte(start,end,num):
    sql="SELECT end_date,ts_code,q_gr_yoy FROM fina_indicators WHERE q_gr_yoy >='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_gr_yoy_fina_indicators_lte(start,end,num):
    sql="SELECT end_date,ts_code,q_gr_yoy FROM fina_indicators WHERE q_gr_yoy <='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

#环比应收增长率参数筛选
def q_gr_qoq_fina_indicators_gt(start,end,num):
    sql="SELECT end_date,ts_code,q_gr_qoq FROM fina_indicators WHERE q_gr_qoq >'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_gr_qoq_fina_indicators_lt(start,end,num):
    sql="SELECT end_date,ts_code,q_gr_qoq FROM fina_indicators WHERE q_gr_qoq <'"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_gr_qoq_fina_indicators_eq(start,end,num):
    sql="SELECT end_date,ts_code,q_gr_qoq FROM fina_indicators WHERE q_gr_qoq ='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_gr_qoq_fina_indicators_gte(start,end,num):
    sql="SELECT end_date,ts_code,q_gr_qoq FROM fina_indicators WHERE q_gr_qoq >='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

def q_gr_qoq_fina_indicators_lte(start,end,num):
    sql="SELECT end_date,ts_code,q_gr_qoq FROM fina_indicators WHERE q_gr_qoq <='"+num+"' AND end_date > '"+start+"' AND end_date < '"+end+"'"
    df=pd.read_sql(sql=sql,con=engine)
    return df

    #stockFilter 股票条件筛选
def stockFilter(params):
    start=params['start_time']
    del params['start_time']
    end=params['end_time']
    del params['end_time']
    key=list(params.keys())
    num=params[key[0]]
    ans=eval(key[0]+'(start,end,num)')
    for i in range(1,len(key)):
        num=params[key[i]]
        tmp=eval(key[i]+'(start,end,num)')
        columns=list(set(ans).intersection(set(tmp)))
        ans = pd.merge(ans, tmp, on=columns, how='inner')
    df=ans.sort_values(['end_date','ts_code'])
    raws=list(df['end_date'])
    df=df.set_index('end_date')
    column=[i for i in df]
    content=[]
    for i in range(len(df)):
        content.append(list(df.iloc[i]))
    return {'timeStamp':raws,'codeList':column,'stockInfo':content}
   
if __name__=="__main__":
    s=time.time()
    param='roe_fina_indicators_gt=30&roe_fina_indicators_lt=50&ocfps_fina_indicators_gt=0&ocfps_fina_indicators_lt=10&start_time=20190101&end_time=20200401'
    params={}
    for item in param.split('&'):
        tmp=item.split('=')
        params[tmp[0]]=tmp[1]
    result=stockFilter(params)
    e=time.time()
    print(e-s)
    print(result)