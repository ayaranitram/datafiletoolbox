# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:45:52 2020

@author: MCARAYA
"""

__version__ = '0.0.20-05-19'

from datafiletoolbox.common.inout import extension
#from datafiletoolbox.SimulationResults.mainObject import SimResult
from datafiletoolbox.SimulationResults.vipObject import VIP
from datafiletoolbox.SimulationResults.eclObject import ECL

def loadSimulationResults(FullPath=None,Simulator=None,Verbosity=2) :
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
        if extension(FullPath)[0].upper() in ['.SMSPEC','.UNSMRY','.DATA'] :
            Simulator = 'ECLIPSE'
        elif extension(FullPath)[0].upper() in ['.DAT','.SSS'] :
            Simulator = 'VIP'
        elif extension(FullPath)[0].upper() in ['.FSC','.SS_FIELD','.SS_WELLS','.SS_REGIONS','.SS_NETWORK'] :
            Simulator = 'NEXUS'
    elif type(Simulator) is str and len(Simulator.strip()) > 0 :
        Simulator = Simulator.strip().upper()

    
    if Simulator in ['ECL','E100','E300','ECLIPSE','IX','INTERSECT','TNAV','TNAVIGATOR'] :
        return ECL(FullPath,Verbosity)
    if Simulator in ['VIP'] :
        return VIP(FullPath,Verbosity)
    if Simulator in ['NX','NEXUS']:
        return VIP(FullPath,Verbosity)

