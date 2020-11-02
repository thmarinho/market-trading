
#!/usr/bin/env python3

from statistics import mean, pstdev

amount = 10
loss = -1.5
profit = 3.0

class Bollinger:

    def __init__(self, name, fx):
        self.name = name
        self.fx = fx
        self.arr5 = fx.get_candles(instrument=self.name, period='m1', number=20)
        self.arr15 = fx.get_candles(instrument=self.name, period='m5', number=20)
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

    def check_buy(self):
        last_values = self.fx.get_last_price(self.name) # [bid, ask, high, low]
        if last_values['Ask'] < self.arr5['askclose'][19] and self.arr5['askclose'][19] < self.arr5['askclose'][18]\
        and last_values['Ask'] < self.calculate_price(80, "sell") and last_values['Ask'] > self.calculate_price(20, "sell"):
            #self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False)
            print("Open a sell position for " + self.name)
            try:
                self.fx.create_market_sell_order(self.name, amount)
            except:
                print("Failed to open position for " + self.name)
            return {
                "type": "sell",
                "open": last_values['Ask']
            }
        if last_values['Bid'] > self.arr5['bidclose'][19] and self.arr5['bidclose'][19] > self.arr5['bidclose'][18]\
        and last_values['Bid'] < self.calculate_price(80, "buy") and last_values['Bid'] > self.calculate_price(20, "buy"):
            #self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False)
            print("Open a buy position for " + self.name)
            try:
                self.fx.create_market_buy_order(self.name, amount)
            except:
                print("Failed to open position for " + self.name)
            return {
                "type": "buy",
                "open": last_values['Bid']
            }
        return {
            "type": "",
            "open": 0.0
        }

    def check_PL(self, tradeId, position, l):
        for i in range(0, len(l)):
            if l[i]['grossPL'] < loss or l[i]['grossPL'] > profit:
                self.fx.close_all_for_symbol(self.name)
                #print("Close position for " + self.name)
        return position
