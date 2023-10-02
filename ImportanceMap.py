import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
import matplotlib.colors as clr
import signac

import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)
warnings.simplefilter(action = 'ignore', category = DeprecationWarning)

def ImportanceMap(job, splitStart, splitEnd, stdThreshold, meanThreshold, dataShapeX, dataShapeY):
    #Return point by point mean
    def MeanMap(X):
        return np.mean(X,0)
    
    #Takes the standard deviation of each point in the 30x10 area
    def VarianceMap(X):
        return np.std(X,0)

    with job:
        with job.data:
            destination = "ClassifiedPoints.jpg"

            #Get data from stores
            #Load State
            X = np.array(job.data['Dataset/State'], dtype = float) 

            #Slice up to reduce computation time
            X = X[splitStart:splitEnd,0,:]

            PointClass = np.zeros(dataShapeX*dataShapeY) #This is the temp array that will hold the respective value of each point's classification.
            Means = MeanMap(X)
            Stds = VarianceMap(X)

            tempIndex = 0
            for mean, std in zip(Means, Stds):

                #Classify
                if (mean >= meanThreshold):
                    if (std < stdThreshold):
                        PointClass[tempIndex] = 4 #Essential
                    else:
                        PointClass[tempIndex] = 3 #Sensitive
                else:
                    if (std < stdThreshold):
                        PointClass[tempIndex] = 1 #No Material
                    else:
                        PointClass[tempIndex] = 2 #Free-to-Design
                
                tempIndex += 1

            #Remove any residual open plots
            plt.close('all')
            
            #Now, plot the resulting points, and save the plot to the job folder
            colors = ['blue', 'aquamarine', 'tomato', 'red']
            cmap = clr.ListedColormap(colors)

            #ColormapPlot
            plt.imshow(np.reshape(PointClass, (dataShapeY, dataShapeX), order = 'F'), cmap=cmap)

            #Colorbar
            plt.colorbar(ticks=[1, 2, 3, 4])

            plt.savefig(destination)

            job.data.close()



    