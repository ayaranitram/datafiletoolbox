#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data File Tool Box is a set of routines useful to work with eclipse style
data files and properties.

Created on Tue Jul  9 21:23:27 2019
@author: martin
"""

__version__ = '0.46.0'
__release__ = 220223
__author__ = 'Martin Carlos Araya <martinaraya@gmail.com>'
__all__ = ['stringformat', 'extension', 'Alternate', 'convert', 'SimPandas',
           'SimSeries', 'SimDataFrame', 'loadSimulationResults','melt','pivot','unify','slope']

_msg = """     implementing libecl 2.9.1 from pypi, released on Aug 2020"""


from ._Classes.Iterators import Alternate
from ._Classes.SimPandas import SimSeries, SimDataFrame
from ._Classes import SimPandas

from ._common.eclDATES import simDate as ECLdate
from ._common.functions import _mainKey as mainKey, _itemKey as itemKey, tamiz, _meltDF as melt, _pivotDF as pivot
from ._common.inout import _extension as extension
from ._common.keywordsConversions import fromECLtoVIP, fromVIPtoECL, fromECLtoCSV, fromCSVtoECL
from ._common.stringformat import date as strDate, isDate, multisplit, isnumeric, getnumber
from ._common import stringformat
from ._common.units import convertUnit as convert
from ._common.unify import unify
from ._common.slope import slope

from .SimulationResults.loader import loadSimulationResults

print('\n>>> Datafile Tool Box',
      __version__,
      'r'+str(__release__),
      'loaded <<<\n')
# print(_msg)
