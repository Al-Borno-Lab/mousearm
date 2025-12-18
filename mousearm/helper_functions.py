#!/usr/bin/env python
"""
Helper functions that "main_script.py" uses for running simulations.
"""


# Imports:
import opensim as osim
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import sys
from numpy import genfromtxt
from scipy import interpolate
from scipy.signal import butter,filtfilt
import pandas as pd
import csv
import math as m

# Clipping indexes used for isolating ballistic phase:
dstart = 35
dend = 85

# Model and kinematic generation functions:
def generate_scaled_model(reach_dir):
    """
    Uses a known set of kinematics to scale "model_toScale.osim" to the data.
    Requires:
    a kinematics file, e.g. "kinematics_1.csv" below.
    the kinematics should include a paw, wrist, elbow and shoulder set of markers. I will work with you to make it work with a subset, if necessary.
    You also need Scale_Setup.xml.
    
    This generates "mouse_tracked.trc", which is the formal opensim requires for its scale tool. it will also generate a new model local to the kinematics.
    
    """
    trackingFolder = reach_dir

    trackingFile = "kinematics_1.csv"
    kinKey = ["paw","wrist","shoulder","elbow"]
    markerKey = ["handm","wristm","shoulderm","elbow"]

    inputData = genfromtxt(os.path.join(trackingFolder, trackingFile), delimiter=',')
    dataH = inputData.shape
    
    # write data to trc type file for use in osim
    saveFilename = "mouse_tracked.trc"
    
    
    headerString = "PathFileType\t4\t(X/Y/Z)\t" + saveFilename + "\n"
    
    nFrames = 20;
    lineStr1 = "DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n\t15.00\t15\t"+str(nFrames) +"\t4\tm\t15.00\t1\t"+str(dataH[0]) +"\n"
    lineStr2 = "Frame#\tTime\t"
    lineStr3 = ""
    ii = 1
    for i in markerKey:
        lineStr2 = lineStr2 + str(i) + "\t"
        lineStr3 = lineStr3 + "X" + str(ii) + "\tY" + str(ii) + "\tZ" + str(ii) + "\t"
        ii+=1
        
    lineStr2 = lineStr2 + "\n"
    lineStr3 = lineStr3 + "\n"
    lineStr4 = "\n";
    
    for file in glob.glob(os.path.join(trackingFolder, "kinematics*")):
        print(file)
        trackingFile = file
        kinKey = ["paw","wrist","shoulder","elbow"]
        markerKey = ["handm","wristm","shoulderm","elbow"]
    
        inputData = genfromtxt(trackingFile, delimiter=',')
        for i in range(10,10+nFrames):
            for j in range(dataH[1]):
                lineStr4 += str(inputData[i,j]) + "\t"
            lineStr4 += "\n"    
    
    tof = headerString + lineStr1 + lineStr2 + lineStr3 + lineStr4

    file_object = open(saveFilename, "w")
    file_object.write(tof)
    file_object.close()

    # now run sthe scaling tool on our model, which is dictated by the xml file here:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    setup_path = os.path.join(script_dir, 'Scale_Setup.xml')
    generic_model = os.path.join(script_dir, 'model_toScale.osim')
    marker_file = os.path.join(os.getcwd(), saveFilename)
    geom_dir = os.path.join(script_dir, 'GeomJan01242023')
    output_path = os.path.join(os.path.abspath(reach_dir), "scaled_mouse.osim")

    osim.ModelVisualizer.addDirToGeometrySearchPaths(geom_dir)

    ST = osim.ScaleTool(setup_path)
    ST.getGenericModelMaker().setModelFileName(generic_model)
    ST.getGenericModelMaker().setMarkerSetFileName(marker_file)
    ST.getModelScaler().setMarkerFileName(marker_file)
    ST.getModelScaler().setOutputModelFileName(output_path)
    
    ST.run()
    
