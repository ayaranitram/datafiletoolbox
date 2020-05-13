# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 12:42:34 2020

@author: MCARAYA
"""

from common.inout import extension
from common.inout import verbose
from bases.units import convertUnit
from bases.units import unit
from bases.units import convertible as convertibleUnits
import random
import datafiletoolbox.dictionaries as dictionaries
import os.path
import os
import json
import ecl
# import sys
# import time
import numpy as np
import pandas as pd
import seaborn as sns
# import math
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import is_color_like
# import matplotlib.cbook as cbook
from datetime import timedelta
from datetime import datetime
from datafiletoolbox import date as strDate
import ecl.summary
import time
import fnmatch

class OverwrittingError(Exception):
    pass

def version():
    print('SimulationResults version 0.1')
    
def alternate(start=True):
    """
    returns +1 or -1 alternating between them.
    start = True will return +1 on first call
    """
    while start == True :
        yield 1
        yield -1
    while start == False :
        yield -1
        yield 1


#verbose(1,1,'\n  initializing most commong units conversions...')
verbose(0,0,convertibleUnits('SM3','MMstb',False))
verbose(0,0,convertibleUnits('SM3','Bscf',False))
verbose(0,0,convertibleUnits('SM3','Tscf',False))
verbose(0,0,convertibleUnits('STM3','MMstb',False))
verbose(0,0,convertibleUnits('KSTM3','MMstb',False))
verbose(0,0,convertibleUnits('KSM3','Bscf',False))
verbose(0,0,convertibleUnits('MSM3','Tscf',False))
verbose(0,0,convertibleUnits('SM3/DAY','Mstb/day',False))
verbose(0,0,convertibleUnits('SM3/DAY','stb/day',False))
verbose(0,0,convertibleUnits('SM3/DAY','MMscf/day',False))
verbose(0,0,convertibleUnits('SM3/DAY','Mscf/day',False))
verbose(0,0,convertibleUnits('STM3/DAY','Mstb/day',False))
verbose(0,0,convertibleUnits('STM3/DAY','stb/day',False))
verbose(0,0,convertibleUnits('KSM3/DAY','MMscf/day',False))
verbose(0,0,convertibleUnits('KSM3/DAY','Mscf/day',False))
verbose(0,0,convertibleUnits('STM3/DAY','SM3/DAY',False))
verbose(0,0,convertibleUnits('KSTM3/DAY','SM3/DAY',False))
verbose(0,0,convertibleUnits('KSM3/DAY','SM3/DAY',False))
verbose(0,0,convertibleUnits('STM3','SM3',False))
verbose(0,0,convertibleUnits('KSTM3','SM3',False))
verbose(0,0,convertibleUnits('KSM3','SM3',False))
verbose(0,0,convertibleUnits('MSM3','SM3',False))
verbose(0,0,convertibleUnits('KPA','BARSA',False))
verbose(0,0,convertibleUnits('BARSA','psia',False))
verbose(0,0,convertibleUnits('KPA','psia',False))
verbose(0,0,convertibleUnits('DATE','DATES',False))
verbose(0,0,convertibleUnits('DAY','DAYS',False))


timeout = 0.1


def Plot( SimResultObjects=[] , Y_Keys=[] ,  X_Key='TIME' , X_Units=[], Y_Units=[] , ObjectsColors=[] , SeriesColors=[] ,  graphName='' , Y_Axis=[], Y_Scales=[] , legendLocation='best', X_Scale=[] , Labels={} , linewidth=[] , DoNotRepeatColors=True , ColorBySimulation=None , ColorBySeries=None) :
    """
    uses matplot lib to create graphs of the selected vectors 
    for the selected SimResult objects.
    """
    
    # ensure SimResultObjects is not empty and is OK
    if len(SimResultObjects) == 0 :
        raise TypeError('<Plot> at least one SimResult object is required (first argument).')
    if not is_SimulationResult(SimResultObjects) and type(SimResultObjects) is not list and type(SimResultObjects) is not tuple :
        raise TypeError('<Plot> SimResultObjects must be a SimResult object or a list of SimResult objects.')
    if type(SimResultObjects) is not list :
        SimResultObjects = [SimResultObjects]
    if type(SimResultObjects) is tuple :
        SimResultObjects = list(SimResultObjects)
        
    CheckedList = []
    for each in range(len(SimResultObjects)) :
        if is_SimulationResult( SimResultObjects[each] ) :
            CheckedList.append( SimResultObjects[each] )
        else :
            if each == 0 :
                print( '<Plot> the 1st simulation object (python index 0 of list) is not a SimulationResult object.'  )
            elif each == 1 :
                print( '<Plot> the 2nd simulation object (python index 1 of list) is not a SimulationResult object.'  )
            else :
                print( '<Plot> the ' + str(each+1) + 'th simulation object (python index ' + str(each) + ' of list) is not a SimulationResult object.'  )
    SimResultObjects = CheckedList[:]
    CheckedList = None
    
    # ensure Y_Keys is not empty and is OK
    if type(Y_Keys) is str :
        Y_Keys = [Y_Keys]
    if type(Y_Keys) is tuple :
        Y_Keys = list(Y_Keys)
    if type(Y_Keys) is not list :
        raise TypeError('<Plot> Y_Keys must be a string, or a list of strings.')
    if len(Y_Keys) == 0 :
        raise TypeError('<Plot> at least one Key to plot is required (second argument).')
    
    # put X Key in a list, if not already a list
    if type(X_Key) is str :
        X_Key = [X_Key]
    if type(X_Key) is tuple :
        X_Key = list(X_Key)
    if type(X_Key) is not list :
        raise TypeError('<Plot> X_Key must be a string, or a list of strings.')
    # if more than 1 X key is received
    if len(X_Key) > 1 :
        if len(X_Key) == len(Y_Keys) :
            pass # it is OK, they are pairs of X & Y
        else :
            X_Key = X_Key[:1] # keep only the first one

    # put X Units in a list, if not already
    if type(X_Units) is str :
        X_Units = [ X_Units ]
    if type(X_Units) is tuple :
        X_Units = list(X_Units)
    if type(X_Units) is not list :
        raise TypeError('<Plot> X_Units must be a string, or a list of strings.')
    # if is an empty list, take the units from the X of the first object
    elif len(X_Units) == 0 :
        X_Units = [ SimResultObjects[0].get_plotUnit(X_Key[0]) ]    
    # if more than 1 X Units are in the list
    elif len(X_Units) > 1 :
        if len(X_Units) == len(X_Key) :
            pass # it is OK, one unit per key
        else :
            X_Units = X_Units[:1] # keep only the first one
    
    # put Y Units in a list, if not already
    if type(Y_Units) is str :
        Y_Units = [Y_Units]
    if type(Y_Units) is tuple :
        Y_Units = list(Y_Units)
    if type(Y_Units) is not list :
        raise TypeError('<Plot> Y_Units must be a string, or a list of strings.')
    if len(Y_Units) == 0 :
        Y_Units = [ SimResultObjects[0].get_plotUnit(Y_Keys[0]) ]
    if len(Y_Units) < len(Y_Keys) :
        for y in range( len(Y_Units) , len(Y_Keys) ) :
            Y_Units.append( SimResultObjects[0].get_plotUnit(Y_Keys[y]) )
        time.sleep(timeout)

    # check ObjectsColors is OK or empty
    if type(ObjectsColors) is str :
        ObjectsColors = [ObjectsColors]
    elif type(ObjectsColors) is tuple and len(ObjectsColors) == 3 and ( type(ObjectsColors[0]) is float or type(ObjectsColors[0]) is int ) and ( type(ObjectsColors[1]) is float or type(ObjectsColors[1]) is int ) and ( type(ObjectsColors[2]) is float or type(ObjectsColors[2]) is int ) :
        ObjectsColors = [ObjectsColors]
    elif type(ObjectsColors) is tuple :
        ObjectsColors = list(ObjectsColors)
    if type(ObjectsColors) is not list :
        raise TypeError('<Plot> ObjectsColors must be a matplotlib color string, a single RGB tuple, or a list of strings or RGB tuples.')
    
    # check SeriesColors is OK or empty
    if type(SeriesColors) is str :
        SeriesColors = [SeriesColors]
    elif type(SeriesColors) is tuple and len(SeriesColors) == 3 and ( type(SeriesColors[0]) is float or type(SeriesColors[0]) is int ) and ( type(SeriesColors[1]) is float or type(SeriesColors[1]) is int ) and ( type(SeriesColors[2]) is float or type(SeriesColors[2]) is int ) :
        SeriesColors = [SeriesColors]
    elif type(SeriesColors) is tuple :
        SeriesColors = list(SeriesColors)
    if type(SeriesColors) is not list :
        raise TypeError('<Plot> SeriesColors must be a matplotlib color string, a single RGB tuple, or a list of strings or RGB tuples.')

    # check optial parameters
    if ColorBySimulation is not None and type(ColorBySimulation) is not bool :
        print('<Plot>  ColorBySimulation must be None, True or False')
    if ColorBySeries is not None and type(ColorBySeries) is not bool :
        print('<Plot>  ColorBySeries must be None, True or False')
    if ColorBySimulation is None :
        if len(SimResultObjects) == 1 :
            ColorBySimulation = False
        elif len(SimResultObjects) < len(Y_Keys) :
            ColorBySimulation = False
        else :
            ColorBySimulation = True
    if ColorBySeries is None :
        if len(SimResultObjects) == 1 :
            ColorBySeries = True
        elif len(SimResultObjects) >= len(Y_Keys) :
            ColorBySeries = False
        else :
            ColorBySeries = True
        
            


    # define the figure name if not provided
    assert type(graphName) is str
    if len(graphName.split()) == 0 :
        graphName = str(Y_Keys) + ' vs ' + str(X_Key) + ' from ' + str(SimResultObjects) 
    
    # put Y_Axis in a list, if not already
    if type(Y_Axis) is str :
        try:
            Y_Axis = int(Y_Axis)
        except:
            raise TypeError('<Plot> Y_Axis must be integer')
    if type(Y_Axis) is int :
        Y_Axis = [Y_Axis]
    if type(Y_Axis) is tuple :
        Y_Axis = list(Y_Axis)
    if type(Y_Axis) is not list :
        raise TypeError('<Plot> Y_Units must be a string, or a list of strings.')
    if Y_Axis == [] :
        Y_Names = {}
        Y_Counter = 0
        Y_Axis = [0] * len(Y_Keys)
        for i in range( len(Y_Keys) ) :
            if Y_Keys[i].split(':')[0] in Y_Names :
                Y_Axis[i] = Y_Names[ Y_Keys[i].split(':')[0] ]
                verbose( SimResultObjects[0].get_Verbosity() , 1 , "<Plot> Axis for '" + Y_Keys[i] + "' is " + str(Y_Names[ Y_Keys[i].split(':')[0] ]))
            else :
                Y_Names[ Y_Keys[i].split(':')[0] ] = Y_Counter%2
                Y_Axis[i] = Y_Counter%2
                Y_Counter += 1
                verbose( SimResultObjects[0].get_Verbosity() , 1 , "<Plot> Axis for '" + Y_Keys[i] + "' is " + str(Y_Names[ Y_Keys[i].split(':')[0] ]))
            time.sleep(timeout)
    if len(Y_Axis) != len(Y_Keys) :
        print('<Plot> found ' + str(len(Y_Axis)) + ' Y_Axis but ' + str(len(Y_Keys)) + ' Y_Keys.',Y_Axis,Y_Keys) 
    
    # check Y_Scales is OK
    if Y_Scales == [] :
        Y_Scales = [None] * len(Y_Keys)
    assert len(Y_Scales) == len(Y_Keys)

    # locationDict = { 'best' : 0 ,
    # 'upper right' : 1 ,
    # 'upper left' : 2 ,
    # 'lower left' : 3 ,
    # 'lower right' : 4 ,
    # 'right' : 5 ,
    # 'center left' : 6 ,
    # 'center right' : 7 ,
    # 'lower center' : 8 ,
    # 'upper center' : 9 ,
    # 'center' : 10 }
     

    if len(X_Key) == 1 :
        # define the X label as the 1s X Key + its units
        Xlabel = X_Key[0] + ' [ ' + str(X_Units[0]) + ' ]'
    else :
        Xlabel = True 
        for each in X_Key :
            if X_Key[0].split(':')[0] not in each :
                Xlabel = False
                break
            time.sleep(timeout)
        if Xlabel :
            Xlabel = X_Key[0].split(':')[0] + ' [ ' + str(X_Units[0]) + ' ]'
        else :
            Xlabel = ', '.join(X_Key) +  ' [ ' + ', '.join(list(set(X_Units))) + ' ]'
            
    
    # check linewith parameter
    if type(linewidth) is int or type(linewidth) is float :
        linewidth = [linewidth] * len(Y_Keys)
    assert type(linewidth) is list 
    if len(linewidth) == 0 :
        linewidth = 2.0 / len( SimResultObjects )
        if linewidth < 0.25 :
            linewidth = 0.25
        linewidth = [linewidth] * len(Y_Keys)
        
    
    # set line colors and style:
    if len( SimResultObjects ) == 1 : # only one simulation object to plot
        NColors = len( SeriesColors )
        SeriesColors = SeriesColors + [None]*( len( Y_Keys ) - NColors )
        for c in range ( NColors , len( Y_Keys ) ) :
            if is_color_like( SimResultObjects[0].get_Color(Y_Keys[c]) ) : 
                SeriesColors[c] = SimResultObjects[0].get_Color(Y_Keys[c])
            elif 'BHP' in Y_Keys[c] :
                SeriesColors[c] = ('k')
            elif 'BP' in Y_Keys[c] :
                SeriesColors[c] = ('gray')
            elif 'QOIL' in Y_Keys[c] :
                SeriesColors[c] = ( (0,1,0) )
            elif 'OP' in Y_Keys[c] or 'OIL' in Y_Keys[c]:
                SeriesColors[c] = ('g')
            elif 'NGL' in Y_Keys[c] :
                SeriesColors[c] = ((1,1,0))
            elif 'LPG' in Y_Keys[c] :
                SeriesColors[c] = ('orange')
            elif 'GP' in Y_Keys[c] or 'GAS' in Y_Keys[c] :
                SeriesColors[c] = ('r')
            elif 'GI' in Y_Keys[c] :
                SeriesColors[c] = ('m')
            elif 'WP' in Y_Keys[c] :
                SeriesColors[c] = ('b')
            elif 'WI' in Y_Keys[c] :
                SeriesColors[c] = ('c')
            else :
                SeriesColors[c] = ( random.random() , random.random() , random.random() )
            # time.sleep(timeout)
        
        if DoNotRepeatColors : # repeated colors not-allowrd
            for c in range ( NColors , len( SeriesColors ) ) :
                while SeriesColors.count(SeriesColors[c]) > 1 :
                    SeriesColors[c] = ( random.random() , random.random() , random.random() )

        else : # repeated colors allowed
            Clean = list(set(SeriesColors))
            CleanCount = []
            CleanSorted = {}
            for each in Clean :
                CleanSorted[each] = SeriesColors.count(each)
                CleanCount.append( SeriesColors.count(each) )
            CleanCount.sort()
            New_Y_Keys = [None]*sum(CleanCount)
            New_Y_Colors = [None]*sum(CleanCount)
            NY = 0
            # sort the colors by number of repetition
            SortedColors = [None]*len(CleanSorted)
            for CC in CleanCount[::-1] :
                for color in CleanSorted :
                    if CleanSorted[color] == CC and color not in SortedColors :
                        SortedColors[NY] = color
                        NY += 1
            
            # for CC in CleanCount[::-1] :
            #     for SC in range(len(SeriesColors)) :
            #         if CleanSorted[SeriesColors[SC]] == CC :
            #             New_Y_Colors[NY] = SeriesColors[SC]
            #             New_Y_Keys[NY] = Y_Keys[SC]
            #             NY += 1
            # SeriesColors = New_Y_Colors[:]
            # Y_Keys = New_Y_Keys[:]
            # New_Y_Colors = None
            # New_Y_Keys = None
            NY = 0
            for color in SortedColors :
                for SC in range(len(SeriesColors)) :
                    if SeriesColors[SC] == color :
                        New_Y_Colors[NY] = color
                        New_Y_Keys[NY] = Y_Keys[SC]
                        NY += 1
            SeriesColors = New_Y_Colors[:]
            Y_Keys = New_Y_Keys[:]
            New_Y_Colors = None
            New_Y_Keys = None

    elif len( Y_Keys ) == 1 : # several simulation objects but a single key
        if SeriesColors == [] : 
            SeriesColors = ['solid']
        if len( ObjectsColors ) < len( SimResultObjects ) :
            NObjects = len(ObjectsColors)
            ObjectsColors = ObjectsColors + [None] * ( len( SimResultObjects ) - NObjects )
            for c in range (  NObjects , len( SimResultObjects ) ) :
                ObjectsColors[c] = SimResultObjects[c].get_Color()

    else : # several objects and keys
        if ColorBySimulation and not ColorBySeries :
            if len( ObjectsColors ) < len( SimResultObjects ) :
                for c in range ( len( ObjectsColors ) , len( SimResultObjects ) ) :
                    NObjects = len(ObjectsColors)
                    ObjectsColors = ObjectsColors + [None] * ( len( SimResultObjects ) - NObjects )
                    for c in range (  NObjects , len( SimResultObjects ) ) :
                        ObjectsColors[c] = SimResultObjects[c].get_Color()
    
            # SeriesColors used to set style
            SeriesColors = [None]*len( Y_Keys )
            for c in range ( len( Y_Keys ) ) :
                if 'BHP' in Y_Keys[c] :
                    SeriesColors[c] = (0,(5,10))
                elif 'BP' in Y_Keys[c] :
                    SeriesColors[c] = (0,(7,8))
                elif 'OP' in Y_Keys[c] or 'OIL' in Y_Keys[c]:
                    SeriesColors[c] = 'solid'
                elif 'NGL' in Y_Keys[c] :
                    SeriesColors[c] = 'dashed'
                elif 'LPG' in Y_Keys[c] :
                    SeriesColors[c] = 'dashdot'
                elif 'GP' in Y_Keys[c] or 'GAS' in Y_Keys[c] :
                    SeriesColors[c] = 'dotted'
                elif 'GI' in Y_Keys[c] :
                    SeriesColors[c] = (0,(3,5,1,5,1,5))
                elif 'WP' in Y_Keys[c] :
                    SeriesColors[c] = (0,(3,5,1,5,1,5))
                elif 'WI' in Y_Keys[c] :
                    SeriesColors[c] = ( 0 , (3,5,1,5))
                else :
                    SeriesColors[c] = '--'
            
            if DoNotRepeatColors : # repeated colors not-allowrd
                if len( set( SeriesColors )) == 1 :
                    SeriesColors = ['solid']*len( Y_Keys )
            else : # repeated colors allowrd
                pass
                    # SeriesColors = []
                    # for c in range ( len( Y_Keys ) ) :
                    #     SeriesColors.append('solid')
                        # time.sleep(timeout)
        

        
    if Y_Scales == [] :
        Y_Scales = [None] * len(Y_Keys)
                
    Ylabel = str(Y_Keys[0]) + ' ' + str(Y_Units[0])
    Title = ''
    if len(Y_Keys) == 1 :
        Title = Y_Keys[0] + ' vs ' + X_Key[0]
    if len(SimResultObjects) == 1 :
        if len(Title) > 0 :
            Title = Title + ' for ' + str(SimResultObjects[0].get_Name())
        else :
            Title = str(SimResultObjects[0].get_Name())
           
    fig = plt.figure(num=graphName,figsize=(6,4),dpi=150)
    Axis = [ fig.add_subplot() ]
    
    plt.title(Title)
    Axis[0].set_xlabel(Xlabel)
    Axis[0].set_ylabel(Ylabel)
    
    
    if max(Y_Axis) > 0 :
        for i in range( 1,max(Y_Axis)+1) :
            Axis.append( Axis[0].twinx() )
            Axis[i].set_ylabel('')
            time.sleep(timeout)
    
    AxLabels = {}
    AxUnits = {}
    for i in range( max(Y_Axis) +1 ) :
        AxLabels[i] = []
        AxUnits[i] = []
        time.sleep(timeout)

    
    Xdate = False
    if X_Key[0] in ( 'DATE' , 'DATES' ) :
        Xdate = True
        ToU = SimResultObjects[0].get_plotUnit(X_Key[0])
        FromU = SimResultObjects[0].get_Unit(X_Key[0])
        X0 = SimResultObjects[0].get_Vector(X_Key[0])[X_Key[0]]
        X = convertUnit( X0 , FromU , ToU , PrintConversionPath=(SimResultObjects[0].get_Verbosity()==1) )
        time.sleep(timeout*5)
        datemin = np.datetime64(X[0], 'Y')
        datemax = np.datetime64(X[-1], 'Y') + np.timedelta64(1, 'Y')
        #print('using dates')# format the ticks
        years = mdates.YearLocator()   # every year
        months = mdates.MonthLocator()  # every month
        years_fmt = mdates.DateFormatter('%Y')
        X = X.astype('O')
        Axis[0].xaxis.set_major_locator(years)
        Axis[0].xaxis.set_major_formatter(years_fmt)
        Axis[0].xaxis.set_minor_locator(months)

    plotLines = []
    for s in range(len(SimResultObjects)) :
        FromU = SimResultObjects[s].get_Unit(X_Key[0])
        ToU = X_Units[0]
        X0 = SimResultObjects[s].get_Vector(X_Key[0])[X_Key[0]]
        time.sleep(timeout)
        X = convertUnit( X0 , FromU , ToU , PrintConversionPath=(SimResultObjects[s].get_Verbosity()==1) )
        time.sleep(timeout*5)
        
        if Xdate == False and type(X) != np.ndarray :
            if type(X) == list or type(X) == tuple :
                try :
                    X = np.array(X,dtype='float')
                except :
                    print('<Plot> the X key ' + X_Key[0] + ' from simulation ' + SimResultObjects[s].get_Name() + ' is not numpy array ')
        elif Xdate :
            X = X.astype('datetime64[D]').astype('O') # X = X.astype('O')
                
        for y in range(len(Y_Keys)) :
            time.sleep(timeout)
            # check if the key exists in the object:
            Y0 = SimResultObjects[s].get_Vector( Y_Keys[y] )[ Y_Keys[y] ]

            if Y0 is None :
                pass
            else :
            
                if len( SimResultObjects ) == 1 :
                    # ThisLabel = str( Y_Keys[y] )
                    if str( Y_Keys[y] ) in Labels :
                        ThisLabel = str( Labels[Y_Keys[y]] )
                    else :
                        ThisLabel = str( Y_Keys[y] )

                elif len( Y_Keys ) == 1 :
                    # ThisLabel = str( SimResultObjects[s].get_Name() + ' ' + Y_Keys[0] )
                    if str( SimResultObjects[s] ) in Labels :
                        ThisLabel = str( Labels[SimResultObjects[s]] )
                    elif str( SimResultObjects[s].get_Name() ) in Labels :
                        ThisLabel = str( Labels[SimResultObjects[s].get_Name()] )
                    else :
                        ThisLabel = str( SimResultObjects[s].get_Name() ) # + ' ' + Y_Keys[0] )
                else :
                    # ThisLabel = str( SimResultObjects[s].get_Name() + ' ' + Y_Keys[y] )
                    if str( SimResultObjects[s] ) in Labels :
                        ThisLabel = str( Labels[SimResultObjects[s]] )
                    elif str( SimResultObjects[s].get_Name() ) in Labels :
                        ThisLabel = str( Labels[SimResultObjects[s].get_Name()] )
                    else :
                        ThisLabel = str( SimResultObjects[s].get_Name() )
                        
                    if str( Y_Keys[y] ) in Labels :
                        ThisLabel = ThisLabel + ' ' + str( Labels[Y_Keys[y]] )
                    else :
                        ThisLabel = ThisLabel + ' ' + str( Y_Keys[y] )
                
                # convertUnit(value, fromUnit, toUnit, PrintConversionPath=True):  
                FromU = SimResultObjects[s].get_Unit( Y_Keys[y] )
                ToU = Y_Units[ y ]
                
                Y = convertUnit( Y0 , FromU , ToU , PrintConversionPath=(SimResultObjects[s].get_Verbosity()==1) )
                time.sleep(timeout*5)
                if type(Y) != np.ndarray :
                    if type(X) == list or type(X) == tuple :
                        try :
                            Y = np.array(Y,dtype='float')
                        except :
                            print('<Plot> the Y key ' + Y_Keys[y] + ' from simulation ' + SimResultObjects[s].get_Name() + ' is not numpy array ')
                    
                if type(Y) == np.ndarray :    
                    if len(Y) != len(X) :
                        print('<Plot> the Y vector ' + str( Y_Keys[y]) + ' from the model ' + str( SimResultObjects[s] ) + ' contains less than tha its X vector ' + str( X_Key[0] ) + '\n       len(Y):' + str(len(Y)) + ' != len(X):' + str(len(X))) 
                    else : 
                        Yax = Y_Axis[ y ]
                        Lw = linewidth[y]
                        Ls = 'solid'
                        if len( SimResultObjects ) == 1 :
                            Lc = SeriesColors[y]
                        else :
                            Lc = ObjectsColors[s]
                        if len( Y_Keys ) == 1 :
                            Yax = 0
                        if len( SimResultObjects ) > 1 and len( Y_Keys ) > 1 :
                            Ls = SeriesColors[s]
                        
                        plotLines += Axis[ Yax  ].plot( X ,Y , linestyle=Ls , linewidth=Lw , color=Lc , label=ThisLabel) 
                        # if len( SimResultObjects ) == 1 :
                        #     plotLines += Axis[ Yax  ].plot( X ,Y , linestyle=Ls , linewidth=Lw , color=Lc , label=ThisLabel) 
                        # elif len( Y_Keys ) == 1 :
                        #     plotLines += Axis[ 0 ].plot( X ,Y , linestyle=Ls , linewidth=Lw , color=Lc , label=ThisLabel) 
                        # else :
                        #     plotLines += Axis[ Yax  ].plot( X ,Y , linestyle=Ls , linewidth=Lw , color=Lc , label=ThisLabel) 
            
                        if Xdate :
                            # round to nearest years.
                            if np.datetime64(X[0], 'Y') < datemin :
                                datemin = np.datetime64(X[0], 'Y')
                            if np.datetime64(X[-1], 'Y') + np.timedelta64(1, 'Y') > datemax :
                                datemax = np.datetime64(X[-1], 'Y') + np.timedelta64(1, 'Y')
        
                        AxLabels[ Y_Axis[ y ] ].append( Y_Keys[y].split(':')[0] )
                        AxUnits[ Y_Axis[ y ] ].append( Y_Units[y] )

        if Xdate :
            Axis[0].set_xlim(datemin, datemax)
            fig.autofmt_xdate()
            Axis[0].fmt_xdata = mdates.DateFormatter('%Y-%b')
    
    for i in range( max(Y_Axis) +1 ) : # for i in range( max(Y_Axis) +1) :
        time.sleep(timeout)
        textA = ', '.join( list( set( AxLabels[i] ) ) )
        textB = ' [ ' + ', '.join( list( set( AxUnits[i] ) ) ) + ' ]'
        Axis[i].set_ylabel( textA + textB )
        if len(Y_Scales) < i and Y_Scales[i] is not None :
            Axis[i].set( ylim=(Y_Scales[i]))
    
    if X_Scale != [] :
        Axis[0].set_xlim(X_Scale[0], X_Scale[1])
    # Axis[0].set_xlim(0, 50)
    if DoNotRepeatColors :
        plotLabels = [ l.get_label() for l in plotLines ]
        LegendLines = plotLines
    else :
        plotLabels = []
        LegendLines = []
        labeled = []
        for l in plotLines :
            N = SeriesColors.count( SeriesColors[ Y_Keys.index(l.get_label()) ] )
            if N < 10 :
                plotLabels += [ l.get_label() ]
                LegendLines += [ l ]
            elif mainKey(l.get_label()) not in labeled :
                plotLabels  += [ mainKey(l.get_label()) ]
                LegendLines += [ l ]
                labeled.append( mainKey(l.get_label()) )
            else :
                plotLabels  += [ None ]
                LegendLines += [ None ]
        
    Axis[0].legend( LegendLines , plotLabels , loc=legendLocation )  # LegendLines contains selected plotLines for the leggend
    plt.show()

    return fig

def savePlot(figure,FileName='') :
    figure.savefig(FileName)
    

def SquareDifferences( SimResultObjects=[] , AttributesOrKeys=[] , TimeSteps=None , Interpolate=False ) :
    """
    Calculates the square difference of two or more SimResults objects.
    Return a tuple containing :
        the total of the square difference
        the partial totals of square differences forevery key
        the profile of the total square difference
        the DataFrame of the square difference for every matching key
        a dictionary with all the produced input DataFrames
        
    Parameters: 
        SimResultObjects is a list of the objects to opetate with.
        Usually only two objects are passed but could be more than two,
        in which case all the other objects will be compared to the
        first object and the total summation returned.
            SimResultObjects=[Results1 , Results2] where Results1 
            and Results2 are SimResult objects
            
            SqDiff = sum( ( Profile[0] - Profile[i] )**2 )
            
        AttributesOrKeys is a list of attributes or keys to compare. 
            The attributes or keys must exist in both SimResult objects.
            If a well, group or region attribute is requested all the 
            corresponding and matching keys will be used.
            i.e:
                FOPT, WBHP, GGPR, RPPO are attributes 
                but WBHP:W1, RPPO:1, GGPR:G1 are keys
                the attibute WBHP will generate the key WBHP:W1 
                and any other matching wells 
        TimeSteps is the list or array of timesteps to be compared. 
            If empty all the coinciding TimeSteps will be calculated.
        Interpolate set to True allows the function to interpolate the 
            TimeSteps not matching both SimResult objects.
    """
    MatchingKeys = []
    # MatchingTimes = []
    Atts = []
    TimeKind = 'TIME'
    verbosity = SimResultObjects[0].get_Verbosity()
    verbose( verbosity , 1 , ' < SqDiff > sarting with verbosity set to ' + str(verbosity))
    
    verbose( verbosity , 1 , ' < SqDiff > the following objects will be used:')
    if verbosity > 0 :
        for obj in SimResultObjects :
            verbose( verbosity , 1 , ' < SqDiff > ' + str( obj.get_Name() ))
        
    
    # split keys from attributes
    verbose( verbosity , 1 , ' < SqDiff > checking AttributesOrKeys list:')
    verbose( verbosity , 0 , ' < SqDiff >   Keys          Attributes')
    
    if type(AttributesOrKeys) == str :
        AttributesOrKeys = [AttributesOrKeys]
    for each in AttributesOrKeys :
        if ':' in each :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < SqDiff >   ' + each.strip() )
        elif each.strip()[0] == 'W' or each.strip()[0] == 'G' or each.strip()[0] == 'R' :
            Atts.append(each.strip())
            verbose( verbosity , 0 , ' < SqDiff >                 ' + each.strip() )
        else :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < SqDiff >   ' + each.strip() )
    verbose( verbosity , 1 , ' < SqDiff > found ' + str(len(MatchingKeys)) + ' Keys and ' + str(len(Atts)) + ' Attributes,')
    
    # extract the keys corresponding to the attributes
    for obj in SimResultObjects :
        for Att in Atts :
            MatchingKeys += list( obj.get_Keys(pattern=str(Att)+':*' ) )
    Atts=None
    
    # eliminate duplicated keys
    MatchingKeys = list( set( MatchingKeys ) )
    
    # keep only keys matching all the objects and 
    for obj in SimResultObjects :
        MatchingKeys = list( set(MatchingKeys).intersection(set( obj.get_Keys() )) )
    verbose( verbosity , 1 , ' < SqDiff > totalizing ' + str(len(MatchingKeys)) + ' Keys after extending the Attributes and removing duplicates.')

    if TimeSteps is None :
        verbose( verbosity , 1 , ' < SqDiff > TimeSteps not received, all the matching timesteps will be used.')
        TimeSteps = list()
        for obj in SimResultObjects :
            verbose( verbosity , 0 , ' < SqDiff > getting TimeSteps from ' + str(obj.get_Name()) + '\n < SqDiff > extracted ' + str(len( list( obj.get_Vector( TimeKind )[ TimeKind ] ))) + ' ' + TimeKind + '.' )
            TimeSteps += list( obj.get_Vector( TimeKind )[ TimeKind ] )
        verbose( verbosity , 1 , ' < SqDiff > ' + str(len(TimeSteps)) + ' TimeSteps found.')
        TimeSteps = list( set( TimeSteps ) )
        TimeSteps.sort()
        verbose( verbosity , 1 , ' < SqDiff > ' + str(len(TimeSteps)) + ' sorted TimeSteps found.')
        if Interpolate == False :
            for obj in SimResultObjects :
                verbose( verbosity , 1 , ' < SqDiff > looking for matching TimeSteps for ' + obj.get_Name() )
                TimeSteps = list( set( TimeSteps ).intersection( set( list( obj.get_Vector( TimeKind )[ TimeKind ] ) ) ) )
        verbose( verbosity , 1 , ' < SqDiff > ' + str(len(TimeSteps)) + ' TimeSteps found, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
                
    else :
        verbose( verbosity , 1 , ' < SqDiff > ' + str(len(TimeSteps)) + ' TimeSteps received, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
        if type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('DATES')['DATES'][0] )        :
            TimeKind = 'DATES'
        elif type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('TIME')['TIME'][0] ) :
            TimeKind = 'TIME'
        else :
            verbose( verbosity , -1 , ' < SqDiff > TimeSteps set by default to TIME')
            TimeKind = 'TIME'
        verbose( verbosity , 1 , ' < SqDiff > TimeSteps found to be of type ' + TimeKind )
        if Interpolate == False :
            for obj in SimResultObjects :
                TimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) > 0 :
                verbose( verbosity , 1 , ' < SqDiff > ' + str(len(TimeSteps)) + ' TimeSteps found matching the simulation data TimeSteps, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
            else :
                verbose( verbosity , 2 , ' < SqDiff > ' + 'No matching TimeSteps in the input profiles.' )
        else :
            for obj in SimResultObjects :
                MatchingTimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) - len(MatchingTimeSteps) > 0 :
                verbose( verbosity , 2 , ' < SqDiff > WARNING: data will be interpolated for ' + str( len(TimeSteps) - len(MatchingTimeSteps) ) + ' TimeSteps not found in the simulation results.\n < SqDiff > WARNING: Set Interpolate=False to avoid this behaviour.' )
    
    # calculate differences:
    # request base DataFrame:
    verbose( verbosity , 1 , ' < SqDiff >  prepating the Pandas DataFrames, please wait...')
    baseDF = SimResultObjects[0].get_DataFrame( Keys=MatchingKeys , Index=TimeKind )
    baseDF.replace([SimResultObjects[0].null], np.nan, inplace=True )
    baseDF.interpolate(axis=0,inplace=True)
    baseDF.replace([np.inf, -np.inf], 0.0, inplace=True)
    baseDF.fillna(value=0.0,inplace=True)
    
    # prepare summation DataFrame fill with zeros
    sumDF = {}
    for each in MatchingKeys :
        sumDF[each] = [0]*len(TimeSteps)
    sumDF = pd.DataFrame( data=sumDF , index=TimeSteps )
    
    # prepare differences DataFrame fill with zeros
    diffDF = {}
    for each in MatchingKeys :
        diffDF[each] = [0]*len(TimeSteps)
    diffDF = pd.DataFrame( data=diffDF , index=TimeSteps )   
    
    # filter base DataFrame and save into dictionary
    dictOfDF = {}
    dictOfDF[SimResultObjects[0]] = (diffDF + baseDF).dropna(axis=0 , inplace=False)
    
    # calculate every difference and add it to the sumDF
    for obj in range(1, len(SimResultObjects)) :
        # get DataFrame with units converted to first DataFrame 
        otherDF = SimResultObjects[obj].get_ConvertedDataFrame( Keys=MatchingKeys , Index=TimeKind , OtherObject_or_NewUnits=SimResultObjects[0] )
        otherDF.replace([SimResultObjects[obj].null], np.nan, inplace=True )
        otherDF.interpolate(axis=0,inplace=True)
        otherDF.replace([np.inf, -np.inf], 0.0,inplace=True)
        otherDF.fillna(value=0.0,inplace=True)
        
        if TimeKind in otherDF.columns :
            otherDF.drop( columns=[TimeKind] , inplace=True)
        # filter the required time steps and save into dictionary
        dictOfDF[SimResultObjects[obj]] = diffDF * 0.0 + otherDF
        dictOfDF[SimResultObjects[obj]].dropna(axis=0 , inplace=True)
        # calculate differente 
        deltaDF = ( dictOfDF[SimResultObjects[obj]] - dictOfDF[SimResultObjects[0]] )**2
        # add square difference to totalization DataFrame
        sumDF = sumDF + deltaDF
        sumDF.dropna(axis=0 , inplace=True)
    verbose( verbosity , -1 , ' < SqDiff >  resulting total SquareDifference is: ' + str( sumDF.sum(axis=1).sum(axis=0) ) )
    return ( sumDF.sum(axis=1).sum(axis=0) , sumDF.sum(axis=0) , pd.DataFrame(data=sumDF.sum(axis=1),index=sumDF.index,columns=['SquareDifferences']) , sumDF ,  dictOfDF  )


def PercentualDifference( SimResultObjects=[] , AttributesOrKeys=[] , TimeSteps=None , Interpolate=False ) :
    """
    Calculates the square difference of two or more SimResults objects.
    Return a tuple containing :
        the mean of the absolute normalized differences
        the partial mean of the absolute normalized differences forevery key
        the profile of the absolut normalized differences
        a dictionary with all the produced input DataFrames
        
    Parameters: 
        SimResultObjects is a list of the objects to opetate with.
        Usually only two objects are passed but could be more than two,
        in which case all the other objects will be compared to the
        first object and the total summation returned.
            SimResultObjects=[Results1 , Results2] where Results1 
            and Results2 are SimResult objects
            
            %Diff = mean( abs( Profile[0] - Profile[i] ) / Profile[0] )
            
        AttributesOrKeys is a list of attributes or keys to compare. 
            The attributes or keys must exist in both SimResult objects.
            If a well, group or region attribute is requested all the 
            corresponding and matching keys will be used.
            i.e:
                FOPT, WBHP, GGPR, RPPO are attributes 
                but WBHP:W1, RPPO:1, GGPR:G1 are keys
                the attibute WBHP will generate the key WBHP:W1 
                and any other matching wells 
        TimeSteps is the list or array of timesteps to be compared. 
            If empty all the coinciding TimeSteps will be calculated.
        Interpolate set to True allows the function to interpolate the 
            TimeSteps not matching both SimResult objects.
    """
    MatchingKeys = []
    # MatchingTimes = []
    Atts = []
    TimeKind = 'TIME'
    verbosity = SimResultObjects[0].get_Verbosity()
    verbose( verbosity , 1 , ' < %Diff > sarting with verbosity set to ' + str(verbosity))
    
    verbose( verbosity , 1 , ' < %Diff > the following objects will be used:')
    if verbosity > 0 :
        for obj in SimResultObjects :
            verbose( verbosity , 1 , ' < %Diff > ' + str( obj.get_Name() ))
        
    
    # split keys from attributes
    verbose( verbosity , 1 , ' < %Diff > checking AttributesOrKeys list:')
    verbose( verbosity , 0 , ' < %Diff >   Keys          Attributes')
    
    if type(AttributesOrKeys) == str :
        AttributesOrKeys = [AttributesOrKeys]
    for each in AttributesOrKeys :
        if ':' in each :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < %Diff >   ' + each.strip() )
        elif each.strip()[0] == 'W' or each.strip()[0] == 'G' or each.strip()[0] == 'R' :
            Atts.append(each.strip())
            verbose( verbosity , 0 , ' < %Diff >                 ' + each.strip() )
        else :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < %Diff >   ' + each.strip() )
    verbose( verbosity , 1 , ' < %Diff > found ' + str(len(MatchingKeys)) + ' Keys and ' + str(len(Atts)) + ' Attributes,')
    
    # extract the keys corresponding to the attributes
    for obj in SimResultObjects :
        for Att in Atts :
            MatchingKeys += list( obj.get_Keys(pattern=str(Att)+':*' ) )
    Atts=None
    
    # eliminate duplicated keys
    MatchingKeys = list( set( MatchingKeys ) )
    
    # keep only keys matching all the objects and 
    for obj in SimResultObjects :
        MatchingKeys = list( set(MatchingKeys).intersection(set( obj.get_Keys() )) )
    verbose( verbosity , 1 , ' < %Diff > totalizing ' + str(len(MatchingKeys)) + ' Keys after extending the Attributes and removing duplicates.')

    if TimeSteps is None :
        verbose( verbosity , 1 , ' < %Diff > TimeSteps not received, all the matching timesteps will be used.')
        TimeSteps = list()
        for obj in SimResultObjects :
            verbose( verbosity , 0 , ' < %Diff > getting TimeSteps from ' + str(obj.get_Name()) + '\n < %Diff > extracted ' + str(len( list( obj.get_Vector( TimeKind )[ TimeKind ] ))) + ' ' + TimeKind + '.' )
            TimeSteps += list( obj.get_Vector( TimeKind )[ TimeKind ] )
        verbose( verbosity , 1 , ' < %Diff > ' + str(len(TimeSteps)) + ' TimeSteps found.')
        TimeSteps = list( set( TimeSteps ) )
        TimeSteps.sort()
        verbose( verbosity , 1 , ' < %Diff > ' + str(len(TimeSteps)) + ' sorted TimeSteps found.')
        if Interpolate == False :
            for obj in SimResultObjects :
                verbose( verbosity , 1 , ' < %Diff > looking for matching TimeSteps for ' + obj.get_Name() )
                TimeSteps = list( set( TimeSteps ).intersection( set( list( obj.get_Vector( TimeKind )[ TimeKind ] ) ) ) )
        verbose( verbosity , 1 , ' < %Diff > ' + str(len(TimeSteps)) + ' TimeSteps found, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
                
    else :
        verbose( verbosity , 1 , ' < %Diff > ' + str(len(TimeSteps)) + ' TimeSteps received, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
        if type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('DATES')['DATES'][0] )        :
            TimeKind = 'DATES'
        elif type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('TIME')['TIME'][0] ) :
            TimeKind = 'TIME'
        verbose( verbosity , 1 , ' < %Diff > TimeSteps found to be of type ' + TimeKind )
        if Interpolate == False :
            for obj in SimResultObjects :
                TimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) > 0 :
                verbose( verbosity , 1 , ' < %Diff > ' + str(len(TimeSteps)) + ' TimeSteps found matching the simulation data TimeSteps, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
            else :
                verbose( verbosity , 2 , ' < %Diff > ' + 'No matching TimeSteps in the input profiles.' )
        else :
            for obj in SimResultObjects :
                MatchingTimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) - len(MatchingTimeSteps) > 0 :
                verbose( verbosity , 2 , ' < %Diff > WARNING: data will be interpolated for ' + str( len(TimeSteps) - len(MatchingTimeSteps) ) + ' TimeSteps not found in the simulation results.\n < %Diff > WARNING: Set Interpolate=False to avoid this behaviour.' )
    
    # remove the index from the list of keys:
    if TimeKind in MatchingKeys :
        # removed = MatchingKeys.pop(MatchingKeys.index(TimeKind))
        verbose( SimResultObjects[0].speak , 1 , ' ' + str( MatchingKeys.pop(MatchingKeys.index(TimeKind)) ) + ' used ad index of the dataframe.')
    
    # calculate differences:
    # request base DataFrame:
    verbose( verbosity , 1 , ' < %Diff >  prepating the Pandas DataFrames, please wait...')
    baseDF = SimResultObjects[0].get_DataFrame( Keys=MatchingKeys , Index=TimeKind )
    baseDF.replace([SimResultObjects[0].null], np.nan, inplace=True )
    baseDF.interpolate(axis=0,inplace=True)
    baseDF.replace([np.inf, -np.inf], 0.0, inplace=True)
    baseDF.fillna(value=0.0,inplace=True)

    # prepare summation DataFrame fill with zeros
    sumDF = {}
    for each in MatchingKeys :
        sumDF[each] = [0]*len(TimeSteps)
    sumDF = pd.DataFrame( data=sumDF , index=TimeSteps )
    
    # prepare differences DataFrame fill with zeros
    diffDF = {}
    for each in MatchingKeys :
        diffDF[each] = [0]*len(TimeSteps)
    diffDF = pd.DataFrame( data=diffDF , index=TimeSteps )   
    
    # filter base DataFrame and save into dictionary
    dictOfDF = {}
    dictOfDF[SimResultObjects[0]] = (diffDF + baseDF).dropna(axis=0 , inplace=False)
    
    # calculate inverse base DataFrame and replace divisions by zero with 0.0
    divDF = 1.0/dictOfDF[SimResultObjects[0]]
    divDF.fillna(value=0.0,inplace=True)
    divDF.replace([np.inf, -np.inf], 0.0, inplace=True)
    
    # calculate every difference and add it to the sumDF
    for obj in range(1, len(SimResultObjects)) :
        # get DataFrame with units converted to first DataFrame 
        otherDF = SimResultObjects[obj].get_ConvertedDataFrame( Keys=MatchingKeys , Index=TimeKind , OtherObject_or_NewUnits=SimResultObjects[0] ) 
        otherDF.replace([SimResultObjects[obj].null], np.nan, inplace=True )
        otherDF.interpolate(axis=0,inplace=True)
        otherDF.replace([np.inf, -np.inf], 0.0, inplace=True)
        otherDF.fillna(value=0.0,inplace=True)
        
        if TimeKind in otherDF.columns :
            otherDF.drop( columns=[TimeKind] , inplace=True)
        # filter the required time steps and save into dictionary
        dictOfDF[SimResultObjects[obj]] = diffDF * 0.0 + otherDF
        dictOfDF[SimResultObjects[obj]].dropna(axis=0 , inplace=True)
        # calculate difference
        deltaDF = ( dictOfDF[SimResultObjects[obj]] - dictOfDF[SimResultObjects[0]] )
        # normalize by the base values
        deltaDF = deltaDF * divDF
        deltaDF.dropna(axis=0 , inplace=True)
        # add to the totalization DataFrame
        sumDF = sumDF + deltaDF
        sumDF.dropna(axis=0 , inplace=True)

    verbose( verbosity , -1 , ' < %Diff >  resulting Percentual Difference is: ' + str( abs(sumDF).mean(axis=1).mean(axis=0) ) )
    return ( abs(sumDF).mean(axis=1,skipna=True).mean(axis=0,skipna=True) , abs(sumDF).mean(axis=0,skipna=True) , pd.DataFrame(data=abs(sumDF).mean(axis=1,skipna=True),index=abs(sumDF).index,columns=['PercentualDifference']) , sumDF , dictOfDF ) 


def WeightedDifference( SimResultObjects=[] , AttributesOrKeys=[] , TimeSteps=None , Interpolate=False ) :
    """
    Calculates the square difference of two or more SimResults objects.
    Return a tuple containing :
        the mean of the weighted percentual differences
        the partial mean of the absolute normalized differences forevery key
        the profile of the absolut normalized differences
        the DataFrame of the absolut normalized differences for every matching keys
        the DataFrame of the normalized differences for every matching keys
        a dictionary with all the produced input DataFrames
        
    Parameters: 
        SimResultObjects is a list of the objects to opetate with.
        Usually only two objects are passed but could be more than two,
        in which case all the other objects will be compared to the
        first object and the total summation returned.
            SimResultObjects=[Results1 , Results2] where Results1 
            and Results2 are SimResult objects
            
            WeightDiff = sum( abs( Resutls[0] - Results[i] ) * Resutls[0] / max(Resutls[0])  )
            
        AttributesOrKeys is a list of attributes or keys to compare. 
            The attributes or keys must exist in both SimResult objects.
            If a well, group or region attribute is requested all the 
            corresponding and matching keys will be used.
            i.e:
                FOPT, WBHP, GGPR, RPPO are attributes 
                but WBHP:W1, RPPO:1, GGPR:G1 are keys
                the attibute WBHP will generate the key WBHP:W1 
                and any other matching wells 
        TimeSteps is the list or array of timesteps to be compared. 
            If empty all the coinciding TimeSteps will be calculated.
        Interpolate set to True allows the function to interpolate the 
            TimeSteps not matching both SimResult objects.
    """
    MatchingKeys = []
    # MatchingTimes = []
    Atts = []
    TimeKind = 'TIME'
    verbosity = SimResultObjects[0].get_Verbosity()
    verbose( verbosity , 1 , ' < WeightDiff > sarting with verbosity set to ' + str(verbosity))
    
    verbose( verbosity , 1 , ' < WeightDiff > the following objects will be used:')
    if verbosity > 0 :
        for obj in SimResultObjects :
            verbose( verbosity , 1 , ' < WeightDiff > ' + str( obj.get_Name() ))
        
    
    # split keys from attributes
    verbose( verbosity , 1 , ' < WeightDiff > checking AttributesOrKeys list:')
    verbose( verbosity , 0 , ' < WeightDiff >   Keys          Attributes')
    
    if type(AttributesOrKeys) == str :
        AttributesOrKeys = [AttributesOrKeys]
    for each in AttributesOrKeys :
        if ':' in each :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < WeightDiff >   ' + each.strip() )
        elif each.strip()[0] == 'W' or each.strip()[0] == 'G' or each.strip()[0] == 'R' :
            Atts.append(each.strip())
            verbose( verbosity , 0 , ' < WeightDiff >                 ' + each.strip() )
        else :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < WeightDiff >   ' + each.strip() )
    verbose( verbosity , 1 , ' < WeightDiff > found ' + str(len(MatchingKeys)) + ' Keys and ' + str(len(Atts)) + ' Attributes,')
    
    # extract the keys corresponding to the attributes
    for obj in SimResultObjects :
        for Att in Atts :
            MatchingKeys += list( obj.get_Keys(pattern=str(Att)+':*' ) )
    Atts=None
    
    # eliminate duplicated keys
    MatchingKeys = list( set( MatchingKeys ) )
    
    # keep only keys matching all the objects and 
    for obj in SimResultObjects :
        MatchingKeys = list( set(MatchingKeys).intersection(set( obj.get_Keys() )) )
    verbose( verbosity , 1 , ' < WeightDiff > totalizing ' + str(len(MatchingKeys)) + ' Keys after extending the Attributes and removing duplicates.')

    if TimeSteps is None :
        verbose( verbosity , 1 , ' < WeightDiff > TimeSteps not received, all the matching timesteps will be used.')
        TimeSteps = list()
        for obj in SimResultObjects :
            verbose( verbosity , 0 , ' < WeightDiff > getting TimeSteps from ' + str(obj.get_Name()) + '\n < WeightDiff > extracted ' + str(len( list( obj.get_Vector( TimeKind )[ TimeKind ] ))) + ' ' + TimeKind + '.' )
            TimeSteps += list( obj.get_Vector( TimeKind )[ TimeKind ] )
        verbose( verbosity , 1 , ' < WeightDiff > ' + str(len(TimeSteps)) + ' TimeSteps found.')
        TimeSteps = list( set( TimeSteps ) )
        TimeSteps.sort()
        verbose( verbosity , 1 , ' < WeightDiff > ' + str(len(TimeSteps)) + ' sorted TimeSteps found.')
        if Interpolate == False :
            for obj in SimResultObjects :
                verbose( verbosity , 1 , ' < WeightDiff > looking for matching TimeSteps for ' + obj.get_Name() )
                TimeSteps = list( set( TimeSteps ).intersection( set( list( obj.get_Vector( TimeKind )[ TimeKind ] ) ) ) )
        verbose( verbosity , 1 , ' < WeightDiff > ' + str(len(TimeSteps)) + ' TimeSteps found, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
                
    else :
        verbose( verbosity , 1 , ' < WeightDiff > ' + str(len(TimeSteps)) + ' TimeSteps received, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
        if type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('DATES')['DATES'][0] )        :
            TimeKind = 'DATES'
        elif type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('TIME')['TIME'][0] ) :
            TimeKind = 'TIME'
        verbose( verbosity , 1 , ' < WeightDiff > TimeSteps found to be of type ' + TimeKind )
        if Interpolate == False :
            for obj in SimResultObjects :
                TimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) > 0 :
                verbose( verbosity , 1 , ' < WeightDiff > ' + str(len(TimeSteps)) + ' TimeSteps found matching the simulation data TimeSteps, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
            else :
                verbose( verbosity , 2 , ' < WeightDiff > ' + 'No matching TimeSteps in the input profiles.' )
        else :
            for obj in SimResultObjects :
                MatchingTimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) - len(MatchingTimeSteps) > 0 :
                verbose( verbosity , 2 , ' < WeightDiff > WARNING: data will be interpolated for ' + str( len(TimeSteps) - len(MatchingTimeSteps) ) + ' TimeSteps not found in the simulation results.\n < WeightDiff > WARNING: Set Interpolate=False to avoid this behaviour.' )
    
    # remove the index from the list of keys:
    if TimeKind in MatchingKeys :
        # removed = MatchingKeys.pop(MatchingKeys.index(TimeKind))
        verbose( SimResultObjects[0].speak , 1 , ' ' + str( MatchingKeys.pop(MatchingKeys.index(TimeKind)) ) + ' used ad index of the dataframe.')
    
    # calculate differences:
    # request base DataFrame:
    verbose( verbosity , 1 , ' < WeightDiff >  prepating the Pandas DataFrames, please wait...')
    baseDF = SimResultObjects[0].get_DataFrame( Keys=MatchingKeys , Index=TimeKind )
    baseDF.replace([SimResultObjects[0].null], np.nan , inplace=True )
    baseDF.interpolate(axis=0,inplace=True)
    baseDF.replace([np.inf, -np.inf], 0.0,inplace=True)
    baseDF.fillna(value=0.0,inplace=True)

    # prepare summation DataFrame fill with zeros
    sumDF = {}
    for each in MatchingKeys :
        sumDF[each] = [0]*len(TimeSteps)
    sumDF = pd.DataFrame( data=sumDF , index=TimeSteps )
    # prepare differences DataFrame fill with zeros
    diffDF = {}
    for each in MatchingKeys :
        diffDF[each] = [0]*len(TimeSteps)
    diffDF = pd.DataFrame( data=diffDF , index=TimeSteps )   
    
    dictOfDF = {}
    dictOfDF[SimResultObjects[0]] = (diffDF + baseDF).dropna(axis=0 , inplace=False)
    
    # calculate the DataFrame of weighting factors 
    MaxDF = abs(dictOfDF[SimResultObjects[0]]).max(axis=0,skipna=True)
    MaxDF.replace([0.0],1.0,inplace=True)
    weightDF = dictOfDF[SimResultObjects[0]] / MaxDF
    weightDF.replace([0.0],1.0,inplace=True)
    
    
    # calculate every difference and add it to the sumDF
    for obj in range(1, len(SimResultObjects)) :
        # get DataFrame with units converted to first DataFrame 
        otherDF = SimResultObjects[obj].get_ConvertedDataFrame( Keys=MatchingKeys , Index=TimeKind , OtherObject_or_NewUnits=SimResultObjects[0] ) 
        otherDF.replace([SimResultObjects[obj].null], np.nan, inplace=True)
        otherDF.interpolate(axis=0,inplace=True)
        otherDF.replace([np.inf, -np.inf], 0.0,inplace=True)
        otherDF.fillna(value=0.0,inplace=True)
        
        if TimeKind in otherDF.columns :
            otherDF.drop( columns=[TimeKind] , inplace=True)
        # filter the required time steps and save into dictionary
        dictOfDF[SimResultObjects[obj]] = diffDF * 0.0 + otherDF
        dictOfDF[SimResultObjects[obj]].dropna(axis=0 , inplace=True)
        
        # calculate the absolute differences
        deltaDF = ( dictOfDF[SimResultObjects[obj]] - dictOfDF[SimResultObjects[0]] )
        # apply the weighting factors
        deltaDF = deltaDF * weightDF
        deltaDF.dropna(axis=0 , inplace=True)
        # add to the totalization DataFrame
        sumDF = sumDF + deltaDF
        sumDF.dropna(axis=0 , inplace=True)

    verbose( verbosity , -1 , ' < WeightDiff >  resulting total WeightedDifference is: ' + str( abs(sumDF).mean(axis=1).mean(axis=0) ) )
    return ( abs(sumDF).mean(axis=1,skipna=True).mean(axis=0,skipna=True) , abs(sumDF).mean(axis=0,skipna=True) , pd.DataFrame(data=abs(sumDF).mean(axis=1,skipna=True),index=abs(sumDF).index,columns=['WeightedDifference']) , sumDF , dictOfDF ) 



def ZScaledDifference( SimResultObjects=[] , AttributesOrKeys=[] , TimeSteps=None , Interpolate=False ) :
    """
    Calculates the square difference of two or more SimResults objects.
    Return a tuple containing :
        the mean of the absolute normalized differences
        the partial mean of the absolute normalized differences forevery key
        the profile of the absolut normalized differences
        the DataFrame of the absolut normalized differences for every matching keys
        a dictionary with all the produced DataFrames
        
    Parameters: 
        SimResultObjects is a list of the objects to opetate with.
        Usually only two objects are passed but could be more than two,
        in which case all the other objects will be compared to the
        first object and the total summation returned.
            SimResultObjects=[Results1 , Results2] where Results1 
            and Results2 are SimResult objects
            
            ZScalDiff = Sum( sqrt( Resutls_1 ^2 - Results_i ^2 ) )
            
        AttributesOrKeys is a list of attributes or keys to compare. 
            The attributes or keys must exist in both SimResult objects.
            If a well, group or region attribute is requested all the 
            corresponding and matching keys will be used.
            i.e:
                FOPT, WBHP, GGPR, RPPO are attributes 
                but WBHP:W1, RPPO:1, GGPR:G1 are keys
                the attibute WBHP will generate the key WBHP:W1 
                and any other matching wells 
        TimeSteps is the list or array of timesteps to be compared. 
            If empty all the coinciding TimeSteps will be calculated.
        Interpolate set to True allows the function to interpolate the 
            TimeSteps not matching both SimResult objects.
    """
    MatchingKeys = []
    # MatchingTimes = []
    Atts = []
    TimeKind = 'TIME'
    verbosity = SimResultObjects[0].get_Verbosity()
    verbose( verbosity , 1 , ' < ZScalDiff > sarting with verbosity set to ' + str(verbosity))
    
    verbose( verbosity , 1 , ' < ZScalDiff > the following objects will be used:')
    if verbosity > 0 :
        for obj in SimResultObjects :
            verbose( verbosity , 1 , ' < ZScalDiff > ' + str( obj.get_Name() ))
        
    
    # split keys from attributes
    verbose( verbosity , 1 , ' < ZScalDiff > checking AttributesOrKeys list:')
    verbose( verbosity , 0 , ' < ZScalDiff >   Keys          Attributes')
    
    if type(AttributesOrKeys) == str :
        AttributesOrKeys = [AttributesOrKeys]
    for each in AttributesOrKeys :
        if ':' in each :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < ZScalDiff >   ' + each.strip() )
        elif each.strip()[0] == 'W' or each.strip()[0] == 'G' or each.strip()[0] == 'R' :
            Atts.append(each.strip())
            verbose( verbosity , 0 , ' < ZScalDiff >                 ' + each.strip() )
        else :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < ZScalDiff >   ' + each.strip() )
    verbose( verbosity , 1 , ' < ZScalDiff > found ' + str(len(MatchingKeys)) + ' Keys and ' + str(len(Atts)) + ' Attributes,')
    
    # extract the keys corresponding to the attributes
    for obj in SimResultObjects :
        for Att in Atts :
            MatchingKeys += list( obj.get_Keys(pattern=str(Att)+':*' ) )
    Atts=None
    
    # eliminate duplicated keys
    MatchingKeys = list( set( MatchingKeys ) )
    
    # keep only keys matching all the objects and 
    for obj in SimResultObjects :
        MatchingKeys = list( set(MatchingKeys).intersection(set( obj.get_Keys() )) )
    verbose( verbosity , 1 , ' < ZScalDiff > totalizing ' + str(len(MatchingKeys)) + ' Keys after extending the Attributes and removing duplicates.')

    if TimeSteps is None :
        verbose( verbosity , 1 , ' < ZScalDiff > TimeSteps not received, all the matching timesteps will be used.')
        TimeSteps = list()
        for obj in SimResultObjects :
            verbose( verbosity , 0 , ' < ZScalDiff > getting TimeSteps from ' + str(obj.get_Name()) + '\n < ZScalDiff > extracted ' + str(len( list( obj.get_Vector( TimeKind )[ TimeKind ] ))) + ' ' + TimeKind + '.' )
            TimeSteps += list( obj.get_Vector( TimeKind )[ TimeKind ] )
        verbose( verbosity , 1 , ' < ZScalDiff > ' + str(len(TimeSteps)) + ' TimeSteps found.')
        TimeSteps = list( set( TimeSteps ) )
        TimeSteps.sort()
        verbose( verbosity , 1 , ' < ZScalDiff > ' + str(len(TimeSteps)) + ' sorted TimeSteps found.')
        if Interpolate == False :
            for obj in SimResultObjects :
                verbose( verbosity , 1 , ' < ZScalDiff > looking for matching TimeSteps for ' + obj.get_Name() )
                TimeSteps = list( set( TimeSteps ).intersection( set( list( obj.get_Vector( TimeKind )[ TimeKind ] ) ) ) )
        verbose( verbosity , 1 , ' < ZScalDiff > ' + str(len(TimeSteps)) + ' TimeSteps found, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
                
    else :
        verbose( verbosity , 1 , ' < ZScalDiff > ' + str(len(TimeSteps)) + ' TimeSteps received, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
        if type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('DATES')['DATES'][0] )        :
            TimeKind = 'DATES'
        elif type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('TIME')['TIME'][0] ) :
            TimeKind = 'TIME'
        verbose( verbosity , 1 , ' < ZScalDiff > TimeSteps found to be of type ' + TimeKind )
        if Interpolate == False :
            for obj in SimResultObjects :
                TimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) > 0 :
                verbose( verbosity , 1 , ' < ZScalDiff > ' + str(len(TimeSteps)) + ' TimeSteps found matching the simulation data TimeSteps, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
            else :
                verbose( verbosity , 2 , ' < ZScalDiff > ' + 'No matching TimeSteps in the input profiles.' )
        else :
            for obj in SimResultObjects :
                MatchingTimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) - len(MatchingTimeSteps) > 0 :
                verbose( verbosity , 2 , ' < ZScalDiff > WARNING: data will be interpolated for ' + str( len(TimeSteps) - len(MatchingTimeSteps) ) + ' TimeSteps not found in the simulation results.\n < ZScalDiff > WARNING: Set Interpolate=False to avoid this behaviour.' )
    
    # remove the index from the list of keys:
    if TimeKind in MatchingKeys :
        # removed = MatchingKeys.pop(MatchingKeys.index(TimeKind))
        verbose( SimResultObjects[0].speak , 1 , ' ' + str( MatchingKeys.pop(MatchingKeys.index(TimeKind)) ) + ' used ad index of the dataframe.')
    
    # calculate differences:
    # request base DataFrame:
    verbose( verbosity , 1 , ' < ZScalDiff >  prepating the Pandas DataFrames, please wait...')
    baseDF = SimResultObjects[0].get_DataFrame( Keys=MatchingKeys , Index=TimeKind )
    baseDF.replace([SimResultObjects[0].null], np.nan, inplace=True )
    baseDF.interpolate(axis=0,inplace=True)
    baseDF.replace([np.inf, -np.inf], 0.0, inplace=True)
    baseDF.fillna(value=0.0,inplace=True)

    # prepare summation DataFrame fill with zeros
    sumDF = {}
    for each in MatchingKeys :
        sumDF[each] = [0]*len(TimeSteps)
    sumDF = pd.DataFrame( data=sumDF , index=TimeSteps )
    # prepare differences DataFrame fill with zeros
    diffDF = {}
    for each in MatchingKeys :
        diffDF[each] = [0]*len(TimeSteps)
    diffDF = pd.DataFrame( data=diffDF , index=TimeSteps )   
    
    dictOfDF = {}
    dictOfDF[SimResultObjects[0]] = (diffDF + baseDF).dropna(axis=0 , inplace=False)
    
    divDF = 1.0/dictOfDF[SimResultObjects[0]]
    divDF.fillna(value=0.0,inplace=True)
    divDF.replace([np.inf, -np.inf], 0.0,inplace=True)
    divDF.fillna(value=0.0,inplace=True)
    
    ZmeanDF = dictOfDF[SimResultObjects[0]].mean(axis=0,skipna=True)
    ZbaseDF = dictOfDF[SimResultObjects[0]] - ZmeanDF
    ZstdDF = ZbaseDF.std(axis=0,skipna=True)
    ZstdDF.replace([0.0], 1.0,inplace=True)
    ZstdDF.fillna(value=1.0,inplace=True)
    ZbaseDF = ZbaseDF / ZstdDF
    
    ZdivDF = 1.0/ZbaseDF
    ZdivDF.replace([np.inf, -np.inf], 0.0,inplace=True)
    ZdivDF.fillna(value=0.0,inplace=True)
    
    # calculate every difference and add it to the sumDF
    for obj in range(1, len(SimResultObjects)) :
        # get DataFrame with units converted to first DataFrame 
        otherDF = SimResultObjects[obj].get_ConvertedDataFrame( Keys=MatchingKeys , Index=TimeKind , OtherObject_or_NewUnits=SimResultObjects[0] ) 
        otherDF.replace([SimResultObjects[obj].null], np.nan, inplace=True )
        otherDF.interpolate(axis=0,inplace=True)
        otherDF.replace([np.inf, -np.inf], 0.0,inplace=True)
        otherDF.fillna(value=0.0,inplace=True)
        
        if TimeKind in otherDF.columns :
            otherDF.drop( columns=[TimeKind] , inplace=True)
        # filter the required time steps and save into dictionary
        dictOfDF[SimResultObjects[obj]] = diffDF * 0.0 + otherDF
        dictOfDF[SimResultObjects[obj]].dropna(axis=0 , inplace=True)
        # standarize the other DataFrame
        ZotherDF = dictOfDF[SimResultObjects[obj]] - ZmeanDF
        ZotherDF = ZotherDF / ZstdDF
        
        deltaDF = ZotherDF - ZbaseDF
        deltaDF.dropna(axis=0 , inplace=True)
        
        diffDF = diffDF + deltaDF * ZdivDF
        diffDF.dropna(axis=0 , inplace=True)
        sumDF = sumDF + deltaDF * divDF
        sumDF.dropna(axis=0 , inplace=True)

    verbose( verbosity , -1 , ' < ZScalDiff >  resulting total ZScaledDifference is: ' + str( abs(sumDF).mean(axis=1).mean(axis=0) ) )
    return ( abs(sumDF).mean(axis=1,skipna=True).mean(axis=0,skipna=True) , abs(sumDF).mean(axis=0,skipna=True) , pd.DataFrame(data=abs(sumDF).mean(axis=1,skipna=True),index=abs(sumDF).index,columns=['ZScaledDifference']) , sumDF , diffDF , dictOfDF ) 

def StandardError( SimResultObjects=[] , AttributesOrKeys=[] , TimeSteps=None , Interpolate=False ) :
    """
    Calculates the square difference of two or more SimResults objects.
    Return a tuple containing :
        the mean of the absolute normalized differences
        the partial mean of the absolute normalized differences forevery key
        the profile of the absolut normalized differences
        the DataFrame of the absolut normalized differences for every matching keys
        the DataFrame of the normalized differences for every matching keys
        a dictionary with all the produced DataFrames
        
    Parameters: 
        SimResultObjects is a list of the objects to opetate with.
        Usually only two objects are passed but could be more than two,
        in which case all the other objects will be compared to the
        first object and the total summation returned.
            SimResultObjects=[Results1 , Results2] where Results1 
            and Results2 are SimResult objects
            
            SqDiff = Sum( sqrt( Resutls_1 ^2 - Results_i ^2 ) )
            
        AttributesOrKeys is a list of attributes or keys to compare. 
            The attributes or keys must exist in both SimResult objects.
            If a well, group or region attribute is requested all the 
            corresponding and matching keys will be used.
            i.e:
                FOPT, WBHP, GGPR, RPPO are attributes 
                but WBHP:W1, RPPO:1, GGPR:G1 are keys
                the attibute WBHP will generate the key WBHP:W1 
                and any other matching wells 
        TimeSteps is the list or array of timesteps to be compared. 
            If empty all the coinciding TimeSteps will be calculated.
        Interpolate set to True allows the function to interpolate the 
            TimeSteps not matching both SimResult objects.
    """
    MatchingKeys = []
    # MatchingTimes = []
    Atts = []
    TimeKind = 'TIME'
    verbosity = SimResultObjects[0].get_Verbosity()
    verbose( verbosity , 1 , ' < StdError > sarting with verbosity set to ' + str(verbosity))
    
    verbose( verbosity , 1 , ' < StdError > the following objects will be used:')
    if verbosity > 0 :
        for obj in SimResultObjects :
            verbose( verbosity , 1 , ' < StdError > ' + str( obj.get_Name() ))
        
    
    # split keys from attributes
    verbose( verbosity , 1 , ' < StdError > checking AttributesOrKeys list:')
    verbose( verbosity , 0 , ' < StdError >   Keys          Attributes')
    
    if type(AttributesOrKeys) == str :
        AttributesOrKeys = [AttributesOrKeys]
    for each in AttributesOrKeys :
        if ':' in each :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < StdError >   ' + each.strip() )
        elif each.strip()[0] == 'W' or each.strip()[0] == 'G' or each.strip()[0] == 'R' :
            Atts.append(each.strip())
            verbose( verbosity , 0 , ' < StdError >                 ' + each.strip() )
        else :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < StdError >   ' + each.strip() )
    verbose( verbosity , 1 , ' < StdError > found ' + str(len(MatchingKeys)) + ' Keys and ' + str(len(Atts)) + ' Attributes,')
    
    # extract the keys corresponding to the attributes
    for obj in SimResultObjects :
        for Att in Atts :
            MatchingKeys += list( obj.get_Keys(pattern=str(Att)+':*' ) )
    Atts=None
    
    # eliminate duplicated keys
    MatchingKeys = list( set( MatchingKeys ) )
    
    # keep only keys matching all the objects and 
    for obj in SimResultObjects :
        MatchingKeys = list( set(MatchingKeys).intersection(set( obj.get_Keys() )) )
    verbose( verbosity , 1 , ' < StdError > totalizing ' + str(len(MatchingKeys)) + ' Keys after extending the Attributes and removing duplicates.')

    if TimeSteps is None :
        verbose( verbosity , 1 , ' < StdError > TimeSteps not received, all the matching timesteps will be used.')
        TimeSteps = list()
        for obj in SimResultObjects :
            verbose( verbosity , 0 , ' < StdError > getting TimeSteps from ' + str(obj.get_Name()) + '\n < SqDiff > extracted ' + str(len( list( obj.get_Vector( TimeKind )[ TimeKind ] ))) + ' ' + TimeKind + '.' )
            TimeSteps += list( obj.get_Vector( TimeKind )[ TimeKind ] )
        verbose( verbosity , 1 , ' < StdError > ' + str(len(TimeSteps)) + ' TimeSteps found.')
        TimeSteps = list( set( TimeSteps ) )
        TimeSteps.sort()
        verbose( verbosity , 1 , ' < StdError > ' + str(len(TimeSteps)) + ' sorted TimeSteps found.')
        if Interpolate == False :
            for obj in SimResultObjects :
                verbose( verbosity , 1 , ' < StdError > looking for matching TimeSteps for ' + obj.get_Name() )
                TimeSteps = list( set( TimeSteps ).intersection( set( list( obj.get_Vector( TimeKind )[ TimeKind ] ) ) ) )
        verbose( verbosity , 1 , ' < StdError > ' + str(len(TimeSteps)) + ' TimeSteps found, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
                
    else :
        verbose( verbosity , 1 , ' < StdError > ' + str(len(TimeSteps)) + ' TimeSteps received, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
        if type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('DATES')['DATES'][0] )        :
            TimeKind = 'DATES'
        elif type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('TIME')['TIME'][0] ) :
            TimeKind = 'TIME'
        verbose( verbosity , 1 , ' < StdError > TimeSteps found to be of type ' + TimeKind )
        if Interpolate == False :
            for obj in SimResultObjects :
                TimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) > 0 :
                verbose( verbosity , 1 , ' < StdError > ' + str(len(TimeSteps)) + ' TimeSteps found matching the simulation data TimeSteps, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
            else :
                verbose( verbosity , 2 , ' < StdError > ' + 'No matching TimeSteps in the input profiles.' )
        else :
            for obj in SimResultObjects :
                MatchingTimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) - len(MatchingTimeSteps) > 0 :
                verbose( verbosity , 2 , ' < StdError > WARNING: data will be interpolated for ' + str( len(TimeSteps) - len(MatchingTimeSteps) ) + ' TimeSteps not found in the simulation results.\n < SqDiff > WARNING: Set Interpolate=False to avoid this behaviour.' )
    
    # remove the index from the list of keys:
    if TimeKind in MatchingKeys :
        # removed = MatchingKeys.pop(MatchingKeys.index(TimeKind))
        verbose( SimResultObjects[0].speak , 1 , ' ' + str( MatchingKeys.pop(MatchingKeys.index(TimeKind)) ) + ' used ad index of the dataframe.')
    
    # calculate differences:
    # request base DataFrame:
    verbose( verbosity , 1 , ' < StdError >  prepating the Pandas DataFrames, please wait...')
    baseDF = SimResultObjects[0].get_DataFrame( Keys=MatchingKeys , Index=TimeKind )
    baseDF.replace([SimResultObjects[0].null], np.nan, inplace=True )
    baseDF.interpolate(axis=0,inplace=True)
    baseDF.replace([np.inf, -np.inf], 0.0, inplace=True)
    baseDF.fillna(value=0.0,inplace=True)
    
    ZbaseDF = baseDF - baseDF.mean(axis=0,skipna=True)
    ZbaseDF = ZbaseDF / ZbaseDF.std(axis=0,skipna=True)

    ZdivDF = 1.0/ZbaseDF
    ZdivDF.fillna(value=0.0,inplace=True)
    ZdivDF.replace([np.inf, -np.inf], 0.0, inplace=True)

    # prepare summation DataFrame fill with zeros
    sumDF = {}
    for each in MatchingKeys :
        sumDF[each] = [0]*len(TimeSteps)
    sumDF = pd.DataFrame( data=sumDF , index=TimeSteps )
    # prepare differences DataFrame fill with zeros
    diffDF = {}
    for each in MatchingKeys :
        diffDF[each] = [0]*len(TimeSteps)
    diffDF = pd.DataFrame( data=diffDF , index=TimeSteps )   
    
    dictOfDF = {}
    dictOfDF[SimResultObjects[0]] = (diffDF + baseDF).dropna(axis=0 , inplace=False)
    
    # MbaseDF = dictOfDF[SimResultObjects[0]].mean(axis=0,skipna=True)
    # DbaseDF = MbaseDF - dictOfDF[SimResultObjects[0]] 
    
    # calculate every difference and add it to the sumDF
    for obj in range(1, len(SimResultObjects)) :
        # using DataFrame with units converted to first DataFrame 
        otherDF = SimResultObjects[obj].get_ConvertedDataFrame( Keys=MatchingKeys , Index=TimeKind , OtherObject_or_NewUnits=SimResultObjects[0] ) 
        otherDF.replace([SimResultObjects[obj].null], np.nan, inplace=True )
        otherDF.interpolate(axis=0,inplace=True)
        otherDF.replace([np.inf, -np.inf], 0.0, inplace=True)
        otherDF.fillna(value=0.0,inplace=True)
        
        if TimeKind in otherDF.columns :
            otherDF.drop( columns=[TimeKind] , inplace=True)
        dictOfDF[SimResultObjects[obj]] = diffDF * 0.0 + otherDF
        dictOfDF[SimResultObjects[obj]].dropna(axis=0 , inplace=True)
        # MotherDF = dictOfDF[SimResultObjects[obj]].mean(axis=0,skipna=True)
        # DotherDF = MotherDF - dictOfDF[SimResultObjects[obj]]
        
        ZotherDF = otherDF - otherDF.mean(axis=0,skipna=True)
        ZotherDF = ZotherDF / ZotherDF.std(axis=0,skipna=True)
        deltaDF = ZotherDF - ZbaseDF
        deltaDF.dropna(axis=0 , inplace=True)
        inputDF = diffDF * 0.0 + otherDF
        inputDF.dropna(axis=0 , inplace=True)
        dictOfDF[SimResultObjects[obj]] = inputDF.copy()
        diffDF = diffDF + deltaDF * ZdivDF
        diffDF.dropna(axis=0 , inplace=True)
        sumDF = sumDF + deltaDF * ZdivDF
        sumDF.dropna(axis=0 , inplace=True)

    verbose( verbosity , -1 , ' < StdError >  resulting total StandardError is: ' + str( sumDF.mean(axis=1).mean(axis=0) ) )
    return ( abs(sumDF).mean(axis=1,skipna=True).mean(axis=0,skipna=True) , abs(sumDF).mean(axis=0,skipna=True) , pd.DataFrame(data=abs(sumDF).mean(axis=1,skipna=True),index=abs(sumDF).index,columns=['StandardError']) , sumDF , dictOfDF ) 


def MinMaxScaledDifference( SimResultObjects=[] , AttributesOrKeys=[] , TimeSteps=None , Interpolate=False ) :
    """
    Calculates the square difference of two or more SimResults objects.
    Return a tuple containing :
        the mean of the absolute normalized differences
        the partial mean of the absolute normalized differences forevery key
        the profile of the absolut normalized differences
        the DataFrame of the absolut normalized differences for every matching keys
        the DataFrame of the normalized differences for every matching keys
        a dictionary with all the produced DataFrames
        
    Parameters: 
        SimResultObjects is a list of the objects to opetate with.
        Usually only two objects are passed but could be more than two,
        in which case all the other objects will be compared to the
        first object and the total summation returned.
            SimResultObjects=[Results1 , Results2] where Results1 
            and Results2 are SimResult objects
            
            MinMaxDiff = Sum( sqrt( Resutls_1 ^2 - Results_i ^2 ) )
            
        AttributesOrKeys is a list of attributes or keys to compare. 
            The attributes or keys must exist in both SimResult objects.
            If a well, group or region attribute is requested all the 
            corresponding and matching keys will be used.
            i.e:
                FOPT, WBHP, GGPR, RPPO are attributes 
                but WBHP:W1, RPPO:1, GGPR:G1 are keys
                the attibute WBHP will generate the key WBHP:W1 
                and any other matching wells 
        TimeSteps is the list or array of timesteps to be compared. 
            If empty all the coinciding TimeSteps will be calculated.
        Interpolate set to True allows the function to interpolate the 
            TimeSteps not matching both SimResult objects.
    """
    MatchingKeys = []
    # MatchingTimes = []
    Atts = []
    TimeKind = 'TIME'
    verbosity = SimResultObjects[0].get_Verbosity()
    verbose( verbosity , 1 , ' < MinMaxDiff > sarting with verbosity set to ' + str(verbosity))
    
    verbose( verbosity , 1 , ' < MinMaxDiff > the following objects will be used:')
    if verbosity > 0 :
        for obj in SimResultObjects :
            verbose( verbosity , 1 , ' < MinMaxDiff > ' + str( obj.get_Name() ))
        
    
    # split keys from attributes
    verbose( verbosity , 1 , ' < MinMaxDiff > checking AttributesOrKeys list:')
    verbose( verbosity , 0 , ' < MinMaxDiff >   Keys          Attributes')
    
    if type(AttributesOrKeys) == str :
        AttributesOrKeys = [AttributesOrKeys]
    for each in AttributesOrKeys :
        if ':' in each :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < MinMaxDiff >   ' + each.strip() )
        elif each.strip()[0] == 'W' or each.strip()[0] == 'G' or each.strip()[0] == 'R' :
            Atts.append(each.strip())
            verbose( verbosity , 0 , ' < MinMaxDiff >                 ' + each.strip() )
        else :
            MatchingKeys.append(each.strip())
            verbose( verbosity , 0 , ' < MinMaxDiff >   ' + each.strip() )
    verbose( verbosity , 1 , ' < MinMaxDiff > found ' + str(len(MatchingKeys)) + ' Keys and ' + str(len(Atts)) + ' Attributes,')
    
    # extract the keys corresponding to the attributes
    for obj in SimResultObjects :
        for Att in Atts :
            MatchingKeys += list( obj.get_Keys(pattern=str(Att)+':*' ) )
    Atts=None
    
    # eliminate duplicated keys
    MatchingKeys = list( set( MatchingKeys ) )
    
    # keep only keys matching all the objects and 
    for obj in SimResultObjects :
        MatchingKeys = list( set(MatchingKeys).intersection(set( obj.get_Keys() )) )
    verbose( verbosity , 1 , ' < MinMaxDiff > totalizing ' + str(len(MatchingKeys)) + ' Keys after extending the Attributes and removing duplicates.')

    if TimeSteps is None :
        verbose( verbosity , 1 , ' < MinMaxDiff > TimeSteps not received, all the matching timesteps will be used.')
        TimeSteps = list()
        for obj in SimResultObjects :
            verbose( verbosity , 0 , ' < MinMaxDiff > getting TimeSteps from ' + str(obj.get_Name()) + '\n < MinMaxDiff > extracted ' + str(len( list( obj.get_Vector( TimeKind )[ TimeKind ] ))) + ' ' + TimeKind + '.' )
            TimeSteps += list( obj.get_Vector( TimeKind )[ TimeKind ] )
        verbose( verbosity , 1 , ' < MinMaxDiff > ' + str(len(TimeSteps)) + ' TimeSteps found.')
        TimeSteps = list( set( TimeSteps ) )
        TimeSteps.sort()
        verbose( verbosity , 1 , ' < MinMaxDiff > ' + str(len(TimeSteps)) + ' sorted TimeSteps found.')
        if Interpolate == False :
            for obj in SimResultObjects :
                verbose( verbosity , 1 , ' < MinMaxDiff > looking for matching TimeSteps for ' + obj.get_Name() )
                TimeSteps = list( set( TimeSteps ).intersection( set( list( obj.get_Vector( TimeKind )[ TimeKind ] ) ) ) )
        verbose( verbosity , 1 , ' < MinMaxDiff > ' + str(len(TimeSteps)) + ' TimeSteps found, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
                
    else :
        verbose( verbosity , 1 , ' < MinMaxDiff > ' + str(len(TimeSteps)) + ' TimeSteps received, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
        if type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('DATES')['DATES'][0] )        :
            TimeKind = 'DATES'
        elif type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('TIME')['TIME'][0] ) :
            TimeKind = 'TIME'
        verbose( verbosity , 1 , ' < MinMaxDiff > TimeSteps found to be of type ' + TimeKind )
        if Interpolate == False :
            for obj in SimResultObjects :
                TimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) > 0 :
                verbose( verbosity , 1 , ' < MinMaxDiff > ' + str(len(TimeSteps)) + ' TimeSteps found matching the simulation data TimeSteps, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
            else :
                verbose( verbosity , 2 , ' < MinMaxDiff > ' + 'No matching TimeSteps in the input profiles.' )
        else :
            for obj in SimResultObjects :
                MatchingTimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) - len(MatchingTimeSteps) > 0 :
                verbose( verbosity , 2 , ' < MinMaxDiff > WARNING: data will be interpolated for ' + str( len(TimeSteps) - len(MatchingTimeSteps) ) + ' TimeSteps not found in the simulation results.\n < MinMaxDiff > WARNING: Set Interpolate=False to avoid this behaviour.' )
    
    # remove the index from the list of keys:
    if TimeKind in MatchingKeys :
        # removed = MatchingKeys.pop(MatchingKeys.index(TimeKind))
        verbose( SimResultObjects[0].speak , 1 , ' ' + str( MatchingKeys.pop(MatchingKeys.index(TimeKind)) ) + ' used ad index of the dataframe.')
    
    # calculate differences:
    # request base DataFrame:
    verbose( verbosity , 1 , ' < MinMaxDiff >  prepating the Pandas DataFrames, please wait...')
    baseDF = SimResultObjects[0].get_DataFrame( Keys=MatchingKeys , Index=TimeKind )
    baseDF.replace([SimResultObjects[0].null], np.nan, inplace=True )
    baseDF.interpolate(axis=0,inplace=True)
    baseDF.replace([np.inf, -np.inf], 0.0, inplace=True)
    baseDF.fillna(value=0.0,inplace=True)



    # prepare summation DataFrame fill with zeros
    sumDF = {}
    for each in MatchingKeys :
        sumDF[each] = [0]*len(TimeSteps)
    sumDF = pd.DataFrame( data=sumDF , index=TimeSteps )
    # prepare differences DataFrame fill with zeros
    diffDF = {}
    for each in MatchingKeys :
        diffDF[each] = [0]*len(TimeSteps)
    diffDF = pd.DataFrame( data=diffDF , index=TimeSteps )  
    
    dictOfDF = {}
    dictOfDF[SimResultObjects[0]] = (diffDF + baseDF).dropna(axis=0 , inplace=False) 
    
    MinDF = dictOfDF[SimResultObjects[0]].min(axis=0,skipna=True)
    MaxMinDF = ( dictOfDF[SimResultObjects[0]].max(axis=0,skipna=True) - MinDF )

    MdivDF = 1.0/MaxMinDF
    MdivDF.fillna(value=0.0,inplace=True)
    MdivDF.replace([np.inf, -np.inf], 0.0, inplace=True)
    
    MbaseDF = ( dictOfDF[SimResultObjects[0]] - MinDF ) * MdivDF
    
    # calculate every difference and add it to the sumDF
    for obj in range(1, len(SimResultObjects)) :
        # using DataFrame with units converted to first DataFrame 
        otherDF = SimResultObjects[obj].get_ConvertedDataFrame( Keys=MatchingKeys , Index=TimeKind , OtherObject_or_NewUnits=SimResultObjects[0] ) 
        otherDF.replace([SimResultObjects[obj].null], np.nan, inplace=True )
        otherDF.interpolate(axis=0,inplace=True)
        otherDF.replace([np.inf, -np.inf], 0.0, inplace=True)
        otherDF.fillna(value=0.0,inplace=True)
        
        if TimeKind in otherDF.columns :
            otherDF.drop( columns=[TimeKind] , inplace=True)
        
        dictOfDF[SimResultObjects[obj]] = diffDF * 0.0 + otherDF
        dictOfDF[SimResultObjects[obj]].dropna(axis=0 , inplace=True)
        
        MotherDF = ( dictOfDF[SimResultObjects[obj]] - MinDF ) * MdivDF
        deltaDF = ( MotherDF - MbaseDF )
        deltaDF.dropna(axis=0 , inplace=True)

        sumDF = sumDF + deltaDF
        sumDF.dropna(axis=0 , inplace=True)

    verbose( verbosity , -1 , ' < MinMaxDiff >  resulting total MinMaxScaledDifference is: ' + str( abs(sumDF).mean(axis=1).mean(axis=0) ) )
    return ( abs(sumDF).mean(axis=1,skipna=True).mean(axis=0,skipna=True) , abs(sumDF).mean(axis=0,skipna=True) , pd.DataFrame(data=abs(sumDF).mean(axis=1,skipna=True),index=abs(sumDF).index,columns=['MinMaxScaledDifference']) , sumDF , dictOfDF ) 


def loadSimulationResults(FullPath=None,Simulator=None) :
    """
    Loads the results of reservoir simulation into and SimuResult object.
    This library can read:
        .SSS files from VIP simulator
        .SMSPEC files from Eclipse, Intersect or tNavigator
    """
    if FullPath is None :
        print( 'Please provide the path to the simulation results as string.')
        return None
    if Simulator is None :
        if extension(FullPath)[1].upper() in ['.SMSPEC','.UNSMRY','.DATA'] :
            Simulator = 'ECLIPSE'
        elif extension(FullPath)[1].upper() in ['.DAT','.SSS'] :
            Simulator = 'VIP'
        elif extension(FullPath)[1].upper() in ['.FSC','.SS_FIELD','.SS_WELLS','.SS_REGIONS','.SS_NETWORK'] :
            Simulator = 'NEXUS'
    elif type(Simulator) is str and len(Simulator.strip()) > 0 :
        Simulator = Simulator.strip().upper()

    
    if Simulator in ['ECL','E100','E300','ECLIPSE','IX','INTERSECT','TNAV','TNAVIGATOR'] :
        return ECL(FullPath,3)
    if Simulator in ['VIP'] :
        return VIP(FullPath,3)
    if Simulator in ['NX','NEXUS']:
        return VIP(FullPath,3)

def is_SimulationResult(obj) :
    return 'SimulationResults.' in str(type(obj)) 

def mainKey(Key) :
    if type(Key) is str:
        if len(Key.strip()) > 0 :
            return Key.strip().split(':')[0]
        else :
            return None
    if type(Key) is list or type(Key) is tuple :
        results = []
        for K in Key :
            results.append( mainKey(K) )
        return list(set(results))

def regexMatch():
    pass

class SimResult(object):
    """       ___________________________________
    <<< HELP of Simulation Result Objects >>>
    
     0) Basic Concepts:
         The results of the simulation are loaded in this object.
         To access the results, the Keys or Attributes (in eclipse style) 
         must be provided as string:
             Key are the eclipse keywords for a especific vectors, i.e.:
                 'FOIP'
                 'WWPR:WELL-X'
                 'GOPR:GROUP1'
                 'RPRH:1'
            Attributes are the root of the keyword, this will return all the
            keywords matching this root, i.e.:
                'WOPR'
                'GGIT'
                'ROIP'
    
     1) Simple Use:
      A) Calling the ObjectVariable:
            In: ObjectVariable( Key , Index )
            
        -> Calling the object with no argument will return this help. i.e.:
            In: ObjectVariable()
                   ___________________________________
                <<< HELP of Simulation Result Objects >>>
                
        -> Calling the object with a string (a single key) as Key argument will 
           return a Numpy array of the requested key. 
           The Index argument is ignored in this case, i.e.:
            In: ObjectVariable( 'FOIP' ) 
            Out: 
            array([69170384., 69170384., 69170384., ..., 30077594., 30077594., 30069462.])
        
        -> Calling the object with a list (one or multiple keys) as Key argument
           will return a Pandas DataFrame.
           The Index argument is 'TIME' by default but any other key can be 
           selected as index, i.e.:
            In: ObjectVariable( [ 'FOIP' , 'FOPT' ] , 'DATE' )
            Out: 
                                       FOIP        FOPT
            1996-05-04 00:00:00  69170384.0         0.0
            1996-05-07 03:36:00  69170384.0         0.0
                                    ...         ...
            2043-12-11 00:00:00  30077594.0  41477948.0
            2043-12-31 00:00:00  30069462.0  41483604.0
            
      B) Selection like Pandas DataFrame:
         The vectors can be requested to the SimulationResult object in the 
         same way columns are selected from a Pandas DataFrame, i.e.:
             
           > a single Key between single square braket 
           [ Key ] returns a Pandas Series with the column Key, i.e. : 
            In: ObjectVariable[ 'FOPR' ]
            Out:
            0.00          0.000000
            3.15          0.000000
                           ...
            17387.00    286.179718
            17407.00    281.440918
            Name: FOPR, Length: 7692, dtype: float64
            
           > one or multiple Key or Attributes* between double square braket 
           [[ Key , Attribute ]] returns a Pandas DataFrame, i.e. : 
            In: ObjectVariable[[ 'FOPR' , 'WOPR' ]]
            Out:
                            FOPR      WOPR:W_1  ...    WOPR:W_n-1      WOPR:W_n
            0.00        0.000000           0.0  ...           0.0           0.0
            3.15        0.000000           0.0  ...           0.0           0.0
                         ...           ...  ...           ...           ...
            17387.00  286.179718           0.0  ...           0.0           0.0
            17407.00  281.440918           0.0  ...           0.0           0.0
            
            [7692 rows x 141 columns]
            
           * Notice that providing an Attribute will return all the Keys related
           to that Attribute.
        
      C) It is possible to change the default Index  with the .set_index() method.
         By default the index is the 'TIME' series.
         Other useful indexes could be 'DATE' or the cumulatives like 'FOPT'.
         Any Key can be used as index, but keep in mind the phisical or numerical
         meaning and consistency of the index you are setting.

        
        
        
    
     2) Available Methods:
        .describe
            returns a descriptive dataframe of this object content, i.e.:
                In: ObjectVariable.describe
                Out:
                              time        dates kind   keys attributes wells groups regions
                    count   7692.0         7692  ECL  19726        442   140     12      30
                    min        0.0  04-MAY-1996                                            
                    max    17407.0  31-DEC-2043                                            
                                        
        .get_Vector( list_of_keywords )
            returns a dictionary with the Numpy arrays for the requested 
            keywords, i.e.:
                In: ObjectVariable.get_Vector( [ 'FOIP' , 'FOPT' , 'FOPR' ] )
                Out:
                    {'FOPR': array([  0.        ,   0.        ,   0.        , ..., 282.94104004, 282.04125977, 281.44091797]),
                     'FOPT': array([       0.,        0.,        0., ..., 41480784., 41482196., 41483604.]),
                     'FOIP': array([69170384., 69170384., 69170384., ..., 30077594., 30077594., 30069462.])}
        
        .set_Vector( Key , VectorData , Units , DataType='auto' , overwrite=None)
            loads a vector into the SimulationResult object, arguments are:
                Key : the name or keyword where the data will be loaded
                VectorData : a Numpy array (of the same lenght as the arrays already in the results)
                Units : a string indicating the units of these data
                DataType : the strings 'float', 'int', 'date' or 'auto'
                overwrite : True or False, if True any existing data under the same Key will be overwritten. 

        .get_DataFrame( list_of_keywords , optional index )
            returns a Pandas DataFrame with the requested keywords. 
            The optional argument Index can be used to obtain a DataFrame 
            indexed by any other Key from the simulation, default index 
            is 'TIME' but 'DATE', volume in place or cumulatives can be 
            good examples of other useful indexes. i.e.:
                In: ObjectVariable.get_DataFrame( [ 'WOPR:W1','WOPT:W1' ] , 'DATE' )
                Out:
                                          WOPT:W1       WOPR:W1
                1996-05-04 00:00:00           0.0           0.0
                1996-05-07 03:36:00           0.0           0.0
                                          ...           ...
                2043-12-11 00:00:00     6499611.0           0.0
                2043-12-31 00:00:00     6499611.0           0.0
                                    
                In: ObjectVariable.get_DataFrame( [ 'WOPR:W1','WOPR:W2' ] , 'FOPT' )
                Out:
                                 WOPT:W1       WOPT:W2
                0.0                  0.0         0.000
                0.0                  0.0         0.000
                                 ...           ...
                41477948.0     6499611.0   1918401.625
                41483604.0     6499611.0   1918401.625
                
        .get_Unit( keyword_as_string or list_of_keywords ) 
            if the argument is a string (a single keyword), 
            returns the units of that keyword as a strinG, i.e.:
                In: ObjectVariable.get_Unit('FOPT')
                Out: 'SM3'
                
            if the argument is a list (one or multiple keywords), returns 
            a dictionary containg the units of that keywords as a strings.
                In: ObjectVariable.get_Unit(['FOPT','FOPR'])
                {'FOPT': 'SM3', 'FOPR': 'SM3/DAY'}
            
            if no argument is provided, returns a dictionary with all the 
            units defined in the simulation results, i.e.:
                In: ObjectVariable.get_Unit()
                Out: {'FOPT': 'SM3', 'FOPR': 'SM3/DAY', ...}
            
            
    """
    
    UniversalKeys = ( 'DATE','DATES','TIME','DAY','DAYS','MONTH','MONTHS','YEAR','YEARS')
    
    VIP2ECLkey = dictionaries.VIP2ECLkey
    ECL2VIPkey = {}
    for each in VIP2ECLkey :
        ECL2VIPkey[VIP2ECLkey[each]] = each

    VIP2ECLtype = dictionaries.VIP2ECLtype
    ECL2VIPtype = {}
    for each in VIP2ECLtype :
        ECL2VIPtype[VIP2ECLtype[each]] = each
        
    VIPnotECL = []
    
    VIPTypesToExtractVectors = ( 'FIELD' , 'WELL' , 'AREA', 'REGION' )
    KnownCSVsections = ( '[S3INFO]' , '[HEADERS]' , '[DATA]' )
    CSV_Variable2Verbose = {}
    CSV_Verbose2Variable = {}
    
    CSV2ECLkey = dictionaries.CSV2ECLkey
    ECL2CSVkey = {}
    for each in CSV2ECLkey :
        ECL2CSVkey[CSV2ECLkey[each]] = each
    CSV2ECLtype = dictionaries.CSV2ECLtype
    ECL2CSVtype = {}
    for each in CSV2ECLtype :
        ECL2CSVtype[CSV2ECLtype[each]] = each
     
    VIP2CSVkey = dictionaries.VIP2CSVkey
    CSV2VIPkey = {}
    for each in VIP2CSVkey :
        CSV2VIPkey[VIP2CSVkey[each]] = each
    
    def testECLmolarKey(key) :
        if '_' in key :
            if ':' in key :
                var = key.strip().split(':')[0].upper()
                clss = var[0]
                var = var[1:]
                member = key.strip().split(':')[1].upper()
            else :
                member = ''
                var = key.strip().upper()
                clss = var[0]
                var = var[1:]
            if '_' in var :
                comp = var[var.index('_'):]
            else :
                return False
            try :
                comp = int(comp)
            except :
                return False
            if var[0] in ('X','Y','Z') :
                xyz = var[0]
            elif var[0] == 'C' :
                xyz = ''
                if var[var.index('_')-1] == 'R' :
                    xyz = 'Q'
                elif var[var.index('_')-1] == 'T' :
                    xyz = 'C'
                else:
                    return False
                if var[var.index('_')-2] in ( 'P','I' ) :
                    pi = var[var.index('_')-2]
                else :
                    return False
            else :
                return False
            if clss in SimResult.ECL2VIPtype :
                clss = SimResult.ECL2VIPtype[clss]
            else :
                return False
            VIPkey = xyz + str(comp) + pi
            return ( VIPkey , clss , member )
        else :
            return False
        
    def testCSVmolarKey(variableORkey,CLASStype=None,MEMBER=None) :
        variableORkey = variableORkey.strip().upper()
        if ':' in variableORkey :
            if MEMBER is None and len(variableORkey.split(':')[1]) > 0 :
                MEMBER = variableORkey.split(':')[1]
            variableORkey.split(':')[0]
        if variableORkey[-1] in ( 'P','I' ) :
            pi = variableORkey[-1]
        else :
            return False
        if variableORkey[0] in ('X','Y','Z') :
            xyz = variableORkey[0]
            rt = 'MF'
            pi = ''
        elif variableORkey[0] == 'Q' :
            rt = 'R'
            xyz = 'CM'
        elif variableORkey[0] == 'C' :
            rt = 'T'
            xyz = 'CM'
        else :
            return False
        
        comp = variableORkey[1:-1]
        try :
            comp = int(comp)
        except :
            return False
               
        if CLASStype != None and CLASStype in SimResult.CSV2ECLtype[CLASStype] :
            keyType = SimResult.CSV2ECLtype[CLASStype] 
        else :
            return False
        if MEMBER is None :
            MEMBER = ''
        if MEMBER != None and MEMBER != 'FIELD':
            MEMBER = ':' + MEMBER.upper()
        elif CLASStype != None and MEMBER == 'FIELD' :
            keyType = 'F'
        
        ECLkey = keyType + xyz + rt + pi + '_' + str(comp)
        return ECLkey
        
    def fromECLtoVIP(self,key) :
        verbose( self.speak , 1 , 'translating ' + str(key) + ' from ECL to VIP style.')
        test = SimResult.testECLmolarKey(key)
        if type(test) == tuple :
            return test[0] , test[1] , test[2]
        
        key = key.strip().upper()
        if ':' in key :
            keyName = key[key.index(':')+1:]
            keyRoot = key[:key.index(':')]
            keyType = 'W'
            if keyRoot in SimResult.UniversalKeys :
                keyType = 'W'
            else :
                keyType = keyRoot[0]
                keyRoot = keyRoot[1:]
            if keyRoot in ( 'BHP' , 'THP' ) :
                keyType = 'W'
            if keyType == 'F' :
                keyName = 'ROOT'
            if keyType != '' and keyType in SimResult.ECL2VIPtype :
                keyType = SimResult.ECL2VIPtype[keyType]
            if keyRoot in SimResult.ECL2VIPkey :
                VIPkey = SimResult.ECL2VIPkey[keyRoot]
            else :
                VIPkey = keyRoot
        else :
            keyName = 'ROOT'
            keyRoot = key
            keyType = key[0]
            if keyRoot in SimResult.UniversalKeys :
                keyType = 'F'
            else :
                keyType = keyRoot[0]
                keyRoot = keyRoot[1:]
            if keyRoot in ( 'BHP' , 'THP' ) :
                keyType = 'W'
                keyName = ''
            if keyType == 'F' :
                keyName = 'ROOT'
            if keyType != '' and keyType in SimResult.ECL2VIPtype :
                keyType = SimResult.ECL2VIPtype[keyType]
            if keyRoot in SimResult.ECL2VIPkey :
                VIPkey = SimResult.ECL2VIPkey[keyRoot]
            else :
                VIPkey = keyRoot

        verbose( self.speak , 1 ,'ECLIPSE key ' + key + ' interpreted as VIP key ' + VIPkey + ' for ' + str(keyType) + ' summary for the item ' + keyName )
        return VIPkey , keyType , keyName

    def mainKey(self,Key) :
        if type(Key) is str:
            if len(Key.strip()) > 0 :
                return Key.strip().split(':')[0]
            else :
                return None
        if type(Key) is list or type(Key) is tuple :
            results = []
            for K in Key :
                results.append( self.mainKey(K) )
            return list(set(results))
    
    def fromVIPtoECL(self,key,SSStype=None):
        if SSStype != None :
            S = ' of ' + str(SSStype)
        else :
            S = ''
        verbose( self.speak , 1 , 'translating ' + str(key) + S + ' from VIP to ECL style.')
        key = key.strip().upper()
        if ':' in key :
            keyName = key[key.index(':')+1:]
            keyRoot = key[:key.index(':')]
            keyType = 'W'
            ConvertedRoot = keyRoot
            if keyRoot in SimResult.VIP2ECLkey :
                ConvertedRoot = SimResult.VIP2ECLkey[ keyRoot ]  
            if keyRoot in ( 'BHP' , 'THP' , 'AVG PRES' ) :
                keyType = 'W'
            if keyName == 'ROOT' :
                keyType = 'F'
                keyName = ''
            else :
                keyName = ':' + keyName
            if SSStype != None and SSStype in SimResult.VIP2ECLtype :
                keyType = SimResult.VIP2ECLtype[SSStype]
            if keyRoot in SimResult.UniversalKeys :
                keyType = ''
        else :
            keyName = ''
            keyRoot = key
            keyType = 'F'
            ConvertedRoot = keyRoot
            if keyRoot in SimResult.VIP2ECLkey :
                ConvertedRoot = SimResult.VIP2ECLkey[ keyRoot ] 
            if key in ( 'BHP' , 'THP' , 'AVG PRES' ) :
                keyType = 'W'
            if key in SimResult.VIP2ECLkey :
                keyRoot = SimResult.VIP2ECLkey[key]
            if SSStype != None and SSStype in SimResult.VIP2ECLtype :
                keyType = SimResult.VIP2ECLtype[SSStype]
            if keyRoot in SimResult.UniversalKeys :
                keyType = ''
   
        if keyRoot == '' :
            verbose( self.speak , 1 ,'CSV variable ' + key + ' not converted to ECL key.' )
            return None
        ECLkey = keyType + ConvertedRoot + keyName
        verbose( self.speak , 1 ,'VIP key ' + key + ' interpreted as ECL key ' + ECLkey )
        return ECLkey
    
    def fromCSVtoECL(self,variableORkey,CLASStype=None,MEMBER=None):
        test = SimResult.testCSVmolarKey(variableORkey,CLASStype,MEMBER)
        if type(test) == str :
            return test
        
        if CLASStype != None :
            C = ' of class ' + str(CLASStype)
        if MEMBER != None :
            M = ' for ' + str(MEMBER)
        verbose( self.speak , 1 , 'translating ' + str(variableORkey) + C + M + ' from CSV to ECL style.')
        
        keyType = None
        if CLASStype != None :
            if CLASStype in SimResult.CSV2ECLtype :
                keyType = SimResult.CSV2ECLtype[CLASStype] 

        if MEMBER != None and len(MEMBER.strip()) > 0 :
            keyName = MEMBER.strip().upper()
            if keyName in ( 'FIELD' , 'ROOT' ) :
                keyName = ''
            else :
                keyName = ':' + keyName
        else :
            keyName = None
            
        key = self.mainKey(variableORkey).upper()
        if key in SimResult.UniversalKeys :
            keyType = ''
        if key in SimResult.CSV2ECLkey :
            keyRoot = SimResult.CSV2ECLkey[key]
        else :
            keyRoot = None 
        
        verbose( self.speak , 1 , str(keyType) + ' ' + str(keyRoot) + ' ' + str(keyName) )
        if keyRoot != None and keyType != None and keyName != None :
            return keyType + keyRoot + keyName

    def fromECLtoCSV(self,key) :
        verbose( self.speak , 1 , 'translating ' + str(key) + ' from ECL to CSV style.')
        test = SimResult.testECLmolarKey(key)
        if type(test) == tuple :
            return test[0] , test[1] , test[2]
        
        key = key.strip().upper()
        if ':' in key :
            keyName = key[key.index(':')+1:]
            keyRoot = key[:key.index(':')]
            keyType = 'W'
            if keyRoot in SimResult.UniversalKeys :
                keyType = 'MISCELLANEOUS'
                keyName = ''
            else :
                keyType = keyRoot[0]
                keyRoot = keyRoot[1:]
            if keyRoot in ( 'BHP' , 'THP' ) :
                keyType = 'W'
            if keyType == 'F' :
                keyName = 'FIELD'
            if keyType != '' and keyType in SimResult.ECL2CSVtype :
                keyType = SimResult.ECL2CSVtype[keyType]
            if keyRoot in SimResult.ECL2CSVkey :
                CSVkey = SimResult.ECL2CSVkey[keyRoot]
            else :
                CSVkey = keyRoot
        else :
            keyName = 'FIELD'
            keyRoot = key
            keyType = key[0]
            if keyRoot in SimResult.UniversalKeys :
                keyType = 'MISCELLANEOUS'
                keyName = ''
            else :
                keyType = keyRoot[0]
                keyRoot = keyRoot[1:]
            if keyRoot in ( 'BHP' , 'THP' ) :
                keyType = 'W'
                keyName = ''
            if keyType == 'F' :
                keyName = 'FIELD'
            if keyType != '' and keyType in SimResult.ECL2CSVtype :
                keyType = SimResult.ECL2CSVtype[keyType]
            if keyRoot in SimResult.ECL2CSVkey :
                CSVkey = SimResult.ECL2CSVkey[keyRoot]
            else :
                CSVkey = keyRoot

        verbose( self.speak , 1 ,'ECLIPSE key ' + key + ' interpreted as CSV key ' + CSVkey + ' for ' + str(keyType) + ' summary for the item ' + keyName )
        return CSVkey , keyType , keyName


    
    def writeCSVtoPandas(self,CSVFilePath):
        if self.path is None :
            self.path = CSVFilePath
        with open(CSVFilePath,'r') as CSVfile:
            PandasCSV = open( extension(CSVFilePath)[2] + extension(CSVFilePath)[0] + '_forPandas' + extension(CSVFilePath)[1] , 'w' )
            CSVlines = CSVfile.readlines()
            DATA = False
            HEADERS = False
            for line in CSVlines :
                if not HEADERS :
                    if line.split(',')[0] == "['HEADERS']" :
                        print('found HEADERS')
                        HEADERS = True
                else :
                    lineData = line.split(',')
                    if line.split()[0] == "['DATA']" :
                        print('found DATA')
                        DATA = True
                        HEADERS = False
                        
                        for i in range( len( self.pandasColumns['HEADERS']['VARIABLE'] ) ):
                            fullName = []
                            for head in list(self.pandasColumns['HEADERS'].keys()) :
                                fullName.append( self.pandasColumns['HEADERS'][head][i] )
                            self.pandasColumns['COLUMNS'][':'.join(fullName)] = fullName
                        
                        PandasHead = ','.join(list( self.pandasColumns['COLUMNS'].keys() ))
                        PandasCSV.write( PandasHead + '\n' )

                    else :
                        self.pandasColumns['HEADERS'][ lineData[0].split(':')[0] ] = [ lineData[0].split(':')[1] ] + lineData[1:]
                        print( 'reading header ' + str( lineData[0].split(':')[0] ))

                if not DATA :
                    if line.split()[0] == "['DATA']" :
                        print('found DATA')
                        DATA = True
                else :
                    PandasCSV.write( line )
            PandasCSV.close()
                             
        
    def __init__(self,verbosity=3) :
        self.set_Verbosity(verbosity)
        self.SimResult = True
        self.kind = None
        self.results = None
        self.name = None
        self.path = None
        self.start = None
        self.end = None
        self.wells = tuple()
        self.groups = tuple()
        self.regions = tuple()
        self.keys = tuple()
        self.attributes = {}
        self.vectors = {}
        self.units = {}
        self.overwrite = False
        self.null = None
        self.plotUnits = {}
        self.color = ( random.random() , random.random() , random.random() )
        self.keyColors = {}
        self.colorGrouping = 6
        self.DTindex = 'TIME'
        self.restarts = []
        self.vectorsRestart = {}
        self.pandasColumns = { 'HEADERS' : {} , 'COLUMNS' : {} , 'DATA' : {} }
        self.fieldtime = ( None , None , None ) 
    
    def __call__(self,Key=None,Index=None) :
        if Index is None :
            Index = self.DTindex
        if Key is not None :
            if type(Key) is list and len(Key) > 0:
                return self.get_DataFrame(Key,Index)
            elif type(Key) == str and len(Key) > 0 :
                return self.get_Vector(Key)[Key]
        else :
            print( SimResult.__doc__ )
    
    def __getitem__(self, item) :
        if type(item) is tuple :
            pass # what to do with the tupple?
        if type(item) is str :
            return self.__call__([item])[item]
        if type(item) is list :
            cols = []
            for each in item :
                if self.is_Key(each) :
                    cols.append(each)
                elif each in self.attributes :
                    cols += self.attributes[each]
            return self.__call__(cols)
    
    def __len__(self) :
        """
        return the number of keys * number of time steps in the dataset
        """
        return self.len_Keys() * self.len_tSteps()
    
    def __str__(self) :
        return self.name
    
    @property
    def describe(self) :
        # # calling the describe method from pandas for the entire dataframe is very intensive (huge dataframe)
        # describeKeys = list(set(self.keys))
        # describeKeys.sort()
        # return self[describeKeys].describe()
        if 'ECL' in str(self.kind) :
            kind = 'ECL'
        elif 'VIP' in str(self.kind) :
            kind = 'VIP'
        desc = {}
        Index = ['count','min','max']
        desc['time'] = [ self.len_tSteps() , self.fieldtime[0] , self.fieldtime[1] ]
        desc['dates'] = [ len(self('DATE')) , strDate(min(self('DATE')),speak=False)  , strDate(max(self('DATE')),speak=False) ]
        desc['kind'] = [ kind , '' , '' ]
        desc['keys'] = [ len(self.keys) , '' , '' ]
        desc['attributes'] = [ len(self.attributes) , '' , '' ]
        desc['wells'] = [ len(self.wells) , '' , '' ]
        desc['groups'] = [ len(self.groups) , '' , '' ]
        desc['regions'] = [ len(self.regions), '' , '' ]
        return pd.DataFrame( data=desc , index=Index)
    
    def set_index(self,Key) :
        self.set_Index(Key)
    def set_Index(self,Key) :
        if self.is_Key(Key) :
            self.DTindex = Key
    def get_Index(self) :
        return self.DTindex
    
    def set_plotUnits(self,UnitSystem_or_CustomUnitsDictionary='FIELD') :
        if type(UnitSystem_or_CustomUnitsDictionary) is str :
            if UnitSystem_or_CustomUnitsDictionary.upper() in ['F','FIELD'] :
                self.plotUnits = dict(dictionaries.unitsFIELD)
            elif UnitSystem_or_CustomUnitsDictionary.upper() in ['M','METRIC','METRICS'] :
                self.plotUnits = dict(dictionaries.unitsMETRIC)
            elif UnitSystem_or_CustomUnitsDictionary.upper() in ['ORIGINAL'] :
                self.plotUnits = {}
            else :
                print('unit system not recognized, please select FIELD, METRIC or ORIGINAL')

        elif type(UnitSystem_or_CustomUnitsDictionary) is dict :
            for Key in UnitSystem_or_CustomUnitsDictionary :
                if type(Key) is str and type(UnitSystem_or_CustomUnitsDictionary[Key]) is str : 
                    if self.is_Key(Key) :
                        if convertibleUnits( self.get_Unit(Key) , UnitSystem_or_CustomUnitsDictionary[Key] ) :
                            self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                        else :
                            verbose(self.speak , 3 , "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'." )
                    else :
                        verbose(self.speak , 2 , "the key '" + Key + "' can't be found in this simulation." )
                        matchedKeys = []
                        if Key in self.get_Attributes() :
                            # for Att in self.get_Attributes() :
                                # if Key in Att :
                            matchedKeys += self.attributes[Key]
                        if len(matchedKeys) == 0 :
                            verbose(self.speak , 3 , "the key '" + Key + "' does not match any attribute in this simulation." )
                        elif len(matchedKeys) == 1 :
                            if convertibleUnits( self.get_Unit(matchedKeys[0]) , UnitSystem_or_CustomUnitsDictionary[Key] ) :
                                self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                            else :
                                verbose(self.speak , 3 , "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'." )
                            verbose(self.speak , 1 , "the key '" + Key + "' matches one attribute in this simulation:\n"+str(matchedKeys) )
                        else :
                            mainKs = self.mainKey( matchedKeys )
                            if len(mainKs) == 1 :
                                if convertibleUnits( self.get_Unit(matchedKeys[0]) , UnitSystem_or_CustomUnitsDictionary[Key] ) :
                                    self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                                else :
                                    verbose(self.speak , 3 , "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'." )
                                verbose(self.speak , 1 , "the key '" + Key + "' matches " + str(len(matchedKeys)) + " attribute in this simulation:\n"+str(matchedKeys) )
                            else :
                                if convertibleUnits( self.get_Unit(matchedKeys[0]) , UnitSystem_or_CustomUnitsDictionary[Key] ) :
                                    self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                                else :
                                    verbose(self.speak , 3 , "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'." )
                                verbose(self.speak , 1 , "the key '" + Key + "' matches " + str(len(mainKs)) + " attribute in this simulation:\n"+str(matchedKeys) )
        else  :
            print(' Argument missing.\n Please select "FIELD", "METRIC" or "ORIGINAL" or provide a dictionary with the custom units set.')
        
    def get_plotUnits(self,Key=dict) :
        return self.get_plotUnit(Key)
    
    def get_plotUnit(self,Key=dict) :
        if Key is dict :
            return self.plotUnits
        if type(Key) is str :
            if Key in self.plotUnits :
                return self.plotUnits[Key]
            else :
                matchingKeys = []
                for K in self.plotUnits.keys():
                    if K in Key :
                        matchingKeys.append(K)
                if len(matchingKeys) == 0 :
                    return self.get_Unit(Key)
                elif len(matchingKeys) == 1 :
                    return self.plotUnits[matchingKeys[0]]
                else :
                    MK = ''
                    MM = []
                    for K in matchingKeys :
                        if len(K) > len(MK) :
                            MK = K
                            MM = [K]
                        elif len(K) == len(MK) :
                            MM.append(K)
                    if len(MM) == 1 :
                        return self.plotUnits[MK]
                    else :
                        for M in MM :
                            if convertibleUnits( self.get_Unit(Key) , self.plotUnits[M] ) :
                                return self.plotUnits[M]

    def get_Units(self,Key='--EveryType--') :
        return self.get_Unit(Key)

    def len_Wells(self) :
        """
        return the number of wells in the dataset
        """
        return len(self.get_Wells())
    
    def len_Groups(self) :
        """
        return the number of groups in the dataset
        """
        return len(self.get_Groups())
    
    def len_Keys(self) :
        """
        return the number of keys in the dataset
        """
        return len(self.get_Keys())
    
    def len_tSteps(self) :
        """
        return the number of timesteps in the dataset
        """
        keys = ( 'TIME' , 'DATE' , 'DATES' )
        for key in keys :
            if self.is_Key(key) :
                return len(self.get_Vector(key)[key])
    def len_TimeSteps(self) :
        """ 
        alias for len_tSteps 
        """
        return self.len_tSteps()
    
    def plot(self,Keys=[],Index='TIME',otherSims=None,Wells=[],Groups=[],Regions=[],DoNotRepeatColors=None) :

        if type(DoNotRepeatColors) is not bool :
            UserDRC = None
        else :
            UserDRC = DoNotRepeatColors
        DoNotRepeatColors = True
        if type(Keys) is str :
            Keys = [Keys]
        if type(Wells) is str :
            Wells = [Wells]
        if type(Groups) is str :
            Groups = [Groups]
        if type(Regions) is str :
            Regions = [Regions]
        if type(Index) is list or type(Index) is tuple :
            if len(Index) > 0 :                
                if type(Index[0]) is str :
                    if len(Index) == len(Keys) :
                        pass # it is OK, there are pairs of X & Y
                    else : 
                        verbose( 1 , self.speak , ' only a single index\n or pairs of X & Y can be used to plot,\n the 0th item will used as Index.')
                        Index = Index[0]
                #elif 'SimulationResults.' in str(type(Index)) :
                elif is_SimulationResult(Index[0]) :
                    if otherSims is None :
                        otherSims, Index = Index , 'TIME'
                    elif is_SimulationResult(otherSims) :
                        otherSims, Index = list(set([ Index , otherSims ])) , 'TIME'
                    elif type(otherSims) is str :
                        otherSims, Index = Index , otherSims.stip().upper()
                    elif type(otherSims) is list or type(otherSims) is tuple :
                        if is_SimulationResult(otherSims[0]) :
                            otherSims, Index = list(set([Index] + otherSims)) , 'TIME'
                        elif type(otherSims[0]) is str :
                            verbose( 1 , self.speak , 'only a single index can be used to plot, the item 0 will used.')
                            otherSims, Index = Index , otherSims[0]
                    
            else :
                Index='TIME'
        elif type(Index) is str :
            Index = Index.strip().upper()
        elif is_SimulationResult(Index) :
            if otherSims is None :
                otherSims, Index = Index , 'TIME'
            elif is_SimulationResult(otherSims) :
                otherSims, Index = list(set([ Index , otherSims ])) , 'TIME'
            elif type(otherSims) is str :
                otherSims, Index = Index , otherSims.stip().upper()
            elif type(otherSims) is list or type(otherSims) is tuple :
                if is_SimulationResult(otherSims[0]) :
                    otherSims, Index = list(set([Index] + otherSims)) , 'TIME'
                elif type(otherSims[0]) is str :
                    otherSims, Index = Index , otherSims
         
        for K in range(len(Keys)) :
            Keys[K] = Keys[K].strip()
        for W in range(len(Wells)) :
            Wells[W] = Wells[W].strip()
        for G in range(len(Groups)) :
            Groups[G] = Groups[G].strip()
        for R in range(len(Regions)) :
            Regions[R] = Regions[R].strip()

        PlotKeys = []
        for K in Keys :
            if self.is_Key(K) :
                PlotKeys.append(K)
            elif K in self.attributes :
                if K[0] == 'W' :
                    if len(Wells) == 0 :
                        items = self.attributes[K]
                        DoNotRepeatColors = False
                    else :
                        if len(Wells) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Wells)
                        for I in range(len(Wells)) :
                            items[I] = K+':'+Wells[I]
                elif K[0] == 'G' :
                    if len(Groups) == 0 :
                        items = self.attributes[K]
                        DoNotRepeatColors = False
                    else :
                        if len(Groups) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Groups)
                        for I in range(len(Groups)) :
                            items[I] = K+':'+Groups[I]
                elif K[0] == 'R' :
                    if len(Regions) == 0 :
                        items = self.attributes[K]
                        DoNotRepeatColors = False
                    else :
                        if len(Regions) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Regions)
                        for I in range(len(Regions)) :
                            items[I] = K+':'+Regions[I]
                PlotKeys += items

        if type(Index) is str :
            Index = [Index]
        IndexList = []
        for I in Index :
            if self.is_Key(I) :
                IndexList.append(I)
            elif I in self.attributes :
                if I[0] == 'W' :
                    if len(Wells) == 0 :
                        items = self.attributes[I]
                        DoNotRepeatColors = False
                    else :
                        if len(Wells) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Wells)
                        for X in range(len(Wells)) :
                            items[X] = I+':'+Wells[X]
                elif I[0] == 'G' :
                    if len(Groups) == 0 :
                        items = self.attributes[I]
                        DoNotRepeatColors = False
                    else :
                        if len(Groups) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Groups)
                        for X in range(len(Groups)) :
                            items[X] = I+':'+Groups[X]
                elif I[0] == 'R' :
                    if len(Regions) == 0 :
                        items = self.attributes[I]
                        DoNotRepeatColors = False
                    else :
                        if len(Regions) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Regions)
                        for X in range(len(Regions)) :
                            items[X] = I+':'+Regions[X]
                IndexList += items
            

        if len(IndexList) == len(PlotKeys) :
            # check consistency:
            OKflag = True
            for i in range(len(IndexList)) :
                if ':' in IndexList[i] and ':' in PlotKeys[i]:
                    if IndexList[i].split(':')[1] == PlotKeys[i].split(':')[1] :
                        pass # it is OK
                    else :
                        verbose( self.speak , 3 ," the pair '" + PlotKeys[i] + "' vs '" + IndexList[i] + "' might not be correct." )
                        OKflag = False
            
            if not OKflag and len(Keys) == len(Index) : # migt be a sorting issue
                for i in range(len(Keys)) :
                    if not self.is_Key(Keys[i]) and Keys[i] in self.attributes :
                        if not self.is_Key(Index[i]) and Index[i] in self.attributes :
                            IndexList.sort()
                            PlotKeys.sort()
                            OKflag = True
                if OKflag :
                    for i in range(len(IndexList)) :
                        if ':' in IndexList[i] and ':' in PlotKeys[i]:
                            if IndexList[i].split(':')[1] == PlotKeys[i].split(':')[1] :
                                pass # it is OK
                            else :
                                verbose( self.speak , 3 ," the pair '" + PlotKeys[i] + "' vs '" + IndexList[i] + "' might not be correct." )
                                OKflag = False
        
            if OKflag :
                verbose( self.speak , 3, ' the pairs consistency WAS corrected with sorting.')
            else :
                verbose( self.speak , 3, ' the pairs consistency was NOT corrected with sorting.')
        
        if IndexList == [] :
            if len(Index) == 1 :
                IndexList = Index[0]
            else :
                IndexList = Index
        
        if otherSims is not None :
            if is_SimulationResult(otherSims) :
                SimsToPlot = [self , otherSims]
            elif type(otherSims) is list or type(otherSims) is tuple :
                SimsToPlot = [self]
                for each in otherSims :
                    if is_SimulationResult(each) :
                        SimsToPlot += [each]
        else :
            # return self.get_DataFrame(PlotKeys,Index).plot()
            SimsToPlot = [self]

        if type(UserDRC) is bool :
            DoNotRepeatColors = UserDRC

        Plot( SimResultObjects=SimsToPlot , Y_Keys=PlotKeys ,  X_Key=IndexList , DoNotRepeatColors=DoNotRepeatColors ) #, X_Units=[], Y_Units=[] , ObjectsColors=[] , SeriesColors=[] ,  graphName='' , Y_Axis=[], Y_Scales=[] , legendLocation='best', X_Scale=[] , Labels={})
        return( PlotKeys , IndexList )
    
    def replaceNullbyNaN(self) :
        """
        replace in-situ the null value defined in self.null by numpy.nan
        """
        if self.null is not None :
            for key in list(self.vectors.keys()):
                verbose( self.speak , 1 , ' attempting to replace null value ' + str(self.null) + ' in vector ' + str(key) + '.')
                if self.vectors[key] is not None and self.null in self.vectors[key] :
                    verbose( self.speak , 2 , "the key '" + key + "' has null values " + str(self.null) )
                    try :
                        self.vectors[key][self.vectors[key]==self.null]=np.nan
                    except :
                        verbose( self.speak , 2 , ' failed to replace null value ' + str(self.null) + ' in vector ' + str(key) + '.')
    
    def copyUnits(self,other) :
        """
        copy the units from other object to this object
        """
        for key in self.units :
            if other.get_Unit(key) != None:
                self.units[key] = other.get_Unit(key)
                
    def get_aggregatedWells(self,WellsToGroup=[],WellKeys=[],AggregatedKeyName='',aggregate_by='default',force=False) :
        """
        returns vectors of WellKeys for grouped wells, aggregating their data
        according to 'aggregate_by': 'sum' or 'avg'
            by defauylt:
            rates and cumulatives are lumped
            pressures are averaged
            time or date are not aggregated
        AggregatedKeyName is a string aimed to identify the group.
        by default, the well names will be concatenated.
        """
        WellsToGroup = list( set(WellsToGroup))
        WellsToGroup.sort()
        
        returnVector = {}
        
        if type(WellKeys) == str :
            WellKeys = [WellKeys]
        
        verbose( self.speak , 1 , ' aggregating keys ' + str(WellKeys) )
        verbose( self.speak , 1 , ' aggregating wells ' + str(WellsToGroup) )
        
        if AggregatedKeyName == '' :
            for key in WellKeys :
                for well in WellsToGroup :
                    AggregatedKeyName = AggregatedKeyName + well
        
        for key in WellKeys :
            verbose( self.speak  , 1 , " < aggregating key '" + key + "' >" )
            
            KeyUnits = None
            for well in WellsToGroup :
                KeyUnits = self.get_Unit(key + ':' + well)
                if type(KeyUnits) == str and len(KeyUnits) > 0 :
                    verbose( self.speak  , 1 , " < units found to be '" + KeyUnits + "' >" )
                    break
            if KeyUnits is None :
                KeyUnits = 'dimensionless'
                verbose( self.speak  , 1 , " < units NOT found, will be set as '" + KeyUnits + "' >" )
    
            if ( aggregate_by == 'default' and KeyUnits in unit.dictionary['pressure'] ) or aggregate_by.lower() == 'avg' :
                AGG = 'AVG'
            else :
                AGG = 'SUM'
            
            
            NewKey = 'G' + key[1:]
            if AGG + 'of' + key + ':' + ','.join(WellsToGroup) in self.vectors and force == False :
                returnVector[NewKey+':'+AggregatedKeyName] = self.vectors[ AGG + 'of' + key + ':' + ','.join(WellsToGroup) ]
            elif key == 'TIME' or key == 'DATE' or key == 'DATES' :
                returnVector[key+':'+AggregatedKeyName] = self.get_Vector(key)[key]
            else :
                for well in WellsToGroup : 
                    if self.is_Key(key + ':' + well) :
                        if self.get_Vector( key + ':' + well )[ key + ':' + well ] is None :
                            print( 'no data for the key ' + str(key + ':' + well ))
                        elif len( self.get_Vector( key + ':' + well )[ key + ':' + well ] ) > 0 :
                            size = len(self.get_Vector( key + ':' + well )[ key + ':' + well ])
                            verbose( self.speak , 1 , " < inizializing sum vectr with lenght " + str(size) + " >")
                            returnVector[NewKey+':'+AggregatedKeyName] = self.get_Vector( key + ':' + well )[ key + ':' + well ] * 0.0
                            break

                counter=0
                for well in WellsToGroup :
                    verbose( self.speak , 1 , " < looking for item '" + well + "' >")
                    if self.is_Key(key + ':' + well) :
                        AddingVector = self.get_Vector( key + ':' + well )[ key + ':' + well ]
                        if AddingVector is None :
                            verbose( self.speak , 3 , " < the item '" + well + "' doesn't containt this key >")
                        else :
                            verbose( self.speak , 2 , " < adding '" + well + "' >")
                            returnVector[NewKey+':'+AggregatedKeyName] = returnVector[NewKey+':'+AggregatedKeyName] + self.get_Vector( key + ':' + well )[ key + ':' + well ]
                            counter += 1
                        
                if ( aggregate_by == 'default' and KeyUnits in unit.dictionary['pressure'] ) or aggregate_by.lower() == 'avg' : 
                    if counter > 0 :
                        verbose( -1 , 1 , " < calculating average for key '" + key + "' of well '" + WellsToGroup + "' >")
                        returnVector[NewKey+':'+AggregatedKeyName] = returnVector[NewKey+':'+AggregatedKeyName] / counter
                        AGG = 'AVG'
                if counter > 0 :
                    verbose( self.speak , 3 , ' saving vector ' + NewKey + ':' + AggregatedKeyName + ' of lenght ' + str(len(returnVector[NewKey+':'+AggregatedKeyName])))
                    self.set_Vector( AGG + 'of' + key + ':' + ','.join(WellsToGroup) , returnVector[NewKey+':'+AggregatedKeyName] , KeyUnits ,overwrite=True ) 
                    self.set_Vector( NewKey + ':' + AggregatedKeyName , returnVector[NewKey+':'+AggregatedKeyName] , KeyUnits ,overwrite=True ) 
        
        return returnVector
    
    def fillZeros(self,KeyVector,KeyTime,force=False):
        """
        Check if the KeyTime array exists on the entire range of TIME array 
        from Field and complete the corresponding KeyVector with zeros or 
        interpolation for the missing time steps.
        Returns KeyVector that exists on full range of array TIME
        """
        KeyTime = np.array(KeyTime,dtype='float')
            
        if self.fieldtime == ( None , None , None ) :
            self.set_FieldTime()
        
        if len(KeyTime) == 0 or len(KeyVector) == 0 :
            verbose(self.speak, 2 , ' <fillZeros> the received vectors are empty, thus, a zero filled vector will be returned with lenght equal to the field TIME vector.')
            return np.array([0.0]*len(self.fieldtime),dtype='float')
        
        if force == True or min(KeyTime) > self.fieldtime[0] or max(KeyTime) < self.fieldtime[1] :
            verbose(self.speak, 1 , ' <fillZeros> the received vectors starts on TIME=' + str( KeyTime[0] ) + ', it will be filled to start from TIME' + str(self.fieldtime[0]) +  '.')
            OtherDT = pd.DataFrame( data= { 'vector' : np.array(KeyVector,dtype='float') } , index= np.array(KeyTime,dtype='float') )
            FieldDT = pd.DataFrame( data= { 'vector' : np.array( [0.0]*len(self.fieldtime[2]) ) } , index= np.array(self.fieldtime[2],dtype='float') )
            CompleteDT = OtherDT + FieldDT 
            CompleteDT.interpolate(axis=0,inplace=True)
            CompleteDT.fillna(value=0.0,inplace=True)
            return CompleteDT['vector'].values
        else :
            return KeyVector
    
    def report_VIP_AttributesNotTo_ECL(self) :
        if len(SimResult.VIPnotECL) == 0 :
            print('nothing to report.')
        else :
            SimResult.VIPnotECL = list( set( SimResult.VIPnotECL ) )
            print("the following attibutes from VIP simulation couldn't be converted to ECL style attributes:")
            for each in SimResult.VIPnotECL :
                print('  ' + str(each))
    
    def set_Name(self,name):
        if type(name) == list or type(name) == tuple :
            if len(name) == 1 :
                name = name[0]
        if type(name) == str :
            self.name = name
        else :
            verbose( self.speak , 2 , ' Name should be a string'  )
            self.name = str(name)
    def get_Name(self):
        if type( self.name ) != str :
            verbose( self.speak , 3 , ' the name of ' + str(self.name) + ' is not a string.' )
            return str( self.name )
        return self.name
    
    def set_Restart(self,SimResultObject):
        if type( SimResultObject ) == list :
            self.restarts = self.restarts + SimResultObject 
        else :
            self.restarts.append(SimResultObject)
        self.restarts = list( set ( self.restarts ) )
        
        sortedR = []
        selfTi = self.checkIfLoaded('TIME',False)[0]
        # remove simulations that starts after the self
        for i in range(len(self.restarts)) :
            if self.restarts[i].get_Vector('TIME')['TIME'][0] < selfTi :
                sortedR += [self.restarts[i]]
        self.restarts = sortedR
        
        # sort simulations by start time
        for i in range(len(self.restarts)) :
            for j in range(0,len(self.restarts)-i-1) :
                if self.restarts[j].get_Vector('TIME')['TIME'][0] > self.restarts[j+1].get_Vector('TIME')['TIME'][0] :
                    self.restarts[j] , self.restarts[j+1] = self.restarts[j+1] , self.restarts[j]
                    
        self.set_FieldTime()
    
    def remove_Restart(self,SimResultObject) :
        if SimResultObject in self.restarts :
            print(" removed restart object '" + str(self.restarts.pop(SimResultObject)) + "'")
    
    def get_Restart(self):
        if self.speak in ( -1, 1 ) and len( self.restarts ) > 0 :
            string = "\n '" + self.get_Name() + "' restarts from " 
            for r in range(0,len(self.restarts)) :
                string = string + "\n   '" + self.restarts[::-1][r].get_Name() + "'"
            print( string )
        return self.restarts
    
    def set_Color(self,MatplotlibColor=None,Key=None):
        if MatplotlibColor is None :
            MatplotlibColor = ( random.random() , random.random() , random.random() )
        elif not is_color_like(MatplotlibColor) :
            verbose(self.speak,3,'the provided color code is not a correct matplotlib color' )
        if type(MatplotlibColor) is list :
           MatplotlibColor = tuple( MatplotlibColor )
        if Key is None :
            self.color = MatplotlibColor
        else :
            if self.is_Key(Key) :
                self.keyColors[Key] = MatplotlibColor
            elif Key in self.attributes :
                self.keyColors[Key] = MatplotlibColor
                    
    def get_Color(self,Key=None):
        if Key is None :
            return self.color
        elif self.is_Key(Key) :
            if Key in self.keyColors :
                return self.keyColors[Key]
            elif self.mainKey(Key) in self.keyColors :
                return self.keyColors[self.mainKey(Key)]
            else :
                return None
        elif Key in self.attributes :
            return self.keyColors[Key]
    
    def set_Verbosity(self,verbosity_level):
        try :
            self.speak = int(verbosity_level)
        except :
            if type(verbosity_level) == str and verbosity_level.upper() == 'ALL' :
                print('Verbosity set to ALL (-1), EVERY message wil be printed.')
                self.speak = -1
            elif type(verbosity_level) == str and verbosity_level.upper() == 'MUTE' :
                print('Verbosity set to MUTE (0), no message wil be printed.')
                self.speak = -1
            else :
                print('wrong set_Verbosity argument: ' + str(verbosity_level) + '\nVerbosity will be set to True (1)')
                self.speak = 1
    def get_Verbosity(self) :
        return self.speak
    
        
    def set_Start(self,startDate):
        """
        startDate must be a string representing a date or a Pandas or Numpy or datetime object
        """
        self.start = np.datetime64( pd.to_datetime( startDate ) ,'s' )
        return self.start
    
    def get_Start(self):
        """
        startDate must be a string representing a date or a Pandas or Numpy or datetime object
        """
        return self.start
    
    def is_Key(self,Key) :
        if type(Key) != str or len(Key)==0 :
            return False
        if Key in self.get_Keys() :
            return True
        else :
            return False

    def is_Att(self,Key) :
        return self.is_Attribute(Key) 
    
    def is_Attribute(self,Key) :
        if type(Key) != str :
            return False
        Key = Key.strip()
        if len(Key)==0 :
            return False
        if Key[-1] == ':' :
            Key = Key[:-1]
        if Key in self.get_Attributes() :
            return True
        else :
            return False
        
    def get_Attributes(self,pattern=None,reload=False) :
        """
        extract the attribute name from the keys property,
        basically, the part to the left of the ':' in the key name for wells,
        groups and regions.
        """
        if len(list(self.attributes.keys())) == 0 or reload == True :
            props = []
            for each in self.get_Keys() :
                if ':' in each :
                    attr = self.mainKey(each)
                    if attr in self.attributes :
                        if type(self.attributes[ attr ]) == list :
                            self.attributes[ attr ] = self.attributes[ attr ] + [ each ]
                        else :
                            self.attributes[ attr ] = [ each ]
                    else :
                        self.attributes[ attr ] = [each]
                else :
                    self.attributes[ each.strip() ] = []

            for each in list( self.attributes.keys() ) :
                if self.attributes[ each ] != None :
                    self.attributes[ each ] = list(set( self.attributes[ each ] ))
                else :
                    self.attributes[ each ] = []
        if pattern is None :
            return tuple(self.attributes.keys())
        else :
            props = []
            for each in self.get_Keys(pattern,reload=False) :
                if ':' in each :
                    props.append( self.mainKey(each) )
                else :
                    props.append( each.strip() )
            return tuple(set(props))
    
    def get_AttributesDict(self,reload=False) :
        if reload == True :
            self.get_Attributes(None,True)
        return self.attributes

    def add_Key(self,Key) :
        if type(Key) == str :
            Key = Key.strip()
            self.keys = tuple( set( list(self.get_Keys()) + [Key] ) )
        else :
            raise TypeError('Key must be string')
    
    def get_Regions(self,pattern=None,reload=False):
        """
        Will return a list of all the region names in case.

        If the pattern variable is different from None only wells
        matching the pattern will be returned; the matching is based
        on fnmatch(), i.e. shell style wildcards.
        """
        if len(self.regions) == 0 or reload == True :
            self.regions = tuple( self.extract_Regions(pattern) )
        if pattern is None :
            return self.regions
        else:
            return self.extract_Regions(pattern)       
    
    def get_Wells(self,pattern=None,reload=False) :
        """       
        Will return a list of all the well names in case.

        If the pattern variable is different from None only wells
        matching the pattern will be returned; the matching is based
        on fnmatch():
            Pattern     Meaning
            *           matches everything
            ?           matches any single character
            [seq]       matches any character in seq
            [!seq]      matches any character not in seq
            
        """
        if pattern is not None and type( pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        
        if len(self.wells) == 0 or reload == True :
            self.wells = self.extract_Wells() 

        if pattern is None :
            return self.wells
        else:
            return tuple( fnmatch.filter( self.wells , pattern ) )

    def get_Vectors(self,key=None,reload=False):
        return self.get_Vector(key,reload)

    def get_Vector(self,key=None,reload=False):
        """
        returns a dictionary with numpy vectors for the selected key(s)
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        if len( self.get_Restart() ) > 0 :
            return self.checkRestarts(key,reload)
        
        returnVectors = {}
        if self.results != None :
            if type(key) == str :
                returnVectors[key] = self.checkIfLoaded(key,reload)
            if type(key) == list or type(key) == tuple :
                listOfKeys = list(set(key))
                for each in listOfKeys :
                    returnVectors[each] = self.checkIfLoaded(each,reload)
        return returnVectors
    
    # support functions for get_Vector:
    def checkRestarts(self,key=None,reload=False) :
        returnVectors = {}
        Rlist = self.restarts + [ self ]
        if type(key) == str :
            key = [ key ]
            
        for K in key :
            try :
                Rlist[-1].checkIfLoaded(K,False)
                Kexists = True
            except :
                Kexists = False

            if Kexists :
                ti = Rlist[0].checkIfLoaded('TIME',False)[0]
                tf = Rlist[1].checkIfLoaded('TIME',False)[0]

                try :
                    RVector = Rlist[0].checkIfLoaded(K,False)
                except :
                    RVector = np.array( [0]*len(Rlist[0].checkIfLoaded('TIME',False)) , dtype=Rlist[-1].checkIfLoaded(K,False).dtype )

                if RVector is None or len(RVector) == 0 :
                    RVector = np.array( [0]*len(Rlist[0].checkIfLoaded('TIME',False)) , dtype=Rlist[-1].checkIfLoaded(K,False).dtype )

                if tf in Rlist[0].checkIfLoaded('TIME',False) :
                    returnVectors[K] = RVector[ ( Rlist[0].checkIfLoaded('TIME',False)>=ti ) & ( Rlist[0].checkIfLoaded('TIME',False)<tf ) ]
                else :
                    returnVectors[K] = RVector[ Rlist[0].checkIfLoaded('TIME',False) >= ti ]
                verbose( self.speak , 1 , " reading key '" + str(K) + "' from restart " + "0" + ": '" + str(Rlist[0]) + "'")
                
                for R in range(1,len(Rlist)-1) :
                    ti = Rlist[R].checkIfLoaded('TIME',False)[0]
                    tf = Rlist[R+1].checkIfLoaded('TIME',False)[0]
                    try :
                        RVector = Rlist[R].checkIfLoaded(K,False)
                    except :
                        RVector = np.array( [0]*len(Rlist[R].checkIfLoaded('TIME',False)) , dtype=Rlist[-1].checkIfLoaded(K,False).dtype )

                    if RVector is None or len(RVector) == 0 :
                        RVector = np.array( [0]*len(Rlist[R].checkIfLoaded('TIME',False)) , dtype=Rlist[-1].checkIfLoaded(K,False).dtype )

                    if tf in Rlist[R].checkIfLoaded('TIME',False) :
                        returnVectors[K] = np.concatenate( [ returnVectors[K] , RVector[ ( Rlist[R].checkIfLoaded('TIME',False)>=ti ) & ( Rlist[R].checkIfLoaded('TIME',False)<tf ) ] ] )
                    else :
                        returnVectors[K] = np.concatenate( [ returnVectors[K] , RVector[ ( Rlist[R].checkIfLoaded('TIME',False)>=ti ) ] ] )
                    verbose( self.speak , 1 , " reading key '" + str(K) + "' from restart " + str(R) + ": '" + str(Rlist[0]) + "'")
                    
                returnVectors[K] = np.concatenate( [ returnVectors[K] , Rlist[-1].checkIfLoaded(K,False) ] )
                verbose( self.speak , 1 , " reading key '" + str(K) + "' from restart " + str(len(Rlist)) + ": '" + str(Rlist[0]) + "'")
            
        return returnVectors
    
    def checkIfLoaded(self,key,reload) :
        """
        internal function to avoid reloading the same vector twice...
        """
        verbose( self.speak , 1 , ' looking for key ' + str( key ) )
        if str(key).upper().strip() not in self.vectors or reload == True :
            self.vectors[key.upper().strip()] = self.loadVector(key)
        return self.vectors[key.upper().strip()]

    def get_VectorWithoutRestart(self,key=None,reload=False):
        """
        returns a dictionary with numpy vectors for the selected key(s)
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        returnVectors = {}
        if self.results != None :
            if type(key) == str :
                returnVectors[key] = self.checkIfLoaded(key,reload)
            if type(key) == list or type(key) == tuple :
                listOfKeys = list(set(key))
                for each in listOfKeys :
                    returnVectors[each] = self.checkIfLoaded(each,reload)
        return returnVectors
    
    def set_Vector( self , Key , VectorData , Units , DataType='auto' , overwrite=None) :
        """
        Writes a new vector into the dataset 
        or overwrite an existing one if overwrite = True
        The data is stored as numpy.array
        
        > Key must be a string, intended to be the name of the Vector
        > VectorData must be a list, tuple or numpy.array
        > Units must be a string representing the Unit of the data
          optional DataType can define the tipe of data to cast the VectorData.
          The accepted types are the regular numpy types (int , float , datetime).
          If set to 'auto' it will try to guess the datatype or leave as string.
        > optional overwrite protects the data to be overwritten by mistake, 
          the default value for overwrite can be changed with set_Overwrite method
        """
        
        if overwrite is None :
            overwrite = self.overwrite
        elif ( type(overwrite) == int or type(overwrite) == float ) :
            if overwrite == 1 :
                overwrite = True
            else :
                overwrite = False
        elif type(overwrite) == bool :
            pass
        else :
            overwrite = False
        
        if type(Key) == str :
            Key = Key.strip()
        else :
            raise TypeError('Key must be a string')
        
        if Key in self.vectors and overwrite == False :
            raise OverwrittingError('the Key ' + Key + ' already exists in the dataset and overwrite parameter is set to False. Set overwrite=True to avoid this message and change the DataVector.')
            
        if type(VectorData) == list or type(VectorData) == tuple :
            if len(VectorData) == 0 :
                raise TypeError('VectorData must not be empty')
            VectorData = np.array(VectorData)
        elif type(VectorData) == np.ndarray :
            if DataType == 'auto' :
                if 'int' in str(VectorData.dtype) :
                    DataType = 'int'
                    verbose( self.speak , 1 , Key + ' vector detected as numpy.array of dtype ' + DataType + '.' )
                elif 'float' in str(VectorData.dtype) :
                    DataType = 'float'
                    verbose( self.speak , 1 , Key + ' vector detected as numpy.array of dtype ' + DataType + '.' )
                elif 'datetime' in str(VectorData.dtype) :
                    DataType = 'datetime'
                    verbose( self.speak , 1 , Key + ' vector detected as numpy.array of dtype ' + DataType + '.' )
            if VectorData.size == 0 :
                raise TypeError('VectorData must not be empty')
        else :
            raise TypeError('VectorData must be a list, tuple or numpy.ndarray. Received ' + str(type(VectorData)))
        
        if type(Units) == str :
            Units = Units.strip('( )')
            if unit.isUnit(Units) :
                pass
            elif Units == 'DEGREES' and 'API' in self.mainKey(Key).upper() :
                Units = 'API'
                verbose( self.speak , 2 , '\nIMPORTANT: the selected Units: ' + Units + ' were chaged to "API" for the vector with key name ' + Key + '.')
            elif ( ' / ' in Units and unit.isUnit(Units.replace(' / ','/')) ) or ( '/ ' in Units and unit.isUnit(Units.replace('/ ','/')) ) or ( ' /' in Units and unit.isUnit(Units.replace(' /','/')) ) :
                verbose( self.speak , 2 , "\nMESSAGE: the selected Units: '" + Units +"' were chaged to " + Units.replace(' /','/').replace('/ ','/')  + ' for the vector with key name ' + Key + '.')
                Units = Units.replace('/ ','/').replace(' /','/')
            else :
                verbose( self.speak , 3 , "\nIMPORTANT: the selected Units: '" + Units +"' are not recognized by the programm and will not be able to convert this Vector " + str(Key) +' into other units.' )
        else :
            raise TypeError('Units must be a string')
        
        if DataType == 'auto' :
            verbose( self.speak , 1 , ' guessing the data type of the VectorData ' + Key )
            done = False
            if Key.upper() == 'DATE' or Key.upper() == 'DATES' or '/' in str(VectorData) :
                try :
                    VectorData = np.datetime64( pd.to_datetime( VectorData ) , 's' )
                    verbose( self.speak , 1 , Key + ' vector casted as datetime.' )
                    done = True
                except :
                    pass            
            elif Key.upper() == 'TIME' or Key.upper() == 'YEARS' or Key.upper() == 'YEAR' or Key.upper() == 'DAYS' or Key.upper() == 'DAYS' or Key.upper() == 'MONTH' or Key.upper() == 'MONTHS':
                try :
                    VectorData = VectorData.astype('float')
                    verbose( self.speak , 1 , Key + ' vector casted as floating point.' )
                    done = True
                except :
                    pass  
                
            if done == False :
                Integer = False
                try :
                    VectorDataInt = VectorData.astype(int)
                    Integer = True
                except :
                    try :
                        VectorData = VectorData.astype(float)
                        verbose( self.speak , 1 , Key + ' vector casted as floating point.' )
                    except :
                        try :
                            VectorData = np.datetime64( pd.to_datetime(VectorData), 's' )
                            verbose( self.speak , 1 , Key + ' vector casted as datetime.' )
                        except :
                            if type(VectorData) == np.ndarray :
                                VectorType = str( VectorData.dtype )
                            elif type(VectorData) == list or type(VectorData) == tuple :
                                VectorType = str( type(VectorData) ) + ' with ' + type(VectorData[0]) + ' inside'
                            else :
                                VectorType = str( type(VectorData) )
                            verbose( self.speak , 2 , ' not able to cast the VectorData ' + Key + ', kept as received: ' + VectorType + '.' )
                if Integer :
                    try :
                        VectorDataFloat = VectorData.astype(float)
                        if np.all( VectorDataFloat == VectorDataInt ) :
                            VectorData = VectorDataInt
                            verbose( self.speak , 1 , Key + ' vector casted as integer.' )
                        else :
                            VectorData = VectorDataFloat
                            verbose( self.speak , 1 , Key + ' vector casted as floating point.' )
                    except :
                        pass
                    
        elif 'datetime' in DataType :
            try :
                VectorData = np.datetime64( pd.to_datetime( VectorData ) ,'s') 
            except :
                try :
                    VectorData = VectorData.astype(DataType)
                except :
                    verbose( self.speak , 2 , ' not able to cast the VectorData ' + Key + ', kept as received: ' + DataType + '.' )
        else :
            try :
                VectorData = VectorData.astype(DataType)
            except :
                verbose( self.speak , 2 , ' not able to cast the VectorData ' + Key + ', kept as received: ' + DataType + '.' )
        
        self.vectors[Key] = VectorData
        self.units[Key] = Units
        if self.is_Key(Key) == False :
            self.add_Key(Key) 
        self.get_Attributes(reload=True)
    
    def set_Overwrite(self,overwrite) :
        if type(overwrite) == bool :
            self.overwrite = overwrite
    def get_Overwrite(self) :
        return self.overwrite
    
    def stripUnits(self):
        for key in self.units :
            if self.units[key] is None :
                pass
            else :
                self.units[key] = self.units[key].strip('( )').strip("'").strip('"')
                if 'DíA' in self.units[key] :
                    self.units[key] = self.units[key].replace('DíA','DAY')
    
    def fill_FieldBasics(self) :
        
        np.seterr(divide='ignore', invalid='ignore')
        
        if type(self.get_Vector('FOPR')['FOPR']) == np.ndarray and type(self.get_Vector('FWPR')['FWPR']) == np.ndarray :
            # calculated FLPR if not available:
            if self.is_Key('FLPR') == False or len( self.get_Vector('FLPR')['FLPR'] ) < len( self.get_Vector('FWPR')['FWPR'] ) or type(self.get_Vector('FLPR')['FLPR']) != np.ndarray :
                try :
                    self.set_Vector( 'FLPR' , np.array( self.get_Vector('FOPR')['FOPR'],dtype='float' ) + convertUnit( np.array( self.get_Vector('FWPR')['FWPR'],dtype='float' ) , self.get_Unit('FWPR') , self.get_Unit('FOPR') , PrintConversionPath=(self.speak==1) ) , self.get_Unit('FOPR') , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FLPR.')
            
            # calculated FWCT if not available:
            if self.is_Key('FWCT') == False or len( self.get_Vector('FWCT')['FWCT'] ) < len( self.get_Vector('FWPR')['FWPR'] ) or type(self.get_Vector('FWCT')['FWCT']) != np.ndarray :
                try :
                    Vector = np.array( np.divide(  np.array(self.get_Vector('FWPR')['FWPR'],dtype='float') , convertUnit( np.array( self.get_Vector('FLPR')['FLPR'],dtype='float' ) , self.get_Unit('FLPR') , self.get_Unit('FWPR') , PrintConversionPath=(self.speak==1) ) ) ,dtype='float') 
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FWCT' , Vector , 'FRACTION' , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FWCT.')
                    
            # calculated FWOR & FOWR if not available:
            if self.is_Key('FWOR') == False or len( self.get_Vector('FWOR')['FWOR'] ) < len( self.get_Vector('FWPR')['FWPR'] ) or type(self.get_Vector('FWOR')['FWOR']) != np.ndarray :
                try :
                    Vector = np.array( np.divide( np.array( self.get_Vector('FWPR')['FWPR'] , dtype='float' ) , np.array( self.get_Vector('FOPR')['FOPR'] , dtype='float' ) ),dtype='float')
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FWOR' , Vector , self.get_Unit('FWPR').split('/')[0]+'/'+self.get_Unit('FOPR').split('/')[0] , overwrite=True )

                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FWOR.')
                try :
                    Vector = np.array( np.divide( np.array( self.get_Vector('FOPR')['FOPR'] , dtype='float' ) , np.array( self.get_Vector('FWPR')['FWPR'] , dtype='float' ) ) ,dtype='float')
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FOWR' , Vector , self.get_Unit('FOPR').split('/')[0]+'/'+self.get_Unit('FWPR').split('/')[0] , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FOWR.')
                    
        # calculated FGOR if not available:
        if type(self.get_Vector('FOPR')['FOPR']) == np.ndarray and type(self.get_Vector('FGPR')['FGPR']) == np.ndarray :
            if self.is_Key('FGOR') == False or len( self.get_Vector('FGOR')['FGOR'] ) < len( self.get_Vector('FOPR')['FOPR'] ) or type(self.get_Vector('FGOR')['FGOR']) != np.ndarray :
                try :
                    Vector = np.array( np.divide( np.array( self.get_Vector('FGPR')['FGPR'] , dtype='float' ) , np.array( self.get_Vector('FOPR')['FOPR'] , dtype='float' ) ) ,dtype='float')
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FGOR' ,  Vector  , self.get_Unit('FGPR').split('/')[0]+'/'+self.get_Unit('FOPR').split('/')[0] , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FGOR.')
        
        # calculated FOGR if not available:
        if type(self.get_Vector('FOPR')['FOPR']) == np.ndarray and type(self.get_Vector('FGPR')['FGPR']) == np.ndarray :
            if self.is_Key('FOGR') == False or len( self.get_Vector('FOGR')['FOGR'] ) < len( self.get_Vector('FOPR')['FOPR'] ) or type(self.get_Vector('FOGR')['FOGR']) != np.ndarray :
                try :
                    Vector = np.array( np.divide( np.array( self.get_Vector('FOPR')['FOPR'] , dtype='float' ) , np.array( self.get_Vector('FGPR')['FGPR'] , dtype='float' ) ) ,dtype='float')
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FOGR' , Vector , self.get_Unit('FOPR').split('/')[0]+'/'+self.get_Unit('FGPR').split('/')[0] , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FOGR.')
    
        if type(self.get_Vector('FOPT')['FOPT']) == np.ndarray and type(self.get_Vector('FWPT')['FWPT']) == np.ndarray :
            # calculated FLPR if not available:
            if self.is_Key('FLPT') == False or len( self.get_Vector('FLPT')['FLPT'] ) < len( self.get_Vector('FWPT')['FWPT'] ) or type(self.get_Vector('FLPT')['FLPT']) != np.ndarray :
                try :
                    self.set_Vector( 'FLPT' , np.array( self.get_Vector('FOPT')['FOPT'],dtype='float' ) + convertUnit( np.array( self.get_Vector('FWPT')['FWPT'],dtype='float' ), self.get_Unit('FWPT') , self.get_Unit('FOPT') , PrintConversionPath=(self.speak==1)) , self.get_Unit('FOPT') , overwrite=True )
                except :
                    try :
                        Name , Vector , Units = self.integrate( 'FLPR' , 'FLPT' )
                        self.set_Vector(Name,Vector,Units,'float',True)
                        verbose( self.speak , 2 , 'vector FLPT integrated from FLPR.')
                    except :
                        verbose( self.speak , 2 , 'failed to create missing vector FLPT.')
    
        np.seterr(divide=None, invalid=None)
    
    def fill_WellBasics(self) :
        
        np.seterr(divide='ignore', invalid='ignore')
        
        for well in list(self.get_Wells()) :
            if type(well) == str and len(well.strip()) > 0 :
                well = well.strip()
                verbose( self.speak , 2 , ' calculating basic ratios for the well ' + well )
                if type(self.get_Vector('WOPR:'+well)['WOPR:'+well]) == np.ndarray and type(self.get_Vector('WWPR:'+well)['WWPR:'+well]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key('WLPR:'+well) == False or len( self.get_Vector('WLPR:'+well)['WLPR:'+well] ) < len( self.get_Vector('WWPR:'+well)['WWPR:'+well] ) or type(self.get_Vector('WLPR:'+well)['WLPR:'+well]) != np.ndarray :
                        try :
                            self.set_Vector( 'WLPR:'+well , np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) + convertUnit( np.array( self.get_Vector('WWPR:'+well)['WWPR:'+well] , dtype='float' ) , self.get_Unit('WWPR:'+well) , self.get_Unit('WOPR:'+well) , PrintConversionPath=(self.speak==1)) , self.get_Unit('WOPR:'+well) , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WLPR:'+well)
                    
                    # calculated WWCT if not available:
                    if self.is_Key('WWCT:'+well) == False or len( self.get_Vector('WWCT:'+well)['WWCT:'+well] ) < len( self.get_Vector('WWPR:'+well)['WWPR:'+well] ) or type(self.get_Vector('WWCT:'+well)['WWCT:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WWPR:'+well)['WWPR:'+well] , dtype='float' ) , convertUnit( np.array(self.get_Vector('WLPR:'+well)['WLPR:'+well], dtype='float' ), self.get_Unit('WLPR:'+well) , self.get_Unit('WWPR:'+well) , PrintConversionPath=(self.speak==1)) ) , dtype='float' ) 
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WWCT' , Vector , 'FRACTION' , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WWCT:'+well)
                            
                    # calculated WWOR & WOWR if not available:
                    if self.is_Key('WWOR:'+well) == False or len( self.get_Vector('WWOR:'+well)['WWOR:'+well] ) < len( self.get_Vector('WWPR:'+well)['WWPR:'+well] ) or type(self.get_Vector('WWOR:'+well)['WWOR:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WWPR:'+well)['WWPR:'+well] , dtype='float' ) , np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WWOR:'+well , Vector , self.get_Unit('WWPR:'+well).split('/')[0]+'/'+self.get_Unit('WOPR:'+well).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WWOR:'+well)
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) , np.array( self.get_Vector('WWPR:'+well)['WWPR:'+well] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WOWR:'+well , Vector , self.get_Unit('WOPR:'+well).split('/')[0]+'/'+self.get_Unit('WWPR:'+well).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WOWR:'+well)
                            
                # calculated WGOR if not available:
                if type(self.get_Vector('WOPR:'+well)['WOPR:'+well]) == np.ndarray and type(self.get_Vector('WGPR:'+well)['WGPR:'+well]) == np.ndarray :
                    if self.is_Key('WGOR:'+well) == False or len( self.get_Vector('WGOR:'+well)['WGOR:'+well] ) < len( self.get_Vector('WOPR:'+well)['WOPR:'+well] ) or type(self.get_Vector('WGOR:'+well)['WGOR:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WGPR:'+well)['WGPR:'+well] , dtype='float' ) , np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WGOR:'+well , Vector  , self.get_Unit('WGPR:'+well).split('/')[0]+'/'+self.get_Unit('WOPR:'+well).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WGOR:'+well)
                
                # calculated WOGR if not available:
                    if self.is_Key('WOGR:'+well) == False or len( self.get_Vector('WOGR:'+well)['WOGR:'+well] ) < len( self.get_Vector('WOPR:'+well)['WOPR:'+well] ) or type(self.get_Vector('WOGR:'+well)['WOGR:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) , np.array( self.get_Vector('WGPR:'+well)['WGPR:'+well] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WOGR:'+well , Vector , self.get_Unit('WOPR:'+well).split('/')[0]+'/'+self.get_Unit('WGPR:'+well).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WOGR:'+well)
            
                if type(self.get_Vector('WOPT:'+well)['WOPT:'+well]) == np.ndarray and type(self.get_Vector('WWPT:'+well)['WWPT:'+well]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key('WLPT:'+well) == False or len( self.get_Vector('WLPT:'+well)['WLPT:'+well] ) < len( self.get_Vector('WWPT:'+well)['WWPT:'+well] ) or type(self.get_Vector('WLPT:'+well)['WLPT:'+well]) != np.ndarray :
                        try :
                            self.set_Vector( 'WLPT:'+well , np.array( self.get_Vector('WOPT:'+well)['WOPT:'+well] , dtype='float' ) + convertUnit( np.array(self.get_Vector('WWPT:'+well)['WWPT:'+well], dtype='float'), self.get_Unit('WWPT:'+well) , self.get_Unit('WOPT:'+well) , PrintConversionPath=(self.speak==1) ) , self.get_Unit('WOPT:'+well) , overwrite=True )
                        except :
                            try :
                                Name , Vector , Units = self.integrate( 'WLPR:'+well , 'WLPT:'+well )
                                self.set_Vector(Name,Vector,Units,'float',True)
                                verbose( self.speak , 2 , 'vector WLPT:' + well + ' integrated from WLPR:' + well + '.')
                            except :
                                verbose( self.speak , 2 , 'failed to create missing vector WLPT:'+well)
    
        np.seterr(divide=None, invalid=None)
        
    def fill_Basics(self,ItemsNames=[],KeyType='') :
        """
        if the required inputs exists, calculates:
            - liquid rate
            - liquid cumulative
            - water-cut
            - water-oil ratio
            - oil-water ratio
            - gas-oil ratio
            - oil-gas ratio
        
        KeyType in a character that indicates the type of keyword (1st character)
        to save the results:
            - G for groups : GOPR:name, GWCT:name, GGOR:name
            - W for wells : WOPR:name, WWCT:name, WGOR:name
            - R for regions : ROPR:name, RWCT:name, RGOR:name
            etc
        
        default of KeyType is :
            W if the ItemName exists in get_Wells()
            G if the ItemName exists in get_Groups()
            R if the ItemName exists in get_Regions()
        """
        np.seterr(divide='ignore', invalid='ignore')
        
        if type(ItemsNames) == str :
            ItemsNames = [ ItemsNames ]
        
        
        for item in ItemsNames :
            
            KT = 'U'
            if item in list(self.get_Regions()) :
                KT = 'R'
            if item in list(self.get_Groups()) :
                KT = 'G'
            if item in list(self.get_Wells()) :
                KT = 'W'
            if item not in ( 'FIELD' , 'ROOT' ) :
                item = ':'+item
                KT = 'F'
            if KeyType != '' :
                KT = KeyType
                
            if type(item) == str and len(item.strip()) > 0 :
                item = item.strip()
                verbose( self.speak , 2 , ' calculating basic ratios for the item ' + item )
                if type(self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item]) == np.ndarray and type(self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key(KT+'LPR'+item) == False or len( self.get_Vector(KT+'LPR'+item)[KT+'LPR'+item] ) < len( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] ) or type(self.get_Vector(KT+'LPR'+item)[KT+'LPR'+item]) != np.ndarray :
                        try :
                            self.set_Vector( KT+'LPR'+item , np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) + np.array( convertUnit(self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] , dtype='float' , PrintConversionPath=(self.speak==1)) , self.get_Unit(KT+'WPR'+item) , self.get_Unit(KT+'OPR'+item) ) , self.get_Unit(KT+'OPR'+item) , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'LPR'+item)
                    
                    # calculated WWCT if not available:
                    if self.is_Key(KT+'WCT'+item) == False or len( self.get_Vector(KT+'WCT'+item)[KT+'WCT'+item] ) < len( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] ) or type(self.get_Vector(KT+'WCT'+item)[KT+'WCT'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] , dtype='float' ) , np.array( convertUnit(self.get_Vector(KT+'LPR'+item)[KT+'LPR'+item], self.get_Unit(KT+'LPR'+item) , self.get_Unit(KT+'WPR'+item) , PrintConversionPath=(self.speak==1)) , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'WCT' , Vector , 'FRACTION' , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'WCT'+item)
                            
                    # calculated WWOR & WOWR if not available:
                    if self.is_Key(KT+'WOR'+item) == False or len( self.get_Vector(KT+'WOR'+item)[KT+'WOR'+item] ) < len( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] ) or type(self.get_Vector(KT+'WOR'+item)[KT+'WOR'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] , dtype='float' ) , np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'WOR'+item , Vector , self.get_Unit(KT+'WPR'+item).split('/')[0]+'/'+self.get_Unit(KT+'OPR'+item).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'WOR'+item)
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) , np.array( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'OWR'+item , Vector , self.get_Unit(KT+'OPR'+item).split('/')[0]+'/'+self.get_Unit(KT+'WPR'+item).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'OWR'+item)
                            
                # calculated WGOR if not available:
                if type(self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item]) == np.ndarray and type(self.get_Vector(KT+'GPR'+item)[KT+'GPR'+item]) == np.ndarray :
                    if self.is_Key(KT+'GOR'+item) == False or len( self.get_Vector(KT+'GOR'+item)[KT+'GOR'+item] ) < len( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] ) or type(self.get_Vector(KT+'GOR'+item)[KT+'GOR'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'GPR'+item)[KT+'GPR'+item] , dtype='float' ) , np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'GOR'+item , Vector  , self.get_Unit(KT+'GPR'+item).split('/')[0]+'/'+self.get_Unit(KT+'OPR'+item).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'GOR'+item)
                
                # calculated WOGR if not available:
                    if self.is_Key(KT+'OGR'+item) == False or len( self.get_Vector(KT+'OGR'+item)[KT+'OGR'+item] ) < len( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] ) or type(self.get_Vector(KT+'OGR'+item)[KT+'OGR'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) , np.array( self.get_Vector(KT+'GPR'+item)[KT+'GPR'+item] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'OGR'+item , Vector , self.get_Unit(KT+'OPR'+item).split('/')[0]+'/'+self.get_Unit(KT+'GPR'+item).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'OGR'+item)
            
                if type(self.get_Vector(KT+'OPT'+item)[KT+'OPT'+item]) == np.ndarray and type(self.get_Vector(KT+'WPT'+item)[KT+'WPT'+item]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key(KT+'LPT'+item) == False or len( self.get_Vector(KT+'LPT'+item)[KT+'LPT'+item] ) < len( self.get_Vector(KT+'WPT'+item)[KT+'WPT'+item] ) or type(self.get_Vector(KT+'LPT'+item)[KT+'LPT'+item]) != np.ndarray :
                        try :
                            self.set_Vector( KT+'LPT'+item , self.get_Vector(KT+'OPT'+item)[KT+'OPT'+item] + convertUnit(self.get_Vector(KT+'WPT'+item)[KT+'WPT'+item], self.get_Unit(KT+'WPT'+item) , self.get_Unit(KT+'OPT'+item) , PrintConversionPath=(self.speak==1)) , self.get_Unit(KT+'OPT'+item) , overwrite=True )
                        except :
                            try :
                                Name , Vector , Units = self.integrate( KT+'LPR'+item , KT+'LPT'+item )
                                self.set_Vector(Name,Vector,Units,'float',True)
                                verbose( self.speak , 2 , 'vector ' + KT +'LPT' + item + ' integrated from ' + KT + 'LPR' + item + '.')
                            except :
                                verbose( self.speak , 2 , 'failed to create missing vector '+KT+'LPT'+item)
    
        np.seterr(divide=None, invalid=None)
    
    def arithmeticVector(self,Key) :
        """
        returns a calculated vector if the required inputs exist.
        works with ECL keys only
        """
        Key = Key.strip()
        ClassKey = Key.split(':')[0][0]
        CalcKey = Key.split(':')[0][1:]
        ItemKey = ''
        if ':' in Key :
            ItemKey = ':' + Key.split(':')[1]
        if CalcKey in dictionaries.calculations :
            OK = True
            for Req in dictionaries.calculations[CalcKey][::2] :
                if type(Req) == str :
                    if type(self.get_Vector(ClassKey+Req+ItemKey)[ClassKey+Req+ItemKey]) == np.ndarray :
                        # is a vector with values...
                        pass
                    else :
                        OK = False
                        break
                else :
                    #  should be int or float
                    pass
            if OK :

                for i in range( len( dictionaries.calculations[CalcKey] )) :
                    if i == 0 :
                        # initialize CalculationTuple
                        if type( dictionaries.calculations[CalcKey][i] ) == str :
                            CalculationTuple = [ ClassKey + dictionaries.calculations[CalcKey][i] + ItemKey ]
                        else :
                            CalculationTuple = [ dictionaries.calculations[CalcKey][i] ]
                    else :
                        if type( dictionaries.calculations[CalcKey][i] ) == str :
                            CalculationTuple.append( [ ClassKey + dictionaries.calculations[CalcKey][i] + ItemKey ] )
                        else :
                            CalculationTuple.append( [ dictionaries.calculations[CalcKey][i] ] )
                
                return self.calculator( CalculationTuple , Key )

    def calculator(self,CalculationTuple,ResultName=None,ResultUnits=None) :
        """
        receives a tuple indicating the operation to perform and returns a vector
        with ResultName name 
        
        The CalculationTuple is a sequence of Vectors or Floats and operators:
        The syntax of the CalculationTuple is:
            ( 'Vector or float' , 'operator' , 'Vector or float' , 'operator' , 'Vector or float' , 'operator' ... 'Vector or float'  )
        
        The accepted operators are: '+' , '-' , '*' , '/' , '^'
        The CalculationTuple must start with a number or variable, never with an operator

        The operations will be executed in the exact order they are described. i.e.:
            'FLPR' : ( 'FOPR' , '+' , 'FWPR' ) 
                means FLPR = FOPR + FWPR 
                will add FOPR plus FWPR
            'WWCT:P1' : ( 'WOPR:P1' , '/' , 'WLPR:P2' ) 
                means WWCT:P1 = WOPR:P1 + WLPR:P2 
                will add FOPR plus FWPR
        but:
            'R' : ( 'A' , '-', 'B' , '*' , 'C' ) 
                means R = ( A - B ) / C
                will add A plus B and the result will be divided by C

            to represent R = A - B / C the correct sintax is:
            'R' : ( -1 , '*' , 'B' , '/', 'C' , '+' , 'A'  ) 
                that means R = -1 * B / C + A
        """
        if type( CalculationTuple ) == str :
            verbose ( self.speak , 3 , ' the received string for CalculatedTuple was converted to tuple,\n  received: ' + CalculationTuple + '\n  converted to: ' + str( CalculationTuple.split() ) )
            CalculationTuple = tuple ( CalculationTuple.split() )
        elif type( CalculationTuple ) == list :
            CalculationTuple = tuple( CalculationTuple )
        if ResultName is None :
            ResultName = str( CalculationTuple )
            
        OK = True
        Missing = []
        for Req in CalculationTuple[::2] :
            if type(Req) == str :
                if type(self.get_Vector(Req)[Req]) == np.ndarray :
                    # is a vector with values... OK
                    pass
                else :
                    OK = False
                    Missing.append(Req)
            else :
                #  should be int or float
                pass
        if not OK :
            verbose( self.speak , 3 , '\n IMPORTANT: the following required input vectors were not found:\n   -> ' + '\n   -> '.join(Missing) + '\n')
            return { ResultName : None }
        else :
            for i in range(0, len( CalculationTuple ) , 2) :
                if i == 0 :
                    # initialize Result vector
                    if type( CalculationTuple[i] ) == str :
                        Result = np.array( self.get_Vector( CalculationTuple[i] )[ CalculationTuple[i] ] , dtype='float' )
                        Units = [ self.get_Unit( CalculationTuple[i] ) ]
                    else :
                        Result = CalculationTuple[i]
                        Units = [None]
                else :
                    # following the operations sequence
                    # extracting Next vector or float
                    if type( CalculationTuple[i] ) == str :
                        Next = np.array( self.get_Vector(CalculationTuple)[CalculationTuple] , dtype='float' )
                        Units.append( self.get_Unit( CalculationTuple[i] ) )
                        CalcUnit = self.get_Unit( CalculationTuple[i] )
                    else :
                        Next = CalculationTuple[i]
                        Units.append(None)
                        NextUnit = self.get_Unit( CalculationTuple[i] )
                    # appliying calculation
                    if CalculationTuple[i-1] == '+' :
                        if CalcUnit == NextUnit :
                            Result = Result + Next
                        elif convertibleUnits( NextUnit , CalcUnit) :
                            Result = Result + convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                        else :
                            CalcUnit = CalcUnit + '+' + NextUnit
                            Result = Result + Next

                    elif CalculationTuple[i-1] == '-' :
                        if CalcUnit == NextUnit :
                            Result = Result - Next
                        elif convertibleUnits( NextUnit , CalcUnit) :
                            Result = Result - convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                        else :
                            CalcUnit = CalcUnit + '-' + NextUnit
                            Result = Result - Next
                            
                    elif CalculationTuple[i-1] == '*' :
                        if CalcUnit == NextUnit :
                            Result = Result * Next
                        elif convertibleUnits( NextUnit , CalcUnit) :
                            Result = Result * convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                        else :
                            CalcUnit = CalcUnit + '*' + NextUnit
                            Result = Result * Next
                        
                    elif CalculationTuple[i-1] == '/' :
                        if CalcUnit == NextUnit :
                            Result = np.divide ( Result , Next )
                        elif convertibleUnits( NextUnit , CalcUnit) :
                            Result = np.divide ( Result , convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1)) )
                            
                        else :
                            CalcUnit = CalcUnit + '/' + NextUnit
                            Result = np.divide( Result , Next )
                        Result = np.nan_to_num( Result, nan=0.0 , posinf=0.0 , neginf=0.0 )
                        
                    elif CalculationTuple[i-1] == '^' :
                        if CalcUnit == NextUnit :
                            Result = Result ** Next
                        elif convertibleUnits( NextUnit , CalcUnit) :
                            Result = Result ** convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                        else :
                            CalcUnit = CalcUnit + '^' + NextUnit
                            Result = Result ** Next
            
            SameUnits = []
            for each in Units :
                if each != None :
                    SameUnits.append(each)
            if len( set( SameUnits ) ) == 0 :
                Units = 'DIMENSIONLESS'
            elif len( set( SameUnits ) ) == 1 :
                Units = SameUnits[0]
            else :
                Units = Units[0]
                for i in range(1,len( Units )) :
                    Units.append( CalculationTuple[2*i-1] )
                    Units.append( Units[i] )
                Units = str(Units)
                
            if ResultUnits is None :
                ResultUnits = Units
            elif ResultUnits == Units :
                # OK
                pass
            elif ResultUnits == CalcUnit :
                # OK
                Units = CalcUnit
            elif convertibleUnits( CalcUnit , ResultUnits ) :
                # OK
                Result = convertUnit( Result , CalcUnit , ResultUnits , PrintConversionPath=(self.speak==1) )
            else :
                print( 'MESSAGE: The provided units are not equal to the calculated units:\n    ' + str(ResultUnits) + ' != ' + Units  )
            
            self.set_Vector( str( CalculationTuple ) , Result , ResultUnits , 'float' , False )
            if ResultName != str( CalculationTuple ) :
                self.vectors[ResultName] = self.vectors[ str( CalculationTuple ) ]
                self.units[ResultName] = self.units[ str( CalculationTuple ) ]
                
            return { ResultName : Result }
            
    def createDATES(self) :
        TIME = self.get_Vector('TIME')['TIME']
        start = self.start
        DATE = np.empty(len(TIME), dtype='datetime64[s]')
        for i in range(len(TIME)) :
            DATE[i] = start + np.timedelta64( timedelta(days=TIME[i]) )
        self.set_Vector( 'DATES' , DATE , 'DATE' , overwrite=True )
        self.set_Vector( 'DATE' , DATE , 'DATE' , overwrite=True )
    
    def get_UnitsConverted(self,Key=None,OtherObject_or_NewUnits=None):
        """
        returns a vector converted from the unit system of this object 
        to the units of the corresponding vector on the other SimResult object 
        or to the indicated units as string or Unit object. 
        
        If Key is defaulted an empty dictionary will be returned
        If Other_Object_or_Units is set to None or defautl no conversion 
        will be applied. It is equivalent to get_Vector() method.
        
        """
        # checking input parameters
        if type(Key) == str :
            Key = [Key]
        elif type(Key) == list or type(Key) == tuple :
            pass
        if Key is None :
            return {}
        if OtherObject_or_NewUnits is None :
            return self.get_Vector(Key, False)
        
        
        ListOfUnits = False
        if type(OtherObject_or_NewUnits) == str :
            OtherObject_or_NewUnits = [OtherObject_or_NewUnits]
            ListOfUnits = True
        elif type(OtherObject_or_NewUnits) == list or type(OtherObject_or_NewUnits) == tuple :
            ListOfUnits = True
            
        if ListOfUnits == True and len(Key) != len(OtherObject_or_NewUnits) :
            raise TypeError( str(len(Key)) + ' resquested but ' + str(len(OtherObject_or_NewUnits)) + ' units provided.\n          Both should match order and number.' )
        elif ListOfUnits == True and len(Key) == len(OtherObject_or_NewUnits) :
            pass
        else :
            try :
                if OtherObject_or_NewUnits.SimResult == True :
                    errors = False
                    TempConversions = []
                    for each in Key :
                        if OtherObject_or_NewUnits.is_Key(each) == False :
                            errors = True
                            verbose( self.speak , 3 , 'The requested Key ' + str(each) + ' is not present in the simulation ' + str(OtherObject_or_NewUnits.get_Name()) + '.')
                        else :
                            TempConversions.append( OtherObject_or_NewUnits.get_Unit( each.strip() ) )
                    if errors == True :
                        raise TypeError('at least one requested Key is not present in the simulation ' + str(OtherObject_or_NewUnits.get_Name()) + '.')
                    # OtherObject = OtherObject_or_NewUnits
                    OtherObject_or_NewUnits = TempConversions
                    TempConversions = None
                else :
                    raise TypeError('Other_Object_or_Units must be string, a list of strings or a SimResult object.')
            except :
                raise TypeError('Other_Object_or_Units must be string, a list of strings or a SimResult object.')
        
        # extracting and converting the selected Keys
        ConvertedDict = {}
        for each in range(len(Key)) :
            ConvertedDict[Key[each]] = convertUnit(self.get_Vector(Key[each])[Key[each].strip()], self.get_Unit(Key[each]), OtherObject_or_NewUnits[each] , PrintConversionPath=(self.speak==1))
        return ConvertedDict
    
    def integrate(self,InputKey,OutputKey=None,ConstantRate=False,Numpy=True):
        """"
        calculate the integral, or cumulative, of the input vector and saves 
        it to the output vector.
       
        if ConstantRate = True :
            cumulative[i] = cumulative[i-1] + Time[i] * InputKey[i] 
        if ConstantRate = False :
            cumulative[i] = cumulative[i-1] + Time[i] * ( min( InputKey[i] , InputKey[i+1] ) + Time[i] * ( max( InputKey[i] , InputKey[i+1] ) - min( InputKey[i] , InputKey[i+1] ) ) 
            
        Set Numpy=False to not use Numpy, the calculation will be done witha for loop
        """
        if type(InputKey) != str or ( type(OutputKey) != None and type(OutputKey) != str ) :
            raise TypeError(' InputKey and OutputKey must be strings.')
        Vector = self.get_Vector( InputKey )[ InputKey ]
        VectorUnits = self.get_Unit(InputKey)
        verbose( self.speak , 1 , "<integrate> retrieved series '" + InputKey + "' of lenght " + str(len(Vector)) + ' and units ' + str(VectorUnits))
        Time = self.get_Vector( 'TIME' )[ 'TIME' ]
        TimeUnits = self.get_Unit('TIME')
        verbose( self.speak , 1 , "<integrate> retrieved series 'TIME' of lenght " + str(len(Time)) + ' and units ' + str(TimeUnits))
        
        
        OutUnits = ''
        if '/' in VectorUnits :
            VectorSubUnits={}
            for i in range(len(VectorUnits.split('/'))) :
                VectorSubUnits[i] = VectorUnits.split('/')[i]
            if TimeUnits in VectorSubUnits :
                OutUnits = []
                ConvFactor = 1
                for i in range(len(VectorSubUnits)) :
                    if VectorSubUnits[i] == TimeUnits :
                        if i == 0 :
                            OutUnits.append(VectorSubUnits[i]+'*'+VectorSubUnits[i])
                        else :
                            pass
                    else :
                        OutUnits.append(VectorSubUnits[i])
            else :
                OutUnits = []
                ConvFactor = 1
                for i in range(len(VectorSubUnits)) :
                    verbose( self.speak , 1 , "<integrate> converting " + str(TimeUnits) + ' to ' + str(VectorSubUnits[i]))
                    if convertibleUnits(VectorSubUnits[i],TimeUnits) :
                        ConvFactor = ConvFactor * convertUnit(1, TimeUnits , VectorSubUnits[i] , PrintConversionPath=(self.speak==1) )
                        verbose( self.speak , 1 , "<integrate> conversion factor: 1 " + str(TimeUnits) + ' = '  + str( ConvFactor ) + ' ' + str(VectorSubUnits[i]))
                    else :
                        OutUnits.append(VectorSubUnits[i])
                        verbose( self.speak , 1 , "<integrate> not convertible")
                        
            OutUnits = '/'.join(OutUnits)
        else :
            OutUnits = VectorUnits + '*' + TimeUnits
            ConvFactor = 1
        
        verbose( self.speak , 1 , "<integrate> integrated series units will be " + str(OutUnits))
        
        if len(Vector) != len(Time) :
            raise TypeError( ' the Key vector ' + InputKey + ' and its TIME does not have the same lenght: ' + str( len(Vector) ) + ' != ' + str( len(Time) ) + '.' )
        
        
        if Numpy == False :
            # integrating one row at a time, iterating with for:
            verbose( self.speak , 2 , "<integrate> calculating integral for key '" + InputKey + "' using for loor")
            Cumulative = [0.0]
            if ConstantRate == False :
                for i in range(len(Vector)-1) :
                    dt = ( Time[i+1] - Time[i] ) * ConvFactor
                    if Vector[i] <= Vector[i+1] :
                        Vmin = Vector[i]
                        Vmax = Vector[i+1]
                    else :
                        Vmin = Vector[i+1]
                        Vmax = Vector[i]
                    Cumulative.append( Cumulative[i-1] + dt * Vmin + dt * (Vmax - Vmin) / 2.0 )
            else :
                for i in range(len(Vector)-1) :
                    Cumulative.append( Cumulative[i-1] + dt * Vector[i] )
        
        else :
            # integrating numpy method:
            verbose( self.speak , 2 , "<integrate> calculating integral for key '" + InputKey + "' using numpy methods")
            for X in ( Time , Vector ) :
                if type(X) != np.ndarray :
                    if type(X) == list or type(X) == tuple :
                        try :
                            X = np.array(X,dtype='float')
                        except :
                            print(" the key '" + X + "' is not numpy array.")
 
            dt = np.diff( Time ) * ConvFactor
            
            if ConstantRate == False :
                Vmin = np.minimum( Vector[:-1] , Vector[1:] )
                Vmax = np.maximum( Vector[:-1] , Vector[1:] )
                Cumulative = dt * Vmin + dt * ( Vmax - Vmin ) / 2.0
            else : 
                Cumulative = dt * Vector[:-1]
            
            Cumulative = [0.0] + list( Cumulative )
            Cumulative = np.array( Cumulative , dtype='float' )
            Cumulative = np.cumsum( Cumulative )
        
        try :
            self.set_Vector(OutputKey, np.array( Cumulative ) , OutUnits , overwrite=False )
        except OverwrittingError :
            pass
        return ( OutputKey , np.array( Cumulative ) , OutUnits )
    
    def get_DataFrame(self,Keys=None,Index='TIME') :
        """
        returns a pandas DataFrame for the keys in the argument.
        
        The argument * Keys * can be:
            > a string with one Key
            > a list of string Keys
            > the string '--EVERYTHING--' to extract ALL the keys in 
            the summary file but consider it could take long time to run
            before requesting everything.
            
        The argument * Index * will be passed as the index of the DataFrame.
        By default will be 'TIME' but could be 'DATES' or any other like 'FOPT'
        """
        if type(Keys) == str :
            if Keys == '--EVERYTHING--' :
                Keys = list( self.get_Keys() )
            else :
                Keys = [Keys]
        if type(Index) == list or type(Index) == tuple :
            if len(Index) > 1 :
                verbose( self.speak , -1 , '< get_DataFrame > more than value passed in Index argument, only the first one will be used')
            Index = Index[0]
        return pd.DataFrame( data=self.get_Vector( Keys ) , index=self.get_Vector( Index )[ Index ] )
    
    def get_ConvertedDataFrame(self,Keys=None,Index='TIME', OtherObject_or_NewUnits=None) :
        """
        returns a pandas DataFrame for the keys in the argument converted to 
        the specified units.
        
        The argument * Keys * can be:
            > a string with one Key
            > a list of string Keys
            > the string '--EVERYTHING--' to extract ALL the keys in 
            the summary file but consider it could take long time to run
            before requesting everything.
            
        The argument * Index * will be passed as the index of the DataFrame.
        By default will be 'TIME' but could be 'DATES' or any other like 'FOPT'
        
        The argument * OtherObject_or_NewUnits * can be:
            > a string of the new units for a single Key 
            > a list new units for every Key in the Keys argument
            > a SimResult object, the new units will be extracted from it.
        """
        if type(Keys) == str :
            if Keys == '--EVERYTHING--' :
                Keys = list( self.get_Keys() )
            else :
                Keys = [Keys]
        if type(Index) == list or type(Index) == tuple :
            if len(Index) > 1 :
                verbose( self.speak , -1 , '< get_DataFrame > more than value passed in Index argument, only the first one will be used')
            Index = Index[0]
        elif type(Index) == str :
            pass 
        else :
            try :
                if Index.SimResult == True :
                    if OtherObject_or_NewUnits is None :
                        OtherObject_or_NewUnits = Index
                        Index = 'TIME'
            except :
                pass
    
        if Index not in Keys:
            DF = self.get_UnitsConverted( [Index] + Keys , OtherObject_or_NewUnits )
            DF = pd.DataFrame( data=DF , index=DF[Index] )
        else :
            DF = self.get_UnitsConverted( Keys , OtherObject_or_NewUnits )
            DF = pd.DataFrame( data=DF , index=DF[Index] )
        return DF


    def save( self,FileNamePath ) :
        fileName , Ext , Folder , FullPath = extension(FileNamePath)
        # create the folders structure:
        try :
            os.mkdir(Folder + fileName + '_storage')
        except :
            print( ' folder already exists')
        try :
            os.mkdir(Folder + fileName + '_storage' + '/parquet')
        except :
            print( ' parquet already exists')
        try :
            os.mkdir(Folder + fileName + '_storage' + '/raw')
        except :
            print( ' raw already exists')
        try :
            os.mkdir(Folder + fileName + '_storage' + '/json')
        except :
            print( ' raw already exists')
                               
        txtfile = 'SimResult =:= ' + str( self.SimResult ) + '\n'
        txtfile = txtfile + 'kind =:= ' + str( self.kind ) + '\n'
        
        if self.kind == ECL :
            pass
        elif self.kind == VIP :
            count = 0
            if len(self.results) == 0 and self.CSV != False :
                self.CSVgenerateResults()
            
            resultstxt = ''
            for each in list( self.results.keys() ) :
                DF_raw = pd.DataFrame( self.results[each][1]['Data'] )
                if 'TIME' in DF_raw.columns :
                    DF_raw.set_index('TIME',drop=False,inplace=True)
                DF_raw.to_parquet(Folder + fileName + '_storage/raw/' + str(count) + '_rawdata.sro' , index=True)
                with open(Folder + fileName + '_storage/raw/' + str(count) + '_rawunits.sro', 'w') as file:
                    file.write(json.dumps( self.results[each][1]['Units'] )) 
                resultstxt = resultstxt + str( count ) + ' =:= ' + str( each ) + ' =:= ' + self.results[each][0] + ' \n'
                
            with open(Folder + fileName + '_storage/raw/keys.sro', 'w') as file:
                file.write( resultstxt )
        
        if self.name is None :
            txtfile = txtfile + 'name =:= ' + '=@:None:@=' + '\n'
        else :
            txtfile = txtfile + 'name =:= ' + str( self.name ) + '\n'
        txtfile = txtfile + 'path =:= ' + str( self.path ) + '\n'
        txtfile = txtfile + 'start =:= ' + str( self.start ) + '\n'
        txtfile = txtfile + 'end =:= ' + str( self.end ) + '\n'
        txtfile = txtfile + 'wells =:= ' + str( self.wells ) + '\n'
        txtfile = txtfile + 'groups =:= ' + str( self.groups ) + '\n'
        txtfile = txtfile + 'regions =:= ' + str( self.regions ) + '\n'
        txtfile = txtfile + 'keys =:= ' + str( self.keys ) + '\n'
        
        # dump attributes dictionary to JSON file
        with open(Folder + fileName + '_storage/json/attributes.sro', 'w') as file:
            try :
                file.write(json.dumps( self.attributes ))
            except :
                file.write(str( self.attributes ))
        
        # prepare vectors as dataframe and dump to parquet
        DF_vectors = pd.DataFrame(self.vectors)
        DF_vectors.set_index('TIME',drop=False,inplace=True)
        DF_vectors.to_parquet(Folder + fileName + '_storage/parquet/vectors.sro' , index=True )
        
        # dump units dictionary to JSON file
        with open(Folder + fileName + '_storage/json/units.sro', 'w') as file:
            file.write(json.dumps( self.units )) 
            
        txtfile = txtfile + 'overwrite =:= ' + str( self.overwrite ) + '\n'
        txtfile = txtfile + 'null =:= ' + str( self.null ) + '\n'
        txtfile = txtfile + 'color =:= ' + str( self.color ) + '\n'
        txtfile = txtfile + 'restarts =:= ' + str( self.restarts ) + '\n'
        
        # prepare restart vectors as dataframe and dump to parquet
        if len(self.vectorsRestart) > 0 :
            DF_vectors = pd.DataFrame(self.vectorsRestart)
            DF_vectors.to_parquet(Folder + fileName + '_storage/parquet/restarts.sro' , index=True )
                              
        # txtfile = txtfile + 'pandasColumns =:= ' + str( self.pandasColumns ) + '\n'
        if self.fieldtime == (None,None,None) :
            txtfile = txtfile + 'fieldtime =:= ' + str(self.fieldtime) + '\n'
        else :
            txtfile = txtfile + 'fieldtime =:= ' + str( self.fieldtime[0] ) + ' =:= ' + str( self.fieldtime[1] ) + ' =:= ' + str( list(self.fieldtime[2]) ) + '\n'
            

        if self.kind == VIP :
            txtfile = txtfile + 'ECLstyle =:= ' + str( self.ECLstyle ) + '\n'
            txtfile = txtfile + 'VIPstyle =:= ' + str( self.VIPstyle ) + '\n'
            txtfile = txtfile + 'keysECL =:= ' + str( self.keysECL ) + '\n'
            txtfile = txtfile + 'keysVIP =:= ' + str( self.keysVIP ) + '\n'
            txtfile = txtfile + 'keysCSV =:= ' + str( self.keysCSV ) + '\n'
            if self.CSV == False :
                txtfile = txtfile + 'CSV =:= ' + str( False ) + '\n'
            else :
                txtfile = txtfile + 'CSV =:= ' + str( True ) + '\n'
            txtfile = txtfile + 'LPGcorrected =:= ' + str( self.LPGcorrected ) + '\n'
            
        # dump __init__ data to TXT file
        with open(Folder + fileName + '_storage/init.sro', 'w') as file:
            file.write( txtfile )
        with open(Folder + fileName + '.sro', 'w') as file:
            file.write( txtfile )
        
        
        
        
        
    def restore( self,FileNamePath ) :
        fileName , Ext , Folder , FullPath = extension(FileNamePath)

        
        RestorePath = Folder + fileName + '_storage/' 
        try:
            file = open(RestorePath+'init.sro','r')
        except :
            print( " the file " + FileNamePath +  "doesn't 'exist")
            return None
        
        txtfile = file.readlines()
        
        for line in txtfile :
            print(' reading: ' + line)
            key = line.split(' =:= ')[0]
            
            print('reading ', key , line.split(' =:= ')[1])
            if key == 'SimResult' :
                self.SimResult = bool( line.split(' =:= ')[1] )
            elif key == 'kind' :
                if 'ECL' in line.split(' =:= ')[1] :
                    self.kind = ECL
                elif 'VIP' in line.split(' =:= ')[1] :
                    self.kind = VIP
            elif key == 'name' :
                if line.split(' =:= ')[1] == '=@:None:@=' :
                    self.name = None
                else :
                    self.name = line.split(' =:= ')[1]
            elif key == 'path' :
                self.path = line.split(' =:= ')[1]
            elif key == 'start' :
                self.start = line.split(' =:= ')[1]
            elif key == 'end' :
                self.end = line.split(' =:= ')[1]
            elif key == 'wells' :
                self.wells = tuple(line.split(' =:= ')[1][1:-1].split(','))
            elif key == 'groups' :
                self.groups = tuple(line.split(' =:= ')[1][1:-1].split(','))
            elif key == 'regions' :
                self.regions = tuple(line.split(' =:= ')[1][1:-1].split(','))
            elif key == 'keys' :
                self.keys = tuple(line.split(' =:= ')[1][1:-1].split(','))
            elif key == 'overwrite' :
                self.overwrite = line.split(' =:= ')[1]
            elif key == 'null' :
                self.null = line.split(' =:= ')[1]
            elif key == 'color' :
                self.color = tuple(line.split(' =:= ')[1].split(','))
            elif key == 'restarts' :
                self.restarts = line.split(' =:= ')[1]
            elif key == 'ECLstyle' :
                self.ECLstyle = bool( line.split(' =:= ')[1] )
            elif key == 'VIPstyle' :
                self.VIPstyle = bool( line.split(' =:= ')[1] )
            
            elif key == 'keysECL' :
                self.keysECL = tuple(line.split(' =:= ')[1].split(','))
            elif key == 'keysVIP' :
                self.keysVIP = tuple(line.split(' =:= ')[1].split(','))
            elif key == 'keysCSV' :
                self.keysCSV = tuple(line.split(' =:= ')[1].split(','))
            elif key == 'CSV' :
                self.CSV = bool( line.split(' =:= ')[1] )
            elif key == 'LPGcorrected' :
                self.LPGcorrected = bool( line.split(' =:= ')[1] )
            elif key == 'fieldtime' :
                self.fieldtime = ( float(line.split(' =:= ')[1][1:]) , float(line.split(' =:= ')[2]) , np.array( line.split(' =:= ')[3][1:-2].split(',') , dtype='float' ) )
                
        if self.kind == ECL :
            pass
        elif self.kind == VIP :
            pass
            # count = 0

                        
        # load attributes dictionary to JSON file
        with open(RestorePath + 'json/attributes.sro', 'r') as file:
            self.attributes = json.load( file )
        
        # load vectors as dataframe and dump from parquet
        self.vectors = (pd.read_parquet( RestorePath + 'parquet/vectors.sro' )).to_dict()
        
        # dump units dictionary to JSON file
        with open(RestorePath + 'json/units.sro', 'r') as file:
            self.units = json.load( file )
            
        
                
class ECL(SimResult):
    """
    object to contain eclipse format results read from SMSPEC using libecl from equinor 
    """
    def __init__(self,inputFile=None,verbosity=2) :
        SimResult.__init__(self,verbosity=verbosity)
        self.kind = ECL
        if type(inputFile) == str and len(inputFile.strip()) > 0 :
            self.loadSummary(inputFile)

    def loadSummary(self,SummaryFilePath):
        if type(SummaryFilePath) == str :
            SummaryFilePath = SummaryFilePath.strip()
            if self.path is None :
                self.path = SummaryFilePath
            if extension(SummaryFilePath)[1] != '.SMSPEC' :
                newPath = extension(SummaryFilePath)[2] + extension(SummaryFilePath)[0] + '.SMSPEC'
                if os.path.isfile(newPath) :
                    SummaryFilePath = newPath
            if os.path.isfile(SummaryFilePath) :
                verbose( self.speak , 1 , ' > loading summary file:\n  ' + SummaryFilePath)
                self.results = ecl.summary.EclSum(SummaryFilePath)
                self.name = extension(SummaryFilePath)[0]
                self.set_FieldTime()
                self.get_Wells(reload=True)
                self.get_Groups(reload=True)
                self.get_Regions(reload=True)
                self.get_Keys(reload=True)
                self.units = self.get_Unit(self.keys)
                verbose( self.speak , 1 , 'simulation runs from ' +  str( self.get_Dates()[0] ) + ' to ' + str( self.get_Dates()[-1] ) )
                self.set_Vector('DATE' , self.get_Vector('DATES')['DATES'],self.get_Unit('DATES') , DataType='datetime' , overwrite=True)
                self.stripUnits()
                self.get_Attributes(reload=True)
                self.fill_FieldBasics()
                
            else :
                print("the file doesn't exists:\n  -> " + SummaryFilePath)
        else :
            print("SummaryFilePath must be a string")
        
    def reload(self) :
        self.loadSummary(self.path)
        
    # support functions for get_Vector:
    def loadVector(self,key) :
            """ 
            internal function to load a numpy vector from the summary files
            """
            if str(key).upper().strip() == "DATES" :
                return self.results.numpy_dates
            else :    
                return self.results.numpy_vector(str(key).upper().strip())  
    
    def set_FieldTime(self) :
        if len( self.get_Restart() ) > 0 :
            FieldTime = self.checkRestarts('TIME')['TIME']
        else :
            FieldTime = self.loadVector('TIME') 
        if FieldTime is None :
            if self.get_Vector('TIME')['TIME'] is not None :
                FieldTime = self.get_Vector('TIME')['TIME'] 
        if FieldTime is not None :
            self.fieldtime = ( min(FieldTime) , max(FieldTime) , FieldTime )          
    
    def get_Dates(self) :
        self.start = np.datetime64(self.results.start_date , 's' )
        try :
            self.end = self.results.end_date
        except :
            self.end = self.start + int(max(self.get_Vector('TIME')['TIME']))
        return self.results.numpy_dates
    
    def extract_Wells(self) :
        self.wells = self.results.wells() 
        return self.wells
    
    def get_Groups(self,pattern=None,reload=False) :
        """
        calls group method from libecl:
        
        Will return a list of all the group names in case.

        If the pattern variable is different from None only groups
        matching the pattern will be returned; the matching is based
        on fnmatch(), i.e. shell style wildcards.
        """
        if len(self.groups) == 0 or reload == True :
            self.groups = tuple( self.results.groups(pattern) )
        if pattern is None :
            return self.groups
        else:
            return tuple( self.results.groups(pattern) )
        
    def get_Keys(self,pattern=None,reload=False) :
        """
        Return a StringList of summary keys matching @pattern.

        The matching algorithm is ultimately based on the fnmatch()
        function, i.e. normal shell-character syntax is used. With
        @pattern == "WWCT:*" you will get a list of watercut keys for
        all wells.

        If pattern is None you will get all the keys of summary
        object.
        """
        if len(self.keys) == 0 or reload == True :
            self.keys = tuple( self.results.keys(pattern) )
            for extra in ( 'TIME' , 'DATE', 'DATES' ) :
                if extra not in self.keys :
                    self.keys = tuple( [extra] + list(self.keys) )
        if pattern is None :
            return self.keys
        else:
            return tuple( self.results.keys(pattern) )
        
    def extract_Regions(self,pattern=None) :
        # preparing object attribute
        regionsList = list( self.regions )
        for key in self.get_Keys() :
            if key[0] == 'R' :
                if ':' in key :
                    region = key.split(':')[1]
                    regionsList.append( region )
        regionsList = list( set( regionsList ))
        regionsList.sort()                
        self.regions = tuple( regionsList ) 
        # preparing list to return
        if pattern != None :
            regionsList = []
            for region in self.regions :
                if pattern in region :
                    regionsList.append(region)
            return tuple(regionsList)
        else :
            return self.regions
    
    def get_Unit(self,Key='--EveryType--') :
        """
        returns a string identifiying the unit of the requested Key
        
        Key could be a list containing Key strings, in this case a dictionary 
        with the requested Keys and units will be returned.
        the Key '--EveryType--' will return a dictionary Keys and units 
        for all the keys in the results file
        
        """
        if type(Key) is str and Key.strip() != '--EveryType--' :
            Key = Key.strip().upper()
            if Key in self.units :
                return self.units[Key]
            if Key == 'DATES' or Key == 'DATE' :
                    self.units[Key] = 'DATE'
                    return 'DATE'
            if Key in self.keys :
                return self.results.unit(Key)
            else:
                if Key[0] == 'W' :
                    UList=[]
                    for W in self.get_Wells() :
                        if Key+':'+W in self.units :
                            UList.append(self.units[Key+':'+W])
                        elif Key in self.keys :
                            UList.append( self.results.unit(Key+':'+W) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :                    
                        return None
                elif Key[0] == 'G' :
                    UList=[]
                    for G in self.get_Groups() :
                        if Key+':'+G in self.units :
                            UList.append(self.units[Key+':'+G])
                        elif Key in self.keys :
                            UList.append( self.results.unit(Key+':'+G) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :                    
                        return None
                elif Key[0] == 'R' :
                    UList=[]
                    for R in self.get_Regions() :
                        if Key+':'+R in self.units :
                            UList.append(self.units[Key+':'+R])
                        elif Key in self.keys :
                            UList.append( self.results.unit(Key+':'+R) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :                    
                        return None
                UList = None
                
        elif type(Key) is str and Key.strip() == '--EveryType--' :
            Key = []
            KeyDict = {}
            for each in self.keys :
                if ':' in each :
                    Key.append(self.mainKey(each))
                    KeyDict[self.mainKey(each)] = each
                else :
                    Key.append(each)
            Key = list( set (Key) )
            Key.sort()
            tempUnits = {}
            for each in Key :
                if each in self.units :
                    tempUnits[each] = self.units[each]
                elif each in self.keys and ( each != 'DATES' and each != 'DATE' ) :
                    if self.results.unit(each) is None :
                        tempUnits[each] = self.results.unit(each)
                    else :
                        tempUnits[each] = self.results.unit(each).strip('( )').strip("'").strip('"')
                elif each in self.keys and ( each == 'DATES' or each == 'DATE' ) :
                    tempUnits[each] = 'DATE'
                else :
                    if KeyDict[each] in self.units :
                        tempUnits[each] = self.units[KeyDict[each]]
                    elif KeyDict[each] in self.keys :
                        if self.results.unit(KeyDict[each]) is None :
                            tempUnits[each] = self.results.unit(KeyDict[each])
                        else :
                            tempUnits[each] = self.results.unit(KeyDict[each]).strip('( )').strip("'").strip('"')
            return tempUnits
        elif type(Key) == list or type(Key) == tuple :
            tempUnits = {}
            for each in Key :
                if type(each) == str :
                    tempUnits[each] = self.get_Unit(each) 
            return tempUnits
        
            

class VIP(SimResult):
    """
    object to contain VIP results read from .sss ASCII output 
    """
    def __init__(self,inputFile=None,verbosity=2) :
        SimResult.__init__(self,verbosity=verbosity)
        self.kind = VIP
        self.ECLstyle=True
        self.VIPstyle=False
        self.keysECL = ()
        self.keysVIP = ()
        self.keysCSV = ()
        self.results = {}
        self.CSV = False
        self.LPGcorrected = False
        if type(inputFile) == str and len(inputFile.strip()) > 0 :
            self.selectLoader(inputFile)
        self.complete_Units()
        self.stripUnits()
        self.fill_FieldBasics()
        self.get_Attributes(reload=True)
        
    def selectLoader(self,inputFile) :
        if type(inputFile) == str and len(inputFile.strip()) > 0 :
            inputFile = inputFile.strip()
        if extension(inputFile)[1].upper() == '.CSV' :
            self.loadCSV(inputFile) 
        elif extension(inputFile)[1].upper() == '.SSS' :
            self.loadSSS(inputFile)
        
    def use_ECLstyle(self):
        if len(self.keysECL) == 0 :
            verbose( self.speak , 0 , ' ECL style keys: ' + str( self.extract_Keys() ) )
        if len(self.keysECL) > 0 :
            self.keys = self.keysECL
            verbose( self.speak , 0 , 'attributes as ECL style: ' + str( self.get_Attributes() ) )
            self.ECLstyle = True
            self.VIPstyle = False
            verbose( self.speak , 3 , ' Using ECL style keys')
        else :
            self.VIPstyle = 'ERROR'
            verbose( self.speak , 3 , ' Unable to convert to ECL style keys')
            if type(self.ECLstyle) == bool :
                self.use_VIPstyle()
        self.complete_Units()

    def use_VIPstyle(self):
        if len(self.keysVIP) == 0 :
            verbose( self.speak , 0 , ' VIP style keys: ' + str( self.extract_Keys() ) )
        if len(self.keysVIP) > 0 :
            self.keys = self.keysVIP
            verbose( self.speak , 0 , 'attributes as VIP style: ' + str( self.get_Attributes() ) )
            self.ECLstyle = False
            self.VIPstyle = True
            verbose( self.speak , 3 , ' Using VIP style keys')
        else :
            self.ECLstyle = 'ERROR'
            verbose( self.speak , 3 , ' Unable to get VIP style keys.')
            if type(self.VIPstyle) == bool :
                self.use_ECLstyle()
        self.complete_Units()

    def get_Style(self) :
        if self.VIPstyle == True and self.ECLstyle == False :
            return 'using VIP style' 
        if self.ECLstyle == True and self.VIPstyle == False :
            return 'using ECL style'              
        return 'error in style, highly recommended to regenerate style'
    
    def loadCSV(self,CSVFilePath):
        """
        load data from CSV file exported from SimResults applicaion of the Nexus Desktop suite.
        """
        if type(CSVFilePath) == str and len(CSVFilePath.strip()) > 0 :
            CSVFilePath = CSVFilePath.strip()
        if os.path.isfile( CSVFilePath ) == False :
            raise FileNotFoundError('No such file found for: ' + str(CSVFilePath) )
        else :
            Temporal = self.CSVread( CSVFilePath )
            if Temporal != {} :
                if self.CSV == False :
                    self.CSV = {}
                self.CSV[extension(CSVFilePath)[0]] = Temporal
                self.CSVextractBacis()
                self.set_FieldTime()
                self.get_Vector('DATE')
                self.get_Wells(reload=True)
                self.CSVextractBacis()
                self.CSVextractHeaders()

    def loadSSS(self,SSSFilePath):
        if type(SSSFilePath) == str :
            SSSFilePath = SSSFilePath.strip()
            if self.path is None :
                self.path = SSSFilePath

            self.SSSfiles = self.SSSparts( SSSFilePath )
            self.name = extension(SSSFilePath)[0]
            for file in self.SSSfiles :
                self.results[ extension(file)[0] + extension(file)[1] ] = self.SSSread( file )
            self.strip('NAME')
            self.set_FieldTime()
            self.get_Vector('DATE')
            self.get_Wells(reload=True)
            self.get_Groups(reload=True)
            self.get_Regions(reload=True)
            self.get_Keys(reload=True)
            self.units = self.get_Unit(self.keys)
            verbose( self.speak , 1 , 'simulation runs from ' +  str( self.get_Dates()[0] ) + ' to ' + str( self.get_Dates()[-1] ) )
        else :
            print("SummaryFilePath must be a string")
    
    def correction_for_LPG_from_VIPsss(self) :
        if self.LPGcorrected :
            verbose( self.speak , 2 , 'LPG correction for VIP sss reports is already applied.')
        else :
            for LPGkey in ( 'LPG LIQ RATE' , 'FULPGLR'  ) :
                if self.is_Key( LPGkey ) :
                    Before = self.get_Vector(LPGkey)[LPGkey]
                    Corrected = Before * 0.1292 / 33.4962
                    self.set_Vector( LPGkey , Corrected , self.get_Unit(LPGkey) , DataType='float' , overwrite=True )
                    self.LPGcorrected = True
                    verbose( self.speak , 2 , 'Successfully applied LPG correction for VIP sss reports.')

    def CSVread(self,CSVFilePath) :
        """
        extract the data from the CSV file exported from SimResults applicaion of the Nexus Desktop suite.
        Pandas doesn't read this kind of CSV correctly.'
        """
        if self.path is None :
            self.path = CSVFilePath
        CSVfile = open(CSVFilePath,'r')
        CSVlines = CSVfile.read()
        CSVfile.close()
        CSVlines = CSVlines.split('\n')
        
        row = 0
        section = ''
        CSVdict = {}
        
        while row < len(CSVlines) :
            cell0 = CSVlines[ row ].split(',')[0].split('=')[0]
            if cell0 == '[S3INFO]' :
                section = cell0
                CSVdict[section] = {}
                
            elif cell0 == '[HEADERS]' :
                section = cell0
                CSVdict[section] = {}
                
            elif cell0 == '[DATA]' :
                section = cell0
                CSVdict[section] = []
                if '[' in ','.join( CSVlines[row+1:] ) and ']' in ','.join( CSVlines[row+1:] ) :
                    segmentEnd =','.join( CSVlines[row+1:] ).index('[')
                    CSVdict[section] = ','.join( CSVlines[row+1:] )[: segmentEnd ].split(',')
                    dataRows = len( CSVdict[section] ) / len( CSVdict['[HEADERS]']['VARIABLE'] )
                    if int(dataRows) == dataRows :
                        row = row + dataRows 
                    else :
                        pass
                else :
                    CSVdict[section] = ','.join( CSVlines[row+1:] ).split(',')
                    row = len(CSVlines)
            else :
                if '[' in CSVlines[ row ].split(',')[0].split('=')[0][0] and ']' in CSVlines[ row ].split(',')[0].split('=')[0][-1] :
                    section = CSVlines[ row ].split(',')[0].split('=')[0]
                else :
                    CSVdict[section][ cell0 ] = [ CSVlines[ row ].split(',')[0].split('=')[1] ] + CSVlines[ row ].split(',')[1:]
            row += 1
        return CSVdict

    def CSVextractBacis(self, CSVname='' ) :
        if CSVname == '' :
            CSVname = list( self.CSV.keys() )[-1]
        
        if self.name is None :
            try:
                self.name = self.CSV[CSVname]['[S3INFO]']['ORIGIN'][0]
            except :
                pass
        if self.start is None :
            try :
                self.start = np.datetime64( pd.to_datetime( self.CSV[CSVname]['[S3INFO]']['DATE'][0] ) ,'s')
            except:
                pass
        else :
            try :
                if self.start > np.datetime64( pd.to_datetime( self.CSV[CSVname]['[S3INFO]']['DATE'][0] ) ,'s') :
                    self.start = np.datetime64( pd.to_datetime( self.CSV[CSVname]['[S3INFO]']['DATE'][0] ) ,'s')
            except :
                pass
        try :        
            self.null = self.CSV[CSVname]['[S3INFO]']['NULLVALUE'][0]
            nullSet = True
        except :
            nullSet = False
        if nullSet == True :
            try :
                self.null = int(self.null)
            except :
                try :
                    self.null = float(self.null)
                except:
                    pass
    
    def CSVextractHeaders(self, CSVname='' ):
        if CSVname == '' :
            CSVname = list( self.CSV.keys() )[-1]
            
        CSVkeys = []
        ECLkeys = []
        VIPkeys = []
        CSVwells = []
        for i in range( len( self.CSV[CSVname]['[HEADERS]']['VARIABLE'] ) ):
            if len( self.CSV[CSVname]['[HEADERS]']['MEMBER'][i].strip() ) > 0 :
                self.units[ self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i] + ':' + self.CSV[CSVname]['[HEADERS]']['MEMBER'][i] ] = self.CSV[CSVname]['[HEADERS]']['UNITS'][i]
                if self.CSV[CSVname]['[HEADERS]']['CLASS'][i].strip().upper() == 'WELL' :
                    CSVwells += [ self.CSV[CSVname]['[HEADERS]']['MEMBER'][i].strip() ]
            else :
                self.units[ self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i] ] = self.CSV[CSVname]['[HEADERS]']['UNITS'][i]
            SimResult.CSV_Variable2Verbose[ self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i] ] = self.CSV[CSVname]['[HEADERS]']['VERBOSE'][i] 
            SimResult.CSV_Verbose2Variable[ self.CSV[CSVname]['[HEADERS]']['VERBOSE'][i] ] = self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i] 
            CSVkeys += [ self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i] +':' + self.CSV[CSVname]['[HEADERS]']['MEMBER'][i] ]
            ECLkey = self.fromCSVtoECL( variableORkey=self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i] , CLASStype=self.CSV[CSVname]['[HEADERS]']['CLASS'][i] , MEMBER=self.CSV[CSVname]['[HEADERS]']['MEMBER'][i] )
            if ECLkey != None :
                ECLkeys += [ ECLkey ]
                VIPkey , keyType , keyName = self.fromECLtoVIP( ECLkey )
                VIPkeys += [ VIPkey + ':' + keyName ]
            
            fullName = self.CSV[CSVname]['[HEADERS]']['CLASS'][i] + ':' + self.CSV[CSVname]['[HEADERS]']['MEMBER'][i] + ':' + self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i]
            self.pandasColumns[fullName] = [ self.CSV[CSVname]['[HEADERS]']['CLASS'][i] , self.CSV[CSVname]['[HEADERS]']['MEMBER'][i] , self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i] , self.CSV[CSVname]['[HEADERS]']['UNITS'][i] , self.CSV[CSVname]['[HEADERS]']['VERBOSE'][i] ]
        
        CSVwells = list ( set( list( self.wells ) + list( set( CSVwells ) ) ) )
        CSVwells.sort()
        self.wells = tuple ( CSVwells )
        self.keysCSV = tuple ( set( list( self.keysCSV ) + list( set( CSVkeys ) ) ) )
        self.keysVIP = tuple ( set(  list( self.keysVIP ) + list( set( VIPkeys ) ) ) )
        self.keysECL = tuple ( set(  list( self.keysECL ) + list( set( ECLkeys ) ) ) )
    
    def CSVextractVectors(self, CSVname ):
        numHeaders = len( self.CSV[CSVname]['[HEADERS]']['VARIABLE'] )
        
        for i in range( numHeaders ) :
            if len( self.CSV[CSVname]['[HEADERS]']['MEMBER'][i].strip() ) > 0 :
                CSVkey = self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i] + ':' + self.CSV[CSVname]['[HEADERS]']['MEMBER'][i]
            else :
                CSVkey = self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i]
            ECLkey = self.fromCSVtoECL( variableORkey=self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i] , CLASStype=self.CSV[CSVname]['[HEADERS]']['CLASS'][i] , MEMBER=self.CSV[CSVname]['[HEADERS]']['MEMBER'][i] )
            Vector = self.CSV[CSVname]['[DATA]'][i::numHeaders]
            while len(Vector) > 0 and Vector[-1] == '' :
                Vector = Vector[:-1]
            if len(Vector) > 0 :
                Unit = self.CSV[CSVname]['[HEADERS]']['UNITS'][i]
                verbose( self.speak , 1 , ' Setting vector for CSV key ' + CSVkey )
                self.set_Vector( Key=CSVkey , VectorData=Vector , Units=Unit , DataType='auto' , overwrite=True) 
                if ECLkey != None and len(ECLkey) > 0 :
                    verbose( self.speak , 1 , ' Setting vector for ECL key ' + ECLkey )
                    self.set_Vector( Key=ECLkey , VectorData=Vector , Units=Unit , DataType='auto' , overwrite=True) 
        
        if 'TIME' in self.CSV[CSVname]['[HEADERS]']['VARIABLE'] :
            iTIME = self.CSV[CSVname]['[HEADERS]']['VARIABLE'].index('TIME')
            start = np.datetime64( pd.to_datetime( self.CSV[CSVname]['[S3INFO]']['DATE'][0] ) ,'s')
            TIME = self.CSV[CSVname]['[DATA]'][iTIME::numHeaders]
            while len(TIME) > 0 and TIME[-1] == '' :
                TIME = TIME[:-1]
            DATE = np.empty(len(TIME), dtype='datetime64[s]')
            for i in range(len(TIME)) :
                DATE[i] = start + np.timedelta64( timedelta(days=TIME[i]) )  
                
    def get_csvVector(self, CSVname=None , CLASS='' , MEMBER='' , VARIABLE='' ):
        if CSVname is None :
            CSVnames = list( self.CSV.keys() )
        elif type(CSVname) == str :
            CSVnames = [ CSVname ]
        Results = {}
        # Unit = None
        # Verbose = None
        Data = None
        Vector = None
        for CSVname in CSVnames :
            verbose( self.speak , 1 , ' looking into the CSV ' + CSVname )
            numHeaders = len( self.CSV[CSVname]['[HEADERS]']['VARIABLE'] )
            
            # headers = {'CLASS' : [] , 'MEMBER' : [] , 'VARIABLE' : []}
            Results[CSVname] = {}
            for col in range( numHeaders ) :
                CLASSflag = False
                MEMBERflag = False
                VARIABLEflag = False
                                   
                if CLASS != '' and self.CSV[CSVname]['[HEADERS]']['CLASS'][col].strip() == MEMBER :
                    verbose( self.speak , 1 , 'mathcing CLASS')
                    CLASSflag = True
                elif CLASS == '' :
                    CLASSflag = True
                if MEMBER != '' and self.CSV[CSVname]['[HEADERS]']['MEMBER'][col].strip() == MEMBER :
                    verbose( self.speak , 1 , 'mathcing MEMBER')
                    MEMBERflag = True
                elif MEMBER == '' :
                    MEMBERflag = True
                if VARIABLE != '' and self.CSV[CSVname]['[HEADERS]']['VARIABLE'][col].strip() == MEMBER :
                    verbose( self.speak , 1 , 'mathcing VARIABLE')
                    VARIABLEflag = True
                elif VARIABLE == '' :
                    VARIABLEflag = True
                
                if CLASSflag * MEMBERflag * VARIABLEflag == 1 :
                    verbose( self.speak , 1 , '\nVECTOR ' + CLASS + ':' + MEMBER + ':' + VARIABLE + ' FOUND!\n')
                    Data = self.CSV[CSVname]['[DATA]'][col::numHeaders]
                    Data = tuple(Data)
                    Vector = list(Data)
                    while len(Vector) > 0 and Vector[-1] == '' :
                        Vector = Vector[:-1]
                    if len(Vector) > 0 :
                        Temp = []
                        Failed = True
                        if '.' in ' '.join(Vector) or 'E-' in ' '.join(Vector) or 'E+' in ' '.join(Vector):
                            for v in range(len(Vector)) :
                                try :
                                    Temp.append( float(Vector[v]) )
                                    Failed = False
                                except:
                                    break
                        else :
                            for v in range(len(Vector)) :
                                try :
                                    if Vector[v].isdigit() :
                                        Temp.append( int(Vector[v]) )
                                        Failed = False
                                    else :
                                        try :
                                            Temp.append( float(Vector[v]) )
                                            Failed = False
                                        except:
                                            break
                                except:
                                    break
                        if not Failed : 
                            Vector = np.array(Temp)
                        else :
                            Vector = np.array(Vector)
                    if CSVname not in Results :
                        Results[CSVname] = {}
                    Results[CSVname][col] = {}
                    Results[CSVname][col]['CLASS'] = self.CSV[CSVname]['[HEADERS]']['CLASS'][col]
                    Results[CSVname][col]['MEMBER'] = self.CSV[CSVname]['[HEADERS]']['MEMBER'][col]
                    Results[CSVname][col]['VARIABLE'] = self.CSV[CSVname]['[HEADERS]']['VARIABLE'][col]
                    Results[CSVname][col]['UNITS'] = self.CSV[CSVname]['[HEADERS]']['UNITS'][col]
                    Results[CSVname][col]['VERBOSE'] = self.CSV[CSVname]['[HEADERS]']['VERBOSE'][col]
                    Results[CSVname][col]['DATA'] = Data
                    Results[CSVname][col]['NumpyArray'] = Vector
        tot = 0
        for CSVname in CSVnames :
            tot += len( list( Results[CSVname].keys() ) )
        verbose( self.speak , 2 , ' ' + str(tot) + ' matches found for ' + CLASS + ':' + MEMBER + ':' + VARIABLE + '.')
        return Results
                
    def CSVloadVector(self, key , VIPkey='' , keyType='' , keyName='' , CSVname=None ):
        
        key = key.strip().upper()
        
        if key in ( 'DATE' , 'DATES' ) :
            DATEflag = key
            key = 'TIME'
        else :
            DATEflag = False
        
        keyword = key
        
        if CSVname is None :
            CSVnames = list( self.CSV.keys() )
        elif type(CSVname) == str :
            CSVnames = [ CSVname ]
        
        if keyName == '' :
            if ':' in key and len(key.split(':')[1])>0 :
                keyName = key.split(':')[1]
        else :
            keyName = keyName.strip()
        
        if keyType == '' :
            if ':' in key :
                if key.split(':')[1] in self.get_Wells() :
                    keyType = 'WELL'
            elif ':' in VIPkey :
                if VIPkey.split(':')[1] in self.get_Wells() :
                    keyType = 'WELL'
            elif key[0] == 'F' :
                keyType = 'FIELD'
                keyName = 'FIELD'
            elif key[0] == 'W' :
                keyType = 'WELL'

        Variable , Class , Member = self.fromECLtoCSV( key )
        
        if key in SimResult.UniversalKeys or VIPkey in SimResult.UniversalKeys :
            keyType = 'MISCELLANEOUS'
            keyName = ''
            if key in SimResult.UniversalKeys :
                keyword = key
            else : 
                keyword = VIPkey

        elif key in ( 'BHP' , 'THP' ) or VIPkey in ( 'BHP' , 'THP' ) :
            keyType == 'WELL'
            
        if keyName == 'ROOT' :
            keyName = 'FIELD'

        FOUNDflag = False
        for CSVname in CSVnames :
            numHeaders = len( self.CSV[CSVname]['[HEADERS]']['VARIABLE'] )
            verbose( self.speak , -1 , ' looking for vector for key: ' + str(key) + ' where variable=' + Variable + ', class=' + Class + ' or ' + keyType + ' and member=' + Member + ' or ' + keyName )
            for col in range( numHeaders ) :
                if ( self.CSV[CSVname]['[HEADERS]']['CLASS'][col] == keyType or self.CSV[CSVname]['[HEADERS]']['CLASS'][col] == Class ) and \
                   ( self.CSV[CSVname]['[HEADERS]']['MEMBER'][col] == keyName or self.CSV[CSVname]['[HEADERS]']['MEMBER'][col] == Member ) and \
                   ( self.CSV[CSVname]['[HEADERS]']['VARIABLE'][col] == Variable or self.CSV[CSVname]['[HEADERS]']['VARIABLE'][col] == keyword ) :
                    verbose( self.speak , -1 , ' found vector for key: ' + str(key) + ' where variable=' + self.CSV[CSVname]['[HEADERS]']['VARIABLE'][col] + ', class=' + self.CSV[CSVname]['[HEADERS]']['CLASS'][col] + ' and member=' + self.CSV[CSVname]['[HEADERS]']['MEMBER'][col] + '.' )
                    if len( self.CSV[CSVname]['[HEADERS]']['MEMBER'][col] ) > 0 :
                        CSVkey = self.CSV[CSVname]['[HEADERS]']['VARIABLE'][col] + ':' + self.CSV[CSVname]['[HEADERS]']['MEMBER'][col]
                    else :
                        CSVkey = self.CSV[CSVname]['[HEADERS]']['VARIABLE'][col]
                    ECLkey = self.fromCSVtoECL( variableORkey=self.CSV[CSVname]['[HEADERS]']['VARIABLE'][col] , CLASStype=self.CSV[CSVname]['[HEADERS]']['CLASS'][col] , MEMBER=self.CSV[CSVname]['[HEADERS]']['MEMBER'][col] )
                    Vector = self.CSV[CSVname]['[DATA]'][col::numHeaders]
                    while len(Vector) > 0 and Vector[-1] == '' :
                        Vector = Vector[:-1]
                    if len(Vector) > 0 :
                        Temp = []
                        Failed = True
                        if '.' in ' '.join(Vector) or 'E-' in ' '.join(Vector) or 'E+' in ' '.join(Vector):
                            for i in range(len(Vector)) :
                                try :
                                    Temp.append( float(Vector[i]) )
                                    Failed = False
                                except:
                                    break
                        else :
                            for i in range(len(Vector)) :
                                try :
                                    if Vector[i].isdigit() :
                                        Temp.append( int(Vector[i]) )
                                        Failed = False
                                    else :
                                        try :
                                            Temp.append( float(Vector[i]) )
                                            Failed = False
                                        except:
                                            break
                                except:
                                    break
                        if not Failed : 
                            Vector = np.array(Temp)
                        else :
                            Vector = np.array(Vector)
                        Unit = self.CSV[CSVname]['[HEADERS]']['UNITS'][col]
                        verbose( self.speak , 1 , ' Setting vector for CSV key ' + CSVkey )
                        self.set_Vector( Key=CSVkey , VectorData=Vector , Units=Unit , DataType='auto' , overwrite=True) 
                        if ECLkey != None and len(ECLkey) > 0 :
                            verbose( self.speak , 1 , ' Setting vector for ECL key ' + ECLkey )
                            self.set_Vector( Key=ECLkey , VectorData=Vector , Units=Unit , DataType='auto' , overwrite=True) 
                        FOUNDflag = True
                        if type(DATEflag) == str  :
                            verbose( self.speak , 1 , ' Creating date vector for CSV key ' + DATEflag )
                            start = np.datetime64( pd.to_datetime( self.CSV[CSVname]['[S3INFO]']['DATE'][0] ) , 's' )
                            TIME = self.vectors['TIME']
                            DATE = np.empty(len(TIME), dtype='datetime64[s]')
                            for i in range(len(TIME)) :
                                DATE[i] = start + np.timedelta64( timedelta(days=TIME[i]) )  
                            self.vectors[DATEflag] = DATE
                            self.units[DATEflag] = 'DATE'
                        break
        
        if FOUNDflag == False :
            verbose( self.speak , 2 , 'vector corresponding to key ' + key + ' not found in CSV data.')
        else :
            if type(DATEflag) == str :
                return DATE
            else:
                return Vector
    
    def CSVgenerateResults(self) :
        for CSVname in list( self.CSV.keys() ) :
            self.CSV[CSVname] = self.CSV[CSVname]
            numHeaders = len( self.CSV[CSVname]['[HEADERS]']['VARIABLE'] )
            numRows = int( len( self.CSV[CSVname]['[DATA]'] ) / numHeaders )

            # generate the diccionaries for every CLASS:
            verbose( self.speak , 3 , ' generating raw data dictionary from CSV table,\n  > preparing results dictionary\n    ... please wait ...')
            for sss in list( set( self.CSV[CSVname]['[HEADERS]']['CLASS'] ) ) :
                if sss not in self.results.keys() :
                    self.results[ str(sss) + '@' + extension(self.path)[0]+extension(self.path)[1] ] = ( str(sss) , { 'Data':{} , 'Units':{} } ) 
            
            # generate Units dictionary
            verbose( self.speak , 3 , '  > loading units\n    ... please wait ...')
            for i in range( numHeaders ) :
                self.results[ self.CSV[CSVname]['[HEADERS]']['CLASS'][i] + '@' + extension(self.path)[0]+extension(self.path)[1] ][1]['Units'][ self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i] ] = self.CSV[CSVname]['[HEADERS]']['UNITS'][i]
            
            # load the series from [DATA] into results dictionary
            verbose( self.speak , 3 , '  > transforming and loading data series\n    ... please wait ...')
            for i in range( numHeaders ) :
                Vector = self.CSV[CSVname]['[DATA]'][i::numHeaders]
                while len( Vector ) > 0 and Vector[-1] == '' :
                    Vector = Vector[:-1]
                if len(Vector) != numRows :
                    print('issue with rows', len(Vector) , numRows )
                if len( self.CSV[CSVname]['[HEADERS]']['MEMBER'][i] ) > 0 :
                    Name = self.CSV[CSVname]['[HEADERS]']['MEMBER'][i]
                else :
                    Name = 'ROOT'
                self.results[ self.CSV[CSVname]['[HEADERS]']['CLASS'][i] + '@' + extension(self.path)[0]+extension(self.path)[1] ][1]['Data'][ self.CSV[CSVname]['[HEADERS]']['VARIABLE'][i]+':'+Name ] = Vector
            verbose( self.speak , 3 , '  > DONE! results dictionary generated.')
        
        verbose( self.speak , 3 , '  > checking the transformed data\n    ... please wait ...')
        OK = True
        for CSV in list( self.results.keys() ) :
            KEYsLenght = []
            for KEY in list( self.results[CSV][1]['Data'].keys() ) :
                KEYsLenght.append( len( self.results[CSV][1]['Data'][KEY] ) )
            if max(KEYsLenght) == min(KEYsLenght) :
                verbose( self.speak , 3 , '  > ' + str(CSV) + ' properly created with ' + str( numHeaders ) + ' columns and ' + str( max(KEYsLenght) ) + ' rows.')
            else :
                print( max(KEYsLenght) , min(KEYsLenght) , numRows)
                verbose( self.speak , -1 , '  > ' + str(CSV) + ' issue: ' + str( numHeaders ) + ' columns and ' + str( max(KEYsLenght) ) + ' rows.')
                OK = False
        
        if OK :
            verbose( self.speak , 3 , '  > DONE! results dictionary generated.')
        else :
            verbose( self.speak , -1 , '  > results dictionary generated with issues.')
        
    def reload(self) :
        if self.CSV == False :
            self.loadSSS(self.path)
        else :
            self.loadCSV(self.path)
    
    def strip(self,VIPkey,stringToStrip=' ') :
        """
        applies .strip() method to every item in a Key of the results dictionaries
        """
        for sss in self.results.keys() :
            for i in range(len( self.results[sss][1]['Data'][ VIPkey ] )) :
                if type( self.results[sss][1]['Data'][ VIPkey ][i] ) == str :
                    self.results[sss][1]['Data'][ VIPkey ][i] = self.results[sss][1]['Data'][ VIPkey ][i].strip(stringToStrip)
    
    def SSSparts(self,SSSFilePath):
        SSSfiles = []
        expectedParts = [ ( '_field.sss' , '_area.sss' , '_flow.sss' , '_gather.sss' , '_region.sss' , '_well.sss' ) ,
                          ( '_FIELD.SSS' , '_AREA.SSS' , '_FLOW.SSS' , '_GATHER.SSS' , '_REGION.SSS' , '_WELL.SSS' ) ]
        if extension(SSSFilePath)[1].upper() == '.SSS' :
            for Case in expectedParts :
                for part in Case :
                    if part in SSSFilePath and SSSFilePath[SSSFilePath.index(part):] == part:
                        SSSroot = SSSFilePath[:SSSFilePath.index(part)]
                        break
                for part in Case :
                    if os.path.isfile(SSSroot + part) :
                        SSSfiles.append(SSSroot + part)
                if len( SSSfiles ) > 0 :
                    return tuple( SSSfiles )
            if os.path.isfile(SSSFilePath) : # if this line is reached, implicitly len( SSSfiles ) == 0 
                return tuple ( SSSFilePath )
            else :
                raise FileNotFoundError('No such file or related VIP files found for: ' + str(SSSFilePath) )
        
        else : # if extension(SSSFilePath)[1] != '.SSS' : 
            SSSroot = extension(SSSFilePath)[2] + extension(SSSFilePath)[0]
            for Case in expectedParts :
                for part in Case :
                    if os.path.isfile(SSSroot + part) :
                        SSSfiles.append(SSSroot + part)
                if len( SSSfiles ) > 0 :
                    return tuple( SSSfiles )
        
        if len( SSSfiles ) == 0 :
            raise FileNotFoundError('No such file or related VIP files found for: ' + str(SSSFilePath) )
    
    def SSSread(self,sssPath) :
        verbose( self.speak , 1 , '\nREADING ' + str(sssPath) )
        sssfile = open(sssPath,'r')
        sss = sssfile.read()
        sssfile.close()
        sss = sss.split('\n')
        
        sssType = sss[0].split()[0]
        verbose( self.speak , 1 , 'Type of data in this input file: ' + str(sssType) )
        
        sssColumns = sss[1].split('\t')
        for i in range(len(sssColumns)):
            sssColumns[i] = sssColumns[i].strip()
            
        sssUnits = sss[2].split('\t')
        for i in range(len(sssUnits)):
            sssUnits[i] = sssUnits[i].strip()
        
        sssClean = []
        for i in range(len(sss[3:])) :
            if len(sss[3+i].strip()) > 0 :
                sssClean.append(sss[3+i])
                    
        sssData = []
        sssData = '\t'.join(sssClean).split('\t')
        
        sssDict = { 'Data' : {} , 'Units' : {} }
        
        for i in range(len(sssColumns)) :
            sssDict['Data'][sssColumns[i]] = sssData[i::len(sssColumns)]
        for i in range(len(sssColumns)) :
            sssDict['Units'][sssColumns[i]] = sssUnits[i]
        
        if self.speak !=0 :
            verbose( self.speak , 1 ,' data found in the ' + str(sssType) + ' summary file:')
            for each in sssDict['Data'] :
                verbose( self.speak , 1 ,'  > ' + str(each) + str( ' ' * (16-len(str(each))) ) + ' with ' + str(len(sssDict['Data'][each])) + ' rows with units: ' + str( sssDict['Units'][each] ) )
        
        return ( sssType , sssDict )

    # support functions for get_Vector:
    def loadVector(self,key,SSStype=[],forceVIP=False) :
        """ 
        internal function to load a numpy vector from the summary files
        """
        def fromECLtoVIP(key) :
            return self.fromECLtoVIP(key)

        def alreadyVIP(key,SSStype):
            wellVIPkeys = ('BHP','THP')
            if ':' in key :
                VIPkey = key[:key.index(':')]
                keyName = key[key.index(':')+1:]
            else :
                VIPkey = key
                if key in wellVIPkeys :
                    keyName = list(self.get_Wells())
                    SSStype = ['WELL']
                elif VIPkey in SimResult.UniversalKeys :
                    keyName = 'ROOT'
                    SSStype = ['FIELD']
                else :
                    keyName = 'ROOT'
            if len( SSStype ) > 1 :
                if keyName == 'ROOT' :
                    keyType = 'FIELD'
                else :
                    verbose( self.speak, 2 , 'none or more than one type summary were selected,  ')
                    keyType = SSStype
            else :
                keyType = SSStype[0]
            
            verbose( self.speak , 1 ,'identified VIP key ' + VIPkey + ' for ' + str(keyType) + ' summary for the item ' + keyName )
            return VIPkey , keyType , keyName
            
      ####################### end of auxiliar functions #######################
        
        if SSStype == [] and self.CSV == False:
            for sss in list(self.results.keys()) :
                SSStype += [self.results[sss][0]]
        elif type(SSStype) == str :
            SSStype = [SSStype]
        
        key = str(key).strip().upper()
        if forceVIP :
            verbose( self.speak , 1 , 'forced to use inputs as VIP keywords')
        if self.ECLstyle == True and forceVIP == False:
            # if key in self.keysECL :
            try :
                VIPkey , keyType , keyName = fromECLtoVIP(key)
            except :
                try :
                    VIPkey , keyType , keyName = alreadyVIP(key,SSStype)
                except :
                    pass
                    
        else : # VIP style first
            try :
                VIPkey , keyType , keyName = alreadyVIP(key,SSStype)
            except :
                try :
                    VIPkey , keyType , keyName = fromECLtoVIP(key)
                except :
                    pass
        
        if type(keyType) == str :
            keyTypeList = tuple([keyType])
        else :
            keyTypeList = tuple(keyType[:])
        
        
        ###### in case of CSV load :
        if self.CSV != False :
            return self.CSVloadVector( key , VIPkey , keyType , keyName ) 
        ###### in case of CSV load.
        
        for keyType in keyTypeList :
            
            if keyType in SSStype :
                if keyType == 'FIELD' :
                    for sss in list(self.results.keys()) :
                        if self.results[sss][0] == keyType :
                            if VIPkey in self.results[sss][1]['Data'].keys() :
                                RawCol = np.array( self.results[sss][1]['Data'][ VIPkey ] )
                                verbose( self.speak , 1 ,'extracted ' + VIPkey + ' from ' + keyType + ' with lenght ' + str(len(RawCol)) )
                                try :
                                    RawCol = RawCol.astype(int)
                                    verbose( self.speak , 1 , 'the values were converted to integer type')
                                except :
                                    try :
                                        RawCol = RawCol.astype(float)
                                        verbose( self.speak , 1 ,'the values were converted to floating point type')
                                    except :
                                        verbose( self.speak , 1 , 'the values are treated as string type')
                                return RawCol
                else :
                    for sss in list(self.results.keys()) :
                        if self.results[sss][0] == keyType :
                            if VIPkey in self.results[sss][1]['Data'].keys() :
                                RawCol = np.array( self.results[sss][1]['Data'][ VIPkey ] ) 
                                NameCol = np.array( self.results[sss][1]['Data'][ 'NAME' ] )
                                TimeCol = np.array( self.results[sss][1]['Data'][ 'TIME' ] )
                                verbose( self.speak , 1 ,'extracted ' + VIPkey + ' from ' + keyType + ' with lenght ' + str(len(RawCol)) )
                                verbose( self.speak , 0 ,'extracted ' + 'NAME' + ' from ' + keyType + ' with lenght ' + str(len(NameCol)) )
                                verbose( self.speak , 0 ,'extracted ' + 'TIME' + ' from ' + keyType + ' with lenght ' + str(len(NameCol)) )
                                try :
                                    RawCol = RawCol.astype(int)
                                    verbose( self.speak , 1 , 'the values were converted to integer type')
                                except :
                                    try :
                                        RawCol = RawCol.astype(float)
                                        verbose( self.speak , 1 ,'the values were converted to floating point type')
                                    except :
                                        verbose( self.speak , 1 , 'the values are treated as string type')
                                
                                if type(keyName) == str :
                                    verbose( self.speak , 1 ,'filtering data for item: ' + keyName)    
                                    CleanCol = np.extract( np.char.equal( NameCol , keyName ) , RawCol )
                                    CleanTime = np.extract( np.char.equal( NameCol , keyName ) , TimeCol )
                                    verbose( self.speak , 1 , 'extracting ' + VIPkey + ' with lenght ' + str(len(CleanCol))  + ' for item ' + keyName + '.')
                                elif len(keyName) == 1 :
                                    keyName = keyName[0]
                                    verbose( self.speak , 2 ,'the item name was not especified by only one options ( ' + keyName + ' ) has been found for the key : ' + key ) 
                                    verbose( self.speak , 1 ,'filtering data for item: ' + keyName )    
                                    CleanCol = np.extract( np.char.equal( NameCol , keyName ) , RawCol )
                                    CleanTime = np.extract( np.char.equal( NameCol , keyName ) , TimeCol )
                                    verbose( self.speak , 1 , 'cleaned ' + VIPkey + ' with lenght ' + str(len(CleanCol)) + ' for item ' + keyName + '.' )
                                else :
                                    verbose( self.speak , 2 ,'multiple ( ' + str(len(keyName)) + ' ) item options found for the key : ' + key + ':\n' + str(keyName) ) 
                                    CleanCol = np.array([],dtype='float')
                                    CleanTime = np.array([],dtype='float')
                                
                                if len(CleanCol) > 0 :
                                    CleanCol = self.fillZeros( CleanCol , CleanTime ) 

                                return CleanCol

    def set_FieldTime(self) :
        if len( self.get_Restart() ) > 0 :
            FieldTime = self.checkRestarts('TIME')['TIME']
        else :
            FieldTime = self.loadVector('TIME',SSStype=['FIELD']) 
        if FieldTime is None :
            if self.get_Vector('TIME')['TIME'] is not None :
                FieldTime = self.get_Vector('TIME')['TIME'] 
        if FieldTime is not None :
            self.fieldtime = ( min(FieldTime) , max(FieldTime) , FieldTime )
        
    
    def get_Dates(self) :
        self.set_Vector( 'DATES' , np.array( pd.to_datetime( strDate( list( self.loadVector('DATE','FIELD',True) ) , speak=(self.speak==1)) ) , dtype='datetime64[s]') , self.get_Unit('DATE') , DataType='datetime64' , overwrite=True )
        #self.set_Vector( 'DATES' , np.array( pd.to_datetime( self.get_Vector('DATE')['DATE'] ) , dtype='datetime64[s]') , self.get_Unit('DATE') , DataType='datetime64' , overwrite=True )
        self.set_Vector( 'DATE' , self.get_Vector('DATES')['DATES'] , self.get_Unit('DATES') , overwrite=True )
        self.start = min( self.get_Vector('DATE')['DATE'] )
        self.end = max( self.get_Vector('DATE')['DATE'] )
        return self.get_Vector('DATE')['DATE']
    
    def extract_Wells(self) : #,pattern=None) :
        # preparing object attribute
        wellsList = list( self.wells )
        if self.CSV == False :
            for sss in self.results :
                if self.results[sss][0] == 'WELL' :
                    wellsList += ( ' '.join( self.results[sss][1]['Data']['NAME'] ).split() ) 
        else :
            for CSVname in self.CSV :
                for i in range( len( self.CSV[CSVname]['[HEADERS]']['VARIABLE'] ) ):
                    if len( self.CSV[CSVname]['[HEADERS]']['MEMBER'][i].strip() ) > 0 :
                        if self.CSV[CSVname]['[HEADERS]']['CLASS'][i].strip().upper() == 'WELL' :
                            wellsList += [ self.CSV[CSVname]['[HEADERS]']['MEMBER'][i].strip() ]
        wellsList = list( set( wellsList ) )
        wellsList.sort()
        self.wells = tuple( wellsList ) 

        return self.wells
            
    def get_Groups(self,pattern=None,reload=False) :
        """
        Will return a list of all the group names in case.

        If the pattern variable is different from None only groups
        matching the pattern will be returned; the matching is based
        on fnmatch(), i.e. shell style wildcards.
        """
        if len(self.groups) == 0 or reload == True :
            self.groups = tuple( self.extract_Areas(pattern) )
        if pattern is None :
            return self.groups
        else:
            return tuple( self.extract_Areas(pattern) )
    
    def extract_Areas(self,pattern=None) :
        # preparing object attribute
        areaList = list( self.groups )
        for sss in self.results :
            if self.results[sss][0] == 'AREA' :
                areaList += ( ' '.join( self.results[sss][1]['Data']['NAME'] ).split() ) 
        areaList = list( set( areaList ) )
        areaList.sort()
        self.groups = tuple( areaList ) 
        # preparing list to return
        if pattern != None :
            areaList = []
            for group in self.groups :
                if pattern in group :
                    areaList.append(group)
            return tuple(areaList)
        else :
            return self.groups
        
    def extract_Regions(self,pattern=None) :
        # preparing object attribute
        regionsList = list( self.regions )
        if self.CSV == False :
            for sss in self.results :
                if self.results[sss][0] == 'REGION' :
                    regionsList += ( ' '.join( self.results[sss][1]['Data']['NAME'] ).split() ) 
        else :
            pass
        regionsList = list( set( regionsList ) )
        regionsList.sort()
        self.regions = tuple( regionsList ) 
        # preparing list to return
        if pattern != None :
            regionsList = []
            for region in self.regions :
                if pattern in region :
                    regionsList.append(region)
            return tuple(regionsList)
        else :
            return self.regions
    
    def add_Key(self,Key,SSStype=None) :
        if type(Key) == str :
            Key = Key.strip()
            if self.ECLstyle :
                self.keys = tuple( set( list(self.get_Keys()) + [Key] ) )
                self.keysECL = tuple( set( list(self.get_Keys()) + [Key] ) )
                VIPkey , keyType , keyName = self.fromECLtoVIP(Key)
                self.keysVIP = tuple( set( list(self.get_Keys()) + [ VIPkey +':'+ keyName ] ) )
            else :
                self.keys = tuple( set( list(self.get_Keys()) [Key] ) )
                self.keysVIP = tuple( set( list(self.get_Keys()) + [Key] ) )
                ECLkey = self.fromVIPtoECL(Key,SSStype)
                self.keysECL = tuple( set( list(self.get_Keys()) + [ECLkey] ) )
            
        else :
            raise TypeError('Key must be string')
    
    def get_Keys(self,pattern=None,reload=False) :
        """
        Return a StringList of summary keys matching @pattern.

        The matching algorithm is ultimately based on the fnmatch()
        function, i.e. normal shell-character syntax is used. With
        @pattern == "WWCT:*" you will get a list of watercut keys for
        all wells.

        If pattern is None you will get all the keys of summary
        object.
        """
        if self.ECLstyle :
            self.keys = self.keysECL
        else :
            self.keys = self.keysVIP
        
        if len(self.keys) == 0 or reload == True :
            self.keys = []
            self.keys +=  list( self.extract_Keys(pattern) )
            for extra in ( 'TIME' , 'DATE' , 'DATES' ) :
                if extra not in self.keys :
                    self.keys.append(extra) 
            self.keys = tuple( self.keys )
        if pattern is None :
            if self.ECLstyle == True :
                return self.keysECL
            elif self.VIPstyle == True :
                return self.keysVIP
            else :
                return self.keys
        else:
            return tuple( self.extract_Keys(pattern) )
    
    def extract_Keys(self,pattern=None,SSStoExtract=None) :
        # preparing object attribute
        keysList = list( self.keys )
        keysListVIP = list( self.keysVIP )
        keysListECL = list( self.keysECL )
        
        if SSStoExtract is None :
            SSStoExtract = list(self.results.keys())
        for sss in SSStoExtract :
            if self.results[sss][0] in SimResult.VIPTypesToExtractVectors :
                names = list(set( ' '.join( self.results[sss][1]['Data']['NAME'] ).split() ))
                atts = list( self.results[sss][1]['Data'].keys() )
               
                for att in atts :
                    attECL = self.fromVIPtoECL( att , self.results[sss][0] )
                    if attECL is None :
                        SimResult.VIPnotECL.append( self.results[sss][0] + ' : ' + att )
                        attECL = ''
                    for name in names :
                        keysListVIP.append( att + ':' + name )
                        if self.results[sss][0] == 'FIELD' and attECL != '' :
                            keysListECL.append( attECL )
                        elif self.results[sss][0] in SimResult.VIP2ECLtype and attECL != '' :
                            keysListECL.append( attECL + ':' + name )
        
        if len(SimResult.VIPnotECL) > 0 :
            verbose( self.speak , -1 , '\nsome VIP attributes was not recognized as ECL style attributes,\nto get a report of these attributes use the method:\n  .report_VIP_AttributesNotTo_ECL() \n')                
        keysListVIP = list( set( keysListVIP ) )
        keysListVIP.sort()
        self.keysVIP = tuple( keysListVIP ) 
        keysListECL = list( set( keysListECL ) )
        keysListECL.sort()
        self.keysECL = tuple( keysListECL ) 
        # preparing list to return
        if pattern != None :
            keysList = []
            for key in self.keysVIP :
                if pattern in key :
                    keysList.append(key)
            if len(keysList) > 0 : 
                return tuple(keysList)
            keysList = [] # redundante
            for key in self.keysECL :
                if pattern in key :
                    keysList.append(key)
            if len(keysList) > 0 : 
                return tuple(keysList)
        else :
            if self.ECLstyle == True :
                return self.keysECL
            elif self.VIPstyle == True :
                return self.keysVIP
            else :
                return self.keys
    
    def get_Unit(self,Key='--EveryType--') :
        """
        returns a string identifiying the unit of the requested Key
        
        Key could be a list containing Key strings, in this case a dictionary 
        with the requested Keys and units will be returned.
        the Key '--EveryType--' will return a dictionary Keys and units 
        for all the keys in the results file
        
        """
        if type(Key) is str and Key.strip() != '--EveryType--' :
            Key = Key.strip().upper()
            if Key in self.units :
                if self.units[Key] is not None:
                    return self.units[Key]
                else : # if self.units[Key] is None:
                    if ':' in Key :
                        if self.mainKey(Key) in self.units :
                            if self.units[ self.mainKey(Key) ] is not None :
                                return self.units[ self.mainKey(Key) ]
                            else :
                                return self.extract_Unit(Key)
            if Key == 'DATES' or Key == 'DATE' :
                    self.units[Key] = 'DATE'
                    return 'DATE'
            if Key in self.keys :
                return self.extract_Unit(Key)
            else:
                if Key[0] == 'W' :
                    UList=[]
                    for W in self.get_Wells() :
                        if Key+':'+W in self.units :
                            UList.append(self.units[Key+':'+W])
                        elif Key+':'+R in self.keys :
                            UList.append( self.extract_Unit(Key+':'+W) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :                    
                        return None
                elif Key[0] == 'G' :
                    UList=[]
                    for G in self.get_Groups() :
                        if Key+':'+G in self.units :
                            UList.append(self.units[Key+':'+G])
                        elif Key+':'+R in self.keys :
                            UList.append( self.extract_Unit(Key+':'+G) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :                    
                        return None
                elif Key[0] == 'R' :
                    UList=[]
                    for R in self.get_Regions() :
                        if Key+':'+R in self.units :
                            UList.append(self.units[Key+':'+R])
                        elif Key+':'+R in self.keys :
                            UList.append( self.extract_Unit(Key+':'+R) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :                    
                        return None
                UList = None
                
        elif type(Key) is str and Key.strip() == '--EveryType--' :
            Key = []
            KeyDict = {}
            for each in self.keys :
                if ':' in each :
                    Key.append(self.mainKey(each))
                    KeyDict[self.mainKey(each)] = each
                else :
                    Key.append(each)
            Key = list( set (Key) )
            Key.sort()
            tempUnits = {}
            for each in Key :
                if each in self.units :
                    tempUnits[each] = self.units[each]
                elif each in self.keys and ( each != 'DATES' and each != 'DATE' ) :
                    tempUnits[each] = self.extract_Unit(each)
                elif each in self.keys and ( each == 'DATES' or each == 'DATE' ) :
                    tempUnits[each] = 'DATE'
                else :
                    if KeyDict[each] in self.units :
                        tempUnits[each] = self.units[KeyDict[each]]
                    elif KeyDict[each] in self.keys :
                        if self.extract_Unit(KeyDict[each]) is None :
                            tempUnits[each] = self.extract_Unit(KeyDict[each])
                        else :
                            tempUnits[each] = self.extract_Unit(KeyDict[each]).strip('( )').strip("'").strip('"')
            return tempUnits
        elif type(Key) == list or type(Key) == tuple :
            tempUnits = {}
            for each in Key :
                if type(each) == str and each.strip() in self.units :
                    tempUnits[each] = self.units[each.strip()]
                if type(each) == str and ( each.strip() == 'DATES' or each.strip() == 'DATE' ) :
                    tempUnits[each] = 'DATE'
                elif type(each) == str and each.strip() in self.keys :
                    if self.extract_Unit(each.strip()) is None :
                        tempUnits[each] = self.extract_Unit(each.strip())
                    else :
                        tempUnits[each] = self.extract_Unit(each.strip()).strip('( )').strip("'").strip('"')
            return tempUnits
    
    def extract_Unit(self,Key) :
        for sss in list(self.results.keys()) :
            for Vector in list(self.results[sss][1]['Units'].keys()) :
                if Vector == 'DATE' or Vector == 'DATES' :
                    self.units[Vector] = 'DATE'
                else :
                    if self.ECLstyle == True :
                        ECLkey = self.fromVIPtoECL( Vector , self.results[sss][0] )
                        if ECLkey != None :                       
                            self.units[ ECLkey ] = self.results[sss][1]['Units'][Vector].strip('( )').strip("'").strip('"')
                    if self.VIPstyle == True :
                        self.units[Vector] = self.results[sss][1]['Units'][Vector].strip('( )').strip("'").strip('"')
        Key = Key.strip()
        if self.ECLstyle == True :   
            if Key in self.units :
                return self.units[Key]
            elif Key in SimResult.ECL2VIPkey and SimResult.ECL2VIPkey[Key] in self.units :
                return self.units[ self.fromECLtoVIP(Key) ]
        if self.VIPstyle == True :
            if Key.strip() in self.units :
                return self.units[Key]
            elif Key in SimResult.VIP2ECLkey and SimResult.VIP2ECLkey[Key] in self.units :
                return self.units[ self.fromVIPtoECL[Key] ]
    
    def complete_Units(self) :
        for key in list(self.units.keys()) :
            if self.units[key] is None :
                if ':' in key :
                    self.units[key] = self.extract_Unit(key)
                    if self.units[key] is None :
                        self.units[key] = self.extract_Unit(key[:key.index(':')])
                        if self.units[key] is None :
                            VIPkey = self.fromECLtoVIP(key)
                            for sss in self.results :
                                self.units[key] = self.results[ VIPkey[1] ][1]['Units'][ VIPkey[0] ].strip('( )').strip("'").strip('"')
                                if self.units[key] is None :
                                    break
                    if self.units[key] is None :
                        verbose( self.speak , 3 , 'impossible to found unit system for key ' + key )
                    else :
                        verbose( self.speak , 1 , 'found unit system ' + self.units[key] + ' for key ' + key )
                else :
                    self.units[key] = self.extract_Unit(key)
                    if self.units[key] is None :
                        VIPkey = self.fromECLtoVIP(key)
                        for sss in self.results :
                            self.units[key] = self.results[ VIPkey[1] ][1]['Units'][ VIPkey[0] ].strip('( )').strip("'").strip('"')
                            if self.units[key] is None :
                                    break
                    if self.units[key] is None :
                        verbose( self.speak , 3 , 'impossible to found unit system for key ' + key )
                    else :
                        verbose( self.speak , 1 , 'found unit system ' + self.units[key] + ' for key ' + key )
                    
    def OUTPAVG(KeyArguments=None,ECLkey=None) :
        if ECLkey is not None :
            if type(ECLkey) is str :
                ECLkey = ECLkey.strip()
                if self.is_Key(ECLkey) :
                    print(" WARNING: the keyword '" + ECLkey + "' already exists here, do you want to overwrite?" )
                    user = ''
                    while user.upper() not in ['Y','YES','N','NO','NOT','SI','SÍ','OUI'] :
                        user = input('please write YES or NO: ')
                    if user in ['Y','YES','SI','SÍ','OUI'] :
                        if ':' in ECLkey :
                            if self.is_Key( 'WBP:'+ECLkey.split(':')[1] ) :
                                self.set_Vector( Key=ECLkey , VectorData=self('WBP:'+ECLkey.split(':')[1]) , Units=self.get_Unit('WBP:'+ECLkey.split(':')[1]) , DataType='float' , overwrite=True ) 
                            else :
                                verbose( self.speak , -1 , " the corresponding well for the key '" + mainKey(ECLkey) + "' does not have WBP here.")
                        else :
                            verbose( self.speak , -1 , " the well name can not be found in the key '" + ECLkey + "'\n use .set_Vector() method to set an especific key")
                elif self.is_Att(ECLkey) :
                    print(" WARNING: the attribute '" + ECLkey + "' already exists here, do you want to overwrite this attribute for all the wells?" )
                    user = ''
                    while user.upper() not in ['Y','YES','N','NO','NOT','SI','SÍ','OUI'] :
                        user = input('please write YES or NO: ')
                    if user in ['Y','YES','SI','SÍ','OUI'] :
                        for W in self.get_Wells() :
                            self.set_Vector( Key=W , VectorData=self('WBP:'+W) , Units=self.get_Unit('WBP:'+W) , DataType='float' , overwrite=True ) 
                else :
                    for W in self.get_Wells() :
                        self.set_Vector( Key=W , VectorData=self('WBP:'+W) , Units=self.get_Unit('WBP:'+W) , DataType='float' , overwrite=True ) 
        elif KeyArguments is not None :
            if type(KeyArguments) is str and len(KeyArguments) > 0 :
                KeyArguments = KeyArguments.strip()
                if len(KeyArguments).split() == 1 :
                    if KeyArguments.upper() != 'WELL' and KeyArguments[0] == 'W' :
                        verbose( self.speak , 2 , " the KeyArguments '" + KeyArguments + "' seems to be a ECL style keyword...")
                        self.OUTPAVG(ECLkey=KeyArguments)
                else :
                    KeyArguments = KeyArguments.split()
                    WPAVE = ['WPAVE','1st','2nd','3rd','4th']
                    
                    if KeyArguments[0].upper() == 'OUTPAVG' :
                        verbose( self.speak , 1 , " VIP CARD '" + KeyArguments.pop(0) + "' found")
                        
                    if KeyArguments[0].upper() == 'STD' :
                        # Alpha label indicating that the mobility-weighted datum pressure average is to be computed. This is the default.
                        verbose( self.speak , 3 , " IMPORTANT: in VIP the mobility-weighted datum pressure average was computed, the most similar behaviour in eclipse could be to set " + WPAVE[2] + " item of keyword '" + WPAVE[0] + "' to 1.0 (purely connection factor weighted).")
                    elif KeyArguments[0].upper() == 'WELL' :
                        # Alpha label indicating that a pattern is being assigned to each well in the well list.
                        WellList = KeyArguments[-2]
                        WPAVE = ['WWPAVE','2nd','3rd','4th','5th']
                        verbose( self.speak , 3 , " IMPORTANT: notice that 'WWPAVE' should be used in eclipse, not 'WPAVE', in order to be compilant with the well list: " + WellList )
                    elif KeyArguments[0].upper() == 'PATTERN' :
                        # Alpha label indicating one of the possible patterns is to be used to compute the well average pressure.
                        if KeyArguments[-1].isdecimal() :
                            if int(KeyArguments[-1]) == 1 :
                                # Square pattern of size 1 gridblock by 1 gridblock
                                WBPkey = 'WBP'
                                verbose( self.speak , 3 , " IMPORTANT: be sure that the " + WPAVE[1] + " item of keyword '" + WPAVE[0] + "' is set to a negative value, like '-1', in your eclipse simulation.")
                            elif int(KeyArguments[-1]) == 2 :
                                # 5-spot pattern
                                WBPkey = 'WBP5'
                                verbose( self.speak , 3 , " IMPORTANT: be sure that the " + WPAVE[1] + " item of keyword '" + WPAVE[0] + "' is set to a negative value, like '-1', in your eclipse simulation.")
                            elif int(KeyArguments[-1]) == 3 :
                                # Square pattern of size 3 gridblocks by 3 gridblocks
                                WBPkey = 'WBP9'
                                verbose( self.speak , 3 , " IMPORTANT: be sure that the " + WPAVE[1] + " item of keyword '" + WPAVE[0] + "' is set to a negative value, like '-1', in your eclipse simulation.")
                            elif int(KeyArguments[-1]) in [ 5 , 7 , 9 ] :
                                # Square pattern of size N gridblocks by N gridblocks
                                WBPkey = 'WBP'+ KeyArguments[-1] + 'x' + KeyArguments[-1]
                                verbose(self.speak, -1 , " there is not eclipse keyword that matched this VIP configuration,\n this VIP average pressure will be loaded as '" + WBPkey + "'")
                            elif int(KeyArguments[-1]) == 0 :
                                # Exclude this layer from the calculation.
                                WBPkey = 'WBP0'
                                verbose( self.speak , 3 , " IMPORTANT: this layer has been excluded from the average pressure calculation")

                    elif KeyArguments[0].upper() == 'ACTIVE' :
                        # Alpha label indicating that only active perforations are used in the calculation. This is the default.
                        verbose( self.speak , 3 , " IMPORTANT: be sure that the " + WPAVE[4] + " item of keyword '" + WPAVE[0] + "' is set to 'OPEN' in your eclipse simulation.")
                    elif KeyArguments[0].upper() == 'ALL' :
                        # Alpha label indicating that all perforations, including inactive or shut-in perforations, are used in the calculation.
                        verbose( self.speak , 3 , " IMPORTANT: be sure that the " + WPAVE[4] + " item of keyword '" + WPAVE[0] + "' is set to 'ALL' in your eclipse simulation.")
                    elif KeyArguments[0].upper() == 'DATUM' :
                        # Alpha label indicating that the well average datum pressure is to be computed. This is the default for a pattern calculation.
                        verbose( self.speak , 3 , " IMPORTANT: be sure that the " + WPAVE[3] + " item of keyword '" + WPAVE[0] + "' is set to 'WELL' in your eclipse simulation.")
                    elif KeyArguments[0].upper() == 'GRIDBLOCK' :
                        # Alpha label indicating that the well average gridblock pressure is to be computed.
                        verbose( self.speak , 3 , " IMPORTANT: be sure that the " + WPAVE[3] + " item of keyword '" + WPAVE[0] + "' is set to 'NONE' in your eclipse simulation.")
                    
        if WPAVE == "WPAVE" :
            return self.OUTPAVG(ECLkey=WBPkey)
        if WPAVE == "WWPAVE" :
            for W in self.get_Wells( WellList ) :
                self.OUTPAVG(ECLkey=WBPkey+':'+W)
            return None

                    
                    
                        
                    
                    
            