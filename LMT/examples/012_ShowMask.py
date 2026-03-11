# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Example script demonstrating common analysis flows (uses FileUtil dialogs).
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: sqlite3
# Example: Run as: python LMT/examples/012_ShowMask.py
'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3

from lmtanalysis.Animal import AnimalPool
from lmtanalysis.FileUtil import getFilesToProcess

def process( file ):

    print ("**********************")
    print(file)
    print ("**********************")
    connection = sqlite3.connect( file )        
        
    animalPool = AnimalPool( )
    animalPool.loadAnimals( connection )
    
    # show the mask of animals at frame 300
    animalPool.showMask( 300 )
          

if __name__ == '__main__':
    
    print("Code launched.")
     
    files = getFilesToProcess()
    
    for file in files:

        process( file )
        
    print( "*** ALL JOBS DONE ***")

            
        