def generate_scaled_kinematics_rigid(reach_dir):
    """
    This will enforce joint to joint scaling of kinematics using markers. This is necessary for tracking, as the model has rigid inter-joint distances.
    This produces an updated kinematics file.
    """
    
    # you need to run generate_scaled_model() before calling this.
    model = getTorqueDrivenModel(reach_dir+'/scaled_mouse.osim')
    state = model.initSystem()
    
    # get relevant markers in opensim model:
    handm = model.getMarkerSet().get("handm")
    elbowm = model.getMarkerSet().get("elbow")
    shoulderm = model.getMarkerSet().get("shoulderm")
    
    shoulder_loc = shoulderm.getLocationInGround(state)
    shx = shoulder_loc[0];
    shy = shoulder_loc[1];
    shz = shoulder_loc[2];
    
    hand_loc = handm.getLocationInGround(state)
    hx = hand_loc[0];
    hy = hand_loc[1];
    hz = hand_loc[2];
    
    elbow_loc = elbowm.getLocationInGround(state)
    elx = elbow_loc[0];
    ely = elbow_loc[1];
    elz = elbow_loc[2];

    sh_el_dist  = np.sqrt(np.square(shx-elx) + np.square(shy-ely) + np.square(shz-elz))
    el_paw_dist = np.sqrt(np.square(hx-elx) + np.square(hy-ely) + np.square(hz-elz))
    
    # itterate through kinematics and adjust kinematics
    for file in glob.glob(reach_dir+"/kinematics*"):
        DATA = genfromtxt(file, delimiter=',')    
        DATA2 = DATA.copy() 
        
        # For data use only, write the "start time" and "end time" determined by dstart, dend user defined indexes at top of file
        DXF = DATA[dstart,0]
        f = reach_dir+"/start_time_"+ os.path.basename(file);
        with open(f, 'w') as f2:
            f2.write(str(DXF))
            
        DXF = DATA[dend,0]
        f = reach_dir+"/end_time_"+ os.path.basename(file);
        #f = f.replace('.csv','.txt')
        with open(f, 'w') as f2:
            f2.write(str(DXF))    

        # clip data to pre-defined slice
        DATA = DATA[dstart:dend,:]
        
        print(DATA.shape[0])
        nan = np.nan
        for i in range(1,DATA.shape[1]):
            X = DATA[:,i]
            ok = ~np.isnan(X)
            xp = ok.ravel().nonzero()[0]
            fp = X[~np.isnan(X)]
            x  = np.isnan(X).ravel().nonzero()[0]
            
            X[np.isnan(X)] = np.interp(x, xp, fp)
            DATA[:,i] = X;

        model = getTorqueDrivenModel(reach_dir+'/scaled_mouse.osim')
        #model = getTorqueDrivenModel('scaled_mouse_gen.osim')

        state = model.initSystem()
        
        handm = model.getMarkerSet().get("handm")
        elbowm = model.getMarkerSet().get("elbow")
        shoulderm = model.getMarkerSet().get("shoulderm")
        
        shoulder_loc = shoulderm.getLocationInGround(state)
        print(shoulder_loc);
        
        shx = shoulder_loc[0];
        shy = shoulder_loc[1];
        shz = shoulder_loc[2];
        
        T = DATA[:,0]
        Tmin = np.nanmin(T)
        T = T - np.nanmin(T)
        
        # Filter requirements, change per your recording. This is from a 150hz camera.
        fs = 150.0       # sample rate, Hz
        cutoff = 10      # desired cutoff frequency of the filter, Hz
        nyq = 0.5 * fs
        order = 1
        
        # defs: 15 ^ 2
        
        def butter_lowpass_filter(data, cutoff, fs, order):
            normal_cutoff = cutoff / nyq
            # Get the filter coefficients 
            b, a = butter(order, normal_cutoff, btype='low', analog=False)
            y = filtfilt(b, a, data)
            return y
            
        for i in range(1,13):
            y = butter_lowpass_filter(DATA[:,i], cutoff, fs, order)
            DATA[:,i] = y

        shoulderst = DATA[:,7:10]
        dshx = -shx + shoulderst[:,0];
        dshy = -shy + shoulderst[:,1];
        dshz = -shz + shoulderst[:,2];

        for i in range(1,13,3):
            DATA[:,i] = DATA[:,i] - dshx[i]
        for i in range(2,13,3):
            DATA[:,i] = DATA[:,i] - dshy[i]
        for i in range(3,13,3):
            DATA[:,i] = DATA[:,i] - dshz[i]

        DATA[:,0] = DATA[:,0] - DATA[0,0]
        
        # Rectify elbow to paw length
        paw = DATA[:,1:4]
        elbow = DATA[:,10:13]
        shoulder = DATA[:,7:10]
        sed = []
        sedx =  []
        sedy =  []
        sedz =  []
        for i in range(len(paw)):
            xyz = [elbow[i,0]-shoulder[i,0],elbow[i,1]-shoulder[i,1],elbow[i,2]-shoulder[i,2]]
            angs = cart2sph(xyz[0],xyz[1],xyz[2])
            sedx.append(sh_el_dist * np.cos(angs[1]) * np.cos(angs[2]))
            sedy.append(sh_el_dist * np.cos(angs[1]) * np.sin(angs[2]))
            sedz.append(sh_el_dist * np.sin(angs[1]))
        sed  = np.array(sed )
        sedx = np.array(sedx)
        sedy = np.array(sedy)
        sedz = np.array(sedz)

        epd = []
        epdx =  []
        epdy =  []
        epdz =  []
        angs = []
        xyz = [];
        for i in range(len(paw)):
            xyz = [paw[i,0]-elbow[i,0],paw[i,1]-elbow[i,1],paw[i,2]-elbow[i,2]]
            angs = cart2sph(xyz[0],xyz[1],xyz[2]) #defined below
            epdx.append(el_paw_dist * np.cos(angs[1]) * np.cos(angs[2]))
            epdy.append(el_paw_dist * np.cos(angs[1]) * np.sin(angs[2]))
            epdz.append(el_paw_dist * np.sin(angs[1]))
        epd  = np.array(epd )
        epdx = np.array(epdx)
        epdy = np.array(epdy)
        epdz = np.array(epdz)
        
        DATA[:,10:13] = DATA[:,7:10] + np.array([sedx, sedy, sedz]).T    
        DATA[:,1:4] = DATA[:,10:13] + np.array([epdx, epdy, epdz]).T   

        DF = pd.DataFrame(DATA)

        # save the dataframe as a csv file
        DF.to_csv(reach_dir+"/adjusted_"+ os.path.basename(file),index=False,header=False)

