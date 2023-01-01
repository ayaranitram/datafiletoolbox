# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 14: 36: 56 2020

@author: MCARAYA
"""

__version__ = '0.0.0'
__release__ = 20210225

from .calculations import *
from .unitsSystems import *
from .keywords import *

ECL2VIPkey = {}
for each in VIP2ECLkey:
    ECL2VIPkey[VIP2ECLkey[each]] = each

ECL2VIPtype = {}
for each in VIP2ECLtype:
    ECL2VIPtype[VIP2ECLtype[each]] = each

ECL2CSVkey = {}
for each in CSV2ECLkey:
    ECL2CSVkey[CSV2ECLkey[each]] = each

ECL2CSVtype = {}
for each in CSV2ECLtype:
    ECL2CSVtype[CSV2ECLtype[each]] = each

CSV2VIPkey = {}
for each in VIP2CSVkey:
    CSV2VIPkey[VIP2CSVkey[each]] = each
