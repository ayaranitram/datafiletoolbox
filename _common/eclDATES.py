#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul 27 14:49:56 2019

@author: martin
"""

from math import floor
from datetime import date

__all__ = ['simDate']

def _monthStr2Int(month) :
    """
    receives a month as string in english and
    return the corresponding integer for that month.
    """
    str2int = {
            'JAN' : 1 ,
            'FEB' : 2 ,
            'MAR' : 3 ,
            'APR' : 4 ,
            'MAY' : 5 ,
            'JUN' : 6 ,
            'JUL' : 7 ,
            'JLY' : 7 ,
            'AUG' : 8 ,
            'SEP' : 9 ,
            'OCT' : 10 ,
            'NOV' : 11 ,
            'DEC' : 12 ,
            }
    int2str = dict(list(zip(list(str2int.values()),list(str2int.keys()))))
    if type(month) is float :
        month = floor(month)
    if type(month) is int :
        if month >= 1 and month <= 12 :
            return int2str[ month ]
        elif month > 12 :
            if month%12 == 0 :
                return int2str[ 12 ]
            else :
                return int2str[ month%12 ]
        elif month < 0 :
            return int2str[ month%12 +1 ]
        else :
            print( " month should be integer or string." )
    
    try :
        return str2int[ month.strip().upper()[0:3] ]
    except :
        print( " not recognized month string: '" + str(month) + "'" )


def simDate(DateArgument) :
    """
    simDate convert a date string in eclipse format to a datetime.date object.
    """

    if type(DateArgument) == str :
        DateArgument = DateArgument.split()
        print(DateArgument)
    DateArgument[0] = int(DateArgument[0])
    try :
        DateArgument[1] = int(DateArgument[1])
    except:
        DateArgument[1] = _monthStr2Int(DateArgument[1])
    DateArgument[2] = int(DateArgument[2])
    return date(DateArgument[2],DateArgument[1],DateArgument[0])
