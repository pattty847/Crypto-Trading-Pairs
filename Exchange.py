from genericpath import isdir, isfile
from os import mkdir

from pyparsing import col
from utils.DoStuff import DoStuff

import dearpygui.dearpygui as dpg
import ccxt as ccxt
import pandas as pd
import os
import csv


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
                
            else:
                self.name = exchange.capitalize
        except ccxt.ExchangeError as e:
            print(f'Error connecting to {exchange.capitalize}')

        # Check if we have a file of the symbols
        try:
            self.symbols = open(f'CSV\\{exchange}\\symbols.txt', "r").read().splitlines()
        except FileNotFoundError as e:
            if self.api.id == "binance":
                symbols = self.api.symbols
            elif self.api.id == "ftx":
                symbols = [x for x in self.api.fetch_tickers().items()]
            # If not grab the symbols from the API and store them for quick loading next time. 
            self.symbols = symbols
            mkdir(f'CSV\\{exchange}\\')
            pd.Series(self.symbols).to_csv(f'CSV\\{exchange}\\symbols.txt', index=False)
        print('Symbols imported.')
        
        # Setting up attributes
        # self.api.load_markets()
        self.exchange = exchange
        self.do = DoStuff()
        
        print(f'{self.api.name} connected.')
        
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


    def scrape_ohlcv(self, max_retries:int, symbol: str, timeframe: str, since: str, limit: int):
        timeframe_duration_in_seconds = self.api.parse_timeframe(timeframe)
        timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
        timedelta = limit * timeframe_duration_in_ms
        # This will always be the current time unless updating OLD candles using the TO var where TO is first_pull_time in CSV file
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


    def get_mark_price(self, symbol: str):
        if symbol not in self.symbols:
            print(f'{self.exchange}: Does not have [{symbol}].')
            return
        orderbook = self.api.fetch_order_book(symbol)
        bid = orderbook['bids'][0][0] if len (orderbook['bids']) > 0 else None
        ask = orderbook['asks'][0][0] if len (orderbook['asks']) > 0 else None
        spread = (ask - bid) if (bid and ask) else None
        return (bid, ask, spread)


    def get_candles(self, symbol: str, timeframe: str, since: str):
        
        if symbol not in self.symbols:
            print(f'{self.exchange}: Does not have [{symbol}].')
            return

        columns=['date', 'open', 'high', 'low', 'close', 'volume']
        sym = symbol.replace('/', '').lower() # remove /
        exch = str(self.exchange).replace(" ", "").lower() # remove spaces, lowercase
        dir_ = f'CSV/{exch}/' # build directory: CSV/exchange/
        file = f'{dir_}{sym}-{timeframe}.csv' # build file: CSV/exchange/btcusdt-5m.csv
        since = self.api.parse8601(since)
        if not os.path.exists(dir_): # make directory if it doesn't exist
            os.mkdir(dir_)
        if not (os.path.isfile(file)): # make file if it doesn't exist
            ohlcv = pd.DataFrame(self.scrape_ohlcv(3, symbol, timeframe, since, 500), columns=columns) # pull ohlcv data
            ohlcv.to_csv(file, mode='w', index=False) # write to CSV file. 
            return ohlcv

        # If the file exists load it
        old_candles = pd.read_csv(file)
        first_pull_time = old_candles.iat[0, 0] # first stored time
        last_pull_time = old_candles.iat[-1, 0] # last stored time

        # If we are requesting information within the file

        new_candles = pd.DataFrame(self.scrape_ohlcv(3, symbol, timeframe, last_pull_time, 500), columns=columns)
        new_candles.drop(new_candles.head(1).index, inplace=True)
        new_ohlcv = pd.concat([old_candles, new_candles], ignore_index=True)
        new_candles.to_csv(file, mode='a', index=False, header=False)
        return new_ohlcv


    
    def get_orders(self, symbol, since):
        market = self.api.market(symbol)
        one_hour = 3600 * 1000
        since = self.api.parse8601(since)
        now = self.api.milliseconds()
        end = self.api.parse8601(self.api.ymd(now) + 'T00:00:00')
        previous_trade_id = None
        filename = "CSV\\" + self.api.id + '\\' + market['id'].replace('/', '').lower() + '-orders.csv'
        all_orders = []
        while since < end:
            try:
                trades = self.api.fetch_trades(symbol, since)
                print(self.api.iso8601(since), len(trades), 'trades')
                if len(trades):
                    last_trade = trades[-1]
                    if previous_trade_id != last_trade['id']:
                        since = last_trade['timestamp']
                        previous_trade_id = last_trade['id']
                        for trade in trades:
                            all_orders.append({
                                'timestamp': trade['timestamp'],
                                'size': trade['amount'],
                                'price': trade['price'],
                                'side': trade['side'],
                            })
                    else:
                        since += one_hour
                else:
                    since += one_hour
            except ccxt.NetworkError as e:
                print(type(e).__name__, str(e))
                self.api.sleep(60000)
        df = pd.DataFrame(all_orders, columns=["timestamp", "size", "price", "side"])
        return df


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