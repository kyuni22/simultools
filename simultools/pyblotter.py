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
            # if there's no position, skip.
            if self.eq.ix[currDate, symbol] != 0.0 or self.txns.ix[currDate, symbol] != 0.0:
                # if any position exist for this symbol before, then eq should be multiplyied by return of symbol
                # return of symbol for today is return from previous day to today
                self.eq.ix[currDate, symbol] = self.eq.ix[currDate, symbol] * (1.0 + value[symbol])
                # Check if transaction occur
                before_txns = self.eq.ix[currDate, symbol]
                if self.txns.ix[currDate, symbol] != shifted_txns.ix[currDate, symbol]:
                    """
                    Cases: same logic can be applied to case 1, 2
                    1. Sell all existing position
                    2. Sell partial existing position
                    3. add to existing position
                    """
                    # case 3, add to eq
                    if self.txns.ix[currDate, symbol] > shifted_txns.ix[currDate, symbol]:
                        self.eq.ix[currDate, symbol] = before_txns + (self.txns.ix[currDate, symbol] - shifted_txns.ix[currDate, symbol])
                        self.eq.ix[currDate, 'Cash'] = self.eq.ix[currDate, 'Cash'] - (self.txns.ix[currDate, symbol] - shifted_txns.ix[currDate, symbol])
                    # case 1, 2
                    else :
                        if self.txns.ix[currDate, symbol] < shifted_txns.ix[currDate, symbol]:
                            self.eq.ix[currDate, symbol] = before_txns + before_txns * (self.txns.ix[currDate, symbol] - shifted_txns.ix[currDate, symbol]) / shifted_txns.ix[currDate, symbol]
                            self.eq.ix[currDate, 'Cash'] = self.eq.ix[currDate, 'Cash'] + before_txns - self.eq.ix[currDate, symbol]

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