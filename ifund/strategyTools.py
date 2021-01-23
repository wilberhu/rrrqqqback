from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

import datetime
import pandas as pd

import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import backtrader.analyzers as btanalyzers

file_path = r'./tushare_data/data/hist_data/'

class DoubleAverages(bt.Strategy):
    params = (
        ('period_sma5', 5),
        ('period_sma10', 10),
        ('stake',1000)
    )
    # 打印日志
    def log(self, txt, dt=None):
        dt = dt or self.data.datetime.date(0)
        print('%s, %s' % (dt, txt))
    def __init__(self):
        # 用于保存订单
        self.order = None
        # 订单价格
        self.buyprice = None
        # 订单佣金
        self.buycomm = None
        # 定义变量保存所有收盘价
        self.dataclose = self.data.close
        #计算10日均线
        self.sma10 = btind.MovingAverageSimple(self.dataclose, period=self.params.period_sma5)
        # 计算30日均线
        self.sma30 = btind.MovingAverageSimple(self.dataclose, period=self.params.period_sma10)
    def notify_order(self, order):
        # 等待订单提交、订单被cerebro接受
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 等待订单完成
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
            else:
                self.log(
                    'SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
        # 如果订单保证金不足，将不会完成，而是执行以下拒绝程序
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))  # pnl：盈利  pnlcomm：手续费
    # 策略逻辑实现
    def next(self):
        # 当今天的10日均线大于30日均线并且昨天的10日均线小于30日均线，则进入市场（买）
        if self.sma10[0] > self.sma30[0] and self.sma10[-1] < self.sma30[-1]:
            # 判断订单是否完成，完成则为None，否则为订单信息
            if self.order:
                return
            #若上一个订单处理完成，可继续执行买入操作
            self.order = self.buy(size=self.params.stake)
            
        # 当今天的10日均线小于30日均线并且昨天的10日均线大于30日均线，则退出市场（卖）
        elif self.sma10[0] < self.sma30[0] and self.sma10[-1] > self.sma30[-1]:
            # 卖出
            self.order = self.sell(size=self.params.stake)

#策略字典
d={'MACD':DoubleAverages}
            
def basic(stock_name,start,end,cash,comm,strategy):
    df=pd.read_csv(file_path+stock_name+'.csv',usecols=['trade_date','open','close','high','low','vol'],index_col=['trade_date'],parse_dates=True)
    df['openinterest']=-1
    
    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=df,fromdate = datetime.datetime(int(start[:4]), int(start[4:6]), int(start[6:])),todate = datetime.datetime(int(end[:4]), int(end[4:6]), int(end[6:])))
    cerebro.adddata(data)

    cerebro.addstrategy(d[strategy])

    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(comm)

    cerebro.addsizer(bt.sizers.PercentSizer,percents=10)
    cerebro.addanalyzer(btanalyzers.SharpeRatio,_name="sharpe")
    cerebro.addanalyzer(btanalyzers.DrawDown,_name="drawdown")
    cerebro.addanalyzer(btanalyzers.Returns,_name="returns")

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    return cerebro.broker.getvalue()


if __name__ == "__main__":
    fund=basic('000005.SZ','20190103','20200103',100000,0.0005,'MACD')
    print(fund)