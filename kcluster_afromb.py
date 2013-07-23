"""
kcluster_afromb.py

2013 CJ Carr, Zack Zukowski 
cortexel.us
cj@imreallyawesome.com
http://github.com/cortexelus/dadabots

An improved version of Ben Lacker's afromb.py.

Uses k-means clustering on timbre data.
For each segment in a:
	Puts it into one of k groups
	Matches that group with a group in b
	Picks a new segment from b's group (randomly, the best match, or from a set of best matches)

In this way, the diversity of timbre is preserved.
(afromb.py takes every segment in a and finds the closest segment in b---but this process doesn't preserve the diversity of b)

Which makes it possible to take simple beats (kick snare hithat) and layer an enslaught of samples ontop of them while preserving the ebb and flow of the rhythm. 
For example, as this song: http://soundcloud.com/cortexelus/23-mindsplosion-algorithmic

#############################

USAGE:
python kcluster_afromb.py INPUT1 INPUT2 OUTPUT MIX NUMCLUSTERS BESTMATCH

EXAMPLES:
python kcluster_afromb.py song_structure.mp3 sample_library.mp3 remix.mp3 0.8 10 2

# Setting NUMCLUSTERS to 1 and BESTMATCH to 1 is essentially the same thing as running the original afromb.py
python kcluster_afromb.py a.mp3 b.mp3 out.mp3 0.5 1 1  

# To layer an enslaught of samples on a simple beat, set k to around 3-6 and set bestmatch to 0. Sample enslaught!!!!!!!!
python kcluster_afromb.py drumbreaks.mp3 synthlib.mp3 out.mp3 0.5 4 0 

#############################

INPUT1: soundfile, the song's structure

INPUT2: soundfile, where the samples are coming from 

OUTPUT: output file, sounds like INPUT2 remixed to fit the structure of INPUT1

MIX The volume mix between remixed INPUT2 and the original INPUT1. 
0 only the original INPUT1
1.0 only the remixed INPUT2
0.5 half of each

NUMCLUSTERS: the k in k-means clustering.
There are usually about 500-1500 segments in a song. 
We groups those segments into K groups. 
k = 1 is the same as not running k-means clustering at all. 
I usually get good results using something between k = 3 (kick, snare, hihat) and k = 20, but you should really just experiment to find out, because it depends on your source files and what effect you want.  

BESTMATCH: Which segment do we pick from b's group? 
0 random
1 pick the best match
2 pick randomly from the best 2 matches
n pick randomly from the best n matches

#############################

TODO:
* How do we fit b's segments to a's structure? Right now we add silence. TODO: add option to stretch audio. 
* Option to set K as a fraction of total segments.

<3\m/

"""

from numpy import vstack,array
from numpy.random import rand
from numpy.linalg import norm
from scipy.cluster.vq import kmeans,vq
from random import choice

import sys
import echonest.audio as audio
from echonest.sorting import *
from echonest.selection import *
import pyechonest.config as config
config.MP3_BITRATE = 192 # take this line out if you want to use default bitrate

inputFilename = sys.argv[1]
inputFilename2 = sys.argv[2]
outputFilename = sys.argv[3]

# how many different groups will we cluster our data into?
mix = float(sys.argv[4])

# how many different groups will we cluster our data into?
num_clusters = int(sys.argv[5])

# best_match = 1  # slower, less varied version. Good for b's which are percussion loops
# best_match = 0 # faster, more varied version, picks a random segment from that cluster. Good for b's which are sample salads. 
best_match = int(sys.argv[6])

# analyze the songs
song = audio.LocalAudioFile(inputFilename)
song2 = audio.LocalAudioFile(inputFilename2)

# build a blank output song, to populate later
sample_rate = song.sampleRate
num_channels = song.numChannels
out_shape = list(song.data.shape)
out_shape[0] = 2
out = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)

# grab timbre data
# must be converted to a numpy.array() so that kmeans(data, n) is happy
data = array(song.analysis.segments.timbre)
data2 = array(song2.analysis.segments.timbre)

# computing K-Means with k = num_clusters
centroids,_ = kmeans(data,num_clusters)
centroids2,_ = kmeans(data2,num_clusters)
# assign each sample to a cluster
idx,_ = vq(data,centroids)
idx2,_ = vq(data2,centroids2)
#idx lists the cluster that each data point belongs to
# ex. (k=2) [2, 0, 0, 1, 0, 2, 0, 0, 1, 2]

# How to pair up clusters?
# I think a largest-first greedy algorithm will work. 
# 1) Find largest cluster A[c] in A
# 2) Find closest cluster in B from A[c]
# 3) Pair them. Remove from data. 
# 4) Continue until everything is paired. 

# first create a collection, and then sort it
# not using python's collection, because of python2.6 compatability
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
	segment1 = song.analysis.segments[s]
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
		
	reference_data = song[segment1]
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
	out.append(mixed_data)

# redner output
out.encode(outputFilename)
