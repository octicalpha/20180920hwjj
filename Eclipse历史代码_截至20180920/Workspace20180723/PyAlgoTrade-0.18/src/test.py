from pyalgotrade import plotter
from pyalgotrade import strategy
from pyalgotrade.bar import Frequency
from pyalgotrade.barfeed.csvfeed import GenericBarFeed
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.technical import ma
from sqlalchemy.engine import create_engine
import pandas as pd

"""
@date:2018-08-24
@author:David
"""


def sql_to_csv(label=True, database='vic_1d', table='1d', instrument='BINA--BTC--USDT'):
    """导出mysql数据到csv，其中csv需要根据pyalgotrade的数据格式调整字段，如果本地无该csv则下载，有则label设为False直接使用本地csv
    """
    if label:
        engine = create_engine('mysql+pymysql://ops:ops!@#9988@47.74.249.179:3308/david')
        con = engine.connect()
        sql = """select ts,high as High,open as Open,low as Low,close as Close,quantity as Volume from %s.%s where symbol='%s' order by ts;
        """ % (database, table, instrument)
        df = pd.read_sql(sql, con)
        df.rename(columns={'ts': 'Date Time'}, inplace=True)
        df['Adj Close'] = df['Close']
        df.to_csv(instrument + '.csv', index=False)
        con.close()
        return instrument
    else:
        return instrument


class close_above_sma(strategy.BacktestingStrategy):
    """策略逻辑：当前bar的close大于sma且前3天的close小于sma则买入，先买后卖，不做连续加仓
    """

    def __init__(self, feed, instrument):
        """注入feed和instrument，close和sma是两个全序列
        """
        super(close_above_sma, self).__init__(feed)
        self.__instrument = instrument
        self.__close = feed[instrument].getCloseDataSeries()
        self.__sma = ma.SMA(self.__close, 20)
        
    def getSma(self):
        """返回值用于画图
        """
        return self.__sma

    def onBars(self, bars):
        """一根bar就是一个事件，一根bar只含当前时点的数据，如果需要更早的数据，使用self里面的全序列
        """
        # 需要对当前的值做个检验
        if self.__sma[-1] is None:
            return
              
        shares = self.getBroker().getShares(self.__instrument)
        bar = bars[self.__instrument]
        cash = self.getBroker().getCash(False)  # False无做空下的资金
        
        if shares == 0 and bar.getClose() > self.__sma[-1] and self.__close[-3] < self.__sma[-3]:
            sharesToBuy = int(cash / bar.getClose())
            self.marketOrder(self.__instrument, sharesToBuy)
            
        elif shares > 0 and bar.getClose() < self.__sma[-1]:
            self.marketOrder(self.__instrument, -1 * shares)


def main(plot):
    """
    """
    # 初始化常量
    instrument = 'BINA--BTC--USDT'
    # 数据
    # 1、从mysql导出csv数据
    # 2、指定数据频率
    # 3、读入csv给feed
    sql_to_csv(True)  
    feed = GenericBarFeed(Frequency.DAY, None, None)  
    feed.addBarsFromCSV(instrument, instrument + '.csv')      
    # 评价器
    # 1、初始化一个sharpratio评价器
    sharpeRatioAnalyzer = sharpe.SharpeRatio()  
    # 注入
    # 1、实例化一个策略
    # 2、注入评价器
    strat = close_above_sma(feed, instrument)  
    strat.attachAnalyzer(sharpeRatioAnalyzer)  

    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        plt.getInstrumentSubplot(instrument).addDataSeries("sma", strat.getSma())

    strat.run()
    plt.plot()
    print("Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05))


if __name__ == "__main__":
    main(True)
