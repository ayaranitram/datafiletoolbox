# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 11:00:20 2021

@author: MCARAYA
"""

__version__ = 0.0
__release__ = 210312
__all__ = ['TABLE']

from .mainObject import SimResult as _SimResult
from .._common.inout import _extension, _verbose
from .._common.functions import _mainKey, _itemKey
from .._common.stringformat import date as _strDate, getnumber as _getnumber, isDate as _isDate
from .._common.keywordsConversions import fromECLtoVIP as _fromECLtoVIP, fromVIPtoECL as _fromVIPtoECL #, fromCSVtoECL
from .._dictionaries import UniversalKeys as _UniversalKeys, VIPTypesToExtractVectors as _VIPTypesToExtractVectors
from .._dictionaries import ECL2VIPkey as _ECL2VIPkey, VIP2ECLtype as _VIP2ECLtype, VIP2ECLkey as _VIP2ECLkey #, ECL2VIPtype
# from datafiletoolbox.dictionaries import ECL2CSVtype, ECL2CSVkey, CSV2ECLtype, CSV2ECLkey
# from datetime import timedelta
import pandas as pd
from numpy import nan as NaN
import os


class TABLE(_SimResult):
    """
    object to contain data read from generic table files, like .txt or csv
    
    """
    def __init__(self, inputFile=None, verbosity=2, sep=None, header='infer', units='infer', names=None, overwrite=True) :
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = TABLE
        self.results = {}
        self.Frames = {}
        self.lastFrame = ''
        self.lastItem = ''
        self.null = NaN
        self.overwrite = False
        self.itemsCol = {}
        self.dates = None
        if type(inputFile) is str and len(inputFile.strip()) > 0 :
            if os.path.isfile(inputFile) :
                self.readTable(inputFile, sep=sep, header=header, units=units, names=names)
            else :
                print("file doesn't exists")
        if len(self.Frames) > 0:
            self.name = _extension(inputFile)[1]
            self.initialize()
    
    def initialize(self) :
        """
        run intensive routines, to have the data loaded and ready
        """
        self.findItemsCol()
        self.extract_Keys()
        self.extractDATE()
        self.find_index()
        self.extract_Wells()
        self.extract_Groups()
        self.extract_Regions()
        self.get_Attributes(None, True)
        if self.is_Key('DATES') and not self.is_Key('DATE') :
            self['DATE'] = 'DATES'
        if not self.is_Key('DATE') :
            self.createDATES()
        elif self.get_Unit('DATE') is None or self.get_Unit('DATE') != 'DATE' :
            self.set_Units('DATE', 'DATE', overwrite=True)
        if not self.is_Key('DATES') and self.is_Key('DATE') :
            self['DATES'] = 'DATE'
        if self.is_Key('DATES') and ( self.get_Unit('DATES') is None or self.get_Unit('DATES') != 'DATE' ) :
            self.set_Unit('DATES', 'DATE', overwrite=True)
        if not self.is_Key('TIME') and self.is_Key('DATE') :
            self['TIME'] = ( self('DATE').astype('datetime64[s]') - self.start ).astype('int') / (60*60*24)
        if self.is_Key('TIME') and ( self.get_Unit('TIME') is None or self.get_Unit('TIME').upper() in ['', 'NONE'] ) :
            self.set_Unit('TIME', 'DAYS', overwrite=True)
        _SimResult.initialize(self)
    
    def set_itemsCol(self,column,frame=None):
        if frame is None:
            for Frame in self.Frames:
                if column in self.Frames[Frame].columns:
                    self.itemsCol[Frame] = column
    
    def findItemsCol(self):
        for frame in self.Frames:
            for col in self.Frames[frame]:
                if str(self.Frames[frame][col].dtype) not in ['float64','float32','float','int64','int32','int']:
                    if type(self.Frames[frame][col][0]) is str:
                        if _isDate(self.Frames[frame][col][0]):
                            continue
                        else :
                            self.itemsCol[frame] = col
                            break
    
    def readTable(self, inputFile, sep=None, header='infer', units=None, names=None):
        """
        internal function to read a generic table from a file (header in first row, units in second row)
        """
        if type(header) is int :
            if type(units) is int :
                if header != units :
                    header = [header, units]
        elif type(header) in [list, tuple] :
            if type(units) is int :
                if units not in header :
                    header = list(header)+[units]
        elif type(header) is str and header.strip().lower() == 'infer':
            pass  # to be implemented
        
        if type(units) is str and units.strip().lower() == 'infer':
            units = None  # to be implemented
        elif type(units) is int:
            if type(header) is int:
                if units == header:
                    units = None
                else :
                    header = [header,units]
            elif type(header) in (list,tuple):
                if units in header:
                    units = None
                else:
                    header = list(header) + [units]

        try :
            NewFrame = pd.read_table(inputFile, sep=sep, header=header, engine='python')
        except ImportError:
            raise ImportError("Missing optional dependencies 'xlrd' and 'openpyxl'.\nInstall xlrd and openpyxl for Excel support.\nUse pip or conda to install xlrd and install openpyxl.")
        except :
            try:
                import xlrd
                try:
                    import openpyxl
                except:
                    raise ModuleNotFoundError("Missing optional dependency 'openpyxl'.\nInstall openpyxl for Excel support.\nUse pip or conda to install openpyxl.")
            except:
                raise ModuleNotFoundError("Missing optional dependency 'xlrd'.\nInstall xlrd for Excel support.\nUse pip or conda to install xlrd.")
            raise TypeError('Not able to read the excel file, please check input parameters and excel sheets format.')
        
        if inputFile in self.Frames:
            _verbose(self.speak, 2, "the file '"+str(inputFile)+"' will overwrite the previously loaded file with the same name.")
        
        NewNames = {}
        if units is not None:
            for col in NewFrame.columns:
                NewKey = ' '.join(list(map(str,col[0:-1]))).strip()
                NewNames[col] = NewKey
                if col[-1].startswith('Unnamed:') :
                    NewUnits = ''
                    unitsMessage = ''
                else :
                    NewUnits = col[-1].strip()
                    unitsMessage = " with units: '"+NewUnits+"'"
                self.add_Key(NewKey)
                self.set_Unit(NewKey, NewUnits)
                _verbose(self.speak, 1, " > found key: '"+NewKey+"'" + unitsMessage)
        elif units is None:
            for col in NewFrame.columns:
                if type(col) is str:
                    NewNames[col] = col.strip().replace(' ','_').upper()
                elif type(col) in [list,tuple]:
                    NewNames[col] = ' '.join(list(map(str,col))).strip().replace(' ','_').upper()
                else:
                    NewNames[col] = col

        NewFrame.rename(columns=NewNames,inplace=True)
        self.Frames[inputFile] = NewFrame

    # support functions for get_Vector:
    def loadVector(self, key, frame=None) :
        """
        internal function to return a numpy vector from the Frame files
        """
        if key in self.vectors:
            return self.vectors[key]
        
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
            if key == self.DTindex and self.lastFrame in self.Frames and key in self.Frames[self.lastFrame] and self.lastItem != '':
                return self.Frames[self.lastFrame][self.Frames[self.lastFrame][self.itemsCol[self.lastFrame]] == self.lastItem][key]
            for Frame in self.Frames:
                if ':' in key and ':' not in [key[0],key[-1]]:
                    if _mainKey(key) in self.Frames[Frame].columns:
                        if _itemKey(key) in self.Frames[Frame][self.itemsCol]:
                            self.lastItem = _itemKey(key)
                            self.lastFrame = Frame
                            return self.Frames[Frame][self.Frames[Frame][self.itemsCol[Frame]] == _itemKey(key)][_mainKey(key)]
                elif ':' in key and key[0] == ':':
                    if key[1:] in self.Frames[Frame][self.itemsCol[Frame]]:
                        self.lastItem = _itemKey(key)
                        self.lastFrame = Frame
                        return self.Frame[self.Frames[Frame][self.itemsCol[Frame]] == _itemKey(key)]
                elif ':' in key and key[-1] == ':':
                    if key[:-1] in self.Frames[Frame].columns:
                        self.lastItem = ''
                        self.lastFrame = Frame
                        return self.Frames[Frame][key[:-1]]
                   
        # if Frame is None and key in self.FramesIndex :
        #     Frame = self.FramesIndex[key][0]
        # elif Frame in self.Frames :
        #     pass # OK
        # else :
        #     _verbose(self.speak, 1, "the key '"+key+"' is not present in these frames.")
        #     return None
        # if self.lastFrame == '' :
        #     self.lastFrame = Frame

        # if key == self.DTindex :
        #     if key in self.Frames[self.lastFrame] :
        #         return self.Frames[self.lastFrame][self.FramesIndex[key][1]].to_numpy()
        #     elif key in self.FramesIndex :
        #         result = self.Frames[Frame][self.FramesIndex[key][1]]
        #         if len(result) == len(self.Frames[self.lastFrame]) :
        #             return result.to_numpy()
        #         else :
        #             return self.Frames[self.lastFrame].index.to_numpy()
        #     else :
        #         return None
        # elif key in self.FramesIndex :
        #     result = self.Frames[Frame][self.FramesIndex[key][1]].to_numpy()
        #     self.lastFrame = Frame
        #     return result
    
    def extract_Keys(self):
        keys = []
        for frame in self.Frames:
            for col in self.Frames[frame].columns:
                if col != self.itemsCol[frame]:
                    for item in set(self.Frames[frame][self.itemsCol[frame]]):
                        if not self.Frames[frame][ self.Frames[frame][self.itemsCol[frame]] == item ][col].isna().all():
                            keys.append(str(col) + ':' + str(item))
        self.keys = tuple(sorted(set(keys)))
        
    def list_Keys(self, pattern=None, reload=False) :
        """
        Return a StringList of summary keys matching @pattern.

        The matching algorithm is ultimately based on the fnmatch()
        function, i.e. normal shell-character syntax is used. With
        @pattern == "WWCT:*" you will get a list of watercut keys for
        all wells.

        If pattern is None you will get all the keys of summary
        object.
        """
        if len(self.keys) == 0:
            self.extract_Keys()
        if pattern is None :
            return self.keys
        else:
            keysList = []
            for key in self.keys:
                if pattern in key :
                    keysList.append(key)
            return tuple( keysList )
    
    def extract_Wells(self) :
        """
        Will return a list of all the well names in case.

        If the pattern variable is different from None only groups
        matching the pattern will be returned; the matching is based
        on fnmatch(), i.e. shell style wildcards.
        """
        wellsList = [ K.split(':')[-1].strip() for K in self.keys if ( K[0] == 'W' and ':' in K ) ]
        wellsList = list( set( wellsList ) )
        wellsList.sort()
        self.wells = tuple( wellsList )

        return self.wells

    def extract_Groups(self, pattern=None, reload=False) :
        """
        Will return a list of all the group names in case.

        If the pattern variable is different from None only groups
        matching the pattern will be returned; the matching is based
        on fnmatch(), i.e. shell style wildcards.
        """
        groupsList = [ K.split(':')[-1].strip() for K in self.keys if ( K[0] == 'G' and ':' in K ) ]
        groupsList = list( set( groupsList ) )
        groupsList.sort()
        self.groups = tuple( groupsList )
        if pattern != None :
            results = []
            for group in self.groups :
                if pattern in group :
                    results.append(group)
            return tuple(results)
        else :
            return self.groups

    def extract_Regions(self, pattern=None) :
        # preparing object attribute
        regionsList = [ K.split(':')[-1].strip() for K in self.keys if ( K[0] == 'G' and ':' in K ) ]
        regionsList = list( set( regionsList ) )
        regionsList.sort()
        self.groups = tuple( regionsList )
        if pattern != None :
            results = []
            for group in self.groups :
                if pattern in group :
                    results.append(group)
            return tuple(results)
        else :
            return self.groups

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
            self.dates = tuple(sorted(set(dates)))
            self.add_Key('DATE')

    def find_index(self) :
        """
        identify the column that is common to all the frames, to be used as index.
        If there is a single frame the first column is used.
        """
        # # check current KeyIndex
        # KeyIndex = True
        # IndexVector = None
        # for frame in self.Frames :
        #     if self.DTindex not in self.FramesIndex :
        #         KeyIndex = False
        #         break
        #     elif self.FramesIndex[self.DTindex][1] not in self.Frames[frame] :
        #         KeyIndex = False
        #         break
        #     elif IndexVector is None :
        #         IndexVector = self.Frames[frame][self.FramesIndex[self.DTindex][1]]
        #     elif not IndexVector.equals( self.Frames[frame][self.FramesIndex[IndexVector][1]] ) :
        #         KeyIndex = False
        #         break
        # if KeyIndex :
        #     return self.DTindex

        # # look for other index
        # for Key in ('TIME', 'DATE', 'DATES', 'DAYS', 'MONTHS', 'YEARS') + self.keys :
        #     KeyIndex = True
        #     IndexVector = None
        #     for frame in self.Frames :
        #         if Key not in self.FramesIndex :
        #             KeyIndex = False
        #             break
        #         if self.FramesIndex[Key][1] not in self.Frames[frame].columns :
        #             KeyIndex = False
        #             break
        #         elif IndexVector is None :
        #             IndexVector = self.Frames[frame][self.FramesIndex[Key][1]]
        #         elif not IndexVector.equals( self.Frames[frame][self.FramesIndex[Key][1]] ) :
        #             KeyIndex = False
        #             break
        #     if KeyIndex :
        #         self.DTindex = Key
        #         break

        # if KeyIndex :
        #     return self.DTindex
        # else :
        #     self.DTindex = None