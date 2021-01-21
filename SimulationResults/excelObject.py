# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 11:00:20 2021

@author: MCARAYA
"""

__version__ = '0.1.20-10-18'
__all__ = ['XLSX']

from .mainObject import SimResult as _SimResult
from .._common.inout import _extension , _verbose
from .._common.functions import _mainKey , _wellFromAttribute
from .._common.stringformat import date as _strDate , getnumber as _getnumber
from .._common.keywordsConversions import fromECLtoVIP as _fromECLtoVIP, fromVIPtoECL as _fromVIPtoECL #, fromCSVtoECL
from .._dictionaries import UniversalKeys as _UniversalKeys , VIPTypesToExtractVectors as _VIPTypesToExtractVectors
from .._dictionaries import ECL2VIPkey as _ECL2VIPkey , VIP2ECLtype as _VIP2ECLtype, VIP2ECLkey as _VIP2ECLkey #, ECL2VIPtype
# from datafiletoolbox.dictionaries import ECL2CSVtype , ECL2CSVkey , CSV2ECLtype , CSV2ECLkey


# from datetime import timedelta
import pandas as pd
import numpy as np
import os

class XLSX(_SimResult):
    """
    object to contain data read from .xlsx files
    
    """
    def __init__(self,inputFile=None,verbosity=2,sheet_name=None,header=[0,1],units=1,overwrite=True) :
        _SimResult.__init__(self,verbosity=verbosity)
        self.kind = XLSX
        self.Frames = {}
        self.FramesIndex = {}
        self.overwrite = False
        if type(inputFile) is str and len(inputFile.strip()) > 0 :
            if os.path.isfile(inputFile) :
                self.readSimExcel(inputFile,sheet_name=sheet_name,header=header,units=units)
            else :
                print("file doesn't exists")
        if len(self.Frames) > 0 :
            self.name = _extension(inputFile)[1]
            self.extract_Wells()
            self.extract_Groups()
            self.extract_Regions()
            self.get_Attributes(None,True)
            self.initialize()
    
    def readSimExcel(self,inputFile,sheet_name=None,header=[0,1],units=1,combine_SheetName_ColumnName=False) :
        """
        internal function to read an excel file with SimDataFrame format (header in first row, units in second row)
        """
        if type(header) is int :
            if type(units) is int :
                if header != units :
                    header = [header,units]
        elif type(header) in [list,tuple] :
            if type(units) is int :
                if units not in header :
                    header = list(header)+[units]
        try :
            NewFrames = pd.read_excel(inputFile,sheet_name=sheet_name,header=header)
        except :
            NewFrames = {}
            _verbose(self.speak,-1,'not able to read the excel file, please check input parameters and excel sheets format.')
            return None
        
        if sheet_name is not None and type(NewFrames) is not dict :
            NewFrames = {str(sheet_name):NewFrames}
        
        for each in NewFrames :
            if each not in self.Frames :
                self.Frames[str(each)] = NewFrames[each]
                for col in NewFrames[each].columns :
                    NewKey = ' '.join(col[0:-1]).strip()
                    self.FramesIndex[NewKey] = each
                    if col[-1].startswith('Unnamed:') :
                        NewUnits = ''
                        unitsMessage = ''
                    else :
                        NewUnits = col[-1].strip()
                        unitsMessage = " with units: '"+NewUnits+"'"
                    self.add_Key( NewKey ) 
                    self.set_Unit( NewKey, NewUnits )
                    _verbose(self.speak,1," > found key: '"+NewKey+"'" + unitsMessage )
            elif self.Frames[str(each)].equals(NewFrames[each]) :
                _verbose(self.speak,2,"the sheet '"+each+"' was already loaded.")
            else :
                if self.overwrite :
                    _verbose(self.speak,2,"the sheet '"+str(each)+"' will overwrite the previously loaded sheet.")
                else :
                    i = 1
                    while str(each)+'_'+str(i).zfill(2) in self.Frames :
                        i += 1
                    _verbose(self.speak,2,"the sheet '"+str(each)+"' will be loaded as '"+str(each)+'_'+str(i).zfill(2)+"' to not overwrite the previously loaded sheet.")
                    self.Frames[str(each)+'_'+str(i).zfill(2)] = NewFrames[each]
                    for col in NewFrames[each].columns :
                        NewKey = ' '.join(col[0:-1]).strip()
                        self.FramesIndex[NewKey] = str(each)+'_'+str(i).zfill(2)
                        if col[-1].startswith('Unnamed:') :
                            NewUnits = ''
                            unitsMessage = ''
                        else :
                            NewUnits = col[-1].strip()
                            unitsMessage = " with units: '"+NewUnits+"'"
                        self.add_Key( NewKey ) 
                        self.set_Unit( NewKey, NewUnits )
                        _verbose(self.speak,1," > found key: '"+NewKey+"'" + unitsMessage )
        
    # support functions for get_Vector:
    def loadVector(self,key,Frame=None) :
        """ 
        internal function to return a numpy vector from the Frame files
        """
        if Frame is None and key in self.FramesIndex :
            Frame = self.FramesIndex[key]
        else :
            _verbose(self.speak,1,"the key '"+key+"' is not present in these frames.")
            return None
        if key == self.DTindex :
            if key in self.Frames[self.lastFrame] :
                return self.Frames[self.lastFrame][key].to_numpy()
            elif key in self.FramesIndex :
                result = self.Frames[self.FramesIndex[key]][key]
                if len(result) == len(self.Frames[self.lastFrame]) :
                    return result.to_numpy()
                else :
                    return self.Frames[self.lastFrame].index.to_numpy()
            else :
                return None
        elif key in self.FramesIndex :
            return self.Frames[self.FramesIndex[key]][key]
    
    def extract_Wells(self) : 
                
        wellsList = [ K.split(':')[-1].strip() for K in self.keys if ( K[0] == 'W' and ':' in K ) ]
        wellsList = list( set( wellsList ) )
        wellsList.sort()
        self.wells = tuple( wellsList ) 

        return self.wells
            
    def extract_Groups(self,pattern=None,reload=False) :
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
        
    def extract_Regions(self,pattern=None) :
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