# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:14:35 2020

@author: MCARAYA
"""

__version__ = '0.0.20-05-19'

from datafiletoolbox.dictionaries import dictionaries
from datafiletoolbox.Classes.Errors import OverwrittingError
from datafiletoolbox.common.stringformat import date as strDate
from datafiletoolbox.common.stringformat import isDate
from datafiletoolbox.common.functions import is_SimulationResult 
from datafiletoolbox.common.inout import extension
from datafiletoolbox.common.inout import verbose 
from datafiletoolbox.PlotResults.SmartPlot import Plot

# from .vipObject import VIP
# from .SimulationResults import ECL

from bases.units import unit
from bases.units import convertUnit
from bases.units import convertible as convertibleUnits

from matplotlib.colors import is_color_like
from datetime import timedelta

import pandas as pd
import numpy as np
import fnmatch
import random
import json
import os


# verbose(1,1,'\n  initializing most commong units conversions...')
verbose(0,0,convertibleUnits('SM3','MMstb',False))
verbose(0,0,convertibleUnits('SM3','Bscf',False))
verbose(0,0,convertibleUnits('SM3','Tscf',False))
verbose(0,0,convertibleUnits('STM3','MMstb',False))
verbose(0,0,convertibleUnits('KSTM3','MMstb',False))
verbose(0,0,convertibleUnits('KSM3','Bscf',False))
verbose(0,0,convertibleUnits('MSM3','Tscf',False))
verbose(0,0,convertibleUnits('SM3/DAY','Mstb/day',False))
verbose(0,0,convertibleUnits('SM3/DAY','stb/day',False))
verbose(0,0,convertibleUnits('SM3/DAY','MMscf/day',False))
verbose(0,0,convertibleUnits('SM3/DAY','Mscf/day',False))
verbose(0,0,convertibleUnits('STM3/DAY','Mstb/day',False))
verbose(0,0,convertibleUnits('STM3/DAY','stb/day',False))
verbose(0,0,convertibleUnits('KSM3/DAY','MMscf/day',False))
verbose(0,0,convertibleUnits('KSM3/DAY','Mscf/day',False))
verbose(0,0,convertibleUnits('STM3/DAY','SM3/DAY',False))
verbose(0,0,convertibleUnits('KSTM3/DAY','SM3/DAY',False))
verbose(0,0,convertibleUnits('KSM3/DAY','SM3/DAY',False))
verbose(0,0,convertibleUnits('STM3','SM3',False))
verbose(0,0,convertibleUnits('KSTM3','SM3',False))
verbose(0,0,convertibleUnits('KSM3','SM3',False))
verbose(0,0,convertibleUnits('MSM3','SM3',False))
verbose(0,0,convertibleUnits('KPA','BARSA',False))
verbose(0,0,convertibleUnits('BARSA','psia',False))
verbose(0,0,convertibleUnits('KPA','psia',False))
verbose(0,0,convertibleUnits('DATE','DATES',False))
verbose(0,0,convertibleUnits('DAY','DAYS',False))
timeout = 0.1


class SimResult(object):
    """       ___________________________________
    <<< HELP of Simulation Result Objects >>>
    
     0) Basic Concepts:
         The results of the simulation are loaded in this object.
         To access the results, the Keys or Attributes (in eclipse style) 
         must be provided as string:
             Key are the eclipse keywords for a especific vectors, i.e.:
                 'FOIP'
                 'WWPR:WELL-X'
                 'GOPR:GROUP1'
                 'RPRH:1'
            Attributes are the root of the keyword, this will return all the
            keywords matching this root, i.e.:
                'WOPR'
                'GGIT'
                'ROIP'
    
     1) Simple Use:
      A) Calling the ObjectVariable:
            In: ObjectVariable( Key , Index )
            
        -> Calling the object with no argument will return this help. i.e.:
            In: ObjectVariable()
                   ___________________________________
                <<< HELP of Simulation Result Objects >>>
                
        -> Calling the object with a string (a single key) as Key argument will 
           return a Numpy array of the requested key. 
           The Index argument is ignored in this case, i.e.:
            In: ObjectVariable( 'FOIP' ) 
            Out: 
            array([69170384., 69170384., 69170384., ..., 30077594., 30077594., 30069462.])
        
        -> Calling the object with a list (one or multiple keys) as Key argument
           will return a Pandas DataFrame.
           The Index argument is 'TIME' by default but any other key can be 
           selected as index, i.e.:
            In: ObjectVariable( [ 'FOIP' , 'FOPT' ] , 'DATE' )
            Out: 
                                       FOIP        FOPT
            1996-05-04 00:00:00  69170384.0         0.0
            1996-05-07 03:36:00  69170384.0         0.0
                                    ...         ...
            2043-12-11 00:00:00  30077594.0  41477948.0
            2043-12-31 00:00:00  30069462.0  41483604.0
            
      B) Selection like Pandas DataFrame:
         The vectors can be requested to the SimulationResult object in the 
         same way columns are selected from a Pandas DataFrame, i.e.:
             
           > a single Key between single square braket 
           [ Key ] returns a Pandas Series with the column Key, i.e. : 
            In: ObjectVariable[ 'FOPR' ]
            Out:
            0.00          0.000000
            3.15          0.000000
                           ...
            17387.00    286.179718
            17407.00    281.440918
            Name: FOPR, Length: 7692, dtype: float64
            
           > one or multiple Key or Attributes* between double square braket 
           [[ Key , Attribute ]] returns a Pandas DataFrame, i.e. : 
            In: ObjectVariable[[ 'FOPR' , 'WOPR' ]]
            Out:
                            FOPR      WOPR:W_1  ...    WOPR:W_n-1      WOPR:W_n
            0.00        0.000000           0.0  ...           0.0           0.0
            3.15        0.000000           0.0  ...           0.0           0.0
                         ...           ...  ...           ...           ...
            17387.00  286.179718           0.0  ...           0.0           0.0
            17407.00  281.440918           0.0  ...           0.0           0.0
            
            [7692 rows x 141 columns]
            
           * Notice that providing an Attribute will return all the Keys related
           to that Attribute.
        
      C) It is possible to change the default Index  with the .set_index() method.
         By default the index is the 'TIME' series.
         Other useful indexes could be 'DATE' or the cumulatives like 'FOPT'.
         Any Key can be used as index, but keep in mind the phisical or numerical
         meaning and consistency of the index you are setting.
    
     2) Available Methods:
        .describe
            returns a descriptive dataframe of this object content, i.e.:
                In: ObjectVariable.describe
                Out:
                              time        dates kind   keys attributes wells groups regions
                    count   7692.0         7692  ECL  19726        442   140     12      30
                    min        0.0  04-MAY-1996                                            
                    max    17407.0  31-DEC-2043                                            
                                        
        .get_Vector( list_of_keywords )
            returns a dictionary with the Numpy arrays for the requested 
            keywords, i.e.:
                In: ObjectVariable.get_Vector( [ 'FOIP' , 'FOPT' , 'FOPR' ] )
                Out:
                    {'FOPR': array([  0.        ,   0.        ,   0.        , ..., 282.94104004, 282.04125977, 281.44091797]),
                     'FOPT': array([       0.,        0.,        0., ..., 41480784., 41482196., 41483604.]),
                     'FOIP': array([69170384., 69170384., 69170384., ..., 30077594., 30077594., 30069462.])}
        
        .set_Vector( Key , VectorData , Units , DataType='auto' , overwrite=None)
            loads a vector into the SimulationResult object, arguments are:
                Key : the name or keyword where the data will be loaded
                VectorData : a Numpy array (of the same lenght as the arrays already in the results)
                Units : a string indicating the units of these data
                DataType : the strings 'float', 'int', 'date' or 'auto'
                overwrite : True or False, if True any existing data under the same Key will be overwritten. 

        .get_DataFrame( list_of_keywords , optional index )
            returns a Pandas DataFrame with the requested keywords. 
            The optional argument Index can be used to obtain a DataFrame 
            indexed by any other Key from the simulation, default index 
            is 'TIME' but 'DATE', volume in place or cumulatives can be 
            good examples of other useful indexes. i.e.:
                In: ObjectVariable.get_DataFrame( [ 'WOPR:W1','WOPT:W1' ] , 'DATE' )
                Out:
                                          WOPT:W1       WOPR:W1
                1996-05-04 00:00:00           0.0           0.0
                1996-05-07 03:36:00           0.0           0.0
                                          ...           ...
                2043-12-11 00:00:00     6499611.0           0.0
                2043-12-31 00:00:00     6499611.0           0.0
                                    
                In: ObjectVariable.get_DataFrame( [ 'WOPR:W1','WOPR:W2' ] , 'FOPT' )
                Out:
                                 WOPT:W1       WOPT:W2
                0.0                  0.0         0.000
                0.0                  0.0         0.000
                                 ...           ...
                41477948.0     6499611.0   1918401.625
                41483604.0     6499611.0   1918401.625
                
        .get_Unit( keyword_as_string or list_of_keywords ) 
            if the argument is a string (a single keyword), 
            returns the units of that keyword as a strinG, i.e.:
                In: ObjectVariable.get_Unit('FOPT')
                Out: 'SM3'
                
            if the argument is a list (one or multiple keywords), returns 
            a dictionary containg the units of that keywords as a strings.
                In: ObjectVariable.get_Unit(['FOPT','FOPR'])
                {'FOPT': 'SM3', 'FOPR': 'SM3/DAY'}
            
            if no argument is provided, returns a dictionary with all the 
            units defined in the simulation results, i.e.:
                In: ObjectVariable.get_Unit()
                Out: {'FOPT': 'SM3', 'FOPR': 'SM3/DAY', ...}
            
            
    """
    
    UniversalKeys = ( 'DATE','DATES','TIME','DAY','DAYS','MONTH','MONTHS','YEAR','YEARS')
    
    VIP2ECLkey = dictionaries.VIP2ECLkey
    ECL2VIPkey = {}
    for each in VIP2ECLkey :
        ECL2VIPkey[VIP2ECLkey[each]] = each

    VIP2ECLtype = dictionaries.VIP2ECLtype
    ECL2VIPtype = {}
    for each in VIP2ECLtype :
        ECL2VIPtype[VIP2ECLtype[each]] = each
        
    VIPnotECL = []
    
    VIPTypesToExtractVectors = ( 'FIELD' , 'WELL' , 'AREA', 'REGION' )
    KnownCSVsections = ( '[S3INFO]' , '[HEADERS]' , '[DATA]' )
    CSV_Variable2Verbose = {}
    CSV_Verbose2Variable = {}
    
    CSV2ECLkey = dictionaries.CSV2ECLkey
    ECL2CSVkey = {}
    for each in CSV2ECLkey :
        ECL2CSVkey[CSV2ECLkey[each]] = each
    CSV2ECLtype = dictionaries.CSV2ECLtype
    ECL2CSVtype = {}
    for each in CSV2ECLtype :
        ECL2CSVtype[CSV2ECLtype[each]] = each
     
    VIP2CSVkey = dictionaries.VIP2CSVkey
    CSV2VIPkey = {}
    for each in VIP2CSVkey :
        CSV2VIPkey[VIP2CSVkey[each]] = each
    
    def testECLmolarKey(key) :
        if '_' in key :
            if ':' in key :
                var = key.strip().split(':')[0].upper()
                clss = var[0]
                var = var[1:]
                member = key.strip().split(':')[1].upper()
            else :
                member = ''
                var = key.strip().upper()
                clss = var[0]
                var = var[1:]
            if '_' in var :
                comp = var[var.index('_'):]
            else :
                return False
            try :
                comp = int(comp)
            except :
                return False
            if var[0] in ('X','Y','Z') :
                xyz = var[0]
            elif var[0] == 'C' :
                xyz = ''
                if var[var.index('_')-1] == 'R' :
                    xyz = 'Q'
                elif var[var.index('_')-1] == 'T' :
                    xyz = 'C'
                else:
                    return False
                if var[var.index('_')-2] in ( 'P','I' ) :
                    pi = var[var.index('_')-2]
                else :
                    return False
            else :
                return False
            if clss in SimResult.ECL2VIPtype :
                clss = SimResult.ECL2VIPtype[clss]
            else :
                return False
            VIPkey = xyz + str(comp) + pi
            return ( VIPkey , clss , member )
        else :
            return False
        
    def testCSVmolarKey(variableORkey,CLASStype=None,MEMBER=None) :
        variableORkey = variableORkey.strip().upper()
        if ':' in variableORkey :
            if MEMBER is None and len(variableORkey.split(':')[1]) > 0 :
                MEMBER = variableORkey.split(':')[1]
            variableORkey.split(':')[0]
        if variableORkey[-1] in ( 'P','I' ) :
            pi = variableORkey[-1]
        else :
            return False
        if variableORkey[0] in ('X','Y','Z') :
            xyz = variableORkey[0]
            rt = 'MF'
            pi = ''
        elif variableORkey[0] == 'Q' :
            rt = 'R'
            xyz = 'CM'
        elif variableORkey[0] == 'C' :
            rt = 'T'
            xyz = 'CM'
        else :
            return False
        
        comp = variableORkey[1:-1]
        try :
            comp = int(comp)
        except :
            return False
               
        if CLASStype != None and CLASStype in SimResult.CSV2ECLtype[CLASStype] :
            keyType = SimResult.CSV2ECLtype[CLASStype] 
        else :
            return False
        if MEMBER is None :
            MEMBER = ''
        if MEMBER != None and MEMBER != 'FIELD':
            MEMBER = ':' + MEMBER.upper()
        elif CLASStype != None and MEMBER == 'FIELD' :
            keyType = 'F'
        
        ECLkey = keyType + xyz + rt + pi + '_' + str(comp)
        return ECLkey
        
    def fromECLtoVIP(self,key) :
        verbose( self.speak , 1 , 'translating ' + str(key) + ' from ECL to VIP style.')
        test = SimResult.testECLmolarKey(key)
        if type(test) == tuple :
            return test[0] , test[1] , test[2]
        
        key = key.strip().upper()
        if ':' in key :
            keyName = key[key.index(':')+1:]
            keyRoot = key[:key.index(':')]
            keyType = 'W'
            if keyRoot in SimResult.UniversalKeys :
                keyType = 'W'
            else :
                keyType = keyRoot[0]
                keyRoot = keyRoot[1:]
            if keyRoot in ( 'BHP' , 'THP' ) :
                keyType = 'W'
            if keyType == 'F' :
                keyName = 'ROOT'
            if keyType != '' and keyType in SimResult.ECL2VIPtype :
                keyType = SimResult.ECL2VIPtype[keyType]
            if keyRoot in SimResult.ECL2VIPkey :
                VIPkey = SimResult.ECL2VIPkey[keyRoot]
            else :
                VIPkey = keyRoot
        else :
            keyName = 'ROOT'
            keyRoot = key
            keyType = key[0]
            if keyRoot in SimResult.UniversalKeys :
                keyType = 'F'
            else :
                keyType = keyRoot[0]
                keyRoot = keyRoot[1:]
            if keyRoot in ( 'BHP' , 'THP' ) :
                keyType = 'W'
                keyName = ''
            if keyType == 'F' :
                keyName = 'ROOT'
            if keyType != '' and keyType in SimResult.ECL2VIPtype :
                keyType = SimResult.ECL2VIPtype[keyType]
            if keyRoot in SimResult.ECL2VIPkey :
                VIPkey = SimResult.ECL2VIPkey[keyRoot]
            else :
                VIPkey = keyRoot

        verbose( self.speak , 1 ,'ECLIPSE key ' + key + ' interpreted as VIP key ' + VIPkey + ' for ' + str(keyType) + ' summary for the item ' + keyName )
        return VIPkey , keyType , keyName

    def mainKey(self,Key) :
        if type(Key) is str:
            if len(Key.strip()) > 0 :
                return Key.strip().split(':')[0]
            else :
                return None
        if type(Key) is list or type(Key) is tuple :
            results = []
            for K in Key :
                results.append( self.mainKey(K) )
            return list(set(results))
    
    def fromVIPtoECL(self,key,SSStype=None):
        if SSStype != None :
            S = ' of ' + str(SSStype)
        else :
            S = ''
        verbose( self.speak , 1 , 'translating ' + str(key) + S + ' from VIP to ECL style.')
        key = key.strip().upper()
        if ':' in key :
            keyName = key[key.index(':')+1:]
            keyRoot = key[:key.index(':')]
            keyType = 'W'
            ConvertedRoot = keyRoot
            if keyRoot in SimResult.VIP2ECLkey :
                ConvertedRoot = SimResult.VIP2ECLkey[ keyRoot ]  
            if keyRoot in ( 'BHP' , 'THP' , 'AVG PRES' ) :
                keyType = 'W'
            if keyName == 'ROOT' :
                keyType = 'F'
                keyName = ''
            else :
                keyName = ':' + keyName
            if SSStype != None and SSStype in SimResult.VIP2ECLtype :
                keyType = SimResult.VIP2ECLtype[SSStype]
            if keyRoot in SimResult.UniversalKeys :
                keyType = ''
        else :
            keyName = ''
            keyRoot = key
            keyType = 'F'
            ConvertedRoot = keyRoot
            if keyRoot in SimResult.VIP2ECLkey :
                ConvertedRoot = SimResult.VIP2ECLkey[ keyRoot ] 
            if key in ( 'BHP' , 'THP' , 'AVG PRES' ) :
                keyType = 'W'
            if key in SimResult.VIP2ECLkey :
                keyRoot = SimResult.VIP2ECLkey[key]
            if SSStype != None and SSStype in SimResult.VIP2ECLtype :
                keyType = SimResult.VIP2ECLtype[SSStype]
            if keyRoot in SimResult.UniversalKeys :
                keyType = ''
   
        if keyRoot == '' :
            verbose( self.speak , 1 ,'CSV variable ' + key + ' not converted to ECL key.' )
            return None
        ECLkey = keyType + ConvertedRoot + keyName
        verbose( self.speak , 1 ,'VIP key ' + key + ' interpreted as ECL key ' + ECLkey )
        return ECLkey
    
    def fromCSVtoECL(self,variableORkey,CLASStype=None,MEMBER=None):
        test = SimResult.testCSVmolarKey(variableORkey,CLASStype,MEMBER)
        if type(test) == str :
            return test
        
        if CLASStype != None :
            C = ' of class ' + str(CLASStype)
        if MEMBER != None :
            M = ' for ' + str(MEMBER)
        verbose( self.speak , 1 , 'translating ' + str(variableORkey) + C + M + ' from CSV to ECL style.')
        
        keyType = None
        if CLASStype != None :
            if CLASStype in SimResult.CSV2ECLtype :
                keyType = SimResult.CSV2ECLtype[CLASStype] 

        if MEMBER != None and len(MEMBER.strip()) > 0 :
            keyName = MEMBER.strip().upper()
            if keyName in ( 'FIELD' , 'ROOT' ) :
                keyName = ''
            else :
                keyName = ':' + keyName
        else :
            keyName = None
            
        key = self.mainKey(variableORkey).upper()
        if key in SimResult.UniversalKeys :
            keyType = ''
        if key in SimResult.CSV2ECLkey :
            keyRoot = SimResult.CSV2ECLkey[key]
        else :
            keyRoot = None 
        
        verbose( self.speak , 1 , str(keyType) + ' ' + str(keyRoot) + ' ' + str(keyName) )
        if keyRoot != None and keyType != None and keyName != None :
            return keyType + keyRoot + keyName

    def fromECLtoCSV(self,key) :
        verbose( self.speak , 1 , 'translating ' + str(key) + ' from ECL to CSV style.')
        test = SimResult.testECLmolarKey(key)
        if type(test) == tuple :
            return test[0] , test[1] , test[2]
        
        key = key.strip().upper()
        if ':' in key :
            keyName = key[key.index(':')+1:]
            keyRoot = key[:key.index(':')]
            keyType = 'W'
            if keyRoot in SimResult.UniversalKeys :
                keyType = 'MISCELLANEOUS'
                keyName = ''
            else :
                keyType = keyRoot[0]
                keyRoot = keyRoot[1:]
            if keyRoot in ( 'BHP' , 'THP' ) :
                keyType = 'W'
            if keyType == 'F' :
                keyName = 'FIELD'
            if keyType != '' and keyType in SimResult.ECL2CSVtype :
                keyType = SimResult.ECL2CSVtype[keyType]
            if keyRoot in SimResult.ECL2CSVkey :
                CSVkey = SimResult.ECL2CSVkey[keyRoot]
            else :
                CSVkey = keyRoot
        else :
            keyName = 'FIELD'
            keyRoot = key
            keyType = key[0]
            if keyRoot in SimResult.UniversalKeys :
                keyType = 'MISCELLANEOUS'
                keyName = ''
            else :
                keyType = keyRoot[0]
                keyRoot = keyRoot[1:]
            if keyRoot in ( 'BHP' , 'THP' ) :
                keyType = 'W'
                keyName = ''
            if keyType == 'F' :
                keyName = 'FIELD'
            if keyType != '' and keyType in SimResult.ECL2CSVtype :
                keyType = SimResult.ECL2CSVtype[keyType]
            if keyRoot in SimResult.ECL2CSVkey :
                CSVkey = SimResult.ECL2CSVkey[keyRoot]
            else :
                CSVkey = keyRoot

        verbose( self.speak , 1 ,'ECLIPSE key ' + key + ' interpreted as CSV key ' + CSVkey + ' for ' + str(keyType) + ' summary for the item ' + keyName )
        return CSVkey , keyType , keyName


    
    def writeCSVtoPandas(self,CSVFilePath):
        if self.path is None :
            self.path = CSVFilePath
        with open(CSVFilePath,'r') as CSVfile:
            PandasCSV = open( extension(CSVFilePath)[2] + extension(CSVFilePath)[1] + '_forPandas' + extension(CSVFilePath)[0] , 'w' )
            CSVlines = CSVfile.readlines()
            DATA = False
            HEADERS = False
            for line in CSVlines :
                if not HEADERS :
                    if line.split(',')[0] == "['HEADERS']" :
                        print('found HEADERS')
                        HEADERS = True
                else :
                    lineData = line.split(',')
                    if line.split()[0] == "['DATA']" :
                        print('found DATA')
                        DATA = True
                        HEADERS = False
                        
                        for i in range( len( self.pandasColumns['HEADERS']['VARIABLE'] ) ):
                            fullName = []
                            for head in list(self.pandasColumns['HEADERS'].keys()) :
                                fullName.append( self.pandasColumns['HEADERS'][head][i] )
                            self.pandasColumns['COLUMNS'][':'.join(fullName)] = fullName
                        
                        PandasHead = ','.join(list( self.pandasColumns['COLUMNS'].keys() ))
                        PandasCSV.write( PandasHead + '\n' )

                    else :
                        self.pandasColumns['HEADERS'][ lineData[0].split(':')[0] ] = [ lineData[0].split(':')[1] ] + lineData[1:]
                        print( 'reading header ' + str( lineData[0].split(':')[0] ))

                if not DATA :
                    if line.split()[0] == "['DATA']" :
                        print('found DATA')
                        DATA = True
                else :
                    PandasCSV.write( line )
            PandasCSV.close()
                             
        
    def __init__(self,verbosity=2) :
        self.set_Verbosity(verbosity)
        self.SimResult = True
        self.kind = None
        self.results = None
        self.name = None
        self.path = None
        self.start = None
        self.end = None
        self.filter = {'key':None,'min':None,'max':None,'condition':None,'filter':None}
        self.wells = tuple()
        self.groups = tuple()
        self.regions = tuple()
        self.keys = tuple()
        self.attributes = {}
        self.vectors = {}
        self.units = {}
        self.overwrite = False
        self.null = None
        self.plotUnits = {}
        self.color = ( random.random() , random.random() , random.random() )
        self.keyColors = {}
        self.colorGrouping = 6
        self.DTindex = 'TIME'
        self.restarts = []
        self.vectorsRestart = {}
        self.pandasColumns = { 'HEADERS' : {} , 'COLUMNS' : {} , 'DATA' : {} }
        self.fieldtime = ( None , None , None ) 
    
    def __call__(self,Key=None,Index=None) :
        if Index is None :
            Index = self.DTindex
        if Key is not None :
            if type(Key) is list and len(Key) > 0:
                return self.get_DataFrame(Key,Index)
            elif type(Key) == str and len(Key) > 0 :
                return self.get_Vector(Key)[Key]
        else :
            print( SimResult.__doc__ )
    
    def __getitem__(self, item) :
        if type(item) is tuple :
            pass # what to do with the tupple?
        if type(item) is str :
            if self.is_Key(item) :
                return self.__call__([item])[item]
            else :
                meti = self.__getitem__([item])
                if meti is None :
                    return None
                elif len(meti.columns) == 1 :
                    verbose( self.speak , 2 , " a single item match the pattern,\n return the series for the item '" + meti.columns[0] + "':")
                    return meti[meti.columns[0]]
                else :
                    verbose( self.speak , 2 , " multiple items match the pattern,\n return a dataframe with all the matching items:")
                    return meti
        if type(item) is list :
            cols = []
            for each in item :
                each = each.strip(' :')
                if self.is_Key(each) :
                    cols.append(each)
                elif each in self.attributes :
                    cols += self.attributes[each]
                elif ':' in each :
                    attribute , pattern = each.split(':')
                    cols += self.keyGen(attribute,pattern)

            return self.__call__(cols)
    
    def __setitem__(self,Key,Value,Units=None) :
        if type(Value) is tuple :
            if len(Value) == 2 :
                if type(Value[0]) is np.ndarray :
                    if type(Value[1]) is str :
                        Value , Units = Value[0] , Value[1]
        if self.is_Key(Key) :
            verbose(self.speak,3,"WARNING, the key '" + Key + "' is already in use. It will be overwritten!")
            
        if type(Value) is str :
            if self.is_Key(Value) :
                Units = self.get_Units(Value)
                Value = self.get_Vector(Value)[Value]
        elif type(Value) is list or type(Value) is tuple :
            Value = np.array(Value)
        if type(Value) is np.ndarray :
            if len(Value) != len(self.fieldtime[2]) :
                raise TypeError(" the 'Value' array must have the exact same lenght of the simulation vectors: " + str(len(self.fieldtime[2])) )
            Units = Units.strip('( )')
            if unit.isUnit(Units) :
                pass
            else :
                verbose(self.speak , 2 , " the 'Units' string is not recognized." )
        self.set_Vector( Key , Value , Units , DataType='auto' , overwrite=True)
    
    def __len__(self) :
        """
        return the number of keys * number of time steps in the dataset
        """
        return self.len_Keys() * self.len_tSteps()
    
    def __str__(self) :
        return self.name
    
    def keyGen(self,keys=[],items=[]) :
        """
        returns the combination of every key in keys with all the items.
        keys and items must be list of strings
        """
        if type(items) == str :
            items = [items]
        if type(keys) == str :
            keys = [keys]
        ListOfKeys = []
        for k in keys :
            k.strip(' :')
            for i in items :
                i = i.strip(' :')
                if self.is_Key(k+':'+i) :
                    ListOfKeys.append( k+':'+i )
                elif k[0].upper() == 'W' :
                    wells = self.get_Wells(i)
                    if len(wells) > 0 :
                        for w in wells :
                            if self.is_Key(k+':'+w) :
                                ListOfKeys.append( k+':'+w )
                elif k[0].upper() == 'R' :
                    pass
                elif k[0].upper() == 'G' :
                    pass
        return ListOfKeys
        
    @property
    def describe(self) :
        # # calling the describe method from pandas for the entire dataframe is very intensive (huge dataframe)
        # describeKeys = list(set(self.keys))
        # describeKeys.sort()
        # return self[describeKeys].describe()
        if 'ECL' in str(self.kind) :
            kind = 'ECL'
        elif 'VIP' in str(self.kind) :
            kind = 'VIP'
        desc = {}
        Index = ['count','min','max']
        desc['time'] = [ self.len_tSteps() , self.fieldtime[0] , self.fieldtime[1] ]
        desc['dates'] = [ len(self('DATE')) , strDate(min(self('DATE')),speak=False)  , strDate(max(self('DATE')),speak=False) ]
        desc['kind'] = [ kind , '' , '' ]
        desc['keys'] = [ len(self.keys) , '' , '' ]
        desc['attributes'] = [ len(self.attributes) , '' , '' ]
        desc['wells'] = [ len(self.wells) , '' , '' ]
        desc['groups'] = [ len(self.groups) , '' , '' ]
        desc['regions'] = [ len(self.regions), '' , '' ]
        return pd.DataFrame( data=desc , index=Index)
    
    def set_index(self,Key) :
        self.set_Index(Key)
    def set_Index(self,Key) :
        if self.is_Key(Key) :
            self.DTindex = Key
    def get_Index(self) :
        return self.DTindex
    
    def set_plotUnits(self,UnitSystem_or_CustomUnitsDictionary='FIELD') :
        if type(UnitSystem_or_CustomUnitsDictionary) is str :
            if UnitSystem_or_CustomUnitsDictionary.upper() in ['F','FIELD'] :
                self.plotUnits = dict(dictionaries.unitsFIELD)
            elif UnitSystem_or_CustomUnitsDictionary.upper() in ['M','METRIC','METRICS'] :
                self.plotUnits = dict(dictionaries.unitsMETRIC)
            elif UnitSystem_or_CustomUnitsDictionary.upper() in ['ORIGINAL'] :
                self.plotUnits = {}
            else :
                print('unit system not recognized, please select FIELD, METRIC or ORIGINAL')

        elif type(UnitSystem_or_CustomUnitsDictionary) is dict :
            for Key in UnitSystem_or_CustomUnitsDictionary :
                if type(Key) is str and type(UnitSystem_or_CustomUnitsDictionary[Key]) is str : 
                    if self.is_Key(Key) :
                        if convertibleUnits( self.get_Unit(Key) , UnitSystem_or_CustomUnitsDictionary[Key] ) :
                            self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                        else :
                            verbose(self.speak , 3 , "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'." )
                    else :
                        verbose(self.speak , 2 , "the key '" + Key + "' can't be found in this simulation." )
                        matchedKeys = []
                        if Key in self.get_Attributes() :
                            # for Att in self.get_Attributes() :
                                # if Key in Att :
                            matchedKeys += self.attributes[Key]
                        if len(matchedKeys) == 0 :
                            verbose(self.speak , 3 , "the key '" + Key + "' does not match any attribute in this simulation." )
                        elif len(matchedKeys) == 1 :
                            if convertibleUnits( self.get_Unit(matchedKeys[0]) , UnitSystem_or_CustomUnitsDictionary[Key] ) :
                                self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                            else :
                                verbose(self.speak , 3 , "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'." )
                            verbose(self.speak , 1 , "the key '" + Key + "' matches one attribute in this simulation:\n"+str(matchedKeys) )
                        else :
                            mainKs = self.mainKey( matchedKeys )
                            if len(mainKs) == 1 :
                                if convertibleUnits( self.get_Unit(matchedKeys[0]) , UnitSystem_or_CustomUnitsDictionary[Key] ) :
                                    self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                                else :
                                    verbose(self.speak , 3 , "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'." )
                                verbose(self.speak , 1 , "the key '" + Key + "' matches " + str(len(matchedKeys)) + " attribute in this simulation:\n"+str(matchedKeys) )
                            else :
                                if convertibleUnits( self.get_Unit(matchedKeys[0]) , UnitSystem_or_CustomUnitsDictionary[Key] ) :
                                    self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                                else :
                                    verbose(self.speak , 3 , "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'." )
                                verbose(self.speak , 1 , "the key '" + Key + "' matches " + str(len(mainKs)) + " attribute in this simulation:\n"+str(matchedKeys) )
        else  :
            print(' Argument missing.\n Please select "FIELD", "METRIC" or "ORIGINAL" or provide a dictionary with the custom units set.')
        
    def get_plotUnits(self,Key=dict) :
        return self.get_plotUnit(Key)
    
    def get_plotUnit(self,Key=dict) :
        if Key is dict :
            return self.plotUnits
        if type(Key) is str :
            if Key in self.plotUnits :
                return self.plotUnits[Key]
            else :
                matchingKeys = []
                for K in self.plotUnits.keys():
                    if K in Key :
                        matchingKeys.append(K)
                if len(matchingKeys) == 0 :
                    return self.get_Unit(Key)
                elif len(matchingKeys) == 1 :
                    return self.plotUnits[matchingKeys[0]]
                else :
                    MK = ''
                    MM = []
                    for K in matchingKeys :
                        if len(K) > len(MK) :
                            MK = K
                            MM = [K]
                        elif len(K) == len(MK) :
                            MM.append(K)
                    if len(MM) == 1 :
                        return self.plotUnits[MK]
                    else :
                        for M in MM :
                            if convertibleUnits( self.get_Unit(Key) , self.plotUnits[M] ) :
                                return self.plotUnits[M]

    def get_Units(self,Key='--EveryType--') :
        return self.get_Unit(Key)

    def len_Wells(self) :
        """
        return the number of wells in the dataset
        """
        return len(self.get_Wells())
    
    def len_Groups(self) :
        """
        return the number of groups in the dataset
        """
        return len(self.get_Groups())
    
    def len_Keys(self) :
        """
        return the number of keys in the dataset
        """
        return len(self.get_Keys())
    
    def len_tSteps(self) :
        """
        return the number of timesteps in the dataset
        """
        keys = ( 'TIME' , 'DATE' , 'DATES' )
        for key in keys :
            if self.is_Key(key) :
                return len(self.get_Vector(key)[key])
    def len_TimeSteps(self) :
        """ 
        alias for len_tSteps 
        """
        return self.len_tSteps()
    
    def plot(self,Keys=[],Index='TIME',otherSims=None,Wells=[],Groups=[],Regions=[],DoNotRepeatColors=None) :

        if type(DoNotRepeatColors) is not bool :
            UserDRC = None
        else :
            UserDRC = DoNotRepeatColors
        DoNotRepeatColors = True
        if type(Keys) is str :
            Keys = [Keys]
        if type(Wells) is str :
            Wells = [Wells]
        if type(Groups) is str :
            Groups = [Groups]
        if type(Regions) is str :
            Regions = [Regions]
        if type(Index) is list or type(Index) is tuple :
            if len(Index) > 0 :                
                if type(Index[0]) is str :
                    if len(Index) == len(Keys) :
                        pass # it is OK, there are pairs of X & Y
                    else : 
                        verbose( 1 , self.speak , ' only a single index\n or pairs of X & Y can be used to plot,\n the 0th item will used as Index.')
                        Index = Index[0]
                #elif 'SimulationResults.' in str(type(Index)) :
                elif is_SimulationResult(Index[0]) :
                    if otherSims is None :
                        otherSims, Index = Index , 'TIME'
                    elif is_SimulationResult(otherSims) :
                        otherSims, Index = list(set([ Index , otherSims ])) , 'TIME'
                    elif type(otherSims) is str :
                        otherSims, Index = Index , otherSims.stip().upper()
                    elif type(otherSims) is list or type(otherSims) is tuple :
                        if is_SimulationResult(otherSims[0]) :
                            otherSims, Index = list(set([Index] + otherSims)) , 'TIME'
                        elif type(otherSims[0]) is str :
                            verbose( 1 , self.speak , 'only a single index can be used to plot, the item 0 will used.')
                            otherSims, Index = Index , otherSims[0]
                    
            else :
                Index='TIME'
        elif type(Index) is str :
            Index = Index.strip().upper()
        elif is_SimulationResult(Index) :
            if otherSims is None :
                otherSims, Index = Index , 'TIME'
            elif is_SimulationResult(otherSims) :
                otherSims, Index = list(set([ Index , otherSims ])) , 'TIME'
            elif type(otherSims) is str :
                otherSims, Index = Index , otherSims.stip().upper()
            elif type(otherSims) is list or type(otherSims) is tuple :
                if is_SimulationResult(otherSims[0]) :
                    otherSims, Index = list(set([Index] + otherSims)) , 'TIME'
                elif type(otherSims[0]) is str :
                    otherSims, Index = Index , otherSims
         
        for K in range(len(Keys)) :
            Keys[K] = Keys[K].strip()
        for W in range(len(Wells)) :
            Wells[W] = Wells[W].strip()
        for G in range(len(Groups)) :
            Groups[G] = Groups[G].strip()
        for R in range(len(Regions)) :
            Regions[R] = Regions[R].strip()

        PlotKeys = []
        for K in Keys :
            if self.is_Key(K) :
                PlotKeys.append(K)
            elif K in self.attributes :
                if K[0] == 'W' :
                    if len(Wells) == 0 :
                        items = self.attributes[K]
                        DoNotRepeatColors = False
                    else :
                        if len(Wells) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Wells)
                        for I in range(len(Wells)) :
                            items[I] = K+':'+Wells[I]
                elif K[0] == 'G' :
                    if len(Groups) == 0 :
                        items = self.attributes[K]
                        DoNotRepeatColors = False
                    else :
                        if len(Groups) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Groups)
                        for I in range(len(Groups)) :
                            items[I] = K+':'+Groups[I]
                elif K[0] == 'R' :
                    if len(Regions) == 0 :
                        items = self.attributes[K]
                        DoNotRepeatColors = False
                    else :
                        if len(Regions) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Regions)
                        for I in range(len(Regions)) :
                            items[I] = K+':'+Regions[I]
                PlotKeys += items

        if type(Index) is str :
            Index = [Index]
        IndexList = []
        for I in Index :
            if self.is_Key(I) :
                IndexList.append(I)
            elif I in self.attributes :
                if I[0] == 'W' :
                    if len(Wells) == 0 :
                        items = self.attributes[I]
                        DoNotRepeatColors = False
                    else :
                        if len(Wells) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Wells)
                        for X in range(len(Wells)) :
                            items[X] = I+':'+Wells[X]
                elif I[0] == 'G' :
                    if len(Groups) == 0 :
                        items = self.attributes[I]
                        DoNotRepeatColors = False
                    else :
                        if len(Groups) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Groups)
                        for X in range(len(Groups)) :
                            items[X] = I+':'+Groups[X]
                elif I[0] == 'R' :
                    if len(Regions) == 0 :
                        items = self.attributes[I]
                        DoNotRepeatColors = False
                    else :
                        if len(Regions) > self.colorGrouping :
                            DoNotRepeatColors = False
                        items = [None]*len(Regions)
                        for X in range(len(Regions)) :
                            items[X] = I+':'+Regions[X]
                IndexList += items
            

        if len(IndexList) == len(PlotKeys) :
            # check consistency:
            OKflag = True
            ReviewFlag = False
            for i in range(len(IndexList)) :
                if ':' in IndexList[i] and ':' in PlotKeys[i]:
                    if IndexList[i].split(':')[1] == PlotKeys[i].split(':')[1] :
                        pass # it is OK
                    else :
                        verbose( self.speak , 3 ," the pair '" + PlotKeys[i] + "' vs '" + IndexList[i] + "' might not be correct." )
                        OKflag = False
                        ReviewFlag = True
            
            if not OKflag and len(Keys) == len(Index) : # migt be a sorting issue
                for i in range(len(Keys)) :
                    if not self.is_Key(Keys[i]) and Keys[i] in self.attributes :
                        if not self.is_Key(Index[i]) and Index[i] in self.attributes :
                            IndexList.sort()
                            PlotKeys.sort()
                            OKflag = True
                if OKflag :
                    for i in range(len(IndexList)) :
                        if ':' in IndexList[i] and ':' in PlotKeys[i]:
                            if IndexList[i].split(':')[1] == PlotKeys[i].split(':')[1] :
                                pass # it is OK
                            else :
                                verbose( self.speak , 3 ," the pair '" + PlotKeys[i] + "' vs '" + IndexList[i] + "' might not be correct." )
                                OKflag = False
            if ReviewFlag :
                if OKflag :
                    verbose( self.speak , 3, ' the pairs consistency WAS corrected with sorting.')
                else :
                    verbose( self.speak , 3, ' the pairs consistency was NOT corrected with sorting.')
            
        if IndexList == [] :
            if len(Index) == 1 :
                IndexList = Index[0]
            else :
                IndexList = Index
        
        if otherSims is not None :
            if is_SimulationResult(otherSims) :
                SimsToPlot = [self , otherSims]
            elif type(otherSims) is list or type(otherSims) is tuple :
                SimsToPlot = [self]
                for each in otherSims :
                    if is_SimulationResult(each) :
                        SimsToPlot += [each]
        else :
            # return self.get_DataFrame(PlotKeys,Index).plot()
            SimsToPlot = [self]

        if type(UserDRC) is bool :
            DoNotRepeatColors = UserDRC

        Plot( SimResultObjects=SimsToPlot , Y_Keys=PlotKeys ,  X_Key=IndexList , DoNotRepeatColors=DoNotRepeatColors ) #, X_Units=[], Y_Units=[] , ObjectsColors=[] , SeriesColors=[] ,  graphName='' , Y_Axis=[], Y_Scales=[] , legendLocation='best', X_Scale=[] , Labels={})
        return( PlotKeys , IndexList )
    
    def replaceNullbyNaN(self) :
        """
        replace in-situ the null value defined in self.null by numpy.nan
        """
        if self.null is not None :
            for key in list(self.vectors.keys()):
                verbose( self.speak , 1 , ' attempting to replace null value ' + str(self.null) + ' in vector ' + str(key) + '.')
                if self.vectors[key] is not None and self.null in self.vectors[key] :
                    verbose( self.speak , 2 , "the key '" + key + "' has null values " + str(self.null) )
                    try :
                        self.vectors[key][self.vectors[key]==self.null]=np.nan
                    except :
                        verbose( self.speak , 2 , ' failed to replace null value ' + str(self.null) + ' in vector ' + str(key) + '.')
    
    def copyUnits(self,other) :
        """
        copy the units from other object to this object
        """
        for key in self.units :
            if other.get_Unit(key) != None:
                self.units[key] = other.get_Unit(key)
                
    def get_aggregatedWells(self,WellsToGroup=[],WellKeys=[],AggregatedKeyName='',aggregate_by='default',force=False) :
        """
        returns vectors of WellKeys for grouped wells, aggregating their data
        according to 'aggregate_by': 'sum' or 'avg'
            by defauylt:
            rates and cumulatives are lumped
            pressures are averaged
            time or date are not aggregated
        AggregatedKeyName is a string aimed to identify the group.
        by default, the well names will be concatenated.
        """
        WellsToGroup = list( set(WellsToGroup))
        WellsToGroup.sort()
        
        returnVector = {}
        
        if type(WellKeys) == str :
            WellKeys = [WellKeys]
        
        verbose( self.speak , 1 , ' aggregating keys ' + str(WellKeys) )
        verbose( self.speak , 1 , ' aggregating wells ' + str(WellsToGroup) )
        
        if AggregatedKeyName == '' :
            for key in WellKeys :
                for well in WellsToGroup :
                    AggregatedKeyName = AggregatedKeyName + well
        
        for key in WellKeys :
            verbose( self.speak  , 1 , " < aggregating key '" + key + "' >" )
            
            KeyUnits = None
            for well in WellsToGroup :
                KeyUnits = self.get_Unit(key + ':' + well)
                if type(KeyUnits) == str and len(KeyUnits) > 0 :
                    verbose( self.speak  , 1 , " < units found to be '" + KeyUnits + "' >" )
                    break
            if KeyUnits is None :
                KeyUnits = 'dimensionless'
                verbose( self.speak  , 1 , " < units NOT found, will be set as '" + KeyUnits + "' >" )
    
            if ( aggregate_by == 'default' and KeyUnits in unit.dictionary['pressure'] ) or aggregate_by.lower() == 'avg' :
                AGG = 'AVG'
            else :
                AGG = 'SUM'
            
            
            NewKey = 'G' + key[1:]
            if AGG + 'of' + key + ':' + ','.join(WellsToGroup) in self.vectors and force == False :
                returnVector[NewKey+':'+AggregatedKeyName] = self.vectors[ AGG + 'of' + key + ':' + ','.join(WellsToGroup) ]
            elif key == 'TIME' or key == 'DATE' or key == 'DATES' :
                returnVector[key+':'+AggregatedKeyName] = self.get_Vector(key)[key]
            else :
                for well in WellsToGroup : 
                    if self.is_Key(key + ':' + well) :
                        if self.get_Vector( key + ':' + well )[ key + ':' + well ] is None :
                            print( 'no data for the key ' + str(key + ':' + well ))
                        elif len( self.get_Vector( key + ':' + well )[ key + ':' + well ] ) > 0 :
                            size = len(self.get_Vector( key + ':' + well )[ key + ':' + well ])
                            verbose( self.speak , 1 , " < inizializing sum vectr with lenght " + str(size) + " >")
                            returnVector[NewKey+':'+AggregatedKeyName] = self.get_Vector( key + ':' + well )[ key + ':' + well ] * 0.0
                            break

                counter=0
                for well in WellsToGroup :
                    verbose( self.speak , 1 , " < looking for item '" + well + "' >")
                    if self.is_Key(key + ':' + well) :
                        AddingVector = self.get_Vector( key + ':' + well )[ key + ':' + well ]
                        if AddingVector is None :
                            verbose( self.speak , 3 , " < the item '" + well + "' doesn't containt this key >")
                        else :
                            verbose( self.speak , 2 , " < adding '" + well + "' >")
                            returnVector[NewKey+':'+AggregatedKeyName] = returnVector[NewKey+':'+AggregatedKeyName] + self.get_Vector( key + ':' + well )[ key + ':' + well ]
                            counter += 1
                        
                if ( aggregate_by == 'default' and KeyUnits in unit.dictionary['pressure'] ) or aggregate_by.lower() == 'avg' : 
                    if counter > 0 :
                        verbose( -1 , 1 , " < calculating average for key '" + key + "' of well '" + WellsToGroup + "' >")
                        returnVector[NewKey+':'+AggregatedKeyName] = returnVector[NewKey+':'+AggregatedKeyName] / counter
                        AGG = 'AVG'
                if counter > 0 :
                    verbose( self.speak , 3 , ' saving vector ' + NewKey + ':' + AggregatedKeyName + ' of lenght ' + str(len(returnVector[NewKey+':'+AggregatedKeyName])))
                    self.set_Vector( AGG + 'of' + key + ':' + ','.join(WellsToGroup) , returnVector[NewKey+':'+AggregatedKeyName] , KeyUnits ,overwrite=True ) 
                    self.set_Vector( NewKey + ':' + AggregatedKeyName , returnVector[NewKey+':'+AggregatedKeyName] , KeyUnits ,overwrite=True ) 
        
        return returnVector
    
    def fillZeros(self,KeyVector,KeyTime,force=False):
        """
        Check if the KeyTime array exists on the entire range of TIME array 
        from Field and complete the corresponding KeyVector with zeros or 
        interpolation for the missing time steps.
        Returns KeyVector that exists on full range of array TIME
        """
        KeyTime = np.array(KeyTime,dtype='float')
            
        if self.fieldtime == ( None , None , None ) :
            self.set_FieldTime()
        
        if len(KeyTime) == 0 or len(KeyVector) == 0 :
            verbose(self.speak, 2 , ' <fillZeros> the received vectors are empty, thus, a zero filled vector will be returned with lenght equal to the field TIME vector.')
            return np.array([0.0]*len(self.fieldtime),dtype='float')
        
        if force == True or min(KeyTime) > self.fieldtime[0] or max(KeyTime) < self.fieldtime[1] :
            verbose(self.speak, 1 , ' <fillZeros> the received vectors starts on TIME=' + str( KeyTime[0] ) + ', it will be filled to start from TIME' + str(self.fieldtime[0]) +  '.')
            OtherDT = pd.DataFrame( data= { 'vector' : np.array(KeyVector,dtype='float') } , index= np.array(KeyTime,dtype='float') )
            FieldDT = pd.DataFrame( data= { 'vector' : np.array( [0.0]*len(self.fieldtime[2]) ) } , index= np.array(self.fieldtime[2],dtype='float') )
            CompleteDT = OtherDT + FieldDT 
            CompleteDT.interpolate(axis=0,inplace=True)
            CompleteDT.fillna(value=0.0,inplace=True)
            return CompleteDT['vector'].values
        else :
            return KeyVector
    
    def report_VIP_AttributesNotTo_ECL(self) :
        if len(SimResult.VIPnotECL) == 0 :
            print('nothing to report.')
        else :
            SimResult.VIPnotECL = list( set( SimResult.VIPnotECL ) )
            print("the following attibutes from VIP simulation couldn't be converted to ECL style attributes:")
            for each in SimResult.VIPnotECL :
                print('  ' + str(each))
    
    def set_Name(self,name):
        if type(name) == list or type(name) == tuple :
            if len(name) == 1 :
                name = name[0]
        if type(name) == str :
            self.name = name
        else :
            verbose( self.speak , 2 , ' Name should be a string'  )
            self.name = str(name)
    def get_Name(self):
        if type( self.name ) != str :
            verbose( self.speak , 3 , ' the name of ' + str(self.name) + ' is not a string.' )
            return str( self.name )
        return self.name
    
    def set_Restart(self,SimResultObject):
        if type( SimResultObject ) == list :
            self.restarts = self.restarts + SimResultObject 
        else :
            self.restarts.append(SimResultObject)
        self.restarts = list( set ( self.restarts ) )
        
        sortedR = []
        selfTi = self.checkIfLoaded('TIME',False)[0]
        # remove simulations that starts after the self
        for i in range(len(self.restarts)) :
            if self.restarts[i].get_Vector('TIME')['TIME'][0] < selfTi :
                sortedR += [self.restarts[i]]
        self.restarts = sortedR
        
        # sort simulations by start time
        for i in range(len(self.restarts)) :
            for j in range(0,len(self.restarts)-i-1) :
                if self.restarts[j].get_Vector('TIME')['TIME'][0] > self.restarts[j+1].get_Vector('TIME')['TIME'][0] :
                    self.restarts[j] , self.restarts[j+1] = self.restarts[j+1] , self.restarts[j]
                    
        self.set_FieldTime()
    
    def remove_Restart(self,SimResultObject) :
        if SimResultObject in self.restarts :
            print(" removed restart object '" + str(self.restarts.pop(SimResultObject)) + "'")
    
    def get_Restart(self):
        if self.speak in ( -1, 1 ) and len( self.restarts ) > 0 :
            string = "\n '" + self.get_Name() + "' restarts from " 
            for r in range(0,len(self.restarts)) :
                string = string + "\n   '" + self.restarts[::-1][r].get_Name() + "'"
            print( string )
        return self.restarts
    
    def set_Color(self,MatplotlibColor=None,Key=None):
        if MatplotlibColor is None :
            MatplotlibColor = ( random.random() , random.random() , random.random() )
        elif not is_color_like(MatplotlibColor) :
            verbose(self.speak,3,'the provided color code is not a correct matplotlib color' )
        if type(MatplotlibColor) is list :
           MatplotlibColor = tuple( MatplotlibColor )
        if Key is None :
            self.color = MatplotlibColor
        else :
            if self.is_Key(Key) :
                self.keyColors[Key] = MatplotlibColor
            elif Key in self.attributes :
                self.keyColors[Key] = MatplotlibColor
                    
    def get_Color(self,Key=None):
        if Key is None :
            return self.color
        elif self.is_Key(Key) :
            if Key in self.keyColors :
                return self.keyColors[Key]
            elif self.mainKey(Key) in self.keyColors :
                return self.keyColors[self.mainKey(Key)]
            else :
                return None
        elif Key in self.attributes :
            return self.keyColors[Key]
    
    def set_Verbosity(self,verbosity_level):
        try :
            self.speak = int(verbosity_level)
        except :
            if type(verbosity_level) == str and verbosity_level.upper() == 'ALL' :
                print('Verbosity set to ALL (-1), EVERY message wil be printed.')
                self.speak = -1
            elif type(verbosity_level) == str and verbosity_level.upper() == 'MUTE' :
                print('Verbosity set to MUTE (0), no message wil be printed.')
                self.speak = -1
            else :
                print('wrong set_Verbosity argument: ' + str(verbosity_level) + '\nVerbosity will be set to True (1)')
                self.speak = 1
    def get_Verbosity(self) :
        return self.speak
    
        
    def set_Start(self,startDate):
        """
        startDate must be a string representing a date or a Pandas or Numpy or datetime object
        """
        self.start = np.datetime64( pd.to_datetime( startDate ) ,'s' )
        return self.start
    
    def get_Start(self):
        """
        startDate must be a string representing a date or a Pandas or Numpy or datetime object
        """
        return self.start
    
    def is_Key(self,Key) :
        if type(Key) != str or len(Key)==0 :
            return False
        if Key in self.get_Keys() :
            return True
        else :
            return False

    def is_Att(self,Key) :
        return self.is_Attribute(Key) 
    
    def is_Attribute(self,Key) :
        if type(Key) != str :
            return False
        Key = Key.strip()
        if len(Key)==0 :
            return False
        if Key[-1] == ':' :
            Key = Key[:-1]
        if Key in self.get_Attributes() :
            return True
        else :
            return False
        
    def get_Attributes(self,pattern=None,reload=False) :
        """
        extract the attribute name from the keys property,
        basically, the part to the left of the ':' in the key name for wells,
        groups and regions.
        """
        if len(list(self.attributes.keys())) == 0 or reload == True :
            props = []
            for each in self.get_Keys() :
                if ':' in each :
                    attr = self.mainKey(each)
                    if attr in self.attributes :
                        if type(self.attributes[ attr ]) == list :
                            self.attributes[ attr ] = self.attributes[ attr ] + [ each ]
                        else :
                            self.attributes[ attr ] = [ each ]
                    else :
                        self.attributes[ attr ] = [each]
                else :
                    self.attributes[ each.strip() ] = []

            for each in list( self.attributes.keys() ) :
                if self.attributes[ each ] != None :
                    self.attributes[ each ] = list(set( self.attributes[ each ] ))
                else :
                    self.attributes[ each ] = []
        if pattern is None :
            return tuple(self.attributes.keys())
        else :
            props = []
            for each in self.get_Keys(pattern,reload=False) :
                if ':' in each :
                    props.append( self.mainKey(each) )
                else :
                    props.append( each.strip() )
            return tuple(set(props))
    
    def get_AttributesDict(self,reload=False) :
        if reload == True :
            self.get_Attributes(None,True)
        return self.attributes

    def add_Key(self,Key) :
        if type(Key) == str :
            Key = Key.strip()
            self.keys = tuple( set( list(self.get_Keys()) + [Key] ) )
        else :
            raise TypeError('Key must be string')
    
    def get_Regions(self,pattern=None,reload=False):
        """
        Will return a list of all the region names in case.

        If the pattern variable is different from None only regions
        matching the pattern will be returned; the matching is based
        on fnmatch():
            Pattern     Meaning
            *           matches everything
            ?           matches any single character
            [seq]       matches any character in seq
            [!seq]      matches any character not in seq
        """
        if pattern is not None and type( pattern ) is not str :
            raise TypeError('pattern argument must be a string.')    
    
        if len(self.regions) == 0 or reload == True :
            self.regions = tuple( self.extract_Regions() )
        if pattern is None :
            return self.regions
        else:
            return tuple( fnmatch.filter( self.regions , pattern ) )# return self.extract_Regions(pattern)       
    
    def get_Wells(self,pattern=None,reload=False) :
        """       
        Will return a list of all the well names in case.

        If the pattern variable is different from None only wells
        matching the pattern will be returned; the matching is based
        on fnmatch():
            Pattern     Meaning
            *           matches everything
            ?           matches any single character
            [seq]       matches any character in seq
            [!seq]      matches any character not in seq
            
        """
        if pattern is not None and type( pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        
        if len(self.wells) == 0 or reload == True :
            self.wells = self.extract_Wells() 

        if pattern is None :
            return self.wells
        else:
            return tuple( fnmatch.filter( self.wells , pattern ) )
    
    def get_Groups(self,pattern=None,reload=False) :
        """       
        Will return a list of all the group names in case.

        If the pattern variable is different from None only groups
        matching the pattern will be returned; the matching is based
        on fnmatch():
            Pattern     Meaning
            *           matches everything
            ?           matches any single character
            [seq]       matches any character in seq
            [!seq]      matches any character not in seq
            
        """
        if pattern is not None and type( pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        
        if len(self.groups) == 0 or reload == True :
            self.groups = self.extract_Groups() 

        if pattern is None :
            return self.groups
        else:
            return tuple( fnmatch.filter( self.groups , pattern ) )
    
    def get_Keys(self,pattern=None,reload=False) :
        """       
        Will return a list of all the key names in case.

        If the pattern variable is different from None only keys
        matching the pattern will be returned; the matching is based
        on fnmatch():
            Pattern     Meaning
            *           matches everything
            ?           matches any single character
            [seq]       matches any character in seq
            [!seq]      matches any character not in seq
            
        """
        if pattern is not None and type( pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        
        if len(self.keys) == 0 or reload == True :
            self.keys = self.list_Keys() 

        if pattern is None :
            return self.keys
        else:
            return tuple( fnmatch.filter( self.keys , pattern ) )
    
    def get_Filter(self) :
        return self.filter['filter']
    
    def set_Filter(self,Key=None,Condition=None,Min=None,Max=None,Filter=None,IncrementalFilter=True) :
        if IncrementalFilter :
            if self.filter['filter'] is None :
                Incremental = False
            else :
                Incremental = IncrementalFilter
                
        if Filter is not None :
            if type(Filter) is list or type(Filter) is tuple :
                Filter = np.array(Filter)
            if type(Filter) is np.ndarray : 
                if len(Filter) == len(self.fieldtime[2]) :
                    if Filter.dtype == 'bool' :
                        if Incremental :
                            self.filter['filter'] = Filter * self.filter['filter']
                        else :
                            self.filter['filter'] = Filter
                        return True
                    else :
                        try:
                            Filter = Filter.astype('bool')
                        except:
                            verbose(self.speak , 3 , " the 'Filter' must be an array of dtype 'bool'")
                            return False
                        return self.set_Filter(Filter=Filter,IncrementalFilter=IncrementalFilter)
                else :
                    verbose(self.speak , 3 , " the 'Filter' must have the exact same lenght of the simulation vectors: " + str(len(self.fieldtime[2])) )
                    return False
                
        elif Filter is None :
            if Key is None and Condition is None and Min is None and Max is None :
                self.filter = {'key':None,'min':None,'max':None,'condition':None,'filter':None}
                verbose(self.speak , 3 , " << filter reset >>")
                return True
            elif Key is None :
                if self.filter['key'] is not None :
                    if ( type(Min) is str and isDate(Min) ) or ( type(Max) is str and isDate(Max) ) :
                        if type( self.get_Vector(self.filter['key'])[self.filter['key']][0] ) is np.datetime64 :
                            Key = self.filter['key']
                        else :
                            Key = 'DATE'                    
                    else :  
                        Key = self.filter['key']
                elif type(Min) is str and isDate(Min) :
                    Key = 'DATE'
                elif type(Max) is str and isDate(Max) :
                    Key = 'DATE'
                elif Condition is not None :
                    pass
                else :
                    verbose(self.speak , 2 , ' no Filter or Key received.')
                    return False
            elif not self.is_Key(Key) :
                if Condition is None :
                    return self.set_Filter(Condition=Key)
                else :
                    raise KeyError(" the argument Key: '" + str(Key) + "' is not a key in this simulation")

            if Incremental :
                FilterArray = self.filter['filter']
            previous = self.filter.copy()
            self.filter = {'key':None,'min':None,'max':None,'condition':None,'filter':None}
            if not Incremental :
                FilterArray = np.array([True]*len(self.fieldtime[2]))

                
            if Min is not None :
                if type(Min) is int or type(Min) is float :
                    KeyArray = self.get_Vector(Key)[Key]
                    FilterArray = FilterArray * ( KeyArray >= Min )
                    self.filter['min'] = Min
                    self.filter['key'] = Key
                    self.filter['filter'] = FilterArray
                    return True
                elif type(Min) is str :
                    try :
                        Min = np.datetime64( pd.to_datetime( strDate( Min ) ) )
                    except :
                        verbose(self.speak , 3 , " if the 'Min' is string it must represent a date, better if is formatted like DD-MMM-YYYY")
                if type(Min) is np.datetime64 :
                    KeyArray = self.get_Vector(Key)[Key]
                    FilterArray = FilterArray * ( KeyArray >= Min )
                    self.filter['min'] = Min
                    self.filter['key'] = Key
                    self.filter['filter'] = FilterArray
                    return True
                else :
                    verbose(self.speak , 3 , " the 'Min' value for the filter must be integer or float")
                    return False
                    
            if Max is not None :
                if type(Max) is int or type(Max) is float :
                    KeyArray = self.get_Vector(Key)[Key]
                    FilterArray = FilterArray * ( KeyArray <= Max )
                    self.filter['max'] = Max
                    self.filter['key'] = Key
                    self.filter['filter'] = FilterArray
                    return True
                elif type(Max) is str :
                    try :
                        Max = np.datetime64( pd.to_datetime( strDate( Max ) ) )
                    except :
                        verbose(self.speak , 3 , " if the 'Min' is string it must represent a date, better if is formatted like DD-MMM-YYYY")
                        return False
                if type(Max) is np.datetime64 :
                    KeyArray = self.get_Vector(Key)[Key]
                    FilterArray = FilterArray * ( KeyArray <= Max )
                    self.filter['max'] = Max
                    self.filter['key'] = Key
                    self.filter['filter'] = FilterArray
                    return True
                else :
                    verbose(self.speak , 3 , " the 'Max' value for the filter must be integer or float")
                    return False
                    
            if Condition is not None :
                if type(Condition) is list or type(Condition) is tuple :
                    applying = []
                    if not IncrementalFilter :
                        self.filter['filter'] = None
                    for each in Condition:
                        applying.append( self.set_Filter(Key=Key,Condition=each,IncrementalFilter=True) )
                    applying = np.array(applying)
                    return applying.all == True
                elif type(Condition) is str :
                    if '>=' in Condition :
                        Left,Right = Condition.split('>=')
                        Left = Left.strip()
                        Right = Right.strip()
                        if len(Left)>0 and len(Right)>0 :
                            if self.is_Key(Left) and self.is_Key(Right) :
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] >= self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = None
                                return True
                            elif self.is_Key(Left) :
                                try :
                                    Right = float(Right)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] >= Right )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = None
                                return True
                            elif self.is_Key(Right) :
                                try :
                                    Left = float(Left)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( Left >= self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = None
                                return True
                        elif len(Left)>0 :
                            return self.set_Filter(Condition=Condition+Key)
                        elif len(Right)>0 :
                            return self.set_Filter(Condition=Key+Condition)

                    if '<=' in Condition :
                        Left,Right = Condition.split('<=')
                        Left = Left.strip()
                        Right = Right.strip()
                        if len(Left)>0 and len(Right)>0 :
                            if self.is_Key(Left) and self.is_Key(Right) :
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] <= self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = None
                                self.filter['min'] = None
                                self.filter['max'] = None
                                return True
                            elif self.is_Key(Left) :
                                try :
                                    Right = float(Right)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] <= Right )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = Left
                                self.filter['max'] = Right
                                return True
                            elif self.is_Key(Right) :
                                try :
                                    Left = float(Left)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( Left <= self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = Right
                                self.filter['min'] = Left
                                return True
                        elif len(Left)>0 :
                            return self.set_Filter(Condition=Condition+Key)
                        elif len(Right)>0 :
                            return self.set_Filter(Condition=Key+Condition)

                    if '==' in Condition :
                        Left,Right = Condition.split('==')
                        Left = Left.strip()
                        Right = Right.strip()
                        if len(Left)>0 and len(Right)>0 :
                            if self.is_Key(Left) and self.is_Key(Right) :
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] == self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = None
                                self.filter['min'] = None
                                self.filter['max'] = None
                                return True
                            elif self.is_Key(Left) :
                                try :
                                    Right = float(Right)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] == Right )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = Left
                                self.filter['min'] = Right
                                self.filter['max'] = Right
                                return True
                            elif self.is_Key(Right) :
                                try :
                                    Left = float(Left)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( Left == self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = Right
                                self.filter['min'] = Left
                                self.filter['max'] = Left
                                return True
                        elif len(Left)>0 :
                            return self.set_Filter(Condition=Condition+Key)
                        elif len(Right)>0 :
                            return self.set_Filter(Condition=Key+Condition)
                        
                    if '!=' in Condition :
                        Left,Right = Condition.split('!=')
                        Left = Left.strip()
                        Right = Right.strip()
                        if len(Left)>0 and len(Right)>0 :
                            if self.is_Key(Left) and self.is_Key(Right) :
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] != self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = None
                                self.filter['min'] = None
                                self.filter['max'] = None
                                return True
                            elif self.is_Key(Left) :
                                try :
                                    Right = float(Right)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] != Right )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = Left
                                self.filter['min'] = None
                                self.filter['max'] = None
                                return True
                            elif self.is_Key(Right) :
                                try :
                                    Left = float(Left)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( Left != self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = Right
                                self.filter['min'] = None
                                self.filter['max'] = None
                                return True
                        elif len(Left)>0 :
                            return self.set_Filter(Condition=Condition+Key)
                        elif len(Right)>0 :
                            return self.set_Filter(Condition=Key+Condition)
                        
                    if '<>' in Condition :
                        verbose( self.speak , -1 , " I've saved your life this time, but keep in mind that the inequality check in python is '!=' and not '<>'")
                        Condition = Condition.replace('<>','!=')
                        return self.set_Filter(Key=Key,Condition=Condition,IncrementalFilter=IncrementalFilter)
                        
                    if '>' in Condition :
                        Left,Right = Condition.split('>')
                        Left = Left.strip()
                        Right = Right.strip()
                        if len(Left)>0 and len(Right)>0 :
                            if self.is_Key(Left) and self.is_Key(Right) :
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] > self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = None
                                self.filter['min'] = None
                                self.filter['max'] = None
                                return True
                            elif self.is_Key(Left) :
                                try :
                                    Right = float(Right)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] > Right )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = Left
                                self.filter['min'] = Right
                                return True
                            elif self.is_Key(Right) :
                                try :
                                    Left = float(Left)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( Left > self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = Right
                                self.filter['max'] = Left
                                return True
                        elif len(Left)>0 :
                            return self.set_Filter(Condition=Condition+Key)
                        elif len(Right)>0 :
                            return self.set_Filter(Condition=Key+Condition)
                        
                    if '<' in Condition :
                        Left,Right = Condition.split('<')
                        Left = Left.strip()
                        Right = Right.strip()
                        if len(Left)>0 and len(Right)>0 :
                            if self.is_Key(Left) and self.is_Key(Right) :
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] < self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = None
                                self.filter['min'] = None
                                self.filter['max'] = None
                                return True
                            elif self.is_Key(Left) :
                                try :
                                    Right = float(Right)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( self.get_Vector(Left)[Left] < Right )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = Left
                                self.filter['max'] = Right
                                return True
                            elif self.is_Key(Right) :
                                try :
                                    Left = float(Left)
                                except :
                                    verbose( self.speak , 3 , " the 'Condition' must have\n   two Keys\n   or\n   one Key and one float or integer")
                                    return False
                                FilterArray = FilterArray * ( Left < self.get_Vector(Right)[Right] )
                                self.filter['filter'] = FilterArray
                                self.filter['condition'] = Condition
                                self.filter['key'] = Right
                                self.filter['min'] = Left
                                return True
                        elif len(Left)>0 :
                            return self.set_Filter(Condition=Condition+Key)
                        elif len(Right)>0 :
                            return self.set_Filter(Condition=Key+Condition)
                        
                    if '=' in Condition :
                        verbose( self.speak , -1 , " I've saved your life this time, but keep in mind that the equality check in python is '==' and not '='")
                        Condition = Condition.replace('=','==')
                        return self.set_Filter(Key=Key,Condition=Condition,IncrementalFilter=IncrementalFilter)
                    
    def get_Vectors(self,key=None,reload=False):
        return self.get_Vector(key,reload)

    def get_Vector(self,key=None,reload=False):
        """
        returns a dictionary with numpy vectors for the selected key(s)
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        if len( self.get_Restart() ) > 0 :
            return self.checkRestarts(key,reload)
        
        returnVectors = {}
        if self.results != None :
            if type(key) == str :
                returnVectors[key] = self.checkIfLoaded(key,reload)
            if type(key) == list or type(key) == tuple :
                listOfKeys = list(set(key))
                for each in listOfKeys :
                    returnVectors[each] = self.checkIfLoaded(each,reload)
        
        if self.filter['filter'] is None :
            return returnVectors
        else :
            if self.filter['key'] is not None :
                verbose( self.speak , 1 , " filter by key '" + self.filter['key'] + "'")          
            for each in returnVectors :
                returnVectors[each] = returnVectors[each][self.filter['filter']]
            return returnVectors
    
    # support functions for get_Vector:
    def checkRestarts(self,key=None,reload=False) :
        returnVectors = {}
        Rlist = self.restarts + [ self ]
        if type(key) == str :
            key = [ key ]
            
        for K in key :
            try :
                Rlist[-1].checkIfLoaded(K,False)
                Kexists = True
            except :
                Kexists = False

            if Kexists :
                ti = Rlist[0].checkIfLoaded('TIME',False)[0]
                tf = Rlist[1].checkIfLoaded('TIME',False)[0]

                try :
                    RVector = Rlist[0].checkIfLoaded(K,False)
                except :
                    RVector = np.array( [0]*len(Rlist[0].checkIfLoaded('TIME',False)) , dtype=Rlist[-1].checkIfLoaded(K,False).dtype )

                if RVector is None or len(RVector) == 0 :
                    RVector = np.array( [0]*len(Rlist[0].checkIfLoaded('TIME',False)) , dtype=Rlist[-1].checkIfLoaded(K,False).dtype )

                if tf in Rlist[0].checkIfLoaded('TIME',False) :
                    returnVectors[K] = RVector[ ( Rlist[0].checkIfLoaded('TIME',False)>=ti ) & ( Rlist[0].checkIfLoaded('TIME',False)<tf ) ]
                else :
                    returnVectors[K] = RVector[ Rlist[0].checkIfLoaded('TIME',False) >= ti ]
                verbose( self.speak , 1 , " reading key '" + str(K) + "' from restart " + "0" + ": '" + str(Rlist[0]) + "'")
                
                for R in range(1,len(Rlist)-1) :
                    ti = Rlist[R].checkIfLoaded('TIME',False)[0]
                    tf = Rlist[R+1].checkIfLoaded('TIME',False)[0]
                    try :
                        RVector = Rlist[R].checkIfLoaded(K,False)
                    except :
                        RVector = np.array( [0]*len(Rlist[R].checkIfLoaded('TIME',False)) , dtype=Rlist[-1].checkIfLoaded(K,False).dtype )

                    if RVector is None or len(RVector) == 0 :
                        RVector = np.array( [0]*len(Rlist[R].checkIfLoaded('TIME',False)) , dtype=Rlist[-1].checkIfLoaded(K,False).dtype )

                    if tf in Rlist[R].checkIfLoaded('TIME',False) :
                        returnVectors[K] = np.concatenate( [ returnVectors[K] , RVector[ ( Rlist[R].checkIfLoaded('TIME',False)>=ti ) & ( Rlist[R].checkIfLoaded('TIME',False)<tf ) ] ] )
                    else :
                        returnVectors[K] = np.concatenate( [ returnVectors[K] , RVector[ ( Rlist[R].checkIfLoaded('TIME',False)>=ti ) ] ] )
                    verbose( self.speak , 1 , " reading key '" + str(K) + "' from restart " + str(R) + ": '" + str(Rlist[0]) + "'")
                    
                returnVectors[K] = np.concatenate( [ returnVectors[K] , Rlist[-1].checkIfLoaded(K,False) ] )
                verbose( self.speak , 1 , " reading key '" + str(K) + "' from restart " + str(len(Rlist)) + ": '" + str(Rlist[0]) + "'")
            
        return returnVectors
    
    def checkIfLoaded(self,key,reload) :
        """
        internal function to avoid reloading the same vector twice...
        """
        verbose( self.speak , 1 , ' looking for key ' + str( key ) )
        if str(key).upper().strip() not in self.vectors or reload == True :
            self.vectors[key.upper().strip()] = self.loadVector(key)
        return self.vectors[key.upper().strip()]

    def get_VectorWithoutRestart(self,key=None,reload=False):
        """
        returns a dictionary with numpy vectors for the selected key(s)
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        returnVectors = {}
        if self.results != None :
            if type(key) == str :
                returnVectors[key] = self.checkIfLoaded(key,reload)
            if type(key) == list or type(key) == tuple :
                listOfKeys = list(set(key))
                for each in listOfKeys :
                    returnVectors[each] = self.checkIfLoaded(each,reload)
        return returnVectors
    
    def set_Vector( self , Key , VectorData , Units , DataType='auto' , overwrite=None) :
        """
        Writes a new vector into the dataset 
        or overwrite an existing one if overwrite = True
        The data is stored as numpy.array
        
        > Key must be a string, intended to be the name of the Vector
        > VectorData must be a list, tuple or numpy.array
        > Units must be a string representing the Unit of the data
          optional DataType can define the tipe of data to cast the VectorData.
          The accepted types are the regular numpy types (int , float , datetime).
          If set to 'auto' it will try to guess the datatype or leave as string.
        > optional overwrite protects the data to be overwritten by mistake, 
          the default value for overwrite can be changed with set_Overwrite method
        """
        if type(DataType) is str :
            DataType = DataType.lower().strip()
        
        if overwrite is None :
            overwrite = self.overwrite
        elif ( type(overwrite) is int or type(overwrite) is float ) :
            if overwrite == 1 :
                overwrite = True
            else :
                overwrite = False
        elif type(overwrite) is bool :
            pass
        else :
            overwrite = False
        
        if type(Key) is str :
            Key = Key.strip()
        else :
            raise TypeError('Key must be a string')
        
        if Key in self.vectors and overwrite == False :
            raise OverwrittingError('the Key ' + Key + ' already exists in the dataset and overwrite parameter is set to False. Set overwrite=True to avoid this message and change the DataVector.')
            
        if type(VectorData) is list or type(VectorData) is tuple :
            if len(VectorData) == 0 :
                raise TypeError('VectorData must not be empty')
            VectorData = np.array(VectorData)
        elif type(VectorData) is np.ndarray :
            if DataType == 'auto' :
                if 'int' in str(VectorData.dtype) :
                    DataType = 'int'
                    verbose( self.speak , 1 , Key + ' vector detected as numpy.array of dtype ' + DataType + '.' )
                elif 'float' in str(VectorData.dtype) :
                    DataType = 'float'
                    verbose( self.speak , 1 , Key + ' vector detected as numpy.array of dtype ' + DataType + '.' )
                elif 'datetime' in str(VectorData.dtype) :
                    DataType = 'datetime'
                    verbose( self.speak , 1 , Key + ' vector detected as numpy.array of dtype ' + DataType + '.' )
            if VectorData.size == 0 :
                raise TypeError('VectorData must not be empty')
        else :
            raise TypeError('VectorData must be a list, tuple or numpy.ndarray. Received ' + str(type(VectorData)))
        
        if type(Units) is str :
            Units = Units.strip('( )')
            if unit.isUnit(Units) :
                pass
            elif Units == 'DEGREES' and 'API' in self.mainKey(Key).upper() :
                Units = 'API'
                verbose( self.speak , 2 , '\nIMPORTANT: the selected Units: ' + Units + ' were chaged to "API" for the vector with key name ' + Key + '.')
            elif ( ' / ' in Units and unit.isUnit(Units.replace(' / ','/')) ) or ( '/ ' in Units and unit.isUnit(Units.replace('/ ','/')) ) or ( ' /' in Units and unit.isUnit(Units.replace(' /','/')) ) :
                verbose( self.speak , 2 , "\nMESSAGE: the selected Units: '" + Units +"' were chaged to " + Units.replace(' /','/').replace('/ ','/')  + ' for the vector with key name ' + Key + '.')
                Units = Units.replace('/ ','/').replace(' /','/')
            else :
                verbose( self.speak , 3 , "\nIMPORTANT: the selected Units: '" + Units +"' are not recognized by the programm and will not be able to convert this Vector " + str(Key) +' into other units.' )
        else :
            raise TypeError('Units must be a string')
        
        if DataType == 'auto' :
            verbose( self.speak , 1 , ' guessing the data type of the VectorData ' + Key )
            done = False
            if Key.upper() == 'DATE' or Key.upper() == 'DATES' or '/' in str(VectorData) :
                try :
                    VectorData = np.datetime64( pd.to_datetime( VectorData ) , 's' )
                    verbose( self.speak , 1 , Key + ' vector casted as datetime.' )
                    done = True
                except :
                    pass            
            elif Key.upper() == 'TIME' or Key.upper() == 'YEARS' or Key.upper() == 'YEAR' or Key.upper() == 'DAYS' or Key.upper() == 'DAYS' or Key.upper() == 'MONTH' or Key.upper() == 'MONTHS':
                try :
                    VectorData = VectorData.astype('float')
                    verbose( self.speak , 1 , Key + ' vector casted as floating point.' )
                    done = True
                except :
                    pass  
                
            if done is False :
                Integer = False
                try :
                    VectorDataInt = VectorData.astype(int)
                    Integer = True
                except :
                    try :
                        VectorData = VectorData.astype(float)
                        verbose( self.speak , 1 , Key + ' vector casted as floating point.' )
                    except :
                        try :
                            VectorData = np.datetime64( pd.to_datetime(VectorData), 's' )
                            verbose( self.speak , 1 , Key + ' vector casted as datetime.' )
                        except :
                            if type(VectorData) is np.ndarray :
                                VectorType = str( VectorData.dtype )
                            elif type(VectorData) is list or type(VectorData) is tuple :
                                VectorType = str( type(VectorData) ) + ' with ' + type(VectorData[0]) + ' inside'
                            else :
                                VectorType = str( type(VectorData) )
                            verbose( self.speak , 2 , ' not able to cast the VectorData ' + Key + ', kept as received: ' + VectorType + '.' )
                if Integer :
                    try :
                        VectorDataFloat = VectorData.astype(float)
                        if np.all( VectorDataFloat == VectorDataInt ) :
                            VectorData = VectorDataInt
                            verbose( self.speak , 1 , Key + ' vector casted as integer.' )
                        else :
                            VectorData = VectorDataFloat
                            verbose( self.speak , 1 , Key + ' vector casted as floating point.' )
                    except :
                        pass
                    
        elif 'datetime' in DataType :
            try :
                VectorData = np.array( pd.to_datetime( VectorData ) ,'datetime64[s]') 
            except :
                try :
                    VectorData = VectorData.astype(DataType)
                except :
                    verbose( self.speak , 2 , ' not able to cast the VectorData ' + Key + ', kept as received: ' + DataType + '.' )
        else :
            try :
                VectorData = VectorData.astype(DataType)
            except :
                verbose( self.speak , 2 , ' not able to cast the VectorData ' + Key + ', kept as received: ' + DataType + '.' )
        
        self.vectors[Key] = VectorData
        self.units[Key] = Units
        if self.is_Key(Key) == False :
            self.add_Key(Key) 
        self.get_Attributes(reload=True)
    
    def set_Overwrite(self,overwrite) :
        if type(overwrite) == bool :
            self.overwrite = overwrite
    def get_Overwrite(self) :
        return self.overwrite
    
    def stripUnits(self):
        for key in self.units :
            if self.units[key] is None :
                pass
            else :
                self.units[key] = self.units[key].strip('( )').strip("'").strip('"')
                if 'DíA' in self.units[key] :
                    self.units[key] = self.units[key].replace('DíA','DAY')
    
    def fill_FieldBasics(self) :
        
        np.seterr(divide='ignore', invalid='ignore')
        
        if type(self.get_Vector('FOPR')['FOPR']) == np.ndarray and type(self.get_Vector('FWPR')['FWPR']) == np.ndarray :
            # calculated FLPR if not available:
            if self.is_Key('FLPR') == False or len( self.get_Vector('FLPR')['FLPR'] ) < len( self.get_Vector('FWPR')['FWPR'] ) or type(self.get_Vector('FLPR')['FLPR']) != np.ndarray :
                try :
                    self.set_Vector( 'FLPR' , np.array( self.get_Vector('FOPR')['FOPR'],dtype='float' ) + convertUnit( np.array( self.get_Vector('FWPR')['FWPR'],dtype='float' ) , self.get_Unit('FWPR') , self.get_Unit('FOPR') , PrintConversionPath=(self.speak==1) ) , self.get_Unit('FOPR') , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FLPR.')
            
            # calculated FWCT if not available:
            if self.is_Key('FWCT') == False or len( self.get_Vector('FWCT')['FWCT'] ) < len( self.get_Vector('FWPR')['FWPR'] ) or type(self.get_Vector('FWCT')['FWCT']) != np.ndarray :
                try :
                    Vector = np.array( np.divide(  np.array(self.get_Vector('FWPR')['FWPR'],dtype='float') , convertUnit( np.array( self.get_Vector('FLPR')['FLPR'],dtype='float' ) , self.get_Unit('FLPR') , self.get_Unit('FWPR') , PrintConversionPath=(self.speak==1) ) ) ,dtype='float') 
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FWCT' , Vector , 'FRACTION' , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FWCT.')
                    
            # calculated FWOR & FOWR if not available:
            if self.is_Key('FWOR') == False or len( self.get_Vector('FWOR')['FWOR'] ) < len( self.get_Vector('FWPR')['FWPR'] ) or type(self.get_Vector('FWOR')['FWOR']) != np.ndarray :
                try :
                    Vector = np.array( np.divide( np.array( self.get_Vector('FWPR')['FWPR'] , dtype='float' ) , np.array( self.get_Vector('FOPR')['FOPR'] , dtype='float' ) ),dtype='float')
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FWOR' , Vector , self.get_Unit('FWPR').split('/')[0]+'/'+self.get_Unit('FOPR').split('/')[0] , overwrite=True )

                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FWOR.')
                try :
                    Vector = np.array( np.divide( np.array( self.get_Vector('FOPR')['FOPR'] , dtype='float' ) , np.array( self.get_Vector('FWPR')['FWPR'] , dtype='float' ) ) ,dtype='float')
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FOWR' , Vector , self.get_Unit('FOPR').split('/')[0]+'/'+self.get_Unit('FWPR').split('/')[0] , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FOWR.')
                    
        # calculated FGOR if not available:
        if type(self.get_Vector('FOPR')['FOPR']) == np.ndarray and type(self.get_Vector('FGPR')['FGPR']) == np.ndarray :
            if self.is_Key('FGOR') == False or len( self.get_Vector('FGOR')['FGOR'] ) < len( self.get_Vector('FOPR')['FOPR'] ) or type(self.get_Vector('FGOR')['FGOR']) != np.ndarray :
                try :
                    Vector = np.array( np.divide( np.array( self.get_Vector('FGPR')['FGPR'] , dtype='float' ) , np.array( self.get_Vector('FOPR')['FOPR'] , dtype='float' ) ) ,dtype='float')
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FGOR' ,  Vector  , self.get_Unit('FGPR').split('/')[0]+'/'+self.get_Unit('FOPR').split('/')[0] , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FGOR.')
        
        # calculated FOGR if not available:
        if type(self.get_Vector('FOPR')['FOPR']) == np.ndarray and type(self.get_Vector('FGPR')['FGPR']) == np.ndarray :
            if self.is_Key('FOGR') == False or len( self.get_Vector('FOGR')['FOGR'] ) < len( self.get_Vector('FOPR')['FOPR'] ) or type(self.get_Vector('FOGR')['FOGR']) != np.ndarray :
                try :
                    Vector = np.array( np.divide( np.array( self.get_Vector('FOPR')['FOPR'] , dtype='float' ) , np.array( self.get_Vector('FGPR')['FGPR'] , dtype='float' ) ) ,dtype='float')
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FOGR' , Vector , self.get_Unit('FOPR').split('/')[0]+'/'+self.get_Unit('FGPR').split('/')[0] , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FOGR.')
    
        if type(self.get_Vector('FOPT')['FOPT']) == np.ndarray and type(self.get_Vector('FWPT')['FWPT']) == np.ndarray :
            # calculated FLPR if not available:
            if self.is_Key('FLPT') == False or len( self.get_Vector('FLPT')['FLPT'] ) < len( self.get_Vector('FWPT')['FWPT'] ) or type(self.get_Vector('FLPT')['FLPT']) != np.ndarray :
                try :
                    self.set_Vector( 'FLPT' , np.array( self.get_Vector('FOPT')['FOPT'],dtype='float' ) + convertUnit( np.array( self.get_Vector('FWPT')['FWPT'],dtype='float' ), self.get_Unit('FWPT') , self.get_Unit('FOPT') , PrintConversionPath=(self.speak==1)) , self.get_Unit('FOPT') , overwrite=True )
                except :
                    try :
                        Name , Vector , Units = self.integrate( 'FLPR' , 'FLPT' )
                        self.set_Vector(Name,Vector,Units,'float',True)
                        verbose( self.speak , 2 , 'vector FLPT integrated from FLPR.')
                    except :
                        verbose( self.speak , 2 , 'failed to create missing vector FLPT.')
    
        np.seterr(divide=None, invalid=None)
    
    def fill_WellBasics(self) :
        
        np.seterr(divide='ignore', invalid='ignore')
        
        for well in list(self.get_Wells()) :
            if type(well) == str and len(well.strip()) > 0 :
                well = well.strip()
                verbose( self.speak , 2 , ' calculating basic ratios for the well ' + well )
                if type(self.get_Vector('WOPR:'+well)['WOPR:'+well]) == np.ndarray and type(self.get_Vector('WWPR:'+well)['WWPR:'+well]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key('WLPR:'+well) == False or len( self.get_Vector('WLPR:'+well)['WLPR:'+well] ) < len( self.get_Vector('WWPR:'+well)['WWPR:'+well] ) or type(self.get_Vector('WLPR:'+well)['WLPR:'+well]) != np.ndarray :
                        try :
                            self.set_Vector( 'WLPR:'+well , np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) + convertUnit( np.array( self.get_Vector('WWPR:'+well)['WWPR:'+well] , dtype='float' ) , self.get_Unit('WWPR:'+well) , self.get_Unit('WOPR:'+well) , PrintConversionPath=(self.speak==1)) , self.get_Unit('WOPR:'+well) , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WLPR:'+well)
                    
                    # calculated WWCT if not available:
                    if self.is_Key('WWCT:'+well) == False or len( self.get_Vector('WWCT:'+well)['WWCT:'+well] ) < len( self.get_Vector('WWPR:'+well)['WWPR:'+well] ) or type(self.get_Vector('WWCT:'+well)['WWCT:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WWPR:'+well)['WWPR:'+well] , dtype='float' ) , convertUnit( np.array(self.get_Vector('WLPR:'+well)['WLPR:'+well], dtype='float' ), self.get_Unit('WLPR:'+well) , self.get_Unit('WWPR:'+well) , PrintConversionPath=(self.speak==1)) ) , dtype='float' ) 
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WWCT' , Vector , 'FRACTION' , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WWCT:'+well)
                            
                    # calculated WWOR & WOWR if not available:
                    if self.is_Key('WWOR:'+well) == False or len( self.get_Vector('WWOR:'+well)['WWOR:'+well] ) < len( self.get_Vector('WWPR:'+well)['WWPR:'+well] ) or type(self.get_Vector('WWOR:'+well)['WWOR:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WWPR:'+well)['WWPR:'+well] , dtype='float' ) , np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WWOR:'+well , Vector , self.get_Unit('WWPR:'+well).split('/')[0]+'/'+self.get_Unit('WOPR:'+well).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WWOR:'+well)
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) , np.array( self.get_Vector('WWPR:'+well)['WWPR:'+well] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WOWR:'+well , Vector , self.get_Unit('WOPR:'+well).split('/')[0]+'/'+self.get_Unit('WWPR:'+well).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WOWR:'+well)
                            
                # calculated WGOR if not available:
                if type(self.get_Vector('WOPR:'+well)['WOPR:'+well]) == np.ndarray and type(self.get_Vector('WGPR:'+well)['WGPR:'+well]) == np.ndarray :
                    if self.is_Key('WGOR:'+well) == False or len( self.get_Vector('WGOR:'+well)['WGOR:'+well] ) < len( self.get_Vector('WOPR:'+well)['WOPR:'+well] ) or type(self.get_Vector('WGOR:'+well)['WGOR:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WGPR:'+well)['WGPR:'+well] , dtype='float' ) , np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WGOR:'+well , Vector  , self.get_Unit('WGPR:'+well).split('/')[0]+'/'+self.get_Unit('WOPR:'+well).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WGOR:'+well)
                
                # calculated WOGR if not available:
                    if self.is_Key('WOGR:'+well) == False or len( self.get_Vector('WOGR:'+well)['WOGR:'+well] ) < len( self.get_Vector('WOPR:'+well)['WOPR:'+well] ) or type(self.get_Vector('WOGR:'+well)['WOGR:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) , np.array( self.get_Vector('WGPR:'+well)['WGPR:'+well] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WOGR:'+well , Vector , self.get_Unit('WOPR:'+well).split('/')[0]+'/'+self.get_Unit('WGPR:'+well).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WOGR:'+well)
            
                if type(self.get_Vector('WOPT:'+well)['WOPT:'+well]) == np.ndarray and type(self.get_Vector('WWPT:'+well)['WWPT:'+well]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key('WLPT:'+well) == False or len( self.get_Vector('WLPT:'+well)['WLPT:'+well] ) < len( self.get_Vector('WWPT:'+well)['WWPT:'+well] ) or type(self.get_Vector('WLPT:'+well)['WLPT:'+well]) != np.ndarray :
                        try :
                            self.set_Vector( 'WLPT:'+well , np.array( self.get_Vector('WOPT:'+well)['WOPT:'+well] , dtype='float' ) + convertUnit( np.array(self.get_Vector('WWPT:'+well)['WWPT:'+well], dtype='float'), self.get_Unit('WWPT:'+well) , self.get_Unit('WOPT:'+well) , PrintConversionPath=(self.speak==1) ) , self.get_Unit('WOPT:'+well) , overwrite=True )
                        except :
                            try :
                                Name , Vector , Units = self.integrate( 'WLPR:'+well , 'WLPT:'+well )
                                self.set_Vector(Name,Vector,Units,'float',True)
                                verbose( self.speak , 2 , 'vector WLPT:' + well + ' integrated from WLPR:' + well + '.')
                            except :
                                verbose( self.speak , 2 , 'failed to create missing vector WLPT:'+well)
    
        np.seterr(divide=None, invalid=None)
        
    def fill_Basics(self,ItemsNames=[],KeyType='') :
        """
        if the required inputs exists, calculates:
            - liquid rate
            - liquid cumulative
            - water-cut
            - water-oil ratio
            - oil-water ratio
            - gas-oil ratio
            - oil-gas ratio
        
        KeyType in a character that indicates the type of keyword (1st character)
        to save the results:
            - G for groups : GOPR:name, GWCT:name, GGOR:name
            - W for wells : WOPR:name, WWCT:name, WGOR:name
            - R for regions : ROPR:name, RWCT:name, RGOR:name
            etc
        
        default of KeyType is :
            W if the ItemName exists in get_Wells()
            G if the ItemName exists in get_Groups()
            R if the ItemName exists in get_Regions()
        """
        np.seterr(divide='ignore', invalid='ignore')
        
        if type(ItemsNames) == str :
            ItemsNames = [ ItemsNames ]
        
        
        for item in ItemsNames :
            
            KT = 'U'
            if item in list(self.get_Regions()) :
                KT = 'R'
            if item in list(self.get_Groups()) :
                KT = 'G'
            if item in list(self.get_Wells()) :
                KT = 'W'
            if item not in ( 'FIELD' , 'ROOT' ) :
                item = ':'+item
                KT = 'F'
            if KeyType != '' :
                KT = KeyType
                
            if type(item) == str and len(item.strip()) > 0 :
                item = item.strip()
                verbose( self.speak , 2 , ' calculating basic ratios for the item ' + item )
                if type(self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item]) == np.ndarray and type(self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key(KT+'LPR'+item) == False or len( self.get_Vector(KT+'LPR'+item)[KT+'LPR'+item] ) < len( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] ) or type(self.get_Vector(KT+'LPR'+item)[KT+'LPR'+item]) != np.ndarray :
                        try :
                            self.set_Vector( KT+'LPR'+item , np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) + np.array( convertUnit(self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] , dtype='float' , PrintConversionPath=(self.speak==1)) , self.get_Unit(KT+'WPR'+item) , self.get_Unit(KT+'OPR'+item) ) , self.get_Unit(KT+'OPR'+item) , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'LPR'+item)
                    
                    # calculated WWCT if not available:
                    if self.is_Key(KT+'WCT'+item) == False or len( self.get_Vector(KT+'WCT'+item)[KT+'WCT'+item] ) < len( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] ) or type(self.get_Vector(KT+'WCT'+item)[KT+'WCT'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] , dtype='float' ) , np.array( convertUnit(self.get_Vector(KT+'LPR'+item)[KT+'LPR'+item], self.get_Unit(KT+'LPR'+item) , self.get_Unit(KT+'WPR'+item) , PrintConversionPath=(self.speak==1)) , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'WCT' , Vector , 'FRACTION' , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'WCT'+item)
                            
                    # calculated WWOR & WOWR if not available:
                    if self.is_Key(KT+'WOR'+item) == False or len( self.get_Vector(KT+'WOR'+item)[KT+'WOR'+item] ) < len( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] ) or type(self.get_Vector(KT+'WOR'+item)[KT+'WOR'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] , dtype='float' ) , np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'WOR'+item , Vector , self.get_Unit(KT+'WPR'+item).split('/')[0]+'/'+self.get_Unit(KT+'OPR'+item).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'WOR'+item)
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) , np.array( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'OWR'+item , Vector , self.get_Unit(KT+'OPR'+item).split('/')[0]+'/'+self.get_Unit(KT+'WPR'+item).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'OWR'+item)
                            
                # calculated WGOR if not available:
                if type(self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item]) == np.ndarray and type(self.get_Vector(KT+'GPR'+item)[KT+'GPR'+item]) == np.ndarray :
                    if self.is_Key(KT+'GOR'+item) == False or len( self.get_Vector(KT+'GOR'+item)[KT+'GOR'+item] ) < len( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] ) or type(self.get_Vector(KT+'GOR'+item)[KT+'GOR'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'GPR'+item)[KT+'GPR'+item] , dtype='float' ) , np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'GOR'+item , Vector  , self.get_Unit(KT+'GPR'+item).split('/')[0]+'/'+self.get_Unit(KT+'OPR'+item).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'GOR'+item)
                
                # calculated WOGR if not available:
                    if self.is_Key(KT+'OGR'+item) == False or len( self.get_Vector(KT+'OGR'+item)[KT+'OGR'+item] ) < len( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] ) or type(self.get_Vector(KT+'OGR'+item)[KT+'OGR'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) , np.array( self.get_Vector(KT+'GPR'+item)[KT+'GPR'+item] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'OGR'+item , Vector , self.get_Unit(KT+'OPR'+item).split('/')[0]+'/'+self.get_Unit(KT+'GPR'+item).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'OGR'+item)
            
                if type(self.get_Vector(KT+'OPT'+item)[KT+'OPT'+item]) == np.ndarray and type(self.get_Vector(KT+'WPT'+item)[KT+'WPT'+item]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key(KT+'LPT'+item) == False or len( self.get_Vector(KT+'LPT'+item)[KT+'LPT'+item] ) < len( self.get_Vector(KT+'WPT'+item)[KT+'WPT'+item] ) or type(self.get_Vector(KT+'LPT'+item)[KT+'LPT'+item]) != np.ndarray :
                        try :
                            self.set_Vector( KT+'LPT'+item , self.get_Vector(KT+'OPT'+item)[KT+'OPT'+item] + convertUnit(self.get_Vector(KT+'WPT'+item)[KT+'WPT'+item], self.get_Unit(KT+'WPT'+item) , self.get_Unit(KT+'OPT'+item) , PrintConversionPath=(self.speak==1)) , self.get_Unit(KT+'OPT'+item) , overwrite=True )
                        except :
                            try :
                                Name , Vector , Units = self.integrate( KT+'LPR'+item , KT+'LPT'+item )
                                self.set_Vector(Name,Vector,Units,'float',True)
                                verbose( self.speak , 2 , 'vector ' + KT +'LPT' + item + ' integrated from ' + KT + 'LPR' + item + '.')
                            except :
                                verbose( self.speak , 2 , 'failed to create missing vector '+KT+'LPT'+item)
    
        np.seterr(divide=None, invalid=None)
    
    def arithmeticVector(self,Key) :
        """
        returns a calculated vector if the required inputs exist.
        works with ECL keys only
        """
        Key = Key.strip()
        ClassKey = Key.split(':')[0][0]
        CalcKey = Key.split(':')[0][1:]
        ItemKey = ''
        if ':' in Key :
            ItemKey = ':' + Key.split(':')[1]
        if CalcKey in dictionaries.calculations :
            OK = True
            for Req in dictionaries.calculations[CalcKey][::2] :
                if type(Req) == str :
                    if type(self.get_Vector(ClassKey+Req+ItemKey)[ClassKey+Req+ItemKey]) == np.ndarray :
                        # is a vector with values...
                        pass
                    else :
                        OK = False
                        break
                else :
                    #  should be int or float
                    pass
            if OK :

                for i in range( len( dictionaries.calculations[CalcKey] )) :
                    if i == 0 :
                        # initialize CalculationTuple
                        if type( dictionaries.calculations[CalcKey][i] ) == str :
                            CalculationTuple = [ ClassKey + dictionaries.calculations[CalcKey][i] + ItemKey ]
                        else :
                            CalculationTuple = [ dictionaries.calculations[CalcKey][i] ]
                    else :
                        if type( dictionaries.calculations[CalcKey][i] ) == str :
                            CalculationTuple.append( [ ClassKey + dictionaries.calculations[CalcKey][i] + ItemKey ] )
                        else :
                            CalculationTuple.append( [ dictionaries.calculations[CalcKey][i] ] )
                
                return self.calculator( CalculationTuple , Key )

    def calculator(self,CalculationTuple,ResultName=None,ResultUnits=None) :
        """
        receives a tuple indicating the operation to perform and returns a vector
        with ResultName name 
        
        The CalculationTuple is a sequence of Vectors or Floats and operators:
        The syntax of the CalculationTuple is:
            ( 'Vector or float' , 'operator' , 'Vector or float' , 'operator' , 'Vector or float' , 'operator' ... 'Vector or float'  )
        
        The accepted operators are: '+' , '-' , '*' , '/' , '^'
        The CalculationTuple must start with a number or variable, never with an operator

        The operations will be executed in the exact order they are described. i.e.:
            'FLPR' : ( 'FOPR' , '+' , 'FWPR' ) 
                means FLPR = FOPR + FWPR 
                will add FOPR plus FWPR
            'WWCT:P1' : ( 'WOPR:P1' , '/' , 'WLPR:P2' ) 
                means WWCT:P1 = WOPR:P1 + WLPR:P2 
                will add FOPR plus FWPR
        but:
            'R' : ( 'A' , '-', 'B' , '*' , 'C' ) 
                means R = ( A - B ) / C
                will add A plus B and the result will be divided by C

            to represent R = A - B / C the correct sintax is:
            'R' : ( -1 , '*' , 'B' , '/', 'C' , '+' , 'A'  ) 
                that means R = -1 * B / C + A
        """
        if type( CalculationTuple ) == str :
            verbose ( self.speak , 3 , ' the received string for CalculatedTuple was converted to tuple,\n  received: ' + CalculationTuple + '\n  converted to: ' + str( CalculationTuple.split() ) )
            CalculationTuple = tuple ( CalculationTuple.split() )
        elif type( CalculationTuple ) == list :
            CalculationTuple = tuple( CalculationTuple )
        if ResultName is None :
            ResultName = str( CalculationTuple )
            
        OK = True
        Missing = []
        for Req in CalculationTuple[::2] :
            if type(Req) == str :
                if type(self.get_Vector(Req)[Req]) == np.ndarray :
                    # is a vector with values... OK
                    pass
                else :
                    OK = False
                    Missing.append(Req)
            else :
                #  should be int or float
                pass
        if not OK :
            verbose( self.speak , 3 , '\n IMPORTANT: the following required input vectors were not found:\n   -> ' + '\n   -> '.join(Missing) + '\n')
            return { ResultName : None }
        else :
            for i in range(0, len( CalculationTuple ) , 2) :
                if i == 0 :
                    # initialize Result vector
                    if type( CalculationTuple[i] ) == str :
                        Result = np.array( self.get_Vector( CalculationTuple[i] )[ CalculationTuple[i] ] , dtype='float' )
                        Units = [ self.get_Unit( CalculationTuple[i] ) ]
                    else :
                        Result = CalculationTuple[i]
                        Units = [None]
                else :
                    # following the operations sequence
                    # extracting Next vector or float
                    if type( CalculationTuple[i] ) == str :
                        Next = np.array( self.get_Vector(CalculationTuple)[CalculationTuple] , dtype='float' )
                        Units.append( self.get_Unit( CalculationTuple[i] ) )
                        CalcUnit = self.get_Unit( CalculationTuple[i] )
                    else :
                        Next = CalculationTuple[i]
                        Units.append(None)
                        NextUnit = self.get_Unit( CalculationTuple[i] )
                    # appliying calculation
                    if CalculationTuple[i-1] == '+' :
                        if CalcUnit == NextUnit :
                            Result = Result + Next
                        elif convertibleUnits( NextUnit , CalcUnit) :
                            Result = Result + convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                        else :
                            CalcUnit = CalcUnit + '+' + NextUnit
                            Result = Result + Next

                    elif CalculationTuple[i-1] == '-' :
                        if CalcUnit == NextUnit :
                            Result = Result - Next
                        elif convertibleUnits( NextUnit , CalcUnit) :
                            Result = Result - convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                        else :
                            CalcUnit = CalcUnit + '-' + NextUnit
                            Result = Result - Next
                            
                    elif CalculationTuple[i-1] == '*' :
                        if CalcUnit == NextUnit :
                            Result = Result * Next
                        elif convertibleUnits( NextUnit , CalcUnit) :
                            Result = Result * convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                        else :
                            CalcUnit = CalcUnit + '*' + NextUnit
                            Result = Result * Next
                        
                    elif CalculationTuple[i-1] == '/' :
                        if CalcUnit == NextUnit :
                            Result = np.divide ( Result , Next )
                        elif convertibleUnits( NextUnit , CalcUnit) :
                            Result = np.divide ( Result , convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1)) )
                            
                        else :
                            CalcUnit = CalcUnit + '/' + NextUnit
                            Result = np.divide( Result , Next )
                        Result = np.nan_to_num( Result, nan=0.0 , posinf=0.0 , neginf=0.0 )
                        
                    elif CalculationTuple[i-1] == '^' :
                        if CalcUnit == NextUnit :
                            Result = Result ** Next
                        elif convertibleUnits( NextUnit , CalcUnit) :
                            Result = Result ** convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                        else :
                            CalcUnit = CalcUnit + '^' + NextUnit
                            Result = Result ** Next
            
            SameUnits = []
            for each in Units :
                if each != None :
                    SameUnits.append(each)
            if len( set( SameUnits ) ) == 0 :
                Units = 'DIMENSIONLESS'
            elif len( set( SameUnits ) ) == 1 :
                Units = SameUnits[0]
            else :
                Units = Units[0]
                for i in range(1,len( Units )) :
                    Units.append( CalculationTuple[2*i-1] )
                    Units.append( Units[i] )
                Units = str(Units)
                
            if ResultUnits is None :
                ResultUnits = Units
            elif ResultUnits == Units :
                # OK
                pass
            elif ResultUnits == CalcUnit :
                # OK
                Units = CalcUnit
            elif convertibleUnits( CalcUnit , ResultUnits ) :
                # OK
                Result = convertUnit( Result , CalcUnit , ResultUnits , PrintConversionPath=(self.speak==1) )
            else :
                print( 'MESSAGE: The provided units are not equal to the calculated units:\n    ' + str(ResultUnits) + ' != ' + Units  )
            
            self.set_Vector( str( CalculationTuple ) , Result , ResultUnits , 'float' , False )
            if ResultName != str( CalculationTuple ) :
                self.vectors[ResultName] = self.vectors[ str( CalculationTuple ) ]
                self.units[ResultName] = self.units[ str( CalculationTuple ) ]
                
            return { ResultName : Result }
            
    def createDATES(self) :
        TIME = self.get_Vector('TIME')['TIME']
        start = self.start
        DATE = np.empty(len(TIME), dtype='datetime64[s]')
        for i in range(len(TIME)) :
            DATE[i] = start + np.timedelta64( timedelta(days=TIME[i]) )
        self.set_Vector( 'DATES' , DATE , 'DATE' , overwrite=True )
        self.set_Vector( 'DATE' , DATE , 'DATE' , overwrite=True )
    
    def get_UnitsConverted(self,Key=None,OtherObject_or_NewUnits=None):
        """
        returns a vector converted from the unit system of this object 
        to the units of the corresponding vector on the other SimResult object 
        or to the indicated units as string or Unit object. 
        
        If Key is defaulted an empty dictionary will be returned
        If Other_Object_or_Units is set to None or defautl no conversion 
        will be applied. It is equivalent to get_Vector() method.
        
        """
        # checking input parameters
        if type(Key) == str :
            Key = [Key]
        elif type(Key) == list or type(Key) == tuple :
            pass
        if Key is None :
            return {}
        if OtherObject_or_NewUnits is None :
            return self.get_Vector(Key, False)
        
        
        ListOfUnits = False
        if type(OtherObject_or_NewUnits) == str :
            OtherObject_or_NewUnits = [OtherObject_or_NewUnits]
            ListOfUnits = True
        elif type(OtherObject_or_NewUnits) == list or type(OtherObject_or_NewUnits) == tuple :
            ListOfUnits = True
            
        if ListOfUnits == True and len(Key) != len(OtherObject_or_NewUnits) :
            raise TypeError( str(len(Key)) + ' resquested but ' + str(len(OtherObject_or_NewUnits)) + ' units provided.\n          Both should match order and number.' )
        elif ListOfUnits == True and len(Key) == len(OtherObject_or_NewUnits) :
            pass
        else :
            try :
                if OtherObject_or_NewUnits.SimResult == True :
                    errors = False
                    TempConversions = []
                    for each in Key :
                        if OtherObject_or_NewUnits.is_Key(each) == False :
                            errors = True
                            verbose( self.speak , 3 , 'The requested Key ' + str(each) + ' is not present in the simulation ' + str(OtherObject_or_NewUnits.get_Name()) + '.')
                        else :
                            TempConversions.append( OtherObject_or_NewUnits.get_Unit( each.strip() ) )
                    if errors == True :
                        raise TypeError('at least one requested Key is not present in the simulation ' + str(OtherObject_or_NewUnits.get_Name()) + '.')
                    # OtherObject = OtherObject_or_NewUnits
                    OtherObject_or_NewUnits = TempConversions
                    TempConversions = None
                else :
                    raise TypeError('Other_Object_or_Units must be string, a list of strings or a SimResult object.')
            except :
                raise TypeError('Other_Object_or_Units must be string, a list of strings or a SimResult object.')
        
        # extracting and converting the selected Keys
        ConvertedDict = {}
        for each in range(len(Key)) :
            ConvertedDict[Key[each]] = convertUnit(self.get_Vector(Key[each])[Key[each].strip()], self.get_Unit(Key[each]), OtherObject_or_NewUnits[each] , PrintConversionPath=(self.speak==1))
        return ConvertedDict
    
    def integrate(self,InputKey,OutputKey=None,ConstantRate=False,Numpy=True):
        """"
        calculate the integral, or cumulative, of the input vector and saves 
        it to the output vector.
       
        if ConstantRate = True :
            cumulative[i] = cumulative[i-1] + Time[i] * InputKey[i] 
        if ConstantRate = False :
            cumulative[i] = cumulative[i-1] + Time[i] * ( min( InputKey[i] , InputKey[i+1] ) + Time[i] * ( max( InputKey[i] , InputKey[i+1] ) - min( InputKey[i] , InputKey[i+1] ) ) 
            
        Set Numpy=False to not use Numpy, the calculation will be done witha for loop
        """
        if type(InputKey) != str or ( type(OutputKey) != None and type(OutputKey) != str ) :
            raise TypeError(' InputKey and OutputKey must be strings.')
        Vector = self.get_Vector( InputKey )[ InputKey ]
        VectorUnits = self.get_Unit(InputKey)
        verbose( self.speak , 1 , "<integrate> retrieved series '" + InputKey + "' of lenght " + str(len(Vector)) + ' and units ' + str(VectorUnits))
        Time = self.get_Vector( 'TIME' )[ 'TIME' ]
        TimeUnits = self.get_Unit('TIME')
        verbose( self.speak , 1 , "<integrate> retrieved series 'TIME' of lenght " + str(len(Time)) + ' and units ' + str(TimeUnits))
        
        
        OutUnits = ''
        if '/' in VectorUnits :
            VectorSubUnits={}
            for i in range(len(VectorUnits.split('/'))) :
                VectorSubUnits[i] = VectorUnits.split('/')[i]
            if TimeUnits in VectorSubUnits :
                OutUnits = []
                ConvFactor = 1
                for i in range(len(VectorSubUnits)) :
                    if VectorSubUnits[i] == TimeUnits :
                        if i == 0 :
                            OutUnits.append(VectorSubUnits[i]+'*'+VectorSubUnits[i])
                        else :
                            pass
                    else :
                        OutUnits.append(VectorSubUnits[i])
            else :
                OutUnits = []
                ConvFactor = 1
                for i in range(len(VectorSubUnits)) :
                    verbose( self.speak , 1 , "<integrate> converting " + str(TimeUnits) + ' to ' + str(VectorSubUnits[i]))
                    if convertibleUnits(VectorSubUnits[i],TimeUnits) :
                        ConvFactor = ConvFactor * convertUnit(1, TimeUnits , VectorSubUnits[i] , PrintConversionPath=(self.speak==1) )
                        verbose( self.speak , 1 , "<integrate> conversion factor: 1 " + str(TimeUnits) + ' = '  + str( ConvFactor ) + ' ' + str(VectorSubUnits[i]))
                    else :
                        OutUnits.append(VectorSubUnits[i])
                        verbose( self.speak , 1 , "<integrate> not convertible")
                        
            OutUnits = '/'.join(OutUnits)
        else :
            OutUnits = VectorUnits + '*' + TimeUnits
            ConvFactor = 1
        
        verbose( self.speak , 1 , "<integrate> integrated series units will be " + str(OutUnits))
        
        if len(Vector) != len(Time) :
            raise TypeError( ' the Key vector ' + InputKey + ' and its TIME does not have the same lenght: ' + str( len(Vector) ) + ' != ' + str( len(Time) ) + '.' )
        
        
        if Numpy == False :
            # integrating one row at a time, iterating with for:
            verbose( self.speak , 2 , "<integrate> calculating integral for key '" + InputKey + "' using for loor")
            Cumulative = [0.0]
            if ConstantRate == False :
                for i in range(len(Vector)-1) :
                    dt = ( Time[i+1] - Time[i] ) * ConvFactor
                    if Vector[i] <= Vector[i+1] :
                        Vmin = Vector[i]
                        Vmax = Vector[i+1]
                    else :
                        Vmin = Vector[i+1]
                        Vmax = Vector[i]
                    Cumulative.append( Cumulative[i-1] + dt * Vmin + dt * (Vmax - Vmin) / 2.0 )
            else :
                for i in range(len(Vector)-1) :
                    Cumulative.append( Cumulative[i-1] + dt * Vector[i] )
        
        else :
            # integrating numpy method:
            verbose( self.speak , 2 , "<integrate> calculating integral for key '" + InputKey + "' using numpy methods")
            for X in ( Time , Vector ) :
                if type(X) != np.ndarray :
                    if type(X) == list or type(X) == tuple :
                        try :
                            X = np.array(X,dtype='float')
                        except :
                            print(" the key '" + X + "' is not numpy array.")
 
            dt = np.diff( Time ) * ConvFactor
            
            if ConstantRate == False :
                Vmin = np.minimum( Vector[:-1] , Vector[1:] )
                Vmax = np.maximum( Vector[:-1] , Vector[1:] )
                Cumulative = dt * Vmin + dt * ( Vmax - Vmin ) / 2.0
            else : 
                Cumulative = dt * Vector[:-1]
            
            Cumulative = [0.0] + list( Cumulative )
            Cumulative = np.array( Cumulative , dtype='float' )
            Cumulative = np.cumsum( Cumulative )
        
        try :
            self.set_Vector(OutputKey, np.array( Cumulative ) , OutUnits , overwrite=False )
        except OverwrittingError :
            pass
        return ( OutputKey , np.array( Cumulative ) , OutUnits )
    
    def get_DataFrame(self,Keys=None,Index='TIME') :
        """
        returns a pandas DataFrame for the keys in the argument.
        
        The argument * Keys * can be:
            > a string with one Key
            > a list of string Keys
            > the string '--EVERYTHING--' to extract ALL the keys in 
            the summary file but consider it could take long time to run
            before requesting everything.
            
        The argument * Index * will be passed as the index of the DataFrame.
        By default will be 'TIME' but could be 'DATES' or any other like 'FOPT'
        """
        if type(Keys) == str :
            if Keys == '--EVERYTHING--' :
                Keys = list( self.get_Keys() )
            else :
                Keys = [Keys]
        if type(Index) == list or type(Index) == tuple :
            if len(Index) > 1 :
                verbose( self.speak , -1 , '< get_DataFrame > more than value passed in Index argument, only the first one will be used')
            Index = Index[0]
        return pd.DataFrame( data=self.get_Vector( Keys ) , index=self.get_Vector( Index )[ Index ] )
    
    def get_ConvertedDataFrame(self,Keys=None,Index='TIME', OtherObject_or_NewUnits=None) :
        """
        returns a pandas DataFrame for the keys in the argument converted to 
        the specified units.
        
        The argument * Keys * can be:
            > a string with one Key
            > a list of string Keys
            > the string '--EVERYTHING--' to extract ALL the keys in 
            the summary file but consider it could take long time to run
            before requesting everything.
            
        The argument * Index * will be passed as the index of the DataFrame.
        By default will be 'TIME' but could be 'DATES' or any other like 'FOPT'
        
        The argument * OtherObject_or_NewUnits * can be:
            > a string of the new units for a single Key 
            > a list new units for every Key in the Keys argument
            > a SimResult object, the new units will be extracted from it.
        """
        if type(Keys) == str :
            if Keys == '--EVERYTHING--' :
                Keys = list( self.get_Keys() )
            else :
                Keys = [Keys]
        if type(Index) == list or type(Index) == tuple :
            if len(Index) > 1 :
                verbose( self.speak , -1 , '< get_DataFrame > more than value passed in Index argument, only the first one will be used')
            Index = Index[0]
        elif type(Index) == str :
            pass 
        else :
            try :
                if Index.SimResult == True :
                    if OtherObject_or_NewUnits is None :
                        OtherObject_or_NewUnits = Index
                        Index = 'TIME'
            except :
                pass
    
        if Index not in Keys:
            DF = self.get_UnitsConverted( [Index] + Keys , OtherObject_or_NewUnits )
            DF = pd.DataFrame( data=DF , index=DF[Index] )
        else :
            DF = self.get_UnitsConverted( Keys , OtherObject_or_NewUnits )
            DF = pd.DataFrame( data=DF , index=DF[Index] )
        return DF


    # def save( self,FileNamePath ) :
    #     Ext , fileName , Folder , FullPath = extension(FileNamePath)
    #     # create the folders structure:
    #     try :
    #         os.mkdir(Folder + fileName + '_storage')
    #     except :
    #         print( ' folder already exists')
    #     try :
    #         os.mkdir(Folder + fileName + '_storage' + '/parquet')
    #     except :
    #         print( ' parquet already exists')
    #     try :
    #         os.mkdir(Folder + fileName + '_storage' + '/raw')
    #     except :
    #         print( ' raw already exists')
    #     try :
    #         os.mkdir(Folder + fileName + '_storage' + '/json')
    #     except :
    #         print( ' raw already exists')
                               
    #     txtfile = 'SimResult =:= ' + str( self.SimResult ) + '\n'
    #     txtfile = txtfile + 'kind =:= ' + str( self.kind ) + '\n'
        
    #     if self.kind == ECL :
    #         pass
    #     elif self.kind == VIP :
    #         count = 0
    #         if len(self.results) == 0 and self.CSV != False :
    #             self.CSVgenerateResults()
            
    #         resultstxt = ''
    #         for each in list( self.results.keys() ) :
    #             DF_raw = pd.DataFrame( self.results[each][1]['Data'] )
    #             if 'TIME' in DF_raw.columns :
    #                 DF_raw.set_index('TIME',drop=False,inplace=True)
    #             DF_raw.to_parquet(Folder + fileName + '_storage/raw/' + str(count) + '_rawdata.sro' , index=True)
    #             with open(Folder + fileName + '_storage/raw/' + str(count) + '_rawunits.sro', 'w') as file:
    #                 file.write(json.dumps( self.results[each][1]['Units'] )) 
    #             resultstxt = resultstxt + str( count ) + ' =:= ' + str( each ) + ' =:= ' + self.results[each][0] + ' \n'
                
    #         with open(Folder + fileName + '_storage/raw/keys.sro', 'w') as file:
    #             file.write( resultstxt )
        
    #     if self.name is None :
    #         txtfile = txtfile + 'name =:= ' + '=@:None:@=' + '\n'
    #     else :
    #         txtfile = txtfile + 'name =:= ' + str( self.name ) + '\n'
    #     txtfile = txtfile + 'path =:= ' + str( self.path ) + '\n'
    #     txtfile = txtfile + 'start =:= ' + str( self.start ) + '\n'
    #     txtfile = txtfile + 'end =:= ' + str( self.end ) + '\n'
    #     txtfile = txtfile + 'wells =:= ' + str( self.wells ) + '\n'
    #     txtfile = txtfile + 'groups =:= ' + str( self.groups ) + '\n'
    #     txtfile = txtfile + 'regions =:= ' + str( self.regions ) + '\n'
    #     txtfile = txtfile + 'keys =:= ' + str( self.keys ) + '\n'
        
    #     # dump attributes dictionary to JSON file
    #     with open(Folder + fileName + '_storage/json/attributes.sro', 'w') as file:
    #         try :
    #             file.write(json.dumps( self.attributes ))
    #         except :
    #             file.write(str( self.attributes ))
        
    #     # prepare vectors as dataframe and dump to parquet
    #     DF_vectors = pd.DataFrame(self.vectors)
    #     DF_vectors.set_index('TIME',drop=False,inplace=True)
    #     DF_vectors.to_parquet(Folder + fileName + '_storage/parquet/vectors.sro' , index=True )
        
    #     # dump units dictionary to JSON file
    #     with open(Folder + fileName + '_storage/json/units.sro', 'w') as file:
    #         file.write(json.dumps( self.units )) 
            
    #     txtfile = txtfile + 'overwrite =:= ' + str( self.overwrite ) + '\n'
    #     txtfile = txtfile + 'null =:= ' + str( self.null ) + '\n'
    #     txtfile = txtfile + 'color =:= ' + str( self.color ) + '\n'
    #     txtfile = txtfile + 'restarts =:= ' + str( self.restarts ) + '\n'
        
    #     # prepare restart vectors as dataframe and dump to parquet
    #     if len(self.vectorsRestart) > 0 :
    #         DF_vectors = pd.DataFrame(self.vectorsRestart)
    #         DF_vectors.to_parquet(Folder + fileName + '_storage/parquet/restarts.sro' , index=True )
                              
    #     # txtfile = txtfile + 'pandasColumns =:= ' + str( self.pandasColumns ) + '\n'
    #     if self.fieldtime == (None,None,None) :
    #         txtfile = txtfile + 'fieldtime =:= ' + str(self.fieldtime) + '\n'
    #     else :
    #         txtfile = txtfile + 'fieldtime =:= ' + str( self.fieldtime[0] ) + ' =:= ' + str( self.fieldtime[1] ) + ' =:= ' + str( list(self.fieldtime[2]) ) + '\n'
            

    #     if self.kind == VIP :
    #         txtfile = txtfile + 'ECLstyle =:= ' + str( self.ECLstyle ) + '\n'
    #         txtfile = txtfile + 'VIPstyle =:= ' + str( self.VIPstyle ) + '\n'
    #         txtfile = txtfile + 'keysECL =:= ' + str( self.keysECL ) + '\n'
    #         txtfile = txtfile + 'keysVIP =:= ' + str( self.keysVIP ) + '\n'
    #         txtfile = txtfile + 'keysCSV =:= ' + str( self.keysCSV ) + '\n'
    #         if self.CSV == False :
    #             txtfile = txtfile + 'CSV =:= ' + str( False ) + '\n'
    #         else :
    #             txtfile = txtfile + 'CSV =:= ' + str( True ) + '\n'
    #         txtfile = txtfile + 'LPGcorrected =:= ' + str( self.LPGcorrected ) + '\n'
            
    #     # dump __init__ data to TXT file
    #     with open(Folder + fileName + '_storage/init.sro', 'w') as file:
    #         file.write( txtfile )
    #     with open(Folder + fileName + '.sro', 'w') as file:
    #         file.write( txtfile )
        
        
        
        
        
    # def restore( self,FileNamePath ) :
    #     Ext , fileName , Folder , FullPath = extension(FileNamePath)

        
    #     RestorePath = Folder + fileName + '_storage/' 
    #     try:
    #         file = open(RestorePath+'init.sro','r')
    #     except :
    #         print( " the file " + FileNamePath +  "doesn't 'exist")
    #         return None
        
    #     txtfile = file.readlines()
        
    #     for line in txtfile :
    #         print(' reading: ' + line)
    #         key = line.split(' =:= ')[0]
            
    #         print('reading ', key , line.split(' =:= ')[1])
    #         if key == 'SimResult' :
    #             self.SimResult = bool( line.split(' =:= ')[1] )
    #         elif key == 'kind' :
    #             if 'ECL' in line.split(' =:= ')[1] :
    #                 self.kind = ECL
    #             elif 'VIP' in line.split(' =:= ')[1] :
    #                 self.kind = VIP
    #         elif key == 'name' :
    #             if line.split(' =:= ')[1] == '=@:None:@=' :
    #                 self.name = None
    #             else :
    #                 self.name = line.split(' =:= ')[1]
    #         elif key == 'path' :
    #             self.path = line.split(' =:= ')[1]
    #         elif key == 'start' :
    #             self.start = line.split(' =:= ')[1]
    #         elif key == 'end' :
    #             self.end = line.split(' =:= ')[1]
    #         elif key == 'wells' :
    #             self.wells = tuple(line.split(' =:= ')[1][1:-1].split(','))
    #         elif key == 'groups' :
    #             self.groups = tuple(line.split(' =:= ')[1][1:-1].split(','))
    #         elif key == 'regions' :
    #             self.regions = tuple(line.split(' =:= ')[1][1:-1].split(','))
    #         elif key == 'keys' :
    #             self.keys = tuple(line.split(' =:= ')[1][1:-1].split(','))
    #         elif key == 'overwrite' :
    #             self.overwrite = line.split(' =:= ')[1]
    #         elif key == 'null' :
    #             self.null = line.split(' =:= ')[1]
    #         elif key == 'color' :
    #             self.color = tuple(line.split(' =:= ')[1].split(','))
    #         elif key == 'restarts' :
    #             self.restarts = line.split(' =:= ')[1]
    #         elif key == 'ECLstyle' :
    #             self.ECLstyle = bool( line.split(' =:= ')[1] )
    #         elif key == 'VIPstyle' :
    #             self.VIPstyle = bool( line.split(' =:= ')[1] )
            
    #         elif key == 'keysECL' :
    #             self.keysECL = tuple(line.split(' =:= ')[1].split(','))
    #         elif key == 'keysVIP' :
    #             self.keysVIP = tuple(line.split(' =:= ')[1].split(','))
    #         elif key == 'keysCSV' :
    #             self.keysCSV = tuple(line.split(' =:= ')[1].split(','))
    #         elif key == 'CSV' :
    #             self.CSV = bool( line.split(' =:= ')[1] )
    #         elif key == 'LPGcorrected' :
    #             self.LPGcorrected = bool( line.split(' =:= ')[1] )
    #         elif key == 'fieldtime' :
    #             self.fieldtime = ( float(line.split(' =:= ')[1][1:]) , float(line.split(' =:= ')[2]) , np.array( line.split(' =:= ')[3][1:-2].split(',') , dtype='float' ) )
                
    #     if self.kind == ECL :
    #         pass
    #     elif self.kind == VIP :
    #         pass
    #         # count = 0

                        
    #     # load attributes dictionary to JSON file
    #     with open(RestorePath + 'json/attributes.sro', 'r') as file:
    #         self.attributes = json.load( file )
        
    #     # load vectors as dataframe and dump from parquet
    #     self.vectors = (pd.read_parquet( RestorePath + 'parquet/vectors.sro' )).to_dict()
        
    #     # dump units dictionary to JSON file
    #     with open(RestorePath + 'json/units.sro', 'r') as file:
    #         self.units = json.load( file )
            
        