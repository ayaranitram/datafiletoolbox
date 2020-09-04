# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:31:52 2020

@author: MCARAYA
"""

__version__ = '0.0.20-06-08' 

import time
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import is_color_like


from datafiletoolbox.common.functions import is_SimulationResult
from datafiletoolbox.common.inout import verbose
from datafiletoolbox.common.functions import mainKey
from bases.units import convertUnit

timeout = 0.1

def savePlot(figure,FileName='') :
    figure.savefig(FileName)


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
            # time.sleep(timeout)
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
            elif 'THP' in Y_Keys[c] :
                SeriesColors[c] = ('lightgray')
            elif 'BHP' in Y_Keys[c] :
                SeriesColors[c] = ('darkgray')
            elif 'BP' in Y_Keys[c] :
                SeriesColors[c] = ('black')
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
            elif 'GOR' in Y_Keys[c] :
                SeriesColors[c] = ('gold')
            elif 'WC' in Y_Keys[c] :
                SeriesColors[c] = ('steelblue')
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