#!/usr/bin/env python3

from time import sleep
from _thread import start_new_thread
from os.path import exists
from sys import exit
from time import time
from modules.bollinger import Bollinger

class Instrument:

    def __init__(self, name, fx):
        self.name = name
        self.fx = fx
        self.position = {
            "type": "",
            "open": 0.0,
            "stop": 0.0,
            "limit": 0.0
        }
        start_new_thread(self.init_clandles, ())

    def init_clandles(self):
        try:
            self.fx.subscribe_market_data(self.name, ())
        except:
            print('Killing thread for ' + self.name)
            return
        while True:
            i = Bollinger(self.name, self.fx)
            if not self.have_positions():
                self.position = i.check_buy()
            else:
                self.position = i.check_PL(self.get_trade_id(), self.position)
            sleep(30)

    def have_positions(self):
        positions = self.fx.get_open_positions(kind='list')
        if positions == []:
            return False
        return len(list(filter(lambda d: d['currency'] == self.name, positions))) > 0
    
    def get_trade_id(self):
        positions = self.fx.get_open_positions(kind='list')
        l = list(filter(lambda d: d['currency'] == self.name, positions))
        if l:
            return l[0]['tradeId']
