import numpy as np

class Analyze():

    def __init__(self):
        self.buy = dict()
        self.sell = dict()

        self.delta = 0

    def set_delta(self, data):
        print(data)
        ticker = data['s']
        if data['m'] == False:
            if not self.buy:
                self.buy[ticker] = np.multiply(float(data['p']), float(data['q']))
            else:
                self.buy[ticker] = self.buy[ticker] + np.multiply(float(data['p']), float(data['q']))
        else:
            if not self.sell:
                self.sell[ticker] = np.multiply(float(data['p']), float(data['q']))
            else:
                self.sell[ticker] = self.sell[ticker] + np.multiply(float(data['p']), float(data['q']))

        delta = float(self.buy[ticker] - self.sell[ticker]).__round__(2)
        print(ticker + " | Delta: " + str(delta))