# User defined files
# V4 3.30.21
#
# Thomas Zimmerman IBM Research-Almaden, Center for Cellular Construction (https://ccc.ucsf.edu/) 
# This work is funded by the National Science Foundation (NSF) grant No. DBI-1548297 
# Disclaimer:  Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the National Science Foundation.

# files
VID_FILE_NAME=r'C:\Users\ThomasZimmerman\Videos\microscope\WhiteLightEdit\planktonWhite_960_544.mp4' # video you want to process
OBJECT_ARRAY_FILE_NAME='objectArrayTest.csv' # provide a file name where all the detection, tracking and features are stored

# Video processing
MAX_FRAME=0             # number of frames to process, if equal to zero, read all the frames of the movie
DEBUG=1                 # shows detection and tracking frame-by-frame (but slows down processing)
X_REZ_DEBUG=640; Y_REZ_DEBUG=480;  # debug display
THICK=3                 # ROI box line thickness

# Detector 
THRESH=100
BLUR=7
MIN_AREA=400
MAX_AREA=15000
ENLARGE=10              # increase ROI to include all of obj, also used to detect if near boarder or other objects in ROI window
MULTI_OBJECT_REJECT=0   # 1=reject obj with multiple objects in ROI
MIN_OBJ_LEN=100         # file must have at least this many objets else it is not processed

# tracker
MAX_MATCH_DISTANCE=100  # obj must be this close or better to track ID, couold be as low as 20 based on analysis
MAX_DELTA_AREA=0.2      # tracker won't match with object if caused large percent change in area

# speed
SPEED_WINDOW=10
MIN_SPEED=10            # objects slower than this are rejected

# Clustering
PCA_COMPONENTS=3        # how many PCA components
N_CLUSTERS=10            # how many K Means clusters

# feature 
MAX_FEATURES=68 # number of features getFeatures returns. Area is the first feature

# obj file header and index pointers
header='frame,trackID,cluster,clusterReject,class,classReject,x0,y0,x1,y1,xc,yc,trackDistance,deltaArea,speed,area,aspectRatio,texture,solidity,eMajor,eMinor,contourLen,perimeter,radius,mean,std'

# detection and feature column pointers
FRAME=0; TRACK_ID=1; CLUSTER=2; CLUSTER_STATUS=3; CLASS=4; CLASS_STATUS=5;
X0=6; Y0=7; X1=8; Y1=9; XC=10; YC=11; TRACK_DISTANCE=12; DELTA_AREA=13; SPEED=14; 
MAX_OBJECT_VECTOR=15

MAX_FEATURE_VECTOR=68           # number of features Feature function returns
FEATURE_START=MAX_OBJECT_VECTOR;
FS=FEATURE_START;               # FS is an abbreviation so I don't have to keep writing this big constant name
AREA=FS; ASPECT_RATIO=FS+1; TEXTURE=FS+2; SOLIDITY=FS+3; E_MAJOR=FS+4;
E_MINOR=FS+5; CONTOUR_LEN=FS+6; PERIMETER=FS+7; RADIUS=FS+8; MEAN=FS+9; STD=FS+10;
FEATURE_END=FS+MAX_FEATURE_VECTOR;
PCA_1=FEATURE_END+1; PCA_2=PCA_1+1; PCA_3=PCA_2+1; MAX_OBJ_COL=PCA_3+1 

# GRID CONSTRUCTION
PX=800 # pixels x axis(in pixels)
PY=500 # pixels y axis(in pixels)
#PX=1920 # pixels x axis(in pixels)
#PY=1080 # pixels y axis(in pixels)
GC=10    # grid col max (in cells)
GR=5	# grid row max (in cells)
MAX_IMAGE_IN_GRID=GC*GR
CW=PX/GC    #cell width	(in pixels/cell)
CH=PY/GR    # cell height (in pixels/cell

# GRID ARRAY
GRID_ARRAY_COL=2
GRID_OBJECT_INDEX=0; GRID_OBJECT_REJECT=1; # gridArray col labels
GRID_STATUS_UNPROCESSED=0; GRID_STATUS_PROCESSED=1; GRID_STATUS_REJECT=2; # grid image status
gridArrayHeader='OBJECT_INDEX,CLUSTER_ID,CLUSTER_REJECT'
