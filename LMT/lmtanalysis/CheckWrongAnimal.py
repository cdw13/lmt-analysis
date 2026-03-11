# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: CheckWrongAnimal.py — utility to detect malformed/placeholder animals.
#
# Summary: Provides `check(connection, tmin=None, tmax=None)` which scans the
# database for animals with missing metadata (e.g., name==None) and logs the
# correction action in the DB `LOG` table. Intended to be run as part of
# rebuild/maintenance flows.
#
# Called by (representative callers):
# - LMT/scripts/Rebuild_All_Events.py (invokes `CheckWrongAnimal.check(...)`)
# - LMT/scripts/Rebuild_All_Exclusive_Contact_Events.py
# - Various maintenance/automation scripts under LMT/scripts (ManualNightInput.py,
#   AlterColBase.py, tools/RecoverFrame.py, sensor/plotSensorData.py, and notebooks
#   that run the full rebuild sequence)
#
# Calls / functions used within this file:
# - `AnimalPool.loadAnimals(conn)`, `AnimalPool.getNbAnimals()`, `AnimalPool.getAnimalList()`
#   (from `lmtanalysis.Animal`) to load and iterate animals
# - `TaskLogger( conn ).addLog(process, tmin, tmax)` to record actions into the
#   database `LOG` table (see `lmtanalysis/TaskLogger.py`)
# - Uses standard `sqlite3` connection object passed by callers
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs) provided as a
# SQLite `connection` argument by callers
# Outputs: logs an entry to the DB `LOG` table; prints findings to stdout
# Dependencies: lmtanalysis.Animal, lmtanalysis.TaskLogger, sqlite3, standard library
# Example: In a rebuild script: `CheckWrongAnimal.check(connection, tmin=currentMinT, tmax=currentMaxT)`
'''
Created on 6 sept. 2017

@author: Fab

In some record, we do have an extra animal with None for all parameters.
This script should be used to detect those animal in databases.

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
from lmtanalysis.TaskLogger import TaskLogger


def check( connection, tmin=None, tmax=None ): 
    
    pool = AnimalPool( )
    pool.loadAnimals( connection )

    '''
    get the number of expected animals
    '''
    
    nbAnimals = pool.getNbAnimals()
    print("nb animals: " , nbAnimals )
    for animal in pool.getAnimalList():
        if ( animal.name == None ):
            print( "!!!! None animal detected with lmtanalysis id: " , animal.baseId ) 
    
    # log process
    
    t = TaskLogger( connection )
    t.addLog( "Correct wrong animal" , tmin=tmin, tmax=tmax )

       
    print( "Rebuild event finished." )
        
    