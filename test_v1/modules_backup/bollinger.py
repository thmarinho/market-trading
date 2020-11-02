#!/usr/bin/env python3

from statistics import mean, pstdev

amount = 20

class Bollinger:
    def __init__(self, name, fx):
        self.name = name
        self.fx = fx
        self.arr = fx.get_candles(instrument=self.name, period='m5', number=20)
        deviation = pstdev(self.arr['bidclose'])
        self.mid = mean(self.arr['bidclose'])
        self.top = self.mid + 2 * deviation
        self.bot = self.mid - 2 * deviation
        deviation = pstdev(self.arr['askclose'])
        self.amid = mean(self.arr['askclose'])
        self.atop = self.amid + 2 * deviation
        self.abot = self.amid - 2 * deviation
        # print("deviation = {:.6}\tmid = {:.6}\ttop = {:.6}\tbot = {:.6}".format(deviation, self.mid, self.top, self.bot))

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
    
    def check_buy(self):
        last_values = self.fx.get_last_price(self.name) # [bid, ask, low, high]
        diff = self.top - self.bot
        adiff = self.atop - self.abot
        # Bounces
        if last_values[1] > self.abot + adiff * 0.85 and self.arr['askclose'][19] > self.arr['askclose'][17]:
            self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(self.abot + adiff * 1.1), limit=str(self.amid))
            print("Open a sell position for " + self.name)
            return "sell", self.abot + diff * 1.1
        elif last_values[0] < self.bot + diff * 0.15 and self.arr['bidclose'][19] < self.arr['bidclose'][17]:
            self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(self.bot - diff * 0.1), limit=str(self.mid))
            print("Open a buy position for " + self.name)
            return "buy", self.bot - diff * 0.1
        # Trends
        elif last_values[1] < self.abot + adiff * 0.75 and last_values[1] > self.amid and self.arr['askclose'][19] < self.arr['askclose'][18]:
            self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(self.abot + adiff * 0.85), limit=str(self.abot + adiff * 0.4))
            print("Open a sell position for " + self.name)
            return "sell", self.abot + adiff * 0.85
        elif last_values[0] > self.bot + diff * 0.25 and last_values[0] < self.mid and self.arr['bidclose'][19] > self.arr['bidclose'][18]:
            self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(self.bot + diff * 0.15), limit=str(self.bot + diff * 0.6))
            print("Open a buy position for " + self.name)
            return "buy", self.bot + diff * 0.15
        else:
            return "", 0.0

    def check_PL(self, _type, tradeId, stop):
        last_values = self.fx.get_last_price(self.name) # [bid, ask, low, high]
        diff = self.top - self.bot
        adiff = self.atop - self.abot
        if _type == "buy":
            if last_values[0] > (self.bot + diff * 0.4) and stop < self.bot + diff * 0.3:
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(self.bot + diff * 0.3))
                print("Change stop rate for " + self.name)
                return self.bot + diff * 0.3
            if last_values[0] > self.mid and stop < self.bot + diff * 0.4:
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(self.bot + diff * 0.4))
                print("Change stop rate for " + self.name)
                return self.bot + diff * 0.4
        elif _type == "sell":
            if last_values[1] < self.abot + adiff * 0.6 and stop > self.abot + adiff * 0.7:
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(self.abot + adiff * 0.7))
                print("Change stop rate for " + self.name)
                return self.abot + adiff * 0.7
            if last_values[1] < self.amid and stop > self.abot + adiff * 0.6:
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(self.abot + adiff * 0.6))
                print("Change stop rate for " + self.name)
                return self.abot + adiff * 0.6
        # print("No rate changes for " + self.name)
        return stop

#!/usr/bin/env python3

from statistics import mean, pstdev

