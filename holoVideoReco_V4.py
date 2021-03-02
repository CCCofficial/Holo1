'''
Interactive Holographic Reconstruction with Tkinter Interface
Thomas Zimmerman, IBM Research-Almaden
Holgraphic Reconstruction Algorithms by Nick Antipac, UC Berkeley and  Daniel Elnatan, UCSF
This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297, Center for Cellular Construction.
Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation. 

V4 3.01.21 Removed unused buttons, added instructions, uses vc3 support function file
V3 2.23.21 Changed Z_SCALE to be in units of 10 um 
V1 2.09.21

Button Fuctions
===============
Frame: Select frame to display
Crop: Crops section of image to reconstruction, smaller makes for faster reconstruction
Z: Change reconstruction height (distance between object and image sensor)
Display: Change size of reconstruction display (doesn't effect reconstruction or save image size)
SavePic: Saves reconstructed cropped image, image format= foo_23_100_200_300_holo.jpg and foo_23_100_200_3000_raw.jpg where:
        "foo" is from the video name
        "23" is frame number
        "100" and "200" are the x,y location of the center of the cropped image from the full frame image (1920x1080)
        "3000" is the z value (distance between object and image sensor (in microns)
        "raw" is the original cropped holographic image
        "holo" is the image reconstructed at distance z (3000um in this example)
Center: To center cropped image, press "Center", place cursor over center object, then left click
To end program, click 'X' in top right of button panel

General Use Guide
=================
Put your video file location in 'vid=' below.
Use Center to find an object of interest
Use Crop to select a cropping size that captures the object and it's fringes but not much else to speed up reconstruction time
Use Z+10 and Z-10 to get a coarse "focus" of the object
Use Z+1 and Z-1 to get a fine "focus" of the object
When you are happy with the image, click "SavePic" to save the image. The program will automatically save the raw and reconstructed images along with video name, frame number, crop location and reconstruction Z embeded in the image name.
Use Frame to move around the frames in the movie
'''

import tkinter as tk
import vc3 as vc    # a file of functions used by this program
import cv2
import numpy as np

vid=r'C:\Users\ThomasZimmerman\Videos\microscope\Hologram\ShortHoloVideo\M6.mp4' # <==== put your video location here, must be mp4, use ffmpeg to convert microscope .h264 to .mp4
vid=r'C:\Users\ThomasZimmerman\Videos\microscope\Hologram\fewPlankton\M3.mp4'
#vid=r'C:\Users\ThomasZimmerman\Videos\microscope\Hologram\50umLaserStentor\pinhole2.h264'

###################### INITIALIZE GLOBAL VALUES #############################
xRez=1920; yRez=1080;   # video resolution
displayScale=1          # scale display output
window=[0,yRez,0,xRez]
frameCount=0            # current frame being examined
Z=64                    # starting Z location (x10um)
CROP=25                 # starting crop size
BUTTON_WIDTH=10         # button display width
WINDOW_SCALE=10         # window size increment
Z_SCALE=0.00001         # convert integer Z units to 10 um
FULL_SCALE=2            # reduce full scale image by this factor so it fits in window
xc=1082; yc=468;        # initial center of crop window
getCenter=False         # flag that when sets xc,y, to mouse location on click
savePic=False           # save pic of reconstruction when flag set

# Button names. Some are left blank for future functions.
names = [
    ("Frame -10"),
    ("Frame -1"),
    ("Frame +1"),
    ("Frame +10"),
    ("Crop -10"),
    ("Crop -1"),
    ("Crop +1"),
    ("Crop +10"),
    ("Z -10"),
    ("Z -1"),
    ("Z +1"),
    ("Z +10"),
    (" "), 
    (" "),
    ("Display -1"),
    ("Display +1"), 
    (" "), 
    (" "),
    ("SavePic"),
    ("Center")
]

####################### PROCEDURES ##########################################
def doMouse(event,x,y,flags,param):
    global getCenter,xc,yc
    
    if getCenter and event == cv2.EVENT_LBUTTONDOWN:
        xc,yc = x*FULL_SCALE,y*FULL_SCALE # compensate for full scale scaling
        # xc and yc must be even number for FFT to work
        if xc%2!=0:
            xc+=1
        if yc%2!=0:
            yc+=1
        #print ('updated center',xc,yc)
        processImage()
    return

def updateStatusDisplay():
    textOut='   Frame='+ str(frameCount) + '    Crop=' + str(CROP) + '    Z=' + str(Z) + '    Display=' + str(displayScale)+'   '
    tk.Label(root, text=textOut,bg="yellow",justify = tk.LEFT).grid(row=0,column=0,columnspan=4)
    return

