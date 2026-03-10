import opensim as osim
import os as os
import glob
import shutil

def runFiberReport(path_to_model, path_to_sto, storage_path):
    analyze = osim.AnalyzeTool()
    analyze.setName("analyze")
    analyze.setModelFilename(path_to_model)
    analyze.setStatesFileName(path_to_sto)
    analyze.updAnalysisSet().cloneAndAppend(osim.MuscleAnalysis())
    analyze.updControllerSet().cloneAndAppend(
    osim.PrescribedController(path_to_sto))
    analyze.printToXML(storage_path)
    analyze = osim.AnalyzeTool(storage_path)
    analyze.run()

rset_name = "reachset_1/" # change this accordingly
reach_dir= "C:\\Users\\matte\\Downloads\\MouseArmProject_v1_0\\analysis_and_processing_scripts\\sim scripts\\data\\Predicted EMG\\Test Reaches\\reachset_1" # change to your path
base_dir = "C:\\Users\\matte\\Downloads\\MouseArmProject_v1_0\\analysis_and_processing_scripts\\sim scripts\\data\\Predicted EMG\\Test Reaches\\" # change to your path
model_path = "C:\\Users\\matte\\Downloads\\MouseArmProject_v1_0\\model\\model_toScale.osim" # change to your path
for g2 in glob.glob(reach_dir+"//muscle_solution_*"):
    print(g2)
    gend = g2.split("_")
    gend = gend[-1]
    gend = gend.split(".")
    gend = gend[0]
    s2 = str(g2).replace(".sto",".xml").replace("muscle_solution","fiber_results")
    print(s2)
    runFiberReport(model_path, g2,s2) 

    for ana in glob.glob(base_dir+"*"): 
        if "analyze" in ana:
            ana2 = str(ana).replace("analyze_MuscleAnalysis_",rset_name).replace(".sto","_"+str(gend)+".sto").replace("\\","/")
            shutil.copy(ana, ana2)
            print(ana,ana2)