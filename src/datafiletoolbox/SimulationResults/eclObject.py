# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:45:12 2020

@author: MCARAYA
"""

__version__ = '0.25.9'
__release__ = 20230412
__all__ = ['ECL']

from .mainObject import SimResult as _SimResult
from .._common.functions import _mainKey
from .._common.inout import _extension
from .._common.inout import _verbose
from .._common.stringformat import isnumeric as _isnumeric
from .._Classes.Errors import CorruptedFileError
from .._Classes.EclSumLoader import EclSumLoader
import numpy as np
import os
import glob


def findMultiSummaryFiles(inputFile):
    files = glob.glob(_extension(inputFile)[2] + _extension(inputFile)[1] + '.S*')
    exts = [ _extension(file)[0].replace('.S','') for file in files ]
    summaries = [ files[i] for i in range(len(files)) if (len(exts[i])==4 and _isnumeric(exts[i])) ]
    return summaries


class ECL(_SimResult):
    """
    object to contain eclipse format results read from SMSPEC using libecl from equinor
    """
    loadEclSum = EclSumLoader()

    def __init__(self, inputFile=None, verbosity=2, **kwargs):
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = ECL
        if type(inputFile) == str and len(inputFile.strip()) > 0:
            self.loadSummary(inputFile, **kwargs)
            if ('unload' in kwargs and kwargs['unload'] is True) or ('close' in kwargs and kwargs['close'] is True):
                    return None
        if self.results is not None:
            self.initialize(**kwargs)

    def loadSummary(self, SummaryFilePath, **kwargs):
        if type(SummaryFilePath) is str:
            SummaryFilePath = SummaryFilePath.strip()
            if self.path is None:
                self.path = SummaryFilePath
            if _extension(SummaryFilePath)[0] != '.SMSPEC':
                newPath = _extension(SummaryFilePath)[2] + _extension(SummaryFilePath)[1] + '.SMSPEC'
                if os.path.isfile(newPath):
                    SummaryFilePath = newPath
                else:
                    newPath = _extension(SummaryFilePath)[2] + 'RESULTS/' + _extension(SummaryFilePath)[1] + '.SMSPEC'
                    if os.path.isfile( newPath ):
                        SummaryFilePath = newPath
                        _verbose( self.speak, 3, "\nWARNING: '.SMSPEC' file found in 'RESULTS' subdirectory, not in the same folder the '.DATA' is present.\n")

            if os.path.isfile(SummaryFilePath):
                if not os.path.isfile(_extension(SummaryFilePath)[2] + _extension(SummaryFilePath)[1] + '.UNSMRY') and len(findMultiSummaryFiles(SummaryFilePath)) == 0 :
                    raise FileNotFoundError( "No Summary files found:\n  -> i.e.: " + _extension(SummaryFilePath)[2] + _extension(SummaryFilePath)[1] +'.UNSMRY' )
                if os.path.getsize(SummaryFilePath) <= 680 and ( 'ignoreSMSPEC' not in kwargs or bool(kwargs['ignoreSMSPEC']) is False):
                    raise CorruptedFileError("\nThe SMSPEC file seems to be corrupted.\nIf you think this is not corrupted add the keyword\n   'ignoreSPSPEC=True'\nto skip this check, but if the file corrupted a fatal error will occur!")
                _verbose( self.speak, 1, ' > loading summary file:\n  ' + SummaryFilePath)
                EclSummary = ECL.loadEclSum
                self.results = EclSummary(SummaryFilePath, **kwargs) # ecl.summary.EclSum(SummaryFilePath)
                if ('unload' in kwargs and kwargs['unload'] is True) or ('close' in kwargs and kwargs['close'] is True):
                    return None
                self.name = _extension(SummaryFilePath)[1]
                self.set_FieldTime()
                self.get_wells(reload=True)
                self.get_groups(reload=True)
                self.get_regions(reload=True)
                self.get_keys(reload=True)
                self.units = self.get_Unit(self.keys_)
                _verbose( self.speak, 1, 'simulation runs from ' +  str(self.get_Dates()[0]) + ' to ' + str(self.get_Dates()[-1]))
                self.set_Vector('DATE', self.get_Vector('DATES')['DATES'], self.get_Unit('DATES'), data_type='datetime',
                                overwrite=True)
                self.strip_units()
                self.get_Attributes(reload=True)
                self.fill_field_basics()

            else:
                if not os.path.isfile(_extension(SummaryFilePath)[2] + _extension(SummaryFilePath)[1] + '.UNSMRY'):
                    raise FileNotFoundError( "the files doesn't exist:\n  -> " + _extension(SummaryFilePath)[1] + '.UNSMRY\n  -> ' + SummaryFilePath )
                raise FileNotFoundError( "the file doesn't exist:\n  -> " + SummaryFilePath )
        else:
            raise TypeError("SummaryFilePath must be a string")

    def reload(self):
        self.loadSummary(self.path)

    # support functions for get_Vector:
    def loadVector(self, key):
            """
            internal function to load a numpy vector from the summary files
            """
            if str(key).upper().strip() in ["DATES", "DATE"]:
                return self.results.numpy_dates
            else:
                return self.results.numpy_vector(str(key).upper().strip())

    def get_Dates(self):
        try:
            self.start = np.datetime64(self.results.start_date, 's')
        except:
            self.start = None
        try:
            self.end = self.results.end_date
        except:
            if self.start is None:
                self.end = None
            else:
                self.end = self.start + int(max(self.get_Vector('TIME')['TIME']))
        return self.results.numpy_dates

    def extract_wells(self):
        self.wells = tuple(self.results.wells())
        return self.wells

    def extract_groups(self, pattern=None, reload=False):
        """
        calls group method from libecl:

        Will return a list of all the group names in case.

        If the pattern variable is different from None only groups
        matching the pattern will be returned; the matching is based
        on fnmatch(), i.e. shell style wildcards.
        """
        if len(self.groups) == 0 or reload is True:
            self.groups = tuple(self.results.groups())
        if pattern is None:
            return self.groups
        else:
            return tuple(self.results.groups(pattern))

    def list_Keys(self, pattern=None, reload=False):
        """
        Return a StringList of summary keys matching @pattern.

        The matching algorithm is ultimately based on the fnmatch()
        function, i.e. normal shell-character syntax is used. With
        @pattern == "WWCT:*" you will get a list of watercut keys for
        all wells.

        If pattern is None you will get all the keys of summary
        object.
        """
        if len(self.keys_) == 0 or reload is True:
            self.keys_ = tuple( self.results.keys(pattern))
            for extra in ( 'TIME', 'DATE', 'DATES' ):
                if extra not in self.keys_:
                    self.keys_ = tuple( [extra] + list(self.keys_) )
        if pattern is None:
            return self.keys_
        else:
            return tuple( self.results.keys(pattern) )

    def extract_regions(self, pattern=None):
        # preparing object attribute
        regionsList = list( self.regions )
        for key in self.get_keys():
            if key[0] == 'R':
                if ':' in key:
                    region = key.split(':')[1]
                    regionsList.append( region )
        regionsList = list( set( regionsList ))
        regionsList.sort()
        self.regions = tuple( regionsList )
        # preparing list to return
        if pattern is not None:
            regionsList = []
            for region in self.regions:
                if pattern in region:
                    regionsList.append(region)
            return tuple(regionsList)
        else:
            return self.regions

    def get_Unit(self, key='--EveryType--'):
        """
        returns a string identifiying the unit of the requested Key

        Key could be a list containing Key strings, in this case a dictionary
        with the requested Keys and units will be returned.
        the Key '--EveryType--' will return a dictionary Keys and units
        for all the keys in the results file

        """
        if type(key) is str and key.strip() != '--EveryType--':
            key = key.strip().upper()
            if key in self.units:
                return self.units[key]
            if key in ['DATES', 'DATE']:
                    self.units[key] = 'DATE'
                    return 'DATE'
            if key in self.keys_:
                return self.results.unit(key)
            else:
                if key[0] == 'W':
                    UList=[]
                    for W in self.get_wells():
                        if key+ ':'+W in self.units:
                            UList.append(self.units[key + ':' + W])
                        elif key in self.keys_:
                            UList.append(self.results.unit(key + ':' + W))
                    if len(set(UList)) == 1:
                        self.units[key] = UList[0]
                        return UList[0]
                    else:
                        return None
                elif key[0] == 'G':
                    UList=[]
                    for G in self.get_groups():
                        if key+ ':'+G in self.units:
                            UList.append(self.units[key + ':' + G])
                        elif key in self.keys_:
                            UList.append(self.results.unit(key + ':' + G))
                    if len(set(UList)) == 1:
                        self.units[key] = UList[0]
                        return UList[0]
                    else:
                        return None
                elif key[0] == 'R':
                    UList=[]
                    for R in self.get_regions():
                        if key+ ':'+R in self.units:
                            UList.append(self.units[key + ':' + R])
                        elif key in self.keys_:
                            UList.append(self.results.unit(key + ':' + R))
                    if len(set(UList)) == 1:
                        self.units[key] = UList[0]
                        return UList[0]
                    else:
                        return None
                UList = None

        elif type(key) is str and key.strip() == '--EveryType--':
            key = []
            key_dict = {}
            for each in self.keys_:
                if ':' in each:
                    key.append(_mainKey(each))
                    key_dict[ _mainKey(each)] = each
                else:
                    key.append(each)
            key = list(set(key))
            key.sort()
            temp_units = {}
            for each in key:
                if each in self.units:
                    temp_units[each] = self.units[each]
                elif each in self.keys_ and ( each != 'DATES' and each != 'DATE' ):
                    if self.results.unit(each) is None:
                        temp_units[each] = self.results.unit(each)
                    else:
                        temp_units[each] = self.results.unit(each).strip('( )').strip("'").strip('"')
                elif each in self.keys_ and ( each == 'DATES' or each == 'DATE' ):
                    temp_units[each] = 'DATE'
                else:
                    if key_dict[each] in self.units:
                        temp_units[each] = self.units[key_dict[each]]
                    elif key_dict[each] in self.keys_:
                        if self.results.unit(key_dict[each]) is None:
                            temp_units[each] = self.results.unit(key_dict[each])
                        else:
                            temp_units[each] = self.results.unit(key_dict[each]).strip('( )').strip("'").strip('"')
            return temp_units
        elif type(key) in [list, tuple]:
            temp_units = {}
            for each in key:
                if type(each) is str:
                    temp_units[each] = self.get_Unit(each)
            return temp_units
