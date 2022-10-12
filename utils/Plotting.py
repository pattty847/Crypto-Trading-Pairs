from this import d
from numpy import indices
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as pta

from plotly.subplots import make_subplots


class Plotting():
    def __init__(self) -> None:
        pass

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
            indicator = pta.cg(ohlcv["close"], length=indicator, asc=True)
            fig.add_trace(go.Line(x=ohlcv['date'], y=indicator, name='SMA'), row=2, col=1)

        fig.update(layout_xaxis_rangeslider_visible=False)
        fig.show()


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