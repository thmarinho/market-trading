#!/usr/bin/env python3

import fxcmpy
import sys
import re
from modules.instrument import Instrument

_instruments = []

def main():
    fx = fxcmpy.fxcmpy(access_token="ef1ba0ada018efae88893f622d0997fc354778a2", log_level="error")
    print("Connection to FXCM etablished")
    instruments = fx.get_instruments()
    for i in instruments:
        if re.compile("[A-Z]{3}\/[A-Z]{3}").match(i):
            d = Instrument(i, fx)
            _instruments.append(d)
            print('Succesfully init class for {}'.format(i))
    fx.close()

if __name__ == '__main__':
    main()
