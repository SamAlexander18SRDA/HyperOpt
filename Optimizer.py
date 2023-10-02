import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)
warnings.simplefilter(action = 'ignore', category = DeprecationWarning)

from flow import FlowProject
import flow
import os

#Renames our FlowProject to a better name (@class_name rather than @FlowProject for clarity)
class GvATools(FlowProject):
    pass

#Checks to see if the data h5 file is created.
@GvATools.label
def is_done(job):
    if (os.path.isfile(str(job.id)+'/signac_data.h5')):
        return 1
    else: 
        return 0

#Calls Top88Signac.m with the given job parameters and stores the data in the signac_data.h5 file
@GvATools.operation
@GvATools.post(is_done)
@flow.cmd #This will execute the following line on the command prompt (essentially running MATLAB code)
def compute(job):
    volfrac = job.sp.volfrac
    weight1 = job.sp.weight1
    weight2 = job.sp.weight2
    T = job.sp.T
    print('matlab -batch "Top88Signac(' + str(volfrac) + ',[' + str(weight1) + ' ' + str(weight2) + '],' + str(T) + ",'" + str(job.id) + "'" + '); exit"')
    return 'matlab -batch "Top88Signac(' + str(volfrac) + ',[' + str(weight1) + ' ' + str(weight2) + '],' + str(T) + ",'" + str(job.id) + "'" + '); exit"'

if __name__ == '__main__':
    GvATools().main() 