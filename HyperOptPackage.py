import matplotlib.pyplot as plt
import h5py as h5
import numpy as np
import os
import matplotlib.colors as clr
import cv2

import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)
warnings.simplefilter(action = 'ignore', category = DeprecationWarning)

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

#Define a point-by-point histogram for stage evolution --> Furthered into an entropy calculation as a function of temp
def EvolutionHistogram(project, sliceLeft, sliceRight, dimX, dimY):
    
    #A cheeky way to quickly check the amount of jobs in the workspace --> Need this to formulate a final numpy array
    k = 0

    for job in project:
        k += 1

    totalProbs = np.zeros((dimX*dimY, k*(sliceRight-sliceLeft)), dtype = float)

    for job in project:
        with job:
            with job.data:
                jobHisto = np.zeros((dimX*dimY, sliceRight-sliceLeft), dtype = float)

                X = np.array(job.data['Dataset/State'], dtype = float)

                #Slice the array
                X = X[sliceLeft:sliceRight,:,:]

                #Per Point
                for i in range(0,len(X[0,0,:])):
                    #Per State of each point
                    for j in range(0,len(X[:,0,0])):
                        jobHisto[i,j] = X[j,0,i]
                    
                     
                job.data.close()
           
            totalProbs = np.concatenate((totalProbs, jobHisto), axis = 1) #This array will contain all of the probability values for each job (point by point)

    #Ensure directory is created in the project folder
    #with project:  this doesnt work?
    try: 
        os.mkdir('histograms')
    except OSError:
        pass

    for i in range(dimX*dimY-1):
        #Histogram Plot Title
        HistoPath = 'histograms/' + str(i) + ".jpg"
        
        #Plot the Histogram
        probs = plt.hist(totalProbs[i,:], bins = 10, range = (0,1))
        probs = probs[0]/np.sum(probs[0])
        plt.xlabel("Density (0 -> 1)")
        plt.ylabel("Occurances")
        plt.xlim(0,1)
        plt.savefig(HistoPath)
        plt.close()

        entropy = 0

        #Calculate Entropy
        for prob in probs:
            if (prob == 0):
                entropy = entropy
            else:
                entropy -= prob*np.log(prob)
        

        EntropyPath = 'histograms/' + str(i) + '.txt'
        with open(EntropyPath, 'w') as f:
            f.write(str(entropy))

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

def VideoEdit(job, xResolution, yResolution, fps, startFrame, endFrame, skipFrame, dataDimX, dataDimY):
    #Now, in order to actually get the proper figure resoltion, we need to do some dpi and matplotlib gymnastics to go inches-->pixels
    px = 1/100 #Pixel density for default dpi = 100

    #Root Directory

    #Job Directory
    with job:
        #For each job, generate a video with the specified metadata
        with job.data: #file = h5.File(...)
            #VideoName = 'workspace/' + str(job.id) + '/Evolution.avi' #AVI
            VideoName = 'Evolution.avi' #AVI
            
            X = np.array(job.data['Dataset/State'], dtype = float) #Need this to be constant across all types of problems!

            #Slice to reduce time complexity
            X = X[startFrame:endFrame:skipFrame,:,:] #Again, specify this sort of storage in the README

            #NOTE: RESOLUTION IS EXTREMELY IMPORTANT FOR OPENCV, so we need to be careful in our specifications here
            fourcc = cv2.VideoWriter_fourcc(*'MJPG') #MJPG Codec
            video_writer = cv2.VideoWriter(VideoName, fourcc, fps, (xResolution, yResolution), False) #FIRST PLACE TO LOOK FOR CORRUPTED ISSUES

            for FrameNum in range(0, X.shape[0]):
                plt.figure(figsize = (xResolution*px, yResolution*px))
                plotFrame = np.reshape(X[FrameNum,:,:], (dataDimY, dataDimX), order = 'F') #Remember to specify FORTRAN sorting order in state data
                plt.pcolormesh(plotFrame, cmap = 'binary', shading = 'flat')
                plt.savefig('temp.png')
                plt.close()
                img = cv2.imread('temp.png', cv2.IMREAD_GRAYSCALE)
                video_writer.write(img)

            #Remove any trace of our temp.png file
            os.remove("temp.png")
            video_writer.release()