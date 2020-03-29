#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 23:30:07 2019

@author: martin

CLASSes of objects to contain a simulation object and child objects for the input data.
There are routined to read the imput data from the eclipse style data file.
"""

from datafiletoolbox import extension
from datafiletoolbox import verbose
from datafiletoolbox import datetime
from datafiletoolbox import expandKeyword
from datafiletoolbox import numpy as np
from datafiletoolbox import pandas as pd

class Simulation(object) :
    """
    object containing every aspect of a simulation
    """
    ID = 0
    Index = {}
    Objects = {}
    Count = {}

    msg0 = 0
    msg1 = -1
    msg2 = -1
    msg3 = -1

    def __init__( self , name = None , speak = None ) :
        if speak == None :
            self.speak = 0
        else :
            self.speak = speak
        self.ite = 1
        self.ID = Simulation.ID
        Simulation.ID +=1
        if name == None :
            self.name = str(self.ID)
        else :
            self.name = name
        self.Objects = {}
        
        Simulation.Index[self.ID] = self.name
        # .SimObjects is a dictionary that collects all the subclasses this Collection has
        Simulation.Objects[self.ID] = {}
        self.Count = -1

        self.msg0 = Simulation.msg0
        self.msg1 = Simulation.msg1
        self.msg2 = Simulation.msg2
        self.msg3 = Simulation.msg3

    def __str__(self) :
        line = 'Simulation Object\n  SimID #' + str(self.ID)
        if self.name != str(self.ID) :
            line = line + '\n  Name: ' + self.name

        line = line + '\n  verbosity level is '
        if self.speak == 0 :
            line = line + 'MUTE'
        elif self.speak == 1 :
            line = line + 'MESSAGES'
        elif self.speak == 2 :
            line = line + 'WARNINGS'
        elif self.speak == 3 :
            line = line + 'ERRORS'
        if self.speak == -1 :
            line = line + 'OVERIDE MUTE BY THE PROGRAMM'
        line = line + ' (' + str(self.speak) + ')'

        if len(self) > 0 :
            line = line + '\n  Objects Contained:'
            for each in self.content() :
#                print(self.content()[each] )
                line = line + '\n    ' + str(each) + ' : '
                if str(self.content()[each][0]) == "<class 'datafiletoolbox.simObject.Model'>" :
                    line = line + 'Model'
                    line = line + " with name '" + str(self.content()[each][1]) + "'"
        return line

    def __call__(self,item):
        if type(item) == int :
            if item <= self.Count :
                return self.Objects[item]
            else :
                return None
        elif type(item) == str :
            for each in self.Objects :
                if item == self.Objects[each].name :
                    return self.Objects[each]
            return None
        else :
            for each in self.Objects :
                if item == self.Objects[each] :
                    return self.Objects[each]
            return None

    def __getitem__(self, item) :
        return self.__call__(item)

    def __next__(self) :
        if self.ite < self.Count :
            self.ite += 1
            return self.Objects[self.ite - 1]
        else :
            self.ite = 1
            raise StopIteration

    def __iter__(self) :
        return self

    def __len__(self) :
        return self.Count

    def get_ID(self) :
        return self.ID

    def get_speak(self) :
        return self.speak

    def set_speak(self,speak=1) :
        if type(speak) == int and speak <= 3 and speak >= -1 :
            self.speak = speak

    def content(self) :
        contentDict = {}
        for each in self.Objects :
            contentDict[each] = ( type(self.Objects[each]) , self.Objects[each].get_name() )
        return contentDict
    
    def keys(self) :
        contentKeys = []
        for each in self.Objects :
            contentKeys.append( self.Objects[each].get_name() )
        return tuple(contentKeys)
        
    def set_name( self , name ) :
        try :
            self.name = str(name)
        except :
            pass
        # Simulation.Index[self.ID] = self.name

    def get_name( self ) :
        return str(self.name)

    def add_Model(self,name=None):
        self.Count += 1
        self.Objects[self.Count] = Model( speak = self.speak )
        if name != None :
            self.Objects[self.Count].set_name(name)
        self.Objects[self.Count].set_SimObjectID(self.ID,self.Count)
        # Simulation.Objects[self.ID][0][0].append('Model')
        # Simulation.Objects[self.ID][0][1].append(name)
        self.Objects[self.Count].set_parent(self)
        return self.Count

    def LoadModelFromData(self , filename , name = None , speak = None) :
        if speak == None :
            speak = self.speak
        self.Count += 1
        self.Objects[self.Count] = Model( speak = self.speak )
        # Simulation.Objects[self.ID][0][0].append('Model')
        if name != None :
            self.Objects[self.Count].set_name(name)
            # Simulation.Objects[self.ID][0][1].append(name)
        else :
            self.Objects[self.Count].set_name(extension(filename)[0])
            # Simulation.Objects[self.ID][0][1].append(extension(filename)[0])
        self.Objects[self.Count].set_SimObjectID(self.ID,self.Count)
        self.Objects[self.Count].set_parent(self)
        self.Objects[self.Count].ReadData(filename , speak)









class Model(Simulation) :
    """
    object to contain the input data of the simulation object
    """
    ID = 0
    Objects = {}
    Count = {}
    List = {}

    ZeroArgumentsKeywords = (
        'RUNSPEC','GRID','EDIT','PROPS','REGIONS','SOLUTION','SUMMARY','SCHEDULE',
        'ECHO','NOECHO','ENDBOX','NONNC','MONITOR','NOSIM',
        'FREEZEPC',
        'FIELD','METRIC','CART',
        'OIL','WATER','GAS','DISGAS','VAPOIL','BRINE','API',
        'FMTOUT','FMTIN','UNIFOUT','UNIFIN','MULTOUT','MULTIN',
        'IMPLICIT','AIM','IMPES','AITS','BPARA',
        'AQUCON','AQUCT','AQUANCON','AQUCHWAT','AQUFETP','AQUFLUX',
        'RUNCTRL','DTLOGIC','SMARTMB',
        'SKIP','SKIP100','SKIP300','SKIPTNAV','SKIPTAB','SKIPREST',
        'END','ENDACTIO','ENDSKIP',
        'FILLEPS',

        'ALL','MSUMLINS','MSUMNEWT','SEPARATE','NEWTON','TCPU','ELAPSED','MAXDPR',
        'FOPR','FOPT','FGPR','FGPT','FWPR','FWPT',
        )

    TableFormatKeywords = ( 'DATES','EQUALS','EQUALREG','MULTIPLY','MULTIREG',
            'ADD','ADDREG','ADDZCORN','COPY''COPYBOX','COPYREG','OPERATE','OPERATER',
            'THPRESFT','MULTFLT','FAULTS',
            'TRACER',
            'GRUPTREE','GCONINJE','GINJGAS','GRUPINJE','GCONPROD','GCONINJE',
            'WELSPECS','COMPDAT','COMPDATMD','WPIMULT','WCONHIST','WRFTPLT',
            'WINJGAS','WRFT','WPIMULT','WPI',
            'WCONINJH','WCONPROD','WCONINJE','WELTARG','ACTIONX',
            )

    UndefinedNumberOfTables = ( 'PSPLITX' , 'PSPLITY' )

    TableInTableKeywords = ( 'PVTO','PVTG' )

    SpecialKeywords = ('TITLE','DIMENS','START','EQLDIMS','TABDIMS','WELLDIMS','GPTDIMS','GRID','INCLUDE') #'SUMMARY','SCHEDULE','INCLUDE',)

    NoSlashKeywords = ('TITLE')

    def __init__( self , DataFilePath = '' , speak = None , parent = None ) :
        if speak == None :
            self.speak = self.get_speak()
        else :
            self.speak = speak
        self.SimObjectID = None
        if parent is not None :
            self.ID = parent.ModelID
            parent.childID += 1
        else :
            self.ID = None
        self.parent = parent
        self.Objects = {}
        self.Count = 0
        self.List = []
        #self.KeyworsList = []
        self.title = ''
        if DataFilePath.strip() == '' :
            self.path = ''
            self.name = ''
        else :
            self.path = DataFilePath.strip()
            self.name = extension(self.path)[0]
        self.closing = '/'
        
        
        #self.SimObjects[self.objectID] = ['Model' , self.title , self.path ]
        self.msg0 = Simulation.msg0
        self.msg1 = Simulation.msg1
        self.msg2 = Simulation.msg2
        self.msg3 = Simulation.msg3
        # the ID of the object that create this one
        self.parent = None
        # model dimensions
        self.dims = None
        #self.dimX = None
        #self.dimY = None
        #self.dimZ = None
        self.eqldims = None
        self.welldims = None
        self.tabdims = None
        self.gptdims = None
        self.DimensionedTableKeywords = { 'TUNING' : 3 ,}

    def set_parent(self, parent):
        self.parent = parent
        if self.ID is None :
            self.ID = parent.Count

    def get_parent(self):
        return self.parent

    def __str__(self) :
        line = 'Model Object' + str(self.ID)
        if self.name != self.title :
            line = line + '\n  name: ' + self.name
        if len(self.title) > 0 :
            line = line + '\n  title: ' + self.title
        if len(self.path) > 0 :
            line = line + '\n  read from data file: ' + self.path
        if self.dims != None :
            line = line + '\n  dimensions: ' + str(self.dims)
        if self.start != None :
            line = line + '\n  start date: ' + str(self.start)
        return line

    # def __len__(self) :
    #     # >>> like parent function <<<
    #     return Model.Count[self.ID]

    # def __call__(self,ModObject):
    #     # >>> like parent function <<<
    #     if type(ModObject) == int :
    #         if ModObject <= Model.Count[self.ID] :
    #             return None
    #     elif type(ModObject) == str :
    #         try :
    #             ModObject = Model.Objects[self.ID][0][1].index(ModObject)
    #         except :
    #             return None
    #     return Model.Objects[self.ID][ModObject]
    
    # def __getitem__(self, item) :
    #     # >>> like parent function <<<
    #     if type(item) == int :
    #         if item > Model.Count[self.ID] :
    #             return None
    #     elif type(item) == str :
    #         cont = self.content()
    #         for each in cont :
    #             if cont[each][1] == item :
    #                 return Model.Objects[self.ID][each]
    #         return None
    #     return Model.Objects[self.ID][item]

    # def content(self) :
    #     # >>> like parent function <<<
    #     contentDict = {}
    #     for i in range( 1 , len( Model.Objects[self.ID]) +1 ) :
    #         #contentDict[i] = ( Simulation.Objects[self.ID][0][0][i] , Simulation.Objects[self.ID][0][1][i] )
    #         contentDict[i] = ( type(Model.Objects[self.ID][i]) , Model.Objects[self.ID][i].get_name() )
    #     return contentDict
    
    # def keys(self) :
    #     # >>> like parent function <<<
    #     contentDict = []
    #     for i in range( 1 , len( Model.Objects[self.ID]) +1 ) :
    #         #contentDict[i] = ( Simulation.Objects[self.ID][0][0][i] , Simulation.Objects[self.ID][0][1][i] )
    #         contentDict.append( Model.Objects[self.ID][i].get_name() )
    #     return contentDict

    # def set_name(self,name) :
    #     # >>> like parent function <<<
    #     self.name = str(name)
    #     if self.SimObjectID != None :
    #         Simulation.Objects[self.SimObjectID[0]][0][1][self.SimObjectID[1]] = self.name

    def extract(self , NameCriteria = None , CaseSensitive = False ) :
        contentDict = {}
        if NameCriteria == None :
            for each in self.Objects[self.ID] :
                contentDict[each] = ( type(self.Objects[each]) , self.Objects[each].name , self.Objects[each].get_args() )
        else :
            if type(NameCriteria) == str :
                if CaseSensitive == False :
                    NameCriteria = NameCriteria.upper()
                    for each in self.Objects :
                        if self.Objects[each].name.upper() == NameCriteria :
                            contentDict[each] = ( type(self.Objects[each]) , self.Objects[each].name , self.Objects[each].get_args() )
                else :
                    for each in self.Objects :
                        if self.Objects[each].name == NameCriteria :
                            contentDict[each] = ( type(self.Objects[each]) , self.Objects[each].name , self.Objects[each].get_args() )
            elif type(NameCriteria) == tuple or type(NameCriteria) == list :
                if CaseSensitive == False :
                    for k in range(len(NameCriteria)) :
                        NameCriteria[k] = NameCriteria[k].upper()
                    for each in self.Objects[self.ID] :
                        if self.Objects[each].name.upper() in NameCriteria :
                            contentDict[each] = ( type(self.Objects[each]) , self.Objects[each].name , self.Objects[each].get_args() )
                else :
                    for each in self.Objects[self.ID] :
                        if self.Objects[each].name in NameCriteria :
                            contentDict[each] = ( type(self.Objects[each]) , self.Objects[each].name , self.Objects[each].get_args() )
        return contentDict

    def set_SimObjectID(self,intSimulationID,intModelID):
        if type(intSimulationID) == int and type(intModelID) == int :
            self.SimObjectID = (intSimulationID , intModelID)
        else :
            verbose( self.speak , self.msg2 , 'received SimObjectID is not integer: ' + str(intSimulationID) + ' & ' + str(intModelID))

    def set_title(self,title) :
        if type(title) == list :
            title = ' '.join(title).strip()
        self.title = title
        if self.name == '' :
            self.name = self.title

    def set_dimens(self,dims) :
        if '/' in dims :
            dims = dims[ : dims.index('/') ]
        if type(dims) == str :
            dims = dims.split()
        temporal = []
        for i in range(len(dims)) :
            try :
                temporal.append(int(dims[i]))
            except :
                verbose( self.speak , self.msg3 , '  ERROR: dimension must be integer ' + str(dims))
                return False
            if temporal[i] <= 0 :
                    verbose( self.speak , self.msg2 , '  WARNING: dimension must be positve and greater than zero\n           received ' + str(dims[i]))
        self.dims = tuple(temporal)

    def get_dimens(self) :
        if self.dims == None :
            return None
        else :
            return self.dims

    def get_dimX(self) :
        if self.dims == None :
            return None
        else :
            return self.dims[0]

    def get_dimY(self) :
        if self.dims == None :
            return None
        else :
            return self.dims[1]

    def get_dimZ(self) :
        if self.dims == None :
            return None
        else :
            return self.dims[2]

    def set_eqldims(self,eqldims) :
        if '/' in eqldims :
            eqldims = eqldims[ : eqldims.index('/') ]
        if eqldims.strip() == '' :
            eqldims = ' 5* '
        self.eqldims = expandKeyword(eqldims).split()
        if len(self.eqldims) < 5 :
            self.eqldims = self.eqldims + ['1*']*(5-len(self.eqldims))
        if self.eqldims[0] == '1*' :
            self.eqldims[0] = 1
        if self.eqldims[3] == '1*' :
            self.eqldims[3] = 1
        self.DimensionedTableKeywords['EQUIL'] = int(self.eqldims[0])
        self.DimensionedTableKeywords['SALTVD'] = int(self.eqldims[0])
        self.DimensionedTableKeywords['TVDP'] = int(self.eqldims[3])
        self.DimensionedTableKeywords['TEMPVD'] = int(self.eqldims[0])


    def get_eqldims(self) :
        if self.eqldims == None :
            return ''
        else :
            return self.eqldims

    def set_gptdims(self,gptdims) :
        if '/' in gptdims :
            gptdims = gptdims[ : gptdims.index('/') ]
        if gptdims.strip() == '' :
            gptdims = ' 3* '
        self.gptdims = expandKeyword(gptdims).split()
        if len(self.gptdims) < 3 :
            self.gptdims = self.gptdims + ['1*']*(3-len(self.gptdims))
        if self.gptdims[0] == '1*' :
            self.gptdims[0] = 1
        if self.gptdims[2] == '1*' :
            self.gptdims[2] = 1
        self.DimensionedTableKeywords['GPTABLE'] = int(self.gptdims[0])
        self.DimensionedTableKeywords['GPTABLEN'] = int(self.gptdims[0])
        self.DimensionedTableKeywords['GPTABLE3'] = int(self.gptdims[0])
        self.DimensionedTableKeywords['RECOVERY'] = int(self.gptdims[2])

    def get_gptdims(self) :
        if self.gptdims == None :
            return ''
        else :
            return self.gptdims

    def set_welldims(self,welldims):
        if '/' in welldims :
            welldims = welldims[ : welldims.index('/') ]
        self.welldims = expandKeyword(welldims).split()

    def get_welldims(self):
        if self.welldims == None :
            return ''
        else :
            return self.welldims

    def set_tabdims(self,tabdims) :
        if '/' in tabdims :
            tabdims = tabdims[ : tabdims.index('/') ]
        if tabdims.strip() == '' :
            tabdims = ' 24* '
        self.tabdims = expandKeyword(tabdims).split()
        if len(self.tabdims) < 25 :
            self.tabdims = self.tabdims + ['1*']*(25-len(self.tabdims))
        if self.tabdims[0] == '1*' :
            self.tabdims[0] = 1
        if self.tabdims[1] == '1*' :
            self.tabdims[1] = 1
        if self.tabdims[2] == '1*' :
            self.tabdims[2] = 50
        if self.tabdims[3] == '1*' :
            self.tabdims[3] = 50
        if self.tabdims[4] == '1*' :
            self.tabdims[4] = 1
        if self.tabdims[5] == '1*' :
            self.tabdims[5] = 20
        if self.tabdims[6] == '1*' :
            self.tabdims[6] = 20
        if self.tabdims[7] == '1*' :
            self.tabdims[7] = 1
        if self.tabdims[8] == '1*' :
            self.tabdims[8] = 1
        if self.tabdims[9] == '1*' :
            self.tabdims[9] = self.tabdims[8]
        if self.tabdims[10] == '1*' :
            self.tabdims[10] = 10
        if self.tabdims[11] == '1*' :
            self.tabdims[11] = 1
        if self.tabdims[12] == '1*' :
            self.tabdims[12] = self.tabdims[1]
        if self.tabdims[13] == '1*' :
            self.tabdims[13] = 0
        if self.tabdims[14] == '1*' :
            self.tabdims[14] = 0
        if self.tabdims[15] == '1*' :
            self.tabdims[15] = self.tabdims[1]
        if self.tabdims[16] == '1*' :
            self.tabdims[16] = 10
        if self.tabdims[17] == '1*' :
            self.tabdims[17] = 10
        if self.tabdims[18] == '1*' :
            self.tabdims[18] = 10
        if self.tabdims[20] == '1*' :
            self.tabdims[20] = 5
        if self.tabdims[21] == '1*' :
            self.tabdims[21] = 5
        if self.tabdims[22] == '1*' :
            self.tabdims[22] = 5
        if self.tabdims[23] == '1*' :
            self.tabdims[23] = 0
        self.DimensionedTableKeywords['JFUNCR'] = int(self.tabdims[0])
        self.DimensionedTableKeywords['SGFN'] = int(self.tabdims[0])
        self.DimensionedTableKeywords['SWFN'] = int(self.tabdims[0])
        self.DimensionedTableKeywords['SOF2'] = int(self.tabdims[0])
        self.DimensionedTableKeywords['SOF3'] = int(self.tabdims[0])
        self.DimensionedTableKeywords['SWOF'] = int(self.tabdims[0])
        self.DimensionedTableKeywords['SGOF'] = int(self.tabdims[0])
        self.DimensionedTableKeywords['SGWFN'] = int(self.tabdims[0])
        self.DimensionedTableKeywords['SOR'] = int(self.tabdims[0])
        self.DimensionedTableKeywords['PVTG'] = int(self.tabdims[1])
        self.DimensionedTableKeywords['PVDG'] = int(self.tabdims[1])
        self.DimensionedTableKeywords['PVTO'] = int(self.tabdims[1])
        self.DimensionedTableKeywords['PVDO'] = int(self.tabdims[1])
        self.DimensionedTableKeywords['PVTW'] = int(self.tabdims[1])
        self.DimensionedTableKeywords['PVTWSALT'] = int(self.tabdims[1])*2
        self.DimensionedTableKeywords['PVZG'] = int(self.tabdims[1])*2
        self.DimensionedTableKeywords['EOS'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['BIC'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['OMEGAA'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['OMEGAB'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['TCRIT'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['PCRIT'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['VCRIT'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['ZCRIT'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['MW'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['ACF'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['SSHIFT'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['RTEMP'] = int(self.tabdims[8])
        self.DimensionedTableKeywords['EOSS'] = int(self.tabdims[9])
        self.DimensionedTableKeywords['ROCK'] = int(self.tabdims[12])
        self.DimensionedTableKeywords['ALPHA'] = int(self.tabdims[15])
        self.DimensionedTableKeywords['ALPHAD'] = int(self.tabdims[15])
        self.DimensionedTableKeywords['ALPHAI'] = int(self.tabdims[15])
#        'JFUNCR' : 1 ,'EQUIL' : 1,'RSVD','PBVD','EOS','EOSS',
#                           'SWFN','SGFN','SOF2','SOF3','SWOF','SGOF','PVDO','PVDG',

    def get_tabdims(self) :
        if self.tabdims == None :
            return ''
        else :
            return self.tabdims

    def set_grid(self,dummy=None) :
        if self.tabdims == None :
            self.set_tabdims(' 24* /')
        if self.eqldims == None :
            self.set_eqldims(' 5* /')

    def set_start(self , start) :
        self.start = start

    def get_start(self) :
        if self.start == None :
            return ''
        else :
            return self.start

    def set_path(self , DataFilePath) :
        self.path = str(DataFilePath).strip()

    def get_path(self) :
        if self.path == None :
            return ''
        else :
            return self.path

    def set_include(self,IncludeFile) :
        print('  reading include file\n' + str(IncludeFile) )
        IncludeFile = IncludeFile.replace("\\","/").strip().strip("'")
        if IncludeFile[-1] == '/' :
            IncludeFile = IncludeFile[:-1]
        if "'" in IncludeFile :
            IncludeFile = IncludeFile.strip().strip("'")
        IncludePath = extension(self.path)[2].strip("'")
        IncludeFile = IncludeFile.strip().strip("'")
#        if self.path[-1] == '/' :
#            IncludePath = self.path[:-1]
#        print('\n' + IncludePath + '\n' + IncludeFile )
        if IncludeFile[0] == '/' :
            IncludeFile = IncludeFile[1:]
        IncludePath = IncludePath + IncludeFile
#        IncludePath = IncludePath + '/' + IncludeFile
        self.ReadData(IncludePath)

    def set_summary(self) :
        self.SUMMARY = True
#        self.closing = 'SCHEDULE'

    def set_schedule(self) :
        self.SUMMARY = False
#        self.closing = '/'

    def set_newKeyword(self , name , arguments = None) :
        #self.KeyworsList.append(name)
        self.List.append(name)
        self.Count += 1
        self.Objects[self.Count] = Keyword(name , arguments , KeywordIndex = self.Count , speak = self.speak )
        self.Objects[self.Count].set_parent(self)
        #self.checkSpecials(name)
        self.checkSpecials( self.Count )

    def set_keywordComments(self, keywordComments , KeywordIndex = None ) :
        if KeywordIndex == None :
            KeywordIndex = self.Count
        self.Objects[KeywordIndex].set_comments(keywordComments)

    def set_KeywordArgument(self , arguments) :
        self.Objects[self.Count].append(arguments)

    def checkSpecials( self , keyword_index ) :
#        print('keyword index ' + str(keyword_index))
        if type(keyword_index) == str :
            try :
                keyword_index = len(self.List) - self.List[::-1].index(keyword_index) -1
            except :
                verbose( self.speak , self.msg2 , keyword_index + ' not in keyword list')
        if type(keyword_index) == int and keyword_index <= self.Count :
            if self.Objects[keyword_index].get_name() in Model.SpecialKeywords :
                verbose( self.speak , self.msg1 , 'special keyword identified')
                if self.Objects[keyword_index] != None :
                    self.Objects[keyword_index].expand()
                exec('self.set_' + str(self.Objects[keyword_index].get_name().lower()) + '("' + self.Objects[keyword_index].get_args() + '")' )
                


    def COMPDATtable(self):
        compdatTable = []
        compdatDict = self.extract('COMPDAT',CaseSensitive=False)
        datesDict = self.extract('DATES',CaseSensitive=False)
        compdatArray = np.array(list(compdatDict.keys()))
        datesArray = np.array(list(datesDict.keys()))
        datesMin = min(datesArray)
        for each in compdatArray :
            if each < datesMin :
                compdatDate = self.start
            else :
                compdatDate = datesDict[datesArray[ datesArray < each ][-1]][2][-1]
            for line in compdatDict[each][2] :
                if compdatDate == None :
                    if self.start == None :
                        compdatDate = '01-JAN-1900'
                        print('01-JAN-1900' , line)
                    else :
                        print(compdatDate , line)
                        compdatDate = self.start
                row = [ compdatDate.strip() ] + expandKeyword(line).split()
                compdatTable.append(row)
        return pd.DataFrame(compdatTable)

    def PRODUCTIONandINJECTIONtable(self):
        ProdInjTable = []
        wconhistDict = self.extract('WCONHIST',CaseSensitive=False)
        wconinjhDict = self.extract('WCONINJH',CaseSensitive=False)
        wconprodDict = self.extract('WCONPROD',CaseSensitive=False)
        wconinjeDict = self.extract('WCONINJE',CaseSensitive=False)
        datesDict = self.extract('DATES',CaseSensitive=False)
        wconhistArray = np.array(list(wconhistDict.keys()))
        wconinjhArray = np.array(list(wconinjhDict.keys()))
        wconprodArray = np.array(list(wconprodDict.keys()))
        wconinjeArray = np.array(list(wconinjeDict.keys()))
        datesArray = np.array(list(datesDict.keys()))
        datesMin = min(datesArray)

        for each in wconhistArray :
            if each < datesMin :
                wconhistDate = self.start
            else :
                wconhistDate = datesDict[datesArray[ datesArray < each ][-1]][2][-1]
            for line in wconhistDict[each][2] :
                if wconhistDate == None :
                    if self.start == None :
                        wconhistDate = '01-JAN-1900'
                        print('01-JAN-1900' , line)
                    else :
                        print(wconhistDate , line)
                        wconhistDate = self.start
                row = [ wconhistDate.strip() ] + ['WCONHIST'] + expandKeyword(line).split()
                ProdInjTable.append(row)


        for each in wconinjhArray :
            if each < datesMin :
                wconinjhDate = self.start
            else :
                wconinjhDate = datesDict[datesArray[ datesArray < each ][-1]][2][-1]
            for line in wconinjhDict[each][2] :
                if wconinjhDate == None :
                    if self.start == None :
                        wconinjhDate = '01-JAN-1900'
                        print('01-JAN-1900' , line)
                    else :
                        print(wconinjhDate , line)
                        wconinjhDate = self.start
                row = [ wconinjhDate.strip() ] + ['WCONINJH'] + expandKeyword(line).split()
                ProdInjTable.append(row)

        for each in wconprodArray :
            if each < datesMin :
                wconprodDate = self.start
            else :
                wconprodDate = datesDict[datesArray[ datesArray < each ][-1]][2][-1]
            for line in wconprodDict[each][2] :
                if wconprodDate == None :
                    if self.start == None :
                        wconprodDate = '01-JAN-1900'
                        print('01-JAN-1900' , line)
                    else :
                        print(wconprodDate , line)
                        wconprodDate = self.start
                row = [ wconprodDate.strip() ] + ['WCONPROD'] + expandKeyword(line).split()
                ProdInjTable.append(row)

        for each in wconinjeArray :
            if each < datesMin :
                wconinjeDate = self.start
            else :
                wconinjeDate = datesDict[datesArray[ datesArray < each ][-1]][2][-1]
            for line in wconinjeDict[each][2] :
                if wconinjeDate == None :
                    if self.start == None :
                        wconinjeDate = '01-JAN-1900'
                        print('01-JAN-1900' , line)
                    else :
                        print(wconinjeDate , line)
                        wconinjeDate = self.start
                row = [ wconinjeDate.strip() ] + ['WCONINJE'] + expandKeyword(line).split()
                ProdInjTable.append(row)

        return pd.DataFrame(ProdInjTable)


    def ReadData( self, filename , speak = None ):
        """
        ReadModel reads an eclipse compatible data file or include
        from a given path/filename and return an 'model' object containing all the
        the keywords and values extracted from the data file.
        """

        def appendArgument(previous='',new='') :
            if '/' in new :
                # keywords that can have / as part of the argument
                if keywordName == 'INCLUDE' :
                    return previous + new[ : len(new) - new[::-1].index('/')+1].strip('\n') + '\n'
                # regular keywords
                else :
                    return previous + new[:new.index('/')+1].strip('\n') + '\n'
            else :
                return previous + new.strip('\n') + '\n'

        if speak == None :
            self.speak = self.get_speak()
        else :
            self.speak = speak

        #keywords = {}
        file = open(filename,'r')
        entirefile = file.readlines()
        file.close()

        if self.name == '' :
            self.set_name(extension(filename)[0])
        if self.path == '' :
            self.set_path(filename)

        keywordFlag = False
        SMRYflag = False
        slashCounter = 0
        keywordComments = ''


        for line in entirefile :

            # empty line
            if len(line.strip()) == 0 :
                verbose( speak , self.msg0 , '<  reading empty line')

            # comment line
            elif len(line.strip()) >=2 and line.strip()[:2] == '--' :
                verbose( speak , self.msg0 , '<  reading comment line\n' + str(line))
                keywordComments = keywordComments + line

            # line containing data
            elif len(line.strip()) >=1 :
                values = line.split()
                # ignore comments after keywords or arguments
                if '--' in line :
                    keywordComments = keywordComments + line
                    line = line[:line.index('--')]
                    values = line.split()

                # exception for SUMMARY section, read the entire section as argument of SUMMARY keyword
                if values[0].upper() == 'SUMMARY' or SMRYflag == True :
                    # in case entered here because of SUMMARY keyword
                    if SMRYflag == False :
                        keywordName = str(values[0])
                        verbose( speak , self.msg2 , '   _______________\n>>  found keyword ' + keywordName)
                        SMRYflag = True
                        keywordValues = ''

                    # finished SUMMARY section
                    elif values[0].upper() == 'SCHEDULE' :

                        # saving SUMMARY keyword and its arguments and comments
                        self.set_newKeyword( keywordName ,  keywordValues )
                        self.set_keywordComments( keywordComments )
                        keywordComments = ''

                        # saving the new keyword SCHEDULE
                        keywordName = str(values[0])
                        verbose( speak , self.msg2 , '   _______________\n>>  found keyword ' + keywordName)
                        if '--' in line :
                            keywordComments = keywordComments + line
                        self.set_newKeyword( keywordName )
                        self.set_keywordComments( keywordComments )
                        keywordComments = ''
                        keywordFlag = False
                        keywordName = ''
                        SMRYflag = False

                    # reading arguments of SUMMARY section
                    else :
                        keywordValues = appendArgument( keywordValues ,  line )


                # keyword found
                elif keywordFlag == False :
                    keywordFlag = True
                    slashCounter = 0
                    keywordName = str(values[0])
                    keywordValues = ''
                    verbose( speak , self.msg2 , '   _______________\n>>  found keyword ' + keywordName)
                    
                    # check for keywords that cosists of a base name plus extra characters
                    if keywordName[:4] == 'TVDP' : # tracer keywords
                        self.DimensionedTableKeywords[keywordName.upper()] = self.DimensionedTableKeywords['TVDP']
                        

                    # save keywords that doesn't require arguments
                    if keywordName in Model.ZeroArgumentsKeywords :
                        self.set_newKeyword( keywordName )
                        self.set_keywordComments( keywordComments )
                        keywordFlag = False
                        keywordComments = ''
                        keywordName = ''

                    # set number of tables for dimensioned keywords
                    if keywordName in self.DimensionedTableKeywords :
                        numberOfKeywordTables = self.DimensionedTableKeywords[keywordName.upper()]
                    else :
                        numberOfKeywordTables = 1

                # reading keyword arguments
                else : # elif keywordFlag == True :

                    # interpreting slash in line
                    if '/' in line :

                        # check for comments after slash
                        if len( line[ line.index('/')+1 : ].strip() ) > 0 :
                            keywordComments = keywordComments + line

                        # keywords that must have only one argument line
                        if keywordName not in Model.TableFormatKeywords and keywordName not in self.DimensionedTableKeywords :
                            # save the arguments in case / is not the first character
                            if line.strip().index('/') > 0 :
                                keywordValues = appendArgument( keywordValues ,  line )
                            self.set_newKeyword( keywordName ,  keywordValues )
                            self.set_keywordComments( keywordComments )
                            keywordFlag = False
                            keywordComments = ''
                            keywordName = ''

                        # keywords with undefined number of tables, closed by two consecutive slashes
                        elif keywordName in Model.UndefinedNumberOfTables :

                            # found closing slash
                            if line.strip().index('/') == 0 :

                                # first slash found, it is closing a table
                                if slashCounter == 0 :
                                    slashCounter = 1

                                # only if the preceding line had a slash this one will be the second slash, then closing the keyword
                                else : #if slashCounter == 1 :
                                    verbose( speak , self.msg1 , '<< reading final slash, end of keyword ' + keywordName)
                                    self.set_newKeyword( keywordName ,  keywordValues )
                                    self.set_keywordComments( keywordComments )
                                    keywordFlag = False
                                    keywordComments = ''
                                    keywordName = ''
                                    slashCounter = 0

                            # slash is not the first character in the line, it means the end of a table (not the end of the keyword)
                            else :
                                slashCounter = 1

                        # keywords that could have more than one argument line
                        elif keywordName in Model.TableFormatKeywords :

                            # found closing slash
                            if line.strip().index('/') == 0 :
                                verbose( speak , self.msg1 , '<< reading final slash, end of keyword ' + keywordName)
                                self.set_newKeyword( keywordName ,  keywordValues )
                                self.set_keywordComments( keywordComments )
                                keywordFlag = False
                                keywordComments = ''
                                keywordName = ''

                            # reading table row
                            else : # if line.strip().index('/') > 0 :
                                keywordValues = appendArgument( keywordValues ,  line )

                        # keywords that must have a specific number of argument lines
                        elif keywordName in self.DimensionedTableKeywords :
                            keywordValues = appendArgument( keywordValues ,  line )

                            # in case of TableInTable the closing slash is first character in the line
                            if keywordName in Model.TableInTableKeywords :
                                if line.strip().index('/') == 0 :
                                    slashCounter = slashCounter + 1

                            # slash always closes a table
                            else : # if keywordName not in Model.TableInTableKeywords :
                                slashCounter = slashCounter + 1

                            # slash closing keyword or table
                            if slashCounter == numberOfKeywordTables :
                                keywordValues = appendArgument( keywordValues ,  line )
                                self.set_newKeyword( keywordName ,  keywordValues )
                                self.set_keywordComments( keywordComments )
                                keywordFlag = False
                                keywordComments = ''
                                keywordName = ''

                    # only data line:
                    else : # if '/' not in line :
#                        slashCounter = 0
                        keywordValues = appendArgument( keywordValues ,  line )

                        # in case the keyword does not require slash to close it
                        if keywordName in Model.NoSlashKeywords :
                            self.set_newKeyword( keywordName ,  keywordValues )
                            self.set_keywordComments( keywordComments )
                            keywordComments = ''
                            keywordFlag = False

                        # keywords with undefined number of tables, closed by two consecutive slashes
                        elif keywordName in Model.UndefinedNumberOfTables :
                            slashCounter = 0




class Keyword(Model) :
    """
    object to contain every keyword
    """

    def __init__( self , name , arguments = None , KeywordIndex = None , speak = None , comments = None , parent = None ) :
        if speak == None :
            self.speak = self.get_speak()
        else :
            self.speak = speak
        # Keyword.keyID += 1
        if parent is not None :
            self.ID = parent.Count
        else :
            self.ID = None
        self.name = name
        self.parent = parent
        self.expanded = False
        #self.KeyworsList.append(name)
        self.indexInModel = KeywordIndex
        if arguments != None :
            self.args = arguments
            #self.checkSpecials(self.name)
        else :
            self.args = None
        self.prop = None
        self.propObject = None
        self.msg0 = Simulation.msg0
        self.msg1 = Simulation.msg1
        self.msg2 = Simulation.msg2
        self.msg3 = Simulation.msg3
        if comments == None:
            self.comment = ''
        else :
            self.comment = str(comments)

    def get_dimens(self) :
        return self.parent.get_dimens()

    def __str__(self) :
        line = 'this is keyword ' + str(self.name)
        if self.args != None :
            if len(self.args) < 80 :
                line = line + '\n | ' + ' '.join(self.args) + ' |'
            else :
                line = line + '\n | ' + ' '.join(self.args[:7]) + '\n...\n  ' + ' '.join(self.args[7:])  + ' |'
        return line

    def set_arguments(self , arguments) :
        self.args = arguments
        #if type(arguments) == str :
        #    self.args = aguments
        #elif type(arguments) == list :
        #    self.args = ' '.join(arguments)
        #else :
        #    verbose( self.speak , self.msg3 , '  ERROR: argument is not list or string')

    def set_comments(self, comments='') :
        if comments == None:
            self.comment = ''
        elif comments == '' :
            pass
        else :
            self.comment = str(comments)

    def append(self , arguments ) :
        if type(self.args) == str :
            self.args = [[self.args]]
            if type(arguments) == str :
                self.args.append([arguments])
            elif type(arguments) == list :
                self.args.append(arguments)
            else :
                self.args.append(arguments)
                verbose( self.speak , self.msg2 , '  WARNING: argument is not list or string')
        elif type(self.args) == list :
            if type(arguments) == str :
                self.args.append(arguments.split())
            elif type(arguments) == list :
                self.args.append(arguments)
            else :
                self.args.append(arguments)
                verbose( self.speak , self.msg2 , '  WARNING: argument is not list or string')
        elif type(self.args) == tuple :
            self.args = [self.args]
            if type(arguments) == str :
                self.args.append([arguments])
            elif type(arguments) == list :
                self.args.append(arguments)
            else :
                self.args.append(arguments)
                verbose( self.speak , self.msg2 , '  WARNING: argument is not list or string')

    def annex(self , arguments) :
        if type(arguments) == str :
            self.args = self.args + arguments.split()
        elif type(arguments) == list :
            self.args = self.args + arguments
        else :
            verbose( self.speak , self.msg3 , '  ERROR: argument is not list or string')

    def expand(self):
        if self.expanded == False :
            self.args = expandKeyword(self.args)
            self.expanded = True
        else :
            verbose(self.speak , self.msg1 , 'already expanded')

    def set_name(self , name) :
        self.name = str(name)
        if self.indexInModel != None :
            Model.List[self.ID][self.indexInModel] = self.name
            #self.KeyworsList[self.indexInModel] = self.name

    def get_name(self) :
        return self.name

    def get_args(self) :
        return self.args
    
    def get_prop(self) :
        if self.prop is None :
            if self.args is not None :
                self.arg2prop()
        return self.prop

    def get_comments(self) :
        return self.comment

    def get_comm(self) :
        return self.comments()

    def arg2prop(self) :
        self.propObject = GridProperty( self , self.speak )
        self.prop = self.propObject.prop




class GridProperty(Keyword) :
    def __init__( self , keyword , speak = 0 ) :
        self.speak = speak
        self.prop = None
        self.expanded = False
        self.shaped = False
        self.type = False
        self.parent = keyword
        self.name = keyword.get_name()

        self.msg0 = Simulation.msg0
        self.msg1 = Simulation.msg1
        self.msg2 = Simulation.msg2
        self.msg3 = Simulation.msg3

        
        # expand keyword to be converted to array
        keywordArgument = keyword.get_args()
        if '/' in keywordArgument :
            keywordArgument = keywordArgument[ : keywordArgument.index('/') ]
        keywordArgument = keywordArgument.replace("\n"," ")
        keywordArgument = expandKeyword(keywordArgument)
        self.expanded = True

        # convert to list
        if type(keywordArgument) == tuple :
            keywordArgument = list(keywordArgument)
        elif type(keywordArgument) == str :
            keywordArgument = keywordArgument.split()

        # with the list content identify the type of the values ( int or float )
        if type(keywordArgument) == list :
            countInt = []
            countFloat = []
            countStr = []
            countOther = []
            typeStr = None

            for i in range(len(keywordArgument)) :
                if type(keywordArgument[i]) == int :
                    countInt.append(i)
                elif type(keywordArgument[i]) == float :
                    countFloat.append(i)
                elif type(keywordArgument[i]) == str :
                    countStr.append(i)
                    if '.' in keywordArgument[i] :
                        typeStr = float
                    elif ',' in keywordArgument[i] :
                        typeStr = float
                    else :
                        if typeStr == None :
                            typeStr = int
                else :
                    countOther.append(i)

            if len(countOther) > 0 :
                verbose( self.speak , self.msg3 , 'input type not identified: ' + str(keywordArgument[countOther[0]]) + ' type: ' + str(type(keywordArgument[countOther[0]])) + '.')
            if len(countFloat) > 0 :
                self.type = float
            if len(countInt) > 0 :
                if len(countFloat) > 0 :
                    verbose( self.speak , self.msg2 , 'integers found mixed with floats in keyword arguments')
                    for each in countInt :
                        keywordArgument[each] = float(keywordArgument[each])
                else :
                    self.type = int
            if len(countStr) > 0 :
                if self.type == float :
                    for each in countStr :
                        try :
                            keywordArgument[each] = float(keywordArgument[each])
                        except :
                            verbose( self.speak , self.msg3 , 'input type not identified: ' + str(keywordArgument[each]) + ' type: ' + str(type(keywordArgument[each])) + '.')
                elif self.type == int :
                    for each in countStr :
                        try :
                            keywordArgument[each] = int(keywordArgument[each])
                        except :
                            verbose( self.speak , self.msg3 , 'input type not identified: ' + str(keywordArgument[each]) + ' type: ' + str(type(keywordArgument[each])) + '.')

        # in case string is received, identify the type of the values and then convert to list
        elif type(keywordArgument) == str :
            if '.' in ' '.join(keywordArgument) :
                self.type = float
            elif ',' in ' '.join(keywordArgument) :
                self.type = float
            else :
                self.type = int

            keywordArgument = keywordArgument.split()
            if self.type == float :
                for each in range(len(keywordArgument)) :
                    try :
                        keywordArgument[each] = float(keywordArgument[each])
                    except :
                        verbose( self.speak , self.msg3 , 'input type not identified: ' + str(keywordArgument[each]) + ' type: ' + str(type(keywordArgument[each])) + '.')
            elif self.type == int :
                for each in range(len(keywordArgument)) :
                    try :
                        keywordArgument[each] = int(keywordArgument[each])
                    except :
                        verbose( self.speak , self.msg3 , 'input type not identified: ' + str(keywordArgument[each]) + ' type: ' + str(type(keywordArgument[each])) + '.')

        else :
            # might be a numpy array or something else
            pass

        # create numpy array
        self.prop = np.array( keywordArgument )

        # set shape according to dimension
        self.reshape()
    
    def get_prop(self) :
        return self.prop
    
    def __str__(self) :
        line = 'this is keyword propery' + str(self.name)
        if self.prop is not None :
            if len(self.prop) < 80 :
                line = line + '\n ' + str(self.prop) 
            else :
                line = line + '\n ' + str(self.prop[:7]) + '\n...\n  ' + str(self.args[7:])  
        return line

    def reshape(self , dimensions = None , speak = None) :
        """
        reshape will adapt the shape of the numpy.array to the dimensions of
        the Simulation object or provided in the optional argument 'dimensions'

        """
        # if dimensions are known give the appropiate shape to the array
        if dimensions == None :
            dimensions = self.parent.get_dimens()

        elif type(dimensions) == str :
            dimensions = dimensions.split()
            try :
                for each in range(len(dimensions)) :
                    dimensions[each] = int(dimensions[each])
            except :
                verbose( self.speak , self.msg3 , 'dimensions must be an integer or an tuple of integers' )
                return False

        elif type(dimensions) == list or type(dimensions) == tuple :
            for each in dimensions :
                if type(each) != int :
                    verbose( self.speak , self.msg3 , 'dimensions must be an integer or an tuple of integers' )
                    return False

        if dimensions != None and type(self.prop) == np.ndarray :
            prod = 1
            for each in self.get_dimens() :
                prod = prod * each
            if prod == len(self.prop) :
                self.prop = self.prop.reshape(self.get_dimens())
                self.shaped = True
                return True
            else :
                verbose ( self.speak , self.msg3 , 'dimensions does not match size of property ' + str(self.get_name()) + '.')
                return False

    def clean( self , ValueToClean , SearchBox = None , AverageDirection = 'XY' ) :
        """
        clean will change the ValueToClean by the average (if float)
        or most-of (if integer) of the sorrounding cells.

        The optional argument SearchBox must be a list or tuple containing
        lists or tuples each one containing a pair of indexes
        (the index must be less than or equal to its dimension range ).
        If this argument is not provided the search will be run in the entire
        property. i.e.:
            ((1,100),)
            ((1,100),(1,139))
            ((1,100),(1,139),(25,30))
            ((1,100),(1,139),(1,70),(3,5))

        In case the property doesn't have dimensions (shape), the property will
        be considered unidimensional and the previous and next cells will be
        used to calculate the new value of the cell to be cleaned.

        the optional argument AverageDirection control the search direction
        around each cell to calculate the average or most-of.
        The accepted values are:
            'X', 'Y' or 'XY' for a bidimensional array:
                'X'
                'Y'
                'XY' (default)
            any combination of 'X', 'Y' and 'Z' for a tridimensional array:
                'X'
                'Y'
                'Z'
                'XY' (default)
                'XZ'
                'YZ'
                'XYZ'
            A tridimensional array plus time dimension can be represented by
            the characters 'X', 'Y' and 'Z' and the 'T' for the fourth (time) dimension
            'XYT'
            'XYZT'


        For multidimentional provide a tuple or list with the numbers of the
        dimensions where to look for:
            [1]
            [2]
            [3]
            [1,2]
            [1,3]
            [1,2,3]
            [1,2,3,4]
            [2,4,5,6,8]
            ...
        """
        if self.prop == None :
            return False
        else :
            propdims = len(self.prop.shape)
            if type(AverageDirection) == str :
                AverageDirection = AverageDirection.upper()
                temporal = []
                if propdims == 4 :
                    if 'T' in AverageDirection :
                        temporal.append(0)
                    if 'Z' in AverageDirection :
                        temporal.append(1)
                    if 'Y' in AverageDirection :
                        temporal.append(2)
                    if 'X' in AverageDirection :
                        temporal.append(3)
                elif propdims == 3 :
                    if len(AverageDirection) > 3 :
                        verbose( self.speak , self.msg3 , '4 AverageDirection provided but the property is tridimensional')
                    if 'Z' in AverageDirection :
                        temporal.append(0)
                    if 'Y' in AverageDirection :
                        temporal.append(1)
                    if 'X' in AverageDirection :
                        temporal.append(2)
                elif propdims == 2 :
                    if len(AverageDirection) > 2 :
                        verbose( self.speak , self.msg3 , '3 AverageDirection provided but the property is bidimensional')
                        return False
                    if 'Z' in AverageDirection :
                        temporal.append(0)
                    if 'Y' in AverageDirection :
                        if 'Z' in AverageDirection :
                            temporal.append(1)
                        else :
                            temporal.append(0)
                    if 'X' in AverageDirection :
                        temporal.append(1)
                    elif propdims == 1 :
                        if len(AverageDirection) > 1 :
                            verbose( self.speak , self.msg3 , '2 or 3 AverageDirection provided but the property has a single dimension')
                            return False
                        temporal.append(0)
                    else :
                        if 'T' in AverageDirection :
                            temporal.append(0)
                        if 'Z' in AverageDirection :
                            temporal.append(1)
                        if 'Y' in AverageDirection :
                            temporal.append(2)
                        if 'X' in AverageDirection :
                            temporal.append(3)
                        diffdims = propdims - 3
                        for i in range(len(temporal)) :
                            temporal[i] = temporal[i] + diffdims

                AverageDirection = tuple(temporal)

            elif type(AverageDirection) == list or type(AverageDirection) == tuple :
                AverageDirection = list(AverageDirection)
                for i in range(len(AverageDirection)) :
                    try :
                        AverageDirection[i] = int(AverageDirection[i])
                    except :
                        verbose( self.speak , self.msg3 , 'dimensions must be integers.')
                if 0 in AverageDirection :
                    if propdims <= max(AverageDirection) or propdims < len(AverageDirection) :
                        verbose( self.speak , self.msg3 , 'more dimensions especified for search than dimensions of the property.')
                        return False
                    for i in range(len(AverageDirection)) :
                        AverageDirection[i] = AverageDirection[i] + 1
                maxdim = max((max(AverageDirection) , len(AverageDirection) , propdims))
                for i in range(len(AverageDirection)) :
                    AverageDirection[i] = ( -1 * AverageDirection[i] ) + ( maxdim + 1 )
            else :
                pass
