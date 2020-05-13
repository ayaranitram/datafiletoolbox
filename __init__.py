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

from datafiletoolbox.common.inout import extension
from datafiletoolbox.common.inout import verbose
from datafiletoolbox.common.stringformat import date
from datafiletoolbox.common.loader import loadSimulationResults
from datafiletoolbox.common.functions import mainKey
from datafiletoolbox.common.functions import is_SimulationResult

from datafiletoolbox.propertyManipulation import *
from datafiletoolbox.simObject import *

from datafiletoolbox.SimPlot import Plot

from bases.units import convertUnit

__version__ = '0.20.05.13' 
__author__ = 'Martin Araya'

print('\n >>> Datafile Tool Box ' + str(__version__) + ' loaded <<<')
