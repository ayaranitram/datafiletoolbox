# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 01:07:20 2020

@author: MCARAYA
"""

import datafiletoolbox as dftb
# from datafiletoolbox import expandKeyword
BMS = dftb.simObject.Simulation()
# BMS_HM = BMS.LoadModelFromData('C:/Users/mcaraya/OneDrive - Cepsa/git/sampleData/bms/HM_AZ45_E_1/HM_AZ45_E_1.DATA')
BMS_HM = BMS.LoadModelFromData('D:/git/sampleData/bms/HM_AZ45_E_1/HM_AZ45_E_1.DATA')
SATNUM = BMS[BMS.keys()[0]]['SATNUM'].args
BMS[BMS.keys()[0]]['SATNUM'].arg2prop()
BMS[BMS.keys()[0]]['SATNUM'].prop
BMS[BMS.keys()[0]]['SATNUM'].prop.shape
