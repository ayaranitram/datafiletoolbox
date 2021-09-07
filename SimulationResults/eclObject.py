# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:45:12 2020

@author: MCARAYA
"""

__version__ = '0.25.4'
__release__ = 210907
__all__ = ['ECL']

from .mainObject import SimResult as _SimResult
from .._common.functions import _mainKey
from .._common.inout import _extension
from .._common.inout import _verbose
from .._Classes.EclSumLoader import EclSumLoader
import numpy as np
import os


class ECL(_SimResult):
    """
    object to contain eclipse format results read from SMSPEC using libecl from equinor
    """
    loadEclSum = EclSumLoader()

    def __init__(self, inputFile=None, verbosity=2, **kwargs) :
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = ECL
        if type(inputFile) == str and len(inputFile.strip()) > 0 :
            self.loadSummary(inputFile, **kwargs)
            if 'unload' in kwargs and kwargs['unload'] is True:
                    return None
        if self.results is not None :
            self.initialize(**kwargs)

    def loadSummary(self, SummaryFilePath, **kwargs):
        if type(SummaryFilePath) is str :
            SummaryFilePath = SummaryFilePath.strip()
            if self.path is None :
                self.path = SummaryFilePath
            if _extension(SummaryFilePath)[0] != '.SMSPEC' :
                newPath = _extension(SummaryFilePath)[2] + _extension(SummaryFilePath)[1] + '.SMSPEC'
                if os.path.isfile(newPath) :
                    SummaryFilePath = newPath
                else:
                    newPath = _extension(SummaryFilePath)[2] + 'RESULTS/' + _extension(SummaryFilePath)[1] + '.SMSPEC'
                    if os.path.isfile( newPath ) :
                        SummaryFilePath = newPath
                        _verbose( self.speak, 3, "\nWARNING: '.SMSPEC' file found in 'RESULTS' subdirectory, not in the same folder the '.DATA' is present.\n")

            if os.path.isfile(SummaryFilePath):
                if not os.path.isfile(SummaryFilePath[:-6]+'UNSMRY'):
                    raise FileNotFoundError( "the file doesn't exist:\n  -> " + _extension(SummaryFilePath)[2] + _extension(SummaryFilePath)[1] +'.UNSMRY' )
                _verbose( self.speak, 1, ' > loading summary file:\n  ' + SummaryFilePath)
                EclSummary = ECL.loadEclSum
                self.results = EclSummary(SummaryFilePath, **kwargs) # ecl.summary.EclSum(SummaryFilePath)
                if 'unload' in kwargs and kwargs['unload'] is True:
                    return None
                self.name = _extension(SummaryFilePath)[1]
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
                # print("\n ERROR the file doesn't exists:\n  -> " + SummaryFilePath)
                if not os.path.isfile(SummaryFilePath[:-6]+"UNSMRY"):
                    raise FileNotFoundError( "the files doesn't exist:\n  -> " + SummaryFilePath[:-5]+".UNSMRY\n  -> " + SummaryFilePath )
                raise FileNotFoundError( "the file doesn't exist:\n  -> " + SummaryFilePath )
        else :
            print("SummaryFilePath must be a string")

    def reload(self) :
        self.loadSummary(self.path)

    # support functions for get_Vector:
    def loadVector(self, key) :
            """
            internal function to load a numpy vector from the summary files
            """
            if str(key).upper().strip() in ["DATES", "DATE"] :
                return self.results.numpy_dates
            else :
                return self.results.numpy_vector(str(key).upper().strip())

    def get_Dates(self) :
        try:
            self.start = np.datetime64(self.results.start_date, 's')
        except:
            self.start = None
        try :
            self.end = self.results.end_date
        except :
            if self.start is None:
                self.end = None
            else:
                self.end = self.start + int(max(self.get_Vector('TIME')['TIME']))
        return self.results.numpy_dates

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
