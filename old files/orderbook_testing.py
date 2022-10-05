import ccxt
from pprint import pprint

import time
import plotly.graph_objects as go

def pull_orderbook(wait, symbol, levels, exchange):
    delay = 2 # seconds
    orderbook = exchange.fetch_order_book(symbol, levels)

    # fig = go.Figure(data=go.Heatmap(
    #     z=orderbook['asks'][0][1],
    #     x=orderbook['timestamp'],
    #     y=programmers,
    #     colorscale='Viridis'))

    # fig.update_layout(
    #     title='GitHub commits per day',
    #     xaxis_nticks=36)

    # fig.show()

exchange = getattr(ccxt, 'binance')()
pull_orderbook(0, 'BTC/USDT', 20, exchange)