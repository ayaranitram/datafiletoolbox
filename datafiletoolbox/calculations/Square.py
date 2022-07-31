# -*- coding: utf-8 -*-
"""
Created on Wed May 13 15:00:45 2020

@author: MCARAYA
"""

__version__ = '0.1.0'
__release__ = 210225
__all__ = ['SquareDifferences']

from .._common.inout import _verbose
import numpy as np
import pandas as pd

def SquareDifferences( SimResultObjects=[], AttributesOrKeys=[], TimeSteps=None, Interpolate=False ) :
    """
    Calculates the square difference of two or more SimResults objects.
    Return a tuple containing :
        the total of the square difference
        the partial totals of square differences forevery key
        the profile of the total square difference
        the DataFrame of the square difference for every matching key
        a dictionary with all the produced input DataFrames

    Parameters:
        SimResultObjects is a list of the objects to opetate with.
        Usually only two objects are passed but could be more than two,
        in which case all the other objects will be compared to the
        first object and the total summation returned.
            SimResultObjects=[Results1, Results2] where Results1
            and Results2 are SimResult objects

            SqDiff = sum( ( Profile[0] - Profile[i] )**2 )

        AttributesOrKeys is a list of attributes or keys to compare.
            The attributes or keys must exist in both SimResult objects.
            If a well, group or region attribute is requested all the
            corresponding and matching keys will be used.
            i.e:
                FOPT, WBHP, GGPR, RPPO are attributes
                but WBHP:W1, RPPO:1, GGPR:G1 are keys
                the attibute WBHP will generate the key WBHP:W1
                and any other matching wells
        TimeSteps is the list or array of timesteps to be compared.
            If empty all the coinciding TimeSteps will be calculated.
        Interpolate set to True allows the function to interpolate the
            TimeSteps not matching both SimResult objects.
    """
    MatchingKeys = []
    # MatchingTimes = []
    Atts = []
    TimeKind = 'TIME'
    verbosity = SimResultObjects[0].get_Verbosity()
    _verbose( verbosity, 1, ' < SqDiff > sarting with verbosity set to ' + str(verbosity))

    _verbose( verbosity, 1, ' < SqDiff > the following objects will be used:')
    if verbosity > 0 :
        for obj in SimResultObjects :
            _verbose( verbosity, 1, ' < SqDiff > ' + str( obj.get_Name() ))


    # split keys from attributes
    _verbose( verbosity, 1, ' < SqDiff > checking AttributesOrKeys list:')
    _verbose( verbosity, 0, ' < SqDiff >   Keys          Attributes')

    if type(AttributesOrKeys) == str :
        AttributesOrKeys = [AttributesOrKeys]
    for each in AttributesOrKeys :
        if ':' in each :
            MatchingKeys.append(each.strip())
            _verbose( verbosity, 0, ' < SqDiff >   ' + each.strip() )
        elif each.strip()[0] == 'W' or each.strip()[0] == 'G' or each.strip()[0] == 'R' :
            Atts.append(each.strip())
            _verbose( verbosity, 0, ' < SqDiff >                 ' + each.strip() )
        else :
            MatchingKeys.append(each.strip())
            _verbose( verbosity, 0, ' < SqDiff >   ' + each.strip() )
    _verbose( verbosity, 1, ' < SqDiff > found ' + str(len(MatchingKeys)) + ' Keys and ' + str(len(Atts)) + ' Attributes, ')

    # extract the keys corresponding to the attributes
    for obj in SimResultObjects :
        for Att in Atts :
            MatchingKeys += list( obj.get_Keys(pattern=str(Att)+':*' ) )
    Atts=None

    # eliminate duplicated keys
    MatchingKeys = list( set( MatchingKeys ) )

    # keep only keys matching all the objects and
    for obj in SimResultObjects :
        MatchingKeys = list( set(MatchingKeys).intersection(set( obj.get_Keys() )) )
    _verbose( verbosity, 1, ' < SqDiff > totalizing ' + str(len(MatchingKeys)) + ' Keys after extending the Attributes and removing duplicates.')

    if TimeSteps is None :
        _verbose( verbosity, 1, ' < SqDiff > TimeSteps not received, all the matching timesteps will be used.')
        TimeSteps = list()
        for obj in SimResultObjects :
            _verbose( verbosity, 0, ' < SqDiff > getting TimeSteps from ' + str(obj.get_Name()) + '\n < SqDiff > extracted ' + str(len( list( obj.get_Vector( TimeKind )[ TimeKind ] ))) + ' ' + TimeKind + '.' )
            TimeSteps += list( obj.get_Vector( TimeKind )[ TimeKind ] )
        _verbose( verbosity, 1, ' < SqDiff > ' + str(len(TimeSteps)) + ' TimeSteps found.')
        TimeSteps = list( set( TimeSteps ) )
        TimeSteps.sort()
        _verbose( verbosity, 1, ' < SqDiff > ' + str(len(TimeSteps)) + ' sorted TimeSteps found.')
        if Interpolate == False :
            for obj in SimResultObjects :
                _verbose( verbosity, 1, ' < SqDiff > looking for matching TimeSteps for ' + obj.get_Name() )
                TimeSteps = list( set( TimeSteps ).intersection( set( list( obj.get_Vector( TimeKind )[ TimeKind ] ) ) ) )
        _verbose( verbosity, 1, ' < SqDiff > ' + str(len(TimeSteps)) + ' TimeSteps found, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )

    else :
        _verbose( verbosity, 1, ' < SqDiff > ' + str(len(TimeSteps)) + ' TimeSteps received, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
        if type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('DATES')['DATES'][0] )        :
            TimeKind = 'DATES'
        elif type(TimeSteps[0]) == type( SimResultObjects[0].get_Vector('TIME')['TIME'][0] ) :
            TimeKind = 'TIME'
        else :
            _verbose( verbosity, -1, ' < SqDiff > TimeSteps set by default to TIME')
            TimeKind = 'TIME'
        _verbose( verbosity, 1, ' < SqDiff > TimeSteps found to be of type ' + TimeKind )
        if Interpolate == False :
            for obj in SimResultObjects :
                TimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) > 0 :
                _verbose( verbosity, 1, ' < SqDiff > ' + str(len(TimeSteps)) + ' TimeSteps found matching the simulation data TimeSteps, from ' + str(TimeSteps[0]) + ' to ' + str(TimeSteps[-1]) + '.' )
            else :
                _verbose( verbosity, 2, ' < SqDiff > ' + 'No matching TimeSteps in the input profiles.' )
        else :
            for obj in SimResultObjects :
                MatchingTimeSteps = list( set( TimeSteps ).intersection( set( obj.get_Vector( TimeKind )[ TimeKind ] ) ) )
            if len(TimeSteps) - len(MatchingTimeSteps) > 0 :
                _verbose( verbosity, 2, ' < SqDiff > WARNING: data will be interpolated for ' + str( len(TimeSteps) - len(MatchingTimeSteps) ) + ' TimeSteps not found in the simulation results.\n < SqDiff > WARNING: Set Interpolate=False to avoid this behaviour.' )

    # calculate differences:
    # request base DataFrame:
    _verbose( verbosity, 1, ' < SqDiff >  prepating the Pandas DataFrames, please wait...')
    baseDF = SimResultObjects[0].get_DataFrame( Keys=MatchingKeys, Index=TimeKind )
    baseDF.replace([SimResultObjects[0].null], np.nan, inplace=True )
    baseDF.interpolate(axis=0, inplace=True)
    baseDF.replace([np.inf, -np.inf], 0.0, inplace=True)
    baseDF.fillna(value=0.0, inplace=True)

    # prepare summation DataFrame fill with zeros
    sumDF = {}
    for each in MatchingKeys :
        sumDF[each] = [0]*len(TimeSteps)
    sumDF = pd.DataFrame( data=sumDF, index=TimeSteps )

    # prepare differences DataFrame fill with zeros
    diffDF = {}
    for each in MatchingKeys :
        diffDF[each] = [0]*len(TimeSteps)
    diffDF = pd.DataFrame( data=diffDF, index=TimeSteps )

    # filter base DataFrame and save into dictionary
    dictOfDF = {}
    dictOfDF[SimResultObjects[0]] = (diffDF + baseDF).dropna(axis=0, inplace=False)

    # calculate every difference and add it to the sumDF
    for obj in range(1, len(SimResultObjects)) :
        # get DataFrame with units converted to first DataFrame
        otherDF = SimResultObjects[obj].get_ConvertedDataFrame( Keys=MatchingKeys, Index=TimeKind, OtherObject_or_NewUnits=SimResultObjects[0] )
        otherDF.replace([SimResultObjects[obj].null], np.nan, inplace=True )
        otherDF.interpolate(axis=0, inplace=True)
        otherDF.replace([np.inf, -np.inf], 0.0, inplace=True)
        otherDF.fillna(value=0.0, inplace=True)

        if TimeKind in otherDF.columns :
            otherDF.drop( columns=[TimeKind], inplace=True)
        # filter the required time steps and save into dictionary
        dictOfDF[SimResultObjects[obj]] = diffDF * 0.0 + otherDF
        dictOfDF[SimResultObjects[obj]].dropna(axis=0, inplace=True)
        # calculate differente
        deltaDF = ( dictOfDF[SimResultObjects[obj]] - dictOfDF[SimResultObjects[0]] )**2
        # add square difference to totalization DataFrame
        sumDF = sumDF + deltaDF
        sumDF.dropna(axis=0, inplace=True)
    _verbose( verbosity, -1, ' < SqDiff >  resulting total SquareDifference is: ' + str( sumDF.sum(axis=1).sum(axis=0) ) )
    return ( sumDF.sum(axis=1).sum(axis=0), sumDF.sum(axis=0), pd.DataFrame(data=sumDF.sum(axis=1), index=sumDF.index, columns=['SquareDifferences']), sumDF, dictOfDF  )
