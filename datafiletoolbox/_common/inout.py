# -*- coding: utf-8 -*-
"""
Created on Wed May 29 16:22:25 2019

@author: MCARAYA
"""

__version__ = '1.0.0'
__release__ = 210225
__all__ = ['_extension', '_verbose']


def _verbose(userLevel=0, programLevel=0, StringToPrint='',*args) :
    """
    According to the user desired level of verbosity ( userLevel ) and the
    defined program level ( programLevel ) of the message ( StringToPrint )
    verbose prints the message or not.

    The importance of the message is directly related to the value of level,
    the higher the level the more important the message

    if userLevel == 0 nothing will be printed

    if userLevel <= programLevel verbose will print the message

    if userLevel == -1 verbose will print every messages

    if programLevel == -1 verbose will print the messages,
    no matter the value of userLevel
    """
    # debugging only:
    #print('+++ userLevel: ' + str(userLevel) + '\n+++ programLevel: ' + str(programLevel))

    if type(StringToPrint) is list or type(StringToPrint) is tuple :
        StringToPrint = ' '.join(StringToPrint)
    else :
        StringToPrint = str(StringToPrint)
    if len(args) > 0 :
        StringToPrint = (StringToPrint + ' ' + ' '.join([str(a) for a in args])).rstrip()

    if userLevel == None :
        userLevel = 0
    if programLevel == None :
        programLevel = 0

    if len(StringToPrint) == 0 :
            print('\n verbose 0.2\n  syntax: verbose(userLevel, programLevel, StringToPrint)')
    elif userLevel < 0 or programLevel < 0 :
        print(StringToPrint)
    elif userLevel == 0 :
            pass
    elif userLevel <= programLevel :
        print(StringToPrint)
    else :
        pass


def _extension(filepath, NullValue='', backSlashToSlash=True, backCompatibility=False):
    """
    receives a string indicating a FileName.Extension or
    Path/FileName.Extension and return a tupple containing
    [0] the .Extension of the file in filepath,
    [1] the name of the FileName without extension,
    [2] the Directory containing the file,
    [3] the fullpath

    in case an item is not present an empty string is returned by default.
    """

    filepath = filepath.strip()

    if backSlashToSlash == True :
        filepath = filepath.replace('\\', '/')

    if '/' in filepath :
        lpath = len(filepath)-filepath[::-1].index('/')
        path = filepath[:lpath]
    else :
        lpath = 0
        path = ''

    if '.' in filepath[lpath:] :
        filename = filepath[lpath:len(filepath)-filepath[::-1].index('.')-1]
        extension = filepath[len(filepath)-filepath[::-1].index('.')-1:]
    else :
        filename = filepath[lpath:]
        extension = ''

    if backCompatibility :
        return ( filename, extension, path, path+filename+extension )

    return ( extension, filename, path, path+filename+extension )
