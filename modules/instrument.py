#!/usr/bin/env python3

from time import sleep
from _thread import start_new_thread
from os.path import exists
from sys import exit
from time import time
from modules.bollinger import Bollinger

class Instrument:
    name = ""

    def __init__(self, name, fx):
        self.name = name
        self.fx = fx
        start_new_thread(self.init_clandles, ())

    def init_clandles(self):
        self.fx.subscribe_market_data(self.name, ())
        while True:
            try:
                i = Bollinger(self.name, self.fx)
                if not self.have_positions():
                    if i.should_buy():
                        self.fx.open_trade(symbol=self.name, is_buy=True, amount=str(5), time_in_force='GTC', order_type="AtMarket", is_in_pips=False)
                        print("Buy positions for " + self.name)
                elif i.should_sell():
                    self.fx.close_all_for_symbol(self.name)
                    print("Sell positions for " + self.name)
                else:
                    print("Do nothing for " + self.name)
            except:
                self.fx.close()
                exit(1)
            sleep(2)

    def have_positions(self):
        postions = self.fx.get_open_positions(kind='list')
        if postions == []:
            return False
        return len(list(filter(lambda d: d['currency'] == self.name, postions))) > 0

