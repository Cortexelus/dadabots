#!/usr/bin/env python
# encoding: utf=8

"""
becawwrdsaekva.py

Every section weaves through itself backwards.

Cortexelus James Carr
Music Hack day 11/11/2012
"""

import echonest.audio as audio
from echonest.sorting import *
from echonest.selection import *
import echonest.action as action
import pyechonest.config as config
config.MP3_BITRATE = 128
import math
	
usage = """
Usage: 
	python becawwrdsaekva.py <inputFilename> <outputFilename.wav>

Example:
	python becawwrdsaekva.py hypersisyphus.mp3 hupprsisyehys.mp3
"""

def main(inputFilename, outputFilename, windowing):
	print "HERE WE GO!!!!"
	print inputFilename
	print "\n"
	print outputFilename
	print "\n"
	song = audio.LocalAudioFile(inputFilename)
	
	print "Cool, we loaded the song"
	
	sample_rate = song.sampleRate
	num_channels = song.numChannels
	out_shape = list(song.data.shape)
	out_shape[0] = 2
	out = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)
	
	chunks = []
	for section in song.analysis.sections:
		segs = song.analysis.segments.that(are_contained_by(section))
		
		seglen = len(segs)
		print seglen
		for i in range(0, seglen):
			if i%2 :
				seg = song[segs[i]]
				if windowing:
					seg.data = window(seg.data)
				out.append(seg)
			else:
				seg = song[ segs[seglen - i - 1 ]]
				try:
					seg.data = seg.data[::-1]
					if windowing:
						seg.data = window(seg.data)
					out.append(seg)
					del(seg.data)
					del(seg)
				except:
					print "fuckkkkk"
					seg = song[segs[i]]
					if windowing:
						seg.data = window(seg.data)
					out.append(seg)
			
				
	
	
	#newAudio = audio.getpieces(song, chunks)
	out.encode(outputFilename)
	#newAudio.enc
def window(data):
	w = 8000 # window size; number of samples to taper off
	s = len(data) # total number of samples in segment 
	if(s<2*w):
		w = math.floor(s/2)-1
	
	for n in range(0, w):
		#r = pow(2, i/w)-1  # ratio by which to taper
		#r = 0.5 * (1 - math.cos((2*3.14*n)/( w-1)))
		r = (pow(10, n/w)-1)/9
		data[n] *= r # beginning sample
		data[s-n-1] *= r # end sample
	
	return data
	
	

if __name__ == '__main__':
	import sys
	try :
		inputFilename = sys.argv[1]
		outputFilename = sys.argv[2]
		window = bool(int(sys.argv[3]))
	except :
		print usage
		sys.exit(-1)
	
	main(inputFilename, outputFilename, window)
