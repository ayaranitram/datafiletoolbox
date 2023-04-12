# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 11:00:20 2021

@author: MCARAYA
"""

__version__ = '0.20.4'
__release__ = 20230412
__all__ = ['TABLE']

from .mainObject import SimResult as _SimResult
from .._common.inout import _extension, _verbose
from .._common.functions import _mainKey, _itemKey
from .._common.stringformat import date as _strDate, getnumber as _getnumber, isDate as _isDate
from .._common.keywordsConversions import fromECLtoVIP as _fromECLtoVIP, fromVIPtoECL as _fromVIPtoECL  # , fromCSVtoECL
from .._dictionaries import UniversalKeys as _UniversalKeys, VIPTypesToExtractVectors as _VIPTypesToExtractVectors
from .._dictionaries import ECL2VIPkey as _ECL2VIPkey, VIP2ECLtype as _VIP2ECLtype, \
    VIP2ECLkey as _VIP2ECLkey  # , ECL2VIPtype
# from datafiletoolbox.dictionaries import ECL2CSVtype, ECL2CSVkey, CSV2ECLtype, CSV2ECLkey
# from datetime import timedelta
import pandas as pd
import numpy as np
from numpy import nan as NaN
from pandas import Series
import os


class TABLE(_SimResult):
    """
    object to contain data read from generic table files, like .txt or csv

    """

    def __init__(self, inputFile=None, verbosity=2, sep=None, header='infer', units='infer', names=None, overwrite=True,
                 index_col=False, **kwargs):
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = TABLE
        self.results = {}
        self.Frames = {}
        self.DTindexValues = None
        self.lastFrame = ''
        self.lastItem = ''
        self.null = NaN
        self.interpolateNaN = False
        self.overwrite = False
        self.itemsCol = {}
        self.dates = None
        if type(inputFile) is str and len(inputFile.strip()) > 0:
            if os.path.isfile(inputFile):
                self.readTable(inputFile, sep=sep, header=header, units=units, names=names, index_col=index_col)
            else:
                print("file doesn't exists")
        if len(self.Frames) > 0:
            self.name = _extension(inputFile)[1]
            self.initialize(**kwargs)

    def initialize(self, **kwargs):
        """
        run intensive routines, to have the data loaded and ready
        """
        self.findItemsCol()
        self.stripItems()
        self.extract_Keys()
        self.extractDATE()
        self.find_index()
        self.extract_wells()
        self.extract_groups()
        self.extract_regions()
        self.get_Attributes(None, True)
        if self.is_Key('DATES') and not self.is_Key('DATE'):
            self['DATE'] = 'DATES'
        if not self.is_Key('DATE'):
            self.createDATES()
        elif self.get_Unit('DATE') is None or self.get_Unit('DATE') != 'DATE':
            self.set_Units('DATE', 'DATE', overwrite=True)
        if not self.is_Key('DATES') and self.is_Key('DATE'):
            self['DATES'] = 'DATE'
        if self.is_Key('DATES') and (self.get_Unit('DATES') is None or self.get_Unit('DATES') != 'DATE'):
            self.set_Unit('DATES', 'DATE', overwrite=True)
        if not self.is_Key('TIME') and self.is_Key('DATE'):
            self.createTIME()
            # self['TIME'] = ( self('DATE').astype('datetime64[s]') - self.start ).astype('int') / (60*60*24)
        if self.is_Key('TIME') and (self.get_Unit('TIME') is None or self.get_Unit('TIME').upper() in ['', 'NONE']):
            self.set_Unit('TIME', 'DAYS', overwrite=True)
        if not self.is_Key('YEAR') and self.is_Key('DATE'):
            self.createYEAR()
        if not self.is_Key('MONTH') and self.is_Key('DATE'):
            self.createMONTH()
        if not self.is_Key('DAY') and self.is_Key('DATE'):
            self.createDAY()
        _SimResult.initialize(self, **kwargs)

    def set_itemsCol(self, column, frame=None):
        if frame is None:
            for Frame in self.Frames:
                if column in self.Frames[Frame].columns:
                    self.itemsCol[Frame] = column

    def findItemsCol(self):
        for frame in self.Frames:
            for col in self.Frames[frame].columns:
                if str(self.Frames[frame][col].dtype) not in ['float64', 'float32', 'float', 'int64', 'int32', 'int']:
                    if type(self.Frames[frame][col][0]) is str:
                        if _isDate(self.Frames[frame][col][0]):
                            continue
                        else:
                            self.itemsCol[frame] = col
                            break

    def stripItems(self):
        for frame in self.Frames:
            if frame in self.itemsCol:
                self.Frames[frame][self.itemsCol[frame]] = self.Frames[frame][self.itemsCol[frame]].str.strip(
                    """\t\r\n'" """)

    def readTable(self, inputFile, sep=None, header='infer', units=None, names=None, index_col=False):
        """
        internal function to read a generic table from a file (header in first row, units in second row)
        """
        if type(header) is int:
            if type(units) is int:
                if header != units:
                    header = [header, units]
        elif type(header) in [list, tuple]:
            if type(units) is int:
                if units not in header:
                    header = list(header) + [units]
        elif type(header) is str and header.strip().lower() == 'infer':
            pass  # to be implemented

        if type(units) is str and units.strip().lower() == 'infer':
            units = None  # to be implemented
        elif type(units) is int:
            if type(header) is int:
                if units == header:
                    units = None
                else:
                    header = [header, units]
            elif type(header) in (list, tuple):
                if units in header:
                    pass  # units = None
                else:
                    header = list(header) + [units]

        user_index_col = index_col
        if index_col is False and (type(header) is not int and header != 'infer'):
            index_col = None

        try:
            NewFrame = pd.read_table(inputFile, sep=sep, header=header, engine='python', index_col=index_col)
        except ImportError:
            raise ImportError(
                "Missing optional dependencies 'xlrd' and 'openpyxl'.\nInstall xlrd and openpyxl for Excel support.\nUse pip or conda to install xlrd and install openpyxl.")
        except:
            try:
                import xlrd
                try:
                    import openpyxl
                except:
                    raise ModuleNotFoundError(
                        "Missing optional dependency 'openpyxl'.\nInstall openpyxl for Excel support.\nUse pip or conda to install openpyxl.")
            except:
                raise ModuleNotFoundError(
                    "Missing optional dependency 'xlrd'.\nInstall xlrd for Excel support.\nUse pip or conda to install xlrd.")
            raise TypeError('Not able to read the excel file, please check input parameters and excel sheets format.')

        if inputFile in self.Frames:
            _verbose(self.speak, 2,
                     "the file '" + str(inputFile) + "' will overwrite the previously loaded file with the same name.")

        if user_index_col is False and (type(header) is not int and header != 'infer'):
            colNames = NewFrame.columns
            NewFrame.reset_index(inplace=True)
            NewFrame.drop(NewFrame.columns[-1], axis=1, inplace=True)
            NewFrame.columns = colNames

        NewNames = {}
        if units is not None:
            for col in NewFrame.columns:
                NewKey = ' '.join(list(map(str, col[0:-1]))).strip().replace(' ', '_').upper()
                NewNames[col] = NewKey
                if col[-1].startswith('Unnamed:'):
                    NewUnits = ''
                    unitsMessage = ''
                else:
                    NewUnits = col[-1].strip()
                    unitsMessage = " with units: '" + NewUnits + "'"
                self.add_Key(NewKey)
                self.set_Unit(NewKey, NewUnits)
                _verbose(self.speak, 1, " > found key: '" + NewKey + "'" + unitsMessage)
        elif units is None:
            for col in NewFrame.columns:
                if type(col) is str:
                    NewNames[col] = col.strip().replace(' ', '_').upper()
                elif type(col) in [list, tuple]:
                    NewNames[col] = ' '.join(list(map(str, col))).strip().replace(' ', '_').upper()
                else:
                    NewNames[col] = col

        NewFrame.columns = NewNames.values()  # NewFrame.rename(columns=NewNames,inplace=True)
        self.Frames[inputFile] = NewFrame

    # support functions for get_Vector:
    def loadVector(self, key, frame=None):
        """
        internal function to return a numpy vector from the Frame files
        """
        if key in self.vectors:
            return self.vectors[key]
        if key == self.DTindex:
            return self.DTindexValues

        if frame is None:
            frame = list(self.Frames.keys())
        elif frame in self.Frames:
            frame = [frame]
        else:
            return None

        if type(key) is str:
            key = key.strip()
            if len(key) == 0:
                return None
            if key == self.DTindex and self.lastFrame in self.Frames and key in self.Frames[
                self.lastFrame] and self.lastItem != '':
                result = self.Frames[self.lastFrame][
                    self.Frames[self.lastFrame][self.itemsCol[self.lastFrame]] == self.lastItem][key]

            for Frame in self.Frames:
                if ':' in key and ':' not in [key[0], key[-1]]:
                    if _mainKey(key) in self.Frames[Frame].columns:
                        if _itemKey(key) in self.Frames[Frame][self.itemsCol[Frame]].to_list():
                            self.lastItem = _itemKey(key)
                            self.lastFrame = Frame
                            result = self.Frames[Frame][self.Frames[Frame][self.itemsCol[Frame]] == _itemKey(key)][
                                _mainKey(key)]
                            result.index = \
                            self.Frames[Frame][self.Frames[Frame][self.itemsCol[Frame]] == _itemKey(key)][self.DTindex]
                # the next two option should never happen because key has been already processed by __getitem__
                elif ':' in key and key[0] == ':':
                    if key[1:] in self.Frames[Frame][self.itemsCol[Frame]]:
                        self.lastItem = _itemKey(key)
                        self.lastFrame = Frame
                        result = self.Frame[self.Frames[Frame][self.itemsCol[Frame]] == _itemKey(key)]
                elif ':' in key and key[-1] == ':':
                    if key[:-1] in self.Frames[Frame].columns:
                        self.lastItem = ''
                        self.lastFrame = Frame
                        result = self.Frames[Frame][key[:-1]]

        vector = Series(data=[0] * len(self.DTindexValues), index=self.DTindexValues)
        vector = vector + result
        self.vectors[key] = vector.to_numpy()
        return vector.to_numpy()

    def extract_Keys(self):
        keys = []
        for frame in self.Frames:
            for col in self.Frames[frame].columns:
                if col != self.itemsCol[frame]:
                    for item in set(self.Frames[frame][self.itemsCol[frame]]):
                        if not self.Frames[frame][self.Frames[frame][self.itemsCol[frame]] == item][col].isna().all():
                            if col not in ['DATE', 'DATES', 'TIME', 'YEARS', 'MONTHS', 'DAYS']:
                                keys.append(str(col) + ':' + str(item))
        self.keys_ = tuple(sorted(set(keys)))

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
        if len(self.keys_) == 0:
            self.extract_Keys()
        if pattern is None:
            return self.keys_
        else:
            keysList = []
            for key in self.keys_:
                if pattern in key:
                    keysList.append(key)
            return tuple(keysList)

    # def extract_Wells(self):
    #     """
    #     Will return a list of all the well names in case.

    #     If the pattern variable is different from None only groups
    #     matching the pattern will be returned; the matching is based
    #     on fnmatch(), i.e. shell style wildcards.
    #     """
    #     wellsList = [ K.split(':')[-1].strip() for K in self.keys_ if ( K[0] == 'W' and ':' in K ) ]
    #     wellsList = list( set( wellsList ) )
    #     wellsList.sort()
    #     self.wells = tuple( wellsList )

    #     return self.wells

    # def extract_Groups(self, pattern=None, reload=False):
    #     """
    #     Will return a list of all the group names in case.

    #     If the pattern variable is different from None only groups
    #     matching the pattern will be returned; the matching is based
    #     on fnmatch(), i.e. shell style wildcards.
    #     """
    #     groupsList = [ K.split(':')[-1].strip() for K in self.keys_ if ( K[0] == 'G' and ':' in K ) ]
    #     groupsList = list( set( groupsList ) )
    #     groupsList.sort()
    #     self.groups = tuple( groupsList )
    #     if pattern is not None:
    #         results = []
    #         for group in self.groups:
    #             if pattern in group:
    #                 results.append(group)
    #         return tuple(results)
    #     else:
    #         return self.groups

    # def extract_Regions(self, pattern=None):
    #     # preparing object attribute
    #     regionsList = [ K.split(':')[-1].strip() for K in self.keys_ if ( K[0] == 'G' and ':' in K ) ]
    #     regionsList = list( set( regionsList ) )
    #     regionsList.sort()
    #     self.groups = tuple( regionsList )
    #     if pattern is not None:
    #         results = []
    #         for group in self.groups:
    #             if pattern in group:
    #                 results.append(group)
    #         return tuple(results)
    #     else:
    #         return self.groups

    def extractDATE(self):
        dates = []
        for frame in self.Frames:
            for col in self.Frames[frame]:
                if type(self.Frames[frame][col][0]) is str:
                    if _isDate(self.Frames[frame][col][0]):
                        try:
                            self.Frames[frame][col] = pd.to_datetime(_strDate(self.Frames[frame][col]))
                            dates += self.Frames[frame][col].to_list()
                        except:
                            pass
        if len(dates) > 0:
            self.dates = np.array(sorted(set(dates)), dtype='datetime64[s]')
            self.vectors['DATE'] = self.dates.copy()
            self.add_Key('DATE')
            self.set_Unit('DATE', 'DATE')
            self.vectors['DATES'] = self.vectors['DATE']
            self.add_Key('DATES')
            self.set_Unit('DATES', 'DATE')
            self.start = min(self.dates)
            self.end = max(self.dates)
            return True
        return False

    def find_index(self):
        """
        identify the column that is common to all the frames, to be used as index.
        If there is a single frame the first column is used.
        """
        # check current KeyIndex
        KeyIndex = True
        IndexVector = None
        for frame in self.Frames:
            if self.DTindex not in self.Frames[frame].columns:
                KeyIndex = False
                break
            elif IndexVector is None:
                IndexVector = self.Frames[frame][self.DTindex]
            elif not IndexVector.equals(self.Frames[frame][IndexVector]):
                KeyIndex = False
                break
        if KeyIndex:
            if self.DTindex in ['DATE', 'DATES']:
                self.DTindexValues = self.dates
            else:
                indexValues = []
                for frame in self.Frames:
                    indexValues += self.Frames[frame][KeyIndex].to_list()
                indexValues = np.array(sorted(set(indexValues)))
            return self.DTindex

        # look for other index
        for Key in ('TIME', 'DATE', 'DATES', 'DAYS', 'MONTHS', 'YEARS') + self.keys_:
            KeyIndex = True
            IndexVector = None
            for frame in self.Frames:
                if Key not in self.Frames[frame].columns:
                    KeyIndex = False
                    break
                elif IndexVector is None:
                    IndexVector = np.array(sorted(set(self.Frames[frame][Key].to_list())))
                elif not IndexVector.equals(np.array(sorted(set(self.Frames[frame][Key])))):
                    KeyIndex = False
                    break
            if KeyIndex:
                self.DTindex = Key
                break

        if KeyIndex:
            if Key in ['DATE', 'DATES']:
                self.DTindexValues = self.dates
            else:
                indexValues = []
                for frame in self.Frames:
                    indexValues += self.Frames[frame][KeyIndex].to_list()
                indexValues = np.array(sorted(set(indexValues)))
            return self.DTindex
        else:
            self.DTindex = None

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
                if ':' in key:
                    if key[0] == 'W':
                        if key.split(':')[-1] in self.wells:
                            return self.get_Unit(key.split(':')[0])
                    if key[0] == 'G':
                        if key.split(':')[-1] in self.groups:
                            return self.get_Unit(key.split(':')[0])
                    if key[0] == 'R':
                        if key.split(':')[-1] in self.regions:
                            return self.get_Unit(key.split(':')[0])
                return None
            else:
                if key[0] == 'W':
                    UList = []
                    for W in self.get_wells():
                        if key + ':' + W in self.units:
                            UList.append(self.units[key + ':' + W])
                    if len(set(UList)) == 1:
                        self.units[key] = UList[0]
                        return UList[0]
                    else:
                        return None
                elif key[0] == 'G':
                    UList = []
                    for G in self.get_groups():
                        if key + ':' + G in self.units:
                            UList.append(self.units[key + ':' + G])
                    if len(set(UList)) == 1:
                        self.units[key] = UList[0]
                        return UList[0]
                    else:
                        return None
                elif key[0] == 'R':
                    UList = []
                    for R in self.get_regions():
                        if key + ':' + R in self.units:
                            UList.append(self.units[key + ':' + R])
                    if len(set(UList)) == 1:
                        self.units[key] = UList[0]
                        return UList[0]
                    else:
                        return None
                UList = None

        elif type(key) is str and key.strip() == '--EveryType--':
            key = []
            KeyDict = {}
            for each in self.keys_:
                if ':' in each:
                    key.append(_mainKey(each))
                    KeyDict[_mainKey(each)] = each
                else:
                    key.append(each)
            key = list(set(key))
            key.sort()
            tempUnits = {}
            for each in key:
                if each in self.units:
                    tempUnits[each] = self.units[each]
                elif each in self.keys_ and (each != 'DATES' and each != 'DATE'):
                    if self.results.unit(each) is None:
                        tempUnits[each] = self.results.unit(each)
                    else:
                        tempUnits[each] = self.results.unit(each).strip('( )').strip("'").strip('"')
                elif each in self.keys_ and (each == 'DATES' or each == 'DATE'):
                    tempUnits[each] = 'DATE'
                else:
                    if KeyDict[each] in self.units:
                        tempUnits[each] = self.units[KeyDict[each]]
                    elif KeyDict[each] in self.keys_:
                        if self.results.unit(KeyDict[each]) is None:
                            tempUnits[each] = self.results.unit(KeyDict[each])
                        else:
                            tempUnits[each] = self.results.unit(KeyDict[each]).strip('( )').strip("'").strip('"')
            return tempUnits
        elif type(key) in [list, tuple]:
            tempUnits = {}
            for each in key:
                if type(each) is str:
                    tempUnits[each] = self.get_Unit(each)
            return tempUnits
