# -*- coding: utf-8 -*-
"""
Created on Wed May 29 16:22:25 2019

@author: MCARAYA
"""

__version__ = '0.0.20-05-16'

def verbose(userLevel=0 , programLevel=0 , StringToPrint='') :
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
    
    if userLevel == None :
        userLevel = 0
    if programLevel == None :
        programLevel = 0
    
    if len(StringToPrint) == 0 :
            print('\n verbose 0.2\n  syntax: verbose(userLevel , programLevel , StringToPrint)')
    elif userLevel < 0 or programLevel < 0 :
        print(StringToPrint)
    elif userLevel == 0 :
            pass
    elif userLevel <= programLevel :
        print(StringToPrint)
    else :
        pass



def extension(filepath , NullValue='' , backSlashToSlash=True , backCompatibility=False):
    """
    receives a string indicating a FileName.Extension or 
    Path/FileName.Extension and return a tupple containing 
    [0] the name of the FileName in the first position, 
    [1] the .Extension in the second position and
    [2] the \Path in the third position.
    [3] the fullpath
    
    in case an item is not present an empty string is returned by default.
    """
    
    filepath = filepath.strip()
    
    if backSlashToSlash == True :
        filepath = filepath.replace('\\','/')
    
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
        return ( filename , extension , path , path+filename+extension )
    else :
        return ( extension , filename , path , path+filename+extension )



def openFile(path, mode='r') :
    """
    openFile receives a string indicating the path to a file,
    checks the file exists and return the file object opened.
    
    By default the file will be opened in read only mode, 
    other modes can be espefied as string in the second argument.
    
    Accepted open modes are:
        'r'   read only, default mode
        'w'   write, if file exists overwrite
        'x'   new file. Fails if already exists
        'a'   append mode
        't'   text mode, default
        'b'   binary mode
        '+'   updating, reading and writing
    """
    filePathIN = path
    fileFlag = False
    while fileFlag == False :
        try :
            if len(filePathIN) == 0 :
                filePathIN = input('enter path to file be read: ')
        except :
            filePathIN = input('enter path to file be read: ')

        try : 
            fileIN = open(filePathIN , mode)
            fileFlag = True
            print('  opening input file\n' + filePathIN)
        except :
            print(' file not found, check filename and try again.')
            filePathIN = None
    return fileIN
