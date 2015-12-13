# -*- coding: utf-8 -*-
"""
pyblotter for backtesting
"""

import numpy as np
from pandas import DataFrame

class Account:
    def __init__(self, initDatetime, symbols, cashAmt, acctType='return'):
        """
        input
        initDate is start date of simulation
        symbols is list of universe for simulation
        
        variables
        txns is DataFrame which contains tranaction history
        eq is DataFrame which contains current value of account
        
        For initial implementation, this class only values account based on return data of security. 
        Valuing account with price of security will be implemented later.
        """
        self.txns = DataFrame(np.zeros((1,len(symbols))), index = [initDatetime], columns=symbols)
        self.eq = DataFrame(np.zeros((1,len(symbols)+1)), index = [initDatetime], columns=['Cash'] + symbols)
        self.eq.ix[initDatetime, 'Cash'] = cashAmt
        self.accType = acctType

    def addTxnDate(self, txnDate):
        """
        add one row for txns and eq with index as txnDate
        """
        self.txns.ix[txnDate] = self.txns.tail(1).values.reshape([len(self.txns.columns),])
        self.eq.ix[txnDate] = self.eq.tail(1).values.reshape([len(self.eq.columns),])
        
    def addTxn(self, txnDate, symbol, txnAmt):
        """
        addTxn add transaction data to txns DataFrame
        """
        self.txns.ix[txnDate, symbol] = self.txns.ix[txnDate, symbol] + txnAmt
    
    def updateAcct(self, currDate, value):
        """
        update account based on market data.
        value is market data dataframe containing either return or price data
        
        Transaction cost should be implemented here. many options should be considered.
        """
        shifted_txns = self.txns.shift(1)
        # for each symbol in txns
        for symbol in self.txns.columns:
            """
            Cases                   
            1. no position before and after - skip
            2. there was position or position change
                2-1. no position before, new position
                2-2. position before, either close out or adjust position
            """
            # Case 1. if there's no position, skip.
            # Case 2.
            if shifted_txns.ix[currDate, symbol] != 0.0 or self.txns.ix[currDate, symbol] != 0.0:
                #2-1. no position before, new position
                if shifted_txns.ix[currDate, symbol] == 0.0:
                    # position long or short
                    self.eq.ix[currDate, symbol] = self.txns.ix[currDate, symbol]
                    self.eq.ix[currDate, 'Cash'] = self.eq.ix[currDate, 'Cash'] - self.txns.ix[currDate, symbol]
                else:
                    #2-2. position before, either close out or adjust position
                    # if any position exist for this symbol before, then eq should be multiplyied by return of symbol
                    # NOTE: return of symbol for today is return from previous day to today
                    self.eq.ix[currDate, symbol] = self.eq.ix[currDate, symbol] * (1.0 + value[symbol])
                    # if position changed
                    if self.txns.ix[currDate, symbol] != shifted_txns.ix[currDate, symbol]:
                        before_txns_eq = self.eq.ix[currDate, symbol]
                        self.eq.ix[currDate, symbol] = before_txns_eq + before_txns_eq * (self.txns.ix[currDate, symbol] - shifted_txns.ix[currDate, symbol]) / shifted_txns.ix[currDate, symbol]
                        self.eq.ix[currDate, 'Cash'] = self.eq.ix[currDate, 'Cash'] + before_txns_eq - self.eq.ix[currDate, symbol]

    def getEq(self, currDate):
        """
        get equity value of account at current date(currDate)
        """
        return self.eq.ix[currDate].sum()
    def getPos(self, currDate, symbol):
        """
        get position information of symbol
        """
        return self.txns.ix[currDate, symbol]
    def getUniverse(self):
        """
        get list of all symbols in universe
        """
        return list(self.eq.columns[1:])
    def getEqCurve(self):
        """
        get equty curve of account
        """
        return self.eq.sum(axis=1)