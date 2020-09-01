# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:46:05 2020

@author: MCARAYA
"""

__version__ = '0.0.20-05-16'

import pandas

def is_SimulationResult(obj) :
    """
    returns True if the object is a SimulationResults object.
    """
    return 'SimulationResults.' in str(type(obj)) 


def mainKey(Key) :
    """
    returns the main part (before the name of the item) in the keyword, MAIN:ITEM
    """
    if type(Key) is str:
        if len(Key.strip()) > 0 :
            return Key.strip().split(':')[0]
        else :
            return ''
    if type(Key) is list or type(Key) is tuple :
        results = []
        for K in Key :
            results.append( mainKey(K) )
        return list(set(results))

def itemKey(Key) :
    """
    returns the item part (after the name of the item) in the keyword, MAIN:ITEM
    """
    if type(Key) is str:
        if len(Key.strip()) > 0 :
            if ':' in Key.strip() :
                return Key.strip().split(':')[-1]
        else :
            return ''
    if type(Key) is list or type(Key) is tuple :
        results = []
        for K in Key :
            results.append( itemKey(K) )
        return list(set(results))

def keyType(Key) :
    """
    returns the type of key for an ECL style key:
        FIELD
        REGION
        WELL
        GROUP
    """
    if type(Key) is str :
        Key = Key.strip()
        if len(Key)>0 :
            if Key[0] == 'F' :
                return 'FIELD'
            if Key[0] == 'R' :
                return 'REGION'
            if Key[0] == 'W' :
                return 'WELL'
            if Key[0] == 'G' :
                return 'GROUP'
            return 'OTHER'


def isECLkey(Key,maxLen=12) :
    """
    returns True if the Key is ECL style
    
    The maximum accepted lenght for the main part of the Key can be changed 
    with maxLen parameter. To be compatible with RSM format 12 is a good number. 
    """
    if type(maxLen) is not int :
        raise TypeError("maxLen must be an integer")
    
    if type(Key) is list or type(Key) is tuple :
        results = []
        for K in Key :
            results.append( isECLkey(K) )
        return results
    
    if type(Key) is not str :
        return False
    if '-' in mainKey(Key) :
        return False
    if ' ' in mainKey(Key) :
        return False
    if len(mainKey(Key)) > maxLen :
        return False
    
    return True

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

def wellFromAttribute( listOfAttributes ) :
    """
    receives a list of attributes, like:
        [ 'WOPR:W1' , 'WOPR:W2' , 'WOPR:W3' , ... ]  
    and return a dictionary of the well names only:
        { 'WOPR:W1':'W1' , 'WOPR:W2':'W2' , 'WOPR:W3':'W3' , ... }  

    """
    if type( listOfAttributes ) is str :
        listOfAttributes = listOfAttributes.split()
    if type( listOfAttributes ) is tuple or type( listOfAttributes ) is set :
        listOfAttributes = list( listOfAttributes )
    if type( listOfAttributes ) is pandas.core.indexes.base.Index :
        listOfAttributes = list( listOfAttributes )
    if type( listOfAttributes ) is not list :
        return {}

    newNames = {}
    for each in listOfAttributes :
        newNames[each] = each.split(':')[-1]
    return newNames
