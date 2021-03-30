# FEATURES EXTRACTION

# V12 23 Oct 2020 renamed f as featureVector, ar and texture were reversed on creation of feature vector
# V11 29 Sept 2020 replaced velocity with speed sampled over SPEED_WINDOW samples
# V9 added aspectRatio to feature list
#
# Thomas Zimmerman IBM Research-Almaden, Center for Cellular Construction (https://ccc.ucsf.edu/) 
# This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297 
# Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.

import numpy as np
import cv2
from skimage import feature
from mahotas.zernike import zernike_moments
from mahotas.features import haralick
from scipy.stats import kurtosis,skew,entropy
import math
import Common_4 as C  # constants used by all programs

def getFeatures(grayROI, binaryROI, objContour):
    # features are first converted to lists which makes them easier to append
    # at the end of the function, they are converted to a numpy vector (1xN)
    featureList=[]
    
    #SHAPE
    # area
    area = cv2.contourArea(objContour)

    # aspect ratio
    ((x0,y0),(w,h),theta) = cv2.minAreaRect(objContour)  # from https://www.programcreek.com/python/example/89463/cv2.minAreaRect 
    if w==0 or h==0:
        aspectRatio=0
    elif w>=h:
        aspectRatio = float(w)/h
    else:
        aspectRatio = float(h)/w

    # solidity
    hull = cv2.convexHull(objContour)    
    hull_area = cv2.contourArea(hull)
    solidity = float(area)/hull_area

    # ellipse
    (xe,ye),(eMajor,eMinor),angle = cv2.fitEllipse(objContour)

    # contour
    contourLen=len(objContour)   
    mean = np.mean(objContour)
    std = np.std(objContour)
    perimeter = cv2.arcLength(objContour,True)

    # circle
    (xc,yc),radius = cv2.minEnclosingCircle(objContour)

    # texture
    edgeIM = cv2.Canny(grayROI,100,200) # edge_detection
    onPix=np.sum(edgeIM)/255
    (h,w)=grayROI.shape
    texture=float(onPix/(w*h))
    shape=[area,aspectRatio,texture,solidity,eMajor,eMinor,contourLen,perimeter,radius,mean,std]
    featureList.append(shape)

    # HU MOMENTS
    moments = cv2.moments(binaryROI)
    hu = cv2.HuMoments(moments)
    huMoments = -np.sign(hu)*np.log10(np.abs(hu))
    huMoments=huMoments[:,0]
    featureList.append(huMoments.tolist())

    # ZERNIKE MOMENTS
    W, H = grayROI.shape
    R = min(W, H) / 2
    z = zernike_moments(grayROI, R, 8)
    zsum=np.sum(z[1:])
    z[0]=zsum           # first Zernike moment always constant so replace with sum
    featureList.append(z.tolist())

    # HARALICK FEATURES
    har = haralick(grayROI)
    haralickMean = har.mean(axis=0)
    featureList.append(haralickMean[1:].tolist()) # first entry is usually 0

    # GRAYSCALE HISTOGRAM
    grayHist=np.zeros((5))
    histogram = cv2.calcHist([grayROI], [0], None, [255], [0, 255])
    grayHist[0] = histogram.mean()
    grayHist[1] = histogram.std()
    grayHist[2] = skew(histogram)
    grayHist[3] = kurtosis(histogram)
    histNorm = histogram / np.max(histogram)
    grayHist[4] = entropy(histNorm)
    featureList.append(grayHist.tolist())
      
    # LOCAL BINARY PATTERNS
    eps=1e-7                            # so we don't divide by zero
    radius = 8
    points = 8 * radius                 # Number of points to be considered as neighbourers 
    lbp = feature.local_binary_pattern(grayROI, points, radius, method='uniform') # Uniform LBP is used
    (hist, _) = np.histogram(lbp.ravel(),bins=np.arange(0, points + 3),range=(0, points + 2))
    hist = hist.astype("float")         
    lbpHist = hist/(hist.sum() + eps)   # normalize the histogram
    a=lbpHist[0:6]                      # take the first 6 values and last 2 values, the rest are usually 0
    b=lbpHist[-2:]
    c=np.concatenate((a, b))
    featureList.append(c.tolist())

    # convert featureList to featureVector (a numpy array 1xN)
    ff=featureList[0]+featureList[1]+featureList[2]+featureList[3]+featureList[4]+featureList[5]
    featureVector=np.array([ff])
    #print('featureVector shape',featureVector.shape)
    return(featureVector)

def calcSpeed(obj):
    # speed calculated as distance between two points separated by SPEED_WINDOW frames

    oc=obj[np.lexsort((obj[:,C.FRAME],obj[:,C.TRACK_ID]))] # sort by ID then FRAME
    startIndex=0                    # index where new ID starts
    speed=0
    myID=-1                         # used to detect new ID which resets filter
    for oi in range(len(obj)):
        if myID!=oc[oi,C.TRACK_ID]:       # when new ID detected, reset filter
            myID=oc[oi,C.TRACK_ID]        # update ID
            startIndex=oi           # location of first obj of new ID
            oc[oi,C.SPEED]=0        # initialize new ID speed
        else:
            if oi-startIndex<=C.SPEED_WINDOW:  # if window hasn't been reached, set speed to zero
                speed=0
                oc[oi,C.SPEED]=speed
            else:
                lagIndex=oi-C.SPEED_WINDOW    # speed calculated as distance between current location and location SPEED_WINDOW frames ago
                dx=oc[oi,C.XC]-oc[lagIndex,C.XC]
                dy=oc[oi,C.YC]-oc[lagIndex,C.YC]
                speed=math.sqrt(dx*dx+dy*dy)
                oc[oi,C.SPEED]=speed
        #print('oi',oi,'ID',myID,'startIndex',startIndex,'speed',speed)
    # resort oc by frame
    oc=oc[oc[:,C.FRAME].argsort()]     # sort obj by frame count
    return(oc)