def cart2sph(x,y,z):
    """ 
    Helper for getting 3d angles from cartesians.
    """
    XsqPlusYsq = x**2 + y**2
    r = m.sqrt(XsqPlusYsq + z**2)               # r
    elev = m.atan2(z,m.sqrt(XsqPlusYsq))     # theta
    az = m.atan2(y,x)                           # phi
    return r, elev, az


def generate_initial_pose(reach_dir):
    """
    Constraining the joint angles to their solved initial values is hugely helpful for accuracy in the "full" simulation, so I recommend performing this step. You can skip end pose if you want to.
    """
    
    # Itterate through the adjusted kinematic files that come from generate_scaled_kinematics_rigid(), then simulate them to get approximate starting joint angles.
    for file in glob.glob(reach_dir+"/adjusted_kinematics*"):
        # load kinematics data into a matrix
        DATA = genfromtxt(file, delimiter=',')    
        T = DATA[:,0]
        paw = DATA[:,1:4]
        elbow = DATA[:,10:13]
        
        # Optimize using the torque based model:
        model = getTorqueDrivenModel(reach_dir+'/scaled_mouse.osim')
        
        # Get the references for the hand and elbow marker:
        handm = model.getMarkerSet().get("handm")
        elbowm = model.getMarkerSet().get("elbow")
        
        # Setup the MoCo study:
        study = osim.MocoStudy()
        problem = study.updProblem()
        problem.setModel(model)
        finalTime = T[1]
        problem.setTimeBounds(0, finalTime)
        
        # Read in the limb trajectory:
        markerTrajectories = osim.TimeSeriesTableVec3()
        markerTrajectories.setColumnLabels(["/markerset/handm","/markerset/elbow"])
        ixm = 0
        step = 1
        for ix in range(15):
        #for ix in range(len(trajectoryData[:,0])):
            X2 = paw[0,0]
            Y2 = paw[0,1]
            Z2 = paw[0,2]
            T2 = T[ixm]
            m0 = osim.Vec3(X2,Y2,Z2)
            eX2 = elbow[0,0]
            eY2 = elbow[0,1]
            eZ2 = elbow[0,2]
            m1 = osim.Vec3(eX2,eY2,eZ2)
            markerTrajectories.appendRow(T2,
            osim.RowVectorVec3([m0, m1]))
            ixm = ixm + step
            
        # Assign a weight to each marker.
        markerWeights = osim.SetMarkerWeights()
        markerWeights.cloneAndAppend(osim.MarkerWeight("/markerset/handm", 2000))
        markerWeights.cloneAndAppend(osim.MarkerWeight("/markerset/elbow", 2000))
        
        ref = osim.MarkersReference(markerTrajectories, markerWeights)
        markerTracking = osim.MocoMarkerTrackingGoal()
        markerTracking.setMarkersReference(ref)
        
        problem.addGoal(markerTracking)      
        
        solver = study.initCasADiSolver()
        solver.set_num_mesh_intervals(1)
        solver.set_optim_convergence_tolerance(1e-10)
        solver.set_optim_constraint_tolerance( 1e-10)
        solver.set_optim_max_iterations(250)
        
        print(paw)
        predictSolution = study.solve()
        solutionUnsealed = predictSolution.unseal()
        a = solutionUnsealed.exportToValuesTable()
        a.trim(0,0.000001)
        
        osim.CSVFileAdapter().write(a,reach_dir+"/initpose_"+ os.path.basename(file))
        DATA = genfromtxt(reach_dir+"/initpose_"+ os.path.basename(file), delimiter=',',skip_header=5)   
        print(DATA)        
        DATA = DATA[1:]

        DF = pd.DataFrame(DATA)
        
        # save the dataframe as a csv file
        DF.to_csv(reach_dir+"/initpose_"+ os.path.basename(file),index=False,header=False)

