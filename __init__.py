#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data File Tool Box is a set of routines useful to work with eclipse style
data files and properties.

Created on Tue Jul  9 21:23:27 2019
@author: martin
"""

# import datetime
# import numpy
# import pandas

# from datafiletoolbox.common.inout import extension
# from datafiletoolbox.common.inout import verbose
# from datafiletoolbox.common.stringformat import date
# from datafiletoolbox.common.loader import loadSimulationResults
# from datafiletoolbox.SimPlot.SmartPlot import Plot

# from datafiletoolbox.SimulationResults.oneObject import *

# from datafiletoolbox.SimulationResults.mainObject import SimResult
# from datafiletoolbox.SimulationResults.vipObject import VIP
# from datafiletoolbox.SimulationResults.eclObject import ECL

# from .common.functions import mainKey
# from .common.functions import is_SimulationResult

# from .SimInput.propertyManipulation import *
# from .SimInput.simObject import *

# from .SimulationResults import *

# from bases.units import convertUnit

__version__ = '0.1.21-08-04'
__author__ = 'Martin Araya'

msg = """implementing libecl 2.9.0 from pypi, released on May 2020"""

print('\n >>> Datafile Tool Box ' + str(__version__) + ' loaded <<<')
print(msg)

from .common.stringformat import date
from .common.inout import extension
