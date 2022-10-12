from genericpath import isfile
from utils.Timer import Timer
from utils.Plotting import Plotting
from statsmodels.tsa.stattools import coint

import ccxt as ccxt
import pandas as pd
import backtrader as bt
import numpy as np

class Exchange():
    """
    Initializes both Coinbase exchanges and creates easy functions to access data within the api.
    """
    def __init__(self, exchange: str):
        try: 
            self.api = getattr(ccxt, exchange)()
            self.api.load_markets()
            try:
                self.symbols = open(f'CSV\\{exchange}-symbols.txt', "r").read().splitlines()
            except FileNotFoundError as e:
                self.symbols = self.api.symbols
            self.exchange = exchange
        except ccxt.ExchangeError as e:
            print(e)


    def retry_fetch_ohlcv(self, max_retries:int, symbol: str, timeframe: str, since: str, limit: int):
        num_retries = 0
        try:
            num_retries += 1
            try: 
                ohlcv = self.api.fetch_ohlcv(symbol, timeframe, since, limit)
            except ccxt.ExchangeError as e:
                print(e)
            # print('Fetched', len(ohlcv), symbol, 'candles from', self.api.iso8601 (ohlcv[0][0]), 'to', self.api.iso8601 (ohlcv[-1][0]))
            return ohlcv
        except Exception:
            if num_retries > max_retries:
                raise  # Exception('Failed to fetch', timeframe, symbol, 'OHLCV in', max_retries, 'attempts')


    def scrape_ohlcv(self, max_retries:int, symbol: str, timeframe: str, since: str, limit: int):
        timeframe_duration_in_seconds = self.api.parse_timeframe(timeframe)
        timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
        timedelta = limit * timeframe_duration_in_ms
        now = self.api.milliseconds()
        all_ohlcv = []
        fetch_since = since
        while fetch_since < now:
            ohlcv = self.retry_fetch_ohlcv(max_retries, symbol, timeframe, fetch_since, limit)
            fetch_since = (ohlcv[-1][0] + 1) if len(ohlcv) else (fetch_since + timedelta)
            all_ohlcv = all_ohlcv + ohlcv
            if len(all_ohlcv):
                print(len(all_ohlcv), 'candles in total from', self.api.iso8601(all_ohlcv[0][0]), 'to', self.api.iso8601(all_ohlcv[-1][0]))
            else:
                print(len(all_ohlcv), 'candles in total from', self.api.iso8601(fetch_since))
        return self.api.filter_by_since_limit(all_ohlcv, since, None, key=0)


    def get_roe(self, close_values: pd.Series, quantity: float):
        return float((close_values.iat[-1] - close_values.iat[0]) * quantity).__round__(3)


    def find_cointegrated_pairs(self, data: pd.DataFrame):
        """ FORMAT:
                            AAPL	      ADBE	  AMD	EBAY	    HPQ	    IBM	        JNPR	    MSFT	    ORCL	    QCOM	    SPY
            Date											
            2017-12-22	43.752499	175.000000	10.54	37.759998	21.26	145.793503	28.860001	85.510002	47.360001	64.730003	267.510010
            2017-12-26	42.642502	174.440002	10.46	37.939999	21.23	146.108994	28.860001	85.400002	47.430000	64.300003	267.190002
            2017-12-27	42.650002	175.360001	10.53	37.610001	21.27	146.395798	28.879999	85.709999	47.380001	64.540001	267.320007
            2017-12-28	42.770000	175.550003	10.55	37.919998	21.15	147.265778	28.870001	85.720001	47.520000	64.379997	267.869995
            2017-12-29	42.307499	175.240005	10.28	37.740002	21.01	146.673035	28.500000	85.540001	47.279999	64.019997	266.859985
        """
        # shape[0] will give you the total rows present in the dataFrame. 
        # shape[1] will give you the number of columns present in the dataFrame

        n = data.shape[1]
        score_matrix = np.zeros((n, n))
        pvalue_matrix = np.ones((n, n))
        keys = data.keys()
        pairs = []
        for i in range(n):
            for j in range(i+1, n):
                S1 = data[keys[i]]
                S2 = data[keys[j]]
                result = coint(S1, S2)
                score = result[0]
                pvalue = result[1]
                score_matrix[i, j] = score
                pvalue_matrix[i, j] = pvalue
                if pvalue < 0.05:
                    pairs.append((keys[i], keys[j]))
        return score_matrix, pvalue_matrix, pairs


    def get_mark_price(self, symbol: str):
        if symbol not in self.symbols:
            print(f'{self.exchange}: Does not have [{symbol}].')
            return
        orderbook = self.api.fetch_order_book(symbol)
        bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        return (bid, ask, spread)


    def get_time_in_past(self, minutes: float, days:float):
        from datetime import datetime, timedelta
        then = (datetime.now() - timedelta(days = days, minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S").replace(" ", "T")
        return f'{then}Z'


    def get_new_candles_df(self, max_retries:int, symbol: str, timeframe: str, since: str, limit: int):
        if symbol not in self.symbols:
            print(f'{self.exchange}: Does not have [{symbol}].')
            return

        columns=['date', 'open', 'high', 'low', 'close', 'volume']
        sym = symbol.replace('/', '').lower()
        file = f'CSV\\{str(self.exchange).replace(" ", "").lower()}-{sym}-{timeframe}.csv'
        since = self.api.parse8601(since)
        # Get the timeframe in seconds
        tf = self.api.parse_timeframe(timeframe)
        # Set the wait time to candle close, because we can't request data for new candle until it closes
        wait_time = (self.api.milliseconds() - since) / 1000
        
        if not (isfile(file)):
            ohlcv = pd.DataFrame(self.scrape_ohlcv(max_retries, symbol, timeframe, since, limit), columns=columns)
            ohlcv.to_csv(file, mode='a', index=False)
            return ohlcv


        # If a new candle has closed already
        if not (wait_time) <= tf:
            ohlcv = pd.read_csv(file)
            last_pull_time = ohlcv.iat[-1, 0]
            new_candles = pd.DataFrame(self.scrape_ohlcv(max_retries, symbol, timeframe, last_pull_time, limit), columns=columns)
            new_candles.drop(new_candles.head(1).index, inplace=True)
            new_ohlcv = pd.concat([ohlcv, new_candles], ignore_index=True)
            new_candles.to_csv(file, mode='a', index=False, header=False)
            return new_ohlcv


if __name__ == '__main__':
    t = Timer("Read CSV test")
    plot = Plotting()
    # t.start()

    cb = Exchange('binanceusdm')
    df = cb.get_new_candles_df(3, "BTC/USDT", "1m", "2022-10-11T00:00:00Z", 500)
    # plot.plot_ohlcv(df, 10)
    plot.plot_3d(df)
    # print(cb.get_new_candles_df(3, "BTC/USDT", "5m", cb.get_time_in_past(30, 1), 500))

    # t.stop()

    # print(cb.get_roe(df['close'], 4))
    # cb.get_mark_price("BTC/USDT")