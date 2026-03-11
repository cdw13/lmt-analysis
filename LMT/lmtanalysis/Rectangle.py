# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: Rectangle.py.
#
# Inputs: varies; see module for specifics (often .sqlite or json)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: standard library or project modules
# Example: Example: import Rectangle or run as script if __main__ present.
'''
Created on 6 sept. 2017

@author: Fab
'''

import math


class Rectangle:

    def __init__(self, pA , pB):
        self.pA = pA;
        self.pB = pB;
        
    def isPointInside(self , p ):
        
        if ( p.x >= self.pA.x and p.y >= self.pA.y and p.x <= self.pB.x and p.y <= self.pB.y ):
            return True
        return False
        
        
        