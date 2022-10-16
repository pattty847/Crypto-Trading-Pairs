import pandas as pd
import pandas_ta as pta
import numpy as np
import dearpygui.dearpygui as dpg

from statsmodels.tsa.stattools import coint, adfuller

class DoStuff():

    def get_roe(self, close_values: pd.Series, quantity: float):
        return float((close_values.iat[-1] - close_values.iat[0]) * quantity).__round__(3)


    def get_time_in_past(self, days, month, year):
        import datetime
        year_ = str(year)
        y = int(f'20{year_[1:]}') # can't figure it out this will have to do until 2100 or I figure it out
        x = datetime.datetime(y, month, days)
        y2 = x.strftime("%Y-%m-%dT%H:%M:%S%Z")
        print(y2)
        return y2


    def zscore(self, series):
        return (series - series.mean()) / pta.stdev(series)



    def convert_timeframe(self, tf):
        match (tf[len(tf) - 1]):
            case 's':
                return dpg.mvTimeUnit_S
            case 'm':
                return dpg.mvTimeUnit_Min
            case 'h':
                return dpg.mvTimeUnit_Hr
            case 'd':
                return dpg.mvTimeUnit_Day
            case 'M':
                return dpg.mvTimeUnit_Mo
            case _:
                dpg.mvTimeUnit_Day



    def candles_to_list(self, candles):
        dates = list(candles['date']/1000)
        opens = list(candles['open'])
        closes = list(candles['close'])
        lows = list(candles['low'])
        highs = list(candles['high'])
        return (dates, opens, closes, lows, highs)



    def find_cointegrated_pairs(self, data: pd.DataFrame, pvalue_filter: float):
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
                if pvalue < pvalue_filter:
                    pairs.append((keys[i], keys[j]))
        return (score_matrix, pvalue_matrix, pairs)