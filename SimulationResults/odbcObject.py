# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:34:04 2020

@author: MCARAYA
"""

__version__ = '0.0.0'
__release__ = 220525
__all__ = ['ODBC']

from .mainObject import SimResult as _SimResult
from .._common.inout import _extension, _verbose
from .._common.functions import _mainKey, _wellFromAttribute
from .._common.stringformat import date as _strDate, getnumber as _getnumber
fromCSVtoECL
from .._dictionaries import UniversalKeys as _UniversalKeys, VIPTypesToExtractVectors as _VIPTypesToExtractVectors
from .._dictionaries import ECL2VIPkey as _ECL2VIPkey, VIP2ECLtype as _VIP2ECLtype, VIP2ECLkey as _VIP2ECLkey #, ECL2VIPtype
# from datafiletoolbox.dictionaries import ECL2CSVtype, ECL2CSVkey, CSV2ECLtype, CSV2ECLkey
# from datetime import timedelta
import pandas as pd
import numpy as np
import os

import pyodbc

class ODBC(_SimResult):
    """
    object to contain data read from sql connection to odbc
    """
    def __init__(self,
                 DRIVER='{SQL Server}',
                 SERVER='SQL12progen1\sql12Gen1',
                 DATABASE=None,
                 UID=None,
                 PWD=None,
                 TABLES=None,
                 verbosity=2, nameSeparator=':', preload=True,
                 uniqueID='UniqueID', headertable='OFM_HEADERID',
                 **kwargs):
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = ODBC
        self.name = None
        self.results = {}
        self.overwrite = False
        self.nameSeparator = str(nameSeparator) if nameSeparator is not None else self.nameSeparator
        self.uniqueID = uniqueID
        self.headertable = headertable
        self.conn = None
        self.preload = bool(preload)
        if preload is False:
            raise ImplementationError('direct reading from the database is not yet implemented.')
        if type(DRIVER) is str and len(DRIVER.strip()) > 0:
            if type(SERVER) is str and len(SERVER.strip()) > 0:
                if type(DATABASE) is str and len(DATABASE.strip()) > 0:
                    self.connectDB(DRIVER=DRIVER, SERVER=SERVER, DATABASE=DATABASE, UID=UID, PWD=PWD, TABLES=TABLES **kwargs)
                else:
                    raise TypeError('DATABASE must be a string')
            else:
                raise TypeError('SERVER must be a string')
        else:
            raise TypeError('DRIVER must be a string')

        if len(self.results) > 0:
            if self.name is None:
                self.name = DATABASE
            self.initialize(**kwargs)

    def initialize(self, **kwargs):
        """
        run intensive routines, to have the data loaded and ready
        """
        self.keys = tuple( sorted(self.keys))
        self.extract_Wells()
        self.extract_Groups()
        self.extract_Regions()
        self.get_Attributes(None, True)
        self.find_index()
        _SimResult.initialize(self, **kwargs)
        if self.is_Key('DATES') and not self.is_Key('DATE'):
            self['DATE'] = 'DATES'
        if not self.is_Key('DATE'):
            self.createDATES()
        elif self.get_Unit('DATE') is None or self.get_Unit('DATE') != 'DATE':
            self.set_Units('DATE', 'DATE', overwrite=True)
        if not self.is_Key('DATES') and self.is_Key('DATE'):
            self['DATES'] = 'DATE'
        if self.is_Key('DATES') and ( self.get_Unit('DATES') is None or self.get_Unit('DATES') != 'DATE' ):
            self.set_Unit('DATES', 'DATE', overwrite=True)
        if not self.is_Key('TIME') and self.is_Key('DATE'):
            self['TIME'] = ( self('DATE').astype('datetime64[s]') - self.start ).astype('int') / (60*60*24)
        if self.is_Key('TIME') and ( self.get_Unit('TIME') is None or self.get_Unit('TIME').upper() in ['', 'NONE'] ):
            self.set_Unit('TIME', 'DAYS', overwrite=True)

    def connectDB(self,
                  DRIVER='{SQL Server}',
                  SERVER='SQL12progen1\sql12Gen1',
                  DATABASE=None,
                  UID=None,
                  PWD=None,
                  TABLES=None,
                  **kwargs):
        """
        internal function to connect to ODBC database
        """

        connStr = 'DRIVER=' + DRIVER + ';SERVER=' + SERVER + ';DATABASE=' + DATABASE
        if UID is not None:
            connStr = connStr + ';UID=' + UID
        if PWD is not None:
            connStr = connStr + ';PWD=' + PWD

        conn = pyodbc.connect(connStr)

        if TABLES is not None:
            if type(TABLES) is str:
                TABLES = [TABLES]
            # load all the tables in database
            dbtables = []
            cursor = conn.cursor()
            for row in cursor.tables():
                dbtables.append(str(row.table_name))
            wrongTables = []
            for t in TABLES:
                if t not in dbtables:
                    print('ERROR: The table', t, "doesn't exists in the database", DATABASE)
                    wrongTables.append(t)
            if len(wrongTables) > 0:
                for t in wrongTables:
                    possibleTables = [dbt for dbt in dbtables if t.upper() in dbt.upper()]
                    if len(possibleTables) > 0:
                        print('\n Might the table', t, 'be one of these?:', '\n   '.join(possibleTables))
                raise ValueError('Wrong table(s) names(s)')
        else:  # set tables commonly used for OFM
            TABLES = [#'OFM_CATEGORY',
                      #'OFM_COMPLETION_en_US',
                      'OFM_DAILYFIELD',
                      'OFM_DAILYINJ',
                      'OFM_DAILYPROD',
                      'OFM_DAILYWATSOURCE',
                      #'OFM_DOWNREAS',
                      #'OFM_EVENTS',
                      'OFM_HEADERID',
                      #'OFM_TANKINV',
                      'OFM_TEST',
                      ]

        if preload:
            for t in TABLES:
                self.results[t] = pd.read_sql_query('SELECT * FROM ' + str(t), conn)
                conn.close()
        else:
            self.results[self.headertable] = pd.read_sql_query('SELECT * FROM OFM_HEADERID', conn)
            # not implemented

        self.keys = []
        for t in self.results:
            for c in t.columns:
                if self.uniqueID in t:
                    for uid in t[self.uniqueID].unique():
                        self.keys.append(c+str(self.nameSeparator)+uid)
                else:
                    self.keys.append(c)
        self.keys = tuple(set(self.keys))
        #self.keys = tuple(set([c+self.nameSeparator+uid for t in self.results for c in self.results[t] for uid in self.results[t][self.uniqueID].unique()]))

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

        if pattern is None:
            return self.keys
        else:
            keysList = [k for k in self.keys if pattern in key]
            # for key in self.keys:
            #     if pattern in key:
            #         keysList.append(key)
            return tuple(keysList)

    # support functions for get_Vector:
    def loadVector(self, key, table=None):
        """
        internal function to return a numpy vector from the Frame files
        """
        if table is not None:
            if table not in self.results:
                _verbose(self.speak, 1, "the table '"+str(table)+"' is not present in this database.")
            else:
                if key not in self.results[table]:
                    _verbose(self.speak, 1, "the key '"+str(key)+"' is not present in the table '"+str(table)"'.")
                    return None
                else:
                    return self.results[table][key]
        else:
            for table in self.results:
                if key in self.results[table]:
                    verbose(self.speak, 2, "loading key '"+str(key)+"' from table '"+str(table))
                    return self.loadVector(key, table)

    def extract_Wells(self):
        """
        Will return a list of all the well names in the case.
        """
        wellsList = self.results[self.headertable][self.uniqueID].unique().to_list()
        wellsList = sorted(list(set(wellsList)))
        self.wells = tuple(wellsList)
        return self.wells

    def extract_Groups(self):
        """
        Will return a list of all the group names in the case.
        """
        # groupsList = [K.split(self.nameSeparator)[-1].strip() for K in self.keys if ( K[0] == 'G' and self.nameSeparator in K)]
        # groupsList = sorted(list(set(groupsList)))
        self.groups = tuple()
        return self.groups

    def extract_Regions(self):
        """
        Will return a list of all the regions names or numbers in the case.
        """
        # preparing object attribute
        # regionsList = [K.split(self.nameSeparator)[-1].strip() for K in self.keys if ( K[0] == 'G' and self.nameSeparator in K)]
        # regionsList = sorted(list(set(regionsList)))
        return tuple()