amount = 20
loss = -2
profit = 8

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
        # Trends
        # Sell
        # if self.last_values['Ask'] > self.calculate_price(65, "sell") and self.last_values['Ask'] < self.calculate_price(75, "sell") and self.arr5['askclose'][19] < self.arr5['askclose'][17] and self.arr15['askclose'][19] < self.arr15['askclose'][18]:
        #     stop = self.calculate_price(77, "sell")
        #     limit = self.calculate_price(60, "sell")
        #     self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
        #     print("Open a sell position for " + self.name)
        #     return {
        #         "type": "sell",
        #         "open": self.last_values['Ask'],
        #         "stop": stop,
        #         "limit": limit
        #     }
        # if self.last_values['Ask'] > self.calculate_price(55, "sell") and self.last_values['Ask'] < self.calculate_price(65, "sell") and self.arr5['askclose'][19] < self.arr5['askclose'][17] and self.arr15['askclose'][19] < self.arr15['askclose'][18]:
        #     stop = self.calculate_price(67, "sell")
        #     limit = self.calculate_price(50, "sell")
        #     self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
        #     print("Open a sell position for " + self.name)
        #     return {
        #         "type": "sell",
        #         "open": self.last_values['Ask'],
        #         "stop": stop,
        #         "limit": limit
        #     }
        # if self.last_values['Ask'] > self.calculate_price(45, "sell") and self.last_values['Ask'] < self.calculate_price(55, "sell") and self.arr5['askclose'][19] < self.arr5['askclose'][17] and self.arr15['askclose'][19] < self.arr15['askclose'][18]:
        #     stop = self.calculate_price(57, "sell")
        #     limit = self.calculate_price(40, "sell")
        #     self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
        #     print("Open a sell position for " + self.name)
        #     return {
        #         "type": "sell",
        #         "open": self.last_values['Ask'],
        #         "stop": stop,
        #         "limit": limit
        #     }
        # if self.last_values['Ask'] > self.calculate_price(35, "sell") and self.last_values['Ask'] < self.calculate_price(45, "sell") and self.arr5['askclose'][19] < self.arr5['askclose'][17] and self.arr15['askclose'][19] < self.arr15['askclose'][18]:
        #     stop = self.calculate_price(47, "sell")
        #     limit = self.calculate_price(30, "sell")
        #     self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
        #     print("Open a sell position for " + self.name)
        #     return {
        #         "type": "sell",
        #         "open": self.last_values['Ask'],
        #         "stop": stop,
        #         "limit": limit
        #     }
        # if self.last_values['Ask'] > self.calculate_price(25, "sell") and self.last_values['Ask'] < self.calculate_price(35, "sell") and self.arr5['askclose'][19] < self.arr5['askclose'][17] and self.arr15['askclose'][19] < self.arr15['askclose'][18]:
        #     stop = self.calculate_price(27, "sell")
        #     limit = self.calculate_price(20, "sell")
        #     self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
        #     print("Open a sell position for " + self.name)
        #     return {
        #         "type": "sell",
        #         "open": self.last_values['Ask'],
        #         "stop": stop,
        #         "limit": limit
        #     }
        # # Buy
        # if self.last_values['Bid'] < self.calculate_price(35, "buy") and self.last_values['Bid'] > self.calculate_price(25, "sell") and self.arr5['bidclose'][19] > self.arr5['bidclose'][17] and self.arr15['bidclose'][19] > self.arr15['bidclose'][18]:
        #     stop = self.calculate_price(20, "sell")
        #     limit = self.calculate_price(37, "sell")
        #     self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
        #     print("Open a buy position for " + self.name)
        #     return {
        #         "type": "buy",
        #         "open": self.last_values['Bid'],
        #         "stop": stop,
        #         "limit": limit
        #     }
        # if self.last_values['Bid'] < self.calculate_price(45, "buy") and self.last_values['Bid'] > self.calculate_price(35, "sell") and self.arr5['bidclose'][19] > self.arr5['bidclose'][17] and self.arr15['bidclose'][19] > self.arr15['bidclose'][18]:
        #     stop = self.calculate_price(30, "sell")
        #     limit = self.calculate_price(47, "sell")
        #     self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
        #     print("Open a buy position for " + self.name)
        #     return {
        #         "type": "buy",
        #         "open": self.last_values['Bid'],
        #         "stop": stop,
        #         "limit": limit
        #     }
        # if self.last_values['Bid'] < self.calculate_price(55, "buy") and self.last_values['Bid'] > self.calculate_price(45, "sell") and self.arr5['bidclose'][19] > self.arr5['bidclose'][17] and self.arr15['bidclose'][19] > self.arr15['bidclose'][18]:
        #     stop = self.calculate_price(40, "sell")
        #     limit = self.calculate_price(57, "sell")
        #     self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
        #     print("Open a buy position for " + self.name)
        #     return {
        #         "type": "buy",
        #         "open": self.last_values['Bid'],
        #         "stop": stop,
        #         "limit": limit
        #     }
        # if self.last_values['Bid'] < self.calculate_price(65, "buy") and self.last_values['Bid'] > self.calculate_price(55, "sell") and self.arr5['bidclose'][19] > self.arr5['bidclose'][17] and self.arr15['bidclose'][19] > self.arr15['bidclose'][18]:
        #     stop = self.calculate_price(50, "sell")
        #     limit = self.calculate_price(67, "sell")
        #     self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
        #     print("Open a buy position for " + self.name)
        #     return {
        #         "type": "buy",
        #         "open": self.last_values['Bid'],
        #         "stop": stop,
        #         "limit": limit
        #     }
        # if self.last_values['Bid'] < self.calculate_price(75, "buy") and self.last_values['Bid'] > self.calculate_price(65, "sell") and self.arr5['bidclose'][19] > self.arr5['bidclose'][17] and self.arr15['bidclose'][19] > self.arr15['bidclose'][18]:
        #     stop = self.calculate_price(60, "sell")
        #     limit = self.calculate_price(77, "sell")
        #     self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
        #     print("Open a buy position for " + self.name)
        #     return {
        #         "type": "buy",
        #         "open": self.last_values['Bid'],
        #         "stop": stop,
        #         "limit": limit
        #     }
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
            stop = self.calculate_margin("stop", "sell")
            # limit = self.calculate_margin("limit", "sell")
            if stop < position['stop']:
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": position['limit']
                }
            # if self.last_values['Ask'] < self.calculate_price(60, "sell") and position["stop"] > self.calculate_price(75, "sell"):
            #     stop = self.calculate_price(70, "sell")
            #     limit = self.calculate_price(55, "sell")
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
            #     print("Change stop rate for " + self.name)
            #     return {
            #         "type": position['type'],
            #         "open": position['open'],
            #         "stop": stop,
            #         "limit": limit
            #     }
            # if self.last_values['Ask'] < self.calculate_price(50, "sell") and position["stop"] > self.calculate_price(65, "sell"):
            #     stop = self.calculate_price(60, "sell")
            #     limit = self.calculate_price(45, "sell")
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
            #     print("Change stop rate for " + self.name)
            #     return {
            #         "type": position['type'],
            #         "open": position['open'],
            #         "stop": stop,
            #         "limit": limit
            #     }
            # if self.last_values['Ask'] < self.calculate_price(40, "sell") and position["stop"] > self.calculate_price(55, "sell"):
            #     stop = self.calculate_price(50, "sell")
            #     limit = self.calculate_price(35, "sell")
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
            #     print("Change stop rate for " + self.name)
            #     return {
            #         "type": position['type'],
            #         "open": position['open'],
            #         "stop": stop,
            #         "limit": limit
            #     }
            # if self.last_values['Ask'] < self.calculate_price(30, "sell") and position["stop"] > self.calculate_price(45, "sell"):
            #     stop = self.calculate_price(40, "sell")
            #     limit = self.calculate_price(25, "sell")
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
            #     print("Change stop rate for " + self.name)
            #     return {
            #         "type": position['type'],
            #         "open": position['open'],
            #         "stop": stop,
            #         "limit": limit
            #     }
            if position["type"] == "buy" and self.arr5['bidclose'][19] > self.arr5['bidclose'][17] and self.arr15['bidclose'][19] > self.arr15['bidclose'][18]:
                stop = self.calculate_margin("stop", "buy")
                # limit = self.calculate_margin("limit", "buy")
                if stop > position['stop']:
                    print("Change stop rate for " + self.name)
                    return {
                        "type": position['type'],
                        "open": position['open'],
                        "stop": stop,
                        "limit": position['limit']
                    }
            # if self.last_values['Bid'] > self.calculate_price(45, "buy") and position["stop"] < self.calculate_price(30, "buy"):
            #     stop = self.calculate_price(25, "buy")
            #     limit = self.calculate_price(40, "buy")
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
            #     print("Change stop rate for " + self.name)
            #     return {
            #         "type": position['type'],
            #         "open": position['open'],
            #         "stop": stop,
            #         "limit": limit
            #     }
            # if self.last_values['Bid'] > self.calculate_price(55, "buy") and position["stop"] < self.calculate_price(40, "buy"):
            #     stop = self.calculate_price(35, "buy")
            #     limit = self.calculate_price(50, "buy")
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
            #     print("Change stop rate for " + self.name)
            #     return {
            #         "type": position['type'],
            #         "open": position['open'],
            #         "stop": stop,
            #         "limit": limit
            #     }
            # if self.last_values['Bid'] > self.calculate_price(65, "buy") and position["stop"] < self.calculate_price(50, "buy"):
            #     stop = self.calculate_price(45, "buy")
            #     limit = self.calculate_price(60, "buy")
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
            #     print("Change stop rate for " + self.name)
            #     return {
            #         "type": position['type'],
            #         "open": position['open'],
            #         "stop": stop,
            #         "limit": limit
            #     }
            # if self.last_values['Bid'] > self.calculate_price(75, "buy") and position["stop"] < self.calculate_price(60, "buy"):
            #     stop = self.calculate_price(55, "buy")
            #     limit = self.calculate_price(70, "buy")
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
            #     self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
            #     print("Change stop rate for " + self.name)
            #     return {
            #         "type": position['type'],
            #         "open": position['open'],
            #         "stop": stop,
            #         "limit": limit
            #     }
        # print("No rate changes for " + self.name)
        return position

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

