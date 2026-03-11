# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: Point.py.
#
# Inputs: varies; see module for specifics (often .sqlite or json)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: standard library or project modules
# Example: Example: import Point or run as script if __main__ present.
'''
Created on 6 sept. 2017

@author: Fab
'''

import math

class Point:
    '''
    classdocs
    '''


    __slots__ = ('x', 'y' )


    def __init__(self, x,y):
        self.x = x;
        self.y = y;
        
    def distanceTo(self , p ):
        return math.hypot( self.x-p.x , self.y-p.y )
        
        