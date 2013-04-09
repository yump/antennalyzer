#!/usr/bin/env python3

import scipy as sp
import itertools

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

		workfn : (work,freq) function ( sequence of numpy.ndarray )
			The function to minimize.  Takes a sequence of antennas and returns
			a tuple of the work and the index (or index range) into the samples
			at which that work is achieved. Work should be real and
			nonnegative.

			Each antenna in the sequence is a 2 dimensional numpy array with
			the operating modes on axis 0 (multiple polarizations,etc)
			and the sampled frequencies on axis 1.

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
		bestwork = sp.finfo(float).max
		bestarray = None
		bestind = None # operating frequency
		# exhaustive search: dis gon be slo
		for array in itertools.combinations(range(len(self.ants)),arrsz):
			newwork,newind = workfn( [self.ants[i] for i in array] )
			if newwork < bestwork:
				bestwork = newwork
				bestind = newind
				bestarray = array
		best_asnumbered = [ self.reversemap[i] for i in bestarray ]
		return (best_asnumbered,bestind,bestwork)

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
	usage = (
	"""
	usage: swr_recorder.py <datafile> <desired_array_size>
	""")
	if len(sys.argv) != 3:
		print(usage)
		exit(1)

	filename = sys.argv[1]
	antset = AntennaSet(filename)
	result = antset.optimalarray(int(sys.argv[2]), workfn=minloss)
	print("Array: {}\nFreq: {}\nWork: {}".format(*result))
