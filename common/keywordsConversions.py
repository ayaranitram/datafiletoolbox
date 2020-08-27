# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 13:59:36 2020

@author: MCARAYA
"""
from datafiletoolbox.dictionaries import ECL2VIPtype , ECL2VIPkey , VIP2ECLtype , VIP2ECLkey
from datafiletoolbox.dictionaries import ECL2CSVtype , ECL2CSVkey , CSV2ECLtype , CSV2ECLkey
from datafiletoolbox.common.inout import verbose 
from datafiletoolbox.dictionaries import UniversalKeys
from datafiletoolbox.common.functions import mainKey
    
def testECLmolarKey(key) :
    if '_' in key :
        if ':' in key :
            var = key.strip().split(':')[0].upper()
            clss = var[0]
            var = var[1:]
            member = key.strip().split(':')[1].upper()
        else :
            member = ''
            var = key.strip().upper()
            clss = var[0]
            var = var[1:]
        if '_' in var :
            comp = var[var.index('_'):]
        else :
            return False
        try :
            comp = int(comp)
        except :
            return False
        if var[0] in ('X','Y','Z') :
            xyz = var[0]
        elif var[0] == 'C' :
            xyz = ''
            if var[var.index('_')-1] == 'R' :
                xyz = 'Q'
            elif var[var.index('_')-1] == 'T' :
                xyz = 'C'
            else:
                return False
            if var[var.index('_')-2] in ( 'P','I' ) :
                pi = var[var.index('_')-2]
            else :
                return False
        else :
            return False
        if clss in ECL2VIPtype :
            clss = ECL2VIPtype[clss]
        else :
            return False
        VIPkey = xyz + str(comp) + pi
        return ( VIPkey , clss , member )
    else :
        return False
    
def testCSVmolarKey(variableORkey,CLASStype=None,MEMBER=None) :
    variableORkey = variableORkey.strip().upper()
    if ':' in variableORkey :
        if MEMBER is None and len(variableORkey.split(':')[1]) > 0 :
            MEMBER = variableORkey.split(':')[1]
        variableORkey.split(':')[0]
    if variableORkey[-1] in ( 'P','I' ) :
        pi = variableORkey[-1]
    else :
        return False
    if variableORkey[0] in ('X','Y','Z') :
        xyz = variableORkey[0]
        rt = 'MF'
        pi = ''
    elif variableORkey[0] == 'Q' :
        rt = 'R'
        xyz = 'CM'
    elif variableORkey[0] == 'C' :
        rt = 'T'
        xyz = 'CM'
    else :
        return False
    
    comp = variableORkey[1:-1]
    try :
        comp = int(comp)
    except :
        return False
           
    if CLASStype != None and CLASStype in CSV2ECLtype[CLASStype] :
        keyType = CSV2ECLtype[CLASStype] 
    else :
        return False
    if MEMBER is None :
        MEMBER = ''
    if MEMBER != None and MEMBER != 'FIELD':
        MEMBER = ':' + MEMBER.upper()
    elif CLASStype != None and MEMBER == 'FIELD' :
        keyType = 'F'
    
    ECLkey = keyType + xyz + rt + pi + '_' + str(comp)
    return ECLkey
    
def fromECLtoVIP(key,speak=0) :
    verbose( speak , 1 , 'translating ' + str(key) + ' from ECL to VIP style.')
    test = testECLmolarKey(key)
    if type(test) == tuple :
        return test[0] , test[1] , test[2]
    
    key = key.strip().upper()
    if ':' in key :
        keyName = key[key.index(':')+1:]
        keyRoot = key[:key.index(':')]
        keyType = 'W'
        if keyRoot in UniversalKeys :
            keyType = 'W'
        else :
            keyType = keyRoot[0]
            keyRoot = keyRoot[1:]
        if keyRoot in ( 'BHP' , 'THP' ) :
            keyType = 'W'
        if keyType == 'F' :
            keyName = 'ROOT'
        if keyType != '' and keyType in ECL2VIPtype :
            keyType = ECL2VIPtype[keyType]
        if keyRoot in ECL2VIPkey :
            VIPkey = ECL2VIPkey[keyRoot]
        else :
            VIPkey = keyRoot
    else :
        keyName = 'ROOT'
        keyRoot = key
        keyType = key[0]
        if keyRoot in UniversalKeys :
            keyType = 'F'
        else :
            keyType = keyRoot[0]
            keyRoot = keyRoot[1:]
        if keyRoot in ( 'BHP' , 'THP' ) :
            keyType = 'W'
            keyName = ''
        if keyType == 'F' :
            keyName = 'ROOT'
        if keyType != '' and keyType in ECL2VIPtype :
            keyType = ECL2VIPtype[keyType]
        if keyRoot in ECL2VIPkey :
            VIPkey = ECL2VIPkey[keyRoot]
        else :
            VIPkey = keyRoot

    verbose( speak , 1 ,'ECLIPSE key ' + key + ' interpreted as VIP key ' + VIPkey + ' for ' + str(keyType) + ' summary for the item ' + keyName )
    return VIPkey , keyType , keyName

def fromVIPtoECL(key,SSStype=None,speak=0):
    if SSStype != None :
        S = ' of ' + str(SSStype)
    else :
        S = ''
    verbose( speak , 1 , 'translating ' + str(key) + S + ' from VIP to ECL style.')
    key = key.strip().upper()
    if ':' in key :
        keyName = key[key.index(':')+1:]
        keyRoot = key[:key.index(':')]
        keyType = 'W'
        ConvertedRoot = keyRoot
        if keyRoot in VIP2ECLkey :
            ConvertedRoot = VIP2ECLkey[ keyRoot ]  
        if keyRoot in ( 'BHP' , 'THP' , 'AVG PRES' ) :
            keyType = 'W'
        if keyName == 'ROOT' :
            keyType = 'F'
            keyName = ''
        else :
            keyName = ':' + keyName
        if SSStype != None and SSStype in VIP2ECLtype :
            keyType = VIP2ECLtype[SSStype]
        if keyRoot in UniversalKeys :
            keyType = ''
    else :
        keyName = ''
        keyRoot = key
        keyType = 'F'
        ConvertedRoot = keyRoot
        if keyRoot in VIP2ECLkey :
            ConvertedRoot = VIP2ECLkey[ keyRoot ] 
        if key in ( 'BHP' , 'THP' , 'AVG PRES' ) :
            keyType = 'W'
        if key in VIP2ECLkey :
            keyRoot = VIP2ECLkey[key]
        if SSStype != None and SSStype in VIP2ECLtype :
            keyType = VIP2ECLtype[SSStype]
        if keyRoot in UniversalKeys :
            keyType = ''
   
    if keyRoot == '' :
        verbose( speak , 1 ,'CSV variable ' + key + ' not converted to ECL key.' )
        return None
    ECLkey = keyType + ConvertedRoot + keyName
    verbose( speak , 1 ,'VIP key ' + key + ' interpreted as ECL key ' + ECLkey )
    return ECLkey

def fromCSVtoECL(variableORkey,CLASStype=None,MEMBER=None,speak=0):
    test = testCSVmolarKey(variableORkey,CLASStype,MEMBER)
    if type(test) == str :
        return test
    
    if CLASStype != None :
        C = ' of class ' + str(CLASStype)
    if MEMBER != None :
        M = ' for ' + str(MEMBER)
    verbose( speak , 1 , 'translating ' + str(variableORkey) + C + M + ' from CSV to ECL style.')
    
    keyType = None
    if CLASStype != None :
        if CLASStype in CSV2ECLtype :
            keyType = CSV2ECLtype[CLASStype] 

    if MEMBER != None and len(MEMBER.strip()) > 0 :
        keyName = MEMBER.strip().upper()
        if keyName in ( 'FIELD' , 'ROOT' ) :
            keyName = ''
        else :
            keyName = ':' + keyName
    else :
        keyName = None
        
    key = mainKey(variableORkey).upper()
    if key in UniversalKeys :
        keyType = ''
    if key in CSV2ECLkey :
        keyRoot = CSV2ECLkey[key]
    else :
        keyRoot = None 
    
    verbose( speak , 1 , str(keyType) + ' ' + str(keyRoot) + ' ' + str(keyName) )
    if keyRoot != None and keyType != None and keyName != None :
        return keyType + keyRoot + keyName

def fromECLtoCSV(key,speak=0) :
    verbose( speak , 1 , 'translating ' + str(key) + ' from ECL to CSV style.')
    test = testECLmolarKey(key)
    if type(test) == tuple :
        return test[0] , test[1] , test[2]
    
    key = key.strip().upper()
    if ':' in key :
        keyName = key[key.index(':')+1:]
        keyRoot = key[:key.index(':')]
        keyType = 'W'
        if keyRoot in UniversalKeys :
            keyType = 'MISCELLANEOUS'
            keyName = ''
        else :
            keyType = keyRoot[0]
            keyRoot = keyRoot[1:]
        if keyRoot in ( 'BHP' , 'THP' ) :
            keyType = 'W'
        if keyType == 'F' :
            keyName = 'FIELD'
        if keyType != '' and keyType in ECL2CSVtype :
            keyType = ECL2CSVtype[keyType]
        if keyRoot in ECL2CSVkey :
            CSVkey = ECL2CSVkey[keyRoot]
        else :
            CSVkey = keyRoot
    else :
        keyName = 'FIELD'
        keyRoot = key
        keyType = key[0]
        if keyRoot in UniversalKeys :
            keyType = 'MISCELLANEOUS'
            keyName = ''
        else :
            keyType = keyRoot[0]
            keyRoot = keyRoot[1:]
        if keyRoot in ( 'BHP' , 'THP' ) :
            keyType = 'W'
            keyName = ''
        if keyType == 'F' :
            keyName = 'FIELD'
        if keyType != '' and keyType in ECL2CSVtype :
            keyType = ECL2CSVtype[keyType]
        if keyRoot in ECL2CSVkey :
            CSVkey = ECL2CSVkey[keyRoot]
        else :
            CSVkey = keyRoot

    verbose( speak , 1 ,'ECLIPSE key ' + key + ' interpreted as CSV key ' + CSVkey + ' for ' + str(keyType) + ' summary for the item ' + keyName )
    return CSVkey , keyType , keyName