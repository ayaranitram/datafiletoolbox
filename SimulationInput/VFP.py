# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 12:24:58 2020

@author: MCARAYA
"""

from .propertyManipulation import expandKeyword
import pandas as pd
import numpy as np
from scipy.interpolate import interpn

class VFP(object) :
    """
    VFP is a class to load VFP tables and extract values from that VFP table.
    
    To load a VFP table, can provided:
        the simulation include file in eclipse format using paramenter 'InputFile'
        a diccionary with the keywords data read from the eclipse include, 
        using the paramenter 'KeywordData'
    
    To extract values from the VFP, call the VFP passing the arguments:
        RATE, THP, WFR, GFR, ALQ
    will return:
        a float, if a single value is returned
        a numpy array, if one of the parameters is not provided or a list is provided
        a dataframe, if more than one parameter are not provided or lists are provided
    
    For each not provided paramenter, all the values defining that parameter in 
    the VFP will be used to calculate the requested value.
    
    """
    def __init__(self,KeywordData=None,InputFile=None) :
        if KeywordData is None and InputFile is not None :
            from .readInput import readKeyword 
            KeywordData = readKeyword( InputFile )
        self.KeywordData = KeywordData
        self.records = []
        self.type = None
        self.number = None
        self.datum = None
        self.FLO = None
        self.WFR = None
        self.GFR = None
        self.FixedPressure = None
        self.ALQ = None
        self.units = None
        self.TabulatedQuantity = None
        self.FLOvalues = tuple()
        self.THPvalues = tuple()
        self.WFRvalues = tuple()
        self.GFRvalues = tuple()
        self.ALQvalues = tuple()
        self.VFPvalues = {}
        self.array = None
        self.dataframe = None
        self.VFPGridValues = None
        self.VFPGridAxes = None
        self._readData()

        
    def _readData(self,KeywordData=None) :
        if KeywordData is None :
            KeywordData = self.KeywordData
        if len(KeywordData) == 1 :
            self.type = list(KeywordData.keys())[0]
        self.records = KeywordData[self.type].split('/')
        records = KeywordData[self.type].split('/')
        
        # record 1
        record = self.records[0] + ' '
        record = expandKeyword(record.replace(" ' ' ",'1*'))
        record += ' ' + '1* '*(9-len(record.split()))
        record = record.split()
        self.number = int(record[0]) if record[0] != '1*' else None
        self.datum = float(record[1]) if record[1] != '1*' else None
        self.FLO = record[2] if record[2] != '1*' else 'GAS'
        self.WFR = record[3] if record[3] != '1*' else 'WCT'
        self.GFR = record[4] if record[4] != '1*' else 'GOR'
        self.FixedPressure = record[5] if record[5] != '1*' else 'THP'
        self.ALQ = record[6] if record[6] != '1*' else 'GRAT'
        self.units = record[7] if record[7] != '1*' else None
        if self.units is not None and self.units.upper() == 'METRIC' :
            self.units = { 'METRIC':'METRIC',
                          'RATE':'sm3/day',
                          'THP':'barsa',
                          'WCT':'fraction',
                          'GOR':'sm3/sm3',
                          'BHP':'barsa'}
        elif self.units is not None and self.units.upper() == 'FIELD' :
            self.units = { 'FIELD':'FIELD',
                          'RATE':'stb/day',
                          'THP':'psia',
                          'WCT':'fraction',
                          'GOR':'Mscf/stb',
                          'BHP':'psia'}
        
        self.TabulatedQuantity = record[8] if record[8] != '1*' else 'BHP'
        # records 2 to 6
        self.FLOvalues = tuple(map(float,records[1].split()))
        self.THPvalues = tuple(map(float,records[2].split()))
        self.WFRvalues = tuple(map(float,records[3].split()))
        self.GFRvalues = tuple(map(float,records[4].split()))
        self.ALQvalues = tuple(map(float,records[5].split()))
        # records 7+
        self.VFPvalues = {}
        for i in self.FLOvalues :
            self.VFPvalues[i] = {}
            for j in self.THPvalues :
                self.VFPvalues[i][j] = {}
                for k in self.WFRvalues :
                    self.VFPvalues[i][j][k] = {}
                    for l in self.GFRvalues :
                        self.VFPvalues[i][j][k][l] = {}
                        for m in self.ALQvalues :
                            self.VFPvalues[i][j][k][l][m] = []

        
        self.dataframe ={}
        self.array = np.zeros((len(self.FLOvalues),len(self.THPvalues),len(self.WFRvalues),len(self.GFRvalues),len(self.ALQvalues)))
        
        for r in range(6,len(records)) :
            if len( records[r].strip() ) > 0 :
                temp = [ float(i) for i in records[r].split() ]
                thp = self.THPvalues[int(temp[0])-1]
                wfr = self.WFRvalues[int(temp[1])-1]
                gfr = self.GFRvalues[int(temp[2])-1]
                alq = self.ALQvalues[int(temp[3])-1]
                for i in range(len(self.FLOvalues)) :
                    rate = self.FLOvalues[i]
                    self.VFPvalues[rate][thp][wfr][gfr][alq] = temp[i+4]
                    self.dataframe[(rate,thp,wfr,gfr,alq)] = temp[i+4]
                    self.array[i][int(temp[0])-1][int(temp[1])-1][int(temp[2])-1][int(temp[3])-1] = temp[i+4]
        
        self.VFPGridValues = np.squeeze(self.array)
        self.VFPGridAxes = []
        
        axes = (self.FLOvalues,self.THPvalues,self.WFRvalues,self.GFRvalues,self.ALQvalues)
        for axis in axes :
            if len(axis) > 1 :
                self.VFPGridAxes.append(np.array(axis,dtype='float'))
        self.VFPGridAxes = tuple(self.VFPGridAxes)
                    
        multindex = list(self.dataframe.keys())
        serie = list(self.dataframe.values())
        multindex = pd.MultiIndex.from_tuples(multindex, names=['RATE','THP','WFR','GFR','ALQ'])
        self.dataframe = pd.DataFrame(data={'BHP':serie}, index=multindex)        
        
                           
    def __call__(self,RATE=None,THP=None,WFR=None,GFR=None,ALQ=None,**kwargs) :
        
        if type(RATE) is tuple and len(RATE)==5 and THP is None and WFR is None and GFR is None and ALQ is None:
            RATE, THP, WFR, GFR, ALQ = RATE[0], RATE[1], RATE[2], RATE[3], RATE[4]
        
        lookfor = [RATE,THP,WFR,GFR,ALQ]
        
        ranges = [self.FLOvalues,self.THPvalues,self.WFRvalues,self.GFRvalues,self.ALQvalues]
        corrected = False
        if 'multipleCount' in kwargs :
            multipleCount = kwargs['multipleCount']
        else :
            multipleCount = 0
        for x in range(len(lookfor)) :
            if lookfor[x] is None :
                corrected = True
                if len(ranges[x]) == 1:
                    lookfor[x] = ranges[x][0]
                else :
                    lookfor[x] = ranges[x]
                    multipleCount += 1
        
        if corrected :
            for k in ['RATE','THP','WFR','GFR','ALQ'] :
                kwargs.pop(k,None)
                kwargs['multipleCount'] = multipleCount
            return self.__call__(lookfor[0],lookfor[1],lookfor[2],lookfor[3],lookfor[4],**kwargs)

        if tuple(lookfor) in self.dataframe.index :
            return self.dataframe.loc[tuple(lookfor)].BHP
            
        sqeezedlookfor=[]
        axes = (self.FLOvalues,self.THPvalues,self.WFRvalues,self.GFRvalues,self.ALQvalues)
        for i in range(len(axes)) :
            if len(axes[i]) > 1 :
                sqeezedlookfor.append(lookfor[i])
        sqeezedlookfor = tuple(sqeezedlookfor)
        
        for k in ['RATE','THP','WFR','GFR','ALQ','multipleCount'] :
            kwargs.pop(k,None)
        if 'method' not in kwargs :
            kwargs['method'] = 'linear'
        
        if multipleCount <= 1 :
            result = interpn(self.VFPGridAxes,self.VFPGridValues,sqeezedlookfor,**kwargs)
            if len(result)==1:
                return float(result)
            else :
                return result
        else :
            result = {}
            loopfor = []
            for rate in [lookfor[0]] if type(lookfor[0]) in [int,float] else lookfor[0] :
                for thp in [lookfor[1]] if type(lookfor[1]) in [int,float] else lookfor[1] :
                    for wfr in [lookfor[2]] if type(lookfor[2]) in [int,float] else lookfor[2] :
                        for gfr in [lookfor[3]] if type(lookfor[3]) in [int,float] else lookfor[3] :
                            for alq in [lookfor[4]] if type(lookfor[4]) in [int,float] else lookfor[4] :
                                loopfor.append( ( rate , thp , wfr , gfr , alq ) )
            for each in loopfor :
                result[each] = self.__call__(each)
            multindex = list(result.keys())
            serie = list(result.values())
            multindex = pd.MultiIndex.from_tuples(multindex, names=['RATE','THP','WFR','GFR','ALQ'])
            return pd.DataFrame(data={'BHP':serie}, index=multindex)  
                
            
            
        
        
        

                    
                    