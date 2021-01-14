# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 18:21:37 2021

@author: MCARAYA
"""

from datafiletoolbox.SimulationInput.readInput import readKeyword 
from datafiletoolbox.SimulationInput.propertyManipulation import expandKeyword
import pandas as pd
import numpy as np

def DataFrame_fromGridPropertiesInclude(path) :
    """
    reads an ASCII eclipse style include file and returns the grid properties 
    as a pandas DataFrame.
    """
    dataDict = readKeyword(path)
    for each in dataDict :
        if type(dataDict[each]) is str and ( '.' in dataDict[each] or 'E' in dataDict[each] ) :
            try :
                dataDict[each] = list(map(float,expandKeyword(dataDict[each]).replace('/',' ').split()))
            except :
                pass
        elif type(dataDict[each]) is str :
            try :
                dataDict[each] = list(map(int,expandKeyword(dataDict[each]).replace('/',' ').split()))
            except :
                try :
                    dataDict[each] = list(map(float,expandKeyword(dataDict[each]).replace('/',' ').split()))
                except :
                    pass
                
    sizes = []
    toClean = []
    for each in dataDict :
        if dataDict[each] is None :
            toClean.append(each)
        elif len(dataDict[each]) == 0 :
            toClean.append(each)
        else :
            sizes.append( len(dataDict[each]) )
    for each in toClean :
        del dataDict[each]
    sizes = list(set(sizes))
    if len(sizes) == 1 :
        print(' the following properties were found:\n   -> '+'\n   -> '.join( list(dataDict.keys()) ) + '\n of size '+str(sizes[0]))
        dataDF = pd.DataFrame(dataDict)
        dataDF.replace(0.0,np.nan,inplace=True)
        return dataDF
    elif len(sizes) > 1:
        result = []
        for size in sizes :
            sizeDict = {}
            for each in dataDict :
                if len(dataDict[each]) == size :
                    sizeDict[each] = dataDict[each]
            print(' the following properties were found:\n   -> '+'\n   -> '.join( list(sizeDict.keys()) ) + '\n of size '+str(size))
            dataDF = pd.DataFrame(sizeDict)
            dataDF.replace(0.0,np.nan,inplace=True)
            result.append( dataDF.copy() )
        return tuple(result)

