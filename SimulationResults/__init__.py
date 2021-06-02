# -*- coding: utf-8 -*-
"""
Created on Sat May 16 20:10:06 2020

@author: martin
"""

__version__ = '0.1.0'
__release__ = 210225
__all__ = ['loadSimulationResults']

from .mainObject import SimResult
from .vipObject import VIP
from .CSVSimResultNexusDesktopObject import NexusDesktopCSV
from .excelObject import XLSX
from .tableObject import TABLE

try:
    from .eclObject import ECL
except ImportError:
    print("""ERROR: failed import ECL, usually due to fail to import libecl.
                    Please install or upgrade libecl using pip command:

                        pip install libecl

                    or upgrade:
                        pip install libecl --upgrade
                        """)

from .loader import loadSimulationResults
