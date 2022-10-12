import pandas as pd
import pandas_ta as pta

class PTA():
    def __init__(self) -> None:
        pass


    def get_wells_ma(self, src, period):
        alpha = 1 / period
        WM = 0.0
        # WM := alpha*src + (1-alpha)*(WM[1])