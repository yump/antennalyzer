#!/usr/bin/env python3
#   Copyright 2012,2013 Russell Haley
#   (Please add yourself if you make changes)
#
#   This file is part of swr-recorder.
#
#   swr-recorder is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   swr-recorder is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with swr-recorder.  If not, see <http://www.gnu.org/licenses/>.

import logging
import FieldFox
import numpy as np

logging.basicConfig(filename="swr_recorder.log", level=logging.DEBUG)
log = logging.getLogger()

ffhost="192.168.0.100" #IIRC

print("Connecting to network analyzer...")
meter = FieldFox.FieldFox(ffhost,numpoints=1001,lo=2.35e9,hi=2.55e9)
file = 'antenna_swr'
datadict = {}

while True:
    try:
        ant = int(input("Antenna number?"))
        pol = input("Antenna polarization (x/y)")
        if pol == "x" or pol == "y":
            pass
        else:
            raise ValueError("Bad polarization")
            log.warn("User entered polarization other than 'x' or 'y'")
    except ValueError:
        print("Bad antenna number or polarization.")
    except KeyboardInterrupt:
        print("Exiting...")
        log.debug("Exiting due to keyboard interrupt")
        exit(0)
    else:
        log.info("Sampling antenna {} polariztion {}".format(ant,pol))
        swrsamples = meter.sample(avg=5)
        datadict.update({"{}_{}".format(ant,pol) : swrsamples})
        np.savez(file,**datadict)
