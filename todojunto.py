# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 12:42:34 2020

@author: MCARAYA
"""

from datafiletoolbox import extension
from datafiletoolbox import verbose
from bases.units import convertUnit
from bases.units import unit
from bases.units import convertible as convertibleUnits

import datafiletoolbox.dictionaries.dictionaries as dictionaries
import os.path
import os
import json
import ecl
# import sys
# import time
import numpy as np
import pandas as pd
import seaborn as sns
# import math
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import is_color_like
import random
# import matplotlib.cbook as cbook
from datetime import timedelta
from datetime import datetime
from datafiletoolbox import date as strDate
# from datafiletoolbox import Plot
from datafiletoolbox.SimPlot.SmartPlot import Plot
from datafiletoolbox.common.functions import is_SimulationResult
from datafiletoolbox.common.functions import mainKey

import ecl.summary

import fnmatch

class OverwrittingError(Exception):
    pass

@property()
def version():
    print('SimulationResults version 0.15')
    


#verbose(1,1,'\n  initializing most commong units conversions...')
verbose(0,0,convertibleUnits('SM3','MMstb',False))
verbose(0,0,convertibleUnits('SM3','Bscf',False))
verbose(0,0,convertibleUnits('SM3','Tscf',False))
verbose(0,0,convertibleUnits('STM3','MMstb',False))
verbose(0,0,convertibleUnits('KSTM3','MMstb',False))
verbose(0,0,convertibleUnits('KSM3','Bscf',False))
verbose(0,0,convertibleUnits('MSM3','Tscf',False))
verbose(0,0,convertibleUnits('SM3/DAY','Mstb/day',False))
verbose(0,0,convertibleUnits('SM3/DAY','stb/day',False))
verbose(0,0,convertibleUnits('SM3/DAY','MMscf/day',False))
verbose(0,0,convertibleUnits('SM3/DAY','Mscf/day',False))
verbose(0,0,convertibleUnits('STM3/DAY','Mstb/day',False))
verbose(0,0,convertibleUnits('STM3/DAY','stb/day',False))
verbose(0,0,convertibleUnits('KSM3/DAY','MMscf/day',False))
verbose(0,0,convertibleUnits('KSM3/DAY','Mscf/day',False))
verbose(0,0,convertibleUnits('STM3/DAY','SM3/DAY',False))
verbose(0,0,convertibleUnits('KSTM3/DAY','SM3/DAY',False))
verbose(0,0,convertibleUnits('KSM3/DAY','SM3/DAY',False))
verbose(0,0,convertibleUnits('STM3','SM3',False))
verbose(0,0,convertibleUnits('KSTM3','SM3',False))
verbose(0,0,convertibleUnits('KSM3','SM3',False))
verbose(0,0,convertibleUnits('MSM3','SM3',False))
verbose(0,0,convertibleUnits('KPA','BARSA',False))
verbose(0,0,convertibleUnits('BARSA','psia',False))
verbose(0,0,convertibleUnits('KPA','psia',False))
verbose(0,0,convertibleUnits('DATE','DATES',False))
verbose(0,0,convertibleUnits('DAY','DAYS',False))


timeout = 0.1


    

















                    
                        
                    
                    
            