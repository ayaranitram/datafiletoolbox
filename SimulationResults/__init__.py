# -*- coding: utf-8 -*-
"""
Created on Sat May 16 20:10:06 2020

@author: martin
"""
__version__ = '0.0.20-10-18'
__all__ = ['loadSimulationResults']

from .mainObject import SimResult
from .vipObject import VIP
from .CSVSimResultNexusDesktopObject import NexusDesktopCSV

try :
    from .eclObject import ECL
except ImportError :
    print ( 'ERROR: failed import ECL, usually due to fail to import libecl.\n       Please install or upgrade libecl using pip command:\n\n          pip install libecl\n\n       or upgrade:\n\n          pip install libecl --upgrade\n')

from .loader import loadSimulationResults
 


