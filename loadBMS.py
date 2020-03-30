# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 01:07:20 2020

@author: MCARAYA
"""

import datafiletoolbox as dftb
import pandas as pd
import numpy as np

# from datafiletoolbox import expandKeyword
BMS = dftb.simObject.Simulation()
# BMS_HM = BMS.LoadModelFromData('C:/Users/mcaraya/OneDrive - Cepsa/git/sampleData/bms/HM_AZ45_E_1/HM_AZ45_E_1.DATA')
BMS_HM = BMS.LoadModelFromData('D:/git/sampleData/bms/HM_AZ45_E_1/HM_AZ45_E_1.DATA')
SATNUM_arg = BMS[BMS.keys()[0]]['SATNUM'].args
BMS[BMS.keys()[0]]['SATNUM'].arg2prop()
SATNUM = BMS[BMS.keys()[0]]['SATNUM'].prop
print(BMS[BMS.keys()[0]]['SATNUM'].prop.shape)
PORO = BMS[BMS.keys()[0]]['PORO'].get_prop()
PERMX = BMS[BMS.keys()[0]]['PERMX'].get_prop()
SWFN_args = BMS[0]['SWFN'].get_args()
BMS[0]['SWFN'].arg2table()
SWFN = BMS[0]['SWFN'].get_table()
SOF2 = BMS[0]['SOF2'].get_table()



