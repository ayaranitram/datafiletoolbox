#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data File Tool Box is a set of routines useful to work with eclipse style
data files and properties.

Created on Tue Jul  9 21:23:27 2019
@author: martin
"""

__version__ = '0.2.20-10-18'
__author__ = 'Martin Araya'
__all__ = ['stringformat','extension','Alternate','SimPandas']

_msg = """     implementing libecl 2.9.1 from pypi, released on Aug 2020"""

print('\n >>> Datafile Tool Box ' + str(__version__) + ' loaded <<<')
# print(_msg)

from ._Classes.Iterators import Alternate
from ._Classes import SimPandas
from ._Classes.SimPandas import SimSeries , SimDataFrame

from ._common.eclDATES import simDate as ECLdate
from ._common.functions import _mainKey as mainKey , _itemKey as itemKey , tamiz
from ._common.inout import _extension as extension
from ._common.keywordsConversions import fromECLtoVIP , fromVIPtoECL , fromECLtoCSV , fromCSVtoECL
from ._common import stringformat
from ._common.stringformat import date as strDate , isDate , multisplit , isnumeric , getnumber

from .SimulationResults.loader import loadSimulationResults
