# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Example: 001_draw_anonymous_detection.py
#
# Detailed summary:
#   This example demonstrates how to load and visualize anonymous detections from
#   Live Mouse Tracker `.sqlite` experiments. "Anonymous detections" are the
#   mass-center detections recorded for each frame when animals are present but
#   not necessarily identified to a specific animal (useful for pooled/anonymous
#   density visualizations or when identity tracking is unreliable).
#
#   The script performs the following steps:
#   1. Prompts the user to select one or more `.sqlite` files using
#      `getFilesToProcess()` from `lmtanalysis.FileUtil`.
#   2. For each selected file it opens an sqlite connection and creates an
#      `AnimalPool` instance to load animal metadata (`loadAnimals()`).
#   3. Calls `animalPool.loadAnonymousDetection(start, end)` to load anonymous
#      detection points for the specified time window. By default the example
#      uses `start = 0` and `end = 10 * oneMinute` (first 10 minutes); adjust
#      `start`/`end` in the script to change the time window.
#   4. Aggregates the mass-center points into `xList`/`yList` and draws a
#      low-opacity scatter plot to visualize where animals were detected.
#   5. Calls `animalPool.plotTrajectory()` to show reconstructed trajectories
#      (if named/identified trajectories are available).
#
#   Intended use / notes:
#   - This is a non-destructive example that only reads from the database.
#   - Use the `start`/`end` variables and the `oneMinute` constant (from
#     `lmtanalysis.Measure`) to control the analysis window.
#   - The plotting parameters (`alpha`, `s`, axis limits) are chosen for a
#     general cage layout — adjust `ax.set_xlim()` / `ax.set_ylim()` to your
#     arena coordinates.
#
# Inputs: .sqlite tracking DB files selected via dialog
# Outputs: Matplotlib scatter plot of anonymous detections and optional
#          trajectory plots via `animalPool.plotTrajectory()`
# Dependencies: sqlite3, matplotlib, lmtanalysis.FileUtil, lmtanalysis.Animal,
#               lmtanalysis.Measure
#
# Callers:
#   - Standalone example run by users; not intended for import by other modules.
#
# Callees (functions/classes used):
#   - `getFilesToProcess()` from `lmtanalysis.FileUtil`
#   - `AnimalPool`, `loadAnimals()`, `loadAnonymousDetection()`,
#     `plotTrajectory()` from `lmtanalysis.Animal`
#   - `oneMinute` (time constant) from `lmtanalysis.Measure`
#
# Example: Run from repository root with PYTHONPATH set:
#   PYTHONPATH=/path/to/LMT python3 LMT/examples/001_draw_anonymous_detection.py
'''
Created on 18 dec. 2018

@author: Fab
'''

import sqlite3
import os
from datetime import datetime
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import oneHour, oneMinute
import matplotlib.pyplot as plt

if __name__ == '__main__':
    
    #ask the user for database to process
    files = getFilesToProcess()
    
    # Extract filename from the first file (without extension)
    first_filename = os.path.splitext(os.path.basename(files[0]))[0]
    
    # Get current date and time in format YYYY-MM-DD_HH-MM-SS
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create output filename with dynamic format
    output_filename = f"anonymous_detection_frames-{first_filename}-{now}.txt"
    
    # Make output file with dynamic name
    output_file = open(output_filename, "w")
    
    for file in files:
        
        print( file )
        
        # connect to database
        connection = sqlite3.connect( file )
        
        # create an animalPool, which basically contains your animals
        animalPool = AnimalPool()
         
        # load infos about the animals
        animalPool.loadAnimals( connection )
        
        start = 0
        end = 64*oneHour
        
        # load all detection (positions) of all animals for the first hour
        animalPool.loadAnonymousDetection( start = start, end = end )
        
        
        # get all points
        
        
        tList = []
        gapList = []

        for t in range( start, end ): #how does for index in range work? is the length of the range t?
            if t in animalPool.anonymousDetection:
                # make list of frames where anonymous detections are present
                tList.append(t)
                gapList.append(t)
                # check if t is sequential from the last entry, if not, then add to new list
                
                # if the last entry in the tList is more than 10000 frames (5.55m) before the current t, then add to gap list
                # if tList not empty, and teh entry before t added is not within the 10000 frames before t, and the entry 
                
                if len(tList)>1 and tList[-2]<= t-10000 : 
                    gapList.append(tList[-1])
              
                
        
    #print( "Frames with anonymous detections: " + str(tList) + "number of frames: " + str(len(tList)) )
    output_file.write("Frames with anonymous detections: " + str(tList) + "number of frames: " + str(len(tList)) + "\n")
    print("Gaps in anonymous detections: " + str(gapList) + "\n")
    output_file.write("Gaps in anonymous detections: " + str(gapList) + "\n")
    output_file.close()
    print(f"Output saved to: {output_filename}")
    
          

    
    