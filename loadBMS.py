# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 01:07:20 2020

@author: MCARAYA
"""

import datafiletoolbox as dftb
# import pandas as pd
# import numpy as np

# from datafiletoolbox import expandKeyword
BMS = dftb.simObject.Simulation()
# BMS_HM = BMS.LoadModelFromData('C:/Users/mcaraya/OneDrive - Cepsa/git/sampleData/bms/HM_AZ45_E_1/HM_AZ45_E_1.DATA')
# BMS.LoadModelFromData('D:/git/sampleData/bms/HM_AZ45_E_1/HM_AZ45_E_1.DATA')
BMS.LoadModelFromData('C:/Users/mcaraya/OneDrive - Cepsa/git/sampleData/bms/HM_AZ45_E_1/HM_AZ45_E_1.DATA')
SATNUM = BMS[BMS.keys()[0]]['SATNUM'].get_prop()
PORO = BMS[BMS.keys()[0]]['PORO'].get_prop()
PERMX = BMS[BMS.keys()[0]]['PERMX'].get_prop()
SWFN = BMS[0]['SWFN'].get_table()
SOF2 = BMS[0]['SOF2'].get_table()
PVDO = BMS[0]['PVDO'].get_table()
COMPDAT = BMS[0].COMPDATtable()


