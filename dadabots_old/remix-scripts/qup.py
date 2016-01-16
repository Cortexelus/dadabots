#!/usr/bin/env python
# encoding: utf=8

"""
qup.py

Turns any song into drum'n'bass. 
Why qup? Because we're turning music production on its head. 

CJ Carr (Cortexelus James)
Hack2LAUNCH 4/12/2013
"""
import copy
import random
import math
import echonest.audio as audio
import echonest.modify as modify
st = modify.Modify()
from echonest.sorting import *
from echonest.selection import *
import pyechonest.config as config
config.MP3_BITRATE = 192

import sys
from numpy import vstack,array
from numpy.random import rand
from numpy.linalg import norm
from scipy.cluster.vq import kmeans,vq
from random import choice

# take an input song
input_filename = "mp3/vaetxh-unfolding.mp3";
output_filename = "mp3/qup-creation.mp3";

input_filename = sys.argv[1]
output_filename = sys.argv[2]

song = audio.LocalAudioFile(input_filename)

# set
sample_rate = song.sampleRate
num_channels = song.numChannels
out_shape = list(song.data.shape)
out_shape[0] = 2
out = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)

secs = song.analysis.sections
num_sections = len(secs)
### ZEPTO -> DNB -> ZEPTO -> DNB ??


def loudness(section):
	segs = song.analysis.segments.that(overlap(section))
	num_segs = len(segs)
	loudness_total = 0
	for seg in segs:
		loudness_total += seg.loudness_max
	avg_loudness = loudness_total / num_segs
	return avg_loudness

	
def tempo_warp(section, bpm):
	print "tempo_warp"
	new_beat_duration = 60.0/bpm
	beats = song.analysis.beats.that(are_contained_by(section))
	
	new_beats = []
	for beat in beats:
		ratio = beat.duration / new_beat_duration
		new_beat = st.shiftTempo(song[beat], ratio)
		new_beats.append(new_beat)
	out = audio.assemble(new_beats)
	return out


#dnbify(song.analysis.sections[0])



def beatrepeat(section):
	print "original with beat repeat"

	beats = song.analysis.beats.that(are_contained_by(section))
	tatums = song.analysis.beats.that(are_contained_by(section))
	br = audio.AudioQuantumList()

	for _ in range(2): 
		br.append(song[beats[0]])
		br.append(song[beats[1]])
		br.append(song[beats[2]])
		br.append(song[beats[3]])
	for _ in range(2): 
		br.append(song[beats[0]])
		br.append(song[beats[1]])
	for _ in range(2): 
		br.append(song[beats[0]])
	for _ in range(2): 
		br.append(song[tatums[0]])

	return br

	
def beatrepeat_and_tempo_warp(section, bpm):
	print "beatrepeat_and_tempo_warp"
	beats = song.analysis.beats.that(are_contained_by(section))
	tatums = song.analysis.beats.that(are_contained_by(section))
	br = audio.AudioQuantumList()
	
	new_beat_duration = 60.0/bpm
	beats = song.analysis.beats.that(are_contained_by(section))
	
	new_beats = []
	for beat in beats:
		ratio = beat.duration / new_beat_duration
		new_beat = st.shiftTempo(song[beat], ratio)
		new_beats.append(new_beat)
	out = audio.assemble(new_beats)
	return out
	
	
	for _ in range(2): 
		br.append(song[beats[-4]])
		br.append(song[beats[-3]])
		br.append(song[beats[-2]])
		br.append(song[beats[-1]])
	
	
	
	
"""
shorter_beat = st.shiftTempo(song[beats[0]], 2)
for _ in range(8): 	
	more_beat_repeat.append(shorter_beat)
shorter_beat = st.shiftTempo(song[beats[0]], 4)
for _ in range(8): 	
	more_beat_repeat.append(shorter_beat)
shorter_beat = st.shiftTempo(song[beats[0]], 8)
for _ in range(16): 	
	more_beat_repeat.append(shorter_beat)
assembled_beat_repeat = audio.assemble(more_beat_repeat)
"""


	#return br
	
import shutil 
	
