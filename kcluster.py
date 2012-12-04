from pylab import plot,show
from numpy import vstack,array
from numpy.random import rand
from scipy.cluster.vq import kmeans,vq

# data generation
# rand creates a random 150x2 matrix..or a multidimensional array of 150 (two floated) arrays
# vstack concatenates matrices together
data = vstack((rand(150,2),rand(150,2)))

# computing K-Means with K = 2 (2 clusters)
centroids,_ = kmeans(data,4)
# assign each sample to a cluster
idx,_ = vq(data,centroids)
#idx lists the cluster that each data point belongs to [2, 0, 0, 1, 2]

# some plotting using numpy's logical indexing

#plot(list of x's, list of y's)
# data[idx==0] is a list of all the data points that belong to cluster 0
plot(data[idx==0,0],data[idx==0,1],'ob',
     data[idx==1,0],data[idx==1,1],'or',
     data[idx==2,0],data[idx==2,1],'og',
     data[idx==3,0],data[idx==3,1],'ok')
plot(centroids[:,0],centroids[:,1],'sg',markersize=8)
show()










