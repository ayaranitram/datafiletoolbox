# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:45:12 2020

@author: MCARAYA
"""

__version__ = '0.1.8'
__release__ = 20220901
__all__ = ['H5']

from .mainObject import SimResult as _SimResult
from .._common.functions import _mainKey, _itemKey
from .._common.inout import _extension
from .._common.inout import _verbose
# from .._common.stringformat import isnumeric as _isnumeric
from .._Classes.Errors import CorruptedFileError
from .._Classes.Errors import InvalidKeyError
import numpy as np
import os
import h5py
import warnings
import datetime as dt
import fnmatch


class H5(_SimResult):
    """
    object to contain HDF5 format results read from h5 file using h5py
    """

    def __init__(self, inputFile=None, verbosity=2, **kwargs):
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = H5
        self.keynames = None
        self.numpy_dates = None
        if type(inputFile) == str and len(inputFile.strip()) > 0:
            self.smspec = self.readSMSPEC(inputFile)
            self.loadSummary(inputFile, **kwargs)
            # if ('unload' in kwargs and kwargs['unload'] is True) or ('close' in kwargs and kwargs['close'] is True):
            #         return None
        if self.results is not None:
            self.initialize(**kwargs)

    def loadSummary(self, h5FilePath, **kwargs):
        if type(h5FilePath) is str:
            h5FilePath = h5FilePath.strip()
            if self.path is None:
                self.path = h5FilePath
            if _extension(h5FilePath)[0].lower() != '.h5':
                newPath = _extension(h5FilePath)[2] + _extension(h5FilePath)[1] + '.h5'
                if os.path.isfile(newPath):
                    h5FilePath = newPath
                else:
                    newPath = _extension(h5FilePath)[2] + _extension(h5FilePath)[1] + '.H5'
                    if os.path.isfile(newPath):
                        h5FilePath = newPath

            if os.path.isfile(h5FilePath):
                if os.path.getsize(h5FilePath) == 0:
                    raise CorruptedFileError("\nThe .h5 file seems to be empty")
                _verbose(self.speak, 1, ' > loading HDF5 file:\n  ' + h5FilePath)
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
                if self.get_Dates() is not None:
                    _verbose(self.speak, 1,
                             'simulation runs from ' + str(self.get_Dates()[0]) + ' to ' + str(self.get_Dates()[-1]))
                self.set_Vector('DATE', self.get_Vector('DATES')['DATES'], self.get_Unit('DATES'), DataType='datetime',
                                overwrite=True)
                self.stripUnits()
                self.get_Attributes(reload=True)
                self.fill_FieldBasics()

            else:
                raise FileNotFoundError("the file doesn't exist:\n  -> " + h5FilePath)
        else:
            print("h5FilePath must be a string")

    def readSMSPEC(self, smspecPath):
        """
        read the SMSPEC file and extract the well and group names
        """
        import string

        if type(smspecPath) is str:
            smspecPath = smspecPath.strip()
            if _extension(smspecPath)[0].upper() != '.SMSPEC':
                newPath = _extension(smspecPath)[2] + _extension(smspecPath)[1] + '.SMSPEC'
                if os.path.isfile(newPath):
                    smspecPath = newPath
            if os.path.isfile(smspecPath):
                if os.path.getsize(smspecPath) == 0:
                    warnings.warn("\nThe .SMSPEC file seems to be empty:\n  -> " + smspecPath)
            else:
                warnings.warn("the SMSPEC file doesn't exist:\n  -> " + smspecPath)
        if not os.path.isfile(smspecPath) or os.path.getsize(smspecPath) == 0:
            warnings.warn(
                "the SMSPEC file doesn't exist or is empty:\n  -> " + smspecPath + "\n  Units and well names will be unkown.")

        with open(smspecPath, 'r', errors='surrogateescape') as file:
            smspec = file.read()

        keywords_index = smspec.index('\x00\x00\x10KEYWORDS')
        # if '@CHAR' in smspec[keywords_index:]:
        #     keywords_index = keywords_index + smspec[keywords_index:].index('@CHAR') + 5 + 8
        # else:
        #     keywords_index = keywords_index + smspec[keywords_index:].index('CHAR') + 4 + 8
        keywords_index += 27
        last_index = keywords_index + smspec[keywords_index:].index('\x00\x00\x10')
        keywords = smspec[keywords_index:last_index]
        keywords = [keywords[i:i + 8].strip() for i in range(0, len(keywords), 8)]

        # names_index = last_index + smspec[last_index:].index('\x00\x00\x10NAMES   ')
        if '\x00\x00\x10NAMES   ' in smspec:
            names_index = smspec.index('\x00\x00\x10NAMES   ')
        elif '\x00\x00\x10WGNAMES ' in smspec:
            names_index = smspec.index('\x00\x00\x10WGNAMES ')
        elif '\x00\x00\x10WNAMES  ' in smspec:
            names_index = smspec.index('\x00\x00\x10WNAMES  ')
        elif '\x00\x00\x10GNAMES  ' in smspec:
            names_index = smspec.index('\x00\x00\x10GNAMES  ')
        else:
            names_index = smspec.index('NAMES')

        # if '@C0' in smspec[names_index:]:
        #     name_len = smspec[names_index + smspec[names_index:].index('@C0') + 2:names_index + smspec[names_index:].index('@C0') + 5]

        #     if name_len.isdigit():
        #         name_len = int(name_len)
        #         names_index = names_index + smspec[names_index:].index('@C0') + 5 + 8  # 8 bits
        #     else:
        #         name_len = 8
        #         names_index = names_index + smspec[names_index:].index('@CHAR') + 5 + 8  #.index('\x00\x00\x03H')
        # elif 'CHAR' in smspec[names_index:]:
        #     name_len = 8
        #     names_index = names_index + smspec[names_index:].index('CHAR') + 4 + 8
        # else:
        #     name_len = 8
        #     names_index = names_index + smspec[names_index:].index('@CHAR') + 5 + 8
        name_len = smspec[names_index + 16:names_index + 19]
        if name_len.isdigit():
            name_len = int(name_len)
        else:
            name_len = 8
        names_index += 27

        # names_index = names_index + smspec[names_index:].index('\x00\x00\x03H') + 4
        last_index = names_index + smspec[names_index:].index('\x00\x00\x10')
        names = smspec[names_index:last_index]

        if name_len == 8:
            names = [names[i:i + name_len].strip() for i in range(0, len(names), name_len)]
        else:
            namesList = []
            i = 0
            while i < len(names):
                if names[i] in string.printable:
                    namesList.append(names[i:i + name_len].strip())
                    i += name_len
                else:
                    f = i
                    while f < len(names) and names[f] not in string.ascii_letters + string.digits + '-.+,:;':
                        f += 1
                    namesList.append(names[i:f])
                    i = f
            names = namesList

        # names = [None if n != ':+:+:+:+' else n for n in names]

        # nums_index = smspec.index('\x00\x00\x10NUMS    ')

        units_index = smspec.index('\x00\x00\x10UNITS   ')
        # if '@CHAR' in smspec[units_index:]:
        #     units_index = units_index + smspec[units_index:].index('@CHAR') + 5 + 8
        # elif 'CHAR' in smspec[units_index:]:
        #     units_index = units_index + smspec[units_index:].index('CHAR') + 4 + 8
        # else:
        #     units_index = units_index + smspec[units_index:].index('CHAR') + 4 + 8
        units_index += 27

        last_index = units_index + smspec[units_index:].index('\x00\x00\x10')
        units = smspec[units_index:last_index]
        units = [units[i:i + 8].strip() for i in range(0, len(units), 8)]

        # measrmnt_index = smspec.index('\x00\x00\x10MEASRMNT')

        self.units = {keywords[i] + (':' + names[i] if len(names[i]) > 0 else ''): units[i] for i in
                      range(len(keywords))}
        fieldKeys = [k for k in self.units.keys() if _mainKey(k) != k if k[0] == 'F']
        for k in fieldKeys:
            self.units[_mainKey(k)] = self.units[k]

        self.keynames = {}
        for i in range(len(keywords)):
            if keywords[i] not in self.keynames:
                self.keynames[keywords[i]] = []
            if names[i] not in self.keynames[keywords[i]]:
                self.keynames[keywords[i]].append(names[i])

    def reload(self):
        self.loadSummary(self.path)

    def readH5(self, key):
        """
        support function to extract data from the 'summary_vectors' key of the HDF5 file
        """
        main, item = _mainKey(key), _itemKey(key)
        item_pos = 0
        if main in self.keynames:
            if item is not None and item in self.keynames[main]:
                item_pos = self.keynames[main].index(item)
            elif item is not None:
                raise InvalidKeyError("'" + str(key) + "' is not a valid Key in this dataset.\nThe item '" + str(
                    item) + "' does not have a " + str(main))
        else:
            raise InvalidKeyError("'" + str(key) + "' is not a valid Key in this dataset")
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
        else:
            return self.readH5(key)

    def get_Dates(self):
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
            self.numpy_dates = self.start + np.array(
                [np.timedelta64(dt.timedelta(float(t))) for t in self.results['general']['time']])
            self.end = self.numpy_dates[-1]
        return self.numpy_dates

    def extract_Wells(self, pattern=None):
        """
        Will return a list of all the well names in case.
        """
        # preparing object attribute
        outList = list(self.wells)
        for key in self.get_Keys():
            if key[0] == 'W':
                if ':' in key:
                    item = key.split(':')[1]
                    if item not in ('', ':+:+:+:+'):
                        outList.append(item)
        self.wells = tuple(set(outList))
        # preparing list to return
        if pattern is None:
            return self.wells
        else:
            return tuple(fnmatch.filter(self.wells, pattern))

    def extract_Groups(self, pattern=None, reload=False):
        """
        calls group method from libecl:

        Will return a list of all the group names in case.

        If the pattern variable is different from None only groups
        matching the pattern will be returned; the matching is based
        on fnmatch(), i.e. shell style wildcards.
        """
        # preparing object attribute
        outList = list(self.groups)
        for key in self.get_Keys():
            if key[0] == 'G':
                if ':' in key:
                    item = key.split(':')[1]
                    if item not in ('', ':+:+:+:+'):
                        outList.append(item)
        self.groups = tuple(set(outList))
        # preparing list to return
        if pattern is None:
            return self.groups
        else:
            return tuple(fnmatch.filter(self.groups, pattern))

    def list_Keys(self, pattern=None, reload=False):
        """
        Return a StringList of summary keys matching @pattern.

        The matching algorithm is ultimately based on the fnmatch()
        function, i.e. normal shell-character syntax is used. With
        @pattern == "WWCT:*" you will get a list of watercut keys for
        all wells.

        If pattern is None you will get all the keys of summary
        object.
        """
        if len(self.keys) == 0 or reload is True:
            listOfKeys = []
            for key in list(self.results['summary_vectors'].keys()):
                if key not in self.keynames or len(self.keynames[key]) == 1:
                    listOfKeys.append(key)
                else:  # key in self.keynames and len(self.keynames[key]) > 1:
                    for item in self.keynames[key]:
                        if item not in ('', ':+:+:+:+'):
                            listOfKeys.append(key + ':' + item)
            self.keys = tuple(set(listOfKeys))
            for extra in ('TIME', 'DATE', 'DATES'):
                if extra not in self.keys:
                    self.keys = tuple([extra] + list(self.keys))
        if pattern is None:
            return self.keys
        else:
            return tuple(fnmatch.filter(self.keys, pattern))

    def extract_Regions(self, pattern=None):
        # preparing object attribute
        outList = list(self.regions)
        for key in self.get_Keys():
            if key[0] == 'R':
                if ':' in key:
                    item = key.split(':')[1]
                    if item not in ('', ':+:+:+:+'):
                        outList.append(item)
        self.regions = tuple(set(outList))
        # preparing list to return
        if pattern is None:
            return self.regions
        else:
            return tuple(fnmatch.filter(self.regions, pattern))

    def close(self):
        self.results.close()
