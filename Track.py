# Tracker
# V3 9/26/2020
# Thomas Zimmerman IBM Research-Almaden, Center for Cellular Construction (https://ccc.ucsf.edu/) 
# This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297 
# Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.

import numpy as np
import math
import Common as C # constants used by all programs

nextID=1 # start ID with 1

def findID(xc,yc,area,objectArray,oiStart,oiStop,assigned):
    #print('oiStart',oiStart,'oiStop',oiStop)
    # search all the objects in the past frame for the closest to current object
    bestOI=-1; minDistance=99999; dArea=99999; match=0; objID=-1; # set up loop and default values in case cannot process object
    for i in range(oiStart,oiStop):
        dx=xc-objectArray[i,C.XC]
        dy=yc-objectArray[i,C.YC]
        distance=math.sqrt(dx*dx+dy*dy)
        #print(i,round(distance,1))
        if distance<minDistance and objectArray[i,C.TRACK_ID] not in assigned:
            minDistance=distance
            bestOI=i
    if bestOI!=-1:  # only process if a match is found, otherwise return with default values indicating no match     
        # if distance and change of area isn't too big, match found
        if objectArray[bestOI,C.AREA]==0:
            dArea=C.MAX_DELTA_AREA+1 # matched with obj with no area so force bad match
        else:
            dArea=abs((area-objectArray[bestOI,C.AREA])/objectArray[bestOI,C.AREA])

        #print('0,',round(dArea,1))
        
        # if distance and area are acceptable, assign ID, else reject match
        if minDistance<C.MAX_MATCH_DISTANCE and dArea<C.MAX_DELTA_AREA:
            match=1          # distance and delta area are ok so assign ID
            objID=objectArray[bestOI,C.TRACK_ID]
        else:
            if minDistance>=C.MAX_MATCH_DISTANCE:
                match=-1
            else:
                match=-2
            objID=0             # dummy value since no match
    else:
        match=-3            # no good match found
        objID=0             # dummy value since no match    

    # match: 1=good, 0=no process, -1 distance, -2 dArea, -3 no match found
    return(match,objID,minDistance,dArea)

def trackObject(objectArray,oi,oiStart,oiStop,assigned):
    global nextID # defined at top of file, only seen by this file
    objID=-1

    frameCount=objectArray[oi,C.FRAME]
    area=objectArray[oi,C.AREA]
    xc=objectArray[oi,C.XC]
    yc=objectArray[oi,C.YC]
     
    if frameCount==0:           # all objects start out with a unique ID
        objID=nextID
        nextID+=1
        distance=0; dArea=0; match=1; assigned=1 # initial values for first frame
    else:
        (match,objID,distance,dArea)=findID(xc,yc,area,objectArray,oiStart,oiStop,assigned)
        if match==1: # good match
            assigned.append(objID)  # good match so prevent obj from being matched again
        else:                       # if can't find obj in previous frame, assign a new ID
            objID=nextID
            nextID+=1               # prepare for next assignment

    # save values
    objectArray[oi,C.TRACK_DISTANCE]=distance
    objectArray[oi,C.DELTA_AREA]=dArea
    objectArray[oi,C.TRACK_ID]=objID

    return(match,assigned,objectArray)
