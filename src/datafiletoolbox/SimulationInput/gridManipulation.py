#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 23:06:08 2019

@author: martin
"""

def joinZCORNkeywords(outputFile , keywordName , listOfDimensionsANDValues , valuesPerLine = 16 , speak=0 ) :
    """
    joinZCORNkeywords will create a single and continuous ZCORN keyword from
    the different ZCORN coordinates provided.

    This version will work properly only with grids of the same X & Y dimensions.
    If the coordinates of the grids does not coincide, the other grids will
    result moved to the coordinates of the first one.
    """
    file = open( outputFile , 'w')
    log = open( extension(outputFile)[0] + '.log' , 'w')
    file.write(keywordName + '\n')

    verbose( speak , 2 , 'writing keyword ' + str(keywordName))
    log.write('writing keyword ' + str(keywordName) + '\n')

    gridsNum = len(listOfDimensionsANDValues)

    maxI = []
    maxJ = []
    maxK = []
    sumK = 0
    for G in range(gridsNum) :
        maxI = maxI + [listOfDimensionsANDValues[G][0][0]]
        maxJ = maxJ + [listOfDimensionsANDValues[G][0][1]]
        maxK = maxK + [listOfDimensionsANDValues[G][0][2]]
        sumK = sumK + listOfDimensionsANDValues[G][0][2]
        if type(listOfDimensionsANDValues[G][1]) == str :
            log.write('expanding values for grid ' + str(G) + '\n')
            listOfDimensionsANDValues[G][1] = expandKeyword(listOfDimensionsANDValues[G][1])
        elif type(listOfDimensionsANDValues[G][1]) == list :
            if len(listOfDimensionsANDValues[G][1]) == 0 :
                log.write('\n  ERROR: The ZCORN keyword for grid ' + str(G) + ' is empty, no values found.\n')
                raise Exception('The ZCORN keyword for grid ' + str(G) + ' is empty, no values found.')
            elif listOfDimensionsANDValues[G][0][0] * listOfDimensionsANDValues[G][0][1] * listOfDimensionsANDValues[G][0][2] * 8 > len(listOfDimensionsANDValues[G][1]) :
                log.write('expanding values for grid ' + str(G) + '\n')
                listOfDimensionsANDValues[G][1] = expandKeyword(listOfDimensionsANDValues[G][1])
            elif listOfDimensionsANDValues[G][0][0] * listOfDimensionsANDValues[G][0][1] * listOfDimensionsANDValues[G][0][2] * 8 < len(listOfDimensionsANDValues[G][1]) :
                log.write('\n  ERROR: Too many values in keyword ZCORN for grid ' + str(G) + '. Usualy a / is missing.\n')
                raise Exception('Too many values in keyword ZCORN for grid ' + str(G) + '. Usualy a / is missing.')
            else :
                #correct dimensions, proceed
                log.write('values in keyword ZCORN for grid ' + str(G) + ' has the correct dimensions\n')

    maxI = max(maxI)
    maxJ = max(maxJ)
    maxK = max(maxK)

    totaldimen = 2*maxI * 2*maxJ * 2*sumK + 2*maxI * 2*maxJ * 2*(gridsNum - 1)

    writtenValues = 0

    logline = 'total dimension will be: 2*' + str(maxI) +' * 2*' + str(maxJ) +' * 2*' + str(sumK) + ' + 2*' + str(maxI) + ' * 2*' + str(maxJ) + ' * 2*' + str(gridsNum-1)
    log.write(logline + '\n')
    log.write('total number of values to be written: ' + str(totaldimen) + '\n')
    prog = 0

    log.write('creating array of grids and parts of grids to be exported\n')
    verbose( speak , 1 , 'creating array of grids and parts of grids to be exported')

    gridsToWrite = []
    halfIntermediate = maxI * maxJ * 4
    for G in range(gridsNum) :
        if G > 0 and G < gridsNum :
            verbose( speak , 2 , 'preparing intermeadiate layer between grids ' + str(G-1) + ' and ' + str(G) )
            log.write('preparing intermeadiate layer between grids ' + str(G-1) + ' and ' + str(G) + '\n' )
            intermediateGrid = listOfDimensionsANDValues[G-1][1][-1*halfIntermediate:] + listOfDimensionsANDValues[G][1][:halfIntermediate]
            gridsToWrite.append( [ (maxI,maxJ,1) , intermediateGrid ] )
        verbose( speak , 2 , 'preparing grid ' + str(G) )
        log.write('preparing grid ' + str(G) + '\n' )
        gridsToWrite.append( listOfDimensionsANDValues[G] )


    intermediate = False
    lastValueCum = 0
    Krange = (0,0)
    for grid in range(len(gridsToWrite)) :

        gridfile = open(extension(outputFile)[0] + '_Grid' + str(grid+1) + extension(outputFile)[1] , 'w')
        gridfile.write(keywordName + '\n')

        gridDims = (gridsToWrite[grid][0][0] , gridsToWrite[grid][0][1] , gridsToWrite[grid][0][2])
        #print('grid ' + str(grid) + ' size is: ' + str(gridDims[0]) + 'i ' + str(gridDims[1]) + 'j ' + str(gridDims[2]) + 'k ' )
        log.write('grid ' + str(grid) + ' size is: ' + str(gridDims[0]) + 'i ' + str(gridDims[1]) + 'j ' + str(gridDims[2]) + 'k ' + '\n')

        totalvalues = (gridDims[0]*gridDims[1]*gridDims[2]) * 8
        completeLines = totalvalues // valuesPerLine
        lastLine = (completeLines * valuesPerLine) - totalvalues
        Krange = ( Krange[1] + 1 , Krange[1] + gridDims[2] )

        #print('> starting to write section ' + str(grid) + ' of the new property')
        log.write('> starting to write section ' + str(grid) + ' of the new property' + '\n')
        if intermediate :
            intermediate = False
            file.write('-- layers ' + str(Krange[0]) + '-' + str(Krange[1])  + ' corresponding to intemediate layer between grids ' + str(grid+1) + ' and ' + str(grid+2) + '\n')
            gridfile.write('-- layers ' + str(Krange[0]) + '-' + str(Krange[1])  + ' corresponding to intemediate layer between grids ' + str(grid+1) + ' and ' + str(grid+2) + '\n')
        else :
            intermediate = True
            file.write('-- layers ' + str(Krange[0]) + '-' + str(Krange[1])  + ' corresponding to grid ' + str(grid+1) + '\n')
            gridfile.write('-- layers ' + str(Krange[0]) + '-' + str(Krange[1])  + ' corresponding to grid ' + str(grid+1) + '\n')


        lineToWrite = ' ' + ' '.join(gridsToWrite[grid][1][:valuesPerLine]) + ' '
        #print('first line written:\n' + str(lineToWrite))
        log.write('first line written:\n' + str(lineToWrite) + '\n')

        # write all the entire lines
        for lineNumber in range(completeLines) :
            firstValue = lineNumber * valuesPerLine
            lastValue = firstValue + valuesPerLine
            lineToWrite = ' ' + ' '.join(gridsToWrite[grid][1][firstValue:lastValue]) + ' '
            file.write(lineToWrite + '\n')
            gridfile.write(lineToWrite + '\n')
            writtenValues = writtenValues + len(gridsToWrite[grid][1][firstValue:lastValue])

            lastValueCum = lastValueCum + valuesPerLine
            if prog < 100*lastValueCum//totaldimen :
                prog = 100*lastValueCum//totaldimen
                verbose( speak , 1 , 'writing grid ' + str(grid) + ' | ' + str(prog) + '%')

        # write line of last values
        if lastLine < 0 :
            lineToWrite = ' ' + ' '.join(gridsToWrite[grid][1][lastLine:]) + ' '
            file.write(lineToWrite + '\n')
            gridfile.write(lineToWrite + '\n')
            writtenValues = writtenValues + len(gridsToWrite[grid][1][lastLine:])

            lastValueCum = lastValueCum - lastLine
            if prog < 100*lastValueCum//totaldimen :
                prog = 100*lastValueCum//totaldimen
                verbose( speak , 1 , 'writing grid ' + str(grid) + ' | ' + str(prog) + '%')

        gridfile.write('/ \n')
        gridfile.close()

        #print('last line written for grid :' + str(grid) + '\n' + str(lineToWrite))
        log.write('last line written for grid :' + str(grid) + '\n' + str(lineToWrite) + '\ndone!\n')

    #write slash to close keyword in the main file
    file.write('/ \n')
    file.close()

    verbose( speak , 3 , 'keyword ' + str(keywordName) + ' successfully processed' )

    return True
