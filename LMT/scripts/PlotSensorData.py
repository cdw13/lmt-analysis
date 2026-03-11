# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: PlotSensorData.py.
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: sqlite3
# Example: Example: import PlotSensorData or run as script if __main__ present.
'''
Created on 22 nov. 2019

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *

def process( file ):

    print(file)
        
    connection = sqlite3.connect( file )
    
    # build sensor data
    animalPool = AnimalPool( )
    animalPool.loadAnimals( connection )
    animalPool.buildSensorData(file , show=True )