# dnbify
def dnbify(randombeat):
	print "dnbify"
	
	dnbfile = "mp3/breaks/RC4_Breakbeat_175 (%i).mp3" % randombeat
	dnbloop = audio.LocalAudioFile(dnbfile)
	
	# how many different groups will we cluster our data into?
	num_clusters = 5

	mix = 1.0
		
	dnbouts = []
	for layer in range(0, 2):
		# best_match = 1  # slower, less varied version. Good for b's which are percussion loops
		# best_match = 0 # faster, more varied version, picks a random segment from that cluster. Good for b's which are sample salads. 
		best_match = layer
		print "layer"
		print layer
		
		song1 = dnbloop
		song2 = song
		
		dnbout = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)
		
		# here we just grab the segments that overlap the section
		sectionsegments = song1.analysis.segments
		#for _ in range(3):
		#	sectionsegments.extend(song1.analysis.segments)
		sectionsegments2 = song2.analysis.segments #.that(overlap(section));
		

		# this is just too easy
		# song.analysis.segments.timbre is a list of all 12-valued timbre vectors. 
		# must be converted to a numpy.array() so that kmeans(data, n) is happy
		data = array(sectionsegments.timbre)
		data2 = array(sectionsegments2.timbre)
		
		"""
		# grab timbre data
		# must be converted to a numpy.array() so that kmeans(data, n) is happy
		data = array(song1.analysis.segments.timbre)
		data2 = array(song2.analysis.segments.timbre)
		"""
		
		
		# computing K-Means with k = num_clusters
		centroids,_ = kmeans(data,num_clusters)
		centroids2,_ = kmeans(data2,num_clusters)
		# assign each sample to a cluster
		idx,_ = vq(data,centroids)
		idx2,_ = vq(data2,centroids2)
		
		collection = []
		for c in range(0, num_clusters):
			ccount = 0
			for i in idx:
				if i==c: 
					ccount += 1
			collection.append([ccount, c])
		collection.sort()
		# list of cluster indices from largest to smallest

		centroid_pairs = []
		for _,c in collection:
			centroid1 = array(centroids[c])
			min_distance = [9999999999,0]
			for ci in range(0,len(centroids2)):
				if ci in [li[1] for li in centroid_pairs]:
					continue
				centroid2 = array(centroids2[ci])
				euclidian_distance = norm(centroid1-centroid2)
				if euclidian_distance < min_distance[0]:
					min_distance = [euclidian_distance, ci]
			centroid_pairs.append([c,min_distance[1]])

		print centroid_pairs
		# now we have a list of paired up cluster indices. Cool.

		# Just so we're clear, we're rebuilding the structure of song1 with segments from song2

		# prepare song2 clusters, 
		segclusters2 = [audio.AudioQuantumList()]*len(centroids2)
		for s2 in range(0,len(idx2)):
			segment2 = song2.analysis.segments[s2]
			cluster2 = idx2[s2]
			segment2.numpytimbre = array(segment2.timbre)
			segclusters2[cluster2].append(segment2)

		
		# for each segment1 in song1, find the timbrely closest segment2 in song2 belonging to the cluster2 with which segment1's cluster1 is paired. 
		for s in range(0,len(idx)):
			segment1 = song1.analysis.segments[s]
			cluster1 = idx[s]
			cluster2 = [li[1] for li in centroid_pairs if li[0]==cluster1][0]

			if(best_match>0):
				# slower, less varied version. Good for b's which are percussion loops
				
				"""
				# there's already a function for this, use that instead: timbre_distance_from
				timbre1 = array(segment1.timbre)
				min_distance = [9999999999999,0]
				for seg in segclusters2[cluster2]:
					timbre2 = seg.numpytimbre
					euclidian_distance = norm(timbre2-timbre1)
					if euclidian_distance < min_distance[0]:
						min_distance = [euclidian_distance, seg]
				bestmatchsegment2 = min_distance[1]
				# we found the segment2 in song2 that best matches segment1
				"""
				
				bestmatches = segclusters2[cluster2].ordered_by(timbre_distance_from(segment1))
				
				if(best_match > 1):
					# if best_match > 1, it randomly grabs from the top best_matches.
					maxmatches = max(best_match, len(bestmatches))
					bestmatchsegment2 = choice(bestmatches[0:maxmatches])
				else:
					# if best_match == 1, it grabs the exact best match
					bestmatchsegment2 = bestmatches[0]
			else:
				# faster, more varied version, picks a random segment from that cluster. Good for sample salads. 
				bestmatchsegment2 = choice(segclusters2[cluster2])
				
			reference_data = song1[segment1]
			segment_data = song2[bestmatchsegment2]
			
			# what to do when segments lengths aren't equal? (almost always)
			# do we add silence? or do we stretch the samples?
			add_silence = True
			
			# This is the add silence solution:
			if add_silence: 
				if reference_data.endindex > segment_data.endindex:
					# we need to add silence, because segment1 is longer
					if num_channels > 1:
						silence_shape = (reference_data.endindex,num_channels)
					else:
						silence_shape = (reference_data.endindex,)
					new_segment = audio.AudioData(shape=silence_shape,
											sampleRate=out.sampleRate,
											numChannels=segment_data.numChannels)
					new_segment.append(segment_data)
					new_segment.endindex = len(new_segment)
					segment_data = new_segment
				elif reference_data.endindex < segment_data.endindex:
					# we need to cut segment2 shorter, because segment2 is shorter
					index = slice(0, int(reference_data.endindex), 1)
					segment_data = audio.AudioData(None, segment_data.data[index], sampleRate=segment_data.sampleRate)
			else: 		  
				# TODO: stretch samples to fit.
				# haven't written this part yet.
				segment_data = segment_data

			# mix the original and the remix
			mixed_data = audio.mix(segment_data,reference_data,mix=mix)
			dnbout.append(mixed_data)
		
		dnbouts.append(dnbout)
	
	print "YEA"
	mixed_dnbouts = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)
	print len(dnbouts[0])
	print len(dnbouts[1])
	#for s in range(0,len(dnbouts[0])):
	#	print s
