## This file is part of the shooting game example for PyGaze
##
##	PyGaze is a Python module for easily creating gaze contingent experiments
##	or other software (as well as non-gaze contingent experiments/software)
##	Copyright (C) 2012-2013  Edwin S. Dalmaijer
##
##	This program is free software: you can redistribute it and/or modify
##	it under the terms of the GNU General Public License as published by
##	the Free Software Foundation, either version 3 of the License, or
##	(at your option) any later version.
##
##	This program is distributed in the hope that it will be useful,
##	but WITHOUT ANY WARRANTY; without even the implied warranty of
##	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##	GNU General Public License for more details.
##
##	You should have received a copy of the GNU General Public License
##	along with this program.  If not, see <http://www.gnu.org/licenses/>
#

import os.path, pickle

# # # # #
# general

datadir = os.path.split(os.path.abspath(__file__))[0]
datafile = 'highscores.dat'

# # # # #
# functions

def find():
	
	"""Checks if there is a highscores file and loads it if it exists;
	otherwise a new file is created"""
	
	# check if there already is a highscores file
	if os.path.isfile(os.path.join(datadir,datafile)):
		# if there is one, load it
		return load()
	else:
		# if it doesn't exist, create a new one
		return new()


def load():
	
	"""Loads high scores from an existing highscores file"""
	
	# open pickle file
	picklefile = open(datafile, "rb")
	
	# load highscores
	highscores = pickle.load(picklefile)
	
	# close file
	picklefile.close()
	
	return highscores


def new():
	
	"""Creates a new (empty!) high scores file, overwritting any existing file"""
	
	# create new highscores dict
	highscores = {'names':[],'scores':[],'loser':['',0]}

	# open data file
	picklefile = open(datafile, "wb")
	
	# store highscores
	pickle.dump(highscores, picklefile)
	
	# close file
	picklefile.close()
	
	return highscores


def update(name, score):
	
	"""Updates the highscores file with the new name and score"""
	
	# check the current high scores
	replace = False
	highscores = find()

	# check if there are highscores
	if highscores['names'] == []:
		highscores['names'].append(name)
		highscores['scores'].append(score)

	else:
		# check if highscores list is shorter than five names
		if len(highscores['names']) < 5:
			inserted = False
			
		# in any other case, keep track of biggest loser
		else:
			inserted = True
	
			# check if current score is lowest
			if score < highscores['loser'][1]:
				highscores['loser'][0] = name
				highscores['loser'][1] = score
	
		# check if current score is among highest
		for i in range(0,len(highscores['names'])):
			if score > highscores['scores'][i]:
				# add name and score to highscores
				highscores['names'].insert(i,name)
				highscores['scores'].insert(i,score)
				replace = True
				inserted = True
				# kill the for loop to prevent further addition of current score
				break
		
		# if the new score is the lowest, but there are fewer than five score
		if not inserted:
			highscores['names'].append(name)
			highscores['scores'].append(score)

	
	# kick out lowest score
	if replace:
		highscores['names'].pop(-1)
		highscores['scores'].pop(-1)
	
	# open data file
	picklefile = open(datafile, "wb")
	
	# store highscores
	pickle.dump(highscores, picklefile)
	
	# close file
	picklefile.close()
	
	# return current scores in a string
	return current(highscores)


def current(highscores):
	
	"""Returns a string containing a list of the current high scores
	
	arguments
	highscores	--	a dict as is stored in highscores.dat
	
	returns
	highscores	--	a string containing in the following layout:
				name		score
				edwin		500000
				player2	123456
				player3	123456
				player4	123456
				player5	123456
				
				biggest loser:
				player6	-10000
	"""
	
	# basic highscore string
	hcstring = 'name		score\n'
	
	# fill out highscore string
	for i in range(0,len(highscores['names'])):
		
		name = highscores['names'][i]
		score = highscores['scores'][i]
		
		if len(name) < 8:
			name = name + (8 - len(name))*' '
		else:
			name = name[:8]
		
		string = name + '	' + str(score) + '\n'

		hcstring += (string)
	
	# add loser
	if highscores['loser'][0] != '':
		name = highscores['loser'][0]
		score = highscores['loser'][1]
		
		if len(name) < 8:
			name = name + (8 - len(name))*' '
		else:
			name = name[:8]
		
		hcstring += ('\nbiggest loser:\n%s	%d' % (name, score))
	
	return hcstring