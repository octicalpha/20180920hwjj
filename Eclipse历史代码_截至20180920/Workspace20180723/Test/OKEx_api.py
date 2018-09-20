# -*- coding: utf-8 -*-
"""

"""

from OkcoinFutureAPI import OKCoinFuture
from OkcoinSpotAPI import OKCoinSpot
import numpy as np

# 初始化
apikey = 'cdffc016-fdea-4e97-a200-39de74f0021a'
secretkey = '4277FB3395F1590ABC1FC8218B8CC1DF'
okcoinRESTURL = 'www.okcoin.com'

# 现货
okcoinSpot = OKCoinSpot(okcoinRESTURL, apikey, secretkey)

# 期货
okcoinFuture = OKCoinFuture(okcoinRESTURL, apikey, secretkey)

print('下载现货行情数据')

with open('d://OKEx_buy.csv', 'w') as f:
    f.write('date,buy,\n')

    i = 0
    while(1):
        print(i)

        ticker_buy = float(okcoinSpot.ticker('btc_usd')['ticker']['buy'])
        ticker_date = okcoinSpot.ticker('btc_usd')['date']

        f.write(ticker_date + ',' + str(ticker_buy) + ',\n')
        i += 1

        if i > 1000:
            break
