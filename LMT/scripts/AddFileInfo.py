# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Script: AddFileInfo.py
#
# Summary:
#   Batch utility to update ANIMAL table fields in .sqlite tracking database files.
#   Reads multiple .sqlite files via dialog, and for each file updates GENOTYPE, AGE, SEX, 
#   STRAIN, and SETUP columns in the ANIMAL table to specified values.
#   Intended for preprocessing experiment metadata across multiple recordings.
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs) via file dialog
# Outputs: Modified .sqlite files (updates written to ANIMAL table)
# Dependencies: sqlite3, lmtanalysis.Event, lmtanalysis.FileUtil, lmtanalysis.Chronometer
#
# Callers (files/scripts that import or call this):
#   - None currently (designed as standalone script; not typically imported)
#
# Callees (functions/modules called within this file):
#   - getFilesToProcess() from lmtanalysis.FileUtil
#   - Chronometer() from lmtanalysis.Chronometer
#   - sqlite3.connect() for database operations
#
# Example: Run as script from command line with PYTHONPATH set:
#   PYTHONPATH=/path/to/LMT python3 AddFileInfo.py
'''
Created on 24 Septembre 2021

@author: Elodie
'''


from lmtanalysis.Event import *


from lmtanalysis.FileUtil import getFilesToProcess


def process( file ):

    print(file)
    #extract the name of the individual from the name of the file; adjust position!!!
    '''print('ind name: ', file[15:18])
    ind = str(file[15:18])'''
    '''print('ind name: ', file[89:92])
    ind = str(file[89:92])'''
    '''print('ind name: ', file[42:44])
    ind = str(file[42:44])'''

    connection = sqlite3.connect( file )
    
    c = connection.cursor()
    query = "UPDATE ANIMAL SET GENOTYPE = 'Del/+'";
    c.execute(query)
    query = "UPDATE ANIMAL SET AGE = '14we'";
    c.execute( query )
    query = "UPDATE ANIMAL SET SEX = 'female'";
    c.execute( query )
    query = "UPDATE ANIMAL SET STRAIN = 'B6C3B17p21.31'";
    c.execute( query )
    query = "UPDATE ANIMAL SET SETUP = '2'";
    c.execute(query)
    '''query = "UPDATE ANIMAL SET NAME = '189N3-{}'".format(ind);
    c.execute(query)
    query = "UPDATE ANIMAL SET RFID = '189N3-{}'".format(ind);
    c.execute(query)'''

    connection.commit()
    c.close()
    connection.close()

    

def processAll():
    
    
    files = getFilesToProcess()

    chronoFullBatch = Chronometer("Full batch" )    
        
    if ( files != None ):
    
        for file in files:
                print ( "Processing file" , file )
                process( file )
        
    chronoFullBatch.printTimeInS()
    print( "*** ALL JOBS DONE ***")

if __name__ == '__main__':
    
    print("Code launched.")
    processAll()
    