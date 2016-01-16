from pylab import plot,show
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
config.MP3_BITRATE = 192


inputFilename="mp3/violin111.mp3"
inputFilename2="mp3/isaaccjlaugh.mp3"


# USAGE/EXAMPLE
# python kcluster_afromb.py INPUT INPUT OUTPUT CLUSTERS MIX
# python kcluster_afromb.py build.mp3 from.mp3 to.mp3 5 0.5



inputFilename = sys.argv[1]
inputFilename2 = sys.argv[2]

outputFilename = sys.argv[3]
# how many different groups will we cluster our data into?
num_clusters = int(sys.argv[4])
# how many different groups will we cluster our data into?
mix = float(sys.argv[5])


song = audio.LocalAudioFile(inputFilename)
song2 = audio.LocalAudioFile(inputFilename2)
	
	
sample_rate = song.sampleRate
num_channels = song.numChannels
out_shape = list(song.data.shape)
out_shape[0] = 2
out = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)


"""
outs = [None]*2
for n in range(0,num_clusters):
	outs[n] = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)
"""

# for each section in song1
for sectionnumber in range(0,len(song.analysis.bars)):
	# song1 section
	section = song.analysis.bars[sectionnumber]
	# song2 section. If too many sections, it loops back to beginning
	sectionnumber2 = sectionnumber % len(song2.analysis.sections)
	section2 = song2.analysis.sections[sectionnumber2]
	
	print "SECTION PAIRING: %i AND %i" % (sectionnumber, sectionnumber2)
	# default is grab all segments
	#sectionsegments = song.analysis.segments
	#sectionsegments2 = song2.analysis.segments

	# here we just grab the segments that overlap the section
	sectionsegments = song.analysis.segments.that(overlap(section))
	sectionsegments2 = song2.analysis.segments.that(overlap(section2))
	
	# this is just too easy
	# song.analysis.segments.timbre is a list of all 12-valued timbre vectors. 
	# must be converted to a numpy.array() so that kmeans(data, n) is happy
	data = array(sectionsegments.timbre)
	data2 = array(sectionsegments2.timbre)

	# data generation
	# rand creates a random 150x2 matrix..or a multidimensional array of 150 (two floated) arrays
	# vstack concatenates matrices together
	# data = vstack((rand(150,2),rand(150,2)))

	while True:
		# computing K-Means with K = 2 (2 clusters)
		centroids,_ = kmeans(data,num_clusters)
		centroids2,_ = kmeans(data2,num_clusters)
		# assign each sample to a cluster
		idx,_ = vq(data,centroids)
		idx2,_ = vq(data2,centroids2)
		#idx lists the cluster that each data point belongs to [2, 0, 0, 1, 2]

		# sometimes kmeans won't return num_clusters
		if (len(centroids) == num_clusters) and (len(centroids2) == num_clusters): 
			break
		else:
			print "We want %i num_clusters, but instead we got %i and %i" % (num_clusters, len(centroids), len(centroids2))
	
	# How to sync up clusters?
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
	# list of clusterindexes from largest to smallest
	centroid_pairs = []

	
	for _,c in collection:
		centroid1 = array(centroids[c])
	
		min_distance = [999999999999999999999999,0]
		for ci in range(0,len(centroids2)):
			if ci in [li[1] for li in centroid_pairs]:
				continue
			centroid2 = array(centroids2[ci])
			euclidian_distance = norm(centroid1-centroid2)
			if euclidian_distance < min_distance[0]:
				min_distance = [euclidian_distance, ci]
		centroid_pairs.append([c,min_distance[1]])
		

	print centroid_pairs


	# Just so we're clear, we're rebuilding the structure of song1 with segments from song2

	# prepare song2 clusters, 
	segclusters2 = [[]]*len(centroids2)
	for s2 in range(0,len(idx2)):
		segment2 = sectionsegments2[s2]
		cluster2 = idx2[s2]
		segment2.numpytimbre = array(segment2.timbre)
		segclusters2[cluster2].append(segment2)
		
	# for each segment1 in song1, find the timbrely closest segment2 in song2 belonging to the cluster2 with which segment1's cluster1 is paired. 
	for s in range(0,len(idx)):
		segment1 = sectionsegments[s]
		cluster1 = idx[s]
		cluster2 = [li[1] for li in centroid_pairs if li[0]==cluster1][0]
		
		
		timbre1 = array(segment1.timbre)
		min_distance = [9999999999999,0]
		for seg in segclusters2[cluster2]:
			timbre2 = seg.numpytimbre
			euclidian_distance = norm(timbre2-timbre1)
			if euclidian_distance < min_distance[0]:
				min_distance = [euclidian_distance, seg]
		bestmatchsegment2 = min_distance[1]
		# we found the segment2 in song2 that best matches segment1
		
		
		# faster, more varied version, picks a random segment from that cluster
		# bestmatchsegment2 = choice(segclusters2[cluster2])
		
		reference_data = song[segment1]
		segment_data = song2[bestmatchsegment2]
		
		# do we stretch or do we add silence?
		#
		# SILENCE:
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
			   
			   
		mixed_data = audio.mix(segment_data,reference_data,mix=mix)
		out.append(mixed_data)

	
out.encode(outputFilename)
	
"""
RENDER TO FILES:

#this code makes segclusters, which is a list of each cluster of segments. 
segclusters = [[]]*num_clusters
for s in range(0, len(idx)):
	segment = song.analysis.segments[s]
	cluster_number = idx[s]
	outs[cluster_number].append(song[segment])


# render each out to files
inc = 0
for out in outs:
	out.encode("clusters/afromb"+str(inc)+".mp3")
	inc += 1


"""