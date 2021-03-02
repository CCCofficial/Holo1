'''
Supporting functions for Holographic Reconstruction with Tkinter interface
Thomase Zimmerman, IBM Research-Almaden 

Holgraphic Reconstruction Algorithms by Nick Antipac, UC Berkeley and  Daniel Elnatan, UCSF
This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297, Center for Cellular Construction.
Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation. 

V3 03.01.21 removed unused background subtraction code
V2 03.01.21 added description of program
V1 09.24.19
'''
import cv2
import numpy as np

def openVid(vid):
    cap = cv2.VideoCapture(vid)
    return(cap)

def getFrame(cap,index):
    cap.set(1,index)
    ret, rawFrame = cap.read()
    return(ret,rawFrame)

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

def recoFrame(cropIM,z): 
    dxy   = 1.4e-6 # imager pixel (meters)
    wvlen = 650.0e-9 # wavelength of light is red, 650 nm
    res = propagate(np.sqrt(cropIM), wvlen, z, dxy)	 #calculate wavefront at z
    amp=np.abs(res)**2          # output is the complex field, still need to compute intensity via abs(res)**2
    ampInt=amp.astype('uint8')  
    return(ampInt)


