#!/usr/bin/env python
"""This is the main simulation script. For ease of use, most of the 
heavy lifting is functionalized in the "helper_functions" script. 
So, look there for additional details. 

This requires access to "Test Reaches", a folder which holds N reachsets named "reachset_n" etc.
"""
__author__ = "Jesse Gilmer, Mazen Al Borno"
__email__ = "jesse.gilmer@cuanschutz.edu"
__status__ = "preprinted"

from . import helper_functions as helpers
import os
def run_simulation(folderNameSchema: str, nReachSets: int):
    """
    Args:
        folderNameSchema (str, required): Name of the folder.
        nReachSets (int, required): Number of reachset folders present.
    """
    for i in range(nReachSets): #python is 0-indexed
        reach_loc = os.path.join(folderNameSchema, f"reachset_{i+1}")
        helpers.generate_scaled_model(reach_loc)
        helpers.generate_scaled_kinematics_rigid(reach_loc)
        helpers.generate_initial_pose(reach_loc)
        helpers.generate_final_pose(reach_loc)
        helpers.synth_reach_torques(reach_loc)
        #helpers.synth_reach_inverse(reach_loc)
        helpers.synth_reach_mu(reach_loc)
    # After this, you'll have the synthetic kinematics and muscle excitations in the same folder as your initial emg and kinematics. This will take several hours to run.

if __name__ == "__main__":
    run_simulation()