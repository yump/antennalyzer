#!/usr/bin/env python3

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
