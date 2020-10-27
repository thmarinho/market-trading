#!/usr/bin/env python3

from statistics import mean, pstdev

class Bollinger:
    def __init__(self, name, fx):
        self.name = name
        self.fx = fx
        d = fx.get_candles(instrument=self.name, period='m1', number=240)
        deviation = pstdev(d['bidclose'])
        self.mid = mean(d['bidopen'])
        self.top = self.mid + 2 * deviation
        self.bot = self.mid - 2 * deviation

    def should_buy(self):
        last_value = self.fx.get_last_price(self.name)[0] # 0 is actualy bid
        if (last_value < self.mid):
            return True
        return False

    def should_sell(self):
        last_value = self.fx.get_last_price(self.name)[0] # 0 is actually bid
        if (last_value > self.mid):
            return True
        return False
