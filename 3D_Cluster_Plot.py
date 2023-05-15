# Display scatter plot of area, texture and aspect ratio
# Tom Zimmerman, IBM Research 26 Sept 2020
#
# This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297, Center for Cellular Construction.
# Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.

############################## FOR EDUCATIONAL USE ONLY ####################
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cv2
import clusterConstants as C # constants used by all programs
########## USER SETTINGS ##############################
PLANKTON='blep_1'
VID=r'blep1.mp4'
CLASS_FILE=r'blep_1_class.csv'

# make colors for displaying class
colorTable = [[0,0,255],[255,0,0],[0,255,255],[75,0,130],[0,255,0],[0,0,0]]

########### Procedures ##############################
def plotCluster():  
    # plot clusters
    labels = f[:,C.PREDICT_CLASS]              # Get lables to determine color
    X = f[:,C.AREA]; Y = f[:,C.TEXTURE]; Z = f[:,C.ASPECT_RATIO]; 
    fig = plt.figure(1,figsize=(4, 3))
    ax = Axes3D(fig, rect=[0, 0, .95, 1], elev=48, azim=134)
    sc=ax.scatter(X,Y,Z,c=labels, edgecolor='k',cmap='prism')
    ax.set_xlabel('AREA')
    ax.set_ylabel('TEXTURE')
    ax.set_zlabel('ASPECT_RATIO')
    plt.legend(*sc.legend_elements())
    fig.show()
    return
 
def showVideo(VID):
    status=0        # return status, 1=good (found and processed video)
    # display video using bounding box color to indicate predicted class
    cap = cv2.VideoCapture(VID)
    print('vid open',cap.isOpened())
    frameCount=0; oi=0;             # object index
    eof=False                       # end of file indicator
    while(cap.isOpened() and eof==False):
        ret, frameIM = cap.read()   # get image
        if not ret:                 # check to make sure there was a frame to read
            break
        vgaIM = cv2.resize(frameIM,(C.X_REZ, C.Y_REZ))
        while (f[oi,C.FRAME]==frameCount and eof==False):
            x0=int(f[oi,C.X0]); y0=int(f[oi,C.Y0]); x1=int(f[oi,C.X1]); y1=int(f[oi,C.Y1]); 
            colorIndex=int(f[oi,C.PREDICT_CLASS])
            cv2.rectangle(vgaIM, (x0,y0), (x1,y1), colorTable[colorIndex], 3) # place rectangle around each object, color indicate predicted class
            if oi==len(f)-1: # quit when reached last row
                eof=True
            else:
                oi+=1
        cv2.imshow('vgaIM', vgaIM)# display thresh image
        key=cv2.waitKey(100) & 0xFF # pause x msec
        frameCount+=1
        status=1            # indicate that reading frames successfully
    cap.release()
    cv2.destroyAllWindows()
    return(status)
            
    
################ Main ################
np.random.seed(5)
f=np.loadtxt(CLASS_FILE,skiprows=1,delimiter=',')
print('Loaded',CLASS_FILE)
plotCluster()
status=showVideo(VID)
print('video status',status)
print('Program ended, bye!')


