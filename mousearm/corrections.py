#!/usr/bin/env python
"""This is the main simulation script. For ease of use, most of the 
heavy lifting is functionalized in the "helper_functions" script. 
So, look there for additional details. 

This requires access to "Test Reaches", a folder which holds N reachsets named "reachset_n" etc.
"""
__author__ = "Jesse Gilmer, Mazen Al Borno"
__email__ = "jesse.gilmer@cuanschutz.edu"
__status__ = "preprinted"

import helper_functions as helpers

basenames = ["/muscle_solution_adjusted_kinematics_5.sto", "/muscle_solution_adjusted_kinematics_4.sto", '/muscle_solution_adjusted_kinematics_8.sto', 
'/muscle_solution_adjusted_kinematics_8.sto', '/muscle_solution_adjusted_kinematics_6.sto','/muscle_solution_adjusted_kinematics_3.sto']

# user defined properties:
folderNameSchema = "Test Reaches/reachset_"
c =  [1, 2, 3, 3, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6]
tr = [1, 5, 2, 3, 5, 7, 9, 3, 6, 9, 3, 4, 9, 8]

c =  [1]
tr = [1]

for i in range(len(c)): #python is 0-indexed
    reach_loc = folderNameSchema + str(c[i])
    helpers.synth_reach_mu_corrected(reach_loc,tr[i],basename = basenames[c[i]-1])
