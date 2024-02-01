# -*- coding: utf-8 -*-
"""
Created on Thu Oct 22 12:24:58 2020

@author: MCARAYA
"""

from .propertyManipulation import expandKeyword
import pandas as pd
import numpy as np
from scipy.interpolate import interpn, interp1d

class VFP(object) :
    """
    VFP is a class to load VFP tables and extract values from that VFP table.
    
    To load a VFP table, can be provided:
        the simulation include file in eclipse format using parameter 'InputFile'
        a dictionary with the keywords data read from the eclipse include,
        using the parameter 'KeywordData'
    
    To extract values from the VFP, call the VFP passing the arguments:
        RATE, THP, WFR, GFR, ALQ
    will return:
        a float, if a single value is returned
        a numpy array, if one of the parameters is not provided or a list is provided
        a dataframe, if more than one parameter are not provided or lists are provided
    
    For each not provided parameter, all the values defining that parameter in
    the VFP will be used to calculate the requested value.
    
    """
    def __init__(self, keyword_data=None, input_file=None) :
        if keyword_data is None and input_file is not None :
            from .readInput import readKeyword 
            keyword_data = readKeyword(input_file)
        self.KeywordData = keyword_data
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
        self.FLO_values = tuple()
        self.THP_values = tuple()
        self.WFR_values = tuple()
        self.GFR_values = tuple()
        self.ALQ_values = tuple()
        self.VFP_values = {}
        self.array = None
        self.dataframe = None
        self.VFPGridValues = None
        self.VFPGridAxes = None
        self.extrapolate=True
        self._read_data()

        
    def _read_data(self, keyword_data=None):
        if keyword_data is None :
            keyword_data = self.KeywordData
        if len(keyword_data) == 1 :
            self.type = list(keyword_data.keys())[0]
        self.records = keyword_data[self.type].split('/')
        records = keyword_data[self.type].split('/')
        
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
        self.FLO_values = tuple(map(float, records[1].split()))
        self.THP_values = tuple(map(float, records[2].split()))
        self.WFR_values = tuple(map(float, records[3].split()))
        self.GFR_values = tuple(map(float, records[4].split()))
        self.ALQ_values = tuple(map(float, records[5].split()))
        # records 7+
        self.VFP_values = {}
        for i in self.FLO_values :
            self.VFP_values[i] = {}
            for j in self.THP_values :
                self.VFP_values[i][j] = {}
                for k in self.WFR_values :
                    self.VFP_values[i][j][k] = {}
                    for l in self.GFR_values :
                        self.VFP_values[i][j][k][l] = {}
                        for m in self.ALQ_values :
                            self.VFP_values[i][j][k][l][m] = []

        self.dataframe ={}
        self.array = np.zeros((len(self.FLO_values), len(self.THP_values), len(self.WFR_values), len(self.GFR_values), len(self.ALQ_values)))
        
        for r in range(6,len(records)) :
            if len( records[r].strip() ) > 0 :
                temp = [ float(i) for i in records[r].split() ]
                thp = self.THP_values[int(temp[0]) - 1]
                wfr = self.WFR_values[int(temp[1]) - 1]
                gfr = self.GFR_values[int(temp[2]) - 1]
                alq = self.ALQ_values[int(temp[3]) - 1]
                for i in range(len(self.FLO_values)) :
                    rate = self.FLO_values[i]
                    self.VFP_values[rate][thp][wfr][gfr][alq] = temp[i + 4]
                    self.dataframe[(rate,thp,wfr,gfr,alq)] = temp[i+4]
                    self.array[i][int(temp[0])-1][int(temp[1])-1][int(temp[2])-1][int(temp[3])-1] = temp[i+4]
        
        self.VFPGridValues = np.squeeze(self.array)
        self.VFPGridAxes = []
        
        axes = (self.FLO_values, self.THP_values, self.WFR_values, self.GFR_values, self.ALQ_values)
        for axis in axes :
            if len(axis) > 1 :
                self.VFPGridAxes.append(np.array(axis,dtype='float'))
        self.VFPGridAxes = tuple(self.VFPGridAxes)
                    
        multindex = list(self.dataframe.keys())
        serie = list(self.dataframe.values())
        multindex = pd.MultiIndex.from_tuples(multindex, names=['RATE','THP','WFR','GFR','ALQ'])
        self.dataframe = pd.DataFrame(data={'BHP':serie}, index=multindex)


    def inRange(self, RATE=None, THP=None, WFR=None, GFR=None, ALQ=None) :
        return self.in_range(RATE=RATE, THP=THP, WFR=WFR, GFR=GFR, ALQ=ALQ)
    def in_range(self,RATE=None,THP=None,WFR=None,GFR=None,ALQ=None) :
        if type(RATE) is tuple and len(RATE)==5 and THP is None and WFR is None and GFR is None and ALQ is None:
            RATE, THP, WFR, GFR, ALQ = RATE[0], RATE[1], RATE[2], RATE[3], RATE[4]
        result = []
        values = [self.FLO_values, self.THP_values, self.WFR_values, self.GFR_values, self.ALQ_values]
        inputs = ['RATE','THP','WFR','GFR','ALQ']
        for i in range(5) :
            if eval(inputs[i]) is not None :
                if eval(inputs[i]) < min(values[i]) or eval(inputs[i]) > max(values[i]) :
                    result += [inputs[i]]
                    print( inputs[i],'value out of range:\n   ',eval(inputs[i]),'not in [ '+str(min(values[i]))+' : '+str(max(values[i]))+' ]')
        return not bool(result) , '' + ' '.join(result)
                    

    def __call__(self,RATE=None,THP=None,WFR=None,GFR=None,ALQ=None,**kwargs) :
        """
        given RATE, THP, WFR, GFR and ALQ calculates the corresponding BHP using 
        the loaded VFP table.
        All input and output values in the table unit system.
        
        allowExtrapolation=True by default
        """
        extrapolate=self.extrapolate
        
        if type(RATE) is tuple and len(RATE)==5 and THP is None and WFR is None and GFR is None and ALQ is None:
            RATE, THP, WFR, GFR, ALQ = RATE[0], RATE[1], RATE[2], RATE[3], RATE[4]
        
        lookfor = [RATE,THP,WFR,GFR,ALQ]
        
        ranges = [self.FLO_values, self.THP_values, self.WFR_values, self.GFR_values, self.ALQ_values]
        corrected = False
        if 'multiple_count' in kwargs :
            multiple_count = kwargs['multiple_count']
        else :
            multiple_count = 0
        for x in range(len(lookfor)) :
            if lookfor[x] is None :
                corrected = True
                if len(ranges[x]) == 1:
                    lookfor[x] = ranges[x][0]
                else :
                    lookfor[x] = ranges[x]
                    multiple_count += 1
        
        if corrected :
            for k in ['RATE','THP','WFR','GFR','ALQ'] :
                kwargs.pop(k,None)
            kwargs['multiple_count'] = multiple_count
            return self.__call__(lookfor[0],lookfor[1],lookfor[2],lookfor[3],lookfor[4],**kwargs)

        if tuple(lookfor) in self.dataframe.index :
            return self.dataframe.loc[tuple(lookfor)].BHP
            
        squeezed_look_for=[]
        axes = (self.FLO_values, self.THP_values, self.WFR_values, self.GFR_values, self.ALQ_values)
        for i in range(len(axes)) :
            if len(axes[i]) > 1 :
                squeezed_look_for.append(lookfor[i])
        squeezed_look_for = tuple(squeezed_look_for)
        
        if 'allowExtrapolation' in kwargs :
            kwargs['bounds_error'] = kwargs['allowExtrapolation']
            extrapolate = bool(kwargs['allowExtrapolation'])
        for k in ['RATE','THP','WFR','GFR','ALQ','multiple_count','allowExtrapolation'] :
            kwargs.pop(k,None)
        if 'method' not in kwargs :
            kwargs['method'] = 'linear'
        if 'bounds_error' not in kwargs :
            kwargs['bounds_error'] = False

        
        if multiple_count <= 1 :
            result = interpn(self.VFPGridAxes,self.VFPGridValues,squeezed_look_for,**kwargs)
            if extrapolate is True and len(result)==1 and ( not result[0]>=0 and not result[0]<0 ) :
                out_range = self.in_range(RATE=RATE, THP=THP, WFR=WFR, GFR=GFR, ALQ=ALQ)[1]
                limits = {}
                values = {'RATE':self.FLO_values, 'THP':self.THP_values, 'WFR':self.WFR_values, 'GFR':self.GFR_values, 'ALQ':self.ALQ_values}
                for each in out_range.split()  :
                    if eval(each) < min(values[each]) :
                        limits[each] = ( values[each][0] , values[each][1] ) if len(values[each])>1 else ( values[each][0] ,)
                    elif eval(each) > max(values[each]) :
                        limits[each] = ( values[each][-2] , values[each][-1] ) if len(values[each])>1 else ( values[each][-1] ,)
                to_interpolate = {}
                result = {}
                for each in limits :
                    to_interpolate[each] = []
                    result[each] = []
                    for i in range(len(limits[each])) :
                        tup = []
                        for var in ['RATE','THP','WFR','GFR','ALQ'] :
                            tup += [ limits[each][i] if var in limits else eval(var) ]
                        to_interpolate[each] += [ self( tuple(tup) ) ]
                    result[each] += [ float( interp1d( np.array(limits[each]), np.array(to_interpolate[each]),
                                                       bounds_error=False,fill_value="extrapolate" )(eval(each)) ) , {'lookfor':eval(each),'x':np.array(limits[each]),'y':np.array(to_interpolate[each])} ]
                if len(result)==1 :
                    result = np.array([result[list(result.keys())[0]][0]])
                elif len(result)==2 :
                    x2D = result[list(result.keys())[1]][1]['x']
                    look2D = result[list(result.keys())[0]][1]['lookfor']
                    look_final = result[list(result.keys())[1]][1]['lookfor']
                    y2D = []
                    for i in range(len(x2D)) :
                        lookY = []
                        for var in ['RATE','THP','WFR','GFR','ALQ'] :
                            lookY.append( look2D if var == list(result.keys())[0] else x2D[i] if var == list(result.keys())[1] else eval(var) )
                        y2D.append( self.__call__( tuple(lookY) ,**kwargs) )
                    cath = float( interp1d( np.array(x2D), np.array(y2D) ,bounds_error=False,fill_value="extrapolate" )( look_final ) )
                    result = np.array([cath])
                elif len(result)>2 :
                    pass
                    # finalresult = {}
                    # finalresult[list(result.keys())[0]] = result[list(result.keys())[0]].copy()
                    # for r in range(1,len(result)) :
                    #     x2D = result[list(result.keys())[r]][1]['x']
                    #     look2D = finalresult[1]['lookfor']
                    #     look_final = result[list(result.keys())[1]][1]['lookfor']
                    #     y2D = []
                    #     for i in range(len(x2D)) :
                    #         lookY = []
                    #         for var in ['RATE','THP','WFR','GFR','ALQ'] :
                    #             lookY.append( look2D if var == list(result.keys())[0] else x2D[i] if var == list(result.keys())[1] else eval(var) )
                    #         y2D.append( self.__call__( tuple(lookY) ,**kwargs) )
                    #     cath = float( interp1d( np.array(x2D), np.array(y2D) ,bounds_error=False,fill_value="extrapolate" )( look_final ) )
                    #     result['result'] = np.array([cath])
                    
            if len(result)==1:
                return float(result)
            else :
                return result
        else :
            result = {}
            loop_for = []
            for rate in [lookfor[0]] if type(lookfor[0]) in [int,float] else lookfor[0] :
                for thp in [lookfor[1]] if type(lookfor[1]) in [int,float] else lookfor[1] :
                    for wfr in [lookfor[2]] if type(lookfor[2]) in [int,float] else lookfor[2] :
                        for gfr in [lookfor[3]] if type(lookfor[3]) in [int,float] else lookfor[3] :
                            for alq in [lookfor[4]] if type(lookfor[4]) in [int,float] else lookfor[4] :
                                loop_for.append( ( rate , thp , wfr , gfr , alq ) )
            for each in loop_for :
                result[each] = self.__call__(each)
            multindex = list(result.keys())
            serie = list(result.values())
            multindex = pd.MultiIndex.from_tuples(multindex, names=['RATE','THP','WFR','GFR','ALQ'])
            return pd.DataFrame(data={'BHP':serie}, index=multindex)  
                
            
            
        
        
        

                    
                    