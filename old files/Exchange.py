import websocket
import json
import numpy as np

class Exchange():
    def __init__(self, stream, tickers):
        self.wsapp = websocket.WebSocketApp(stream, on_message=self.on_message, on_open=self.on_open, on_close=self.on_close)
        self.tickers = tickers

        self.delta = 0
        self.buy = dict()
        self.sell = dict()

        self.market_buys = 0
        self.market_sells = 0

        self.bid_sizes = []
        self.ask_sizes = []


    def on_open(self, message):
        self.wsapp.send(json.dumps({
            "method": "SUBSCRIBE",
            "params": self.tickers,
            "id": 1
        }))

    def on_close(self):
        print('Exchange: UNSUBSCRIBED')
        self.wsapp.send(json.dumps({
            "method": "UNSUBSCRIBE",
            "params": self.tickers,
            "id": 312
        }))


    def on_message(self, wsapp, message):
        message = json.loads(message)
        self.set_delta(message)


    def set_delta(self, data):
        ticker = data['s']
        if data['m'] == False:
            if not self.buy:
                self.buy[ticker] = np.multiply(float(data['p']), float(data['q']))
            else:
                self.buy[ticker] = self.buy[ticker] + np.multiply(float(data['p']), float(data['q']))
        else:
            if not self.sell:
                self.sell[ticker] = np.multiply(float(data['p']), float(data['q']))
            else:
                self.sell[ticker] = self.sell[ticker] + np.multiply(float(data['p']), float(data['q']))

        delta = float(self.buy[ticker] - self.sell[ticker]).__round__(2)
        print(ticker + " | Delta: " + str(delta))
        



base_url = 'wss://stream.binance.com:9443/ws'
tickers = [
    "btcusdt@aggTrade",
    "ethusdt@aggTrade",
    "bnbusdt@aggTrade",
]
binance = Exchange(base_url, tickers)
binance.wsapp.run_forever()