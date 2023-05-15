# Display scatter plot of area, texture and aspect ratio of all objects for all frames, while viewing video
# V1 Sept 30, 2020 Color is object ID that varies with every frame (determined by the scan of findContour)
#
# Tom Zimmerman, IBM Research
# This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297, Center for Cellular Construction. Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.

# See video https://pythonprogramming.net/3d-scatter-plot-customizing/

############################## FOR EDUCATIONAL USE ONLY ####################
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib
import cv2
########## USER SETTINGS ##############################
VID=r'blep1.mp4' # PUT YOUR VIDEO HERE
FEATURE_FILE=r'featureFile.csv'

############## Program Constants and Variables #################
# make colors for displaying class
colorTable = [[0,0,255],[255,0,0],[0,255,255],[75,0,130],[0,255,0],[0,0,0]]
MAX_COLOR=len(colorTable)

X_REZ=640; Y_REZ=480;   # image resize 
FRAME=0; OBJ_ID=1; X0=2; Y0=3; X1=4; Y1=5; AREA=6; ASPECT_RATIO=7; TEXTURE=8; SOLIDITY=9;  # array column pointers 

########### Procedures ##############################
def plotCluster():  
    # plot clusters
    labels = f[:,OBJ_ID]                                    # Get lables to determine color
    X = f[:,AREA]; Y = f[:,TEXTURE]; Z = f[:,ASPECT_RATIO]; # load x,y,z with values to display in scatter plot 
    fig = plt.figure(1,figsize=(12, 9))                     # Create the figure
    ax = Axes3D(fig, rect=[0, 0, 1, 1], elev=48, azim=134)  # create the point-of-view for the 3D scatter plot
    sc=ax.scatter(X,Y,Z,c=labels, edgecolor='k',cmap='prism')
    ax.set_xlabel('AREA')
    ax.set_ylabel('TEXTURE')
    ax.set_zlabel('ASPECT_RATIO')
    plt.legend(*sc.legend_elements())                       # put a color legend on the figure
    fig.show()
    plt.pause(0.01)                                         # need delay to show figure
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
        vgaIM = cv2.resize(frameIM,(X_REZ, Y_REZ))
        while (f[oi,FRAME]==frameCount and eof==False):
            x0=int(f[oi,X0]); y0=int(f[oi,Y0]); x1=int(f[oi,X1]); y1=int(f[oi,Y1]); 
            colorIndex=int(f[oi,OBJ_ID])%MAX_COLOR  # make sure color index does not exceed the number of colors in our table!
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
#np.random.seed(5)
f=np.loadtxt(FEATURE_FILE,skiprows=1,delimiter=',')
print('Loaded',FEATURE_FILE)
plotCluster()
status=showVideo(VID)
print('video status',status)
print('Program ended, bye!')