#!/usr/bin/env python3

from statistics import mean, pstdev

amount = 10
loss = 0
profit = 10

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

    def calculate_margin(self, last_values, rate_type, _type):
        if _type == "sell":
            if rate_type == "stop":
                return last_values['Ask'] + self.adiff * (loss / 100)
            if rate_type == "limit":
                return last_values['Ask'] - self.adiff * (profit / 100)
        if _type == "buy":
            if rate_type == "stop":
                return last_values['Bid'] - self.diff * (loss / 100)
            if rate_type == "limit":
                return last_values['Bid'] + self.diff * (profit / 100)

    def check_buy(self):
        last_values = self.fx.get_last_price(self.name) # [bid, ask, high, low]
        if self.arr5['askclose'][19] < self.arr5['askclose'][17] and self.arr15['askclose'][19] < self.arr15['askclose'][18]\
        and last_values['Ask'] < self.calculate_price(80, "sell") and last_values['Ask'] > self.calculate_price(20, "sell"):
            #     stop = self.calculate_price(35, "buy"):
            stop = self.calculate_margin(last_values, "stop", "sell")
            limit = self.calculate_margin(last_values, "limit", "sell")
            print("Open a sell position for " + self.name)
            print("open = {:.6}\tstop = {:.6}\tlimit = {:.6}".format(last_values['Ask'], stop, limit))
            self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            return {
                "type": "sell",
                "open": last_values['Ask'],
                "stop": stop,
                "limit": limit
            }
        if self.arr5['bidclose'][19] > self.arr5['bidclose'][17] and self.arr15['bidclose'][19] > self.arr15['bidclose'][18]\
        and last_values['Bid'] < self.calculate_price(80, "buy") and last_values['Bid'] > self.calculate_price(20, "buy"):
            stop = self.calculate_margin(last_values, "stop", "buy")
            limit = self.calculate_margin(last_values, "limit", "buy")
            print("Open a buy position for " + self.name)
            print("open = {:.6}\tstop = {:.6}\tlimit = {:.6}".format(last_values['Bid'], stop, limit))
            self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
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

