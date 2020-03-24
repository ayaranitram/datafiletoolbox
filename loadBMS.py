# -*- coding: utf-8 -*-
"""
Created on Tue Mar 24 01:07:20 2020

@author: MCARAYA
"""

import datafiletoolbox as dftb
from datafiletoolbox import expandKeyword
BMS = dftb.simObject.Simulation()
BMS_HM = BMS.LoadModelFromData('C:/Users/mcaraya/OneDrive - Cepsa/git/sampleData/bms/HM_AZ45_E_1/HM_AZ45_E_1.DATA')
SATNUM = BMS[1]['SATNUM'].args

# keywordArgument = SATNUM
# if '/' in keywordArgument :
#     keywordArgument = keywordArgument[ : keywordArgument.index('/') ]
# keywordArgument = keywordArgument.replace("\n"," ")
# keywordArgument = expandKeyword(keywordArgument)


        
BMS[1]['SATNUM'].arg2prop()
BMS[1]['SATNUM'].prop
BMS[1]['SATNUM'].prop.shape
