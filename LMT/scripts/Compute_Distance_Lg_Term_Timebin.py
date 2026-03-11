# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: Compute_Distance_Lg_Term_Timebin.py.
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs)
# Outputs: plots (matplotlib) and images
# Dependencies: matplotlib, tkinter, sqlite3
# Example: Example: import Compute_Distance_Lg_Term_Timebin or run as script if __main__ present.
'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
import os
from tkinter.filedialog import askopenfilename
from lmtanalysis.Util import getMinTMaxTAndFileNameInput


if __name__ == '__main__':
    
    print("Code launched.")

    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    tmin, tmax, text_file = getMinTMaxTAndFileNameInput()

    '''
    min_dur = 0
    max_dur = 3*oneDay
    text_file = open ("btbr_3days_distance_per_time_bin.txt", "w")
    '''

    
    
    
    for file in files:

        print(file)
        connection = sqlite3.connect( file )
        
        #cursor = connection.cursor()

        pool = AnimalPool( )
        pool.loadAnimals( connection )

        pool.loadDetection( start = tmin, end = tmax, lightLoad=True)

        for animal in pool.animalDictionary.keys():
            
            print ( pool.animalDictionary[animal].RFID )

            dt = pool.animalDictionary[animal].getDistancePerBin(binFrameSize = 20*oneMinute, maxFrame = tmax )
            
            res = [file, pool.animalDictionary[animal].RFID, pool.animalDictionary[animal].genotype, pool.animalDictionary[animal].user1, *dt]
            
            text_file.write( "{}\n".format( res ) ) 
        
           
    
    text_file.write( "\n" )
    text_file.close()
        
    