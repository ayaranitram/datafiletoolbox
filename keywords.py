#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 19:54:53 2019

@author: martin
"""

ZeroArgumentsKeywords = (
    'RUNSPEC','GRID','EDIT','PROPS','REGIONS','SOLUTION','SUMMARY','SCHEDULE',
    'ECHO','NOECHO','ENDBOX','NONNC',
    'OIL','WATER','GAS','DISGAS','VAPOIL','FIELD','METRIC',
    'FMTOUT','FMTIN','UNIFOUT','UNIFIN','MULTOUT','MULTIN',
    'IMPLICIT',
    'END',
    'ALL',
    'MSUMLINS'
    'MSUMNEWT',
    'SEPARATE'
    )

#TableFormatKeywords = ( 'DATES','EQUALS','MULTIPLY','ADD','OPERATE','OPERATER',
#        'SWFN','SGFN','SOF2','SOF3','SWOF','SGOF','PVTO','PVTG','PVDO','PVDG',
#        'GRUPTREE','GCONINJE','GINJGAS','GRUPINJE','GCONPROD','GCONINJE',
#        'WELSPECS','COMPDAT','COMPDATMD','WPIMULT','WCONHIST','WRFTPLT','WINJGAS',
#        'WCONINJH','WCONPROD','WCONINJE' 
#        )
TableFormatKeywords = ( 'SWFN','SGFN','SOF2','SOF3','SWOF','SGOF',
                       'PVTO','PVTG','PVDO','PVDG',
        )

MultiLineKeywords = ( 'DATES','EQUALS','MULTIPLY','ADD','OPERATE','OPERATER',
        'GRUPTREE','GCONINJE','GINJGAS','GRUPINJE','GCONPROD','GCONINJE',
        'WELSPECS','COMPDAT','COMPDATMD','WPIMULT','WCONHIST','WRFTPLT','WINJGAS',
        'WCONINJH','WCONPROD','WCONINJE' 
        )

SpecialKeywords = ('TITLE','DIMENS','START','EQLDIMS','TABDIMS','WELLDIMS')

NoSlashKeywords = ('TITLE')