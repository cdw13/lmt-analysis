# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Module: AnimalType.py.
#
# Inputs: varies; see module for specifics (often .sqlite or json)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: standard library or project modules
# Example: Example: import AnimalType or run as script if __main__ present.
'''
Created on 20 d�c. 2022

@author: Fab
'''

from enum import Enum

class AnimalType(Enum):
    MOUSE = 1
    RAT = 2
    
    