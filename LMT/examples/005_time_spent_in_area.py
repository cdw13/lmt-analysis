# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Example: 005_time_spent_in_area.py
#
# Summary:
#   Compute and report the time each animal spends within a rectangular area
#   of the arena. The script:
#   - Prompts the user to select one or more `.sqlite` experiment files via
#     `getFilesToProcess()`.
#   - Loads animal metadata and detections into an `AnimalPool`.
#   - Loads detections for a short time window (default: first 10 minutes).
#   - Filters detections to a rectangular area (in centimeters, measured from
#     the top-left corner of the arena) using `filterDetectionByArea(x1,y1,x2,y2)`.
#   - For each animal, computes the number of frames detected inside that area
#     and converts frames → seconds (30 fps) to give time spent in area.
#   - Optionally plots filtered trajectories with `plotTrajectory()`.
#
# Inputs: .sqlite tracking DB files selected via dialog
# Outputs: Console lines reporting time spent in the area (seconds) and a
#          trajectory plot for the filtered detections
# Dependencies: sqlite3, matplotlib, lmtanalysis.FileUtil, lmtanalysis.Animal,
#               lmtanalysis.Measure
#
# Callers:
#   - Designed as a standalone example script for users; not typically imported.
#
# Callees (functions/classes used):
#   - `getFilesToProcess()` from `lmtanalysis.FileUtil` (file selection dialog)
#   - `AnimalPool`, `loadAnimals()`, `loadDetection()`, `filterDetectionByArea()`,
#     `getAnimalList()`, and `plotTrajectory()` from `lmtanalysis.Animal`
#   - time constants `oneMinute`, `oneHour` from `lmtanalysis.Measure`
#
# Usage notes:
#   - The area coordinates passed to `filterDetectionByArea(x1,y1,x2,y2)` are in
#     centimeters measured from the arena top-left; adjust them to match your
#     arena layout. The script assumes 30 frames per second when converting
#     frames to seconds.
#
'''
Created on 18 dec. 2018

@author: Fab
'''

import sqlite3
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import oneHour, oneMinute

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
        
        # load all detection (positions) of all animals for the first hour
        animalPool.loadDetection( start = 0, end = 60*oneMinute )
        
        # filter detection by area (in cm from the top left of the cage)
        animalPool.filterDetectionByArea( 0, 0, 50, 50 );
        
        # loop over all animals in this database
        for animal in animalPool.getAnimalList():
            
            # print RFID of animal
            print ( "Animal : " , animal.RFID )
            # number of frame in which the animal has been detected:
            numberOfFrame = len ( animal.detectionDictionary.keys() )
            # we have 30 frames per second
            timeInSecond = numberOfFrame / 30
            # print result
            print( "Time spent in area: (in second): " , timeInSecond )
            
        animalPool.plotTrajectory( title="Trajectories filtered by area" , scatter=True )
            
    
    