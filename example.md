# 2D Part
# STEP 1: Install Anaconda
Download the executable from [this link](https://www.anaconda.com/download) then follow the instructions there to install Anaconda.

# STEP 2: Install DeepLabCut
Go to [their website](https://deeplabcut.github.io/DeepLabCut/docs/installation.html) and follow the instructions to install DeepLabCut. When you are done, try running the command `python -m deeplabcut` to open up the deeplabcut GUI. You should see the following window pop up:
![deeplabcut intro page](/images/deeplabcut_intro.png)

# STEP 3: Analyze your video files
## Creating the Project
Now that you installed DeepLabCut, it's time to use it. Go ahead and click on the "Create New Project" button on the screen.

Fill in the "Project" and "Experimenter" sections, then enter the bodyparts to track in this exact order: paw, wrist, shoulder, elbow. Now, click on the "Browse for videos" button and select the folder that contains your raw .mp4 files that were recorded. Click "Open," then deselect all the files except for the videos you want to analyze. I recommend selecting "Copy videos to project folder" because it makes the process easier and avoids future errors. When you're done, the window should look something like the below image. You can go ahead and click the "Create" button to create the project now.
![deeplabcut project creation](/images/deeplabcut_project_creation.png)

## Extracting and Labeling Frames
Now click on the "Extract frames" tab at the top of the screen. Click "Select videos" and then select the video you want to label (only select one). You don't have to change any of the other settings if you don't want to, so now just press "Extract Frames" at the bottom right. This may take up to a couple minutes to run, depending on the size of the video and your processor's speed. When it is done, a friendly window will pop up telling you so.

For labeling, head over to the "Label frames" tab (the third tab from the left). Click the "Label frames" button on the screen that pops up and you will see this open in a separate window:
![deeplabcut labeling screen](/images/deeplabcut_labeling.png)

You can either use their tutorial or follow along here.

There are only a few important things you need to know for labeling frames:
1. Add labels: Located in the top left, there is a plus sign in a circle. Clicking this will switch you to adding labels mode, and wherever you click it will add a label.
2. Move labels: If you ever place a label wrong, or want to adjust it, clicking the cursor icon next to the add labels button will switch you to moving labelc mode. You can click and drag to adjust the labels as you wish.
3. Switching between frames: At the bottom there is a play bar like the ones on youtube videos. You can use the buttons on the left and right of this to move left and right by a frame, respectively.
4. Switching keypoints: At the bottom right, there is a dropdown menu with a bodypart name in it. This shows you which label the program is asking you to place next. You can click on this and select a different one from the dropdown menu if you wish.

It will ask you to label 20 frames by default (you can always change this later, and will likely want to for more complex models). Make sure to ctrl+s when you are done to save them before closing this window. 

## Training the Model
Deeplabcut uses pytorch and tensorflow to train a model that labels the rest of the points for you. Click on the "Create training dataset" tab (4th from the left) and click "Create Training Dataset." It should tell you pretty much immediately that it is done.

Now move to the "Train network" tab (5th from the left). These should already be some default training parameters filled in for you, so you can click "Train Network" at the bottom right to start training. This may take a while, depending on your computer. My computer with an RTX 3070 Ti took around 10-15 minutes to train the minimum 200 epochs. Note it is 10-100x faster running this on a GPU, as opposed to a CPU. When it is done, it will pop up telling you so.

## Creating the Labeled Video
Go to the next tab, the "Evaluate network" tab (6th tab). I recommend checking "Compare all bodyparts", which will open a window when it is done showing you the difference between your labeled points and what the system labeled them as. This is a good way to know if you need to add more labeled frames early on. Now click "Evaluate Network" in the bottom right, and it will not let you know when it is done, but it text will show up at the bottom of the screen.

Now, you can move on to the "Analyze videos" tab (7th tab). The video should already be selected, but if it is not, you can re-add it. 

:warning: **Make sure to check the "Save result(s) as csv" box**. Now you can click "Analyze Videos" and wait for it to complete. 

# 3D Part
Now, repeat the above process for both of the 2d camera views, then you can generate the 3d data, using the following code:
```
import deeplabcut
import matplotlib
config_path3d = '/home/nexus/Downloads/analyze_all_videos/DLC_3D_calibration/calibration-Susan-2022-09-01-3d/config.yaml' # edit this to your config path
# if creating a new 3D calibration 
# config_path3d = deeplabcut.create_new_project_3d('calibration','Susan',num_cameras=2)
# deeplabcut.calibrate_cameras(config_path3d, cbrow =5,cbcol =7,calibrate=False,alpha=0.9)
# deeplabcut.calibrate_cameras(config_path3d, cbrow =5,cbcol =7,calibrate=True,alpha=0.9)
# deeplabcut.check_undistortion(config_path3d, cbrow=5, cbcol=7)

video_path = '/home/nexus/Downloads/20230308/DLC_3D'

deeplabcut.triangulate(config_path3d,video_path,filterpredictions=True, videotype='mp4',save_as_csv =True)
```

# Analysis of Data
## STEP 1: Create a new Conda environment
In an Anaconda terminal, run `conda create -n "mousearm-test python=3.11 -y"` or any environment name.  
Activate the environment with `conda activate mousearm-test`.

## STEP 2: Install opensim via conda
**Windows/Linux**: `conda install -c opensim-org opensim`.  
**macOS (Apple Silicon)**: `CONDA_SUBDIR=osx-64 conda install -c opensim-org opensim`.

## STEP 3: Go to your Documents folder
**Windows**: `cd %USERPROFILE%\Documents`.
**Linux/macOS**: `cd ~/Documents`.

## STEP 4: Clone this git repo and install the library
Run the following in the Anaconda terminal:
```
# Using SSH:
git clone git@github.com:Al-Borno-Lab/mousearm.git

# OR using HTTPS:
git clone https://github.com/Al-Borno-Lab/mousearm.git

cd mousearm
pip install uv'

uv pip install -e .
```

## STEP 5: Place your data folder anywhere with the following format (any number of reachsets)
```
Data/
├── reachset_1/
│   └── kinematics_1.csv
└── reachset_2/
    └── kinematics_1.csv
```
Then, in a separate anaconda terminal, cd into the parent directory of the Data folder.

In a new python file in the same folder as the Data folder, enter:
```
from mousearm.simulate import run_simulation
run_simulation("Data", nReachSets=2) # Adjust nReachSets accordingly
```
Then, run it using `python run ` from the parent directory of the Data folder.

# Data Formatting
Process the motion capture data through [DeepLabCut](https://github.com/DeepLabCut/DeepLabCut). The output file will have more data than necessary, so delete everything except time, paw (x,y,z), wrist (x,y,z), shoulder (x,y,z), elbow (x,y,z). At the end, the csv file should look like the following:  
![Example input file](/images/image_2025-12-31_145620844.png)  

After formatting, the data folder should be formatted like this:
```
RawData/
└── reachsets/
    ├── reachset_1/
    │   └── kinematics_1.csv
    ├── reachset_2/
    │   └── kinematics_1.csv
    └── ...
```

# Output File Processing

The important output files are muscle_solution and the muscle_kinematics:
* muscle_solution shows the solution that the model found for the movement. These can be visualized in OpenSim to observe the movement and predicted muscle actuations. 
* muscle_kinematics shows the difference between the captured movement and the movement predicted by the model

These files can both be imported into a pandas dataframe for further analysis with the below python code. The directory should be structured like this:
```
RawData/
└── reachsets/
    ├── reachset_1/
    │   ├── muscle_solution_adjusted_kinematics_1.sto
    │   └── muscle_kinematics_adjusted_kinematics_1.csv
    ├── reachset_2/
    │   ├── muscle_solution_adjusted_kinematics_1.sto
    │   └── muscle_kinematics_adjusted_kinematics_1.csv
    └── ...
```
```
import pandas as pd
import glob
import numpy as np
base_dir = "../../RawData/reachsets/" # Adjust this path to yours
save_dir = "../../Data/" # Adjust this path to yours
mcolnames = ["time", "/jointset/shoulder/elv_angle/value", "/jointset/shoulder/extension_angle/value", "/jointset/shoulder/rotation_angle/value", "/jointset/humerus_ulna/elbow_flex/value", "/jointset/ulna_radius_pj/radius_rot/value", "/jointset/wrist/wrist_angle/value", "/jointset/shoulder/elv_angle/speed", "/jointset/shoulder/extension_angle/speed", "/jointset/shoulder/rotation_angle/speed", "/jointset/humerus_ulna/elbow_flex/speed", "/jointset/ulna_radius_pj/radius_rot/speed", "/jointset/wrist/wrist_angle/speed", "/forceset/Pectoralis_Clavicle_Head/activation", "/forceset/Biceps_Short_Head/activation", "/forceset/Biceps_Long_Head/activation", "/forceset/Deltoid_Medial/activation", "/forceset/Triceps_Lat_Head/activation", "/forceset/Triceps_Long_Head/activation", "/forceset/Brachialis_Proximal_Head/activation", "/forceset/Brachialis_Distal_Head/activation", "/forceset/Anconeus/activation", "/forceset/Deltoid_Posterior/activation", "/forceset/Anconeus_Short_Head/activation", "/forceset/Subscapularis_SuperiorHead/activation", "/forceset/Infraspinatus/activation", "/forceset/PronatorTeres/activation", "/forceset/FlexorCarpiRadialis/activation", "/forceset/Brachioradialis/activation", "/forceset/Triceps_Medial_Head/activation", "/forceset/Latissimus_Dorsi_Rostral/activation", "/forceset/Latissimus_Dorsi_Caudal/activation", "/forceset/Pectoralis_Major_Anterior/activation", "/forceset/Pectoralis_Major_Posterior/activation", "/forceset/Pectoralis_Clavicle_Head", "/forceset/Biceps_Short_Head", "/forceset/Biceps_Long_Head", "/forceset/Deltoid_Medial", "/forceset/Triceps_Lat_Head", "/forceset/Triceps_Long_Head", "/forceset/Brachialis_Proximal_Head", "/forceset/Brachialis_Distal_Head", "/forceset/Anconeus", "/forceset/Deltoid_Posterior", "/forceset/Anconeus_Short_Head", "/forceset/Subscapularis_SuperiorHead", "/forceset/Infraspinatus", "/forceset/PronatorTeres", "/forceset/FlexorCarpiRadialis", "/forceset/Brachioradialis", "/forceset/Triceps_Medial_Head", "/forceset/Latissimus_Dorsi_Rostral", "/forceset/Latissimus_Dorsi_Caudal", "/forceset/Pectoralis_Major_Anterior", "/forceset/Pectoralis_Major_Posterior"]
kcolnames = ["time","paw_x","paw_y","paw_z","elbow_x","elbow_y","elbow_z"]

def getMu(which_sets):
    mu = pd.DataFrame();
    for set in which_sets:
        for file in glob.glob(base_dir+"reachset_"+str(set)+"/muscle_sol*"):
            tdf = pd.read_csv(file, sep= r'\t',engine='python', header=18, names=mcolnames, index_col=None)
            mu = pd.concat([mu,tdf], ignore_index=True)
    return mu

def getKin(which_sets):
    kin = pd.DataFrame();
    for set in which_sets:
        for file in glob.glob(base_dir+"reachset_"+str(set)+"/muscle_kinematics_*"):
            tdf = pd.read_csv(file, sep= r',|\t',engine='python', header=4, names=kcolnames,index_col=None)
            kin = pd.concat([kin,tdf],  ignore_index=True)
    return kin
```
