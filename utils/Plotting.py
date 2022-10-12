import plotly.graph_objects as go
import pandas as pd
import pandas_ta as pta
import matplotlib.pyplot as plt
import seaborn
import statsmodels.api as sm

from utils.DoStuff import DoStuff
from plotly.subplots import make_subplots



class Plotting():
    def __init__(self) -> None:
        self.do = DoStuff()

    # TODO: FINISH THIS FUNC
    def plot_ohlcv(self, ohlcv: pd.DataFrame, indicator: int):
        ohlcv['date'] = pd.to_datetime(ohlcv['date'], unit='ms')
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, 
               vertical_spacing=0.03, subplot_titles=('OHLC', 'Volume'), 
               row_width=[0.2, 0.2, 0.7])
        fig.add_trace(go.Candlestick(
                    x=ohlcv['date'],
                    open=ohlcv['open'],
                    high=ohlcv['high'],
                    low=ohlcv['low'],
                    close=ohlcv['close'], name='Price'), row=1, col=1)

        fig.add_trace(go.Bar(x=ohlcv['date'], y=ohlcv['volume']), row=3, col=1)

        if indicator:
            indicator = pta.ewma(ohlcv["close"], length=indicator, asc=True)
            fig.add_trace(go.Line(x=ohlcv['date'], y=indicator, name='SMA'), row=2, col=1)

        fig.update(layout_xaxis_rangeslider_visible=False)
        fig.show()

    # TODO: FINISH THIS FUNC
    def plot_ohlcv_orders(self, ohlcv: pd.DataFrame, orders: pd.DataFrame):
        ohlcv['date'] = pd.to_datetime(ohlcv['date'], unit='ms')
        orders['date'] = pd.to_datetime(orders['date'], unit='ms')
        size = orders['size'] * 0.5

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
               vertical_spacing=0.03, subplot_titles=('OHLC', 'Volume'), 
               row_width=[0.2, 0.7])

        fig.add_trace(go.Candlestick(
                    x=ohlcv['date'],
                    open=ohlcv['open'],
                    high=ohlcv['high'],
                    low=ohlcv['low'],
                    close=ohlcv['close'], name='Price'), row=1, col=1)


        fig.add_trace(go.Scatter(x=orders['date'], y=orders['price'], mode="markers", marker = dict(
                color = ['green' if s == 'buy' else 'red' for s in orders['side']],
                size=size,
                row=1,
                col=1
            )
        ))

        fig.add_trace(go.Bar(x=ohlcv['date'], y=ohlcv['volume']), row=2, col=1)

        fig.show()

    # TODO: FINISH THIS FUNC
    def plot_3d(self, df):
        N = 70

        fig = go.Figure(data=[go.Mesh3d(
                        x=df['date'],
                        y=df['close'],
                        z=df['volume'],
                        opacity=0.5,
                        color='rgba(244,22,100,0.6)'
                        )])

        fig.update_layout(
            width=700,
            margin=dict(r=20, l=10, b=10, t=10))

        fig.show()


    def plot_coint_pairs(self, tickers:list, timeframe:str, since:str, exchange):
        scores, pvalues, pairs = self.do.find_cointegrated_pairs(exchange.get_matrix_of_closes(tickers, timeframe, since))
        fig, ax = plt.subplots(figsize=(10,10))
        seaborn.heatmap(
            pvalues, 
            xticklabels=tickers, 
            yticklabels=tickers, 
            cmap='RdYlGn_r', 
            mask = (pvalues >= 0.05)
        )
        plt.show()


    def plot_spread_ratio(self, sym_1: pd.Series, sym_2: pd.Series, ratio=False, zscore=False):
        sym_1 = sm.add_constant(sym_1)
        result = sm.OLS(sym_2, sym_1).fit()
        sym_1 = sym_1['close']
        b = result.params['close']

        if ratio:
            ratio = sym_1/sym_2
            ratio.plot(figsize=(12,6))
            plt.axhline(ratio.mean(), color='black')
            plt.legend(['Price Ratio'])
            plt.show()
        
        if zscore:
            ratio = sym_1/sym_2
            score = self.do.zscore(ratio)
            score.plot(figsize=(12, 6))
            plt.axhline(self.do.zscore(score).mean())
            plt.axhline(1.0, color='red')
            plt.axhline(-1.0, color='green')
            plt.show()
            
        # TODO: Fix this and add a spread condition or make whole function use params, learn the param thing
        if not ratio and not zscore:
            spread = sym_2 - b * sym_1
            spread.plot(figsize=(12, 6))
            plt.axhline(spread.mean(), color='black')
            plt.legend(['Spread'])
            plt.show()