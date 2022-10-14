import pandas as pd
import pandas_ta as pta
import numpy as np
from statsmodels.tsa.stattools import coint, adfuller

class DoStuff():

    def get_roe(self, close_values: pd.Series, quantity: float):
        return float((close_values.iat[-1] - close_values.iat[0]) * quantity).__round__(3)


    def get_time_in_past(self, minutes: float, days:float):
        from datetime import datetime, timedelta
        then = (datetime.now() - timedelta(days = days, minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S").replace(" ", "T")
        return f'{then}Z'


    def zscore(self, series):
        return (series - series.mean()) / pta.stdev(series)



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