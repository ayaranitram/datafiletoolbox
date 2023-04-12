# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:14:35 2020

@author: MCARAYA
"""

__version__ = '0.60.23'
__release__ = 20230412
__all__ = ['SimResult']

from .. import _dictionaries
from .._Classes.Errors import OverwritingError, InvalidKeyError, MissingDependence
from .._Classes.SimPandas import SimSeries, SimDataFrame
from .._common.stringformat import date as _strDate, isDate as _isDate, multisplit as _multisplit, \
    isnumeric as _isnumeric, getnumber as _getnumber
from .._common.functions import _is_SimulationResult, _mainKey, _itemKey, _wellFromAttribute, _isECLkey, _keyType, \
    tamiz as _tamiz, _meltDF  # _AttributeFromKeys,
from .._common.inout import _extension, _verbose
from ..PlotResults.SmartPlot import Plot
# from .._common.progressbar import progressbar
from .._common.units import unit
from .._common.units import convertUnit
from .._common.units import convertible as convertibleUnits
from matplotlib.colors import is_color_like
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import timedelta
import pandas as pd
from pandas import Series, DataFrame
import numpy as np
import fnmatch
import random
# import json
import os
from functools import reduce

# creating vectorized numpy object for len function
nplen = np.vectorize(len)

# _verbose(1, 1, '\n  initializing most commong units conversions...')
_verbose(0, 0, convertibleUnits('SM3', 'MMstb', False))
_verbose(0, 0, convertibleUnits('SM3', 'Bscf', False))
_verbose(0, 0, convertibleUnits('SM3', 'Tscf', False))
_verbose(0, 0, convertibleUnits('STM3', 'MMstb', False))
_verbose(0, 0, convertibleUnits('KSTM3', 'MMstb', False))
_verbose(0, 0, convertibleUnits('KSM3', 'Bscf', False))
_verbose(0, 0, convertibleUnits('MSM3', 'Tscf', False))
_verbose(0, 0, convertibleUnits('SM3/DAY', 'Mstb/day', False))
_verbose(0, 0, convertibleUnits('SM3/DAY', 'stb/day', False))
_verbose(0, 0, convertibleUnits('SM3/DAY', 'MMscf/day', False))
_verbose(0, 0, convertibleUnits('SM3/DAY', 'Mscf/day', False))
_verbose(0, 0, convertibleUnits('STM3/DAY', 'Mstb/day', False))
_verbose(0, 0, convertibleUnits('STM3/DAY', 'stb/day', False))
_verbose(0, 0, convertibleUnits('KSM3/DAY', 'MMscf/day', False))
_verbose(0, 0, convertibleUnits('KSM3/DAY', 'Mscf/day', False))
_verbose(0, 0, convertibleUnits('STM3/DAY', 'SM3/DAY', False))
_verbose(0, 0, convertibleUnits('KSTM3/DAY', 'SM3/DAY', False))
_verbose(0, 0, convertibleUnits('KSM3/DAY', 'SM3/DAY', False))
_verbose(0, 0, convertibleUnits('STM3', 'SM3', False))
_verbose(0, 0, convertibleUnits('KSTM3', 'SM3', False))
_verbose(0, 0, convertibleUnits('KSM3', 'SM3', False))
_verbose(0, 0, convertibleUnits('MSM3', 'SM3', False))
_verbose(0, 0, convertibleUnits('KPA', 'BARSA', False))
_verbose(0, 0, convertibleUnits('BARSA', 'psia', False))
_verbose(0, 0, convertibleUnits('KPA', 'psia', False))
_verbose(0, 0, convertibleUnits('DATE', 'DATES', False))
_verbose(0, 0, convertibleUnits('DAY', 'DAYS', False))
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
            In: ObjectVariable(Key, Index)

        -> Calling the object with no argument will return this help. i.e.:
            In: ObjectVariable()
                   ___________________________________
                <<< HELP of Simulation Result Objects >>>

        -> Calling the object with a string (a single key) as Key argument will
           return a Numpy array of the requested key.
           The Index argument is ignored in this case, i.e.:
            In: ObjectVariable('FOIP')
            Out:
            array([69170384., 69170384., 69170384., ..., 30077594., 30077594., 30069462.])

        -> Calling the object with a list (one or multiple keys) as Key argument
           will return a Pandas DataFrame.
           The Index argument is 'TIME' by default but any other key can be
           selected as index, i.e.:
            In: ObjectVariable([ 'FOIP', 'FOPT' ], 'DATE')
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
           [ Key ] returns a Pandas Series with the column Key, i.e.:
            In: ObjectVariable[ 'FOPR' ]
            Out:
            0.00          0.000000
            3.15          0.000000
                           ...
            17387.00    286.179718
            17407.00    281.440918
            Name: FOPR, Length: 7692, dtype: float64

           > one or multiple Key or Attributes* between double square braket
           [[ Key, Attribute ]] returns a Pandas DataFrame, i.e.:
            In: ObjectVariable[[ 'FOPR', 'WOPR' ]]
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

        .get_Vector(list_of_keywords)
            returns a dictionary with the Numpy arrays for the requested
            keywords, i.e.:
                In: ObjectVariable.get_Vector([ 'FOIP', 'FOPT', 'FOPR' ])
                Out:
                    {'FOPR': array([  0., 0., 0., ..., 282.94104004, 282.04125977, 281.44091797]),
                     'FOPT': array([       0., 0., 0., ..., 41480784., 41482196., 41483604.]),
                     'FOIP': array([69170384., 69170384., 69170384., ..., 30077594., 30077594., 30069462.])}

        .set_Vector(Key, VectorData, Units, DataType='auto', overwrite=None)
            loads a vector into the SimulationResult object, arguments are:
                Key : the name or keyword where the data will be loaded
                VectorData : a Numpy array (of the same length as the arrays already in the results)
                Units : a string indicating the units of these data
                DataType : the strings 'float', 'int', 'date' or 'auto'
                overwrite : True or False, if True any existing data under the same Key will be overwritten.

        .get_DataFrame(list_of_keywords, optional index)
            returns a Pandas DataFrame with the requested keywords.
            The optional argument Index can be used to obtain a DataFrame
            indexed by any other Key from the simulation, default index
            is 'TIME' but 'DATE', volume in place or cumulatives can be
            good examples of other useful indexes. i.e.:
                In: ObjectVariable.get_DataFrame([ 'WOPR:W1', 'WOPT:W1' ], 'DATE')
                Out:
                                          WOPT:W1       WOPR:W1
                1996-05-04 00:00:00           0.0           0.0
                1996-05-07 03:36:00           0.0           0.0
                                          ...           ...
                2043-12-11 00:00:00     6499611.0           0.0
                2043-12-31 00:00:00     6499611.0           0.0

                In: ObjectVariable.get_DataFrame([ 'WOPR:W1', 'WOPR:W2' ], 'FOPT')
                Out:
                                 WOPT:W1       WOPT:W2
                0.0                  0.0         0.000
                0.0                  0.0         0.000
                                 ...           ...
                41477948.0     6499611.0   1918401.625
                41483604.0     6499611.0   1918401.625

        .get_Unit(keyword_as_string or list_of_keywords)
            if the argument is a string (a single keyword),
            returns the units of that keyword as a strinG, i.e.:
                In: ObjectVariable.get_Unit('FOPT')
                Out: 'SM3'

            if the argument is a list (one or multiple keywords), returns
            a dictionary containg the units of that keywords as a strings.
                In: ObjectVariable.get_Unit(['FOPT', 'FOPR'])
                {'FOPT': 'SM3', 'FOPR': 'SM3/DAY'}

            if no argument is provided, returns a dictionary with all the
            units defined in the simulation results, i.e.:
                In: ObjectVariable.get_Unit()
                Out: {'FOPT': 'SM3', 'FOPR': 'SM3/DAY', ...}


    """

    def __init__(self, verbosity=2):
        self.set_Verbosity(verbosity)
        self.SimResult = True
        self.useSimPandas = False
        self.kind = None
        self.results = None
        self.name = None
        self.nameSeparator = ':'
        self.path = None
        self.start = None
        self.end = None
        self.filter = {'key': [None], 'min': [None], 'max': [None], 'condition': [None], 'filter': None, 'reset': True,
                       'incremental': [None], 'operation': [None]}
        self.filterUndo = None
        self.wells = tuple()
        self.groups = tuple()
        self.regions = tuple()
        self.keys_ = tuple()
        self.attributes = {}
        self.vectors = {}
        self.units = {}
        self.overwrite = False
        self.null = None
        self.plotUnits = {}
        self.color = (random.random(), random.random(), random.random())
        self.keyColors = {}
        self.width = None
        self.keyWidths = {}
        self.marker = 'None'
        self.markersize = 1.0
        self.keyMarkers = {}
        self.keyMarkersSize = {}
        self.style = '-'
        self.key_styles = {}
        self.alpha = 1.0
        self.keyAlphas = {}
        self.historyAsDots = True
        self.colorGrouping = 6
        self.DTindex = 'TIME'
        self.TimeVector = None
        self.restarts = []
        self.restartFilters = {}
        self.continuations = []
        self.continuationFilters = {}
        self.vectorsRestart = {}
        self.vectorsContinue = {}
        self.vectorTemplate = None
        self.savingFilter = None
        self.pandasColumns = {'HEADERS': {}, 'COLUMNS': {}, 'DATA': {}}
        self.fieldtime = (None, None, None)
        self.GORcriteria = (10, 'Mscf/stb')
        self.WCcriteria = 1
        self.wellsLists = {}
        self.printMessages = 0
        self.zeroThreshold = 1e-6

    def initialize(self, **kwargs):
        """
        run intensive routines, to have the data loaded and ready
        """
        # if self.start is None and self.is_Key('DATE'):
        #     self.start = min(self('DATE').astype('datetime64[s]'))
        # elif self.start is not None:
        #     self.start = np.datetime64(self.start)
        # if self.end is None and self.is_Key('DATE'):
        #     self.end = max(self('DATE').astype('datetime64[s]'))
        # elif self.end is not None:
        #     self.end = np.datetime64(self.end)
        if not self.is_Key('YEAR'):
            self.createYEAR()
        if not self.is_Key('MONTH'):
            self.createMONTH()
        if not self.is_Key('DAY'):
            self.createDAY()
        if not self.is_Key('DATE'):
            self.createDATES()
        if not self.is_Key('DATES'):
            self.createDATES()
        if not self.is_Key('TIME'):
            self.createTIME()
        _ = self.get_start()
        _ = self.get_end()

        if ('preload' not in kwargs) or ('preload' in kwargs and kwargs['preload'] is True):
            self.get_Producers()
            self.get_Injectors()
        else:
            self.wellsLists = {wellList: [] for wellList in
                               ['WaterProducers', 'GasProducers', 'OilProducers', 'Producers', 'WaterInjectors',
                                'GasInjectors', 'OilInjectors', 'Injectors']}
        self.use_SimPandas()
        self.set_RestartsTimeVector()
        # self.set_savingFilter()
        self.set_vectorTemplate()
        if 'index' in kwargs:
            if self.is_Key(kwargs['index']):
                _ = self.set_index(kwargs['index'])
            else:
                print(
                    "\n ·-> the requested index is not a valid key in this object: '" + str(kwargs['index']) + "' !!!")

    def keys(self):
        return self.keys_

    def get_start(self):
        if self.start is not None:
            try:
                self.start = np.datetime64(self.start)
            except:
                self.start = None
        if self.start is None and self.is_Key('DATE'):
            self.start = min(self('DATE').astype('datetime64[s]'))
        elif self.start is not None and self.is_Key('DATE') and self.start > min(self('DATE')):
            self.start = min(self('DATE').astype('datetime64[s]'))
        return self.start

    def get_end(self):
        if self.end is not None:
            try:
                self.end = np.datetime64(self.end)
            except:
                self.end = None
        if self.end is None and self.is_Key('DATE'):
            self.end = max(self('DATE').astype('datetime64[s]'))
        elif self.end is not None and self.is_Key('DATE') and self.end < max(self('DATE')):
            self.end = max(self('DATE').astype('datetime64[s]'))
        elif self.end is None and not self.is_Key('DATE') and self.is_Key('TIME') and self.start is not None and type(
                self.get_Units('TIME')) is str and self.get_Units('TIME').upper() in ['DAY', 'DAYS']:
            self.end = self.start + np.timedelta64(int(max(self('TIME')) * 24 * 60 * 60), 's')
        return self.end

    def set_vectorTemplate(self, Restart=False, Continue=False):
        if self.vectorTemplate is None:
            self.vectorTemplate = np.array([0] * len(self.get_RawVector(self.get_TimeVector())[self.get_TimeVector()]))
        if Restart:
            self.vectorTemplate = np.array(
                [-1] * len(self.checkRestarts(self.get_TimeVector())[self.get_TimeVector()]) + list(
                    self.vectorTemplate[self.vectorTemplate != -1]))
        if Continue:
            self.vectorTemplate = np.array(list(self.vectorTemplate[self.vectorTemplate != 1]) + [1] * len(
                self.checkContinuations(self.get_TimeVector())[self.get_TimeVector()]))
        if not Restart and not Continue:
            self.vectorTemplate = np.array([0] * len(self.get_RawVector(self.get_TimeVector())[self.get_TimeVector()]))

    def get_vectorTemplate(self):
        if self.vectorTemplate is None:
            self.set_vectorTemplate()
        if len(self.get_Vector(self.get_TimeVector())[self.get_TimeVector()]) < len(
                self.get_UnfilteredVector(self.get_TimeVector())[self.get_TimeVector()]):
            usedFilter = np.array([self.get_UnfilteredVector(self.get_TimeVector())[self.get_TimeVector()][i] in
                                   self.get_Vector(self.get_TimeVector())[self.get_TimeVector()] for i in
                                   range(len(self.get_UnfilteredVector(self.get_TimeVector())[self.get_TimeVector()]))])
            return self.vectorTemplate[usedFilter]
        elif len(self.get_Vector(self.get_TimeVector())) > len(self.get_UnfilteredVector(self.get_TimeVector())):
            raise ValueError('something went wrong')
        else:
            return self.vectorTemplate

    # # savingFilter is deprecrecated, from now on is easier to use vectorTemplate. get_savingFilter will be a wrapper for get_vectorTemplate
    # def set_savingFilter(self, Restart=False, Continue=False):
    #     if self.savingFilter is None:
    #         if self.TimeVector is None:
    #             self.set_RestartsTimeVector()
    #         self.savingFilter = np.array([True]*len(self.get_UnfilteredVector(self.TimeVector)[self.TimeVector]))
    #         _verbose(self.speak, 2, " <set_savingFilter> started savingFilter with lenght " + str(len(self.get_UnfilteredVector(self.TimeVector)[self.TimeVector])) + " using vector '"+str(self.TimeVector)+"' as reference")
    #     else:
    #         if Restart:
    #             _verbose(self.speak, 2, " <set_savingFilter> updating savingFilter for Restart:\nprevious savingFilter of length " + str(len(self.get_savingFilter()))  + "\nfor new vectors of length " + str(len(self.get_UnfilteredVector(self.TimeVector)[self.TimeVector])))
    #             self.savingFilter = np.array([False]*(len(self.get_UnfilteredVector(self.TimeVector)[self.TimeVector])-len(self.get_savingFilter())) + list(self.get_savingFilter()))
    #         elif Continue:
    #             _verbose(self.speak, 2, " <set_savingFilter> updating savingFilter for Continue:\nprevious savingFilter of length " + str(len(self.get_savingFilter())) + "\nfor new vectors of length " + str(len(self.get_UnfilteredVector(self.TimeVector)[self.TimeVector])))
    #             self.savingFilter = np.array(list(self.get_savingFilter()) + [False]*(len(self.get_Vector(self.TimeVector)[self.TimeVector])-len(self.get_savingFilter())))
    #         else:
    #             _verbose(self.speak, 2, " <set_savingFilter> reseting savingFilter with lenght " + str(len(self.get_Vector(self.TimeVector)[self.TimeVector])) + " using vector '"+str(self.TimeVector)+"' as reference")
    #             self.savingFilter = np.array([True]*len(self.get_UnfilteredVector(self.TimeVector)[self.TimeVector]))
    # savingFilter is deprecrecated, from now on is easier to use vectorTemplate. get_savingFilter will be a wrapper for get_vectorTemplate

    def get_savingFilter(self):
        # if self.savingFilter is None:
        #     self.set_savingFilter()
        return self.get_vectorTemplate()[self.get_vectorTemplate() == 0]

    def set_RestartsTimeVector(self, time_vector=None):
        if time_vector is None:
            for Time in ['DATE', 'DATES', 'TIME', 'DAYS', 'MONTHS', 'YEARS', 'Date', 'date', 'Dates', 'dates', 'Time',
                         'time']:
                if self.is_Key(Time):
                    self.TimeVector = Time
                    break
        elif type(time_vector) is str:
            if self.is_Key(time_vector):
                self.TimeVector = time_vector
            else:
                raise ValueError(' the provided TimeVector is not a valid key in this simulation.')
        else:
            raise TypeError(' TimeVector must be a string name of a valid Key.')

    def get_TimeVector(self):
        return self.get_RestartsTimeVector()

    def get_RestartsTimeVector(self):
        if self.TimeVector is None:
            self.set_RestartsTimeVector()
        return self.TimeVector

    def use_SimPandas(self, switch=True):
        switch = bool(switch)
        self.useSimPandas = bool(switch)
        if switch:
            _verbose(1, self.speak, "\n-> using SimPandas <-")
        else:
            _verbose(1, self.speak, "\n-> using Pandas <-")

    @property
    def index(self):
        return self[[self.keys_[0]]].index

    @property
    def columns(self):
        return list(self.keys_)

    def __call__(self, key=None, index=None):
        if key is None and index is None:
            print(SimResult.__doc__)
        elif key is None and index is not None:
            return pd.Index(self.get_Vector(index)[index])
        elif type(key) is str and len(key) > 0 and index is None:
            return self.get_Vector(key)[key]
        elif type(key) in (list, tuple) and len(key) > 0 or index is not None:
            if index is None:
                index = self.DTindex
            data = self.get_DataFrame(key, index)
            if self.useSimPandas:
                units = self.get_Units(key)
                if type(units) is str:
                    units = {key: units}
                if units is None:
                    units = {key: None}
                unitsIndex = self.get_Units(index)
                units[index] = unitsIndex
                return SimDataFrame(data=data, units=units, indexName=index, indexUnits=unitsIndex, nameSeparator=':')
            else:
                return data

    def __getitem__(self, item):
        if type(item) is tuple:
            if len(item) == 0:
                return None
            else:
                keys, indexes = _tamiz(item)
                meti = self.__getitem__(keys)
                if meti is None:
                    return None
                try:
                    return meti.loc[indexes]
                except:
                    try:
                        return meti.iloc[indexes]
                    except:
                        return None

        if type(item) is str:
            if self.is_Key(item):
                return self.__call__([item])[item]
            if item in self.wells or item in self.groups or item in self.regions:
                keys = list(self.get_keys('*:' + item))
                return self.__getitem__(keys)
            if item in ['FIELD', 'ROOT']:
                keys = list(self.get_keys('F*'))
                return self.__getitem__(keys)
            if len(self.get_keys(item)) > 0:
                keys = list(self.get_keys(item))
                return self.__getitem__(keys)
            if len(self.find_Keys(item)) > 0:
                keys = list(self.find_Keys(item))
                return self.__getitem__(keys)
            if len(self.get_Vector(item)) == 1 and self.get_Vector(item)[item] is not None:
                return self.__call__([item])[item]
            else:
                meti = self.__getitem__([item])
                if meti is None:
                    return None
                elif len(meti.columns) == 1:
                    _verbose(self.speak, 2,
                             " a single item match the pattern, \n return the series for the item '" + meti.columns[
                                 0] + "':")
                    if self.null is None:
                        return meti[meti.columns[0]]
                    return meti.replace(self.null, 0)[meti.columns[0]]
                else:
                    _verbose(self.speak, 2,
                             " multiple items match the pattern, \n return a dataframe with all the matching items:")
                    if self.null is None:
                        return meti
                    return meti.replace(self.null, 0)

        if type(item) is list:
            def each_item(each):
                each = each.strip(' :')
                if self.is_Key(each):
                    return [each]
                elif each in self.attributes:
                    return self.attributes[each]
                elif ':' in each and len(each.split(':')) == 2:
                    attribute, pattern = each.split(':')
                    return self.keyGen(attribute, pattern)
                elif each in self.wells or each in self.groups or each in self.regions:
                    return list(self.get_keys('*:' + each))
                elif each in ['FIELD', 'ROOT']:
                    return list(self.get_keys('F*'))
                else:
                    return list(self.get_keys(each))

            cols = [each_item(each) for each in item]
            cols = reduce(list.__add__, cols)

            return self.__call__(cols)

        else:
            try:
                return self.__getitem__(list(self.get_keys())).loc[item]
            except:
                try:
                    return self.__getitem__(list(self.get_keys())).iloc[item]
                except:
                    return None

    def __setitem__(self, key, value, units=None):
        """
        creates s vector with the provided Key or the pair of Values and Units
        """
        if type(value) is tuple:
            if len(value) == 2:
                if type(value[0]) is np.ndarray:
                    if type(value[1]) is str:
                        value, units = value[0], value[1]
                elif type(value[0]) is list or type(value[0]) is tuple:
                    if type(value[1]) is str:
                        value, units = np.array(value[0]), value[1]
                elif type(value[0]) is int or type(value[0]) is float:
                    if type(value[1]) is str:
                        value, units = [value[0]] * len(self.fieldtime[2]), value[1]
                    elif type(value[1]) is None:
                        value, units = [value[0]] * len(self.fieldtime[2]), 'DIMENSIONLESS'
                elif type(value[0]) is DataFrame:
                    if type(value[1]) is str:
                        value, units = value[0], value[1]
                    elif type(value[1]) in [list, tuple]:
                        pass
                        # if len(Value[1]) == len(Value[0].columns):
                        #     Value, Units = Value[0], Value[1]
                        # else:
                        #     _verbose(self.speal, 3, "not enough units received\n received: " + str(len(Value[1])) + "\n required: " + str(len(Value[0].columns)))
                        #     return False
                    elif type(value[1]) is None:
                        value, units = value[0], 'DIMENSIONLESS'
                        _verbose(self.speak, 3,
                                 "no Units received, set as DIMENSIONLESS.\nto set other units use second argument.\nto set different units for each column, use '!' as separator to define the units as sufix in each name:\n i.e.: MAIN:ITEN!UNIT \n       MAIN!UNIT ")

        if self.is_Key(key):
            _verbose(self.speak, 3, "WARNING, the key '" + key + "' is already in use. It will be overwritten!")

        if type(value) is str:
            if self.is_Key(value):
                units = self.get_Units(value)
                value = self.get_Vector(value)[value]
            elif self.is_Attribute(value):
                _verbose(self.speak, 2,
                         "the received argument '" + value + "' is not a Key but an Attribute, every key for the attribute will be processed.")
                KeyList = self.get_KeysFromAttribute(value)

                for K in KeyList:
                    NewKey = _mainKey(key) + ':' + K.split(':')[-1]
                    _verbose(self.speak, 2, "   processing '" + K + "'")
                    self.__setitem__(NewKey, K)
                return None
            else:
                # might be calculation
                if '=' in value:
                    calcStr = key + '=' + value[value.index('=') + 1:]
                else:
                    calcStr = key + '=' + value
                return self.RPNcalculator(calcStr)
                # try:
                #     return self.RPNcalculator(calcStr)
                # except:
                #     _verbose(self.speak, 2, "failed to treat '" + Value + "' as a calculation string.")
                #     return None

        elif type(value) in (list, tuple):
            if self.is_Attribute(key) and not self.is_Key(key):
                raise TypeError("The key '" + key + "' is an attribute! Value must be a DataFrame")
            value = np.array(value)

        elif type(value) in (int, float):
            if self.is_Attribute(key) and not self.is_Key(key):
                raise TypeError("The key '" + key + "' is an attribute! Value must be a DataFrame")
            value, units = [value] * len(self.fieldtime[2]), 'DIMENSIONLESS'

        if type(value) is np.ndarray:
            if self.is_Attribute(key) and not self.is_Key(key):
                raise TypeError("The key '" + key + "' is an attribute! Value must be a DataFrame")
            if len(value) != len(self.fieldtime[2]):
                raise ValueError(" the 'Value' array must have the exact same length of the simulation vectors: " + str(
                    len(self.fieldtime[2])))
            if type(units) is str:
                units = units.strip('( )')
            elif units is None:
                units = str(None)
            else:
                units = str(units)
            if unit.isUnit(units):
                pass
            else:
                _verbose(self.speak, 2, " the 'Units' string is not recognized.")

        elif type(value) is DataFrame:
            if len(value) == len(self.fieldtime[2]):
                for Col in value.columns:
                    if '!' in Col:
                        Col, ThisUnits = Col.split('!')[0].strip(), Col.split('!')[1].strip()
                    elif units is not None:
                        ThisUnits = units
                    else:
                        ThisUnits = 'DIMENSIONLESS'

                    if ':' in Col:
                        if key is None:
                            ThisMain, ThisItem = Col.split(':')[0].strip(), Col.split(':')[1].strip()
                        else:
                            ThisMain, ThisItem = key, Col.split(':')[1].strip()
                    else:
                        ThisMain, ThisItem = key, Col.strip()

                    if self.is_Key(Col):
                        ThisMain = key

                    if ThisItem == '':
                        ThisKey = key
                    elif ThisItem == key:
                        ThisKey = key
                    else:
                        ThisKey = ThisMain + ':' + ThisItem

                    self.set_Vector(ThisKey, value[Col].to_numpy(), ThisUnits, data_type='auto', overwrite=True)
                return None
            else:
                raise ValueError(
                    "the lengh of the DataFrame must coincide with the number of steps of this simulation results.")

        elif type(value) is Series:
            if len(value) == len(self.fieldtime[2]):
                Col = value.name
                if type(Col) is str and '!' in Col:
                    Col, ThisUnits = Col.split('!')[0].strip(), Col.split('!')[1].strip()
                elif units is not None:
                    ThisUnits = units
                else:
                    ThisUnits = 'DIMENSIONLESS'

                if ':' in Col:
                    ThisMain, ThisItem = key, Col.split(':')[1].strip() if type(Col) is str else Col
                else:
                    ThisMain, ThisItem = key, Col.strip() if type(Col) is str else Col

                if key is None:
                    ThisKey = Col
                elif self.is_Key(Col):
                    ThisMain = key

                if ThisItem == '':
                    ThisKey = key
                elif ThisItem == key:
                    ThisKey = key
                else:
                    ThisKey = str(ThisMain) + ':' + str(ThisItem)

                self.set_Vector(key, value.to_numpy(), ThisUnits, data_type='auto', overwrite=True)
                return None
            else:
                raise ValueError(
                    "the lengh of the Series must coincide with the number of steps of this simulation results.")

        elif type(value) in (SimSeries, SimDataFrame):
            if len(value) == len(self.fieldtime[2]):
                for Col in value.columns:
                    if value.get_Units(Col) is not None:
                        if type(value.get_Units(Col)) is dict:
                            ThisUnits = value.get_Units(Col)[Col]
                        elif type(value.get_Units(Col)) is str:
                            ThisUnits = value.get_Units(Col)
                        else:
                            ThisUnits = str(value.get_Units(Col))
                    else:
                        ThisUnits = 'DIMENSIONLESS'

                    if ':' in Col:
                        if key is not None:  # if Value.intersectionCharacter in Col:
                            ThisMain, ThisItem = key, Col.split(':')[1].strip()
                        else:
                            ThisMain, ThisItem = Col.split(':')[0].strip(), Col.split(':')[1].strip()
                    else:
                        ThisMain, ThisItem = key, Col.strip()

                    if key is None:
                        ThisKey = Col
                    elif self.is_Key(Col):
                        ThisMain = key

                    if ThisItem == '':
                        ThisKey = key
                    elif ThisItem == key:
                        ThisKey = key
                    else:
                        ThisKey = ThisMain + ':' + ThisItem

                    self.set_Vector(ThisKey, value[Col].to_numpy(), ThisUnits, data_type='auto', overwrite=True)
                return None
            else:
                raise ValueError(
                    "the lengh of the SimDataFrame or SimSeries must coincide with the number of steps of this simulation results.")

        self.set_Vector(key, value, units, data_type='auto', overwrite=True)

    def __len__(self):
        """
        return the number of time steps in the dataset
        """
        return self.len_tSteps()

    def first(self, key):
        """
        returns only the first value of the array
        """
        if type(key) is str:
            if self.is_Key(key):
                return self(key)[0]
            if self.is_Attribute(key):
                return self[key].iloc[0]
        elif type(key) is list:
            return self[key].iloc[0]

    def last(self, key):
        """
        returns only the first value of the array
        """
        if type(key) is str:
            if self.is_Key(key):
                return self(key)[-1]
            if self.is_Attribute(key):
                return self[key].iloc[-1]
        elif type(key) is list:
            return self[key].iloc[-1]

    def __str__(self):
        return self.name

    def __repr__(self):
        self.printMessages = 1

        text = "\n" + str(self.kind).split('.')[-1][:-2] + " source: '" + str(self.name) + "'"
        if self.is_Key('DATE'):
            text = text + '\n from ' + str(self.start) + ' to ' + str(
                self.end)  # str(self('DATE')[0]) + ' to ' + str(self('DATE')[-1])
        if self.is_Key('FOIP'):
            text = text + '\n STOIP @ first tstep: ' + str(self('FOIP')[0]) + ' ' + self.get_Units(
                'FOIP') if self.get_Units('FOIP') is not None else ''
        if self.is_Key('FGIP'):
            text = text + '\n GIP @ first tstep: ' + str(self('FGIP')[0]) + ' ' + self.get_Units(
                'FGIP') if self.get_Units('FGIP') is not None else ''

        if len(self.get_regions()) > 0 and (self.is_Key('FOIP') or self.is_Key('FGIP')):
            text = text + '\n distributed in ' + str(len(self.get_regions())) + ' reporting region' + 's' * (len(
                self.get_regions()) > 1)

        text = text + '\n\n With ' + str(len(self.get_wells())) + ' well' + 's' * (len(self.get_wells()) > 1)
        if len(self.get_groups()) > 0 and len(self.get_wells()) > 1:
            text = text + ' in ' + str(len(self.get_groups())) + ' group' + 's' * (len(self.get_groups()) > 1)
        text = text + ':'

        text = text + '\n\n production wells: ' + str(len(self.get_Producers()))
        if self.get_OilProducers() != []:
            text = text + '\n    oil wells' + ' (with GOR<' + str(self.get_GORcriteria()[0]) + str(
                self.get_GORcriteria()[1]) + ') : ' + str(len(self.get_OilProducers()))
        if self.get_GasProducers() != []:
            text = text + '\n    gas wells' + ' (with GOR>' + str(self.get_GORcriteria()[0]) + str(
                self.get_GORcriteria()[1]) + ') : ' + str(len(self.get_GasProducers()))
        if self.get_WaterProducers() != []:
            text = text + '\n  water wells: ' + str(len(self.get_WaterProducers()))

        text = text + '\n\n injection wells: ' + str(len(self.get_Injectors()))
        if self.get_OilInjectors() != []:
            text = text + '\n    oil wells: ' + str(len(self.get_OilInjectors()))
        if self.get_GasInjectors() != []:
            text = text + '\n    gas wells: ' + str(len(self.get_GasInjectors()))
        if self.get_WaterInjectors() != []:
            text = text + '\n  water wells: ' + str(len(self.get_WaterInjectors()))

        self.printMessages = 0
        return text

    def keyGen(self, keys=[], items=[]):
        """
        returns the combination of every key in keys with all the items.
        keys and items must be list of strings
        """
        if type(items) is str:
            items = [items]
        if type(keys) is str:
            keys = [keys]
        ListOfKeys = []
        for k in keys:
            k.strip(' :')
            for i in items:
                i = i.strip(' :')
                if self.is_Key(k + ':' + i):
                    ListOfKeys.append(k + ':' + i)
                elif k[0].upper() == 'W':
                    wells = self.get_wells(i)
                    if len(wells) > 0:
                        for w in wells:
                            if self.is_Key(k + ':' + w):
                                ListOfKeys.append(k + ':' + w)
                elif k[0].upper() == 'R':
                    pass
                elif k[0].upper() == 'G':
                    pass
        return ListOfKeys

    # @property
    def describe(self):
        # # calling the describe method from pandas for the entire dataframe is very intensive (huge dataframe)
        # describeKeys = list(set(self.keys_))
        # describeKeys.sort()
        # return self[describeKeys].describe()
        print()
        print(self.__repr__())
        print()

        if 'ECL' in str(self.kind):
            kind = 'ECL'
        elif 'VIP' in str(self.kind):
            kind = 'VIP'
        desc = {}
        Index = ['count', 'min', 'max']
        desc['time'] = [self.len_tSteps(), self.fieldtime[0], self.fieldtime[1]]
        desc['dates'] = [len(self('DATE')), _strDate(min(self('DATE')), speak=False),
                         _strDate(max(self('DATE')), speak=False)]
        desc['kind'] = [kind, '', '']
        desc['keys'] = [len(self.keys_), '', '']
        desc['attributes'] = [len(self.attributes), '', '']
        desc['wells'] = [len(self.wells), '', '']
        desc['groups'] = [len(self.groups), '', '']
        desc['regions'] = [len(self.regions), '', '']

        # if self.is_Attribute('WOPR') is True or (self.is_Attribute('WGPR') is True and (self.is_Attribute('WOGR') is True or self.is_Attribute('WGOR') is True)):
        #     desc['oilProducers'] = [ len(self.get_OilProducers()), '', '' ]
        # if self.is_Attribute('WGPR') is True or (self.is_Attribute('WOPR') is True and (self.is_Attribute('WOGR') is True or self.is_Attribute('WGOR') is True)):
        #     desc['gasProducers'] = [ len(self.get_GasProducers()), '', '' ]
        # if self.is_Attribute('WWPR') is True or self.is_Attribute('WWCT') is True:
        #     desc['waterProducers'] = [ len(self.get_WaterProducers()), '', '' ]
        # if self.is_Attribute('WOIR'):
        #     desc['oilInjectors'] = [ len(self.get_OilInjectors()), '', '' ]
        # if self.is_Attribute('WGIR'):
        #     desc['gasInjectors'] = [ len(self.get_GasInjectors()), '', '' ]
        # if self.is_Attribute('WWIR'):
        #     desc['waterInjectors'] = [ len(self.get_WaterInjectors()), '', '' ]
        return DataFrame(data=desc, index=Index)

    def get_WaterInjectors(self, reload=False):
        """
        returns a list of the wells that inject water at any time in the simulation.
        """
        if 'WaterInjectors' not in self.wellsLists or reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count water injection wells')
            if self.is_Attribute('WWIR'):
                self.wellsLists['WaterInjectors'] = list(
                    _wellFromAttribute((self[['WWIR']].replace(0, np.nan).dropna(axis=1, how='all')).columns).values())
            else:
                self.wellsLists['WaterInjectors'] = []
            _ = self.get_WaterInjectorsHistory(reload=True)
        return self.wellsLists['WaterInjectors']

    def get_WaterInjectorsHistory(self, reload=False):
        """
        returns a list of the wells that inject water at any time in the simulation with history keyword.
        """
        if 'WaterInjectors' not in self.wellsLists:
            self.wellsLists['WaterInjectors'] = []
        if reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count water injection wells')
            if self.is_Attribute('WWIRH'):
                self.wellsLists['WaterInjectors'] += list(
                    _wellFromAttribute((self[['WWIRH']].replace(0, np.nan).dropna(axis=1, how='all')).columns).values())
                if len(self.wellsLists['WaterInjectors']) > 1:
                    self.wellsLists['WaterInjectors'] = list(set(self.wellsLists['WaterInjectors']))
        return self.wellsLists['WaterInjectors']

    def get_GasInjectors(self, reload=False):
        """
        returns a list of the wells that inject gas at any time in the simulation.
        """
        if 'GasInjectors' not in self.wellsLists or reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count gas injection wells')
            if self.is_Attribute('WGIR'):
                self.wellsLists['GasInjectors'] = list(
                    _wellFromAttribute((self[['WGIR']].replace(0, np.nan).dropna(axis=1, how='all')).columns).values())
            else:
                self.wellsLists['GasInjectors'] = []

            _ = self.get_GasInjectorsHistory(reload=True)

        return self.wellsLists['GasInjectors']

    def get_GasInjectorsHistory(self, reload=False):
        """
        returns a list of the wells that inject gas at any time in the simulation.
        """
        if 'GasInjectors' not in self.wellsLists:
            self.wellsLists['GasInjectors'] = []
        if reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count gas injection wells')
            if self.is_Attribute('WGIRH'):
                self.wellsLists['GasInjectors'] += list(
                    _wellFromAttribute((self[['WGIRH']].replace(0, np.nan).dropna(axis=1, how='all')).columns).values())
                if len(self.wellsLists['GasInjectors']) > 1:
                    self.wellsLists['GasInjectors'] = list(set(self.wellsLists['GasInjectors']))
        return self.wellsLists['GasInjectors']

    def get_OilInjectors(self, reload=False):
        """
        returns a list of the wells that inject oil at any time in the simulation.
        """
        if 'OilInjectors' not in self.wellsLists or reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count oil injection wells')
            if self.is_Attribute('WOIR'):
                self.wellsLists['OilInjectors'] = list(
                    _wellFromAttribute((self[['WOIR']].replace(0, np.nan).dropna(axis=1, how='all')).columns).values())
            else:
                self.wellsLists['OilInjectors'] = []

            _ = self.get_OilInjectorsHistory(reload=True)

        return self.wellsLists['OilInjectors']

    def get_OilInjectorsHistory(self, reload=False):
        """
        returns a list of the wells that inject oil at any time in the simulation.
        """
        if 'OilInjectors' not in self.wellsLists:
            self.wellsLists['OilInjectors'] = []
        if reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count oil injection wells')
            if self.is_Attribute('WOIRH'):
                self.wellsLists['OilInjectors'] += list(
                    _wellFromAttribute((self[['WOIRH']].replace(0, np.nan).dropna(axis=1, how='all')).columns).values())
                if len(self.wellsLists['OilInjectors']) > 1:
                    self.wellsLists['OilInjectors'] = list(set(self.wellsLists['OilInjectors']))
        return self.wellsLists['OilInjectors']

    def get_Injectors(self, reload=False):
        if 'Injectors' not in self.wellsLists or reload is True:
            self.wellsLists['Injectors'] = list(
                set(self.get_WaterInjectors(reload) + self.get_GasInjectors(reload) + self.get_OilInjectors(reload)))
        return self.wellsLists['Injectors']

    def get_WaterProducers(self, reload=False):
        """
        returns a list of the wells that produces more than 99.99% water at any time in the simulation.
        """
        if 'WaterProducers' not in self.wellsLists or reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count water production wells')
            if self.is_Attribute('WWPR'):
                waterProducers = self[['WWPR']]
                waterProducers = waterProducers.rename(columns=_wellFromAttribute(waterProducers.columns))

                prodCheck = waterProducers * 0

                if self.is_Attribute('WOPR'):
                    oilProducers = self[['WOPR']]
                    oilProducers = oilProducers.rename(columns=_wellFromAttribute(oilProducers.columns))
                    prodCheck = oilProducers + prodCheck

                if self.is_Attribute('WGPR'):
                    gasProducers = self[['WGPR']]
                    gasProducers = gasProducers.rename(columns=_wellFromAttribute(gasProducers.columns))
                    prodCheck = gasProducers + prodCheck

                prodCheck = ((prodCheck == 0) & (waterProducers > self.zeroThreshold)).replace(False, np.nan).dropna(
                    axis=1, how='all')

                self.wellsLists['WaterProducers'] = list(prodCheck.columns)

            elif self.is_Attribute('WWCT'):
                waterCheck = self[['WWPR']]
                waterCheck = waterCheck.rename(columns=_wellFromAttribute(waterCheck.columns))
                waterCheck = (waterCheck >= self.WCcriteria).replace(False, np.nan).dropna(axis=1, how='all')
                self.wellsLists['WaterProducers'] = list(waterCheck.columns)

            else:
                self.wellsLists['WaterProducers'] = []

            _ = self.get_WaterProducersHistory(reload=True)

        return self.wellsLists['WaterProducers']

    def get_WaterProducersHistory(self, reload=False):
        """
        returns a list of the wells that produces more than 99.99% water at any time in the simulation.
        """
        if 'WaterProducers' not in self.wellsLists:
            self.wellsLists['WaterProducers'] = []
        if reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count water production wells')
            if self.is_Attribute('WWPRH'):
                waterProducers = self[['WWPRH']]
                waterProducers = waterProducers.rename(columns=_wellFromAttribute(waterProducers.columns))

                prodCheck = waterProducers * 0

                if self.is_Attribute('WOPRH'):
                    oilProducers = self[['WOPRH']]
                    oilProducers = oilProducers.rename(columns=_wellFromAttribute(oilProducers.columns))
                    prodCheck = oilProducers + prodCheck

                if self.is_Attribute('WGPRH'):
                    gasProducers = self[['WGPRH']]
                    gasProducers = gasProducers.rename(columns=_wellFromAttribute(gasProducers.columns))
                    prodCheck = gasProducers + prodCheck

                prodCheck = ((prodCheck == 0) & (waterProducers > self.zeroThreshold)).replace(False, np.nan).dropna(
                    axis=1, how='all')

                self.wellsLists['WaterProducers'] += list(prodCheck.columns)
                if len(self.wellsLists['WaterProducers']) > 1:
                    self.wellsLists['WaterProducers'] = list(set(self.wellsLists['WaterProducers']))

            elif self.is_Attribute('WWCTH'):
                waterCheck = self[['WWPRH']]
                waterCheck = waterCheck.rename(columns=_wellFromAttribute(waterCheck.columns))
                waterCheck = (waterCheck >= self.WCcriteria).replace(False, np.nan).dropna(axis=1, how='all')
                self.wellsLists['WaterProducers'] += list(waterCheck.columns)
                if len(self.wellsLists['WaterProducers']) > 1:
                    self.wellsLists['WaterProducers'] = list(set(self.wellsLists['WaterProducers']))

        return self.wellsLists['WaterProducers']

    def get_OilProducers(self, reload=False):
        """
        returns a list of the wells considered oil producers at any time in the simulation.
        the GOR criteria to define the oil and gas producers can be modified by the method .set_GORcriteria()
        """
        if 'OilProducers' not in self.wellsLists or reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count oil production wells')
            if self.is_Attribute('WOPR') and self.is_Attribute('WGPR') and self.get_Unit(
                    'WGPR') is not None and self.get_Unit('WOPR') is not None:
                OIL = self[['WOPR']]
                OIL.rename(columns=_wellFromAttribute(OIL.columns), inplace=True)
                # OIL.replace(0, np.nan, inplace=True)

                GAS = self[['WGPR']]
                GAS.rename(columns=_wellFromAttribute(GAS.columns), inplace=True)

                rateCheck = ((OIL > self.zeroThreshold) | (GAS > self.zeroThreshold))  # rateCheck = ((OIL>0) + (GAS>0))

                GOR = GAS / OIL
                GOR.replace(np.nan, 9E9, inplace=True)
                GOR = GOR[rateCheck].dropna(axis=1, how='all')

                # the loop is a trick to avoid memory issues when converting new
                i = 0
                test = False
                while not test and i < 10:
                    i += 1
                    test = convertibleUnits(self.GORcriteria[1],
                                            self.get_Unit('WGPR').split('/')[0] + '/' + self.get_Unit(
                                                'WOPR').split('/')[0])
                GORcriteria = convertUnit(self.GORcriteria[0], self.GORcriteria[1], self.get_Unit(
                    'WGPR').split('/')[0] + '/' + self.get_Unit('WOPR').split('/')[0], PrintConversionPath=False)

                self.wellsLists['OilProducers'] = list(
                    (GOR <= GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)
                self.wellsLists['GasProducers'] = list(
                    (GOR > GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)

            elif self.is_Attribute('WGOR') and self.get_Unit('WGOR') is not None:
                GOR = self[['WGOR']]
                GOR = (GOR.rename(columns=_wellFromAttribute(GOR.columns)))

                rateCheck = (GOR < self.zeroThreshold) & (
                            GOR > self.zeroThreshold)  # to generate a dataframe full of False

                if self.is_Attribute('WOPR'):
                    OIL = self[['WOPR']]
                    OIL.rename(columns=_wellFromAttribute(OIL.columns), inplace=True)
                    rateCheck = rateCheck | (OIL > self.zeroThreshold)
                if self.is_Attribute('WGPR'):
                    GAS = self[['WGPR']]
                    GAS.rename(columns=_wellFromAttribute(GAS.columns), inplace=True)
                    rateCheck = rateCheck | (GAS > self.zeroThreshold)

                GOR = GOR[rateCheck].dropna(axis=1, how='all')

                GORcriteria = convertUnit(self.GORcriteria[0], self.GORcriteria[1], self.get_Unit('WGOR'))
                self.wellsLists['OilProducers'] = list(
                    (GOR <= GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)
                self.wellsLists['GasProducers'] = list(
                    (GOR > GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)

            elif self.is_Attribute('WOGR') and self.get_Unit('WOGR') is not None:
                GOR = 1 / self[['WOGR']]
                GOR = (GOR.rename(columns=_wellFromAttribute(GOR.columns))).dropna(axis=1, how='all')

                GORcriteria = convertUnit(self.GORcriteria[0], self.GORcriteria[1], self.get_Unit('WOGR'))
                self.wellsLists['OilProducers'] = list(
                    (GOR <= GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)
                self.wellsLists['GasProducers'] = list(
                    (GOR > GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)

            elif self.is_Attribute('WOPR'):
                _verbose(self.speak, 2,
                         "neither GOR or GAS RATE available or the data doesn't has units, every well with oil rate > 0 will be listeda as oil producer.")
                self.wellsLists['OilProducers'] = list(
                    _wellFromAttribute(list(self[['WOPR']].replace(0, np.nan).dropna(axis=1, how='all').columns)))

            else:
                self.wellsLists['OilProducers'] = []

            _ = self.get_OilProducersHistory(reload=True)

        return self.wellsLists['OilProducers']

    def get_OilProducersHistory(self, reload=False):
        """
        returns a list of the wells considered oil producers at any time in the simulation.
        the GOR criteria to define the oil and gas producers can be modified by the method .set_GORcriteria()
        """
        if 'OilProducers' not in self.wellsLists:
            self.wellsLists['OilProducers'] = []
        if 'GasProducers' not in self.wellsLists:
            self.wellsLists['GasProducers'] = []
        if reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count oil production wells')
            if self.is_Attribute('WOPRH') and self.is_Attribute('WGPRH') and self.get_Unit(
                    'WGPRH') is not None and self.get_Unit('WOPRH') is not None:
                OIL = self[['WOPRH']]
                OIL.rename(columns=_wellFromAttribute(OIL.columns), inplace=True)
                # OIL.replace(0, np.nan, inplace=True)

                GAS = self[['WGPRH']]
                GAS.rename(columns=_wellFromAttribute(GAS.columns), inplace=True)

                rateCheck = ((OIL > self.zeroThreshold) | (GAS > self.zeroThreshold))  # rateCheck = ((OIL>0) + (GAS>0))

                GOR = GAS / OIL
                GOR.replace(np.nan, 9E9, inplace=True)
                GOR = GOR[rateCheck].dropna(axis=1, how='all')

                # the loop is a trick to avoid memory issues when converting new
                i = 0
                test = False
                while not test and i < 10:
                    i += 1
                    test = convertibleUnits(self.GORcriteria[1],
                                            self.get_Unit('WGPRH').split('/')[0] + '/' + self.get_Unit(
                                                'WOPRH').split('/')[0])
                GORcriteria = convertUnit(self.GORcriteria[0], self.GORcriteria[1], self.get_Unit(
                    'WGPRH').split('/')[0] + '/' + self.get_Unit('WOPRH').split('/')[0], PrintConversionPath=False)

                self.wellsLists['OilProducers'] += list(
                    (GOR <= GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)
                if len(self.wellsLists['OilProducers']) > 1:
                    self.wellsLists['OilProducers'] = list(set(self.wellsLists['OilProducers']))
                self.wellsLists['GasProducers'] += list(
                    (GOR > GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)
                if len(self.wellsLists['GasProducers']) > 1:
                    self.wellsLists['GasProducers'] = list(set(self.wellsLists['GasProducers']))

            elif self.is_Attribute('WGORH') and self.get_Unit('WGORH') is not None:
                GOR = self[['WGORH']]
                GOR = (GOR.rename(columns=_wellFromAttribute(GOR.columns)))

                rateCheck = (GOR < self.zeroThreshold) & (
                            GOR > self.zeroThreshold)  # to generate a dataframe full of False

                if self.is_Attribute('WOPRH'):
                    OIL = self[['WOPRH']]
                    OIL.rename(columns=_wellFromAttribute(OIL.columns), inplace=True)
                    rateCheck = rateCheck | (OIL > self.zeroThreshold)
                if self.is_Attribute('WGPRH'):
                    GAS = self[['WGPRH']]
                    GAS.rename(columns=_wellFromAttribute(GAS.columns), inplace=True)
                    rateCheck = rateCheck | (GAS > self.zeroThreshold)

                GOR = GOR[rateCheck].dropna(axis=1, how='all')

                GORcriteria = convertUnit(self.GORcriteria[0], self.GORcriteria[1], self.get_Unit('WGORH'))
                self.wellsLists['OilProducers'] += list(
                    (GOR <= GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)
                if len(self.wellsLists['OilProducers']) > 1:
                    self.wellsLists['OilProducers'] = list(set(self.wellsLists['OilProducers']))
                self.wellsLists['GasProducers'] += list(
                    (GOR > GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)
                if len(self.wellsLists['GasProducers']) > 1:
                    self.wellsLists['GasProducers'] = list(set(self.wellsLists['GasProducers']))

            elif self.is_Attribute('WOGRH') and self.get_Unit('WOGRH') is not None:
                GOR = 1 / self[['WOGRH']]
                GOR = (GOR.rename(columns=_wellFromAttribute(GOR.columns))).dropna(axis=1, how='all')

                GORcriteria = convertUnit(self.GORcriteria[0], self.GORcriteria[1], self.get_Unit('WOGRH'))
                self.wellsLists['OilProducers'] += list(
                    (GOR <= GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)
                if len(self.wellsLists['OilProducers']) > 1:
                    self.wellsLists['OilProducers'] = list(set(self.wellsLists['OilProducers']))
                self.wellsLists['GasProducers'] += list(
                    (GOR > GORcriteria).replace(False, np.nan).dropna(axis=1, how='all').columns)
                if len(self.wellsLists['GasProducers']) > 1:
                    self.wellsLists['GasProducers'] = list(set(self.wellsLists['GasProducers']))

            elif self.is_Attribute('WOPRH'):
                _verbose(self.speak, 1,
                         "neither historic GOR or GAS RATE available or the data doesn't has units, every well with oil rate > 0 will be listeda as oil producer.")
                self.wellsLists['OilProducers'] += list(
                    _wellFromAttribute(list(self[['WOPRH']].replace(0, np.nan).dropna(axis=1, how='all').columns)))
                if len(self.wellsLists['OilProducers']) > 1:
                    self.wellsLists['OilProducers'] = list(set(self.wellsLists['OilProducers']))

        return self.wellsLists['OilProducers']

    def get_GasProducers(self, reload=False):
        """
        returns a list of the wells considered gas producers at any time in the simulation.
        the GOR criteria to define the oil and gas producers can be modified by the method .set_GORcriteria()
        """
        if 'GasProducers' not in self.wellsLists or reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count gas production wells')
            _ = self.get_OilProducers(reload=True)
            if 'GasProducers' not in self.wellsLists and self.is_Attribute('WGPR') is True:
                _verbose(self.speak, 2,
                         "neither GOR or OIL RATE available or the data doesn't has units, every well with gas rate > 0 will be listeda as gas producer.")
                self.wellsLists['GasProducers'] = list(
                    _wellFromAttribute(list(self[['WGPR']].replace(0, np.nan).dropna(axis=1, how='all').columns)))
            elif 'GasProducers' not in self.wellsLists:
                self.wellsLists['GasProducers'] = []

            _ = self.get_GasProducersHistory(reload=True)

        return self.wellsLists['GasProducers']

    def get_GasProducersHistory(self, reload=False):
        """
        returns a list of the wells considered gas producers at any time in the simulation.
        the GOR criteria to define the oil and gas producers can be modified by the method .set_GORcriteria()
        """
        if 'GasProducers' not in self.wellsLists:
            self.wellsLists['GasProducers'] = []
        if reload is True:
            _verbose(self.printMessages, 1, '# extrating data to count gas production wells')
            _ = self.get_OilProducers(reload=True)
            if 'GasProducers' not in self.wellsLists and self.is_Attribute('WGPRH') is True:
                _verbose(self.speak, 2,
                         "neither GOR or OIL RATE available or the data doesn't has units, every well with gas rate > 0 will be listeda as gas producer.")
                self.wellsLists['GasProducers'] += list(
                    _wellFromAttribute(list(self[['WGPRH']].replace(0, np.nan).dropna(axis=1, how='all').columns)))
                self.wellsLists['GasProducers'] = list(set(self.wellsLists['GasProducers']))

        return self.wellsLists['GasProducers']

    def get_Producers(self, reload=False):
        if 'Producers' not in self.wellsLists or reload is True:
            self.wellsLists['Producers'] = list(
                set(self.get_WaterProducers(reload) + self.get_GasProducers(reload) + self.get_OilProducers(reload)))
        return self.wellsLists['Producers']

    def set_index(self, key):
        """
        defines the Key to be used as default index for the returned DataFrames.

        Parameters
        ----------
        key : str
            a string, must be a valid Key in the loaded data.

        Returns
        -------
        None.

        Raises
        -------
        InvalidKeyError if the requested Key is not valid.

        """
        return self.set_Index(key)

    def set_Index(self, key):
        """
        defines the Key to be used as default index for the returned DataFrames.

        Parameters
        ----------
        key : str
            a string, must be a valid Key in the loaded data.

        Returns
        -------
        None.

        Raises
        -------
        InvalidKeyError if the requested Key is not valid.

        """
        if self.is_Key(key):
            self.DTindex = key
            return self
        else:
            raise InvalidKeyError("'" + key + "' is not a valid Key in this dataset")

    def get_index(self):
        return self.get_Index()

    def get_Index(self):
        return self.DTindex

    def set_GORcriteria(self, GOR=10.0, units=None):
        """
        change the GOR criteria to define a producer well as oil or gas producer.
        By default, it is set to 10Mscf/stb.

        if changed, the lists oilProducers and gasProducers will be recalculated.

        """

        if type(self.get_Unit('WGOR')) is str and len(self.get_Unit('WGOR')) > 0:
            SimUnits = self.get_Unit('WGOR')
        elif type(self.get_Unit('WOPR')) is str and len(self.get_Unit('WOPR')) > 0 and \
                type(self.get_Unit('WGPR')) is str and len(self.get_Unit('WGPR')) > 0:
            SimUnits = self.get_Unit('WGPR').split(':')[0] / self.get_Unit('WOPR').split(':')[0]

        if units is None:
            units = SimUnits
        elif type(units) is str and len(units) > 0:
            units = units.strip()
            if not convertibleUnits(units, SimUnits):
                print("please provide valid GOR units, received, '" + units + "'")
        else:
            print('please provide Units for the GOR criteria')
            return False

        if type(GOR) is float or type(GOR) is int:
            self.GORcriteria = (GOR, units)
            _ = self.get_OilProducers(reload=True)
            return True
        else:
            print('GOR value should be integer or float')
            return False

    def get_GORcriteria(self):
        return self.GORcriteria

    def set_plotUnits(self, UnitSystem_or_CustomUnitsDictionary='FIELD'):
        if type(UnitSystem_or_CustomUnitsDictionary) is str:
            if UnitSystem_or_CustomUnitsDictionary.upper() in ['F', 'FIELD']:
                self.plotUnits = dict(_dictionaries.unitsFIELD)
            elif UnitSystem_or_CustomUnitsDictionary.upper() in ['M', 'METRIC', 'METRICS']:
                self.plotUnits = dict(_dictionaries.unitsMETRIC)
            elif UnitSystem_or_CustomUnitsDictionary.upper() in ['ORIGINAL']:
                self.plotUnits = {}
            else:
                print('unit system not recognized, please select FIELD, METRIC or ORIGINAL')

        elif type(UnitSystem_or_CustomUnitsDictionary) is dict:
            for Key in UnitSystem_or_CustomUnitsDictionary:
                if type(Key) is str and type(UnitSystem_or_CustomUnitsDictionary[Key]) is str:
                    if self.is_Key(Key):
                        if convertibleUnits(self.get_Unit(Key), UnitSystem_or_CustomUnitsDictionary[Key]):
                            self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                    elif self.is_Attribute(Key):
                        if convertibleUnits(self.get_Unit(Key), UnitSystem_or_CustomUnitsDictionary[Key]):
                            self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                        else:
                            _verbose(self.speak, 3,
                                     "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(
                                         Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'.")
                    else:
                        _verbose(self.speak, 2, "the key '" + Key + "' can't be found in this simulation.")
                        matchedKeys = []
                        if Key in self.get_Attributes():
                            matchedKeys = self.attributes[Key]
                        if len(matchedKeys) == 0:
                            _verbose(self.speak, 3,
                                     "the key '" + Key + "' does not match any attribute in this simulation.")
                        elif len(matchedKeys) == 1:
                            if convertibleUnits(self.get_Unit(matchedKeys[0]),
                                                UnitSystem_or_CustomUnitsDictionary[Key]):
                                self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                            else:
                                _verbose(self.speak, 3,
                                         "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(
                                             Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'.")
                            _verbose(self.speak, 1,
                                     "the key '" + Key + "' matches one attribute in this simulation:\n" + str(
                                         matchedKeys))
                        else:
                            mainKs = _mainKey(matchedKeys)
                            if len(mainKs) == 1:
                                if convertibleUnits(self.get_Unit(matchedKeys[0]),
                                                    UnitSystem_or_CustomUnitsDictionary[Key]):
                                    self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                                else:
                                    _verbose(self.speak, 3,
                                             "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(
                                                 Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'.")
                                _verbose(self.speak, 1, "the key '" + Key + "' matches " + str(
                                    len(matchedKeys)) + " attribute in this simulation:\n" + str(matchedKeys))
                            else:
                                if convertibleUnits(self.get_Unit(matchedKeys[0]),
                                                    UnitSystem_or_CustomUnitsDictionary[Key]):
                                    self.plotUnits[Key] = UnitSystem_or_CustomUnitsDictionary[Key]
                                else:
                                    _verbose(self.speak, 3,
                                             "the units for the key '" + Key + "' can't be converted from '" + self.get_Unit(
                                                 Key) + "' to '" + UnitSystem_or_CustomUnitsDictionary[Key] + "'.")
                                _verbose(self.speak, 1, "the key '" + Key + "' matches " + str(
                                    len(mainKs)) + " attribute in this simulation:\n" + str(matchedKeys))
        else:
            print(
                ' Argument missing.\n Please select "FIELD", "METRIC" or "ORIGINAL" or provide a dictionary with the custom units set.')

    def get_plotUnits(self, key=dict):
        return self.get_plotUnit(key)

    def get_plotUnit(self, key=dict):
        if key is dict:
            return self.plotUnits
        if type(key) is str:
            if key in self.plotUnits:
                return self.plotUnits[key]
            else:
                matchingKeys = [K for K in self.plotUnits.keys() if K in key]
                if len(matchingKeys) == 0:
                    return self.get_Unit(key)
                elif len(matchingKeys) == 1:
                    return self.plotUnits[matchingKeys[0]]
                else:
                    MK = ''
                    MM = []
                    for K in matchingKeys:
                        if len(K) > len(MK):
                            MK = K
                            MM = [K]
                        elif len(K) == len(MK):
                            MM.append(K)
                    if len(MM) == 1:
                        return self.plotUnits[MK]
                    else:
                        for M in MM:
                            if convertibleUnits(self.get_Unit(key), self.plotUnits[M]):
                                return self.plotUnits[M]

    def get_Unit(self, key='--EveryType--'):
        """
        returns a string identifiying the unit of the requested Key

        Key could be a list containing Key strings, in this case a dictionary
        with the requested Keys and units will be returned.
        the Key '--EveryType--' will return a dictionary Keys and units
        for all the keys in the results file

        """
        if type(key) is str and key.strip() != '--EveryType--':
            if key in self.units:
                return self.units[key]
            if key.strip() in self.units:
                return self.units[key.strip()]
            key = key.strip().upper()
            if key in self.units:
                return self.units[key]
            if key in ['DATES', 'DATE', 'Date', 'date']:
                self.units[key] = 'DATE'
                return 'DATE'
            if key in self.keys_:
                if ':' in key:
                    if key[0] == 'W':
                        if key.split(':')[-1] in self.wells:
                            return self.get_Unit(key.split(':')[0])
                    if key[0] == 'G':
                        if key.split(':')[-1] in self.groups:
                            return self.get_Unit(key.split(':')[0])
                    if key[0] == 'R':
                        if key.split(':')[-1] in self.regions:
                            return self.get_Unit(key.split(':')[0])
                return None
            else:
                if key[0] == 'W':
                    UList = [self.units[key + ':' + W] for W in self.get_wells() if key + ':' + W in self.units]
                    if len(set(UList)) == 1:
                        self.units[key] = UList[0]
                        return UList[0]
                    else:
                        return None
                elif key[0] == 'G':
                    UList = [self.units[key + ':' + G] for G in self.get_groups() if key + ':' + G in self.units]
                    if len(set(UList)) == 1:
                        self.units[key] = UList[0]
                        return UList[0]
                    else:
                        return None
                elif key[0] == 'R':

                    UList = [self.units[key + ':' + R] for R in self.get_regions() if key + ':' + R in self.units]
                    if len(set(UList)) == 1:
                        self.units[key] = UList[0]
                        return UList[0]
                    else:
                        return None
                UList = None

        elif type(key) is str and key.strip() == '--EveryType--':
            key = [_mainKey(each) if ':' in each else each for each in self.keys_]
            key = list(set(key))
            key.sort()
            tempUnits = {each: self.get_Unit(each) for each in key}
            return tempUnits
        elif type(key) in [list, tuple]:
            tempUnits = {each: self.get_Unit(each) for each in key if type(each) is str}
            return tempUnits

    def get_Units(self, key='--EveryType--'):
        if type(key) is str:
            if key not in self.keys_ and key not in self.attributes:
                if key in self.wells or key in self.groups or key in self.regions:
                    key = list(self.get_keys('*:' + key))
                elif key in ['FIELD', 'ROOT']:
                    key = list(self.get_keys('F*'))
                elif len(self.get_keys(key)) > 0:
                    key = list(self.get_keys(key))
        if type(key) is list:
            def each_Key(each):
                if each in self.keys_:
                    return [each]
                elif each in self.attributes:
                    return self.attributes[each]
                elif each in self.wells or each in self.groups or each in self.regions:
                    return list(self.get_keys('*:' + each))
                elif each in ['FIELD', 'ROOT']:
                    return list(self.get_keys('F*'))
                elif len(self.get_keys(each)) > 0:
                    return list(self.get_keys(each))
                else:
                    return [each]

            Keys = [each_Key(each) for each in key]
            Keys = reduce(list.__add__, Keys)
            key = Keys[:]

        return self.get_Unit(key)

    def set_Units(self, key, unit=None, overwrite=False):
        return self.set_Unit(key, unit=unit, overwrite=overwrite)

    def set_Unit(self, key, unit=None, overwrite=False):
        if type(key) is str:
            if self.is_Key(key):
                key = [key]
            elif self.is_Attribute(key):
                key = self.attributes[key]
            elif len(self.find_Keys(key)) > 0:
                key = list(self.find_Keys(key))
            else:
                raise ValueError("the key '" + key + "'is not present in this object.")
        if type(unit) is str:
            unit = [unit] * len(key)

        if unit is None and type(key) is dict:
            unit, key = list(key.keys()), list(key.values())
        elif unit is not None and len(key) != len(unit):
            raise ValueError('the lists of Keys and Units must have the same length')
        elif unit is None and len(key) > 0:
            unit = [unit]
        elif unit is None and len(key) == 0:
            raise ValueError("missing 'Key' argument")

        keysDict = dict(zip(key, unit))

        for k, u in keysDict.items():
            if k in self.units:
                if self.units[k] is None or self.units[k].strip() in ['None', ''] or overwrite is True:
                    self.units[k] = u
                    keysDict[k] = True
                elif u == self.units[k]:
                    pass  # ignore
                else:
                    _verbose(self.speak, 2,
                             "the key '" + k + "' has '" + u + "' already defined as units, add parameter  overwrite=True  to change this key units.")
                    keysDict[k] = False
            else:
                self.units[k] = u
                keysDict[k] = True
        return keysDict

    def len_Wells(self):
        """
        return the number of wells in the dataset
        """
        return len(self.get_wells())

    def len_Groups(self):
        """
        return the number of groups in the dataset
        """
        return len(self.get_groups())

    def len_Keys(self):
        """
        return the number of keys in the dataset
        """
        return len(self.get_keys())

    def len_tSteps(self):
        """
        return the number of timesteps in the dataset
        """
        keys = ('TIME', 'DATE', 'DATES', 'DAYS', 'MONTHS', 'YEARS')
        for key in keys:
            if self.is_Key(key):
                return len(self.get_Vector(key)[key])

    def len_TimeSteps(self):
        """
        alias for len_tSteps
        """
        return self.len_tSteps()

    def _commonInputCleaning(self, keys=[], objects=None, other_sims=None):
        """
        function to clean common input of ploting functions
        """
        if type(keys) not in [list, tuple, set, str]:
            raise TypeError(" Keys must be a list of keys or a string.")

        if type(keys) is str:
            keys = [keys]

        if _is_SimulationResult(objects) and other_sims is None:
            objects, other_sims = None, objects
        elif other_sims is None and type(objects) in (list, tuple, set) and len(objects) > 0:
            sims = sum([_is_SimulationResult(ob) for ob in objects])
            if sims == 0:
                pass  # none of them are SimulationResults, should be objects (wells, regions, etc)
            elif sims == len(objects):
                objects, other_sims = None, objects  # all of them are Simulation Results
            else:
                raise TypeError("some of the 'otherSims' provided are not SimulationResults instances.")

        if objects is not None:
            if type(objects) not in [str, list, tuple, set]:
                raise TypeError(
                    " objects must be list of wells, groups or regions or one of the magic words 'wells', 'groups', 'regions'.")
            else:
                if type(objects) is str:
                    objects = [objects]
                newKeys = []
                for K in keys:
                    if K[0] == 'F':
                        newKeys.append(K)
                    else:
                        if ':' in K:
                            for O in objects:
                                newKeys.append(_mainKey(K).strip(': ') + ':' + O.strip(': '))
                        else:
                            for O in objects:
                                newKeys.append(K.strip(': ') + ':' + O.strip(': '))
                newKeys = list(set(self.find_Keys(newKeys)))
                keys = []
                for K in newKeys:
                    if self.is_Key(K):
                        keys.append(K)

        # expand Keys
        keys = list(self.find_Keys(keys))

        return keys, objects, other_sims

    def _auto_meltingDF(self, df, hue='--auto', label='--auto'):
        return _meltDF(df, hue=hue, label=label, SimObject=self, FullOutput=True)

    def relplot(self, keys=[], objects=None, other_sims=None, clean_all_zeros=True, ignore_zeros=True,
                hue='--auto', size='--auto', style='--auto',
                col='--auto', row='--auto',
                kind='line', col_wrap=None,
                share_Yaxis=True, share_Xaxis=True, **kwargs):
        """
        """
        sns.set_theme(style="ticks", palette="pastel")

        if col_wrap is not None:
            if type(col_wrap) is not int:
                col_wrap = None

        share_Yaxis, share_Xaxis = bool(share_Yaxis), bool(share_Xaxis)

        if hue == 'main':
            hue = 'attribute'
        if size == 'main':
            size = 'attribute'
        if style == 'main':
            style = 'attribute'
        if col == 'main':
            col = 'attribute'
        if row == 'main':
            row = 'attribute'

        if row == '--auto' and col == '--auto':
            pass
        elif row == '--auto':
            if col == 'attribute':
                row = 'item'
            elif col == 'item':
                row = 'attribute'
        elif col == '--auto':
            if row == 'attribute':
                col = 'item'
            elif row == 'item':
                col = 'attribute'

        # cleaning the data
        userKeys = keys
        keys, objects, other_sims = self._commonInputCleaning(keys=keys, objects=objects, other_sims=other_sims)

        # relplot with other simulations not yet implemented
        if other_sims is not None:
            _verbose(self.speak, 4,
                     "\nI'm sorry, creating realplots with several sourcers (simulation objects) is not yet implemented.\nIf you need this feature please send me an email at martincarlos.araya@cepsa.com\nRegards, \nMartin\n")

        # define plot units
        plotUnits = {}
        for K in keys:
            plotUnits[K] = self.get_plotUnits(K)

        # get the data
        df = self[keys]

        if df is None or len(df) == 0:
            _verbose(self.speak, 3, "no data found for the key: " + str(userKeys))
            return None

        # clean the data
        if clean_all_zeros:
            df = df.replace(0, np.nan).dropna(axis='columns', how='all').replace(np.nan, 0)
        if ignore_zeros:
            df = df.replace(0, np.nan)
        df = df.convert(plotUnits)

        # melt the dataframe
        var1, var2, itemLabel, values, df = self._auto_meltingDF(df)

        if ignore_zeros:
            df = df.dropna(axis='index', how='any')

        if row == '--auto' and col == '--auto':
            if var1 is not None and var2 is not None:
                if set(df[var1]) >= set(df[var2]):
                    col, row = var1, var2
                else:
                    col, row = var2, var1
            elif var1 is None and var2 is not None:
                col = var2
                row = None
                if col_wrap is None:
                    col_wrap = 7  # int(len(set(df[var2])) * 16/9)
            elif var1 is not None and var2 is None:
                col = var1
                row = None
                if col_wrap is None:
                    col_wrap = 7  # int(len(set(df[var1])) * 16/9)
            else:
                col = None
                row = None

        if row is None and col is None and hue == '--auto' and size == '--auto' and style == '--auto':
            if set(df[var1]) >= set(df[var2]):
                hue, style, size = var1, var2, None
            else:
                style, hue, size = var2, var1, None

        if hue == '--auto':
            hue = None
        if size == '--auto':
            size = None
        if style == '--auto':
            style = None

        facet_kws = {'sharey': share_Yaxis, 'sharex': share_Xaxis}

        for K in (
        'Keys', 'objects', 'otherSims', 'cleanAllZeros', 'ignoreZeros', 'hue', 'size', 'style', 'row', 'col', 'kind',
        'share_Yaxis', 'share_Xaxis'):
            if K in kwargs:
                del kwargs[K]

        if 'facet_kws' in kwargs:
            if 'sharey' not in kwargs['facet_kws']:
                kwargs['facet_kws']['sharey'] = share_Yaxis
            if 'sharex' not in kwargs['facet_kws']:
                kwargs['facet_kws']['sharex'] = share_Xaxis
        else:
            kwargs['facet_kws'] = {'sharey': share_Yaxis, 'sharex': share_Xaxis}

        # Draw a nested boxplot to show bills by day and time

        namesBefore = list(df.columns)
        df = df.reset_index()
        for n in list(df.columns):
            if n not in namesBefore:
                indexName = n
                break

        if row is not None:
            row = df[row]
        if col is not None:
            col = df[col]
        if hue is not None:
            hue = df[hue]
        if size is not None:
            size = df[size]
        if style is not None:
            style = df[style]

        fig = sns.relplot(x=df[indexName], y=df[values], row=row, col=col, hue=hue, size=size, style=style, kind=kind,
                          col_wrap=col_wrap, **kwargs)

        return fig

    def pairplot(self, keys=[], objects=None, other_sims=None, clean_all_zeros=True, ignore_zeros=True,
                 hue='--auto', label='--auto', **kwargs):
        """
        this function uses seaborn pairplot to create the chart.
        """
        sns.set_theme(style="ticks", palette="pastel")

        if hue == 'main':
            hue = 'attribute'
        if label == 'main':
            label = 'attribute'

        if hue == '--auto' and label == '--auto':
            hue = 'item'
            label = 'attribute'
        elif hue == '--auto':
            if label == 'attribute':
                hue = 'item'
            elif label == 'item':
                hue = 'attribute'
        elif label == '--auto':
            if hue == 'attribute':
                label = 'item'
            elif hue == 'item':
                label = 'attribute'

        # cleaning the data
        keys, objects, other_sims = self._commonInputCleaning(keys=keys, objects=objects, other_sims=other_sims)

        # define plot units
        plotUnits = {}
        for K in keys:
            plotUnits[K] = self.get_plotUnits(K)

        # get the data
        df = self[keys]

        # clean the data
        if clean_all_zeros:
            df = df.replace(0, np.nan).dropna(axis='columns', how='all').replace(np.nan, 0)
        if ignore_zeros:
            df = df.replace(0, np.nan)
        df = df.convert(plotUnits)

        # melt the dataframe
        hue, label, itemLabel, values, df = self._auto_meltingDF(df, hue=hue, label=label)

        if ignore_zeros:
            df = df.dropna(axis='index', how='any')

        indexName = df.index.name
        df = df.pivot_table(columns=label, index=[df.index, df[hue]])
        df = df.reset_index()
        df = df.set_index(indexName)
        newNames = []
        for col in list(df.columns):
            if type(col) is tuple:
                if col[0] == values:
                    newNames.append(col[-1])
                else:
                    newNames.append(col[0])
        df.columns = newNames

        for K in ('Keys', 'objects', 'otherSims', 'cleanAllZeros', 'ignoreZeros', 'hue', 'label'):
            if K in kwargs:
                del kwargs[K]
        if 'plot_kws' in kwargs:
            if 'alpha' not in kwargs:
                kwargs['plot_kws']['alpha'] = 0.25
            if 'edgecolor' not in kwargs:
                kwargs['plot_kws']['edgecolor'] = 'none'
            if 's' not in kwargs:
                kwargs['plot_kws']['s'] = 7
        else:
            kwargs['plot_kws'] = {'alpha': 0.25, 'edgecolor': 'none', 's': 7}

        # Draw a nested boxplot to show bills by day and time
        fig = sns.pairplot(data=df, hue=hue, **kwargs, )

        return fig

    def _common_dataprep_for_seaborn(self, keys=[], objects=None, other_sims=None, clean_all_zeros=True,
                                     ignore_zeros=True,
                                     hue='--auto', label='--auto', sort='item', ascending=True, resample='daily'):
        """
        support function for box and violin plots data preprocessing
        """
        # getting and cleaning the Keys
        keys, objects, other_sims = self._commonInputCleaning(keys=keys, objects=objects, other_sims=other_sims)

        # define plot units
        plotUnits = {}
        for K in keys:
            plotUnits[K] = self.get_plotUnits(K)

        # define sorting
        quantile = 0.5  # P50 by default
        if sort is None:
            sort = 'none'
        if type(sort) is not str:
            if type(sort) is float:
                quantile = sort
                sort = 'quantile'
            elif type(sort) is int:
                quantile = sort / 100
                sort = 'quantile'
            else:
                sort = 'item'

        sort = sort.lower().strip()
        if sort.replace('.', '').replace(', ', '').isdigit():
            if '.' in sort:
                quantile = float(sort)
                sort = 'quantile'
            elif '.' in sort:
                quantile = float(sort.replace(', ', '.'))
                sort = 'quantile'
            else:
                quantile = int(sort) / 100
                sort = 'quantile'

        if sort in ['name', 'wellname', 'well', 'groupname', 'group', 'region', 'regionname', 'alphabeticaly', 'alpha',
                    'abc']:
            sort = 'item'
        if sort not in ['item', 'min', 'mean', 'median', 'max', 'sum', 'quantile', 'std']:
            if sort[0] in ['p', 'q'] and sort[1:].isdigit():
                quantile = int(sort[1:]) / 100
                sort = 'quantile'
            else:
                sort = ''

        # get the data
        df, dateIndex = self[keys], True

        # convert units and keep the regular Pandas DataFrame only
        if type(df) is SimDataFrame:
            df = df.convert(plotUnits)
            df = df.DF

        # clean the data
        if ignore_zeros:
            df = df.replace(0, np.nan)
        if clean_all_zeros:
            df = df.replace(0, np.nan).dropna(axis='columns', how='all').replace(np.nan, 0)

        # prepare index to resample
        if bool(resample):
            if self.is_Key('DATE'):
                df.index = self('DATE')
            elif self.is_Key('TIME'):
                df.index = pd.to_datetime('1-1-1900') + pd.to_timedelta(self('TIME'), unit='D')
            else:
                dateIndex = False

        # resample
        if resample == 'daily':
            resample = '1D'
        elif resample == 'weekly':
            resample = '1W'
        elif resample == 'monthly':
            resample = '1M'
        elif resample in ['quarterly', 'quarter']:
            resample = '1Q'
        elif resample == 'yearly':
            resample = '1Y'
        elif resample is True:
            resample = '1D'
        elif resample is None:
            resample = False
        if bool(resample) and dateIndex:
            resample = resample.upper()
            if 'D' in resample or 'W' in resample or 'M' in resample or 'Q' in resample or 'Y' in resample:
                df = df.resample('1D', axis=0).median().interpolate(axis=0, method='slinear').resample(resample,
                                                                                                       axis=0).median().interpolate(
                    axis=0, method='slinear')
            else:
                df = df.resample(resample, axis=0).median().interpolate(axis=0, method='slinear')

        # sort the data
        if sort in ['min', 'mean', 'median', 'max', 'sum', 'quantile', 'std']:
            ascending = bool(ascending)
            if sort == 'min':
                sorted_index = list(df.min().sort_values(ascending=ascending).index)
            elif sort == 'mean':
                sorted_index = list(df.mean().sort_values(ascending=ascending).index)
            elif sort == 'median':
                sorted_index = list(df.median().sort_values(ascending=ascending).index)
            elif sort == 'max':
                sorted_index = list(df.max().sort_values(ascending=ascending).index)
            elif sort == 'sum':
                sorted_index = list(df.sum().sort_values(ascending=ascending).index)
            elif sort == 'quantile':
                sorted_index = list(df.quantile(q=quantile).sort_values(ascending=ascending).index)
            elif sort == 'std':
                sorted_index = list(df.std().sort_values(ascending=ascending).index)
            df = df[sorted_index]

        # melt the dataframe
        hue, label, itemLabel, values, df = self._auto_meltingDF(df, hue, label)

        if ignore_zeros:
            df = df.replace(0, np.nan).dropna(axis=0, how='any')

        if sort in ['item']:
            df = df.sort_values(by=itemLabel, axis=0, ascending=bool(ascending))

        if other_sims is not None:
            df['Simulation'] = str(self.name)
            if _is_SimulationResult(other_sims):
                other_sims = [other_sims]

            for os in other_sims:
                other = os._common_dataprep_for_seaborn(Keys=keys, objects=None, otherSims=None,
                                                        cleanAllZeros=clean_all_zeros, ignoreZeros=ignore_zeros,
                                                        hue=hue, label=label, sort=sort, ascending=ascending,
                                                        resample=resample)
                other = other[0].rename(columns={'value': values})
                other['Simulation'] = str(os.name)
                df = df.append(other)
            hue = 'Simulation'

        return df, hue, label, itemLabel, values

    def box(self, keys=[], objects=None, other_sims=None, clean_all_aeros=True, ignore_zeros=True, hue='--auto',
            label='--auto', figsize=(8, 6), dpi=100, grid=False, sort='item', ascending=True, rotation=True,
            tight_layout=True, resample='daily', row=None, col=None,
            return_fig=True, return_df=False,
            logY=False, logX=False, **kwargs):
        """
        alias of boxplot method
        """
        return self.boxplot(keys=keys, objects=objects, other_sims=other_sims, clean_all_zeros=clean_all_aeros,
                            ignore_zeros=ignore_zeros, hue=hue, label=label, figsize=figsize, dpi=dpi, grid=grid,
                            sort=sort, ascending=ascending, rotation=rotation, tight_layout=tight_layout,
                            resample=resample, row=row, col=col, return_fig=return_fig, return_df=return_df, logY=logY,
                            logX=logX, style="ticks", palette="pastel", **kwargs)

    def boxplot(self, keys=[], objects=None, other_sims=None, clean_all_zeros=True, ignore_zeros=True,
                hue='--auto', label='--auto',
                figsize=(8, 6), dpi=100, grid=False,
                sort='item', ascending=True, rotation=True, tight_layout=True, resample='daily',
                row=None, col=None, return_fig=True, return_df=False, logY=False, logX=False,
                style="ticks", palette="pastel", show=False, **kwargs):
        """
        creates a boxplot for the desired keys

        hue must be None, 'item', 'attribute' or 'main'
        label must be None, 'item', 'attribute' or 'main'
        sort must be None, 'item', 'mean', 'max', 'min', 'std'
            or a quantile expressed as a float

        main and item refers to the ECL style kewords, like:
            main:item   -->   WOPR:P1


        this function uses seaborn boxplot to create the chart.
        """
        sns.set_theme(style=style, palette=palette)

        df, hue, label, itemLabel, values = self._common_dataprep_for_seaborn(keys=keys, objects=objects,
                                                                              other_sims=other_sims,
                                                                              clean_all_zeros=clean_all_zeros,
                                                                              ignore_zeros=ignore_zeros, hue=hue,
                                                                              label=label, sort=sort,
                                                                              ascending=ascending, resample=resample)
        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = sns.boxplot(
            x=label, y=values,
            hue=hue,
            data=df,
            **kwargs
        )
        sns.despine(offset=10, trim=True)
        if grid:
            ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)

        if bool(rotation) is True:
            if rotation is True:
                rotation = 90
            plt.xticks(rotation=rotation)

        if bool(tight_layout):
            plt.tight_layout()
        if bool(logY):
            plt.yscale('log')
        if bool(logX):
            plt.xscale('log')
        if show:
            plt.show()

        if bool(return_fig) and bool(return_df):
            return fig, df
        elif bool(return_fig) and not bool(return_df):
            return fig
        elif not bool(return_fig) and bool(return_df):
            return df
        else:
            return None

    def violin(self, keys=[], objects=None, other_sims=None, clean_all_zeros=True, ignore_zeros=True,
               hue='--auto', label='--auto',
               figsize=(8, 6), dpi=100, grid=False,
               sort='item', ascending=True, rotation=True, tight_layout=True, scale='width',
               split=True, resample='daily',
               row=None, col=None, inner=None, logY=False, logX=False,
               return_fig=True, return_df=False,
               style="ticks", palette="pastel", show=False, **kwargs):
        """
        wrapper for violinplot method
        """
        return self.violinplot(keys=keys, objects=objects, other_sims=other_sims, clean_all_zeros=clean_all_zeros,
                               ignore_zeros=ignore_zeros, hue=hue, label=label, figsize=figsize, dpi=dpi, grid=grid,
                               sort=sort, ascending=ascending, rotation=rotation, tight_layout=tight_layout,
                               scale=scale, split=split, resample=resample, row=row, col=col, inner=inner, logY=logY,
                               logX=logX, return_fig=return_fig, return_df=return_df, style=style, palette=palette,
                               **kwargs)

    def violinplot(self, keys=[], objects=None, other_sims=None, clean_all_zeros=True, ignore_zeros=True,
                   hue='--auto', label='--auto', figsize=(8, 6), dpi=100, grid=False,
                   sort='item', ascending=True, rotation=True, tight_layout=True, scale='width', split=True,
                   resample='daily',
                   row=None, col=None, inner=None, logY=False, logX=False,
                   return_fig=True, return_df=False,
                   style="ticks", palette="pastel", **kwargs):
        """
        creates a violin plot for the desired keys

        hue must be None, 'item', 'attribute' or 'main'
        label must be None, 'item', 'attribute' or 'main'

        main and item refers to the ECL style kewords, like:
            main:item   -->   WOPR:P1


        this function uses seaborn boxplot to create the chart.
        """
        sns.set_theme(style=style, palette=palette)

        df, hue, label, itemLabel, values = self._common_dataprep_for_seaborn(keys=keys, objects=objects,
                                                                              other_sims=other_sims,
                                                                              clean_all_zeros=clean_all_zeros,
                                                                              ignore_zeros=ignore_zeros, hue=hue,
                                                                              label=label, sort=sort,
                                                                              ascending=ascending, resample=resample)

        if inner not in ('box', 'quartile', 'point', 'stick', None):
            inner = None

        if split and len(df[hue].unique()) > 2:
            split = False
            _verbose(2, self.speak, "There must be exactly two hue levels to use 'split', thus it will be ignored.")

        fig = plt.figure(figsize=figsize, dpi=dpi)
        ax = sns.violinplot(
            x=label, y=values,
            hue=hue,
            data=df,
            scale=scale,
            split=split,
            inner=inner,
            **kwargs
        )
        sns.despine(offset=10, trim=True)
        if grid:
            ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)

        if bool(rotation) is True:
            if rotation is True:
                rotation = 90
            plt.xticks(rotation=rotation)

        if bool(tight_layout):
            plt.tight_layout()
        if show:
            plt.show()

        if bool(return_fig) and bool(return_df):
            return fig, df
        elif bool(return_fig) and not bool(return_df):
            return fig
        elif not bool(return_fig) and bool(return_df):
            return df
        else:
            return None

    def plot(self, keys=[], index=None, other_sims=None,
             wells=[], groups=[], regions=[],
             do_not_repeat_colors=None, grid=False,
             show=False, hline=None, fig=None, num=None, figsize=(6, 4), dpi=150,
             singleYaxis=False, **kwargs):
        """
        creates a line chart for the selected Keys vs the selected Index.
        returns the a tuple with (the plot, list of Keys in Y axes, list of Indexes in X axis)

        Optional parameters:
            otherSims : another SimulationResults object to plot together with this object.
            Wells : list of wells to plot for the desired Keys
            Groups : list of groups to plot for the desired Keys
            Regions : list of Regions to plot for the desired Keys
            do_not_repeat_colors : True or False
                the colors of the lines are by default asigned based on the property of the Key,
                then for several objects plotting the same Key all the lines will have the same color.
                To avoid that behaviour, set this parameter to True

        """
        from matplotlib.figure import Figure
        if type(fig) is tuple:
            fig = fig[0]
        if fig is None:
            pass
        elif not isinstance(fig, Figure):
            raise TypeError('fig must be a matplotlib.pyplot Figure instance')

        if hline is None:
            pass
        elif type(hline) is bool:
            hline = int(hline)
        elif type(hline) not in [int, float]:
            raise ValueError('hline must be int, float or bool')

        Xgrid, Ygrid = 0, 0
        if type(grid) is str:
            grid = grid.strip()
            if 'x' in grid:
                Xgrid += 1
            if 'y' in grid:
                Ygrid += 1
            if 'X' in grid:
                Xgrid += 2
            if 'Y' in grid:
                Ygrid += 2
            print(Xgrid, Ygrid)
        else:
            grid = bool(grid)
            if grid:
                Xgrid, Ygrid = 2, 2

        if keys == []:
            keys = [keys.append(K) for K in ['FOPR', 'FGPR', 'FWPR', 'FGIR', 'FWIR', 'FOIR'] if
                    self.is_Key(K) and not (min(self(K)) == max(self(K)) and sum(self(K)) == 0)]
            if index is None:
                if self.is_Key('DATE'):
                    index = 'DATE'
                elif self.is_Key('DATES'):
                    index = 'DATES'
                elif self.is_Key('TIME'):
                    index = 'TIME'

        if type(do_not_repeat_colors) is not bool:
            UserDRC = None
        else:
            UserDRC = do_not_repeat_colors
        do_not_repeat_colors = True
        if type(keys) is str:
            keys = [keys]
        if type(wells) is str:
            wells = [wells]
        if type(groups) is str:
            groups = [groups]
        if type(regions) is str:
            regions = [regions]
        if index is None:
            index = self.get_Index()
        if type(index) is list or type(index) is tuple:
            if len(index) > 0:
                if type(index[0]) is str:
                    if len(index) == len(keys):
                        pass  # it is OK, there are pairs of X & Y
                    else:
                        _verbose(1, self.speak,
                                 ' only a single index\n or pairs of X & Y can be used to plot, \n the 0th item will used as Index.')
                        index = index[0]
                # elif 'SimulationResults.' in str(type(Index)):
                elif _is_SimulationResult(index[0]):
                    if other_sims is None:
                        other_sims, index = index, self.get_Index()
                    elif _is_SimulationResult(other_sims):
                        other_sims, index = list({index, other_sims}), self.get_Index()
                    elif type(other_sims) is str and self.is_Key(other_sims):
                        other_sims, index = index, other_sims.stip().upper()
                    elif type(other_sims) is list or type(other_sims) is tuple:
                        if _is_SimulationResult(other_sims[0]):
                            other_sims, index = list(set([index] + other_sims)), self.get_Index()
                        elif type(other_sims[0]) is str and self.is_Key(other_sims[0]):
                            _verbose(1, self.speak, 'only a single index can be used to plot, the item 0 will used.')
                            other_sims, index = index, other_sims[0]

            else:
                index = self.get_Index()
        elif type(index) is str:
            index = index.strip().upper()
        elif _is_SimulationResult(index):
            if other_sims is None:
                other_sims, index = index, self.get_Index()
            elif _is_SimulationResult(other_sims):
                other_sims, index = list({index, other_sims}), self.get_Index()
            elif type(other_sims) is str and self.is_Key(other_sims):
                other_sims, index = index, other_sims.stip().upper()
            elif type(other_sims) is list or type(other_sims) is tuple:
                if _is_SimulationResult(other_sims[0]):
                    other_sims, index = list(set([index] + other_sims)), self.get_Index()
                elif type(other_sims[0]) is str and self.is_Key(other_sims[0]):
                    other_sims, index = index, other_sims

        for k in range(len(keys)):
            keys[k] = keys[k].strip()
        for W in range(len(wells)):
            wells[W] = wells[W].strip()
        for G in range(len(groups)):
            groups[G] = groups[G].strip()
        for R in range(len(regions)):
            regions[R] = regions[R].strip()

        plot_keys = []
        for k in keys:
            if self.is_Key(k):
                plot_keys.append(k)
            elif k in self.attributes:
                if k[0] == 'W':
                    if len(wells) == 0:
                        items = self.attributes[k]
                        do_not_repeat_colors = False
                    else:
                        if len(wells) > self.colorGrouping:
                            do_not_repeat_colors = False
                        items = [None] * len(wells)
                        for i in range(len(wells)):
                            items[i] = k + ':' + wells[i]
                elif k[0] == 'G':
                    if len(groups) == 0:
                        items = self.attributes[k]
                        do_not_repeat_colors = False
                    else:
                        if len(groups) > self.colorGrouping:
                            do_not_repeat_colors = False
                        items = [None] * len(groups)
                        for i in range(len(groups)):
                            items[i] = k + ':' + groups[i]
                elif k[0] == 'R':
                    if len(regions) == 0:
                        items = self.attributes[k]
                        do_not_repeat_colors = False
                    else:
                        if len(regions) > self.colorGrouping:
                            do_not_repeat_colors = False
                        items = [None] * len(regions)
                        for i in range(len(regions)):
                            items[i] = k + ':' + regions[i]
                plot_keys += items
            elif len(self.find_Keys(k)) > 0:
                plot_keys += list(self.find_Keys(k))

        if type(index) is str:
            index = [index]
        index_list = []
        for i in index:
            if self.is_Key(i):
                index_list.append(i)
            elif i in self.attributes:
                if i[0] == 'W':
                    if len(wells) == 0:
                        items = self.attributes[i]
                        do_not_repeat_colors = False
                    else:
                        if len(wells) > self.colorGrouping:
                            do_not_repeat_colors = False
                        items = [None] * len(wells)
                        for X in range(len(wells)):
                            items[X] = i + ':' + wells[X]
                elif i[0] == 'G':
                    if len(groups) == 0:
                        items = self.attributes[i]
                        do_not_repeat_colors = False
                    else:
                        if len(groups) > self.colorGrouping:
                            do_not_repeat_colors = False
                        items = [None] * len(groups)
                        for X in range(len(groups)):
                            items[X] = i + ':' + groups[X]
                elif i[0] == 'R':
                    if len(regions) == 0:
                        items = self.attributes[i]
                        do_not_repeat_colors = False
                    else:
                        if len(regions) > self.colorGrouping:
                            do_not_repeat_colors = False
                        items = [None] * len(regions)
                        for X in range(len(regions)):
                            items[X] = i + ':' + regions[X]
                index_list += items

        warnings = ' WARNING:\n'
        if len(index_list) == len(plot_keys):
            # check consistency:
            ok_flag = True
            review_flag = False
            for i in range(len(index_list)):
                if ':' in index_list[i] and ':' in plot_keys[i]:
                    if index_list[i].split(':')[1] == plot_keys[i].split(':')[1]:
                        pass  # it is OK
                    else:
                        warnings += " the pair '" + plot_keys[i] + "' vs '" + index_list[
                            i] + "' might not be correct.\n"
                        ok_flag = False
                        review_flag = True

            if not ok_flag and len(keys) == len(index):  # migt be a sorting issue
                for i in range(len(keys)):
                    if not self.is_Key(keys[i]) and keys[i] in self.attributes:
                        if not self.is_Key(index[i]) and index[i] in self.attributes:
                            index_list.sort()
                            plot_keys.sort()
                            ok_flag = True
                if ok_flag:
                    for i in range(len(index_list)):
                        if ':' in index_list[i] and ':' in plot_keys[i]:
                            if index_list[i].split(':')[1] == plot_keys[i].split(':')[1]:
                                pass  # it is OK
                            else:
                                warnings += " the pair '" + plot_keys[i] + "' vs '" + index_list[
                                    i] + "' might not be correct.\n"
                                ok_flag = False
            if review_flag:
                if ok_flag:
                    _verbose(self.speak, 2, '\n the pairs consistency WAS corrected with sorting.')
                else:
                    _verbose(self.speak, 3, warnings + ' the pairs consistency was NOT corrected with sorting.')

        if index_list == []:
            if len(index) == 1:
                index_list = index[0]
            else:
                index_list = index

        if other_sims is not None:
            if _is_SimulationResult(other_sims):
                sims_to_plot = [other_sims, self]
            elif type(other_sims) is list or type(other_sims) is tuple:
                sims_to_plot = []
                for each in other_sims:
                    if _is_SimulationResult(each):
                        sims_to_plot.append(each)
                sims_to_plot.append(self)
        else:
            # return self.get_DataFrame(plot_keys, Index).plot()
            sims_to_plot = [self]

        if type(UserDRC) is bool:
            do_not_repeat_colors = UserDRC

        # extract and discard the vectors before calling the Plot, to avoid latency issues
        for sim in sims_to_plot:
            prevSpeak, sim.speak = sim.speak, 0
            for Y in plot_keys:
                if sim.is_Key(Y):
                    _ = sim(Y)
            for X in index_list:
                if sim.is_Key(X):
                    _ = sim(X)
            sim.speak = prevSpeak

        if hline is not None:
            xmin = min(self(index_list[0]))
            xmax = min(self(index_list[0]))
            for i in range(1, len(index_list)):
                xmin = min(self(index_list[i])) if min(self(index_list[i])) < xmin else xmin
                xmin = max(self(index_list[i])) if max(self(index_list[i])) < xmax else xmax
            hline = {'y': hline, 'xmin': xmin, 'xmax': xmax, 'colors': 'black', 'linestyle': '-'}

        figure = Plot(SimResultObjects=sims_to_plot, Y_Keys=plot_keys, X_Key=index_list,
                      do_not_repeat_colors=do_not_repeat_colors, Xgrid=Xgrid, Ygrid=Ygrid, fig=fig, show=show, hline=hline,
                      singleYaxis=singleYaxis, figsize=figsize, dpi=dpi, num=num, **kwargs)

        return figure  # return (figure, plot_keys, index_list)

    def replaceNullbyNaN(self):
        """
        replace in-situ the null value defined in self.null by numpy.nan
        """
        if self.null is not None:
            for key in list(self.vectors.keys()):
                _verbose(self.speak, 1,
                         ' attempting to replace null value ' + str(self.null) + ' in vector ' + str(key) + '.')
                if self.vectors[key] is not None and self.null in self.vectors[key]:
                    _verbose(self.speak, 2, "the key '" + key + "' has null values " + str(self.null))
                    try:
                        self.vectors[key][self.vectors[key] == self.null] = np.nan
                    except:
                        _verbose(self.speak, 2,
                                 ' failed to replace null value ' + str(self.null) + ' in vector ' + str(key) + '.')

    def copyUnits(self, other):
        """
        copy the units from other object to this object
        """
        for key in self.units:
            if other.get_Unit(key) is not None:
                self.units[key] = other.get_Unit(key)

    def get_aggregatedWells(self, wells_to_group=[], well_keys=[], aggregated_key_name='', aggregate_by='default',
                            force=False):
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
        wells_to_group = list(set(wells_to_group))
        wells_to_group.sort()

        returnVector = {}

        if type(well_keys) is str:
            well_keys = [well_keys]

        _verbose(self.speak, 1, ' aggregating keys ' + str(well_keys))
        _verbose(self.speak, 1, ' aggregating wells ' + str(wells_to_group))

        if aggregated_key_name == '':
            for key in well_keys:
                for well in wells_to_group:
                    aggregated_key_name = aggregated_key_name + well

        for key in well_keys:
            _verbose(self.speak, 1, " < aggregating key '" + key + "' >")

            KeyUnits = None
            for well in wells_to_group:
                KeyUnits = self.get_Unit(key + ':' + well)
                if type(KeyUnits) is str and len(KeyUnits) > 0:
                    _verbose(self.speak, 1, " < units found to be '" + KeyUnits + "' >")
                    break
            if KeyUnits is None:
                KeyUnits = 'dimensionless'
                _verbose(self.speak, 1, " < units NOT found, will be set as '" + KeyUnits + "' >")

            if (aggregate_by == 'default' and KeyUnits in unit.dictionary['pressure']) or aggregate_by.lower() == 'avg':
                AGG = 'AVG'
            else:
                AGG = 'SUM'

            NewKey = 'G' + key[1:]
            if AGG + 'of' + key + ':' + ', '.join(wells_to_group) in self.vectors and force is False:
                returnVector[NewKey + ':' + aggregated_key_name] = self.vectors[
                    AGG + 'of' + key + ':' + ', '.join(wells_to_group)]
            elif key == 'TIME' or key == 'DATE' or key == 'DATES':
                returnVector[key + ':' + aggregated_key_name] = self.get_Vector(key)[key]
            else:
                for well in wells_to_group:
                    if self.is_Key(key + ':' + well):
                        if self.get_Vector(key + ':' + well)[key + ':' + well] is None:
                            print('no data for the key ' + str(key + ':' + well))
                        elif len(self.get_Vector(key + ':' + well)[key + ':' + well]) > 0:
                            size = len(self.get_Vector(key + ':' + well)[key + ':' + well])
                            _verbose(self.speak, 1, " < inizializing sum vectr with length " + str(size) + " >")
                            returnVector[NewKey + ':' + aggregated_key_name] = self.get_Vector(key + ':' + well)[
                                                                                   key + ':' + well] * 0.0
                            break

                counter = 0
                for well in wells_to_group:
                    _verbose(self.speak, 1, " < looking for item '" + well + "' >")
                    if self.is_Key(key + ':' + well):
                        AddingVector = self.get_Vector(key + ':' + well)[key + ':' + well]
                        if AddingVector is None:
                            _verbose(self.speak, 3, " < the item '" + well + "' doesn't containt this key >")
                        else:
                            _verbose(self.speak, 2, " < adding '" + well + "' >")
                            returnVector[NewKey + ':' + aggregated_key_name] = returnVector[
                                                                                   NewKey + ':' + aggregated_key_name] + \
                                                                               self.get_Vector(key + ':' + well)[
                                                                                   key + ':' + well]
                            counter += 1

                if (aggregate_by == 'default' and KeyUnits in unit.dictionary[
                    'pressure']) or aggregate_by.lower() == 'avg':
                    if counter > 0:
                        _verbose(-1, 1,
                                 " < calculating average for key '" + key + "' of well '" + wells_to_group + "' >")
                        returnVector[NewKey + ':' + aggregated_key_name] = returnVector[
                                                                               NewKey + ':' + aggregated_key_name] / counter
                        AGG = 'AVG'
                if counter > 0:
                    _verbose(self.speak, 3,
                             ' saving vector ' + NewKey + ':' + aggregated_key_name + ' of length ' + str(
                                 len(returnVector[NewKey + ':' + aggregated_key_name])))
                    self.set_Vector(AGG + 'of' + key + ':' + ', '.join(wells_to_group),
                                    returnVector[NewKey + ':' + aggregated_key_name], KeyUnits, overwrite=True)
                    self.set_Vector(NewKey + ':' + aggregated_key_name,
                                    returnVector[NewKey + ':' + aggregated_key_name], KeyUnits, overwrite=True)
        return returnVector

    def fillZeros(self, key_vector, key_time, force=False):
        """
        Check if the KeyTime array exists on the entire range of TIME array
        from Field and complete the corresponding KeyVector with zeros or
        interpolation for the missing time steps.
        Returns KeyVector that exists on full range of array TIME
        """
        key_time = np.array(key_time, dtype='float')
        force = bool(force)

        if self.fieldtime == (None, None, None):
            self.set_FieldTime()

        if len(key_time) == 0 or len(key_vector) == 0:
            _verbose(self.speak, 2,
                     ' <fillZeros> the received vectors are empty, thus, a zero filled vector will be returned with length equal to the field TIME vector.')
            return np.array([0.0] * len(self.fieldtime), dtype='float')

        if force is True or min(key_time) > self.fieldtime[0] or max(key_time) < self.fieldtime[1]:
            _verbose(self.speak, 1, ' <fillZeros> the received vectors starts on TIME=' + str(
                key_time[0]) + ', it will be filled to start from TIME' + str(self.fieldtime[0]) + '.')
            OtherDT = DataFrame(data={'vector': np.array(key_vector, dtype='float')},
                                index=np.array(key_time, dtype='float'))
            FieldDT = DataFrame(data={'vector': np.array([0.0] * len(self.fieldtime[2]))},
                                index=np.array(self.fieldtime[2], dtype='float'))
            CompleteDT = OtherDT + FieldDT
            CompleteDT.interpolate(axis=0, inplace=True)
            CompleteDT.fillna(value=0.0, inplace=True)
            return CompleteDT['vector'].values
        else:
            return key_vector

    def report_VIP_AttributesNotTo_ECL(self):
        if len(SimResult.VIPnotECL) == 0:
            print('nothing to report.')
        else:
            SimResult.VIPnotECL = list(set(SimResult.VIPnotECL))
            print("the following attibutes from VIP simulation couldn't be converted to ECL style attributes:")
            for each in SimResult.VIPnotECL:
                print('  ' + str(each))

    def set_FieldTime(self):
        TimeVector = self.get_RestartsTimeVector()
        FieldTime = self(TimeVector)
        if FieldTime is None:
            if self.get_Vector(TimeVector)[TimeVector] is not None:
                FieldTime = self.get_Vector(TimeVector)[TimeVector]
        if FieldTime is not None:
            self.fieldtime = (
            min(FieldTime) if len(FieldTime) > 0 else None, max(FieldTime) if len(FieldTime) > 0 else None, FieldTime)

    def set_Name(self, name):
        if type(name) is list or type(name) is tuple:
            if len(name) == 1:
                name = name[0]
        if type(name) is str:
            self.name = name
        else:
            _verbose(self.speak, 2, ' <set_Name> Name should be a string')
            self.name = str(name)

    def get_Name(self):
        if type(self.name) != str:
            _verbose(self.speak, 3, ' <get_Name> the name of ' + str(self.name) + ' is not a string.')
            return str(self.name)
        return self.name

    def set_Restart(self, SimResult_object):
        if type(SimResult_object) is list:
            self.restarts = self.restarts + SimResult_object
        elif type(SimResult_object) is tuple:
            self.restarts = self.restarts + list(SimResult_object)
        else:
            self.restarts.append(SimResult_object)
        self.restarts = list(set(self.restarts))

        for TimeVector in [self.get_TimeVector(), 'DATE', 'DATES', 'TIME', 'DAYS', 'MONTHS', 'YEARS']:
            flag = True
            for R in self.restarts:
                if self.get_TimeVector() != R.get_TimeVector():
                    flag = False
                    break
            if flag:
                break
        _verbose(self.speak, 1, " <set_Restart> using '" + TimeVector + "' to concatenate restarts.")

        sortedR = []
        selfTi = self.get_RawVector(TimeVector)[TimeVector][0]
        # remove simulations that starts after this one (self)
        for i in range(len(self.restarts)):
            if self.restarts[i].get_RawVector(TimeVector)[TimeVector][0] < selfTi:
                sortedR += [self.restarts[i]]
            else:
                _verbose(self.speak, 3, " <set_Restart> the simulation '" + str(self.restarts[
                                                                                    i]) + "' was not added as restart because it doesn't contain data before this simulation ('" + str(
                    self) + "').")
        self.restarts = sortedR

        # sort simulations by start time
        for i in range(len(self.restarts)):
            for j in range(0, len(self.restarts) - i - 1):
                if self.restarts[j].get_RawVector(TimeVector)[TimeVector][0] > \
                        self.restarts[j + 1].get_RawVector(TimeVector)[TimeVector][0]:
                    self.restarts[j], self.restarts[j + 1] = self.restarts[j + 1], self.restarts[j]

        # calculate restartFilters for each restart but the last one
        for i in range(len(self.restarts) - 1):
            thisFilter = self.restarts[i].get_RawVector(TimeVector)[TimeVector] < \
                         self.restarts[i + 1].get_RawVector(TimeVector)[TimeVector][0]
            self.restartFilters[self.restarts[i]] = thisFilter

        if len(self.restarts) > 0:
            # claculate restartFilters for the last restart
            thisFilter = self.restarts[-1].get_RawVector(TimeVector)[TimeVector] < \
                         self.get_RawVector(TimeVector)[TimeVector][0]
            self.restartFilters[self.restarts[-1]] = thisFilter
            # update self.vectorTemplate
            self.set_vectorTemplate(Restart=True)

            # recreate filter for this simulation (self), now considering the restarts
            self.redo_filter()
            # recreate TIME vector if TimeVector is DATE
            if TimeVector in ['DATE', 'DATES']:
                self.createTIME()
            # recalculate the total time for this simulation (self), now considering the restarts
            self.set_FieldTime()
        # print the restarts
        self.print_Restart()

    def set_Continue(self, SimResult_object):
        self.set_Continuation(SimResult_object)

    def set_Continuation(self, SimResult_object):
        if type(SimResult_object) is list:
            self.continuations = self.continuations + SimResult_object
        elif type(SimResult_object) is tuple:
            self.continuations = self.continuations + list(SimResult_object)
        else:
            self.continuations.append(SimResult_object)
        self.continuations = list(set(self.continuations))

        for TimeVector in [self.get_TimeVector(), 'DATE', 'TIME', 'DAYS', 'MONTHS', 'YEARS']:
            flag = True
            for C in self.continuations:
                if self.get_TimeVector() != C.get_TimeVector():
                    flag = False
                    break
            if flag:
                break
        _verbose(self.speak, 1, " using '" + TimeVector + "' to concatenate continuations.")

        sortedC = []
        selfTf = self.get_RawVector(TimeVector)[TimeVector][-1]
        # remove simulations that ends before this one (self)
        for i in range(len(self.continuations)):
            if self.continuations[i].get_RawVector(TimeVector)[TimeVector][-1] > selfTf:
                sortedC += [self.continuations[i]]
            else:
                _verbose(self.speak, 3, "\n the simulation '" + str(self.continuations[
                                                                        i]) + "' was not added as continuation because it doesn't contain data after this simulation ('" + str(
                    self) + "').")
        self.continuations = sortedC

        # sort simulations by start time
        for i in range(len(self.continuations)):
            for j in range(0, len(self.continuations) - i - 1):
                if self.continuations[j].get_RawVector(TimeVector)[TimeVector][-1] > \
                        self.continuations[j + 1].get_RawVector(TimeVector)[TimeVector][-1]:
                    self.continuations[j], self.continuations[j + 1] = self.continuations[j + 1], self.continuations[j]

        # calculate continuationFilters for each continuation but the first one
        for i in range(1, len(self.continuations)):
            thisFilter = self.continuations[i].get_RawVector(TimeVector)[TimeVector] > \
                         self.continuations[i - 1].get_RawVector(TimeVector)[TimeVector][-1]
            self.continuationFilters[self.continuations[i]] = thisFilter

        if len(self.continuations) > 0:
            # claculate continuationFilters for the first continuation
            thisFilter = self.continuations[0].get_RawVector(TimeVector)[TimeVector] > \
                         self.get_RawVector(TimeVector)[TimeVector][-1]
            self.continuationFilters[self.continuations[0]] = thisFilter
            # update self.vectorTemplate
            self.set_vectorTemplate(Continue=True)

            # recreate filter for this simulation (self), now considering the continuations
            self.redo_filter()
            # recreate TIME vector if TimeVector is DATE
            if TimeVector in ['DATE', 'DATES']:
                self.createTIME()
            # recalculate the total time for this simulation (self), now considering the continuations
            self.set_FieldTime()
        # print the continuation
        self.print_Continuation()

    def print_Restart(self):
        prevSpeak, self.speak = self.speak, -1
        _ = self.get_Restart()
        self.speak = prevSpeak

    def print_Continuation(self):
        prevSpeak, self.speak = self.speak, -1
        _ = self.get_Continuation()
        self.speak = prevSpeak

    def clean_Restarts(self):
        """
        ** alias for remove_Restart() **
        removes ALL the simulations from the restart list.
        equivalent to:
            .remove_Restart('--ALL')
        """
        self.remove_Restart(SimResult_object='--ALL')

    def clean_Restart(self):
        """
        ** alias for remove_Restart() **
        removes ALL the simulations from the restart list.
        equivalent to:
            .remove_Restart('--ALL')
        """
        self.remove_Restart(SimResult_object='--ALL')

    def remove_Restarts(self, SimResult_object='--ALL'):
        """
        ** alias for remove_Restart() **
        removes ALL the simulations from the restart list.
        equivalent to:
            .remove_Restart('--ALL')
        """
        self.remove_Restart(self)

    def remove_Restart(self, SimResult_object='--ALL'):
        """
        removes ALL the simulations from the restart list.
        equivalent to:
            .remove_Restart('--ALL')
        """
        if SimResult_object == '--ALL':
            if len(self.restarts) == 0:
                print(" nothing to remove, no restarts objects defined")
            else:
                print(" removed ALL the restart objects (" + str(len(self.restarts)) + " objects removed)")
                self.restarts = []

        if SimResult_object in self.restarts:
            print(" removed restart object '" + str(self.restarts.pop(SimResult_object)) + "'")

        # # update self.set_vectorTemplate()
        self.set_vectorTemplate()
        # recreate TIME vector if TimeVector is DATE
        if self.get_TimeVector() in ['DATE', 'DATES']:
            self.createTIME()
        # recreate filter for this simulation (self), now considering the restarts
        self.redo_filter()
        # recalculate the total time for this simulation (self), now considering the restarts
        self.set_FieldTime()

    def clean_Continuations(self):
        """
        ** alias for remove_Restart() **
        removes ALL the simulations from the restart list.
        equivalent to:
            .remove_Restart('--ALL')
        """
        self.remove_Continuation(SimResult_object='--ALL')

    def clean_Continuation(self):
        """
        ** alias for remove_Restart() **
        removes ALL the simulations from the restart list.
        equivalent to:
            .remove_Restart('--ALL')
        """
        self.remove_Continuation(SimResult_object='--ALL')

    def remove_Continuations(self, SimResult_object='--ALL'):
        """
        ** alias for remove_Restart() **
        removes ALL the simulations from the restart list.
        equivalent to:
            .remove_Restart('--ALL')
        """
        self.remove_Continuation(self)

    def remove_Continuation(self, SimResult_object='--ALL'):
        """
        removes ALL the simulations from the continuation list.
        equivalent to:
            .remove_Continuation('--ALL')
        """
        if SimResult_object == '--ALL':
            if len(self.continuations) == 0:
                print(" nothing to remove, no continuation objects defined")
            else:
                print(" removed ALL the continuation objects (" + str(len(self.continuations)) + " objects removed)")
                self.continuations = []

        if SimResult_object in self.continuations:
            print(" removed continuation object '" + str(self.continuations.pop(SimResult_object)) + "'")

        # # update self.set_vectorTemplate()
        self.set_vectorTemplate()
        # recreate TIME vector if TimeVector is DATE
        if self.get_TimeVector() in ['DATE', 'DATES']:
            self.createTIME()
        # recreate filter for this simulation (self), now considering the restarts
        self.redo_filter()
        # recalculate the total time for this simulation (self), now considering the restarts
        self.set_FieldTime()

    def get_Restarts(self):
        return self.get_Restart()

    def get_Restart(self):
        if self.speak in (-1, 1):
            if len(self.restarts) > 0:
                string = "\n '" + self.get_Name() + "' restarts from "
                for r in range(len(self.restarts) - 1, -1, -1):
                    string = string + "\n   ◄'" + self.restarts[r].get_Name() + "'"
                    if len(self.restarts[r].restarts) > 0:
                        string += self.restarts[r].print_RecursiveRestarts(1)
                    if len(self.restarts[r].continuations) > 0:
                        string += self.restarts[r].print_RecursiveContinuations(1)
                print(string)
        return self.restarts

    def get_Continuations(self):
        return self.get_Restart()

    def get_Continuation(self):
        if self.speak in (-1, 1):
            if len(self.continuations) > 0:
                string = "\n '" + self.get_Name() + "' continues to "
                for r in range(len(self.continuations)):
                    string = string + "\n   ►'" + self.continuations[r].get_Name() + "'"
                    if len(self.continuations[r].continuations) > 0:
                        string += self.continuations[r].print_RecursiveContinuations(1)
                    if len(self.continuations[r].restarts) > 0:
                        string += self.continuations[r].print_RecursiveRestarts(1)
                print(string)
        return self.continuations

    def get_RecursiveRestarts(self):
        if len(self.restarts) == 0:
            return self.restarts
        else:
            restarts = []
            for r in self.restarts:
                if len(r.restarts) == 0:
                    restarts.append([r])
                else:
                    restarts.append([r, r.get_RecursiveRestarts()])
            return restarts

    def get_RecursiveContinuations(self):
        if len(self.continuations) == 0:
            return self.continuations
        else:
            continuations = []
            for c in self.continuations:
                if len(c.continuations) == 0:
                    continuations.append([c])
                else:
                    continuations.append([c, c.get_RecursiveContinuations()])
            return continuations

    def print_RecursiveContinuations(self, ite=0):
        if len(self.continuations) == 0:
            return ''
        else:
            string = ''
            for c in self.continuations:
                string = string + "\n" + "   " * ite + "   " + u"\U0001F6C7" + "►'" + c.get_Name() + "'"
                string += c.print_RecursiveContinuations(ite + 1)
            return string

    def print_RecursiveRestarts(self, ite=0):
        if len(self.restarts) == 0:
            return ''
        else:
            string = ''
            for R in self.restarts[::-1]:
                string = string + "\n" + "   " * ite + "   " + u"\U0001F6C7" + "◄'" + R.get_Name() + "'"
                string += R.print_RecursiveRestarts(ite + 1)
            return string

    def set_Color(self, matplotlib_color=None, key=None):
        """
        Defines the color to use in graphs created from .plot() method,
        must be a valid matplotlib.

        The provided color applies to all the values ploted from this instance,
        optional parameter `Key´ could be used to assing the property to a
        particular Key.
        """
        if matplotlib_color is None:
            matplotlib_color = (random.random(), random.random(), random.random())
        elif not is_color_like(matplotlib_color):
            raise ValueError('<set_Color> the provided color code is not a correct matplotlib color')
        if type(matplotlib_color) is list:
            matplotlib_color = tuple(matplotlib_color)
        if key is None:
            self.color = matplotlib_color
        else:
            if self.is_Key(key):
                self.keyColors[key] = matplotlib_color
            elif key in self.attributes:
                self.keyColors[key] = matplotlib_color
            elif len(self.find_Keys(key)) > 0:
                for K in self.find_Keys(key):
                    _verbose(self.speak, 2, "<set_Color> applying color to key '" + str(K) + "'")
                    self.keyColors[K] = matplotlib_color

    def set_RandomColorPerWell(self):
        """
        ramdomly defines a color for each well.
        """
        for Well in self.wells:
            wellColor = (random.random(), random.random(), random.random())
            for wellKey in self.find_Keys('*:' + Well):
                self.set_Color(wellColor, wellKey)

    def get_Color(self, key=None):
        if key is None:
            return self.color
        elif self.is_Key(key):
            if key in self.keyColors:
                return self.keyColors[key]
            elif _mainKey(key) in self.keyColors:
                return self.keyColors[_mainKey(key)]
            else:
                return None
        elif key in self.attributes:
            return self.keyColors[key]

    def set_Thickness(self, linewidth=None, key=None):
        """
        Defines the line width to use in graphs created from .plot() method,
        must be a positive float.

        The provided line width applies to all the values ploted from this instance,
        optional parameter `Key´ could be used to assing the property to a
        particular Key.
        """
        return self.set_Width(linewidth=linewidth, key=key)

    def set_Width(self, linewidth=None, key=None):
        """
        Defines the line width to use in graphs created from .plot() method,
        must be a positive float.

        The provided line width applies to all the values ploted from this instance,
        optional parameter `Key´ could be used to assing the property to a
        particular Key.
        """
        if linewidth is None:
            pass  # linewidth = 2.0
        elif key is None and type(linewidth) is str:
            if len(self.find_Keys(linewidth)) > 0:
                linewidth, key = None, linewidth
            else:
                raise TypeError('<set_Width> the `linewidth´ value must be int or float')
        elif type(linewidth) not in [float, int, bool]:
            TypeError('<set_Width> the `linewidth´ value must be int or float')
        if type(linewidth) in [int, bool]:
            linewidth = float(linewidth)
        if key is None:
            self.width = linewidth
        else:
            if self.is_Key(key):
                self.keyWidths[key] = linewidth
            elif self.is_Attribute(key):
                self.keyWidths[key] = linewidth
            elif len(self.find_Keys(key)) > 0:
                for K in self.find_Keys(key):
                    _verbose(self.speak, 2, '<set_Width> applying width to key', K)
                    self.set_Width(linewidth, K)

    def get_Width(self, key=None):
        if key is None:
            return self.width
        elif self.is_Key(key):
            if key in self.keyWidths:
                return self.keyWidths[key]
            elif _mainKey(key) in self.keyWidths:
                return self.keyWidths[_mainKey(key)]
            else:
                return None
        elif key in self.attributes:
            return self.keyWidths[key]

    def set_Style(self, linestyle='-', key=None):
        """
        Defines the line style to use in graphs created from .plot() method,
        must be a valid matplotlib linestyle:
            '-' or 'solid' 	      solid line
            '--' or 'dashed'      dashed line
            '-.' or 'dashdot'     dash-dotted line
            ':' or 'dotted'	      dotted line
            'None' or ' ' or ''   draw nothing

        The provided line style applies to all the values ploted from this instance,
        optional parameter `Key´ could be used to assing the property to a
        particular Key.
        """
        if linestyle is None:
            linestyle = 'None'
        if linestyle is False:
            if not linestyle.startswith('None'):
                if self.get_Style(key) in ['None', ' ', '']:
                    linestyle = 'None'
                else:
                    linestyle = 'None#' + self.get_Style(key).strip()
        elif linestyle is True:
            if self.get_Style(key) in ['None', ' ', '']:
                linestyle = '-'
            elif self.get_Style(key).startswith('None#'):
                linestyle = self.get_Style(key)[5:].strip()
        if type(linestyle) is not str:
            raise TypeError('<set_Style> the `linestyle´ value must be a string valid as matplotlib linestyle')
        elif linestyle not in ['-', 'solid', '--', 'dashed', '-.', 'dashdot', ':', 'dotted', 'None', ' ', '']:
            raise ValueError(
                '<set_Style> the `linestyle´ value must be a string valid as matplotlib linestyle:\n  ' + "'-' or 'solid' 	      solid line\n  '--' or 'dashed'      dashed line\n  '-.' or 'dashdot'     dash-dotted line\n  ':' or 'dotted'	      dotted line\n  'None' or ' ' or ''   draw nothing\n")

        if key is None:
            self.style = linestyle
        else:
            if self.is_Key(key):
                self.key_styles[key] = linestyle
            elif key in self.attributes:
                self.key_styles[key] = linestyle
            elif len(self.find_Keys(key)) > 0:
                for K in self.find_Keys(key):
                    _verbose(self.speak, 2, '<set_Style> applying style to key', K)
                    self.set_Style(linestyle, K)

    def get_Style(self, Key=None):
        if Key is None:
            return 'None' if self.style.startswith('None#') else self.style
        elif self.is_Key(Key):
            if Key in self.key_styles:
                return 'None' if self.key_styles[Key].startswith('None#') else self.key_styles[Key]
            elif _mainKey(Key) in self.key_styles:
                return 'None' if self.key_styles[_mainKey(Key)].startswith('None#') else self.key_styles[_mainKey(Key)]
            else:
                return None
        elif Key in self.attributes:
            return 'None' if self.key_styles[Key].startswith('None#') else self.key_styles[Key]

    def set_Marker(self, marker=None, key=None):
        """
        Defines the marker style to use in graphs created from .plot() method,
        must be a valid matplotlib marker.

        The provided marker applies to all the values ploted from this instance,
        optional parameter `Key´ could be used to assing the property to a
        particular Key.
        """
        if marker is None:
            marker = 2.0
        if type(marker) is str:
            if marker.strip() in [".", ", ", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h",
                                  "H", "+", "x", "X", "D", "d", "|", "_", "None", " ", ""]:
                marker = marker.strip()
            elif len(marker.strip()) > 2 and marker.strip()[0] == marker.strip()[-1]:
                marker = marker.strip()
            else:
                raise ValueError('<set_Marker> the provided marker is not a valid string code for matplotlib')
        elif type(marker) in [int, float]:
            if int(marker) >= 0 and int(marker) <= 11:
                market = int(marker)
            else:
                raise ValueError('<set_Marker> the provided marker is not a valid integer for matplotlib')
        elif type(marker) is tuple:
            if len(marker) == 3:
                if type(marker[0]) is int and marker[0] > 0 and type(marker[1]) is int and marker[1] in [0, 1, 2,
                                                                                                         3] and type(
                        marker[2]) in [float, int]:
                    pass  # ok
                else:
                    raise ValueError(
                        '<set_Marker> the provided marker is not a valid tuple - (numsides, style, angle) - for matplotlib')
        else:
            _verbose(self.speak, 3,
                     '<set_Marker> the provided marker could not be validated, will be stored as received')

        if key is None:
            self.marker = marker
        else:
            if self.is_Key(key):
                self.keyMarkers[key] = marker
            elif key in self.attributes:
                self.keyMarkers[key] = marker
            elif len(self.find_Keys(key)) > 0:
                for K in self.find_Keys(key):
                    _verbose(self.speak, 2, '<set_Marker> applying marker to key', K)
                    self.keyMarkers[key] = marker

    def get_Marker(self, key=None):
        if key is None:
            return 'None' if self.marker.startswith('None#') else self.marker
        elif self.is_Key(key):
            if key in self.keyMarkers:
                return 'None' if self.keyMarkers[key].startswith('None#') else self.keyMarkers[key]
            elif _mainKey(key) in self.keyMarkers:
                return 'None' if self.keyMarkers[_mainKey(key)].startswith('None#') else self.keyMarkers[_mainKey(key)]
            else:
                return None
        elif key in self.attributes:
            return 'None' if self.keyMarkers[key].startswith('None#') else self.keyMarkers[key]

    def set_MarkerSize(self, markersize=1.0, key=None):
        """
        Defines the marker size to use in graphs created from .plot() method,
        must be a positive float or integer.

        The provided marker size applies to all the values ploted from this
        instance, optional parameter `Key´ could be used to assing the property
        to a particular Key.
        """
        if markersize is None:
            markersize = 1.0
        if type(markersize) is str:
            markersize = 1.0
            raise TypeError('<set_MarkerSize> the provided markersize is not a float or integer')
        elif type(markersize) in [int, float]:
            if markersize >= 0:
                markersize = float(markersize)
            else:
                raise ValueError('<set_MarkerSize> the provided markersize must be positive')
        else:
            raise TypeError('<set_MarkerSize> the provided markersize is not valid')

        if key is None:
            self.markersize = markersize
        else:
            if self.is_Key(key):
                self.keyMarkersSize[key] = markersize
            elif key in self.attributes:
                self.keyMarkersSize[key] = markersize
            elif len(self.find_Keys(key)) > 0:
                for K in self.find_Keys(key):
                    _verbose(self.speak, 2, '<set_MarkerSize>  applying marker size to key', K)
                    self.keyMarkersSize[key] = markersize

    def get_MarkerSize(self, key=None):
        if key is None:
            return self.markersize
        elif self.is_Key(key):
            if key in self.keyMarkersSize:
                return self.keyMarkersSize[key]
            elif _mainKey(key) in self.keyMarkersSize:
                return self.keyMarkersSize[_mainKey(key)]
            else:
                return None
        elif key in self.attributes:
            return self.keyMarkersSize[key]

    def set_Verbosity(self, verbosity_level):
        try:
            self.speak = int(verbosity_level)
        except:
            if type(verbosity_level) is str and verbosity_level.upper() == 'ALL':
                print('Verbosity set to ALL (-1), EVERY message wil be printed.')
                self.speak = -1
            elif type(verbosity_level) is str and verbosity_level.upper() == 'MUTE':
                print('Verbosity set to MUTE (0), no message wil be printed.')
                self.speak = -1
            else:
                print('wrong set_Verbosity argument: ' + str(verbosity_level) + '\nVerbosity will be set to True (1)')
                self.speak = 1

    def get_Verbosity(self):
        return self.speak

    def set_Start(self, start_date):
        """
        startDate must be a string representing a date or a Pandas or Numpy or datetime object
        """
        self.start = np.datetime64(pd.to_datetime(start_date), 's')
        return self.start

    def get_Start(self):
        """
        startDate must be a string representing a date or a Pandas or Numpy or datetime object
        """
        return self.start

    def isKey(self, key):
        return self.is_Key(key)

    def is_Key(self, key):
        if type(key) is not str or len(key) == 0:
            return False
        if key in self.get_keys():
            return True
        else:
            return False

    def isAtt(self, key):
        return self.is_Attribute(Key)

    def is_Att(self, key):
        return self.is_Attribute(key)

    def is_Attribute(self, key):
        return self.is_Attribute(key)

    def is_Attribute(self, key):
        if type(key) != str:
            return False
        key = key.strip()
        if len(key) == 0:
            return False
        if key[-1] == ':':
            key = key[:-1]
        if key in self.get_Attributes():
            return True
        else:
            return False

    def get_Attributes(self, pattern=None, reload=False):
        """
        extract the attribute name from the keys property,
        basically, the part to the left of the ':' in the key name for wells,
        groups and regions.
        """
        reload = bool(reload)
        if len(list(self.attributes.keys())) == 0 or reload is True:
            props = []
            for each in self.get_keys():
                if ':' in each:
                    attr = _mainKey(each)
                    if attr in self.attributes:
                        if type(self.attributes[attr]) is list:
                            self.attributes[attr] = self.attributes[attr] + [each]
                        else:
                            self.attributes[attr] = [each]
                    else:
                        self.attributes[attr] = [each]
                else:
                    self.attributes[each.strip()] = []

            for each in list(self.attributes.keys()):
                if self.attributes[each] is not None:
                    self.attributes[each] = list(set(self.attributes[each]))
                else:
                    self.attributes[each] = []
        if pattern is None:
            return tuple(self.attributes.keys())
        else:
            props = []
            for each in self.get_keys(pattern, reload=False):
                if ':' in each:
                    props.append(_mainKey(each))
                else:
                    props.append(each.strip())
            return tuple(set(props))

    def get_AttributesDict(self, reload=False):
        reload = bool(reload)
        if reload is True:
            self.get_Attributes(None, True)
        return self.attributes

    def get_KeysFromAttribute(self, attribute):
        """
        returns a list of Keys for the given attribute
        """
        if self.is_Key(attribute):
            return [attribute]
        if self.is_Attribute(attribute):
            return self.attributes[attribute]
        return []

    def add_Key(self, key):
        if type(key) is str:
            key = key.strip()
            self.keys_ = tuple(set(list(self.get_keys()) + [key]))
        else:
            raise TypeError('Key must be string')

    def extract_wells(self):
        """
        Will return a list of all the well names in the case.
        """
        wellsList = [K.split(self.nameSeparator)[-1].strip() for K in self.keys_ if
                     (K[0] == 'W' and self.nameSeparator in K)]
        wellsList = sorted(list(set(wellsList)))
        self.wells = tuple(wellsList)
        return self.wells

    def extract_groups(self):
        """
        Will return a list of all the group names in the case.
        """
        groupsList = [K.split(self.nameSeparator)[-1].strip() for K in self.keys_ if
                      (K[0] == 'G' and self.nameSeparator in K)]
        groupsList = sorted(list(set(groupsList)))
        self.groups = tuple(groupsList)
        return self.groups

    def extract_regions(self):
        """
        Will return a list of all the regions names or numbers in the case.
        """
        # preparing object attribute
        regionsList = [K.split(self.nameSeparator)[-1].strip() for K in self.keys_ if
                       (K[0] == 'G' and self.nameSeparator in K)]
        regionsList = sorted(list(set(regionsList)))
        return tuple(regionsList)

    def get_regions(self, pattern=None, reload=False):
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
        reload = bool(reload)

        if pattern is not None and type(pattern) is not str:
            raise TypeError('pattern argument must be a string.')

        if len(self.regions) == 0 or reload is True:
            self.regions = tuple(self.extract_regions())
        if pattern is None:
            return self.regions
        else:
            return tuple(fnmatch.filter(self.regions, pattern))

    def get_wells(self, pattern=None, reload=False):
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
        reload = bool(reload)

        if pattern is not None and type(pattern) is not str:
            raise TypeError('pattern argument must be a string.')

        if len(self.wells) == 0 or reload is True:
            self.extract_wells()

        if pattern is None:
            return tuple(self.wells)
        else:
            return tuple(fnmatch.filter(self.wells, pattern))

    def get_groups(self, pattern=None, reload=False):
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
        reload = bool(reload)

        if pattern is not None and type(pattern) is not str:
            raise TypeError('pattern argument must be a string.')

        if len(self.groups) == 0 or reload is True:
            self.extract_groups()

        if pattern is None:
            return self.groups
        else:
            return tuple(fnmatch.filter(self.groups, pattern))

    def get_keys(self, pattern=None, reload=False):
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
        reload = bool(reload)

        if pattern is not None and type(pattern) is not str:
            raise TypeError('pattern argument must be a string.')

        if len(self.keys_) == 0 or reload is True:
            self.keys_ = self.list_Keys()

        if pattern is None:
            return self.keys_
        else:
            return tuple(fnmatch.filter(self.keys_, pattern))

    def find_keys(self, criteria=None, reload=False):
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
        return self.find_Keys(criteria=criteria, reload=reload)

    def find_Keys(self, criteria=None, reload=False):
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
        reload = bool(reload)

        if len(self.keys_) == 0 or reload is True:
            self.keys_ = self.get_keys(reload=reload)

        if criteria is not None and (type(criteria) is not str and type(criteria) not in [list, tuple, set]):
            raise TypeError('criteria argument must be a string or list of strings.')

        if criteria is None:
            return self.keys_

        keys = []
        if type(criteria) is str and len(criteria.strip()) > 0:
            if criteria.strip()[0] == '!' and len(criteria.strip()) > 1:
                keys = list(self.keys_)
                keys.remove(criteria[1:])
                return tuple(keys)
            criteria = [criteria]
        elif type(criteria) is not list:
            try:
                criteria = list(criteria)
            except:
                raise TypeError('criteria argument must be a string or list of strings.')
        for key in criteria:
            if type(key) is str and key not in self.keys_:
                if key in self.wells or key in self.groups or key in self.regions:
                    keys += list(self.get_keys('*:' + key))
                elif key in self.attributes:
                    keys += list(self.attributes[key])  # list(self.keyGen(key, self.attributes[key]))
                else:
                    if '?' in key and key[0] != 'F' and ':' not in key:
                        keys += list(self.get_keys(key + ':*'))
                    else:
                        keys += list(self.get_keys(key))
            elif type(key) is str and key in self.keys_:
                keys += [key]
            else:
                keys += list(self.find_Keys(key))
        return tuple(keys)

    def get_filter(self):
        if self.filter['filter'] is None:
            _verbose(self.speak, 1, " <get_Filter> filter is not yet defined")
            return np.array([True] * len(self.get_Vector(self.keys_[0])[self.keys_[0]]))
        if len(self.filter['filter']) != len(self.vectorTemplate):
            self.redo_filter()
        return self.filter['filter']

    def reset_filter(self):
        if self.filter['reset']:
            if self.filter['key'] == [None] and self.filter['condition'] == [None] and self.filter['min'] == [None] and \
                    self.filter['max'] == [None]:
                pass
            else:
                self.filter = {'key': [None], 'min': [None], 'max': [None], 'condition': [None], 'filter': None,
                               'reset': True, 'incremental': [None], 'operation': [None]}
                _verbose(self.speak, 2, " << filter reset >>")
            return True
        else:
            self.filter['reset'] = True
            return False

    def undo_Filter(self):
        if self.filterUndo is None:
            _verbose(self.speak, -1, " << not possible to revert last set_Filter operation or already reverted >>")
            return False
        else:
            self.filter['filter'] = self.filterUndo
            for each in ['key', 'min', 'max', 'condition']:
                self.filter[each] = self.filter[each][:-1]
            _verbose(self.speak, -1, " << last set_Filter has been reverted, \n filter set to previous version >>")
            self.filterUndo = None
            return True

    def redo_filter(self):
        redo = self.filter.copy()
        self.reset_filter()
        for i in range(len(redo['key'])):
            if redo['key'][i] is None and redo['condition'][i] is None and redo['min'][i] is None and redo['max'][
                i] is None:
                _verbose(self.speak, 1, " <redo_Filter> skipping empty filter...")
            else:
                Key = redo['key'][i]
                Condition = redo['condition'][i]
                Min = redo['min'][i]
                Max = redo['max'][i]
                Incremental = redo['incremental'][i]
                Operation = redo['operation'][i]
                filterStr = []
                if Key is not None:
                    filterStr += ["Key='" + str(Key) + "'"]
                if Condition is not None:
                    filterStr += ["Condition='" + str(Condition) + "'"]
                if Min is not None:
                    filterStr += ["Min='" + str(Min) + "'"]
                if Max is not None:
                    filterStr += ["Min='" + str(Max) + "'"]
                filterStr = ', '.join(filterStr) + ", IncrementalFilter=" + str(
                    Incremental) + ", FilterOperation='" + str(Operation) + "'"
                _verbose(self.speak, 2, " <redo_Filter> applying filter: " + filterStr)
                self.set_filter(key=Key, condition=Condition, min=Min, max=Max, incremental_filter=Incremental,
                                filter_operation=Operation)

    def clean_filter(self):
        """
        alias for .set_Filter() method without arguments,
        aimed to remove any previouly set filter
        """
        self.set_filter()

    def remove_filter(self):
        """
        alias for .set_Filter() method without arguments,
        aimed to remove any previouly set filter
        """
        self.set_filter()

    def set_filter(self, key=None, condition=None, min=None, max=None, filter=None, incremental_filter=True,
                   filter_operation=None, undo=True):
        # support function to validate date string
        def MightBeDate(string):
            if _isDate(string):
                return ''
            else:
                for DateType in [['DD', 'MM', 'YY'], ['DD', 'MM', 'YYYY']]:
                    for sep in ['/', '-', ' ', '\t', '_', ':', ';', '#', "'"]:
                        formatStr = sep.join(DateType)
                        if _isDate(string, formatIN=formatStr):
                            return formatStr
            return False

        # convert the string to numpy date
        def toNumpyDate(DateString):
            DateFormat = str(MightBeDate(DateString))
            try:
                return np.datetime64(pd.to_datetime(_strDate(DateString, DateFormat, speak=False)))
            except:
                raise TypeError(" a string must represent a date, better if is formatted like DD-MMM-YYYY")

        # check if aditional conditions waiting to be applied
        def ContinueFiltering(Key, Condition, Min, Max, Filter, Operation):
            if Condition is None and Min is None and Max is None and Filter is None:
                self.filter['reset'] = True
                self.set_FieldTime()
                return True
            else:
                self.filter['reset'] = False
                return self.set_filter(key=Key, condition=Condition, min=Min, max=Max, filter=Filter,
                                       incremental_filter=True, filter_operation=Operation)

        # apply the Filter
        def applyFilter(NewFilter, CurrentFilter=None, UnDo=True):
            if CurrentFilter is not None:
                self.filter['filter'] = CurrentFilter
                if UnDo is None:
                    self.filterUndo = CurrentFilter.copy()
                    UnDo = False
                elif UnDo:
                    self.filterUndo = CurrentFilter.copy()
                # self.filterUndo = CurrentFilter.copy()
            if Incremental and len(self.filter['filter']) > 0:
                if Operation == '*':
                    self.filter['filter'] = NewFilter * self.filter['filter']
                else:
                    self.filter['filter'] = NewFilter + self.filter['filter']
            else:
                self.filter['filter'] = NewFilter
            if True not in self.filter['filter']:
                _verbose(self.speak, -1, "\n***IMPORTANT*****IMPORTANT*****IMPORTANT*****IMPORTANT*****" + \
                         "\n The new filter will result in empty vectors." + \
                         "\n Nothing will be following plots, dataframes or vectors." + \
                         "\n To restore previous filter call the method .undo_Filter()\n")

        # apply a Condition
        def applyCondition(Left, Mid, Right):
            if Right is None:
                if Left in ['>=', '<=', '==', '!=', '>', '<']:
                    if _isnumeric(Mid):
                        applyCondition(key, Left, Mid)
                    elif self.is_Key(Mid):
                        applyCondition(key, Left, Mid)
                    else:
                        raise TypeError(" the Condition is not correct: '" + key + Left + Mid + "'")
                if Mid in ['>=', '<=', '==', '!=', '>', '<']:
                    if _isnumeric(Left):
                        applyCondition(Left, Mid, key)
                    elif self.is_Key(Left):
                        applyCondition(Left, Mid, key)
                    else:
                        raise TypeError(" the Condition is not correct: '" + Left + Mid + key + "'")
            else:
                # check Left parameter
                if self.is_Key(Left):
                    Left = self.get_Vector(Left)[Left]
                elif _isnumeric(Left):
                    Left = float(Left)
                elif MightBeDate(Left) != False:
                    Left = toNumpyDate(Left)
                    if self.is_Key(Right) and type(self.get_Vector(Right)[Right][0]) is not np.datetime64:
                        raise TypeError(" if condition compares to a date, the Key must be DATE or date kind ")
                else:
                    raise TypeError(" the condition should be composed by Keys, conditions, numbers or dates ")
                # check Right parameter
                if self.is_Key(Right):
                    Right = self.get_Vector(Right)[Right]
                elif _isnumeric(Right):
                    Right = float(Right)
                elif MightBeDate(Right) != False:
                    Right = toNumpyDate(Right)
                    if type(Left[0]) is not np.datetime64:
                        raise TypeError(" if condition compares to a date, the Key must be DATE or date kind ")
                else:
                    raise TypeError(" the condition should be composed by Keys, conditions, numbers or dates ")
                # check Mid parameter
                if Mid not in ['>=', '<=', '==', '!=', '>', '<']:
                    raise TypeError(" the condition should be composed by Keys, conditions, numbers or dates ")
                if Mid == '>=':
                    return Left >= Right
                if Mid == '<=':
                    return Left <= Right
                if Mid == '==':
                    return Left == Right
                if Mid == '!=':
                    return Left != Right
                if Mid == '>':
                    return Left > Right
                if Mid == '<':
                    return Left < Right

        # validate Key
        if not self.is_Key(key) and (condition is not None or min is not None or max is not None or filter is not None):
            if len(self.find_Keys(key)) > 0:
                _verbose(self.speak, 1,
                         "applying filter for each Key matching the pattern of " + str(key) + ":\n " + ', '.join(
                             map(str, self.find_Keys(key))))
                for K in self.find_Keys(key):
                    self.set_filter(K, condition=condition, min=min, max=max, filter=filter,
                                    incremental_filter=incremental_filter, filter_operation=filter_operation, undo=None)
                return None

        # start of main function, setting parameters
        DateFormat = ''  # set default date string format

        Incremental = bool(incremental_filter)  # move parameter to internal variable
        if incremental_filter and self.filter['filter'] is None:
            Incremental = False  # if IncrementalFilter is True but previous filter is None, there is nothing to "increment"

        # verify Filter operation is AND or * or OR or +
        if type(filter_operation) is str and filter_operation.lower() in ['+', 'or']:
            Operation = '+'  # OR operation
        else:
            Operation = '*'  # AND is the default operation

        # APPLY or calculate the Filter
        if filter is not None:  # apply it if Filter parameter is provided
            if type(filter) is list or type(filter) is tuple:
                filter = np.array(filter)  # convert to numpy array
            if type(filter) is np.ndarray:
                if len(filter) == len(self.fieldtime[2]):  # check Filter has the proper length
                    if filter.dtype == 'bool':  # check it has the correct dtype
                        applyFilter(filter, UnDo=undo)
                        self.filter['key'].append(None)
                        self.filter['min'].append(None)
                        self.filter['max'].append(None)
                        self.filter['condition'].append(None)
                        self.filter['incremental'].append(incremental_filter)
                        self.filter['operation'].append(filter_operation)
                        return ContinueFiltering(Key=key, Condition=condition, Min=min, Max=max, Filter=None,
                                                 Operation=Operation)
                    else:
                        try:
                            filter = filter.astype('bool')
                            # corrected the filter, apply it
                            return ContinueFiltering(Key=key, Condition=condition, Min=min, Max=max, Filter=None,
                                                     Operation=Operation)
                        except:
                            _verbose(self.speak, 3, " the 'Filter' must be an array of dtype 'bool'")
                            return False

                else:  # filter is not correct
                    _verbose(self.speak, 3,
                             " the 'Filter' must have the exact same length of the simulation vectors: " + str(
                                 len(self.fieldtime[2])))
                    return False

        # apply or CALCULATE the Filter
        else:  # calculate the filter
            if key is None and condition is None and min is None and max is None:
                # no arguments provided, means reset
                return self.reset_filter()

            elif key is None:  # Key is not provided
                # take previous Key
                if self.filter['key'][-1] is not None:
                    if (type(min) is str and MightBeDate(min) != False) or (
                            type(max) is str and MightBeDate(max) != False):
                        if type(self.get_Vector(self.filter['key'][-1])[self.filter['key'][-1]][0]) is np.datetime64:
                            key = self.filter['key'][-1]  # previous Key is DATE kind and Min or Max are dates
                        else:
                            key = 'DATE'  # Min or Max are dates but previos Key is not DATE kind, set proper Key for this Min or Max
                    else:  # take the previous Key
                        key = self.filter['key'][-1]

                # no previous Key
                elif (type(min) is str and MightBeDate(min) != False) or (
                        type(max) is str and MightBeDate(max) != False):
                    # Min or Max are DATE strings, set Key accordingly
                    key = 'DATE'

                # the Key might be inside the Condition
                elif condition is not None:
                    pass  # check later

                # if Key is a numpy.array or a list, it could be a filter
                elif type(key) is list or type(key) is tuple or type(filter) is np.ndarray:
                    if len(key) == len(self.fieldtime[2]):  # it looks like a Filter
                        _verbose(self.speak, 1, ' a Filter was received')
                        return ContinueFiltering(Key=None, Condition=condition, Min=min, Max=max, Filter=key,
                                                 Operation=Operation)

                # missing Key
                else:
                    _verbose(self.speak, 2, ' no Filter or Key received.')
                    return False

            # ckeck the received is valid:
            elif not self.is_Key(key):
                # the Key is a not in the simulation, might be a Condition string
                if condition is None:  # there is no Condition argument provided
                    for cond in ['<', '>', '<=', '>=', '!=', '==', '=', '<>', '><']:  # check for conditional strings
                        if cond in key:
                            _verbose(self.speak, 1, ' a Condition was received')
                            return ContinueFiltering(Key=None, Condition=key, Min=min, Max=max, Filter=filter,
                                                     Operation=Operation)
                else:
                    raise KeyError(" the argument Key: '" + str(key) + "' is not a key in this simulation")

            # calculate the NewFilter

            if Incremental:  # if Incremental is True, keep the current Filter for new calculations
                FilterArray = self.filter['filter']
            else:  # if Incremental is False, create a new array
                FilterArray = np.array([True] * len(self.fieldtime[2]))
            # temporarily deactivate current filter
            self.filter['filter'] = None

            # previous = self.filter.copy()
            # self.filter = {'key':None, 'min':None, 'max':None, 'condition':None, 'filter':None, 'reset':True}

            if min is not None:  # apply Min parameter
                if type(min) in [int, float]:
                    # Min is a number

                    # check consistency with Max parameter
                    if max is None:
                        pass  # is OK
                    elif type(max) is int or type(max) is float:
                        pass  # OK
                    else:  # Max is not number
                        _verbose(self.speak, 3, " the parameter 'Min' is a number: " + str(
                            min) + "\n then 'Max' must be also a number.")
                        # raise TypeError(" if Min is a number, Max must be a number also.")
                        return False

                    # calculate and apply filter
                    KeyArray = self.get_Vector(key)[key]
                    applyFilter(KeyArray >= min, FilterArray, UnDo=undo)
                    self.filter['key'].append(key)
                    self.filter['min'].append(min)
                    self.filter['max'].append(None)
                    self.filter['condition'].append(None)
                    self.filter['incremental'].append(incremental_filter)
                    self.filter['operation'].append(filter_operation)

                    if filter_operation is None:
                        if condition is None:
                            if (type(max) is int or type(max) is float) and min > max:
                                return ContinueFiltering(Key=key, Condition=condition, Min=None, Max=max, Filter=filter,
                                                         Operation='+')
                        else:
                            pass  # to implement later
                    return ContinueFiltering(Key=key, Condition=condition, Min=None, Max=max, Filter=filter,
                                             Operation=Operation)

                if type(min) is str:
                    # Min a string, might be a date
                    DateFormat = str(MightBeDate(min))
                    try:
                        min = np.datetime64(
                            pd.to_datetime(_strDate(min, DateFormat, speak=(self.speak == 1 or DateFormat == ''))))
                        if DateFormat != '':
                            _verbose(self.speak, 2, " the 'Min' date format is " + DateFormat)
                    except:
                        _verbose(self.speak, 3,
                                 " if the 'Min' is string it must represent a date, better if is formatted like DD-MMM-YYYY")
                        return False

                if type(min) is np.datetime64:
                    # Min is a date

                    # check consistency with Max parameter
                    if max is None:
                        pass  # is OK
                    elif type(max) is str:
                        DateFormat = str(MightBeDate(max))
                        try:
                            max = np.datetime64(
                                pd.to_datetime(_strDate(max, DateFormat, speak=(self.speak == 1 or DateFormat == ''))))
                        except:
                            _verbose(self.speak, 3,
                                     " the parameter 'Min' is represents a date: " + _strDate(min, DateFormat,
                                                                                              speak=False) + "\n then 'Max' should be a valid date.")
                            # raise TypeError(" if Min is a date, Max must be a date also.")
                            return False
                    else:  # Max is not None and is not a date string
                        _verbose(self.speak, 3,
                                 " the parameter 'Min' is represents a date: " + _strDate(min, DateFormat,
                                                                                          speak=False) + "\n then 'Max' must be also a date.")
                        # raise TypeError(" if Min is a date, Max must be a date also.")
                        return False

                    # calculate and apply filter
                    KeyArray = self.get_Vector(key)[key]
                    applyFilter(KeyArray >= min, FilterArray, UnDo=undo)
                    self.filter['key'].append(key)
                    self.filter['min'].append(min)
                    self.filter['max'].append(None)
                    self.filter['condition'].append(None)
                    self.filter['incremental'].append(incremental_filter)
                    self.filter['operation'].append(filter_operation)

                    if filter_operation is None:
                        if type(max) is np.datetime64 and min > max:
                            return ContinueFiltering(Key=key, Condition=condition, Min=None, Max=max, Filter=filter,
                                                     Operation='+')
                    return ContinueFiltering(Key=key, Condition=condition, Min=None, Max=max, Filter=filter,
                                             Operation=Operation)


                else:  # not proper type of Min
                    _verbose(self.speak, 3, " the 'Min' value for the filter must be integer, float or date")
                    return False

            if max is not None:  # apply Max parameter
                if type(max) is int or type(max) is float:
                    # Min is a number

                    # calculate and apply filter
                    KeyArray = self.get_Vector(key)[key]
                    applyFilter(KeyArray <= max, FilterArray, UnDo=undo)

                    self.filter['key'].append(key)
                    self.filter['min'].append(None)
                    self.filter['max'].append(max)
                    self.filter['condition'].append(None)
                    self.filter['incremental'].append(incremental_filter)
                    self.filter['operation'].append(filter_operation)

                    return ContinueFiltering(Key=key, Condition=condition, Min=min, Max=None, Filter=filter,
                                             Operation=Operation)

                if type(max) is str:
                    # Max a string, might be a date
                    DateFormat = str(MightBeDate(max))
                    try:
                        max = np.datetime64(
                            pd.to_datetime(_strDate(max, DateFormat, speak=(self.speak == 1 or DateFormat == ''))))
                        if DateFormat != '':
                            _verbose(self.speak, 2, " the 'Max' date format is " + DateFormat)
                    except:
                        _verbose(self.speak, 3,
                                 " if the 'Max' is string it must represent a date, better if is formatted like DD-MMM-YYYY")
                        return False

                if type(max) is np.datetime64:
                    # Max is a date

                    # calculate and apply filter
                    KeyArray = self.get_Vector(key)[key]
                    applyFilter(KeyArray <= max, FilterArray, UnDo=undo)
                    self.filter['key'].append(key)
                    self.filter['min'].append(None)
                    self.filter['max'].append(max)
                    self.filter['condition'].append(None)
                    self.filter['incremental'].append(incremental_filter)
                    self.filter['operation'].append(filter_operation)

                    return ContinueFiltering(Key=key, Condition=condition, Min=min, Max=None, Filter=filter,
                                             Operation=Operation)

                else:  # not proper type of Max
                    _verbose(self.speak, 3, " the 'Max' value for the filter must be integer or float")
                    return False

            if condition is not None:  # apply Condition parameter
                if type(condition) is str:
                    NewCondition = ''
                    for cond in ['<>', '><']:  # check common mistakes
                        if cond in condition:
                            _verbose(self.speak, -1,
                                     " I've saved your life this time, but keep in mind that the inequality check in python is '!=' and not '" + cond + "'")
                            NewCondition = condition.replace(cond, '!=')
                    for cond in ['=>', '=<']:  # check common mistakes
                        if cond in condition:
                            _verbose(self.speak, -1,
                                     " I've saved your life this time, but keep in mind that the '" + cond + "' is not the correct sintax in Python for '" + cond[
                                                                                                                                                             ::-1] + "'")
                            NewCondition = condition.replace(cond, cond[::-1])
                    for c in range(1, len(condition) - 1):
                        if condition[c] == '=':
                            if condition[c + 1] == '=' or condition[c - 1] == '=':
                                pass  # means ==
                            elif condition[c - 1] == '!':
                                pass  # means !=
                            elif condition[c - 1] == '>':
                                pass  # means >=
                            elif condition[c - 1] == '<':
                                pass  # means <=
                            else:
                                _verbose(self.speak, -1,
                                         " I've saved your life this time, but keep in mind that the equality check in python is '==' and not '='")
                                NewCondition = condition[:c] + '=' + condition[c:]
                    if NewCondition != '':
                        _verbose(self.speak, 2, "\n the received condition was: '" + condition + "'" + \
                                 "\n the corrected condition in: '" + NewCondition + "'")
                        condition = NewCondition
                    found = []
                    for cond in ['>=', '<=', '==', '!=']:
                        if cond in condition:
                            found.append(cond)
                    for c in range(len(condition) - 1):
                        if condition[c] in ['<', '>']:
                            if condition[c + 1] != '=':
                                found.append(condition[c])
                    CondList = _multisplit(condition, found)

                    if len(CondList) < 2:
                        _verbose(self.speak, 3, " the Condition parameter is not correct: '" + condition + "'")
                        return False
                    if len(CondList) == 2:
                        CondFilter = applyCondition(CondList[0], CondList[1], None)
                        applyFilter(CondFilter, FilterArray, UnDo=undo)
                        self.filter['key'].append(key)
                        self.filter['min'].append(None)
                        self.filter['max'].append(None)
                        self.filter['condition'].append(condition)
                        self.filter['incremental'].append(incremental_filter)
                        self.filter['operation'].append(filter_operation)
                        self.filter['reset'] = True
                        self.set_FieldTime()
                        return True
                    if len(CondList) == 3:
                        CondFilter = applyCondition(CondList[0], CondList[1], CondList[2])
                        applyFilter(CondFilter, FilterArray, UnDo=undo)
                        self.filter['key'].append(key)
                        self.filter['min'].append(None)
                        self.filter['max'].append(None)
                        self.filter['condition'].append(condition)
                        self.filter['incremental'].append(incremental_filter)
                        self.filter['operation'].append(filter_operation)
                        self.filter['reset'] = True
                        self.set_FieldTime()
                        return True
                    if len(CondList) == 5:
                        if ('<' in CondList[1] and '<' in CondList[3]) and (CondList[0] <= CondList[2]):
                            CondOperation = '*'
                        elif ('>' in CondList[1] and '>' in CondList[3]) and (CondList[0] >= CondList[2]):
                            CondOperation = '*'
                        elif ('<' in CondList[1] and '!=' in CondList[3]) and (CondList[0] <= CondList[2]):
                            CondOperation = '*'
                        elif ('!=' in CondList[1] and '>' in CondList[3]) and (CondList[0] >= CondList[2]):
                            CondOperation = '*'
                        else:
                            CondOperation = '+'
                        CondFilter1 = applyCondition(CondList[0], CondList[1], CondList[2])
                        CondFilter2 = applyCondition(CondList[2], CondList[3], CondList[4])

                        if type(CondFilter1) is np.ndarray and type(CondFilter2) is np.ndarray:
                            if CondOperation == '+':
                                CondFilter = CondFilter1 + CondFilter2
                            else:
                                CondFilter = CondFilter1 * CondFilter2
                            applyFilter(CondFilter, FilterArray, UnDo=undo)
                            self.filter['key'].append(key)
                            self.filter['min'].append(None)
                            self.filter['max'].append(None)
                            self.filter['condition'].append(condition)
                            self.filter['incremental'].append(incremental_filter)
                            self.filter['operation'].append(filter_operation)
                            self.filter['reset'] = True
                            self.set_FieldTime()
                            return True
                        else:
                            self.filter['reset'] = True
                            return False

    def get_Vectors(self, key=None, reload=False):
        return self.get_Vector(key, reload)

    def get_Vector(self, key=None, reload=False):
        """
        returns a dictionary with numpy vectors for the selected key(s)
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        returnVectors = self.get_UnfilteredVector(key, reload)

        if self.filter['filter'] is None:
            return returnVectors
        else:
            if self.filter['key'][-1] is not None:
                _verbose(self.speak, 1, " filter by key '" + self.filter['key'][-1] + "'")
            # for each in returnVectors:
            #     returnVectors[each] = returnVectors[each][self.get_Filter()]
            returnVectors = {each: returnVectors[each][self.get_filter()] for each in returnVectors}
            return returnVectors

    def get_VectorWithUnits(self, key=None, reload=False):
        """
        returns a dictionary with a tuple (units, numpy vectors)
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        returnVectors = self.get_Vector(key=key, reload=reload)
        for key in returnVectors:
            returnVectors[key] = (self.get_Unit(key), returnVectors[key])
        return returnVectors

    # extract the raw vector, without apply filter and without restarts or continues
    def get_RawVector(self, key=None, reload=False):
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
        if self.results is not None:
            if type(key) is str:
                returnVectors[key] = self.checkIfLoaded(key, reload)
            if type(key) is list or type(key) is tuple:
                listOfKeys = list(set(key))
                for each in listOfKeys:
                    returnVectors[each] = self.checkIfLoaded(each, reload)
        return returnVectors

    def get_UnfilteredVector(self, key=None, reload=False):
        """
        returns a dictionary with numpy vectors for the selected key(s)
        ignoring any applied filter
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        # check restarts
        restartDict = {}
        if len(self.get_Restart()) > 0:
            restartDict = self.checkRestarts(key, reload)

        # check continuations
        continuationDict = {}
        if len(self.get_Continuation()) > 0:
            continuationDict = self.checkContinuations(key, reload)

        # get vector for current simulation
        returnVectors = self.get_RawVector(key=key, reload=reload)

        if restartDict != {} and continuationDict != {}:
            # concatenate restarts + self + continuations
            # for each in returnVectors:
            #     returnVectors[each] = np.concatenate([ restartDict[each], returnVectors[each], continuationDict[each] ])
            returnVectors = {each: np.concatenate([restartDict[each], returnVectors[each], continuationDict[each]]) for
                             each in returnVectors}
        elif restartDict != {}:
            # concatenate restarts + self
            # for each in returnVectors:
            #     returnVectors[each] = np.concatenate([ restartDict[each], returnVectors[each] ])
            returnVectors = {each: np.concatenate([restartDict[each], returnVectors[each]]) for each in returnVectors}
        elif continuationDict != {}:
            # concatenate self + continuations
            # for each in returnVectors:
            #     returnVectors[each] = np.concatenate([ returnVectors[each], continuationDict[each] ])
            returnVectors = {each: np.concatenate([returnVectors[each], continuationDict[each]]) for each in
                             returnVectors}

        return returnVectors

    def get_RawVectorWithUnits(self, key=None, reload=False):
        """
        returns a dictionary with a tuple (units, numpy vectors)
        ignoring:
            any applied filter
            any restarts
            any continuations
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        returnVectors = self.get_RawVector(key=key, reload=reload)
        # for key in returnVectors:
        #     returnVectors[key] = (self.get_Unit(key), returnVectors[key])
        returnVectors = {key: (self.get_Unit(key), returnVectors[key]) for key in returnVectors}
        return returnVectors

    # support functions for get_Vector:
    def checkRestarts(self, key=None, reload=False):

        returnVectors = {}
        Rlist = self.restarts  # + [self]
        if type(key) is str:
            key = [key]

        for K in key:

            # check vectors previously calculated over the restarts
            if not reload and K in self.vectorsRestart:
                _verbose(self.speak, 1, "          recovering vector from precious calculations dictionary")
                returnVectors[K] = self.vectorsRestart[K]

            # extract vector from restarts
            else:
                # VectorsList = []
                _verbose(self.speak, 1, " preparing key '" + str(K) + "'")
                for R in Rlist:
                    if R.is_Key(K):
                        # try to extract the not-filtered vector from the simulation
                        Vector = R.get_RawVector(K)[K]
                        _verbose(self.speak, 1, "     reading from restart " + str(R))
                    else:
                        # if failed to extract, create a zeros vector of the 'TIME' vector size
                        Vector = np.zeros(len(R))
                        _verbose(self.speak, 1, "     filling with zeros for restart " + str(R))

                    # apply filter
                    _verbose(self.speak, 1, "          applying filter")
                    Vector = Vector[self.restartFilters[R]]

                    # concatenate vectors
                    if K in returnVectors:
                        _verbose(self.speak, 1, "          concatenating vectors")
                        returnVectors[K] = np.concatenate([returnVectors[K], Vector])
                    else:
                        _verbose(self.speak, 1, "          creating vector")
                        returnVectors[K] = Vector
                # returnVectors[K] = np.concatenate([returnVectors[K], self.checkIfLoaded(K, False)])

        # return returnVectors
        if self.filter['filter'] is None:
            return returnVectors
        else:
            if self.filter['key'][-1] is not None:
                _verbose(self.speak, 1, " filter by key '" + self.filter['key'][-1] + "'")
            for each in returnVectors:
                returnVectors[each] = returnVectors[each]  # [self.get_Filter()]
            return returnVectors

    def checkContinuations(self, key=None, reload=False):

        returnVectors = {}
        Clist = self.continuations  # + [self]
        if type(key) is str:
            key = [key]

        for K in key:

            # check vectors previously calculated over the continues
            if not reload and K in self.vectorsContinue:
                _verbose(self.speak, 1, "          recovering vector from precious calculations dictionary")
                returnVectors[K] = self.vectorsContinue[K]

            # extract vector from continues
            else:
                VectorsList = []
                _verbose(self.speak, 1, " preparing key '" + str(K) + "'")
                for C in Clist:
                    if C.is_Key(K):
                        # try to extract the not-filtered vector from the simulation
                        Vector = C.get_RawVector(K)[K]
                        _verbose(self.speak, 1, "     reading from continue " + str(C))
                    else:
                        # if failed to extract, create a zeros vector of the 'TIME' vector size
                        Vector = np.zeros(len(C))
                        _verbose(self.speak, 1, "     filling with zeros for continue " + str(C))

                    # apply filter
                    _verbose(self.speak, 1, "          applying filter")
                    Vector = Vector[self.continuationFilters[C]]

                    # concatenate vectors
                    if K in returnVectors:
                        _verbose(self.speak, 1, "          concatenating vectors")
                        returnVectors[K] = np.concatenate([returnVectors[K], Vector])
                    else:
                        _verbose(self.speak, 1, "          creating vector")
                        returnVectors[K] = Vector
                # returnVectors[K] = np.concatenate([self.checkIfLoaded(K, False), returnVectors[K]])

        # return returnVectors
        if self.filter['filter'] is None:
            return returnVectors
        else:
            if self.filter['key'][-1] is not None:
                _verbose(self.speak, 1, " filter by key '" + self.filter['key'][-1] + "'")
            for each in returnVectors:
                returnVectors[each] = returnVectors[each]  # [self.get_Filter()]
            return returnVectors

    def checkIfLoaded(self, key, reload):
        """
        internal function to avoid reloading the same vector twice...
        """
        reload = bool(reload)
        _verbose(self.speak, 1, ' looking for key ' + str(key))
        if str(key).upper().strip() not in self.vectors or reload is True:
            self.vectors[key.upper().strip()] = self.loadVector(key)
        return self.vectors[key.upper().strip()]

    def get_VectorWithoutRestart(self, key=None, reload=False):
        """
        returns a dictionary with numpy vectors for the selected key(s)
        key may be:
            a string with a single key or,
            a list or tuple containing the keys names as strings.
        """
        returnVectors = {}
        if self.results is not None:
            if type(key) is str:
                returnVectors[key] = self.checkIfLoaded(key, reload)
            if type(key) is list or type(key) is tuple:
                listOfKeys = list(set(key))
                for each in listOfKeys:
                    returnVectors[each] = self.checkIfLoaded(each, reload)
        return returnVectors

    def set_Vector(self, key, vector_data, units, data_type='auto', overwrite=None):
        """
        Writes a new vector into the dataset
        or overwrite an existing one if overwrite = True
        The data is stored as numpy.array

        > Key must be a string, intended to be the name of the Vector
        > VectorData must be a list, tuple or numpy.array
        > Units must be a string representing the Unit of the data
          optional DataType can define the tipe of data to cast the VectorData.
          The accepted types are the regular numpy types (int, float, datetime).
          If set to 'auto' it will try to guess the datatype or leave as string.
        > optional overwrite protects the data to be overwritten by mistake,
          the default value for overwrite can be changed with set_Overwrite method
        """
        if type(data_type) is str:
            data_type = data_type.lower().strip()

        if overwrite is None:
            overwrite = self.overwrite
        elif type(overwrite) in (int, float):
            overwrite = bool(overwrite)
        elif type(overwrite) is bool:
            pass
        else:
            overwrite = False

        # validating Key
        if type(key) is str:
            key = key.strip()
        else:
            raise TypeError(' <set_Vector> Key must be a string')

        if key in self.vectors and overwrite is False:
            raise OverwritingError(
                ' <set_Vector> the Key ' + key + ' already exists in the dataset and overwrite parameter is set to False. Set overwrite=True to avoid this message and change the DataVector.')

        # validating VectorData
        if type(vector_data) in (list, tuple):
            if len(vector_data) == 0:
                raise TypeError(' <set_Vector> VectorData must not be empty')
            vector_data = np.array(vector_data)
        elif type(vector_data) is np.ndarray:
            if data_type == 'auto':
                if 'int' in str(vector_data.dtype):
                    data_type = 'int'
                    _verbose(self.speak, 1,
                             key + ' <set_Vector> vector detected as numpy.array of dtype ' + data_type + '.')
                elif 'float' in str(vector_data.dtype):
                    data_type = 'float'
                    _verbose(self.speak, 1,
                             key + ' <set_Vector> vector detected as numpy.array of dtype ' + data_type + '.')
                elif 'datetime' in str(vector_data.dtype):
                    data_type = 'datetime'
                    _verbose(self.speak, 1,
                             key + ' <set_Vector> vector detected as numpy.array of dtype ' + data_type + '.')
            if vector_data.size == 0:
                raise TypeError(' <set_Vector> VectorData must not be empty')
            if len(vector_data.shape) == 1:
                pass  # OK
            elif len(vector_data.shape) == 2:
                if vector_data.shape[0] == 1 or vector_data.shape[1] == 1:
                    vector_data = vector_data.reshape(-1, )
                else:
                    pass  # is a matrix
            else:
                pass  # is a multidimensional matrix!!!
        elif isinstance(vector_data, Series):
            if data_type == 'auto':
                if 'int' in str(vector_data.dtype):
                    data_type = 'int'
                    _verbose(self.speak, 1,
                             key + ' <set_Vector> vector detected as pandas.series of dtype ' + data_type + '.')
                elif 'float' in str(vector_data.dtype):
                    data_type = 'float'
                    _verbose(self.speak, 1,
                             key + ' <set_Vector> vector detected as pandas.series of dtype ' + data_type + '.')
                elif 'datetime' in str(vector_data.dtype):
                    data_type = 'datetime'
                    _verbose(self.speak, 1,
                             key + ' <set_Vector> vector detected as pandas.series of dtype ' + data_type + '.')
            if vector_data.size == 0:
                raise TypeError(' <set_Vector> VectorData must not be empty')
        elif isinstance(vector_data, (DataFrame)):
            if vector_data.size == 0:
                raise TypeError(' <set_Vector> VectorData must not be empty')
            else:
                return self.__setitem__(key, vector_data, units)
        else:
            raise TypeError(
                ' <set_Vector> VectorData must be a list, tuple, numpy.ndarray, pandas Series or DataFrame, SimSeries or SimDataFrame. Received ' + str(
                    type(vector_data)))

        # validating Units
        if units is None:
            units = 'dimensionless'
        elif type(units) is str:
            units = units.strip()
            if units.startswith('(') and units.endswith(')') and units.count('(') == 1 and units.count(')') == 1:
                units = units.strip('()')
            if unit.isUnit(units):
                pass
            elif units == 'DEGREES' and 'API' in _mainKey(key).upper():
                units = 'API'
                _verbose(self.speak, 2,
                         ' <set_Vector>\nIMPORTANT: the selected Units: ' + units + ' were chaged to "API" for the vector with key name ' + key + '.')
            elif (' / ' in units and unit.isUnit(units.replace(' / ', '/'))) or (
                    '/ ' in units and unit.isUnit(units.replace('/ ', '/'))) or (
                    ' /' in units and unit.isUnit(units.replace(' /', '/'))):
                _verbose(self.speak, 1,
                         " <set_Vector>\nMESSAGE: the selected Units: '" + units + "' were chaged to " + units.replace(
                             ' /', '/').replace('/ ', '/') + ' for the vector with key name ' + key + '.')
                units = units.replace('/ ', '/').replace(' /', '/')
            else:
                _verbose(self.speak, 3,
                         " <set_Vector>\nIMPORTANT: the selected Units: '" + units + "' are not recognized by the programm and will not be able to convert this Vector " + str(
                             key) + ' into other units.')
        elif type(units) is dict:
            if isinstance(vector_data, SimSeries):
                units = vector_data.get_UnitsString()
            elif key in units:
                units = units[key]
            else:
                raise TypeError(' <set_Vector> Units must be a string')
        elif units is None and isinstance(vector_data, (SimSeries, SimDataFrame)):
            pass  # units are included in the SimDataFrame or SimSeries
        else:
            raise TypeError(' <set_Vector> Units must be a string')

        if data_type == 'auto':
            _verbose(self.speak, 1, ' <set_Vector> guessing the data type of the VectorData ' + key)
            done = False
            if key.upper() == 'DATE' or key.upper() == 'DATES':
                try:
                    vector_data = np.datetime64(pd.to_datetime(vector_data), 's')
                    _verbose(self.speak, 1, key + ' <set_Vector> vector casted as datetime.')
                    done = True
                except:
                    pass
            elif key.upper() in ['TIME', 'YEARS', 'YEAR', 'DAYS', 'DAYS', 'MONTH', 'MONTHS']:
                try:
                    vector_data = vector_data.astype('float')
                    _verbose(self.speak, 1, key + ' <set_Vector> vector casted as floating point.')
                    done = True
                except:
                    pass

            if done is False:
                Integer = False
                try:
                    VectorDataInt = vector_data.astype(int)
                    Integer = True
                except:
                    try:
                        vector_data = vector_data.astype(float)
                        _verbose(self.speak, 1, key + ' <set_Vector> vector casted as floating point.')
                    except:
                        try:
                            vector_data = np.datetime64(pd.to_datetime(vector_data), 's')
                            _verbose(self.speak, 1, key + ' <set_Vector> vector casted as datetime.')
                        except:
                            if type(vector_data) is np.ndarray:
                                VectorType = str(vector_data.dtype)
                            elif type(vector_data) is list or type(vector_data) is tuple:
                                VectorType = str(type(vector_data)) + ' with ' + type(vector_data[0]) + ' inside'
                            else:
                                VectorType = str(type(vector_data))
                            _verbose(self.speak, 2,
                                     ' <set_Vector> not able to cast the VectorData ' + key + ', kept as received: ' + VectorType + '.')
                if Integer:
                    try:
                        VectorDataFloat = vector_data.astype(float)
                        if np.all(VectorDataFloat == VectorDataInt):
                            vector_data = VectorDataInt
                            _verbose(self.speak, 1, key + ' <set_Vector> vector casted as integer.')
                        else:
                            vector_data = VectorDataFloat
                            _verbose(self.speak, 1, key + ' <set_Vector> vector casted as floating point.')
                    except:
                        pass

        elif 'datetime' in data_type:
            try:
                vector_data = np.array(pd.to_datetime(vector_data), 'datetime64[s]')
            except:
                try:
                    vector_data = vector_data.astype(data_type)
                except:
                    _verbose(self.speak, 2,
                             ' <set_Vector> not able to cast the VectorData ' + key + ', kept as received: ' + data_type + '.')
        else:
            try:
                vector_data = vector_data.astype(data_type)
            except:
                _verbose(self.speak, 2,
                         ' <set_Vector> not able to cast the VectorData ' + key + ', kept as received: ' + data_type + '.')

        # ensure VectorData is numpy.array
        if isinstance(vector_data, Series):
            vector_data = vector_data.to_numpy()

        # save restart vector part
        if len(self.get_vectorTemplate()[self.get_vectorTemplate() == -1]) > 0:
            if len(vector_data[self.get_vectorTemplate() == -1]) == len(
                    self.checkRestarts(self.get_TimeVector())[self.get_TimeVector()]):
                self.vectorsRestart[key] = vector_data[self.get_vectorTemplate() == -1]
            elif len(vector_data[self.get_vectorTemplate() == -1]) < len(
                    self.checkRestarts(self.get_TimeVector())[self.get_TimeVector()]):
                # a filter is applied
                filteredTime = self.get_Vector(self.get_TimeVector())[(self.get_TimeVector())][
                    self.get_vectorTemplate() == -1]
                filteredDF = DataFrame(
                    {'SelfTime': filteredTime, key: vector_data[self.get_vectorTemplate() == -1]}).set_index('SelfTime')
                rawTime = self.checkRestarts(self.get_TimeVector())[self.get_TimeVector()]
                rawDF = DataFrame({'SelfTime': rawTime}).set_index('SelfTime')
                rawDF[key] = filteredDF[key]
                rawDF = rawDF.replace(np.nan, self.null)
                newRawVector = rawDF[key].to_numpy()
                self.vectorsRestart[key] = newRawVector
            elif len(vector_data[self.get_vectorTemplate() == -1]) > len(
                    self.checkRestarts(self.get_TimeVector())[self.get_TimeVector()]):
                print(vector_data[self.get_vectorTemplate() == -1],
                      self.get_RawVector(self.get_TimeVector())[self.get_TimeVector()])
                print(len(vector_data[self.get_vectorTemplate() == -1]),
                      len(self.get_RawVector(self.get_TimeVector())[self.get_TimeVector()]))
                raise ValueError('something went wrong')

        # save this simulation vector part
        if len(self.get_vectorTemplate()[self.get_vectorTemplate() == 0]) > 0:
            if len(vector_data[self.get_vectorTemplate() == 0]) == len(
                    self.get_RawVector(self.get_TimeVector())[self.get_TimeVector()]):
                # no filter seems to be applied
                self.vectors[key] = vector_data[self.get_vectorTemplate() == 0]
            elif len(vector_data[self.get_vectorTemplate() == 0]) < len(
                    self.get_RawVector(self.get_TimeVector())[self.get_TimeVector()]):
                # a filter is applied
                filteredTime = self.get_Vector(self.get_TimeVector())[(self.get_TimeVector())][
                    self.get_vectorTemplate() == 0]
                filteredDF = SimDataFrame(
                    {'SelfTime': filteredTime, key: vector_data[self.get_vectorTemplate() == 0]}).set_index('SelfTime')
                rawTime = self.get_RawVector(self.get_TimeVector())[self.get_TimeVector()]
                rawDF = SimDataFrame({'SelfTime': rawTime}).set_index('SelfTime')
                rawDF[key] = filteredDF[key]
                rawDF = rawDF.replace(np.nan, self.null)
                newRawVector = rawDF[key].to_numpy()
                self.vectors[key] = newRawVector
            elif len(vector_data[self.get_vectorTemplate() == 0]) > len(
                    self.get_RawVector(self.get_TimeVector())[self.get_TimeVector()]):
                raise ValueError('something went wrong')

        # save contuation vector part
        if len(self.get_vectorTemplate()[self.get_vectorTemplate() == 1]) > 0:
            if len(vector_data[self.get_vectorTemplate() == 1]) == len(
                    self.checkContinuations(self.get_TimeVector())[self.get_TimeVector()]):
                self.vectorsContinue[key] = vector_data[self.get_vectorTemplate() == 1]
            elif len(vector_data[self.get_vectorTemplate() == 1]) < len(
                    self.checkContinuations(self.get_TimeVector())[self.get_TimeVector()]):
                # a filter is applied
                filteredTime = self.get_Vector(self.get_TimeVector())[(self.get_TimeVector())][
                    self.get_vectorTemplate() == 1]
                filteredDF = DataFrame(
                    {'SelfTime': filteredTime, key: vector_data[self.get_vectorTemplate() == 1]}).set_index('SelfTime')
                rawTime = self.checkContinuations(self.get_TimeVector())[self.get_TimeVector()]
                rawDF = DataFrame({'SelfTime': rawTime}).set_index('SelfTime')
                rawDF[key] = filteredDF[key]
                rawDF = rawDF.replace(np.nan, self.null)
                newRawVector = rawDF[key].to_numpy()
                self.vectorsContinue[key] = newRawVector
            elif len(vector_data[self.get_vectorTemplate() == 1]) > len(
                    self.checkContinuations(self.get_TimeVector())[self.get_TimeVector()]):
                raise ValueError('something went wrong')

        self.units[key] = units
        if not self.is_Key(key):
            self.add_Key(key)
        self.get_Attributes(reload=True)

    def set_Overwrite(self, overwrite):
        if type(overwrite) is bool:
            self.overwrite = overwrite

    def get_Overwrite(self):
        return self.overwrite

    def strip_units(self):
        for key in self.units:
            if self.units[key] is None:
                pass
            else:
                self.units[key] = self.units[key].strip().strip("'").strip('"')
                if (self.units[key] is not None and len(self.units[key]) > 0) and (
                        self.units[key][0] == '(' and self.units[key][-1] == ')' and self.units[key].count('(') == 1 and
                        self.units[key].count(')') == 1):
                    self.units[key] = self.units[key].strip('( )').strip(" '").strip(' "')
                if 'DíA' in self.units[key]:
                    self.units[key] = self.units[key].replace('DíA', 'DAY')

    def fill_field_basics(self):
        np.seterr(divide='ignore', invalid='ignore')

        if self.is_Key('FOPR') is True and type(self.get_Vector('FOPR')['FOPR']) is np.ndarray and self.is_Key(
                'FWPR') is True and type(self.get_Vector('FWPR')['FWPR']) is np.ndarray:
            # calculated FLPR if not available:
            if self.is_Key('FLPR') is False or len(self.get_Vector('FLPR')['FLPR']) < len(
                    self.get_Vector('FWPR')['FWPR']) or type(self.get_Vector('FLPR')['FLPR']) != np.ndarray:
                try:
                    self.set_Vector('FLPR', np.array(self.get_Vector('FOPR')['FOPR'], dtype='float') + convertUnit(
                        np.array(self.get_Vector('FWPR')['FWPR'], dtype='float'),
                        self.get_Unit(
                            'FWPR'),
                        self.get_Unit(
                            'FOPR'), PrintConversionPath=(self.speak == 1)), self.get_Unit('FOPR'), overwrite=True)
                except:
                    _verbose(self.speak, 2, 'failed to create missing vector FLPR.')

            # calculated FWCT if not available:
            if self.is_Key('FWCT') is False or len(self.get_Vector('FWCT')['FWCT']) < len(
                    self.get_Vector('FWPR')['FWPR']) or type(self.get_Vector('FWCT')['FWCT']) != np.ndarray:
                try:
                    Vector = np.array(np.divide(np.array(self.get_Vector('FWPR')['FWPR'], dtype='float'),
                                                convertUnit(np.array(self.get_Vector('FLPR')['FLPR'], dtype='float'),
                                                            self.get_Unit(
                                                                'FLPR'),
                                                            self.get_Unit(
                                                                'FWPR'), PrintConversionPath=(self.speak == 1))),
                                      dtype='float')
                    Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                    self.set_Vector('FWCT', Vector, 'FRACTION', overwrite=True)
                except:
                    _verbose(self.speak, 2, 'failed to create missing vector FWCT.')

            # calculated FWOR & FOWR if not available:
            if self.is_Key('FWOR') is False or len(self.get_Vector('FWOR')['FWOR']) < len(
                    self.get_Vector('FWPR')['FWPR']) or type(self.get_Vector('FWOR')['FWOR']) != np.ndarray:
                try:
                    Vector = np.array(np.divide(np.array(self.get_Vector('FWPR')['FWPR'], dtype='float'),
                                                np.array(self.get_Vector('FOPR')['FOPR'], dtype='float')),
                                      dtype='float')
                    Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                    self.set_Vector('FWOR', Vector, self.get_Unit('FWPR').split('/')[0] + '/' +
                                    self.get_Unit('FOPR').split('/')[0], overwrite=True)

                except:
                    _verbose(self.speak, 2, 'failed to create missing vector FWOR.')
                try:
                    Vector = np.array(np.divide(np.array(self.get_Vector('FOPR')['FOPR'], dtype='float'),
                                                np.array(self.get_Vector('FWPR')['FWPR'], dtype='float')),
                                      dtype='float')
                    Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                    self.set_Vector('FOWR', Vector, self.get_Unit('FOPR').split('/')[0] + '/' +
                                    self.get_Unit('FWPR').split('/')[0], overwrite=True)
                except:
                    _verbose(self.speak, 2, 'failed to create missing vector FOWR.')

        if self.is_Key('FOPR') is True and type(self.get_Vector('FOPR')['FOPR']) is np.ndarray and self.is_Key(
                'FGPR') is True and type(self.get_Vector('FGPR')['FGPR']) is np.ndarray:
            # calculated FGOR if not available:
            if self.is_Key('FGOR') is False or len(self.get_Vector('FGOR')['FGOR']) < len(
                    self.get_Vector('FOPR')['FOPR']) or type(self.get_Vector('FGOR')['FGOR']) != np.ndarray:
                try:
                    Vector = np.array(np.divide(np.array(self.get_Vector('FGPR')['FGPR'], dtype='float'),
                                                np.array(self.get_Vector('FOPR')['FOPR'], dtype='float')),
                                      dtype='float')
                    Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                    self.set_Vector('FGOR', Vector, self.get_Unit('FGPR').split('/')[0] + '/' +
                                    self.get_Unit('FOPR').split('/')[0], overwrite=True)
                except:
                    _verbose(self.speak, 2, 'failed to create missing vector FGOR.')

            # calculated FOGR if not available:
            if self.is_Key('FOGR') is False or len(self.get_Vector('FOGR')['FOGR']) < len(
                    self.get_Vector('FOPR')['FOPR']) or type(self.get_Vector('FOGR')['FOGR']) != np.ndarray:
                try:
                    Vector = np.array(np.divide(np.array(self.get_Vector('FOPR')['FOPR'], dtype='float'),
                                                np.array(self.get_Vector('FGPR')['FGPR'], dtype='float')),
                                      dtype='float')
                    Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                    self.set_Vector('FOGR', Vector, self.get_Unit('FOPR').split('/')[0] + '/' +
                                    self.get_Unit('FGPR').split('/')[0], overwrite=True)
                except:
                    _verbose(self.speak, 2, 'failed to create missing vector FOGR.')

        if self.is_Key('FOPT') is True and type(self.get_Vector('FOPT')['FOPT']) is np.ndarray and self.is_Key(
                'FWPT') is True and type(self.get_Vector('FWPT')['FWPT']) is np.ndarray:
            # calculated FLPR if not available:
            if self.is_Key('FLPT') is False or len(self.get_Vector('FLPT')['FLPT']) < len(
                    self.get_Vector('FWPT')['FWPT']) or type(self.get_Vector('FLPT')['FLPT']) != np.ndarray:
                try:
                    self.set_Vector('FLPT', np.array(self.get_Vector('FOPT')['FOPT'], dtype='float') + convertUnit(
                        np.array(self.get_Vector('FWPT')['FWPT'], dtype='float'),
                        self.get_Unit(
                            'FWPT'),
                        self.get_Unit(
                            'FOPT'), PrintConversionPath=(self.speak == 1)), self.get_Unit('FOPT'), overwrite=True)
                except:
                    try:
                        Name, Vector, Units = self.integrate('FLPR', 'FLPT')
                        self.set_Vector(Name, Vector, Units, 'float', True)
                        _verbose(self.speak, 2, 'vector FLPT integrated from FLPR.')
                    except:
                        _verbose(self.speak, 2, 'failed to create missing vector FLPT.')

        if self.is_Key('TIME') is True and type(self.get_Vector('TIME')['TIME']) is np.ndarray:
            if self.is_Key('DATE') is False or len(self.get_Vector('DATE')['DATE']) < len(
                    self.get_Vector('TIME')['TIME']) or type(self.get_Vector('DATE')['DATE']) != np.ndarray:
                self.createDATES()
            if self.is_Key('DATES') is False or len(self.get_Vector('DATES')['DATES']) < len(
                    self.get_Vector('TIME')['TIME']) or type(self.get_Vector('DATES')['DATES']) != np.ndarray:
                self.createDATES()

        if self.is_Key('DATE') is True and type(self.get_Vector('DATE')['DATE']) is np.ndarray:
            for T in ['YEAR', 'MONTH', 'DAY']:
                if self.is_Key(T) is False or len(self.get_Vector(T)[T]) < len(self.get_Vector('DATE')['DATE']) or type(
                        self.get_Vector(T)[T]) != np.ndarray:
                    if T == 'YEAR':
                        self.createYEAR()
                    elif T == 'MONTH':
                        self.createMONTH()
                    elif T == 'DAY':
                        self.createDAY()
        np.seterr(divide=None, invalid=None)

    def fill_well_basics(self):
        np.seterr(divide='ignore', invalid='ignore')

        for well in self.get_wells():
            if type(well) is str and len(well.strip()) > 0:
                well = well.strip()
                _verbose(self.speak, 2, ' calculating basic ratios for the well ' + well)
                if self.is_Key('WOPR:' + well) is True and type(
                        self.get_Vector('WOPR:' + well)['WOPR:' + well]) is np.ndarray and self.is_Key(
                        'WWPR:' + well) is True and type(self.get_Vector('WWPR:' + well)['WWPR:' + well]) is np.ndarray:
                    # calculated WLPR if not available:
                    if self.is_Key('WLPR:' + well) is False or len(
                            self.get_Vector('WLPR:' + well)['WLPR:' + well]) < len(
                            self.get_Vector('WWPR:' + well)['WWPR:' + well]) or type(
                            self.get_Vector('WLPR:' + well)['WLPR:' + well]) != np.ndarray:
                        try:
                            self.set_Vector('WLPR:' + well, np.array(self.get_Vector('WOPR:' + well)['WOPR:' + well],
                                                                     dtype='float') + convertUnit(
                                np.array(self.get_Vector('WWPR:' + well)['WWPR:' + well], dtype='float'),
                                self.get_Unit(
                                    'WWPR:' + well),
                                self.get_Unit(
                                    'WOPR:' + well), PrintConversionPath=(self.speak == 1)),
                                            self.get_Unit('WOPR:' + well), overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector WLPR:' + well)

                    # calculated WWCT if not available:
                    if self.is_Key('WWCT:' + well) is False or len(
                            self.get_Vector('WWCT:' + well)['WWCT:' + well]) < len(
                            self.get_Vector('WWPR:' + well)['WWPR:' + well]) or type(
                            self.get_Vector('WWCT:' + well)['WWCT:' + well]) != np.ndarray:
                        try:
                            Vector = np.array(
                                np.divide(np.array(self.get_Vector('WWPR:' + well)['WWPR:' + well], dtype='float'),
                                          convertUnit(
                                              np.array(self.get_Vector('WLPR:' + well)['WLPR:' + well], dtype='float'),
                                              self.get_Unit(
                                                  'WLPR:' + well),
                                              self.get_Unit(
                                                  'WWPR:' + well), PrintConversionPath=(self.speak == 1))),
                                dtype='float')
                            Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                            self.set_Vector('WWCT', Vector, 'FRACTION', overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector WWCT:' + well)

                    # calculated WWOR & WOWR if not available:
                    if self.is_Key('WWOR:' + well) is False or len(
                            self.get_Vector('WWOR:' + well)['WWOR:' + well]) < len(
                            self.get_Vector('WWPR:' + well)['WWPR:' + well]) or type(
                            self.get_Vector('WWOR:' + well)['WWOR:' + well]) != np.ndarray:
                        try:
                            Vector = np.array(
                                np.divide(np.array(self.get_Vector('WWPR:' + well)['WWPR:' + well], dtype='float'),
                                          np.array(self.get_Vector('WOPR:' + well)['WOPR:' + well], dtype='float')),
                                dtype='float')
                            Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                            self.set_Vector('WWOR:' + well, Vector, self.get_Unit('WWPR:' + well).split('/')[0] + '/' +
                                            self.get_Unit('WOPR:' + well).split('/')[0], overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector WWOR:' + well)
                        try:
                            Vector = np.array(
                                np.divide(np.array(self.get_Vector('WOPR:' + well)['WOPR:' + well], dtype='float'),
                                          np.array(self.get_Vector('WWPR:' + well)['WWPR:' + well], dtype='float')),
                                dtype='float')
                            Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                            self.set_Vector('WOWR:' + well, Vector, self.get_Unit('WOPR:' + well).split('/')[0] + '/' +
                                            self.get_Unit('WWPR:' + well).split('/')[0], overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector WOWR:' + well)

                # calculated WGOR if not available:
                if self.is_Key('WOPR:' + well) is True and type(
                        self.get_Vector('WOPR:' + well)['WOPR:' + well]) is np.ndarray and self.is_Key(
                        'WGPR:' + well) is True and type(self.get_Vector('WGPR:' + well)['WGPR:' + well]) is np.ndarray:
                    if self.is_Key('WGOR:' + well) is False or len(
                            self.get_Vector('WGOR:' + well)['WGOR:' + well]) < len(
                            self.get_Vector('WOPR:' + well)['WOPR:' + well]) or type(
                            self.get_Vector('WGOR:' + well)['WGOR:' + well]) != np.ndarray:
                        try:
                            Vector = np.array(
                                np.divide(np.array(self.get_Vector('WGPR:' + well)['WGPR:' + well], dtype='float'),
                                          np.array(self.get_Vector('WOPR:' + well)['WOPR:' + well], dtype='float')),
                                dtype='float')
                            Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                            self.set_Vector('WGOR:' + well, Vector, self.get_Unit('WGPR:' + well).split('/')[0] + '/' +
                                            self.get_Unit('WOPR:' + well).split('/')[0], overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector WGOR:' + well)

                    # calculated WOGR if not available:
                    if self.is_Key('WOGR:' + well) is False or len(
                            self.get_Vector('WOGR:' + well)['WOGR:' + well]) < len(
                            self.get_Vector('WOPR:' + well)['WOPR:' + well]) or type(
                            self.get_Vector('WOGR:' + well)['WOGR:' + well]) != np.ndarray:
                        try:
                            Vector = np.array(
                                np.divide(np.array(self.get_Vector('WOPR:' + well)['WOPR:' + well], dtype='float'),
                                          np.array(self.get_Vector('WGPR:' + well)['WGPR:' + well], dtype='float')),
                                dtype='float')
                            Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                            self.set_Vector('WOGR:' + well, Vector, self.get_Unit('WOPR:' + well).split('/')[0] + '/' +
                                            self.get_Unit('WGPR:' + well).split('/')[0], overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector WOGR:' + well)

                if self.is_Key('WOPT:' + well) is True and type(
                        self.get_Vector('WOPT:' + well)['WOPT:' + well]) is np.ndarray and self.is_Key(
                        'WWPT:' + well) is True and type(self.get_Vector('WWPT:' + well)['WWPT:' + well]) is np.ndarray:
                    # calculated WLPR if not available:
                    if self.is_Key('WLPT:' + well) is False or len(
                            self.get_Vector('WLPT:' + well)['WLPT:' + well]) < len(
                            self.get_Vector('WWPT:' + well)['WWPT:' + well]) or type(
                            self.get_Vector('WLPT:' + well)['WLPT:' + well]) != np.ndarray:
                        try:
                            self.set_Vector('WLPT:' + well, np.array(self.get_Vector('WOPT:' + well)['WOPT:' + well],
                                                                     dtype='float') + convertUnit(
                                np.array(self.get_Vector('WWPT:' + well)['WWPT:' + well], dtype='float'),
                                self.get_Unit(
                                    'WWPT:' + well),
                                self.get_Unit(
                                    'WOPT:' + well), PrintConversionPath=(self.speak == 1)),
                                            self.get_Unit('WOPT:' + well), overwrite=True)
                        except:
                            try:
                                Name, Vector, Units = self.integrate('WLPR:' + well, 'WLPT:' + well)
                                self.set_Vector(Name, Vector, Units, 'float', True)
                                _verbose(self.speak, 2, 'vector WLPT:' + well + ' integrated from WLPR:' + well + '.')
                            except:
                                _verbose(self.speak, 2, 'failed to create missing vector WLPT:' + well)
        np.seterr(divide=None, invalid=None)

    def fill_basics(self, items_names=[], key_type=''):
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

        default of KeyType is:
            W if the ItemName exists in get_wells()
            G if the ItemName exists in get_groups()
            R if the ItemName exists in get_regions()
        """
        np.seterr(divide='ignore', invalid='ignore')

        if type(items_names) is str:
            items_names = [items_names]
        elif items_names == []:
            items_names = self.get_wells() + self.get_groups() + ('FIELD',)

        for item in items_names:
            KT = 'U'
            if item in list(self.get_regions()):
                KT = 'R'
            if item in list(self.get_groups()):
                KT = 'G'
            if item in list(self.get_wells()):
                KT = 'W'
            if item not in ('FIELD', 'ROOT'):
                item = ':' + item
                KT = 'F'
            if key_type != '':
                KT = key_type

            if type(item) is str and len(item.strip()) > 0:
                item = item.strip()
                _verbose(self.speak, 2, ' calculating basic ratios for the item ' + item)
                if self.is_Key(KT + 'OPR' + item) is True and type(
                        self.get_Vector(KT + 'OPR' + item)[KT + 'OPR' + item]) is np.ndarray and self.is_Key(
                        KT + 'WPR' + item) is True and type(
                    self.get_Vector(KT + 'WPR' + item)[KT + 'WPR' + item]) is np.ndarray:
                    # calculated WLPR if not available:
                    if self.is_Key(KT + 'LPR' + item) is False or len(
                            self.get_Vector(KT + 'LPR' + item)[KT + 'LPR' + item]) < len(
                            self.get_Vector(KT + 'WPR' + item)[KT + 'WPR' + item]) or type(
                            self.get_Vector(KT + 'LPR' + item)[KT + 'LPR' + item]) != np.ndarray:
                        try:
                            self.set_Vector(KT + 'LPR' + item,
                                            np.array(self.get_Vector(KT + 'OPR' + item)[KT + 'OPR' + item],
                                                     dtype='float') + np.array(
                                                convertUnit(self.get_Vector(KT + 'WPR' + item)[KT + 'WPR' + item],
                                                            dtype='float', PrintConversionPath=(self.speak == 1)),
                                                self.get_Unit(
                                                    KT + 'WPR' + item),
                                                self.get_Unit(
                                                    KT + 'OPR' + item)), self.get_Unit(KT + 'OPR' + item),
                                            overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector ' + KT + 'LPR' + item)

                    # calculated WWCT if not available:
                    if self.is_Key(KT + 'WCT' + item) is False or len(
                            self.get_Vector(KT + 'WCT' + item)[KT + 'WCT' + item]) < len(
                            self.get_Vector(KT + 'WPR' + item)[KT + 'WPR' + item]) or type(
                            self.get_Vector(KT + 'WCT' + item)[KT + 'WCT' + item]) != np.ndarray:
                        try:
                            Vector = np.array(np.divide(
                                np.array(self.get_Vector(KT + 'WPR' + item)[KT + 'WPR' + item], dtype='float'),
                                np.array(convertUnit(self.get_Vector(KT + 'LPR' + item)[KT + 'LPR' + item],
                                                     self.get_Unit(
                                                         KT + 'LPR' + item),
                                                     self.get_Unit(
                                                         KT + 'WPR' + item), PrintConversionPath=(self.speak == 1)),
                                         dtype='float')), dtype='float')
                            Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                            self.set_Vector(KT + 'WCT', Vector, 'FRACTION', overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector ' + KT + 'WCT' + item)

                    # calculated WWOR & WOWR if not available:
                    if self.is_Key(KT + 'WOR' + item) is False or len(
                            self.get_Vector(KT + 'WOR' + item)[KT + 'WOR' + item]) < len(
                            self.get_Vector(KT + 'WPR' + item)[KT + 'WPR' + item]) or type(
                            self.get_Vector(KT + 'WOR' + item)[KT + 'WOR' + item]) != np.ndarray:
                        try:
                            Vector = np.array(np.divide(
                                np.array(self.get_Vector(KT + 'WPR' + item)[KT + 'WPR' + item], dtype='float'),
                                np.array(self.get_Vector(KT + 'OPR' + item)[KT + 'OPR' + item], dtype='float')),
                                              dtype='float')
                            Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                            self.set_Vector(KT + 'WOR' + item, Vector, self.get_Unit(
                                KT + 'WPR' + item).split('/')[0] + '/' + self.get_Unit(KT + 'OPR' + item).split('/')[0],
                                            overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector ' + KT + 'WOR' + item)
                        try:
                            Vector = np.array(np.divide(
                                np.array(self.get_Vector(KT + 'OPR' + item)[KT + 'OPR' + item], dtype='float'),
                                np.array(self.get_Vector(KT + 'WPR' + item)[KT + 'WPR' + item], dtype='float')),
                                              dtype='float')
                            Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                            self.set_Vector(KT + 'OWR' + item, Vector, self.get_Unit(
                                KT + 'OPR' + item).split('/')[0] + '/' + self.get_Unit(KT + 'WPR' + item).split('/')[0],
                                            overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector ' + KT + 'OWR' + item)

                # calculated WGOR if not available:
                if self.is_Key(KT + 'OPR' + item) is True and type(
                        self.get_Vector(KT + 'OPR' + item)[KT + 'OPR' + item]) is np.ndarray and self.is_Key(
                        KT + 'GPR' + item) is True and type(
                    self.get_Vector(KT + 'GPR' + item)[KT + 'GPR' + item]) is np.ndarray:
                    if self.is_Key(KT + 'GOR' + item) is False or len(
                            self.get_Vector(KT + 'GOR' + item)[KT + 'GOR' + item]) < len(
                            self.get_Vector(KT + 'OPR' + item)[KT + 'OPR' + item]) or type(
                            self.get_Vector(KT + 'GOR' + item)[KT + 'GOR' + item]) != np.ndarray:
                        try:
                            Vector = np.array(np.divide(
                                np.array(self.get_Vector(KT + 'GPR' + item)[KT + 'GPR' + item], dtype='float'),
                                np.array(self.get_Vector(KT + 'OPR' + item)[KT + 'OPR' + item], dtype='float')),
                                              dtype='float')
                            Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                            self.set_Vector(KT + 'GOR' + item, Vector, self.get_Unit(
                                KT + 'GPR' + item).split('/')[0] + '/' + self.get_Unit(KT + 'OPR' + item).split('/')[0],
                                            overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector ' + KT + 'GOR' + item)

                    # calculated WOGR if not available:
                    if self.is_Key(KT + 'OGR' + item) is False or len(
                            self.get_Vector(KT + 'OGR' + item)[KT + 'OGR' + item]) < len(
                            self.get_Vector(KT + 'OPR' + item)[KT + 'OPR' + item]) or type(
                            self.get_Vector(KT + 'OGR' + item)[KT + 'OGR' + item]) != np.ndarray:
                        try:
                            Vector = np.array(np.divide(
                                np.array(self.get_Vector(KT + 'OPR' + item)[KT + 'OPR' + item], dtype='float'),
                                np.array(self.get_Vector(KT + 'GPR' + item)[KT + 'GPR' + item], dtype='float')),
                                              dtype='float')
                            Vector = np.nan_to_num(Vector, nan=0.0, posinf=0.0, neginf=0.0)
                            self.set_Vector(KT + 'OGR' + item, Vector, self.get_Unit(
                                KT + 'OPR' + item).split('/')[0] + '/' + self.get_Unit(KT + 'GPR' + item).split('/')[0],
                                            overwrite=True)
                        except:
                            _verbose(self.speak, 2, 'failed to create missing vector ' + KT + 'OGR' + item)

                if self.is_Key(KT + 'OPT' + item) is True and type(
                        self.get_Vector(KT + 'OPT' + item)[KT + 'OPT' + item]) is np.ndarray and self.is_Key(
                        KT + 'WPT' + item) is True and type(
                    self.get_Vector(KT + 'WPT' + item)[KT + 'WPT' + item]) is np.ndarray:
                    # calculated WLPR if not available:
                    if self.is_Key(KT + 'LPT' + item) is False or len(
                            self.get_Vector(KT + 'LPT' + item)[KT + 'LPT' + item]) < len(
                            self.get_Vector(KT + 'WPT' + item)[KT + 'WPT' + item]) or type(
                            self.get_Vector(KT + 'LPT' + item)[KT + 'LPT' + item]) != np.ndarray:
                        try:
                            self.set_Vector(KT + 'LPT' + item,
                                            self.get_Vector(KT + 'OPT' + item)[KT + 'OPT' + item] + convertUnit(
                                                self.get_Vector(KT + 'WPT' + item)[KT + 'WPT' + item],
                                                self.get_Unit(
                                                    KT + 'WPT' + item),
                                                self.get_Unit(
                                                    KT + 'OPT' + item), PrintConversionPath=(self.speak == 1)),
                                            self.get_Unit(KT + 'OPT' + item), overwrite=True)
                        except:
                            try:
                                Name, Vector, Units = self.integrate(KT + 'LPR' + item, KT + 'LPT' + item)
                                self.set_Vector(Name, Vector, Units, 'float', True)
                                _verbose(self.speak, 2,
                                         'vector ' + KT + 'LPT' + item + ' integrated from ' + KT + 'LPR' + item + '.')
                            except:
                                _verbose(self.speak, 2, 'failed to create missing vector ' + KT + 'LPT' + item)
        np.seterr(divide=None, invalid=None)

    def check_vector_length(self, key_or_array):
        """
        returns True if the length of the given array or Key corresponds
        with the length of the simulation Keys.
        """
        if self.is_Key(self.get_TimeVector()):
            Vlen = len(self(self.get_TimeVector()))
        elif len(self.keys_) > 0:
            Vlen = len(self(self.keys_[0]))
        else:
            _verbose(self.speak, 3, 'there are no Keys in this object.')
            return True

        if self.is_Key(key_or_array):
            key_or_array = self(key_or_array)
        elif self.is_Attribute(key_or_array):
            key_or_array = self[[key_or_array]]

        if len(key_or_array) == Vlen:
            return True
        else:
            return False

    def arithmetic_vector(self, key):
        """
        returns a calculated vector if the required inputs exist.
        works with ECL keys only
        """
        key = key.strip()
        class_key = key.split(':')[0][0]
        calc_key = key.split(':')[0][1:]
        item_key = ''
        if ':' in key:
            item_key = ':' + key.split(':')[1]
        if calc_key in _dictionaries.calculations:
            ok = True
            for Req in _dictionaries.calculations[calc_key][::2]:
                if type(Req) is str:
                    if type(self.get_Vector(class_key + Req + item_key)[class_key + Req + item_key]) == np.ndarray:
                        # is a vector with values...
                        pass
                    else:
                        ok = False
                        break
                else:
                    #  should be int or float
                    pass
            if ok:
                for i in range(len(_dictionaries.calculations[calc_key])):
                    if i == 0:
                        # initialize CalculationTuple
                        if type(_dictionaries.calculations[calc_key][i]) is str:
                            CalculationTuple = [class_key + _dictionaries.calculations[calc_key][i] + item_key]
                        else:
                            CalculationTuple = [_dictionaries.calculations[calc_key][i]]
                    else:
                        if type(_dictionaries.calculations[calc_key][i]) is str:
                            CalculationTuple.append([class_key + _dictionaries.calculations[calc_key][i] + item_key])
                        else:
                            CalculationTuple.append([_dictionaries.calculations[calc_key][i]])
                return self.RPNcalculator(CalculationTuple, key)

    def RPNcalculator(self, calculation_tuple, result_name=None, result_units=None):
        """
        receives a tuple indicating the operation to perform and returns a vector
        with ResultName name

        The CalculationTuple is a sequence of Vectors or Floats and operators:
        The syntax of the CalculationTuple follows the Reverser Polish Notation (RPN)
            ('operand', 'operand', 'operator', 'operand', 'operator', ... 'operand', 'operator')

        The accepted operators are: '+', '-', '*', '/', '^'
        The CalculationTuple must start with a number or variable, never with an operator

        The operations will be executed in the exact order they are described. i.e.:
           ('FLPR', '=', 'FOPR', 'FWPR', '+')
                means FLPR = FOPR + FWPR
                will add FOPR plus FWPR
           ('WWCT:P1', '=', 'WOPR:P1', 'WLPR:P1', '/')
                means WWCT:P1 = WOPR:P1 / WLPR:P1
                will divide WOPR by WLPR of well P1
        but:
           ('R', '=', 'A', 'B', '-', 'C', '/')
                means R = (A - B) / C
                will add A plus B and the result will be divided by C

            to represent R = A - B / C the correct sintax would be:
           ('R', '=', '-B', 'C', '/', 'A', '+')
                that means R = -B / C + A

        Special operators can be used with Attributes or DataFrames:
            '.sum' will return the total of the all the columns at each tstep
            '.avg' or 'mean' will return the average of the all the columns at each tstep
            '.min' will return the minimum value of the all the columns at each tstep
            '.max' will return the maximum value of the all the columns at each tstep
            '.mode' will return the mode value of the all the columns at each tstep
            '.prod' will return the product value of the all the columns at each tstep
            '.var' will return the variance value of the all the columns at each tstep
            '.std' will return the stardard deviation the all the columns at each tstep

        To ignore 0 in these calculation, the variant of the operator
        with a '0' sufix can be used. i.e.:
            '.sum0', '.avg0', '.mean0', '.min0', '.max0', '.std0'

            '.avg0' or '.mean0' will return the average of the all the columns
            but ignoring the zeros in the data

        """
        if not self.useSimPandas:
            raise MissingDependence(
                'simPandas is required to interpret calculation strings.\n Activate simPandas .use_SimPandas()')
        CalcData, CalcUnits, i, firstNeg = [], [], 0, False

        def _getValues(Key):
            if len(self.find_Keys(Key)) == 0:
                if Key[0] == '-':
                    if self.find_Keys(Key[1:]):
                        CalcData.append(self(Key[1:]) * -1)
                        CalcUnits.append(self.get_Unit(Key[1:]))
            elif self.is_Key(Key):
                CalcData.append(self[[Key]])
                CalcUnits.append(self.get_Unit(Key))
            elif self.is_Attribute(Key):
                CalcData.append(self[[Key]])
                CalcUnits.append(self.get_Unit(Key))
            elif len(self.find_Keys(Key)) == 1:
                CalcData.append(self[Key])
                CalcUnits.append(self.get_Unit(Key))
            elif len(self.find_Keys(Key)) > 1:
                CalcData.append(self[[Key]])
                CalcUnits.append(self.get_Unit(Key))
            else:  # len(self.find_Keys(Key)) > 1:
                CalcData.append(self[[Key]])
                CalcUnits.append(self.get_Unit(Key))

        # supported operators:
        operators = [' ', '**', '--', '+-', '-+', '++', '*-', '/-', '//', '=', '+', '*', '/', '^', '.abs', '.sum',
                     '.avg', '.mean', '.median', '.min', '.max', '.mode', '.prod', '.var', '.std', '.sum0', '.avg0',
                     '.mean0', '.median0', '.min0', '.max0', '.std0', '.mode0', '.prod0', '.var0', '>', '<', '>=', '<=',
                     '!=', '==', '<>', '><', '=>', '=<']
        if '-' in (' '.join(map(str, self.wells)) + ' '.join(map(str, self.groups)) + ' '.join(map(str, self.regions))):
            substractionSign = ' -'
        else:
            substractionSign = '-'
        operators.append(substractionSign)

        # convert string to calculation tuple
        if type(calculation_tuple) is str:
            _verbose(self.speak, 1,
                     ' the received string for CalculatedTuple was converted to tuple, \n  received: ' + calculation_tuple + '\n  converted to: ' + str(
                         tuple(_multisplit(calculation_tuple, operators))))
            calculation_tuple = tuple(_multisplit(' ' + calculation_tuple + ' ', operators))
        elif type(calculation_tuple) is list:
            calculation_tuple = tuple(calculation_tuple)
        if result_name is None:
            if calculation_tuple[1] == '=':
                result_name = calculation_tuple[0]
                _verbose(self.speak, 1, "found Key name '" + result_name + "'")
                calculation_tuple = calculation_tuple[2:]
            else:
                result_name = str(calculation_tuple)

        # simplify equation
        calculation_tuple = list(calculation_tuple)
        while '--' in calculation_tuple:
            where = calculation_tuple.index('--')
            calculation_tuple[where] = '+'
        while '+-' in calculation_tuple:
            where = calculation_tuple.index('+-')
            calculation_tuple[where] = '-'
        while '-+' in calculation_tuple:
            where = calculation_tuple.index('-+')
            calculation_tuple[where] = '-'
        while '++' in calculation_tuple:
            where = calculation_tuple.index('++')
            calculation_tuple[where] = '+'
        while '**' in calculation_tuple:
            where = calculation_tuple.index('**')
            calculation_tuple[where] = '^'
        while '*-' in calculation_tuple:
            where = calculation_tuple.index('*-')
            calculation_tuple[where] = '*'
            if (where + 2) <= len(calculation_tuple):
                calculation_tuple = calculation_tuple[:where] + [calculation_tuple[where]] + [
                    '-' + calculation_tuple[where + 1]] + calculation_tuple[where + 2:]
            elif (where + 1) <= len(calculation_tuple):
                calculation_tuple = calculation_tuple[:where] + [calculation_tuple[where]] + [
                    '-' + calculation_tuple[where + 1]]
        while '/-' in calculation_tuple:
            where = calculation_tuple.index('/-')
            calculation_tuple[where] = '/'
            if (where + 2) <= len(calculation_tuple):
                calculation_tuple = calculation_tuple[:where] + [calculation_tuple[where]] + [
                    '-' + calculation_tuple[where + 1]] + calculation_tuple[where + 2:]
            elif (where + 1) <= len(calculation_tuple):
                calculation_tuple = calculation_tuple[:where] + [calculation_tuple[where]] + [
                    '-' + calculation_tuple[where + 1]]
        for notequal in ('><', '<>'):
            while notequal in calculation_tuple:
                where = calculation_tuple.index(notequal)
                calculation_tuple[where] = '!='
        while '=>' in calculation_tuple:
            where = calculation_tuple.index('=>')
            calculation_tuple[where] = '>='
        while '=<' in calculation_tuple:
            where = calculation_tuple.index('=<')
            calculation_tuple[where] = '<='

        while calculation_tuple[0] in ['-', ' -']:
            if len(calculation_tuple) > 2:
                calculation_tuple = ['-' + calculation_tuple[1]] + calculation_tuple[2:]
            else:
                calculation_tuple = ['-' + calculation_tuple[1]]

        while calculation_tuple[0] in ['*', '+', '/', '**', '//']:
            _verbose(self.speak, 2, "the first item '" + calculation_tuple.pop(0) + "' is an operand and will ignored")

        # convert numbers to float or int
        for i in range(len(calculation_tuple)):
            if _isnumeric(calculation_tuple[i]):
                calculation_tuple[i] = _getnumber(calculation_tuple[i])

        calculation_tuple = tuple(calculation_tuple)
        _verbose(self.speak, 1, "calculation simplified to " + str(calculation_tuple))

        operators = [substractionSign] + ['+', '*', '//', '/', '^', '.abs', '.sum', '.avg', '.mean', '.median', '.min',
                                          '.max', '.mode', '.prod', '.std', '.var', '.sum0', '.avg0', '.mean0',
                                          '.median0', '.min0', '.max0', '.mode0', '.prod0', '.std0', '.var0', '>', '<',
                                          '>=', '<=', '!=']
        OK = True
        Missing = []
        WrongLen = []
        for Req in calculation_tuple:
            if type(Req) is str:
                if Req in operators:
                    # is an operand ... OK
                    pass
                elif len(self.find_Keys(Req)) > 0:
                    # is a vector or table with values... OK
                    for R in self.find_Keys(Req):
                        if not self.check_vector_length(R):
                            WrongLen.append(R)
                            OK = False
                elif Req[0] == '-' and Req != '-':
                    Req = Req[1:]
                    if len(self.find_Keys(Req)) > 0:
                        # is a vector or table with values... OK
                        for R in self.find_Keys(Req):
                            if not self.check_vector_length(R):
                                WrongLen.append(R)
                                OK = False
                else:
                    OK = False
                    Missing.append(Req)
            elif type(Req) in [int, float]:
                # is an int or float
                pass
            elif type(Req) is np.ndarray:
                if not self.check_vector_length(Req):
                    WrongLen.append(str(Req))
                    OK = False

        if not OK:
            if len(Missing) > 0:
                _verbose(self.speak, 3,
                         '\n IMPORTANT: the following required input vectors were not found:\n   -> ' + '\n   -> '.join(
                             Missing) + '\n')
            if len(WrongLen) > 0:
                _verbose(self.speak, 3,
                         '\n IMPORTANT: the following input vectors does not have the correct length:\n   -> ' + '\n   -> '.join(
                             WrongLen) + '\n')
            return {result_name: None}

        # prepare the data
        i = 0
        while i < len(calculation_tuple):

            # a string Key, must be interpreted
            if type(calculation_tuple[i]) is str and calculation_tuple[i] not in operators:
                _getValues(calculation_tuple[i])

            # string operator
            elif type(calculation_tuple[i]) is str and calculation_tuple[i] in operators:
                if i == 0 and calculation_tuple[i].strip() == '-':
                    CalcData.append(-1)
                    CalcUnits.append(None)
                    firstNeg = True
                else:
                    CalcData.append(calculation_tuple[i])
                    CalcUnits.append(None)

            # something else, a number, array or table
            else:
                CalcData.append(calculation_tuple[i])
                CalcUnits.append(None)

            if i == 1 and firstNeg:
                CalcData.append('*')
                CalcUnits.append(None)

            i += 1

        # initialize calculation with first item
        Stack = []
        # StackUnits = []
        for i in range(len(CalcData)):
            # following the operations sequence

            if type(CalcData[i]) is str and CalcData[i] not in operators:
                Stack.append(CalcData[i])
                # StackUnits.append(CalcUnits[i])
                continue
            elif type(CalcData[i]) is not str:
                Stack.append(CalcData[i])
                # StackUnits.append(CalcUnits[i])
                continue

            else:
                if len(Stack) >= 2:
                    operandB = Stack.pop()
                    operandA = Stack.pop()
                elif len(Stack) == 1:
                    operandB = Stack.pop()
                    operandA = 0
                else:
                    operandB = 0
                    operandA = 0

                if type(operandA) is SimDataFrame and len(operandA.columns) == 1:
                    operandA = operandA.to_SimSeries()
                if type(operandB) is SimDataFrame and len(operandB.columns) == 1:
                    operandB = operandB.to_SimSeries()

                if calculation_tuple[i] == substractionSign:  # '-' or ' -'
                    Stack.append(operandA - operandB)
                elif calculation_tuple[i] == '+':
                    Stack.append(operandA + operandB)
                elif calculation_tuple[i] == '*':
                    Stack.append(operandA * operandB)
                elif calculation_tuple[i] == '/':
                    Stack.append(operandA / operandB)
                elif calculation_tuple[i] == '//':
                    Stack.append(operandA // operandB)
                elif calculation_tuple[i] == '^':
                    Stack.append(operandA ** operandB)
                elif calculation_tuple[i] == '>':
                    Stack.append(operandA > operandB)
                elif calculation_tuple[i] == '<':
                    Stack.append(operandA < operandB)
                elif calculation_tuple[i] == '>=':
                    Stack.append(operandA >= operandB)
                elif calculation_tuple[i] == '<=':
                    Stack.append(operandA <= operandB)
                elif calculation_tuple[i] == '!=':
                    Stack.append(operandA != operandB)
                elif calculation_tuple[i] == '==':
                    Stack.append(operandA == operandB)
                elif calculation_tuple[i] in ['.sum', '.avg', '.mean', '.min', '.max', '.mode', '.prod', '.std', '.var',
                                              '.sum0', '.avg0', '.mean0', '.min0', '.max0', '.mode0', '.prod0', '.std0',
                                              '.var0']:
                    if isinstance(operandB, (DataFrame, Series)):
                        Stack.append(operandA)

                        if calculation_tuple[i].endswith('0'):
                            operandB.replace(0, np.nan, inplace=True)  # ignore zeros in the data

                        if calculation_tuple[i] in ['.sum', '.sum0']:
                            Stack.append(operandB.sum(axis=1))
                        elif calculation_tuple[i] in ['.avg', '.mean', '.avg0', '.mean0']:
                            Stack.append(operandB.mean(axis=1))
                        elif calculation_tuple[i] in ['.median', '.median0']:
                            Stack.append(operandB.median(axis=1))
                        elif calculation_tuple[i] in ['.min', '.min0']:
                            Stack.append(operandB.min(axis=1))
                        elif calculation_tuple[i] in ['.max', '.max0']:
                            Stack.append(operandB.max(axis=1))
                        elif calculation_tuple[i] in ['.mode', '.mode0']:
                            Stack.append(operandB.mode(axis=1))
                        elif calculation_tuple[i] in ['.std', '.std0']:
                            Stack.append(operandB.std(axis=1))
                        elif calculation_tuple[i] in ['.prod', '.prod0']:
                            Stack.append(operandB.prod(axis=1))
                        elif calculation_tuple[i] in ['.var', '.var0']:
                            Stack.append(operandB.var(axis=1))
                        elif calculation_tuple[i] in ['.abs']:
                            Stack.append(operandB.abs())

                        if calculation_tuple[i].endswith('0'):
                            Stack[-1].replace(np.nan, 0, inplace=True)  # replace NaN by zeros in the data

        Result = Stack[-1]
        if isinstance(Result, SimDataFrame) and len(Result.columns) == 1:
            Result = Result.to_SimSeries()
        print(Result)
        # save the result
        self.set_Vector(str(calculation_tuple), Result, Result.get_units(), 'auto', True)

        # if a name was given, link the data to the new name
        if result_name != str(calculation_tuple):
            if isinstance(Result, Series) or (isinstance(Result, DataFrame) and len(Result.columns) == 1):
                if str(calculation_tuple) in self.vectors:
                    self.vectors[result_name] = self.vectors[str(calculation_tuple)]
                    self.units[result_name] = self.units[str(calculation_tuple)]
                else:
                    item = ':' + str(list(Result.columns)[0].split(':')[-1])
                    if str(calculation_tuple) + item in self.vectors:
                        self.vectors[result_name] = self.vectors[str(calculation_tuple) + item]
                        self.units[result_name] = self.units[str(calculation_tuple) + item]
                    else:
                        self.set_Vector(result_name, Result.to_numpy(), Result.get_UnitsString(), 'auto', True)
                if not self.is_Key(result_name):
                    self.add_Key(result_name)
            elif isinstance(Result, DataFrame):
                for each in Result.columns:
                    item = ':' + str(each.split(':')[-1])
                    self.vectors[result_name + item] = self.vectors[str(calculation_tuple) + item]
                    self.units[result_name + item] = self.units[str(calculation_tuple) + item]
                    if not self.is_Key(result_name + item):
                        self.add_Key(result_name + item)
            self.get_Attributes(reload=True)
            return None
        else:
            return Result

    def createDATES(self):
        if self.is_Key('DATE') and not self.is_Key('DATES'):
            DATE = self.get_Vector('DATE')['DATE']
            self.set_Vector('DATES', DATE, 'DATE')
        elif self.is_Key('DATES') and not self.is_Key('DATE'):
            DATE = self.get_Vector('DATES')['DATES']
            self.set_Vector('DATE', DATE, 'DATE')
        elif self.is_Key('TIME') is True and self.start is not None:
            TIME = self.get_Vector('TIME')['TIME']
            start = self.start
            DATE = np.empty(len(TIME), dtype='datetime64[s]')
            for i in range(len(TIME)):
                DATE[i] = start + np.timedelta64(timedelta(days=TIME[i]))
            self.set_Vector('DATES', DATE, 'DATE', overwrite=True)
            self.set_Vector('DATE', DATE, 'DATE', overwrite=True)
        elif self.is_Key('YEAR') is True and self.is_Key('MONTH') is True and self.is_Key('DAY') is True:
            YEAR = self.get_Vector('YEAR')['YEAR']
            MONTH = self.get_Vector('MONTH')['MONTH']
            DAY = self.get_Vector('DAY')['DAY']
            tupleDate = lambda d: str(d).strip('()').replace(', ', '-')
            DATE = _strDate(list(map(tupleDate, zip(YEAR, MONTH, DAY))), formatIN='YYYY-MM-DD', formatOUT='DD-MMM-YYYY')
            self.set_Start(DATE[0])
            DATE = np.array(pd.to_datetime(DATE), dtype='datetime64[s]')
            self.set_Vector('DATES', DATE, 'DATE', overwrite=True)
            self.set_Vector('DATE', DATE, 'DATE', overwrite=True)
        if self.is_Key('DATE'):
            if not self.is_Key('DATES'):
                DATE = self.get_Vector('DATE')['DATE']
                self.set_Vector('DATES', DATE, 'DATE')
        if self.is_Key('DATES'):
            if not self.is_Key('DATE'):
                DATE = self.get_Vector('DATES')['DATES']
                self.set_Vector('DATE', DATE, 'DATE')
        else:
            _verbose(self.speak, 3, "Not possible to create 'DATE' key, the requiered data is not available")
            return False

    def createYEAR(self):
        if self.is_Key('DATE'):
            Years = list(pd.to_datetime(self.get_Vector('DATE')['DATE']).year)
            self.set_Vector('YEAR', Years, 'Year', data_type='int', overwrite=True)
        else:
            _verbose(self.speak, 3, "Not possible to create 'YEAR' key, the requiered data is not available")
            return False

    def createMONTH(self):
        if self.is_Key('DATE'):
            Months = list(pd.to_datetime(self.get_Vector('DATE')['DATE']).month)
            self.set_Vector('MONTH', Months, 'Month', data_type='int', overwrite=True)
        else:
            _verbose(self.speak, 3, "Not possible to create 'MONTH' key, the requiered data is not available")
            return False

    def createDAY(self):
        if self.is_Key('DATE'):
            Days = list(pd.to_datetime(self.get_Vector('DATE')['DATE']).day)
            self.set_Vector('DAY', Days, 'Day', data_type='int', overwrite=True)
        else:
            _verbose(self.speak, 3, "Not possible to create 'DAY' key, the requiered data is not available")
            return False

    def createTIME(self, start_date=None):
        if self.is_Key('DATE'):
            date = self('DATE')
        elif self.is_Key('DATES'):
            date = self('DATES')
        else:
            catch = self.createDATES()
            if catch is None:
                date = self('DATES')
            else:
                date = None
        if date is None:
            return False
        else:
            if startDate is None:
                startDate = min(date)
            else:
                import datetime as dt
                if type(startDate) is str:
                    try:
                        startDate = np.datetime64(pd.to_datetime(startDate))
                    except:
                        raise ValueError(" string date not understood: '" + startDate + "'")
                elif isinstance(startDate, pd._libs.tslibs.timestamps.Timestamp):
                    startDate = np.datetime64(startDate)
                elif isinstance(startDate, dt.datetime):
                    startDate = np.datetime64(startDate)
                elif type(startDate) is np.datetime64:
                    pass  # ok
                else:
                    raise TypeError(" not recognized startDate paramenter", startDate)

            time = (pd.to_timedelta(date - startDate).astype('timedelta64[s]') / 60 / 60 / 24).to_numpy()
            ow = self.overwrite
            self.overwrite = True
            self.set_Vector('TIME', time, 'DAYS', data_type='float', overwrite=True)
            self.set_Unit('TIME', 'DAYS', overwrite=True)
            self.set_FieldTime()
            self.overwrite = ow

    def get_UnitsConverted(self, key=None, OtherObject_or_NewUnits=None):
        """
        returns a vector converted from the unit system of this object
        to the units of the corresponding vector on the other SimResult object
        or to the indicated units as string or Unit object.

        If Key is defaulted an empty dictionary will be returned
        If Other_Object_or_Units is set to None or defautl no conversion
        will be applied. It is equivalent to get_Vector() method.

        """
        # checking input parameters
        if type(key) is str:
            key = [key]
        elif type(key) is list or type(key) is tuple:
            pass
        if key is None:
            return {}
        if OtherObject_or_NewUnits is None:
            return self.get_Vector(key, False)

        ListOfUnits = False
        if type(OtherObject_or_NewUnits) is str:
            OtherObject_or_NewUnits = [OtherObject_or_NewUnits]
            ListOfUnits = True
        elif type(OtherObject_or_NewUnits) is list or type(OtherObject_or_NewUnits) is tuple:
            ListOfUnits = True

        if ListOfUnits is True and len(key) != len(OtherObject_or_NewUnits):
            raise TypeError(str(len(key)) + ' resquested but ' + str(
                len(OtherObject_or_NewUnits)) + ' units provided.\n          Both should match order and number.')
        elif ListOfUnits is True and len(key) == len(OtherObject_or_NewUnits):
            pass
        else:
            try:
                if OtherObject_or_NewUnits.SimResult is True:
                    errors = False
                    TempConversions = []
                    for each in key:
                        if not OtherObject_or_NewUnits.is_Key(each):
                            errors = True
                            _verbose(self.speak, 3,
                                     'The requested Key ' + str(each) + ' is not present in the simulation ' + str(
                                         OtherObject_or_NewUnits.get_Name()) + '.')
                        else:
                            TempConversions.append(OtherObject_or_NewUnits.get_Unit(each.strip()))
                    if errors:
                        raise TypeError('at least one requested Key is not present in the simulation ' + str(
                            OtherObject_or_NewUnits.get_Name()) + '.')
                    # OtherObject = OtherObject_or_NewUnits
                    OtherObject_or_NewUnits = TempConversions
                    TempConversions = None
                else:
                    raise TypeError('Other_Object_or_Units must be string, a list of strings or a SimResult object.')
            except:
                raise TypeError('Other_Object_or_Units must be string, a list of strings or a SimResult object.')

        # extracting and converting the selected Keys
        ConvertedDict = {}
        for each in range(len(key)):
            ConvertedDict[key[each]] = convertUnit(self.get_Vector(key[each])[key[each].strip()],
                                                   self.get_Unit(key[each]), OtherObject_or_NewUnits[each],
                                                   PrintConversionPath=(self.speak == 1))
        return ConvertedDict

    def integrate(self, input_key, output_key=None, constant_rate=False, numpy=True, overwrite=None, save_others=False,
                  time_vector=None):
        """"
        calculate the integral, or cumulative, of the input vector and saves
        it to the output vector.

        if ConstantRate = True:
            cumulative[i] = cumulative[i-1] + Time[i] * InputKey[i]
        if ConstantRate = False:
            cumulative[i] = cumulative[i-1] + Time[i] * (min(InputKey[i], InputKey[i+1]) + Time[i] * (max(InputKey[i], InputKey[i+1]) - min(InputKey[i], InputKey[i+1]))

        Set Numpy=False to not use Numpy, the calculation will be done using a for loop
        """
        if type(input_key) is not str or (type(output_key) is not None and type(output_key) is not str):
            raise TypeError(' InputKey and OutputKey must be strings.')
        if not self.is_Key(input_key):
            if not self.is_Attribute(input_key):
                _verbose(self.speak, 2, "<integrate> the requiered Key '" + input_key + "' is not a valid Key")
                return None
            else:
                if type(output_key) is str:
                    for eachKey in self.attributes[input_key]:
                        eachOut = _mainKey(output_key) + ':' + _itemKey(eachKey)
                        self.integrate(eachKey, eachOut)
                else:
                    for eachKey in self.attributes[input_key]:
                        self.integrate(eachKey, output_key)
                return None
        Vector = self.get_Vector(input_key)[input_key]
        if Vector is None:
            _verbose(self.speak, 2, "<integrate> the vector Key '" + input_key + "' is empty")
            return None
        VectorUnits = self.get_Unit(input_key)
        _verbose(self.speak, 1,
                 "<integrate> retrieved series '" + input_key + "' of length " + str(len(Vector)) + ' and units ' + str(
                     VectorUnits))

        if time_vector is not None:
            if self.is_Key(time_vector):
                _verbose(self.speak, 2, "<interpolate> using vector '" + time_vector + "' to interpolate")
            else:
                _verbose(self.speak, 2,
                         "<interpolate> the provided Key '" + time_vector + "' is not present in this simulation")
        else:
            for TimeKey in ['TIME', 'DATE', 'DATES', 'DAYS', 'MONTHS', 'YEARS']:
                if self.is_Key(TimeKey):
                    break
        Time = self.get_Vector(TimeKey)[TimeKey]
        TimeUnits = self.get_Unit(TimeKey)
        _verbose(self.speak, 1,
                 "<integrate> retrieved series '" + TimeKey + "' of length " + str(len(Time)) + ' and units ' + str(
                     TimeUnits))
        if TimeKey in ['DATE', 'DATES']:
            TimeUnits = 'DAYS'

        numpy = bool(numpy)
        constant_rate = bool(constant_rate)
        if overwrite is None:
            overwrite = self.overwrite

        OutUnits = ''
        if '/' in VectorUnits:
            VectorSubUnits = {}
            for i in range(len(VectorUnits.split('/'))):
                VectorSubUnits[i] = VectorUnits.split('/')[i]
            if TimeUnits in VectorSubUnits:
                OutUnits = []
                ConvFactor = 1
                for i in range(len(VectorSubUnits)):
                    if VectorSubUnits[i] == TimeUnits:
                        if i == 0:
                            OutUnits.append(VectorSubUnits[i] + '*' + VectorSubUnits[i])
                        else:
                            pass
                    else:
                        OutUnits.append(VectorSubUnits[i])
            else:
                OutUnits = []
                ConvFactor = 1
                for i in range(len(VectorSubUnits)):
                    _verbose(self.speak, 1,
                             "<integrate> converting " + str(TimeUnits) + ' to ' + str(VectorSubUnits[i]))
                    if convertibleUnits(VectorSubUnits[i], TimeUnits):
                        ConvFactor = ConvFactor * convertUnit(1, TimeUnits, VectorSubUnits[i],
                                                              PrintConversionPath=(self.speak == 1))
                        _verbose(self.speak, 1, "<integrate> conversion factor: 1 " + str(TimeUnits) + ' = ' + str(
                            ConvFactor) + ' ' + str(VectorSubUnits[i]))
                    else:
                        OutUnits.append(VectorSubUnits[i])
                        _verbose(self.speak, 1, "<integrate> not convertible")

            OutUnits = '/'.join(OutUnits)
        else:
            OutUnits = VectorUnits + '*' + TimeUnits
            ConvFactor = 1

        _verbose(self.speak, 1, "<integrate> integrated series units will be " + str(OutUnits))

        if len(Vector) != len(Time):
            raise TypeError(' the Key vector ' + input_key + ' and its TIME does not have the same length: ' + str(
                len(Vector)) + ' != ' + str(len(Time)) + '.')

        if not numpy:
            # integrating one row at a time, iterating with for:
            _verbose(self.speak, 2, "<integrate> calculating integral for key '" + input_key + "' using for loop")
            Cumulative = [0.0]
            if not constant_rate:
                for i in range(len(Vector) - 1):
                    dt = (Time[i + 1] - Time[i])
                    if TimeKey in ['DATE', 'DATES']:
                        dt = dt.astype('timedelta64[s]').astype('float64') / 60 / 60 / 24
                    dt = dt * ConvFactor
                    if Vector[i] <= Vector[i + 1]:
                        Vmin = Vector[i]
                        Vmax = Vector[i + 1]
                    else:
                        Vmin = Vector[i + 1]
                        Vmax = Vector[i]
                    Cumulative.append(Cumulative[i - 1] + dt * Vmin + dt * (Vmax - Vmin) / 2.0)
            else:
                for i in range(len(Vector) - 1):
                    Cumulative.append(Cumulative[i - 1] + dt * Vector[i])

        else:
            # integrating numpy method:
            _verbose(self.speak, 2, "<integrate> calculating integral for key '" + input_key + "' using numpy methods")
            for X in (Time, Vector):
                if type(X) != np.ndarray:
                    if type(X) is list or type(X) is tuple:
                        try:
                            X = np.array(X, dtype='float')
                        except:
                            print(" the key '" + X + "' is not numpy array.")

            dt = np.diff(Time) * ConvFactor

            if TimeKey in ['DATE', 'DATES']:
                dt = dt.astype('timedelta64[D]').astype('float64')

            if not constant_rate:
                Vmin = np.minimum(Vector[:-1], Vector[1:])
                Vmax = np.maximum(Vector[:-1], Vector[1:])
                Cumulative = dt * Vmin + dt * (Vmax - Vmin) / 2.0
            else:
                Cumulative = dt * Vector[:-1]

            Cumulative = [0.0] + list(Cumulative)
            Cumulative = np.array(Cumulative, dtype='float')
            Cumulative = np.cumsum(Cumulative)

        try:
            self.set_Vector(output_key, np.array(Cumulative), OutUnits, overwrite=overwrite)
            # if len(self.restarts) == 0 and len(self.continuations) == 0:
            #     self.set_Vector(OutputKey, np.array(Cumulative), OutUnits, overwrite=overwrite)
            # elif len(self.restarts) > 0 and len(self.continuations) == 0:
            #     # self.set_Vector(OutputKey, np.array(Cumulative[-len(self.get_RawVector(InputKey)[InputKey]):]), OutUnits, overwrite=overwrite)
            #     self.set_Vector(OutputKey, np.array(Cumulative), OutUnits, overwrite=overwrite)
            #     if saveOthers:
            #         for other in self.restarts:
            #             if other.is_Key(InputKey):
            #                 # previuosRestarts = other.restarts
            #                 # other.clean_Restart()
            #                 # other.set_Restart(self.restarts)
            #                 other.integrate(InputKey, OutputKey=OutputKey, ConstantRate=ConstantRate, Numpy=Numpy, overwrite=overwrite, saveOthers=False)
            #                 # other.restarts = previuosRestarts
            # elif len(self.restarts) == 0 and len(self.continuations) > 0:
            #     # self.set_Vector(OutputKey, np.array(Cumulative[-len(self.get_RawVector(InputKey)[InputKey]):]), OutUnits, overwrite=overwrite)
            #     self.set_Vector(OutputKey, np.array(Cumulative), OutUnits, overwrite=overwrite)
            #     if saveOthers:
            #         i = -1
            #         for other in self.continuations:
            #             i += 1
            #             if other.is_Key(InputKey):
            #                 otherRestarts = other.restarts
            #                 other.restarts = [self] + self.continuations[:i] # not sure will work if continuation point is not the last point
            #                 other.integrate(InputKey, OutputKey=OutputKey, ConstantRate=ConstantRate, Numpy=Numpy, overwrite=overwrite, saveOthers=False)
            #                 other.restarts = otherRestarts
            # elif len(self.restarts) > 0 and len(self.continuations) > 0:
            #     self.set_Vector(OutputKey, np.array(Cumulative), OutUnits, overwrite=overwrite)
            #     # _verbose(self.speak, 2, 'not able to save vector because the case has both restarts and continuations.')

        except OverwritingError:
            _verbose(self.speak, 2, 'not able to save vector because the Key already exists.')
        return (output_key, np.array(Cumulative), OutUnits)

    def get_DataFrame(self, keys=None, index='TIME'):
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
        if type(keys) is str:
            if keys == '--EVERYTHING--':
                keys = list(self.get_keys())
            else:
                keys = [keys]
        if type(index) is list or type(index) is tuple:
            if len(index) > 1:
                _verbose(self.speak, -1,
                         '< get_DataFrame > more than value passed in Index argument, only the first one will be used')
            index = index[0]
        return DataFrame(data=self.get_Vector(keys), index=self.get_Vector(index)[index])[keys]

    def get_ConvertedDataFrame(self, keys=None, index='TIME', OtherObject_or_NewUnits=None):
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
        if type(keys) is str:
            if keys == '--EVERYTHING--':
                keys = list(self.get_keys())
            else:
                keys = [keys]
        if type(index) is list or type(index) is tuple:
            if len(index) > 1:
                _verbose(self.speak, -1,
                         '< get_DataFrame > more than value passed in Index argument, only the first one will be used')
            index = index[0]
        elif type(index) is str:
            pass
        else:
            try:
                if index.SimResult is True:
                    if OtherObject_or_NewUnits is None:
                        OtherObject_or_NewUnits = index
                        index = 'TIME'
            except:
                pass

        if index not in keys:
            DF = self.get_UnitsConverted([index] + keys, OtherObject_or_NewUnits)
            DF = DataFrame(data=DF, index=DF[index])
        else:
            DF = self.get_UnitsConverted(keys, OtherObject_or_NewUnits)
            DF = DataFrame(data=DF, index=DF[index])
        return DF

    # def save(self, FileNamePath):
    #     Ext, fileName, Folder, FullPath = _extension(FileNamePath)
    #     # create the folders structure:
    #     try:
    #         os.mkdir(Folder + fileName + '_storage')
    #     except:
    #         print(' folder already exists')
    #     try:
    #         os.mkdir(Folder + fileName + '_storage' + '/parquet')
    #     except:
    #         print(' parquet already exists')
    #     try:
    #         os.mkdir(Folder + fileName + '_storage' + '/raw')
    #     except:
    #         print(' raw already exists')
    #     try:
    #         os.mkdir(Folder + fileName + '_storage' + '/json')
    #     except:
    #         print(' raw already exists')

    #     txtfile = 'SimResult =:= ' + str(self.SimResult) + '\n'
    #     txtfile = txtfile + 'kind =:= ' + str(self.kind) + '\n'

    #     if self.kind == ECL:
    #         pass
    #     elif self.kind == VIP:
    #         count = 0
    #         if len(self.results) == 0 and self.CSV != False:
    #             self.CSVgenerateResults()

    #         resultstxt = ''
    #         for each in list(self.results.keys()):
    #             DF_raw = DataFrame(self.results[each][1]['Data'])
    #             if 'TIME' in DF_raw.columns:
    #                 DF_raw.set_index('TIME', drop=False, inplace=True)
    #             DF_raw.to_parquet(Folder + fileName + '_storage/raw/' + str(count) + '_rawdata.sro', index=True)
    #             with open(Folder + fileName + '_storage/raw/' + str(count) + '_rawunits.sro', 'w') as file:
    #                 file.write(json.dumps(self.results[each][1]['Units']))
    #             resultstxt = resultstxt + str(count) + ' =:= ' + str(each) + ' =:= ' + self.results[each][0] + ' \n'

    #         with open(Folder + fileName + '_storage/raw/keys.sro', 'w') as file:
    #             file.write(resultstxt)

    #     if self.name is None:
    #         txtfile = txtfile + 'name =:= ' + '=@:None:@=' + '\n'
    #     else:
    #         txtfile = txtfile + 'name =:= ' + str(self.name) + '\n'
    #     txtfile = txtfile + 'path =:= ' + str(self.path) + '\n'
    #     txtfile = txtfile + 'start =:= ' + str(self.start) + '\n'
    #     txtfile = txtfile + 'end =:= ' + str(self.end) + '\n'
    #     txtfile = txtfile + 'wells =:= ' + str(self.wells) + '\n'
    #     txtfile = txtfile + 'groups =:= ' + str(self.groups) + '\n'
    #     txtfile = txtfile + 'regions =:= ' + str(self.regions) + '\n'
    #     txtfile = txtfile + 'keys =:= ' + str(self.keys_) + '\n'

    #     # dump attributes dictionary to JSON file
    #     with open(Folder + fileName + '_storage/json/attributes.sro', 'w') as file:
    #         try:
    #             file.write(json.dumps(self.attributes))
    #         except:
    #             file.write(str(self.attributes))

    #     # prepare vectors as dataframe and dump to parquet
    #     DF_vectors = DataFrame(self.vectors)
    #     DF_vectors.set_index('TIME', drop=False, inplace=True)
    #     DF_vectors.to_parquet(Folder + fileName + '_storage/parquet/vectors.sro', index=True)

    #     # dump units dictionary to JSON file
    #     with open(Folder + fileName + '_storage/json/units.sro', 'w') as file:
    #         file.write(json.dumps(self.units))

    #     txtfile = txtfile + 'overwrite =:= ' + str(self.overwrite) + '\n'
    #     txtfile = txtfile + 'null =:= ' + str(self.null) + '\n'
    #     txtfile = txtfile + 'color =:= ' + str(self.color) + '\n'
    #     txtfile = txtfile + 'restarts =:= ' + str(self.restarts) + '\n'

    #     # prepare restart vectors as dataframe and dump to parquet
    #     if len(self.vectorsRestart) > 0:
    #         DF_vectors = DataFrame(self.vectorsRestart)
    #         DF_vectors.to_parquet(Folder + fileName + '_storage/parquet/restarts.sro', index=True)

    #     # txtfile = txtfile + 'pandasColumns =:= ' + str(self.pandasColumns) + '\n'
    #     if self.fieldtime == (None, None, None):
    #         txtfile = txtfile + 'fieldtime =:= ' + str(self.fieldtime) + '\n'
    #     else:
    #         txtfile = txtfile + 'fieldtime =:= ' + str(self.fieldtime[0]) + ' =:= ' + str(self.fieldtime[1]) + ' =:= ' + str(list(self.fieldtime[2])) + '\n'

    #     if self.kind == VIP:
    #         txtfile = txtfile + 'ECLstyle =:= ' + str(self.ECLstyle) + '\n'
    #         txtfile = txtfile + 'VIPstyle =:= ' + str(self.VIPstyle) + '\n'
    #         txtfile = txtfile + 'keysECL =:= ' + str(self.keysECL) + '\n'
    #         txtfile = txtfile + 'keysVIP =:= ' + str(self.keysVIP) + '\n'
    #         txtfile = txtfile + 'keysCSV =:= ' + str(self.keysCSV) + '\n'
    #         if self.CSV is False:
    #             txtfile = txtfile + 'CSV =:= ' + str(False) + '\n'
    #         else:
    #             txtfile = txtfile + 'CSV =:= ' + str(True) + '\n'
    #         txtfile = txtfile + 'LPGcorrected =:= ' + str(self.LPGcorrected) + '\n'

    #     # dump __init__ data to TXT file
    #     with open(Folder + fileName + '_storage/init.sro', 'w') as file:
    #         file.write(txtfile)
    #     with open(Folder + fileName + '.sro', 'w') as file:
    #         file.write(txtfile)

    # def restore(self, FileNamePath):
    #     Ext, fileName, Folder, FullPath = _extension(FileNamePath)

    #     RestorePath = Folder + fileName + '_storage/'
    #     try:
    #         file = open(RestorePath+'init.sro', 'r')
    #     except:
    #         print(" the file " + FileNamePath +  "doesn't 'exist")
    #         return None

    #     txtfile = file.readlines()

    #     for line in txtfile:
    #         print(' reading: ' + line)
    #         key = line.split(' =:= ')[0]

    #         print('reading ', key, line.split(' =:= ')[1])
    #         if key == 'SimResult':
    #             self.SimResult = bool(line.split(' =:= ')[1])
    #         elif key == 'kind':
    #             if 'ECL' in line.split(' =:= ')[1]:
    #                 self.kind = ECL
    #             elif 'VIP' in line.split(' =:= ')[1]:
    #                 self.kind = VIP
    #         elif key == 'name':
    #             if line.split(' =:= ')[1] == '=@:None:@=':
    #                 self.name = None
    #             else:
    #                 self.name = line.split(' =:= ')[1]
    #         elif key == 'path':
    #             self.path = line.split(' =:= ')[1]
    #         elif key == 'start':
    #             self.start = line.split(' =:= ')[1]
    #         elif key == 'end':
    #             self.end = line.split(' =:= ')[1]
    #         elif key == 'wells':
    #             self.wells = tuple(line.split(' =:= ')[1][1:-1].split(', '))
    #         elif key == 'groups':
    #             self.groups = tuple(line.split(' =:= ')[1][1:-1].split(', '))
    #         elif key == 'regions':
    #             self.regions = tuple(line.split(' =:= ')[1][1:-1].split(', '))
    #         elif key == 'keys':
    #             self.keys_ = tuple(line.split(' =:= ')[1][1:-1].split(', '))
    #         elif key == 'overwrite':
    #             self.overwrite = line.split(' =:= ')[1]
    #         elif key == 'null':
    #             self.null = line.split(' =:= ')[1]
    #         elif key == 'color':
    #             self.color = tuple(line.split(' =:= ')[1].split(', '))
    #         elif key == 'restarts':
    #             self.restarts = line.split(' =:= ')[1]
    #         elif key == 'ECLstyle':
    #             self.ECLstyle = bool(line.split(' =:= ')[1])
    #         elif key == 'VIPstyle':
    #             self.VIPstyle = bool(line.split(' =:= ')[1])

    #         elif key == 'keysECL':
    #             self.keysECL = tuple(line.split(' =:= ')[1].split(', '))
    #         elif key == 'keysVIP':
    #             self.keysVIP = tuple(line.split(' =:= ')[1].split(', '))
    #         elif key == 'keysCSV':
    #             self.keysCSV = tuple(line.split(' =:= ')[1].split(', '))
    #         elif key == 'CSV':
    #             self.CSV = bool(line.split(' =:= ')[1])
    #         elif key == 'LPGcorrected':
    #             self.LPGcorrected = bool(line.split(' =:= ')[1])
    #         elif key == 'fieldtime':
    #             self.fieldtime = (float(line.split(' =:= ')[1][1:]), float(line.split(' =:= ')[2]), np.array(line.split(' =:= ')[3][1:-2].split(', '), dtype='float'))

    #     if self.kind == ECL:
    #         pass
    #     elif self.kind == VIP:
    #         pass
    #         # count = 0

    #     # load attributes dictionary to JSON file
    #     with open(RestorePath + 'json/attributes.sro', 'r') as file:
    #         self.attributes = json.load(file)

    #     # load vectors as dataframe and dump from parquet
    #     self.vectors = (pd.read_parquet(RestorePath + 'parquet/vectors.sro')).to_dict()

    #     # dump units dictionary to JSON file
    #     with open(RestorePath + 'json/units.sro', 'r') as file:
    #         self.units = json.load(file)

    def to_pickle(self, filepath=None):
        import pickle
        if filepath is None:
            if self.path is not None:
                filepath = _extension(self.path)[0] + _extension(self.path)[1] + '.pkl'
                print('\n>>> saving current state to the file:\n   ', filepath)
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)

    def to_RSM(self, keys='--all', filepath=None, RSM_leng=12, RSM_cols=10, include_DATE=True, ECL_keywords_only=True,
               region_names=False):
        """
        writes the selected vectors, or all the vectors by default, to an RSM format file.
        """
        from decimal import Decimal
        def RSMunits(string):
            RSMdict = {
                # 'VIP unit' : [ 'ECL unit', Multiplier, ShiftX, ShiftY ] -> ECLunit = ((VIP_unit + ShiftX) * Multiplier) + ShiftY
                'FRACTION': ['', '', 1, 0, 0],
                'DIMENSIONLESS': ['', '', 1, 0, 0],
                'KPA': ['BARSA', '', 0.01, 0, 0],
                'STM3/KSM3': ['SM3/SM3', '', 1000, 0, 0],
            }
            notChange = ['KPA', 'K', 'KG', '']
            dimless = ['DIMENSIONLESS', 'FRACTION', 'UNITLESS', 'NONE', 'None', 'RATIO', None]
            if string in RSMdict.keys():
                return RSMdict[string]
            if string in notChange:
                return [string, '', 1, 0, 0]
            if string in dimless:
                return ['', '', 1, 0, 0]
            if len(string) == 1:
                return [string, '', 1, 0, 0]

            string = string.replace('STM3', 'SM3')

            if string[0].upper() == 'K':
                ret = [string[1:], '', 1E3, 0, 0]
            elif string[0].upper() == 'M':
                ret = [string[1:], '', 1E6, 0, 0]
            elif string[0].upper() == 'G':
                ret = [string[1:], '', 1E9, 0, 0]
            else:
                ret = [string, '', 1, 0, 0]

            return ret

        include_DATE = bool(include_DATE)
        ECL_keywords_only = bool(ECL_keywords_only)

        if type(RSM_leng) is not int:
            raise TypeError("RSMleng must be an integer")
        if type(RSM_cols) is not int:
            raise TypeError("RSMcols must be an integer")

        if type(keys) is str and len(self.get_keys(keys)) == 0 and filepath is None:
            keys = keys.strip()
            if os.path.isfile(_extension(keys)[3]):
                filepath = keys
                keys = '--all'
            elif os.path.isdir(_extension(keys)[3]):
                filepath = _extension(self.path)[1]
                for end in ['_field', '_well', '_area', '_flow', '_gather', '_region']:
                    if filepath.endswith(end):
                        filepath = filepath[:-len(end)]
                        break
                if _extension(keys[-1])[3] == '/':
                    filepath = _extension(keys[-1])[3] + filepath + '.RSM'
                else:
                    filepath = _extension(keys[-1])[3] + '/' + filepath + '.RSM'
                keys = '--all'
            elif os.path.isdir(_extension(keys)[2]):
                filepath = _extension(keys)[2] + _extension(keys)[1] + '.RSM'
                keys = '--all'

        if filepath is None:
            filepath = _extension(self.path)[1]
            for end in ['_field', '_well', '_area', '_flow', '_gather', '_region']:
                if filepath.endswith(end):
                    filepath = filepath[:-len(end)]
                    break
            filepath = _extension(self.path)[2] + filepath + '.RSM'
        elif type(filepath) is str:
            if _extension(filepath)[0].upper() != '.RSM':
                filepath = _extension(filepath)[2] + _extension(filepath)[1] + '.RSM'
            if _extension(filepath)[2] == '':
                filepath = _extension(self.path)[2] + filepath
        filepath = _extension(filepath)[3]

        try:
            RSMfile = open(filepath, 'w')
            print('\n...working on it: preparing the data for the RSM file...\n      ' + filepath)
            RSMfile.close()
        except:
            print('\n...failed to create the output RSM file...\n      ' + filepath)
            return False

        rsmOutput = self.name
        for end in ['_field', '_well', '_area', '_flow', '_gather', '_region']:
            if rsmOutput.endswith(end):
                rsmOutput = rsmOutput[:-len(end)]
                break

        if keys == '--all':
            if ECL_keywords_only:
                CleanColumns = []
                for Key in self.keys_:
                    if _isECLkey(Key, maxLen=RSM_leng):
                        CleanColumns.append(Key)
            else:
                CleanColumns = self.keys_
                VIPcolLen = max(nplen(np.array(_mainKey(self.keys_))))
                if VIPcolLen > RSM_leng:
                    _verbose(self.speak, 3, "\nIMPORTANT: the lenght of the columns must be set to " + str(
                        VIPcolLen) + " to fit key names.")
                    RSM_leng = VIPcolLen
        else:
            CleanColumns = []
            if type(keys) is str:
                keys = [keys]
            for K in keys:
                if len(self.get_KeysFromAttribute(K)) > 0:
                    CleanColumns += self.get_KeysFromAttribute(K)
                elif len(self.get_keys(K)) > 0:
                    CleanColumns += list(self.get_KeysFromAttribute(K))
                    _verbose(self.speak, 3, "\nMESSAGE: " + str(len(
                        self.get_keys(K))) + " keys found for the pattern '" + K + "':\n" + str(
                        self.get_keys(K)).strip('( )'))
                else:
                    _verbose(self.speak, 3, "\nWARNING: the key '" + K + "' is not valid.")

        if len(CleanColumns) == 0:
            _verbose(self.speak, 3, "\nERROR: no valid keys found to export to the RSM.")
            return False

        # check vectors are numeric
        NotValueVector = []
        # cc = 0
        for each in CleanColumns:
            # progressbar(cc/len(CleanColumns))
            if _mainKey(each) in ['DATE', 'DATES', 'WNAME']:
                NotValueVector.append(each)
            elif _itemKey(each) in ['DATE', 'DATES']:
                NotValueVector.append(each)
            elif len(self(each)) == 0:
                NotValueVector.append(each)
            elif not _isnumeric(str(self(each)[0])):
                NotValueVector.append(each)
            # cc += 1
        for each in NotValueVector:
            CleanColumns.pop(CleanColumns.index(each))

        # move the following keys to the front
        for each in ['YEARS', 'YEAR', 'DAY', 'MONTH', 'TIME', 'DATES', 'DATE']:
            if each in CleanColumns:
                CleanColumns.pop(CleanColumns.index(each))
                CleanColumns = [each] + CleanColumns

        # create DATE key if required
        if 'DATE' in CleanColumns or 'DATES' in CleanColumns or include_DATE:
            if not self.is_Key('DATE'):
                if self.is_Key('DATES'):
                    self['DATE'] = 'DATES'
                else:
                    try:
                        self.createDATES()
                        _verbose(self.speak, 3, "MESSAGE: DATE key created")
                    except:
                        pass

        if include_DATE:
            if self.is_Key('DATE'):
                if 'DATE' not in CleanColumns:
                    _verbose(self.speak, 3, "MESSAGE: added 'DATE'")
                    CleanColumns = ['DATE'] + CleanColumns
            else:
                if self.createDATES() is None:
                    _verbose(self.speak, 3, "MESSAGE: DATE created and added to the RSM")
                    CleanColumns = ['DATE'] + CleanColumns
                else:
                    _verbose(self.speak, 3, "WARNING: DATE key is not available.")

        if 'DATE' in CleanColumns and 'DATES' in CleanColumns:
            if (self('DATE') == self('DATES')).all():
                CleanColumns.pop(CleanColumns.index('DATES'))
                _verbose(self.speak, 2, "MESSAGE: removed duplicated key DATES")

        # list of found regions
        try:  # if type(self) is VIP:
            REGIONS = self.regionNumber
        except:  # else:
            REGIONS = {}
            for i in range(len(self.regions)):
                REGIONS[self.regions[i]] = self.regions[i]

        print('\n...working on it: writing the data into the RSM file...')
        print()

        # prepare the time column
        fechas = None
        if self.is_Key('DATE'):
            fechas = _strDate(self('DATE'), formatOUT='DD-MMM-YYYY')
            CleanColumns.pop(CleanColumns.index('DATE'))
        elif self.is_Key('TIME'):
            fechas = list(map(str, self('TIME')))
            _verbose(self.speak, 3, "WARNING: DATE key is not available, will use TIME as index to create the RSM.")
        elif self.is_Key('YEAR') or self.is_Key('MONTH') or self.is_Key('DAY'):
            T = []
            for t in ['DAY', 'MONTH', 'YEAR']:
                if self.is_Key(t):
                    T.append(t)
            if len(T) == 1:
                fecha = list(map(str, self(T[0])))
                _verbose(self.speak, 3, "WARNING: neither DATE or TIME keys are available, \nthe         the key '" + T[
                    0] + "' will be used as index to create the RSM.")
            elif len(T) == 2:
                formatStr = lambda s: str(s[0]) + '-' + str(s[1])
                fechas = list(map(formatStr, zip(T[0], T[1])))
                _verbose(self.speak, 3,
                         "WARNING: neither DATE or TIME keys are available, \nthe         the keys '" + T[0] + "'-'" +
                         T[1] + "' will be used as index to create the RSM.")
            elif len(T) == 3:
                formatStr = lambda s: str(s[0]) + '-' + str(s[1]) + '-' + str(s[2])
                fechas = list(map(formatStr, zip(T[0], T[1], T[2])))
                _verbose(self.speak, 3,
                         "WARNING: neither DATE or TIME keys are available, \nthe         the keys '" + T[0] + "'-'" +
                         T[1] + "'-'" + T[2] + "' will be used as index to create the RSM.")
        else:
            FieldKeys = list(self.get_keys('FPR*')) + list(self.get_keys('F*T'))
            for F in ['FOPT', 'FGPT', 'FPRH', 'FPR', 'FPRP', 'FWIT', 'FGIT', 'FWPT']:
                if F in FieldKeys:
                    fechas = list(map(str, self(F)))
                    _verbose(self.speak, 3,
                             "WARNING: neither DATE or TIME keys are available, \nthe         the key '" + F + "' will be used as index to create the RSM.")
                    break
        if fechas is None:
            for K in CleanColumns:
                if self.is_Key(K):
                    fechas = list(map(str, self(K)))
                    _verbose(self.speak, 3,
                             "WARNING: neither DATE or TIME keys are available, \nthe         the key '" + K + "' will be used as index to create the RSM.")
                    break

        RSMfile = open(filepath, 'w')

        cc = 0
        while cc < len(CleanColumns):
            # progressbar(cc/len(CleanColumns))
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

            for each in CleanColumns[cc: cc + RSM_cols - 1]:

                if each in ['TIME', 'DAY', 'MONTH', 'YEAR', 'DATE']:
                    line1 = line1 + '\t' + each + ' ' * (RSM_leng - len(each))
                elif _itemKey(each) in ['TIME', 'DAY', 'MONTH', 'YEAR', 'DATE']:
                    # is a VIP style keyword
                    line1 = line1 + '\t' + _itemKey(each) + ' ' * (RSM_leng - len(_itemKey(each)))
                else:
                    line1 = line1 + '\t' + _mainKey(each) + ' ' * (RSM_leng - len(_mainKey(each)))

                CombiU = RSMunits(self.get_Units(each))

                line2 = line2 + '\t' + CombiU[0] + ' ' * (RSM_leng - len(CombiU[0]))
                line3 = line3 + '\t' + CombiU[1] + ' ' * (RSM_leng - len(CombiU[1]))

                unitMult.append(CombiU[2])
                unitSumY.append(CombiU[3])
                unitSumX.append(CombiU[4])

                if _keyType(each) == 'FIELD':
                    Combi0 = ''
                    CombiR = ''
                elif _keyType(each) == 'REGION':
                    if _itemKey(each) not in REGIONS.keys():
                        REGIONS[_itemKey(each)] = len(REGIONS) + 1
                    CombiR = str(REGIONS[_itemKey(each)])
                    if region_names:
                        Combi0 = _itemKey(each).strip() if _itemKey(each).strip() != CombiR.strip() else _mainKey(each)
                    else:
                        Combi0 = ''
                else:
                    Combi0 = _itemKey(each)
                    CombiR = ''
                if Combi0 is None:
                    Combi0 = ''
                if CombiR is None:
                    CombiR = ''
                line4 = line4 + '\t' + Combi0 + ' ' * (RSM_leng - len(Combi0))
                line5 = line5 + '\t' + CombiR + ' ' * (RSM_leng - len(CombiR))
            line1 = line1 + '\n'
            line2 = line2 + '\n'
            line3 = line3 + '\n'
            line4 = line4 + '\n'
            line5 = line5 + '\n'

            if len(line3.strip()) == 0:
                line3 = line4
                line4 = line5
                line5 = ' \t            ' + (('\t' + (' ' * RSM_leng)) * (RSM_cols - 1)) + '\n'

            line = line1 + line2 + line3 + line4 + line5  # + '\n'
            RSMfile.write(line)

            for f in range(len(fechas)):
                line = '\t ' + fechas[f]
                unitN = 0

                for each in CleanColumns[cc: cc + RSM_cols - 1]:
                    #  the value
                    value = str(self(each)[f])

                    if '.' in value:
                        if 'E' in value:
                            value = str((float(value) + unitSumX[unitN]) * unitMult[unitN] + unitSumY[unitN])
                        else:
                            value = str((float(value) + unitSumX[unitN]) * unitMult[unitN] + unitSumY[unitN])
                    else:
                        value = str((int(value) + unitSumX[unitN]) * unitMult[unitN] + unitSumY[unitN])

                    if len(value) > RSM_leng:
                        if len(str(int(float(value)))) <= RSM_leng:
                            value = str(float(value))[:RSM_leng]
                        else:
                            value = ('%.' + str(RSM_leng - 6) + 'E') % Decimal(value)

                    # preparing and printing the line
                    if (RSM_leng - len(value)) > 0:
                        rept = ' ' * (RSM_leng - len(value))
                    else:
                        rept = ''

                    line = line + '\t' + rept + value

                    unitN += 1

                line = line + '\n'
                RSMfile.write(line)

            cc += RSM_cols - 1

        RSMfile.close()
        print(
            "the RMS file is completed, feel free to open it:\n\n '" + filepath + "'\n")  # "\nPlease wait for the report of the conversion to be finished.")
        try:
            RSMfile.close()
        except:
            pass
        return None

    def to_excel(self, keys='--all', filepath=None, include_DATE=True, ECL_keywords_only=True, split_by='left',
                 write_units=True):
        """
        writes the selected vectors, or all the vectors by default, to an Excel format file.
        """
        if split_by is None or type(split_by) is str and split_by.upper == 'NONE':
            if write_units is False:
                write_units = True
                _verbose(self.speak, 3, "\n `split_by´ must be used together with writeUnits=True.")

        if type(keys) is str and len(self.get_keys(keys)) == 0 and filepath is None:
            keys = keys.strip()
            if os.path.isfile(_extension(keys)[3]):
                filepath = keys
                keys = '--all'
            elif os.path.isdir(_extension(keys)[3]):
                filepath = _extension(self.path)[1]
                for end in ['_field', '_well', '_area', '_flow', '_gather', '_region']:
                    if filepath.endswith(end):
                        filepath = filepath[:-len(end)]
                        break
                if _extension(keys[-1])[3] == '/':
                    filepath = _extension(keys[-1])[3] + filepath + '.xlsx'
                else:
                    filepath = _extension(keys[-1])[3] + '/' + filepath + '.xlsx'
                keys = '--all'
            elif os.path.isdir(_extension(keys)[2]):
                filepath = _extension(keys)[2] + _extension(keys)[1] + '.xlsx'
                keys = '--all'

        if filepath is None:
            filepath = _extension(self.path)[1]
            for end in ['_field', '_well', '_area', '_flow', '_gather', '_region']:
                if filepath.endswith(end):
                    filepath = filepath[:-len(end)]
                    break
            filepath = _extension(self.path)[2] + filepath + '.xlsx'
        elif type(filepath) is str:
            if _extension(filepath)[0].lower() != '.xlsx':
                filepath = _extension(filepath)[2] + _extension(filepath)[1] + '.xlsx'
            if _extension(filepath)[2] == '':
                filepath = _extension(self.path)[2] + filepath
        filepath = _extension(filepath)[3]

        if filepath.lower().endswith('.xls.xlsx'):
            filepath = filepath[:-9] + '.xlsx'

        if keys == '--all':
            if ECL_keywords_only:
                CleanColumns = []
                for Key in self.keys_:
                    if _isECLkey(Key, maxLen=16):
                        CleanColumns.append(Key)
            else:
                CleanColumns = self.keys_

        else:
            CleanColumns = []
            if type(keys) is str:
                keys = [keys]
            for K in keys:
                if len(self.get_KeysFromAttribute(K)) > 0:
                    CleanColumns += self.get_KeysFromAttribute(K)
                elif len(self.get_keys(K)) > 0:
                    CleanColumns += list(self.get_KeysFromAttribute(K))
                    _verbose(self.speak, 3, "\nMESSAGE: " + str(len(
                        self.get_keys(K))) + " keys found for the pattern '" + K + "':\n" + str(
                        self.get_keys(K)).strip('( )'))
                else:
                    _verbose(self.speak, 3, "\nWARNING: the key '" + K + "' is not valid.")

        if len(CleanColumns) == 0:
            _verbose(self.speak, 3, "\nERROR: no valid keys found to export to the EXCEL file.")
            return False

        # check vectors are numeric
        NotValueVector = []
        # cc = 0
        for each in CleanColumns:
            # progressbar(cc/len(CleanColumns))
            if _mainKey(each) in ['DATE', 'DATES', 'WNAME']:
                NotValueVector.append(each)
            elif _itemKey(each) in ['DATE', 'DATES']:
                NotValueVector.append(each)
            elif len(self(each)) == 0:
                NotValueVector.append(each)
            elif not _isnumeric(str(self(each)[0])):
                NotValueVector.append(each)
            # cc += 1
        for each in NotValueVector:
            CleanColumns.pop(CleanColumns.index(each))

        # move the following keys to the front
        for each in ['YEARS', 'YEAR', 'DAY', 'MONTH', 'TIME', 'DATES', 'DATE']:
            if each in CleanColumns:
                CleanColumns.pop(CleanColumns.index(each))
                CleanColumns = [each] + CleanColumns

        # create DATE key if required
        if 'DATE' in CleanColumns or 'DATES' in CleanColumns or include_DATE:
            if not self.is_Key('DATE'):
                if self.is_Key('DATES'):
                    self['DATE'] = 'DATES'
                else:
                    try:
                        self.createDATES()
                        _verbose(self.speak, 3, "MESSAGE: DATE key created")
                    except:
                        pass

        if include_DATE:
            if self.is_Key('DATE'):
                if 'DATE' not in CleanColumns:
                    _verbose(self.speak, 3, "MESSAGE: added 'DATE'")
                    CleanColumns = ['DATE'] + CleanColumns
            else:
                if self.createDATES() is None:
                    _verbose(self.speak, 3, "MESSAGE: DATE created and added to the EXCEL")
                    CleanColumns = ['DATE'] + CleanColumns
                else:
                    _verbose(self.speak, 3, "WARNING: DATE key is not available.")

        if 'DATE' in CleanColumns and 'DATES' in CleanColumns:
            if (self('DATE') == self('DATES')).all():
                CleanColumns.pop(CleanColumns.index('DATES'))
                _verbose(self.speak, 2, "MESSAGE: removed duplicated key DATES")

        print('\n...working on it: preparing the data for the RSM file...\n      ' + filepath)

        if write_units is True and self.useSimPandas is False:
            self.useSimPandas = True
            ExcelDF = self[CleanColumns]
            ExcelDF.to_excel(filepath, split_by=split_by)
            self.useSimPandas = False
        elif write_units is False and self.useSimPandas is True:
            self.useSimPandas = False
            ExcelDF = self[CleanColumns]
            ExcelDF.to_excel(filepath)
            self.useSimPandas = False
        else:
            ExcelDF = self[CleanColumns]
            ExcelDF.to_excel(filepath)

        return None

    def to_schedule(self, path=None, units='FIELD', control_mode=None, shut_stop=None, keys=None, wells=None,
                    groups=None,
                    as_history=False, as_forecast=False, drop_zeros_columns=True, use_dates=True):
        """
        export a eclipse style schedule file.

        Parameters
        ----------
        path : str, optional
            the full path to output file to be written.
            Defeult is the name of the object in the same folder with the extension ".sch"
        units : str or dict, optional
            a string 'FIELD', 'METRIC', LAB or PVT-M will convert the data to the corresponding eclipse simulator units system.
            a dictionary should contain desired units for all the columns to be converted. The default is None.
        control_mode : str or dict, optional
            a string defining the control mode for the simulation:'ORAT','WRAT','GRAT'
            a dictionary with pairs of item:ControlModel for each item (well or group).
        shut_stop : str, optional
            a string 'OPEN, 'SHUT' or 'STOP' indicating what to do with the wells when their rate is zero.
            Default is 'STOP'
        keys : list or dict, optional
            the list of keywords to be exported to the schedule file.
            if the keys in the data does not follow Eclipse names, a dict of pairs {key_name:ecl_name} should be provided.
            Default is: 'WOPRH', 'WWPRH','WGPRH', 'WBHPH', 'WGIRH', 'WWIRH', 'WOPR', 'WWPR','WGPR', 'WBHP', 'WGIR', 'WWIR' if exist.
        wells : list or dict
            the list of wells to be exported, if None all the wells will be exported.
            if needed to rename the wells, a dict of pairs {current_name:new_name} can be provided.
        groups : list or dict
            ** NOT IMPLEMENTED **
            the list of groups to be exported, if None no groups will be exported.
            if needed to rename the groups, a dict of pairs {current_name:new_name} can be provided.
        as_history : bool
            ** EXPERIMENTAL **
            export the well forecast keys as history keywrods.
        as_forecast : bool
            ** NOT IMPLEMENTED **
            export the well history keys as forecast keywords.
        drop_zeros_columns : bool
            set True to remove columns filled entirely with zeroes.
        use_dates : bool
            set True to use the 'DATE' key to generate DATES keywords.
            set False to calculate time differences from TIME or DATES and generate TSTEP keywords.  ** NOT IMPLEMENTED **

        Returns
        -------
        None.
        """
        import os.path
        if path is None:
            path = _extension(self.path)[2] + _extension(self.path)[1] + '.SCH'
        if os.path.isfile(path):
            raise OverwritingError("The output file already exists:\n  '" + str(path) + "'")
        if keys is None:
            userKeys, keys = [], ['WOPRH', 'WWPRH', 'WGPRH', 'WBHPH', 'WGIRH', 'WWIRH', 'WOPR', 'WWPR', 'WGPR', 'WBHP',
                                  'WGIR', 'WWIR']
        elif type(keys) is str:
            keys = [keys]
            userKeys = tuple(keys)
        elif type(keys) is dict:
            userKeys, keys = keys, list(keys.keys())
        if wells is None:
            exportWells = list(self.wells)
        else:
            exportWells = [w for w in wells if w in self.wells]
        if groups is None:
            exportGroups = []

        if (len(self.get_Producers()) + len(self.get_Injectors())) > 0:
            exportKeys = [_mainKey(k) + ':' + w for k in keys for w in exportWells if k[0] in 'wW' if
                          _mainKey(k)[-2:].upper() in ('PR', 'PRH') if w in self.get_Producers()]
            exportKeys += [_mainKey(k) + ':' + w for k in keys for w in exportWells if k[0] in 'wW' if
                           _mainKey(k)[-2:].upper() in ('IR', 'IRH') if w in self.get_Injectors()]
            exportKeys += [_mainKey(k) + ':' + w for k in keys for w in exportWells if _mainKey(k).upper() not in (
            'PR', 'PRH', 'IR', 'IRH')]  # -> 'WBHPH','WTHPH', 'WALQH','WBHP','WTHP','WALQ', ...
        elif len(self.wells) > 0:
            exportKeys = [_mainKey(k) + ':' + w for k in keys for w in exportWells if k[0] in 'wW']
        else:
            _verbose(self.speak, 3, "WARNING: No wells found to be exported.")
            exportKeys = []

        # put all the keywords provided by the user
        exportKeys += [_mainKey(k) + ':' + w for k in userKeys for w in exportWells if _itemKey(k) is not None]
        exportKeys += [_mainKey(k) for k in userKeys if _itemKey(k) is None]
        # exportKeys += [ _mainKey(k)+':'+g for k in keys for g in exportGroups if k[0] == 'G' ]

        # keep only valid keys, not duplicated
        exportKeys = [k for k in exportKeys if k in self.keys_]
        exportKeys = list(set(exportKeys))

        if use_dates:
            if type(use_dates) is str:
                if use_dates in self.keys_:
                    if 'datetime' in str(test('DATE').dtype):
                        datekey = use_dates
                    else:
                        raise TypeError("The key '" + str(
                            use_dates) + "' requested to be used as DATES is not a valid 'date' type.")
                else:
                    raise ValueError("The key '" + str(
                        use_dates) + "' requested to be used as DATES is not a key in this simulation results.")
            else:
                for datekey in ('DATE', 'DATES'):
                    if datekey in self.keys_ and datekey not in exportKeys:
                        exportKeys.append(datekey)
                        break

        data = self[exportKeys]
        if use_dates:
            data = data.set_index(datekey, drop=True)

        if drop_zeros_columns:
            data = data.dropzeros()

        if as_history:
            histKeys = [k for k in exportKeys if _mainKey(k)[-1] != 'H']
            histKeys = {k: _mainKey(k) + 'H:' + _itemKey(k) for k in histKeys}
            dataHist = data.rename(columns=histKeys)[list(histKeys.values())]
            dataExport = data.drop(columns=list(histKeys.keys()))
            if len(dataExport.columns) == 0:
                dataExport = dataHist
            else:
                dataExport = dataHist + dataOriginal
        else:
            dataExport = data

        if as_forecast:
            foreKeys = [k for k in exportKeys if _mainKey(k)[-1] == 'H']
            foreKeys = {k: _mainKey(k) + 'H:' + _itemKey(k) for k in foreKeys}
            dataFore = data.rename(columns=foreKeys)[list(foreKeys.values())]
            dataClean = data.drop(columns=list(foreKeys.keys()))
            if len(dataClean.columns) == 0:
                if as_history:
                    pass  # dataExport = dataExport from previos process
                else:
                    dataExport = dataFore
            else:
                if as_history:
                    dataExport = dataFore + dataExport
                else:
                    dataExport = dataFore + dataClean
            dataClean = None
        elif as_history:
            pass  # dataExport = dataExport from previos process
        else:
            dataExport = data

        if type(userKeys) is dict:
            mainUserKeys = {_mainKey(k): _mainKey(v) for k, v in userKeys.items()}
            renameKeys = {
                _mainKey(k) + (':' + _itemKey(k) if _itemKey(k) is not None else ''): mainUserKeys[_mainKey(k)] + (
                    ':' + _itemKey(k) if _itemKey(k) is not None else '') for k in dataExport.columns}
            dataExport = dataExport.rename(columns=renameKeys)
        if type(wells) is dict:
            wells = {w: nw for w, nw in wells.items() if w in dataExport.wells}
            dataExport = dataExport.renameItem(columns=wells)

        dataExport.to_schedule(path)

    def to_vol(self, path, wells=None, keys=None, units='FIELD'):
        """
        writes out a .vol file for the selected wells and selected keys.

        Parameters
        ----------
        path : str
            A string indicating the path to the file to exported
        wells : str or list-like, optional
            The name of the well to be exported (a string) or a list containing
            the names (strings) of the wells to be exported.
            By default will export all the well in this SimResults.
        keys : str or list-like, optional
            The keys to be exported.
            By default will export all the rates.
        units : str, optional
            The string 'FIELD' or 'METRIC' indicating the units to export the .vol
            The default is 'FIELD'.

        Raises
        ------
        ValueError
            if a parameter is wrong.

        Returns
        -------
        None

        """

        def isRate(unit_string):
            if '/' in unit_string:
                if len(unit_string.split('/')) > 1:
                    if unit_string.split('/')[1].strip('( )').upper()[:3] == 'DAY':
                        return True
            return False

        if keys is None:
            keys = _mainKey(self.find_Keys('W*'))
            wkeys = [k for k in keys if isRate(self.get_Unit(k))]
        elif type(keys) is str:
            keys, ukeys = _mainKey(self.find_Keys(keys)), keys
            if len(keys) == 0:
                raise ValueError("No keys found by the string '" + ukeys + "'")
        if wells is None:
            wells = self.wells
        if type(units) is not str or (
                type(units) is not str and
                units.upper().strip() not in ('FIELD', 'METRIC')):
            raise ValueError("units must be 'FIELD' or 'METRIC'")
        else:
            if units.upper().strip() == 'FIELD':
                unitsDict = _dictionaries.unitsFIELD
            else:  # elif units.upper().strip() == 'METRIC':
                unitsDict = _dictionaries.unitsMETRIC
            exportUnits = {k: unitsDict[k[1:]] for k in keys if k[1:] in unitsDict}

        with open(path, 'w') as out:
            out.write('*' + units + '\n')
            out.write('*DAILY\n')
            out.write('*IGNORE_MISSING\n')
            out.write('\t'.join([self.DTindex] + ['*' + k for k in keys]) + '\n')
            for well in wells:
                out.write('*NAME\t' + str(well) + '\n')
                wkeys = [k + ':' + str(well) for k in keys]
                data = self[[self.DTindex] + wkeys].to(exportUnits)
                datastr = '\n'.join(
                    ['\t'.join(map(str, [data.iloc[i, c]
                                         for c in range(len(data.columns))
                                         ]
                                   )
                               )
                     for i in range(len(data.index))
                     ]
                ) + '\n'
                out.write(datastr)

    def close(self):
        print("close method not defined for this type of source.")