def generate_final_pose(reach_dir):
    """
    This may or may not be a useful constraint for the full simulation.
    """
    for file in glob.glob(reach_dir+"/adjusted_kinematics*"):
        DATA = genfromtxt(file, delimiter=',')    
        T = DATA[:,0]
        paw = DATA[:,1:4]
        elbow = DATA[:,10:13]
        
        # First, optimize the torque bassed model:
        model = getTorqueDrivenModel(reach_dir+'/scaled_mouse.osim')
        #model = getTorqueDrivenModel('scaled_mouse_gen.osim')
        
        # Get the references for the hand and elbow marker:
        handm = model.getMarkerSet().get("handm")
        elbowm = model.getMarkerSet().get("elbow")
        
        # Setup the MoCo study:
        study = osim.MocoStudy()
        problem = study.updProblem()
        problem.setModel(model)
        finalTime = T[1]
        problem.setTimeBounds(0, finalTime)
        
        # Read in the limb trajectory:
        markerTrajectories = osim.TimeSeriesTableVec3()
        markerTrajectories.setColumnLabels(["/markerset/handm","/markerset/elbow"])
        ixm = 0
        step = 1
        for ix in range(15):
        #for ix in range(len(trajectoryData[:,0])):
            X2 = paw[-1,0]
            Y2 = paw[-1,1]
            Z2 = paw[-1,2]
            T2 = T[ixm]
            m0 = osim.Vec3(X2,Y2,Z2)
            eX2 = elbow[-1,0]
            eY2 = elbow[-1,1]
            eZ2 = elbow[-1,2]
            m1 = osim.Vec3(eX2,eY2,eZ2)
            markerTrajectories.appendRow(T2,
            osim.RowVectorVec3([m0, m1]))
            ixm = ixm + step
            
        # Assign a weight to each marker.
        markerWeights = osim.SetMarkerWeights()
        markerWeights.cloneAndAppend(osim.MarkerWeight("/markerset/handm", 1000))
        markerWeights.cloneAndAppend(osim.MarkerWeight("/markerset/elbow", 1000))
        
        ref = osim.MarkersReference(markerTrajectories, markerWeights)
        markerTracking = osim.MocoMarkerTrackingGoal()
        markerTracking.setMarkersReference(ref)
        
        problem.addGoal(markerTracking)      
        
        
        solver = study.initCasADiSolver()
        solver.set_num_mesh_intervals(1)
        solver.set_optim_convergence_tolerance(1e-10)
        solver.set_optim_constraint_tolerance( 1e-10)
        solver.set_optim_max_iterations(250)
        
        print(paw)
        predictSolution = study.solve()
        solutionUnsealed = predictSolution.unseal()
        a = solutionUnsealed.exportToValuesTable()
        a.trim(0,0.000001)
        
        osim.CSVFileAdapter().write(a,reach_dir+"/endpose_"+ os.path.basename(file))
        DATA = genfromtxt(reach_dir+"/endpose_"+ os.path.basename(file), delimiter=',',skip_header=5)   
        print(DATA)        
        DATA = DATA[1:]

        DF = pd.DataFrame(DATA)
        
        # save the dataframe as a csv file
        DF.to_csv(reach_dir+"/endpose_"+ os.path.basename(file),index=False,header=False)

