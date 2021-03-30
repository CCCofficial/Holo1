# Create composite image by selecting darkets pixel of several Z reconstructions.
# 
# V5 3.30.21 removed summing with the last composite image to get higher contrast
#
# Thomas Zimmerman IBM Research-Almaden, Center for Cellular Construction (https://ccc.ucsf.edu/) 
# This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297 
# Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.

import cv2
import numpy as np

# put the link to your video here
vid=r'C:\Users\ThomasZimmerman\Videos\microscope\Hologram\BrianRusk\Videos\326G.mp4'

# tweek performance variables
minZ = 4000 # minimum possible Z value.  
maxZ = 7000 # maximum possible Z value.  
zStep = 500  # how many Z values to traverse at a time.
SKIP_FRAME=30 # number of frames to skip
THRESH=2 # Binary quantization threshold, lower values detects more objects
MIN_AREA=50    # min area of object detected
MAX_AREA=1500
MAX_OBJ=50 # maximum objects to process

# other constants you should not need to change
wvlen = 650.0e-9 # wavelength of laser. Blue is 405 nm. Red is 650
dxy   = 1.4e-6 # imager pixel size in meters.
zScale=1e-6 # convert z units to microns
VGA=(640,480)
X_REZ=640; Y_REZ=480; # viewing resolution
MIN_X=100; MIN_Y=100; # minimum full size of cropped image for reconstruction
AGC_SETTLE=30   # skip this many frames in the beginning of video to let AGC calm down

def getMedian(vid,medianFrames):
    # Open Video
    print ('openVideo:',vid)
    cap = cv2.VideoCapture(vid)
    maxFrame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print('maxFrame',maxFrame)
     
    # Randomly select N frames
    print('calculating median for',medianFrames,'frames')
    frameIds = AGC_SETTLE + (maxFrame-AGC_SETTLE) * np.random.uniform(size=medianFrames)
    frames = [] # Store selected frames in an array
    for fid in frameIds:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fid)
        ret, colorIM = cap.read()
        grayIM = cv2.cvtColor(colorIM, cv2.COLOR_BGR2GRAY)    # convert color to grayscale image
        frames.append(grayIM)
    medianFrame = np.median(frames, axis=0).astype(dtype=np.uint8)     # Calculate the median along the time axis
    #medianFrame=cv2.medianBlur(medianFrame,BLUR_MEDIAN)       # blur image to fill in holes to make solid object
    cap.release()
    return(medianFrame)

def recoFrame(cropIM, z):
    complex = propagate(np.sqrt(cropIM), wvlen, z*zScale, dxy)	 #calculate wavefront at z
    amp = np.abs(complex)**2          # output is the complex field, still need to compute intensity via abs(res)**2
    ampInt = amp.astype('uint8')
    return(ampInt)

def propagate(input_img, wvlen, zdist, dxy):
    M, N = input_img.shape # get image size, rows M, columns N, they must be even numbers!

    # prepare grid in frequency space with origin at 0,0
    _x1 = np.arange(0,N/2)
    _x2 = np.arange(N/2,0,-1)
    _y1 = np.arange(0,M/2)
    _y2 = np.arange(M/2,0,-1)
    _x  = np.concatenate([_x1, _x2])
    _y  = np.concatenate([_y1, _y2])
    x, y  = np.meshgrid(_x, _y)
    kx,ky = x / (dxy * N), y / (dxy * M)
    kxy2  = (kx * kx) + (ky * ky)

    # compute FT at z=0
    E0 = np.fft.fft2(np.fft.fftshift(input_img))

    # compute phase aberration
    _ph_abbr   = np.exp(-1j * np.pi * wvlen * zdist * kxy2)
    output_img = np.fft.ifftshift(np.fft.ifft2(E0 * _ph_abbr))
    return output_img

####################### MAIN ###################
medianFrames=20
medianIM=getMedian(vid,medianFrames) 
    
cap = cv2.VideoCapture(vid)
frameCount=AGC_SETTLE # skip this many frames in the beginning of video to let AGC calm down
firstTime=1
cap.set(cv2.CAP_PROP_POS_FRAMES, frameCount) # starting frame
while(cap.isOpened()):
    #cap.set(cv2.CAP_PROP_POS_FRAMES, frameCount)
    # read key, test for 'q' quit
    key=cv2.waitKey(1) & 0xFF # pause 1 second (1000 msec)
    if key== ord('q'):
        break
    
    # get image
    ret, frameIM = cap.read()
    if not ret: # check to make sure there was a frame to read
        print('Can not find video or we are all done')
        break
    frameCount+=SKIP_FRAME

    grayIM = cv2.cvtColor(frameIM, cv2.COLOR_BGR2GRAY)    # convert color to grayscale image  
    grayIM=cv2.subtract(grayIM,medianIM)
    
    # create composite image with darkest pixel
    darkIM=recoFrame(grayIM, minZ)    
    for z in range(minZ+zStep, maxZ, zStep):
        recoIM=recoFrame(grayIM, z)
        darkIM=np.minimum(darkIM,recoIM)

    # bootstrap first time through loop
    if firstTime:
        lastIM=darkIM
        firstTime=0

    # increase constrast by summing images, only works if SKIP_FRAME ~ 1
    #sumIM=cv2.add(darkIM,lastIM)
    #lastIM=darkIM
    
    #lastIM=darkIM
    BLUR=7
    blurIM=cv2.medianBlur(darkIM,BLUR) # blur image to fill in holes to make solid object
  
    # binary quantize using fixed threshold
    ret,binaryIM = cv2.threshold(blurIM,THRESH,255,cv2.THRESH_BINARY) # threshold image to make pixels 0 or 255

    # draw bounding boxes around objects
    objCount=0      # used as object ID in objectArray
    color=(255,0,0) # blue boundary color
    THICK=1         # bounding box line thickness
    dummy,contourList, hierarchy = cv2.findContours(binaryIM, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # all countour points, uses more memory
    for objContour in contourList:                  # process all objects in the contourList
        area = int(cv2.contourArea(objContour))     # find obj area
        PO = cv2.boundingRect(objContour)
        x0=PO[0]; y0=PO[1]; x1=x0+PO[2]; y1=y0+PO[3]
        THICK=3 # bounding box line thickness
        if area>=MIN_AREA and area<MAX_AREA and objCount<MAX_OBJ: # only detect acceptable size objects
            cv2.rectangle(frameIM, (x0,y0), (x1,y1), color, THICK) # place GREEN rectangle around each object, BGR
            objCount+=1
            
    #cv2.imshow('sumIM', cv2.resize(sumIM, (VGA)))      # display reduced image
    cv2.imshow('binaryIM', cv2.resize(binaryIM, (VGA)))      # display reduced image
    #cv2.imshow('recoIM', cv2.resize(darkIM, (VGA)))      # display reduced image
    cv2.imshow('frameIM', cv2.resize(frameIM, (VGA)))      # display reduced image
    #cv2.imshow('darkIM', cv2.resize(darkIM, (VGA)))      # display reduced image
    cv2.waitKey(100) 
    
cv2.destroyAllWindows()
