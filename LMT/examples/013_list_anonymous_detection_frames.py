
'''
Created on 2026-02-11 by Caroline Woodard
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
    output_filename1 = f"anonymous_detection_frames-{first_filename}-{now}.csv"
    
    # Make output file with dynamic name
    output_file1 = open(output_filename1, "w")

    
    for file in files:
        
        print( file )
        
        # connect to database
        connection = sqlite3.connect( file )
        
        # create an animalPool, which basically contains your animals
        animalPool = AnimalPool()
         
        # load info about the animals
        animalPool.loadAnimals( connection )
        
        start = 0
        end = 22*oneHour # 22 hours in frames (30 frames per second)
        
        # load all detection (positions) of all animals for the first hour
        animalPool.loadAnonymousDetection( start = start, end = end )
        
        
        # get all frames with anonymous detections and the number of detections per frame
        
        masterList = []

        for t in range( start, end ): #how does for index in range work? is the length of the range t?
           #t represents the frame number, so we are iterating through each frame from start to end
            if t in animalPool.anonymousDetection:
                #detectionList = []
                # make list of number of anonymous detections per frame
               masterList.append((t, len(animalPool.anonymousDetection[t])))
               # make list of frames where anonymous detections are present
                #masterList.append(detectionList)
              
                
        
    #print( "Frames with anonymous detections: " + str(masterList) + "number of frames: " + str(len(masterList)) )
    output_file1.write("Frame,Anonymous_Detections\n")
    for frame, count in masterList:
        output_file1.write(f"{frame},{count}\n")
    #print("number of detections per frame: " + str(detectionList) + "\n")
    output_file1.close()
    print(f"Output saved to: {output_filename1}")
    
          

    
    