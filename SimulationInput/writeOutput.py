#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 22:59:49 2019

@author: martin

routine to export, write to ASCII file in eclipse style a property.
"""

__version__ = '0.0.20-10-16'
__all__ = ['exportProperty']

from .._common.inout import _extension , _verbose 
from os import getcwd
import numpy as np
import pandas as pd

def exportProperty(keywordName , KeywordValues , outputFile='' , ECHOkeyword=False , charactersPerLine = 128 , speak=0) :
    """
    exportProperty writes the ASCII file for the keyword name and values received
    in the first and second argument

    the parameter ECHOkeyword:
        set to True will write 'ECHO' before the output
        set to False will write 'NOECHO' before the output

    the optional argument speak controls the verbosity of expandKeyword, where:
        0 = not ouptut at all
        1 = print every message
        2 = print final statement only
    """


    valuesPerLine = charactersPerLine - 3

    if len(outputFile) == 0 :
        outputFile = getcwd() + '/' + str(keywordName) +  '.inc'

    if type(KeywordValues) is np.array :
        KeywordValues = list(KeywordValues)
    if type(KeywordValues) is list :
        KeywordValues = ' ' + ' '.join(map(str,KeywordValues)) + ' '
    elif type(KeywordValues) is str :
        if KeywordValues[0] != ' ' :
            KeywordValues = ' ' + KeywordValues
        if KeywordValues[-1] != ' ' :
            KeywordValues = KeywordValues + ' '
    else :
        _verbose(speak , 3 , '  ERROR : incorrect type of input KeywordValues in property ' + str(keywordName) )
        return 'incorrect type of input KeywordValues'

    totalvalues = len(KeywordValues)

    file = open( outputFile , 'w')

    if ECHOkeyword == False :
        file.write('NOECHO\n\n')
    else :
        file.write('ECHO\n\n')

    file.write(str(keywordName) + '\n')

    prog = 0

    firstValue = 0
    lastValue = valuesPerLine
    # write all the entire lines
    while firstValue <= totalvalues :
        space = KeywordValues[lastValue:firstValue:-1].index(' ')
        lastValue = lastValue - space
        lineToWrite = KeywordValues[firstValue:lastValue] + ' '
        file.write(lineToWrite + '\n')
        firstValue = lastValue
        lastValue = firstValue + valuesPerLine
        if lastValue >= totalvalues:
            lastValue = totalvalues
            lineToWrite = KeywordValues[firstValue:lastValue] + ' '
            file.write(lineToWrite + '\n')
            firstValue = totalvalues + 1

        if prog < 100*lastValue//totalvalues :
            prog = 100*lastValue//totalvalues
            _verbose(speak , 1 , 'writing property ' + str(keywordName) + ' | ' + str(prog) + '%')

    file.write('/ \n')
    file.close()

    if prog < 100 :
        _verbose(speak , 1 , 'writing property ' + str(keywordName) + ' | 100%')

    _verbose(speak , 2 , 'property written ' + str(keywordName) + ' -> Done!')

    return True


def multiExport(keywordName , KeywordValues , outputFile='') :
    for key in range(len(keywordName)) :
        exportProperty(keywordName[key] , KeywordValues[key] , str(_extension(outputFile)[2] + _extension(outputFile)[0] + '_' + keywordName[key] + _extension(outputFile)[1] ) )
