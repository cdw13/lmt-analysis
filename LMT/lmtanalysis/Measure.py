# HEADER_ADDED_BY_GITHUB_COPILOT_2026-02-11
# Computation helpers for measures (distance, speed, durations).
#
# Inputs: varies; see module for specifics (often .sqlite or json)
# Outputs: in-memory objects, event tables, or files depending on callers
# Dependencies: standard library or project modules
# Example: Example: import Measure or run as script if __main__ present.
'''
Created on 13 sept. 2017

@author: Fab
'''
from lmtanalysis.Point import Point

oneFrame = 1
oneSecond = 30
oneMinute = 30*60
oneHour = 30*60*60
oneDay = 30*60*60*24
oneWeek = 30*60*60*24*7

'''time window at the end of an event to test overlap with another event'''
TIME_WINDOW_BEFORE_EVENT = 15*oneFrame

def second( second ):
    return second * oneSecond

def day( day ):
    return day* oneDay

def hour( hour ):
    return hour * oneHour