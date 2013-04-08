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

class QAMRadio:
	"""Superclass for QAM radios."""

	def __init__(self, host=None, port=None):
		raise NotImplementedError

	def sample(self):
		raise NotImplementedError

