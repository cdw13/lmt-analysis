'''
Created on 6 oct. 2025

@author: Fabrice de Chaumont

Link to lmt-analysis required
'''

import sqlite3
import argparse
from lmtanalysis.FileUtil import getFilesToProcess
from lmtanalysis.Animal import AnimalPool
from lmtanalysis.Measure import oneDay, oneHour
from lmtanalysis.Event import EventTimeLine, Event
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    from experiments.api.report.ReportTools import getAnimalReportColorMap
except ImportError:
    def getAnimalReportColorMap(rfidList):
        """Fallback color map when experiments package is unavailable."""
        colorPool = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
            "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
        ]
        return {rfid: colorPool[i % len(colorPool)] for i, rfid in enumerate(rfidList)}

try:
    from experiments.api.report.Report import Report
except ImportError:
    class Report:
        """Fallback report container when experiments package is unavailable."""

        def __init__(self, title, html, experimentName=None):
            self.title = title
            self.html = html
            self.experimentName = experimentName
            self.downloadableContent = {}

        def setDownloadableContent(self, name, content):
            self.downloadableContent[name] = content

import numpy as np
from abc import abstractmethod, ABC
import math
from test.test_colorsys import frange
from lmtanalysis.EventTimeLineCache import EventTimeLineCached

class LMTShape(ABC):
    
    @abstractmethod
    def isIn(self , x , y ) -> bool:
        pass
    
    @abstractmethod
    def drawFig(self , fig ):
        pass
    
    def createEvent(self , animalPool ): 
            
        for animal in animalPool.getAnimalList():
            # create event timeline for animal
            eventFrameDic = {}
            # for each detection of the animal, check if it is in the area and add it to the eventFrameDic
            for frame in animal.detectionDictionary:
                detection = animal.detectionDictionary[frame]
                if self.isIn( detection.massX, detection.massY ):
                    eventFrameDic[frame] = True
            timeLine = EventTimeLine( animalPool.conn, self.name, idA = animal.baseId, loadEvent=False )
            timeLine.reBuildWithDictionary( eventFrameDic )
            timeLine.endRebuildEventTimeLine( animalPool.conn, deleteExistingEvent=True )
        
    
class LMTRect(LMTShape):
    
    def __init__(self , name, x0,y0,x1,y1 ):
        self.name = name
        self.x0 = x0
        self.x1 = x1
        self.y0 = y0
        self.y1 = y1
        
    def isIn(self , x , y ):
        return ( x >= self.x0 and x <= self.x1 and y >= self.y0 and y<=self.y1 ) 
    
    def drawFig(self , fig ): 
        fig.add_shape(
            type="rect",
            xref="x", yref="y",
            x0=self.x0,y0=self.y0,
            x1=self.x1,y1=self.y1,
            line_width=2,
            #opacity=0.2,
            #fillcolor="red",
            line_color="black",
            label=dict(text= self.name ) )
        
class LMTCircle(LMTShape):
    
    def __init__(self , name, x,y,ray ):
        self.name = name                
        self.ray = ray
        self.centerX = x
        self.centerY = y
        self.x0 = x-ray
        self.x1 = x+ray
        self.y0 = y-ray
        self.y1 = y+ray
        print( self.ray )
        print( self.centerX )
        print( self.centerY )
        
        
    def isIn(self , x , y ):
        dist = math.sqrt( (self.centerX-x)**2 + (self.centerY-y)**2 )
        return ( dist <= self.ray ) 
    
    def drawFig(self , fig ): 
        fig.add_shape(
            type="circle",
            xref="x", yref="y",
            x0=self.x0,y0=self.y0,  # reversed for display
            x1=self.x1,y1=self.y1,  # reversed for display
            line_width=2,
            #opacity=0.2,
            #fillcolor="red",
            line_color="black",
            label=dict(text= self.name ) )

