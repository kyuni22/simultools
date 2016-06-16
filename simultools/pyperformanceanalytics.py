# -*- coding: utf-8 -*-
"""
PerformanceAnalytics for backtesting
"""

import numpy as np
from pandas import Series
import matplotlib.pyplot as plt

class PerformanceAnalytics():
    def __init__(self, daily_ret):
        """
        Get daily return for cum_ret and dd
        """
        # daily ret
        self.daily_ret = daily_ret
        # Equity Curve Series
        self.cum_ret = daily_ret.fillna(0).cumsum()
        # Drawdown Seriesfa
        self.dd = self.cum_ret - self.cum_ret.cummax()

    def getCumRet(self):
        return self.cum_ret

    def getDD(self):
        return self.dd

    def describe(self):
        return self.daily_ret[self.daily_ret!=0].describe()

    def hist(self, bin_unit):
        bins = np.arange(min(self.daily_ret),max(self.daily_ret)+bin_unit, bin_unit)
        self.daily_ret[self.daily_ret!=0].hist(bins=bins)
    
    def measures(self, annualize_factor=1.0):
        measures = {}
        measures['Avg PL'] = self.daily_ret.mean() * annualize_factor
        measures['Stdev'] = self.daily_ret.std() * np.sqrt(annualize_factor)
        measures['Sharpe Ratio'] = measures['Avg PL'] / measures['Stdev']
        measures['MDD'] = self.dd.min()
        measures['Hit Rate'] = self.daily_ret[self.daily_ret>0].count()*1.0 / (self.daily_ret[self.daily_ret<=0].count()+self.daily_ret[self.daily_ret>0].count())*1.0        
        
        return Series(measures)

    def getOtherDDInfo(self):
        timetogain = [0]
        consecloss = [0]
        for i, item in enumerate(self.dd.iteritems()):
            if i > 0 :
                if self.dd[i] >= 0:
                    timetogain.append(0)
                    consecloss.append(0)
                elif self.dd[i] < self.dd[i-1]:
                    timetogain.append(timetogain[i-1] + 1)
                    consecloss.append(consecloss[i-1] + 1)
                elif self.dd[i] >= self.dd[i-1]:
                    timetogain.append(timetogain[i-1] + 1)
                    consecloss.append(0)
        
        timetogain = Series(timetogain, index=self.dd.index)
        consecloss = Series(consecloss, index=self.dd.index)
        return timetogain, consecloss

# heatmap for changing 2 variables
def heatmap(df, cmap=plt.cm.gray_r):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    axim = ax.imshow(df.values, cmap=cmap, interpolation='nearest')
    ax.set_xlabel(df.columns.name)
    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_xticklabels(list(df.columns))
    ax.set_ylabel(df.index.name)
    ax.set_yticks(np.arange(len(df.index)))
    ax.set_yticklabels(list(df.index))
    plt.colorbar(axim)
    

def get_intraday_stop_ret(daily_ret, MAE_ret, stop_lv, overnight_pl=None):
    '''
    Maximum Adverse Excusion (MAE) is max loss from one entered position
    Stop Level (stop_lv) is loss where you want to exit
    other cost would be added later
    '''
    daily_ret = daily_ret
    MAE_ret = MAE_ret
    if overnight_pl is not None:
        stop_lv = Series(np.where(overnight_pl < stop_lv, overnight_pl, stop_lv), index=daily_ret.index)
    return Series(np.where(MAE_ret < stop_lv, stop_lv, daily_ret), index=daily_ret.index)