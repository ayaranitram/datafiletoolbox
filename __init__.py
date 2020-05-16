#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data File Tool Box is a set of routines useful to work with eclipse style
data files and properties.

Created on Tue Jul  9 21:23:27 2019
@author: martin
"""

import datetime
import numpy
import pandas

from .common.inout import extension
from .common.inout import verbose
from .common.stringformat import date
from .common.loader import loadSimulationResults
from .common.functions import mainKey
from .common.functions import is_SimulationResult

from .SimInput.propertyManipulation import *
from .SimInput.simObject import *
from .SimPlot.SmartPlot import Plot
from .SimulationResults import *

from bases.units import convertUnit

__version__ = '0.20.05.13' 
__author__ = 'Martin Araya'

print('\n >>> Datafile Tool Box ' + str(__version__) + ' loaded <<<')
