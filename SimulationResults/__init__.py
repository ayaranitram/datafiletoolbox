# -*- coding: utf-8 -*-
"""
Created on Sat May 16 20:10:06 2020

@author: martin
"""

from .mainObject import SimResult
from .vipObject import VIP

try :
    from .eclObject import ECL
except ImportError :
    print ( 'failed import ECL, usually due to fail to import libecl')

from .loader import loadSimulationResults
 
__version__ = '0.0.20-08-16'

