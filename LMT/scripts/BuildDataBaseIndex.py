# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: BuildDataBaseIndex.py.
#
# Inputs: .sqlite tracking DB files (Live Mouse Tracker outputs)
# Outputs: in-database indices and optional console logs
# Dependencies: tkinter, sqlite3, lmtanalysis utilities
# Example: Example: import BuildDataBaseIndex or run as script if __main__ present.
#
# Summary:
# - Small script that shells into the `lmtanalysis.BuildDataBaseIndex.buildDataBaseIndex`
#   function to create or refresh database indices for one or more Live Mouse Tracker
#   sqlite files. When executed as `__main__` it queries files via `FileUtil.getFilesToProcess()`
#   and calls `buildDataBaseIndex(connection, force=True)` for each selected file.
#
# Callers (examples):
# - Typically executed directly by users from command line or by automation scripts that
#   invoke top-level scripts in `LMT/scripts/` (no repository files import this script as a module).
#
# Callees / internal dependencies called from this file:
# - lmtanalysis.BuildDataBaseIndex.buildDataBaseIndex (per-file index builder)
# - lmtanalysis.FileUtil.getFilesToProcess (file selection helper)
# - tkinter.filedialog.askopenfilename (optional file picker)
# - sqlite3 (DB connection)
#
# Notes:
# - This is a comments-only header update added by GitHub Copilot on 2026-02-11.
'''
Created on 13 sept. 2017

@author: Fab
'''

import sqlite3

from lmtanalysis.BuildDataBaseIndex import buildDataBaseIndex
from tkinter.filedialog import askopenfilename
from lmtanalysis.FileUtil import getFilesToProcess

if __name__ == '__main__':
    
    print("Code launched.")
    
    files = getFilesToProcess()
    #files = askopenfilename( title="Choose a set of file to process", multiple=1 )
    
    for file in files:
        connection = sqlite3.connect( file )
    
        buildDataBaseIndex( connection , force=True )
        


    
    