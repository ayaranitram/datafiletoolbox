# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 16:03:33 2020

@author: MCARAYA
"""

__version__ = '0.0.20-05-16'

unitsFIELD = {'OIP' : 'MMstb' ,
              'WIP' : 'MMstb' ,
              'GIP' : 'Tscf' ,
              'OPR' : 'stb/day' ,
              'WPR' : 'stb/day' ,
              'GPR' : 'MMscf/day' ,
              'OIR' : 'stb/day' ,
              'WIR' : 'stb/day' ,
              'GIR' : 'MMscf/day' ,
              'BHP' : 'psia' ,
              'BP' : 'psia' ,
              'BP9' : 'psia' ,
              'BP5' : 'psia' ,
              'OPT' : 'MMstb' ,
              'WPT' : 'MMstb' ,
              'GPT' : 'Tscf' ,
              'OIT' : 'MMstb' ,
              'WIT' : 'MMstb' ,
              'GIT' : 'Tscf' ,
              'PR' : 'psia' ,
              'PRH' : 'psia' ,
              'PRP' : 'psia' ,
    }
unitsMETRIC = {'OIP' : 'Ksm3' ,
              'WIP' : 'Ksm3' ,
              'GIP' : 'Msm3' ,
              'OPR' : 'sm3/day' ,
              'WPR' : 'sm3/day' ,
              'GPR' : 'Ksm3/day' ,
              'OIR' : 'sm3/day' ,
              'WIR' : 'sm3/day' ,
              'GIR' : 'Ksm3/day' ,
              'BHP' : 'bara' ,
              'BP' : 'bara' ,
              'BP9' : 'bara' ,
              'BP5' : 'bara' ,
              'OPT' : 'Ksm3' ,
              'WPT' : 'Ksm3' ,
              'GPT' : 'Msm3' ,
              'OIT' : 'Ksm3' ,
              'WIT' : 'Ksm3' ,
              'GIT' : 'Msm3' ,    
              'PR' : 'bara' ,
              'PRH' : 'bara' ,
              'PRP' : 'bara' ,
    }


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

VIP2ECLkey = { #'NAME OF COLUMN in VIP sss' : 'base ECL output keyword' 
            'DATE' : 'DATE' ,
            'TIME' : 'TIME' ,
            'DAY' : 'DAY' ,
            'MONTH' : 'MONTH' ,
            'YEAR' : 'YEAR' ,
           'GAS PRD RATE' : 'GPR' ,
           'OIL PRD RATE' : 'OPR' , 
           'WTR PRD RATE' : 'WPR' ,
           'WTR INJ RATE' : 'WIR' ,
           'GAS INJ RATE' : 'GIR' ,
           'GASLIFT GAS' : 'GLIR' ,
           'WATER-CUT' : 'WCT' ,
           'WTR-GAS RATIO' : 'WGR' ,
           'WTR-OIL RATIO' : 'WOR' ,
           'OIL-GAS RATIO' : 'OGR' ,
           'GAS-OIL RATIO' : 'GOR' ,
           'CUM PRD GAS' : 'GPT' ,
           'CUM PRD OIL' : 'OPT' ,
           'CUM PRD WTR' : 'WPT' ,
           'CUM INJ WTR' : 'WIT' ,
           'CUM INJ GAS' : 'GIT' ,
           'BHP' : 'BHP' ,
           'THP' : 'THP' ,
           'AVG PRES' : 'BP' ,
           'OIL-IN-PLACE' : 'OIP' ,
           'GAS-IN-PLACE' : 'GIP' ,
           'HCPVD PRES' : 'PRH' ,
           'HCPV PRES' : 'PRH' ,
           'GAS POT PRD' : 'GPP' ,
           'OIL POT PRD' : 'OPP' ,
           'WTR POT PRD' : 'WPP' ,
           'GAS POT INJ' : 'GPI' ,
           'WTR POT INJ' : 'WPI' ,
           'NGL FEED RATE' : 'UNGLFR' ,
           'NGL LIQ RATE' : 'UNGLLR' ,
#               'NGL LIQ RATE' : 'NLPR' ,
           'NGL VAP RATE' : 'UNGLVR' ,
           'CUM NGL PROD' : 'NLPT' ,
#               'LPG FEED RATE' : 'O6PR' ,
           'LPG FEED RATE' : 'ULPGFR' ,
#               'LPG LIQ RATE' : 'O6PR' ,
           'LPG LIQ RATE' : 'ULPGLR' ,
           'LPG VAP RATE' : 'ULPGVR' ,
           'CUM LPG PROD' : 'O6PT' ,
           'FUEL GAS' : 'FGR' ,
#               'FUEL GAS' : 'UFUELG' ,
           'SALES GAS' : 'USALEG' ,
           'CUM FUEL GAS' : 'FGT' ,
           'MAKEUP GAS' : 'GIMR' ,
#               'MAKEUP GAS' : 'UMAKEG' ,
           'CUM MKP GAS' : 'GIMT' ,
           'FLARED GAS' : 'UFLAREG' ,
           'SHRINKAGE GAS' : 'USHRINKG' ,
           '# PROD' : 'MWPR' ,
           '# GLIFT' : 'MWPL' ,
           '# WINJ' : 'UAWI' ,
           '# GINJ' : 'UAGI' ,
           }

VIP2ECLtype = {'WELL' : 'W' ,
               'FIELD' : 'F' ,
               'AREA' : 'G' ,
               'REGION' : 'R' ,
               }

VIP2CSVkey = { #'NAME OF COLUMN in VIP sss' : 'base ECL output keyword' 
            'DATE' : 'DATE' ,
            'TIME' : 'TIME' ,
            'DAY' : 'DAY' ,
            'MONTH' : 'MONTH' ,
            'YEAR' : 'YEARS' ,
           'GAS PRD RATE' : 'QGP' ,
           'OIL PRD RATE' : 'QOP' , 
           'WTR PRD RATE' : 'QWP' ,
           'WTR INJ RATE' : 'QWI' ,
           'GAS INJ RATE' : 'QGI' ,
           'GASLIFT GAS' : 'QGLG' ,
           'WATER-CUT' : 'WCUT' ,
           'WTR-GAS RATIO' : 'WGR' ,
           'WTR-OIL RATIO' : 'WOR' ,
           'OIL-GAS RATIO' : 'OGR' ,
           'GAS-OIL RATIO' : 'GOR' ,
           'CUM PRD GAS' : 'CGP' ,
           'CUM PRD OIL' : 'COP' ,
           'CUM PRD WTR' : 'CWP' ,
           'CUM INJ WTR' : 'CWI' ,
           'CUM INJ GAS' : 'CGI' ,
           'BHP' : 'BHP' ,
           'THP' : 'THP' ,
           'AVG PRES' : 'PAVT' ,
           'OIL-IN-PLACE' : 'OIP' ,
           'GAS-IN-PLACE' : 'GIP' ,
           'HCPVD PRES' : 'PAVH' ,
           'HCPV PRES' : 'PAVH' ,
           # 'GAS POT PRD' : 'GPP' ,
           # 'OIL POT PRD' : 'OPP' ,
           # 'WTR POT PRD' : 'WPP' ,
           # 'GAS POT INJ' : 'GPI' ,
           # 'WTR POT INJ' : 'WPI' ,
           # 'NGL FEED RATE' : 'UNGLFR' ,
           # 'NGL LIQ RATE' : 'UNGLLR' ,
#               'NGL LIQ RATE' : 'NLPR' ,
           # 'NGL VAP RATE' : 'UNGLVR' ,
           # 'CUM NGL PROD' : 'NLPT' ,
#               'LPG FEED RATE' : 'O6PR' ,
           # 'LPG FEED RATE' : 'ULPGFR' ,
#               'LPG LIQ RATE' : 'O6PR' ,
           # 'LPG LIQ RATE' : 'ULPGLR' ,
           # 'LPG VAP RATE' : 'ULPGVR' ,
           # 'CUM LPG PROD' : 'O6PT' ,
           'FUEL GAS' : 'FULF' ,
#               'FUEL GAS' : 'UFUELG' ,
           'SALES GAS' : 'SLSG' ,
           'CUM FUEL GAS' : 'CFUL' ,
           'MAKEUP GAS' : 'MKPG' ,
#               'MAKEUP GAS' : 'UMAKEG' ,
           'CUM MKP GAS' : 'CMKP' ,
           'FLARED GAS' : 'UFLAREG' ,
           'SHRINKAGE GAS' : 'SHKG' ,
           '# PROD' : 'PRDW' ,
           '# GLIFT' : 'GLFW' ,
           '# WINJ' : 'WINJ' ,
           '# GINJ' : 'GINJ' ,
           }


CSV2ECLtype = {'CONNLIST' : 'C', 
               'CONN' : 'C',
               'MISCELLANEOUS' : 'F' ,
               'FIELD' : 'F', 
               'NODE' : 'N' ,
               'TARGET' : 'T', 
               'WELL' : 'W',
               'REGION' : 'R' }

CSV2ECLkey = { #'NAME OF VARIABLE in CSV' : 'base ECL output keyword'
        'TIME' : 'TIME' ,
         'YEARS' : 'YEAR' ,
         'COP' : 'OPT' ,
         'CGP' : 'GPT' ,
         'CWP' : 'WPT' ,
         'CGI' : 'GIP' ,
         'CWI' : 'WIT' ,
         'QOP' : 'OPR' ,
         'QGP' : 'GPR' ,
         'QWP' : 'WPR' ,
         'QGI' : 'GIR' ,
         'QWI' : 'WIR' ,
         'BHP' : 'BHP' ,
        #  'WPH' : '' ,
        #  'WKH' : '' ,
         'WPAV' : 'BP' ,
         'THP' : 'THP' ,
         'COWP' : 'LPT' ,
         'QOWP' : 'LPR' ,
         'GOR' : 'GOR' ,
         'WCUT' : 'WCT' ,
         'WOR' : 'WOR' ,
         'QGLG' : 'GLIR' ,
        #  'CGLG' : '' ,
        #  'DRDN' : '' ,
        #  'DRMX' : '' ,
        #  'CROP' : '' ,
        #  'CRGP' : '' ,
        #  'CRWP' : '' ,
        #  'CROI' : '' ,
        #  'CRGI' : '' ,
        #  'CRWI' : '' ,
        #  'ROP' : '' ,
        #  'RGP' : '' ,
        #  'RWP' : '' ,
        #  'ROI' : '' ,
        #  'RGI' : '' ,
        #  'RWI' : '' ,
        #  'ONTM' : '' ,
        #  'ALQ' : '' ,
        #  'API' : '' ,
        #  'QCDP' : '' ,
        #  'CCDP' : '' ,
        #  'YCDP' : '' ,
        #  'ACTV' : '' ,
        #  'STAT' : '' ,
        #  'SAL' : '' ,
        #  'Q1P' : '' ,
        #  'Q1I' : '' ,
        #  'C1P' : '' ,
        #  'C1I' : '' ,
        #  'X1P' : '' ,
        #  'Y1P' : '' ,
        #  'Q2P' : '' ,
        #  'Q2I' : '' ,
        #  'C2P' : '' ,
        #  'C2I' : '' ,
        #  'X2P' : '' ,
        #  'Y2P' : '' ,
        #  'Q3P' : '' ,
        #  'Q3I' : '' ,
        #  'C3P' : '' ,
        #  'C3I' : '' ,
        #  'X3P' : '' ,
        #  'Y3P' : '' ,
        #  'Q4P' : '' ,
        #  'Q4I' : '' ,
        #  'C4P' : '' ,
        #  'C4I' : '' ,
        #  'X4P' : '' ,
        #  'Y4P' : '' ,
        #  'Q5P' : '' ,
        #  'Q5I' : '' ,
        #  'C5P' : '' ,
        #  'C5I' : '' ,
        #  'X5P' : '' ,
        #  'Y5P' : '' ,
        #  'Q6P' : '' ,
        #  'Q6I' : '' ,
        #  'C6P' : '' ,
        #  'C6I' : '' ,
        #  'X6P' : '' ,
        #  'Y6P' : '' ,
        #  'Q7P' : '' ,
        #  'Q7I' : '' ,
        #  'C7P' : '' ,
        #  'C7I' : '' ,
        #  'X7P' : '' ,
        #  'Y7P' : '' ,
        #  'Q8P' : '' ,
        #  'Q8I' : '' ,
        #  'C8P' : '' ,
        #  'C8I' : '' ,
        #  'X8P' : '' ,
        #  'Y8P' : '' ,
        #  'Q9P' : '' ,
        #  'Q9I' : '' ,
        #  'C9P' : '' ,
        #  'C9I' : '' ,
        #  'X9P' : '' ,
        #  'Y9P' : '' ,
        #  'Q10P' : '' ,
        #  'Q10I' : '' ,
        #  'C10P' : '' ,
        #  'C10I' : '' ,
        #  'X10P' : '' ,
        #  'Y10P' : '' ,
        #  'Q11P' : '' ,
        #  'Q11I' : '' ,
        #  'C11P' : '' ,
        #  'C11I' : '' ,
        #  'X11P' : '' ,
        #  'Y11P' : '' ,
        #  'PNOD' : '' ,
        #  'PDAT' : '' ,
        #  'TNOD' : '' ,
        #  'QGAS' : '' ,
        #  'QOIL' : '' ,
        #  'QWTR' : '' ,
        #  'CGAS' : '' ,
        #  'COIL' : '' ,
        #  'CWTR' : '' ,
        #  'CBFG' : '' ,
        #  'CBFO' : '' ,
        #  'CBFW' : '' ,
        #  'QGIS' : '' ,
        #  'QOIS' : '' ,
        #  'QWIS' : '' ,
        #  'P_IN' : '' ,
        #  'POUT' : '' ,
        #  'T_IN' : '' ,
        #  'TOUT' : '' ,
        #  'CSTR' : '' ,
        #  'ITRG' : '' ,
        #  'SETM' : '' ,
        #  'SETA' : '' ,
        #  'POWM' : '' ,
        #  'POWA' : '' ,
        #  'SPDM' : '' ,
        #  'SPDA' : '' ,
        #  'DELP' : '' ,
        #  'QTOT' : '' ,
        #  'GVF' : '' ,
        #  'EFF' : '' ,
        #  'POSN' : '' ,
         'FULG' : 'FGR' ,
         'CFUL' : 'FGT' ,
        #  'SHKG' : '' ,
        #  'CSHK' : '' ,
         'SLSG' : 'USALEG' ,
        #  'CSLS' : '' ,
        #  'Q1' : '' ,
        #  'C1' : '' ,
        #  'X1' : '' ,
        #  'Y1' : '' ,
        #  'Q2' : '' ,
        #  'C2' : '' ,
        #  'X2' : '' ,
        #  'Y2' : '' ,
        #  'Q3' : '' ,
        #  'C3' : '' ,
        #  'X3' : '' ,
        #  'Y3' : '' ,
        #  'Q4' : '' ,
        #  'C4' : '' ,
        #  'X4' : '' ,
        #  'Y4' : '' ,
        #  'Q5' : '' ,
        #  'C5' : '' ,
        #  'X5' : '' ,
        #  'Y5' : '' ,
        #  'Q6' : '' ,
        #  'C6' : '' ,
        #  'X6' : '' ,
        #  'Y6' : '' ,
        #  'Q7' : '' ,
        #  'C7' : '' ,
        #  'X7' : '' ,
        #  'Y7' : '' ,
        #  'Q8' : '' ,
        #  'C8' : '' ,
        #  'X8' : '' ,
        #  'Y8' : '' ,
        #  'Q9' : '' ,
        #  'C9' : '' ,
        #  'X9' : '' ,
        #  'Y9' : '' ,
        #  'Q10' : '' ,
        #  'C10' : '' ,
        #  'X10' : '' ,
        #  'Y10' : '' ,
        #  'Q11' : '' ,
        #  'C11' : '' ,
        #  'X11' : '' ,
        #  'Y11' : '' ,
        #  'OREC' : '' ,
        #  'GREC' : '' ,
        #  'PAVT' : '' ,
        #  'PAVH' : '' ,
        #  'NFLX' : '' ,
         'OIP' : 'OIP' ,
         'GIP' : 'GIP' ,
         'WIP' : 'WIP' ,
        #  'WLLS' : '' ,
        #  'PRDW' : '' ,
        #  'GLFW' : '' ,
        #  'WINJ' : '' ,
        #  'GINJ' : '' ,
        #  'ACTW' : '' ,
         'MKPG' : 'GIMR' ,
        #  'CMKP' : '' ,
         'QOI' : 'OIR' ,
         'COI' : 'OIT' ,
        #  'SALP' : '' ,
        #  'SALI' : '' ,
        #  'SQO' : '' ,
        #  'SQG' : '' ,
        #  'SQW' : '' ,
        #  'SQL' : '' ,
        #  'SQA' : '' ,
        #  'SQH' : '' ,
        #  'RQO' : '' ,
        #  'RQG' : '' ,
        #  'RQW' : '' ,
        #  'RQL' : '' ,
        #  'RQA' : '' ,
        #  'RQH' : '' ,
        #  'QM' : '' ,
        #  'TSQO' : '' ,
        #  'TSQG' : '' ,
        #  'TSQW' : '' ,
        #  'TSQL' : '' ,
        #  'TSQA' : '' ,
        #  'TSQH' : '' ,
        #  'TRQO' : '' ,
        #  'TRQG' : '' ,
        #  'TRQW' : '' ,
        #  'TRQL' : '' ,
        #  'TRQA' : '' ,
        #  'TRQH' : '' ,
        #  'TQM' : '' ,
        #  'P' : '' ,
        }