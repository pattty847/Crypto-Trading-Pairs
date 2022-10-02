# -*- coding: utf-8 -*-

import os
import sys
import csv
from time import time

from pyparsing import col

# -----------------------------------------------------------------------------

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root + '/python')

import ccxt  # noqa: E402
import pandas as pd


# -----------------------------------------------------------------------------
class Scrape():
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
        with open(filename, mode='w') as output_file:
            csv_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_writer.writerows(data)


    def scrape_candles_to_csv(self, filename, exchange_id, max_retries, symbol, timeframe, since, limit):
        # instantiate the exchange by id
        exchange = getattr(ccxt, exchange_id)()
        # convert since from string to milliseconds integer if needed
        if isinstance(since, str):
            since = exchange.parse8601(since)
        # preload all markets from the exchange
        exchange.load_markets()
        # fetch all candles
        ohlcv = self.scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)
        # save them to csv file
        self.write_to_csv(filename, ohlcv)
        print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]), 'to', filename)


    def scrape_orders_to_csv(self, filename, symbol, since, exchange_):
        exchange = getattr(ccxt, exchange_)()
        one_hour = 3600 * 1000
        since = exchange.parse8601(since)
        now = exchange.milliseconds()
        end = exchange.parse8601(exchange.ymd(now) + 'T00:00:00')
        previous_trade_id = None

        with open(filename, mode="w") as csv_f:
            csv_writer = csv.DictWriter(csv_f, delimiter=",", fieldnames=["timestamp", "size", "price", "side"])
            csv_writer.writeheader()
            while since < end:
                try:
                    trades = exchange.fetch_trades(symbol, since)
                    print(exchange.iso8601(since), len(trades), 'trades')
                    if len(trades):
                        last_trade = trades[-1]
                        if previous_trade_id != last_trade['id']:
                            since = last_trade['timestamp']
                            previous_trade_id = last_trade['id']
                            for trade in trades:
                                if trade['amount'] > 20:
                                    csv_writer.writerow({
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
                    exchange.sleep(60000)


    def scrape_candles_to_df(self, exchange_id, max_retries, symbol, timeframe, since, limit):
        from os.path import exists

        file = symbol.replace('/', '').lower() + '-candles-' + timeframe + '.csv'
        columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        print(file)
        if(exists(file)):
            df = pd.read_csv(file)
            df.columns = columns
            since = df['time'].iloc[-1]

            # instantiate the exchange by id
            exchange = getattr(ccxt, exchange_id)()
            # convert since from string to milliseconds integer if needed
            if isinstance(since, str):
                since = exchange.parse8601(since)

            # preload all markets from the exchange
            exchange.load_markets()

            # fetch all candles
            ohlcv = self.scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)
            ohlcv.pop(0)
            if ohlcv[-1][0]:
                # save them to csv file
                print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]))
            self.write_to_csv(file, ohlcv)

            ohlcv = pd.DataFrame(ohlcv, columns=columns)
            return pd.concat([df, ohlcv])
        else:
            # instantiate the exchange by id
            exchange = getattr(ccxt, exchange_id)()
            # convert since from string to milliseconds integer if needed
            if isinstance(since, str):
                since = exchange.parse8601(since)
            # preload all markets from the exchange
            exchange.load_markets()
            # fetch all candles
            ohlcv = self.scrape_ohlcv(exchange, max_retries, symbol, timeframe, since, limit)
            # save them to csv file
            print('Saved', len(ohlcv), 'candles from', exchange.iso8601(ohlcv[0][0]), 'to', exchange.iso8601(ohlcv[-1][0]))
            self.write_to_csv(file, ohlcv)
            return pd.DataFrame(ohlcv, columns=columns)