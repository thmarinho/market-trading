#!/usr/bin/env python3

import fxcmpy
import sys
import re
import os
from modules.instrument import Instrument
from modules.color import colors

_instruments = []
fx = None

def main():
    fx = fxcmpy.fxcmpy(config_file="./config/fxcm.cfg")
    print("Connection to FXCM etablished")
    instruments = fx.get_instruments()
    for i in instruments:
        if re.compile("[A-Z]{3}\/[A-Z]{3}").match(i):
            Instrument(i, fx)
            try:
                d = Instrument(i, fx)
                _instruments.append(d)
                print("[" + colors.OK + " OK " + colors.DEF + "] Initializing class for {}".format(i))
            except:
                print("[" + colors.FAIL + " KO " + colors.DEF + "] Initializing class for {}".format(i))
                fx.close()
                sys.exit(1)
    while True:
        None
    fx.close()

if __name__ == '__main__':
    main()
    #try:
    #    main()
    #except:
    #    print(colors.FAIL + "An unhandled error occured.\nAborting." + colors.DEF)
    #    if fx:
    #        fx.close()
    #    sys.exit(1)