#		print dnbouts[0]
	#	print dnbouts[1]
	mixed_data = audio.mix(dnbouts[0], dnbouts[1], 0.5)
	mixed_dnbouts.append(mixed_data)
	print "woah"
	
	dnbrepeatout = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)
	for _ in range(4):
		dnbrepeatout.append(mixed_dnbouts)
	print "oh okay"
	return dnbrepeatout
	
	
# zeptoify
# creates a buildup
# basically orders segments with high timbre[6] by length
def zepto(length_seconds):	
	print "zeptoify"
	
	section = False
	if section==False:
		total_duration = song.analysis.duration
		segments = song.analysis.segments
	else:
		total_duration = section.duration
		#order by length)	
		segments = song.analysis.segments.that(are_contained_by(section))
		
	length_order = segments.ordered_by(duration)
	# grab the one with the highest timbre[6] value from every 4 segment
	i = 0

	length = len(segments)
	unused_segs = audio.AudioQuantumList()
	while total_duration > length_seconds:
		print_seg_durations(length_order)

		sorted_segs = audio.AudioQuantumList()

		while i < length:
			j = 0
			four_segs = audio.AudioQuantumList()
			# append the next four segments
			while j < 4: 
				if(j+i < length):
					four_segs.append(length_order[j + i])
					j += 1
				else: 
					break
			# order the four segments by timbre value 6
			timbre_segs = four_segs.ordered_by(timbre_value(6))
			# Remove the worst candidate while the total time is less than 30secs
			for k in range(0, j-1):
				sorted_segs.append(timbre_segs[k])
			unused_segs.append(timbre_segs[j-1])

			deduction = timbre_segs[j-1].duration
			total_duration = total_duration - deduction
			if total_duration < length_seconds:
				sorted_segs.extend(length_order[i:])
				break
			i = i + 4 
		length_order = copy.copy(sorted_segs)
		length = len(length_order)
		print "I think the total duration is " + str(total_duration)
		print "However the toal duration is actually " + str(get_total_duration(length_order))
		i = 0
	fixed_order = length_order.ordered_by(duration)
	fixed_order.reverse()

	#print_seg_durations(fixed_order)
	print "total duration: " + str(total_duration)
	#return [fixed_order, unused_segs]
	return fixed_order.render()
	
def get_total_duration(segment_list):
	total_dur = 0
	for seg in segment_list:
		total_dur += seg.duration
	return total_dur

def print_seg_durations(segments):
	string0 = ""
	for s in segments:
		string0 += str(s.duration) + ", "
	print string0	
	
	
	

def longestsample():
	length_order = song.analysis.segments.ordered_by(duration)
	return length_order[-1].render()
	
def original(section):
	print "original"

# combine

#itsalive = zepto(30)

for n in range(0,10):
	
	randombeat = random.randrange(17,86)
	itsalive = dnbify(randombeat)
	itsalive.encode(output_filename + "." + str(n) + "." + str(randombeat) + ".mp3")

#ITSALIVE = zepto(song.analysis, 40)
#ITSALIVE.encode(output_filename)
