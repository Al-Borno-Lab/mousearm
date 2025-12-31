# Demo

## STEP 1: Create a new Conda environment
In an Anaconda terminal, run `conda create -n "mousearm-test python=3.11 -y"` or any environment name.  
Activate the environment with `conda activate mousearm-test`.

## STEP 2: Install opensim via conda
**Windows/Linux**: `conda install -c opensim-org opensim`.  
**macOS (Apple Silicon)**: `CONDA_SUBDIR=osx-64 conda install -c opensim-org opensim`.

## STEP 3: Clone this git repo and install the library
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
## STEP 4: Run the demo
In a new anaconda terminal, cd to the parent directory of the cloned repo. Then, run:
```
cd mousearm/mousearm/Demo
python demo.py
```

# Sample Usage

## STEP 4: Place your data folder anywhere with the following format (any number of reachsets)
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
run_simulation("Data", nReachSets=2)
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
* muscle_kinematics shows the difference between the real movement and the movement predicted by the model

These files can both be imported into a pandas dataframe for further analysis with the below python code. The directory should be structured like this:
```
RawData/
└── reachsets/
    ├── reachset_1/
    │   ├── muscle_sol*
    │   └── muscle_kinematics_*
    ├── reachset_2/
    │   ├── muscle_sol*
    │   └── muscle_kinematics_*
    └── ...
```
```
import pandas as pd
import glob
import numpy as np
base_dir = "../../RawData/reachsets/"
save_dir = "../../Data/"
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
