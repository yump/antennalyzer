#!/usr/bin/env python3
"""
swr_optimizer : Find an optimal subset of a set of antennas, based on VSWR.

Usage:
	swr_optmizer.py <datafile> minloss <desired_array_size>
	swr_optmizer.py <datafile> worstvswr <desired_array_size>
	swr_optmizer.py <datafile> maxvswrbw <desired_array_size> <maximum_VSWR>

	minloss : Find the set of antennas and operating frequency that minimize
	          mismatch loss for the entire array.

	worstvswr : Find the set of antennas and operating frequency that minimize 
	            the VSWR of the worst antenna.

	maxvswrbw : Find the set of antennas that maximizes the bandwidth for which
	            the VSWR of the worst antenna is below a specified value.
"""

import scipy as sp
import numpy as np
import itertools
import iterrecipe

class AntennaSet:
	def __init__(self,fn):
		# data['n_x'] is the x polarization data for the nth antenna.
		# data['n_y'] is the y polariztion data.  Each data element is a 1001
		# element array.  We want to coalesce the polarization pairs into
		# 2x1001 element arrays, because both polarizations have to be used
		# together, and we can concatenate all the antennas vertically and find
		# the optimal frequency.
		data = sp.load(fn)
		self.ants = []
		self.reversemap = {}
		# iterate over physical antennas
		for antsx,antnum in enumerate(set( 
				(int(i.split('_')[0]) for i in data.files) 
				)):
			ant = sp.array(( data["{}_x".format(antnum)], 
							 data["{}_y".format(antnum)] ))
			ant = sp.atleast_2d(ant)
			self.ants.append(ant)
			self.reversemap[antsx] = antnum
		
	def optimalarray(self,arrsz,workfn):
		"""
		Find the subset of the AntennaSet that minimizes some work function.

		Parameters
		----------
		arrsz : int
			The number of elements in the desired array.

		workfn : (work,freq) function ( list of numpy.ndarray )
			The function to minimize.  Takes a list of antennas and returns a
			tuple of the work and the index (or index range) into the samples
			at which that work is achieved. Work should be real and
			nonnegative.

			Each antenna in the sequence is a 2 dimensional numpy array with
			the operating modes on axis 0 (multiple polarizations,etc) and the
			sampled frequencies on axis 1.

		Returns
		-------
		array : sequence of int
			The antenna numbers for which the work function is minimized.
		
		bestind : int or tuple of int
			The index or range of indices into the samples for which the array
			is optimal.  This maps to the operating frequency of the array,
			though exactly how depends on the sampling range.

		bestwork : nonnegative real
			The work function achieved by the optimal array.
		"""
		bestwork = sp.inf
		bestarray = None
		bestind = None # operating frequency
		# exhaustive search: dis gon be slo
		for array in itertools.combinations(range(len(self.ants)),arrsz):
			newwork,newind = workfn( [self.ants[i] for i in array] )
			if newwork < bestwork:
				bestwork = newwork
				bestind = newind
				bestarray = array
		if bestarray == None:
			raise ConstraintError("Unsatisfiable constraints")
		else:
			best_asnumbered = [ self.reversemap[i] for i in bestarray ]
			return (best_asnumbered,bestind,bestwork)

class ConstraintError(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class maxvswrbw:
	"""
	Class of objective functions for maximizing bandwidth given an 
	upper bound on VSWR.
	"""
	def __init__(self,vswr):
		self.max = vswr

	def __call__(self,ants):
		antarr = sp.concatenate(ants)
		# shared bandwidth
		vswr_ok = sp.all(antarr < self.max, axis=0)
		# find the widest region (there's probably only one, but...)
		best = 0
		for before,end in iterrecipe.grouper(2,sp.nonzero(sp.diff(vswr_ok))[0]):
			if end - before > best:
				best = end - before
				region = (before+1, end)
		# invert the objective (so small is good)
		if best == 0:
			return sp.inf,(0,0)
		else:
			return 1.0/best, region

def worstminvswr(ants):
	antarr = sp.concatenate(ants)
	worstvswr = np.max(antarr,axis=0)
	bestind = sp.argmin(worstvswr)
	return worstvswr[bestind],bestind

def minloss(ants):
	antarr = sp.concatenate(ants)
	arr_reflpwr = sp.sum(reflpwr(antarr),axis=0)
	bestind = sp.argmin(arr_reflpwr)
	return arr_reflpwr[bestind], bestind

def reflpwr(swr):
	swr = sp.asarray(swr)
	return ((swr - 1)/(swr + 1))**2

if __name__ == "__main__":
	import sys
	try:
		filename = sys.argv[1]
		antset = AntennaSet(filename)
		method = sys.argv[2]
		arrsz = int(sys.argv[3])
		if method == "minloss":
			result = antset.optimalarray(arrsz, workfn=minloss)
			print("Array: {}\nFreq: {}\nWork: {}".format(*result))
		elif method == "worstvswr":
			result = antset.optimalarray(arrsz, workfn=worstminvswr)
			print("Array: {}\nFreq: {}\nWorst VSWR: {}".format(*result))
		elif method == "maxvswrbw":
			maxvswr = float(sys.argv[4])
			result = antset.optimalarray(arrsz,workfn=maxvswrbw(maxvswr))
			print("Array: {}\nBandwitdth: {}\nWork: {}".format(*result))
		else:
			print(__doc__)
			exit(1)
	except (IndexError,ValueError):
		print(__doc__)
		exit(1)



