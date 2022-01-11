# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:45:12 2020

@author: MCARAYA
"""

__version__ = '0.0.0'
__release__ = 220110
__all__ = ['H5']

from .mainObject import SimResult as _SimResult
from .._common.functions import _mainKey, _itemKey
from .._common.inout import _extension
from .._common.inout import _verbose
# from .._common.stringformat import isnumeric as _isnumeric
from .._Classes.Errors import CorruptedFileError
import numpy as np
import os
import h5py
import warnings
import datetime as dt



class H5(_SimResult):
    """
    object to contain HDF5 format results read from h5 file using h5py
    """

    def __init__(self, inputFile=None, verbosity=2, **kwargs) :
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = H5
        self.keynames = None
        self.numpy_dates =  None
        if type(inputFile) == str and len(inputFile.strip()) > 0:
            self.smspec = self.readSMSPEC(inputFile)
            self.loadSummary(inputFile, **kwargs)
            # if ('unload' in kwargs and kwargs['unload'] is True) or ('close' in kwargs and kwargs['close'] is True):
            #         return None
        if self.results is not None:
            self.initialize(**kwargs)

    def loadSummary(self, h5FilePath, **kwargs):
        if type(h5FilePath) is str :
            h5FilePath = h5FilePath.strip()
            if self.path is None :
                self.path = h5FilePath
            if _extension(h5FilePath)[0].lower() != '.h5' :
                newPath = _extension(h5FilePath)[2] + _extension(h5FilePath)[1] + '.h5'
                if os.path.isfile(newPath):
                    h5FilePath = newPath
                else:
                    newPath = _extension(h5FilePath)[2] + _extension(h5FilePath)[1] + '.H5'
                    if os.path.isfile( newPath ) :
                        h5FilePath = newPath

            if os.path.isfile(h5FilePath):
                if os.path.getsize(h5FilePath) == 0:
                    raise CorruptedFileError("\nThe .h5 file seems to be empty")
                _verbose( self.speak, 1, ' > loading HDF5 file:\n  ' + h5FilePath)
                self.results = h5py.File(h5FilePath, "r")
                # if ('unload' in kwargs and kwargs['unload'] is True) or ('close' in kwargs and kwargs['close'] is True):
                #     return None
                self.name = _extension(h5FilePath)[1]
                self.set_FieldTime()
                self.get_Wells(reload=True)
                self.get_Groups(reload=True)
                self.get_Regions(reload=True)
                self.get_Keys(reload=True)
                self.units = self.get_Unit(self.keys)
                _verbose( self.speak, 1, 'simulation runs from ' +  str(self.get_Dates()[0]) + ' to ' + str(self.get_Dates()[-1]))
                self.set_Vector('DATE', self.get_Vector('DATES')['DATES'], self.get_Unit('DATES'), DataType='datetime', overwrite=True)
                self.stripUnits()
                self.get_Attributes(reload=True)
                self.fill_FieldBasics()

            else :
                raise FileNotFoundError( "the file doesn't exist:\n  -> " + h5FilePath )
        else :
            print("h5FilePath must be a string")

    def readSMSPEC(self,smspecPath):
        """
        read the SMSPEC file and extract the well and group names
        """
        if type(smspecPath) is str :
            smspecPath = smspecPath.strip()
            if _extension(smspecPath)[0].lower() != '.SMSPEC' :
                newPath = _extension(smspecPath)[2] + _extension(smspecPath)[1] + '.SMSPEC'
                if os.path.isfile(newPath):
                    smspecPath = newPath
            if os.path.isfile(smspecPath):
                if os.path.getsize(smspecPath) == 0:
                    warnings.warn("\nThe .SMSPEC file seems to be empty")
            else :
                warnings.warn( "the file doesn't exist:\n  -> " + smspecPath )
        with open(smspecPath, 'r', errors='surrogateescape') as file:
            smspec = file.read()
        keywords_index =  smspec.index('\x00\x00\x10KEYWORDS')
        keywords_index = keywords_index + smspec[keywords_index:].index('\x00\x00\x03H') + 4
        names_index = keywords_index + smspec[keywords_index:].index('\x00\x00\x10NAMES   ') 
        keywords = smspec[keywords_index:names_index]
        keywords = [ keywords[i:i+8].strip() for i in range(0,len(keywords),8) ]

        names_index = names_index + smspec[names_index:].index('\x00\x00\x03H') + 4
        
        nums_index = names_index + smspec[names_index:].index('NUMS    ')
        
        names = smspec[names_index:nums_index]
        names = [ names[i:i+8].strip() for i in range(0,len(names),8) ]

        units_index = nums_index + smspec[nums_index:].index('\x00\x00\x10UNITS   ')
        units_index = units_index + smspec[units_index:].index('\x00\x00\x03H') + 4
        measrmnt_index = units_index + smspec[units_index:].index('\x00\x00\x10MEASRMNT')
        units = smspec[units_index:measrmnt_index]
        units = [ units[i:i+8].strip() for i in range(0,len(units),8) ]

        self.units = { keywords[i]+(':'+names[i] if len(names[i])>0 else '') : units[i] for i in range(len(keywords)) }
        
        self.keynames = {}
        for i in range(len(keywords)):
            if keywords[i] not in self.keynames:
                self.keynames[keywords[i]] = []
            if names[i] not in self.keynames[keywords[i]]:
                self.keynames[keywords[i]].append(names[i])

    def reload(self) :
        self.loadSummary(self.path)

    def readH5(self, key):
        """
        support function to extract data from the 'summary_vectors' key of the HDF5 file
        """
        main , item = _mainKey(key) , _itemKey(key)
        if main[0] == 'F':
            item_pos = 0
        elif main in self.keynames:
            if item in self.keynames[main]:
                item_pos = self.keynames[main].index(item)
        else:
            item_pos =  None
        
        item_h5 = list(self.results['summary_vectors'][main].keys())[item_pos]
        return np.array(self.results['summary_vectors'][main][item_h5]['values'])
            

    # support functions for get_Vector:
    def loadVector(self, key):
            """
            internal function to load a numpy vector from the HDF5 files
            """
            if str(key).upper().strip() in ["DATES", "DATE"]:
                self.get_Dates()
                if self.start is not None:
                    return self.numpy_dates
            else :
                return self.readH5(key)

    def get_Dates(self) :
        try:
            self.start = np.datetime64(str(self.results['general']['start_date'][2]) + '-' +
                                       str(self.results['general']['start_date'][1]).zfill(2) + '-' +
                                       str(self.results['general']['start_date'][0]).zfill(2) + 'T' +
                                       str(self.results['general']['start_date'][3]).zfill(2) + ':' +
                                       str(self.results['general']['start_date'][4]).zfill(2) + ':' +
                                       str(self.results['general']['start_date'][5]).zfill(2) + '.' +
                                       str(self.results['general']['start_date'][6])
                                       , 's')
        except:
            self.start = None

        if self.start is None:
            self.end = None
        else:
            self.numpy_dates = self.start + np.array([ np.timedelta64(dt.timedelta(float(t))) for t in self.results['general']['time'] ] )
            self.end = self.numpy_dates[-1]
        return self.numpy_dates

    def extract_Wells(self) :
        self.wells = tuple(self.results.wells())
        return self.wells

    def extract_Groups(self, pattern=None, reload=False) :
        """
        calls group method from libecl:

        Will return a list of all the group names in case.

        If the pattern variable is different from None only groups
        matching the pattern will be returned; the matching is based
        on fnmatch(), i.e. shell style wildcards.
        """
        if len(self.groups) == 0 or reload is True :
            self.groups = tuple(self.results.groups())
        if pattern is None :
            return self.groups
        else:
            return tuple(self.results.groups(pattern))

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
        if len(self.keys) == 0 or reload is True :
            self.keys = tuple( self.results.keys(pattern))
            for extra in ( 'TIME', 'DATE', 'DATES' ) :
                if extra not in self.keys :
                    self.keys = tuple( [extra] + list(self.keys) )
        if pattern is None :
            return self.keys
        else:
            return tuple( self.results.keys(pattern) )

    def extract_Regions(self, pattern=None) :
        # preparing object attribute
        regionsList = list( self.regions )
        for key in self.get_Keys() :
            if key[0] == 'R' :
                if ':' in key :
                    region = key.split(':')[1]
                    regionsList.append( region )
        regionsList = list( set( regionsList ))
        regionsList.sort()
        self.regions = tuple( regionsList )
        # preparing list to return
        if pattern != None :
            regionsList = []
            for region in self.regions :
                if pattern in region :
                    regionsList.append(region)
            return tuple(regionsList)
        else :
            return self.regions

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
            if Key in ['DATES','DATE']:
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
        elif type(Key) in [list,tuple] :
            tempUnits = {}
            for each in Key :
                if type(each) is str :
                    tempUnits[each] = self.get_Unit(each)
            return tempUnits
