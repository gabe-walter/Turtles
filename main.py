import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from copy import deepcopy, copy
from datetime import date

class Turtle:
    
    def __init__(self, tickers, initial_balance = 100000, start="2000-01-01", end=str(date.today())):
        self.tickers = tickers
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.cash = initial_balance
        self.start = start
        self.end = end
        self.last_win = {t: False for t in self.tickers}
        self.unit_limit = 4
        
        self.data = self._get_and_prepare_data()
        
    def _get_and_prepare_data(self):
        yfObj = yf.Tickers(self.tickers)
        df = yfObj.history(start = self.start, end = self.end)
        df.drop(['Open', 'Dividends', 'Stock Splits', 'Volume'], inplace = True, axis = 1)
        df.ffill(inplace = True)
        df = df.swaplevel(axis = 1)
        
        for ticker in self.tickers:
            # Breakouts for enter long position (EL), exit long (ExL), enter short (ES), exit short (ExS)
            df[ticker, 'EL'] = df[ticker]['Close'].rolling(20).max()
            df[ticker, 'ExL'] = df[ticker]['Close'].rolling(20).min()
            df[ticker, 'ES'] = df[ticker]['Close'].rolling(20).min()
            df[ticker, 'ExS'] = df[ticker]['Close'].rolling(20).max()
            
            #Compute N for all datapoints
            N = df[ticker].apply(lambda r: abs(max(r["High"]-r["Low"], r["Close"]-r["Low"], r["Low"]-r["Close"])), axis = 1)
            df[ticker, "N"] = N.rolling(20).mean()
            
        return df
    
    def _scale_risk(self, units):
        #Scale down sizing for every 10% of original account balance lost
        percent_loss = 1 - self.current_balance/self.initial_balance
        if percent_loss > 0.1:
            scale_by = np.floor(percent_loss/0.1)
            units *= 1 - scale_by * 0.2
        return units

    def _cash_check(self, shares, price):
        if self.cash <= shares * price:
            shares = np.floor(self.cash/price)
        return shares
    
    def _get_port_value(self, port):
        pv = 0
        for v0 in port.values():
            if isinstance(v0, dict):
                pv += v0.get('value', 0)
        pv += self.cash
        if np.isnan(pv):
            raise ValueError(f"PV = {pv}\n{port}")
        return pv
    
    def _get_units(self):
        dollar_units = 0.02 * self.current_balance
        dollar_units = self._scale_risk(dollar_units)
        return dollar_units
    
    def _get_position_size(self, data, dollar_units):
        shares = np.floor(dollar_units / (data['N'] * data['Close']))
        return shares
    
    def _run(self, ticker, data, position):
        price = data['Close']
        if np.isnan(price):
            # Return current position in case of missing data
            return position
        dollar_units = self._get_units()
        N = data['N']
        shares =  0
        if position is None:
            if price == data["EL"]: # Buy on breakout
                if self.last_win[ticker]:
                    self.last_win[ticker] = False
                    return None
                shares = self._get_position_size(data, dollar_units)
                stop_price = price - 2 * N
                long = True
            elif price == data["ES"]: # Sell short
                if self.last_win[ticker]:
                    self.last_win[ticker] = False
                    return None
                shares = self._get_position_size(data, dollar_units)
                stop_price = price + 2 * N
                long = False
            else:
                return None
            if shares == 0:
                return None
            
            shares = self._cash_check(shares, price)
            value = price * shares
            self.cash -= value
            
            position = {'units': 1,
                  'shares': shares,
                  'entry_price': price,
                  'stop_price': stop_price,
                  'entry_N': N,
                  'value': value,
                  'long': long}
        else:
            if position['long']:
            # Check to exit existing long position
                if price == data["ExL"] or price <= position['stop_price']:
                    self.cash += position['shares'] * price
                    if price >= position['entry_price']:
                        self.last_win[ticker] = True
                    else:
                        self.last_win[ticker] = False
                    position = None
                    
                # Check to pyramid existing position
                elif position['units'] < self.unit_limit:
                    if price >= position['entry_price'] + position['entry_N']:
                        shares = self._get_position_size(data, dollar_units)
                        shares = self._cash_check(shares, price)
                        self.cash -= shares * price
                        stop_price = price - 2 * N
                        avg_price = (position['entry_price'] * position['shares'] +
                                     shares * price) / (position['shares'] + shares)
                        position['entry_price'] = avg_price
                        position['shares'] += shares
                        position['stop_price'] = stop_price
                        position['units'] += 1
            
            else:
            # Check to exit existing short position
                if price == data["ExS"] or price >= position['stop_price']:
                    self.cash += position['shares'] * price    
                    if price <= position['entry_price']:
                        self.last_win[ticker] = True
                    else:
                        self.last_win[ticker] = False
                    position = None
                # Check to pyramid existing position
                elif position['units'] < self.unit_limit:
                    if price <= position['entry_price'] - position['entry_N']:
                        shares = self._get_position_size(data, dollar_units)
                        shares = self._cash_check(shares, price)
                        self.cash -= shares * price
                        stop_price = price + 2 * N
                        avg_price = (position['entry_price'] * position['shares'] +
                                     shares * price) / (position['shares'] + shares)
                        position['entry_price'] = avg_price
                        position['shares'] += shares
                        position['stop_price'] = stop_price
                        position['units'] += 1
            
            
            if position is not None:
                # Update value at each time step
                position['value'] = position['shares'] * price
                
        return position   
    
    
    def backtest(self):
        self.portfolio = {}
        position = {t: None for t in self.tickers}

        for i, (ts, row) in enumerate(self.data.iterrows()):
            for t in self.tickers:
                position[t] = self._run(t, row[t], position[t])
            self.portfolio[i] = deepcopy(position)
            self.portfolio[i]['date'] = ts
            self.portfolio[i]['cash'] = copy(self.cash)
            self.current_balance = self._get_port_value(self.portfolio[i])      
            
    def get_portfolio_history(self):
        return self.portfolio
    
    def get_portfolio_values(self):
        vals = []
        for obj in self.portfolio.values():
            pv = 0
            pv += obj["cash"]
            for obj2 in obj.values():
                if isinstance(obj2, dict):
                    pv += obj2["value"]
            vals.append(pv)
        return pd.Series(vals, index=self.data.index)
        
        
        
