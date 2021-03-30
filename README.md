# Holography
Images and Python code for holographic microscope. This repository is dedicated to our work on an inexpensive digital in-line holographic microscope made from a laser, image sensor and Raspberry Pi. Construction instructions can be found here in the youtube video, youtu.be/zqBVLydhUBg "Microscope Kit V3" (2020). This project is supported by the Center for Cellular Construction (ccc.ucsf.edu) and the National Science Foundation under Grant No. DBI-1548297. Disclaimer: Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.

# goldHolo.zip
64 cropped raw images of plankton and microfiber from dryer lint

# holoVideoReco
Interactive Holographic Reconstruction with Tkinter Interface
Mouse and button driven GUI to opens a video, view frame-by-frame, selecting area to crop and reconstruct

# vc3.py
Supporting functions for holoVideoReco program

# Detect_10.py
Main program to detect, track and extract morphological features of plankton. Requires Feature_12.py, Track_3.py, and Common_4.py.
To detect, track and extract features of plankton:
1. Edit Common_4.py for the video file you want to process, the file name to store detection, tracking and features, and operating parameters you desire.
2. Run Dect_10.py. It requires the files Feature_12.py, Track_3.py and Common_4.py.
