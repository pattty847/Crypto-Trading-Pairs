import imp
from multiprocessing.spawn import import_main_path
from utils.Timer import Timer
from utils.Plotting import Plotting
from utils.DoStuff import DoStuff
from Exchange import Exchange

if __name__ == '__main__':
    t = Timer("Read CSV test")
    plot = Plotting()
    do = DoStuff()
    # t.start()
    cb = Exchange('ftx')
    tickers = ["BTC/USDT", "ETH/USDT", "ATOM/USDT", "XRP/USDT", "SUSHI/USDT", "SOL/USDT"]
    plot.plot_coint_pairs(tickers, "4h", do.get_time_in_past(minutes=0, days=30), cb)

    # date = cb.get_time_in_past(0, 90)
    # print(date)
    # df = cb.get_candles("BTC/USDT", "1d", date)
    # print(df)
    # plot.plot_ohlcv(df, 10)
    # plot.plot_3d(df)
    # print(cb.get_new_candles_df(3, "BTC/USDT", "5m", cb.get_time_in_past(30, 1), 500))

    # t.stop()

    # print(cb.get_roe(df['close'], 4))
    # cb.get_mark_price("BTC/USDT")