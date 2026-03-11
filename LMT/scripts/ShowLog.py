# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: ShowLog.py.
# This simple Python script (ShowLog.py) displays the processing log 
# from Live Mouse Tracker (LMT) SQLite databases. It opens one or more 
# database files via a file dialog, connects to each, loads the TaskLogger 
# to read the Log table (tracking post-processing steps like event rebuilds), 
# and prints a list of all logged tasks/actions performed on the data.
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: tkinter, sqlite3
# Example: Example: import ShowLog or run as script if __main__ present.
'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3

from tkinter.filedialog import askopenfilename
from lmtanalysis.TaskLogger import TaskLogger

def process( file ):

    print ("**********************")
    print(file)
    print ("**********************")
    connection = sqlite3.connect( file )        
        
    t = TaskLogger( connection )
    t.listLog()
  

if __name__ == '__main__':
    
    print("Code launched.")
     
    files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    for file in files:

        process( file )
        
    print( "*** ALL JOBS DONE ***")
        
        