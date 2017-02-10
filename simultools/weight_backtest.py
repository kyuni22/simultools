import numpy as np
import pandas as pd

def price_backtest(prices, weights, capital, offset=1., commission=0.):
    '''
    Get this function from Github.
    :param returns: pandas DataFramee. Header of prices should be same with that of weights
    :param weights: pandas DataFramee. Header of weights should be same with that of returns
    :param capital: Amount invested
    :param offset: time steps from weight change date
    :param commission: trade commission per share
    :return: equity curve, number of share per securities, daily return in %, real weight including total cash
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
    Re-write function for my own use.
    Commission logic is wrong. Different time step should be applied to take and exit the position.
    It is impossible to implement it with matrix backtesting logic. This will be changed if I find better way.
    :param returns: daily return of all securities, pandas.DataFrame
    :param weights: weights of all securities, pandas.DataFrame
    :param offset: time steps after weight change. must be greater than 1?
    :param commission: commission in %
    :return: cumulative return equity curve, number of share per securities, daily return in %, real weight including total cash
    '''
    prices = (1.0 + returns).cumprod()  # make price dataframe
    p_holdings = (1.0 / prices * weights.align(prices)[0]).shift(offset).ffill().fillna(0)  # Holdings in share
    totalcash = (1.0 - weights.sum(1)).align(prices[prices.columns[0]])[0].shift(offset).ffill().fillna(0)
    p_returns = (totalcash + (p_holdings * prices).sum(1) - \
                 (abs(p_holdings - p_holdings.shift(1)) * prices.shift(1) * commission).sum(1)) / \
                (totalcash + (p_holdings * prices.shift(1)).sum(1)) - 1.
    p_returns = p_returns.fillna(0)

    p_weights = pd.DataFrame([(p_holdings * prices.shift(offset))[symbol] / \
                              (totalcash + (p_holdings * prices.shift(offset)).sum(1)) \
                              for symbol in prices.columns], index=prices.columns).T
    p_weights = p_weights.fillna(0) # unnecessary but left it for consistency

    return np.cumproduct(1. + p_returns), p_holdings, p_returns, p_weights

def groupby_backtest(returns, qcut_signal_data):
    """

    :param returns:
    :param qcut_signal_data:
    :return:
    """
    simul_data = qcut_signal_data.merge(returns, left_on=['tdate', 'code'], right_on=['tdate', 'code'])
    simul_data = simul_data[sorted(simul_data.columns)]
    simul_data.columns = ['code', 'tdate', 'sig', 'ret']
    grouped_simul_val = simul_data.groupby(['tdate', 'sig'])
    return grouped_simul_val.mean().unstack()