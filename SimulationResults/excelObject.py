# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 11:00:20 2021

@author: MCARAYA
"""

__version__ = '0.22.0'
__release__ = 220221
__all__ = ['XLSX']

from .mainObject import SimResult as _SimResult
from .._common.inout import _extension, _verbose
from .._common.functions import _mainKey
import pandas as pd
import os


class XLSX(_SimResult):
    """
    object to contain data read from .xlsx files

    """
    def __init__(self, inputFile=None, verbosity=2, sheet_name=None, header=[0, 1], units=1, overwrite=True, combine_SheetName_ColumnName=None, sheetName_auto='R', nameSeparator=':', **kwargs) :
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = XLSX
        self.results = {}
        self.Frames = {}
        self.FramesIndex = {}
        self.overwrite = False
        self.lastFrame = ''
        if sheetName_auto.upper().strip() in ('L','R'):
            self.sheetName_auto = sheetName_auto.upper().strip()
        else:
            self.sheetName_auto = 'R'
        self.nameSeparator = str(nameSeparator)
        self.commonIndex = None
        if 'frames' in kwargs or ( type(inputFile) is str and len(inputFile.strip()) > 0 ):
            if 'frames' in kwargs and kwargs['frames'] is not None:
                self.fromSimDataFrame(kwargs['frames'])
            elif os.path.isfile(inputFile) :
                self.readSimExcel(inputFile, sheet_name=sheet_name, header=header, units=units, combine_SheetName_ColumnName=combine_SheetName_ColumnName, **kwargs)
            else :
                print("file doesn't exists")
        if len(self.Frames) > 0 and inputFile is not None:
            self.name = _extension(inputFile)[1]
            # if 'TIME' not in self.keys :
            #     if 'DATE' in self.keys :
            #         TIME = np.array( [0] + list( self('DATE')[1:] - self('DATE')[:-1] ) )
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
        self.find_index(**kwargs)
        self.otherDateNames()
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

    def find_index(self,**kwargs):
        """
        identify the column that is common to all the frames, to be used as index.
        If there is a single frame the first column is used.
        """

        possibleKeys = ('DATE', 'DATES', 'Date', 'date', 'Dates', 'dates', 'TIME', 'Time', 'time', 'DAYS', 'Days', 'days', 'MONTHS', 'Months', 'months', 'YEARS', 'Years', 'years') + self.keys  # + tuple(map(_mainKey,self.FramesIndex.keys()))
        if 'index' in kwargs and kwargs['index'] in self.FramesIndex:
            possibleKeys = (kwargs['index'],) + possibleKeys
            self.DTindex = kwargs['index']
        # possibleKeys = tuple(set(possibleKeys))

        # check current KeyIndex
        KeyIndex = True
        IndexVector = None
        _verbose(self.speak, 1, "looking for a common index column.")
        _verbose(self.speak, 1, " default index name is: " + str(self.DTindex))
        for frame in self.Frames:
            _verbose(self.speak, 1, "checking frame: " + str(frame))
            if self.DTindex not in self.FramesIndex:
                KeyIndex = False
                break
            elif self.FramesIndex[self.DTindex][1] not in self.Frames[frame] :
                KeyIndex = False
                break
            elif IndexVector is None :
                IndexVector = self.Frames[frame][self.FramesIndex[self.DTindex][1]]
            elif not IndexVector.equals( self.Frames[frame][self.FramesIndex[self.DTindex][1]] ):
                KeyIndex = False
                break
        if KeyIndex:
            _verbose(self.speak, 1, "found the common index: " + str(self.DTindex))
            return self.DTindex

        # look for other identical index
        for Key in possibleKeys:

            IndexVector = None
            if Key not in self.FramesIndex:  # and Key not in map(_mainKey,self.FramesIndex):
                KeyIndex = False
            else:
                KeyIndex = True
                for frame in self.Frames :
                    if self.FramesIndex[Key][1] not in self.Frames[frame].columns:
                        KeyIndex = False
                        break
                    elif IndexVector is None :
                        IndexVector = self.Frames[frame][self.FramesIndex[Key][1]]
                    elif not IndexVector.equals( self.Frames[frame][self.FramesIndex[Key][1]] ):
                        KeyIndex = False
                        break

            if KeyIndex :
                self.DTindex = Key
                break

        # # look for other not indentical but common index
        # if not KeyIndex:
        #     for Key in ('DATE', 'DATES', 'TIME', 'DAYS', 'MONTHS', 'YEARS') + self.keys :
        #         KeyIndex = True
        #         IndexVector = None
        #         for frame in self.Frames :
        #             if Key not in self.FramesIndex :
        #                 KeyIndex = False
        #                 break
        #             if self.FramesIndex[Key][1] not in self.Frames[frame].columns :
        #                 KeyIndex = False
        #                 break
        #             elif IndexVector is None :
        #                 IndexVector = self.Frames[frame][self.FramesIndex[Key][1]]
        #             elif not IndexVector.equals( self.Frames[frame][self.FramesIndex[Key][1]] ) :
        #                 KeyIndex = False
        #                 break
        #         if KeyIndex :
        #             self.DTindex = Key
        #             break

        if KeyIndex :
            _verbose(self.speak, 1, "found the common index: " + str(self.DTindex))
            # create result vector for the common index
            IndexVector = None
            for frame in self.Frames:
                if IndexVector is None:
                    IndexVector = self.Frames[frame][self.DTindex]
                else:
                    IndexVector = pd.merge_ordered(IndexVector,self.Frames[frame][self.DTindex],on=self.DTindex,how='outer')
            self.add_Key(self.DTindex)
            self.TimeVector = self.DTindex
            _ = self.set_Vector(Key=self.DTindex, VectorData=IndexVector.to_numpy().reshape(-1,), Units=self.get_Units(self.DTindex), DataType='auto', overwrite=True)
            return self.DTindex
        else :
            _verbose(self.speak, 3, "not a common index name found.")
            self.DTindex = None

    def otherDateNames(self):
        if not self.is_Key('DATE') and not self.is_Key('DATES') :
            for datename in ['Date','date','Dates','dates','FECHA','Fecha','fecha','DATA','Data','data']:
                if self.is_Key(datename):
                    if 'date' in str(self.get_RawVector(datename)[datename].dtype):
                        try:
                            _ = self.set_Vector(Key='DATE', VectorData=self.get_RawVector(datename)[datename].reshape(-1,), Units='date', DataType='datetime', overwrite=True)
                            return
                        except:
                            pass

    def fromSimDataFrame(self,frame):
        self.units = frame.get_units()
        self.nameSeparator = frame.nameSeparator
        if frame.index.name is not None and frame.index.name not in frame.columns:
            indexName = frame.index.name
            self.DTindex = indexName
            frame.reset_index(inplace=True)
        self.Frames['sdf'] = frame
        self.name = 'from SimDataFrame'
        self.keys = frame.columns

    def readSimExcel(self, inputFile, sheet_name=None, header=[0, 1], units=1, combine_SheetName_ColumnName=None, **kwargs) :
        """
        internal function to read an excel file with SimDataFrame format (header in first row, units in second row)
        """
        from .._dictionaries import ECL2VIPkey
        ECLkeys = tuple(ECL2VIPkey.keys())
        cleaningList = []
        # def _foundNewKey():
        #     self.FramesIndex[NewKey] = ( each, col )
        #     if col[-1].startswith('Unnamed:') :
        #         NewUnits = ''
        #         unitsMessage = ''
        #     else :
        #         NewUnits = col[-1].strip()
        #         unitsMessage = " with units: '"+NewUnits+"'"
        #     self.add_Key( NewKey )
        #     self.set_Unit( NewKey, NewUnits )
        #     _verbose(self.speak, 1, " > found key: '" + NewKey + "'" + unitsMessage )

        if type(header) is int :
            if type(units) is int :
                if header != units :
                    header = [header, units]
        elif type(header) in [list, tuple] :
            if type(units) is int :
                if units not in header :
                    header = list(header)+[units]

        pdkwargs = kwargs.copy()
        for k in ['speak','verbosity','verbose','reload','preload','unload','ignoreSMSPEC','index','frames']:
            if k in pdkwargs:
                del pdkwargs[k]
        try :
            NewFrames = pd.read_excel(inputFile, sheet_name=sheet_name, header=header, **pdkwargs)
        except OSError:
            raise OSError("[Errno 24] Too many open files: " + str(inputFile) + '\nPlease close some other files.')
        except ImportError:
            raise ImportError("Missing optional dependencies 'xlrd' and 'openpyxl'.\nInstall xlrd and openpyxl for Excel support.\nUse pip or conda to install xlrd and install openpyxl.")
        except :
            try:
                import xlrd
                try:
                    import openpyxl
                except:
                    raise ModuleNotFoundError("Missing optional dependency 'openpyxl'.\nInstall openpyxl for Excel support.\nUse pip or conda to install openpyxl.")
            except:
                raise ModuleNotFoundError("Missing optional dependency 'xlrd'.\nInstall xlrd for Excel support.\nUse pip or conda to install xlrd.")
            raise TypeError('Not able to read the excel file, please check input parameters and excel sheets format.')

        if sheet_name is not None and type(NewFrames) is not dict :
            NewFrames = {str(sheet_name):NewFrames}

        if bool(combine_SheetName_ColumnName):
            if type(combine_SheetName_ColumnName) in (int,float):
                combine_SheetName_ColumnName = [combine_SheetName_ColumnName]
            elif type(combine_SheetName_ColumnName) is str and combine_SheetName_ColumnName.upper().strip() in ['RIGHT','LEFT','R','L']:
                if combine_SheetName_ColumnName in NewFrames:
                    _verbose(self.speak, 3, "WARNING: The paramater combine_SheetName_ColumnName is set to " + combine_SheetName_ColumnName +
                             " but this is also the name a sheet in the workbook.\n It will be considered as the " + combine_SheetName_ColumnName +
                             " option of the parameter. To set it as the sheet name provide the name of the sheet in a list: [" + combine_SheetName_ColumnName + "]")
                combine_SheetName_ColumnName = combine_SheetName_ColumnName.upper()[0]
            elif type(combine_SheetName_ColumnName) is str:
                combine_SheetName_ColumnName = [combine_SheetName_ColumnName]
            elif combine_SheetName_ColumnName is True:
                if len(NewFrames.keys()) == 1:
                    _verbose(self.speak, 2, " > You have requested to combine the name of the sheets with the names of the columns, but this excel file has only ONE sheet.\n If prefer not to combine the sheet name '" + str(list(NewFrames.keys())[0]) + "' with the name of every column set the parameter combine_SheetName_ColumnName=False")
                combine_SheetName_ColumnName = list(NewFrames.keys())
            else:
                try:
                    combine_SheetName_ColumnName = list(combine_SheetName_ColumnName)
                except:
                    raise TypeError("not able to understand combine_SheetName_ColumnName parameter.")
        elif combine_SheetName_ColumnName is None:
            if len(NewFrames.keys()) == 1:
                combine_SheetName_ColumnName = False
            else:
                allColumns = []
                for nf in NewFrames:
                    allColumns += list(NewFrames[nf].columns)
                if len(set(allColumns)) == len(allColumns):
                    combine_SheetName_ColumnName = False
                else:
                    columnsKeys, sheetnameKeys = 0, 0
                    for k in ['OPR','GPR','WPR','GIR','WIR','BHP','THP']:
                        sheetnameKeys += len( [ sn for sn in NewFrames.keys() if k in str(sn) ] )
                        columnsKeys += len( [ co for sn in NewFrames.keys() for co in NewFrames[sn] if k in str(co) ] )
                    if columnsKeys >= sheetnameKeys:
                        combine_SheetName_ColumnName = 'R'
                    else:
                        combine_SheetName_ColumnName = 'L'
        else:
            combine_SheetName_ColumnName = False

        for each in NewFrames :
            if each not in self.Frames :
                self.Frames[str(each)] = NewFrames[each]
                for col in NewFrames[each].columns :
                    NewKey = ' '.join(col[0:-1]).strip()

                    if combine_SheetName_ColumnName == 'R':
                        NewKey = NewKey + self.nameSeparator + str(each).strip()
                    elif combine_SheetName_ColumnName == 'L':
                        NewKey = str(each).strip() + self.nameSeparator + NewKey
                    elif type(combine_SheetName_ColumnName) is list:
                        if ( each in combine_SheetName_ColumnName and self.sheetName_auto == 'R' ) \
                            or (each,'R') in combine_SheetName_ColumnName or (each,'r') in combine_SheetName_ColumnName \
                                or ('R', each) in combine_SheetName_ColumnName or('r', each) in combine_SheetName_ColumnName:
                                    NewKey = NewKey + self.nameSeparator + str(each).strip()
                        if ( each in combine_SheetName_ColumnName and self.sheetName_auto == 'L' ) \
                            or (each,'R') in combine_SheetName_ColumnName or (each,'r') in combine_SheetName_ColumnName \
                                or ('R', each) in combine_SheetName_ColumnName or ('r', each) in combine_SheetName_ColumnName:
                                    NewKey = str(each).strip() + self.nameSeparator + NewKey

                    if NewKey in self.FramesIndex:
                        #if ( NewFrames[each][col].values == self.Frames[ self.FramesIndex[NewKey][0] ][ self.FramesIndex[NewKey][1] ].values ).all():
                        if NewFrames[each][col].equals( self.Frames[ self.FramesIndex[NewKey][0] ][ self.FramesIndex[NewKey][1] ] ):
                            # both columns contains the same data
                            _verbose(self.speak, 1, " > skipping duplicated key: '" + NewKey + "' with duplicated data." )
                        # elif NewKey.strip().upper() in ('TIME','DATE','YEAR','YEARS','MONTH','MONTHS','DAY','DAYS'):
                        #     if min( self.Frames[ self.FramesIndex[NewKey][0] ][ self.FramesIndex[NewKey][1] ) <= min( NewFrames[each][col] ) and max( self.Frames[ self.FramesIndex[NewKey][0] ][ self.FramesIndex[NewKey][1] ) >= max( NewFrames[each][col] ):
                        #         _verbose(self.speak, 1, " > skipping key: '" + NewKey + "' contained in data from previous key." )
                        else:
                            if bool(combine_SheetName_ColumnName) is True and self.nameSeparator not in str(NewKey):
                                cleaningList.append(NewKey)  # to later remove the key

                                # rename the other Key
                                otherFrame = self.FramesIndex[NewKey][0]
                                if str(otherFrame) in ECLkeys or str(otherFrame)[1:4] in ECLkeys:
                                    NewOtherKey = str(otherFrame).strip() + self.nameSeparator + NewKey
                                else:
                                    NewOtherKey = NewKey + self.nameSeparator + str(otherFrame).strip()
                                if NewOtherKey not in self.FramesIndex:
                                    self.FramesIndex[NewOtherKey] = ( self.FramesIndex[NewKey][0] , self.FramesIndex[NewKey][1] )
                                    self.add_Key( NewOtherKey )
                                    self.set_Unit( NewOtherKey, self.get_Unit(NewKey) )
                                    _verbose(self.speak, 1, " > renamed key: '" + NewKey + "' to '" + NewOtherKey + "'")

                                # rename this frame key
                                if str(each) in ECLkeys or str(each)[1:4] in ECLkeys:
                                    NewKey = str(each).strip() + self.nameSeparator + NewKey
                                else:
                                    NewKey = NewKey + self.nameSeparator + str(each).strip()

                            elif combine_SheetName_ColumnName is False or self.nameSeparator in str(otherFrame):
                                NewKey = NewKey + '_' + str( list(self.FramesIndex.keys()).count(NewKey) +1 )

                            self.FramesIndex[NewKey] = ( each, col )
                            if col[-1].startswith('Unnamed:') :
                                NewUnits = ''
                                unitsMessage = ''
                            else :
                                NewUnits = col[-1].strip()
                                unitsMessage = " with units: '"+NewUnits+"'"
                            self.add_Key( NewKey )
                            self.set_Unit( NewKey, NewUnits )
                            _verbose(self.speak, 1, " > found key: '" + NewKey + "'" + unitsMessage)

                    else:
                        self.FramesIndex[NewKey] = ( each, col )
                        if col[-1].startswith('Unnamed:') :
                            NewUnits = ''
                            unitsMessage = ''
                        else :
                            NewUnits = col[-1].strip()
                            unitsMessage = " with units: '"+NewUnits+"'"
                        self.add_Key( NewKey )
                        self.set_Unit( NewKey, NewUnits )
                        _verbose(self.speak, 1, " > found key: '" + NewKey + "'" + unitsMessage)
                        # _foundNewKey()
                        if bool(combine_SheetName_ColumnName) is True and self.nameSeparator not in str(NewKey):
                            cleaningList.append(NewKey)  # to later remove the key

                            # rename the other Key
                            otherFrame = self.FramesIndex[NewKey][0]
                            if str(otherFrame) in ECLkeys or str(otherFrame)[1:4] in ECLkeys:
                                NewOtherKey = str(otherFrame).strip() + self.nameSeparator + NewKey
                            else:
                                NewOtherKey = NewKey + self.nameSeparator + str(otherFrame).strip()
                            if NewOtherKey not in self.FramesIndex:
                                self.FramesIndex[NewOtherKey] = ( self.FramesIndex[NewKey][0] , self.FramesIndex[NewKey][1] )
                                self.add_Key( NewOtherKey )
                                self.set_Unit( NewOtherKey, self.get_Unit(NewKey) )
                                _verbose(self.speak, 1, " > renamed key: '" + NewKey + "' to '" + NewOtherKey + "'")

            elif self.Frames[str(each)].equals(NewFrames[each]) :
                _verbose(self.speak, 2, "the sheet '"+each+"' was already loaded.")

            else :
                if self.overwrite :
                    _verbose(self.speak, 2, "the sheet '"+str(each)+"' will overwrite the previously loaded sheet.")
                else :
                    i = 1
                    while str(each)+'_'+str(i).zfill(2) in self.Frames :
                        i += 1
                    _verbose(self.speak, 2, "the sheet '"+str(each)+"' will be loaded as '"+str(each)+'_'+str(i).zfill(2)+"' to not overwrite the previously loaded sheet.")
                    self.Frames[str(each)+'_'+str(i).zfill(2)] = NewFrames[each]
                    for col in NewFrames[each].columns :
                        NewKey = ' '.join(list(map(str,col[0:-1]))).strip()
                        self.FramesIndex[NewKey] = ( str(each)+'_'+str(i).zfill(2), col )
                        if col[-1].startswith('Unnamed:') :
                            NewUnits = ''
                            unitsMessage = ''
                        else :
                            NewUnits = col[-1].strip()
                            unitsMessage = " with units: '"+NewUnits+"'"
                        self.add_Key( NewKey )
                        userVerbose, self.speak = self.speak, 0
                        self.set_Unit( NewKey, NewUnits )
                        self.speak = userVerbose
                        _verbose(self.speak, 1, " > found key: '"+NewKey+"'" + unitsMessage )

        # if len(cleaningList) > 0:
        #     self.keys = tuple(set( [ K for K in self.keys if K not in set(cleaningList) ] ))
        #     for K in cleaningList:
        #         if K in self.units:
        #             del self.units[K]
        #         if K in self.FramesIndex:
        #             del self.FramesIndex[K]

            columnsList = [ str(col[0] if type(col) is tuple else col) for frame in self.Frames for col in self.Frames[frame].columns  ]
            commonIndex = None
            for timeK in ['DATE','DATES','TIME','DAYS','MONTHS','YEARS']:
                if timeK in list(map(str.upper,map(_mainKey,columnsList))):
                    commonIndex = None
                    commonTimeK = timeK
                    for frame in self.Frames:
                        if timeK in [ str(col[0] if type(col) is tuple else col).strip().upper() for col in self.Frames[frame].columns ]:
                            candidate = self.Frames[frame][ [ col for col in self.Frames[frame].columns if str(col[0]).strip().upper() == timeK ][0] ]
                            candidate.rename(timeK, inplace=True)
                            if commonIndex is None:
                                commonIndex = candidate
                            else:
                                try:
                                    commonIndex = pd.merge_ordered( commonIndex, candidate, on=timeK, how='outer' )
                                except ValueError:
                                    if timeK in ['DATE','DATES']:
                                        raise ValueError('column ' + str(timeK) + ' has values that are not in date format in sheet ' + str(frame) + '.')
                                    else:
                                        raise ValueError('index column ' + str(timeK) + ' has different kind of values in sheet ' + str(frame) + '.')
                        else:
                            commonIndex = None
                            commonTimeK = None
                            break
                    if commonIndex is not None:
                        break
            if commonIndex is not None:
                if isinstance(commonIndex,pd.Series):
                    self.commonIndex = ( commonTimeK, pd.Index(commonIndex.values) )
                elif isinstance(commonIndex,pd.DataFrame):
                    self.commonIndex = ( commonTimeK, commonIndex.set_index(commonTimeK).index )
                self.FramesIndex[self.commonIndex[0]] = ( list(self.Frames.keys())[0], self.commonIndex[0] )
                for frame in self.Frames:
                    thisTimeK = [ col for col in self.Frames[frame].columns if str(col[0]).strip().upper() == self.commonIndex[0] ][0]
                    self.Frames[frame] = self.Frames[frame].set_index(thisTimeK, drop=True).reindex(index=self.commonIndex[1], method=None)
                    colsBefore = list(self.Frames[frame].columns)
                    self.Frames[frame] = self.Frames[frame].reset_index()
                    colsAfter = list(self.Frames[frame].columns)
                    indexName = [ c for c in colsAfter if c not in colsBefore ][0]
                    if type(indexName) is tuple:
                        indexName = indexName[0]
                    self.Frames[frame] = self.Frames[frame].rename(columns={indexName:self.commonIndex[0]})
                    if type(thisTimeK) is tuple:
                        partK = str(thisTimeK[0]).strip()
                    else:
                        partK = str(thisTimeK)

                    if partK + self.nameSeparator + frame in self.FramesIndex:
                        del self.FramesIndex[ partK + self.nameSeparator + frame ]
                    elif frame + self.nameSeparator + partK in self.FramesIndex:
                        del self.FramesIndex[ frame + self.nameSeparator + partK ]

                    if partK + self.nameSeparator + frame in self.units:
                        del self.units[ partK + self.nameSeparator + frame ]
                    elif frame + self.nameSeparator + partK in self.units:
                        del self.units[ frame + self.nameSeparator + partK ]

                    self.keys = tuple([ K for K in self.keys if K != (partK + self.nameSeparator + frame) and K != (frame + self.nameSeparator + partK) ])


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
    def loadVector(self, key, Frame=None) :
        """
        internal function to return a numpy vector from the Frame files
        """
        if Frame is None and key not in self.FramesIndex:
            if ':' in key:
                if key.split(':')[0] in self.FramesIndex and key.split(':')[-1] in self.Frames:
                    return self.loadVector(key.split(':')[0], key.split(':')[-1])
                elif key.split(':')[-1] in self.FramesIndex and key.split(':')[0] in self.Frames:
                    return self.loadVector(key.split(':')[-1], key.split(':')[0])
        elif Frame is None and key in self.FramesIndex:
            Frame = self.FramesIndex[key][0]
        elif Frame in self.Frames:
            pass # OK
        else :
            _verbose(self.speak, 1, "the key '"+key+"' is not present in these frames.")
            return None
        if self.lastFrame == '':
            self.lastFrame = Frame

        if key == self.DTindex:
            if self.lastFrame in self.Frames and key in self.Frames[self.lastFrame]:
                return self.Frames[self.lastFrame][self.FramesIndex[key][1]].to_numpy()
            elif key in self.FramesIndex :
                result = self.Frames[Frame][self.FramesIndex[key][1]]
                if len(result) == len(self.Frames[self.lastFrame]) :
                    return result.to_numpy()
                else :
                    return self.Frames[self.lastFrame].index.to_numpy()
            else :
                return None
        elif key in self.FramesIndex:
            result = self.Frames[Frame][self.FramesIndex[key][1]].to_numpy()
            self.lastFrame = Frame
            return result

    # def extract_Wells(self) :
    #     """
    #     Will return a list of all the well names in case.

    #     If the pattern variable is different from None only groups
    #     matching the pattern will be returned; the matching is based
    #     on fnmatch(), i.e. shell style wildcards.
    #     """
    #     wellsList = [ K.split(':')[-1].strip() for K in self.keys if ( K[0] == 'W' and ':' in K ) ]
    #     wellsList = list( set( wellsList ) )
    #     wellsList.sort()
    #     self.wells = tuple( wellsList )

    #     return self.wells

    # def extract_Groups(self, pattern=None, reload=False) :
    #     """
    #     Will return a list of all the group names in case.

    #     If the pattern variable is different from None only groups
    #     matching the pattern will be returned; the matching is based
    #     on fnmatch(), i.e. shell style wildcards.
    #     """
    #     groupsList = [ K.split(':')[-1].strip() for K in self.keys if ( K[0] == 'G' and ':' in K ) ]
    #     groupsList = list( set( groupsList ) )
    #     groupsList.sort()
    #     self.groups = tuple( groupsList )
    #     if pattern is not None :
    #         results = []
    #         for group in self.groups :
    #             if pattern in group :
    #                 results.append(group)
    #         return tuple(results)
    #     else :
    #         return self.groups

    # def extract_Regions(self, pattern=None) :
    #     # preparing object attribute
    #     regionsList = [ K.split(':')[-1].strip() for K in self.keys if ( K[0] == 'G' and ':' in K ) ]
    #     regionsList = list( set( regionsList ) )
    #     regionsList.sort()
    #     self.groups = tuple( regionsList )
    #     if pattern is not None :
    #         results = []
    #         for group in self.groups :
    #             if pattern in group :
    #                 results.append(group)
    #         return tuple(results)
    #     else :
    #         return self.groups

    # def get_Unit(self, Key='--EveryType--') :
    #     """
    #     returns a string identifiying the unit of the requested Key

    #     Key could be a list containing Key strings, in this case a dictionary
    #     with the requested Keys and units will be returned.
    #     the Key '--EveryType--' will return a dictionary Keys and units
    #     for all the keys in the results file

    #     """
    #     if type(Key) is str and Key.strip() != '--EveryType--' :
    #         Key = Key.strip().upper()
    #         if Key in self.units :
    #             return self.units[Key]
    #         if Key in ['DATES','DATE'] :
    #                 self.units[Key] = 'DATE'
    #                 return 'DATE'
    #         # if Key in self.keys :
    #         #     return 'unitless'
    #         # else:
    #         #     UList = None
    #         #     if Key[0] == 'W' :
    #         #         UList=[]
    #         #         for W in self.get_Wells() :
    #         #             if Key+':'+W in self.units :
    #         #                 UList.append(self.units[Key+':'+W])
    #         #             elif Key in self.keys :
    #         #                 UList.append( self.results.unit(Key+':'+W) )
    #         #         if len(set(UList)) == 1 :
    #         #             self.units[Key] = UList[0]
    #         #             return UList[0]
    #         #         else :
    #         #             UList = None
    #         #     elif Key[0] == 'G' :
    #         #         UList=[]
    #         #         for G in self.get_Groups() :
    #         #             if Key+':'+G in self.units :
    #         #                 UList.append(self.units[Key+':'+G])
    #         #             elif Key in self.keys :
    #         #                 UList.append( self.results.unit(Key+':'+G) )
    #         #         if len(set(UList)) == 1 :
    #         #             self.units[Key] = UList[0]
    #         #             return UList[0]
    #         #         else :
    #         #             UList = None
    #         #     elif Key[0] == 'R' :
    #         #         UList=[]
    #         #         for R in self.get_Regions() :
    #         #             if Key+':'+R in self.units :
    #         #                 UList.append(self.units[Key+':'+R])
    #         #             elif Key in self.keys :
    #         #                 UList.append( self.results.unit(Key+':'+R) )
    #         #         if len(set(UList)) == 1 :
    #         #             self.units[Key] = UList[0]
    #         #             return UList[0]
    #         #         else :
    #         #             UList = None
    #         # if UList is None:
    #         #     if ':' in Key:
    #         #         if Key.split(':')[0] in self.FramesIndex and Key.split(':')[-1] in self.Frames:
    #         #             return self.get_Unit(Key.split(':')[0])
    #         #         elif Key.split(':')[-1] in self.FramesIndex and Key.split(':')[0] in self.Frames:
    #         #             return self.get_Unit(Key.split(':')[-1])
    #         if Key in self.keys :
    #             if ':' in Key :
    #                 if Key[0] == 'W' :
    #                     if Key.split(':')[-1] in self.wells :
    #                         return self.get_Unit(Key.split(':')[0])
    #                 if Key[0] == 'G' :
    #                     if Key.split(':')[-1] in self.groups :
    #                         return self.get_Unit(Key.split(':')[0])
    #                 if Key[0] == 'R' :
    #                     if Key.split(':')[-1] in self.regions :
    #                         return self.get_Unit(Key.split(':')[0])
    #             return None
    #         else:
    #             if Key[0] == 'W' :
    #                 UList=[]
    #                 for W in self.get_Wells() :
    #                     if Key+':'+W in self.units :
    #                         UList.append(self.units[Key+':'+W])
    #                 if len(set(UList)) == 1 :
    #                     self.units[Key] = UList[0]
    #                     return UList[0]
    #                 else :
    #                     return None
    #             elif Key[0] == 'G' :
    #                 UList=[]
    #                 for G in self.get_Groups() :
    #                     if Key+':'+G in self.units :
    #                         UList.append(self.units[Key+':'+G])
    #                 if len(set(UList)) == 1 :
    #                     self.units[Key] = UList[0]
    #                     return UList[0]
    #                 else :
    #                     return None
    #             elif Key[0] == 'R' :
    #                 UList=[]
    #                 for R in self.get_Regions() :
    #                     if Key+':'+R in self.units :
    #                         UList.append(self.units[Key+':'+R])
    #                 if len(set(UList)) == 1 :
    #                     self.units[Key] = UList[0]
    #                     return UList[0]
    #                 else :
    #                     return None
    #             UList = None

    #     elif type(Key) is str and Key.strip() == '--EveryType--' :
    #         Key = []
    #         KeyDict = {}
    #         for each in self.keys :
    #             if ':' in each :
    #                 Key.append( _mainKey(each) )
    #                 KeyDict[ _mainKey(each) ] = each
    #             else :
    #                 Key.append(each)
    #         Key = list( set (Key) )
    #         Key.sort()
    #         tempUnits = {}
    #         for each in Key :
    #             if each in self.units :
    #                 tempUnits[each] = self.units[each]
    #             elif each in self.keys and ( each != 'DATES' and each != 'DATE' ) :
    #                 if self.results.unit(each) is None :
    #                     tempUnits[each] = self.results.unit(each)
    #                 else :
    #                     tempUnits[each] = self.results.unit(each).strip('( )').strip("'").strip('"')
    #             elif each in self.keys and ( each == 'DATES' or each == 'DATE' ) :
    #                 tempUnits[each] = 'DATE'
    #             else :
    #                 if KeyDict[each] in self.units :
    #                     tempUnits[each] = self.units[KeyDict[each]]
    #                 elif KeyDict[each] in self.keys :
    #                     if self.results.unit(KeyDict[each]) is None :
    #                         tempUnits[each] = self.results.unit(KeyDict[each])
    #                     else :
    #                         tempUnits[each] = self.results.unit(KeyDict[each]).strip('( )').strip("'").strip('"')
    #         return tempUnits
    #     elif type(Key) in [list,tuple] :
    #         tempUnits = {}
    #         for each in Key :
    #             if type(each) == str :
    #                 tempUnits[each] = self.get_Unit(each)
    #         return tempUnits
