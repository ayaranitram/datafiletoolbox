# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 09:46:24 2022

@author: MCARAYA
"""

import string

def readSMSPEC(smspecPath):
    """
    read the SMSPEC file and extract the well and group names
    """
    if type(smspecPath) is str :
        smspecPath = smspecPath.strip()
        if _extension(smspecPath)[0].lower() != '.SMSPEC' :
            newPath = _extension(smspecPath)[2] + _extension(smspecPath)[1] + '.SMSPEC'
            if os.path.isfile(newPath):
                smspecPath = newPath
        if os.path.isfile(smspecPath):
            if os.path.getsize(smspecPath) == 0:
                warnings.warn("\nThe .SMSPEC file seems to be empty")
        else :
            warnings.warn( "the file doesn't exist:\n  -> " + smspecPath )
    with open(smspecPath, 'rb') as file:
        smspec = file.read()

    temp = [ chr(b) if chr(b) in string.printable else int(b) for b in smspec ]

    temp2 = []
    for t in temp:
        if type(t) is int:
            temp2.append(t)
        else:  # if type(t) is str:
            if len(temp2) == 0 or type(temp2[-1]) is int:
                temp2.append(t)
            else:  # if type(temp2[-1]) is str:
                temp2[-1] = temp2[-1] + t

    data = {}
    i = 0
    while i < len(temp2):
        h = len(temp2)-1 if 16 not in temp2[i:] else i + temp2[i:].index(16) + 1
        f = len(temp2)-1 if 16 not in temp2[h:] else h + temp2[h:].index(16) + 1
        d = len(temp2)-1 if 16 not in temp2[f:] else f + temp2[f:].index(16)
        data[temp2[h]] = [temp2[h+1:f],temp2[f+1:d+1]]
        i = f + 1

    for k in ['KEYWORDS','']
        if k in data:
            data[k] = data[k][1][2]

    keywords_index =  smspec.index('\x00\x00\x10KEYWORDS')
    keywords_index = keywords_index + smspec[keywords_index:].index('\x00\x00\x03H') + 4
    names_index = keywords_index + smspec[keywords_index:].index('\x00\x00\x10NAMES   ')
    keywords = smspec[keywords_index:names_index]
    keywords = [ keywords[i:i+8].strip() for i in range(0,len(keywords),8) ]

    names_index = names_index + smspec[names_index:].index('\x00\x00\x03H') + 4

    nums_index = names_index + smspec[names_index:].index('NUMS    ')

    names = smspec[names_index:nums_index]
    names = [ names[i:i+8].strip() for i in range(0,len(names),8) ]

    units_index = nums_index + smspec[nums_index:].index('\x00\x00\x10UNITS   ')
    units_index = units_index + smspec[units_index:].index('\x00\x00\x03H') + 4
    measrmnt_index = units_index + smspec[units_index:].index('\x00\x00\x10MEASRMNT')
    units = smspec[units_index:measrmnt_index]
    units = [ units[i:i+8].strip() for i in range(0,len(units),8) ]

    self.units = { keywords[i]+(':'+names[i] if len(names[i])>0 else '') : units[i] for i in range(len(keywords)) }

    self.keynames = {}
    for i in range(len(keywords)):
        if keywords[i] not in self.keynames:
            self.keynames[keywords[i]] = []
        if names[i] not in self.keynames[keywords[i]]:
            self.keynames[keywords[i]].append(names[i])
