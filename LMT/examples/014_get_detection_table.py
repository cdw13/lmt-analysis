
'''
014_get_detection_table
created by Caroline Woodard, 2026-03-20'''

import sqlite3
import os
from datetime import datetime
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import oneHour

if __name__ == '__main__':
    
    #ask the user for database to process
    files = getFilesToProcess()

    if not files:
        print("No file selected. Exiting.")
        raise SystemExit(0)
    
    # Extract filename from the first file (without extension)
    first_filename = os.path.splitext(os.path.basename(files[0]))[0]
    
    # Get current date and time in format YYYY-MM-DD_HH-MM-SS
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create output filename with dynamic format
    output_filename = f"detection_table-{first_filename}-{now}.txt"
    
    # Make output file with dynamic name
    with open(output_filename, "w") as output_file:

        for file in files:

            print( file )

            # connect to database
            connection = sqlite3.connect( file )

            # create an animalPool, which basically contains your animals
            animalPool = AnimalPool()

            # load infos about the animals
            animalPool.loadAnimals( connection )

            # in frames, since time variables in LMT are in frames (30 frames per second)
            start = 0
            end = 22*oneHour # 22 hours in frames (30 frames per second)

            # load all detections (positions) of identified animals for the first hour
            animalPool.loadDetection( start = start, end = end )

            # get detection table for the first hour
            detection_table = animalPool.getDetectionTable()

            output_file.write("# file: {}\n".format(file))
            if detection_table.empty:
                output_file.write("No identified detections in selected time range.\n\n")
            else:
                detection_table.to_csv(output_file, sep="\t", index=False)
                output_file.write("\n")

            connection.close()
       
        
    
    
          

    
    