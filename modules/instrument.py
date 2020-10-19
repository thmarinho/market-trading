#!/usr/bin/env python3

from time import sleep
from _thread import start_new_thread
from os.path import exists
from sys import exit
from time import time

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
            try:
                d = self.fx.get_last_price(self.name)
                print("Thread-" + self.name + " | ", d[0], d[1], d[2], d[3])
                self.log_file.write(str(int(time() * 1000)) + ',' + str(d[0]) + ',' + str(d[1]) + ',' + str(d[2]) + ',' + str(d[3]) + "\n")
                self.log_file.flush()
                sleep(1)
            except:
                self.fx.close()
                exit(1)

    def init_log_file(self):
        if not exists(self.get_log_path()):
            d = open(self.get_log_path(), "w+")
            d.write("Timestamp,Bid,Ask,High,Low\n")
            d.close()
        self.log_file = open(self.get_log_path(), 'a')

    def get_log_path(self):
        return "./logs/" + self.name.replace('/', "-") + ".csv"
