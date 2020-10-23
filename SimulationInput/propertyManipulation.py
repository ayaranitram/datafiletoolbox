#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 21:44:45 2019

@author: martin

routines:
    to decompress, or expand, and to compress the property keywords (eclipse style).
    to shift the propery keywords.
"""

__version__ = '0.0.20-05-16'

from .._common.inout import _verbose

def expandKeyword( keywordValues , speak=0 , expandDefaults=True) :
    """
    expandKeyword receives list of values or a space-separated string containing
    the values of the property keyword in the compressed format ' 3*0.257 ' and
    returns the expanded ' 0.257 0.257 0.257 ' property as a list or
    space-separated string according to the format of the received input.

    the optional argument speak controls the verbosity of expandKeyword, where:
        0 = not ouptut at all
        1 = print every message
        2 = print final statement only
    """
    if keywordValues == None :
        return ''

    if type(keywordValues) == list :
        outformat = 'list'
        try :
            inputValues = ' ' + ' '.join(keywordValues) + ' '
        except :
            inputValues = ' ' + ' '.join(list(map(str,keywordValues))) + ' '
    elif type(keywordValues) == str :
        outformat = 'str'
        
        inputValues = ' ' + keywordValues + ' '
        inputValues = inputValues.replace('\n',' ')
        inputValues = inputValues.replace('/',' /')
    else :
        _verbose(speak,-1,'ERROR: keyword values to be expanded should be provided as LIST or STRING')
        raise Exception('keyword values to be expanded should be provided as LIST or STRING')
    outputValues = ''
    ini = 0
    end = len(inputValues)
    starFlag = '*' in inputValues[ini:]
    prog = 100*ini//end
    _verbose(speak,2,'expanding 0%')

    while starFlag :

        star = inputValues[ini:].index('*')
        star = star + ini
        starIni = inputValues[star::-1].index(' ')
        starIni = star - starIni + 1
        starEnd = inputValues[star:].index(' ')
        starEnd = star + starEnd

        temp = ' '
        rept = inputValues[star+1:starEnd]
        inte = inputValues[starIni:star]
        if len(inte) == 0 :
            inte = '1'
        if len(rept) > 0 :
            inte = int(inte)
            for i in range(inte) :
                temp = temp + ' ' + rept
            outputValues = outputValues + ' ' + inputValues[ini:starIni] + temp + ' '
        else:
            if expandDefaults == True :
                inte = int(inte)
                rept = '1*'
                for i in range(inte) :
                    temp = temp + ' ' + rept
                outputValues = outputValues + ' ' + inputValues[ini:starIni] + temp + ' '
            else :
                outputValues = outputValues + ' ' + inputValues[ini:starEnd] + ' '

        ini = starEnd
        starFlag = '*' in inputValues[ini:]
        if prog < 100*ini//end :
            prog = 100*ini//end
            _verbose(speak,1,'expanding ' + str(prog) + '%')

    outputValues = outputValues + ' ' + inputValues[ini:]
    if prog < 100 :
        _verbose(speak,1,'expanding 100%')
    _verbose(speak,2,'property expanded')

    outputValues = outputValues.split()
    if outformat == 'str' :
        outputValues = ' ' + ' '.join(outputValues) + ' '

    return outputValues



def compressKeyword(keywordValues , speak=0):
    """
    compressKeyword receives list of values or a space-separated string containing
    the values of the property keyword and returns the compressed property
    ' 0.114 3*0.257 0.362 ' instead ' 0.114 0.257 0.257 0.257 0.362 ' as a list or
    space-separated string according to the format of the received input.

    the optional argument speak controls the verbosity of expandKeyword, where:
        0 = not ouptut at all
        1 = print every message
        2 = print final statement only
    """


    if type(keywordValues) == str :
        keywordValues = keywordValues.split()
        inFormat = 'str'
    elif type(keywordValues) == list :
        inFormat = 'list'
    else:
        return 'incorrect input format, string or list expected'

    Compressed = []
    prog = 0
    totaldimen = len(keywordValues)-1
    reptFlag = False
    uniqueFlag = True
    irept = 1
    uniqueStart = 0

    i = 0
    while i < totaldimen:
        if keywordValues[i] == keywordValues[i+1]:
            irept += 1
            if uniqueFlag == True :
                uniqueFlag = False
                Compressed = Compressed + keywordValues[uniqueStart:i]
            if reptFlag == False:
                reptFlag = True
                reptStr = keywordValues[i]
        else:
            if reptFlag == True :
                reptFlag = False
                Compressed = Compressed + [str(irept) + '*' + str(reptStr)]
                irept = 1
            if uniqueFlag == False :
                uniqueFlag = True
                uniqueStart = i + 1
                load = True
        i += 1

        if prog < 100*i//totaldimen :
            prog = 100*i//totaldimen
            _verbose(speak , 1 , 'compressing ' + str(prog) + '%')

    if reptFlag == True:
        Compressed = Compressed + [str(irept) + '*' + str(reptStr)]
    if uniqueFlag == True:
        Compressed = Compressed + keywordValues[uniqueStart:]

    _verbose(speak , 2 , 'compressed finished')
    if inFormat == 'str' :
        Compressed = ' '.join(Compressed)
    return Compressed



def shiftProperty( ValuesArray , DIMENS=[] , newValues=0 , skipI=-1 , shiftI=0 , skipJ=-1 , shiftJ=0 , skipK=-1 , shiftK=0 , speak=0 ) :
    """
    shift moves values inside the array, like COPYREG but works withs overlaping boxes
    """

    if '*' in ValuesArray :
        compressed = True
        ValuesArray = expandKeyword( ValuesArray , speak)
    else:
        compressed = False

    if type(ValuesArray) == list :
        outformat = 'list'
    elif type(ValuesArray) == str :
        outformat = 'str'
        ValuesArray = list(' ' + ValuesArray + ' ')

    _verbose( speak , 1 , 'shifting from layer ' + str(skipK + 1) + ' by ' + str(shiftK) + ' layers' )

    Kskip = DIMENS[0] * DIMENS[1] * skipK
    NewArray = ValuesArray[:Kskip] + [str(DIMENS[0]*DIMENS[1]) + '*' + str(newValues)] + ValuesArray[Kskip:]

    _verbose( speak , 2 , 'property shifted')

    if compressed == True :
        NewArray = compressKeyword( NewArray , speak )

    if outformat == 'str' :
        NewArray = ' ' + ' '.join(NewArray) + ' '

    return NewArray