def addCoordinateActuator(model, coordName, optForce):
    coordSet = model.updCoordinateSet()
    actu = osim.CoordinateActuator()
    actu.setName('tau_' + coordName)
    actu.setCoordinate(coordSet.get(coordName))
    actu.setOptimalForce(optForce)
    actu.setMinControl(-.5)
    actu.setMaxControl(.5)
    model.addComponent(actu)

def getTorqueDrivenModel(model_filename):
    """
    This loads the biophysical model, destroys the muscles, then adds coordiante actuators at every joint. 
    This is a useful tool for examining joint angles and torques alone, but obviously won't provide any information about muscle activation.
    """
    # Load the base model.
    model = osim.Model(model_filename)
    # Remove the muscles in the model.
    model.updForceSet().clearAndDestroy()
    model.initSystem()
    addCoordinateActuator(model, 'elv_angle', 15)
    addCoordinateActuator(model, 'extension_angle', 15)
    addCoordinateActuator(model, 'rotation_angle', 15)
    addCoordinateActuator(model, 'elbow_flex', 15)
    addCoordinateActuator(model, 'wrist_angle', 15)
    addCoordinateActuator(model, 'radius_rot', 15)
    return model

def synth_reach_torques(reach_dir):
    ii = 0
    for file in glob.glob(reach_dir+"/adjusted_kinematics*"):
        ii += 1
        DATA = genfromtxt(file, delimiter=',')    
        T = DATA[:,0]
        paw = DATA[:,1:4]
        elbow = DATA[:,10:13]
        
        # First, optimize the torque bassed model:
        model = getTorqueDrivenModel(reach_dir+'/scaled_mouse.osim')
        #model = getTorqueDrivenModel('scaled_mouse_gen.osim')
        # Get the references for the hand and elbow marker:
        handm = model.getMarkerSet().get("handm")
        elbowm = model.getMarkerSet().get("elbow")
        
        # Setup the MoCo study:
        study = osim.MocoStudy()
        problem = study.updProblem()
        problem.setModel(model)
        finalTime = T[-1]
        problem.setTimeBounds(0, finalTime)
        
        angles = genfromtxt(reach_dir+"/initpose_adjusted_kinematics_" + str(ii) + ".csv", delimiter=',')
        
        # Set the initial conditions and limits for the model:
        # Note that some of these are commented out. If you ever decide to have a working wrist, then consider constraining their starting conditions as well.
        problem.setStateInfo('/jointset/shoulder/elv_angle/value',        [],angles[0],[])
        problem.setStateInfo('/jointset/shoulder/extension_angle/value',  [],angles[1],[])
        problem.setStateInfo('/jointset/shoulder/rotation_angle/value',   [],angles[2],[])
        problem.setStateInfo('/jointset/humerus_ulna/elbow_flex/value',   [],angles[3],[])
        #problem.setStateInfo('/jointset/wrist/wrist_angle/value',         [],angles[4],[])
        #problem.setStateInfo('/jointset/ulna_radius_pj/radius_rot/value', [],angles[5],[])
        
        # Read in the limb trajectory:
        markerTrajectories = osim.TimeSeriesTableVec3()
        markerTrajectories.setColumnLabels(["/markerset/handm","/markerset/elbow"])
        ixm = 0
        step = 1
        for ix in range(int(np.floor(len(T)/step))):
            X2 = paw[ixm,0]
            Y2 = paw[ixm,1]
            Z2 = paw[ixm,2]
            T2 = T[ixm]
            m0 = osim.Vec3(X2,Y2,Z2)
            eX2 = elbow[ixm,0]
            eY2 = elbow[ixm,1]
            eZ2 = elbow[ixm,2]
            m1 = osim.Vec3(eX2,eY2,eZ2)
            markerTrajectories.appendRow(T2,
            osim.RowVectorVec3([m0, m1]))
            ixm = ixm + step
            
        # Assign a weight to each marker.
        markerWeights = osim.SetMarkerWeights()
        markerWeights.cloneAndAppend(osim.MarkerWeight("/markerset/handm", 2000))
        markerWeights.cloneAndAppend(osim.MarkerWeight("/markerset/elbow", 2000))
        
        ref = osim.MarkersReference(markerTrajectories, markerWeights)
        markerTracking = osim.MocoMarkerTrackingGoal()
        markerTracking.setMarkersReference(ref)
        
        problem.addGoal(markerTracking)      
        problem.addGoal(osim.MocoControlGoal('myeffort',1)) 
        
        solver = study.initCasADiSolver()
        solver.set_num_mesh_intervals(len(T))
        solver.set_optim_convergence_tolerance(1e-5)
        solver.set_optim_constraint_tolerance(1e-5)
        solver.set_optim_max_iterations(250)
        
        print(elbow)
        predictSolution = study.solve()
        solutionUnsealed = predictSolution.unseal()
        filename = reach_dir+"/torque_solution_"+ os.path.basename(file)
        filename = filename.replace('.csv','.sto')
        solutionUnsealed.write(filename)
        print(solutionUnsealed)
        states = predictSolution.exportToStatesTable()
        print_kin(reach_dir+"/torque_kinematics_"+ os.path.basename(file),model,states)
 
