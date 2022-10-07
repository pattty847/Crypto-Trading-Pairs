import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller

import numpy as np
import csv
import ccxt
import matplotlib.pyplot as plt
import seaborn as sns

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly.express

class PepeFramework():
    def __init__(self) -> None:
        pass

    def plot_ohlcv_matplotlib(self, df):
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


    def plot_ohlcv_plotly(self, ohlcv):
        ohlcv['time'] = pd.to_datetime(ohlcv['time'], unit='ms')
        fig = go.Figure(
            data=[go.Candlestick(
                    x=ohlcv['time'],
                    open=ohlcv['open'],
                    high=ohlcv['high'],
                    low=ohlcv['low'],
                    close=ohlcv['close'])])

        # date = pd.to_datetime(orders['timestamp'], unit='ms')

        # size = orders['size'] * 0.5

        # fig.add_trace(go.Scatter(x=date, y=orders['price'], mode="markers", marker = dict(
        #         color = ['green' if s == 'buy' else 'red' for s in orders['side']],
        #         size=size
        #     )
        # ))

        fig.show()


    def cointegration(self, x, y):
        score, pvalue, _ = coint(x, y)
        return pvalue

    def zscore(self, series):
        return (series - series.mean()) / np.std(series)

    # TODO: ADD THIS
    # def linear_regression(self, df, ticker_a, ticker_b):
    #     X = df[ticker_a].iloc[1:].to_numpy().reshape(-1, 1)
    #     Y = df[ticker_b].iloc[1:].to_numpy().reshape(-1, 1)
        
    #     # S1 = sm.add_constant(coin1.close)
    #     # results = sm.OLS(coin2.close, coin1.close).fit()

    #     # lin_regr = LinearRegression()
    #     # lin_regr.fit(X, Y)
    
    #     # Y_pred = lin_regr.predict(X)
    
    #     # alpha = lin_regr.intercept_[0]
    #     # beta = lin_regr.coef_[0, 0]
    
    #     fig, ax = plt.subplots()
    #     ax.set_title("Alpha: " + str(round(alpha, 5)) + ", Beta: " + str(round(beta, 3)))
    #     ax.scatter(X, Y)
    #     ax.plot(X, Y_pred, c='r')


    def plot_ohlcv_orders_plotly(self, candles, orders):
        pepe = PepeFramework()

        grouped_multiple = orders.groupby(['timestamp']).agg({'size': ['sum'], 'price': ['mean'], 'side':['first']})
        grouped_multiple.columns = ['size', 'price', 'side']
        orders = grouped_multiple.reset_index()

        orders = orders.loc[orders['size'] > 10]

        pepe.plot_ohlcv_plotly(candles, orders)

    
    # def get_coinintegration(self, since, exchange, timeframe, symbol):
    #     scrape = Scrape()
    #     coin1 = scrape.scrape_candles_to_df(exchange_id=exchange, max_retries = 3, symbol=symbol[0], timeframe=timeframe, since = since, limit=1000)
    #     coin2 = scrape.scrape_candles_to_df(exchange_id=exchange, max_retries = 3, symbol=symbol[1], timeframe=timeframe, since = since, limit=1000)

    #     return pepe.cointegration(coin1.close, coin2.close)

# pepe = PepeFramework()
# scrape = Scrape()
# since = '2022-09-01T00:00:00Z'
# exchange = 'binance'
# timeframe = '1m'
# symbols = ['BTC/USDT', 'ETH/USDT']
# #print(pepe.get_coinintegration(since, exchange, timeframe, symbols))

# coin1 = scrape.scrape_candles_to_df_and_return(exchange_id=exchange, max_retries = 3, symbol=symbols[0], timeframe=timeframe, since = since, limit=1000)
# coin2 = scrape.scrape_candles_to_df_and_return(exchange_id=exchange, max_retries = 3, symbol=symbols[1], timeframe=timeframe, since = since, limit=1000)


# coin1 = pd.read_csv('CSV\\btcusdt-candles-1m.csv')
# coin2 = pd.read_csv('CSV\\ethusdt-candles-1m.csv')
# columns = ['time', 'open', 'high', 'low', 'close', 'volume']
# coin1.columns = columns
# coin2.columns = columns
# print(pepe.cointegration(coin1.close, coin2.close))

# # plt.figure(figsize=(12,6))
# # (coin1.close - coin2.close).plot() # Plot the spread
# # plt.axhline((coin1.close - coin2.close).mean(), color='red', linestyle='--') # Add the mean
# # plt.xlabel('Time')
# # plt.legend(['Price Spread', 'Mean'])
# # # plt.show()

# S1 = sm.add_constant(coin1.close)
# results = sm.OLS(coin2.close, coin1.close).fit()

# spread = coin2.close - results.params['close'] * coin1.close
# spread.plot(figsize=(12,6))
# plt.axhline(spread.mean(), color='black')
# plt.legend(['Spread'])
# plt.show()

# ratio = coin1.close/coin2.close
# ratio.plot(figsize=(12,6))
# plt.axhline(ratio.mean(), color='black')
# plt.legend(['Price Ratio'])
# plt.show()

# pepe.zscore(ratio).plot(figsize=(12,6))
# plt.axhline(pepe.zscore(ratio).mean())
# plt.axhline(1.0, color='red')
# plt.axhline(-1.0, color='green')
# plt.show()



"""
PAIRS TRADING: PSEUDO CODE

beta = a + (b*x)
Use a linear regression formula.

if X and Y are cointegrated:
    calculate Beta between X and Y 
    calculate spread as X - Beta * Y
    calculate z-score of spread

S1 = sm.add_constant(S1)
results = sm.OLS(S2, S1).fit()
S1 = S1['ADBE']
b = results.params['ADBE']

spread = S2 - b * S1
spread.plot(figsize=(12,6))
plt.axhline(spread.mean(), color='black')
plt.xlim('2013-01-01', '2018-01-01')
plt.legend(['Spread']);




    # entering trade (spread is away from mean by two sigmas):
    if z-score > 2:
        sell spread (sell 1000 of X, buy 1000 * Beta of Y)
    if z-score < -2:
        buy spread (buy 1000 of X, sell 1000 * Beta of Y)

    # exiting trade (spread converged close to mean):
    if we're short spread and z-score < 1:
        close the trades
    if we're long spread and z-score > -1:
        close the trades

# repeat above on each new bar, recalculating rolling Beta and spread etc.


"""