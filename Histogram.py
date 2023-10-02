import matplotlib.pyplot as plt
import numpy as np
import os

#Define a point-by-point histogram for stage evolution --> Furthered into an entropy calculation as a function of temp
def EvolutionHistogram(project, sliceLeft, sliceRight, dimX, dimY):
    
    #A cheeky way to quickly check the amount of jobs in the workspace --> Need this to formulate a final numpy array
    k = 0

    for job in project:
        k += 1

    totalProbs = np.zeros((dimX*dimY, k*(sliceRight-sliceLeft)), dtype = float)
    TempReform = []
    Temperatures = []

    for job in project:
        with job:
            with job.data:
                Temperatures.append(job.sp.T)
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
            TempReform.append(jobHisto) #used to categorize by temperature
            totalProbs = np.concatenate((totalProbs, jobHisto), axis = 1) #This array will contain all of the probability values for each job (point by point)

    #Now, we will calculate the entropy at each unique temperature, and then make a plot of S vs. T
    UniqueT = np.unique(Temperatures)
    pltTArray = []
    EntropyArray = []
    for tU in UniqueT:
        pltTArray.append(tU)
        idx = np.array(np.where(Temperatures == tU))
        
        finalIndex = np.zeros(len(idx))

        #Sneaky silent error here, np.where is returning a tuple which will tend to mess up alot of this analysis... fixing quick.
        for i in range (len(idx)):
            finalIndex[i] = idx[i]

        print(finalIndex)

        jobsCopy = TempReform[finalIndex]

        for i in range(dimX*dimY-1):
            probs = plt.hist(jobsCopy[i,:], bins = 10, range = (0,1))
            probs = probs[0]/np.sum(probs[0])
            plt.close()

            entropy = 0

            for prob in probs:
                if (prob == 0):
                    entropy = entropy
                else:
                    entropy -= prob*np.log(prob)
            
        EntropyArray.append((tU,entropy))
    
    print(EntropyArray)

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