#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 15 23:30:07 2019

@author: martin
"""

from inout import verbose
from inout import extension 
import datetime

class Simulation(object) :
    """
    object containing every aspect of a simulation
    """
    ID = 0
    Index = {}
    #Objects = {}
    #Count = {}

    def __init__( self , name = None , speak = 0) :
        self.speak = speak
        self.ite = 1
        self.ID = Simulation.ID
        Simulation.ID +=1
        if name == None :
            self.name = str(self.ID)
        else :
            self.name = name
        Simulation.Index[self.ID] = self.name
        # .SimObjects is a dictionary that collects all the subclasses this Collection has 
        #self.SimObjects = {}
        #self.SimCount = 0
        #self.SimObjects[self.SimCount] = [['ObjectType'],['ObjectName']]
        self.SimCount = 0
        self.SimObjects = {}
        self.SimObjects[0] = [['ObjectType'],['ObjectName']]

        
    def __str__(self) :
        line = 'Simulation Object\  SimID #' + str(self.ID)
        if self.name != str(self.ID) :
            line = line + '\  Name: ' + self.name
        if len(self.SimObjects) > 0 :
            line = line + '\n  Objects Contained:'
            for each in self.SimObjects :
                line = line + '\n    ' + str(each) + ' : ' + str(type(self.SimObjects[each]))
        return line
    
    def __call__(self,SimObject):
        if type(SimObject) == int :
            if SimObject > self.SimCount :
                return None
        elif type(SimObject) == str :
            try : 
                SimObject = self.SimObjects[0][1].index(SimObject)
            except :
                return None
        return self.SimObjects[SimObject]
    
    def __next__(self) :
        if self.ite < self.SimCount :
            self.ite += 1
            return self.SimObjects[self.ite - 1]
        else :
            self.ite = 1
            raise StopIteration

    def __iter__(self) :
        return self
        
    def __len__(self) :
        return self.SimCount
    
    def content(self) :
        contentDict = {}
        for i in range( 1 , len(self.SimObjects)+1 ) :
            contentDict[i] = ( self.SimObjects[0][i] , self.SimObjects[1][i] )
        return contentDict
     
    def set_name( self, name ) :
        self.name = name
        Simulation.Index[self.ID] = self.name
        
    def add_Model(self,name=None):
        self.SimCount += 1
        self.SimObjects[self.SimCount] = Model()
        if name != None :
            self.SimObjects[self.SimCount].set_name(name)
        self.SimObjects[self.SimCount].set_SimObjectID(self.ID,self.SimCount)
        self.SimObjects[0][0].append('Model')
        self.SimObjects[0][1].append(name)
        return self.SimCount
    
    def LoadModelFromData(self , filename , name = None , speak = None) :
        if speak == None :
            speak = self.speak
        self.SimCount += 1
        self.SimObjects[self.SimCount] = Model()
        self.SimObjects[0][0].append('Model')
        if name != None :
            self.SimObjects[self.SimCount].set_name(name)
            self.SimObjects[0][1].append(name)
        else :
            self.SimObjects[self.SimCount].set_name(extension(filename)[0])
            self.SimObjects[0][1].append(extension(filename)[0])
        self.SimObjects[self.SimCount].set_SimObjectID(self.ID,self.SimCount)
        self.SimObjects[self.SimCount].ReadData(filename , speak)
        
        
 

        

        


class Model(Simulation) :
    """
    object to contain the input data of the simulation object
    """
    ID = 0
    #Objects = {}
    #Count = {}
    #List = {}
    
    ZeroArgumentsKeywords = (
        'RUNSPEC','GRID','EDIT','PROPS','REGIONS','SOLUTION','SUMMARY','SCHEDULE',
        'ECHO','NOECHO','ENDBOX','NONNC',
        'OIL','WATER','GAS','DISGAS','VAPOIL','FIELD','METRIC',
        'FMTOUT','FMTIN','UNIFOUT','UNIFIN','MULTOUT','MULTIN',
        'IMPLICIT',
        'END',
        'ALL',
        'MSUMLINS'
        'MSUMNEWT',
        'SEPARATE'
        )

    specialKeywords = ('TITLE','DIMENS','START','EQLDIMS','TABDIMS','WELLDIMS')
    
    def __init__(self , DataFilePath = '') :
        self.SimObjectID = None
        Model.ID += 1
        self.modelID = Model.ID
        self.ModObjects = {}
        self.ModCount = -1
        self.ModList = []
        #self.KeyworsList = []
        self.title = ''
        if DataFilePath == '' :
            self.path = ''
        else :
            self.path = DataFilePath.strip()
        if self.path == '' :
            self.name = ''
        else :
            self.name = extension(self.path)[0]
        self.dimX = None
        self.dimY = None
        self.dimZ = None
        self.dims = (self.dimX,self.dimY,self.dimZ)
        self.start = None
        #self.SimObjects[self.objectID] = ['Model' , self.title , self.path ] 
        
    def test(self) :
        print(type(Simulation.SimObjects[0]))
    
    def __str__(self) :
        line = 'Model Object' + str(self.modelID)
        if self.name != self.title :
            line = line + '\n  name: ' + self.name
        if len(self.title) > 0 :
            line = line + '\n  title: ' + self.title
        if len(self.path) > 0 :
            line = line + '\n  read from data file: ' + self.path
        if self.dimX != None or self.dimZ != None  or self.dimZ != None :
            line = line + '\n  dimensions: ' + str(self.dims)
        if self.start != None :
            line = line + '\n  start date: ' + str(self.start)
        return line
    
    def __len__(self) :
        return Model.Count[self.ID]
    
    def set_SimObjectID(self,intSimulationID,intModelID):
        if type(intSimulationID) == int and type(intModelID) == int :
            self.SimObjectID = (intSimulationID , intModelID)
        else :
            verbose( self.speak , 2 , 'received SimObjectID is not integer: ' + str(intID))
    
    def set_title(self,title) :
        if type(title) == list :
            title = ' '.join(title).strip()
        self.title = title
        if self.name == '' :
            self.name = self.title
    
    def set_name(self,name) :
        self.name = str(name)
        if self.SimObjectID != None :
            self.SimObjects[0][1][self.SimObjectID[1]] = self.name
    
    def set_dimens(self,dims) :
        if type(dims) == str :
            dims = dims.split()
        if len(dims) == 3 :
            try :
                self.dimX = int(dims[0])
                self.dimY = int(dims[1])
                self.dimZ = int(dims[2])
                self.dims = (self.dimX,self.dimY,self.dimZ)
                if self.dimX <= 0 or self.dimY <= 0 or self.dimZ <= 0 :
                    verbose( self.speak , 2 , '  WARNING: dimension must be positve and greater than zero\n           received ' + str(self.dims))
            except :
                verbose( self.speak , 3 , '  ERROR: dimension must be integer')

        else :
            verbose( self.speak , 3 , '  ERROR: wrong number of dimension')
    
    def set_start(self , start) :
        self.start = simDate(start)
    
    def set_path(self , DataFilePath) :
        self.path = str(DataFilePath).strip()
        
    def set_newKeyword(self , name , arguments = None) :
        #self.KeyworsList.append(name)
        self.ModList.append(name)
        self.ModCount += 1
        self.ModObjects[self.ModCount] = Keyword(name , arguments = None , KeywordIndex = self.ModCount )
        
    def set_KeywordArgument(self , arguments) :
        self.ModObjects[self.ModCount].append(arguments)
    
    def checkSpecials( self , keyword_index ) :
        if type(keyword_index) == str :
            try : 
                keyword_index = ModelObjectsList[self.modelID].index(keyword_index)
            except :
                verbose( speak , -1 , keyword_index + ' not in keyword list')
        if type(keyword_index) == int and keyword_index <= ModelObjectsCount[self.modelID] :
            if self.ModObjects[keyword_index].get_name() in Model.specialKeywords :
                verbose( self.speak , 1 , 'special keyword identified')
                self.ModObjects[keyword_index].expand()
                exec('self.set_' + str(self.ModObjects[keyword_index].get_name().lower()) + '(' + self.ModObjects[keyword_index].get_args() + ')' )
    
    
    def ReadData( self, filename , speak = None ):
        """
        ReadModel reads an eclipse compatible data file or include 
        from a given path/filename and return an 'model' object containing all the 
        the keywords and values extracted from the data file.
        """
        
        if speak == None :
            speak = self.speak
        
        #keywords = {}
        file = open(filename,'r')
        entirefile = file.readlines()
        file.close()
        
        self.set_name(extension(filename)[0])
        self.set_path(filename)
    
        keywordFlag = False
        for line in entirefile :
            if len(line) > 0 :
                values = line.split()
                if len(line) >= 2 and len(values) >= 1 and values[0][:2] == '--' :
                    verbose( speak , 1 , '<  reading comment line\n' + str(line))                
                elif len(line) >= 1 and len(values) >= 1 and values[0][0] == '/' :
                    verbose( speak , 1 , '<< reading slash, end of keywork ' + keywordName)
                    keywordFlag = False
                    #keywords[keywordName] = keywordValues.split()
                    self.set_newKeyword( keywordName ,  keywordValues.split() )
                elif keywordFlag == True :
                    if counter1 < 4 or counter2 == 10000 :
                        verbose( speak , 1 , '>> keyword ' + keywordName + ' line :' + str(counter1) )
                        if counter2 == 10000 :
                            lapseStart = datetime.datetime.now()  
                            counter2 = 0
                    counter1 = counter1 + 1
                    counter2 = counter2 + 1
                    if '--' in line :
                        line = line[:line.index('--')]
                        values = line.split()
                    if '/' in line :
                        verbose( speak , 1 , '<< reading slash, end of keywork ' + keywordName)
                        if line.index('/') > 0 :
                            keywordValues = keywordValues + ' ' + line[:line.index('/')]
                        keywordFlag = False
                        #keywords[keywordName] = keywordValues.split()
                        self.set_newKeyword( keywordName ,  keywordValues.split() )
                    else :       
                        keywordValues = keywordValues + ' ' + line
                elif len(line) >= 1 and len(values) >= 1 :
                    keywordFlag = True
                    keywordName = str(values[0])
                    keywordValues = ''
                    counter1 = 0
                    counter2 = 0
                    lapseStart = datetime.datetime.now()  
                    verbose( speak , 2 , '   _______________\n>>  found keyword ' + keywordName)

                    if keywordName in Model.ZeroArgumentsKeywords :
                        keywordFlag = False
                        #keywords[keywordName] = None
                        self.set_newKeyword( keywordName )
                        #keywordsIndex.append(keywordName)
                        break
                else : 
                    #empty line
                    pass
                
#        if indexKeywords == True :
#            keywordsIndex = tuple(keywordsIndex)
#            return ( keywordsIndex , keywords )
#        else :
#            return keywords
        



class Keyword(Model) :
    """
    object to contain every keyword
    """
    keyID = 0
    
    def __init__(self , name , arguments = None , KeywordIndex = None ) :
        self.ID = Keyword.keyID
        Keyword.keyID += 1
        self.name = name
        self.expanded = False
        #self.KeyworsList.append(name)
        self.indexInModel = KeywordIndex
        if arguments != None :
            if type(arguments) == str :
                self.args = aguments.split()
            elif type(arguments) == list :
                self.args = arguments
            else :
                print('argument is not list or string')
            self.checkSpecials()
        else :
            self.args = []

    def __str__(self) :
        line = 'this is keyword ' + str(self.name)
        if arguments != None :
            if len(self.args) < 80 :
                line = line + '\n | ' + ' '.join(self.args) + ' |'
            else :
                line = line + '\n | ' + ' '.join(self.args[:7]) + '\n...\n  ' + ' '.join(self.args[7:])  + ' |'
        return line
        
    def set_arguments(self , arguments) :
        if type(arguments) == str :
            self.args = aguments.split()
        elif type(arguments) == list :
            self.args = arguments
        else :
            verbose( self.speak , 3 , '  ERROR: argument is not list or string')
    
    def append(self , arguments) :
        if type(arguments) == str :
            self.args.append(aguments.split())
        elif type(arguments) == list :
            self.args.append(arguments)
        else :
            verbose( self.speak , 3 , '  ERROR: argument is not list or string')
            
    def annex(self , arguments) :
        if type(arguments) == str :
            self.args = self.args + aguments.split()
        elif type(arguments) == list :
            self.args = self.args + arguments
        else :
            verbose( self.speak , 3 , '  ERROR: argument is not list or string')
    
    def expand(self):
        if self.expanded == False :
            self.args = expandKeyword(self.args)
            self.expanded = True
        else :
            verbose(self.speak , 1 , 'already expanded')
            
    def set_name(self , name) :
        self.name = str(name)
        if self.indexInModel != None :
            self.ModList[self.indexInModel] = self.name
            #self.KeyworsList[self.indexInModel] = self.name
    
    def get_name(self) :
        return self.name

    def get_args(self) :
        return self.args
    
    
            

class GridProperty(Keyword) : 
    pass


