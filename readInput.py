#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:23:27 2019
@author: martin
"""

from inout import verbose

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
    try :
        ignoredKeywords = ZeroArgumentsKeywords
    except :
        from datafiletoolbox import ZeroArgumentsKeywords
        ignoredKeywords = ZeroArgumentsKeywords
    keywordsIndex = []

    keywordFlag = False
    for line in entirefile :
        if len(line) > 0 :
            values = line.split()
            if len(line) >= 2 and len(values) >= 1 and values[0][:2] == '--' :
                verbose( speak , 1 , '<  reading comment line\n' + str(line))                
            elif len(line) >= 1 and len(values) >= 1 and values[0][0] == '/' :
                verbose( speak , 1 , '<< reading slash, end of keywork ' + keywordName)
                keywordFlag = False
                keywords[keywordName] = keywordValues.split()
            elif keywordFlag == True :
                if counter1 < 4 or counter2 == 10000 :
                    verbose( speak , 1 , '>> keyword ' + keywordName + ' line :' + str(counter1) )
                    if counter2 == 10000 :
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
                    keywords[keywordName] = keywordValues.split()
                else :       
                    keywordValues = keywordValues + ' ' + line
            elif len(line) >= 1 and len(values) >= 1 :
                keywordFlag = True
                keywordName = str(values[0])
                keywordValues = ''
                counter1 = 0
                counter2 = 0
                verbose( speak , 2 , '   _______________\n>>  found keyword ' + keywordName)
                for ignored in ignoredKeywords :
                    if keywordName == ignored :
                        keywordFlag = False
                        keywords[keywordName] = None
                        break
            else : 
                #empty line
                pass
            
    return keywords



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
