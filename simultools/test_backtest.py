# -*- coding: utf-8 -*-

import unittest
import pandas_datareader.data as web
import datetime as dt

from simultools.weight_backtest import return_backtest, price_backtest

class Test_weight_backtest(unittest.TestCase):
    def setUp(self):
        self.spy = web.DataReader('SPY', 'yahoo', dt.datetime(2000,1,1), dt.datetime(2010,12,30))
        self.spy['Low'] = self.spy['Low'] * self.spy['Adj Close'] / self.spy['Close']
        self.signal = self.spy['Adj Close'].shift(1) < self.spy['Low']
        self.result_to_compare = (1. + self.signal * self.spy['Adj Close'].pct_change(1).shift(-1)).shift(1).cumprod()

    def test_return_backtest(self):
        returns, p_holdings, p_returns, p_weights = return_backtest(self.spy['Adj Close'].pct_change(1).to_frame('spy'),
                                                                    (self.signal * 1.).to_frame('spy'), offset=1., commission=0.)
        print returns[-1], self.result_to_compare[-1]


    def test_price_backtest(self):
        returns, p_holdings, p_returns, p_weights = price_backtest(self.spy['Adj Close'].to_frame('spy'),
                                                                     (self.signal * 1.).to_frame('spy'), 1000000., offset=1.,
                                                                     commission=0.)
        print(returns[-1])


if __name__ == '__main__':
    unittest.main()