# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Example script demonstrating common analysis flows (uses FileUtil dialogs).
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs)
# Outputs: plots (matplotlib) and images
# Dependencies: sqlite3
# Example: Run as: python LMT/examples/002_draw_trajectory_filter_speed_1.py
'''
Created on 18 dec. 2018

@author: Fab
'''

import sqlite3
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import oneHour

if __name__ == '__main__':
    
    #ask the user for database to process
    files = getFilesToProcess()
    
    for file in files:
        
        # connect to database
        connection = sqlite3.connect( file )
        
        # create an animalPool, which basically contains your animals
        animalPool = AnimalPool()
        
        # load infos about the animals
        animalPool.loadAnimals( connection )
        
        # load all detection (positions) of all animals for the first 22 hours
        animalPool.loadDetection( start = 0, end = 22*oneHour )
        
        # filter detection by animalSpeed (speed is in centimeters per second)
        animalPool.filterDetectionByInstantSpeed( 0, 20 )
        
        # plot and show trajectory
        animalPool.plotTrajectory( title="Trajectories filtered by speed (max 2) \n" + file )

    
    