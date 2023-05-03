# -*- coding: utf-8 -*-
"""
Created on Wed May  3 16:00:39 2023

@author: MCARAYA
"""

__version__ = '0.0.0'
__release__ = 20230503
__all__ = ['OBSH']

from .mainObject import SimResult as _SimResult
from .._common.inout import _extension, _verbose
from .._common.functions import _mainKey
import pandas as pd
import numpy as np
import os


class OBSH(_SimResult):
    """
    object to contain data read from .xlsx files

    """

    def __init__(self, input_file=None, verbosity=2, nameSeparator=':', **kwargs):
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = OBSH
        self.results = {}
        self.obsh = None
        self.overwrite = False
        self.nameSeparator = str(nameSeparator)
        self.read_obsh(input_file)
        self.initialize(**kwargs)
        self.att_names_ = {'OIL_PRODUCTION_CUML': 'WOPTH',
                          'WATER_PRODUCTION_CUML': 'WWPTH',
                          'WATER_INJECTION_CUML': 'WWITH',
                          'GAS_PRODUCTION_CUML': 'WGPTH',
                          'GAS_INJECTION_CUML': 'WGITH',
                          'BOTTOM_HOLE_PRESSURE': 'WBHPH',
                          'TUBING_HEAD_PRESSURE': 'WTHPH'}
        self.att_names_.update({v: k for k, v in self.att_names_.items()})
        self.read_obsh(input_file)
        
    def read_obsh(self, input_file):
        with open(input_file, 'r') as f:
            obsh = f.readlines()
        obsh = [line for line in obsh if not line.startswith('#') and len(line) > 0]
        units = None
        date_format = None
        first = -1
        for line in obsh:
            first += 1
            if len(line.split()) > 1:
                break
            elif 'METRIC' in line or 'FIELD' in line:
                self.units = line
            elif 'DMY' in line:
                date_format = line
        if len(obsh) > first:
            first += 1
        else:
            raise ValueError("empty file")
        header = line.split()
        limits = [0] + [(line.index(each) + len(each)) for each in header]
        data = np.array([[line[limits[i]:limits[i+1]].strip() for i in range(len(limits[:-1]))] for line in obsh[first:]])
        data = pd.DataFrame(data, columns=header)
        for col in data.columns:
            if 'object' not in str(data[col].dtype) and 'string' not in str(data[col].dtype):
                continue                
            if col == 'WELL':
                try:
                    data[col] = data[col].astype('category')
                except:
                    pass
            elif col == 'DATE':
                try:
                    data[col] = pd.to_datetime(data[col])
                except:
                    pass
            else:
                try:
                    data[col] = data[col].astype(int)
                except ValueError:
                    try:
                        data[col] = data[col].astype(float)
                    except:
                        pass
                except:
                    pass
            if units == 'ECLIPSE_METRIC':
                self.units = {'OIL_PRODUCTION_CUML': 'SM3',
                              'WATER_PRODUCTION_CUML': 'SM3',
                              'WATER_INJECTION_CUML': 'SM3',
                              'GAS_PRODUCTION_CUML': 'SM3',
                              'GAS_INJECTION_CUML': 'SM3',
                              'BOTTOM_HOLE_PRESSURE': 'BARSA',
                              'TUBING_HEAD_PRESSURE': 'BARSA'}
            elif units == 'ECLIPSE_FIELD':
                self.units = {'OIL_PRODUCTION_CUML': 'STB',
                              'WATER_PRODUCTION_CUML': 'STB',
                              'WATER_INJECTION_CUML': 'STB',
                              'GAS_PRODUCTION_CUML': 'STB',
                              'GAS_INJECTION_CUML': 'STB',
                              'BOTTOM_HOLE_PRESSURE': 'PSIA',
                              'TUBING_HEAD_PRESSURE': 'PSIA'}
            self.units = {(self.att_names_[k] if k in self.att_names_ else k): u for k, u in self.units.items()}
            self.obsh = data

    # support functions for get_Vector:
    def loadVector(self, key):
        """
        internal function to return a numpy vector from the Frame files
        """
        if key in self.results:
            return self.results[key]
        if self.nameSeparator in key and len(key.split(self.nameSeparator)) == 2:
            att, item = key.split(self.nameSeparator)
        if att not in self.obsh.columns and att in self.att_names_:
            att = self.att_names_[att]
        else:
            raise ValueError("The attribute in the key '" + str(key) + "' is not in the obsh file.")
        if item in self.obsh['WELL']:
            return self.obsh[self.obsh['WELL'] == item][att]
        else:
            raise ValueError("The well '" + str(item) + "' is not in the obsh file.")

            