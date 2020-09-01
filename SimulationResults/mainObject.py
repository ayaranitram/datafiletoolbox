# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:14:35 2020

@author: MCARAYA
"""

__version__ = '0.0.20-08-27'

from datafiletoolbox import dictionaries
from datafiletoolbox.Classes.Errors import OverwrittingError
from datafiletoolbox.common.stringformat import date as strDate
from datafiletoolbox.common.stringformat import isDate 
from datafiletoolbox.common.stringformat import multisplit , isnumeric , getnumber
from datafiletoolbox.common.functions import is_SimulationResult , mainKey , itemKey , wellFromAttribute , isECLkey , keyType
from datafiletoolbox.common.inout import extension
from datafiletoolbox.common.inout import verbose 
from datafiletoolbox.PlotResults.SmartPlot import Plot
from datafiletoolbox.common.progressbar import progressbar

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

# creating vectorized numpy object for len function
nplen = np.vectorize(len)

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
                VectorData : a Numpy array (of the same length as the arrays already in the results)
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
    
    ### define common dictionaries and constants
        
    VIPnotECL = []
    
    CSV_Variable2Verbose = {}
    CSV_Verbose2Variable = {}
    
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
        self.filter = {'key':[None],'min':[None],'max':[None],'condition':[None],'filter':None,'reset':True,'incremental':[None],'operation':[None]}
        self.filterUndo = None
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
        self.restartFilters = {}
        self.continuations = []
        self.continuationFilters = {}
        self.vectorsRestart = {}
        self.pandasColumns = { 'HEADERS' : {} , 'COLUMNS' : {} , 'DATA' : {} }
        self.fieldtime = ( None , None , None ) 
        self.GORcriteria = ( 10 , 'Mscf/stb' )
        self.WCcriteria = 1 
        self.wellsLists = {}
        self.printMessages = 0
    
    def initialize(self) :
        """
        run intensive routines, to have the data loaded and ready
        """
        self.get_Producers()
        self.get_Injectors()
    
    def __call__(self,Key=None,Index=None) :
        if Index is None :
            Index = self.DTindex
        if Key is not None :
            if type(Key) is list and len(Key) > 0:
                return self.get_DataFrame(Key,Index)
            elif type(Key) is str and len(Key) > 0 :
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
        """
        creates s vector with the provided Key or the pair of Values and Units
        """
        if type(Value) is tuple :
            if len(Value) == 2 :
                if type(Value[0]) is np.ndarray :
                    if type(Value[1]) is str :
                        Value , Units = Value[0] , Value[1]
                elif type(Value[0]) is list or type(Value[0]) is tuple :
                    if type(Value[1]) is str :
                        Value , Units = np.array(Value[0]) , Value[1]
                elif type(Value[0]) is int or type(Value[0]) is float :
                    if type(Value[1]) is str :
                        Value , Units = [ Value[0] ] * len(self.fieldtime[2]) , Value[1]
                    elif type(Value[1]) is None :
                        Value , Units = [ Value[0] ] * len(self.fieldtime[2]) , 'DIMENSIONLESS'
                elif type(Value[0]) is pd.core.frame.DataFrame :
                    if type(Value[1]) is str :
                        Value , Units = Value[0] , Value[1]
                    elif type(Value[1]) is list or type(Value[1]) is tuple :
                        pass
                        # if len(Value[1]) == len(Value[0].columns) :
                        #     Value , Units = Value[0] , Value[1]
                        # else :
                        #     verbose( self.speal , 3 , "not enough units received\n received: " + str(len(Value[1])) + "\n required: " + str(len(Value[0].columns)) )
                        #     return False
                    elif type(Value[1]) is None :
                        Value , Units = Value[0] , 'DIMENSIONLESS'
                        verbose( self.speak , 3 , "no Units received, set as DIMENSIONLESS.\nto set other units use second argument.\nto set different units for each column, use '!' as separator to define the units as sufix in each name:\n i.e.: MAIN:ITEN!UNIT \n       MAIN!UNIT ")

                    
        if self.is_Key(Key) :
            verbose(self.speak,3,"WARNING, the key '" + Key + "' is already in use. It will be overwritten!")
            
        if type(Value) is str :
            if self.is_Key(Value) :
                Units = self.get_Units(Value)
                Value = self.get_Vector(Value)[Value]
            elif self.is_Attribute(Value) :
                verbose( self.speak , 2 , "the received argument '" + Value + "' is not a Key but an Attribute, every key for the attribute will be processed.")                   
                KeyList = self.get_KeysFromAttribute(Value)
                
                for K in KeyList :
                    NewKey = mainKey(Key) + ':' + K.split(':')[-1]
                    verbose( self.speak , 2 , "   processing '" + K + "'") 
                    self.__setitem__( NewKey , K )
                return None
            else :
                # might be calculation
                if '=' in Value :
                    calcStr = Key + '=' + Value[Value.index('=')+1:]
                else :
                    calcStr = Key + '=' + Value
                try :
                    # print(calcStr)
                    return self.RPNcalculator( calcStr )
                except :
                    return None
                
        elif type(Value) is list or type(Value) is tuple :
            Value = np.array(Value)
        
        elif type(Value) is int or type(Value) is float :
            Value , Units = [ Value ] * len(self.fieldtime[2]) , 'DIMENSIONLESS'
            
        if type(Value) is np.ndarray :
            if len(Value) != len(self.fieldtime[2]) :
                raise TypeError(" the 'Value' array must have the exact same length of the simulation vectors: " + str(len(self.fieldtime[2])) )
            if type(Units) is str :
                Units = Units.strip('( )')
            elif Units is None :
                Units = str(None)
            else :
                Units = str(Units)
            if unit.isUnit(Units) :
                pass
            else :
                verbose(self.speak , 2 , " the 'Units' string is not recognized." )
        
        if type(Value) is pd.core.frame.DataFrame :
            if len(Value) == len(self.fieldtime[2]) :
                for Col in Value.columns :
                    if '!' in Col :
                        Col , ThisUnits = Col.split('!')[0].strip() , Col.split('!')[1].strip()
                    else :
                        ThisUnits = Units
                    if ':' in Col :
                        ThisMain , ThisItem = Col.split(':')[0].strip() , Col.split(':')[1].strip()
                    else :
                        ThisMain , ThisItem = Key , Col.strip()
                    
                    if self.is_Key(Col) :
                        ThisMain = Key
                    
                    if ThisItem == '' :
                        ThisKey = Key
                    elif ThisItem == Key :
                        ThisKey = Key
                    else :
                        ThisKey = ThisMain + ':' + ThisItem

                    self.set_Vector( ThisKey , Value[Col].to_numpy() , ThisUnits , DataType='auto' , overwrite=True)
                return None
            else :
                verbose( self.speak , 3 , "the lengh of the DataFrame must coincide with the number of steps of this simulation results.")

        self.set_Vector( Key , Value , Units , DataType='auto' , overwrite=True)
    
    def __len__(self) :
        """
        return the number of keys * number of time steps in the dataset
        """
        return self.len_Keys() * self.len_tSteps()
    
    def __str__(self) :
        return self.name
    
    def __repr__(self):
        self.printMessages = 1
        
        text = str(self.kind).split('.')[-1][:-2] + " simulation: '" + self.name + "'"
        if self.is_Key('DATE') :
            text = text + '\n from ' + str(self('DATE')[0]) + ' to ' + str(self('DATE')[-1])
        if self.is_Key('FOIP') :
            text = text + '\n STOIP @ first tstep: ' + str(self('FOIP')[0]) + ' ' + self.get_Units('FOIP')
        if self.is_Key('FGIP') :
            text = text + '\n GIP @ first tstep: ' + str(self('FGIP')[0]) + ' ' + self.get_Units('FGIP')
            
        text = text + '\n\n production wells: ' + str( len( self.get_Producers() ) )
        if self.get_OilProducers() != [] :
            text = text + '\n    oil wells' + ' ( with GOR<' + str(self.get_GORcriteria()[0]) + str(self.get_GORcriteria()[1]) + ' ) : ' + str(len( self.get_OilProducers() )) 
        if self.get_GasProducers() != [] :
            text = text + '\n    gas wells' + ' ( with GOR>' + str(self.get_GORcriteria()[0]) + str(self.get_GORcriteria()[1]) + ' ) : ' + str(len( self.get_GasProducers() )) 
        if self.get_WaterProducers() != [] :
            text = text + '\n  water wells: ' + str(len( self.get_WaterProducers() ))
            
        text = text + '\n\n injection wells: ' + str( len( self.get_Injectors() ) )
        if self.get_OilInjectors() != [] :
            text = text + '\n    oil wells: ' + str(len( self.get_OilInjectors() ))
        if self.get_GasInjectors() != [] :
            text = text + '\n    gas wells: ' + str(len( self.get_GasInjectors() ))
        if self.get_WaterInjectors() != [] :
            text = text + '\n  water wells: ' + str(len( self.get_WaterInjectors() ))
        
        self.printMessages = 0
        return text
    
    def keyGen(self,keys=[],items=[]) :
        """
        returns the combination of every key in keys with all the items.
        keys and items must be list of strings
        """
        if type(items) is str :
            items = [items]
        if type(keys) is str :
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
        print()
        print( self.__repr__() )
        print()
        
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
        
        # if self.is_Attribute('WOPR') is True or ( self.is_Attribute('WGPR') is True and ( self.is_Attribute('WOGR') is True or self.is_Attribute('WGOR') is True ) ) :
        #     desc['oilProducers'] = [ len( self.get_OilProducers() ) , '' , '' ]
        
        # if self.is_Attribute('WGPR') is True or ( self.is_Attribute('WOPR') is True and ( self.is_Attribute('WOGR') is True or self.is_Attribute('WGOR') is True ) ) :
        #     desc['gasProducers'] = [ len( self.get_GasProducers() ) , '' , '' ]
        
        # if self.is_Attribute('WWPR') is True or self.is_Attribute('WWCT') is True :
        #     desc['waterProducers'] = [ len( self.get_WaterProducers() ) , '' , '' ] 

        # if self.is_Attribute('WOIR') :
        #     desc['oilInjectors'] = [ len( self.get_OilInjectors() ) , '' , '' ]
        
        # if self.is_Attribute('WGIR') :
        #     desc['gasInjectors'] = [ len( self.get_GasInjectors() ) , '' , '' ]
        
        # if self.is_Attribute('WWIR') :
        #     desc['waterInjectors'] = [ len( self.get_WaterInjectors() ) , '' , '' ]
        
        return pd.DataFrame( data=desc , index=Index)
    
    def get_WaterInjectors( self , reload=False ) :
        """
        returns a list of the wells that inject water at any time in the simulation.
        """
        if 'WaterInjectors' not in self.wellsLists or reload is True :
            verbose( self.printMessages , 1 , '# extrating data to count water injection wells' )
            if self.is_Attribute('WWIR') :
                self.wellsLists['WaterInjectors'] = list( self[['WWIR']].replace(0,np.nan).dropna(axis=1,how='all').columns ) 
            else :
                self.wellsLists['WaterInjectors'] = []
        return self.wellsLists['WaterInjectors']
        
    def get_GasInjectors( self , reload=False ) :
        """
        returns a list of the wells that inject gas at any time in the simulation.
        """
        if 'GasInjectors' not in self.wellsLists or reload is True :
            verbose( self.printMessages , 1 , '# extrating data to count gas injection wells' )
            if self.is_Attribute('WGIR') :
                self.wellsLists['GasInjectors'] = list( self[['WGIR']].replace(0,np.nan).dropna(axis=1,how='all').columns ) 
            else :
                self.wellsLists['GasInjectors'] = []
        return self.wellsLists['GasInjectors']
    
    def get_OilInjectors( self , reload=False ) :
        """
        returns a list of the wells that inject oil at any time in the simulation.
        """
        if 'OilInjectors' not in self.wellsLists or reload is True :
            verbose( self.printMessages , 1 , '# extrating data to count oil injection wells' )
            if self.is_Attribute('WOIR') :
                self.wellsLists['OilInjectors'] = list( self[['WOIR']].replace(0,np.nan).dropna(axis=1,how='all').columns ) 
            else :
                self.wellsLists['OilInjectors'] = []
        return self.wellsLists['OilInjectors']
    
    def get_Injectors( self , reload=False ) :
        if 'Injectors' not in self.wellsLists or reload is True :
            self.wellsLists['Injectors'] = list( set( self.get_WaterInjectors( reload ) + self.get_GasInjectors( reload ) + self.get_OilInjectors( reload ) ) )
        return self.wellsLists['Injectors']
    
    def get_WaterProducers( self , reload=False ) :
        """
        returns a list of the wells that produces more than 99.99% water at any time in the simulation.
        """
        if 'WaterProducers' not in self.wellsLists or reload is True :
            verbose( self.printMessages , 1 , '# extrating data to count water production wells' )
            if self.is_Attribute('WWPR') :
                waterProducers = self[['WWPR']]
                waterProducers = waterProducers.rename( columns=wellFromAttribute( waterProducers.columns ) )
                
                prodCheck = waterProducers * 0
                
                if self.is_Attribute('WOPR') :
                    oilProducers = self[['WOPR']]
                    oilProducers = oilProducers.rename( columns=wellFromAttribute( oilProducers.columns ) )
                    prodCheck = oilProducers + prodCheck
                
                if self.is_Attribute('WGPR') :
                    gasProducers = self[['WGPR']]
                    gasProducers = gasProducers.rename( columns=wellFromAttribute( gasProducers.columns ) )
                    prodCheck = gasProducers + prodCheck
                
                prodCheck = ( (prodCheck==0) & (waterProducers>0) ).replace(False,np.nan).dropna(axis=1,how='all')
                
                self.wellsLists['WaterProducers'] = list( prodCheck.columns ) 
                
        elif self.is_Attribute('WWCT') :
            waterCheck = self[['WWPR']]
            waterCheck = waterCheck.rename( columns=wellFromAttribute( waterCheck.columns ) )
            waterCheck = ( waterCheck >= self.WCcriteria ).replace(False,np.nan).dropna(axis=1,how='all')
            self.wellsLists['WaterProducers'] = list( waterCheck.columns ) 
            
        else :
            self.wellsLists['WaterProducers'] = []
        
        return self.wellsLists['WaterProducers']
    
    def get_OilProducers( self , reload=False ) :
        """
        returns a list of the wells considered oil producers at any time in the simulation.
        the GOR criteria to define the oil and gas producers can be modified by the method .set_GORcriteria()
        """
        if reload is True or 'OilProducers' not in self.wellsLists :
            verbose( self.printMessages , 1 , '# extrating data to count oil production wells' )
            if self.is_Attribute('WOPR') and self.is_Attribute('WGPR') :
                OIL = self[['WOPR']]
                OIL.rename( columns=wellFromAttribute( OIL.columns ) , inplace=True ) 
                # OIL.replace( 0,np.nan , inplace=True )
                
                GAS = self[['WGPR']]
                GAS.rename( columns=wellFromAttribute( GAS.columns ) , inplace=True )
                
                rateCheck = ((OIL>0) | (GAS>0)) # rateCheck = ((OIL>0) + (GAS>0))
                
                GOR = GAS / OIL
                GOR.replace(np.nan,9E9 , inplace=True)
                GOR = GOR[rateCheck].dropna(axis=1,how='all')
                
                # the loop is a trick to avoid memory issues when converting new 
                i = 0
                test = False
                while not test and i < 10 :
                    i += 1
                    test = convertibleUnits( self.GORcriteria[1] , self.get_Unit('WGPR').split('/')[0] + '/' + self.get_Unit('WOPR').split('/')[0] )
                GORcriteria = convertUnit( self.GORcriteria[0] , self.GORcriteria[1] , self.get_Unit('WGPR').split('/')[0] + '/' + self.get_Unit('WOPR').split('/')[0] , PrintConversionPath=False )

                self.wellsLists['OilProducers'] = list( (GOR<=GORcriteria).replace(False,np.nan).dropna(axis=1,how='all').columns )
                self.wellsLists['GasProducers'] = list( (GOR >GORcriteria).replace(False,np.nan).dropna(axis=1,how='all').columns )
            
            elif self.is_Attribute('WGOR') :
                GOR = self[['WGOR']]
                GOR = ( GOR.rename( columns=wellFromAttribute( GOR.columns ) ) )
                
                rateCheck = (GOR<0) & (GOR>0) # to generate a dataframe full of False
                
                if self.is_Attribute('WOPR') :
                    OIL = self[['WOPR']]
                    OIL.rename( columns=wellFromAttribute( OIL.columns ) , inplace=True ) 
                    rateCheck = rateCheck | (OIL>0)
                if self.is_Attribute('WGPR') :
                    GAS = self[['WGPR']]
                    GAS.rename( columns=wellFromAttribute( GAS.columns ) , inplace=True )
                    rateCheck = rateCheck | (GAS>0)
                
                GOR = GOR[rateCheck].dropna(axis=1,how='all')
                
                GORcriteria = convertUnit( self.GORcriteria[0] , self.GORcriteria[1] , self.get_Unit('WGOR') )
                self.wellsLists['OilProducers'] = list( (GOR<=GORcriteria).replace(False,np.nan).dropna(axis=1,how='all').columns )
                self.wellsLists['GasProducers'] = list( (GOR >GORcriteria).replace(False,np.nan).dropna(axis=1,how='all').columns )
            
            elif self.is_Attribute('WOGR') :
                GOR = 1 / self[['WGOR']]
                GOR = ( GOR.rename( columns=wellFromAttribute( GOR.columns ) ) ).dropna(axis=1,how='all')
                GORcriteria = convertUnit( self.GORcriteria[0] , self.GORcriteria[1] , self.get_Unit('WGOR') )
                self.wellsLists['OilProducers'] = list( (GOR<=GORcriteria).replace(False,np.nan).dropna(axis=1,how='all').columns )
                self.wellsLists['GasProducers'] = list( (GOR >GORcriteria).replace(False,np.nan).dropna(axis=1,how='all').columns )
           
            elif self.is_Attribute('WOPR') :
                verbose( self.speak , 2 , 'neither GOR or GAS RATE available, every well with oil rate > 0 will be listeda as oil producer.' )
                self.wellsLists['OilProducers'] = wellFromAttribute( list( self[['WOPR']].replace(0,np.nan).dropna(axis=1,how='all').columns ) )
            
            else :
                self.wellsLists['OilProducers'] = []
        return self.wellsLists['OilProducers']
    
    def get_GasProducers( self , reload=False ) :
        """
        returns a list of the wells considered gas producers at any time in the simulation.
        the GOR criteria to define the oil and gas producers can be modified by the method .set_GORcriteria()
        """
        if reload is True or 'GasProducers' not in self.wellsLists :
            verbose( self.printMessages , 1 , '# extrating data to count gas production wells' )
            catch = self.get_OilProducers(reload=True)
            if 'GasProducers' not in self.wellsLists and self.is_Attribute('WGPR') is True :
                verbose( self.speak , 2 , 'neither GOR or OIL RATE available, every well with gas rate > 0 will be listeda as gas producer.' )
                self.wellsLists['GasProducers'] = wellFromAttribute( list( self[['WGPR']].replace(0,np.nan).dropna(axis=1,how='all').columns ) )
            elif 'GasProducers' not in self.wellsLists :
                self.wellsLists['GasProducers'] = []
        return self.wellsLists['GasProducers']

    def get_Producers( self , reload=False ) :
        if 'Producers' not in self.wellsLists or reload is True :
            self.wellsLists['Producers'] = list( set( self.get_WaterProducers( reload ) + self.get_GasProducers( reload ) + self.get_OilProducers( reload ) ) )
        return self.wellsLists['Producers']
        
    def set_index(self,Key) :
        self.set_Index(Key)
    def set_Index(self,Key) :
        if self.is_Key(Key) :
            self.DTindex = Key
    def get_index(self) :
        return self.get_Index()
    def get_Index(self) :
        return self.DTindex
    
    def set_GORcriteria( self, GOR=10.0 , Units=None ) :
        """
        change the GOR criteria to define a producer well as oil or gas producer.
        By default, it is set to 10Mscf/stb.
        
        if changed, the lists oilProducers and gasProducers will be recalculated.

        """
        
        if type(self.get_Unit('WGOR')) is str and len(self.get_Unit('WGOR'))>0 :
            SimUnits = self.get_Unit('WGOR')
        elif type(self.get_Unit('WOPR')) is str and len(self.get_Unit('WOPR'))>0 and \
            type(self.get_Unit('WGPR')) is str and len(self.get_Unit('WGPR'))>0:
            SimUnits = self.get_Unit('WGPR').split(':')[0] / self.get_Unit('WOPR').split(':')[0] 
            
        if Units is None :
            Units = SimUnits
        elif type(Units) is str and len(Units)>0 :
            Units = Units.strip()
            if not convertibleUnits(Units,SimUnits) :
                print( "please provide valid GOR units, received,'"+Units+"'")
        else :
            print( 'please provide Units for the GOR criteria')
            return False
        
        if type(GOR) is float or type(GOR) is int :
            self.GORcriteria = ( GOR , Units )
            catch = self.get_OilProducers(reload=True)
            return True
        else :
            print( 'GOR value should be integer or float')
            return False
        
    def get_GORcriteria( self ) :
        return self.GORcriteria
        
        
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
                            mainKs = mainKey( matchedKeys )
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

    def set_Units(self,Key,Unit=None,overwrite=False) :
        return self.set_Unit(Key)    
    def set_Unit(self,Key,Unit=None,overwrite=False) :
        if type(Key) is str :
            if self.is_Key(Key) :
                Key = [Key]
            elif self.is_Attribute(Key) :
                Key = self.attributes[Key]
        if type(Unit) is str :
            Unit = [Unit]*len(Key)

        if Unit is None and type(Key) is dict :
            keysDict = Key.copy()  
        elif len(Key) != len(Unit) :
            raise ValueError('the lists of Keys and Units must have the same length')
        
        keysDict = dict(zip(Key,Unit))
        
        for k , u in keysDict.items() :
            if k in self.units :
                if self.units[k] == 'None' or overwrite is True :
                    self.units[k] = u
                    keysDict[k] = True
                else :
                    verbose( self.speak , 2 , "the key '" +k+ "' has '" +u+ "' already defined as units, add parameter  overwrite=True  to change this key units." )
                    keysDict[k] = False
            else :
                self.units[k] = u
                keysDict[k] = True
        return keysDict

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
    
    def plot(self,Keys=[],Index=None,otherSims=None,Wells=[],Groups=[],Regions=[],DoNotRepeatColors=None) : # Index='TIME'

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
        if Index is None :
            Index = self.get_Index()
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

        # extract and discard the vectors before calling the Plot, to avoid latency issues
        for sim in SimsToPlot :
            prevSpeak , sim.speak = sim.speak , 0
            for Y in PlotKeys :
                trash = sim(Y)
            for X in IndexList :
                trash = sim(X)
            sim.speak = prevSpeak
            
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
        
        if type(WellKeys) is str :
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
                if type(KeyUnits) is str and len(KeyUnits) > 0 :
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
            if AGG + 'of' + key + ':' + ','.join(WellsToGroup) in self.vectors and force is False :
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
                            verbose( self.speak , 1 , " < inizializing sum vectr with length " + str(size) + " >")
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
                    verbose( self.speak , 3 , ' saving vector ' + NewKey + ':' + AggregatedKeyName + ' of length ' + str(len(returnVector[NewKey+':'+AggregatedKeyName])))
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
        force = bool(force)
        
        if self.fieldtime == ( None , None , None ) :
            self.set_FieldTime()
        
        if len(KeyTime) == 0 or len(KeyVector) == 0 :
            verbose(self.speak, 2 , ' <fillZeros> the received vectors are empty, thus, a zero filled vector will be returned with length equal to the field TIME vector.')
            return np.array([0.0]*len(self.fieldtime),dtype='float')
        
        if force is True or min(KeyTime) > self.fieldtime[0] or max(KeyTime) < self.fieldtime[1] :
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
        if type(name) is list or type(name) is tuple :
            if len(name) == 1 :
                name = name[0]
        if type(name) is str :
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
        if type( SimResultObject ) is list :
            self.restarts = self.restarts + SimResultObject 
        else :
            self.restarts.append(SimResultObject)
        self.restarts = list( set ( self.restarts ) )
        
        sortedR = []
        selfTi = self.get_RawVector('TIME')['TIME'][0]
        # remove simulations that starts after this one (self)
        for i in range(len(self.restarts)) :
            if self.restarts[i].get_RawVector('TIME')['TIME'][0] < selfTi :
                sortedR += [self.restarts[i]]
            else :
                verbose( self.speak , 3 , " the simulation '" + str(self.restarts[i]) + "' was not added as restart because it doesn't contain data before this simulation ( '" + str(self) +"' )." )
        self.restarts = sortedR
        
        # sort simulations by start time
        for i in range(len(self.restarts)) :
            for j in range(0,len(self.restarts)-i-1) :
                if self.restarts[j].get_RawVector('TIME')['TIME'][0] > self.restarts[j+1].get_RawVector('TIME')['TIME'][0] :
                    self.restarts[j] , self.restarts[j+1] = self.restarts[j+1] , self.restarts[j]
        
        # calculate restartFilters for each restart
        for i in range(len(self.restarts)-1) :
            thisFilter = self.restarts[i].get_RawVector('TIME')['TIME'] < self.restarts[i+1].get_RawVector('TIME')['TIME'][0]
            self.restartFilters[ self.restarts[i] ] = thisFilter
        # claculate restartFilters for the last restart
        thisFilter = self.restarts[-1].get_RawVector('TIME')['TIME'] < self.get_RawVector('TIME')['TIME'][0]
        self.restartFilters[ self.restarts[-1] ] = thisFilter
    
        # recreate filter for this simulation (self), now considering the restarts
        self.redo_Filter()
        # recalculate the total time for this simulation (self), now considering the restarts
        self.set_FieldTime()
        # print the restarts
        self.print_Restart()
    
    def set_Continue(self,SimResultObject) :
        self.set_Continuation(SimResultObject)
    def set_Continuation(self,SimResultObject) :
        if type( SimResultObject ) is list :
            self.continuations = self.continuations + SimResultObject 
        else :
            self.continuations.append(SimResultObject)
        self.continuations = list( set ( self.continuations ) )
        
        sortedC = []
        selfTf = self.get_RawVector('TIME')['TIME'][-1]
        # remove simulations that ends before this one (self)
        for i in range(len(self.continuations)) :
            if self.continuations[i].get_RawVector('TIME')['TIME'][-1] > selfTf :
                sortedC += [self.continuations[i]]
            else :
                verbose( self.speak , 3 , " the simulation '" + str(self.continuations[i]) + "' was not added as continuation because it doesn't contain data after this simulation ( '" + str(self) +"' )." )
        self.continuations = sortedC
        
        # sort simulations by start time
        for i in range(len(self.continuations)) :
            for j in range(0,len(self.continuations)-i-1) :
                if self.continuations[j].get_RawVector('TIME')['TIME'][-1] > self.continuations[j+1].get_RawVector('TIME')['TIME'][-1] :
                    self.continuations[j] , self.continuations[j+1] = self.continuations[j+1] , self.continuations[j]
        
        # calculate continuationFilters for each continuation
        for i in range(1,len(self.continuations)) :
            thisFilter = self.continuations[i].get_RawVector('TIME')['TIME'] > self.continuations[i-1].get_RawVector('TIME')['TIME'][-1]
            self.continuationFilters[ self.continuations[i] ] = thisFilter
        # claculate continuationFilters for the last continuation
        thisFilter = self.continuations[0].get_RawVector('TIME')['TIME'] > self.get_RawVector('TIME')['TIME'][-1]
        self.continuationFilters[ self.continuations[0] ] = thisFilter
    
        # recreate filter for this simulation (self), now considering the restarts
        self.redo_Filter()
        # recalculate the total time for this simulation (self), now considering the restarts
        self.set_FieldTime()
        # print the continuation
        self.print_Continuation()
        
    def print_Restart(self) :
        prevSpeak , self.speak = self.speak , -1
        message = self.get_Restart()
        self.speak = prevSpeak
    
    def print_Continuation(self) :
        prevSpeak , self.speak = self.speak , -1
        message = self.get_Continuation()
        self.speak = prevSpeak
 
    def clean_Restarts(self) :
        """
        ** alias for remove_Restart() ** 
        removes ALL the simulations from the restart list.
        equivalent to :
            .remove_Restart('--ALL')
        """
        self.remove_Restart(SimResultObject='--ALL')
    def clean_Restart(self) :
        """
        ** alias for remove_Restart() ** 
        removes ALL the simulations from the restart list.
        equivalent to :
            .remove_Restart('--ALL')
        """
        self.remove_Restart(SimResultObject='--ALL')
    def remove_Restarts(self,SimResultObject='--ALL') :
        """
        ** alias for remove_Restart() ** 
        removes ALL the simulations from the restart list.
        equivalent to :
            .remove_Restart('--ALL')
        """
        self.remove_Restart(self,SimResultObject='--ALL') 
    def remove_Restart(self,SimResultObject='--ALL') :
        """
        removes ALL the simulations from the restart list.
        equivalent to :
            .remove_Restart('--ALL')
        """
        if SimResultObject == '--ALL' :
            if len(self.restarts) == 0 :
                print(" nothing to remove, no restarts objects defined")
            else :
                print(" removed ALL the restart objects (" + str(len(self.restarts)) + " objects removed)" )
                self.restarts = []
                
        if SimResultObject in self.restarts :
            print(" removed restart object '" + str(self.restarts.pop(SimResultObject)) + "'")
    
    def clean_Continuations(self) :
        """
        ** alias for remove_Restart() ** 
        removes ALL the simulations from the restart list.
        equivalent to :
            .remove_Restart('--ALL')
        """
        self.remove_Continuation(SimResultObject='--ALL')
    def clean_Continuation(self) :
        """
        ** alias for remove_Restart() ** 
        removes ALL the simulations from the restart list.
        equivalent to :
            .remove_Restart('--ALL')
        """
        self.remove_Continuation(SimResultObject='--ALL')
    def remove_Continuations(self,SimResultObject='--ALL') :
        """
        ** alias for remove_Restart() ** 
        removes ALL the simulations from the restart list.
        equivalent to :
            .remove_Restart('--ALL')
        """
        self.remove_Continuation(self,SimResultObject='--ALL') 
    def remove_Continuation(self,SimResultObject='--ALL') :
        """
        removes ALL the simulations from the continuation list.
        equivalent to :
            .remove_Continuation('--ALL')
        """
        if SimResultObject == '--ALL' :
            if len(self.continuations) == 0 :
                print(" nothing to remove, no continuation objects defined")
            else :
                print(" removed ALL the continuation objects (" + str(len(self.restarts)) + " objects removed)" )
                self.restarts = []
                
        if SimResultObject in self.restarts :
            print(" removed continuation object '" + str(self.restarts.pop(SimResultObject)) + "'")
    
    def get_Restarts(self):
        return self.get_Restart()
    def get_Restart(self):
        if self.speak in ( -1, 1 ) :
            if len( self.restarts ) > 0 :
                string = "\n '" + self.get_Name() + "' restarts from " 
                for r in range(len(self.restarts)-1,-1,-1) :
                    string = string + "\n   ◄'" + self.restarts[r].get_Name() + "'"
                    if len( self.restarts[r].restarts ) > 0 :
                        string += self.restarts[r].print_RecursiveRestarts(1)
                    if len( self.restarts[r].continuations ) > 0 :
                        string += self.restarts[r].print_RecursiveContinuations(1)
                print( string )
        return self.restarts
    
    def get_Continuations(self):
        return self.get_Restart()
    def get_Continuation(self):
        if self.speak in ( -1, 1 ) :
            if len( self.continuations ) > 0 :
                string = "\n '" + self.get_Name() + "' continues to " 
                for r in range(len(self.continuations)) :
                    string = string + "\n   ►'" + self.continuations[r].get_Name() + "'"
                    if len( self.continuations[r].continuations ) > 0 :
                        string += self.continuations[r].print_RecursiveContinuations(1)
                    if len( self.continuations[r].restarts ) > 0 :
                        string += self.continuations[r].print_RecursiveRestarts(1)
                print( string )
        return self.continuations
    
    def get_RecursiveRestarts(self):
        if len( self.restarts ) == 0 :
            return self.restarts
        else :
            restarts = []
            for R in self.restarts :
                if len( R.restarts ) == 0 :
                    restarts.append ( [ R ] )
                else :
                    restarts.append( [ R , R.get_RecursiveRestarts() ] )
            return restarts
    
    def get_RecursiveContinuations(self):
        if len( self.continuations ) == 0 :
            return self.continuations
        else :
            continuations = []
            for C in self.continuations :
                if len( C.continuations ) == 0 :
                    continuations.append ( [ C ] )
                else :
                    continuations.append( [ C , C.get_RecursiveContinuations() ] )
            return continuations
    
    def print_RecursiveContinuations(self,ite=0):
        if len( self.continuations ) == 0 :
            return ''
        else :
            string = ''
            for C in self.continuations :
                string = string + "\n" + "   "*ite + "   "+u"\U0001F6C7"+"►'" + C.get_Name() + "'"
                string += C.print_RecursiveContinuations(ite+1)
            return string
    
    def print_RecursiveRestarts(self,ite=0) :
        if len( self.restarts ) == 0 :
            return ''
        else :
            string = ''
            for R in self.restarts[::-1] :
                string = string + "\n" + "   "*ite + "   "+u"\U0001F6C7"+"◄'" + R.get_Name() + "'"
                string += R.print_RecursiveRestarts(ite+1)
            return string
    
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
            elif mainKey(Key) in self.keyColors :
                return self.keyColors[mainKey(Key)]
            else :
                return None
        elif Key in self.attributes :
            return self.keyColors[Key]


    def set_Verbosity(self,verbosity_level):
        try :
            self.speak = int(verbosity_level)
        except :
            if type(verbosity_level) is str and verbosity_level.upper() == 'ALL' :
                print('Verbosity set to ALL (-1), EVERY message wil be printed.')
                self.speak = -1
            elif type(verbosity_level) is str and verbosity_level.upper() == 'MUTE' :
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
        reload = bool(reload)
        if len(list(self.attributes.keys())) == 0 or reload is True :
            props = []
            for each in self.get_Keys() :
                if ':' in each :
                    attr = mainKey(each)
                    if attr in self.attributes :
                        if type(self.attributes[ attr ]) is list :
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
                    props.append( mainKey(each) )
                else :
                    props.append( each.strip() )
            return tuple(set(props))


    def get_AttributesDict(self,reload=False) :
        reload = bool(reload)
        if reload is True :
            self.get_Attributes(None,True)
        return self.attributes


    def get_KeysFromAttribute(self,Attribute) :
        """
        returns a list of Keys for the given attribute
        """
        if self.is_Key( Attribute ) :
            return Attribute
        if self.is_Attribute( Attribute ) :
            return self.attributes[ Attribute ]


    def add_Key(self,Key) :
        if type(Key) is str :
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
        reload = bool(reload)
        
        if pattern is not None and type( pattern ) is not str :
            raise TypeError('pattern argument must be a string.')    
    
        if len(self.regions) == 0 or reload is True :
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
        reload = bool(reload)
        
        if pattern is not None and type( pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        
        if len(self.wells) == 0 or reload is True :
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
        reload = bool(reload)
        
        if pattern is not None and type( pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        
        if len(self.groups) == 0 or reload is True :
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
        reload = bool(reload)
        
        if pattern is not None and type( pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        
        if len(self.keys) == 0 or reload is True :
            self.keys = self.list_Keys() 

        if pattern is None :
            return self.keys
        else:
            return tuple( fnmatch.filter( self.keys , pattern ) )


    def get_Filter(self) :
        return self.filter['filter']

    def reset_Filter(self) :
        if self.filter['reset'] :
            if self.filter['key'] == [None] and self.filter['condition'] == [None] and self.filter['min'] == [None] and self.filter['max'] == [None] :
                pass
            else :
                self.filter = {'key':[None],'min':[None],'max':[None],'condition':[None],'filter':None,'reset':True,'incremental':[None],'operation':[None]}
                verbose(self.speak , 2 , " << filter reset >>")
            return True
        else :
            self.filter['reset'] = True
            return False


    def undo_Filter(self) :
        if self.filterUndo is None :
            verbose(self.speak , -1 , " << not possible to revert last set_Filter operation or already reverted >>")
            return False
        else :
            self.filter['filter'] = self.filterUndo
            for each in ['key','min','max','condition'] :
                self.filter[each] = self.filter[each][:-1]
            verbose(self.speak , -1 , " << last set_Filter has been reverted,\n filter set to previous version >>")
            self.filterUndo = None
            return True


    def redo_Filter(self) :
        redo = self.filter.copy()
        self.reset_Filter()
        for i in range(len(redo['key'])) :
            if redo['key'][i] is None and redo['condition'][i] is None and redo['min'][i] is None and redo['max'][i] is None :
                verbose( self.speak , 1 , " <redo_Filter> skipping empty filter...")
            else :
                Key = redo['key'][i]
                Condition = redo['condition'][i]
                Min = redo['min'][i]
                Max = redo['max'][i]
                Incremental = redo['incremental'][i]
                Operation = redo['operation'][i]
                filterStr = []
                if Key is not None :
                    filterStr += ["Key='"+str(Key)+"'"]                    
                if Condition is not None :
                    filterStr += ["Condition='"+str(Condition)+"'"]
                if Min is not None :
                    filterStr += ["Min='"+str(Min)+"'"]
                if Max is not None :
                    filterStr += ["Min='"+str(Max)+"'"]
                filterStr = ', '.join(filterStr) + ", IncrementalFilter="+str(Incremental)+", FilterOperation='"+str(Operation)+"'"
                verbose( self.speak , 2 , " <redo_Filter> applying filter: " + filterStr )
                self.set_Filter( Key=Key , Condition=Condition , Min=Min , Max=Max , IncrementalFilter=Incremental , FilterOperation=Operation  )


    def set_Filter(self,Key=None,Condition=None,Min=None,Max=None,Filter=None,IncrementalFilter=True,FilterOperation=None) :
        # support function to validate date string
        def MightBeDate(string) :
            if isDate(string) :
                return ''
            else :
                for DateType in [ ['DD','MM','YY'] , ['DD','MM','YYYY'] ] :
                    for sep in ['/', '-' , ' ' , '\t', '_', ':', ';', '#', "'"] :
                        formatStr = sep.join(DateType)
                        if isDate(string,formatIN=formatStr) :
                            return formatStr
            return False
        
        # convert the string to numpy date
        def toNumpyDate(DateString) :
            DateFormat = str(MightBeDate(DateString))
            try :
                return np.datetime64( pd.to_datetime( strDate( DateString , DateFormat , speak=False ) ) )
            except :
                raise TypeError(" a string must represent a date, better if is formatted like DD-MMM-YYYY")
        
        # check if aditional conditions waiting to be applied
        def ContinueFiltering(Key,Condition,Min,Max,Filter,Operation) :
            if Condition is None and Min is None and Max is None and Filter is None :
                self.filter['reset'] = True
                self.set_FieldTime()
                return True
            else :
                self.filter['reset'] = False
                return self.set_Filter(Key=Key,Condition=Condition,Min=Min,Max=Max,Filter=Filter,IncrementalFilter=True,FilterOperation=Operation)
        
        # apply the Filter
        def applyFilter( NewFilter , CurrentFilter=None ) :
            if CurrentFilter is not None :
                self.filter['filter'] = CurrentFilter
                self.filterUndo = CurrentFilter.copy()
            if Incremental :
                if Operation == '*' :
                    self.filter['filter'] = NewFilter * self.filter['filter']
                else : 
                    self.filter['filter'] = NewFilter + self.filter['filter']
            else :
                self.filter['filter'] = NewFilter
            if True not in self.filter['filter'] :
                verbose( self.speak , -1 , "\n***IMPORTANT*****IMPORTANT*****IMPORTANT*****IMPORTANT*****"+\
                                           "\n The new filter will result in empty vectors." +\
                                           "\n Nothing will be following plots, dataframes or vectors." +\
                                           "\n To restore previous filter call the method .undo_Filter()\n")
        
        # apply a Condition 
        def applyCondition( Left, Mid , Right ) :
            if Right is None :
                if Left in ['>=','<=','==','!=','>','<'] :
                    if isnumeric(Mid) :
                        applyCondition( Key , Left , Mid )
                    elif self.isKey(Mid):
                        applyCondition( Key , Left , Mid )
                    else :
                        raise TypeError(" the Condition is not correct: '" + Key+Left+Mid + "'")
                if Mid in ['>=','<=','==','!=','>','<'] :
                    if isnumeric(Left) :
                        applyCondition( Left , Mid , Key )
                    elif self.isKey(Left):
                        applyCondition( Left , Mid , Key )
                    else :
                        raise TypeError(" the Condition is not correct: '" + Left+Mid+Key + "'")
            else :
                # check Left parameter
                if self.is_Key(Left) :
                    Left = self.get_Vector(Left)[Left]
                elif isnumeric(Left) :
                    Left = float(Left)
                elif MightBeDate(Left) != False :
                    Left = toNumpyDate(Left)
                    if self.is_Key(Right) and type( self.get_Vector(Right)[Right][0] ) is not np.datetime64 :
                        raise TypeError(" if condition compares to a date, the Key must be DATE or date kind ")
                else :
                    raise TypeError(" the condition should be composed by Keys, conditions, numbers or dates ")
                # check Right parameter
                if self.is_Key(Right) :
                    Right = self.get_Vector(Right)[Right]
                elif isnumeric(Right) :
                    Right = float(Right)
                elif MightBeDate(Right) != False :
                    Right = toNumpyDate(Right)
                    if type( Left[0] ) is not np.datetime64 :
                        raise TypeError(" if condition compares to a date, the Key must be DATE or date kind ")
                else :
                    raise TypeError(" the condition should be composed by Keys, conditions, numbers or dates ")
                # check Mid parameter
                if Mid not in ['>=','<=','==','!=','>','<'] :
                    raise TypeError(" the condition should be composed by Keys, conditions, numbers or dates ")
                if Mid == '>=' :
                    return Left >= Right
                if Mid == '<=' :
                    return Left <= Right
                if Mid == '==' :
                    return Left == Right
                if Mid == '!=' :
                    return Left != Right
                if Mid == '>' :
                    return Left > Right
                if Mid == '<' :
                    return Left < Right
                
        
        # start of main function, setting parameters
        DateFormat = '' # set default date string format
        
        Incremental = bool(IncrementalFilter) # move parameter to internal variable
        if IncrementalFilter and self.filter['filter'] is None :
            Incremental = False # if IncrementalFilter is True but previous filter is None, there is nothing to "increment"
        
        
        # verify Filter operation is AND or * or OR or +
        if type(FilterOperation) is str and FilterOperation.lower() in ['+','or'] :
            Operation = '+' # OR operation
        else :
            Operation = '*' # AND is the default operation
            
        # APPLY or calculate the Filter
        if Filter is not None : # apply it if Filter parameter is provided
            if type(Filter) is list or type(Filter) is tuple :
                Filter = np.array(Filter) # convert to numpy array
            if type(Filter) is np.ndarray : 
                if len(Filter) == len(self.fieldtime[2]) : # check Filter has the proper length
                    if Filter.dtype == 'bool' : # check it has the correct dtype
                        applyFilter( Filter )
                        self.filter['key'].append(None)
                        self.filter['min'].append(None)
                        self.filter['max'].append(None)
                        self.filter['condition'].append(None)
                        self.filter['incremental'].append(IncrementalFilter)
                        self.filter['operation'].append(FilterOperation)
                        return ContinueFiltering(Key=Key,Condition=Condition,Min=Min,Max=Max,Filter=None,Operation=Operation)
                    else :
                        try:
                            Filter = Filter.astype('bool')
                            # corrected the filter, apply it
                            return ContinueFiltering(Key=Key,Condition=Condition,Min=Min,Max=Max,Filter=None,Operation=Operation)
                        except:
                            verbose(self.speak , 3 , " the 'Filter' must be an array of dtype 'bool'")
                            return False

                else : # filter is not correct
                    verbose(self.speak , 3 , " the 'Filter' must have the exact same length of the simulation vectors: " + str(len(self.fieldtime[2])) )
                    return False
                
        # apply or CALCULATE the Filter     
        else : # calculate the filter
            if Key is None and Condition is None and Min is None and Max is None :
                # no arguments provided, means reset
                return self.reset_Filter() 
            
            elif Key is None : # Key is not provided
                # take previous Key  
                if self.filter['key'][-1] is not None : 
                    if ( type(Min) is str and MightBeDate(Min) != False ) or ( type(Max) is str and MightBeDate(Max) != False ) :
                        if type( self.get_Vector(self.filter['key'][-1])[self.filter['key'][-1]][0] ) is np.datetime64 :
                            Key = self.filter['key'][-1] # previous Key is DATE kind and Min or Max are dates
                        else :
                            Key = 'DATE' # Min or Max are dates but previos Key is not DATE kind, set proper Key for this Min or Max
                    else :  # take the previous Key
                        Key = self.filter['key'][-1]
                
                # no previous Key
                elif ( type(Min) is str and MightBeDate(Min) != False ) or ( type(Max) is str and MightBeDate(Max) != False ) :
                    # Min or Max are DATE strings, set Key accordingly
                    Key = 'DATE'
                
                # the Key might be inside the Condition
                elif Condition is not None :
                    pass # check later
                
                # if Key is a numpy.array or a list, it could be a filter
                elif type(Key) is list or type(Key) is tuple or type(Filter) is np.ndarray :
                    if len(Key) == len(self.fieldtime[2]) : # it looks like a Filter
                        verbose( self.speak , 1 , ' a Filter was received')
                        return ContinueFiltering(Key=None,Condition=Condition,Min=Min,Max=Max,Filter=Key,Operation=Operation)
                
                # missing Key
                else :
                    verbose(self.speak , 2 , ' no Filter or Key received.')
                    return False
            
            # ckeck the received is valid:
            elif not self.is_Key(Key) :
                # the Key is a not in the simulation, might be a Condition string
                if Condition is None : # there is no Condition argument provided
                    for cond in ['<','>','<=','>=','!=','==','=','<>','><'] : # check for conditional strings
                        if cond in Key :
                            verbose( self.speak , 1 , ' a Condition was received')
                            return ContinueFiltering(Key=None,Condition=Key,Min=Min,Max=Max,Filter=Filter,Operation=Operation)
                else :
                    raise KeyError(" the argument Key: '" + str(Key) + "' is not a key in this simulation")

            
            # calculate the NewFilter
            
            if Incremental : # if Incremental is True, keep the current Filter for new calculations
                FilterArray = self.filter['filter']
            else : # if Incremental is False, create a new array
                FilterArray = np.array([True]*len(self.fieldtime[2]))
            # temporarily deactivate current filter
            self.filter['filter'] = None 
            
            
            # previous = self.filter.copy()
            # self.filter = {'key':None,'min':None,'max':None,'condition':None,'filter':None,'reset':True}
            
                
            if Min is not None : # apply Min parameter
                if type(Min) is int or type(Min) is float :
                    # Min is a number
                    
                    # check consistency with Max parameter
                    if Max is None :
                        pass # is OK
                    elif type(Max) is int or type(Max) is float :
                        pass # OK
                    else : # Max is not number
                        verbose(self.speak , 3 , " the parameter 'Min' is a number: " + str(Min) + "\n then 'Max' must be also a number.")
                        # raise TypeError(" if Min is a number, Max must be a number also.")
                        return False
                    
                    # calculate and apply filter
                    KeyArray = self.get_Vector(Key)[Key]
                    applyFilter( KeyArray >= Min , FilterArray )
                    self.filter['key'].append(Key)
                    self.filter['min'].append(Min)
                    self.filter['max'].append(None)
                    self.filter['condition'].append(None)
                    self.filter['incremental'].append(IncrementalFilter)
                    self.filter['operation'].append(FilterOperation)
                    
                    if FilterOperation is None :
                        if Condition is None :
                            if ( type(Max) is int or type(Max) is float ) and Min > Max :
                                return ContinueFiltering(Key=Key,Condition=Condition,Min=None,Max=Max,Filter=Filter,Operation='+')
                        else :
                            pass # to implement later
                    return ContinueFiltering(Key=Key,Condition=Condition,Min=None,Max=Max,Filter=Filter,Operation=Operation)

                if type(Min) is str :
                    # Min a string, might be a date
                    DateFormat = str(MightBeDate(Min))
                    try :
                        Min = np.datetime64( pd.to_datetime( strDate( Min , DateFormat , speak=(self.speak==1 or DateFormat=='') ) ) )
                        if DateFormat != '' :
                            verbose(self.speak , 2 , " the 'Min' date format is " + DateFormat)
                    except :
                        verbose(self.speak , 3 , " if the 'Min' is string it must represent a date, better if is formatted like DD-MMM-YYYY")
                        return False
                    
                if type(Min) is np.datetime64 :
                    # Min is a date
                    
                    # check consistency with Max parameter
                    if Max is None :
                        pass # is OK
                    elif type(Max) is str :
                        DateFormat = str(MightBeDate(Max))
                        try :
                            Max = np.datetime64( pd.to_datetime( strDate( Max , DateFormat , speak=(self.speak==1 or DateFormat=='') ) ) )
                        except :
                            verbose(self.speak , 3 , " the parameter 'Min' is represents a date: " + strDate(Min,DateFormat,speak=False) + "\n then 'Max' should be a valid date.")
                            # raise TypeError(" if Min is a date, Max must be a date also.")
                            return False
                    else : # Max is not None and is not a date string
                        verbose(self.speak , 3 , " the parameter 'Min' is represents a date: " + strDate(Min,DateFormat,speak=False) + "\n then 'Max' must be also a date.")
                        # raise TypeError(" if Min is a date, Max must be a date also.")
                        return False
                    
                    # calculate and apply filter
                    KeyArray = self.get_Vector(Key)[Key]
                    applyFilter( KeyArray >= Min , FilterArray )
                    self.filter['key'].append(Key)
                    self.filter['min'].append(Min)
                    self.filter['max'].append(None)
                    self.filter['condition'].append(None)
                    self.filter['incremental'].append(IncrementalFilter)
                    self.filter['operation'].append(FilterOperation)
                    
                    if FilterOperation is None :
                        if type(Max) is np.datetime64 and Min > Max :
                            return ContinueFiltering(Key=Key,Condition=Condition,Min=None,Max=Max,Filter=Filter,Operation='+')
                    return ContinueFiltering(Key=Key,Condition=Condition,Min=None,Max=Max,Filter=Filter,Operation=Operation)

                    
                else : # not proper type of Min
                    verbose(self.speak , 3 , " the 'Min' value for the filter must be integer, float or date")
                    return False
            
            if Max is not None : # apply Max parameter
                if type(Max) is int or type(Max) is float :
                    # Min is a number
                    
                    # calculate and apply filter
                    KeyArray = self.get_Vector(Key)[Key]
                    applyFilter( KeyArray <= Max , FilterArray )

                    self.filter['key'].append(Key)
                    self.filter['min'].append(None)
                    self.filter['max'].append(Max)
                    self.filter['condition'].append(None)
                    self.filter['incremental'].append(IncrementalFilter)
                    self.filter['operation'].append(FilterOperation)
                    
                    return ContinueFiltering(Key=Key,Condition=Condition,Min=Min,Max=None,Filter=Filter,Operation=Operation)
                    
                if type(Max) is str :
                    # Max a string, might be a date
                    DateFormat = str(MightBeDate(Max))
                    try :
                        Max = np.datetime64( pd.to_datetime( strDate( Max , DateFormat , speak=(self.speak==1 or DateFormat=='') ) ) )
                        if DateFormat != '' :
                            verbose(self.speak , 2 , " the 'Max' date format is " + DateFormat)
                    except :
                        verbose(self.speak , 3 , " if the 'Max' is string it must represent a date, better if is formatted like DD-MMM-YYYY")
                        return False
                    
                if type(Max) is np.datetime64 :
                    # Max is a date
                    
                    # calculate and apply filter
                    KeyArray = self.get_Vector(Key)[Key]
                    applyFilter( KeyArray <= Max , FilterArray )
                    self.filter['key'].append(Key)
                    self.filter['min'].append(None)
                    self.filter['max'].append(Max)
                    self.filter['condition'].append(None)
                    self.filter['incremental'].append(IncrementalFilter)
                    self.filter['operation'].append(FilterOperation)
                    
                    return ContinueFiltering(Key=Key,Condition=Condition,Min=Min,Max=None,Filter=Filter,Operation=Operation)

                else : # not proper type of Max
                    verbose(self.speak , 3 , " the 'Max' value for the filter must be integer or float")
                    return False
                    
            if Condition is not None : # apply Condition parameter
                if type(Condition) is str :
                    NewCondition = ''
                    for cond in ['<>','><'] : # check common mistakes
                        if cond in Condition :
                            verbose( self.speak , -1 , " I've saved your life this time, but keep in mind that the inequality check in python is '!=' and not '" + cond + "'")
                            NewCondition = Condition.replace(cond,'!=')
                    for cond in ['=>','=<'] : # check common mistakes
                        if cond in Condition :
                            verbose( self.speak , -1 , " I've saved your life this time, but keep in mind that the '" + cond + "' is not the correct sintax in Python for '" + cond[::-1] + "'")
                            NewCondition = Condition.replace(cond,cond[::-1])
                    for c in range(1, len(Condition)-1) :
                        if Condition[c] == '=' :
                            if Condition[c+1] == '=' or Condition[c-1] == '=' :
                                pass # means ==
                            elif Condition[c-1] == '!' :
                                pass # means !=
                            elif Condition[c-1] == '>' :
                                pass # means >=
                            elif Condition[c-1] == '<' :
                                pass # means <=
                            else :
                                verbose( self.speak , -1 , " I've saved your life this time, but keep in mind that the equality check in python is '==' and not '='")
                                NewCondition = Condition[:c]+'='+Condition[c:]
                    if NewCondition != '' :
                        verbose( self.speak , 2 , "\n the received condition was: '" + Condition + "'" + \
                                                  "\n the corrected condition in: '" + NewCondition + "'"  )
                        Condition = NewCondition
                    found=[]
                    for cond in ['>=','<=','==','!='] :
                        if cond in Condition :                               
                            found.append(cond)
                    for c in range(len(Condition)-1) :
                        if Condition[c] in ['<','>'] :
                            if Condition[c+1] != '=' :
                                found.append(Condition[c])
                    CondList=multisplit(Condition,found)

                    if len(CondList) < 2 :
                        verbose( self.speak , 3 , " the Condition parameter is not correct: '" + Condition + "'")
                        return False
                    if len(CondList) == 2 :
                        CondFilter = applyCondition( CondList[0] , CondList[1] , None )
                        applyFilter( CondFilter , FilterArray )
                        self.filter['key'].append(Key)
                        self.filter['min'].append(None)
                        self.filter['max'].append(None)
                        self.filter['condition'].append(Condition)
                        self.filter['incremental'].append(IncrementalFilter)
                        self.filter['operation'].append(FilterOperation)
                        self.filter['reset'] = True
                        self.set_FieldTime()
                        return True
                    if len(CondList) == 3 :
                        CondFilter = applyCondition( CondList[0] , CondList[1] , CondList[2] )
                        applyFilter( CondFilter , FilterArray )
                        self.filter['key'].append(Key)
                        self.filter['min'].append(None)
                        self.filter['max'].append(None)
                        self.filter['condition'].append(Condition)
                        self.filter['incremental'].append(IncrementalFilter)
                        self.filter['operation'].append(FilterOperation)
                        self.filter['reset'] = True
                        self.set_FieldTime()
                        return True
                    if len(CondList) == 5 :
                        if ( '<' in CondList[1] and '<' in CondList[3] ) and ( CondList[0] <= CondList[2] ):
                            CondOperation = '*'
                        elif ( '>' in CondList[1] and '>' in CondList[3] ) and ( CondList[0] >= CondList[2] ):
                            CondOperation = '*'
                        elif ( '<' in CondList[1] and '!=' in CondList[3] ) and ( CondList[0] <= CondList[2] ):
                            CondOperation = '*'
                        elif ( '!=' in CondList[1] and '>' in CondList[3] ) and ( CondList[0] >= CondList[2] ):
                            CondOperation = '*'
                        else :
                            CondOperation = '+'
                        CondFilter1 = applyCondition( CondList[0] , CondList[1] , CondList[2] ) 
                        CondFilter2 = applyCondition( CondList[2] , CondList[3] , CondList[4] ) 
                        
                        if type(CondFilter1) is np.ndarray and type(CondFilter2) is np.ndarray :
                            if CondOperation == '+' :
                                CondFilter = CondFilter1 + CondFilter2
                            else :
                                CondFilter = CondFilter1 * CondFilter2
                            applyFilter( CondFilter , FilterArray )
                            self.filter['key'].append(Key)
                            self.filter['min'].append(None)
                            self.filter['max'].append(None)
                            self.filter['condition'].append(Condition)
                            self.filter['incremental'].append(IncrementalFilter)
                            self.filter['operation'].append(FilterOperation)
                            self.filter['reset'] = True
                            self.set_FieldTime()
                            return True
                        else :
                            self.filter['reset'] = True
                            return False


    def get_Vectors(self,key=None,reload=False):
        return self.get_Vector(key,reload)
    def get_Vector(self,key=None,reload=False):
        """
        returns a dictionary with numpy vectors for the selected key(s)
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """

        returnVectors = self.get_UnfilteredVector(key,reload)
        
        if self.filter['filter'] is None :
            return returnVectors
        else :
            if self.filter['key'][-1] is not None :
                verbose( self.speak , 1 , " filter by key '" + self.filter['key'][-1] + "'")          
            for each in returnVectors :
                returnVectors[each] = returnVectors[each][self.filter['filter']]
            return returnVectors


    def get_VectorWithUnits(self,key=None,reload=False):
        """
        returns a dictionary with a tuple ( units , numpy vectors ) 
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        returnVectors = self.get_Vector(key=key,reload=reload)
        for key in returnVectors :
            returnVectors[key] = ( self.get_Unit(key) , returnVectors[key] )
        return returnVectors  


    # extract the raw vector, without apply filter and without restarts or continues
    def get_RawVector(self,key=None,reload=False):
        """
        returns a dictionary with numpy vectors for the selected key(s) ignoring:
            any applied filter
            any restarts
            any continuations
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        returnVectors = {}
        if self.results != None :
            if type(key) is str :
                returnVectors[key] = self.checkIfLoaded(key,reload)
            if type(key) is list or type(key) is tuple :
                listOfKeys = list(set(key))
                for each in listOfKeys :
                    returnVectors[each] = self.checkIfLoaded(each,reload)        
        return returnVectors


    def get_UnfilteredVector(self,key=None,reload=False):
        """
        returns a dictionary with numpy vectors for the selected key(s) 
        ignoring any applied filter
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        # check restarts
        restartDict = {}
        if len( self.get_Restart() ) > 0 :
            restartDict = self.checkRestarts(key,reload)
        
        # check continuations
        continuationDict = {}
        if len( self.get_Continuation() ) > 0 :
            continuationDict = self.checkContinuations(key,reload)
            
        # get vector for current simulation
        returnVectors = self.get_RawVector(key=key,reload=reload)
        
        if restartDict != {} and continuationDict != {} :
            # concatenate restarts + self + continuations
            for each in returnVectors :
                returnVectors[each] = np.concatenate( [ restartDict[each] , returnVectors[each] , continuationDict[each] ] )
        elif restartDict != {} :
            # concatenate restarts + self 
            for each in returnVectors :
                returnVectors[each] = np.concatenate( [ restartDict[each] , returnVectors[each] ] )
        elif continuationDict != {} :
            # concatenate self + continuations
            for each in returnVectors :
                returnVectors[each] = np.concatenate( [ returnVectors[each] , continuationDict[each] ] )
                
        return returnVectors
    
    
    def get_RawVectorWithUnits(self,key=None,reload=False):
        """
        returns a dictionary with a tuple ( units , numpy vectors ) 
        ignoring:
            any applied filter
            any restarts
            any continuations
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        returnVectors = self.get_RawVector(key=key,reload=reload)
        for key in returnVectors :
            returnVectors[key] = ( self.get_Unit(key) , returnVectors[key] )
        return returnVectors    


    # support functions for get_Vector:
    def checkRestarts(self,key=None,reload=False) :
        returnVectors = {}
        Rlist = self.restarts # + [ self ]
        if type(key) is str :
            key = [ key ]
            
        for K in key :
            VectorsList = []
            verbose( self.speak , 1 , " preparing key '" + str(K) + "'")
            for R in Rlist :
                try :
                    # try to extract the not-filtered vector from the simulation
                    Vector = R.get_RawVector(K)[K]
                    #Vector = R.get_UnfilteredVector(K)[K]
                    verbose( self.speak , 1 , "     reading from restart " + str(R) )
                except :
                    # if failed to extract, create a zeros vector of the 'TIME' size
                    Vector = np.zeros( len(R.get_RawVector(K)[K]) )
                    #Vector = np.zeros( len(R.get_UnfilteredVector(K)[K]) )
                    verbose( self.speak , 1 , "     filling with zeros for restart "+ str(R) )
                
                # apply filter
                verbose( self.speak , 1 , "          applying filter")
                Vector = Vector[ self.restartFilters[R] ]
                
                # concatenate vectors                
                if K in returnVectors :
                    verbose( self.speak , 1 , "          concatenating vectors")
                    returnVectors[K] = np.concatenate( [ returnVectors[K] , Vector ] )
                else :
                    verbose( self.speak , 1 , "          creating vector")
                    returnVectors[K] = Vector
            # returnVectors[K] = np.concatenate( [ returnVectors[K] , self.checkIfLoaded( K , False ) ] )
        
        # return returnVectors
        if self.filter['filter'] is None :
            return returnVectors
        else :
            if self.filter['key'][-1] is not None :
                verbose( self.speak , 1 , " filter by key '" + self.filter['key'][-1] + "'")          
            for each in returnVectors :
                returnVectors[each] = returnVectors[each][self.filter['filter']]
            return returnVectors


    def checkContinuations(self,key=None,reload=False) :
        returnVectors = {}
        Clist = self.continuations # + [ self ]
        if type(key) is str :
            key = [ key ]
            
        for K in key :
            VectorsList = []
            verbose( self.speak , 1 , " preparing key '" + str(K) + "'")
            for C in Clist :
                try :
                    # try to extract the not-filtered vector from the simulation
                    Vector = C.get_RawVector(K)[K]
                    verbose( self.speak , 1 , "     reading from restart " + str(C) )
                except :
                    # if failed to extract, create a zeros vector of the 'TIME' size
                    Vector = np.zeros( len(C.get_RawVector(K)[K]) )
                    verbose( self.speak , 1 , "     filling with zeros for restart "+ str(C) )
                
                # apply filter
                verbose( self.speak , 1 , "          applying filter")
                Vector = Vector[ self.continuationFilters[C] ]
                
                # concatenate vectors                
                if K in returnVectors :
                    verbose( self.speak , 1 , "          concatenating vectors")
                    returnVectors[K] = np.concatenate( [ returnVectors[K] , Vector ] )
                else :
                    verbose( self.speak , 1 , "          creating vector")
                    returnVectors[K] = Vector
            # returnVectors[K] = np.concatenate( [ self.checkIfLoaded( K , False ) , returnVectors[K] ] )
            
        # return returnVectors
        if self.filter['filter'] is None :
            return returnVectors
        else :
            if self.filter['key'][-1] is not None :
                verbose( self.speak , 1 , " filter by key '" + self.filter['key'][-1] + "'")          
            for each in returnVectors :
                returnVectors[each] = returnVectors[each][self.filter['filter']]
            return returnVectors


    def checkIfLoaded(self,key,reload) :
        """
        internal function to avoid reloading the same vector twice...
        """
        reload = bool(reload)
        verbose( self.speak , 1 , ' looking for key ' + str( key ) )
        if str(key).upper().strip() not in self.vectors or reload is True :
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
            if type(key) is str :
                returnVectors[key] = self.checkIfLoaded(key,reload)
            if type(key) is list or type(key) is tuple :
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
        
        if Key in self.vectors and overwrite is False :
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
            elif Units == 'DEGREES' and 'API' in mainKey(Key).upper() :
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
        if not self.is_Key(Key) :
            self.add_Key(Key) 
        self.get_Attributes(reload=True)
    
    def set_Overwrite(self,overwrite) :
        if type(overwrite) is bool :
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
            if self.is_Key('FLPR') is False or len( self.get_Vector('FLPR')['FLPR'] ) < len( self.get_Vector('FWPR')['FWPR'] ) or type(self.get_Vector('FLPR')['FLPR']) != np.ndarray :
                try :
                    self.set_Vector( 'FLPR' , np.array( self.get_Vector('FOPR')['FOPR'],dtype='float' ) + convertUnit( np.array( self.get_Vector('FWPR')['FWPR'],dtype='float' ) , self.get_Unit('FWPR') , self.get_Unit('FOPR') , PrintConversionPath=(self.speak==1) ) , self.get_Unit('FOPR') , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FLPR.')
            
            # calculated FWCT if not available:
            if self.is_Key('FWCT') is False or len( self.get_Vector('FWCT')['FWCT'] ) < len( self.get_Vector('FWPR')['FWPR'] ) or type(self.get_Vector('FWCT')['FWCT']) != np.ndarray :
                try :
                    Vector = np.array( np.divide(  np.array(self.get_Vector('FWPR')['FWPR'],dtype='float') , convertUnit( np.array( self.get_Vector('FLPR')['FLPR'],dtype='float' ) , self.get_Unit('FLPR') , self.get_Unit('FWPR') , PrintConversionPath=(self.speak==1) ) ) ,dtype='float') 
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FWCT' , Vector , 'FRACTION' , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FWCT.')
                    
            # calculated FWOR & FOWR if not available:
            if self.is_Key('FWOR') is False or len( self.get_Vector('FWOR')['FWOR'] ) < len( self.get_Vector('FWPR')['FWPR'] ) or type(self.get_Vector('FWOR')['FWOR']) != np.ndarray :
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
            if self.is_Key('FGOR') is False or len( self.get_Vector('FGOR')['FGOR'] ) < len( self.get_Vector('FOPR')['FOPR'] ) or type(self.get_Vector('FGOR')['FGOR']) != np.ndarray :
                try :
                    Vector = np.array( np.divide( np.array( self.get_Vector('FGPR')['FGPR'] , dtype='float' ) , np.array( self.get_Vector('FOPR')['FOPR'] , dtype='float' ) ) ,dtype='float')
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FGOR' ,  Vector  , self.get_Unit('FGPR').split('/')[0]+'/'+self.get_Unit('FOPR').split('/')[0] , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FGOR.')
        
        # calculated FOGR if not available:
        if type(self.get_Vector('FOPR')['FOPR']) == np.ndarray and type(self.get_Vector('FGPR')['FGPR']) == np.ndarray :
            if self.is_Key('FOGR') is False or len( self.get_Vector('FOGR')['FOGR'] ) < len( self.get_Vector('FOPR')['FOPR'] ) or type(self.get_Vector('FOGR')['FOGR']) != np.ndarray :
                try :
                    Vector = np.array( np.divide( np.array( self.get_Vector('FOPR')['FOPR'] , dtype='float' ) , np.array( self.get_Vector('FGPR')['FGPR'] , dtype='float' ) ) ,dtype='float')
                    Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    self.set_Vector( 'FOGR' , Vector , self.get_Unit('FOPR').split('/')[0]+'/'+self.get_Unit('FGPR').split('/')[0] , overwrite=True )
                except :
                    verbose( self.speak , 2 , 'failed to create missing vector FOGR.')
    
        if type(self.get_Vector('FOPT')['FOPT']) == np.ndarray and type(self.get_Vector('FWPT')['FWPT']) == np.ndarray :
            # calculated FLPR if not available:
            if self.is_Key('FLPT') is False or len( self.get_Vector('FLPT')['FLPT'] ) < len( self.get_Vector('FWPT')['FWPT'] ) or type(self.get_Vector('FLPT')['FLPT']) != np.ndarray :
                try :
                    self.set_Vector( 'FLPT' , np.array( self.get_Vector('FOPT')['FOPT'],dtype='float' ) + convertUnit( np.array( self.get_Vector('FWPT')['FWPT'],dtype='float' ), self.get_Unit('FWPT') , self.get_Unit('FOPT') , PrintConversionPath=(self.speak==1)) , self.get_Unit('FOPT') , overwrite=True )
                except :
                    try :
                        Name , Vector , Units = self.integrate( 'FLPR' , 'FLPT' )
                        self.set_Vector(Name,Vector,Units,'float',True)
                        verbose( self.speak , 2 , 'vector FLPT integrated from FLPR.')
                    except :
                        verbose( self.speak , 2 , 'failed to create missing vector FLPT.')
        
        if type(self.get_Vector('TIME')['TIME']) == np.ndarray :
            if self.is_Key('DATE') is False or len( self.get_Vector('DATE')['DATE'] ) < len( self.get_Vector('TIME')['TIME'] ) or type(self.get_Vector('DATE')['DATE']) != np.ndarray :
                self.createDATES()
            if self.is_Key('DATES') is False or len( self.get_Vector('DATES')['DATES'] ) < len( self.get_Vector('TIME')['TIME'] ) or type(self.get_Vector('DATES')['DATES']) != np.ndarray :
                self.createDATES()
        
        if type(self.get_Vector('DATE')['DATE']) == np.ndarray :
            for T in ['YEAR','MONTH','DAY'] :
                if self.is_Key(T) is False or len( self.get_Vector(T)[T] ) < len( self.get_Vector('DATE')['DATE'] ) or type(self.get_Vector(T)[T]) != np.ndarray :
                    if T == 'YEAR' :
                        self.createYEAR()
                    elif T == 'MONTH' :
                        self.createMONTH()
                    elif T == 'DAY' :
                        self.createDAY()
            
    
        np.seterr(divide=None, invalid=None)


    def fill_WellBasics(self) :
        np.seterr(divide='ignore', invalid='ignore')
        
        for well in list(self.get_Wells()) :
            if type(well) is str and len(well.strip()) > 0 :
                well = well.strip()
                verbose( self.speak , 2 , ' calculating basic ratios for the well ' + well )
                if type(self.get_Vector('WOPR:'+well)['WOPR:'+well]) == np.ndarray and type(self.get_Vector('WWPR:'+well)['WWPR:'+well]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key('WLPR:'+well) is False or len( self.get_Vector('WLPR:'+well)['WLPR:'+well] ) < len( self.get_Vector('WWPR:'+well)['WWPR:'+well] ) or type(self.get_Vector('WLPR:'+well)['WLPR:'+well]) != np.ndarray :
                        try :
                            self.set_Vector( 'WLPR:'+well , np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) + convertUnit( np.array( self.get_Vector('WWPR:'+well)['WWPR:'+well] , dtype='float' ) , self.get_Unit('WWPR:'+well) , self.get_Unit('WOPR:'+well) , PrintConversionPath=(self.speak==1)) , self.get_Unit('WOPR:'+well) , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WLPR:'+well)
                    
                    # calculated WWCT if not available:
                    if self.is_Key('WWCT:'+well) is False or len( self.get_Vector('WWCT:'+well)['WWCT:'+well] ) < len( self.get_Vector('WWPR:'+well)['WWPR:'+well] ) or type(self.get_Vector('WWCT:'+well)['WWCT:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WWPR:'+well)['WWPR:'+well] , dtype='float' ) , convertUnit( np.array(self.get_Vector('WLPR:'+well)['WLPR:'+well], dtype='float' ), self.get_Unit('WLPR:'+well) , self.get_Unit('WWPR:'+well) , PrintConversionPath=(self.speak==1)) ) , dtype='float' ) 
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WWCT' , Vector , 'FRACTION' , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WWCT:'+well)
                            
                    # calculated WWOR & WOWR if not available:
                    if self.is_Key('WWOR:'+well) is False or len( self.get_Vector('WWOR:'+well)['WWOR:'+well] ) < len( self.get_Vector('WWPR:'+well)['WWPR:'+well] ) or type(self.get_Vector('WWOR:'+well)['WWOR:'+well]) != np.ndarray :
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
                    if self.is_Key('WGOR:'+well) is False or len( self.get_Vector('WGOR:'+well)['WGOR:'+well] ) < len( self.get_Vector('WOPR:'+well)['WOPR:'+well] ) or type(self.get_Vector('WGOR:'+well)['WGOR:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WGPR:'+well)['WGPR:'+well] , dtype='float' ) , np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WGOR:'+well , Vector  , self.get_Unit('WGPR:'+well).split('/')[0]+'/'+self.get_Unit('WOPR:'+well).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WGOR:'+well)
                
                # calculated WOGR if not available:
                    if self.is_Key('WOGR:'+well) is False or len( self.get_Vector('WOGR:'+well)['WOGR:'+well] ) < len( self.get_Vector('WOPR:'+well)['WOPR:'+well] ) or type(self.get_Vector('WOGR:'+well)['WOGR:'+well]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector('WOPR:'+well)['WOPR:'+well] , dtype='float' ) , np.array( self.get_Vector('WGPR:'+well)['WGPR:'+well] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( 'WOGR:'+well , Vector , self.get_Unit('WOPR:'+well).split('/')[0]+'/'+self.get_Unit('WGPR:'+well).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector WOGR:'+well)
            
                if type(self.get_Vector('WOPT:'+well)['WOPT:'+well]) == np.ndarray and type(self.get_Vector('WWPT:'+well)['WWPT:'+well]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key('WLPT:'+well) is False or len( self.get_Vector('WLPT:'+well)['WLPT:'+well] ) < len( self.get_Vector('WWPT:'+well)['WWPT:'+well] ) or type(self.get_Vector('WLPT:'+well)['WLPT:'+well]) != np.ndarray :
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
        
        if type(ItemsNames) is str :
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
                
            if type(item) is str and len(item.strip()) > 0 :
                item = item.strip()
                verbose( self.speak , 2 , ' calculating basic ratios for the item ' + item )
                if type(self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item]) == np.ndarray and type(self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key(KT+'LPR'+item) is False or len( self.get_Vector(KT+'LPR'+item)[KT+'LPR'+item] ) < len( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] ) or type(self.get_Vector(KT+'LPR'+item)[KT+'LPR'+item]) != np.ndarray :
                        try :
                            self.set_Vector( KT+'LPR'+item , np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) + np.array( convertUnit(self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] , dtype='float' , PrintConversionPath=(self.speak==1)) , self.get_Unit(KT+'WPR'+item) , self.get_Unit(KT+'OPR'+item) ) , self.get_Unit(KT+'OPR'+item) , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'LPR'+item)
                    
                    # calculated WWCT if not available:
                    if self.is_Key(KT+'WCT'+item) is False or len( self.get_Vector(KT+'WCT'+item)[KT+'WCT'+item] ) < len( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] ) or type(self.get_Vector(KT+'WCT'+item)[KT+'WCT'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] , dtype='float' ) , np.array( convertUnit(self.get_Vector(KT+'LPR'+item)[KT+'LPR'+item], self.get_Unit(KT+'LPR'+item) , self.get_Unit(KT+'WPR'+item) , PrintConversionPath=(self.speak==1)) , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'WCT' , Vector , 'FRACTION' , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'WCT'+item)
                            
                    # calculated WWOR & WOWR if not available:
                    if self.is_Key(KT+'WOR'+item) is False or len( self.get_Vector(KT+'WOR'+item)[KT+'WOR'+item] ) < len( self.get_Vector(KT+'WPR'+item)[KT+'WPR'+item] ) or type(self.get_Vector(KT+'WOR'+item)[KT+'WOR'+item]) != np.ndarray :
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
                    if self.is_Key(KT+'GOR'+item) is False or len( self.get_Vector(KT+'GOR'+item)[KT+'GOR'+item] ) < len( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] ) or type(self.get_Vector(KT+'GOR'+item)[KT+'GOR'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'GPR'+item)[KT+'GPR'+item] , dtype='float' ) , np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'GOR'+item , Vector  , self.get_Unit(KT+'GPR'+item).split('/')[0]+'/'+self.get_Unit(KT+'OPR'+item).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'GOR'+item)
                
                # calculated WOGR if not available:
                    if self.is_Key(KT+'OGR'+item) is False or len( self.get_Vector(KT+'OGR'+item)[KT+'OGR'+item] ) < len( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] ) or type(self.get_Vector(KT+'OGR'+item)[KT+'OGR'+item]) != np.ndarray :
                        try :
                            Vector = np.array( np.divide( np.array( self.get_Vector(KT+'OPR'+item)[KT+'OPR'+item] , dtype='float' ) , np.array( self.get_Vector(KT+'GPR'+item)[KT+'GPR'+item] , dtype='float' ) ) ,dtype='float')
                            Vector = np.nan_to_num( Vector, nan=0.0 , posinf=0.0 , neginf=0.0 )
                            self.set_Vector( KT+'OGR'+item , Vector , self.get_Unit(KT+'OPR'+item).split('/')[0]+'/'+self.get_Unit(KT+'GPR'+item).split('/')[0] , overwrite=True )
                        except :
                            verbose( self.speak , 2 , 'failed to create missing vector '+KT+'OGR'+item)
            
                if type(self.get_Vector(KT+'OPT'+item)[KT+'OPT'+item]) == np.ndarray and type(self.get_Vector(KT+'WPT'+item)[KT+'WPT'+item]) == np.ndarray :
                    # calculated WLPR if not available:
                    if self.is_Key(KT+'LPT'+item) is False or len( self.get_Vector(KT+'LPT'+item)[KT+'LPT'+item] ) < len( self.get_Vector(KT+'WPT'+item)[KT+'WPT'+item] ) or type(self.get_Vector(KT+'LPT'+item)[KT+'LPT'+item]) != np.ndarray :
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


    def checkVectorLength(self,Key_or_Array) :
        """
        returns True if the length of the given array or Key corresponds
        with the length of the simulation Keys.
        """
        if self.is_Key('TIME') :
            Vlen = len(self('TIME'))
        elif len(self.keys) > 0 :
            Vlen = len( self( self.keys[0] ))
        else :
            verbose( self.speak , 3 , 'there are no Keys in this object.')
            return True
        
        if self.is_Key(Key_or_Array) :
            Key_or_Array = self(Key_or_Array)
        elif self.is_Attribute(Key_or_Array) :
            Key_or_Array = self[[Key_or_Array]]
            
        if len(Key_or_Array) == Vlen :
            return True
        else :
            return False


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
                if type(Req) is str :
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
                        if type( dictionaries.calculations[CalcKey][i] ) is str :
                            CalculationTuple = [ ClassKey + dictionaries.calculations[CalcKey][i] + ItemKey ]
                        else :
                            CalculationTuple = [ dictionaries.calculations[CalcKey][i] ]
                    else :
                        if type( dictionaries.calculations[CalcKey][i] ) is str :
                            CalculationTuple.append( [ ClassKey + dictionaries.calculations[CalcKey][i] + ItemKey ] )
                        else :
                            CalculationTuple.append( [ dictionaries.calculations[CalcKey][i] ] )
                
                return self.RPNcalculator( CalculationTuple , Key )


    def RPNcalculator(self,CalculationTuple,ResultName=None,ResultUnits=None) :
        """
        receives a tuple indicating the operation to perform and returns a vector
        with ResultName name 
        
        The CalculationTuple is a sequence of Vectors or Floats and operators:
        The syntax of the CalculationTuple follows the Reverser Polish Notation (RPN)
            ( 'operand' , 'operand' , 'operator' , 'operand' , 'operator' , ... 'operand' , 'operator' )
        
        The accepted operators are: '+' , '-' , '*' , '/' , '^'
        The CalculationTuple must start with a number or variable, never with an operator

        The operations will be executed in the exact order they are described. i.e.:
           ( 'FLPR' , '=' , 'FOPR' , 'FWPR' , '+' )
                means FLPR = FOPR + FWPR 
                will add FOPR plus FWPR
           ( 'WWCT:P1' , '=' , 'WOPR:P1' , 'WLPR:P1' , '/' ) 
                means WWCT:P1 = WOPR:P1 / WLPR:P1 
                will divide WOPR by WLPR of well P1
        but:
           ( 'R' , '=' , 'A' , 'B' , '-' , 'C' , '/' )
                means R = ( A - B ) / C
                will add A plus B and the result will be divided by C

            to represent R = A - B / C the correct sintax would be:
           ( 'R' , '=' , '-B' , 'C' , '/', 'A' , '+' ) 
                that means R = -B / C + A
                
        Special operators can be used with Attributes or DataFrames:
            'sum' will return the total of the all the columns
            'avg' or 'mean' will return the average of the all the columns
            'min' will return the minimum value of the all the columns at each tstep
            'max' will return the maximum value of the all the columns at each tstep
            'std' will return the stardard deviation the all the columns 
            
        To ignore 0 in these calculation, the variant of the operator
        with a '0' sufix can be used. i.e.:
            'sum0','avg0','mean0','min0','max0','std0'
            
            'avg0' or 'mean0' will return the average of the all the columns
            but ignoring the zeros in the data
        
        """
        # supported operators:
        operators = [' ','**','--','+-','++','*-','/-','=','+','-','*','/','^','sum','avg','mean','min','max','std','sum0','avg0','mean0','min0','max0','std0']
        
        # convert string to calculation tuple
        if type( CalculationTuple ) is str :
            verbose ( self.speak , 1 , ' the received string for CalculatedTuple was converted to tuple,\n  received: ' + CalculationTuple + '\n  converted to: ' + str( tuple( multisplit( CalculationTuple , operators ) ) ) )
            CalculationTuple = tuple ( multisplit( CalculationTuple , operators ) )
        elif type( CalculationTuple ) is list :
            CalculationTuple = tuple( CalculationTuple )
        if ResultName is None :
            if CalculationTuple[1] == '=' :
                ResultName = CalculationTuple[0]
                verbose ( self.speak , 1 , "found Key name '" + ResultName + "'")
                CalculationTuple = CalculationTuple[2:] 
            else :
                ResultName = str( CalculationTuple )
        
        # simplify equation
        CalculationTuple = list(CalculationTuple)
        while '--' in CalculationTuple :
            where = CalculationTuple.index('--')
            CalculationTuple[where] = '+'
        while '+-' in CalculationTuple :
            where = CalculationTuple.index('+-')
            CalculationTuple[where] = '-'
        while '++' in CalculationTuple :
            where = CalculationTuple.index('++')
            CalculationTuple[where] = '+'
        while '**' in CalculationTuple :
            where = CalculationTuple.index('**')
            CalculationTuple[where] = '^'
        while '*-' in CalculationTuple :
            where = CalculationTuple.index('*-')
            CalculationTuple[where] = '*'
            if (where+2) <= len(CalculationTuple) :
                CalculationTuple = CalculationTuple[:where] + [ CalculationTuple[where] ] + [ '-' + CalculationTuple[where+1] ] + CalculationTuple[where+2:]
            elif (where+1) <= len(CalculationTuple) :
                CalculationTuple = CalculationTuple[:where] + [ CalculationTuple[where] ] + [ '-' + CalculationTuple[where+1] ] 
        while '/-' in CalculationTuple :
            where = CalculationTuple.index('/-')
            CalculationTuple[where] = '/'
            if (where+2) <= len(CalculationTuple) :
                CalculationTuple = CalculationTuple[:where] + [ CalculationTuple[where] ] + [ '-' + CalculationTuple[where+1] ] + CalculationTuple[where+2:]
            elif (where+1) <= len(CalculationTuple) :
                CalculationTuple = CalculationTuple[:where] + [ CalculationTuple[where] ] + [ '-' + CalculationTuple[where+1] ] 
        
        while CalculationTuple[0] == '-' :
            if len(CalculationTuple) > 2 :
                CalculationTuple = [ '-' + CalculationTuple[1] ] + CalculationTuple[2:]
            else :
                CalculationTuple = [ '-' + CalculationTuple[1] ]
        
        while CalculationTuple[0] in ['*','+','/'] :
            verbose( self.speak , 2 , "the first item '" + CalculationTuple.pop(0) + "' is an operand and will ignored") 

        # convert numbers to float or int        
        for i in range(len(CalculationTuple)) :
            if isnumeric( CalculationTuple[i] ) :
                CalculationTuple[i] = getnumber( CalculationTuple[i] )
        
        CalculationTuple = tuple(CalculationTuple)
        verbose ( self.speak , 1 , "calculation simplified to " + str(CalculationTuple))
        
        
        operators = ['+','-','*','/','^','sum','avg','mean','min','max','std','sum0','avg0','mean0','min0','max0','std0']
        OK = True
        Missing = []
        WrongLen = []
        for Req in CalculationTuple :
            if type(Req) is str :
                if Req[0] == '-' and Req != '-' :
                    Req = Req[1:]
                if self.is_Key(Req) or self.is_Attribute(Req) :
                    # is a vector with values... OK
                    if not self.checkVectorLength( Req ) :
                        WrongLen.append(Req)
                        OK = False
                elif Req in operators :
                    # is an operand ... OK
                    pass
                else :
                    OK = False
                    Missing.append(Req)
            elif type(Req) is int or type(Req) is float :
                # is an int or float 
                pass
            elif type(Req) is np.ndarray :
                if not self.checkVectorLength( Req ) :
                    WrongLen.append(str(Req))
                    OK = False


        if not OK :
            if len(Missing) > 0 :
                verbose( self.speak , 3 , '\n IMPORTANT: the following required input vectors were not found:\n   -> ' + '\n   -> '.join(Missing) + '\n')
            if len(WrongLen) > 0 :
                verbose( self.speak , 3 , '\n IMPORTANT: the following input vectors does not have the correct length:\n   -> ' + '\n   -> '.join(WrongLen) + '\n')
            return { ResultName : None }
        
        
        # initialize calculation with first item
        i = 0
        if type( CalculationTuple[i] ) is str :               
            if CalculationTuple[i][0] == '-' :
                if self.is_Key( CalculationTuple[i][1:] ) :
                    Result = self(CalculationTuple[i][1:]) * -1
                elif self.is_Attribute( CalculationTuple[i][1:] ) :
                    Result = self[[CalculationTuple[i][1:]]] * -1
                Units = [ self.get_Unit( CalculationTuple[i][1:] ) ]
                    
            else :
                if self.is_Key( CalculationTuple[i] ) :
                    Result = self(CalculationTuple[i])
                elif self.is_Attribute( CalculationTuple[i] ) :
                    Result = self[[CalculationTuple[i]]]
                Units = [ self.get_Unit( CalculationTuple[i] ) ]
        else :
            Result = CalculationTuple[i]
            Units = [None]
        CalcUnit = Units[-1] # units 
        Next = Result.copy()
        NextUnit = Units[-1]
        i += 1
        
        while i < len( CalculationTuple ) :
            # following the operations sequence
            
            if i<len(CalculationTuple) and type( CalculationTuple[i] ) is str and CalculationTuple[i] not in operators :
                # extract the next array to apply calculations
                if CalculationTuple[i][0] == '-' :
                    if self.is_Key( CalculationTuple[i][1:] ) :
                        Next = self(CalculationTuple[i][1:]) * -1
                    elif self.is_Attribute( CalculationTuple[i][1:] ) :
                        Next = self[[CalculationTuple[i][1:]]] * -1
                        
                else :
                    if self.is_Key( CalculationTuple[i] ) :
                        Next = self(CalculationTuple[i])
                    elif self.is_Attribute( CalculationTuple[i] ) :
                        Next = self[[CalculationTuple[i]]]

                Units.append( self.get_Unit( CalculationTuple[i] ) )
                NextUnit = Units[-1] # units 
                i += 1 
            
            
            if i<len(CalculationTuple) and type( CalculationTuple[i] ) is str and CalculationTuple[i] in operators :
                # appliying calculation
                if CalculationTuple[i] == '+' :
                    if CalcUnit == NextUnit or NextUnit is None :
                        Result = Result + Next
                    elif convertibleUnits( NextUnit , CalcUnit) :
                        Result = Result + convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                    else :
                        CalcUnit = CalcUnit + '+' + NextUnit
                        Result = Result + Next
    
                elif CalculationTuple[i] == '-' :
                    if CalcUnit == NextUnit or NextUnit is None :
                        Result = Result - Next
                    elif convertibleUnits( NextUnit , CalcUnit) :
                        Result = Result - convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                    else :
                        CalcUnit = CalcUnit + '-' + NextUnit
                        Result = Result - Next
                        
                elif CalculationTuple[i] == '*' :
                    if CalcUnit == NextUnit or NextUnit is None :
                        Result = Result * Next
                    elif convertibleUnits( NextUnit , CalcUnit) :
                        Result = Result * convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1))
                    else :
                        CalcUnit = CalcUnit + '*' + NextUnit
                        Result = Result * Next
                    
                elif CalculationTuple[i] == '/' :
                    if CalcUnit == NextUnit or NextUnit is None :
                        Result = np.divide ( Result , Next )
                    elif convertibleUnits( NextUnit , CalcUnit) :
                        Result = np.divide ( Result , convertUnit(Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1)) )
                        
                    else :
                        CalcUnit = CalcUnit + '/' + NextUnit
                        Result = np.divide( Result , Next )
                    Result = np.nan_to_num( Result, nan=0.0 , posinf=0.0 , neginf=0.0 )
                    
                elif CalculationTuple[i] == '^' :
                    if CalcUnit == NextUnit or NextUnit is None :
                        Result = Result ** Next
                    elif convertibleUnits( NextUnit , CalcUnit) :
                        Result = Result ** convertUnit( Next, NextUnit , CalcUnit , PrintConversionPath=(self.speak==1) )
                    else :
                        CalcUnit = CalcUnit + '^' + NextUnit
                        Result = Result ** Next
                
                elif CalculationTuple[i] in ['sum','avg','mean','min','max','std','sum0','avg0','mean0','min0','max0','std0'] :
                    if type( Next ) is pd.core.frame.DataFrame :
                        if CalculationTuple[i][-1] == '0' : 
                            Next.replace(0,np.nan, inplace=True) #ignore zeros in the data
                            CalculationTuple[i] = CalculationTuple[i][:-1]
                        if CalculationTuple[i] == 'sum' :
                            Next = Next.sum(axis=1).to_numpy()
                        elif CalculationTuple[i] in ['avg','mean'] :
                            Next = Next.mean(axis=1).to_numpy()
                        elif CalculationTuple[i] == 'min' :
                            Next = Next.min(axis=1).to_numpy()
                        elif CalculationTuple[i] == 'max' :
                            Next = Next.max(axis=1).to_numpy()
                        elif CalculationTuple[i] == 'std' :
                            Next = Next.std(axis=1).to_numpy()
                        if i == 1 : 
                            Result = Next.copy()
                    else :
                        verbose( self.speak , 3 , 'the operator ' + CalculationTuple[i] + ' was ignored because the previous operand is not an Attribute or a DataFrame' )
                i += 1
                
                
            if i<len(CalculationTuple) and ( type( CalculationTuple[i] ) is np.ndarray or type( CalculationTuple[i] ) is int or type( CalculationTuple[i] ) is float ) :
                # numbers or arrays
                Next = CalculationTuple[i]
                Units.append(None)
                NextUnit = Units[-1] # units 
                i += 1

        # check resulting units
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
        
        # a name was given, link the data to the new name
        if ResultName != str( CalculationTuple ) :
            self.vectors[ResultName] = self.vectors[ str( CalculationTuple ) ]
            self.units[ResultName] = self.units[ str( CalculationTuple ) ]
            if not self.is_Key(ResultName) :
                self.add_Key(ResultName) 
            self.get_Attributes(reload=True)
            
        return { ResultName : Result }


    def createDATES(self) :
        TIME = self.get_Vector('TIME')['TIME']
        start = self.start
        DATE = np.empty(len(TIME), dtype='datetime64[s]')
        for i in range(len(TIME)) :
            DATE[i] = start + np.timedelta64( timedelta(days=TIME[i]) )
        self.set_Vector( 'DATES' , DATE , 'DATE' , overwrite=True )
        self.set_Vector( 'DATE' , DATE , 'DATE' , overwrite=True )

    def createYEAR(self) :
        Years = list(pd.to_datetime(self.get_Vector('DATE')['DATE']).year)
        self.set_Vector( 'YEAR' , Years , 'Year' , DataType='int' , overwrite=True) 

    def createMONTH(self) :
        Months = list(pd.to_datetime(self.get_Vector('DATE')['DATE']).month)
        self.set_Vector( 'MONTH' , Months , 'Month' , DataType='int' , overwrite=True) 

    def createDAY(self) :
        Days = list(pd.to_datetime(self.get_Vector('DATE')['DATE']).day)
        self.set_Vector( 'DAY' , Days , 'Day' , DataType='int' , overwrite=True) 


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
        if type(Key) is str :
            Key = [Key]
        elif type(Key) is list or type(Key) is tuple :
            pass
        if Key is None :
            return {}
        if OtherObject_or_NewUnits is None :
            return self.get_Vector(Key, False)

        ListOfUnits = False
        if type(OtherObject_or_NewUnits) is str :
            OtherObject_or_NewUnits = [OtherObject_or_NewUnits]
            ListOfUnits = True
        elif type(OtherObject_or_NewUnits) is list or type(OtherObject_or_NewUnits) is tuple :
            ListOfUnits = True
            
        if ListOfUnits is True and len(Key) != len(OtherObject_or_NewUnits) :
            raise TypeError( str(len(Key)) + ' resquested but ' + str(len(OtherObject_or_NewUnits)) + ' units provided.\n          Both should match order and number.' )
        elif ListOfUnits is True and len(Key) == len(OtherObject_or_NewUnits) :
            pass
        else :
            try :
                if OtherObject_or_NewUnits.SimResult is True :
                    errors = False
                    TempConversions = []
                    for each in Key :
                        if not OtherObject_or_NewUnits.is_Key(each) :
                            errors = True
                            verbose( self.speak , 3 , 'The requested Key ' + str(each) + ' is not present in the simulation ' + str(OtherObject_or_NewUnits.get_Name()) + '.')
                        else :
                            TempConversions.append( OtherObject_or_NewUnits.get_Unit( each.strip() ) )
                    if errors :
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
        verbose( self.speak , 1 , "<integrate> retrieved series '" + InputKey + "' of length " + str(len(Vector)) + ' and units ' + str(VectorUnits))
        Time = self.get_Vector( 'TIME' )[ 'TIME' ]
        TimeUnits = self.get_Unit('TIME')
        verbose( self.speak , 1 , "<integrate> retrieved series 'TIME' of length " + str(len(Time)) + ' and units ' + str(TimeUnits))
        
        Numpy = bool(Numpy)
        ConstantRate = bool(ConstantRate)
        
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
            raise TypeError( ' the Key vector ' + InputKey + ' and its TIME does not have the same length: ' + str( len(Vector) ) + ' != ' + str( len(Time) ) + '.' )
        
        if not Numpy :
            # integrating one row at a time, iterating with for:
            verbose( self.speak , 2 , "<integrate> calculating integral for key '" + InputKey + "' using for loor")
            Cumulative = [0.0]
            if not ConstantRate :
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
                    if type(X) is list or type(X) is tuple :
                        try :
                            X = np.array(X,dtype='float')
                        except :
                            print(" the key '" + X + "' is not numpy array.")
 
            dt = np.diff( Time ) * ConvFactor
            
            if not ConstantRate :
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
            verbose( self.speak , 2 , 'not able to save vector because the Key already exists.')
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
        if type(Keys) is str :
            if Keys == '--EVERYTHING--' :
                Keys = list( self.get_Keys() )
            else :
                Keys = [Keys]
        if type(Index) is list or type(Index) is tuple :
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
        if type(Keys) is str :
            if Keys == '--EVERYTHING--' :
                Keys = list( self.get_Keys() )
            else :
                Keys = [Keys]
        if type(Index) is list or type(Index) is tuple :
            if len(Index) > 1 :
                verbose( self.speak , -1 , '< get_DataFrame > more than value passed in Index argument, only the first one will be used')
            Index = Index[0]
        elif type(Index) is str :
            pass 
        else :
            try :
                if Index.SimResult is True :
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
            
    def to_RSM(self, RSMpath=None , RSMleng=12 , RSMcols=10 , ECLkeywordsOnly=True) :
        """
        writes all the vectors to an RSM format file
        """
        from decimal import Decimal
        def RSMunits(string) :
            RSMdict = {#'VIP unit' : [ 'ECL unit' , Multiplier , ShiftX , ShiftY ] -> ECLunit = ( ( VIP_unit + ShiftX ) * Multiplier ) + ShiftY
                    'FRACTION' : ['','',1,0,0] ,
                    'DIMENSIONLESS' : ['','',1,0,0] ,
                    'KPA' : ['BARSA','',0.01,0,0] ,
                    'STM3/KSM3' : ['SM3/SM3','',1000,0,0] ,
                   }
            notChange = ['KPA','K','KG','']
            dimless = ['DIMENSIONLESS','FRACTION','UNITLESS','NONE','None','RATIO',None]
            if string in RSMdict.keys() :
                return RSMdict[string]
            if string in notChange :
                return [string,'',1,0,0]
            if string in dimless :
                return ['','',1,0,0]
            if len(string) == 1 :
                return [string,'',1,0,0]

            string = string.replace('STM3','SM3')
            
            if string[0].upper() == 'K' :
                ret = [string[1:],'',1E3,0,0]
            elif string[0].upper() == 'M' :
                ret = [string[1:],'',1E6,0,0]
            elif string[0].upper() == 'G' :
                ret = [string[1:],'',1E9,0,0]
            else :
                ret = [string,'',1,0,0]
            
            return ret
        

        if type(RSMleng) is not int :
            raise TypeError("RSMleng must be an integer")
        if type(RSMcols) is not int :
            raise TypeError("RSMcols must be an integer")  
    
        print('\n...working on it: writing RSM file...')

        if RSMpath is None :
            RSMpath = extension(self.path)[1]
            for end in [ '_field' , '_well' , '_area' , '_flow' , '_gather' , '_region' ]:
                if RSMpath.endswith(end) :
                    RSMpath = RSMpath[:-len(end)]
                    break 
            RSMpath = extension(self.path)[0] + RSMpath + '.RSM'
        elif type(RSMpath) is str :
            if extension(RSMpath)[0].upper() != '.RSM' :
                RSMpath = extension(RSMpath)[1] + '.RSM'
            if extension(RSMpath)[2] == '' :
               RSMpath = extension(self.path)[2] + RSMpath
        RSMpath = extension(RSMpath)[3]

        
        RSMfile = open(RSMpath, 'w' )
        
        rsmOutput = self.name
        for end in [ '_field' , '_well' , '_area' , '_flow' , '_gather' , '_region' ]:
            if rsmOutput.endswith(end) :
                rsmOutput = rsmOutput[:-len(end)]
                break
        
        if ECLkeywordsOnly :
            CleanColumns = []
            for Key in self.keys :
                if isECLkey(Key , maxLen=RSMleng) :
                    CleanColumns.append(Key)
        else :
            CleanColumns = self.keys
            VIPcolLen = max(nplen(np.array(mainKey(self.keys))))
            if VIPcolLen > RSMleng :
                verbose( self.speak , 3 , "the lenght of the columns must be set to " + str(VIPcolLen) + " to fit key names." )
                RSMleng = VIPcolLen
        
        # check vectors are numeric
        NotValueVector = []
        for each in CleanColumns :
            print(each)
            if mainKey(each) in [ 'DATE' , 'DATES' , 'WNAME' ] :
                NotValueVector.append( each )
            elif itemKey(each) in [ 'DATE' , 'DATES' ] :
                NotValueVector.append( each )
            elif len(self(each)) == 0 :
                NotValueVector.append( each )
            elif not isnumeric( str(self(each)[0]) ) :
                NotValueVector.append( each )
        for each in NotValueVector :
            print(CleanColumns.pop( CleanColumns.index(each) ))

        # list of found regions
        try :
            REGIONS = self.regionNumber 
        except :
            REGIONS = {}
            for i in range(len(self.regions)) :
                REGIONS[self.regions[i]] = i+1
            
            
        cc = 0
        while cc < len(CleanColumns) :
            progressbar( cc/len(CleanColumns) )
            line = '\n\tSUMMARY OF RUN ' + rsmOutput + '\n'
            RSMfile.write(line)
        
            line1 = ' \tDATE        '
            line2 = ' \t            '
            line3 = ' \t            '
            line4 = ' \t            '
            line5 = ' \t            '
            unitMult = []
            unitSumY = []
            unitSumX = []
            
            for each in CleanColumns[ cc : cc+RSMcols-1 ] :
                print(each)
                if each in [ 'TIME' , 'DAY' , 'MONTH' , 'YEAR' , 'DATE' ] :
                    line1 = line1 + '\t' + each + ' ' * (RSMleng - len(each))
                elif itemKey(each) in [ 'TIME' , 'DAY' , 'MONTH' , 'YEAR' , 'DATE' ] :
                    # is a VIP style keyword
                    line1 = line1 + '\t' + itemKey(each) + ' ' * (RSMleng - len(itemKey(each)))
                else :
                    line1 = line1 + '\t' + mainKey(each) + ' ' * (RSMleng - len(mainKey(each)))
        

                CombiU = RSMunits( self.get_Units(each) )

                line2 = line2 + '\t'  + CombiU[0] + ' ' * (RSMleng - len(CombiU[0]))
                line3 = line3 + '\t' + CombiU[1] + ' ' * (RSMleng - len(CombiU[1]))
        
                unitMult.append(CombiU[2])
                unitSumY.append(CombiU[3])
                unitSumX.append(CombiU[4])
                
                if keyType(each) == 'FIELD' :
                    Combi0 = ''
                    CombiR=''
                elif keyType(each) == 'REGION' :
                    if itemKey(each) not in REGIONS.keys() :
                        REGIONS[ itemKey(each) ] = len(REGIONS) +1
                    CombiR = str( REGIONS[ itemKey(each) ] )
                    Combi0 = mainKey(each)
                else :
                    Combi0 = itemKey(each)
                    CombiR = ''
                if Combi0 is None :
                    Combi0 = ''
                if CombiR is None :
                    CombiR = ''
                line4 = line4 + '\t' + Combi0 + ' ' * (RSMleng - len(Combi0))
                line5 = line5 + '\t' + CombiR + ' ' * (RSMleng - len(CombiR))
            line1 = line1 + '\n'
            line2 = line2 + '\n'
            line3 = line3 + '\n'
            line4 = line4 + '\n'
            line5 = line5 + '\n'
            
            if len(line3.strip()) == 0 :
                line3 = line4
                line4 = line5
                line5 = ' \t            ' + ( ( '\t' + ( ' ' * RSMleng ) ) * (RSMcols - 1) ) + '\n'
            
            line = line1 + line2 + line3 + line4 + line5 # + '\n'
            RSMfile.write(line)
            
            fechas = strDate(self('DATES'),formatOUT='DD-MMM-YYYY')
            for f in range(len(fechas)) :
                line = '\t ' + fechas[f]
                unitN = 0
        
                for each in CleanColumns[ cc : cc+RSMcols-1 ] :      
                    #  the value
                    value = str( self(each)[f] )

                    if '.' in value :
                        if 'E' in value :
                            value = str( ( float(value) + unitSumX[unitN] ) * unitMult[unitN] + unitSumY[unitN] )
                        else :
                            value = str( (float(value) + unitSumX[unitN] ) * unitMult[unitN] + unitSumY[unitN] )
                    else :
                        value = str( (int(value) + unitSumX[unitN] ) * unitMult[unitN] + unitSumY[unitN] )
                        
                    if len(value) > RSMleng :
                        if len(str(int(float(value)))) <= RSMleng :
                            value = str(float(value))[:RSMleng]
                        else :
                            value = ('%.' + str(RSMleng - 6) + 'E') % Decimal(value)
    
                    # preparing and printing the line
                    if (RSMleng - len(value)) > 0 :
                        rept = ' ' * (RSMleng - len(value))
                    else :
                        rept = ''
                        
                    line = line + '\t' + rept + value

                    unitN += 1
        
                line = line + '\n'
                RSMfile.write(line)
        
            cc += RSMcols - 1
        
        RSMfile.close()
        print( "RMS file is completed, feel free to open it:\n\n '" + RSMpath + "'\n\nPlease wait for the report of the conversion to be finished." )