#!/usr/bin/env python3

from statistics import mean, pstdev

amount = 20
loss = -3
profit = 10

class Bollinger:

    def __init__(self, name, fx):
        self.name = name
        self.fx = fx
        self.arr5 = fx.get_candles(instrument=self.name, period='m5', number=20)
        self.arr15 = fx.get_candles(instrument=self.name, period='m15', number=20)
        deviation = pstdev(self.arr5['bidclose'])
        self.mid = mean(self.arr5['bidclose'])
        self.top = self.mid + 2 * deviation
        self.bot = self.mid - 2 * deviation
        deviation = pstdev(self.arr5['askclose'])
        self.amid = mean(self.arr5['askclose'])
        self.atop = self.amid + 2 * deviation
        self.abot = self.amid - 2 * deviation
        self.diff = self.top - self.bot
        self.adiff = self.atop - self.abot

    def calculate_price(self, percentage, _type):
        if (_type == "buy"):
            return self.bot + self.diff * (percentage / 100)
        if (_type == "sell"):
            return self.abot + self.adiff * (percentage / 100)

    def calculate_margin(self, last_values, rate_type, _type):
        if _type == "sell":
            if rate_type == "stop":
                return last_values['Ask'] - self.adiff * (loss / 100)
            if rate_type == "limit":
                return last_values['Ask'] - self.adiff * (profit / 100)
        if _type == "buy":
            if rate_type == "stop":
                return last_values['Bid'] + self.diff * (loss / 100)
            if rate_type == "limit":
                return last_values['Bid'] + self.diff * (profit / 100)

    def check_buy(self):
        if self.arr5['askclose'][19] < self.arr5['askclose'][17] and self.arr15['askclose'][19] < self.arr15['askclose'][18]:
            last_values = self.fx.get_last_price(self.name) # [bid, ask, high, low]
            stop = self.calculate_margin(last_values, "stop", "sell")
            limit = self.calculate_margin(last_values, "limit", "sell")
            self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a sell position for " + self.name)
            return {
                "type": "sell",
                "open": last_values['Ask'],
                "stop": stop,
                "limit": limit
            }
        if self.arr5['bidclose'][19] > self.arr5['bidclose'][17] and self.arr15['bidclose'][19] > self.arr15['bidclose'][18]:
            last_values = self.fx.get_last_price(self.name) # [bid, ask, high, low]
            stop = self.calculate_margin(last_values, "stop", "buy")
            limit = self.calculate_margin(last_values, "limit", "buy")
            self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a buy position for " + self.name)
            return {
                "type": "buy",
                "open": last_values['Bid'],
                "stop": stop,
                "limit": limit
            }
        return {
            "type": "",
            "open": 0.0,
            "stop": 0.0,
            "limit": 0.0
        }

    def check_PL(self, tradeId, position):
        if position["type"] == "sell" and self.arr5['askclose'][19] < self.arr5['askclose'][17] and self.arr15['askclose'][19] < self.arr15['askclose'][18]:
            last_values = self.fx.get_last_price(self.name) # [bid, ask, high, low]
            stop = self.calculate_margin(last_values, "stop", "buy")
            # limit = self.calculate_margin(last_values, "limit", "buy")
            if stop < position['stop']:
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": position['limit']
                }

        if position["type"] == "buy" and self.arr5['bidclose'][19] > self.arr5['bidclose'][17] and self.arr15['bidclose'][19] > self.arr15['bidclose'][18]:
            last_values = self.fx.get_last_price(self.name) # [bid, ask, high, low]
            stop = self.calculate_margin(last_values, "stop", "buy")
            # limit = self.calculate_margin(last_values, "limit", "buy")
            if stop > position['stop']:
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": position['limit']
                }
        return position