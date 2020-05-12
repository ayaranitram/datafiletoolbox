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

from common.inout import extension
from common.inout import verbose
verbose()

from datafiletoolbox.propertyManipulation import *
from datafiletoolbox.simObject import *
from datafiletoolbox.stringformat import *


__version__ = '0.20.05.12' # cambio de versionado, la última fue 0.215
__author__ = 'Martin Araya'

print('\n >>> Datafile Tool Box ' + str(__version__) + ' loaded <<<')
