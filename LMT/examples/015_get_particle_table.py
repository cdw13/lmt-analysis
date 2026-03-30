
'''
015_get_particle_table
created by Caroline Woodard, 2026-03-20'''

import sqlite3
import os
from datetime import datetime
import pandas as pd
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import oneHour

if __name__ == '__main__':
    
    #ask the user for database to process
    files = getFilesToProcess()

    if isinstance(files, str):
        files = [files]
    elif files is not None:
        files = list(files)

    if not files:
        print("No file selected. Exiting.")
        raise SystemExit(0)
    
    # Extract filename from the first file (without extension)
    first_filename = os.path.splitext(os.path.basename(files[0]))[0]
    
    # Get current date and time in format YYYY-MM-DD_HH-MM-SS
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create output filename with dynamic format
    output_filename = f"particle_table-{first_filename}-{now}.txt"
    
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
            start = 3993900
            end = 3999518

            # load all detections (positions) of identified animals for the first hour
            animalPool.loadAnonymousDetection( start = start, end = end )

            # get particle table for the first hour
            particle_table = animalPool.getParticleDictionary(start, end)

            output_file.write("# file: {}\n".format(file))
            if len(particle_table) == 0:
                output_file.write("No particle data in selected time range.\n\n")
            else:
                particle_df = pd.DataFrame(
                    [(frame, nb_particle) for frame, nb_particle in sorted(particle_table.items())],
                    columns=["frame", "numparticle"]
                )
                particle_df.to_csv(output_file, sep="\t", index=False)
                output_file.write("\n")

            connection.close()
       
        
    print(f"Output saved to: {output_filename}")
    
          

    
    