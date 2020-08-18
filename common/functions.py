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
            return None
    if type(Key) is list or type(Key) is tuple :
        results = []
        for K in Key :
            results.append( mainKey(K) )
        return list(set(results))

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