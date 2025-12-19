# Demo

## STEP 1: Create a new Conda environment
In an Anaconda terminal, run `conda create -n "mousearm-test"` or any environment name.
Activate the environment with `conda activate mousearm-test`.

## STEP 2: Install opensim via conda
### Windows
In the Anaconda terminal, run `conda install opensim-org::opensim`.
### Linux
In the Anaconda terminal, run `conda install -c opensim-org opensim`.

## STEP 3: Clone this git repo and install the library
Run the following in the Anaconda terminal:
```
git clone https://github.com/Al-Borno-Lab/mousearm.git
cd mousearm
pip install uv
uv pip install .
```

## STEP 4: 
In a new anaconda terminal, cd to the parent directory of the cloned repo. Then, run:
```
cd mousearm/mousearm/Demo
python Demo.py
```

# Sample Usage

## STEP 4: Place your data folder anywhere with the following format (any number of reachsets)
```
Data/
├── reachset_1/
│   └── kinematics_1.csv
└── reachset_2/
    └── kinematics_2.csv
```
Then, in a separate anaconda terminal, cd into the parent directory of the Data folder.

In a new python file in the same folder as the Data folder, enter:
```
from mousearm.simulate import run_simulation
run_simulation("Data", nReachSets=2)
```
Then, run it using `python run ` from the parent directory of the Data folder.
