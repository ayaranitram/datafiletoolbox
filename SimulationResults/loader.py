# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:45:52 2020

@author: MCARAYA
"""

__version__ = 0.5
__release__ = 210225
__all__ = ['loadSimulationResults']

from .._common.inout import _extension
#from datafiletoolbox.SimulationResults.mainObject import SimResult
from .vipObject import VIP as _VIP
from .CSVSimResultNexusDesktopObject import NexusDesktopCSV as _NexusDesktopCSV
from .excelObject import XLSX as _XLSX

okECL = False
try :
    from .eclObject import ECL as _ECL
    okECL = True
except ImportError :
    print ( 'failed import ECL, usually due to fail to import libecl')


def loadSimulationResults(FullPath,Simulator=None,Verbosity=None,**kwargs) :
    """
    Loads the results of reservoir simulation into and SimuResult object.
    This library can read:
        .SSS files from VIP simulator
        .SMSPEC files from Eclipse, Intersect or tNavigator
    """
    if 'speak' in kwargs and type(kwargs['speak']) in [bool,int,float] :
        if Verbosity is None :
            Verbosity = kwargs['speak']
            del kwargs['speak']

    if Verbosity is None :
        Verbosity = 2
    elif type(Verbosity) in [bool,float] :
        Verbosity = int(Verbosity)
    else :
        Verbosity = 2

    if FullPath is None :
        print( 'Please provide the path to the simulation results as string.')
        return None
    if Simulator is None :
        if _extension(FullPath)[0].upper() in ['.SMSPEC','.UNSMRY','.DATA'] :
            Simulator = 'ECLIPSE'
        elif _extension(FullPath)[0].upper() in ['.DAT','.SSS'] :
            Simulator = 'VIP'
        elif _extension(FullPath)[0].upper() in ['.FSC','.SS_FIELD','.SS_WELLS','.SS_REGIONS','.SS_NETWORK'] :
            Simulator = 'NEXUS'
        elif _extension(FullPath)[0].upper() in ['.CSV'] :
            Simulator = 'NexusDesktopSimResult'
        elif _extension(FullPath)[0].upper() in ['.XLSX'] :
            Simulator = 'SimPandasExcel'
    elif type(Simulator) is str and len(Simulator.strip()) > 0 :
        Simulator = Simulator.strip().upper()

    OBJ = None
    if Simulator in ['ECL','E100','E300','ECLIPSE','IX','INTERSECT','TNAV','TNAVIGATOR'] :
        if okECL is True :
            OBJ = _ECL(FullPath,verbosity=Verbosity)
        else :
            print( 'ECL object not loaded')
    elif Simulator in ['VIP'] :
        OBJ = _VIP(FullPath,verbosity=Verbosity)
    elif Simulator in ['NX','NEXUS'] :
        OBJ = _VIP(FullPath,verbosity=Verbosity)
    elif Simulator in ['NexusDesktopSimResult'] :
        OBJ = _NexusDesktopCSV(FullPath,verbosity=Verbosity)
    elif Simulator in ['SimPandasExcel'] :
        OBJ = _XLSX(FullPath,verbosity=Verbosity,**kwargs)

    if OBJ is not None and Verbosity != 0 :
        print(OBJ.__repr__())
    return OBJ

