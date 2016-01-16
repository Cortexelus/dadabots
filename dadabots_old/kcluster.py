from pylab import plot,show
from numpy import vstack,array
from numpy.random import rand
from scipy.cluster.vq import kmeans,vq

import echonest.audio as audio
from echonest.sorting import *
from echonest.selection import *
import pyechonest.config as config
config.MP3_BITRATE = 192


#def main(inputFilename, outputFilename):
inputFilename="mp3/softhotlong.mp3"
song = audio.LocalAudioFile(inputFilename)

sample_rate = song.sampleRate

num_channels = song.numChannels
out_shape = list(song.data.shape)
out_shape[0] = 2

# how many different groups will we cluster our data into?
num_clusters = 50

outs = [None]*num_clusters
for n in range(0,num_clusters):
	outs[n] = audio.AudioData(shape=out_shape, sampleRate=sample_rate,numChannels=num_channels)

# this is just too easy
# song.analysis.segments.timbre is a list of all 12-valued timbre vectors. 
# must be converted to a numpy.array() so that kmeans(data, n) is happy
data = array(song.analysis.segments.timbre)

# data generation
# rand creates a random 150x2 matrix..or a multidimensional array of 150 (two floated) arrays
# vstack concatenates matrices together
# data = vstack((rand(150,2),rand(150,2)))

# computing K-Means with K = 2 (2 clusters)
centroids,_ = kmeans(data,num_clusters)
# assign each sample to a cluster
idx,_ = vq(data,centroids)
#idx lists the cluster that each data point belongs to [2, 0, 0, 1, 2]

#this code makes segclusters, which is a list of each cluster of segments. 
segclusters = [[]]*num_clusters
for s in range(0, len(idx)):
	segment = song.analysis.segments[s]
	cluster_number = idx[s]
	outs[cluster_number].append(song[segment])
	
	
inc = 0
rand = random(
for out in outs:
	out.encode("clusters/cluster"+str(inc)+".mp3")
	inc += 1
	





