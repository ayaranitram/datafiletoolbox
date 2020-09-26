# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:45:12 2020

@author: MCARAYA
"""

__version__ = '0.0.20-09-13'

from datafiletoolbox.SimulationResults.mainObject import SimResult
from datafiletoolbox.common.functions import mainKey
from datafiletoolbox.common.inout import extension
from datafiletoolbox.common.inout import verbose 

import numpy as np
import os


try :
    # try to use libecl instalation from pypi.org
    from ecl.summary import EclSum
    from ecl.version import version as libecl_version
    print('\n using libecl version ' + str(libecl_version))
except :
    # try to use my compiled version of libecl from https://github.com/equinor/libecl
    eclPath = extension(str(os.getcwd()))[3] + '/datafiletoolbox/equinor/libecl/win10/lib/python' 
    os.environ['PYTHONPATH'] = eclPath + ';' + os.environ['PYTHONPATH']
    eclPath = eclPath + ';' + extension(str(os.getcwd()))[3] + '/datafiletoolbox/equinor/libecl/win10/lib'
    eclPath = eclPath + ';' + extension(str(os.getcwd()))[3] + '/datafiletoolbox/equinor/libecl/win10/bin'
    os.environ['PATH'] = eclPath + ';' + os.environ['PATH']
    #from datafiletoolbox.equinor.libecl.win10.lib.python import ecl
    from datafiletoolbox.equinor.libecl.win10.lib.python.ecl.summary import EclSum
    print('\n using ecl from https://github.com/equinor/libecl compiled for Windows10')


class ECL(SimResult):
    """
    object to contain eclipse format results read from SMSPEC using libecl from equinor 
    """
    def __init__(self,inputFile=None,verbosity=2) :
        SimResult.__init__(self,verbosity=verbosity)
        self.kind = ECL
        if type(inputFile) == str and len(inputFile.strip()) > 0 :
            self.loadSummary(inputFile)
        self.initialize()

    def loadSummary(self,SummaryFilePath):
        if type(SummaryFilePath) == str :
            SummaryFilePath = SummaryFilePath.strip()
            if self.path is None :
                self.path = SummaryFilePath
            if extension(SummaryFilePath)[0] != '.SMSPEC' :
                newPath = extension(SummaryFilePath)[2] + extension(SummaryFilePath)[1] + '.SMSPEC'
                if os.path.isfile(newPath) :
                    SummaryFilePath = newPath
                else:
                    newPath = extension(SummaryFilePath)[2] + 'RESULTS/' + extension(SummaryFilePath)[1] + '.SMSPEC' 
                    if os.path.isfile( newPath ) :
                        SummaryFilePath = newPath
                        verbose( self.speak , 3 , "\nWARNING: '.SMSPEC' file found in 'RESULTS' subdirectory, not in the same folder the '.DATA' is present.\n")
                    
            if os.path.isfile(SummaryFilePath) :
                verbose( self.speak , 1 , ' > loading summary file:\n  ' + SummaryFilePath)
                self.results = EclSum(SummaryFilePath) # ecl.summary.EclSum(SummaryFilePath)
                self.name = extension(SummaryFilePath)[1]
                self.set_FieldTime()
                self.get_Wells(reload=True)
                self.get_Groups(reload=True)
                self.get_Regions(reload=True)
                self.get_Keys(reload=True)
                self.units = self.get_Unit(self.keys)
                verbose( self.speak , 1 , 'simulation runs from ' +  str( self.get_Dates()[0] ) + ' to ' + str( self.get_Dates()[-1] ) )
                self.set_Vector('DATE' , self.get_Vector('DATES')['DATES'],self.get_Unit('DATES') , DataType='datetime' , overwrite=True)
                self.stripUnits()
                self.get_Attributes(reload=True)
                self.fill_FieldBasics()
                
            else :
                print("the file doesn't exists:\n  -> " + SummaryFilePath)
        else :
            print("SummaryFilePath must be a string")
        
    def reload(self) :
        self.loadSummary(self.path)
        
    # support functions for get_Vector:
    def loadVector(self,key) :
            """ 
            internal function to load a numpy vector from the summary files
            """
            if str(key).upper().strip() == "DATES" :
                return self.results.numpy_dates
            else :    
                return self.results.numpy_vector(str(key).upper().strip())  
    
    def set_FieldTime(self) :
        if len( self.get_Restart() ) > 0 :
            FieldTime = self.checkRestarts('TIME')['TIME']
        else :
            FieldTime = self.loadVector('TIME') 
        if FieldTime is None :
            if self.get_Vector('TIME')['TIME'] is not None :
                FieldTime = self.get_Vector('TIME')['TIME'] 
        if FieldTime is not None :
            self.fieldtime = ( min(FieldTime) , max(FieldTime) , FieldTime )          
    
    def get_Dates(self) :
        self.start = np.datetime64(self.results.start_date , 's' )
        try :
            self.end = self.results.end_date
        except :
            self.end = self.start + int(max(self.get_Vector('TIME')['TIME']))
        return self.results.numpy_dates
    
    def extract_Wells(self) :
        self.wells = self.results.wells() 
        return self.wells
    
    def extract_Groups(self,pattern=None,reload=False) :
        """
        calls group method from libecl:
        
        Will return a list of all the group names in case.

        If the pattern variable is different from None only groups
        matching the pattern will be returned; the matching is based
        on fnmatch(), i.e. shell style wildcards.
        """
        if len(self.groups) == 0 or reload == True :
            self.groups = tuple( self.results.groups() )
        if pattern is None :
            return self.groups
        else:
            return tuple( self.results.groups(pattern) )
        
    def list_Keys(self,pattern=None,reload=False) :
        """
        Return a StringList of summary keys matching @pattern.

        The matching algorithm is ultimately based on the fnmatch()
        function, i.e. normal shell-character syntax is used. With
        @pattern == "WWCT:*" you will get a list of watercut keys for
        all wells.

        If pattern is None you will get all the keys of summary
        object.
        """
        if len(self.keys) == 0 or reload == True :
            self.keys = tuple( self.results.keys(pattern) )
            for extra in ( 'TIME' , 'DATE', 'DATES' ) :
                if extra not in self.keys :
                    self.keys = tuple( [extra] + list(self.keys) )
        if pattern is None :
            return self.keys
        else:
            return tuple( self.results.keys(pattern) )
        
    def extract_Regions(self,pattern=None) :
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
    
    def get_Unit(self,Key='--EveryType--') :
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
                    Key.append( mainKey(each) )
                    KeyDict[ mainKey(each) ] = each
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
        
            