import csv
import ccxt.async_support as ccxt  # noqa: E402
import asyncio
import pandas as pd
import numpy as np
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


    # Old scrape candles function
    def scrape_candles(self, max_retries:int, symbol: str, timeframe: str, since: str, limit: int):
        """
        Pulls new candle data for timeframe on each symbol passed. It will check if there exists data for the symbol, if so, pull that file, 
        and update it with the latest candle information. It the latest candle in the timeframe requested is not closed, it will return what's
        on the CSV file.

        Return: Dataframe for each symbol
        
        """

        from os.path import exists

        # List of OHLCV dataframes indexed by their time
        dataframes = [] 

        # We must create a global var for the function or whatever bc it turns into a None Type after one iteration of the exchange loop.
        self.since = since
        if isinstance(since, str):
            # Set a temp var for each exchange bc the second one in the loop gets lost, idk y
            since = self.api.parse8601(self.since)

            # Get the timeframe in seconds
            tf = self.api.parse_timeframe(timeframe)
            # Loop through symbols
            # Create the file object for each CSV file
            sym = symbol.replace('/', '').lower()
            file = f'CSV\\{str(self.exchange).replace(" ", "").lower()}-{sym}-{timeframe}.csv'
            print(file)
            # If it exists 
            if(exists(file)):
                # Read the dataframe stuff
                df = pd.read_csv(file)
                # Assign the columns and index
                # Grab the last timeframe candle
                since = df['time'].iloc[-1]

                # Set the wait time to candle close, because we can't request data for new candle until it closes
                wait_time = (self.api.milliseconds() - since) / 1000

                # If a new candle has closed already
                if not (wait_time) <= tf:
                    # fetch all the new candles
                    ohlcv = self.scrape_ohlcv(self.api, max_retries, symbol, timeframe, since, limit)

                    # Remove the last row because we will rewrite it
                    ohlcv.pop(0)
                    print('Saved', len(ohlcv), 'candles from', self.api.iso8601(ohlcv[0][0]), 'to', self.api.iso8601(ohlcv[-1][0]))

                    # Write the data to the file before we make it into a dataframe
                    self.write_to_csv(file, ohlcv)

                    # Convert to dataframe
                    ohlcv = pd.DataFrame(ohlcv)

                    # Append the concatinated result of the original df and the new data to dataframes list
                    dataframes.append(pd.concat([df, ohlcv]))
                else:
                    # If we need more time for a new candle to close tell them how long and pass the opened CSV files
                    print(f"Time till next candle close: {wait_time}s, {float(wait_time / 60).__round__(2)}m, {float(wait_time / 60 / 60).__round__(2)}h, {float(wait_time / 60 / 60 / 24).__round__(2)}d.")
                    dataframes.append(df)
            else:

                # fetch all candles
                ohlcv = self.scrape_ohlcv(max_retries, symbol, timeframe, since, limit)
                # save them to csv file
                print('Saved', len(ohlcv), 'candles from', self.api.iso8601(ohlcv[0][0]), 'to', self.api.iso8601(ohlcv[-1][0]))
                self.write_to_csv(file, ohlcv)
                dataframes.append(pd.DataFrame(ohlcv))
        self.since = None
        return dataframes



scrape = Scrape(['binance', 'ftx', 'coinbasepro', 'bitfinex'], ['BTC/USDT', 'ETH/USDT'])
pepe = PepeFramework()
df = scrape.scrape_candles(3, '1d', "2017-01-01T00:00:00Z", 200)
pepe.plot_ohlcv_plotly(df[3])




class Exchange():
    def __init__(self, exchanges) -> None:
        self.api = self.init_exchanges(exchanges)


    def init_exchanges(self, exchanges):
        apis = {}  # a placeholder for your instances
        for id in exchanges:
            exchange = getattr(ccxt, id)
            apis[id] = exchange()
        return apis


    async def get_orderbook(self, symbol):
        results = {}
        for exchange in self.api.keys():
            orderbook = await self.fetch_orderbook(self.api[exchange], symbol)  # ←------ STEP 3

            await self.api[exchange].close()  # ←----------- LAST STEP GOES AFTER ALL CALLS
            results[exchange] = orderbook
        return results


    async def fetch_orderbook(self, exchange, symbol):
        try:
            result = await exchange.fetch_order_book(symbol)
            return result
        except ccxt.BaseError as e:
            print(type(e).__name__, str(e), str(e.args))
            raise e

    def test_call():
        exchanges = ['binance', 'ftx', 'coinbasepro', 'kucoin', 'gateio']

        exchange = Exchange(exchanges)
        results = asyncio.run(exchange.get_orderbook('BTC/USDT'))
        print([(exchange_id, ticker) for exchange_id, ticker in results.items()])