#This file will initialize the workspace folder with the jobs that I want to have
#In this case, lets do 5 jobs each for three temperatures. Additionally, each sub job will have a different volfrac

import signac
import numpy as np

#Filter out warnings
import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)
warnings.simplefilter(action = 'ignore', category = DeprecationWarning)

project = signac.init_project(name = "GvATools")

#Initalize Jobs Here
T = np.array([0, 0.01, 0.05, 0.1, 0.15])
volfrac = 0.6

for temp in T:
    sp = {"volfrac": volfrac, "T": temp, "weight1": 0, "weight2": 1}
    job = project.open_job(sp)
    job.init()