#!/usr/bin/env python3

from statistics import mean, pstdev

amount = 10
loss = -1.5
profit = 3.0

class Bollinger:

    def __init__(self, name, fx):
        self.name = name
        self.fx = fx
        self.last_values = self.fx.get_last_price(self.name) # [bid, ask, high, low]
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
            return self.bot + self.diff * (percentage + 5)/ 100
        if (_type == "sell"):
            return self.abot + self.adiff * (percentage - 5) / 100

    def check_buy(self):
        # Trends
        # Sell
        if self.last_values['Ask'] > self.calculate_price(65, "sell") and self.last_values['Ask'] < self.calculate_price(75, "sell") and self.arr5['askclose'][19] < self.arr5['askclose'][18]:
            stop = self.calculate_price(77, "sell")
            limit = self.calculate_price(60, "sell")
            self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a sell position for " + self.name)
            return {
                "type": "sell",
                "open": self.last_values['Ask'],
                "stop": stop,
                "limit": limit
            }
        if self.last_values['Ask'] > self.calculate_price(55, "sell") and self.last_values['Ask'] < self.calculate_price(65, "sell") and self.arr5['askclose'][19] < self.arr5['askclose'][18]:
            stop = self.calculate_price(67, "sell")
            limit = self.calculate_price(50, "sell")
            self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a sell position for " + self.name)
            return {
                "type": "sell",
                "open": self.last_values['Ask'],
                "stop": stop,
                "limit": limit
            }
        if self.last_values['Ask'] > self.calculate_price(45, "sell") and self.last_values['Ask'] < self.calculate_price(55, "sell") and self.arr5['askclose'][19] < self.arr5['askclose'][18]:
            stop = self.calculate_price(57, "sell")
            limit = self.calculate_price(40, "sell")
            self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a sell position for " + self.name)
            return {
                "type": "sell",
                "open": self.last_values['Ask'],
                "stop": stop,
                "limit": limit
            }
        if self.last_values['Ask'] > self.calculate_price(35, "sell") and self.last_values['Ask'] < self.calculate_price(45, "sell") and self.arr5['askclose'][19] < self.arr5['askclose'][18]:
            stop = self.calculate_price(47, "sell")
            limit = self.calculate_price(30, "sell")
            self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a sell position for " + self.name)
            return {
                "type": "sell",
                "open": self.last_values['Ask'],
                "stop": stop,
                "limit": limit
            }
        if self.last_values['Ask'] > self.calculate_price(25, "sell") and self.last_values['Ask'] < self.calculate_price(35, "sell") and self.arr5['askclose'][19] < self.arr5['askclose'][18]:
            stop = self.calculate_price(27, "sell")
            limit = self.calculate_price(20, "sell")
            self.fx.open_trade(symbol=self.name, is_buy=False, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a sell position for " + self.name)
            return {
                "type": "sell",
                "open": self.last_values['Ask'],
                "stop": stop,
                "limit": limit
            }
        # Buy
        if self.last_values['Bid'] < self.calculate_price(35, "buy") and self.last_values['Bid'] > self.calculate_price(25, "buy") and self.arr5['askclose'][19] < self.arr5['askclose'][18]:
            stop = self.calculate_price(20, "buy")
            limit = self.calculate_price(37, "buy")
            self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a buy position for " + self.name)
            return {
                "type": "buy",
                "open": self.last_values['Bid'],
                "stop": stop,
                "limit": limit
            }
        if self.last_values['Bid'] < self.calculate_price(45, "buy") and self.last_values['Bid'] > self.calculate_price(35, "buy") and self.arr5['bidclose'][19] > self.arr5['bidclose'][18]:
            stop = self.calculate_price(30, "buy")
            limit = self.calculate_price(47, "buy")
            self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a buy position for " + self.name)
            return {
                "type": "buy",
                "open": self.last_values['Bid'],
                "stop": stop,
                "limit": limit
            }
        if self.last_values['Bid'] < self.calculate_price(55, "buy") and self.last_values['Bid'] > self.calculate_price(45, "buy") and self.arr5['bidclose'][19] > self.arr5['bidclose'][18]:
            stop = self.calculate_price(40, "buy")
            limit = self.calculate_price(57, "buy")
            self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a buy position for " + self.name)
            return {
                "type": "buy",
                "open": self.last_values['Bid'],
                "stop": stop,
                "limit": limit
            }
        if self.last_values['Bid'] < self.calculate_price(65, "buy") and self.last_values['Bid'] > self.calculate_price(55, "buy") and self.arr5['bidclose'][19] > self.arr5['bidclose'][18]:
            stop = self.calculate_price(50, "buy")
            limit = self.calculate_price(67, "buy")
            self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a buy position for " + self.name)
            return {
                "type": "buy",
                "open": self.last_values['Bid'],
                "stop": stop,
                "limit": limit
            }
        if self.last_values['Bid'] < self.calculate_price(75, "buy") and self.last_values['Bid'] > self.calculate_price(65, "buy") and self.arr5['bidclose'][19] > self.arr5['bidclose'][18]:
            stop = self.calculate_price(60, "buy")
            limit = self.calculate_price(77, "buy")
            self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(amount), time_in_force='GTC', order_type="AtMarket", is_in_pips=False, stop=str(stop), limit=str(limit))
            print("Open a buy position for " + self.name)
            return {
                "type": "buy",
                "open": self.last_values['Bid'],
                "stop": stop,
                "limit": limit
            }
        return {
            "type": "",
            "open": 0.0,
            "stop": 0.0,
            "limit": 0.0
        }

    def check_PL(self, tradeId, position, l):
        for i in range(0, len(l)):
            if l[i]['grossPL'] < loss or l[i]['grossPL'] > profit:
                self.fx.close_all_for_symbol(self.name)
                return position
        if position["type"] == "sell" and self.arr5['askclose'][19] < self.arr5['askclose'][18]:
            if self.last_values['Ask'] < self.calculate_price(60, "sell") and position["stop"] > self.calculate_price(75, "sell"):
                stop = self.calculate_price(70, "sell")
                limit = self.calculate_price(55, "sell")
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": limit
                }
            if self.last_values['Ask'] < self.calculate_price(50, "sell") and position["stop"] > self.calculate_price(65, "sell"):
                stop = self.calculate_price(60, "sell")
                limit = self.calculate_price(45, "sell")
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": limit
                }
            if self.last_values['Ask'] < self.calculate_price(40, "sell") and position["stop"] > self.calculate_price(55, "sell"):
                stop = self.calculate_price(50, "sell")
                limit = self.calculate_price(35, "sell")
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": limit
                }
            if self.last_values['Ask'] < self.calculate_price(30, "sell") and position["stop"] > self.calculate_price(45, "sell"):
                stop = self.calculate_price(40, "sell")
                limit = self.calculate_price(25, "sell")
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": limit
                }
        if position["type"] == "buy" and self.arr5['bidclose'][19] > self.arr5['bidclose'][17] and self.arr15['bidclose'][19] > self.arr15['bidclose'][18]:
            if self.last_values['Bid'] > self.calculate_price(45, "buy") and position["stop"] < self.calculate_price(30, "buy"):
                stop = self.calculate_price(25, "buy")
                limit = self.calculate_price(40, "buy")
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": limit
                }
            if self.last_values['Bid'] > self.calculate_price(55, "buy") and position["stop"] < self.calculate_price(40, "buy"):
                stop = self.calculate_price(35, "buy")
                limit = self.calculate_price(50, "buy")
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": limit
                }
            if self.last_values['Bid'] > self.calculate_price(65, "buy") and position["stop"] < self.calculate_price(50, "buy"):
                stop = self.calculate_price(45, "buy")
                limit = self.calculate_price(60, "buy")
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": limit
                }
            if self.last_values['Bid'] > self.calculate_price(75, "buy") and position["stop"] < self.calculate_price(60, "buy"):
                stop = self.calculate_price(55, "buy")
                limit = self.calculate_price(70, "buy")
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=True, rate=(stop))
                self.fx.change_trade_stop_limit(tradeId, is_in_pips=False, is_stop=False, rate=(limit))
                print("Change stop rate for " + self.name)
                return {
                    "type": position['type'],
                    "open": position['open'],
                    "stop": stop,
                    "limit": limit
                }
        # print("No rate changes for " + self.name)
        return position
