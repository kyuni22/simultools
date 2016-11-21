import numpy as np
import pandas as pd

def price_backtest(prices, weights, capital, offset=1., commission=0.):
    '''

    :param returns: pandas DataFramee. Header of returns should be same with that of weights
    :param weights: pandas DataFramee. Header of weights should be same with that of returns
    :param capital:
    :param offset:
    :param commission:
    :return:
    '''
    p_holdings = (capital / prices * weights.align(prices)[0]).shift(offset).ffill().fillna(0) # Holdings in share
    w = weights.align(prices)[0].shift(offset).fillna(0)
    trade_dates = w[w.sum(1) != 0].index
    p_cash = capital - (p_holdings * prices.shift(offset)).sum(1)
    totalcash = p_cash[trade_dates].align(prices[prices.columns[0]])[0].ffill().fillna(0)
    p_returns = (totalcash + (p_holdings * prices).sum(1) - \
                 (abs(p_holdings - p_holdings.shift(1)) * commission).sum(1)) / \
                (totalcash + (p_holdings * prices.shift(1)).sum(1)) - 1
    p_returns = p_returns.fillna(0)

    p_weights = pd.DataFrame([(p_holdings * prices.shift(offset))[symbol] / \
                              (totalcash + (p_holdings * prices.shift(offset)).sum(1)) \
                              for symbol in prices.columns], index=prices.columns).T
    p_weights = p_weights.fillna(0) # return adjust weight

    return np.cumproduct(1. + p_returns) * capital, p_holdings, p_returns, p_weights

def return_backtest(returns, weights, offset=1., commission=0.):
    '''

    :param returns: pandas DataFramee. Header of returns should be same with that of weights
    :param weights: pandas DataFramee. Header of weights should be same with that of returns
    :param offset:
    :param commission:
    :return:
    '''
    prices = (1.0 + returns).cumprod()
    p_holdings = (1.0 / prices * weights.align(prices)[0]).shift(offset).ffill().fillna(0) # Holdings in share
    w = weights.align(prices)[0].shift(offset).fillna(0)
    trade_dates = w[w.sum(1) != 0].index
    p_cash = 1.0 - (p_holdings * prices.shift(offset)).sum(1)
    totalcash = p_cash[trade_dates].align(prices[prices.columns[0]])[0].ffill().fillna(0)
    p_returns = (totalcash + (p_holdings * prices).sum(1) - \
                 (abs(p_holdings - p_holdings.shift(1)) * commission).sum(1)) / \
                (totalcash + (p_holdings * prices.shift(1)).sum(1)) - 1
    p_returns = p_returns.fillna(0)

    p_weights = pd.DataFrame([(p_holdings * prices.shift(offset))[symbol] / \
                              (totalcash + (p_holdings * prices.shift(offset)).sum(1)) \
                              for symbol in prices.columns], index=prices.columns).T
    p_weights = p_weights.fillna(0) # return adjust weight

    return np.cumproduct(1. + p_returns), p_holdings, p_returns, p_weights