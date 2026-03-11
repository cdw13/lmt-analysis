# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Project parameters/constants (thresholds, sizes, speeds) for animals.
#
# Inputs: varies; see module for specifics (often .sqlite or json)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: standard library or project modules
# Example: Example: import Parameters or run as script if __main__ present.
'''
Created on 20 dec. 2022

@author: Fab
'''
from lmtanalysis.AnimalType import AnimalType
from lmtanalysis.ParametersMouse import ParametersMouse
from lmtanalysis.ParametersRat import ParametersRat

def getAnimalTypeParameters( animalType ):

    if animalType == AnimalType.MOUSE:
        return ParametersMouse()

    if animalType == AnimalType.RAT:
        return ParametersRat()

    print("Error: animal type is None")
    quit()
    


    return None