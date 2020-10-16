#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 11:14:32 2020

@author: martin
"""

__version__ = '0.5.20-10-14'

from io import StringIO
from shutil import get_terminal_size
from pandas._config import get_option
from pandas.io.formats import console

import fnmatch
import warnings
from pandas import Series , DataFrame , DatetimeIndex , Timestamp
import numpy as np
import datetime as dt

from bases.units import unit # to use unit.isUnit method
from bases.units import convertUnit, unitProduct, unitDivision
from bases.units import convertible as convertibleUnits

from datafiletoolbox import multisplit , isDate , date as strDate

_SERIES_WARNING_MSG = """\
    You are passing unitless data to the SimSeries constructor. Currently,
    it falls back to returning a pandas Series. But in the future, we will start
    to raise a TypeError instead."""

def _simseries_constructor_with_fallback(data=None, index=None, units=None, **kwargs):
    """
    A flexible constructor for SimSeries._constructor, which needs to be able
    to fall back to a Series (if a certain operation does not produce
    units)
    """
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=_SERIES_WARNING_MSG,
                category=FutureWarning,
                module="SimPandas[.*]",
            )
            return SimSeries(data=data, index=index, units=units, **kwargs)
    except TypeError:
        return Series(data=data, index=index, **kwargs)


def Series2Frame(aSimSeries) :
    """
    when a row is extracted from a DataFrame, Pandas returns a Series in wich
    the columns of the DataFrame are converted to the indexes of the Series and
    the extracted index from the DataFrame is set as the Name of the Series.
    
    This function returns the proper DataFrame view of such Series.
    
    Works with SimSeries as well as with Pandas standard Series 
    """
    if isinstance(aSimSeries,DataFrame) :
        return aSimSeries
    if type(aSimSeries) is SimSeries :
        try :
            return SimDataFrame( data=dict( zip( list(aSimSeries.index) , aSimSeries.to_list() ) ) , units=aSimSeries.get_Units() , index=[aSimSeries.name] , dtype=aSimSeries.dtype )
        except :
            return aSimSeries
    if type(aSimSeries) is Series :
        try :
            return DataFrame( data=dict( zip( list(aSimSeries.index) , aSimSeries.to_list() ) ) , index=[aSimSeries.name] , dtype=aSimSeries.dtype )
        except :
            return aSimSeries

class SimSeries(Series) :
    """
    A Series object designed to store data with units.

    Parameters
    ----------
    data : array-like, dict, scalar value
        The data to store in the SimSeries.
    index : array-like or Index
        The index for the SimSeries.
    units : string or dictionary of units (optional)
        Can be any string, but only units acepted by the UnitConverter will
        be considered when doing arithmetic calculations with other SimSeries 
        or SimDataFrames.

    kwargs
        Additional arguments passed to the Series constructor,
         e.g. ``name``.

    See Also
    --------
    SimDataFrame
    pandas.Series

    """
    
    _metadata = ["units","speak"]
    
    def __init__(self, data=None , units=None , index=None , speak=False , *args , **kwargs) :
        Uname = None
        Udict = None
        self.units = None
        self.speak = bool(speak)
        
        # validaton
        if isinstance(data,DataFrame) and len(data.columns)>1 :
            raise ValueError( "'data' paramanter can be an instance of DataFrame but must have only one column.")
        
        indexInput = None
        # catch index keyword from input parameters
        if index is not None :
            indexInput = index
        elif 'index' in kwargs and kwargs['index'] is not None :
            indexInput = kwargs['index']
        elif len(args) >= 3 and args[2] is not None :
            indexInput = args[2]
        # if index is a Series, get the name
        elif isinstance(indexInput,Series):
            if type(indexInput.name) is str :
                indexInput = indexInput.name
        # if index is None and data is SimSeries or SimDataFrame get the name
        elif type(data) in [SimSeries,SimDataFrame] and type(data.index.name) is str and len(data.index.name)>0 :
            indexInput = data.index.name
        
        # catch units or get from data if it is SimDataFrame or SimSeries
        if type(units) is dict :
            Udict , units = units , None
            if len(Udict) == 1 :
                if type( Udict[ list(Udict.keys())[0] ] ) is str :
                    Uname = list(Udict.keys())[0]
                    units = Udict[ Uname ]                    
        elif type(units) is str :
            self.units = units
        elif units is None and type(data) is SimSeries :
                units = data.units
        
        # remove arguments not known by Pandas
        kwargs.pop('indexName',None)
        # convert to pure Pandas
        if type(data) in [ SimDataFrame , SimSeries ] :
            data = data.to_Pandas()
        super().__init__(data=data, index=index, *args, **kwargs)
        
        # set the name of the index
        if ( self.index.name is None or ( type(self.index.name) is str and len(self.index.name)==0 ) ) and ( type(indexInput) is str and len(indexInput)>0 ) :
            self.index.name = indexInput       
        # overwrite the index.name with input from the argument indexName
        if 'indexName' in kwargs and type(kwargs['indexName']) is str and len(kwargs['indexName'].strip())>0 :
            self.set_indexName(kwargs['indexName'])
        
        # set the units
        if self.name is None and Uname is not None :
            self.name = Uname
        if self.name is not None and self.units is None and Udict is not None :
            if self.name in Udict :
                self.units = Udict[ self.name ]
            else :
                for each in self.index :
                    if each in Udict :
                        if type(self.units) is dict :
                            self.units[each] = Udict[each]
                        else :
                            self.units = { each:Udict[each] }
                    else :
                        if type(self.units) is dict :
                            self.units[each] = 'UNITLESS'
                        else :
                            self.units = { each:'UNITLESS' }
    
    @property
    def _constructor(self):
        return _simseries_constructor_with_fallback
    @property
    def _constructor_expanddim(self):
        # from datafiletoolbox.SimPandas.simframe import SimDataFrame
        return SimDataFrame

    def set_index(self,Name) :
        self.set_indexName( Name )

    def set_indexName(self,Name) :
        if type(Name) is str :
            self.index.name = Name

    def to_Pandas(self) :
        return self.as_Series()

    def as_Series(self) :
        return Series( self )
    @property
    def Series(self) :
        return self.as_Series()
    @property
    def S(self) :
        return self.as_Series()
    
    def __neg__(self) :
        result = -self.as_Series()
        return SimSeries( data=result , units=self.units , dtype=self.dtype )
    
    def __add__(self,other) :
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                if self.units == other.units :
                    result = self.add(other)
                    return SimSeries( data=result , units=self.units , dtype=self.dtype )
                elif convertibleUnits( other.units , self.units ) :
                    otherC = convertUnit( other , other.units , self.units , self.speak )
                    result = self.add(otherC)
                    return SimSeries( data=result , units=self.units , dtype=self.dtype )
                elif convertibleUnits( self.units , other.units ) :
                    selfC = convertUnit( self , self.units , other.units , self.speak )
                    result = other.add(selfC)
                    return SimSeries( data=result , units=other.units , dtype=other.dtype )
                else :
                    result = self.add(other)
                    return SimSeries( data=result , units=self.units+'+'+other.units , dtype=self.dtype )
            else :
                raise NotImplementedError
        
        # let's Pandas deal with other types, maintain units and dtype
        result = self.as_Series() + other
        return SimSeries( data=result , units=self.units , dtype=self.dtype )

    def __sub__(self,other) :
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                if self.units == other.units :
                    result = self.sub(other)
                    return SimSeries( data=result , units=self.units , dtype=self.dtype )
                elif convertibleUnits( other.units , self.units ) :
                    otherC = convertUnit( other , other.units , self.units , self.speak )
                    result = self.sub(otherC)
                    return SimSeries( data=result , units=self.units , dtype=self.dtype )
                elif convertibleUnits( self.units , other.units ) :
                    selfC = convertUnit( self , self.units , other.units , self.speak )
                    result = other.sub(selfC)
                    return SimSeries( data=result , units=other.units , dtype=other.dtype )
                else :
                    result = self.sub(other)
                    return SimSeries( data=result , units=self.units+'-'+other.units , dtype=self.dtype )
            else :
                raise NotImplementedError

        # let's Pandas deal with other types, maintain units and dtype
        result = self.as_Series() - other
        return SimSeries( data=result , units=self.units , dtype=self.dtype )
    
    def __mul__(self,other) :
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                if self.units == other.units :
                    result = self.mul(other)
                    unitsResult = unitProduct(self.units,other.units)
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
                elif convertibleUnits( other.units , self.units ) :
                    otherC = convertUnit( other , other.units , self.units , self.speak )
                    result = self.mul(otherC)
                    unitsResult = unitProduct(self.units,other.units)
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
                elif convertibleUnits( self.units , other.units ) :
                    selfC = convertUnit( self , self.units , other.units , self.speak )
                    result = other.mul(selfC)
                    unitsResult = unitProduct(other.units,self.units)
                    return SimSeries( data=result , units=unitsResult , dtype=other.dtype )
                else :
                    result = self.mul(other)
                    unitsResult = unitProduct(self.units,other.units)
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
            else :
                raise NotImplementedError
        
        # let's Pandas deal with other types (types with no units), maintain units and dtype
        result = self.as_Series() * other
        return SimSeries( data=result , units=self.units , dtype=self.dtype )

    def __truediv__(self,other) :
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                if self.units == other.units :
                    result = self.truediv(other)
                    unitsResult = unitDivision(self.units,other.units)
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
                elif convertibleUnits( other.units , self.units ) :
                    otherC = convertUnit( other , other.units , self.units , self.speak )
                    result = self.truediv(otherC)
                    unitsResult = unitDivision(self.units,other.units)
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
                elif convertibleUnits( self.units , other.units ) :
                    selfC = convertUnit( self , self.units , other.units , self.speak )
                    result = other.truediv(selfC)
                    unitsResult = unitDivision(other.units,self.units)
                    return SimSeries( data=result , units=unitsResult , dtype=other.dtype )
                else :
                    result = self.truediv(other)
                    unitsResult = unitDivision(self.units,other.units)
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
            else :
                raise NotImplementedError
        
        # let's Pandas deal with other types (types with no units), maintain units and dtype
        result = self.as_Series() / other
        return SimSeries( data=result , units=self.units , dtype=self.dtype )

    def __floordiv__(self,other) :
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                if self.units == other.units :
                    result = self.floordiv(other)
                    unitsResult = unitDivision(self.units,other.units)
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
                elif convertibleUnits( other.units , self.units ) :
                    otherC = convertUnit( other , other.units , self.units , self.speak )
                    result = self.floordiv(otherC)
                    unitsResult = unitDivision(self.units,other.units)
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
                elif convertibleUnits( self.units , other.units ) :
                    selfC = convertUnit( self , self.units , other.units , self.speak )
                    result = other.floordiv(selfC)
                    unitsResult = unitDivision(other.units,self.units)
                    return SimSeries( data=result , units=unitsResult , dtype=other.dtype )
                else :
                    result = self.floordiv(other)
                    unitsResult = unitDivision(self.units,other.units)
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
            else :
                raise NotImplementedError
        
        # let's Pandas deal with other types (types with no units), maintain units and dtype
        result = self.as_Series() // other
        return SimSeries( data=result , units=self.units , dtype=self.dtype )
    
    def __mod__(self,other) :
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                if self.units == other.units :
                    result = self.mod(other)
                    return SimSeries( data=result , units=self.units , dtype=self.dtype )
                elif convertibleUnits( other.units , self.units ) :
                    otherC = convertUnit( other , other.units , self.units , self.speak )
                    result = self.mod(otherC)
                    return SimSeries( data=result , units=self.units , dtype=self.dtype )
                elif convertibleUnits( self.units , other.units ) :
                    selfC = convertUnit( self , self.units , other.units , self.speak )
                    result = other.mod(selfC)
                    return SimSeries( data=result , units=other.units , dtype=other.dtype )
                else :
                    result = self.mod(other)
                    return SimSeries( data=result , units=self.units , dtype=self.dtype )
            else :
                raise NotImplementedError
        
        # let's Pandas deal with other types, maintain units and dtype
        result = self.as_Series() % other
        return SimSeries( data=result , units=self.units , dtype=self.dtype )

    def __pow__(self,other) :
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                if self.units == other.units :
                    result = self.pow(other)
                    unitsResult = self.units+'^'+other.units
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
                elif convertibleUnits( other.units , self.units ) :
                    otherC = convertUnit( other , other.units , self.units , self.speak )
                    result = self.floordiv(otherC)
                    unitsResult = self.units+'^'+other.units
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
                elif convertibleUnits( self.units , other.units ) :
                    selfC = convertUnit( self , self.units , other.units , self.speak )
                    result = other.floordiv(selfC)
                    unitsResult = other.units+'^'+self.units
                    return SimSeries( data=result , units=unitsResult , dtype=other.dtype )
                else :
                    result = self.floordiv(other)
                    unitsResult = self.units+'^'+other.units
                    return SimSeries( data=result , units=unitsResult , dtype=self.dtype )
            else :
                raise NotImplementedError
        
        # let's Pandas deal with other types (types with no units), maintain units and dtype
        result = self.as_Series() // other
        return SimSeries( data=result , units=self.units , dtype=self.dtype )
    
    def __repr__(self) -> str :
        """
        Return a string representation for a particular Series, with Units.
        """
        # from Pandas Series
        buf = StringIO("")
        width, height = get_terminal_size()
        max_rows = (
            height
            if get_option("display.max_rows") == 0
            else get_option("display.max_rows")
        )
        min_rows = (
            height
            if get_option("display.max_rows") == 0
            else get_option("display.min_rows")
        )
        show_dimensions = get_option("display.show_dimensions")

        self.to_string(
            buf=buf,
            name=self.name,
            dtype=self.dtype,
            min_rows=min_rows,
            max_rows=max_rows,
            length=show_dimensions,
        )
        result = buf.getvalue()
        
        if type(self.units) is str :
            return result + ', Units: ' + self.units
        elif type(self.units) is dict :
            result = result.split('\n')
            for n in range(len(result)-1) :
                keys = result[n] + ' '
                i , f = 0 , 0
                while i < len(keys) :
                    f = keys.index(' ',i) 
                    key = keys[i:f]
                    if key == '...' :
                        i = len(keys)
                        continue
                    while key not in self.index and f <= len(keys) :
                        f = keys.index(' ',f+1) 
                        key = keys[i:f]
                    if key not in self.index :
                        i = len(keys)
                        continue
                    if key in self.units :
                        result[n] += '    ' + self.units[key].strip()
                    i = len(keys)
            result = '\n'.join(result)
            return '\n' + result
    
    def get_units(self) :
        return self.get_Units()
    def get_Units(self) :
        if type(self.units) is str and type(self.name) is str :
            uDic = { str(self.name) : self.units }
        elif type(self.units) is dict :
            uDic = {}
            for each in self.index :
                if each in self.units :
                    uDic[each] = self.units[each]
                else :
                    uDic[each] = 'UNITLESS'
        return uDic

    def copy(self) :
        if type(self.units) is dict :
            return SimSeries( data=self.as_Series().copy(True) , units=self.units.copy() , dtype=self.dtype , indexName=self.index.name )
        return SimSeries( data=self.as_Series().copy(True) , units=self.units , dtype=self.dtype , indexName=self.index.name )

    def filter(self,conditions=None,**kwargs) :
        """
        Returns a filtered SimSeries based on conditions argument.
        
        To filter over the series simply define the 
        condition:
            '>0'
                    
        To set several conditions together the operatos 'and' and 'or' 
        are accepted:
            '>0 and <1000'
        
        To filter only over the index set the condition directly:
            '>0'
        or use the key '.index' or '.i' to refer to the index of the SimSeries.
        
        To remove null values append '.notnull' to the column name:
            'NAME.notnull'
        To keep only null values append '.null' to the column name:
            'NAME'.null
        """
        returnString = False
        if 'returnString' in kwargs :
            returnString = bool( kwargs['returnString'] )
        returnFilter = False
        if 'returnFilter' in kwargs :
            returnFilter = bool( kwargs['returnFilter'] )
        returnFrame = False
        if 'returnFrame' in kwargs :
            returnFrame = bool( kwargs['returnFrame'] )
        if 'returnSeries' in kwargs :
            returnFrame = bool( kwargs['returnSeries'] )
        if not returnFilter and not returnString and ( 'returnSeries' not in kwargs or 'returnFrame' not in kwargs ) :
            returnFrame = True
        
        
        specialOperation = ['.notnull','.null','.isnull','.abs']
        numpyOperation = ['.sqrt','.log10','.log2','.log','.ln']
        pandasAggregation = ['.any','.all']
        PandasAgg = ''
        
        def KeyToString(filterStr,key,PandasAgg) :
            if len(key) > 0 :
                # catch particular operations performed by Pandas
                foundSO , foundNO = '' , '' 
                if key in specialOperation :
                    if filterStr[-1] == ' ' :
                        filterStr = filterStr.rstrip()
                    filterStr += key+'()'
                else :
                    for SO in specialOperation :
                        if key.strip().endswith(SO) :
                            key = key[:-len(SO)]
                            foundSO = ( SO if SO != '.null' else '.isnull' ) + '()'
                            break
                # catch particular operations performed by Numpy
                if key in numpyOperation :
                    raise ValueError( "wrong syntax for '"+key+" (blank space before) in:\n   "+conditions)
                else :
                    for NO in numpyOperation :
                        if key.strip().endswith(NO) :
                            key = key[:-len(NO)]
                            NO = '.log' if NO == '.ln' else NO
                            filterStr += 'np' + NO + '('
                            foundNO = ' )'
                            break
                # catch aggregation operations performed by Pandas
                if key in pandasAggregation :
                    PandasAgg = key+'(axis=1)'
                else :
                    for PA in pandasAggregation :
                        if key.strip().endswith(PA) :
                            PandasAgg = PA+'(axis=1)'
                            break
                # if key is the index
                if key in ['.i','.index'] :
                    filterStr = filterStr.rstrip()
                    filterStr += ' self.DF.index'
                # if key is a column
                elif key in self.columns :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.DF['"+key+"']"
                # key might be a wellname, attribute or a pattern
                elif len( self.find_Keys(key) ) == 1 :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.DF['"+ self.find_Keys(key)[0] +"']"
                elif len( self.find_Keys(key) ) > 1 :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.DF["+ str( list(self.find_Keys(key)) ) +"]"
                    PandasAgg = '.any(axis=1)'
                else :
                    filterStr += ' ' + key
                filterStr = filterStr.rstrip()
                filterStr += foundSO + foundNO
                key = ''
            return filterStr , key , PandasAgg
                        
        if type(conditions) is not str :
            if type(conditions) is not list :
                try :
                    conditions = list(conditions)
                except :
                    raise TypeError('conditions argument must be a string.')
            conditions = ' and '.join(conditions)
        
        conditions = conditions.strip() + ' '
        
        # find logical operators and translate to correct key
        AndOrNot = False
        if ' and ' in conditions :
            conditions = conditions.replace(' and ',' & ')
        if ' or ' in conditions :
            conditions = conditions.replace(' or ',' | ')
        if ' not ' in conditions :
            conditions = conditions.replace(' not ',' ~ ')
        if '&' in conditions :
            AndOrNot = True
        elif '|' in conditions :
            AndOrNot = True
        elif '~' in conditions :
            AndOrNot = True

        # create Pandas compatible condition string
        filterStr =  ' ' + '('*AndOrNot 
        key = ''
        cond , oper = '' , '' 
        i = 0
        while i < len(conditions) :
            
            # catch logital operators
            if conditions[i] in ['&',"|",'~'] :
                filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                filterStr = filterStr.rstrip()
                filterStr += ' )' + PandasAgg + ' ' + conditions[i] + ' ('
                PandasAgg = ''
                i += 1
                continue
            
            # catch enclosed strings
            if conditions[i] in ['"',"'",'['] :
                if conditions[i] in ['"',"'"] :
                    try :
                        f = conditions.index( conditions[i] , i+1 )
                    except :
                        raise ValueError('wring syntax, closing ' + conditions[i] + ' not found in:\n   '+conditions)
                else :
                    try :
                        f = conditions.index( ']' , i+1 )
                    except :
                        raise ValueError("wring syntax, closing ']' not found in:\n   "+conditions)
                if f > i+1 :
                    key = conditions[i+1:f]
                    filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                    i = f+1
                    continue
            
            # pass blank spaces
            if conditions[i] == ' ' :
                filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                if len(filterStr) > 0 and filterStr[-1] != ' ' :
                    filterStr += ' '
                i += 1
                continue
            
            # pass parenthesis
            if conditions[i] in ['(',')'] :
                filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                filterStr += conditions[i]
                i += 1
                continue
                
            # catch conditions
            if conditions[i] in ['=','>','<','!'] :
                cond = ''
                f = i+1
                while conditions[f] in ['=','>','<','!'] :
                    f += 1
                cond = conditions[i:f]
                if cond == '=' :
                    cond = '=='
                elif cond in ['=>','=<','=!'] :
                    cond = cond[::-1]
                elif cond in ['><','<>'] :
                    cond = '!='
                filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                filterStr = filterStr.rstrip()
                filterStr += ' ' + cond
                i += len(cond)
                continue
            
            # catch operations
            if conditions[i] in ['+','-','*','/','%','^'] :
                oper = ''
                f = i+1
                while conditions[f] in ['+','-','*','/','%','^'] :
                    f += 1
                oper = conditions[i:f]
                oper = oper.replace('^','**')
                filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                filterStr = filterStr.rstrip()
                filterStr += ' ' + oper
                i += len(oper)
                continue
            
            # catch other characters
            else :
                key += conditions[i]
                i += 1
                continue
        
        # clean up
        filterStr = filterStr.strip()
        # check missing key, means .index by default
        if filterStr[0] in ['=','>','<','!'] :
            filterStr = 'self.DF.index ' + filterStr
        elif filterStr[-1] in ['=','>','<','!'] :
            filterStr = filterStr + ' self.DF.index' 
        # close last parethesis and aggregation
        filterStr += ' )' * bool( AndOrNot + bool(PandasAgg) ) + PandasAgg
        # open parenthesis for aggregation, if needed
        if not AndOrNot and bool(PandasAgg) :
            filterStr = '( ' + filterStr
        
        retTuple = []
        
        if returnString :
            retTuple += [ filterStr ]
        filterArray = eval( filterStr )
        if returnFilter :
            retTuple += [ filterArray ]
        if returnFrame :
            retTuple += [ self.DF[ filterArray ] ]
        
        if len( retTuple ) == 1 :
            return retTuple[0]
        else :
            return tuple( retTuple )
        


class SimDataFrame(DataFrame) :
    """
    A SimDataFrame object is a pandas.DataFrame that units associated with to 
    each column. In addition to the standard DataFrame constructor arguments,
    SimDataFrame also accepts the following keyword arguments:

    Parameters
    ----------
    units : string or dictionary of units (optional)
        Can be any string, but only units acepted by the UnitConverter will
        be considered when doing arithmetic calculations with other SimSeries 
        or SimDataFrames.

    See Also
    --------
    SimSeries
    pandas.DataFrame
    
    """
    _metadata = ["units","speak"]
    
    def __init__(self , data=None , units=None , index=None , speak=False , *args , **kwargs) :
        self.units = None
        self.speak = bool(speak)
        
        indexInput = None
        # catch index keyword from input parameters
        if index is not None :
            indexInput = index
        elif 'index' in kwargs and kwargs['index'] is not None :
            indexInput = kwargs['index']
        elif len(args) >= 3 and args[2] is not None :
            indexInput = args[2]
        # if index is a Series, get the name
        elif isinstance(indexInput,Series) :
            if type(indexInput.name) is str :
                indexInput = indexInput.name
        # if index is None and data is SimSeries or SimDataFrame get the name
        elif type(data) in [SimSeries,SimDataFrame] and type(data.index.name) is str and len(data.index.name)>0 :
            indexInput = data.index.name
        
        # if units is None data is SimDataFrame or SimSeries get the units
        if units is None :
            if type(data) is SimDataFrame :
                units = data.units.copy()
            elif type(data) is SimSeries :
                if type(data.units) is dict :
                    units = data.units.copy()
                elif type(data.name) is str and type(data.units) is str :
                    units = { data.name : data.units }
        
        # remove arguments not known by Pandas
        kwargs.pop('indexName',None)
        # convert to pure Pandas
        if type(data) in [ SimDataFrame , SimSeries ] :
            data = data.to_Pandas()
        super().__init__(data=data,index=index,*args, **kwargs)

        # set the name of the index
        if ( self.index.name is None or ( type(self.index.name) is str and len(self.index.name)==0 ) ) and ( type(indexInput) is str and len(indexInput)>0 ) :
            self.index.name = indexInput
        # overwrite the index.name with input from the argument indexName
        if 'indexName' in kwargs and type(kwargs['indexName']) is str and len(kwargs['indexName'].strip())>0 :
            self.set_indexName(kwargs['indexName'])

        # set the units
        if type(units) is str :
            self.units = {}
            for key in list( self.columns ) :
                self.units[ key ] = units
        elif type(units) is list or type(units) is tuple :
            if len(units) == len(self.columns) :
                self.units = dict( zip( list(self.columns) , units ) )
        elif type(units) is dict and len(units)>0 :
            self.units = {}
            for key in list( self.columns ) :
                if key in units :
                    self.units[key] = units[key]
                else :
                    self.units[key] = 'UNITLESS'
    
    # @property
    # def _constructor(self):
    #     return SimDataFrame
    
    def set_indexName(self,Name) :
        if type(Name) is str and len(Name.strip())>0:
            self.index.name = Name
    
    def set_index(self,key,drop=False,append=False,inplace=True,verify_integrity=False,**kwargs) :
        if key not in self.columns :
            raise ValueError( "The key '"+str(key)+"' is not a column name of this DataFrame.")
        super().set_index(key,drop=drop,append=append,inplace=inplace,verify_integrity=verify_integrity,**kwargs)
    
    def to_Pandas(self) :
        return self.as_DataFrame()
    
    def as_DataFrame(self) :
        return DataFrame( self )
    @property
    def DataFrame(self) :
        return self.as_DataFrame()
    @property
    def DF(self) :
        return self.as_DataFrame()
    
    def __neg__(self) :
        result = -self.as_DataFrame()
        return SimDataFrame( data=result , units=self.units , indexName=self.index.name )
    
    def __add__(self,other) :
        # both SimDataFra,es
        if isinstance(other, SimDataFrame) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning( "indexes of both SimDataFrames are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            otherC = other.copy()
            selfC = self.copy()
            for col in self.columns :
                if col in other.columns :
                    if self.get_Units(col)[col] == other.get_Units(col)[col] :
                        pass # OK
                    elif convertibleUnits( other.get_Units(col)[col] , self.get_Units(col)[col] ) :
                        otherC[col] = convertUnit( other[col] , other.get_Units(col)[col] , self.get_Units(col)[col] , self.speak )
                    elif convertibleUnits( self.get_Units(col)[col] , other.get_Units(col)[col] ) :
                        selfC[col] = convertUnit( self[col] , self.get_Units(col)[col] , other.get_Units(col)[col] , self.speak )
                    else :
                        selfC.units[col] = self.get_Units(col)[col]+'+'+other.get_Units(col)[col]
                else :
                    selfC.units[col] = other.get_Units(col)[col]
            result = selfC.add(otherC)
            return SimDataFrame( data=result , units=selfC.units , indexName=self.index.name )
        
        # let's Pandas deal with other types, maintain units and dtype
        result = self.as_DataFrame() + other
        return SimDataFrame( data=result , units=self.units , indexName=self.index.name )
    
    def __sub__(self,other) :
        # both SimDataFra,es
        if isinstance(other, SimDataFrame) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning( "indexes of both SimDataFrames are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            otherC = other.copy()
            selfC = self.copy()
            for col in self.columns :
                if col in other.columns :
                    if self.get_Units(col)[col] == other.get_Units(col)[col] :
                        pass # OK
                    elif convertibleUnits( other.get_Units(col)[col] , self.get_Units(col)[col] ) :
                        otherC[col] = convertUnit( other[col] , other.get_Units(col)[col] , self.get_Units(col)[col] , self.speak )
                    elif convertibleUnits( self.get_Units(col)[col] , other.get_Units(col)[col] ) :
                        selfC[col] = convertUnit( self[col] , self.get_Units(col)[col] , other.get_Units(col)[col] , self.speak )
                    else :
                        selfC.units[col] = self.get_Units(col)[col]+'+'+other.get_Units(col)[col]
                else :
                    selfC.units[col] = other.get_Units(col)[col]
            result = selfC.sub(otherC)
            return SimDataFrame( data=result , units=selfC.units , indexName=self.index.name )
        
        # let's Pandas deal with other types, maintain units and dtype
        result = self.as_DataFrame() - other
        return SimDataFrame( data=result , units=self.units , indexName=self.index.name )
    
    def copy(self) :
        return SimDataFrame( data=self.as_DataFrame().copy(True) , units=self.units.copy() , indexName=self.index.name )
    
    def __call__(self,key=None) :
        if key is None :
            key = self.columns

        result = self.__getitem__(key)
        if isinstance(result,SimSeries) :
            result = result.to_numpy()
        return result
    
    def __setitem__(self, key, value , units=None):
        
        if type(key) is str :
            key = key.strip()
        
        if units is None :
            if isinstance(value,SimSeries) :
                if type(value.units) is str :
                    uDic = { str(key) : value.units }
                elif type(value.units) is dict :
                    uDic = value.units
            elif isinstance(value,SimDataFrame) :
                pass
            else :
                uDic = { str(key) : 'UNITLESS' }
        elif type(units) is str :
            uDic = { str(key) : units.strip() }
        elif type(units) is dict :
            raise NotImplementedError
        else :
            raise NotImplementedError
        
        before = len(self.columns)
        super().__setitem__(key,value)
        after = len(self.columns)
        
        if after == before :
            self.new_Units(key,uDic[key])
        elif after > before :
            for c in range( before , after ) :
                if self.columns[c] in self.columns[ before : after ] :
                    self.new_Units( self.columns[c] , uDic[ self.columns[c] ] )
                else :
                    self.new_Units( self.columns[c] , 'UNITLESS' )
    
    def __getitem__(self, key) :

        if isinstance(key,(Series)) or type(key) is np.array :
            if str(key.dtype) == 'bool' :
                return self._getbyFilter(key)

        byIndex = False
        indexFilter = None
        indexes = None
        slices = None
        
        ### convert tuple argument to list
        if type(key) is tuple :
            key = list(key)
        
        ### if key is a string but not a column name, check if it is an item, attribute, pattern, filter or index
        if type(key) is str and key not in self.columns :
            
            if bool( self.find_Keys(key) ) : # catch the column names this key represent
                key = list( self.find_Keys(key) )
            else : # key is not a column name
                try : # to evalue as a filter
                    return self._getbyCriteria(key)
                except :
                    try : # to evaluate as an index value
                        return self._getbyIndex(key)
                    except :
                        raise ValueError ('requested key is not a valid column name, pattern, index or filter criteria:\n   '+ key) 
        
        ### key is a list, have to check every item in the list
        elif type(key) is list :
            keyList , key , filters , indexes , slices = key , [] , [] , [] , []
            for each in keyList :
                ### the key is a column name
                if type(each) is slice :
                    slices += [each]
                elif each in self.columns :
                    key += [each]
                ### if key is a string but not a column name, check if it is an item, attribute, pattern, filter or index
                elif type(each) is str :
                    if bool( self.find_Keys(each) ) : # catch the column names this key represent
                        key += list( self.find_Keys(each) )
                    else : # key is not a column name, might be a filter or index
                        try : # to evalue as a filter
                            trash = self.filter(each,returnFilter=True)
                            filters += [each]
                        except :
                            try : # to evaluate as an index value
                                trash = self._getbyIndex(each)
                                indexes += [each]
                            except :
                                # discard this item
                                print(' the paramenter '+str(each)+' is not valid.')
                
                ### must be an index, not a column name o relative, not a filter, not in the index
                else :
                    indexes += [each]

            ### get the filter array, if filter criteria was provided
            if bool(filters) :
                try :
                    indexFilter = self.filter(filters,returnFilter=True)
                except :
                    raise Warning ('filter conditions are not valid:\n   '+ ' and '.join(filters) )
                if not indexFilter.any() :
                    raise Warning ('filter conditions removed every row :\n   '+ ' and '.join(filters) )
        
        ### attempt to get the desired keys, first as column names, then as indexes
        if bool(key) :
            try :
                result = self._getbyColumn(key)
            except :
                result = self._getbyIndex(key)
                if result is not None : byIndex = True
        else :
            result = SimDataFrame( data=self )
        
        ### convert returned object to SimDataFrame or SimSeries accordingly
        if type(result) is DataFrame :
            resultUnits = self.get_Units(result.columns)
            result = SimDataFrame(data=result , units=resultUnits)
        elif type(result) is Series :
            if result.name is None or type(result.name) is not str :
                # this Series is one index for multiple columns
                resultUnits = self.get_Units(result.index)
            else :
                resultUnits = self.get_Units(result.name)
            result = SimSeries(data=result , units=resultUnits)
        
        ### apply filter array if applicable
        if indexFilter is not None :
            if type(indexFilter) is np.ndarray :
                result = result.iloc[indexFilter]
            else :
                result = result[indexFilter.array]
        
        ### apply indexes and slices
        if bool(indexes) or bool(slices) :
            indexeslices = indexes + slices
            iresult = Series2Frame(result._getbyIndex(indexeslices[0]))
            if len(indexeslices) > 1 :
                for i in indexeslices[1:] :
                    iresult = iresult.append( Series2Frame(result._getbyIndex(i)) )
            try :
                result = iresult.sort_index()
            except :
                result = iresult
        
        ### if is a single row return it as a DataFrame instead of a Series
        if byIndex :
            result = Series2Frame(result)
        
        return result
    
    def _getbyFilter(self,key) :
        """
        ** helper function to __getitem__ method **
        
        try to get a filtered DataFrame or Series ( .filter[key] )
        
        """
        if len(key) != len(self.DF) :
            raise ValueError( 'Filter wrong length ' + len(key) + ' instead of ' + len(self.DF) )
        if not isinstance(key,(Series,SimSeries)) and type(key) is not np.array :
            raise TypeError( "Filter must be a Series or Array" )
        else :
            if str(key.dtype) != 'bool' :
                raise TypeError( "Filter dtype must be 'bool'" )
        
        return super().loc(key)
    
    def _getbyCriteria(self,key) :
        """
        ** helper function to __getitem__ method **
        
        try to get a filtered DataFrame or Series ( .filter[key] )
        
        """
        return self.filter(key)
    
    def _getbyColumn(self,key) :
        """
        ** helper function to __getitem__ method **
        
        try to get a column by column name ( .__getitem__[key] )
        
        """
        return super().__getitem__(key)
        
    
    def _getbyIndex(self,key) :
        """
        ** helper function to __getitem__ method **
        
        try to get a row by index value ( .loc[key] ) or by position ( .iloc[key] )
        
        """
        # if index is date try to undestand key as a date
        if type(self.index) is DatetimeIndex and type(key) not in [DatetimeIndex,Timestamp,int,float,np.ndarray] :
            try :
                return self._getbyDateIndex(key)
            except :
                pass

        # try to find key by index value using .loc
        try :
            return self.loc[key]
        except :
            # try to find key by index position using .loc
            try :
                return self.iloc[key]
            except :
                raise ValueError(' ' + str(key) + ' is not a valid index value or position.')
    
    def _getbyDateIndex(self,key) :
        """
        ** helper function to __getitem__ method **
        
        try to get a row by index value ( .loc[key] ) or by position ( .iloc[key] )
        
        """
        if type(self.index) is DatetimeIndex :
            if type(key) in [DatetimeIndex,Timestamp,np.datetime64,np.ndarray,dt.date] :
                try :
                    return self.loc[key]
                except :
                    pass
            
            if type(key) is not str and ( isDate(key) or type(key) not in [DatetimeIndex,Timestamp] ) :
                try:
                    return self.loc[key]
                except :
                    try :
                        return self.iloc[key]
                    except :
                        pass
            
            if type(key) is str and len( multisplit(key,('==','!=','>=','<=','<>','><','>','<','=',' ')) ) == 1 and isDate(key) :
                try :
                    key = strDate( key )
                except :
                    try :
                        key = strDate( key , formatIN=isDate(key,returnFormat=True) , formatOUT='DD-MMM-YYYY' )
                    except :
                        raise Warning('\n Not able to undertand the key as a date.\n')
                try :
                    return self.loc[key]
                except :
                    pass 
            
            if type(key) is str :
                keyParts = multisplit(key,('==','!=','>=','<=','<>','><','>','<','=',' '))
                keySearch = ''
                datesDict = {}
                temporal = SimDataFrame(index=self.index)
                datesN = len(self)
                for P in range(len(keyParts)) :
                    if isDate(keyParts[P]) :
                        keySearch += ' D'+str(P)
                        datesDict['D'+str(P)] = keyParts[P]
                        temporal.__setitem__( 'D'+str(P) , DatetimeIndex( [ Timestamp(strDate(keyParts[P],formatIN=isDate(keyParts[P],returnFormat=True),formatOUT='YYYY-MMM-DD')) ] * datesN ).to_numpy() )
                    else :
                        keySearch += ' '+keyParts[P]
                datesFilter = temporal.filter( keySearch , returnFilter=True)
                return self.iloc[datesFilter.array]

            else :
                return self.iloc[key]
        
    def __repr__(self) -> str:
        """
        Return a string representation for a particular DataFrame, with Units.
        """
        firstRow = 1 if self.index.name is None else 2
        lastRow = -2
        def thisColumnMaxLen() :
            thisColumn = [None]*len( result[firstRow:lastRow] )
            for line in range(len(result[firstRow:lastRow])) :
                rawLine = multisplit( result[firstRow:lastRow][line] , ['  ',' -'] )
                thisLine = []
                for raw in rawLine :
                    if len(raw.strip(' -')) > 0 :
                        thisLine.append( raw )
                print('\ndebug:\n   keys:',keys,'\n   line:',line,'len(thisColumn):',len(thisColumn),'\n   keyN:',keyN,'len(thisLine):',len(thisLine),'\n   rawLine:"',rawLine,'"\n')
                thisColumn[line] = len(thisLine[keyN])
            return max( thisColumn ) 
        
        buf = StringIO("")
        if self._info_repr():
            self.info(buf=buf)
            return buf.getvalue()

        max_rows = get_option("display.max_rows")
        min_rows = get_option("display.min_rows")
        max_cols = get_option("display.max_columns")
        max_colwidth = get_option("display.max_colwidth")
        show_dimensions = get_option("display.show_dimensions")
        if get_option("display.expand_frame_repr"):
            width, _ = console.get_console_size()
        else:
            width = None
        self.to_string(
            buf=buf,
            max_rows=max_rows,
            min_rows=min_rows,
            max_cols=max_cols,
            line_width=width,
            max_colwidth=max_colwidth,
            show_dimensions=show_dimensions,
        )
        
        result = buf.getvalue()
        
        if result.startswith('Empty SimDataFrame\n') or result.startswith('Empty DataFrame\n') :
            return result
        
        result = result.split('\n')
        UnitsLine = ''
        keys = result[0] + ' '
        keyN = 0
        i , f = 0 , 0
        while i < len(keys) :
            
            if keys[i] == ' ' :
                i += 1
                continue
            else :
                f = keys.index(' ',i) 
                key = keys[i:f]
                keyN += 1
                
                if key == '...' :
                    UnitsLine += '  ...'
                    
                # key might be a column name
                else :
                    while key not in self.columns and f <= len(keys) :
                        f = keys.index(' ',f+1)
                        key = keys[i:f]
                    maxLen = max( thisColumnMaxLen() , len(key) )
                    if key in self.units :
                        UnitLabel = self.units[key].strip()
                        if len(UnitLabel) < maxLen :
                            UnitLabel = ' ' * ( maxLen - len(UnitLabel) ) + UnitLabel
                        elif len(UnitLabel) > maxLen :
                            UnitLabel = UnitLabel[:maxLen]
                    else :
                        UnitLabel = ' ' * maxLen
                    UnitsLine += '  ' + UnitLabel
                i = f
        
        keyN = 0
        indexColumnLen = thisColumnMaxLen()
        UnitsLabel = 'Units'
        if indexColumnLen < 5 :
            UnitsLabel = UnitsLabel[:indexColumnLen] + ':'
        elif indexColumnLen > 6 :
            UnitsLabel = UnitsLabel + ':' + ' '*(indexColumnLen-6-1)
        else :
            UnitsLabel = UnitsLabel + ':'
        
        UnitsLine = UnitsLabel + UnitsLine
        result = '\n' + result[0] + '\n' + UnitsLine + '\n' + '\n'.join(result[1:])
        return result

    @property
    def wells(self) :
        objs = []
        for each in list( self.columns ) :
            if ':' in each and each[0] == 'W' :
                objs += [each.split(':')[-1]]
        return tuple(set(objs))
    def get_Wells(self,pattern=None) :
        """       
        Will return a tuple of all the well names in case.

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
        if pattern is None :
            return tuple(self.wells)
        else:
            return tuple( fnmatch.filter( self.wells , pattern ) )

    @property
    def groups(self) :
        objs = []
        for each in list( self.columns ) :
            if ':' in each and each[0] == 'G' :
                objs += [each.split(':')[-1]]
        return tuple(set(objs))
    def get_Groups(self,pattern=None) :
        """       
        Will return a tuple of all the group names in case.

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
        if pattern is None :
            return self.groups
        else:
            return tuple( fnmatch.filter( self.groups , pattern ) )
        
    @property
    def regions(self) :
        objs = []
        for each in list( self.columns ) :
            if ':' in each and each[0] == 'R' :
                objs += [each.split(':')[-1]]
        return tuple(set(objs))
    def get_Regions(self,pattern=None):
        """
        Will return a tuple of all the region names in case.

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
        if pattern is None :
            return self.regions
        else:
            return tuple( fnmatch.filter( self.regions , pattern ) )
        
    @property
    def attributes(self) :
        atts = {}
        for each in list( self.columns ) :
            if ':' in each :
                if each.split(':')[0] in atts :
                    atts[each.split(':')[0]] += [each.split(':')[-1]]
                else :
                    atts[each.split(':')[0]] = [each.split(':')[-1]]
            else :
                if each not in atts :
                    atts[each] = []
        for att in atts :
            atts[att] = list(set(atts[att]))
        return atts
    def get_Attributes(self,pattern=None) :
        """
        Will return a tuple of all the attributes names in case.

        If the pattern variable is different from None only attributes
        matching the pattern will be returned; the matching is based
        on fnmatch():
            Pattern     Meaning
            *           matches everything
            ?           matches any single character
            [seq]       matches any character in seq
            [!seq]      matches any character not in seq
        """
        if pattern is None :
            return tuple(self.attributes.keys())
        else :
            return tuple( fnmatch.filter( tuple(self.attributes.keys()) , pattern ) )
    
    def get_Keys(self,pattern=None) :
        """       
        Will return a tuple of all the key names in case.

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
            raise TypeError('pattern argument must be a string.\nreceived '+str(type(pattern))+' with value '+str(pattern))
        if pattern is None :
            return tuple( self.columns )
        else:
            return tuple( fnmatch.filter( tuple( self.columns ) , pattern ) )
    
    def find_Keys(self,criteria=None) :
        """       
        Will return a tuple of all the key names in case.
        
        If criteria is provided, only keys matching the pattern will be returned.
        Accepted criterias can be:
            > well, group or region names. 
              All the keys related to that name will be returned
            > attributes. 
              All the keys related to that attribute will be returned
            > a fmatch compatible pattern:
                Pattern     Meaning
                *           matches everything
                ?           matches any single character
                [seq]       matches any character in seq
                [!seq]      matches any character not in seq
            
            additionally, ! can be prefixed to a key to return other keys but 
            that particular one:
                '!KEY'     will return every key but not 'KEY'.
                           It will only work with a single key.
        """
        if criteria is None :
            return tuple( self.columns )
        keys = []
        if type(criteria) is str and len(criteria.strip()) > 0 :
            if criteria.strip()[0] == '!' and len(criteria.strip()) > 1 :
                keys = list( self.columns )
                keys.remove(criteria[1:])
                return tuple( keys )
            criteria = [criteria]
        elif type(criteria) is not list :
            try :
                criteria = list(criteria)
            except :
                pass
        for key in criteria :
            if type(key) is str and key not in self.columns :
                if key in self.wells or key in self.groups or key in self.regions :
                    keys += list(self.get_Keys('*:'+key))
                elif key in self.attributes :
                    keys += list( self.keyGen( key , self.attributes[key] ) )
                else :
                    keys += list(self.get_Keys(key))
            elif type(key) is str and key in self.columns :
                keys += [ key ] 
            else :
                keys += list( self.find_Keys(key) )
        return tuple(keys)
    
    def get_units(self,items=None) :
        return self.get_Units(items)
    def get_Units(self,items=None) :
        if items is None :
            return self.units
        uDic = {}
        if type(items) is str :
            items = [items]
        for each in items :
            if each in self.units :
                uDic[each] = self.units[each]
            elif each in self.wells or each in self.groups or each in self.regions :
                for Key in self.get_Keys('*:'+each) :
                    uDic[each] = self.units[each]
            elif each in self.attributes :
                for att in self.keyGen( each , self.attributes[each] ) :
                    if att in self.units :
                        uDic[att] = self.units[att]
                    else :
                        uDic[att] = 'UNITLESS'
            elif len( self.get_Keys(each) ) > 0 :
                for key in self.get_Keys(each) :
                    uDic[key] = self.units[key]
        return uDic
    
    def keysByUnits(self) :
        """
        returns a dictionary of the units present in the SimDataFrame as keys
        and a list of the columns that has that units. 
        """
        kDic = {}
        for k,v in self.units.items() :
            if v in kDic :
                kDic[v] += [k]
            else :
                kDic[v] = [k]
        return kDic
            
    
    def new_Units(self,key,units) :
        if type(key) is str :
            key = key.strip()
        if type(units) is str :
            units = units.strip()
        
        if key not in self.units :
            self.units[key] = units
        else :
            print( "overwritting existing units for key '" + key + "': " + self.units[key] + ' -> ' + units )
            self.units[key] = units
    
    def is_Key(self,Key) :
        if type(Key) != str or len(Key)==0 :
            return False
        if Key in self.get_Keys() :
            return True
        else :
            return False

    def keyGen(self,mainKeys=[],itemKeys=[]) :
        """
        returns the combination of every key in keys with all the items.
        keys and items must be list of strings
        """
        if type(itemKeys) is str :
            itemKeys = [itemKeys]
        if type(mainKeys) is str :
            mainKeys = [mainKeys]
        ListOfKeys = []
        for k in mainKeys :
            k.strip(' :')
            if self.is_Key(k) :
                ListOfKeys.append(k)
            for i in itemKeys :
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
    
    def filter(self,conditions=None,**kwargs) :
        """
        Returns a filtered SimDataFrame based on conditions argument.
        
        To filter over a column simply use the name of the column in the 
        condition:
            'NAME>0'
        
        In case the column name has white spaces, enclose it in ' or " or [ ]:
            "'BLANK SPACE'>0"
            '"BLANK SPACE">0'
            '[BLANK SPACE]>0'
            
        To set several conditions together the operatos 'and' and 'or' 
        are accepted:
            'NAME>0 and LAST>0'
        
        To filter only over the index set the condition directly:
            '>0'
        or use the key '.index' or '.i' to refer to the index of the SimDataFrame.
        
        To remove null values append '.notnull' to the column name:
            'NAME.notnull'
        To keep only null values append '.null' to the column name:
            'NAME'.null
            
        In case the filter criteria is applied on a DataFrame, not a Series, 
        the resulting filter needs to be aggregated into a single column.
        By default, the aggregation criteria will return True if any of the
        columns is True.
        This aggregation behaviour can be changed to return True only if all 
        the columns are True:
            'MULTIPLE_COLUMNS'.any  needs just one column True to return True
            'MULTIPLE_COLUMNS'.any  needs all the columns True to return True
        
        """
        returnString = False
        if 'returnString' in kwargs :
            returnString = bool( kwargs['returnString'] )
        returnFilter = False
        if 'returnFilter' in kwargs :
            returnFilter = bool( kwargs['returnFilter'] )
        returnFrame = False
        if 'returnFrame' in kwargs :
            returnFrame = bool( kwargs['returnFrame'] )
        if not returnFilter and not returnString and 'returnFrame' not in kwargs :
            returnFrame = True
        
        
        specialOperation = ['.notnull','.null','.isnull','.abs']
        numpyOperation = ['.sqrt','.log10','.log2','.log','.ln']
        pandasAggregation = ['.any','.all']
        PandasAgg = ''
        last = ['']
        
        def KeyToString(filterStr,key,PandasAgg) :
            if len(key) > 0 :
                # catch particular operations performed by Pandas
                foundSO , foundNO = '' , '' 
                if key in specialOperation :
                    if filterStr[-1] == ' ' :
                        filterStr = filterStr.rstrip()
                    filterStr += key+'()'
                else :
                    for SO in specialOperation :
                        if key.strip().endswith(SO) :
                            key = key[:-len(SO)]
                            foundSO = ( SO if SO != '.null' else '.isnull' ) + '()'
                            break
                # catch particular operations performed by Numpy
                if key in numpyOperation :
                    raise ValueError( "wrong syntax for '"+key+" (blank space before) in:\n   "+conditions)
                else :
                    for NO in numpyOperation :
                        if key.strip().endswith(NO) :
                            key = key[:-len(NO)]
                            NO = '.log' if NO == '.ln' else NO
                            filterStr += 'np' + NO + '('
                            foundNO = ' )'
                            break
                # catch aggregation operations performed by Pandas
                if key in pandasAggregation :
                    PandasAgg = key+'(axis=1)'
                else :
                    for PA in pandasAggregation :
                        if key.strip().endswith(PA) :
                            PandasAgg = PA+'(axis=1)'
                            break
                # if key is the index
                if key in ['.i','.index'] :
                    filterStr = filterStr.rstrip()
                    filterStr += ' self.DF.index'
                # if key is a column
                elif key in self.columns :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.DF['"+key+"']"
                # key might be a wellname, attribute or a pattern
                elif len( self.find_Keys(key) ) == 1 :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.DF['"+ self.find_Keys(key)[0] +"']"
                elif len( self.find_Keys(key) ) > 1 :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.DF["+ str( list(self.find_Keys(key)) ) +"]"
                    PandasAgg = '.any(axis=1)'
                else :
                    filterStr += ' ' + key
                filterStr = filterStr.rstrip()
                filterStr += foundSO + foundNO
                key = ''
                last.append('key')
            return filterStr , key , PandasAgg
                        
        if type(conditions) is not str :
            if type(conditions) is not list :
                try :
                    conditions = list(conditions)
                except :
                    raise TypeError('conditions argument must be a string.')
            conditions = ' and '.join(conditions)
        
        conditions = conditions.strip() + ' '
        
        # find logical operators and translate to correct key
        AndOrNot = False
        if ' and ' in conditions :
            conditions = conditions.replace(' and ',' & ')
        if ' or ' in conditions :
            conditions = conditions.replace(' or ',' | ')
        if ' not ' in conditions :
            conditions = conditions.replace(' not ',' ~ ')
        if '&' in conditions :
            AndOrNot = True
        elif '|' in conditions :
            AndOrNot = True
        elif '~' in conditions :
            AndOrNot = True

        # create Pandas compatible condition string
        filterStr =  ' ' + '('*AndOrNot 
        key = ''
        cond , oper = '' , '' 
        i = 0
        while i < len(conditions) :
            
            # catch logital operators
            if conditions[i] in ['&',"|",'~'] :
                filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                filterStr = filterStr.rstrip()
                auto = ' self.DF.index' if last[-1] in ['(','cond','oper'] else ''
                filterStr += auto + ' )' + PandasAgg + ' ' + conditions[i] + ' ('
                last.append('log')
                PandasAgg = ''
                i += 1
                continue
            
            # catch enclosed strings
            if conditions[i] in ['"',"'",'['] :
                if conditions[i] in ['"',"'"] :
                    try :
                        f = conditions.index( conditions[i] , i+1 )
                    except :
                        raise ValueError('wring syntax, closing ' + conditions[i] + ' not found in:\n   '+conditions)
                else :
                    try :
                        f = conditions.index( ']' , i+1 )
                    except :
                        raise ValueError("wring syntax, closing ']' not found in:\n   "+conditions)
                if f > i+1 :
                    key = conditions[i+1:f]
                    filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                    i = f+1
                    continue
            
            # pass blank spaces
            if conditions[i] == ' ' :
                filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                if len(filterStr) > 0 and filterStr[-1] != ' ' :
                    filterStr += ' '
                i += 1
                continue
            
            # pass parenthesis
            if conditions[i] in ['(',')'] :
                if conditions[i] == ')' and filterStr.rstrip()[-1] == '(' :
                    filterStr = filterStr.rstrip()[:-1]
                    last.pop()
                else :
                    if last[-1] in ['cond','oper'] : key = 'self.DF.index' 
                    filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                    filterStr += conditions[i]
                    last.append(conditions[i])
                i += 1
                continue
                
            # catch conditions
            if conditions[i] in ['=','>','<','!'] :
                cond = ''
                f = i+1
                while conditions[f] in ['=','>','<','!'] :
                    f += 1
                cond = conditions[i:f]
                if cond == '=' :
                    cond = '=='
                elif cond in ['=>','=<','=!'] :
                    cond = cond[::-1]
                elif cond in ['><','<>'] :
                    cond = '!='
                if key == '' : key = 'self.DF.index' 
                filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                filterStr = filterStr.rstrip()
                filterStr += ' ' + cond
                last.append('cond')
                i += len(cond)
                continue
            
            # catch operations
            if conditions[i] in ['+','-','*','/','%','^'] :
                oper = ''
                f = i+1
                while conditions[f] in ['+','-','*','/','%','^'] :
                    f += 1
                oper = conditions[i:f]
                oper = oper.replace('^','**')
                if last[-1] not in ['key'] : key = 'self.DF.index' 
                filterStr , key , PandasAgg = KeyToString(filterStr,key,PandasAgg) 
                filterStr = filterStr.rstrip()
                filterStr += ' ' + oper
                last.append('oper')
                i += len(oper)
                continue
            
            # catch other characters
            else :
                key += conditions[i]
                i += 1
                continue
        
        # clean up
        filterStr = filterStr.strip()
        # check missing key, means .index by default
        if filterStr[0] in ['=','>','<','!'] :
            filterStr = 'self.DF.index ' + filterStr
        elif filterStr[-1] in ['=','>','<','!'] :
            filterStr = filterStr + ' self.DF.index' 
        # close last parethesis and aggregation
        filterStr += ' )' * bool( AndOrNot + bool(PandasAgg) ) + PandasAgg
        # open parenthesis for aggregation, if needed
        if not AndOrNot and bool(PandasAgg) :
            filterStr = '( ' + filterStr
        
        retTuple = []
        print(last)
        if returnString :
            retTuple += [ filterStr ]
        filterArray = eval( filterStr )
        if returnFilter :
            retTuple += [ filterArray ]
        if returnFrame :
            retTuple += [ self.DF[ filterArray ] ]
        
        if len( retTuple ) == 1 :
            return retTuple[0]
        else :
            return tuple( retTuple )
        

###########
# test data
from datafiletoolbox import loadSimulationResults
# V = loadSimulationResults('/Volumes/git/sampleData/e100/YE_2017_P10_LGR_LA-4HD_VF_30102017.UNSMRY')
V = loadSimulationResults('C:/Users/mcaraya/OneDrive - Cepsa/git/sampleData/e100/YE_2017_P10_LGR_LA-4HD_VF_30102017.UNSMRY')
DF = V[['F?PR','DATE','LA1XST','LANOI3X','WOPR']]
U = V.get_Units(['F?PR','DATE','LANOI3X','LA1XST','WOPR'])
S = DF['WOPT:LA1XST']
Us = U['WOPT:LA1XST']

testS = SimSeries( units=Us , data=S )
print( testS )

testDF = SimDataFrame( data=DF , units=U )
print(testDF)
Z = testDF[-1]
# # Series2Frame(Z)
A = testDF['WOPR:LANOI3X']
B = testDF['WOPR:LA1XST']
F = testDF[['FOPR','FWPR']]
B.units = 'm3/day'
R1 = A + B
R2 = A - B
testDF.find_Keys('!DATE')
testDF['FOPT'] = R1
print(testDF.get_Units('FOPT'))
print(testDF['FOPT'])
print(testDF[-1])
testDF.index.name = 'ABC'
print(testDF)
G = F[['FOPR','FWPR']]
G.units = {'FOPR': 'M3/DAY', 'FWPR': 'MSCF/DAY'}
G = -G
# print(testDF.filter('FOPR<0'))
print(testDF.filter('WOPR>0',returnString=True))
print(testDF.filter('WOPR>0 and .i>10',returnFilter=True))
print(testDF.filter('WOPR>0'))
print(testDF.filter('WOPR>0 and .i>10'))
print(testDF.filter('>10'))
# print(testDF.filter('10<.index<50',returnString=True))
print(testDF.filter(['WOPR>0','WWCT<0.01']))
print(testDF['WOPR>0','WWCT<0.01'])
print(testDF['WWCT'])
print(testDF[500:1500])
print(testDF[500:1500,'FOPT','WOPR'])
print(testDF[0:5,2020,-1,'FOPT','WOPR'])
testDF.set_index('DATE')
print(testDF[0:5,2020,-1,'FOPT','WOPR'])
print(testDF['2038-09-01','2020-01-01'])
print(testDF['< 2020-08-01'])
testDF.set_index('FOPT')
print(testDF['>0 and <500'])
print(testDF['>0','<500'])
print(testDF['>0 and <500 and WOPR>10'])
