# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:45:52 2020

@author: MCARAYA
"""

__version__ = '0.0.20-05-19'

from datafiletoolbox.common.inout import extension
#from datafiletoolbox.SimulationResults.mainObject import SimResult
from datafiletoolbox.SimulationResults.vipObject import VIP

okECL = False
try :
    from datafiletoolbox.SimulationResults.eclObject import ECL
    okECL = True
except ImportError :
    print ( 'failed import ECL, usually due to fail to import libecl')

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
        if okECL is True :
            OBJ = ECL(FullPath,Verbosity)
        else :
            print( 'ECL object not loaded')
    elif Simulator in ['VIP'] :
        OBJ = VIP(FullPath,Verbosity)
    elif Simulator in ['NX','NEXUS']:
        OBJ = VIP(FullPath,Verbosity)
    
    if Verbosity != 0 :
        print(OBJ.__repr__())
    return OBJ
    
