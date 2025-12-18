# STEP 1: Install OpenSim from SimTK
# STEP 2: Create a new Conda environment
In an Anaconda terminal, run `conda create -n "mousearm-test"`
# STEP 3: Install opensim
In the Anaconda terminal, run `conda install opensim-org::opensim`
# STEP 4: Clone this git repo and install the library
Run 
```
git clone https://github.com/Al-Borno-Lab/mousearm.git
cd mousearm
pip install uv
uv pip install .
```
# STEP 5: Place your data folder anywhere
# STEP 6: Run
In a new python file (replace Your Data with the name of your data folder), run:
```
from mousearm.simulate import run_simulation
run_simulation("Your Data", nReachSets=6)
```
