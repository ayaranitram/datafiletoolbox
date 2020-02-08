# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 11:00:42 2019

@author: MCARAYA

routine to convert .sss files from VIP to RSM like files.
"""

#import numpy as np
#import pandas as pd
import datafiletoolbox.stringformat
from decimal import Decimal

#mainFolder = '/Volumes/documentos/SampleData'
#mainFolder = '/Volumes/documentos/_DocumentosTecnicos/Python/SampleData'
mainFolder = 'C:/Users/mcaraya/OneDrive - Cepsa/Macros/Python'
sssInput = [ mainFolder + '/J27r_complete_well.sss',
             mainFolder + '/J27r_complete_field.sss',
             mainFolder + '/J27r_complete_area.sss',
             #mainFolder + '/J27r_complete_flow.sss',
             #mainFolder + '/J27r_complete_gather.sss',
             mainFolder + '/J27r_complete_region.sss'
             ]

rsmOutput = 'J27r_complete'

debug = False

try:
    RSMlog = open(mainFolder + '/' + rsmOutput + '_SSS2RSMConversion.log', 'w' )
    print( 'IMPORTANT MESSAGE: please read the log file of this conversion:\n ' + str(mainFolder + '/' + rsmOutput + '_ConversionLog.RSM') )
except:
    print("WARNING:\n log file is locked and can't be written\n:   " + str(mainFolder + '/' + rsmOutput + '_ConversionLog.RSM') )

if debug == True :
    RSMdebug = open(mainFolder + '/' + rsmOutput + '_debug.log', 'w' )

inputDict = {}

RSMlog.write('\n__________\Reading input files...' + '\n' )

for inputfile in sssInput :

    print('\nREADING ' + str(inputfile))
    RSMlog.write('\nREADING ' + str(inputfile) + '\n' )
    sssfile = open(inputfile,'r')
    #sss = sssfile.readlines()
    sss = sssfile.read()
    sssfile.close()

    sss = sss.split('\n')

    sssType = sss[0].split()[0]
    print( 'Type of data in this input file: ' + str(sssType) )
    RSMlog.write( 'Type of data in this input file: ' + str(sssType) + '\n' )

    sssColumns = sss[1].split('\t')
    for i in range(len(sssColumns)):
        sssColumns[i] = sssColumns[i].strip()
        #sssColumns[i] = sssColumns[i]

    sssUnits = sss[2].split('\t')
    for i in range(len(sssUnits)):
        sssUnits[i] = sssUnits[i].strip()
        #sssUnits[i] = sssUnits[i]

    sssClean = []
    for i in range(len(sss[3:])) :
        if len(sss[3+i].strip()) > 0 :
            sssClean.append(sss[3+i])

    sssData = []
    sssData = '\t'.join(sssClean).split('\t')

    sssDict = { 'Data' : {} , 'Units' : {} }

    for i in range(len(sssColumns)) :
        sssDict['Data'][sssColumns[i]] = sssData[i::len(sssColumns)]
    for i in range(len(sssColumns)) :
        sssDict['Units'][sssColumns[i]] = sssUnits[i]

    print(' data found in the file:')
    for each in sssDict['Data'] :
        print('  > ' + str(each) + str( ' ' * (16-len(str(each))) ) + ' with ' + str(len(sssDict['Data'][each])) + ' rows with units: ' + str( sssDict['Units'][each] ) )
        RSMlog.write('  > ' + str(each) + str( ' ' * (16-len(str(each))) ) + ' with ' + str(len(sssDict['Data'][each])) + ' rows with units: ' + str( sssDict['Units'][each] ) + '\n'  )

    inputDict[sssType] = sssDict


print( '\n...working on it: checking DATEs in the data...')
Dates=[]
for kind in inputDict :
    inputDict[kind]['Data']['DATE'] = datafiletoolbox.stringformat.date(inputDict[kind]['Data']['DATE'] , formatIN='DD/MM/YYYY' , formatOUT='DD-MMM-YYYY')
    print(  '  DATEs in ' + str(kind) + ': ' + str(len(list(dict.fromkeys(inputDict[kind]['Data']['DATE'])))) + ' items, from ' + str(inputDict[kind]['Data']['DATE'][0]) + ' to ' + str(inputDict[kind]['Data']['DATE'][-1]) )
    for i in range(len(inputDict[kind]['Data']['DATE'])) :
        if inputDict[kind]['Data']['DATE'][i] not in Dates :
            Dates.append(inputDict[kind]['Data']['DATE'][i])


print('\n...working on it: creating dictionaries...')

THEdata = dict.fromkeys( Dates )

for each in THEdata.keys() :
    THEdata[each] = {}

for kind in inputDict :
    for name in list(dict.fromkeys(inputDict[kind]['Data']['NAME'])):
        for each in THEdata.keys() :
            THEdata[each][ name.strip() ] = { }

for kind in inputDict :
    for name in list(dict.fromkeys(inputDict[kind]['Data']['NAME'])):
        for column in inputDict[kind]['Data'].keys() :
            if column != 'DATE' and column != 'NAME' :
                for each in THEdata.keys() :
                    THEdata[each][ name.strip() ][column] = {'Kind' : kind , 'Units' : inputDict[kind]['Units'][column] }
                    #THEdata[each][ name.strip() ][column] = {'Units' : inputDict[kind]['Units'][column] , 'Data' : [] }

for kind in inputDict :
    for row in range(len(inputDict[kind]['Data']['DATE'])) :
        for column in inputDict[kind]['Data'].keys() :
            if column != 'DATE' and column != 'NAME' :
                THEdata[ inputDict[kind]['Data']['DATE'][row] ][ inputDict[kind]['Data']['NAME'][row].strip() ][ column ]['Data'] = inputDict[kind]['Data'][column][row]


Names = []
for each in THEdata :
    for name in list(dict.fromkeys(list(THEdata[each].keys()))) :
        if name not in Names :
            Names.append( name )
Names = dict.fromkeys( Names )
for name in Names :
    Names[name] = []
for each in THEdata :
    for name in list(THEdata[each].keys()) :
        for column in THEdata[each][name] :
            if column not in Names[name] :
                Names[name].append(column)

Columns = []
for each in inputDict :
    for col in list( inputDict[each]['Data'].keys() ) :
        if col not in Columns :
            Columns.append(col)



#
# the sss data is loaded into a structure of dictionaries in the variable THEdata
# THEdata
#   dates
#       names (wells, root, groups)
#           data_column
#               units
#               data
#                   list with the value for this property of this name at this date
#
# support lists:
#  Names contains all the names that apear in the sss files
#  Columns contains all the columns that apear in the ss files
#

VIP2ECLkey = { #'NAME OF COLUMN in VIP sss' : [ 'base ECL output keyword' , multiplier , shifterY , shifterX ] -> ECLunit = ( ( VIP_unit + ShiftX ) * Multiplier ) + ShiftY
               'DATE' : ['DATE' , 1 , 0 , 0 ] ,
               'TIME' : ['TIME' , 1 , 0 , 0 ] ,
               'DAY' : ['DAY' , 1 , 0 , 0 ] ,
               'MONTH' : ['MONTH' , 1 , 0 , 0 ] ,
               'YEAR' : ['YEAR' , 1 , 0 , 0 ] ,
               'GAS PRD RATE' : [ 'GPR' , 1 , 0 , 0 ] ,
               'OIL PRD RATE' : ['OPR' , 1 , 0 , 0 ] ,
               'WTR PRD RATE' : ['WPR' , 1 , 0 , 0 ] ,
               'WTR INJ RATE' : ['WIR' , 1 , 0 , 0 ] ,
               'GAS INJ RATE' : ['GIR' , 1 , 0 , 0 ] ,
               'GASLIFT GAS' : ['GLIR' , 1 , 0 , 0 ] ,
               'WATER-CUT' : ['WCT' , 1 , 0 , 0 ] ,
               'WTR-GAS RATIO' : ['WGR' , 1 , 0 , 0 ] ,
               'OIL-GAS RATIO' : ['OGR' , 1 , 0 , 0 ] ,
               'CUM PRD GAS' : ['GPT' , 1 , 0 , 0 ] ,
               'CUM PRD OIL' : ['OPT' , 1 , 0 , 0 ] ,
               'CUM PRD WTR' : ['WPT' , 1 , 0 , 0 ] ,
               'CUM INJ WTR' : ['WIT' , 1 , 0 , 0 ] ,
               'CUM INJ GAS' : ['GIT' , 1 , 0 , 0 ] ,
               'BHP' : ['BHP' , 1 , 0 , 0 ] ,
               'THP' : ['THP' , 1 , 0 , 0 ] ,
               'AVG PRES' : ['BP' , 1 , 0 , 0 ] ,
               'OIL-IN-PLACE' : ['OIP' , 1 , 0 , 0 ] ,
               'GAS-IN-PLACE' : ['GIP' , 1 , 0 , 0 ] ,
               'HCPVD PRES' : ['PRH' , 1 , 0 , 0 ] ,
               'HCPV PRES' : ['PRH' , 1 , 0 , 0 ] ,
               'GAS POT PRD' : ['GPP' , 1 , 0 , 0 ] ,
               'OIL POT PRD' : ['OPP' , 1 , 0 , 0 ] ,
               'WTR POT PRD' : ['WPP' , 1 , 0 , 0 ] ,
               'GAS POT INJ' : ['GPI' , 1 , 0 , 0 ] ,
               'WTR POT INJ' : ['WPI' , 1 , 0 , 0 ] ,
               'NGL FEED RATE' : ['UNGLFR' , 1 , 0 , 0 ] ,
               'NGL LIQ RATE' : ['UNGLLR' , 1 , 0 , 0 ] ,
#               'NGL LIQ RATE' : ['NLPR' , 1 , 0 , 0 ] ,
               'NGL VAP RATE' : ['UNGLVR' , 1 , 0 , 0 ] ,
               'CUM NGL PROD' : ['NLPT' , 1 , 0 , 0 ] ,
#               'LPG FEED RATE' : ['O6PR' , 1 , 0 , 0 ] ,
               'LPG FEED RATE' : ['ULPGFR' , 1 , 0 , 0 ] ,
#               'LPG LIQ RATE' : ['O6PR' , 1 , 0 , 0 ] ,
               'LPG LIQ RATE' : [ 'ULPGLR' , 0.1292/33.4962 , 0 , 0 ] ,
               'LPG VAP RATE' : ['ULPGVR' , 1 , 0 , 0 ] ,
               'CUM LPG PROD' : ['O6PT' , 1 , 0 , 0 ] ,
               'FUEL GAS' : ['FGR' , 1 , 0 , 0 ] ,
#               'FUEL GAS' : ['UFUELG' , 1 , 0 , 0 ] ,
               'SALES GAS' : ['USALEG' , 1 , 0 , 0 ] ,
               'CUM FUEL GAS' : ['FGT' , 1 , 0 , 0 ] ,
               'MAKEUP GAS' : ['GIMR' , 1 , 0 , 0 ] ,
#               'MAKEUP GAS' : ['UMAKEG' , 1 , 0 , 0 ] ,
               'CUM MKP GAS' : ['GIMT' , 1 , 0 , 0 ] ,
               'FLARED GAS' : ['UFLAREG' , 1 , 0 , 0 ] ,
               'SHRINKAGE GAS' : ['USHRINKG' , 1 , 0 , 0 ] ,
               '# PROD' : ['MWPR' , 1 , 0 , 0 ] ,
               '# GLIFT' : ['MWPL' , 1 , 0 , 0 ] ,
               '# WINJ' : ['UAWI' , 1 , 0 , 0 ] ,
               '# GINJ' : ['UAGI' , 1 , 0 , 0 ] ,
               }

VIP2ECLtype = {'WELL' : 'W' ,
               'FIELD' : 'F' ,
               'AREA' : 'G' ,
               'REGION' : 'R'
               }

VIP2ECLunits = {#'VIP unit' : [ 'ECL unit' , Multiplier , ShiftX , ShiftY ] -> ECLunit = ( ( VIP_unit + ShiftX ) * Multiplier ) + ShiftY
                '(FRACTION)' : ['','',1,0,0] ,
                '(KPA)' : ['BARSA','',0.01,0,0] ,
                '(KSM3/DAY)' : ['SM3/DAY','*10**3',1,0,0] ,
                '(STM3/DAY)' : ['SM3/DAY','',1,0,0] ,
                '(MSM3)' : ['SM3','*10**6',1,0,0] ,
                '(KSTM3)' : ['SM3','*10**3',1,0,0] ,
                '(GSM3)' : ['SM3','*10**9',1,0,0] ,
                '(MSTM3)' : ['SM3','*10**6',1,0,0] ,
                '(STM3/KSM3)' : ['SM3/SM3','',1000,0,0] ,
                '(RM3/DAY)' : ['RM3/DAY','',1,0,0] ,
                '(KRM3)' :  ['RM3','*10**3',1,0,0] ,
                '(DAYS)' : ['DAYS','',1,0,0] ,
               }

VIP2ECLreg= {}

print('\n...working on it: preparing data for RSM format...')

CombiColumns = []
for fecha in list(THEdata.keys()) :
    for nombre in list(THEdata[fecha].keys()) :
        for col in list(THEdata[fecha][nombre].keys()) :
            if 'Data' in list(THEdata[fecha][nombre][col].keys()) :
                if ( nombre +':'+ col +':' + THEdata[fecha][nombre][col]['Kind'] +':' + THEdata[fecha][nombre][col]['Units'] ) not in CombiColumns :
                    CombiColumns.append( nombre +':'+ col +':' + THEdata[fecha][nombre][col]['Kind'] +':' + THEdata[fecha][nombre][col]['Units'] )


CleanColumns = []
TIMEflag = False
fDATE = list(THEdata.keys())[0]
for each in CombiColumns :
    eachSplit = each.split(':')
    if eachSplit[1] in list(VIP2ECLkey.keys()) and eachSplit[1] != 'DATE' :
        if eachSplit[1] == 'TIME' :
            if TIMEflag == False :
                if 'Data' in list( THEdata[fDATE][eachSplit[0]][eachSplit[1]].keys() ) :
                    CleanColumns.append(each)
                    TIMEflag = True
        else :
            CleanColumns.append(each)


KindOfColumn = []
RSMlog.write( '\n__________\nNaming convention used in this conversion:\n' )
print( '\nNaming convention used in this conversion:' )
for each in CleanColumns :
    if each.split(':')[1:3] not in KindOfColumn :
        KindOfColumn = each.split(':')[1:3]

        if each.split(':')[3] in VIP2ECLunits :
            unitMult = VIP2ECLunits[each.split(':')[3]][2]
            unitSumY = VIP2ECLunits[each.split(':')[3]][3]
            unitSumX = VIP2ECLunits[each.split(':')[3]][4]
        else:
            unitMult = 1
            unitSumY = 0
            unitSumX = 0
        if each.split(':')[1] in VIP2ECLkey :
            unitMult = unitMult * VIP2ECLkey[each.split(':')[1]][1]
            unitSumY = unitSumY + VIP2ECLkey[each.split(':')[1]][2]
            unitSumX = unitSumX + VIP2ECLkey[each.split(':')[1]][3]

        textU = each.split(':')[3].strip().strip('(').strip(')').strip()
        if unitSumX != 0 :
            textU = str(unitSumX) + ' + '  + textU
        if unitMult != 1 :
            if unitSumX != 0 :
                textU = '( '  + textU + ' )'
            textU = textU + ' * ' + str(unitMult)
        if unitSumY != 0 :
            textU = textU + ' + ' + str(unitSumY)

        text = '  "' + str(each.split(':')[1]) + '" from ' + str(each.split(':')[2]) + ' translated as "' + str( VIP2ECLtype[each.split(':')[2]] + VIP2ECLkey[each.split(':')[1]][0] + '"' )
        if unitMult != 1 or unitSumY != 0 or unitSumX != 0 :
            text = text + ' with unit conversion ' + VIP2ECLunits[each.split(':')[3]][0] + VIP2ECLunits[each.split(':')[3]][1] + ' = ' + textU

        RSMlog.write( text + '\n' )
        print( text )


print('\n...working on it: writing RSM file...')


RSMfile = open(mainFolder + '/' + rsmOutput + '.RSM', 'w' )


RSMleng = 12
RSMcols = 10

cc = 0
while cc < len(CleanColumns) :

    line = '\n\tSUMMARY OF RUN ' + rsmOutput + '\n'
    RSMfile.write(line)

    line1 = ' \tDATE        '
    line2 = ' \t            '
    line3 = ' \t            '
    line4 = ' \t            '
    line5 = ' \t            '
    unitMult = []
    unitSumY = []
    unitSumX = []
    screen = ''
    for each in CleanColumns[ cc : cc+RSMcols-1 ] :
        Combi = each.split(':')

        if VIP2ECLkey[Combi[1]][0] in [ 'TIME' , 'DAY' , 'MONTH' , 'YEAR' , 'DATE' ] :
            line1 = line1 + '\t' + VIP2ECLkey[Combi[1]][0] + ' ' * (RSMleng - len(VIP2ECLkey[Combi[1]][0]))
        else :
            line1 = line1 + '\t' + VIP2ECLtype[Combi[2]] + VIP2ECLkey[Combi[1]][0] + ' ' * (RSMleng - len(VIP2ECLtype[Combi[2]] + VIP2ECLkey[Combi[1]][0]))

        if Combi[3] in list(VIP2ECLunits.keys()) :
            CombiU = VIP2ECLunits[Combi[3]]
        else :
            CombiU = [Combi[3],'',1,0,0]
        line2 = line2 + '\t'  + CombiU[0] + ' ' * (RSMleng - len(CombiU[0]))
        line3 = line3 + '\t' + CombiU[1] + ' ' * (RSMleng - len(CombiU[1]))

        unitMult.append(CombiU[2])
        unitSumY.append(CombiU[3])
        unitSumX.append(CombiU[4])
        unitMult[-1] = unitMult[-1] * VIP2ECLkey[Combi[1]][1]
        unitSumY[-1] = unitSumY[-1] + VIP2ECLkey[Combi[1]][2]
        unitSumX[-1] = unitSumX[-1] + VIP2ECLkey[Combi[1]][3]


        if Combi[2] == 'FIELD' :
            Combi0 = ''
            CombiR=''
        elif Combi[2] == 'REGION' :
            if Combi[0] in VIP2ECLreg :
                CombiR = VIP2ECLreg[Combi[0]]
#                Combi0 = ''
                Combi0 = Combi[0]
            else :
                VIP2ECLreg[Combi[0]] = len(VIP2ECLreg) + 1
                CombiR = VIP2ECLreg[Combi[0]]
#                Combi0 = ''
                Combi0 = Combi[0]
        else :
            Combi0 = Combi[0]
            CombiR = ''
        line4 = line4 + '\t' + Combi0 + ' ' * (RSMleng - len(Combi0))
        line5 = line5 + '\t' + str(CombiR) + ' ' * (RSMleng - len(str(CombiR)))
#        screen = screen + '   ' + VIP2ECLtype[Combi[2]] + VIP2ECLkey[Combi[1]][0] + ':' + Combi[0] + str(CombiR)
    line1 = line1 + '\n'
    line2 = line2 + '\n'
    line3 = line3 + '\n'
    line4 = line4 + '\n'
    line5 = line5 + '\n'

#    if len(line4.strip()) == 0 :
#        line4 = line5
#        line5 = ' \t            ' + ( ( '\t' + ( ' ' * RSMleng ) ) * (RSMcols - 1) ) + '\n'
    if len(line3.strip()) == 0 :
        line3 = line4
        line4 = line5
        line5 = ' \t            ' + ( ( '\t' + ( ' ' * RSMleng ) ) * (RSMcols - 1) ) + '\n'

    line = line1 + line2 + line3 + line4 + line5 # + '\n'
    RSMfile.write(line)
#    screen = 'writting the following vectors:\n' + screen
#    print(screen)

    for fecha in list(THEdata.keys()) :
        line = '\t ' + fecha
        unitN = 0

        #unit conversion debbugin:
        unitdebug = False

        for each in CleanColumns[ cc : cc + RSMcols - 1 ] :
            Combi = each.split(':')
            if Combi[0] in list(THEdata[fecha].keys()) \
            and Combi[1] in list(THEdata[fecha][Combi[0]].keys()) \
            and 'Data' in list(THEdata[fecha][Combi[0]][Combi[1]].keys()) :

                #  the value
                value = THEdata[fecha][Combi[0]][Combi[1]]['Data']


                # apply multiplier if unit conversion applies
                #if unitMult[unitN] != 1 or unitSumY[unitN] != 0 or unitSumX[unitN] != 0 :

                #unit conversion debbugin:
                if unitdebug == False and debug == True :
                    RSMdebug.write('\n*** unit debbuging:\n  ' + str(Combi[0]) + ' : ' + str(Combi[1]) + '\n' )
                    RSMdebug.write('\n***\n  value in:' + str(value) + '\n' )
                    RSMdebug.write('    promgram variables: \n      unitN:' + str(unitN) + '\n      unitMult: ' + str(unitMult) + '\n      unitShiftX: ' + str(unitSumX) + '\n      unitShiftY: ' + str(unitSumY) + '\n' )

                if '.' in value :
                    if 'E' in value :
                        value = str( ( float(value) + unitSumX[unitN] ) * unitMult[unitN] + unitSumY[unitN] )
                    else :
                        value = str( (float(value) + unitSumX[unitN] ) * unitMult[unitN] + unitSumY[unitN] )
                else :
                    value = str( (int(value) + unitSumX[unitN] ) * unitMult[unitN] + unitSumY[unitN] )

                #unit conversion debbugin:
                if unitdebug == False and debug == True :
                    RSMdebug.write('  multiplier: ' + str(unitMult[unitN]) + '\n  shiftX: ' + str(unitSumX[unitN]) + '\n  shiftY: ' + str(unitSumY[unitN]) + '\n')
                    RSMdebug.write('  value out:' + str(value) + '\n   printed value: ' + str( ('%.' + str(RSMleng - 6) + 'E') % Decimal(value) ) + '\n***\n')
                # apply multiplier if unit conversion applies


                # scientific format if the character is longer than the column size
                if len(value) > RSMleng :
                    if len(str(int(float(value)))) <= RSMleng :
                        value = str(float(value))[:RSMleng]
                    else :
                        value = ('%.' + str(RSMleng - 6) + 'E') % Decimal(value)

                # preparing and printing the line
                if (RSMleng - len(value)) > 0 :
                    rept = ' ' * (RSMleng - len(value))
                else :
                    rept = ''
                line = line + '\t' + rept + value
            else :
                line = line + '\t' + ' '*(RSMleng-1) + '0'

            if each == CleanColumns[ cc : cc + RSMcols - 1 ][-1] :
                unitdebug = True

            unitN += 1

        line = line + '\n'
        RSMfile.write(line)

    cc += RSMcols - 1

RSMfile.close()
print( 'RMS file is completed, feel free to open it.\nPlease wait for the report of the conversion to be finished.' )


if len( VIP2ECLreg ) > 0 :
    print('\nRegions written into the RSM file:')
    RSMlog.write( '\n__________\n Regions from the region.sss file written into the RSM file using the following conversion:\n' )
    collen = 11

    for each in VIP2ECLreg :
        if len(str(each)) > collen :
            collen = len(str(each))
    print( ' ' * (collen - len('Region Name')) + 'Region Name' + ' : ' + 'Region Number' )
    RSMlog.write( ' ' * (collen - len('Region Name')) + 'Region Name' + ' : ' + 'Region Number'  + '\n' )

    for each in VIP2ECLreg :
        print( ' ' * (collen - len(str(each))) + str(each) + ' : ' + str(VIP2ECLreg[each]) )
        RSMlog.write( ' ' * (collen - len(str(each))) + str(each) + ' : ' + str(VIP2ECLreg[each]) + '\n' )
else :
    print('\nNo regions written into the RSM file:')


KindOfColumn = {}
RSMlog.write( '\n__________\nObjects found in the input data:\n' )
print( '\nObjects found in the input data:' )
for each in CleanColumns :
    kindlen = 0
    if each.split(':')[2] not in KindOfColumn :
        KindOfColumn[ each.split(':')[2] ] = [ each.split(':')[2] ]
    elif each.split(':')[0] not in KindOfColumn[ each.split(':')[2] ] :
            KindOfColumn[ each.split(':')[2] ].append( each.split(':')[0] )
    if len(str(kind)) > kindlen :
        kindlen = len(str(kind))
for kind in KindOfColumn :
    print( '\n  ' + ( ' ' * ( kindlen - len(str(kind) ) ) ) + str(kind) + ' : ' + KindOfColumn[kind][0] )
    RSMlog.write( '  ' + ( ' ' * ( kindlen - len(str(kind) ) ) ) + str(kind) + ' : ' + KindOfColumn[kind][0] + '\n' )
    for i in range(1 , len(KindOfColumn[kind])) :
        print( '  ' + ' ' * kindlen + ' : ' + KindOfColumn[kind][i] )
        RSMlog.write( '  ' + ' ' * kindlen + ' : ' + KindOfColumn[kind][i]  + '\n' )


RSMlog.close()
print( '\nConversion report ready, please find it here:\n  ' + str(mainFolder + '/' + rsmOutput + '_ConversionLog.RSM') )
