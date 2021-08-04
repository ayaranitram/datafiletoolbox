# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:34:04 2020

@author: MCARAYA
"""

__version__ = '0.1.0'
__release__ = 210804
__all__ = ['RSM']

from .mainObject import SimResult as _SimResult
from .._common.inout import _extension, _verbose
from .._common.functions import _mainKey, _wellFromAttribute
from .._common.stringformat import date as _strDate, getnumber as _getnumber
from .._common.keywordsConversions import fromECLtoVIP as _fromECLtoVIP, fromVIPtoECL as _fromVIPtoECL #, fromCSVtoECL
from .._dictionaries import UniversalKeys as _UniversalKeys, VIPTypesToExtractVectors as _VIPTypesToExtractVectors
from .._dictionaries import ECL2VIPkey as _ECL2VIPkey, VIP2ECLtype as _VIP2ECLtype, VIP2ECLkey as _VIP2ECLkey #, ECL2VIPtype
# from datafiletoolbox.dictionaries import ECL2CSVtype, ECL2CSVkey, CSV2ECLtype, CSV2ECLkey
# from datetime import timedelta
import pandas as pd
import numpy as np
import os


class RSM(_SimResult):
    """
    object to contain RSM results read from .rsm ASCII output
    """
    def __init__(self, inputFile=None, verbosity=2, nameSeparator=':', **kwargs) :
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = RSM
        self.name = None
        self.results = {}
        self.overwrite = False
        self.nameSeparator = str(nameSeparator) if nameSeparator is not None else self.nameSeparator
        if type(inputFile) is str and len(inputFile.strip()) > 0 :
            if os.path.isfile(inputFile) :
                self.readRSM(inputFile, **kwargs)
            else :
                print("file doesn't exists")
        if len(self.results) > 0 :
            if self.name is None:
                self.name = _extension(inputFile)[1]
            self.initialize(**kwargs)

    def initialize(self, **kwargs) :
        """
        run intensive routines, to have the data loaded and ready
        """
        self.keys = tuple( sorted(self.keys) )
        self.extract_Wells()
        self.extract_Groups()
        self.extract_Regions()
        self.get_Attributes(None, True)
        self.find_index()
        _SimResult.initialize(self, **kwargs)
        if self.is_Key('DATES') and not self.is_Key('DATE') :
            self['DATE'] = 'DATES'
        if not self.is_Key('DATE') :
            self.createDATES()
        elif self.get_Unit('DATE') is None or self.get_Unit('DATE') != 'DATE' :
            self.set_Units('DATE', 'DATE', overwrite=True)
        if not self.is_Key('DATES') and self.is_Key('DATE') :
            self['DATES'] = 'DATE'
        if self.is_Key('DATES') and ( self.get_Unit('DATES') is None or self.get_Unit('DATES') != 'DATE' ) :
            self.set_Unit('DATES', 'DATE', overwrite=True)
        if not self.is_Key('TIME') and self.is_Key('DATE') :
            self['TIME'] = ( self('DATE').astype('datetime64[s]') - self.start ).astype('int') / (60*60*24)
        if self.is_Key('TIME') and ( self.get_Unit('TIME') is None or self.get_Unit('TIME').upper() in ['', 'NONE'] ) :
            self.set_Unit('TIME', 'DAYS', overwrite=True)

    def find_index(self) :
        """
        identify the column that is common to all the frames, to be used as index.
        If there is a single frame the first column is used.
        """
        # check current KeyIndex
        KeyIndex = True
        IndexVector = None
        _verbose(self.speak, 1, "looking for an index column.")
        _verbose(self.speak, 1, " default index name is: " + str(self.DTindex))

        if self.DTindex in self.results :
            _verbose(self.speak, 1, "found the column index: " + str(self.DTindex))
            return self.DTindex

        # look for other identical index
        for Key in ('DATE', 'DATES', 'TIME', 'DAYS', 'MONTHS', 'YEARS') + self.keys :
            KeyIndex = False
            IndexVector = None
            if Key in self.results :
                self.DTindex = Key
                KeyIndex = True
                break
            
        if KeyIndex :
            _verbose(self.speak, 1, "found the index: " + str(self.DTindex))
            # create result vector for the common index
            IndexVector = self.results[self.DTindex]
            self.add_Key(self.DTindex)
            self.TimeVector = self.DTindex
            _ = self.set_Vector(Key=self.DTindex, VectorData=IndexVector, Units=self.get_Units(self.DTindex), DataType='auto', overwrite=True) 
            return self.DTindex
        else :
            _verbose(self.speak, 3, "time index not found.")
            self.DTindex = None

    def readRSM(self, inputFile, **kwargs) :
        """
        internal function to read an RSM file 
        """
        with open(inputFile,'r') as file:
            rsm = file.readlines()
        l = 0
        self.keys = []
        while l < len(rsm):

            if len(rsm[l].strip()) == 0:
                l += 1
                continue
            
            if rsm[l].strip().upper().startswith('SUMMARY OF RUN'):
                if self.name is None:
                    self.name =  rsm[l].strip()[15:]
                l += 1

                colnames = [ each.strip() for each in rsm[l].split('\t') ]
                l += 1

                units = [ each.strip() for each in rsm[l].split('\t') ]
                l += 1

                multipliers = [ each.strip() for each in  rsm[l].split('\t') ]
                l += 1
                
                names = [ each.strip() for each in  rsm[l].split('\t') ]
                l += 1

                numbers = [ each.strip() for each in  rsm[l].split('\t') ]
                l += 1
                
                mults = [ each.startswith('*10**') for each in multipliers ]
                if np.array(mults).sum() > 0:
                    nulls = [ len(each.strip())==0 for each in multipliers ]
                    if np.array(nulls).sum() + np.array(mults).sum() == len(multipliers) :
                        # actually are multipliers
                        multipliers = [ 1 if len(each.strip())==0 else 10**float(each.strip()[5:]) for each in multipliers ]
                        multipliers = np.array([ int(each) if int(each) == each else each for each in multipliers ])
                    else:
                        # aren't multipliers
                        other, numbers, names = numbers, names, multipliers
                        multipliers = [ 1 for each in multipliers.split('\t') ]
                else:
                    # no multipliers
                    other, numbers, names = numbers, names, multipliers
                    multipliers = [ 1 ] * len(multipliers)
                for c in range(len(colnames)):
                    if len(names[c]) > 0:
                        colnames[c] = colnames[c] + self.nameSeparator + names[c] 
                    elif len(str(numbers[c])) > 0:
                         colnames[c] = colnames[c] + self.nameSeparator + str(numbers[c])
                
                while sum(map(len,[ each.strip() for each in  rsm[l].split('\t') ])) == 0:
                    l += 1
            
                rsmtext = ''.join(rsm[l:])
                endline = rsmtext.index('\n\n') if '\n\n' in rsmtext else len(rsmtext)-1
                table = np.array([ [ cell.strip() for cell in row.split('\t') ] for row in rsmtext[:endline].split('\n') ])
                l += len(table) + 1

                for c in range(len(colnames)):
                    if c < table.shape[1] and sum(map(len,table[:,c])) > 0:
                        try:
                            self.results[colnames[c]] = table[:,c].astype(int)
                        except ValueError:
                            try:
                                self.results[colnames[c]] = table[:,c].astype(float)
                            except ValueError:
                                try:
                                    self.results[colnames[c]] = pd.to_datetime(table[:,c]).to_numpy().astype('datetime64[s]')
                                except:
                                    self.results[colnames[c]] = table[:,c]
                        self.keys.append(colnames[c])
                        self.units[colnames[c]] = units[c]
                        if 'float' in str(self.results[colnames[c]].dtype) or 'int' in str(self.results[colnames[c]].dtype):
                            self.results[colnames[c]] = self.results[colnames[c]] * multipliers[c]

        self.keys = tuple(set(self.keys))

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

        if pattern is None :
            return self.keys
        else:
            keysList = []
            for key in self.keys:
                if pattern in key :
                    keysList.append(key)
            return tuple( keysList )

    # support functions for get_Vector:
    def loadVector(self, key) :
        """
        internal function to return a numpy vector from the Frame files
        """
        if key not in self.results :
            _verbose(self.speak, 1, "the key '"+key+"' is not present in this RSM.")
            return None
        else:
            return self.results[key]
