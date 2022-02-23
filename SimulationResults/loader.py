# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:45:52 2020

@author: MCARAYA
"""

__version__ = '0.54.3'
__release__ = 220223
__all__ = ['loadSimulationResults']

from .._common.inout import _extension
from .._common.sharedVariables import _loadingECLfile
#from datafiletoolbox.SimulationResults.mainObject import SimResult
from .vipObject import VIP as _VIP
from .CSVSimResultNexusDesktopObject import NexusDesktopCSV as _NexusDesktopCSV
from .excelObject import XLSX as _XLSX
from .tableObject import TABLE as _TABLE
from .rsmObject import RSM as _RSM
from .h5Object import H5 as _H5
import pickle


okECL = False
try:
    from .eclObject import ECL as _ECL
    okECL = True
except ImportError:
    print ( 'failed import ECL, usually due to fail to import libecl')


def loadSimulationResults(FullPath,Simulator=None,Verbosity=None,**kwargs) :
    """
    Loads the results of reservoir simulation into SimResult object.
    This library can read:
        .SSS files from VIP simulator
        .SMSPEC files from Eclipse, Intersect or tNavigator
        .RSM files
        .XLSX files exported from datafiletoolbox
        .PKL files from previously saved SimResults instances
    """
    for verbKey in  ['speak','verbosity','verbose'] :
        if verbKey in kwargs and type(kwargs[verbKey]) in [bool,int,float] :
            if Verbosity is None :
                Verbosity = kwargs[verbKey]
                del kwargs[verbKey]

    if Verbosity is None :
        Verbosity = 2
    elif type(Verbosity) in [int] :
        pass
    elif type(Verbosity) in [bool,float] :
        Verbosity = int(Verbosity)
    else:
        Verbosity = 2

    if FullPath is None :
        print( 'Please provide the path to the simulation results as string.')
        return None
    if Simulator is None :
        if _extension(FullPath)[0].upper() in ['.SMSPEC','.UNSMRY','.DATA','.AFI'] :
            Simulator = 'ECLIPSE'
        elif _extension(FullPath)[0].upper() in ['.DAT','.SSS'] :
            Simulator = 'VIP'
        elif _extension(FullPath)[0].upper() in ['.FSC','.SS_FIELD','.SS_WELLS','.SS_REGIONS','.SS_NETWORK'] :
            Simulator = 'NEXUS'
        elif _extension(FullPath)[0].upper() in ['.CSV'] :
            Simulator = 'NexusDesktopSimResult'
        elif _extension(FullPath)[0].upper() in ['.XLSX'] :
            Simulator = 'SimPandasExcel'
        elif _extension(FullPath)[0].upper() in ['.TXT'] :
            Simulator = 'DataTable'
        elif _extension(FullPath)[0].upper() in ['.PKL'] :
            Simulator = 'Pickle'
        elif _extension(FullPath)[0].upper() in ['.RSM'] :
            Simulator = 'RSM'
        elif _extension(FullPath)[0].upper() in ['.H5'] :
            Simulator = 'H5'
    elif type(Simulator) is str and len(Simulator.strip()) > 0 :
        Simulator = Simulator.strip().upper()

    _loadingECLfile[0] = False
    OBJ = None
    if Simulator in ['ECL','E100','E300','ECLIPSE','IX','INTERSECT','TNAV','TNAVIGATOR'] :
        if okECL is True :
            _loadingECLfile[0] = True
            OBJ = _ECL(FullPath,verbosity=Verbosity,**kwargs)
        else:
            print( 'ECL object not loaded')
    elif Simulator in ['VIP'] :
        OBJ = _VIP(FullPath,verbosity=Verbosity,**kwargs)
    elif Simulator in ['NX','NEXUS'] :
        OBJ = _VIP(FullPath,verbosity=Verbosity,**kwargs)
    elif Simulator in ['NexusDesktopSimResult'] :
        OBJ = _NexusDesktopCSV(FullPath,verbosity=Verbosity,**kwargs)
    elif Simulator in ['SimPandasExcel'] :
        OBJ = _XLSX(FullPath,verbosity=Verbosity,**kwargs)
    elif Simulator in ['DataTable'] :
        OBJ = _TABLE(FullPath,verbosity=Verbosity,**kwargs)
    elif Simulator in ['RSM'] :
        OBJ = _RSM(FullPath,verbosity=Verbosity,**kwargs)
    elif Simulator in ['H5'] :
        OBJ = _H5(FullPath,verbosity=Verbosity,**kwargs)
    elif Simulator in ['Pickle'] :
        import os
        if not os.path.isfile(FullPath):
            raise FileNotFoundError("File doesn't exists:\n  "+str(FullPath))
        with open(FullPath, 'wb') as f:
            OBJ = pickle.load(f)
        if OBJ is not None:
            OBJ.set_Verbosity(Verbosity)

    _loadingECLfile[0] = False
    if OBJ is not None and Verbosity != 0 :
        if ('preload' not in kwargs) or ('preload' in kwargs and kwargs['preload'] is True):
            try:
                print(OBJ.__repr__())
            except:
                pass
    return OBJ