def print_kin(path,model,states):
    """
    This was better as an independent method. It just prints the kinematics that results from simulation to a file.
    """
    model.initSystem()
    statesTraj = osim.StatesTrajectory.createFromStatesTable(model, states)
    
    markerTrajectories = osim.TimeSeriesTableVec3()
    markerTrajectories.setColumnLabels(["/markerset/handm","/markerset/elbow"])
    
    for state in statesTraj:
        model.realizePosition(state)
        m0 = model.getComponent("markerset/handm")
        m1 = model.getComponent("markerset/elbow")
        markerTrajectories.appendRow(state.getTime(),
        osim.RowVectorVec3([m0.getLocationInGround(state), m1.getLocationInGround(state)]))
    osim.STOFileAdapterVec3.write(markerTrajectories,path)

def synth_reach_inverse(reach_dir):
    for file in glob.glob(reach_dir+"/adjusted_kinematics*"):
        filename = reach_dir+"/torque_solution_"+ os.path.basename(file)
        filename = filename.replace('.csv','.sto')
        tableProcessor = osim.TableProcessor(filename)
        
        #modelProcessor = osim.ModelProcessor(reach_dir+'/scaled_mouse.osim')
        modelProcessor = osim.ModelProcessor('scaled_mouse_gen.osim')

        modelProcessor.append(osim.ModOpIgnoreTendonCompliance())
        #modelProcessor.append(osim.ModOpIgnorePassiveFiberForcesDGF())
        
        modelProcessor.append(osim.ModOpAddReserves(.00001))
        
        inverse = osim.MocoInverse()
        inverse.setModel(modelProcessor)
        inverse.setKinematics(tableProcessor)
        
        inverse.set_initial_time(0)
        inverse.set_mesh_interval(.01)
        inverse.set_max_iterations(500)
        inverse.set_constraint_tolerance(1e-8)
        inverse.set_minimize_sum_squared_activations(True)
        inverse.set_kinematics_allow_extra_columns(True)
        
        inverseSolution = inverse.solve()
        solution = inverseSolution.getMocoSolution().unseal()
        inverseSolutionUnsealed = solution.unseal()
        inverse_filename = reach_dir+"/inverse_Solution_"+ os.path.basename(file)
        inverse_filename = inverse_filename.replace('.csv','.sto')
        inverseSolutionUnsealed.write(inverse_filename)
        
