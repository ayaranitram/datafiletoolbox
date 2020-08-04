# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:46:05 2020

@author: MCARAYA
"""

__version__ = '0.0.20-05-16'

def is_SimulationResult(obj) :
    """
    returns True if the object is a SimulationResults object.
    """
    return 'SimulationResults.' in str(type(obj)) 


def mainKey(Key) :
    """
    returns the main part (before the name if the item) of the keyword, MAIN:ITEM
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
