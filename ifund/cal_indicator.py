import numpy as np

# 最大回撤计算
def get_max_drawdown(array, value_type='percent'):
    d = {}
    a = array
    b = np.maximum.accumulate(a)
    rates = [i for i in list((b - a) / b) if np.isnan(i) == False]
    d['percent'] = round(max(rates) * 100, 2)
    d['value'] = round(max(rates), 5)

    return d[value_type]


# 技术指标计算
def cal_indicators(df_ori, benchmark='000001.SH'):
    df = df_ori.sort_index()
    value = df.columns[0]
    # df = df.rename(columns={value: 'value'})
    df['pct_change'] = df['value'].pct_change()
    b = list(df['value'])[0]
    e = list(df['value'])[-1]
    df = df.dropna()
    start = str(df.index[0])
    end = str(df.index[-1])

    res = {'年化收益率(%)': 0, '年化标准差(%)': 0, '贝塔系数': 0, '夏普比率': 0, '信息比率': 0, '最大回撤(%)': 0}

    res['年化收益率(%)'] = round((((e - b) / b + 1) ** (252 / len(df)) - 1), 4) * 100

    res['年化标准差(%)'] = round(df['pct_change'].std() * np.sqrt(250), 4) * 100

    # 连接tushare超时，夏普比率计算需要更新
    '''
    bench=pro.index_daily(ts_code=benchmark, start_date=start, end_date=end).sort_values(by='trade_date')[['trade_date','close','pct_chg']]
    df=pd.merge(df,bench,how='left',left_on='trade_date',right_on='trade_date')

    res['贝塔系数']=round((np.cov(df['pct_change'], df['pct_chg']))[0][1]/np.var(bench['pct_chg']),4)

    df['ex_pct_close']=df['pct_change']-0.04/252
    res['夏普比率']=round((df['ex_pct_close'].mean()*np.sqrt(252))/df['ex_pct_close'].std(),4)

    x=list(df['close'])[0]
    y=list(df['close'])[-1]
    bench_return=round((((y-x)/x+1)**(252/len(df))-1),4)
    tmp=df['pct_change']-df['pct_chg']

    res['信息比率']=round((res['年化收益率']-bench_return)/(tmp.std()*np.sqrt(252)),4)
    '''
    res['最大回撤(%)'] = round(get_max_drawdown(list(df['value'])), 2)

    return res