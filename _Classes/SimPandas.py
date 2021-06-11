#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 11:14:32 2020

@author: martin
"""

__version__ = '0.58.5'
__release__ = 210609
__all__ = ['SimSeries', 'SimDataFrame']

from io import StringIO
from shutil import get_terminal_size
from pandas._config import get_option
from pandas.io.formats import console
from pandas.core import indexing
from os.path import commonprefix
import pandas as pd
import fnmatch
import warnings
from pandas import Series, DataFrame, DatetimeIndex, Timestamp, Index
import numpy as np
import datetime as dt
from warnings import warn
from .._common.units import unit  # to use unit.isUnit method
from .._common.units import convertUnit, unitProduct, unitDivision, convertible as convertibleUnits, unitBase


try :
    from datafiletoolbox import multisplit, isDate, strDate
except :
    try:
        from .._common.stringformat import multisplit, isDate, date as strDate
    except :
        raise ImportError("please install 'datafiletoolbox'.")

_SERIES_WARNING_MSG = """\
    You are passing unitless data to the SimSeries constructor. Currently,
    it falls back to returning a pandas Series. But in the future, we will start
    to raise a TypeError instead."""


def _simseries_constructor_with_fallback(data=None, index=None, units=None, **kwargs):
    """
    A flexible constructor for SimSeries._constructor, which needs to be able
    to fall back to a Series(if a certain operation does not produce
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


def _Series2Frame(aSimSeries) :
    """
    when a row is extracted from a DataFrame, Pandas returns a Series in wich
    the columns of the DataFrame are converted to the indexes of the Series and
    the extracted index from the DataFrame is set as the Name of the Series.

    This function returns the proper DataFrame view of such Series.

    Works with SimSeries as well as with Pandas standard Series
    """
    if isinstance(aSimSeries, DataFrame) :
        return aSimSeries
    if type(aSimSeries) is SimSeries :
        try :
            return SimDataFrame(data=dict(zip(list(aSimSeries.index), aSimSeries.to_list())), units=aSimSeries.get_Units(), index=aSimSeries.columns, speak=aSimSeries.speak, indexName=aSimSeries.index.name, indexUnits=aSimSeries.indexUnits, nameSeparator=aSimSeries.nameSeparator, intersectionCharacter=aSimSeries.intersectionCharacter, autoAppend=aSimSeries.autoAppend)
        except :
            return aSimSeries
    if type(aSimSeries) is Series :
        try :
            return DataFrame(data=dict(zip(list(aSimSeries.index), aSimSeries.to_list())), index=aSimSeries.columns)
        except :
            return aSimSeries

def _cleanAxis(axis=None) :
    if axis is None :
        return 0
    if type(axis) is str and axis.lower() in ['row', 'rows', 'ind', 'index'] :
        return 0
    if type(axis) is str and axis.lower() in ['col', 'cols', 'column', 'columns'] :
        return 1
    if type(axis) is bool :
        return int(axis)
    if type(axis) is float :
        return int(axis)
    return axis

def jitter(df,std=0.10) :
    import numpy as np
    jit = np.random.randn(len(df),len(df.columns))
    jit = ( jit * std ) + 1
    return df*jit

def _stringNewName(newName):
    if len(newName) == 1 :
        return list(newName.values())[0]
    else:
        return '∩'.join(map(str,set(newName.values())))

def typeOfFrame(frame):
    try:
        if frame._isSimSeries:
            return SimSeries
    except:
        try:
            if frame._isSimDataFrame:
                return SimDataFrame
        except:
            if type(frame) is Series:
                return Series
            elif type(frame) is DataFrame:
                return DataFrame
            else:
                raise TypeError('frame is not an instance of Pandas or SimPandas Frames')


class _SimLocIndexer(indexing._LocIndexer):
    def __init__(self, *args):
        self.spd = args[1]
        super().__init__(*args)
        
    def __getitem__(self, *args):
        result = super().__getitem__(*args)
        if isinstance(result,(Series,DataFrame)):
            if type(self.spd) is SimSeries:
                return self.spd._class(data=result, **self.spd._SimParameters)
            
            elif type(self.spd) is SimDataFrame and type(*args) is not tuple and isinstance(result,Series):
                return self.spd._class(data=dict(zip(result.index,result.values)),index=[result.name], **self.spd._SimParameters)
            elif type(self.spd) is SimDataFrame and type(*args) is not tuple and isinstance(result,DataFrame):
                return self.spd._class(data=result, **self.spd._SimParameters)
            elif type(self.spd) is SimDataFrame and type(*args) is tuple and len(*args) > 1 and type(args[0][-1]) in (list,tuple,slice) and isinstance(result,DataFrame):
                return self.spd._class(data=result, **self.spd._SimParameters)
            else:
                result = self.spd._class(data=result.values,index=result.index, **self.spd._SimParameters)
                result.rename(columns=dict(zip(result.columns,self.spd[[args[0][-1]]].columns)),inplace=True)
                result.set_units(self.spd.get_units(self.spd[[args[0][-1]]].columns))
                return result
        else:
            return result


class SimSeries(Series) :
    """
    A Series object designed to store data with units.

    Parameters
    ----------
    data : array-like, dict, scalar value
        The data to store in the SimSeries.
    index : array-like or Index
        The index for the SimSeries.
    units : string or dictionary of units(optional)
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
    _metadata = ["units", "speak", 'indexUnits', 'nameSeparator', 'intersectionCharacter', 'autoAppend', 'spdLocator']  #, 'spdiLocator']

    def __init__(self, data=None, units=None, index=None, name=None, speak=False, indexName=None, indexUnits=None, nameSeparator=None, intersectionCharacter='∩' , autoAppend=False, *args, **kwargs) :
        Uname = None
        Udict = None
        self.units = None
        self.speak = bool(speak)
        self.indexUnits = None
        self.nameSeparator = None
        self.intersectionCharacter = '∩'
        self.autoAppend = False
        self.spdLocator = _SimLocIndexer("loc", self)
        # self.spdiLocator = _SimLocIndexer("iloc", self)

        # validaton
        if isinstance(data, DataFrame) and len(data.columns)>1 :
            raise ValueError("'data' paramanter can be an instance of DataFrame but must have only one column.")

        indexInput = None
        # catch index keyword from input parameters
        if index is not None :
            indexInput = index
        elif 'index' in kwargs and kwargs['index'] is not None :
            indexInput = kwargs['index']
        elif len(args) >= 3 and args[2] is not None :
            indexInput = args[2]
        # if index is a Series, get the name
        elif isinstance(indexInput, Series):
            if type(indexInput.name) is str :
                indexInput = indexInput.name
        # if index is None and data is SimSeries or SimDataFrame get the name
        elif type(data) in [SimSeries, SimDataFrame] and type(data.index.name) is str and len(data.index.name)>0 :
            indexInput = data.index.name
            self.indexUnits = data.indexUnits.copy() if type(data.indexUnits) is dict else data.indexUnits

        # catch units or get from data if it is SimDataFrame or SimSeries
        if type(units) is dict :
            Udict, units = units, None
            if len(Udict) == 1 :
                if type(Udict[ list(Udict.keys())[0] ] ) is str :
                    Uname = list(Udict.keys())[0]
                    units = Udict[ Uname ]
        elif type(units) is str :
            self.units = units
        elif units is None and type(data) is SimSeries :
            if type(data.units) is str:
                units = data.units 
            elif type(data.units) is dict :
                units = data.units.copy() 

        # remove arguments not known by Pandas
        kwargsB = kwargs.copy()
        if name is not None and 'name' in kwargs:
            kwargs.pop('name',None)
        kwargs.pop('columns',None)
        kwargs.pop('indexName', None)
        kwargs.pop('indexUnits', None)
        kwargs.pop('nameSeparator', None)
        kwargs.pop('autoAppend', None)
        # convert to pure Pandas
        if type(data) in [ SimDataFrame, SimSeries ] :
            self.nameSeparator = data.nameSeparator
            data = data.to_Pandas()
        super().__init__(data=data, index=index, *args, **kwargs)

        # set the name of the index
        if (self.index.name is None or(type(self.index.name) is str and len(self.index.name)==0 ) ) and (type(indexInput) is str and len(indexInput)>0 ) :
            self.index.name = indexInput
        # overwrite the index.name with input from the argument indexName
        if indexName is not None and type(indexName) is str and len(indexName.strip())>0 :
            self.set_indexName(indexName)
        elif 'indexName' in kwargsB and type(kwargsB['indexName']) is str and len(kwargsB['indexName'].strip())>0 :
            self.set_indexName(kwargsB['indexName'])

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
        if Udict is not None and self.index.name is not None and self.index.name in Udict :
            self.indexUnits = Udict[self.index.name]
        # overwrite the indexUnits with input from the argument indexName
        if indexUnits is not None and type(indexUnits) is str and len(indexUnits.strip())>0 :
            self.indexUnits = indexUnits
        if 'indexUnits' in kwargsB and type(kwargsB['indexUnits']) is str and len(kwargsB['indexUnits'].strip())>0 :
            self.indexUnits = kwargsB['indexUnits']
        elif 'indexUnits' in kwargsB and type(kwargsB['indexUnits']) is dict and len(kwargsB['indexUnits'])>0 :
            self.indexUnits = kwargsB['indexUnits'].copy()
        if self.indexUnits is not None and self.index.name is not None and len(self.index.name) > 0 and type(self.units) is dict and self.index.name not in self.units:
            self.units[self.index.name] = self.indexUnits

        # get separator for the column names, 'partA'+'separator'+'partB'
        if nameSeparator is not None and type(nameSeparator) is str and len(nameSeparator.strip())>0 :
            self.nameSeparator = nameSeparator
        elif 'nameSeparator' in kwargsB and type(kwargsB['nameSeparator']) is str and len(kwargsB['nameSeparator'].strip())>0 :
            self.set_NameSeparator(kwargsB['nameSeparator'])
        elif (self.nameSeparator is None or self.nameSeparator == '' or self.nameSeparator is False ) and (type(self.name) is str and ':' in self.name ) :
            self.nameSeparator = ':'
        elif self.nameSeparator is None or self.nameSeparator == '' or self.nameSeparator is False :
            self.nameSeparator = ''
        elif self.nameSeparator is True :
            self.nameSeparator = ':'
        else :
            self.nameSeparator = ':'

        if intersectionCharacter is not None and type(intersectionCharacter) is str:
            self.intersectionCharacter = intersectionCharacter

        # catch autoAppend from kwargs
        if autoAppend is not None :
            self.autoAppend = bool(autoAppend)
        elif 'autoAppend' in kwargsB and kwargsB['autoAppend'] is not None :
            self.autoAppend = bool(kwargs['autoAppend'] )
            
        # set the provided name
        if self.name is None and name is not None:
            self.name = name
        if self.name is None and 'columns' in kwargsB and type(kwargsB['columns']) is list and len(kwargsB['columns']) == 1:
            self.name = kwargsB['columns'][0]
        if self.name is None and 'columns' in kwargsB and type(kwargsB['columns']) is str and len(kwargsB['columns'].strip()) > 0:
            self.name = kwargsB['columns'].strip()
    
    @property
    def _constructor(self):
        return _simseries_constructor_with_fallback
    @property
    def _constructor_expanddim(self):
        # from datafiletoolbox.SimPandas.simframe import SimDataFrame
        return SimDataFrame
    
    @property
    def _SimParameters(self) :
        return {'units':self.units.copy() if type(self.units) is dict else self.units,
                'name':self.name,
                'speak':self.speak,
                'indexName':self.index.name,
                'indexUnits':self.indexUnits,
                'nameSeparator':self.nameSeparator,
                'intersectionCharacter':self.intersectionCharacter,
                'autoAppend':self.autoAppend}
    
    @property
    def loc(self) -> _SimLocIndexer:
        """
        wrapper for .loc indexing
        """
        return self.spdLocator

    # @property
    # def iloc(self) -> _SimLocIndexer:
    #     """
    #     wrapper for .iloc indexing
    #     """
    #     return self.spdiLocator
    
    @property
    def _class(self):
        return SimSeries

    def __getitem__(self, key=None) :
        if key is None :
            return self
        if type(key) is str and key.strip() == self.name and not key.strip() in self.index :
            return self
        else :
            try :
                return self.loc[key]
            except :
                try :
                    return self.iloc[key]
                except :
                    raise KeyError("the requested Key is not a valid index or name")

    def __contains__(self, item) :
        if item in self.columns :
            return True
        elif item in self.index :
            return True
        else :
            return False

    def set_index(self, name) :
        self.set_indexName(name)

    def set_indexName(self, name) :
        if type(name) is str and len(name.strip())>0 :
            self.index.name = name.strip()

    def set_indexUnits(self, units) :
        if type(units) is str and len(units.strip())>0 :
            self.indexUnits = units.strip()
        elif type(units) is dict and len(units)>0 :
            self.indexUnits = units

    def set_NameSeparator(self, separator) :
        if type(separator) is str and len(separator) > 0 :
            self.nameSeparator = separator

    def get_NameSeparator(self) :
        if self.nameSeparator in [None, '', False] :
            warn(" NameSeparator is not defined.")
            return ''
        else :
            return self.nameSeparator

    def to_Pandas(self) :
        return self.to_Series()

    def to_pandas(self) :
        return self.to_Series()

    def to_Series(self) :
        return Series(self).copy()

    def as_Series(self) :
        return Series(self)
    
    def to_SimDataFrame(self):
        return SimDataFrame(data=self)

    @property
    def sdf(self) :
        return self.to_SimDataFrame()

    @property
    def SDF(self) :
        return self.to_SimDataFrame()

    @property
    def df(self) :
        return self.to_SimDataFrame().to_DataFrame()

    @property
    def DF(self) :
        return self.to_SimDataFrame().to_DataFrame()

    @property
    def Series(self) :
        return self.as_Series()

    @property
    def s(self) :
        return self.as_Series()

    @property
    def S(self) :
        return self.as_Series()

    @property
    def columns(self) :
        return Index([self.name] )

    @property
    def right(self) :
        if self.nameSeparator in [None, '', False] :
            return tuple(self.columns)
        objs = []
        for each in list(self.columns) :
            if self.nameSeparator in each :
                objs += [each.split(self.nameSeparator)[-1]]
            else :
                objs += [each]
        return tuple(set(objs))

    @property
    def left(self) :
        if self.nameSeparator in [None, '', False] :
            return tuple(self.columns)
        objs = []
        for each in list(self.columns) :
            if self.nameSeparator in each :
                objs += [each.split(self.nameSeparator)[0]]
            else :
                objs += [each]
        return tuple(set(objs))
    
    def renameRight(self, inplace=False) :
        if self.nameSeparator in [None, '', False] :
            return self  # raise ValueError("name separator must not be None")
        objs = {}
        for each in list(self.columns ) :
            if self.nameSeparator in each :
                objs[each] = each.split(self.nameSeparator )[-1]
                # self.units[ each.split(self.nameSeparator )[-1] ] = self.units[ each ]
                # del(self.units[each])
            else :
                objs[each] = each
        if len(self.columns) == 1 :
            objs = list(objs.values())[0]
        if inplace :
            self.rename(objs, inplace=True)
        else :
            return self.rename(objs, inplace=False)

    def renameLeft(self, inplace=False) :
        if self.nameSeparator in [None, '', False] :
            return self  # raise ValueError("name separator must not be None")
        objs = {}
        for each in list(self.columns ) :
            if self.nameSeparator in each :
                objs[each] = each.split(self.nameSeparator)[0]
                # self.units[ each.split(self.nameSeparator )[0] ] = self.units[ each ]
                # del(self.units[each])
            else :
                objs[each] = each
        if len(self.columns) == 1 :
            objs = list(objs.values())[0]
        if inplace :
            self.rename(objs, inplace=True)
        else :
            return self.rename(objs, inplace=False)

    def _CommonRename(self, SimSeries1, SimSeries2=None, LR=None) :
        SDF1, SDF2 = SimSeries1, SimSeries2

        cha = self.intersectionCharacter
        
        if LR is not None :
            LR = LR.upper()
            if LR not in 'LR' :
                LR = None

        if SDF2 is None :
            SDF1, SDF2 = self, SDF1

        if type(SDF1) is not SimSeries :
            raise TypeError("both series to be compared must be SimSeries.")
        if type(SDF2) is not SimSeries :
            raise TypeError("both series to be compared must be SimSeries.")

        if SDF1.nameSeparator is None or SDF2.nameSeparator is None :
            raise ValueError("the 'nameSeparator' must not be empty in both SimSeries.")

        if LR == 'L' or (LR is None and len(SDF1.left) == 1 and len(SDF2.left) == 1 ) :
            SDF2C = SDF2.copy()
            SDF2C.renameRight(inplace=True)
            SDF1C = SDF1.copy()
            SDF1C.renameRight(inplace=True)
            commonNames = {}
            for c in SDF1C.columns :
                if c in SDF2C.columns :
                    commonNames[c] = SDF1.left[0] + cha + SDF2.left[0] + SDF1.nameSeparator + c
                else :
                    commonNames[c] = SDF1.left[0] + SDF1.nameSeparator + c
            for c in SDF2C.columns :
                if c not in SDF1C.columns :
                    commonNames[c] = SDF2.left[0] + SDF1.nameSeparator + c
            if LR is None and len(commonNames) > 1 :
                alternative = self._CommonRename(SDF1, SDF2, LR='R')
                if len(alternative[2]) < len(commonNames) :
                    return alternative

        elif LR == 'R' or (LR is None and len(SDF1.right) == 1 and len(SDF2.right) == 1 ) :
            SDF2C = SDF2.copy()
            SDF2C.renameLeft(inplace=True)
            SDF1C = SDF1.copy()
            SDF1C.renameLeft(inplace=True)
            commonNames = {}
            for c in SDF1C.columns :
                if c in SDF2C.columns :
                    commonNames[c] = c + SDF1.nameSeparator + SDF1.right[0] + cha + SDF2.right[0]
                else :
                    commonNames[c] = c + SDF1.nameSeparator + SDF1.right[0]
            for c in SDF2C.columns :
                if c not in SDF1C.columns :
                    commonNames[c] = c + SDF1.nameSeparator + SDF2.right[0]
            if LR is None and len(commonNames) > 1 :
                alternative = self._CommonRename(SDF1, SDF2, LR='L')
                if len(alternative[2]) < len(commonNames) :
                    return alternative
        return SDF1C, SDF2C, commonNames

    def rename(self,index=None, **kwargs) :
        """
        wrapper of rename function from Pandas.

        Alter Series index labels or name.

        Function / dict values must be unique (1-to-1). 
        Labels not contained in a dict / Series will be left as-is. 
        Extra labels listed don’t throw an error.

        Alternatively, change Series.name with a scalar value.

        See the user guide for more.

        Parameters
        axis{0 or “index”}
        Unused. Accepted for compatibility with DataFrame method only.

        indexscalar, hashable sequence, dict-like or function, optional
        Functions or dict-like are transformations to apply to the index. 
        Scalar or hashable sequence-like will alter the Series.name attribute.

        **kwargs
        Additional keyword arguments passed to the function. Only the “inplace” keyword is used.

        Returns
        Series or None
        Series with index labels or name altered or None if inplace=True.
        """
        if type(index) is dict :
            if len(index) == 1 and list(index.keys()) not in self.index :
                return self.rename(list(index.values())[0],**kwargs)
            cBefore = list(self.index)
            if 'inplace' in kwargs and kwargs['inplace'] :
                super().rename(**kwargs)
                cAfter = list(self.index)
            else :
                catch = super().rename(**kwargs)
                cAfter = list(catch.index)
            newUnits = {}
            for i in range(len(cBefore)) :
                newUnits[cAfter[i]] = self.units[cBefore[i]]
            if 'inplace' in kwargs and kwargs['inplace'] :
                self.units = newUnits
                return None
            else :
                catch.units = newUnits
                return catch
        elif type(index) is str :
            if 'inplace' in kwargs and kwargs['inplace'] :
                self.name = index.strip()
                return None
            else :
                catch = self.copy()
                catch.name = index
                return catch

    def to(self, units) :
        """
        returns the series converted to the requested units if possible,
        else returns None
        """
        return self.convert(units)

    def convert(self, units) :
        """
        returns the series converted to the requested units if possible,
        else returns None
        """
        if type(units) is str and type(self.units) is str :
            if convertibleUnits(self.units, units) :
                params = self._SimParameters
                params['units'] = units
                return SimSeries(data=convertUnit(self.S, self.units, units, self.speak ), **params)
        if type(units) is str and len(set(self.units.values())) == 1 :
            params = self._SimParameters
            params['units'] = units
            return SimSeries(data=convertUnit(self.S, list(set(self.units.values()))[0], units, self.speak ), **params )

    def resample(self, rule, axis=0, closed=None, label=None, convention='start', kind=None, loffset=None, base=None, on=None, level=None, origin='start_day', offset=None) :
        axis = _cleanAxis(axis)
        return SimSeries(data=self.S.resample(rule, axis=axis, closed=closed, label=label, convention=convention, kind=kind, loffset=loffset, base=base, on=on, level=level, origin=origin, offset=offset), **self._SimParameters )

    def reindex(self, index=None, **kwargs) :
        """
        wrapper for pandas.Series.reindex

        index : array-like, optional
            New labels / index to conform to, should be specified using keywords.
            Preferably an Index object to avoid duplicating data.
        """
        return SimSeries(data=self.S.reindex(index=index, **kwargs), **self._SimParameters )  # units=self.units, speak=self.speak, indexUnits=self.indexUnits, nameSeparator=self.nameSeparator )


    def dropna(self, axis=0, inplace=False, how=None) :
        axis = _cleanAxis(axis)
        return SimSeries(data=self.S.dropna(axis=axis, inplace=inplace, how=how), **self._SimParameters )

    def drop(self, labels=None, axis=0, index=None, columns=None, level=None, inplace=False, errors='raise') :
        axis = _cleanAxis(axis)
        return SimSeries(data=self.S.drop(labels=labels, axis=axis, index=index, columns=columns, level=level, inplace=inplace, errors='errors'), **self._SimParameters )

    @property
    def wells(self) :
        objs = []
        if type(self.name) is str :
            if self.nameSeparator in self.name and self.name[0] == 'W' :
                objs = [self.name.split(self.nameSeparator )[-1]]
        elif type(self.index[-1]) is str :
            for each in list(self.index ) :
                if self.nameSeparator in each and each[0] == 'W' :
                    objs += [each.split(self.nameSeparator )[-1]]
        return tuple(set(objs))

    def get_Wells(self, pattern=None) :
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
        if pattern is not None and type(pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        if pattern is None :
            return tuple(self.wells)
        else:
            return tuple(fnmatch.filter(self.wells, pattern ) )

    @property
    def groups(self) :
        if self.nameSeparator in [None, '', False] :
            return []
        objs = []
        if type(self.name) is str :
            if self.nameSeparator in self.name and self.name[0] == 'G' :
                objs = [self.name.split(self.nameSeparator )[-1]]
        elif type(self.index[-1]) is str :
            for each in list(self.index ) :
                if self.nameSeparator in each and each[0] == 'G' :
                    objs += [each.split(self.nameSeparator )[-1]]
        return tuple(set(objs))

    def get_Groups(self, pattern=None) :
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
        if pattern is not None and type(pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        if pattern is None :
            return self.groups
        else:
            return tuple(fnmatch.filter(self.groups, pattern ) )

    @property
    def regions(self) :
        if self.nameSeparator in [None, '', False] :
            return []
        objs = []
        if type(self.name) is str :
            if self.nameSeparator in self.name and self.name[0] == 'R' :
                objs = [self.name.split(self.nameSeparator )[-1]]
        elif type(self.index[-1]) is str :
            for each in list(self.index ) :
                if self.nameSeparator in each and each[0] == 'R' :
                    objs += [each.split(self.nameSeparator )[-1]]
        return tuple(set(objs))

    def get_Regions(self, pattern=None):
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
        if pattern is not None and type(pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        if pattern is None :
            return self.regions
        else:
            return tuple(fnmatch.filter(self.regions, pattern ) )

    @property
    def attributes(self) :
        if self.nameSeparator in [None, '', False] :
            return tuple(self.columns )
        atts = {}
        for each in list(self.get_Keys() ) :
            if self.nameSeparator in each :
                if each.split(self.nameSeparator )[0] in atts :
                    atts[each.split(self.nameSeparator )[0]] += [each.split(self.nameSeparator )[-1]]
                else :
                    atts[each.split(self.nameSeparator )[0]] = [each.split(self.nameSeparator )[-1]]
            else :
                if each not in atts :
                    atts[each] = []
        for att in atts :
            atts[att] = list(set(atts[att]))
        return atts

    @property
    def properties(self) :
        if len(self.attributes.keys()) > 0 :
            return tuple(self.attributes.keys())
        else :
            return tuple()

    def get_Attributes(self, pattern=None) :
        """
        Will return a dictionary of all the attributes names in case as keys
        and their related items as values.

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
            return tuple(fnmatch.filter(tuple(self.attributes.keys()), pattern ) )

    def get_Keys(self, pattern=None) :
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
        if pattern is not None and type(pattern ) is not str :
            raise TypeError('pattern argument must be a string.\nreceived '+str(type(pattern))+' with value '+str(pattern))
        if type(self.name) is str :
            keys =(self.name, )
        else :
            keys = tuple(self.index )
        if pattern is None :
            return keys
        else:
            return tuple(fnmatch.filter(keys, pattern ) )

    def diff(self, periods=1, forward=False):
        if type(periods) is bool:
            periods, forward = 1, periods
        if forward:
            return SimSeries(data=-1*self.S.diff(periods=-1*periods), **self._SimParameters )
        else:
            return SimSeries(data=self.S.diff(periods=periods), **self._SimParameters ) 
        
    def __neg__(self) :
        result = -self.as_Series()
        return SimSeries(data=result, **self._SimParameters )

    def __add__(self, other) :
        params = self._SimParameters
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                newName = _stringNewName(self._CommonRename(other)[2])
                if self.units == other.units :
                    result = self.S.add(other.S, fill_value=0)
                elif convertibleUnits(other.units, self.units ) :
                    otherC = convertUnit(other, other.units, self.units, self.speak )
                    result = self.S.add(otherC.S, fill_value=0)
                elif convertibleUnits(self.units, other.units ) :
                    selfC = convertUnit(self, self.units, other.units, self.speak )
                    result = other.S.add(selfC.S, fill_value=0)
                    params['units'] = other.units
                else :
                    result = self.S.add(other.S, fill_value=0)
                    params['units'] = self.units+'+'+other.units
                params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
                params['name'] = newName
                return SimSeries(data=result, **params)
            else :
                raise NotImplementedError

        # other is Pandas Series
        elif isinstance(other, Series) :
            result = self.S.add(other, fill_value=0)
            newName = _stringNewName(self._CommonRename(SimSeries(other, **self._SimParameters))[2])
            params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
            params['name'] = newName
            return SimSeries(data=result, **params)
            
        # let's Pandas deal with other types, maintain units, dtype and name
        result = self.as_Series() + other
        params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
        return SimSeries(data=result, **params)

    def __radd__(self, other) :
        return self.__add__(other)

    def __sub__(self, other) :
        params = self._SimParameters
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                newName = _stringNewName(self._CommonRename(other)[2])
                if self.units == other.units :
                    result = self.sub(other, fill_value=0)
                elif convertibleUnits(other.units, self.units ) :
                    otherC = convertUnit(other, other.units, self.units, self.speak)
                    result = self.sub(otherC, fill_value=0)
                elif convertibleUnits(self.units, other.units ) :
                    selfC = convertUnit(self, self.units, other.units, self.speak)
                    result = selfC.sub(other, fill_value=0)
                    params['units'] = other.units
                else :
                    result = self.sub(other, fill_value=0)
                    params['units'] = self.units+'-'+other.units
                params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
                params['name'] = newName
                return SimSeries(data=result, **params)
            else :
                raise NotImplementedError

        # other is Pandas Series
        elif isinstance(other, Series) :
            result = self.S.sub(other, fill_value=0)
            newName = _stringNewName(self._CommonRename(SimSeries(other, **self._SimParameters))[2])
            params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
            params['name'] = newName
            return SimSeries(data=result, **params)
        
        # let's Pandas deal with other types, maintain units and dtype
        result = self.as_Series() - other
        params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
        return SimSeries(data=result, **params)

    def __rsub__(self, other) :
        return self.__neg__().__add__(other)

    def __mul__(self, other) :
        params = self._SimParameters
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                params['units'] = unitProduct(self.units, other.units)
                newName = _stringNewName(self._CommonRename(other)[2])
                if self.units == other.units :
                    result = self.mul(other)
                elif convertibleUnits(other.units, self.units):
                    otherC = convertUnit(other, other.units, self.units, self.speak )
                    result = self.mul(otherC)
                elif convertibleUnits(self.units, other.units):
                    selfC = convertUnit(self, self.units, other.units, self.speak )
                    result = other.mul(selfC)
                    params['units'] = unitProduct(other.units, self.units)
                elif convertibleUnits(other.units, unitBase(self.units)):
                    otherC = convertUnit(other, other.units, unitBase(self.units), self.speak )
                    result = self.mul(otherC)
                elif convertibleUnits(self.units, unitBase(other.units)):
                    selfC = convertUnit(self, self.units, unitBase(other.units), self.speak )
                    result = other.mul(selfC)
                    params['units'] = unitProduct(other.units, self.units)
                else :
                    result = self.mul(other)
                    params['units'] = self.units + '*' + other.units
                params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
                params['name'] = newName
                return SimSeries(data=result, **params)
            else :
                raise NotImplementedError

        # let's Pandas deal with other types(types with no units), maintain units and dtype
        result = self.as_Series() * other
        params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
        return SimSeries(data=result, **params )

    def __rmul__(self, other) :
        return self.__mul__(other)

    def __truediv__(self, other) :
        params = self._SimParameters
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                newName = _stringNewName(self._CommonRename(other)[2])
                params['units'] = unitDivision(self.units, other.units)
                if self.units == other.units :
                    result = self.truediv(other)
                elif convertibleUnits(other.units, self.units) :
                    otherC = convertUnit(other, other.units, self.units, self.speak )
                    result = self.truediv(otherC)
                elif convertibleUnits(self.units, other.units) :
                    selfC = convertUnit(self, self.units, other.units, self.speak )
                    result = selfC.truediv(other)
                    params['units'] = unitDivision(other.units, self.units)
                elif convertibleUnits(other.units, unitBase(self.units)):
                    otherC = convertUnit(other, other.units, unitBase(self.units), self.speak )
                    result = self.truediv(otherC)
                elif convertibleUnits(self.units, unitBase(other.units)):
                    selfC = convertUnit(self, self.units, unitBase(other.units), self.speak )
                    result = selfC.truediv(other)
                    params['units'] = unitDivision(other.units, self.units)
                else :
                    result = self.truediv(other)
                    params['units'] = self.units + '/' + other.units
                params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
                params['name'] = newName
                return SimSeries(data=result, **params)
            else :
                raise NotImplementedError

        # let's Pandas deal with other types(types with no units), maintain units and dtype
        result = self.as_Series() / other
        params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
        return SimSeries(data=result, **params)

    def __rtruediv__(self, other) :
        return self.__pow__(-1).__mul__(other)

    def __floordiv__(self, other) :
        params = self._SimParameters
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                params['units'] = unitDivision(self.units, other.units)
                newName = _stringNewName(self._CommonRename(other)[2])
                if self.units == other.units :
                    result = self.floordiv(other)
                elif convertibleUnits(other.units, self.units ) :
                    otherC = convertUnit(other, other.units, self.units, self.speak )
                    result = self.floordiv(otherC)
                elif convertibleUnits(self.units, other.units ) :
                    selfC = convertUnit(self, self.units, other.units, self.speak )
                    result = other.floordiv(selfC)
                    params['units'] = unitDivision(other.units, self.units)
                elif convertibleUnits(other.units, unitBase(self.units) ) :
                    otherC = convertUnit(other, other.units, unitBase(self.units), self.speak )
                    result = self.floordiv(otherC)
                elif convertibleUnits(self.units, unitBase(other.units)) :
                    selfC = convertUnit(self, self.units, unitBase(other.units), self.speak )
                    result = other.floordiv(selfC)
                    params['units'] = unitDivision(other.units, self.units)
                else :
                    result = self.floordiv(other)
                    params['units'] = self.units + '/' + other.units
                params['dtype'] = result.dtype  # self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
                params['name'] = newName
                return SimSeries(data=result, **params)
            else :
                raise NotImplementedError

        # let's Pandas deal with other types(types with no units), maintain units and dtype
        result = self.as_Series() // other
        params['dtype'] = result.dtype
        return SimSeries(data=result, **params)

    def __rfloordiv__(self, other) :
        return self.__pow__(-1).__mul__(other).__int__()

    def __mod__(self, other) :
        params = self._SimParameters
        # both are SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                newName = _stringNewName(self._CommonRename(other)[2])
                if self.units == other.units :
                    result = self.mod(other)
                elif convertibleUnits(other.units, self.units ) :
                    otherC = convertUnit(other, other.units, self.units, self.speak )
                    result = self.mod(otherC)
                elif convertibleUnits(self.units, other.units ) :
                    selfC = convertUnit(self, self.units, other.units, self.speak )
                    result = other.mod(selfC)
                    params['units'] = other.units
                else :
                    result = self.mod(other)
                params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
                params['name'] = newName
                return SimSeries(data=result, **params)
            else :
                raise NotImplementedError

        # let's Pandas deal with other types, maintain units and dtype
        result = self.as_Series() % other
        params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
        return SimSeries(data=result, **params)

    def __pow__(self, other) :
        params = self._SimParameters
        # both SimSeries
        if isinstance(other, SimSeries) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimSeries are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            if type(self.units) is str and type(other.units) is str :
                params['units'] = self.units+'^'+other.units
                newName = _stringNewName(self._CommonRename(other)[2])
                if self.units == other.units :
                    result = self.pow(other)
                elif convertibleUnits(other.units, self.units ) :
                    otherC = convertUnit(other, other.units, self.units, self.speak )
                    result = self.pow(otherC)
                    params['units'] = self.units+'^'+self.units
                elif convertibleUnits(self.units, other.units ) :
                    selfC = convertUnit(self, self.units, other.units, self.speak )
                    result = other.pow(selfC)
                    params['units'] = other.units+'^'+other.units
                else :
                    result = self.pow(other)
                params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
                params['name'] = newName
                return SimSeries(data=result, **params )
            else :
                raise NotImplementedError

        # let's Pandas deal with other types(types with no units), maintain units and dtype
        result = self.as_Series() ** other
        params['dtype'] = self.dtype if (result.astype(self.dtype) == result).all() else result.dtype
        return SimSeries(data=result, **params)

    def __int__(self) :
        return SimSeries(data=self.S.astype(int), **self._SimParameters)
    
    def __abs__(self) :
        return SimSeries(data=abs(self.S), **self._SimParameters)

    def __repr__(self) -> str :
        """
        Return a string representation for a particular Series, with Units.
        """
        # from Pandas Series
        buf = StringIO("")
        width, height = get_terminal_size()
        max_rows =(
            height
            if get_option("display.max_rows") == 0
            else get_option("display.max_rows")
        )
        min_rows =(
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
                i, f = 0, 0
                while i < len(keys) :
                    f = keys.index(' ', i)
                    key = keys[i:f]
                    if key == '...' :
                        i = len(keys)
                        continue
                    while key not in self.index and f <= len(keys):
                        f = keys.index(' ', f+1) if ' ' in keys[f+1:] else len(keys)+1
                        key = keys[i:f]
                    if key not in self.index :
                        i = len(keys)
                        continue
                    if key in self.units and self.units[key] is not None:
                        result[n] += '    ' + self.units[key].strip()
                    i = len(keys)
            result = '\n'.join(result)
            return '\n' + result
        else:
            return result

    def get_units(self, items=None) :
        return self.get_Units()
    
    def get_Units(self, items=None) :
        if type(self.units) is str and type(self.name) is str :
            uDic = { str(self.name) : self.units }
        elif type(self.units) is dict :
            uDic = {}
            for each in self.index :
                if each in self.units :
                    uDic[each] = self.units[each]
                else :
                    uDic[each] = 'UNITLESS'
        elif self.units is None:
            return 'UNITLESS'
        else:
            return self.units
        return uDic
    
    def set_units(self,units,item=None):
        """
        Alias of .set_Units method.
        This method can be used to define the units related to the values of a column (item).

        Parameters
        ----------
        units : str or list of str
            the units to be assigned
        item : str, optional
            The name of the column to apply the units. 
            The default is None. In this case the unit

        Raises
        ------
        ValueError
            when units can't be applied.
        TypeError
            when units or item has the wrong format.

        Returns
        -------
        None.

        """
        return self.set_Units(units=units,item=item)
    
    def set_Units(self,units,item=None):
        """
        This method can be used to define the units related to the values of a column (item).

        Parameters
        ----------
        units : str or list of str
            the units to be assigned
        item : str, optional
            The name of the column to apply the units. 
            The default is None. In this case the unit

        Raises
        ------
        ValueError
            when units can't be applied.
        TypeError
            when units or item has the wrong format.

        Returns
        -------
        None.

        """
        if item is not None and item not in self.columns:
            raise ValueError("the required item '" + str(item) + "' is not in this SimSeries")
            
        if self.units is None or type(self.units) is str:
            if units is None:
                self.units = None
            elif type(units) is str:
                self.units = units.strip()
            else:
                raise TypeError("units must be a string.")
                
        elif type(self.units) is dict:
            if type(units) in [list,tuple]:
                if type(item) in [list,tuple]:
                    if len(item) == len(units):
                        return self.set_Units( dict(zip(item,units)) )
                    else:
                        raise ValueError("both units and item must have the same length.")
                elif item is None:
                    if len(units) == len(self.columns):
                        return self.set_Units( dict(zip(list(self.columns),units)) )
                    else:
                        raise ValueError("units list must be the same length of columns in the SimSeries or must be followed by a list of items.")
                else:
                    raise TypeError("if units is a list, items must be a list of the same length.")
                
            if item is None and len(self.columns) > 1:
                raise ValueError("More than one column in this SimSeries, item must not be None")
            elif item is None and len(self.columns) == 1:
                return self.set_Units(units,[list(self.columns)[0]])
            elif item is not None:
                if item in self.columns:
                    if units is None:
                        self.units[item] = None
                    elif type(units) is str:
                        self.units[item] = units.strip()
                    else:
                        raise TypeError("units must be a string.")
                if item == self.index.name:
                    self.indexUnits = units.strip()
                    self.units[item] = units.strip()
                if item in self.index.names:
                    self.units[item] = units.strip()

    def get_UnitsString(self, items=None) :
        if len(self.get_Units(items)) == 1 :
            return list(self.get_Units(items).values())[0]
        elif len(set(self.get_Units(items).values() )) == 1 :
            return list(set(self.get_Units(items).values() ))[0]

    def copy(self) :
        if type(self.units) is dict :
            params = self._SimParameters
            params['units'] = self.units.copy()
            return SimSeries(data=self.as_Series().copy(True), **params)
        return SimSeries(data=self.as_Series().copy(True), **self._SimParameters )

    def filter(self, conditions=None, **kwargs) :
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
            returnString = bool(kwargs['returnString'] )
        returnFilter = False
        if 'returnFilter' in kwargs :
            returnFilter = bool(kwargs['returnFilter'] )
        returnFrame = False
        if 'returnFrame' in kwargs :
            returnFrame = bool(kwargs['returnFrame'] )
        if 'returnSeries' in kwargs :
            returnFrame = bool(kwargs['returnSeries'] )
        if not returnFilter and not returnString and('returnSeries' not in kwargs or 'returnFrame' not in kwargs ) :
            returnFrame = True

        specialOperation = ['.notnull', '.null', '.isnull', '.abs']
        numpyOperation = ['.sqrt', '.log10', '.log2', '.log', '.ln']
        pandasAggregation = ['.any', '.all']
        PandasAgg = ''

        def KeyToString(filterStr, key, PandasAgg) :
            if len(key) > 0 :
                # catch particular operations performed by Pandas
                foundSO, foundNO = '', ''
                if key in specialOperation :
                    if filterStr[-1] == ' ' :
                        filterStr = filterStr.rstrip()
                    filterStr += key+'()'
                else :
                    for SO in specialOperation :
                        if key.strip().endswith(SO) :
                            key = key[:-len(SO)]
                            foundSO =(SO if SO != '.null' else '.isnull' ) + '()'
                            break
                # catch particular operations performed by Numpy
                if key in numpyOperation :
                    raise ValueError("wrong syntax for '"+key+"(blank space before) in:\n   "+conditions)
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
                if key in ['.i', '.index'] :
                    filterStr = filterStr.rstrip()
                    filterStr += ' self.S.index'
                # if key is a column
                elif key in self.columns :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.S['"+key+"']"
                # key might be a wellname, attribute or a pattern
                elif len(self.find_Keys(key) ) == 1 :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.S['"+ self.find_Keys(key)[0] +"']"
                elif len(self.find_Keys(key) ) > 1 :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.S["+ str(list(self.find_Keys(key)) ) +"]"
                    PandasAgg = '.any(axis=1)'
                else :
                    filterStr += ' ' + key
                filterStr = filterStr.rstrip()
                filterStr += foundSO + foundNO
                key = ''
            return filterStr, key, PandasAgg

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
            conditions = conditions.replace(' and ', ' & ')
        if ' or ' in conditions :
            conditions = conditions.replace(' or ', ' | ')
        if ' not ' in conditions :
            conditions = conditions.replace(' not ', ' ~ ')
        if '&' in conditions :
            AndOrNot = True
        elif '|' in conditions :
            AndOrNot = True
        elif '~' in conditions :
            AndOrNot = True

        # create Pandas compatible condition string
        filterStr =  ' ' + '('*AndOrNot
        key = ''
        cond, oper = '', ''
        i = 0
        while i < len(conditions) :

            # catch logital operators
            if conditions[i] in ['&', "|", '~'] :
                filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
                filterStr = filterStr.rstrip()
                filterStr += ' )' + PandasAgg + ' ' + conditions[i] + '('
                PandasAgg = ''
                i += 1
                continue

            # catch enclosed strings
            if conditions[i] in ['"', "'", '['] :
                if conditions[i] in ['"', "'"] :
                    try :
                        f = conditions.index(conditions[i], i+1 )
                    except :
                        raise ValueError('wring syntax, closing ' + conditions[i] + ' not found in:\n   '+conditions)
                else :
                    try :
                        f = conditions.index(']', i+1 )
                    except :
                        raise ValueError("wring syntax, closing ']' not found in:\n   "+conditions)
                if f > i+1 :
                    key = conditions[i+1:f]
                    filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
                    i = f+1
                    continue

            # pass blank spaces
            if conditions[i] == ' ' :
                filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
                if len(filterStr) > 0 and filterStr[-1] != ' ' :
                    filterStr += ' '
                i += 1
                continue

            # pass parenthesis
            if conditions[i] in ['(', ')'] :
                filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
                filterStr += conditions[i]
                i += 1
                continue

            # catch conditions
            if conditions[i] in ['=', '>', '<', '!'] :
                cond = ''
                f = i+1
                while conditions[f] in ['=', '>', '<', '!'] :
                    f += 1
                cond = conditions[i:f]
                if cond == '=' :
                    cond = '=='
                elif cond in ['=>', '=<', '=!'] :
                    cond = cond[::-1]
                elif cond in ['><', '<>'] :
                    cond = '!='
                filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
                filterStr = filterStr.rstrip()
                filterStr += ' ' + cond
                i += len(cond)
                continue

            # catch operations
            if conditions[i] in ['+', '-', '*', '/', '%', '^'] :
                oper = ''
                f = i+1
                while conditions[f] in ['+', '-', '*', '/', '%', '^'] :
                    f += 1
                oper = conditions[i:f]
                oper = oper.replace('^', '**')
                filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
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
        if filterStr[0] in ['=', '>', '<', '!'] :
            filterStr = 'self.S.index ' + filterStr
        elif filterStr[-1] in ['=', '>', '<', '!'] :
            filterStr = filterStr + ' self.S.index'
        # close last parethesis and aggregation
        filterStr += ' )' * bool(AndOrNot + bool(PandasAgg) ) + PandasAgg
        # open parenthesis for aggregation, if needed
        if not AndOrNot and bool(PandasAgg) :
            filterStr = '(' + filterStr

        retTuple = []

        if returnString :
            retTuple += [ filterStr ]
        filterArray = eval(filterStr )
        if returnFilter :
            retTuple += [ filterArray ]
        if returnFrame :
            retTuple += [ self.S[ filterArray ] ]

        if len(retTuple ) == 1 :
            return retTuple[0]
        else :
            return tuple(retTuple )

    def sort_values(self, axis=0, ascending=True, inplace=False, kind='quicksort', na_position='last', ignore_index=False, key=None) :
        if inplace :
            self.S.sort_values(axis=axis, ascending=ascending, inplace=True, kind=kind, na_position=na_position, ignore_index=ignore_index, key=key)
            return None
        else :
            return SimSeries(data=self.S.sort_values(axis=axis, ascending=ascending, inplace=False, kind=kind, na_position=na_position, ignore_index=ignore_index, key=key), **self._SimParameters)

    def jitter(self,std=0.10) :
        """
        add jitter the values of the SimSeries
        """
        return jitter(self,std)
    
    def daily(self, outBy='mean') :
        """
        return a Series with a single row per day.
        index must be a date type.

        available gropuing calculations are:
            first : keeps the fisrt row per day
            last : keeps the last row per day
            max : returns the maximum value per year
            min : returns the minimum value per year
            mean or avg : returns the average value per year
            median : returns the median value per month
            std : returns the standard deviation per year
            sum : returns the summation of all the values per year
            count : returns the number of rows per year
        """
        return self.to_SimDataFrame().daily(outBy=outBy).to_SimSeries()

    def monthly(self, outBy='mean') :
        """
        return a dataframe with a single row per month.
        index must be a date type.

        available gropuing calculations are:
            first : keeps the fisrt row per month
            last : keeps the last row per month
            max : returns the maximum value per month
            min : returns the minimum value per month
            mean or avg : returns the average value per month
            median : returns the median value per month
            std : returns the standard deviation per month
            sum : returns the summation of all the values per month
            count : returns the number of rows per month
        """
        return self.to_SimDataFrame().monthly(outBy=outBy).to_SimSeries()

    def yearly(self, outBy='mean') :
        """
        return a dataframe with a single row per year.
        index must be a date type.

        available gropuing calculations are:
            first : keeps the fisrt row
            last : keeps the last row
            max : returns the maximum value per year
            min : returns the minimum value per year
            mean or avg : returns the average value per year
            median : returns the median value per month
            std : returns the standard deviation per year
            sum : returns the summation of all the values per year
            count : returns the number of rows per year
        """
        return self.to_SimDataFrame().yearly(outBy=outBy).to_SimSeries()

    def DaysInYear(self,column=None):
        return self.daysInYear(column=column)
    
    def daysinyear(self,column=None):
        return self.daysInYear(column=column)
    
    def daysInYear(self,column=None):
        # params = self._SimParameters
        # params['index'] = self.index
        # params['name'] = 'DaysInYear'
        # params['units'] = 'days'
        if column is not None:
            if type(column) is str and column in self.columns:
                if self[column].dtype in ('int','int64') and self[column].min() > 0 :
                    return daysInYear(self[column])
                elif 'datetime' in str(self[column].dtype):
                    return daysInYear(self[column])
                else:
                    raise ValueError('selected column is not a valid date or year integer')
            elif type(column) is str and column not in self.columns:
                raise ValueError('the selected column is not in this SimDataFrame')
            elif type(colum) is list:
                result = self._class(data={},index=self.index,**self._SimParameters)
                for col in column:
                    if col in self.columns:
                        result[col] = daysInYear(self[col])
                return result
        else:
            if self.index.dtype in ('int','int64') and self.index.min() > 0 :
                return self._class( data=self.values, index=list(daysInYear(self.index)), columns=self.columns, **self._SimParameters )
            elif 'datetime' in str(self.index.dtype):
                return self._class( data=self.values, index=list(daysInYear(self.index)), columns=self.columns, **self._SimParameters )
            else:
                raise ValueError('index is not a valid date or year integer')

    def RealYear(self,column=None):
        return self.realYear(column)

    def realyear(self,column=None):
        return self.realYear(column)

    def realYear(self,column=None):
        if column is not None:
            if type(column) is str and column in self.columns:
                if 'datetime' in str(self[column].dtype):
                    return realYear(self[column])  
                else :
                    raise ValueError('selected column is not a valid date format')
            elif type(column) is str and column not in self.columns:
                raise ValueError('the selected column is not in this SimDataFrame')
            elif type(column) is list:
                result = self._class(data={},index=self.index,**self._SimParameters)
                for col in column:
                    if col in self.columns:
                        result[col] = daysInYear(self[col])
                return result
        else:
            if 'datetime' in str(self.index.dtype):
                return self._class( data=self.values, index=list(realYear(self.index)), columns=self.columns, **self._SimParameters )
            else:
                raise ValueError('index is not a valid date or year integer')

    def integrate(self, method='trapz') :
        """
        Calculates numerical integration, using trapezoidal method,
        or constant value of the columns values over the index values.

        method parameter can be: 'trapz' to use trapezoidal method
                                 'const' to constant vale multiplied
                                         by delta-index

        Returns a new SimSeries
        """
        return self.SDF.integrate(method=method)

class SimDataFrame(DataFrame) :
    """
    A SimDataFrame object is a pandas.DataFrame that units associated with to
    each column. In addition to the standard DataFrame constructor arguments,
    SimDataFrame also accepts the following keyword arguments:

    Parameters
    ----------
    units : string or dictionary of units(optional)
        Can be any string, but only units acepted by the UnitConverter will
        be considered when doing arithmetic calculations with other SimSeries
        or SimDataFrames.

    See Also
    --------
    SimSeries
    pandas.DataFrame

    """
    _metadata = ["units", "speak", "indexUnits", "nameSeparator", "intersectionCharacter", "autoAppend", "spdLocator"]  #, "spdiLocator"]

    def __init__(self, data=None, units=None, index=None, speak=False, indexName=None, indexUnits=None, nameSeparator=None, intersectionCharacter='∩', autoAppend=False, *args, **kwargs) :
        self.units = None
        self.speak = bool(speak)
        self.indexUnits = None
        self.nameSeparator = None
        self.intersectionCharacter = '∩'
        self.autoAppend = False
        self.spdLocator = _SimLocIndexer("loc", self)
        # self.spdiLocator = _SimLocIndexer("iloc", self)


        indexInput = None
        # catch index keyword from input parameters
        if index is not None :
            indexInput = index
        elif 'index' in kwargs and kwargs['index'] is not None :
            indexInput = kwargs['index']
        elif len(args) >= 3 and args[2] is not None :
            indexInput = args[2]
        # if index is a Series, get the name
        elif isinstance(indexInput, Series) :
            if type(indexInput.name) is str :
                indexInput = indexInput.name
        # if index is None and data is SimSeries or SimDataFrame get the name
        elif type(data) in [SimSeries, SimDataFrame] and type(data.index.name) is str and len(data.index.name)>0 :
            indexInput = data.index.name

        # if units is None data is SimDataFrame or SimSeries get the units
        if units is None :
            if type(data) is SimDataFrame :
                if type(data.units) is dict:
                    units = data.units.copy()
            elif type(data) is SimSeries :
                if type(data.units) is dict :
                    units = data.units.copy()
                elif type(data.name) is str and type(data.units) is str :
                    units = { data.name : data.units }

        # remove arguments not known by Pandas
        kwargsB = kwargs.copy()
        kwargs.pop('indexName', None)
        kwargs.pop('indexUnits', None)
        kwargs.pop('nameSeparator', None)
        kwargs.pop('units', None)
        kwargs.pop('speak', None)
        kwargs.pop('autoAppend', None)
        # convert to pure Pandas
        if type(data) in [ SimDataFrame, SimSeries ] :
            self.nameSeparator = data.nameSeparator
            self.autoAppend = data.autoAppend
            data = data.to_Pandas()
        super().__init__(data=data, index=index, *args, **kwargs)

        # set the name of the index
        if(self.index.name is None or(type(self.index.name) is str and len(self.index.name)==0 ) ) and(type(indexInput) is str and len(indexInput)>0 ) :
            self.index.name = indexInput
        # overwrite the index.name with input from the argument indexName
        if indexName is not None and type(indexName) is str and len(indexName.strip())>0 :
            self.set_indexName(indexName)
        elif 'indexName' in kwargsB and type(kwargsB['indexName']) is str and len(kwargsB['indexName'].strip())>0 :
            self.set_indexName(kwargsB['indexName'])
        # set units of the index
        elif indexUnits is not None and type(indexUnits) is str and len(indexUnits.strip())>0 :
            self.set_indexUnits(indexUnits)
        elif 'indexUnits' in kwargsB and type(kwargsB['indexUnits']) is str and len(kwargsB['indexUnits'].strip())>0 :
            self.set_indexUnits(kwargsB['indexUnits'])
        if self.indexUnits is not None and self.index.name is not None and len(self.index.name) > 0 and type(self.units) is dict and self.index.name not in self.units:
            self.units[self.index.name] = self.indexUnits
        
        # set the units
        if type(units) is str :
            # self.units = {}
            # for key in list(self.columns) :
            #     self.units[ key ] = units
            self.units = dict(zip(list(self.columns), [units]*len(list(self.columns))))
        elif type(units) is list or type(units) is tuple :
            if len(units) == len(self.columns) :
                self.units = dict(zip(list(self.columns), units))
        elif type(units) is dict and len(units)>0 :
            self.units = {}
            for key in list(self.columns):
                if key is not None and key in units :
                    self.units[key] = units[key]
                else :
                    self.units[key] = 'UNITLESS'
            if self.index.name in units:
                self.units[self.index.name] = units[self.index.name]
            for key in self.index.names:
                if key is not None and key in units:
                    self.units[key] = units[key]
        if self.indexUnits is None and self.index.name is not None and units is not None:
            if self.index.name in units:
                self.indexUnits = units[self.index.name]

        if self.index.name is not None and type(self.units) is dict and self.index.name not in self.units :
            self.units[self.index.name] = '' if self.indexUnits is None else self.indexUnits

        # get separator for the column names, 'partA'+'separator'+'partB'
        if nameSeparator is not None and type(nameSeparator) is str and len(nameSeparator.strip())>0 :
            self.set_NameSeparator(nameSeparator)
        elif 'nameSeparator' in kwargsB and type(kwargsB['nameSeparator']) is str and len(kwargsB['nameSeparator'].strip())>0 :
            self.set_NameSeparator(kwargsB['nameSeparator'])
        if self.nameSeparator in [None, '', False] and ':' in ' '.join(list(map(str, self.columns))) :
            self.nameSeparator = ':'
        if self.nameSeparator in [None, '', False] :
            self.nameSeparator = ''
        if self.nameSeparator is True :
            self.nameSeparator = ':'

        # set autoAppend if provided as argument
        if autoAppend is not None :
            self.autoAppend = bool(autoAppend)
        elif 'autoAppend' in kwargsB and kwargsB['autoAppend'] is not None :
            self.autoAppend = bool(kwargsB['autoAppend'])

    # @property
    # def _constructor(self):
    #     return SimDataFrame

    @property
    def loc(self) -> _SimLocIndexer:
        """
        wrapper for .loc indexing
        """
        return self.spdLocator

    # @property
    # def iloc(self) -> _SimLocIndexer:
    #     """
    #     wrapper for .iloc indexing
    #     """
    #     return self.spdiLocator

    @property
    def _class(self):
        return SimDataFrame

    @property
    def _SimParameters(self) :
        return {'units':self.units.copy() if type(self.units) is dict else self.units,
                'speak':self.speak,
                'indexName':self.index.name,
                'indexUnits':self.indexUnits,
                'nameSeparator':self.nameSeparator,
                'intersectionCharacter':self.intersectionCharacter,
                'autoAppend':self.autoAppend}

    def set_indexName(self, Name) :
        if type(Name) is str and len(Name.strip())>0:
            self.index.name = Name.strip()

    def set_indexUnits(self, Units) :
        if type(Units) is str and len(Units.strip())>0:
            self.indexUnits = Units.strip()

    def set_NameSeparator(self, separator) :
        if type(separator) is str and len(separator) > 0 :
            if separator in ['=', '-', '+', '&', '*', '/', '!', '%'] :
                print(" the separator '"+separator+"' could be confused with operators.\n it is recommended to use ':' as separator.")
            self.nameSeparator = separator

    def get_NameSeparator(self) :
        if self.nameSeparator in [None, '', False] :
            warn(" NameSeparator is not defined.")
            return ''
        else :
            return self.nameSeparator

    def set_index(self, key, drop=False, append=False, inplace=False, verify_integrity=False, **kwargs) :
        if key not in self.columns :
            raise ValueError("The key '"+str(key)+"' is not a column name of this DataFrame.")
        return super().set_index(key, drop=drop, append=append, inplace=inplace, verify_integrity=verify_integrity, **kwargs)

    def to_excel(self, excel_writer, split_by=None, sheet_name=None, na_rep='', float_format=None, columns=None, header=True, units=True, index=True, index_label=None, startrow=0, startcol=0, engine=None, merge_cells=True, encoding=None, inf_rep='inf', verbose=True, freeze_panes=None, sort=None) :
        """
        Wrapper of .to_excel method from Pandas.
        On top of Pandas method this method is able to split the data into different
        sheets based on the column names. See paramenters `split_by´ and `sheet_name´.

        Write {klass} to an Excel sheet.
        To write a single {klass} to an Excel .xlsx file it is only necessary to
        specify a target file name. To write to multiple sheets it is necessary to
        create an `ExcelWriter` object with a target file name, and specify a sheet
        in the file to write to.
        Multiple sheets may be written to by specifying unique `sheet_name`.
        With all data written to the file it is necessary to save the changes.
        Note that creating an `ExcelWriter` object with a file name that already
        exists will result in the contents of the existing file being erased.

        Parameters
        ----------
        excel_writer : str or ExcelWriter object from Pandas.
            File path or existing ExcelWriter.
        split_by: None, positive or negative integer or str 'left', 'right' or 'first'. Default is None
            If is string 'left' or 'right', creates a sheet grouping the columns by
            the corresponding left:right part of the column name.
            If is string 'first', creates a sheet grouping the columns by
            the first character of the column name.
            If None, all the columns will go into the same sheet.
            if integer i > 0, creates a sheet grouping the columns by the 'i' firsts
            characters of the column name indicated by the integer.
            if integer i < 0, creates a sheet grouping the columns by the 'i' last
            the number characters of the column name indicated by the integer.
        sheet_name : None or str, default None
            Name of sheet which will contain DataFrame.
            If None:
                the `left` or `right` part of the name will be used if is unique,
                or 'FIELD', 'WELLS', 'GROUPS' or 'REGIONS' if all the column names
                start with 'F', 'W', 'G' or 'R'.
            else 'Sheet1' will be used.
        na_rep : str, default ''
            Missing data representation.
        float_format : str, optional
            Format string for floating point numbers. For example
            ``float_format="%.2f"`` will format 0.1234 to 0.12.
        columns : sequence or list of str, optional
            Columns to write.
        header : bool or list of str, default True
            Write out the column names. If a list of string is given it is
            assumed to be aliases for the column names.
        units : bool, default True
            Write the units of the column under the header name.
        index : bool, default True
            Write row names(index).
        index_label : str or sequence, optional
            Column label for index column(s) if desired. If not specified, and
            `header` and `index` are True, then the index names are used. A
            sequence should be given if the DataFrame uses MultiIndex.
        startrow : int, default 0
            Upper left cell row to dump data frame.
        startcol : int, default 0
            Upper left cell column to dump data frame.
        engine : str, optional
            Write engine to use, 'openpyxl' or 'xlsxwriter'. You can also set this
            via the options ``io.excel.xlsx.writer``, ``io.excel.xls.writer``, and
            ``io.excel.xlsm.writer``.
        merge_cells : bool, default True
            Write MultiIndex and Hierarchical Rows as merged cells.
        encoding : str, optional
            Encoding of the resulting excel file. Only necessary for xlwt,
            other writers support unicode natively.
        inf_rep : str, default 'inf'
            Representation for infinity(there is no native representation for
            infinity in Excel).
        verbose : bool, default True
            Display more information in the error logs.
        freeze_panes : tuple of int(length 2), optional
            Specifies the one-based bottommost row and rightmost column that
            is to be frozen.
        sort: None, bool or int
            if None, default behaviour depends on split_by parameter:
                if split_by is None will keep the current order of the columns in the SimDataFrame.
                if split_by is not None will sort alphabetically ascending the names of the columns.
            if True (bool) will sort the columns alphabetically ascending.
            if False (bool) will maintain the current order.
            if int > 0 will sort the columns alphabetically ascending.
            if int < 0 will sort the columns alphabetically descending.
            if int == 0 will keep the current order of the columns.
            
        """
        # if header is not requiered and sheet_name is str, directly pass it to Pandas
        if(not header and type(sheet_name) is str ) or(not units and type(sheet_name) is str ) :
            self.DF.to_excel(excel_writer, sheet_name=sheet_name, na_rep=na_rep, float_format=float_format, columns=columns, header=False, index=index, index_label=index_label, startrow=startrow, startcol=startcol, engine=engine, merge_cells=merge_cells, encoding=encoding, inf_rep=inf_rep, verbose=verbose, freeze_panes=freeze_panes)

        # helper function
        firstChar = lambda s : str(s)[0]
        lastChar = lambda s : str(s)[-1]
        iChar = lambda s : lambda i : str(s)[:i] if i>0 else str(s)[i:]

        # define the columns to be exported
        if type(columns) is str :
            columns = [columns]
        if columns is None :
            cols = list(self.columns)
        else :
            cols = columns.copy()

        # validate split_by parameter
        if type(split_by) is not str and split_by is not None :
            raise ValueError(" `split_by´ parameter must be 'left', 'right', 'first' or None.")

        if type(split_by) is str :
            split_by = split_by.strip().lower()
        if split_by is not None and(len(split_by) == 0 or split_by == 'none' ) :
            split_by = None

        # define the split and sheet(s) name(s)
        if split_by is None : # no split_by, use a single sheet
            if sheet_name is None : # generate the sheet name
                if len(self[cols].left) == 1 :
                    names = self[cols].left
                elif len(self[cols].right) == 1 :
                    names = self[cols].right
                elif len(set(map(firstChar, cols))) == 1 :
                    names = list(set(map(firstChar, cols)))[0]
                    if names == 'F' :
                        names =('FIELD', )
                    elif names == 'W' :
                        names =('WELLS', )
                    elif names == 'G' :
                        names =('GROUPS', )
                    elif names == 'R' :
                        names =('REGIONS', )
                    elif names == 'C' :
                        names =('CONNECTIONS', )
                    else :
                        names =('Sheet1', )
                else :
                    names =('Sheet1', )
            else : # use the provided sheet_name
                if type(sheet_name) is not str :
                    raise TypeError("'sheet_name' must be a string.")
                if len(sheet_name) > 32 and verbose :
                    print(" the sheet_name '"+sheet_name+"' is longer than 32 characters, \n will be but to the first 32 characters: '"+sheet_name[:32]+"'")
                names =(sheet_name[:32], )
                
        elif type(split_by) is str :
            if split_by == 'left' :
                names = tuple(sorted(self[cols].left))
            elif split_by == 'right' :
                names = tuple(sorted(self[cols].right))
            elif split_by == 'first' :
                names = tuple(sorted(set(map(firstChar, cols))))
            elif split_by == 'last' :
                names = tuple(sorted(set(map(lastChar, cols))))
                
        elif type(split_by) is int :
            if split_by == 0 :
                raise ValueError(" integer `split_by´ parameter must be positive or negative, not zero.")
            else :
                names = tuple(sorted(set([iChar(c)(split_by) for c in cols] )))
                
        else :
            raise ValueError(" `split_by´ parameter must be 'left', 'right', 'first', 'last', an integer or None.")

        # initialize an instance of ExcelWriter or use the instance provided
        from pandas import ExcelWriter
        if isinstance(excel_writer, ExcelWriter) :
            SDFwriter = excel_writer
        elif type(excel_writer) is str :
            if excel_writer.strip().lower().endswith('.xlsx') :
                pass # ok
            elif excel_writer.strip().lower().endswith('.xls') :
                if verbose :
                    print(" the file")
            SDFwriter = ExcelWriter(excel_writer, engine='xlsxwriter')
        else :
            raise ValueError(" `excel_writer´ parameter must be a string path to an .xlsx file or an ExcelWriter instance.")

        headerRows = 2 if header is True else 0

        if index :
            if self.index.name is None :
                indexName =('', )
            if type(self.index) is pd.core.indexes.multi.MultiIndex :
                indexName = tuple(self.index.names)
            else :
                indexName =(self.index.name, )
            indexUnits = '' if self.indexUnits is None else self.indexUnits
            indexCols = len(self.index.names) if type(self.index) is pd.core.indexes.multi.MultiIndex else 1

        if freeze_panes is None :
            freeze_panes =(startrow+headerRows, startcol+(indexCols if index else 0))

        # if single name, simpy write the output using .to_excel method from Pandas
        for i in range(len(names)) :

            # get the columns for this sheet
            if split_by is None:
                if sort is None:
                    colselect = tuple(cols) 
                elif int(sort) > 0:
                    colselect = tuple(sorted(cols)) 
                elif int(sort) < 0:
                    colselect = tuple(sorted(cols)[::-1])
                else:
                    colselect = tuple(cols)

            elif split_by == 'left' :
                if sort is None:
                    colselect = tuple(sorted(fnmatch.filter(cols, names[i]+'*' )))
                elif int(sort) > 0:
                    colselect = tuple(sorted(fnmatch.filter(cols, names[i]+'*' )))
                elif int(sort) < 0:
                    colselect = tuple(sorted(fnmatch.filter(cols, names[i]+'*' ))[::-1])
                else:
                    colselect = tuple(fnmatch.filter(cols, names[i]+'*' ))

            elif split_by == 'right' :
                if sort is None:
                    colselect = tuple(sorted(fnmatch.filter(cols, '*'+names[i] )))
                elif int(sort) > 0:
                    colselect = tuple(sorted(fnmatch.filter(cols, '*'+names[i] )))
                elif int(sort) < 0:
                    colselect = tuple(sorted(fnmatch.filter(cols, '*'+names[i] ))[::-1])
                else:
                    colselect = tuple(fnmatch.filter(cols, '*'+names[i] ))

            elif split_by == 'first' :
                if sort is None:
                    colselect = tuple(sorted(fnmatch.filter(cols, names[i][0]+'*' )))
                elif int(sort) > 0:
                    colselect = tuple(sorted(fnmatch.filter(cols, names[i][0]+'*' )))
                elif int(sort) < 0:
                    colselect = tuple(sorted(fnmatch.filter(cols, names[i][0]+'*' ))[::-1])
                else:
                    colselect = tuple(fnmatch.filter(cols, names[i][0]+'*' ))

            elif split_by == 'last' :
                if sort is None:
                    colselect = tuple(sorted(fnmatch.filter(cols, '*'+names[i][-1] )))
                elif int(sort) > 0:
                    colselect = tuple(sorted(fnmatch.filter(cols, '*'+names[i][-1] )))
                elif int(sort) < 0:
                    colselect = tuple(sorted(fnmatch.filter(cols, '*'+names[i][-1] ))[::-1])
                else:
                    colselect = tuple(fnmatch.filter(cols, names[i][0]+'*' ))

            # write the sheet to the ExcelWriter
            self.DF.to_excel(SDFwriter, sheet_name=names[i], na_rep=na_rep, float_format=float_format, columns=colselect, header=False, index=index, index_label=index_label, startrow=startrow+headerRows, startcol=startcol, engine=engine, merge_cells=merge_cells, encoding=encoding, inf_rep=inf_rep, verbose=verbose, freeze_panes=freeze_panes)

            # Get the xlsxwriter workbook and worksheet objects.
            SDFworkbook  = SDFwriter.book
            SDFworksheet = SDFwriter.sheets[names[i]]

            if header :
                header_format = SDFworkbook.add_format({'bold': True, 'font_size':11})
                units_format = SDFworkbook.add_format({'italic': True})

                # add the index name and units to the header
                if index :
                    colselect = indexName+colselect

                # write the column header, name and units
                for c in range(len(colselect)) :
                    colUnit = ''
                    if colselect[c] in self.units :
                        colUnit = self.units[colselect[c]]
                    SDFworksheet.write(startrow, startcol+c, colselect[c], header_format)
                    SDFworksheet.write(startrow+1, startcol+c, colUnit, units_format)

        if isinstance(excel_writer, ExcelWriter) :
            return SDFwriter
        elif type(excel_writer) is str :
            SDFwriter.save()

    def as_Pandas(self) :
        return self.to_DataFrame()

    def to_pandas(self) :
        return self.to_DataFrame()

    def to_Pandas(self) :
        return self.to_DataFrame()

    def to_DataFrameMultiIndex(self) :
        return self._DataFrameWithMultiIndex()

    def to_DataFrame(self) :
        return DataFrame(self).copy()

    def as_DataFrame(self) :
        return DataFrame(self)
    
    def to_Series(self):
        return self.to_SimSeries().to_Series()
    
    def to_SimSeries(self):
        if len(self.columns) == 1 :
            return self[self.columns[0]]
        if len(self) <= 1:
            return SimSeries(data=Series(self.DF.iloc[0].to_list(), name=self.index[0], index=self.columns.to_list()) , **self._SimParameters)
        raise TypeError('Not possioble to converto to SimSeries')
    
    @property
    def Series(self):
        return self.to_Series()
    
    @property
    def SimSeries(self):
        return self.to_SimSeries()
    
    @property
    def S(self):
        return self.to_SimSeries()

    @property
    def SS(self):
        return self.to_SimSeries()
    
    @property
    def s(self):
        return self.to_SimSeries()

    @property
    def ss(self):
        return self.to_SimSeries()


    @property
    def DataFrame(self) :
        return self.as_DataFrame()

    @property
    def DF(self) :
        return self.as_DataFrame()
    
    @property
    def df(self) :
        return self.as_DataFrame()

    def to(self, units) :
        """
        returns the dataframe converted to the requested units if possible,
        else returns None
        """
        return self.convert(units)
    
    @property
    def indexName(self):
        return self.index.name

    def reset_index(self,level=None, drop=False, inplace=False, col_level=0, col_fill=''):
        if inplace:
            indexUnits, indexName = self.indexUnits, None if drop else self.index.name
            super().reset_index(level=level, drop=drop, inplace=inplace, col_level=col_level, col_fill='')
            if indexUnits is not None and indexName is not None:
                self.set_Units(indexUnits,indexName)
            self.index.name = None
        else:
            result = SimDataFrame(
                data=self.DF.reset_index(level=level, drop=drop, inplace=inplace, col_level=col_level, col_fill=''),
                **self._SimParameters)
            if not drop and self.indexUnits is not None and self.index.name is not None:
                result.set_Units(self.indexUnits,item=self.index.name)
            result.index.name = None
            return result

    def convert(self, units) :
        """
        returns the dataframe converted to the requested units if possible,
        else returns None
        """
        if type(units) is str :
            result = self.copy()
            valid = False
            for col in self.columns :
                if convertibleUnits(self.get_Units(col)[col], units ) :
                    result[col] = self[col].to(units)
                    valid = True
            if valid :
                return result
        if type(units) in [list, tuple] :
            result = self.copy()
            valid = False
            for col in self.columns :
                for ThisUnits in units :
                    if convertibleUnits(self.get_Units(col)[col], ThisUnits ) :
                        result[col] = self[col].to(ThisUnits)
                        valid = True
                        break
            if valid :
                return result
        if type(units) is dict :
            unitsDict = {}
            for k, v in units.items() :
                keys = self.find_Keys(k)
                if len(keys) > 0 :
                    for each in keys :
                        unitsDict[each] = v
            result = self.copy()
            for col in self.columns :
                if col in unitsDict and convertibleUnits(self.get_Units(col)[col], unitsDict[col] ) :
                    result[col] = self[col].to(unitsDict[col]) # convertUnit(self[col].S, self.get_Units(col)[col], unitsDict[col], self.speak ), unitsDict[col]
            return result

    def dropzeros(self,axis='both'):
        """
        alias for .drop_zeros() method
        """
        return self.drop_zeros(axis=axis)

    def drop_zeros(self, axis='both'):
        """
        drop the axis(rows or columns) where all the values are zeross.

        axis parameter can be:
            'columns' or 1 : removes all the columns fill with zeroes
            'index' or 'rows' 0 : removes all the rows fill with zeroes
            'both' or 2 : removes all the rows and columns fill with zeroes
        """
        axis = _cleanAxis(axis)
        if axis in ['both', 2] :
            return self.replace(0, np.nan).dropna(axis='columns', how='all').dropna(axis='index', how='all').dropna(axis='columns', how='all').replace(np.nan, 0)
        elif axis in ['rows', 'row', 'index', 0] :
            return self.replace(0, np.nan).dropna(axis='index', how='all').replace(np.nan, 0)
        elif axis in ['columns', 'column', 'col', 'cols', 1] :
            return self.replace(0, np.nan).dropna(axis='columns', how='all').replace(np.nan, 0)
        else :
            raise ValueError(" valid `axis´ argument are 'index', 'columns' or 'both'.")


    def dropna(self, axis='index', how='all', thresh=None, subset=None, inplace=False) :
        axis = _cleanAxis(axis)
        return SimDataFrame(data=self.DF.dropna(axis=axis, how=how, thresh=thresh, subset=subset, inplace=inplace), **self._SimParameters ) 

    def drop(self, labels=None, axis=0, index=None, columns=None, level=None, inplace=False, errors='raise') :
        axis = _cleanAxis(axis)
        return SimDataFrame(data=self.DF.drop(labels=labels, axis=axis, index=index, columns=columns, level=level, inplace=inplace, errors=errors), **self._SimParameters ) 

    def drop_duplicates(self, subset=None, keep='first', inplace=False, ignore_index=False) :
        return SimDataFrame(data=self.DF.drop_duplicates(subset=subset, keep=keep, inplace=inplace, ignore_index=ignore_index), **self._SimParameters )

    def fillna(self, value=None, method=None, axis='index', inplace=False, limit=None, downcast=None) :
        axis = _cleanAxis(axis)
        return SimDataFrame(data=self.DF.fillna(value=value, method=method, axis=axis, inplace=inplace, limit=limit, downcast=downcast), **self._SimParameters ) 
    
    def interpolate(self, method='slinear', axis='index', limit=None, inplace=False, limit_direction=None, limit_area=None, downcast=None, **kwargs) :
        axis = _cleanAxis(axis)
        return SimDataFrame(data=self.DF.interpolate(method=method, axis=axis, limit=limit, inplace=inplace, limit_direction=limit_direction, limit_area=limit_area, downcast=downcast, **kwargs), **self._SimParameters ) 

    def replace(self, to_replace=None, value=None, inplace=False, limit=None, regex=False, method='pad') :
        return SimDataFrame(data=self.DF.replace(to_replace=to_replace, value=value, inplace=inplace, limit=limit, regex=regex, method=method), **self._SimParameters ) 

    def groupby(self, by=None, axis=0, level=None, as_index=True, sort=True, group_keys=True, squeeze=False, observed=False, dropna=True) :
        axis = _cleanAxis(axis)
        selfGrouped = self.DF.groupby(by=by, axis=axis, level=level, as_index=as_index, sort=sort, group_keys=group_keys, squeeze=squeeze, observed=observed, dropna=dropna)
        return SimDataFrame(data=selfGrouped, **self._SimParameters ) 

    def daily(self, outBy='mean') :
        """
        return a dataframe with a single row per day.
        index must be a date type.

        available gropuing calculations are:
            first : keeps the fisrt row per day
            last : keeps the last row per day
            max : returns the maximum value per year
            min : returns the minimum value per year
            mean or avg : returns the average value per year
            median : returns the median value per month
            std : returns the standard deviation per year
            sum : returns the summation of all the values per year
            count : returns the number of rows per year
        """
        try :
            result = self.DF.groupby([self.index.year, self.index.month, self.index.day])
        except:
            raise TypeError('index must be of datetime type.')
        if outBy == 'first' :
            result = result.first()
        elif outBy == 'last' :
            result = result.last()
        elif outBy == 'max' :
            result = result.max()
        elif outBy == 'min' :
            result = result.min()
        elif outBy in ['mean', 'avg'] :
            result = result.mean()
        elif outBy == 'median' :
            result = result.median()
        elif outBy == 'std' :
            result = result.std()
        elif outBy == 'sum' :
            result = result.sum()
        elif outBy == 'count' :
            result = result.count()
        elif outBy in ['int', 'integrate', 'integral', 'cum', 'cumulative', 'representative'] :
            result = self.integrate()
            result = result.DF.groupby([self.index.year, self.index.month, self.index.day])
            index = DataFrame(data=self.index, index=self.index ).groupby([self.index.year, self.index.month, self.index.day])
            index = np.append(index.first().to_numpy(), index.last().to_numpy()[-1] )
            deltaindex = np.diff(index )
            if isinstance(self.index, DatetimeIndex) :
                deltaindex = deltaindex.astype('timedelta64[s]').astype('float64')/60/60/24
            values = result.first().append(result.last().iloc[-1] )
            deltavalues = np.diff(values.transpose())
            result = DataFrame(data=(deltavalues/deltaindex).transpose(), index=result.first().index, columns=self.columns )
        else :
            raise ValueError(" outBy parameter is not valid.")

        output = SimDataFrame(data=result, **self._SimParameters)
        output.index.names = ['YEAR', 'MONTH', 'DAY']
        output.index.name = 'YEAR_MONTH_DAY'
        # output.indexUnits = ('year','month','day')
        return output

    def monthly(self, outBy='mean') :
        """
        return a dataframe with a single row per month.
        index must be a date type.

        available gropuing calculations are:
            first : keeps the fisrt row per month
            last : keeps the last row per month
            max : returns the maximum value per month
            min : returns the minimum value per month
            mean or avg : returns the average value per month
            median : returns the median value per month
            std : returns the standard deviation per month
            sum : returns the summation of all the values per month
            count : returns the number of rows per month
        """
        try :
            result = self.DF.groupby([self.index.year, self.index.month])
        except:
            raise TypeError('index must be of datetime type.')
        if outBy == 'first' :
            result = result.first()
        elif outBy == 'last' :
            result = result.last()
        elif outBy == 'max' :
            result = result.max()
        elif outBy == 'min' :
            result = result.min()
        elif outBy in ['mean', 'avg'] :
            result = result.mean()
        elif outBy == 'median' :
            result = result.median()
        elif outBy == 'std' :
            result = result.std()
        elif outBy == 'sum' :
            result = result.sum()
        elif outBy == 'count' :
            result = result.count()
        elif outBy in ['int', 'integrate', 'integral', 'cum', 'cumulative', 'representative'] :
            result = self.integrate()
            result = result.DF.groupby([self.index.year, self.index.month])
            index = DataFrame(data=self.index, index=self.index ).groupby([self.index.year, self.index.month])
            index = np.append(index.first().to_numpy(), index.last().to_numpy()[-1] )
            deltaindex = np.diff(index )
            if isinstance(self.index, DatetimeIndex) :
                deltaindex = deltaindex.astype('timedelta64[s]').astype('float64')/60/60/24
            values = result.first().append(result.last().iloc[-1] )
            deltavalues = np.diff(values.transpose())
            result = DataFrame(data=(deltavalues/deltaindex).transpose(), index=result.first().index, columns=self.columns )
        else :
            raise ValueError(" outBy parameter is not valid.")

        output = SimDataFrame(data=result, **self._SimParameters) 
        output.index.names = ['YEAR', 'MONTH']
        output.index.name = 'YEAR_MONTH'
        # output.indexUnits = ('year','month')
        return output

    def yearly(self, outBy='mean') :
        """
        return a dataframe with a single row per year.
        index must be a date type.

        available gropuing calculations are:
            first : keeps the fisrt row
            last : keeps the last row
            max : returns the maximum value per year
            min : returns the minimum value per year
            mean or avg : returns the average value per year
            median : returns the median value per month
            std : returns the standard deviation per year
            sum : returns the summation of all the values per year
            count : returns the number of rows per year
        """
        try :
            result = self.DF.groupby(self.index.year)
        except:
            raise TypeError('index must be of datetime type.')
        if outBy == 'first' :
            result = result.first()
        elif outBy == 'last' :
            result = result.last()
        elif outBy == 'max' :
            result = result.max()
        elif outBy == 'min' :
            result = result.min()
        elif outBy in ['mean', 'avg'] :
            result = result.mean()
        elif outBy == 'median' :
            result = result.median()
        elif outBy == 'std' :
            result = result.std()
        elif outBy == 'sum' :
            result = result.sum()
        elif outBy == 'count' :
            result = result.count()
        elif outBy in ['int', 'integrate', 'integral', 'cum', 'cumulative', 'representative'] :
            result = self.integrate()
            result = result.DF.groupby(self.index.year)
            index = DataFrame(data=self.index, index=self.index ).groupby(self.index.year)
            index = np.append(index.first().to_numpy(), index.last().to_numpy()[-1] )
            deltaindex = np.diff(index )
            if isinstance(self.index, DatetimeIndex) :
                deltaindex = deltaindex.astype('timedelta64[s]').astype('float64')/60/60/24
            values = result.first().append(result.last().iloc[-1] )
            deltavalues = np.diff(values.transpose())
            result = DataFrame(data=(deltavalues/deltaindex).transpose(), index=result.first().index, columns=self.columns )
        else :
            raise ValueError(" outBy parameter is not valid.")

        output = SimDataFrame(data=result, **self._SimParameters)  
        output.index.names = ['YEAR']
        output.index.name = 'YEAR'
        output.indexUnits = 'year'
        return output

    def aggregate(self, func=None, axis=0, *args, **kwargs) :
        axis = _cleanAxis(axis)
        return SimDataFrame(data=self.DF.aggregate(func=func, axis=axis, *args, **kwargs), **self._SimParameters )

    def resample(self, rule, axis=0, closed=None, label=None, convention='start', kind=None, loffset=None, base=None, on=None, level=None, origin='start_day', offset=None) :
        axis = _cleanAxis(axis)
        return SimDataFrame(data=self.DF.resample(rule, axis=axis, closed=closed, label=label, convention=convention, kind=kind, loffset=loffset, base=base, on=on, level=level, origin=origin, offset=offset), **self._SimParameters )

    def reindex(self, labels=None, index=None, columns=None, axis=None, **kwargs) :
        """
        wrapper for pandas.DataFrame.reindex

        labels : array-like, optional
            New labels / index to conform the axis specified by ‘axis’ to.
        index, columns : array-like, optional(should be specified using keywords)
            New labels / index to conform to. Preferably an Index object to avoid duplicating data
        axis : int or str, optional
            Axis to target. Can be either the axis name(‘index’, ‘columns’) or number(0, 1).
        """
        if labels is None and axis is None and index is not None :
            labels = index
            axis = 0
        elif labels is None and axis is None and columns is not None :
            labels = columns
            axis = 1
        elif labels is not None and axis is None and columns is None and index is None :
            if len(labels) == len(self.index) :
                axis = 0
            elif len(labels) == len(self.columns) :
                axis = 1
            else :
                raise TypeError("labels does not match neither len(index) or len(columns).")
        axis = _cleanAxis(axis)
        return SimDataFrame(data=self.DF.reindex(labels=labels, axis=axis, **kwargs), **self._SimParameters ) 

    def rename(self, **kwargs) :
        """
        wrapper of rename function from Pandas.

        Alter axes labels.

        Function / dict values must be unique(1-to-1).
        Labels not contained in a dict / Series will be left as-is.
        Extra labels listed don’t throw an error.

        Parameters:
            mapper: dict-like or function
                Dict-like or functions transformations to apply to that axis’ values.
                Use either mapper and axis to specify the axis to target with mapper,
                or index and columns.

            index: dict-like or function
                Alternative to specifying axis(mapper, axis=0 is equivalent to index=mapper).

            columns: dict-like or function
                Alternative to specifying axis(mapper, axis=1 is equivalent to columns=mapper).

            axis: {0 or ‘index’, 1 or ‘columns’}, default 0
                Axis to target with mapper. Can be either the axis name(‘index’, ‘columns’) or number(0, 1). The default is ‘index’.

            copy: bool, default True
                Also copy underlying data.

            inplace:bool, default False
                Whether to apply the chanes directly in the dataframe.
                Always return a new DataFrame.
                If True then value of copy is ignored.

            level: int or level name, default None
                In case of a MultiIndex, only rename labels in the specified level.

            errors: {‘ignore’, ‘raise’}, default ‘ignore’
                If ‘raise’, raise a KeyError when a dict-like mapper, index, or columns
                contains labels that are not present in the Index being transformed.
                If ‘ignore’, existing keys will be renamed and extra keys will be ignored.
        """
        cBefore = list(self.columns)
        if 'inplace' in kwargs and kwargs['inplace'] :
            super().rename(**kwargs)
            cAfter = list(self.columns)
        else :
            catch = super().rename(**kwargs)
            cAfter = list(catch.columns)
        newUnits = {}
        for i in range(len(cBefore)) :
            newUnits[cAfter[i]] = self.units[cBefore[i]]
        if 'inplace' in kwargs and kwargs['inplace'] :
            self.units = newUnits
            return None
        else :
            catch.units = newUnits
            return catch

    @property
    def right(self) :
        if self.nameSeparator in [None, '', False] :
            return tuple(self.columns )
        objs = []
        for each in list(self.columns ) :
            if self.nameSeparator in each :
                objs += [each.split(self.nameSeparator )[-1]]
            else :
                objs += [each]
        return tuple(set(objs))

    @property
    def left(self) :
        if self.nameSeparator in [None, '', False] :
            return tuple(self.columns )
        objs = []
        for each in list(self.columns ) :
            if self.nameSeparator in each :
                objs += [each.split(self.nameSeparator )[0]]
            else :
                objs += [each]
        return tuple(set(objs))

    def renameRight(self, inplace=False) :
        if self.nameSeparator in [None, '', False] :
            return self  # raise ValueError("name separator must not be None")
        objs = {}
        for each in list(self.columns ) :
            if type(each) is str and self.nameSeparator in each :
                objs[each] = each.split(self.nameSeparator )[-1]
                # self.units[ each.split(self.nameSeparator )[-1] ] = self.units[ each ]
                # del(self.units[each])
            else :
                objs[each] = each
        if len(set(objs.keys())) != len(set(objs.values())) :
            objs = dict( zip(objs.keys(),objs.keys()) ) 
        if inplace :
            self.rename(columns=objs, inplace=True)
        else :
            return self.rename(columns=objs, inplace=False)

    def renameLeft(self, inplace=False) :
        if self.nameSeparator in [None, '', False] :
            return self #  raise ValueError("name separator must not be None")
        objs = {}
        for each in list(self.columns ) :
            if type(each) is str and self.nameSeparator in each :
                objs[each] = each.split(self.nameSeparator )[0]
                # self.units[ each.split(self.nameSeparator )[0] ] = self.units[ each ]
                # del(self.units[each])
            else :
                objs[each] = each
        if len(set(objs.keys())) != len(set(objs.values())) :
            objs = dict( zip(objs.keys(),objs.keys()) ) 
        if inplace :
            self.rename(columns=objs, inplace=True)
        else :
            return self.rename(columns=objs, inplace=False)

    def _CommonRename(self, SimDataFrame1, SimDataFrame2=None, LR=None) :
        cha = self.intersectionCharacter
        
        if LR is not None :
            LR = LR.upper()
            if LR not in 'LR' :
                LR = None

        if SimDataFrame2 is None :
            SDF1, SDF2 = self, SimDataFrame1
        else:
            SDF1, SDF2 = SimDataFrame1, SimDataFrame2

        if type(SDF1) is not SimDataFrame :
            raise TypeError("both dataframes to be compared must be SimDataFrames.")
        if type(SDF2) is not SimDataFrame :
            raise TypeError("both dataframes to be compared must be SimDataFrames.")

        if SDF1.nameSeparator is None or SDF2.nameSeparator is None :
            raise ValueError("the 'nameSeparator' must not be empty in both SimDataFrames.")

        if LR == 'L' or (LR is None and len(SDF1.left) == 1 and len(SDF2.left) == 1 ) :
            SDF2C = SDF2.copy()
            SDF2C.renameRight(inplace=True)
            SDF1C = SDF1.copy()
            SDF1C.renameRight(inplace=True)
            commonNames = {}
            for c in SDF1C.columns :
                if c in SDF2C.columns :
                    commonNames[c] = SDF1.left[0] + cha + SDF2.left[0] + SDF1.nameSeparator + c
                else :
                    commonNames[c] = SDF1.left[0] + SDF1.nameSeparator + c
            for c in SDF2C.columns :
                if c not in SDF1C.columns :
                    commonNames[c] = SDF2.left[0] + SDF1.nameSeparator + c
            if LR is None and len(commonNames) > 1 :
                alternative = self._CommonRename(SDF1, SDF2, LR='R')
                if len(alternative[2]) < len(commonNames) :
                    return alternative

        elif LR == 'R' or (LR is None and len(SDF1.right) == 1 and len(SDF2.right) == 1 ) :
            SDF2C = SDF2.copy()
            SDF2C.renameLeft(inplace=True)
            SDF1C = SDF1.copy()
            SDF1C.renameLeft(inplace=True)
            commonNames = {}
            for c in SDF1C.columns :
                if c in SDF2C.columns :
                    commonNames[c] = c + SDF1.nameSeparator + SDF1.right[0] + cha + SDF2.right[0]
                else :
                    commonNames[c] = c + SDF1.nameSeparator + SDF1.right[0]
            for c in SDF2C.columns :
                if c not in SDF1C.columns :
                    commonNames[c] = c + SDF1.nameSeparator + SDF2.right[0]
            if LR is None and len(commonNames) > 1 :
                alternative = self._CommonRename(SDF1, SDF2, LR='L')
                if len(alternative[2]) < len(commonNames) :
                    return alternative
        
        else :
            SDF1C, SDF2C = SDF1, SDF2.copy()
            commonNames = None
        
        return SDF1C, SDF2C, commonNames
    
    def _JoinedIndex(self, other, *, drop_duplicates=True):
        return _MergeIndex(self, other, how='outer', drop_duplicates=drop_duplicates)
    
    def _CommonIndex(self, other, *, drop_duplicates=True):
        return _MergeIndex(self, other, how='inner', drop_duplicates=drop_duplicates)
    
    def _MergeIndex(self, other, how='outer', *, drop_duplicates=True):
        return _MergeIndex(self, other, how=how, drop_duplicates=drop_duplicates)

    def __contains__(self, item) :
        if item in self.columns :
            return True
        elif item in self.index :
            return True
        else :
            return False

    def __neg__(self) :
        result = -self.as_DataFrame()
        return SimDataFrame(data=result, **self._SimParameters )

    def __add__(self, other) :
        # both are SimDataFrame
        if isinstance(other, SimDataFrame) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimDataFrames are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            notFount = 0
            
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            
            for col in otherI.columns :
                if col in selfI.columns :
                    result[col] = selfI[col] + otherI[col]
                else :
                    notFount += 1
                    result[col] = otherI[col]

            if notFount == len(otherI.columns) :
                if selfI.nameSeparator is not None and otherI.nameSeparator is not None :
                    selfC, otherC, newNames = selfI._CommonRename(otherI)
                    
                    # if no columns has common names
                    if newNames is None:
                        if len(otherC.columns) == 1:  # just in case there is only one column in the second operand
                            return selfC + otherC.to_SimSeries()
                        else :
                            raise TypeError("Not possible to operate SimDataFrames if there aren't common columns")
                    
                    if (selfI.columns != selfC.columns).any() or (otherI.columns != otherC.columns).any() :
                        resultX = selfC + otherC
                        resultX.rename(columns=newNames, inplace=True)
                    else :
                        resultX = result
                    if self.autoAppend :
                        for col in newNames.values() :
                            result[col] = resultX[col]
                    else :
                        result = resultX
            return result

        # other is SimSeries
        elif isinstance(other, SimSeries) :
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            if otherI.name in selfI.columns :
                result[otherI.name] = selfI[otherI.name] + otherI
            elif selfI.autoAppend :
                result[otherI.name] = otherI
            else :
                for col in selfI.columns :
                    result[col] = selfI[col] + otherI
            return result

        # other is Pandas DataFrame
        elif isinstance(other, DataFrame) :
            result = self.DF.add(other, fill_value=0)
            selfC, otherC, newNames = self._CommonRename(SimDataFrame(other, **self._SimParameters))
            result = selfC + otherC
            return result if newNames is None else result.rename(columns=newNames)

        # let's Pandas deal with other types, maintain units and dtype
        else :
            result = self.as_DataFrame() + other
            return SimDataFrame(data=result, **self._SimParameters)

    def __radd(self, other) :
        return self.__add__(other)

    def __sub__(self, other) :
        # both are SimDataFrame
        if isinstance(other, SimDataFrame) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimDataFrames are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            notFount = 0
            
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            
            for col in otherI.columns :
                if col in selfI.columns :
                    result[col] = selfI[col] - otherI[col]
                else :
                    notFount += 1
                    result[col] = otherI[col] if selfI.intersectionCharacter in col else -otherI[col]

            if notFount == len(otherI.columns) :
                if selfI.nameSeparator is not None and otherI.nameSeparator is not None :
                    selfC, otherC, newNames = selfI._CommonRename(otherI)
                    
                    # if no columns has common names
                    if newNames is None:
                        if len(otherC.columns) == 1:  # just in case there is only one column in the second operand
                            return selfC - otherC.to_SimSeries()
                        else :
                            raise TypeError("Not possible to operate SimDataFrames if there aren't common columns")
                    
                    resultX = selfC - otherC
                    resultX.rename(columns=newNames, inplace=True)
                    if self.autoAppend :
                        for col in newNames.values() :
                            result[col] = resultX[col]
                    else :
                        result = resultX
            return result

        # other is SimSeries
        elif isinstance(other, SimSeries) :
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            if otherI.name in selfI.columns :
                result[otherI.name] = selfI[otherI.name] - otherI
            elif self.autoAppend :
                result[otherI.name] = -otherI
            else :
                for col in selfI.columns :
                    result[col] = selfI[col] - otherI
            return result

        # other is Pandas DataFrame
        elif isinstance(other, DataFrame) :
            result = self.DF.sub(other, fill_value=0)
            selfC, otherC, newNames = self._CommonRename(SimDataFrame(other, **self._SimParameters))
            result = selfC + otherC
            return result if newNames is None else result.rename(columns=newNames)

        # let's Pandas deal with other types, maintain units and dtype
        else :
            result = self.as_DataFrame() - other
            return SimDataFrame(data=result, **self._SimParameters) 

    def __rsub__(self, other) :
        return self.__neg__().__add__(other)

    def __mul__(self, other) :
        # both are SimDataFrame
        if isinstance(other, SimDataFrame) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimDataFrames are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            
            notFount = 0
            for col in otherI.columns :
                if col in selfI.columns :
                    result[col] = selfI[col] * otherI[col]
                else :
                    notFount += 1

            if notFount == len(otherI.columns) :
                if selfI.nameSeparator is not None and otherI.nameSeparator is not None :
                    selfC, otherC, newNames = selfI._CommonRename(otherI)
                    
                    # if no columns has common names
                    if newNames is None:
                        if len(otherC.columns) == 1:  # just in case there is only one column in the second operand
                            return selfC * otherC.to_SimSeries()
                        else :
                            raise TypeError("Not possible to operate SimDataFrames if there aren't common columns")
                    
                    resultX = selfC * otherC
                    resultX.rename(columns=newNames, inplace=True)
                    if self.autoAppend :
                        for col in newNames.values() :
                            if self.intersectionCharacter in col :  # intersectionCharacter = '∩'
                                result[col] = resultX[col]
                    else :
                        result = resultX

            return result

        # other is SimSeries
        elif isinstance(other, SimSeries) :
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            if otherI.name in selfI.columns :
                result[otherI.name] = self[otherI.name] * otherI
            else :
                for col in selfI.columns :
                    result[col] = selfI[col] * otherI
            return result

        # let's Pandas deal with other types, maintain units and dtype
        else :
            result = self.as_DataFrame() * other
            return SimDataFrame(data=result, **self._SimParameters)

    def __rmul__(self, other) :
        return self.__mul__(other)

    def __truediv__(self, other) :
        # both are SimDataFrame
        if isinstance(other, SimDataFrame) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimDataFrames are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            
            notFount = 0
            for col in otherI.columns :
                if col in selfI.columns :
                    result[col] = selfI[col] / otherI[col]
                else :
                    notFount += 1

            if notFount == len(otherI.columns) :
                if self.nameSeparator is not None and otherI.nameSeparator is not None :
                    selfC, otherC, newNames = selfI._CommonRename(otherI)
                    
                    # if no columns has common names
                    if newNames is None:
                        if len(otherC.columns) == 1:  # just in case there is only one column in the divisor
                            return selfC / otherC.to_SimSeries()
                        else :
                            raise TypeError("Not possible to operate SimDataFrames if there aren't common columns")

                    resultX = selfC / otherC
                    resultX.rename(columns=newNames, inplace=True)
                    if self.autoAppend :
                        for col in newNames.values() :
                            if self.intersectionCharacter in col :  # intersectionCharacter = '∩'
                                result[col] = resultX[col]
                    else :
                        result = resultX
            return result

        # other is SimSeries
        elif isinstance(other, SimSeries) :
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            if otherI.name in selfI.columns :
                result[otherI.name] = selfI[otherI.name] / otherI
            else :
                for col in selfI.columns :
                    result[col] = selfI[col] / otherI
            return result

        # let's Pandas deal with other types, maintain units and dtype
        else :
            result = self.as_DataFrame() / other
            return SimDataFrame(data=result, **self._SimParameters)

    def __rtruediv__(self, other) :
        return self.__pow__(-1).__mul__(other)

    def __floordiv__(self, other) :
        # both are SimDataFrame
        if isinstance(other, SimDataFrame) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimDataFrames are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            
            notFount = 0
            for col in otherI.columns :
                if col in selfI.columns :
                    result[col] = selfI[col] // otherI[col]
                else :
                    notFount += 1

            if notFount == len(otherI.columns) :
                if selfI.nameSeparator is not None and otherI.nameSeparator is not None :
                    selfC, otherC, newNames = selfI._CommonRename(otherI)
                    
                    # if no columns has common names
                    if newNames is None:
                        if len(otherC.columns) == 1:  # just in case there is only one column in the second operand
                            return selfC // otherC.to_SimSeries()
                        else :
                            raise TypeError("Not possible to operate SimDataFrames if there aren't common columns")

                    resultX = selfC // otherC
                    resultX.rename(columns=newNames, inplace=True)
                    if self.autoAppend :
                        for col in newNames.values() :
                            if self.intersectionCharacter in col :  # intersectionCharacter = '∩'
                                result[col] = resultX[col]
                    else :
                        result = resultX
            return result

        # other is SimSeries
        elif isinstance(other, SimSeries) :
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            if otherI.name in selfI.columns :
                result[otherI.name] = selfI[otherI.name] // otherI
            else :
                for col in self.columns :
                    result[col] = self[col] // other
            return result

        # let's Pandas deal with other types, maintain units and dtype
        else :
            result = self.as_DataFrame() // other
            return SimDataFrame(data=result, **self._SimParameters)

    def __rfloordiv__(self, other) :
        return self.__pow__(-1).__mul__(other).__int__()

    def __mod__(self, other) :
        # both are SimDataFrame
        if isinstance(other, SimDataFrame) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimDataFrames are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            
            notFount = 0
            for col in otherI.columns :
                if col in selfI.columns :
                    result[col] = selfI[col] % otherI[col]
                else :
                    notFount += 1

            if notFount == len(otherI.columns) :
                if selfI.nameSeparator is not None and otherI.nameSeparator is not None :
                    selfC, otherC, newNames = selfI._CommonRename(otherI)
                    
                    # if no columns has common names
                    if newNames is None:
                        if len(otherC.columns) == 1:  # just in case there is only one column in the second operand
                            return selfC % otherC.to_SimSeries()
                        else :
                            raise TypeError("Not possible to operate SimDataFrames if there aren't common columns")
                    
                    resultX = selfC % otherC
                    resultX.rename(columns=newNames, inplace=True)
                    if self.autoAppend :
                        for col in newNames.values() :
                            if self.intersectionCharacter in col :  # intersectionCharacter = '∩'
                                result[col] = resultX[col]
                    else :
                        result = resultX

            return result

        # other is SimSeries
        elif isinstance(other, SimSeries) :
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            if otherI.name in selfI.columns :
                result[otherI.name] = selfI[other.name] % otherI
            else :
                for col in selfI.columns :
                    result[col] = selfI[col] % otherI
            return result

        # let's Pandas deal with other types, maintain units and dtype
        else :
            result = self.as_DataFrame() % other
            return SimDataFrame(data=result, **self._SimParameters )

    def __pow__(self, other) :
        # both are SimDataFrame
        if isinstance(other, SimDataFrame) :
            if self.index.name is not None and other.index.name is not None and self.index.name != other.index.name :
                Warning("indexes of both SimDataFrames are not of the same kind:\n   '"+self.index.name+"' != '"+other.index.name+"'")
            
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            
            notFount = 0
            for col in otherI.columns :
                if col in selfI.columns :
                    result[col] = selfI[col] ** otherI[col]
                else :
                    notFount += 1

            if notFount == len(otherI.columns) :
                if selfI.nameSeparator is not None and otherI.nameSeparator is not None :
                    selfC, otherC, newNames = self._CommonRename(otherI)
                    
                    # if no columns has common names
                    if newNames is None:
                        if len(otherC.columns) == 1:  # just in case there is only one column in the second operand
                            return selfC ** otherC.to_SimSeries()
                        else :
                            raise TypeError("Not possible to operate SimDataFrames if there aren't common columns")
                    
                    resultX = selfC ** otherC
                    resultX.rename(columns=newNames, inplace=True)
                    if self.autoAppend :
                        for col in newNames.values() :
                            if self.intersectionCharacter in col :  # intersectionCharacter = '∩'
                                result[col] = resultX[col]
                    else :
                        result = resultX

            return result

        # other is SimSeries
        elif isinstance(other, SimSeries) :
            selfI, otherI = self._JoinedIndex(other)
            result = selfI.copy()
            if otherI.name in selfI.columns :
                result[otherI.name] = self[otherI.name] ** otherI
            else :
                for col in selfI.columns :
                    result[col] = selfI[col] ** otherI
            return result

        # let's Pandas deal with other types, maintain units and dtype
        else :
            result = self.as_DataFrame() ** other
            return SimDataFrame(data=result, **self._SimParameters)

    def __int__(self) :
        return SimDataFrame(data=self.DF.astype(int), **self._SimParameters) 

    def mode(self, axis=0, **kwargs) :
        axis = _cleanAxis(axis)
        if axis == 0 :
            return SimDataFrame(data=self.DF.mode(axis=axis, **kwargs), **self._SimParameters) 
        if axis == 1 :
            newName = '.mode'
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns ) ) == 1 :
                newName = list(set(self.columns ))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns ))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns ))[0]+newName
            data=self.DF.mode(axis=axis, **kwargs)
            data.columns=[newName]
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)
    
    def median(self, axis=0, **kwargs) :
        axis = _cleanAxis(axis)
        if axis == 0 :
            return SimDataFrame(data=self.DF.median(axis=axis, **kwargs), **self._SimParameters)
        if axis == 1 :
            newName = '.median'
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns ) ) == 1 :
                newName = list(set(self.columns ))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns ))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns ))[0]+newName
            data=self.DF.median(axis=axis, **kwargs)
            data.columns=[newName]
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)

    def avg(self, axis=0, **kwargs) :
        return self.mean(axis=axis, **kwargs)

    def average(self, axis=0, **kwargs) :
        return self.mean(axis=axis, **kwargs)

    def mean(self, axis=0, **kwargs) :
        axis = _cleanAxis(axis)
        if axis == 0 :
            return SimDataFrame(data=self.DF.mean(axis=axis, **kwargs), **self._SimParameters)
        if axis == 1 :
            newName = '.mean'
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns ) ) == 1 :
                newName = list(set(self.columns ))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns ))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns ))[0]+newName
            data=self.DF.mean(axis=axis, **kwargs)
            data.columns=[newName]
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)

    def max(self, axis=0, **kwargs) :
        axis = _cleanAxis(axis)
        if axis == 0 :
            return SimDataFrame(data=self.DF.max(axis=axis, **kwargs), **self._SimParameters )
        if axis == 1 :
            newName = '.max'
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns ) ) == 1 :
                newName = list(set(self.columns ))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns ))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns ))[0]+newName
            data=self.DF.max(axis=axis, **kwargs)
            data.columns=[newName]
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)

    def min(self, axis=0, **kwargs) :
        axis = _cleanAxis(axis)
        if axis == 0 :
            return SimDataFrame(data=self.DF.min(axis=axis, **kwargs), **self._SimParameters)
        if axis == 1 :
            newName = '.min'
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns ) ) == 1 :
                newName = list(set(self.columns ))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns ))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns ))[0]+newName
            data=self.DF.min(axis=axis, **kwargs)
            data.columns=[newName]
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)

    def sum(self, axis=0, **kwargs) :
        axis = _cleanAxis(axis)
        if axis == 0 :
            if len(set(self.get_Units(self.columns).values())) == 1 :
                params = self._SimParameters
                params['units'] = list(set(self.get_Units(self.columns).values()))[0]
                return SimDataFrame(data=self.DF.sum(axis=axis, **kwargs).rename('.sum'), **params)
            else :
                params = self._SimParameters
                if type(params['units']) is dict:
                    params['units']['.sum'] = '*units per row'
                return SimDataFrame(data=self.DF.sum(axis=axis, **kwargs).rename('.sum'), **params)

        if axis == 1 :
            newName = '.sum'
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns)) == 1 :
                newName = list(set(self.columns))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns)) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns)) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns))[0]+newName
            else:
                commonL = commonprefix(list(self.renameLeft(inplace=False).columns))
                commonR = commonprefix(list(self.renameRight(inplace=False).columns))
                if len(commonL) >= len(commonR) :
                    newName = commonL + newName
                else :
                    newName = commonR + newName
            if len(set(self.get_Units(self.columns).values())) == 1 :
                data = self.DF.sum(axis=axis, **kwargs)
            else :
                result = self[self.columns[0]]
                units = self.units[self.columns[0]]
                for col in range(1,len(self.columns)):
                    result = result + self[self.columns[col]]
                data = result
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)
        
        if axis == 2 :
            return self.sum(axis=1).sum(axis=0)

    def std(self, axis=0, **kwargs) :
        axis = _cleanAxis(axis)
        if axis == 0 :
            return SimDataFrame(data=self.DF.std(axis=axis, **kwargs), **self._SimParameters)
        if axis == 1 :
            newName = '.std'
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns ) ) == 1 :
                newName = list(set(self.columns ))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns ))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns ))[0]+newName
            data=self.DF.std(axis=axis, **kwargs)
            data.columns=[newName]
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)
    
    def prod(self, axis=0, **kwargs) :
        axis = _cleanAxis(axis)
        if axis == 0 :
            return SimDataFrame(data=self.DF.prod(axis=axis, **kwargs), **self._SimParameters)
        if axis == 1 :
            newName = '.prod'
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns ) ) == 1 :
                newName = list(set(self.columns ))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns ))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns ))[0]+newName
            data=self.DF.prod(axis=axis, **kwargs)
            data.columns=[newName]
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)
   
    def var(self, axis=0, **kwargs) :
        axis = _cleanAxis(axis)
        if axis == 0 :
            return SimDataFrame(data=self.DF.var(axis=axis, **kwargs), **self._SimParameters)
        if axis == 1 :
            newName = '.var'
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns ) ) == 1 :
                newName = list(set(self.columns ))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns ))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns ))[0]+newName
            data=self.DF.var(axis=axis, **kwargs)
            data.columns=[newName]
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)

    def quantile(self, q=0.5, axis=0, **kwargs) :
        axis = _cleanAxis(axis)
        if axis == 0 :
            return SimDataFrame(data=self.DF.quantile(q=q, axis=axis, **kwargs), **self._SimParameters)
        if axis == 1 :
            newName = '.Q'+str(q*100)
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns ) ) == 1 :
                newName = list(set(self.columns ))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns ))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns ))[0]+newName
            data=self.DF.quantile(q=q, axis=axis, **kwargs)
            data.columns=[newName]
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)

    def round(self, decimals=0, **kwargs):
        return SimDataFrame(data=self.DF.round(decimals=decimals, **kwargs), **self._SimParameters)

    def diff(self,periods=1, axis=0, forward=False):
        axis = _cleanAxis(axis)
        if type(periods) is bool:
            periods, forward = 1, periods
        if axis == 0 :
            if forward:
                return SimDataFrame(data=-1*self.DF.diff(periods=-1*periods, axis=axis), **self._SimParameters)
            else:
                return SimDataFrame(data=self.DF.diff(periods=periods, axis=axis), **self._SimParameters)
        if axis == 1 :
            newName = '.diff'
            if len(set(self.get_Units(self.columns).values())) == 1 :
                units = list(set(self.get_Units(self.columns).values()))[0]
            else :
                units = 'dimensionless'
            if len(set(self.columns ) ) == 1 :
                newName = list(set(self.columns ))[0]+newName
            elif len(set(self.renameRight(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameRight(inplace=False).columns ))[0]+newName
            elif len(set(self.renameLeft(inplace=False).columns ) ) == 1 :
                newName = list(set(self.renameLeft(inplace=False).columns ))[0]+newName
            if forward:
                data=-1*self.DF.diff(periods=-1*periods, axis=axis)
            else:
                data=self.DF.diff(periods=periods, axis=axis)
            data.columns=[newName]
            data.name = newName
            params = self._SimParameters
            params['units'] = units
            return SimDataFrame(data=data, **params)

    def copy(self, **kwargs) :
        return SimDataFrame(data=self.as_DataFrame().copy(True), **self._SimParameters)

    def __call__(self, key=None) :
        if key is None :
            key = self.columns

        result = self.__getitem__(key)
        if isinstance(result, SimSeries) :
            result = result.to_numpy()
        return result

    def __setitem__(self, key, value, units=None):
        if type(key) is str :
            key = key.strip()
        if type(value) is tuple and len(value) == 2 and type(value[1]) in [str,dict] and units is None :  # and type(value[0]) in [SimSeries, Series, list, tuple, np.ndarray,float,int,str] 
            value, units = value[0], value[1]
        if units is None :
            if type(value) is SimSeries :
                if type(value.units) is str :
                    uDic = { str(key) : value.units }
                elif type(value.units) is dict :
                    uDic = value.units
            elif isinstance(value, SimDataFrame) :
                if len(value.columns) == 1 :
                    if value.columns[0] in value.units:
                        uDic = { str(key) : value.units[value.columns[0]] }
                    else :
                        uDic = { str(key) : 'UNITLESS' }
                else :
                    uDic = value.units.copy() if type(value.units) is dict else { str(key) : value.units }
                    if value.index.name not in value.columns and value.index.name in uDic:
                        del uDic[value.index.name]
                    if key not in uDic and len(set(uDic.values())) == 1:
                        uDic[str(key)] = list(set(uDic.values()))[0]
            else :
                uDic = { str(key) : 'UNITLESS' }
        elif type(units) is str :
            uDic = { str(key) : units.strip() }
        elif type(units) is dict :
            raise NotImplementedError
        else :
            raise NotImplementedError

        before = len(self.columns)
        super().__setitem__(key, value)
        after = len(self.columns)

        if after == before :
            self.new_Units(key, uDic[key])
        elif after > before :
            for c in range(before, after ) :
                if self.columns[c] in self.columns[ before : after ] and self.columns[c] in uDic:
                    self.new_Units(self.columns[c], uDic[ self.columns[c] ])
                else :
                    self.new_Units(self.columns[c], 'UNITLESS')

    def __getitem__(self, key) :
        
        ### if key is boolean filter, return the filtered SimDataFrame
        if isinstance(key, (Series)) or type(key) is np.ndarray :
            if str(key.dtype) == 'bool' :
                return SimDataFrame( data=self._getbyFilter(key), **self._SimParameters)
        
        ### if key is pd.Index or pd.MultiIndex return selected rows or columns 
        if isinstance(key, (Index)) :
            keyCols = True
            for each in key :
                if each not in self.columns :
                    keyCols = False
                    break
            if keyCols :
                return SimDataFrame(data=self._getbyColumn(key), **self._SimParameters)
            else :
                result = SimDataFrame(data=self._getbyIndex(key), **self._SimParameters)
                if len(result) == 1 :
                    result = _Series2Frame(result)
                return result

        ### here below we try to guess what the user is requesting
        byIndex = False
        indexFilter = None
        indexes = None
        slices = None

        ### convert tuple argument to list
        if type(key) is tuple :
            key = list(key)

        ### if key is a string but not a column name, check if it is an item, attribute, pattern, filter or index
        if type(key) is str and key not in self.columns :

            if bool(self.find_Keys(key)) : # catch the column names this key represent
                key = list(self.find_Keys(key))
            else : # key is not a column name
                try : # to evalue as a filter
                    result = self._getbyCriteria(key)
                except :
                    try : # to evaluate as an index value
                        result = self._getbyIndex(key)
                    except :
                        raise ValueError('requested key is not a valid column name, pattern, index or filter criteria:\n   ' + key)
                if result is None :
                    try:
                        result = self._getbyIndex(key)
                    except:
                        raise ValueError('requested key is not a valid column name, pattern, index or filter criteria:\n   ' + key)

        ### key is a list, have to check every item in the list
        elif type(key) is list :
            keyList, key, filters, indexes, slices = key, [], [], [], []
            for each in keyList :
                ### the key is a column name
                if type(each) is slice :
                    slices += [each]
                elif each in self.columns :
                    key += [each]
                ### if key is a string but not a column name, check if it is an item, attribute, pattern, filter or index
                elif type(each) is str :
                    if bool(self.find_Keys(each) ) : # catch the column names this key represent
                        key += list(self.find_Keys(each) )
                    else : # key is not a column name, might be a filter or index
                        try : # to evalue as a filter
                            trash = self.filter(each, returnFilter=True)
                            filters += [each]
                        except :
                            try : # to evaluate as an index value
                                _ = self._getbyIndex(each)
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
                    indexFilter = self.filter(filters, returnFilter=True)
                except :
                    raise Warning('filter conditions are not valid:\n   '+ ' and '.join(filters))
                if not indexFilter.any() :
                    raise Warning('filter conditions removed every row :\n   '+ ' and '.join(filters))

        ### attempt to get the desired keys, first as column names, then as indexes
        if bool(key) or key == 0 :
            try :
                result = self._getbyColumn(key)
            except :
                result = self._getbyIndex(key)
                if result is not None : byIndex = True
        else :
            result = SimDataFrame(data=self, **self._SimParameters)

        ### convert returned object to SimDataFrame or SimSeries accordingly
        if type(result) is DataFrame :
            resultUnits = self.get_Units(result.columns)
            params = self._SimParameters
            params['units'] = resultUnits
            result = SimDataFrame(data=result, **params)
        elif type(result) is Series :
            if result.name is None or result.name not in self.get_Units():
                # this Series is one index for multiple columns
                resultUnits = self.get_Units(result.index)
            else :
                resultUnits = self.get_Units(result.name)
            params = self._SimParameters
            params['units'] = resultUnits
            result = SimSeries(data=result, **params)

        ### apply filter array if applicable
        if indexFilter is not None :
            if type(indexFilter) is np.ndarray :
                result = result.iloc[indexFilter]
            else :
                result = result[indexFilter.array]

        ### apply indexes and slices
        if bool(indexes) or bool(slices) :
            indexeslices = indexes + slices
            iresult = _Series2Frame(result._getbyIndex(indexeslices[0]))
            if len(indexeslices) > 1 :
                for i in indexeslices[1:] :
                    iresult = iresult.append(_Series2Frame(result._getbyIndex(i)) )
            try :
                result = iresult.sort_index()
            except :
                result = iresult

        ### if is a single row return it as a DataFrame instead of a Series
        if byIndex :
            result = _Series2Frame(result)
        
        if type(result) is DataFrame:
            result = SimDataFrame(result, **self._SimParameters)
        elif type(result) is Series:
            result = SimSeries(result, **self._SimParameters)

        return result

    def _getbyFilter(self, key) :
        """
        ** helper function to __getitem__ method **

        try to get a filtered DataFrame or Series(.filter[key] )
        """
        if len(key) != len(self.DF) :
            raise ValueError('Filter wrong length ' + len(key) + ' instead of ' + len(self.DF) )
        if not isinstance(key, (Series, SimSeries)) and type(key) is not np.ndarray :
            raise TypeError("Filter must be a Series or Array" )
        else :
            if str(key.dtype) != 'bool' :
                raise TypeError("Filter dtype must be 'bool'" )

        return super().loc[key]

    def _getbyCriteria(self, key) :
        """
        ** helper function to __getitem__ method **

        try to get a filtered DataFrame or Series(.filter[key] )
        """
        return self.filter(key)

    def _getbyColumn(self, key) :
        """
        ** helper function to __getitem__ method **

        try to get a column by column name(.__getitem__[key] )
        """
        return super().__getitem__(key)


    def _getbyIndex(self, key) :
        """
        ** helper function to __getitem__ method **

        try to get a row by index value(.loc[key] ) or by position(.iloc[key] )
        """
        # if index is date try to undestand key as a date
        if type(self.index) is DatetimeIndex and type(key) not in [DatetimeIndex, Timestamp, int, float, np.ndarray] :
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
                try:
                    return self.loc[:,key]
                except:
                    try:
                        return self.iloc[:,key]
                    except:
                        raise ValueError(' ' + str(key) + ' is not a valid index value or position.')

    def _getbyDateIndex(self, key) :
        """
        ** helper function to __getitem__ method **

        try to get a row by index value(.loc[key] ) or by position(.iloc[key] )
        """
        if type(self.index) is DatetimeIndex :
            if type(key) in [DatetimeIndex, Timestamp, np.datetime64, np.ndarray, dt.date] :
                try :
                    return self.loc[key]
                except :
                    pass

            if type(key) is not str and(isDate(key) or type(key) not in [DatetimeIndex, Timestamp] ) :
                try:
                    return self.loc[key]
                except :
                    try :
                        return self.iloc[key]
                    except :
                        pass

            if type(key) is str and len(multisplit(key, ('==', '!=', '>=', '<=', '<>', '><', '>', '<', '=', ' ')) ) == 1 and isDate(key) :
                try :
                    key = strDate(key )
                except :
                    try :
                        key = strDate(key, formatIN=isDate(key, returnFormat=True), formatOUT='DD-MMM-YYYY' )
                    except :
                        raise Warning('\n Not able to undertand the key as a date.\n')
                try :
                    return self.loc[key]
                except :
                    pass

            if type(key) is str :
                keyParts = multisplit(key, ('==', '!=', '>=', '<=', '<>', '><', '>', '<', '=', ' '))
                keySearch = ''
                datesDict = {}
                temporal = SimDataFrame(index=self.index, **self._SimParameters)
                datesN = len(self)
                for P in range(len(keyParts)) :
                    if isDate(keyParts[P]) :
                        keySearch += ' D'+str(P)
                        datesDict['D'+str(P)] = keyParts[P]
                        temporal.__setitem__('D'+str(P), DatetimeIndex([ Timestamp(strDate(keyParts[P], formatIN=isDate(keyParts[P], returnFormat=True), formatOUT='YYYY-MMM-DD')) ] * datesN ).to_numpy() )
                    else :
                        keySearch += ' '+keyParts[P]
                datesFilter = temporal.filter(keySearch, returnFilter=True)
                return self.iloc[datesFilter.array]

            else :
                return self.iloc[key]

    def _columnsNameAndUnits2MultiIndex(self) :
        out = {}
        units = self.get_units()
        if units is None:
            return self.columns  # there are not units, return column names as they are
        for col in self.columns :
            if col in units :
                out[col] = units[col]
            else :
                out[col] = None
        out = pd.MultiIndex.from_tuples(out.items() )
        return out

    def _DataFrameWithMultiIndex(self) :
        result = self.DF.copy()
        newName = self._columnsNameAndUnits2MultiIndex()
        result.columns=newName
        return result

    def _repr_html_(self) :
        """
        Return a html representation for a particular DataFrame, with Units.
        """
        return self._DataFrameWithMultiIndex()._repr_html_()

    def __repr__(self) -> str:
        """
        Return a string representation for a particular DataFrame, with Units.
        """
        return self._DataFrameWithMultiIndex().__repr__()

    @property
    def wells(self) :
        if self.nameSeparator in [None, '', False] :
            return []
        objs = []
        for each in list(self.columns ) :
            if type(each) is str and self.nameSeparator in each and each[0] == 'W' :
                objs += [each.split(self.nameSeparator )[-1]]
        return tuple(set(objs))
    def get_Wells(self, pattern=None) :
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
        if pattern is not None and type(pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        if pattern is None :
            return tuple(self.wells)
        else:
            return tuple(fnmatch.filter(self.wells, pattern ) )

    @property
    def groups(self) :
        if self.nameSeparator in [None, '', False] :
            return []
        objs = []
        for each in list(self.columns ) :
            if type(each) is str and self.nameSeparator in each and each[0] == 'G' :
                objs += [each.split(self.nameSeparator )[-1]]
        return tuple(set(objs))

    def get_Groups(self, pattern=None) :
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
        if pattern is not None and type(pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        if pattern is None :
            return self.groups
        else:
            return tuple(fnmatch.filter(self.groups, pattern ) )

    @property
    def regions(self) :
        if self.nameSeparator in [None, '', False] :
            return []
        objs = []
        for each in list(self.columns ) :
            if type(each) is str and self.nameSeparator in each and each[0] == 'R' :
                objs += [each.split(self.nameSeparator )[-1]]
        return tuple(set(objs))

    def get_Regions(self, pattern=None):
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
        if pattern is not None and type(pattern ) is not str :
            raise TypeError('pattern argument must be a string.')
        if pattern is None :
            return self.regions
        else:
            return tuple(fnmatch.filter(self.regions, pattern ) )

    @property
    def attributes(self) :
        if self.nameSeparator in [None, '', False] :
            return tuple(self.columns )
        atts = {}
        for each in list(self.columns ) :
            if type(each) is str and self.nameSeparator in each :
                if type(each) is str and each.split(self.nameSeparator )[0] in atts :
                    atts[each.split(self.nameSeparator )[0]] += [each.split(self.nameSeparator )[-1]]
                else :
                    atts[each.split(self.nameSeparator )[0]] = [each.split(self.nameSeparator )[-1]]
            else :
                if each not in atts :
                    atts[each] = []
        for att in atts :
            atts[att] = list(set(atts[att]))
        return atts

    @property
    def properties(self) :
        if len(self.attributes.keys()) > 0 :
            return tuple(self.attributes.keys())
        else :
            return tuple()

    def get_Attributes(self, pattern=None) :
        """
        Will return a dictionary of all the attributes names in case as keys
        and their related items as values.

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
            return tuple(fnmatch.filter(tuple(self.attributes.keys()), pattern ) )

    def get_Keys(self, pattern=None) :
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
        if pattern is not None and type(pattern) is not str and type(pattern) not in [int,float]:
            raise TypeError('pattern argument must be a string.\nreceived '+str(type(pattern))+' with value '+str(pattern))
        if type(pattern) in [int,float]:
            if pattern in self.columns:
                return self[pattern]
            else:
                raise KeyError("The requested key: "+str(pattern)+"is not present in this SimDataFrame.")
        if pattern is None :
            return tuple(self.columns)
        else:
            return tuple(fnmatch.filter(map(str,tuple(self.columns)), pattern))

    def find_Keys(self, criteria=None) :
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
            return tuple(self.columns )
        keys = []
        if type(criteria) is str and len(criteria.strip()) > 0 :
            if criteria.strip()[0] == '!' and len(criteria.strip()) > 1 :
                keys = list(self.columns )
                keys.remove(criteria[1:])
                return tuple(keys )
            criteria = [criteria]
        elif type(criteria) is not list :
            try :
                criteria = list(criteria)
            except :
                pass
        for key in criteria :
            if type(key) is str and key not in self.columns :
                if key in self.wells or key in self.groups or key in self.regions :
                    keys += list(self.get_Keys('*'+self.nameSeparator+key))
                elif key in self.attributes :
                    keys += list(self.keyGen(key, self.attributes[key] ) )
                else :
                    keys += list(self.get_Keys(key))
            elif type(key) is str and key in self.columns :
                keys += [ key ]
            else :
                keys += list(self.find_Keys(key) )
        return tuple(keys)

    def get_units(self, items=None) :
        return self.get_Units(items)

    def get_Units(self, items=None) :
        if self.units is None:
            self.units = {}
        if items is None :
            return self.units
        uDic = {}
        if not isinstance(items,(list,tuple,dict,set,Index)):
            items = [items]
        for each in items :
            if each in self.units :
                uDic[each] = self.units[each]
            elif each in self.wells or each in self.groups or each in self.regions :
                for Key in self.get_Keys('*'+self.nameSeparator+each) :
                    uDic[each] = self.units[each]
            elif each in self.attributes :
                for att in self.keyGen(each, self.attributes[each] ) :
                    if att in self.units :
                        uDic[att] = self.units[att]
                    else :
                        uDic[att] = 'UNITLESS'
            elif len(self.get_Keys(each)) > 0 :
                for key in self.get_Keys(each) :
                    uDic[key] = self.units[key]
        return uDic

    def get_UnitsString(self, items=None) :
        if len(self.get_Units(items)) == 1 :
            return list(self.get_Units(items).values())[0]
        elif len(set(self.get_Units(items).values() )) == 1 :
            return list(set(self.get_Units(items).values() ))[0]

    def set_units(self, units, item=None):
        """
        This method can be used to define the units related to the values of a column (item).

        Parameters
        ----------
        units : str or list of str
            the units to be assigned
        item : str, optional
            The name of the column to apply the units. 
            The default is None. In this case the unit

        Raises
        ------
        ValueError
            when units can't be applied.
        TypeError
            when units or item has the wrong format.

        Returns
        -------
        None.

        """
        return self.set_Units(units=units, item=item)

    def set_Units(self, units, item=None):
        """
        This method can be used to define the units related to the values of a column (item).

        Parameters
        ----------
        units : str or list of str
            the units to be assigned
        item : str, optional
            The name of the column to apply the units. 
            The default is None. In this case the unit

        Raises
        ------
        ValueError
            when units can't be applied.
        TypeError
            when units or item has the wrong format.

        Returns
        -------
        None.

        """
        if item is not None and item not in self.columns and item != self.index.name and item not in self.index.names:
            raise ValueError("the required item '" + str(item) + "' is not in this SimDataFrame.")
        if type(units) in [list,tuple]:
            if type(item) in [list,tuple]:
                if len(item) == len(units):
                    return self.set_Units( dict(zip(item,units)) )
                else:
                    raise ValueError("both units and item must have the same length.")
            elif item is None:
                if len(units) == len(self.columns):
                    return self.set_Units( dict(zip(list(self.columns),units)) )
                else:
                    raise ValueError("units list must be the same length of columns in the SimDataFrame or must be followed by a list of items.")
            else:
                raise TypeError("if units is a list, items must be a list of the same length.")

        if type(units) is dict:
            for k,u in units.items():
                self.set_Units(u,k)
            return None
        
        if self.units is None:
            self.units = {}
        if type(self.units) is dict:
            if item is None and len(self.columns) > 1:
                raise ValueError("item must not be None")
            elif item is None and len(self.columns) == 1:
                return self.set_Units(units,[list(self.columns)[0]])
            elif item is not None:
                if item in self.columns:
                    if units is None:
                        self.units[item] = None
                    elif type(units) is str:
                        self.units[item] = units.strip()
                    else:
                        raise TypeError("units must be a string.")
                if item == self.index.name:
                    self.indexUnits = units.strip()
                    self.units[item] = units.strip()
                if item in self.index.names:
                    self.units[item] = units.strip()

    def keysByUnits(self) :
        """
        returns a dictionary of the units present in the SimDataFrame as keys
        and a list of the columns that has that units.
        """
        kDic = {}
        for k, v in self.units.items() :
            if v in kDic :
                kDic[v] += [k]
            else :
                kDic[v] = [k]
        return kDic

    def new_Units(self, key, units) :
        if type(key) is str :
            key = key.strip()
        if type(units) is str :
            units = units.strip()

        if self.units is None:
            self.units = {}
        
        if key not in self.units :
            self.units[key] = units
        else :
            if units != self.units[key] and self.speak :
                print("overwritting existing units for key '" + key + "': " + self.units[key] + ' -> ' + units )
            self.units[key] = units

    def is_Key(self, Key) :
        if type(Key) != str or len(Key)==0 :
            return False
        if Key in self.get_Keys() :
            return True
        else :
            return False

    def keyGen(self, mainKeys=[], itemKeys=[]) :
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
            k.strip(self.nameSeparator)
            if self.is_Key(k) :
                ListOfKeys.append(k)
            for i in itemKeys :
                i = i.strip(self.nameSeparator)
                if self.is_Key(k+self.nameSeparator+i) :
                    ListOfKeys.append(k+self.nameSeparator+i )
                elif k[0].upper() == 'W' :
                    wells = self.get_Wells(i)
                    if len(wells) > 0 :
                        for w in wells :
                            if self.is_Key(k+self.nameSeparator+w) :
                                ListOfKeys.append(k+self.nameSeparator+w )
                elif k[0].upper() == 'R' :
                    pass
                elif k[0].upper() == 'G' :
                    pass
        return ListOfKeys

    def filter(self, conditions=None, **kwargs) :
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
            returnString = bool(kwargs['returnString'] )
        returnFilter = False
        if 'returnFilter' in kwargs :
            returnFilter = bool(kwargs['returnFilter'] )
        returnFrame = False
        if 'returnFrame' in kwargs :
            returnFrame = bool(kwargs['returnFrame'] )
        if not returnFilter and not returnString and 'returnFrame' not in kwargs :
            returnFrame = True


        specialOperation = ['.notnull', '.null', '.isnull', '.abs']
        numpyOperation = ['.sqrt', '.log10', '.log2', '.log', '.ln']
        pandasAggregation = ['.any', '.all']
        PandasAgg = ''
        last = ['']

        def KeyToString(filterStr, key, PandasAgg) :
            if len(key) > 0 :
                # catch particular operations performed by Pandas
                foundSO, foundNO = '', ''
                if key in specialOperation :
                    if filterStr[-1] == ' ' :
                        filterStr = filterStr.rstrip()
                    filterStr += key+'()'
                else :
                    for SO in specialOperation :
                        if key.strip().endswith(SO) :
                            key = key[:-len(SO)]
                            foundSO =(SO if SO != '.null' else '.isnull' ) + '()'
                            break
                # catch particular operations performed by Numpy
                if key in numpyOperation :
                    raise ValueError("wrong syntax for '"+key+"(blank space before) in:\n   "+conditions)
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
                if key in ['.i', '.index'] :
                    filterStr = filterStr.rstrip()
                    filterStr += ' self.DF.index'
                # if key is a column
                elif key in self.columns :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.DF['"+key+"']"
                # key might be a wellname, attribute or a pattern
                elif len(self.find_Keys(key) ) == 1 :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.DF['"+ self.find_Keys(key)[0] +"']"
                elif len(self.find_Keys(key) ) > 1 :
                    filterStr = filterStr.rstrip()
                    filterStr += " self.DF["+ str(list(self.find_Keys(key)) ) +"]"
                    PandasAgg = '.any(axis=1)'
                else :
                    filterStr += ' ' + key
                filterStr = filterStr.rstrip()
                filterStr += foundSO + foundNO
                key = ''
                last.append('key')
            return filterStr, key, PandasAgg

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
            conditions = conditions.replace(' and ', ' & ')
        if ' or ' in conditions :
            conditions = conditions.replace(' or ', ' | ')
        if ' not ' in conditions :
            conditions = conditions.replace(' not ', ' ~ ')
        if '&' in conditions :
            AndOrNot = True
        elif '|' in conditions :
            AndOrNot = True
        elif '~' in conditions :
            AndOrNot = True

        # create Pandas compatible condition string
        filterStr =  ' ' + '('*AndOrNot
        key = ''
        cond, oper = '', ''
        i = 0
        while i < len(conditions) :

            # catch logital operators
            if conditions[i] in ['&', "|", '~'] :
                filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
                filterStr = filterStr.rstrip()
                auto = ' self.DF.index' if last[-1] in ['(', 'cond', 'oper'] else ''
                filterStr += auto + ' )' + PandasAgg + ' ' + conditions[i] + '('
                last.append('log')
                PandasAgg = ''
                i += 1
                continue

            # catch enclosed strings
            if conditions[i] in ['"', "'", '['] :
                if conditions[i] in ['"', "'"] :
                    try :
                        f = conditions.index(conditions[i], i+1 )
                    except :
                        raise ValueError('wring syntax, closing ' + conditions[i] + ' not found in:\n   '+conditions)
                else :
                    try :
                        f = conditions.index(']', i+1 )
                    except :
                        raise ValueError("wring syntax, closing ']' not found in:\n   "+conditions)
                if f > i+1 :
                    key = conditions[i+1:f]
                    filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
                    i = f+1
                    continue

            # pass blank spaces
            if conditions[i] == ' ' :
                filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
                if len(filterStr) > 0 and filterStr[-1] != ' ' :
                    filterStr += ' '
                i += 1
                continue

            # pass parenthesis
            if conditions[i] in ['(', ')'] :
                if conditions[i] == ')' and filterStr.rstrip()[-1] == '(' :
                    filterStr = filterStr.rstrip()[:-1]
                    last.pop()
                else :
                    if last[-1] in ['cond', 'oper'] : key = 'self.DF.index'
                    filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
                    filterStr += conditions[i]
                    last.append(conditions[i])
                i += 1
                continue

            # catch conditions
            if conditions[i] in ['=', '>', '<', '!'] :
                cond = ''
                f = i+1
                while conditions[f] in ['=', '>', '<', '!'] :
                    f += 1
                cond = conditions[i:f]
                if cond == '=' :
                    cond = '=='
                elif cond in ['=>', '=<', '=!'] :
                    cond = cond[::-1]
                elif cond in ['><', '<>'] :
                    cond = '!='
                if key == '' : key = 'self.DF.index'
                filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
                filterStr = filterStr.rstrip()
                filterStr += ' ' + cond
                last.append('cond')
                i += len(cond)
                continue

            # catch operations
            if conditions[i] in ['+', '-', '*', '/', '%', '^'] :
                oper = ''
                f = i+1
                while conditions[f] in ['+', '-', '*', '/', '%', '^'] :
                    f += 1
                oper = conditions[i:f]
                oper = oper.replace('^', '**')
                if last[-1] not in ['key'] : key = 'self.DF.index'
                filterStr, key, PandasAgg = KeyToString(filterStr, key, PandasAgg)
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
        if filterStr[0] in ['=', '>', '<', '!'] :
            filterStr = 'self.DF.index ' + filterStr
        elif filterStr[-1] in ['=', '>', '<', '!'] :
            filterStr = filterStr + ' self.DF.index'
        # close last parethesis and aggregation
        filterStr += ' )' * bool(AndOrNot + bool(PandasAgg) ) + PandasAgg
        # open parenthesis for aggregation, if needed
        if not AndOrNot and bool(PandasAgg) :
            filterStr = '(' + filterStr

        retTuple = []
        # print(last)
        if returnString :
            retTuple += [ filterStr ]
        if returnFilter or returnFrame :
            try :
                filterArray = eval(filterStr )
            except :
                return None
        if returnFilter :
            retTuple += [ filterArray ]
        if returnFrame :
            retTuple += [ self.DF[ filterArray ] ]

        if len(retTuple ) == 1 :
            return retTuple[0]
        else :
            return tuple(retTuple )

    def integrate(self, method='trapz') :
        """
        Calculates numerical integration, using trapezoidal method,
        or constant value of the columns values over the index values.

        method parameter can be: 'trapz' to use trapezoidal method
                                 'const' to constant vale multiplied
                                         by delta-index

        Returns a new SimDataFrame
        """
        method=method.lower().strip()

        dt = np.diff(self.index )
        dtUnits = self.indexUnits
        if str(dt.dtype).startswith('timedelta') :
            dt = dt.astype('timedelta64[s]').astype('float64')/60/60/24
            dtUnits = 'DAYS'

        if method in ['trapz', 'trapeziod'] :
            Vmin = np.minimum(self.DF[:-1].set_index(self.index[1:]), self.DF[1:] )
            Vmax = np.maximum(self.DF[:-1].set_index(self.index[1:]), self.DF[1:] )
            Cumulative =(dt * Vmin.transpose() ).transpose() +(dt *(Vmax - Vmin ).transpose() / 2.0 ).transpose()
        elif method in ['const', 'constant'] :
            Cumulative = (dt *(self.DF[:-1]).transpose() ).transpose()[1:]

        newUnits = {}
        for C, U in self.units.items() :
            if len(U.split('/'))==2 and(U.split('/')[-1].upper() == dtUnits or(U.split('/')[-1].upper() in ['DAY', 'DAYS'] and dtUnits == 'DAYS' ) ) :
                newUnits[C]=U.split('/')[0]
            else :
                newUnits[C]=U+'*'+dtUnits

        firstRow = DataFrame(dict(zip(self.columns, [0.0]*len(self.columns))), index=['0']).set_index(DatetimeIndex([self.index[0]]) )
        params = self._SimParameters
        params['units'] = newUnits
        return SimDataFrame(data=np.cumsum(firstRow.append(Cumulative ) ), **params)
    
    def sort_values(self,by=None, axis='--auto', ascending=True, inplace=False, kind='quicksort', na_position='last', ignore_index=False, key=None) :
        if by is None and axis == '--auto' :
            if len(self.index) == 1 and len(self.columns) > 1 :
                result = SimDataFrame(data=self.DF.T[self.DF.T.columns[0]].sort_values(axis=0,
                                                                                  ascending=ascending,
                                                                                  inplace=False,
                                                                                  kind=kind,
                                                                                  na_position=na_position,
                                                                                  ignore_index=ignore_index,
                                                                                  key=key).T, **self._SimParameters)
                if inplace :
                    self = result
                    return None
                else :
                    return result
            elif len(self.index) > 1 and len(self.columns) == 1 :
                if inplace :
                    self.DF.sort_values(by=self.columns[0], axis=0, ascending=ascending, inplace=True, kind=kind, na_position=na_position, ignore_index=ignore_index, key=key)
                    return None
                else :
                    return SimDataFrame(data=self.DF.sort_values(by=self.columns[0], axis=0, ascending=ascending, inplace=True, kind=kind, na_position=na_position, ignore_index=ignore_index, key=key), **self._SimParameters)
            else :
                if axis == '--auto' :
                    axis = 0
                if inplace :
                    self.DF.sort_values(axis=axis, ascending=ascending, inplace=True, kind=kind, na_position=na_position, ignore_index=ignore_index, key=key)
                    return None
                else :
                    return SimDataFrame(data=self.DF.sort_values(axis=axis, ascending=ascending, inplace=True, kind=kind, na_position=na_position, ignore_index=ignore_index, key=key), **self._SimParameters)
        else :
            if axis == '--auto' :
                axis = 0
            if inplace :
                self.DF.sort_values(by=by, axis=axis, ascending=ascending, inplace=True, kind=kind, na_position=na_position, ignore_index=ignore_index, key=key)
                return None
            else :
                return SimDataFrame(data=self.DF.sort_values(by=by, axis=axis, ascending=ascending, inplace=True, kind=kind, na_position=na_position, ignore_index=ignore_index, key=key), **self._SimParameters)

    def head(self,n=5):
        return SimDataFrame(data=self.DF.head(n),**self._SimParameters)
    
    def tail(self,n=5):
        return SimDataFrame(data=self.DF.head(n),**self._SimParameters)

    def jitter(self,std=0.10) :
        """
        add jitter the values of the SimDataFrame
        """
        return jitter(self,std)

    def melt(self,**kwargs):
        from .._common.functions import _meltDF
        return _meltDF(self,FullOutput=False)

    def DaysInYear(self,column=None):
        return self.daysInYear(column=column)
    
    def daysinyear(self,column=None):
        return self.daysInYear(column=column)
    
    def daysInYear(self,column=None):
        params = self._SimParameters
        params['index'] = self.index
        params['name'] = 'DaysInYear'
        params['units'] = 'days'
        if column is not None:
            if type(column) is str and column in self.columns:
                if self[column].dtype in ('int','int64') and self[column].min() > 0 :
                    return daysInYear(self[column])
                elif 'datetime' in str(self[column].dtype):
                    return daysInYear(self[column])
                else:
                    raise ValueError('selected column is not a valid date or year integer')
            elif type(column) is str and column not in self.columns:
                raise ValueError('the selected column is not in this SimDataFrame')
            elif type(colum) is list:
                result = self._class(data={},index=self.index,**self._SimParameters)
                for col in column:
                    if col in self.columns:
                        result[col] = daysInYear(self[col])
                return result
        else:
            if self.index.dtype in ('int','int64') and self.index.min() > 0 :
                return self._class( data=self.values, index=list(daysInYear(self.index)), columns=self.columns, **self._SimParameters )
            elif 'datetime' in str(self.index.dtype):
                return self._class( data=self.values, index=list(daysInYear(self.index)), columns=self.columns, **self._SimParameters )
            else:
                raise ValueError('index is not a valid date or year integer')

    def RealYear(self,column=None):
        return self.realYear(column)

    def realyear(self,column=None):
        return self.realYear(column)

    def realYear(self,column=None):
        if column is not None:
            if type(column) is str and column in self.columns:
                if 'datetime' in str(self[column].dtype):
                    return realYear(self[column])  
                else :
                    raise ValueError('selected column is not a valid date format')
            elif type(column) is str and column not in self.columns:
                raise ValueError('the selected column is not in this SimDataFrame')
            elif type(colum) is list:
                result = self._class(data={},index=self.index,**self._SimParameters)
                for col in column:
                    if col in self.columns:
                        result[col] = daysInYear(self[col])
                return result
        else:
            if 'datetime' in str(self.index.dtype):
                return self._class( data=self.values, index=list(realYear(self.index)), columns=self.columns, **self._SimParameters )
            else:
                raise ValueError('index is not a valid date or year integer')
                


def daysInYear(year):
    """
    returns the number of days in a particular year

    Parameters
    ----------
    year : int, date, datetime or array-like of int, date, or datetime
        The year to calculate the number of day.
        Can a single year, represented as an integer or as date or datetime object
        Also, list or array of year is accepted.

    Returns
    -------
    int or array of ints, according to the input
    """
    if type(year) in (int,float):
        return dt.date(int(year), 12, 31).timetuple().tm_yday
    if type(year) in (dt.date, dt.datetime):
        return dt.date(year.timetuple().tm_year, 12, 31).timetuple().tm_yday
    if type(year) is pd.Timestamp:
        return dt.date(year.year,12,31).timetuple().tm_yday
    
    if type(year) in (list,tuple,np.ndarray):
        if np.array(year).dtype in ('int','int64','float','float64') :
            return np.array([ dt.date(int(Y), 12, 31).timetuple().tm_yday for Y in year ], dtype=int)
        elif 'datetime' in str(np.array(year).dtype):
            return np.array([ dt.date(Y.astype(object).timetuple().tm_year, 12, 31).timetuple().tm_yday for Y in year ], dtype=int)
        elif len(set(map(type,year))) == 1 and list(set(map(type,year)))[0] in (dt.date, dt.datetime):
            return np.array([ dt.date(Y.timetuple().tm_year, 12, 31).timetuple().tm_yday for Y in year ], dtype=int)
        elif len(set(map(type,year))) == 2 and list(set(map(type,year)))[0] in (dt.date, dt.datetime) and list(set(map(type,year)))[1] in (dt.date, dt.datetime):
            return np.array([ dt.date(Y.timetuple().tm_year, 12, 31).timetuple().tm_yday for Y in year ], dtype=int)
    if isinstance(year,pd.DatetimeIndex):
        return np.array([ dt.date(Y.year, 12, 31).timetuple().tm_yday for Y in year ], dtype=int) 
    
    if isinstance(year,SimSeries):
        params = year._SimParameters
        params['name'] = 'DaysInYear'
        params['units'] = 'days'
        return SimSeries(data=np.array([ dt.date(Y.year, 12, 31).timetuple().tm_yday for Y in year ], dtype=int), index=year.index, **params)
    
    if isinstance(year,Series):
        return Series(data=np.array([ dt.date(Y.year, 12, 31).timetuple().tm_yday for Y in year ], dtype=int), index=year.index)

    raise ValueError("input 'year' is not a valid date or year integer")

def realYear(date):
    """
    returns a float corresponding for the year and the fraction of year represented by the date.

    Parameters
    ----------
    date : date, datetime, or array of date objects

    Returns
    -------
    float
    """
    if type(date) in (dt.date, dt.datetime):
        return date.timetuple().tm_year + date.timetuple().tm_yday / dt.date(date.timetuple().tm_year, 12, 31).timetuple().tm_yday
    if type(date) is pd.Timestamp:
        return date.year + dt.date(date.year,date.month,date.day).timetuple().tm_yday / dt.date(date.year, 12, 31).timetuple().tm_yday
    
    if type(date) is np.ndarray and 'datetime' in str(np.array(date).dtype):
            return np.array([ Y.year + dt.date(Y.year, Y.month, Y.day).timetuple().tm_yday / dt.date(Y.year, 12, 31).timetuple().tm_yday for Y in pd.to_datetime(date) ], dtype=float)
    if type(date) in (list,tuple):
        if len(set(map(type,date))) == 1 and list(set(map(type,date)))[0] in (dt.date, dt.datetime):
            return np.array([ Y.timetuple().tm_year + Y.timetuple().tm_yday / dt.date(Y.timetuple().tm_year, 12, 31).timetuple().tm_yday for Y in date ], dtype=float)
        elif len(set(map(type,date))) == 2 and list(set(map(type,date)))[0] in (dt.date, dt.datetime) and list(set(map(type,date)))[1] in (dt.date, dt.datetime):
            return np.array([ Y.timetuple().tm_year + Y.timetuple().tm_yday / dt.date(Y.timetuple().tm_year, 12, 31).timetuple().tm_yday for Y in date ], dtype=float)
    if isinstance(date,pd.DatetimeIndex):
        return np.array([ Y.year + dt.date(Y.year,Y.month,Y.day).timetuple().tm_yday / dt.date(Y.year, 12, 31).timetuple().tm_yday for Y in date ], dtype=float) 

    if isinstance(date,SimSeries):
        params = date._SimParameters
        params['name'] = 'Year'
        params['units'] = 'year'
        return SimSeries(data=realYear(date.to_Pandas()), **params)
    
    if isinstance(date,Series):
        return Series(data=np.array([ Y.year + dt.date(Y.year, Y.month, Y.day).timetuple().tm_yday / dt.date(Y.year, 12, 31).timetuple().tm_yday for Y in date ], dtype=float), index=date.index)

def _MergeIndex(left, right, how='outer', *, drop_duplicates=True):
    """
    returns an left and right Frames or Series reindexed with a common index.

    Parameters
    ----------
    left : Series, SimSeries, DataFrame or SimDataFrame
        The left frame to merge
    right : Series, SimSeries, DataFrame or SimDataFrame
        The right frame to merge
    how : str, optional
        The merge method to be used. 
        The default is 'outer'.
    drop_duplicates : boo, optional
        If True, drop duplicated lines to avoid reindexing error due to repeated rows.
        If the index has duplicated values but the row is not entire equal reindexing will raise error.

    Raises
    ------
    ValueError
        If how parameter is not valir.

    Returns
    -------
    Series, SimSeries, DataFrame or SimDataFrame
        Reindexed to the merged index.
    Series, SimSeries, DataFrame or SimDataFrame
        Reindexed to the merged index.

    """
    if how not in ('outer','inner','left','right','cross'):
        raise ValueError("how must be 'outer', 'iner', 'left', 'right' or 'cross'")
    
    # if both indexes are equal
    if len(left.index) == len(right.index) and (left.index == right.index).all():
        return left, right
    
    # if are different, extract a Series accoring to the type of input    
    else:
        # from datafiletoolbox import SimSeries, SimDataFrame
        # from pandas import Series, DataFrame
        # checking left
        if type(left) is SimDataFrame:
            ileft = left.DF.iloc[:,0]
        elif type(left) is SimSeries:
            ileft = left.S
        elif type(left) is DataFrame:
            ileft = left.iloc[:,0]
        elif type(left) is Series:
            ileft = left
        
        # checking right
        if type(right) is SimDataFrame:
            iright = right.DF.iloc[:,0]
        elif type(right) is SimSeries:
            iright = right.S
        elif type(right) is DataFrame:
            iright = right.iloc[:,0]
        elif type(right) is Series:
            iright = right
        
        # merge the indexes
        newIndex= pd.merge(ileft,iright,how=how,left_index=True,right_index=True).index
        # return original dataframes reindexed to the merged index
        if bool(drop_duplicates):
            return left.drop_duplicates().reindex(index=newIndex), right.drop_duplicates().reindex(index=newIndex)
        else:
            return left.reindex(index=newIndex), right.reindex(index=newIndex)