#!/usr/bin/env python3

class CurrencyExtract:
    
    def __init__(self, name, bid, ask, high, low):
        self.name = name
        self.final_line = "\n" + str(bid) + ',' + str(ask) + ',' + str(high) + ',' + str(low)
        self.path = 'logs/' + self.name.replace('/', '-') + ".csv"

    def write_in_file(self):
        fd = open(self.path, 'a')
        fd.write(self.final_line)
        fd.close()
