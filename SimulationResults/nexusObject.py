# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:34:04 2020

@author: MCARAYA
"""

__version__ = '0.1.1'
__release__ = 220113
__all__ = ['NEXUS']

from .mainObject import SimResult as _SimResult
from .._common.inout import _extension, _verbose
from .._common.functions import _mainKey, _wellFromAttribute
from .._common.stringformat import date as _strDate, getnumber as _getnumber
from .._common.keywordsConversions import fromECLtoVIP as _fromECLtoVIP, fromVIPtoECL as _fromVIPtoECL #, fromCSVtoECL
from .._dictionaries import UniversalKeys as _UniversalKeys, VIPTypesToExtractVectors as _VIPTypesToExtractVectors
from .._dictionaries import VIP2ECLtype as _VIP2ECLtype, VIP2ECLkey as _VIP2ECLkey, ECL2VIPkey as _ECL2VIPkey #, ECL2VIPtype, ECL2VIPkey
# from datafiletoolbox.dictionaries import ECL2CSVtype, ECL2CSVkey, CSV2ECLtype, CSV2ECLkey
# from datetime import timedelta
import pandas as pd
import numpy as np
import os


class NEXUS(_SimResult):
    """
    object to contain VIP results read from .sss ASCII output
    """

    def __init__(self, inputFile=None, verbosity=2, **kwargs) :
        _SimResult.__init__(self, verbosity=verbosity)
        self.kind = NEXUS
        self.ECLstyle=True
        self.VIPstyle=False
        self.keysECL = ()
        self.keysVIP = ()
        # self.keysCSV = ()
        self.results = {}
        # self.CSV = False
        self.VIPnotECL = []
        self.LPGcorrected = False
        if type(inputFile) == str and len(inputFile.strip()) > 0 :
            self.selectLoader(inputFile)
        self.initialize(**kwargs)

    def keys(self) :
        if self.ECLstyle :
            return self.keysECL
        if self.VIPstyle :
            return self.keysVIP

    def initialize(self, **kwargs) :
        """
        run intensive routines, to have the data loaded and ready
        """
        self.stripUnits()
        self.fill_FieldBasics()
        self.get_Attributes(reload=True)
        self.complete_Units()
        self.regionNumber = self.extract_Region_Numbers()
        self.buldSalinityVectors()
        self.get_TotalReservoirVolumes()
        _SimResult.initialize(self, **kwargs)

    def selectLoader(self, inputFile) :
        if type(inputFile) == str and len(inputFile.strip()) > 0 :
            inputFile = inputFile.strip()
        if _extension(inputFile)[0].upper() == '.CSV' :
            from datafiletoolbox.SimulationResults.CSVSimResultNexusDesktopObject import NexusDesktopCSV
            return NexusDesktopCSV( inputFile, self.speak )
        elif _extension(inputFile)[0].upper() == '.SSS' :
            self.loadSSS(inputFile)
        elif _extension(inputFile)[0].upper() == '.DAT' :
            for sss in [ '_field.sss', '_well.sss', '_region.sss', '_area.sss', '_flow.sss', '_node.sss', '_gather.sss' ] :
                sssFile = None
                if os.path.isfile( _extension(inputFile)[1] + sss ) :
                    sssFile = _extension(inputFile)[1] + sss
                    break
            if sssFile is not None :
                self.loadSSS(sssFile)
            else :
                _verbose( self.speak, 3, " not possible to find SSS file for the .dat file\n   '" + inputFile + "'")

    def use_ECLstyle(self):
        if len(self.keysECL) == 0 :
            _verbose( self.speak, 0, ' ECL style keys: ' + str( self.extract_Keys() ) )
        if len(self.keysECL) > 0 :
            self.keys = self.keysECL
            _verbose( self.speak, 0, ' attributes as ECL style: ' + str( self.get_Attributes() ) )
            self.ECLstyle = True
            self.VIPstyle = False
            _verbose( self.speak, 3, ' Using ECL style keys')
        else :
            self.VIPstyle = 'ERROR'
            _verbose( self.speak, 3, ' Unable to convert to ECL style keys')
            if type(self.ECLstyle) is bool :
                self.use_VIPstyle()
        self.complete_Units()

    def use_VIPstyle(self):
        if len(self.keysVIP) == 0 :
            _verbose( self.speak, 0, ' VIP style keys: ' + str( self.extract_Keys() ) )
        if len(self.keysVIP) > 0 :
            self.keys = self.keysVIP
            _verbose( self.speak, 0, 'attributes as VIP style: ' + str( self.get_Attributes() ) )
            self.ECLstyle = False
            self.VIPstyle = True
            _verbose( self.speak, 3, ' Using VIP style keys')
        else :
            self.ECLstyle = 'ERROR'
            _verbose( self.speak, 3, ' Unable to get VIP style keys.')
            if type(self.VIPstyle) is bool :
                self.use_ECLstyle()
        self.complete_Units()

    def get_Style(self) :
        if self.VIPstyle is True and self.ECLstyle is False :
            return 'using VIP style'
        if self.ECLstyle is True and self.VIPstyle is False :
            return 'using ECL style'
        return 'error in style, highly recommended to regenerate style'

    def loadSSS(self, SSSFilePath):
        if type(SSSFilePath) == str :
            SSSFilePath = SSSFilePath.strip()
            if self.path is None :
                self.path = SSSFilePath

            self.SSSfiles = self.SSSparts( SSSFilePath )
            self.name = _extension(SSSFilePath)[1]
            for file in self.SSSfiles :
                self.results[ _extension(file)[1] + _extension(file)[0] ] = self.SSSread( file )
            self.strip('NAME')
            self.set_FieldTime()
            self.get_Vector('DATE')
            self.get_Wells(reload=True)
            self.get_Groups(reload=True)
            self.get_Regions(reload=True)
            self.get_Keys(reload=True)
            self.units = self.get_Unit(self.keys)
            _verbose( self.speak, 1, 'simulation runs from ' +  str( self.get_Dates()[0] ) + ' to ' + str( self.get_Dates()[-1] ) )
        else :
            print("SummaryFilePath must be a string")

    def correction_for_LPG_from_VIPsss(self) :
        if self.LPGcorrected :
            _verbose( self.speak, 2, 'LPG correction for VIP sss reports is already applied.')
        else :
            for LPGkey in ( 'LPG LIQ RATE', 'FULPGLR'  ) :
                if self.is_Key( LPGkey ) :
                    Before = self.get_Vector(LPGkey)[LPGkey]
                    Corrected = Before * 0.1292 / 33.4962
                    self.set_Vector( LPGkey, Corrected, self.get_Unit(LPGkey), DataType='float', overwrite=True )
                    self.LPGcorrected = True
                    _verbose( self.speak, 2, 'Successfully applied LPG correction for VIP sss reports.')

    def reload(self) :
        # if self.CSV is False :
        #     self.loadSSS(self.path)
        # else :
        #     self.loadCSV(self.path)
        self.loadSSS(self.path)

    def strip(self, VIPkey, stringToStrip=' ') :
        """
        applies .strip() method to every item in a Key of the results dictionaries
        """
        for sss in self.results.keys() :
            for i in range(len( self.results[sss][1]['Data'][ VIPkey ] )) :
                if type( self.results[sss][1]['Data'][ VIPkey ][i] ) == str :
                    self.results[sss][1]['Data'][ VIPkey ][i] = self.results[sss][1]['Data'][ VIPkey ][i].strip(stringToStrip)

    def SSSparts(self, SSSFilePath):
        SSSfiles = []
        expectedParts = [ ( '.ss_field', '.ss_network', '.ss_regions', '.ss_targets', '.ss_wells' ) ] #,
                          # ( '_FIELD.SSS', '_AREA.SSS', '_FLOW.SSS', '_GATHER.SSS', '_REGION.SSS', '_WELL.SSS' ) ]
        if _extension(SSSFilePath)[0].upper() == '.SSS' :
            for Case in expectedParts :
                for part in Case :
                    if part in SSSFilePath and SSSFilePath[SSSFilePath.index(part):] == part:
                        SSSroot = SSSFilePath[:SSSFilePath.index(part)]
                        break
                for part in Case :
                    if os.path.isfile(SSSroot + part) :
                        SSSfiles.append(SSSroot + part)
                if len( SSSfiles ) > 0 :
                    return tuple( SSSfiles )
            if os.path.isfile(SSSFilePath) : # if this line is reached, implicitly len( SSSfiles ) == 0
                return tuple ( SSSFilePath )
            else :
                raise FileNotFoundError('No such file or related VIP files found for: ' + str(SSSFilePath) )

        else : # if _extension(SSSFilePath)[0] != '.SSS' :
            SSSroot = _extension(SSSFilePath)[2] + _extension(SSSFilePath)[1]
            for Case in expectedParts :
                for part in Case :
                    if os.path.isfile(SSSroot + part) :
                        SSSfiles.append(SSSroot + part)
                if len( SSSfiles ) > 0 :
                    return tuple( SSSfiles )

        if len( SSSfiles ) == 0 :
            raise FileNotFoundError('No such file or related VIP files found for: ' + str(SSSFilePath) )

    def SSSread(self, sssPath) :
        _verbose( self.speak, 1, '\nREADING ' + str(sssPath) )
        sssfile = open(sssPath, 'r')
        sss = sssfile.read()
        sssfile.close()
        sss = sss.split('\n')

        sssType = sss[0].split()[0]
        _verbose( self.speak, 1, 'Type of data in this input file: ' + str(sssType) )

        sssColumns = sss[1].split('\t')
        for i in range(len(sssColumns)):
            sssColumns[i] = sssColumns[i].strip()

        sssUnits = sss[2].split('\t')
        for i in range(len(sssUnits)):
            sssUnits[i] = sssUnits[i].strip()

        sssClean = []
        for i in range(len(sss[3:])) :
            if len(sss[3+i].strip()) > 0 :
                sssClean.append(sss[3+i])

        sssData = []
        sssData = '\t'.join(sssClean).split('\t')

        sssDict = { 'Data' : {}, 'Units' : {} }

        for i in range(len(sssColumns)) :
            sssDict['Data'][sssColumns[i]] = sssData[i::len(sssColumns)]
        for i in range(len(sssColumns)) :
            sssDict['Units'][sssColumns[i]] = sssUnits[i]

        if self.speak !=0 :
            _verbose( self.speak, 1, ' data found in the ' + str(sssType) + ' summary file:')
            for each in sssDict['Data'] :
                _verbose( self.speak, 1, '  > ' + str(each) + str( ' ' * (16-len(str(each))) ) + ' with ' + str(len(sssDict['Data'][each])) + ' rows with units: ' + str( sssDict['Units'][each] ) )

        return ( sssType, sssDict )

    # support functions for get_Vector:
    def loadVector(self, key, SSStype=[], forceVIP=False) :
        """
        internal function to load a numpy vector from the summary files
        """

        def alreadyVIP(key, SSStype):
            wellVIPkeys = ('BHP', 'THP')
            if ':' in key :
                VIPkey = key[:key.index(':')]
                keyName = key[key.index(':')+1:]
            else :
                VIPkey = key
                if key in wellVIPkeys :
                    keyName = list(self.get_Wells())
                    SSStype = ['WELL']
                elif VIPkey in _UniversalKeys :
                    keyName = 'ROOT'
                    SSStype = ['FIELD']
                else :
                    keyName = 'ROOT'
            if len( SSStype ) > 1 :
                if keyName == 'ROOT' :
                    keyType = 'FIELD'
                else :
                    _verbose( self.speak, 2, 'none or more than one type summary were selected, ')
                    keyType = SSStype
            else :
                keyType = SSStype[0]

            _verbose( self.speak, 1, 'identified VIP key ' + VIPkey + ' for ' + str(keyType) + ' summary for the item ' + keyName )
            return VIPkey, keyType, keyName

      ####################### end of auxiliar functions #######################

        if SSStype == [] : # and self.CSV is False:
            for sss in list(self.results.keys()) :
                SSStype += [self.results[sss][0]]
        elif type(SSStype) == str :
            SSStype = [SSStype]

        key = str(key).strip().upper()
        if forceVIP :
            _verbose( self.speak, 1, 'forced to use inputs as VIP keywords')
        if self.ECLstyle is True and forceVIP is False:
            # if key in self.keysECL :
            try :
                VIPkey, keyType, keyName = _fromECLtoVIP( key, self.speak )
            except :
                try :
                    VIPkey, keyType, keyName = alreadyVIP(key, SSStype)
                except :
                    pass

        else : # VIP style first
            try :
                VIPkey, keyType, keyName = alreadyVIP(key, SSStype)
            except :
                try :
                    VIPkey, keyType, keyName = _fromECLtoVIP( key, self.speak )
                except :
                    pass

        if type(keyType) == str :
            keyTypeList = tuple([keyType])
        else :
            keyTypeList = tuple(keyType[:])


        ###### in case of CSV load :
        # if self.CSV != False :
        #     return self.CSVloadVector( key, VIPkey, keyType, keyName )
        ###### in case of CSV load.

        for keyType in keyTypeList :

            if keyType in SSStype :
                if keyType == 'FIELD' :
                    for sss in list(self.results.keys()) :
                        if self.results[sss][0] == keyType :
                            if VIPkey in self.results[sss][1]['Data'].keys() :
                                RawCol = np.array( self.results[sss][1]['Data'][ VIPkey ] )
                                _verbose( self.speak, 1, 'extracted ' + VIPkey + ' from ' + keyType + ' with lenght ' + str(len(RawCol)) )
                                try :
                                    RawCol = RawCol.astype(int)
                                    _verbose( self.speak, 1, 'the values were converted to integer type')
                                except :
                                    try :
                                        RawCol = RawCol.astype(float)
                                        _verbose( self.speak, 1, 'the values were converted to floating point type')
                                    except :
                                        _verbose( self.speak, 1, 'the values are treated as string type')
                                return RawCol
                else :
                    for sss in list(self.results.keys()) :
                        if self.results[sss][0] == keyType :
                            if VIPkey in self.results[sss][1]['Data'].keys() :
                                RawCol = np.array( self.results[sss][1]['Data'][ VIPkey ] )
                                NameCol = np.array( self.results[sss][1]['Data'][ 'NAME' ] )
                                TimeCol = np.array( self.results[sss][1]['Data'][ 'TIME' ] )
                                _verbose( self.speak, 1, 'extracted ' + VIPkey + ' from ' + keyType + ' with lenght ' + str(len(RawCol)) )
                                _verbose( self.speak, 0, 'extracted ' + 'NAME' + ' from ' + keyType + ' with lenght ' + str(len(NameCol)) )
                                _verbose( self.speak, 0, 'extracted ' + 'TIME' + ' from ' + keyType + ' with lenght ' + str(len(NameCol)) )
                                try :
                                    RawCol = RawCol.astype(int)
                                    _verbose( self.speak, 1, 'the values were converted to integer type')
                                except :
                                    try :
                                        RawCol = RawCol.astype(float)
                                        _verbose( self.speak, 1, 'the values were converted to floating point type')
                                    except :
                                        _verbose( self.speak, 1, 'the values are treated as string type')

                                if type(keyName) == str :
                                    _verbose( self.speak, 1, 'filtering data for item: ' + keyName)
                                    CleanCol = np.extract( np.char.equal( NameCol, keyName ), RawCol )
                                    CleanTime = np.extract( np.char.equal( NameCol, keyName ), TimeCol )
                                    _verbose( self.speak, 1, 'extracting ' + VIPkey + ' with lenght ' + str(len(CleanCol))  + ' for item ' + keyName + '.')
                                elif len(keyName) == 1 :
                                    keyName = keyName[0]
                                    _verbose( self.speak, 2, 'the item name was not especified by only one options ( ' + keyName + ' ) has been found for the key : ' + key )
                                    _verbose( self.speak, 1, 'filtering data for item: ' + keyName )
                                    CleanCol = np.extract( np.char.equal( NameCol, keyName ), RawCol )
                                    CleanTime = np.extract( np.char.equal( NameCol, keyName ), TimeCol )
                                    _verbose( self.speak, 1, 'cleaned ' + VIPkey + ' with lenght ' + str(len(CleanCol)) + ' for item ' + keyName + '.' )
                                else :
                                    _verbose( self.speak, 2, 'multiple ( ' + str(len(keyName)) + ' ) item options found for the key : ' + key + ':\n' + str(keyName) )
                                    CleanCol = np.array([], dtype='float')
                                    CleanTime = np.array([], dtype='float')

                                if len(CleanCol) > 0 :
                                    CleanCol = self.fillZeros( CleanCol, CleanTime )

                                return CleanCol

    def set_FieldTime(self) :
        if len( self.get_Restart() ) > 0 :
            FieldTime = self.checkRestarts('TIME')['TIME']
        else :
            FieldTime = self.loadVector('TIME', SSStype=['FIELD'])
        if FieldTime is None :
            if self.get_Vector('TIME')['TIME'] is not None :
                FieldTime = self.get_Vector('TIME')['TIME']
        if FieldTime is not None :
            self.fieldtime = ( min(FieldTime), max(FieldTime), FieldTime )

    def get_Dates(self) :
        try :
            DateVector = _strDate( list( self.loadVector('DATE', 'FIELD', True) ), speak=(self.speak==1))
        except :
            DateVector = _strDate( list( self.loadVector('DATE', 'FIELD', True) ), formatIN='DD-MM-YYYY', speak=(self.speak==1))
        self.set_Vector( 'DATES', np.array( pd.to_datetime( DateVector ), dtype='datetime64[s]'), self.get_Unit('DATE'), DataType='datetime64', overwrite=True )
        #self.set_Vector( 'DATES', np.array( pd.to_datetime( self.get_Vector('DATE')['DATE'] ), dtype='datetime64[s]'), self.get_Unit('DATE'), DataType='datetime64', overwrite=True )
        self.set_Vector( 'DATE', self.get_Vector('DATES')['DATES'], self.get_Unit('DATES'), overwrite=True )
        self.start = min( self.get_Vector('DATE')['DATE'] )
        self.end = max( self.get_Vector('DATE')['DATE'] )
        return self.get_Vector('DATE')['DATE']

    def extract_Wells(self) : #, pattern=None) :
        # preparing object attribute
        wellsList = list( self.wells )
        # if self.CSV is False :
        #     for sss in self.results :
        #         if self.results[sss][0] == 'WELL' :
        #             wellsList += ( ' '.join( self.results[sss][1]['Data']['NAME'] ).split() )
        # else :
        #     for CSVname in self.CSV :
        #         for i in range( len( self.CSV[CSVname]['[HEADERS]']['VARIABLE'] ) ):
        #             if len( self.CSV[CSVname]['[HEADERS]']['MEMBER'][i].strip() ) > 0 :
        #                 if self.CSV[CSVname]['[HEADERS]']['CLASS'][i].strip().upper() == 'WELL' :
        #                     wellsList += [ self.CSV[CSVname]['[HEADERS]']['MEMBER'][i].strip() ]
        for sss in self.results :
            if self.results[sss][0] == 'WELL' :
                wellsList += ( ' '.join( self.results[sss][1]['Data']['NAME'] ).split() )
        wellsList = list( set( wellsList ) )
        wellsList.sort()
        self.wells = tuple( wellsList )

        return self.wells

    def extract_Groups(self, pattern=None, reload=False) :
        """
        Will return a list of all the group names in case.

        If the pattern variable is different from None only groups
        matching the pattern will be returned; the matching is based
        on fnmatch(), i.e. shell style wildcards.
        """
        if len(self.groups) == 0 or reload is True :
            self.groups = tuple( self.extract_Areas(pattern) )
        if pattern is None :
            return self.groups
        else:
            return tuple( self.extract_Areas(pattern) )

    def extract_Areas(self, pattern=None) :
        # preparing object attribute
        areaList = list( self.groups )
        for sss in self.results :
            if self.results[sss][0] == 'AREA' :
                areaList += ( ' '.join( self.results[sss][1]['Data']['NAME'] ).split() )
        areaList = list( set( areaList ) )
        areaList.sort()
        self.groups = tuple( areaList )
        # preparing list to return
        if pattern is not None :
            areaList = []
            for group in self.groups :
                if pattern in group :
                    areaList.append(group)
            return tuple(areaList)
        else :
            return self.groups

    def extract_Regions(self, pattern=None) :
        # preparing object attribute
        regionsList = list( self.regions )
        # if self.CSV is False :
        #     for sss in self.results :
        #         if self.results[sss][0] == 'REGION' :
        #             regionsList += ( ' '.join( self.results[sss][1]['Data']['NAME'] ).split() )
        # else :
        #     pass
        for sss in self.results :
            if self.results[sss][0] == 'REGION' :
                regionsList += ( ' '.join( self.results[sss][1]['Data']['NAME'] ).split() )
        regionsList = list( set( regionsList ) )
        regionsList.sort()
        self.regions = tuple( regionsList )
        # preparing list to return
        if pattern is not None :
            regionsList = []
            for region in self.regions :
                if pattern in region :
                    regionsList.append(region)
            return tuple(regionsList)
        else :
            return self.regions

    def directSSS(self, Key, SSStype):
        """
        returns the string column from the SSS file for the required Key.
        """
        SSStype = SSStype.strip()
        if type(SSStype) is str :
            SSS = None
            for SSS in self.SSSfiles :
                if _extension(SSS)[1].upper().endswith( SSStype.upper() ) :
                    break
            if SSS is None :
                print('SSS type ' + SSStype + ' not found')
                return None

        SSS = _extension(SSS)[1] + _extension(SSS)[0]
        Key = Key.strip()
        if type(Key) is str :
            if Key in self.results[SSS][1]['Data'] :
                return self.results[SSS][1]['Data'][Key]
            else :
                print("Key '" + Key + "' not found in SSS " + SSStype )
                return None

    def get_VIPkeys(self, SSStype=None) :
        """
        returns a dictinary with the SSStype as keys and the kewords found in each SSS file.
        """

        if type(SSStype) is str :
            SSStype = SSStype.strip()
            SSS = None
            for Sfile in self.SSSfiles :
                if _extension(Sfile)[1].upper().endswith( SSStype.upper() ) :
                    SSS = Sfile
                    break
            if SSS is None :
                print('SSS type ' + SSStype + ' not found')
                return {}
            else :
                SSS = [ _extension(SSS)[1] + _extension(SSS)[0] ]
        elif SSStype is None :
            SSS = []
            for Sfile in self.SSSfiles :
                SSS += [ _extension(Sfile)[1] + _extension(Sfile)[0] ]
        elif type(SSStype) is list or type(SSStype) is tuple :
            SSS = []
            for Stype in SSStype :
                for Sfile in self.SSSfiles :
                    if _extension(Sfile)[1].upper().endswith( Stype.upper() ) :
                        SSS += [ _extension(Sfile)[1] + _extension(Sfile)[0] ]
            if SSS == [] :
                print('SSS type ' + SSStype + ' not found')
                return {}

        output = {}
        for each in SSS :
            output[ _extension(each)[1].split('_')[-1].upper() ] = list( self.results[each][1]['Data'].keys() )
        return output

    def SSSkeys_asECL(self) :
        """
        returns a list of the keys in the SSS file converted to ECL style
        """
        Kdicts = _fromVIPtoECL( self.get_VIPkeys() )
        output = []
        for S in Kdicts :
            output += Kdicts[S]
        return output

    def extract_Region_Numbers(self) :
        """
        reads the region numbers from the SSS file and creates a dictionary for
        regiond names and number.
        """
        Numbers = self.directSSS('#', 'REGION')
        Names = self.directSSS('NAME', 'REGION')
        regNum = {}

        if len(Names) != len(Numbers) :
            print("lenght doesn't match!")
        for i in range(len(Names)) :
            regNum[Names[i].strip()] = _getnumber(Numbers[i])
        return regNum

    def buldSalinityVectors(self) :
        """
        creates the ECL style salinity vectors WWIR and WWPR from
        the SALINITY vector from VIP and production and injection rates.
        """
        if self.is_Attribute('WSALINITY') :
            if self.is_Attribute('WWIR') :
                if self.is_Attribute('WWPR') :
                    prod = self[['WWPR']]
                elif self.is_Attribute('WOPR') :
                    prod = self[['WOPR']]
                elif self.is_Attribute('WGPR') :
                    prod = self[['WGPR']]
                else :
                    self['WSIR'] = 'WSALINITY'
                    self.set_Unit('WSIT', 'CONCENTRATION')
                    return None
            inje = self[['WWIR']]
            salt = self[['WSALINITY']]

            for DF in [salt, prod, inje] :
                DF.rename( columns = _wellFromAttribute(DF.columns) )

            self['WSIR'] = ( salt * inje>0 ), self.get_Unit('WSALINITY')
            # self.set_Unit('WSIR', self.get_Unit('WSALINITY') )
            self['WSPR'] = ( salt * prod>0 ), self.get_Unit('WSALINITY')
            # self.set_Unit('WSPR', self.get_Unit('WSALINITY') )

    def add_Key(self, Key, SSStype=None) :
        if type(Key) == str :
            Key = Key.strip()
            if self.ECLstyle :
                self.keys = tuple( set( list(self.get_Keys()) + [Key] ) )
                self.keysECL = tuple( set( list(self.get_Keys()) + [Key] ) )
                VIPkey, keyType, keyName = _fromECLtoVIP( Key, self.speak )
                self.keysVIP = tuple( set( list(self.get_Keys()) + [ VIPkey +':'+ keyName ] ) )
            else :
                self.keys = tuple( set( list(self.get_Keys()) [Key] ) )
                self.keysVIP = tuple( set( list(self.get_Keys()) + [Key] ) )
                ECLkey = _fromVIPtoECL(Key, SSStype, self.speak)
                self.keysECL = tuple( set( list(self.get_Keys()) + [ECLkey] ) )

        else :
            raise TypeError('Key must be string')

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
        # if self.ECLstyle :
        #     self.keys = self.keysECL
        # else :
        #     self.keys = self.keysVIP

        if len(self.keys) == 0 or reload is True :
            keys = []
            keys +=  list( self.extract_Keys() )
            for extra in ( 'TIME', 'DATE', 'DATES' ) :
                if extra not in keys :
                    keys.append(extra)
            keys = tuple( keys )
        if self.ECLstyle :
            self.keysECL = keys
        else :
            self.keysVIP = keys

        if pattern is None :
            if self.ECLstyle is True :
                return self.keysECL
            elif self.VIPstyle is True :
                return self.keysVIP
            else :
                return self.keys
        else:
            return tuple( self.extract_Keys(pattern) )

    def extract_Keys(self, pattern=None, SSStoExtract=None) :
        # preparing object attribute
        keysList = list( self.keys )
        keysListVIP = list( self.keysVIP )
        keysListECL = list( self.keysECL )

        if SSStoExtract is None :
            SSStoExtract = list(self.results.keys())
        for sss in SSStoExtract :
            if self.results[sss][0] in _VIPTypesToExtractVectors :
                names = list(set( ' '.join( self.results[sss][1]['Data']['NAME'] ).split() ))
                atts = list( self.results[sss][1]['Data'].keys() )

                for att in atts :
                    attECL = _fromVIPtoECL( att, self.results[sss][0], self.speak )
                    if attECL is None :
                        self.VIPnotECL.append( self.results[sss][0] + ' : ' + att )
                        attECL = ''
                    for name in names :
                        keysListVIP.append( att + ':' + name )
                        if self.results[sss][0] == 'FIELD' and attECL != '' :
                            keysListECL.append( attECL )
                        elif self.results[sss][0] in _VIP2ECLtype and attECL != '' :
                            keysListECL.append( attECL + ':' + name )

        if len(self.VIPnotECL) > 0 :
            _verbose( self.speak, -1, '\nsome VIP attributes was not recognized as ECL style attributes, \nto get a report of these attributes use the method:\n  .report_VIP_AttributesNotTo_ECL() \n')
        keysListVIP = list( set( keysListVIP ) )
        keysListVIP.sort()
        self.keysVIP = tuple( keysListVIP )
        keysListECL = list( set( keysListECL ) )
        keysListECL.sort()
        self.keysECL = tuple( keysListECL )
        # preparing list to return
        if pattern is not None :
            keysList = []
            for key in self.keysVIP :
                if pattern in key :
                    keysList.append(key)
            if len(keysList) > 0 :
                return tuple(keysList)
            keysList = [] # redundante
            for key in self.keysECL :
                if pattern in key :
                    keysList.append(key)
            if len(keysList) > 0 :
                return tuple(keysList)
        else :
            if self.ECLstyle is True :
                return self.keysECL
            elif self.VIPstyle is True :
                return self.keysVIP
            else :
                return self.keys

    def get_Unit(self, Key='--EveryType--') :
        """
        returns a string identifiying the unit of the requested Key

        Key could be a list containing Key strings, in this case a dictionary
        with the requested Keys and units will be returned.
        the Key '--EveryType--' will return a dictionary Keys and units
        for all the keys in the results file

        """
        if type(Key) is str and Key.strip() != '--EveryType--' :
            Key = Key.strip().upper()
            if Key in self.units :
                if self.units[Key] is not None:
                    return self.units[Key]
                else : # if self.units[Key] is None:
                    if ':' in Key :
                        if _mainKey(Key) in self.units :
                            if self.units[ _mainKey(Key) ] is not None :
                                return self.units[ _mainKey(Key) ]
                            else :
                                return self.extract_Unit(Key)
            if Key == 'DATES' or Key == 'DATE' :
                    self.units[Key] = 'DATE'
                    return 'DATE'
            if Key in self.keys :
                return self.extract_Unit(Key)
            else:
                if Key[0] == 'W' :
                    UList=[]
                    for W in self.get_Wells() :
                        if Key+':'+W in self.units :
                            UList.append(self.units[Key+':'+W])
                        elif Key+':'+W in self.keys :
                            UList.append( self.extract_Unit(Key+':'+W) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :
                        return None
                elif Key[0] == 'G' :
                    UList=[]
                    for G in self.get_Groups() :
                        if Key+':'+G in self.units :
                            UList.append(self.units[Key+':'+G])
                        elif Key+':'+G in self.keys :
                            UList.append( self.extract_Unit(Key+':'+G) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :
                        return None
                elif Key[0] == 'R' :
                    UList=[]
                    for R in self.get_Regions() :
                        if Key+':'+R in self.units :
                            UList.append(self.units[Key+':'+R])
                        elif Key+':'+R in self.keys :
                            UList.append( self.extract_Unit(Key+':'+R) )
                    if len(set(UList)) == 1 :
                        self.units[Key] = UList[0]
                        return UList[0]
                    else :
                        return None
                UList = None

        elif type(Key) is str and Key.strip() == '--EveryType--' :
            Key = []
            KeyDict = {}
            for each in self.keys :
                if ':' in each :
                    Key.append( _mainKey(each) )
                    KeyDict[ _mainKey(each) ] = each
                else :
                    Key.append(each)
            Key = list( set (Key) )
            Key.sort()
            tempUnits = {}
            for each in Key :
                if each in self.units :
                    tempUnits[each] = self.units[each]
                elif each in self.keys and ( each != 'DATES' and each != 'DATE' ) :
                    tempUnits[each] = self.extract_Unit(each)
                elif each in self.keys and ( each == 'DATES' or each == 'DATE' ) :
                    tempUnits[each] = 'DATE'
                else :
                    if KeyDict[each] in self.units :
                        tempUnits[each] = self.units[KeyDict[each]]
                    elif KeyDict[each] in self.keys :
                        if self.extract_Unit(KeyDict[each]) is None :
                            tempUnits[each] = self.extract_Unit(KeyDict[each])
                        else :
                            tempUnits[each] = self.extract_Unit(KeyDict[each]).strip('( )').strip("'").strip('"')
            return tempUnits
        elif type(Key) in [list,tuple] :
            tempUnits = {}
            for each in Key :
                if type(each) == str and each.strip() in self.units :
                    tempUnits[each] = self.units[each.strip()]
                if type(each) == str and ( each.strip() == 'DATES' or each.strip() == 'DATE' ) :
                    tempUnits[each] = 'DATE'
                elif type(each) == str and each.strip() in self.keys :
                    if self.extract_Unit(each.strip()) is None :
                        tempUnits[each] = self.extract_Unit(each.strip())
                    else :
                        tempUnits[each] = self.extract_Unit(each.strip()).strip('( )').strip("'").strip('"')
            return tempUnits

    def extract_Unit(self, Key, SSStype='FIELD') :
        for sss in list(self.results.keys()) :
            for Vector in list(self.results[sss][1]['Units'].keys()) :
                if Vector == 'DATE' or Vector == 'DATES' :
                    self.units[Vector] = 'DATE'
                else :
                    if self.ECLstyle is True :
                        ECLkey = _fromVIPtoECL( Vector, self.results[sss][0], self.speak )
                        if ECLkey is not None :
                            self.units[ ECLkey ] = self.results[sss][1]['Units'][Vector].strip('( )').strip("'").strip('"')
                    if self.VIPstyle is True :
                        self.units[Vector] = self.results[sss][1]['Units'][Vector].strip('( )').strip("'").strip('"')
        Key = Key.strip()
        if self.ECLstyle is True :
            if Key in self.units :
                return self.units[Key]
            elif Key in _ECL2VIPkey and _ECL2VIPkey[Key] in self.units :
                return self.units[ _fromECLtoVIP( Key, self.speak ) ]
        if self.VIPstyle is True :
            if Key.strip() in self.units :
                return self.units[Key]
            elif Key in _VIP2ECLkey and _VIP2ECLkey[Key] in self.units :
                return self.units[ _fromVIPtoECL( Key, SSStype, self.speak ) ]

    def complete_Units(self) :
        for key in list(self.units.keys()) :
            if self.units[key] is None :
                if ':' in key :
                    self.units[key] = self.extract_Unit(key)
                    if self.units[key] is None :
                        self.units[key] = self.extract_Unit(key[:key.index(':')])
                        if self.units[key] is None :
                            VIPkey = _fromECLtoVIP( key, self.speak )
                            for sss in self.results :
                                self.units[key] = self.results[ VIPkey[1] ][1]['Units'][ VIPkey[0] ].strip('( )').strip("'").strip('"')
                                if self.units[key] is None :
                                    break
                    if self.units[key] is None :
                        _verbose( self.speak, 3, 'impossible to found unit system for key ' + key )
                    else :
                        _verbose( self.speak, 1, 'found unit system ' + self.units[key] + ' for key ' + key )
                else :
                    self.units[key] = self.extract_Unit(key)
                    if self.units[key] is None :
                        VIPkey = _fromECLtoVIP( key, self.speak )
                        for sss in self.results :
                            self.units[key] = self.results[ VIPkey[1] ][1]['Units'][ VIPkey[0] ].strip('( )').strip("'").strip('"')
                            if self.units[key] is None :
                                    break
                    if self.units[key] is None :
                        _verbose( self.speak, 3, 'impossible to found unit system for key ' + key )
                    else :
                        _verbose( self.speak, 1, 'found unit system ' + self.units[key] + ' for key ' + key )

    def OUTPAVG(self, KeyArguments=None, ECLkey=None) :
        if ECLkey is not None :
            if type(ECLkey) is str :
                ECLkey = ECLkey.strip()
                if self.is_Key(ECLkey) :
                    print(" WARNING: the keyword '" + ECLkey + "' already exists here, do you want to overwrite?" )
                    user = ''
                    while user.upper() not in ['Y', 'YES', 'N', 'NO', 'NOT', 'SI', 'SÍ', 'OUI'] :
                        user = input('please write YES or NO: ')
                    if user in ['Y', 'YES', 'SI', 'SÍ', 'OUI'] :
                        if ':' in ECLkey :
                            if self.is_Key( 'WBP:'+ECLkey.split(':')[1] ) :
                                self.set_Vector( Key=ECLkey, VectorData=self('WBP:'+ECLkey.split(':')[1]), Units=self.get_Unit('WBP:'+ECLkey.split(':')[1]), DataType='float', overwrite=True )
                            else :
                                _verbose( self.speak, -1, " the corresponding well for the key '" + _mainKey(ECLkey) + "' does not have WBP here.")
                        else :
                            _verbose( self.speak, -1, " the well name can not be found in the key '" + ECLkey + "'\n use .set_Vector() method to set an especific key")
                elif self.is_Att(ECLkey) :
                    print(" WARNING: the attribute '" + ECLkey + "' already exists here, do you want to overwrite this attribute for all the wells?" )
                    user = ''
                    while user.upper() not in ['Y', 'YES', 'N', 'NO', 'NOT', 'SI', 'SÍ', 'OUI'] :
                        user = input('please write YES or NO: ')
                    if user in ['Y', 'YES', 'SI', 'SÍ', 'OUI'] :
                        for W in self.get_Wells() :
                            self.set_Vector( Key=W, VectorData=self('WBP:'+W), Units=self.get_Unit('WBP:'+W), DataType='float', overwrite=True )
                else :
                    for W in self.get_Wells() :
                        self.set_Vector( Key=W, VectorData=self('WBP:'+W), Units=self.get_Unit('WBP:'+W), DataType='float', overwrite=True )
        elif KeyArguments is not None :
            if type(KeyArguments) is str and len(KeyArguments) > 0 :
                KeyArguments = KeyArguments.strip()
                if len(KeyArguments).split() == 1 :
                    if KeyArguments.upper() != 'WELL' and KeyArguments[0] == 'W' :
                        _verbose( self.speak, 2, " the KeyArguments '" + KeyArguments + "' seems to be a ECL style keyword...")
                        self.OUTPAVG(ECLkey=KeyArguments)
                else :
                    KeyArguments = KeyArguments.split()
                    WPAVE = ['WPAVE', '1st', '2nd', '3rd', '4th']

                    if KeyArguments[0].upper() == 'OUTPAVG' :
                        _verbose( self.speak, 1, " VIP CARD '" + KeyArguments.pop(0) + "' found")

                    if KeyArguments[0].upper() == 'STD' :
                        # Alpha label indicating that the mobility-weighted datum pressure average is to be computed. This is the default.
                        _verbose( self.speak, 3, " IMPORTANT: in VIP the mobility-weighted datum pressure average was computed, the most similar behaviour in eclipse could be to set " + WPAVE[2] + " item of keyword '" + WPAVE[0] + "' to 1.0 (purely connection factor weighted).")
                    elif KeyArguments[0].upper() == 'WELL' :
                        # Alpha label indicating that a pattern is being assigned to each well in the well list.
                        WellList = KeyArguments[-2]
                        WPAVE = ['WWPAVE', '2nd', '3rd', '4th', '5th']
                        _verbose( self.speak, 3, " IMPORTANT: notice that 'WWPAVE' should be used in eclipse, not 'WPAVE', in order to be compilant with the well list: " + WellList )
                    elif KeyArguments[0].upper() == 'PATTERN' :
                        # Alpha label indicating one of the possible patterns is to be used to compute the well average pressure.
                        if KeyArguments[-1].isdecimal() :
                            if int(KeyArguments[-1]) == 1 :
                                # Square pattern of size 1 gridblock by 1 gridblock
                                WBPkey = 'WBP'
                                _verbose( self.speak, 3, " IMPORTANT: be sure that the " + WPAVE[1] + " item of keyword '" + WPAVE[0] + "' is set to a negative value, like '-1', in your eclipse simulation.")
                            elif int(KeyArguments[-1]) == 2 :
                                # 5-spot pattern
                                WBPkey = 'WBP5'
                                _verbose( self.speak, 3, " IMPORTANT: be sure that the " + WPAVE[1] + " item of keyword '" + WPAVE[0] + "' is set to a negative value, like '-1', in your eclipse simulation.")
                            elif int(KeyArguments[-1]) == 3 :
                                # Square pattern of size 3 gridblocks by 3 gridblocks
                                WBPkey = 'WBP9'
                                _verbose( self.speak, 3, " IMPORTANT: be sure that the " + WPAVE[1] + " item of keyword '" + WPAVE[0] + "' is set to a negative value, like '-1', in your eclipse simulation.")
                            elif int(KeyArguments[-1]) in [ 5, 7, 9 ] :
                                # Square pattern of size N gridblocks by N gridblocks
                                WBPkey = 'WBP'+ KeyArguments[-1] + 'x' + KeyArguments[-1]
                                _verbose(self.speak, -1, " there is not eclipse keyword that matched this VIP configuration, \n this VIP average pressure will be loaded as '" + WBPkey + "'")
                            elif int(KeyArguments[-1]) == 0 :
                                # Exclude this layer from the calculation.
                                WBPkey = 'WBP0'
                                _verbose( self.speak, 3, " IMPORTANT: this layer has been excluded from the average pressure calculation")

                    elif KeyArguments[0].upper() == 'ACTIVE' :
                        # Alpha label indicating that only active perforations are used in the calculation. This is the default.
                        _verbose( self.speak, 3, " IMPORTANT: be sure that the " + WPAVE[4] + " item of keyword '" + WPAVE[0] + "' is set to 'OPEN' in your eclipse simulation.")
                    elif KeyArguments[0].upper() == 'ALL' :
                        # Alpha label indicating that all perforations, including inactive or shut-in perforations, are used in the calculation.
                        _verbose( self.speak, 3, " IMPORTANT: be sure that the " + WPAVE[4] + " item of keyword '" + WPAVE[0] + "' is set to 'ALL' in your eclipse simulation.")
                    elif KeyArguments[0].upper() == 'DATUM' :
                        # Alpha label indicating that the well average datum pressure is to be computed. This is the default for a pattern calculation.
                        _verbose( self.speak, 3, " IMPORTANT: be sure that the " + WPAVE[3] + " item of keyword '" + WPAVE[0] + "' is set to 'WELL' in your eclipse simulation.")
                    elif KeyArguments[0].upper() == 'GRIDBLOCK' :
                        # Alpha label indicating that the well average gridblock pressure is to be computed.
                        _verbose( self.speak, 3, " IMPORTANT: be sure that the " + WPAVE[3] + " item of keyword '" + WPAVE[0] + "' is set to 'NONE' in your eclipse simulation.")

        if WPAVE == "WPAVE" :
            return self.OUTPAVG(ECLkey=WBPkey)
        if WPAVE == "WWPAVE" :
            for W in self.get_Wells( WellList ) :
                self.OUTPAVG(ECLkey=WBPkey+':'+W)
            return None

    def get_TotalReservoirVolumes(self) :

        for IP in ['I', 'P'] :
            for TR in ['R', 'T'] :
                # for FIELD
                for OGW in ['O', 'G', 'W'] :
                    rv = []
                    key = 'FV'+IP+TR+OGW
                    if self.is_Key( key ) :
                        rv.append( key )

                key = 'FV'+IP+TR
                if len(rv) > 0 :
                    _verbose( self.speak, 1, 'adding up reservoir volumes for ' + key )

                if len(rv) == 1 :
                    self[key] = self(rv[0]), self.get_Units(rv[0])
                elif len(rv) == 2 :
                    self[key] = self(rv[0]) + self(rv[1]), self.get_Units(rv[0])
                elif len(rv) == 3 :
                    self[key] = self(rv[0]) + self(rv[1]) + self(rv[2]), self.get_Units(rv[0])

                # for WELL, GROUP, REGION
                for T in ['W', 'G', 'R'] :
                    for OGW in ['O', 'G', 'W'] :
                        rv = []
                        key = T+'V'+IP+TR+OGW
                        if self.is_Attribute( key ) :
                            rv.append( key )

                    key = T+'V'+IP+TR
                    if len(rv) > 0 :
                        _verbose( self.speak, 1, 'adding up reservoir volumes for ' + key )

                    if len(rv) == 1 :
                        df = self[[rv[0]]]
                        df.rename( columns=_wellFromAttribute(df.columns), inplace=True )
                        self[key] = df, self.get_Units(rv[0])
                    elif len(rv) == 2 :
                        df0 = self[[rv[0]]]
                        df0.rename( columns=_wellFromAttribute(df0.columns), inplace=True )
                        df1 = self[[rv[1]]]
                        df1.rename( columns=_wellFromAttribute(df1.columns), inplace=True )
                        self[key] = df0 + df1, self.get_Units(rv[0])
                    elif len(rv) == 3 :
                        df0 = self[[rv[0]]]
                        df0.rename( columns=_wellFromAttribute(df0.columns), inplace=True )
                        df1 = self[[rv[1]]]
                        df1.rename( columns=_wellFromAttribute(df1.columns), inplace=True )
                        df2 = self[[rv[2]]]
                        df2.rename( columns=_wellFromAttribute(df2.columns), inplace=True )
                        self[key] = df0 + df1 + df2, self.get_Units(rv[0])