class StateMachine():
    """
    Gets event like animal local, which are mutually exclusive
    """
    def __init__(self , rfid ):
        self.rfid = rfid
        self.stateFrame = {} # key = frame, value = event name
        
    def addEventTimeLine(self , eventTimeLine ):
        
        for event in eventTimeLine.getEventList():
            
            self.stateFrame[event.startFrame] = eventTimeLine.eventName
            
        
            
    def getStateAtFrame(self, targetFrame ):
        '''
        returns the first state above the targetFrame 
        '''
        
          
        for frame in sorted( self.stateFrame.keys( ) ):
            
            print( frame, self.stateFrame[frame] )
            if targetFrame > frame:
                return self.stateFrame[frame]
             
        return None
    
    def getNbEvent( self, targetState, min, max ):
        '''
        returns the number of event of a state in min/max frame
        '''

        return len( self.getEventList( targetState, min, max ) )
        
    
    
    def getEventList(self , targetState, min , max ):
        
        '''
        16 Food
        40 House A
        156 Top right corner
        198 Top right corner
        235 Test entry
        370 Test entry
        376 Test entry
        425 House A
        522 House A
        615 House A
        644 House A
        662 House A
        683 House A
        733 House B
        '''
        
        eventList = []        
        start = None
        end = None
        
        for frame in sorted( self.stateFrame.keys( ) ):
            
            #print( frame, self.stateFrame[frame] )
            if frame < min or frame > max:
                continue
            
            state = self.stateFrame[frame]
            
            if state == targetState and start == None:
                start = frame                
                
            if state != targetState and start!=None:
                end = frame
                eventList.append( Event( start, end ) )
                
                start = None
                end = None
        
        print( f"{targetState} {min} {max} {len(eventList)}" )
        '''
        if "alone" in targetState.lower():
            print("quit") 
            quit()
        '''
            
        return eventList
        
            
    def getTotalDuration(self , targetState, min, max ):
        '''
        returns the total duration of an event. The last event of all state is not counted as it has infinite length
        '''
        
        eventList = self.getEventList( targetState, min, max )
        
        totalDuration = 0
        for event in eventList:
            totalDuration += event.duration()
        
        return totalDuration
    
        


