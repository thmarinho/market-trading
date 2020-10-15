#!/usr/bin/env python3

from time import sleep
from _thread import start_new_thread
from os.path import exists

class Instrument:
    name = ""
    log_file = None

    def __init__(self, name, fx):
        self.name = name
        self.fx = fx
        self.init_log_file()
        start_new_thread(self.init_clandles, ())

    def init_clandles(self):
        self.fx.subscribe_market_data(self.name, ())
        while True:
            d = self.fx.get_last_price(self.name)
            print("Thread-" + self.name + " | ", d[0], d[1], d[2], d[3])
            sleep(1)

    def init_log_file(self):
        if not exists(self.get_log_path()):
            d = open(self.get_log_path(), "w+")
            d.write("Bid,Ask,High,Low")
            d.close()
        self.log_file = open(self.get_log_path(), 'a')

    def get_log_path(self):
        return "./logs/" + self.name.replace('/', "-") + ".csv"
