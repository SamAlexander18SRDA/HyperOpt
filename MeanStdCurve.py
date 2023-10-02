import matplotlib.pyplot as plt
import h5py as h5
import numpy as np

def FourQuads(job, StartSlice, EndSlice, stdCutoff, meanCutoff):
    #For a set of jobs, try and find a plot of std vs. mean to illustrate the four kinds of sites.
    def MeanMapRedux(job, X):
        return np.mean(X,0)
    
    #Takes the standard deviation of each point in the 30x10 area and stores a figure of it in the job folder
    def VarianceMapRedux(job, X):
        return np.std(X,0)

    with job:
        with job.data:
            destination = "stdMean.jpg"
            #Load State
            X = np.array(job.data['Dataset/State'], dtype = float) #Don't think I need this?

            #Slice only 70000:90000 to improve runtime
            X = X[StartSlice:EndSlice,:,:]
            meanVals = MeanMapRedux(job, X)
            stdVals = VarianceMapRedux(job, X)

            #Some issues with a plot carrying over from another application? Just a good check here.
            plt.close('all')

            plt.scatter(meanVals, stdVals)
            plt.axhline(stdCutoff)
            plt.axvline(meanCutoff)
            plt.xlabel("Mean")
            plt.ylabel("Standard Deviation")
            plt.savefig(destination)

            job.data.close()
