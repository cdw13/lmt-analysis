# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: CorrectDetectionIntegrity.py — repair detection identity integrity.
#
# Summary: Scans detection records in a `.sqlite` LMT DB between `tmin` and
# `tmax`. If not all animals are detected at a frame, this module marks those
# detections as anonymous (sets `ANIMALID` to NULL) to avoid false identities.
# This operation permanently alters the `DETECTION` table and should be used
# with caution (typically as part of maintenance/rebuild flows).
#
# Representative callers (who invoke / import this module):
# - `LMT/scripts/Rebuild_All_Events.py` (commented optional step)
# - `LMT/scripts/Rebuild_All_Exclusive_Contact_Events.py` (commented optional step)
# - `LMT/scripts/ManualNightInput.py`, `LMT/scripts/tools/RecoverFrame.py`,
#   `LMT/scripts/AlterColBase.py`, and `LMT/scripts/sensor/plotSensorData.py`
# - Notebooks that run the full rebuild sequence (e.g. `Rebuild all events.ipynb`)
#
# Functions / modules called from here (callees):
# - `lmtanalysis.Animal.AnimalPool`: `loadAnimals()`, `getAnimalDictionary()` to enumerate animals
# - `lmtanalysis.Detection.Detection` (module imported for constructing detection objects elsewhere)
# - `lmtanalysis.Measure` helpers (time constants)
# - `lmtanalysis.Event.EventTimeLine`: used to build `validDetectionTimeLine` and `reBuildWithDictionary`/`endRebuildEventTimeLine`
# - `lmtanalysis.Chronometer.Chronometer` for timing operations
# - `lmtanalysis.TaskLogger.TaskLogger.addLog(...)` to record the change in the DB `LOG` table
# - Standard `sqlite3` connection and SQL `UPDATE` statements (this module executes `UPDATE DETECTION SET ANIMALID=NULL WHERE FRAMENUMBER=...`)
#
# Inputs: SQLite `connection` over Live Mouse Tracker `.sqlite` DB; `tmin` and `tmax` frame range
# Outputs: mutates `DETECTION` rows (sets `ANIMALID` to NULL when integrity fails); writes a `LOG` entry
# Dependencies: lmtanalysis modules (Animal, Detection, Event, Chronometer, TaskLogger), sqlite3, standard library
# Example: In a rebuild script (commented):
#   `# CorrectDetectionIntegrity.correct(connection, tmin=0, tmax=maxT)`
'''

@author: Fab

In case of a nest, for instance, 2 animals can be seen as one detection. Which is wrong.
in that case only one animal is observed and this should not be considered in other labeling.

The purpose of this code is to remove those faulty situation by switching the identity of animals involved in such situation to anonymous.

This script should not be ran if there is occlusion in the scene. This script assumes all animals could be watched all the time.

WARNING: 
This script alters the lmtanalysis:
After running this script detection at t without all identity recognized will be all switched to anonymous !

'''
import sqlite3
from time import *

from lmtanalysis.Animal import *
from lmtanalysis.Detection import *
from lmtanalysis.Measure import *
import matplotlib.pyplot as plt
import numpy as np
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.Chronometer import Chronometer

def loadDetectionMap( connection, animal, start=None, end=None ):
    
        chrono = Chronometer("Correct detection integrity: Load detection map")
        print( "processing animal ID: {}".format( animal ))

        result = {}
        
        cursor = connection.cursor()
        query = "SELECT FRAMENUMBER FROM DETECTION WHERE ANIMALID={}".format( animal )

        if ( start != None ):
            query += " AND FRAMENUMBER>={}".format(start )
        if ( end != None ):
            query += " AND FRAMENUMBER<={}".format(end )
            
        print( query )
        cursor.execute( query )
        
        rows = cursor.fetchall()
        cursor.close()    
        
        for row in rows:
            frameNumber = row[0]
            result[frameNumber] = True;
        
        print ( " detections loaded in {} seconds.".format( chrono.getTimeInS( )) )
        
        return result


def correct( connection, tmin=None, tmax=None ): 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )
    #pool.loadDetection( start = tmin, end = tmax )
    
    '''
    get the number of expected animals
    if there is not all detections expected, switch all to anonymous
    '''
    
    validDetectionTimeLine = EventTimeLine( None, "IDs integrity ok" , None , None , None , None , loadEvent=False )
    validDetectionTimeLineDictionary = {}

    detectionTimeLine = {}
    for idAnimal in pool.getAnimalDictionary():
        detectionTimeLine[idAnimal] = loadDetectionMap( connection, idAnimal, tmin, tmax )

    for t in range ( tmin , tmax +1 ):
        
        valid = True
        for idAnimal in detectionTimeLine.keys():
            if not ( t in detectionTimeLine[idAnimal] ):
                valid = False
        if ( valid ):
            validDetectionTimeLineDictionary[t] = True
    
    '''
    rebuild detection set
    '''
    
    cursor = connection.cursor()
    for idAnimal in detectionTimeLine.keys():
        
        for t in range ( tmin , tmax +1 ):
            if ( t in detectionTimeLine[idAnimal] ):
                if not ( t in validDetectionTimeLineDictionary ):
            
                    query = "UPDATE `DETECTION` SET `ANIMALID`=NULL WHERE `FRAMENUMBER`='{}';".format( t )
                    #print ( query )
                    cursor.execute( query )
    
    connection.commit()
    cursor.close()
    validDetectionTimeLine.reBuildWithDictionary( validDetectionTimeLineDictionary )
    validDetectionTimeLine.endRebuildEventTimeLine(connection )
    
    
    # log process
    from lmtanalysis.TaskLogger import TaskLogger
    t = TaskLogger( connection )
    t.addLog( "Correct detection integrity" , tmin=tmin, tmax=tmax )

       
    print( "Rebuild event finished." )
        
    