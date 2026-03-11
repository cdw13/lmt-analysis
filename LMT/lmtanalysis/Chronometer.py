# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: Chronometer.py.
#
# Inputs: varies; see module for specifics (often .sqlite or json)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: standard library or project modules
# Example: Example: import Chronometer or run as script if __main__ present.
'''
Created on 6 sept. 2017

@author: Fab
'''
from time import *

class Chronometer:
    '''
    classdocs
    '''


    def __init__(self, name):
        '''
        Constructor
        '''
        self.t = time()
        self.name= name
        
    def printTimeInS(self):
        print ( "[Chrono " , self.name , " ] " , self.getTimeInS() , " seconds")
        
    def printTimeInMS(self):
        print ( "[Chrono " , self.name , " ] " , self.getTimeInMS() , " milliseconds")
    
    def getTimeInS(self):
        return time()-self.t
        
    def getTimeInMS(self):
        return ( time()-self.t ) * 1000
        
        
        