# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Event-builder module for ExclusiveUndetected.
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs)
# Outputs: events written to the `EVENT` table in the sqlite DB; console logs
# Dependencies: numpy, matplotlib, sqlite3, lmtanalysis.* helper modules
# Example: import BuildEventExclusiveUndetected or run as script if __main__ present.
#
# Callers (example files that import/use this module):
# - LMT/scripts/Rebuild_All_Exclusive_Contact_Events.py
# - (may also be invoked by higher-level rebuild scripts that orchestrate event builders)
#
# Callees / internal dependencies (functions/modules called from here):
# - lmtanalysis.Chronometer.Chronometer
# - lmtanalysis.Animal (AnimalPool, loadAnimals)
# - lmtanalysis.Detection (detection timeline utilities)
# - lmtanalysis.Measure (imported symbols)
# - lmtanalysis.Event (Event, EventTimeLine)
# - lmtanalysis.EventTimeLineCache.EventTimeLineCached (loads cached timelines)
# - lmtanalysis.BehaviouralSequencesUtil.exclusiveEventList (utility for exclusive events)
# - lmtanalysis.TaskLogger.TaskLogger (logging to DB)
#
# Notes:
# - This header was updated by GitHub Copilot on 2026-02-11 to list callers and callees.
# Summary:
# - Provides functions to (re)build the "Undetected exclusive" event timeline for each animal
#   in a recording. For each animal it loads the detection timeline (cached), computes frames
#   where the animal is not detected, reconstructs `Event` objects from those frames, and
#   saves the resulting timeline into the `EVENT` table (via `endRebuildEventTimeLine()`).
# - Also exposes `flush()` to delete previously stored "Undetected exclusive" events from the DB.
'''
Created on 6 sept. 2017

@author: Fab
'''
import sqlite3
from time import *
from lmtanalysis.Chronometer import Chronometer
from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.EventTimeLineCache import EventTimeLineCached
from lmtanalysis.BehaviouralSequencesUtil import exclusiveEventList
from lmtanalysis.TaskLogger import TaskLogger

def flush( connection ):
    ''' flush event in database '''
    eventUndetected = 'Undetected exclusive'
    deleteEventTimeLineInBase(connection, eventUndetected)

def reBuildEvent( connection, file, tmin=None, tmax=None , pool = None, animalType = None ):
    eventUndetected = 'Undetected exclusive'
    if ( pool == None ):
        pool = AnimalPool( )
        pool.loadAnimals( connection )

    ''' load the existing detection timeline for animal '''
    detectionTimeLine = {}
    dicoDetection = {}
    undetectedTimeLine = {}
    for animal in range(1, pool.getNbAnimals() + 1):
        detectionTimeLine[animal] = EventTimeLineCached( connection, file, 'Detection', animal, minFrame=tmin, maxFrame=tmax )
        dicoDetection[animal] = detectionTimeLine[animal].getDictionary(minFrame=tmin, maxFrame=tmax)
        undetectedTimeLine[animal] = EventTimeLine(None, eventUndetected, animal, loadEvent=False)

    '''select the frames where the animals are not detected'''
    undetectedDico = {}
    for animal in range(1, pool.getNbAnimals() + 1):
        undetectedDico[animal] = {}
        for t in range(tmin, tmax+1):
            if t not in dicoDetection[animal]:
                undetectedDico[animal][t] = True


    #####################################################
    #reduild all events based on dictionary
    for animal in range(1, pool.getNbAnimals() + 1):
        undetectedTimeLine[animal].reBuildWithDictionary(undetectedDico[animal])
        undetectedTimeLine[animal].endRebuildEventTimeLine(connection)

    # log process
    
    t = TaskLogger( connection )
    t.addLog( "Build Event Exclusive undetected events" , tmin=tmin, tmax=tmax )
                       
    print( "Rebuild event finished." )
        
    