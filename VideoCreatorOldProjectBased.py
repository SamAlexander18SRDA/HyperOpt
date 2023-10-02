import matplotlib.pyplot as plt
import numpy as np
import h5py as h5
import cv2
import os
import signac

def VideoCreator(project, xResolution, yResolution, fps, startFrame, endFrame, skipFrame, dataDimX, dataDimY):
    #Now, in order to actually get the proper figure resoltion, we need to do some dpi and matplotlib gymnastics to go inches-->pixels
    px = 1/100 #Pixel density for default dpi = 100

    #For each job, generate a video with the specified metadata
    for job in project:
        VideoName = 'workspace/' + str(job.id) + '/Evolution.avi' #AVI
        path = "workspace/" + str(job.id) + "/signac_data.h5" #NEED TO UPDATE THIS TO ACTUALLY USE JOB.DATA() --> STILL HAVING SMALL ISSUES
        f = h5.File(path, 'r')
        X = f['Dataset/State'] #Need this to be constant across all types of problems!

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
            img = cv2.imread('temp.png', cv2.IMREAD_GRAYSCALE)
            video_writer.write(img)

        #Remove any trace of our temp.png file
        os.remove("temp.png")
        video_writer.release()

