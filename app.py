#!/usr/bin/env python3

import fxcmpy
import sys
import re
import os
from time import sleep
from modules.instrument import Instrument
from modules.color import colors

fx = None

def main():
    fx = fxcmpy.fxcmpy(config_file="./config/fxcm.cfg")
    print("Connection to FXCM etablished")
    if '--dev' in sys.argv:
        try:
            Instrument("EUR/USD", fx)
            print("[" + colors.OK + " OK " + colors.DEF + "] Initializing class for EUR/USD")
        except:
            fx.close()
            sys.exit(1)
    else:
        instruments = fx.get_instruments()
        for i in instruments[0:5]:
            if re.compile("[A-Z]{3}\/[A-Z]{3}").match(i):
                Instrument(i, fx)
                try:
                    Instrument(i, fx)
                    print("[" + colors.OK + " OK " + colors.DEF + "] Initializing class for {}".format(i))
                except:
                    print("[" + colors.FAIL + " KO " + colors.DEF + "] Initializing class for {}".format(i))
                    sys.exit(1)
    while True:
        None
    fx.close()

if __name__ == '__main__':
    try:
        main()
    except:
        print(colors.FAIL + "An unhandled error occured.\nAborting." + colors.DEF)
        if fx:
            fx.close()
        sys.exit(1)