def synth_reach_mu(reach_dir):
    ii = 0;
    for file in glob.glob(reach_dir+"/adjusted_kinematics*"):

        ii += 1
        DATA = genfromtxt(file, delimiter=',')    
        T = DATA[:,0]
        paw = DATA[:,1:4]
        elbow = DATA[:,10:13]
        
        # First, optimize the torque bassed model:
        model = getMuscleDrivenModel(reach_dir+'/scaled_mouse.osim')
        #model = getMuscleDrivenModel('scaled_mouse_gen.osim')
        # Get the references for the hand and elbow marker:
        handm = model.getMarkerSet().get("handm")
        elbowm = model.getMarkerSet().get("elbow")
        
        # Setup the MoCo study:
        study = osim.MocoStudy()
        problem = study.updProblem()
        problem.setModel(model)
        finalTime = T[-1]
        problem.setTimeBounds(0, finalTime)
        
        angles = DATA = genfromtxt(reach_dir+"/initpose_adjusted_kinematics_" + str(ii) + ".csv", delimiter=',')
        endangles = DATA = genfromtxt(reach_dir+"/endpose_adjusted_kinematics_" + str(ii) + ".csv", delimiter=',')
        
        # Set the initial conditions and limits for the model:
        problem.setStateInfo('/jointset/shoulder/elv_angle/value',        [],angles[0],endangles[0])
        problem.setStateInfo('/jointset/shoulder/extension_angle/value',  [],angles[1],endangles[1])
        problem.setStateInfo('/jointset/shoulder/rotation_angle/value',   [],angles[2],endangles[2])
        problem.setStateInfo('/jointset/humerus_ulna/elbow_flex/value',   [],angles[3],endangles[3])
        #problem.setStateInfo('/jointset/wrist/wrist_angle/value',         [],[angles[4]-.1, angles[4]+.1])
        #problem.setStateInfo('/jointset/ulna_radius_pj/radius_rot/value', [],[angles[5]-.1, angles[5]+.1])
        #problem.setStateInfoPattern('/jointset/.*/speed', [], 0, 0)
        
        # Read in the limb trajectory:
        markerTrajectories = osim.TimeSeriesTableVec3()
        markerTrajectories.setColumnLabels(["/markerset/handm","/markerset/elbow"])
        ixm = 0
        step = 1
        for ix in range(int(np.floor(len(T)/step))):
            X2 = paw[ixm,0]
            Y2 = paw[ixm,1]
            Z2 = paw[ixm,2]
            T2 = T[ixm]
            m0 = osim.Vec3(X2,Y2,Z2)
            eX2 = elbow[ixm,0]
            eY2 = elbow[ixm,1]
            eZ2 = elbow[ixm,2]
            m1 = osim.Vec3(eX2,eY2,eZ2)
            markerTrajectories.appendRow(T2,
            osim.RowVectorVec3([m0, m1]))
            ixm = ixm + step
            
        # Assign a weight to each marker.
        markerWeights = osim.SetMarkerWeights()
        markerWeights.cloneAndAppend(osim.MarkerWeight("/markerset/handm", 1000000000))
        markerWeights.cloneAndAppend(osim.MarkerWeight("/markerset/elbow", 1000000000))
        
        ref = osim.MarkersReference(markerTrajectories, markerWeights)
        markerTracking = osim.MocoMarkerTrackingGoal()
        markerTracking.setMarkersReference(ref)
        
        problem.addGoal(markerTracking)   
        problem.addGoal(osim.MocoControlGoal('myeffort',1))         

        solver = study.initCasADiSolver()
        solver.set_num_mesh_intervals(len(T))
        solver.set_optim_convergence_tolerance(1e-7)
        solver.set_optim_constraint_tolerance(1e-7)
        solver.set_optim_max_iterations(2500)
        
        print(paw)
        predictSolution = study.solve()
        solutionUnsealed = predictSolution.unseal()
        filename = reach_dir+"/muscle_solution_"+ os.path.basename(file)
        filename = filename.replace('.csv','.sto')
        solutionUnsealed.write(filename)
        states = predictSolution.exportToStatesTable()
        print_kin(reach_dir+"/muscle_kinematics_"+ os.path.basename(file),model,states)

def getMuscleDrivenModel(model_filename):
    # Load the base model.
    model = osim.Model(model_filename)
    model.finalizeConnections()
    model = osim.Model(model_filename)
    model.finalizeConnections()
 
    # Replace the muscles in the model with muscles from DeGroote, Fregly,
    # et al. 2016, "Evaluation of Direct Collocation Optimal Control Problem
    # Formulations for Solving the Muscle Redundancy Problem". These muscles
    # have the same properties as the original muscles but their characteristic
    # curves are optimized for direct collocation (i.e. no discontinuities,
    # twice differentiable, etc).
    #osim.DeGrooteFregly2016Muscle().replaceMuscles(model)
 
    # Make problems easier to solve by strengthening the model and widening the
    # active force-length curve.
    
    for m in np.arange(model.getMuscles().getSize()):
        musc = model.updMuscles().get(int(m))
        musc.setMinControl(0.0)
        musc.set_ignore_activation_dynamics(False)
        musc.set_ignore_tendon_compliance(True)
        musc.set_max_isometric_force(musc.get_max_isometric_force() * 100) #important. Moco NEEDS these forces to be multiplied or it will fail to generate kinematics.
        dgf = osim.DeGrooteFregly2016Muscle.safeDownCast(musc)
        dgf.set_deactivation_time_constant(0.04)
        dgf.set_activation_time_constant(0.01)
        dgf.set_active_force_width_scale(1.5)
        dgf.set_tendon_compliance_dynamics_mode('implicit')
        dgf.set_ignore_passive_fiber_force(True)
 
    return model
    
