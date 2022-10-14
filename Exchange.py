from genericpath import isdir, isfile
from os import mkdir

from pyparsing import col
from utils.DoStuff import DoStuff

import dearpygui.dearpygui as dpg
import ccxt as ccxt
import pandas as pd


class Exchange():
    """
        This exchange class initializes a ccxt exchange connection and stores some information as attributes.
        You can pull candles for one or many tickers. 
        You can get a dataframe of ticker closes
    """
    def __init__(self, exchange: str, api=False):
        # Try initializing the exchange and catch any errors.
        try: 
            self.api = getattr(ccxt, exchange)()
            if self.api.name:
                self.name = self.api.name
                print(f'{self.api.name} connected.')
            else:
                self.name = exchange.capitalize
                print(f'{exchange.capitalize} connected.')
        except ccxt.ExchangeError as e:
            print(f'Error connecting to {exchange.capitalize}')

        # Check if we have a file of the symbols
        try:
            self.symbols = open(f'CSV\\{exchange}\\symbols.txt', "r").read().splitlines()
        except FileNotFoundError as e:
            symbols = [x for x in self.api.fetch_tickers().items()]
            # If not grab the symbols from the API and store them for quick loading next time. 
            self.symbols = symbols
            mkdir(f'CSV\\{exchange}\\')
            pd.Series(self.symbols).to_csv(f'CSV\\{exchange}\\symbols.txt', index=False)

        # Setting up attributes
        self.api.load_markets()
        self.exchange = exchange
        
        if self.api.has['fetchOHLCV']:
            self.timeframes = list(self.api.timeframes.keys())


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


    def scrape_ohlcv(self, max_retries:int, symbol: str, timeframe: str, since: str, limit: int, to:int=None):
        timeframe_duration_in_seconds = self.api.parse_timeframe(timeframe)
        timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
        timedelta = limit * timeframe_duration_in_ms
        # This will always be the current time unless updating OLD candles using the TO var where TO is first_pull_time in CSV file
        now = to if to else self.api.milliseconds()
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


    def get_mark_price(self, symbol: str):
        if symbol not in self.symbols:
            print(f'{self.exchange}: Does not have [{symbol}].')
            return
        orderbook = self.api.fetch_order_book(symbol)
        bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        return (bid, ask, spread)


    def get_candles(self, symbol: str, timeframe: str, since: str, gui):
        if symbol not in self.symbols:
            print(f'{self.exchange}: Does not have [{symbol}].')
            return

        columns=['date', 'open', 'high', 'low', 'close', 'volume']
        sym = symbol.replace('/', '').lower()
        exch = str(self.exchange).replace(" ", "").lower()
        dir_ = f'CSV\\{exch}\\'
        file = f'{dir_}{sym}-{timeframe}.csv'
        since = self.api.parse8601(since)
        if not isdir(dir_):
            mkdir(dir_)
        if not (isfile(file)):
            ohlcv = pd.DataFrame(self.scrape_ohlcv(3, symbol, timeframe, since, 500), columns=columns)
            ohlcv.to_csv(file, mode='a', index=False)
            return ohlcv

        # If its on file
        old_candles = pd.read_csv(file)
        first_pull_time = old_candles.iat[0, 0]
        last_pull_time = old_candles.iat[-1, 0]

        # This is where we update NEW information to file
        if first_pull_time < since:
            new_candles = pd.DataFrame(self.scrape_ohlcv(3, symbol, timeframe, last_pull_time, 500), columns=columns)
            new_candles.drop(new_candles.head(1).index, inplace=True)
            new_ohlcv = pd.concat([old_candles, new_candles], ignore_index=True)
            new_candles.to_csv(file, mode='a', index=False, header=False)
            return new_ohlcv
        
        return old_candles

        # Set ohlcv values for old candles
        # dates_ = list(old_candles['date']/1000)
        # opens_ = list(old_candles['open'])
        # closes_ = list(old_candles['close'])
        # lows_ = list(old_candles['low'])
        # highs_ = list(old_candles['high'])
        # # Push these to chart
        # gui.update_old_candle(dates_, opens_, highs_, closes_, lows_)
        # # Pull older candles
        # new_candles = pd.DataFrame(self.scrape_ohlcv(3, symbol, timeframe, since, 500, first_pull_time, True), columns=columns)
        # # Add them to beginning of list
        # dates = list(new_candles['date']/1000)
        # opens = list(new_candles['open'])
        # closes = list(new_candles['close'])
        # lows = list(new_candles['low'])
        # highs = list(new_candles['high'])
        # # Push these to chart
        # gui.update_old_candle(dates, opens, highs, closes, lows)
        # new_candles.to_csv(file, mode='w', index=False)

        # return (dates, opens, highs, closes, lows)



        # This is where we update OLD information to file
        # Pseudo code
        """ 
        check if first_pull_time < since
        set values to candles
        pull older candles
        restore them in the CSV file
        set values to candles
        refresh axis
        """


    def get_candles_from_csv(self, symbol: str, timeframe: str):
        columns=['date', 'open', 'high', 'low', 'close', 'volume']
        sym = symbol.replace('/', '').lower()
        file = f'CSV\\{str(self.exchange).replace(" ", "").lower()}-{sym}-{timeframe}.csv'
        df = pd.read_csv(file)
        df.columns = columns
        return df


    def get_multi_candles(self, tickers:list, timeframe:str, since:str):
        """
            This function will return a dictionary of dataframe object(s) where the key is the ticker. It will loop through the tickers passed to it
            and call the get_candles() function, storing or updating the data in the CSV folder. 
        """
        candles = {}
        if len(tickers) == 1:
            df = self.get_candles(tickers[0])
            return df
        for ticker in tickers:
            df = self.get_candles(ticker, timeframe, since)
            candles[ticker] = df
        return candles


    def get_matrix_of_closes(self, tickers:list, timeframe:str, since:str):
        ohlcv = self.get_multi_candles(tickers, timeframe, since)
        df = pd.DataFrame()
        for ticker in ohlcv.keys():
            df[ticker] = ohlcv[ticker]['close']
        # df.index = ohlcv[df.columns.tolist()[0]]['date']
        return df


    def update_all_tickers(self, symbol: str, timeframe: str, since: str):
        pass


    def automate_data_pulls(self):
        pass