class LMTAnalysisReportGeneric(object):
    
    '''
    Provides LMT data analysis for reports
    '''
    

    def __init__(self, sqliteFile , experimentName, animalDataCardManager ):
        
        
        #end = 1*oneHour
        loadEnd = 2*24*oneHour
        
        
        
        reComputeLMTEvents = False
        loadDetections = False
        showTrajectories= False
        
        
        '''
        reComputeLMTEvents = True
        loadDetections = True
        showTrajectories= False
        '''
        
        self.sqliteFile = sqliteFile
        self.animalDataCardManager = animalDataCardManager

        # Local geometric conversion fallbacks (cm <-> px) for repositories
        # where AnimalPool does not expose transform helpers.
        def transformCoordinateCmToPixel(x_cm, y_cm):
            return x_cm * 57.0 / 10.0, y_cm * 57.0 / 10.0

        def transformDistanceCmToPixel(dist_cm):
            return dist_cm * 57.0 / 10.0
                
        print( f"LMTAnalysisReportGeneric - Loading file: {self.sqliteFile}")
        
        self.reportList = []
        
        if not os.path.isfile( self.sqliteFile ):
            print("File does not exists. Quit.")
            quit()
            
        # connect to database
        connection = sqlite3.connect( self.sqliteFile )
        print( connection )
        
        # create an animalPool, which basically contains your animals
        animalPool = AnimalPool()
        
        # load infos about the animals
        animalPool.loadAnimals( connection )
        
        if loadDetections:
            animalPool.loadDetection( start = 0, end = loadEnd, lightLoad=True )
        
        animalDic = animalPool.getAnimalDictionary()
        
        #eventTimeLine = {}
        
        dataNbEvent = []
        dataDurationEvent = []
                
        shortEventList = ["Contact", "Oral-oral Contact", "Oral-genital Contact", "Side by side Contact",
                                 "Side by side Contact, opposite way", "Approach rear", "FollowZone Isolated", "Train2"]
        
        for eventName in shortEventList:
            for k,animal in animalDic.items():
                for j in [1]: #range(3):
                    #start = 24*j*60*60*30
                    #end = (24*j+24)*60*60*30
                    start = j*oneDay
                    end = (j+1)*oneDay
                    
                    rfid = animal.RFID
                    eventTimeLine = EventTimeLine( connection, eventName, idA = k , minFrame = start, maxFrame = end )
    
                    dataNbEvent.append( [ rfid , eventTimeLine.getNbEvent(), eventName ] )            
                    self.animalDataCardManager.setData( rfid, experimentName, f"{eventName} j{j} - nbEvent", eventTimeLine.getNbEvent() )
                    
                    dataDurationEvent.append( [ rfid , eventTimeLine.getTotalLength() / 30.0, eventName ] )
                    self.animalDataCardManager.setData( rfid, experimentName, f"{eventName} j{j} - total duration", eventTimeLine.getTotalLength() / 30.0 )
                    
        # render nbEvent 

        rfidList = [animal.RFID for animal in animalPool.getAnimalList()] 
        
        print( rfidList )
        
        
        cm = getAnimalReportColorMap( rfidList  )
        
        # --------------- number of events
        
        dfNbEvent = pd.DataFrame(dataNbEvent, columns=['rfid','value' ,"event"])
        
        fig = px.bar(dfNbEvent, x="event", y="value", color='rfid', barmode="group", color_discrete_map= cm )            
        html = fig.to_html(full_html=False, include_plotlyjs='cdn', config= {'displaylogo': False} )
        
        
        report = Report( "Number of events", html , experimentName=experimentName )
        report.setDownloadableContent("Xlsx number of event data", dfNbEvent)
        self.reportList.append( report )  

        # --------------- total duration of events
        
        dfDurationEvent = pd.DataFrame(dataDurationEvent, columns=['rfid','value' ,"event"])
        
        fig = px.bar(dfDurationEvent, x="event", y="value", color='rfid', barmode="group", color_discrete_map= cm )            
        html = fig.to_html(full_html=False, include_plotlyjs='cdn', config= {'displaylogo': False} )
        
        
        report = Report( "Total duration of events (in seconds)", html , experimentName=experimentName )
        #report.setDownloadableContent("Xlsx duration of event data", dfDurationEvent)
        self.reportList.append( report )
        
        # --------------- all trajectories and areas
        html=""
        dataAllTrajectory = []
        fig = go.Figure()
        
        areaNames = []
        
        if showTrajectories:
            for animal in animalPool.getAnimalList():
    
                print ("Compute trajectory of animal " + animal.name )
                xList, yList = self.getTrajectoryDataForPlotly( animal )
                
                for i in range( len ( xList ) ):
                    dataAllTrajectory.append( [ animal.RFID, xList[i], yList[i] ] )
            
            dfAllTrajectory = pd.DataFrame(dataAllTrajectory, columns=['rfid', 'x' ,'y'])        
            fig = px.line(dfAllTrajectory, x="x", y="y", color='rfid' )
        
                
        # create event in AREA
        x0,y0 = transformCoordinateCmToPixel( 41 , 41 )
        areaName = "Wheel"
        areaNames.append( areaName )
        circle = LMTCircle( areaName , x0, y0, transformDistanceCmToPixel( 8.5 ) )
        circle.drawFig( fig )
        if reComputeLMTEvents:
            circle.createEvent( animalPool )
                
        # create event in AREA
        x0,y0 = transformCoordinateCmToPixel( 0 , 0 )
        x1,y1 = transformCoordinateCmToPixel( 10 , 10 )
        areaName = "House A"
        areaNames.append( areaName )
        rect = LMTRect( areaName , x0, y0, x1, y1 )
        rect.drawFig( fig )
        if reComputeLMTEvents:
            rect.createEvent( animalPool )
                
        # create event in AREA
        x0,y0 = transformCoordinateCmToPixel( 0 , 40 )
        x1,y1 = transformCoordinateCmToPixel( 10 , 50 )
        areaName = "House B"
        areaNames.append( areaName )
        rect = LMTRect( areaName , x0, y0, x1, y1 )
        rect.drawFig( fig )
        if reComputeLMTEvents:
            rect.createEvent( animalPool )
        
        # create event in AREA
        x0,y0 = transformCoordinateCmToPixel( 40 , 20 )
        x1,y1 = transformCoordinateCmToPixel( 55 , 30 )
        areaName = "Test entry"
        areaNames.append( areaName )
        rect = LMTRect( areaName , x0, y0, x1, y1 )
        rect.drawFig( fig )
        if reComputeLMTEvents:
            rect.createEvent( animalPool )
        
        # create event in AREA
        x0,y0 = transformCoordinateCmToPixel( 40 , 0 )
        x1,y1 = transformCoordinateCmToPixel( 50 , 10 )
        areaName = "Top right corner"
        areaNames.append( areaName )
        rect = LMTRect( areaName , x0, y0, x1, y1 )
        rect.drawFig( fig )
        if reComputeLMTEvents:
            rect.createEvent( animalPool )

        # create event in AREA        
        x0,y0 = transformCoordinateCmToPixel( -10 , 10 )
        x1,y1 = transformCoordinateCmToPixel( 2 , 25 )
        areaName = "Food"
        areaNames.append( areaName )
        rect = LMTRect( areaName , x0, y0, x1, y1 )
        rect.drawFig( fig )
        if reComputeLMTEvents:
            rect.createEvent( animalPool )
        

        
        # find most isolated animal
        
        '''
        area = "House A"
        dicInHouseA = {}
        for animal in animalPool.getAnimalList():
            dicInHouseA[animal.RFID] = EventTimeLine( animalPool.conn, area, idA = animal.baseId )
        
        for animalAlone in animalPool.getAnimalList():
            
            # copy timeLine
            timeLine = EventTimeLine( animalPool.conn, "House 1 alone", idA = animalAlone.baseId, loadEvent = False )
            timeLine.reBuildWithDictionary( dicInHouseA[animalAlone.RFID].getDictionary() )
            
            for animal in animalPool.getAnimalList():
                if animal != animalAlone:
                    timeLine.removeEventOfTimeLine( dicInHouseA[animal.RFID] )
                    
            timeLine.endRebuildEventTimeLine( animalPool.conn, deleteExistingEvent=True )
        '''
        stateMachine = {}
        
        for animal in animalPool.getAnimalList():
            
            stateMachine[ animal.RFID ] = StateMachine( animal.RFID )
            
            for area in areaNames:
            
                e = EventTimeLine( animalPool.conn, area, idA = animal.baseId )
                stateMachine[ animal.RFID ].addEventTimeLine( e )
                
        '''
        for animal in animalPool.getAnimalList():
            for area in areaNames:
                nbEvent = stateMachine[ animal.RFID ].getNbEvent( area )                
                self.animalDataCardManager.setData( animal.RFID, experimentName, f"in {area} - nbEvent", nbEvent )
                
                eventTotalDuration = stateMachine[ animal.RFID ].getTotalDuration( area )
                self.animalDataCardManager.setData( animal.RFID, experimentName, f"in {area} - total duration", eventTotalDuration/(15*60*60) ) # to hours
        '''
                
        for animal in animalPool.getAnimalList():
            for area in areaNames:
                for j in [1]: #range(3):
                    #start = 24*j*60*60*30
                    #end = (24*j+24)*60*60*30
                    start = j*oneDay
                    end = (j+1)*oneDay
                    nbEvent = stateMachine[ animal.RFID ].getNbEvent( area , start , end )                
                    self.animalDataCardManager.setData( animal.RFID, experimentName, f"in {area} j{j}- nbEvent", nbEvent )
                    
                    eventTotalDuration = stateMachine[ animal.RFID ].getTotalDuration( area , start, end )
                    self.animalDataCardManager.setData( animal.RFID, experimentName, f"in {area} j{j} - total duration", eventTotalDuration/(15*60*60) ) # to hours
                    
                    
                    
            


                #self.animalDataCardManager.setData( animal.RFID, experimentName, f"in {area} - nbEvent", e.getNbEvent() )
                #self.animalDataCardManager.setData( animal.RFID, experimentName, f"in {area} - total duration", e.getTotalLength()/(60*60) )
        
        # animal alone in area
        # if reComputeLMTEvents: TODO: mettre ca en place
        for area in areaNames:
            
            for animalAlone in animalPool.getAnimalList():

                for j in [1]: #range(3):
                    #start = 24*j*60*60*30
                    #end = (24*j+24)*60*60*30
                    start = j*oneDay
                    end = (j+1)*oneDay

                    timeLineAlone = EventTimeLine( animalPool.conn, f"Alone in {area} j{j}", idA=animalAlone.baseId, loadEvent=False )
                    
                    events = stateMachine[ animalAlone.RFID ].getEventList( area, start, end ) 
                    
                    for event in events:                
                        timeLineAlone.addEvent( event, noCheck=True )
                    
                    for animal2 in animalPool.getAnimalList():
                        
                        if animalAlone == animal2:
                            continue
    
                        timeLine2 = EventTimeLine( animalPool.conn, "", loadEvent=False )
                        
                        events = stateMachine[ animal2.RFID ].getEventList( area, start, end )
                        for event in events:                
                            timeLine2.addEvent( event, noCheck=True )
                            
                        timeLineAlone.removeEventOfTimeLine( timeLine2 )
                        
                    self.animalDataCardManager.setData( animalAlone.RFID, experimentName, f"Alone in {area} j{j} - nbEvent", timeLineAlone.getNbEvent() )
                    self.animalDataCardManager.setData( animalAlone.RFID, experimentName, f"Alone in {area} j{j} - total duration", timeLineAlone.getTotalLength()/(60*60) ) 
                    
                    timeLineAlone.endRebuildEventTimeLine( animalPool.conn, deleteExistingEvent=True )
                
                    '''
                    nbEvent = stateMachine[ animal.RFID ].getNbEvent( area )                
                    self.animalDataCardManager.setData( animal.RFID, experimentName, f"in {area} - nbEvent", nbEvent )
                    
                    eventTotalDuration = stateMachine[ animal.RFID ].getTotalDuration( area )
                    self.animalDataCardManager.setData( animal.RFID, experimentName, f"in {area} - total duration", eventTotalDuration/(15*60*60) ) # to hours
                    '''
        
        


        
        '''
        for area in areaNames:
            for animal in animalPool.getAnimalList():
                for h in range(3):
                    start = 24*h*60*60*30
                    end = (24*h+24)*60*60*30
                    e = EventTimeLine( animalPool.conn, area, idA = animal.baseId, minFrame = start, maxFrame=end )
                    self.animalDataCardManager.setData( animal.RFID, experimentName, f"in {area} {h*24}h-{h*24+24}h - nbEvent", e.getNbEvent() )
                    self.animalDataCardManager.setData( animal.RFID, experimentName, f"in {area} {h*24}h-{h*24+24}h - total duration", e.getTotalLength()/(60*60) )
        '''
        
        fig.update_yaxes(autorange="reversed") # invert y axis to match image coordinates
        fig.update_layout(yaxis_scaleanchor="x") # force square rendering

        if showTrajectories:                
            html = fig.to_html(full_html=False, include_plotlyjs='cdn', config= {'displaylogo': False} )
            report = Report( "Trajectory of animals in housing area", html , experimentName=experimentName )
            self.reportList.append( report )
        
        # --------------- wheel trajectories
        html=""
        if showTrajectories:

            animalPool.filterDetectionByDistanceToPoint( 41, 41, 8.5 ); # wheel area
            
            dataWheelTrajectory = []
            
            for animal in animalPool.getAnimalList():
    
                print ("Compute trajectory of animal " + animal.name )
                xList, yList = self.getTrajectoryDataForPlotly( animal )
                
                for i in range( len ( xList ) ):
                    dataWheelTrajectory.append( [ animal.RFID, xList[i], yList[i] ] )

        
            dfWheelTrajectory = pd.DataFrame(dataWheelTrajectory, columns=['rfid', 'x' ,'y'])
            fig = px.line(dfWheelTrajectory, x="x", y="y", color='rfid' )
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(yaxis_scaleanchor="x")                
            
            html = fig.to_html(full_html=False, include_plotlyjs='cdn', config= {'displaylogo': False} )
                    
            report = Report( "Trajectory of animals in wheel area", html , experimentName=experimentName )
            report.setDownloadableContent("Xlsx trajectory wheel data", dfWheelTrajectory)
            self.reportList.append( report )
        
        html =""
        report = Report( "Total duration & nbEvent on wheel area", html , experimentName=experimentName )        
        self.reportList.append( report )        

        report = Report( "Total duration & nbEvent on wheel area in food area", html , experimentName=experimentName )        
        self.reportList.append( report )
        
        report = Report( "Total duration & nbEvent on wheel area in top-left house area", html , experimentName=experimentName )        
        self.reportList.append( report )

        report = Report( "Total duration & nbEvent on wheel area in bottom-left house area", html , experimentName=experimentName )        
        self.reportList.append( report )
        
        report = Report( "Total duration & nbEvent on wheel area in top-right corner", html , experimentName=experimentName )        
        self.reportList.append( report )

        report = Report( "Total duration & nbEvent on wheel area in test entrance area", html , experimentName=experimentName )        
        self.reportList.append( report )

        report = Report( "Total duration & nbEvent Isolated sleep", html , experimentName=experimentName )        
        self.reportList.append( report )

        report = Report( "Session ratio day night", html , experimentName=experimentName )        
        self.reportList.append( report )



        
    
    def getReportList(self):
        return self.reportList
    
    
    
    def getTrajectoryDataForPlotly( self , animal, maskingEventTimeLine=None ):

        xList = []
        yList = []
        
        keyList = sorted( animal.detectionDictionary.keys() )

        if maskingEventTimeLine!=None:
            keyList = maskingEventTimeLine.getDictionary()

        previousKey = 0
        

        for key in keyList:
            
            if previousKey+1 != key:
                xList.append( np.nan )
                yList.append( np.nan )    
                
            previousKey = key
            
            a = animal.detectionDictionary.get( key )
            xList.append( a.massX )
            yList.append( a.massY )
                        
        return xList, yList


