# Detect and Track objects to get location, features and ID

import Feature as F
import Track as T
import numpy as np
import cv2
import Common as C
import colorsys

# V10 Nov 10, 2020 If MAX_FRAME==0, read all the frames.
# V9 Nov  4, 2020 Put a white border around original image in case it has a black border, to prevent findContour detecting whole image as one object
# V8 Oct 24, 2020 Got rid of objectVector by writing directly into ObjectArray
# V7 Oct 23, 2020 Use full size image for best results (don't reduce resolution)
# V6 Oct 8, 2020  Color code reject, white=dArea, black=distance, gray=no match
# V5 Oct 8, 2020  Masks off everthing outside of obj contour to get rid of other objects in ROI
# V4 Oct 2, 2020  Reject objects near boarder and with other objects in extended ROI
# V3 Sept 29, 2020 Replaced velocity with average speed
#
# Thomas Zimmerman IBM Research-Almaden, Center for Cellular Construction (https://ccc.ucsf.edu/) 
# This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297 
# Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.

def checkROI(xMaxRez,yMaxRez,xx0,yy0,xx1,yy1):
    xx0-=C.ENLARGE; yy0-=C.ENLARGE; xx1+=C.ENLARGE; yy1+=C.ENLARGE;
    touch=0         # assume enlarged ROI does not touch boundary
    x0=max(xx0,0)   # check for negative
    x1=min(xx1,xMaxRez) # check for too big 
    y0=max(yy0,0)
    y1=min(yy1,yMaxRez)
    if x0!=xx0 or x1!=xx1 or y0!=yy0 or y1!=yy1: # if changed any, report touch image boarder
        touch=1
    return(touch,x0,y0,x1,y1)

def maskIM(colorIM,threshIM,cnt,x0,y0,x1,y1):
    # create a mask based on image contour
    blackIM=np.zeros_like(threshIM)
    cv2.drawContours(blackIM, [cnt], -1,255,-1) # function takes array of arrays so need [objContour] !!!
    binaryROI=blackIM[y0:y1,x0:x1]
    colorROI=colorIM[y0:y1,x0:x1]
    colorROI = cv2.bitwise_and(colorROI,colorROI,mask = binaryROI)
    grayROI = cv2.cvtColor(colorROI, cv2.COLOR_BGR2GRAY)     # convert color to grayscale image
    return(colorROI,grayROI,binaryROI)

def imageProcessing(colorIM):
    grayIM = cv2.cvtColor(colorIM, cv2.COLOR_BGR2GRAY)     # convert color to grayscale image
    blurIM=cv2.medianBlur(grayIM,C.BLUR)                 # blur image to fill in holes to make solid object
    ret,threshIM = cv2.threshold(blurIM,C.THRESH,255,cv2.THRESH_BINARY_INV) # threshold image to make pixels 0 or 255
    dummy,contourList, hierarchy = cv2.findContours(threshIM, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # all countour points, uses more memory
    return(grayIM,threshIM,blurIM,contourList)

def debugDisplay(oi,objectArray,match,rectIM):
 # draw bounding box in color representing ID
    objID=int(objectArray[oi,C.TRACK_ID]); x0=int(objectArray[oi,C.X0]); x1=int(objectArray[oi,C.X1]); y0=int(objectArray[oi,C.Y0]); y1=int(objectArray[oi,C.Y1]);
    
  # make colors for display
    MAX_COLOR=20
    HSV = [(x*1.0/MAX_COLOR, 1, 1) for x in range(MAX_COLOR)]
    color =list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV))

    colorIndex=objID%MAX_COLOR
    c=[255*color[colorIndex][0],255*color[colorIndex][1],255*color[colorIndex][2]] 
    if match==1:    # Color of ID, good match
        #cv2.rectangle(rectIM, (x0,y0), (x1,y1), c, C.THICK)        # place rectangle around matched object
        cv2.rectangle(rectIM, (x0,y0), (x1,y1), (0,255,0), C.THICK)        # place GREEN rectangle around matched object
    else:
        # match: 1=good, 0=no process, -1 distance, -2 dArea, -3 no match found
        if match==-1:   # BLACK big distance
            cv2.rectangle(rectIM, (x0,y0), (x1,y1), (0,0,0), C.THICK)  
        elif match==-2: # WHITE big dArea
            cv2.rectangle(rectIM, (x0,y0), (x1,y1), (255,255,255), C.THICK) 
        elif match==-3: # C.THICK WHITE no match found 
            cv2.rectangle(rectIM, (x0,y0), (x1,y1), (255,255,0), C.THICK*4)  
        else:           # GRAY unknown  
            cv2.rectangle(rectIM, (x0,y0), (x1,y1), (200,200,200), C.THICK)  
    return(rectIM)

