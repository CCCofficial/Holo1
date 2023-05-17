# Confusion Matrix
# Thomas Zimmerman, IBM Research/CCC
# This material is based upon work supported by the NSF under Grant No. DBI-1548297.  
# Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation. 

from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sn

# Constants
VID_FILE_NAME=r'planktonVariety_960_544.mp4'
OBJECT_ARRAY_FILE_NAME=r'FeaturesForConfusionMatrix.csv'
# detection and feature column pointers
FRAME=0; TRACK_ID=1; TRACK_STATUS=2; CLUSTER=3; CLUSTER_REJECT=4; GRID_INDEX=5; CLASS=6;
X0=7; Y0=8; X1=9; Y1=10; XC=11; YC=12; TRACK_DISTANCE=13; DELTA_AREA=14; SPEED=15; 
MAX_OBJECT_VECTOR=16
MAX_FEATURE_VECTOR=68           # number of features Feature function returns
FEATURE_START=MAX_OBJECT_VECTOR;
FS=FEATURE_START;               # FS is an abbreviation so I don't have to keep writing this big constant name
AREA=FS; ASPECT_RATIO=FS+1; TEXTURE=FS+2; SOLIDITY=FS+3; E_MAJOR=FS+4;
E_MINOR=FS+5; CONTOUR_LEN=FS+6; PERIMETER=FS+7; RADIUS=FS+8; MEAN=FS+9; STD=FS+10;
FEATURE_END=FS+MAX_FEATURE_VECTOR;
PCA_1=FEATURE_END+1; PCA_2=PCA_1+1; PCA_3=PCA_2+1; MAX_OBJ_COL=PCA_3+1 

######### PROGRAM STARTS HERE ######################
# Load array
objectArray=np.loadtxt(OBJECT_ARRAY_FILE_NAME,skiprows=1,delimiter=',')
ds=np.where(objectArray[:,GRID_INDEX]>0)
print('Original grid images',len(ds[0]))

objectArray=objectArray[np.where(objectArray[:,CLUSTER_REJECT]==0)] # only use objects that haven't been removed
ds=np.where(objectArray[:,GRID_INDEX]>0)
print('After removing rejected images',len(ds[0]))

x=objectArray[ds[0],PCA_1:PCA_3+1] # features
y=objectArray[ds[0],CLUSTER]       # cluster

TEST_SIZE=0.5 # what fraction of plankton samples are used for testing 
x_train,x_test,y_train,y_test=train_test_split(x,y,test_size=TEST_SIZE)


# Display membership
print('train',len(x_train),'test',len(x_test))
unique=np.unique(y_train)
unique=unique.astype(int)
clusters=len(unique)
print('training clusters',clusters)
member=[]
for coi in unique:
    m=np.count_nonzero(y_train==coi)
    member.append(m)
print(member)

# Classify
classifier=tree.DecisionTreeClassifier()
classifier.fit(x_train,y_train)
y_predict=classifier.predict(x_test)

# Calculate classification performance
accuracy=round(accuracy_score(y_test,y_predict),2)
print('accuracy',accuracy)

# Create confusion matrix without normalization
cm=confusion_matrix(y_test, y_predict)  

# Normalize confusion matrix by the number of samples in each cluster
cmNorm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

# Plot normalized confusion matrix
plt.figure(figsize = (10,7))
xNames=['dil','eup1','ble1','bv','alg','ste','eup2','did','ble2','vb'] # replace with cluster plankton names
yNames=['dil','eup1','ble1','bv','alg','ste','eup2','did','ble2','vb'] # replace with cluster plankton names
#ax=sn.heatmap(cm,annot=True,xticklabels=xNames,yticklabels=yNames)  # if you want to view cm without normalization, use this instruction instead
ax=sn.heatmap(cmNorm,annot=True,xticklabels=xNames,yticklabels=yNames)
plt.title('Normalized confusion matrix')
plt.ylabel('True label')
plt.xlabel('Predicted label')
plt.show()

