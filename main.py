from utils.Timer import Timer
from utils.Plotting import Plotting
from utils.DoStuff import DoStuff
from Exchange import Exchange

import argparse

if __name__ == '__main__':

    cb = Exchange(exchange='ftx')
    t = Timer("")
    plot = Plotting()
    do = DoStuff()

    # t.start()

    tickers = ["BTC/USDT", "ETH/USDT", "ATOM/USDT", "XRP/USDT", "SUSHI/USDT", "SOL/USDT", 'AAVE/USDT', 'BNB/USD', 'CRV/USD', 'DOT/USD', 'DOGE/USD']

    df = cb.get_multi_candles(tickers, '4h', do.get_time_in_past(minutes=0, days=30))
    # plot.plot_coint_pairs(tickers, "4h", do.get_time_in_past(minutes=0, days=30), cb)
    plot.plot_spread_ratio(df['BTC/USDT']['close'], df['DOGE/USD']['close'], True, True)

    
    # t.stop()