def savePicture(holoIM,cropIM):
    global v 
    if 'mp4' in vid:
        name=vid[:-4]
    elif 'h264' in vid:
        name=vid[:-5]
    else:
        name=vid

    # save holo image
    imageName=name+'_'+str(frameCount)+'_'+str(xc)+'_'+str(yc)+'_'+str(Z*10)+'_holo.jpg'
    cv2.imwrite(imageName,holoIM)
    print ('Saved image',imageName)
    
    # save raw cropped image
    imageName=name+'_'+str(frameCount)+'_'+str(xc)+'_'+str(yc)+'_'+str(Z*10)+'_raw.jpg'
    cv2.imwrite(imageName,cropIM)
    print ('Saved image',imageName)
    
    v.set(2)  # set choice to "+1 Frame" so user won't be confused by SavePic being on
    return
    
def updateWindow():
    global window
    x0=xc-(WINDOW_SCALE*CROP)
    x1=xc+(WINDOW_SCALE*CROP)
    y0=yc-(WINDOW_SCALE*CROP)
    y1=yc+(WINDOW_SCALE*CROP)

    x0=clamp(x0,0,xRez)
    x1=clamp(x1,x0,xRez)
    y0=clamp(y0,0,yRez)
    y1=clamp(y1,y0,yRez)

    window=[y0,y1,x0,x1]
    return

def doButton():
    global frameCount,displayScale,Z,CROP,getCenter,savePic,bkgState,bkgIM

    getCenter=False #clear flag in case button is not Center, allows multiple centers until another button pushed
    val=v.get()
    but=names[val]

    increment=0
    if "-10" in but:
        increment=-10
    elif "+10" in but:
        increment=10
    elif "-1" in but:
        increment=-1
    elif "+1" in but:
        increment=1

    if 'Center' in but:
        getCenter=True  # this flag tells doCenter to update xc,yc
    elif 'SavePic' in but:
        savePic=True  # flag indicates picture capture requested
    elif 'Frame' in but:
        frameCount+=increment
        frameCount=clamp(frameCount,0,MAX_FRAME-2) # limit frame to those in video
    elif 'Z' in but:
        Z+=increment
        if Z<1:
            Z=1
    elif 'Display' in but:
        displayScale+=increment
        if displayScale<1:
            displayScale=1
    elif 'Crop' in but:
        CROP+=increment
        if CROP<1:
           CROP=1
    
    updateStatusDisplay()
    processImage()
    return


def processImage():
    global savePic
    
    updateWindow()
    (ret,rawIM)=vc.getFrame(cap,frameCount)
    grayIM = cv2.cvtColor(rawIM, cv2.COLOR_BGR2GRAY)

    cropIM=grayIM[window[0]:window[1],window[2]:window[3]] # crop window of image
    recoIM=vc.recoFrame(cropIM,Z*Z_SCALE)
    rescaleRecoIM=cv2.resize(recoIM,None,fx=displayScale,fy=displayScale)
    rescaleFullIM=cv2.resize(grayIM,None,fx=1.0/FULL_SCALE,fy=1.0/FULL_SCALE)

    cv2.imshow('Crop Reconstructed',rescaleRecoIM)
    cv2.imshow('Full Image',rescaleFullIM)
    cv2.waitKey(1)

    if savePic==True:
        savePicture(recoIM,cropIM) # save reconstructed and cropped raw image
        savePic=False   # reset flag so it ony does once per mouse click
    return

################################ MAIN ##################################
clamp = lambda value, minv, maxv: max(min(value, maxv), minv)

#test to see if we can open the video, else quit the program
print('Opening video file:',vid)
cap=vc.openVid(vid)
goodVideo, frame = cap.read()
if 'mp4' not in vid: # can only process mp4 videos!
    goodVideo=0
    
if goodVideo:
    root = tk.Tk()
    v = tk.IntVar()
    v.set(2)  # set choice to "+1 Frame"

    root.title("Holographic Reconstruction")
    updateStatusDisplay()

    for val, txt in enumerate(names):
        r=int(1+val/4)
        c=int(val%4)
        tk.Radiobutton(root, text=txt,padx = 1, variable=v,width=BUTTON_WIDTH,command=doButton,indicatoron=0,value=val).grid(row=r,column=c)

    cap=vc.openVid(vid)
    processImage()
    cv2.setMouseCallback('Full Image',doMouse)
    MAX_FRAME=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print ("Total frames:",MAX_FRAME)

    root.mainloop()
    cap.release()
    cv2.destroyAllWindows()
    print ('Ending program, bye!')
else:
    print('Could not open video file:',vid)
    print('Either can not find file or it is not an mp4 video')
