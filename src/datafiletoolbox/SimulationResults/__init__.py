# -*- coding: utf-8 -*-
"""
Created on Sat May 16 20:10:06 2020

@author: martin
"""

__version__ = '0.2.2'
__release__ = 20220316
__all__ = ['loadSimulationResults']

from .mainObject import SimResult
from .vipObject import VIP
from .CSVSimResultNexusDesktopObject import NexusDesktopCSV
from .excelObject import XLSX
from .tableObject import TABLE
from .h5Object import H5
from .rsmObject import RSM


try:
    from .eclObject import ECL
except ImportError as e:
    print("""ERROR: failed import ECL, usually due to fail to import libecl.
       Please install or upgrade libecl using pip command:

           pip install libecl

       or upgrade:

           pip install libecl --upgrade""")
    print("""
*******************************************************************************
                         error message from libecl:""")
    print(e)
    print("""
*******************************************************************************
""")

from .loader import loadSimulationResults
