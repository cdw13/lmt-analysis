# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Example script demonstrating common analysis flows (uses FileUtil dialogs).
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: sqlite3
# Example: Run as: python LMT/examples/011_number_and_duration_event.py
'''
Created on 18 dec. 2018

@author: Fab
'''

import sqlite3
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import *
from lmtanalysis.Event import EventTimeLine

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
        animalPool.loadDetection( start = 0, end = oneHour )
        
        eventTimeLine = EventTimeLine( connection, "Oral-genital Contact", idA = 1 , idB = 2, minFrame = 0, maxFrame = oneHour )

        print ( "Event list for label ", eventTimeLine.eventNameWithId )
        print ( "for animal 1:", animalPool.getAnimalDictionary()[1].RFID )
        print ( "for animal 2:", animalPool.getAnimalDictionary()[2].RFID )
        print ( "Number of events:", len( eventTimeLine.getEventList() ) )
        
        print ( "start frame","end frame", "duration(in frame)")        
        for event in eventTimeLine.eventList:
            print( event.startFrame, event.endFrame, event.duration() )
        
            
            
        
            
    
    