def synth_reach_mu_corrected(reach_dir,jj, basename = None):
    ii = 0;
    for file in glob.glob(reach_dir+"/adjusted_kinematics_" + str(jj) + "*"):
        print("="*30)
        print("Correcting reach....")
        print(file)
        print("="*30)
        ii += 1
        DATA = genfromtxt(file, delimiter=',')    
        T = DATA[:,0]
        paw = DATA[:,1:4]
        elbow = DATA[:,10:13]
        
        # First, optimize the torque bassed model:
        model = getMuscleDrivenModel(reach_dir+'/scaled_mouse.osim')
        #model = getMuscleDrivenModel('scaled_mouse_gen.osim')
        # Get the references for the hand and elbow marker:
        handm = model.getMarkerSet().get("handm")
        elbowm = model.getMarkerSet().get("elbow")
        
        # Setup the MoCo study:
        study = osim.MocoStudy()
        problem = study.updProblem()
        problem.setModel(model)
        finalTime = T[-1]
        problem.setTimeBounds(0, finalTime)
        
        angles = DATA = genfromtxt(reach_dir+"/initpose_adjusted_kinematics_" + str(ii) + ".csv", delimiter=',')
        endangles = DATA = genfromtxt(reach_dir+"/endpose_adjusted_kinematics_" + str(ii) + ".csv", delimiter=',')
        
        # Set the initial conditions and limits for the model:
        problem.setStateInfo('/jointset/shoulder/elv_angle/value',        [],angles[0],endangles[0])
        problem.setStateInfo('/jointset/shoulder/extension_angle/value',  [],angles[1],endangles[1])
        problem.setStateInfo('/jointset/shoulder/rotation_angle/value',   [],angles[2],endangles[2])
        problem.setStateInfo('/jointset/humerus_ulna/elbow_flex/value',   [],angles[3],endangles[3])
        #problem.setStateInfo('/jointset/wrist/wrist_angle/value',         [],[angles[4]-.1, angles[4]+.1])
        #problem.setStateInfo('/jointset/ulna_radius_pj/radius_rot/value', [],[angles[5]-.1, angles[5]+.1])
        #problem.setStateInfoPattern('/jointset/.*/speed', [], 0, 0)
        
        # Read in the limb trajectory:
        markerTrajectories = osim.TimeSeriesTableVec3()
        markerTrajectories.setColumnLabels(["/markerset/handm","/markerset/elbow"])
        ixm = 0
        step = 1
        for ix in range(int(np.floor(len(T)/step))):
            X2 = paw[ixm,0]
            Y2 = paw[ixm,1]
            Z2 = paw[ixm,2]
            T2 = T[ixm]
            m0 = osim.Vec3(X2,Y2,Z2)
            eX2 = elbow[ixm,0]
            eY2 = elbow[ixm,1]
            eZ2 = elbow[ixm,2]
            m1 = osim.Vec3(eX2,eY2,eZ2)
            markerTrajectories.appendRow(T2,
            osim.RowVectorVec3([m0, m1]))
            ixm = ixm + step
            
        # Assign a weight to each marker.
        markerWeights = osim.SetMarkerWeights()
        markerWeights.cloneAndAppend(osim.MarkerWeight("/markerset/handm", 100000000000))
        markerWeights.cloneAndAppend(osim.MarkerWeight("/markerset/elbow", 100000000000))
        
        ref = osim.MarkersReference(markerTrajectories, markerWeights)
        markerTracking = osim.MocoMarkerTrackingGoal()
        markerTracking.setMarkersReference(ref)
        
        problem.addGoal(markerTracking)   
        problem.addGoal(osim.MocoControlGoal('myeffort',.1))         

        solver = study.initCasADiSolver()
        solver.set_num_mesh_intervals(len(T))
        solver.set_optim_convergence_tolerance(1e-6)
        solver.set_optim_constraint_tolerance(1e-6)
        solver.set_optim_max_iterations(150)
        if basename:
            solver.setGuessFile(reach_dir+basename)
        
        print(paw)
        predictSolution = study.solve()
        solutionUnsealed = predictSolution.unseal()
        filename = reach_dir+"/muscle_solution_"+ os.path.basename(file)
        filename = filename.replace('.csv','.sto')
        solutionUnsealed.write(filename)
        states = predictSolution.exportToStatesTable()
        print_kin(reach_dir+"/muscle_kinematics_"+ os.path.basename(file),model,states)