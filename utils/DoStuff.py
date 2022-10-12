import pandas as pd
import numpy as np

from statsmodels.tsa.stattools import coint

class DoStuff():

    def get_roe(self, close_values: pd.Series, quantity: float):
        return float((close_values.iat[-1] - close_values.iat[0]) * quantity).__round__(3)


    def get_time_in_past(self, minutes: float, days:float):
        from datetime import datetime, timedelta
        then = (datetime.now() - timedelta(days = days, minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S").replace(" ", "T")
        return f'{then}Z'



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