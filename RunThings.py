#This file can be used to import routines and run them
import signac

import HyperOptPackage as Hyper
from Histogram import EvolutionHistogram

project = signac.get_project()

#Call to create a video!
#VideoCreator(project, 300, 100, 24, 70000, 89999, 100, 30, 10)

#Call to create Hazhir's new 4-point classification
#for job in project:
    #FourQuads(job, 70000,89999, 0.32, 0.5)

    #Call to Create a map of the above classifications.
    #ImportanceMap(job, 70000, 89999, 0.32, 0.5, 30, 10)
    #VideoEdit(job, 300,100,24,70000,89999,100,30,10)


EvolutionHistogram(project, 70000, 89999, 30, 10)