# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: Inter animal interaction matrix.py — simple matrix of pairwise events.
#
# Summary: Builds and prints a matrix counting occurrences of a chosen event
# between every ordered pair of animals in an experiment. Loads animals and
# event timelines from the sqlite DB and prints counts to stdout.
#
# Called by (representative callers):
# - Typically executed interactively or from examples/notebooks; referenced by
#   analysis scripts that inspect pairwise interactions (ad-hoc use via import or
#   direct execution). Not commonly imported by other modules in this repo.
#
# Calls / functions used within this file:
# - `AnimalPool.loadAnimals(conn)` and `pool.animalDictionary` from `lmtanalysis.Animal`
# - `EventTimeLine(connection, eventName, idA, idB)` and `getEventList()` from `lmtanalysis.Event`
# - `getAllEvents(file=...)` from `lmtanalysis.Util` to list available event names
# - Imports many `BuildEvent*` modules so they are available/registered for `getAllEvents` and related tooling
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs) selected via GUI dialog or passed to `process(files, eventName)`
# Outputs: printed matrix (stdout); no DB modifications performed
# Dependencies: lmtanalysis (Animal, Event, Util), sqlite3, matplotlib (imported but not essential), tkinter (for file dialog)
# Example: Run interactively: `python LMT/scripts/Inter\ animal\ interaction\ matrix.py` and choose an event when prompted
'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3
from lmtanalysis.Animal import *
import matplotlib.pyplot as plt
from lmtanalysis.Event import *
from lmtanalysis.Measure import *
from lmtanalysis.Util import getAllEvents
from lmtanalysis import BuildEventTrain3, BuildEventTrain4, BuildEventTrain2, BuildEventFollowZone, BuildEventRear5, BuildEventFloorSniffing,\
    BuildEventSocialApproach, BuildEventSocialEscape, BuildEventApproachContact,BuildEventOralOralContact,\
    BuildEventApproachRear, BuildEventGroup2, BuildEventGroup3, BuildEventGroup4, BuildEventOralGenitalContact, \
    BuildEventStop, BuildEventWaterPoint, \
    BuildEventMove, BuildEventGroup3MakeBreak, BuildEventGroup4MakeBreak,\
    BuildEventSideBySide, BuildEventSideBySideOpposite, BuildEventDetection,\
    BuildDataBaseIndex, BuildEventWallJump, BuildEventSAP,\
    BuildEventOralSideSequence

import lmtanalysis, sys
from tkinter.filedialog import askopenfilename


def process( files, eventName ):

    for file in files:

        print(file)
        connection = sqlite3.connect( file )

        pool = AnimalPool( )
        pool.loadAnimals( connection )

        event= {}

        for idAnimalA in pool.animalDictionary.keys():

            for idAnimalB in pool.animalDictionary.keys():

                event[idAnimalA, idAnimalB] = EventTimeLine( connection, eventName, idAnimalA, idAnimalB )



        for idAnimalA in pool.animalDictionary.keys():

            txt = str(idAnimalA) + ":" + str( pool.animalDictionary[idAnimalA]) + "\t"

            for idAnimalB in pool.animalDictionary.keys():

                txt += str( len( event[idAnimalA, idAnimalB].getEventList() ) ) + "\t"

            print( txt )


    print( "*** DONE ***")


if __name__ == '__main__':

    print("Code launched.")


    files = askopenfilename( title="Choose a set of file to process", multiple=1 )

    eventList = getAllEvents(file=files[0] )

    for i in range( 0 , len( eventList) ):
        print( "[" + str( i ) + "] :" + eventList[i] )

    while( True ):

        userInput = input ("Event to read (full name or number ) (enter to quit): ")

        if userInput=="":
            print("Exit :)")
            quit()

        if ( userInput.isdigit() ):
            eventName = eventList[ int( userInput )]
        else:
            eventName = userInput

        process( files, eventName )


