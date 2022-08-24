#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:23:27 2019
@author: martin

routines to read keywords in eclipse style
"""

from .._common.inout import _verbose 

from .keywords import *

ignoredKeywords = ZeroArgumentsKeywords + NoSlashKeywords
tableKeywords = TableFormatKeywords
undefinedTables = VFPtables + TableInTableKeywords + UndefinedNumberOfTables + tuple(KnownTables.keys())

def readKeyword( filename , speak=0 ):
    """
    loadInput.readKeyword extracts the keywords and values from a given
    path/filename of an eclipse compatible data file or include and return
    a dictionary containing the keyword and its values inside a list:

        { 'PERMX' : [ 0.0 , 0.0 , 536.2 , 1324.45 , ... , 30.7 , 0 ] }

    HIGHLIGHTS: by default
        > keywords with no arguments will be ignored
        > repeated keywords will be overriten and only the last entry of
          the keyword will be returned.

    To avoid this behaviour please use the function readData.simulationModel
    """
    keywords = {}
    file = open(filename,'r')
    entirefile = file.readlines()
    file.close()
    
    # keywordsIndex = []
    keywordFlag = False
    
    for line in entirefile :
        
        cleanLine = line.strip()
        
        # skip empty line
        if len(cleanLine) == 0 :
            continue

        # skip comment lines
        if len(cleanLine) >= 2 and cleanLine[:2] == '--' :
            _verbose( speak , 1 , '<  reading comment line\n' + str(line))
            continue
        
        # remove comments after the data
        dataLine = cleanLine[: cleanLine.index('--') ].strip() if '--' in cleanLine else cleanLine.strip()
        values = dataLine.split()
        
        # skip lines with no data
        if len(dataLine) == 0 :
            continue
        
        # open a new keyword entry
        if not keywordFlag :
            keywordFlag = True
            keywordName = values[0]
            keywordValues = ''
            _verbose( speak , 2 , '   _______________\n>>  found keyword ' + keywordName)
            
            # close this keyword if is one of the ignored keywords
            if keywordName in ignoredKeywords :
                keywordFlag = False
                keywords[keywordName] = None
            
            continue

        # read the data for the keyword
        if keywordFlag :
            
            # for undefinedTables, read next keyword and close previous one
            if keywordName in undefinedTables :
                if dataLine[0] not in '0123456789/' and ( keywordName in VFPtables and values[0].upper().strip("'").strip('"') not in ['METRIC','FIELD','LAB','PVT-M'] ) :
                    # found next keyword, close previous
                    keywords[keywordName] = keywordValues + '/'
                    keywordName = values[0]
                    keywordValues = ''
                    continue
            
            # read data from regular line
            if '/' not in dataLine :
                keywordValues += ' ' + dataLine
                continue
            
            # read lines with slash
            if '/' in dataLine :
                keywordValues += ' ' + dataLine[:dataLine.index('/')+1]
                
                # close keyword
                if keywordName in undefinedTables :
                    continue # slash doesn't mean end of keyword
                    
                if keywordName in tableKeywords :
                    if dataLine[0]=='/' : # end of keyword
                        _verbose( speak , 1 , '<< reading slash, end of keyword ' + keywordName)
                        keywordFlag = False
                        keywords[keywordName] = keywordValues + '/'
                        keywordValues = ''
                    continue
                
                # any other keyword
                _verbose( speak , 1 , '<< reading slash, end of keyword ' + keywordName)
                keywordFlag = False
                keywords[keywordName] = keywordValues + '/'
                keywordValues = ''
                continue
        
    # in case data is still in the keywordValues, because end of file
    if keywordValues != '' :
        keywords[keywordName] = keywordValues + '/'
        _verbose( speak , 1 , '<< end of file, end of keyword ' + keywordName)

    return keywords

        #     # 
        
        # if len(line) >= 1 and len(values) >= 1 and values[0][0] == '/' :
        #     _verbose( speak , 1 , '<< reading slash, end of keywork ' + keywordName)
        #     keywordFlag = False
        #     keywords[keywordName] = keywordValues.split()
            
        #     elif keywordFlag == True :
        #         if counter1 < 4 or counter2 == 10000 :
        #             _verbose( speak , 1 , '>> keyword ' + keywordName + ' line :' + str(counter1) )
        #             if counter2 == 10000 :
        #                 counter2 = 0
        #         counter1 = counter1 + 1
        #         counter2 = counter2 + 1
        #         if '--' in line :
        #             line = line[:line.index('--')]
        #             values = line.split()
        #         if '/' in line and keywordName not in VFPtables :
        #             _verbose( speak , 1 , '<< reading slash, end of keywork ' + keywordName)
        #             if line.index('/') > 0 :
        #                 keywordValues = keywordValues + ' ' + line[:line.index('/')]
        #             keywordFlag = False
        #             keywords[keywordName] = keywordValues.split()
        #         elif keywordName in VFPtables and len(line.strip())>0 and not line.strip()[0].isdigit() :
        #             _verbose( speak , 1 , '<< reading next keyword, end of keywork ' + keywordName)

        #         else :
        #             keywordValues = keywordValues + ' ' + line

        #     else :
        #         #empty line
        #         pass





def simulationModel( filename , speak=0 ):
    """
    loadInput.simulationModel reads an eclipse compatible data file or include
    from a given path/filename and return an 'model' object containing all the
    the keywords and values extracted from the data file.
    """

    keywords = {}
    file = open(filename,'r')
    entirefile = file.readlines()
    file.close()
    ignoredKeywords = ZeroArgumentsKeywords
    keywordsIndex = []

    ModelObject = Simulation()
    ModelObject.set_name(extension(filename)[0])
    ModelObject.add_Model(DataFilePath=filename)

    keywordFlag = False
    for line in entirefile :
        if len(line) > 0 :
            values = line.split()
            if len(line) >= 2 and len(values) >= 1 and values[0][:2] == '--' :
                print('<  reading comment line\n' + str(line))
            elif len(line) >= 1 and len(values) >= 1 and values[0][0] == '/' :
                print('<< reading slash, end of keywork ' + keywordName)
                keywordFlag = False
                keywords[keywordName] = keywordValues.split()
            elif keywordFlag == True :
                if counter1 < 4 or counter2 == 10000 :
                    print('>> keyword ' + keywordName + ' line :' + str(counter1) )
                    if counter2 == 10000 :
                        lapseStart = datetime.datetime.now()
                        counter2 = 0
                counter1 = counter1 + 1
                counter2 = counter2 + 1
                if '--' in line :
                    line = line[:line.index('--')]
                    values = line.split()
                if '/' in line :
                    print('<< reading slash, end of keywork ' + keywordName)
                    if line.index('/') > 0 :
                        keywordValues = keywordValues + ' ' + line[:line.index('/')]
                    keywordFlag = False
                    keywords[keywordName] = keywordValues.split()
                else :
                    keywordValues = keywordValues + ' ' + line
            elif len(line) >= 1 and len(values) >= 1 :
                keywordFlag = True
                keywordName = str(values[0])
                keywordValues = ''
                counter1 = 0
                counter2 = 0
                lapseStart = datetime.datetime.now()
                print('   _______________\n>>  found keyword ' + keywordName)
                for ignored in ignoredKeywords :
                    if keywordName == ignored :
                        keywordFlag = False
                        keywords[keywordName] = None
                        keywordsIndex.append(keywordName)
                        break
            else :
                #empty line
                pass

    if indexKeywords == True :
        keywordsIndex = tuple(keywordsIndex)
        return ( keywordsIndex , keywords )
    else :
        return keywords