class DummyAnimalDataCardManager:

    def __init__(self):
        self.data = {}

    def setData(self, rfid, experimentName, key, value):
        if (rfid, experimentName) not in self.data:
            self.data[(rfid, experimentName)] = {}
        self.data[(rfid, experimentName)][key] = value


def _to_safe_file_name(text):
    return ''.join(ch if (ch.isalnum() or ch in (' ', '-', '_')) else '_' for ch in text).strip().replace(' ', '_')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate HTML reports from an LMT sqlite file.')
    parser.add_argument('--sqlite', help='Path to input sqlite file')
    parser.add_argument('--experiment-name', default='lmt_experiment', help='Experiment name for report metadata')
    parser.add_argument('--out-dir', default='report_exports', help='Directory where report HTML files are saved')
    args = parser.parse_args()

    sqliteFile = args.sqlite
    if sqliteFile is None:
        files = getFilesToProcess()
        if files is None or len(files) == 0:
            print('No sqlite file selected. Quit.')
            quit()
        sqliteFile = files[0]

    outDir = Path(args.out_dir)
    if not outDir.is_absolute():
        outDir = (Path(__file__).resolve().parent / outDir).resolve()
    outDir.mkdir(parents=True, exist_ok=True)

    dataCardManager = DummyAnimalDataCardManager()
    lmtReport = LMTAnalysisReportGeneric(sqliteFile, args.experiment_name, dataCardManager)
    reportList = lmtReport.getReportList()

    for i, report in enumerate(reportList, start=1):
        title = getattr(report, 'title', 'report_{}'.format(i))
        html = getattr(report, 'html', '')
        safeName = _to_safe_file_name(title)
        outPath = outDir / '{:02d}_{}.html'.format(i, safeName)
        outPath.write_text(html if html is not None else '', encoding='utf-8')

    print('Generated {} report(s).'.format(len(reportList)))
    print('Output folder: {}'.format(outDir))
    
    
    
    
    
        
