# Clustering using K-Means
# See https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html#sklearn.cluster.KMeans.get_params
#
# V5 Oct 5, 2020 Consolidated code into one program
#
# Tom Zimmerman, IBM Research
# This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297, Center for Cellular Construction. Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.

from sklearn.cluster import KMeans
import numpy as np

################ USER SETTINGS #####################
VID_NAME=r'C:\Code\A_PINC_SFSU\blep1.mp4'       # video to be displayed
FEATURE_FILE_NAME=r'featureFile_2.csv'          # feature file input
CLUSTER_FILE_NAME=r'clusterFile_2.csv'          # cluster file output (feature file with objID replaced with clusterID 
CLUSTERS=5# how many clusters to create

############# CONSTANTS and VARIABLES ###################
# feature file index
FRAME=0; ID=1; CLUSTER=1; X0=2; Y0=3; X1=4; Y1=5; AREA=6; ASPECT_RATIO=7; TEXTURE=8; SOLIDITY=9;    # index to feature and cluster file
clusterHeader='frame,cluster,x0,y0,x1,y1,area,aspectRatio,texture,solidity'                         # header out cluster output file
X_REZ=640; Y_REZ=480;                                                                               # display resolution

#################### FUNCTIONS ###########################
def doCluster(XT):
    K=KMeans(n_clusters=CLUSTERS)       # initiate the k means estimator
    K.fit(XT)                           # Compute k-means clustering
    predict=K.fit_predict(XT)           # Predict the closest cluster each sample in X belongs to.
    centers = np.array(K.cluster_centers_)
    #print('centers',centers)
    inertia=K.inertia_
    iterations=K.n_iter_
    scaledInertia=int(inertia/1000000)  # inertia is a big floating point number, so divide by 1M and take integer value for easy reading when displayed 
    print('inertia',scaledInertia,'iterations',iterations)   
    return(K,predict,centers)

####################### MAIN ########################
# load feature file
featureFile=np.loadtxt(FEATURE_FILE_NAME,skiprows=1,delimiter=',')
print('Loaded',FEATURE_FILE_NAME,'Shape',featureFile.shape)

# Cluster and put cluster group into obj file as predicted class
XT=featureFile[:,AREA:]

# Ppredict cluster using K-mean on features
(K,predict,centers)=doCluster(XT)
featureFile[:,CLUSTER]=predict[:] # assign cluster to predicted class

# Save cluster file
np.savetxt(CLUSTER_FILE_NAME,featureFile,header=clusterHeader,fmt='%f',delimiter=',') # saves numpy array as a csv file    
print('saved cluster file',CLUSTER_FILE_NAME)


