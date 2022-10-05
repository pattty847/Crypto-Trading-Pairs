# -*- coding: utf-8 -*-

import os
import sys
import csv
import time

# -----------------------------------------------------------------------------

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt  # noqa: E402
import pandas as pd
import numpy as np
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller
from Pepe import PepeFramework

# -----------------------------------------------------------------------------
class Scrape():

    def __init__(self, exchanges, symbols) -> None:
        try: 
            self.exchanges = [getattr(ccxt, exchange)() for exchange in exchanges]
        except ccxt.ExchangeError as e:
            print(e)
        [exchange.load_markets() for exchange in self.exchanges]
        self.symbols = symbols


    def retry_fetch_ohlcv(self, exchange, max_retries, symbol, timeframe, since, limit):
        num_retries = 0
        try:
            num_retries += 1
            try: 
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            except ccxt.ExchangeError as e:
                print(e)
            # print('Fetched', len(ohlcv), symbol, 'candles from', exchange.iso8601 (ohlcv[0][0]), 'to', exchange.iso8601 (ohlcv[-1][0]))
            return ohlcv
        except Exception:
            if num_retries > max_retries:
                raise  # Exception('Failed to fetch', timeframe, symbol, 'OHLCV in', max_retries, 'attempts')


    def scrape_ohlcv(self, exchange, max_retries, symbol, timeframe, since, limit):
        timeframe_duration_in_seconds = exchange.parse_timeframe(timeframe)
        timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
        timedelta = limit * timeframe_duration_in_ms
        now = exchange.milliseconds()
        all_ohlcv = []
        fetch_since = since
        print(fetch_since)
        print(now)
        while fetch_since < now:
            ohlcv = self.retry_fetch_ohlcv(exchange, max_retries, symbol, timeframe, fetch_since, limit)
            fetch_since = (ohlcv[-1][0] + 1) if len(ohlcv) else (fetch_since + timedelta)
            all_ohlcv = all_ohlcv + ohlcv
            if len(all_ohlcv):
                print(len(all_ohlcv), 'candles in total from', exchange.iso8601(all_ohlcv[0][0]), 'to', exchange.iso8601(all_ohlcv[-1][0]))
            else:
                print(len(all_ohlcv), 'candles in total from', exchange.iso8601(fetch_since))
        return exchange.filter_by_since_limit(all_ohlcv, since, None, key=0)


    def write_to_csv(self, filename, data):
        with open(filename, mode='a') as output_file:
            csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerows(data)


    def scrape_candles_to_csv(self, filename, exchange, max_retries, symbol, timeframe, since, limit):
        # fetch all candles
        ohlcv = self.scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)
        # save them to csv file
        self.write_to_csv(filename, ohlcv)
        print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]), 'to', filename)


    def find_cointegrated_pairs(self, data):
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

    
    def crossing(self, x, y):
        wtCross = []
        for i in range(len(x)):
            # check if the value wt1 is greater than wt2 AND less than the previous row OR the opposite for crossing down
            if(x.iloc[i] > y.iloc[i] and x.iloc[i-1] < y.iloc[i-1]) | (x.iloc[i] < y.iloc[i] and x.iloc[i-1] > y.iloc[i-1]):
                wtCross.append(True)
            else:
                wtCross.append(False)
        return wtCross

    # TODO: Make this function return a series of buy or sell values for a dataframe
    def calculateWaveTrend(self, src):
        chlen = 9
        avg = 12
        malen = 3
        oslevel = -53
        oblevel = 53


        tfSrc = src.copy(deep=True)

        HLC3 = (tfSrc.iloc[:, 2] + tfSrc.iloc[:, 3] + tfSrc.iloc[:, 4]) / 3

        # ESA = Exponential Moving Average
        ESA = HLC3.ewm(span=chlen, adjust=False).mean()

        # de = ema(abs(tfsrc - esa), chlen)
        DE = abs(HLC3 - ESA).ewm(span=chlen, adjust=False).mean()

        # ci = (tfsrc - esa) / (0.015 * de)
        CI = (HLC3 - ESA) / (0.015 * DE)
        # wt1 = security(syminfo.tickerid, tf, ema(ci, avg))
        WT1 = CI.ewm(span=avg, adjust=False).mean()
        # wt2 = security(syminfo.tickerid, tf, sma(wt1, malen))
        WT2 = WT1.rolling(malen).mean()
        WTVWAP = WT1 - WT2
        WTOVERSOLD = WT1 <= oslevel
        WTOVERBOUGHT= WT2 >= oblevel
        # see crossing(x, y) function
        WTCROSS = self.crossing(WT1, WT2)
        # determines if the cross above is bullish by being <= 0
        WTCROSSUP = WT2 - WT1 <= 0
        # determines if the cross above is bearish by being <= 0
        WTCROSSDOWN= WT2 - WT1 >= 0
        # see crossing(x, y) function (passing the series shifted to determine if the last row was a cross)
        WTCROSSLAST = self.crossing(WT1.shift(-1), WT2.shift(-1))
        WTCROSSUPLAST = WT2.shift(-1) - WT1.shift(-1) <= 0
        WTCROSSDOWNLAST= WT2.shift(-1) - WT1.shift(-1) >= 0
        # Buy signal.
        tfSrc['Buy'] = WTCROSS & WTCROSSUP & WTOVERSOLD
        # Sell signal
        tfSrc['Sell'] = WTCROSS & WTCROSSDOWN & WTOVERBOUGHT

        tfSrc.drop(tfSrc.head(50).index, inplace=True)
        # return the waveTrend DataFrame or return the last minute
        return (tfSrc)


    def scrape_candles(self, max_retries, timeframe, since, limit):
        """
        Pulls new candle data for timeframe on each symbol passed. It will check if there exists data for the symbol, if so, pull that file, 
        and update it with the latest candle information. It does not let you call it until the last timeframe you called closes,
        ex: 1m timeframe call must wait 1m for new candle data to call function again. 

        Return: Dataframe for each symbol
        
        """

        from os.path import exists

        # List of OHLCV dataframes indexed by their time
        dataframes = [] 
        df_columns = ['time', 'open', 'high', 'low', 'close', 'volume']

        # We must create a global var for the function or whatever bc it turns into a None Type after one iteration of the exchange loop.
        self.since = since
        if isinstance(since, str):
            for exchange in self.exchanges:
                # Set a temp var for each exchange bc the second one in the loop gets lost, idk y
                since = exchange.parse8601(self.since)
                tf = exchange.parse_timeframe(timeframe)
                for symbol in self.symbols:
                    sym = symbol.replace('/', '').lower()
                    file = f'CSV\\{exchange}-{sym}-{timeframe}.csv'
                    if(exists(file)):
                        df = pd.read_csv(file)
                        df.columns = df_columns
                        since = df['time'].iloc[-1]
                        wait_time = (exchange.milliseconds() - since) / 1000
                        if not (wait_time) <= tf:
                            # fetch all the new candles
                            ohlcv = self.scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)

                            # Remove the last row because we will rewrite it
                            ohlcv.pop(0)
                            print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]))

                            # Write the data to the file before we make it into a dataframe
                            self.write_to_csv(file, ohlcv)

                            # Convert to dataframe
                            ohlcv = pd.DataFrame(ohlcv, columns=df_columns)

                            # Append the concatinated result of the original df and the new data to dataframes list
                            dataframes.append(pd.concat([df, ohlcv]))
                        else:
                            print(f"Time till next candle close: {wait_time}s, {float(wait_time / 60).__round__(2)}m, {float(wait_time / 60 / 60).__round__(2)}h, {float(wait_time / 60 / 60 / 24).__round__(2)}d.")
                            dataframes.append(df)
                    else:

                        # fetch all candles
                        ohlcv = self.scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)
                        # save them to csv file
                        print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]))
                        self.write_to_csv(file, ohlcv)
                        dataframes.append(pd.DataFrame(ohlcv, columns=df_columns))
        self.since = None
        return dataframes



scrape = Scrape(['binance'], ['BTC/USDT'])
pepe = PepeFramework()
df = scrape.scrape_candles(3, '1m', "2022-10-04T00:00:00Z", 1000)
print(scrape.calculateWaveTrend(df[0]))