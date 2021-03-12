# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 11:00:20 2021

@author: MCARAYA
"""

__version__ = 0.2
__release__ = 210305
__all__ = ['XLSX']

from .mainObject import SimResult as _SimResult
from .._common.inout import _extension, _verbose
from .._common.functions import _mainKey
import pandas as pd
import os


class XLSX(_SimResult):
    """
    object to contain data read from .xlsx files
    
    """
    def __init__(self, inputFile=None, verbosity=2, sheet_name=None, header=[0, 1], units=1, overwrite=True) :
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = XLSX
        self.results = {}
        self.Frames = {}
        self.FramesIndex = {}
        self.overwrite = False
        self.lastFrame = ''
        if type(inputFile) is str and len(inputFile.strip()) > 0 :
            if os.path.isfile(inputFile) :
                self.readSimExcel(inputFile, sheet_name=sheet_name, header=header, units=units)
            else :
                print("file doesn't exists")
        if len(self.Frames) > 0 :
            self.name = _extension(inputFile)[1]
            # if 'TIME' not in self.keys :
            #     if 'DATE' in self.keys :
            #         TIME = np.array( [0] + list( self('DATE')[1:] - self('DATE')[:-1] ) )
            self.initialize()

    def initialize(self) :
        """
        run intensive routines, to have the data loaded and ready
        """
        self.keys = tuple( sorted(self.keys) )
        self.extract_Wells()
        self.extract_Groups()
        self.extract_Regions()
        self.get_Attributes(None, True)
        self.find_index()
        _SimResult.initialize(self)
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

    def find_index(self) :
        """
        identify the column that is common to all the frames, to be used as index.
        If there is a single frame the first column is used.
        """
        # check current KeyIndex
        KeyIndex = True
        IndexVector = None
        for frame in self.Frames :
            if self.DTindex not in self.FramesIndex :
                KeyIndex = False
                break
            elif self.FramesIndex[self.DTindex][1] not in self.Frames[frame] :
                KeyIndex = False
                break
            elif IndexVector is None :
                IndexVector = self.Frames[frame][self.FramesIndex[self.DTindex][1]]
            elif not IndexVector.equals( self.Frames[frame][self.FramesIndex[IndexVector][1]] ) :
                KeyIndex = False
                break
        if KeyIndex :
            return self.DTindex

        # look for other index
        for Key in ('TIME', 'DATE', 'DATES', 'DAYS', 'MONTHS', 'YEARS') + self.keys :
            KeyIndex = True
            IndexVector = None
            for frame in self.Frames :
                if Key not in self.FramesIndex :
                    KeyIndex = False
                    break
                if self.FramesIndex[Key][1] not in self.Frames[frame].columns :
                    KeyIndex = False
                    break
                elif IndexVector is None :
                    IndexVector = self.Frames[frame][self.FramesIndex[Key][1]]
                elif not IndexVector.equals( self.Frames[frame][self.FramesIndex[Key][1]] ) :
                    KeyIndex = False
                    break
            if KeyIndex :
                self.DTindex = Key
                break

        if KeyIndex :
            return self.DTindex
        else :
            self.DTindex = None

    def readSimExcel(self, inputFile, sheet_name=None, header=[0, 1], units=1, combine_SheetName_ColumnName=False) :
        """
        internal function to read an excel file with SimDataFrame format (header in first row, units in second row)
        """
        if type(header) is int :
            if type(units) is int :
                if header != units :
                    header = [header, units]
        elif type(header) in [list, tuple] :
            if type(units) is int :
                if units not in header :
                    header = list(header)+[units]
        try :
            NewFrames = pd.read_excel(inputFile, sheet_name=sheet_name, header=header)
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
            
        if sheet_name is not None and type(NewFrames) is not dict :
            NewFrames = {str(sheet_name):NewFrames}

        for each in NewFrames :
            if each not in self.Frames :
                self.Frames[str(each)] = NewFrames[each]
                for col in NewFrames[each].columns :
                    NewKey = ' '.join(col[0:-1]).strip()
                    self.FramesIndex[NewKey] = ( each, col )
                    if col[-1].startswith('Unnamed:') :
                        NewUnits = ''
                        unitsMessage = ''
                    else :
                        NewUnits = col[-1].strip()
                        unitsMessage = " with units: '"+NewUnits+"'"
                    self.add_Key( NewKey )
                    self.set_Unit( NewKey, NewUnits )
                    _verbose(self.speak, 1, " > found key: '"+NewKey+"'" + unitsMessage )
            elif self.Frames[str(each)].equals(NewFrames[each]) :
                _verbose(self.speak, 2, "the sheet '"+each+"' was already loaded.")
            else :
                if self.overwrite :
                    _verbose(self.speak, 2, "the sheet '"+str(each)+"' will overwrite the previously loaded sheet.")
                else :
                    i = 1
                    while str(each)+'_'+str(i).zfill(2) in self.Frames :
                        i += 1
                    _verbose(self.speak, 2, "the sheet '"+str(each)+"' will be loaded as '"+str(each)+'_'+str(i).zfill(2)+"' to not overwrite the previously loaded sheet.")
                    self.Frames[str(each)+'_'+str(i).zfill(2)] = NewFrames[each]
                    for col in NewFrames[each].columns :
                        NewKey = ' '.join(list(map(str,col[0:-1]))).strip()
                        self.FramesIndex[NewKey] = ( str(each)+'_'+str(i).zfill(2), col )
                        if col[-1].startswith('Unnamed:') :
                            NewUnits = ''
                            unitsMessage = ''
                        else :
                            NewUnits = col[-1].strip()
                            unitsMessage = " with units: '"+NewUnits+"'"
                        self.add_Key( NewKey )
                        userVerbose, self.speak = self.speak, 0
                        self.set_Unit( NewKey, NewUnits )
                        self.speak = userVerbose
                        _verbose(self.speak, 1, " > found key: '"+NewKey+"'" + unitsMessage )

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

        if pattern is None :
            return self.keys
        else:
            keysList = []
            for key in self.keys:
                if pattern in key :
                    keysList.append(key)
            return tuple( keysList )

    # support functions for get_Vector:
    def loadVector(self, key, Frame=None) :
        """
        internal function to return a numpy vector from the Frame files
        """
        if Frame is None and key in self.FramesIndex :
            Frame = self.FramesIndex[key][0]
        elif Frame in self.Frames :
            pass # OK
        else :
            _verbose(self.speak, 1, "the key '"+key+"' is not present in these frames.")
            return None
        if self.lastFrame == '' :
            self.lastFrame = Frame

        if key == self.DTindex :
            if self.lastFrame in self.Frames and key in self.Frames[self.lastFrame] :
                return self.Frames[self.lastFrame][self.FramesIndex[key][1]].to_numpy()
            elif key in self.FramesIndex :
                result = self.Frames[Frame][self.FramesIndex[key][1]]
                if len(result) == len(self.Frames[self.lastFrame]) :
                    return result.to_numpy()
                else :
                    return self.Frames[self.lastFrame].index.to_numpy()
            else :
                return None
        elif key in self.FramesIndex :
            result = self.Frames[Frame][self.FramesIndex[key][1]].to_numpy()
            self.lastFrame = Frame
            return result

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

    def get_Unit(self, Key='--EveryType--') :
        """
        returns a string identifiying the unit of the requested Key

        Key could be a list containing Key strings, in this case a dictionary
        with the requested Keys and units will be returned.
        the Key '--EveryType--' will return a dictionary Keys and units
        for all the keys in the results file

        """
        if type(Key) is str and Key.strip() != '--EveryType--' :
            Key = Key.strip().upper()
            if Key in self.units :
                return self.units[Key]
            if Key == 'DATES' or Key == 'DATE' :
                    self.units[Key] = 'DATE'
                    return 'DATE'
            if Key in self.keys :
                return self.results.unit(Key)
            else:
                if Key[0] == 'W' :
                    UList=[]
                    for W in self.get_Wells() :
                        if Key+':'+W in self.units :
                            UList.append(self.units[Key+':'+W])
                        elif Key in self.keys :
                            UList.append( self.results.unit(Key+':'+W) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :
                        return None
                elif Key[0] == 'G' :
                    UList=[]
                    for G in self.get_Groups() :
                        if Key+':'+G in self.units :
                            UList.append(self.units[Key+':'+G])
                        elif Key in self.keys :
                            UList.append( self.results.unit(Key+':'+G) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :
                        return None
                elif Key[0] == 'R' :
                    UList=[]
                    for R in self.get_Regions() :
                        if Key+':'+R in self.units :
                            UList.append(self.units[Key+':'+R])
                        elif Key in self.keys :
                            UList.append( self.results.unit(Key+':'+R) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :
                        return None
                UList = None

        elif type(Key) is str and Key.strip() == '--EveryType--' :
            Key = []
            KeyDict = {}
            for each in self.keys :
                if ':' in each :
                    Key.append( _mainKey(each) )
                    KeyDict[ _mainKey(each) ] = each
                else :
                    Key.append(each)
            Key = list( set (Key) )
            Key.sort()
            tempUnits = {}
            for each in Key :
                if each in self.units :
                    tempUnits[each] = self.units[each]
                elif each in self.keys and ( each != 'DATES' and each != 'DATE' ) :
                    if self.results.unit(each) is None :
                        tempUnits[each] = self.results.unit(each)
                    else :
                        tempUnits[each] = self.results.unit(each).strip('( )').strip("'").strip('"')
                elif each in self.keys and ( each == 'DATES' or each == 'DATE' ) :
                    tempUnits[each] = 'DATE'
                else :
                    if KeyDict[each] in self.units :
                        tempUnits[each] = self.units[KeyDict[each]]
                    elif KeyDict[each] in self.keys :
                        if self.results.unit(KeyDict[each]) is None :
                            tempUnits[each] = self.results.unit(KeyDict[each])
                        else :
                            tempUnits[each] = self.results.unit(KeyDict[each]).strip('( )').strip("'").strip('"')
            return tempUnits
        elif type(Key) == list or type(Key) == tuple :
            tempUnits = {}
            for each in Key :
                if type(each) == str :
                    tempUnits[each] = self.get_Unit(each)
            return tempUnits