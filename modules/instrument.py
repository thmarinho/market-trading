#!/usr/bin/env python3

import os
import dotenv import load_dotenv

load_dotenv()

class Instrument:
    name = ""
    values = []

    def __init__(self, name, fx):
        self.name = name
        self.fx = fx
        self.init_clandles()

    def init_clandles(self):
        d = self.fx.get_candles(self.name, period=og.getenv("UPDATE_PERIOD"), number=os.getenv("CANDLES_TO_GET_ON_INIT"))
        self.values.insert(0, d)

    def update(self):
        d = self.fx.get_candles(self.name, period=os.getenv("UPDATE_PERIOD"), number=1)
        self.values.insert(0, d)
