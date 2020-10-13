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
from pandas import Series , DataFrame
import numpy as np

from bases.units import unit # to use unit.isUnit method
from bases.units import convertUnit, unitProduct, unitDivision
from bases.units import convertible as convertibleUnits

from datafiletoolbox.common.stringformat import multisplit

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
    if isinstance(aSimSeries, SimSeries) :
        try :
            return SimDataFrame( data=dict( zip( list(aSimSeries.index) , aSimSeries.to_list() ) ) , units=aSimSeries.get_Units() , index=[aSimSeries.name] , dtype=aSimSeries.dtype )
        except :
            return aSimSeries
    if isinstance(aSimSeries, Series) :
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
    
    _metadata = ["units","indexKey","speak"]
    
    def __init__(self, data=None , units=None , index=None , speak=False , *args , **kwargs) :
        Uname = None
        Udict = None
        self.units = None
        self.speak = bool(speak)
        
        indexInput = None
        if 'index' in kwargs and type(kwargs['index']) is not None :
            indexInput = kwargs['index']
        elif len(args) >= 3 and args[2] is not None :
            indexInput = args[2]
        if isinstance(indexInput,(SimSeries,Series)) :
            if type(indexInput.name) is str :
                indexInput = indexInput.name
        if indexInput is None and isinstance(data,(SimSeries,SimDataFrame)) and type(data.indexKey) is str :
            indexInput = data.indexKey
        if indexInput is None and 'indexKey' in kwargs :
            indexInput = kwargs['indexKey']
        self.indexKey = indexInput
        
        if type(units) is dict :
            Udict , units = units , None
            if len(Udict) == 1 :
                if type( Udict[ list(Udict.keys())[0] ] ) is str :
                    Uname = list(Udict.keys())[0]
                    units = Udict[ Uname ]                    
        if type(units) is str :
            self.units = units
        kwargs.pop('indexKey',None) 
        super().__init__(data=data, index=index, *args, **kwargs)
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
            if self.indexKey is not None and other.indexKey is not None and self.indexKey != other.indexKey :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.indexKey+"' != '"+other.indexKey+"'")
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
            if self.indexKey is not None and other.indexKey is not None and self.indexKey != other.indexKey :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.indexKey+"' != '"+other.indexKey+"'")
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
            if self.indexKey is not None and other.indexKey is not None and self.indexKey != other.indexKey :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.indexKey+"' != '"+other.indexKey+"'")
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
            if self.indexKey is not None and other.indexKey is not None and self.indexKey != other.indexKey :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.indexKey+"' != '"+other.indexKey+"'")
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
            if self.indexKey is not None and other.indexKey is not None and self.indexKey != other.indexKey :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.indexKey+"' != '"+other.indexKey+"'")
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
            if self.indexKey is not None and other.indexKey is not None and self.indexKey != other.indexKey :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.indexKey+"' != '"+other.indexKey+"'")
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
            if self.indexKey is not None and other.indexKey is not None and self.indexKey != other.indexKey :
                Warning( "indexes of both SimSeries are not of the same kind:\n   '"+self.indexKey+"' != '"+other.indexKey+"'")
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
            return SimSeries( data=self.as_Series().copy(True) , units=self.units.copy() , dtype=self.dtype , indexKey=self.indexKey )
        return SimSeries( data=self.as_Series().copy(True) , units=self.units , dtype=self.dtype , indexKey=self.indexKey )
    
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
    _metadata = ["units","indexKey","speak"]
    
    def __init__(self , data=None , units=None , index=None , speak=False , *args , **kwargs) :
        self.units = None
        self.speak = bool(speak)
        
        indexInput = None
        if 'index' in kwargs and type(kwargs['index']) is not None :
            indexInput = kwargs['index']
        elif len(args) >= 3 and args[2] is not None :
            indexInput = args[2]
        if isinstance(indexInput,(SimSeries,Series)) :
            if type(indexInput.name) is str :
                indexInput = indexInput.name
        if indexInput is None and isinstance(data,(SimSeries,SimDataFrame)) and type(data.indexKey) is str :
            indexInput = data.indexKey
        if indexInput is None and 'indexKey' in kwargs :
            indexInput = kwargs['indexKey']
        self.indexKey = indexInput
        kwargs.pop('indexKey',None)        
        super().__init__(data=data,index=index,*args, **kwargs)
        if self.units is None :
            if type(units) is str :
                self.units = {}
                for key in list( self.columns ) :
                    self.units[ key ] = units
            if type(units) is list or type(units) is tuple :
                if len(units) == len(self.columns) :
                    self.units = dict( zip( list(self.columns) , units ) )
            if type(units) is dict and len(units)>0 :
                self.units = {}
                for key in list( self.columns ) :
                    if key in units :
                        self.units[key] = units[key]
                    else :
                        self.units[key] = 'UNITLESS'
    
    # @property
    # def _constructor(self):
    #     return SimDataFrame
    
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
        return SimDataFrame( data=result , units=self.units , indexKey=self.indexKey )
    
    def __add__(self,other) :
        # both SimDataFra,es
        if isinstance(other, SimDataFrame) :
            if self.indexKey is not None and other.indexKey is not None and self.indexKey != other.indexKey :
                Warning( "indexes of both SimDataFrames are not of the same kind:\n   '"+self.indexKey+"' != '"+other.indexKey+"'")
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
            return SimDataFrame( data=result , units=selfC.units , indexKey=self.indexKey )
        
        # let's Pandas deal with other types, maintain units and dtype
        result = self.as_DataFrame() + other
        return SimDataFrame( data=result , units=self.units , indexKey=self.indexKey )
    
    def __sub__(self,other) :
        # both SimDataFra,es
        if isinstance(other, SimDataFrame) :
            if self.indexKey is not None and other.indexKey is not None and self.indexKey != other.indexKey :
                Warning( "indexes of both SimDataFrames are not of the same kind:\n   '"+self.indexKey+"' != '"+other.indexKey+"'")
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
            return SimDataFrame( data=result , units=selfC.units , indexKey=self.indexKey )
        
        # let's Pandas deal with other types, maintain units and dtype
        result = self.as_DataFrame() - other
        return SimDataFrame( data=result , units=self.units , indexKey=self.indexKey )
    
    def copy(self) :
        return SimDataFrame( data=self.as_DataFrame().copy(True) , units=self.units.copy() , indexKey=self.indexKey )
    
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

        byIndex = False
        indexFilter = None
        
        if type(key) is str and key not in self.columns :
            if bool( self.find_Keys(key) ) :
                key = list( self.find_Keys(key) )
            else :
                try :
                    return self.filter(key)
                except :
                    raise ValueError ('filter conditions not valid:\n   '+ key) 

        elif type(key) is list :
            keyList , key , filters = key , [] , []
            for each in keyList :
                if type(each) is str and each not in self.columns :
                    if bool( self.find_Keys(each) ) :
                        key += list( self.find_Keys(each) )
                    else :
                        filters += [each]
                elif type(each) is str and each in self.columns :
                    key += [each]
                else :
                    key += list( self.find_Keys(each) )

            if bool(filters) :
                try :
                    indexFilter = self.filter(filters,returnFilter=True)
                except :
                    raise Warning ('filter conditions are not valid:\n   '+ ' and '.join(filters) )
                if not indexFilter.any() :
                    raise Warning ('filter conditions removed every row :\n   '+ ' and '.join(filters) )

        try :
            result = super().__getitem__(key)
        except :
            try :
                result = self.loc[key]
                byIndex = True
            except :
                try :
                    result = self.iloc[key]
                    byIndex = True
                except :
                    result = dict()
        
        if isinstance(result,DataFrame) :
            resultUnits = self.get_Units(result.columns)
            result = SimDataFrame(data=result , units=resultUnits)
        elif isinstance(result,Series) :
            if result.name is None or type(result.name) is not str :
                # this Series is one index for multiple columns
                resultUnits = self.get_Units(result.index)
            else :
                resultUnits = self.get_Units(result.name)
            result = SimSeries(data=result , units=resultUnits)
        
        if byIndex :
            result = Series2Frame(result)
        
        if indexFilter is not None :
            return result[indexFilter]
        
        return result
        
    def __repr__(self) -> str:
        """
        Return a string representation for a particular DataFrame, with Units.
        """
        def thisColumnMaxLen() :
            thisColumn = [None]*len( result[1:-2] )
            for line in range(len(result[1:-2])) :
                rawLine = multisplit( result[1:-1][line] , ['  ',' -'] )
                thisLine = []
                for raw in rawLine :
                    if len(raw.strip(' -')) > 0 :
                        thisLine.append( raw )
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
        if not returnFilter and not returnString :
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
                    filterStr += ' self.index'
                # if key is a column
                elif key in self.columns :
                    filterStr = filterStr.rstrip()
                    filterStr += " self['"+key+"']"
                # key might be a wellname, attribute or a pattern
                elif len( self.find_Keys(key) ) == 1 :
                    filterStr = filterStr.rstrip()
                    filterStr += " self['"+ self.find_Keys(key)[0] +"']"
                elif len( self.find_Keys(key) ) > 1 :
                    filterStr = filterStr.rstrip()
                    filterStr += " self["+ str( list(self.find_Keys(key)) ) +"]"
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
            filterStr = 'self.index ' + filterStr
        elif filterStr[-1] in ['=','>','<','!'] :
            filterStr = filterStr + ' self.index' 
        # close last parethesis and aggregation
        filterStr += ' )' * bool( AndOrNot + bool(PandasAgg) ) + PandasAgg
        # open parenthesis for aggregation, if needed
        if not AndOrNot and bool(PandasAgg) :
            filterStr = '( ' + filterStr
        
        retTuple = []
        
        if returnString :
            retTuple += [ filterStr ]
        if returnFilter :
            retTuple += [ eval( filterStr ) ]
        if returnFrame :
            retTuple += [ self[ eval( filterStr ) ] ]
        
        if len( retTuple ) == 1 :
            return retTuple[0]
        else :
            return tuple( retTuple )
        

if __name__ == '__main__' :
    from datafiletoolbox import loadSimulationResults
    # V = loadSimulationResults('/Volumes/git/sampleData/e100/YE_2017_P10_LGR_LA-4HD_VF_30102017.UNSMRY')
    V = loadSimulationResults('C:/Users/mcaraya/OneDrive - Cepsa/git/sampleData/e100/YE_2017_P10_LGR_LA-4HD_VF_30102017.UNSMRY')
    DF = V[['F?PR','DATE','LANOI3X','LA1XST','WOPR']]
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
    R1 = A + B
    R2 = A - B
    B.units = 'm3/day'
    testDF.find_Keys('!DATE')
    testDF['FOPT'] = R1
    print(testDF.get_Units('FOPT'))
    print(testDF['FOPT'])
    print(testDF[-1])
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
    print(testDF.filter('10<.index<50',returnString=True))
    print(testDF.filter(['WOPR>0','']))
