from pyparsing import col
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

import csv
import ccxt
import matplotlib.pyplot as plt
import seaborn as sns

from Scrape_Binance import Scrape; sns.set(style="whitegrid")

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly.express

class Pepe():
    def __init__(self) -> None:
        pass

    def plot_ohlcv_matplotlib(self, df, orders):
        df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
        #create figure
        plt.figure()

        #define width of candlestick elements
        width = .4
        width2 = .05

        up = df[df.Close >= df.Open]
        down = df[df.Close < df.Open]

        col1 = 'green'
        col2 = 'red'

        plt.bar(up.index, up.Close - up.Open, width, bottom=up.Open, color=col1)
        plt.bar(up.index, up.High - up.Close, width2, bottom=up.Close, color=col1)
        plt.bar(up.index, up.Low - up.Open, width2, bottom=up.Open, color=col1)

        plt.bar(down.index, down.Close - down.Open, width, bottom=down.Open, color=col2)
        plt.bar(down.index, down.High - down.Close, width2, bottom=down.Open, color=col2)
        plt.bar(down.index, down.Low - down.Open, width2, bottom=down.Close, color=col2)

        plt.show()


    def plot_orders(self, orders):
        area = orders['price_mean'] * orders['size_sum'] * 0.02
        time = pd.to_datetime(orders['timestamp'], unit='ms')
        plt.scatter(time, orders['price_mean'] * orders['size_sum'], s=area, c='red', alpha=0.5)
        plt.plot(time, orders['price_mean'])
        plt.show()


    def plot_ohlcv_plotly(self, ohlcv, orders):
        ohlcv.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        ohlcv['Date'] = pd.to_datetime(ohlcv['Date'], unit='ms')
        fig = go.Figure(
            data=[go.Candlestick(
                    x=ohlcv['Date'],
                    open=ohlcv['Open'],
                    high=ohlcv['High'],
                    low=ohlcv['Low'],
                    close=ohlcv['Close'])])

        date = pd.to_datetime(orders['timestamp'], unit='ms')

        size = orders['size'] * 0.5

        fig.add_trace(go.Scatter(x=date, y=orders['price'], mode="markers", marker = dict(
                # color = 'green' if orders['color'] == 'buy' else 'red',
                size=size
            )
        ))

        fig.show()


    def cointegration(self, x, y):
        score, pvalue, _ = coint(x, y)
        return pvalue


    def plot_with_plotly(self):
        pepe = Pepe()

        df = pd.read_csv('CSV/btcusdt-orders.csv')
        candles = pd.read_csv('CSV/btcusdt-candles.csv')

        grouped_multiple = df.groupby(['timestamp']).agg({'size': ['sum'], 'price': ['mean'], 'side':['first']})
        grouped_multiple.columns = ['size', 'price', 'side']
        orders = grouped_multiple.reset_index()

        orders = orders.loc[orders['size'] > 10]

        # pepe.plot_orders(grouped_multiple)
        pepe.plot_ohlcv_plotly(candles, orders)
        # pepe.plot_ohlcv_matplotlib(df, grouped_multiple)

    
    def get_coinintegration(self, since, exchange, timeframe, symbol):
        scrape = Scrape()
        coin1 = scrape.scrape_candles_to_df(exchange_id=exchange, max_retries = 3, symbol=symbol[0], timeframe=timeframe, since = since, limit=1000)
        coin2 = scrape.scrape_candles_to_df(exchange_id=exchange, max_retries = 3, symbol=symbol[1], timeframe=timeframe, since = since, limit=1000)

        return pepe.cointegration(coin1.close, coin2.close)

pepe = Pepe()
since = '2022-09-28T00:00:00Z'
exchange = 'binance'
timeframe = '1h'
symbols = ['XRP/USDT', 'BTC/USDT']
print(pepe.get_coinintegration(since, exchange, timeframe, symbols))

btc = pd.read_csv('btcusdt-candles-1h.csv')
xrp = pd.read_csv('xrpusdt-candles-1h.csv')

pepe.plot_ohlcv_plotly()