def detectTrackFeature(VID):
    # processes video, returns obj file with obj location, features, etc for video
    status=0        # return status, 1=good (found and processed video)

    # Create objectArray to store objectArray+featureVector
    objectArray=np.zeros((0,C.MAX_OBJ_COL), dtype='float') # array of all objects for all frames
    objectArrayZero=np.zeros((1,C.MAX_OBJ_COL), dtype='float') # one row filled with zeros to append at beginning of loop

    print('Detect, Feature, Track video',VID)
    cap = cv2.VideoCapture(VID)
    frameCount=0    # keep video reader and object processing in sync
    oi=0            # object index, points into objectArray
    oiStart=0       # first obj of first frame (frameCount=0)
    match=False     # tracking flag, true if obj match found

    while(cap.isOpened()):  # start frame capture
        # get image
        ret, colorIM = cap.read()
        rectIM=np.copy(colorIM) # make copy that can be marked up with rectangles
        if not ret: # check to make sure there was a frame to read
            print('End of video detected, so finish')
            break
        
        # put a white border around image in case it has a black border
        # so the entire frame won't be detected as one object
        BORDER=10
        colorIM[0:BORDER,:,:]=255        # get rid of black boarder around image, turn it white so it won't appear as an object
        colorIM[-BORDER:,:]=255        # get rid of black boarder around image, turn it white so it won't appear as an object
        colorIM[:,0:BORDER,:]=255        # get rid of black boarder around image, turn it white so it won't appear as an object
        colorIM[:,-BORDER:,:]=255        # get rid of black boarder around image, turn it white so it won't appear as an object
        (yColorIM,xColorIM,color)=colorIM.shape
        
        
        # do image processing
        (grayIM,threshIM,blurIM,contourList)=imageProcessing(colorIM)
        
        # draw bounding boxes around objects
        oiStop=oi       # first object of the last frame
        assigned=[]     # create obj assigned list for tracker
        goodObjCount=0  # counts number of objects of acceptable area and no touch
        for objContour in contourList:
            area = cv2.contourArea(objContour)

            # Get bounding box for ROI
            PO = cv2.boundingRect(objContour)
            x0=PO[0]; y0=PO[1]; x1=x0+PO[2]; y1=y0+PO[3]; xc=x0+(x0+x1)/2; yc=y0+(y0+y1)/2;

            # check if object at the edge of image
            (touch,x0,y0,x1,y1)=checkROI(xColorIM,yColorIM,x0,y0,x1,y1) # return 1 if obj touches edge
            if area>C.MAX_AREA:
                print('MAX_AREA detected. touch',touch,'area',area,'len(contourList)',len(contourList))
            if area>C.MIN_AREA and area<C.MAX_AREA and touch==0:    # only process objects of good size that don't touch image edge
                goodObjCount+=1     # count number of acceptable objects
                # add a row of zeros and assign columns to obj variables
                objectArray=np.append(objectArray,objectArrayZero,axis=0)  # append empty row to objectArray, then fill with values 
                objectArray[oi,C.FRAME]=frameCount;    objectArray[oi,C.X0:C.YC+1]=(x0,y0,x1,y1,xc,yc); objectArray[oi,C.AREA]=area;
                
                # Get ROI using a mask to eliminate everything in the ROI except the object
                (colorROI,grayROI,binaryROI)=maskIM(colorIM,threshIM,objContour,x0,y0,x1,y1) # mask images using contour to eliminate any other objects in ROI                 
                
                # Track to get object ID
                (match,assigned,objectArray)=T.trackObject(objectArray,oi,oiStart,oiStop,assigned)

                # Get object features, add to objectArray, then append objectArray to objectArray
                featureVector=F.getFeatures(grayROI, binaryROI, objContour)
                objectArray[oi,C.FEATURE_START:C.FEATURE_END]=featureVector
                
                # Debug display
                if C.DEBUG:
                    rectIM=debugDisplay(oi,objectArray,match,rectIM)
                oi+=1                                                   # end of processing object so increment obj index
                
        # Finished processing objects in frame. Get indexing locations for tracker
        if frameCount==0:
            oiStart=0       # first obj of first frame 
            oiStop=oi       # last obj of first frame
        else:
            oiStart=oiStop  # first obj of current frame 

        if C.DEBUG:
            #cv2.imshow('blurIM', cv2.resize(blurIM,(C.X_REZ_DEBUG,C.Y_REZ_DEBUG)))      # display reduced image
            cv2.imshow('threshIM', cv2.resize(threshIM,(C.X_REZ_DEBUG,C.Y_REZ_DEBUG)))      # display reduced image
            cv2.imshow('rectIM', cv2.resize(rectIM,(C.X_REZ_DEBUG,C.Y_REZ_DEBUG)))      # display reduced image
            #print('Frame',frameCount,'Good objects',goodObjCount)
            key=cv2.waitKey(10) & 0xFF # read key, test for 'q' quit, pause in msec
            if key== ord('q'):
                break

        # Finished processing frame, get ready to read and process next frame
        status=1                # indicate that reading frames successfully
        frameCount+=1           # increment frame counter
        if frameCount%100==0:   # periodically give progress indicator to show program is running
            print('Processed frame:',frameCount)
        if C.MAX_FRAME!=0 and frameCount>C.MAX_FRAME: # end processing if reaches max frame (in case request to process partial video)
            break
        
    # Finished processing video so calc velocity and remove objects with features with NaN values
    if status:                      # if able to process video, calculate velocity from distance measurements
        objectArray=F.calcSpeed(objectArray)  # calc speed and place in obj feature columns
        print('before touch reject',objectArray.shape)
        objectArray=objectArray[~np.isnan(objectArray).any(axis=1)] # remove obj with features containing NaN values
        print('after touch reject',objectArray.shape)
        objectArray=objectArray[np.where(objectArray[:,C.SPEED]>C.MIN_SPEED)] # remove obj moving too slow
        print('after min speed reject',objectArray.shape)
        
    cap.release()
    cv2.destroyAllWindows()
    return(status,objectArray)

########## TEST ###########
if False:
    plankton='did_1_1'
    vid=r'C:\Users\ThomasZimmerman\Videos\microscope\WhiteLight\\'+plankton+'.mp4'
    #objFile='C:/Code/AAA/IEEE_V1/IEEE_V2/DetectTrackCluster/Cluster/csvFile/'+plankton+'_CLUSTER5.csv'
    objFile='test.csv'
    print('Processing',plankton)
    (status,objectArray)=detectTrack(vid)
    np.savetxt(objFile,objectArray,header=C.header,fmt='%f',delimiter=',') # saves numpy array as a csv file    
            

