# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:45:52 2020

@author: MCARAYA
"""

from datafiletoolbox import extension
from datafiletoolbox.SimulationResults import *

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

