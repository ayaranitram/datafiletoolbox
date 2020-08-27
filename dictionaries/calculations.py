# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 14:08:49 2020

@author: MCARAYA
"""

__version__ = '0.0.20-06-03'

calculations = { 
    # dictionary for the function "arithmeticVector" 
    # the accepted operators are: '+' , '-' , '*' , '/' , '^'
    # the operation must start with a number or variable, never with an operator
    #
    # the operations will be executed in the exact order they are described. i.e.:
    # 'LPR' : ( 'OPR' , '+' , 'WPR' ) 
    #    means LPR = OPR + WPR 
    #    will add OPR plus WPR
    # but:
    # 'R' : ( 'A' , '-', 'B' , '*' , 'C' ) 
    #   means R = ( A - B ) / C
    #   will add A plus B and the result will be divided by C
    # to represent R = A - B / C the correct sintax is:
    # 'R' : ( -1 , '*' , 'B' , '/', 'C' , '+' , 'A'  ) 
    #   that means R = -1 * B / C + A
    
    'LPR' : ( 'OPR' , '+', 'WPR' ) ,
    'WCT' : ( 'WPR' , '/', 'LPR'  ) ,
    'GOR' : ( 'GPR' , '/', 'OPR' ) ,
    'OGR' : ( 'OPR' , '/', 'GPR' ) ,
    'WOR' : ( 'WPR' , '/', 'OPR' ) ,
    'OWR' : ( 'OPR' , '/', 'WPR' ) ,
    'GLR' : ( 'GPR' , '/', 'LPR' ) ,
    'LGR' : ( 'LPR' , '/', 'GPR' ) ,
    }