# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 12:33:46 2019

@author: MCARAYA

routine intended to manipulate and transform date strings.
"""
import numpy as np

def date(date , formatIN='', formatOUT=''):
    """
    stringformat.date receives a string containing a date or a list of strings
    containing dates and changes the date format to the format especified by
    the user. By default the out format will be 'DD-MMM-YYYY'.

    The input and output format can be stated with the keywords formatIN
    and formatOUT followed by a string containing the characters 'D', 'M'
    and 'Y' to identify day, month and year and the characters '/', '-' , ' ',
    '\t' (tab) or '_' as separators.

    If the keyword formatIN is not entered, the program will try to infer
    the date format from the provided data.

    syntax examples:

    stringformat.date('31/DEC/1984' , formatIN='DD/MMM/YYYY' , formatOUT='MM-DD-YYYY')

    """

    MonthString2Number = {'JAN' :  1 ,
                          'FEB' :  2 ,
                          'MAR' :  3 ,
                          'APR' :  4 ,
                          'MAY' :  5 ,
                          'JUN' :  6 ,
                          'JUL' :  7 ,
                          'JLY' :  7 ,
                          'AUG' :  8 ,
                          'SEP' :  9 ,
                          'OCT' : 10 ,
                          'NOV' : 11 ,
                          'DEC' : 12 }
    MonthNumber2String = { 1 : 'JAN' ,
                           2 : 'FEB' ,
                           3 : 'MAR' ,
                           4 : 'APR' ,
                           5 : 'MAY' ,
                           6 : 'JUN' ,
                           7 : 'JUL' ,
                           8 : 'AUG' ,
                           9 : 'SEP' ,
                          10 : 'OCT' ,
                          11 : 'NOV' ,
                          12 : 'DEC'  }

    # define if input is a list/tuple of dates or a single date
    # if type(date) == np.str_ or type(date) == np.ndarray or type(date) == np.datetime64 :
    #     sample = date[0]
    #     output = np
    #     date = date.tolist()
    if type(date) == list or type(date) == tuple:
        sample = date[0].strip()
        for i in range(len(date)) :
            date[i] = date[i].strip()
        output = list
    else :
        sample = date.strip()
        date = [ date ]
        output = str

    # look for the separator, empty string if not found
    separator = ''
    for sep in ['/', '-' , ' ' , '\t', '_', ':', ';', '#', "'"] :
            if sep in sample :
                separator = sep
                break

    # separate the 1st, 2nd and 3rd components of the DATEs in three lists
    datelist = separator.join(date).split(separator)
    datelist = [ datelist[0::3] , datelist[1::3] , datelist[2::3] ]


    # if formatIN is not defined try to guess what it is
    if formatIN == '' :
        datestr = [False, False, False]
        datemax = [None, None, None]

        for i in range(3) :
            for j in range(len(date)) :
                try:
                    datelist[i][j] = int(datelist[i][j])
                except :
                    datestr[i] = True
                    break
            if datestr[i] == False :
                datemax[i] = max(datelist[i])

        orderIN = [None, None, None, separator , None, None , None]
        found = ''
        if True in datestr :
            orderIN[5] = 3
            found = found + 'Ms'
        for i in range(3) :
            if datestr[i] == True :
                orderIN[1] = i
                found = found + 'M'
            elif datemax[i] != None and datemax[i] > 1000 :
                orderIN[2] = i
                orderIN[6] = 4
                found = found + 'Y'
            elif datemax[i] != None and datemax[i] > 31 :
                orderIN[2] = i
                orderIN[6] = 2
                found = found + 'Y'
            elif datemax[i] != None and datemax[i] > 12 and datemax[i] < 32 :
                orderIN[0] = i
                orderIN[4] = 2
                found = found + 'D'
            else :
                pass

        if None in orderIN :
            for i in range(3) :
                if datemax[i] != None and datemax[i] <= 12 :
                    if 'D' in found and 'M' not in found:
                        orderIN[1] = i
                        orderIN[5] = 2
                        found = found + 'M'
                    elif 'M' in found and 'D' not in found :
                        orderIN[0] = i
                        orderIN[4] = 2
                        found = found + 'D'

        if 'Ms' in found :
            found = found[2:]

        if 'D' in found and 'M' in found and 'Y' in found :
            formatIN = []
            for i in range(3) :
                if orderIN[i] == 0 :
                    formatIN.append('D'*orderIN[4])
                elif orderIN[i] == 1 :
                    formatIN.append('M'*orderIN[5])
                elif orderIN[i] == 2 :
                    formatIN.append('Y'*orderIN[6])
            formatIN = orderIN[3].join(formatIN)
            print('the input format is: ' + formatIN)
        else :
            raise Exception('unable to idenfy date format, please provide with keyword formatIN')

    # read input format from formatIN
    else :
        orderIN = [None, None, None, None, None, None, None] # [day, month, year, separator, day_digit, month_digits , year_digits]
        for sep in ['/', '-' , ' ' , '\t', '_', ':', ';', '#', "'"] :
            if sep in formatIN :
                orderIN[3] = sep
                break
        indexDMY = [ formatIN.upper().index('D') , formatIN.upper().index('M') , formatIN.upper().index('Y') ]
        for i in range(3) :
            if indexDMY[i] == min(indexDMY):
                orderIN[i] = 0
            elif indexDMY[i] == max(indexDMY):
                orderIN[i] = 2
            else :
                orderIN[i] = 1
        orderIN[4] = formatIN.upper().count('D')
        orderIN[5] = formatIN.upper().count('M')
        orderIN[6] = formatIN.upper().count('Y')

        for sep in ['/', '-' , ' ' , '\t'] :
            if sep in formatIN :
                test = sep
                break


    # set formatOUT by default if not provided
    if formatOUT == '' :
        formatOUT = 'DD-MMM-YYYY'
        orderOUT = [0,1,2,'-',2,3,4]
        print('default output format is: DD-MMM-YYYY')

    # read format from formatOUT
    else :
        orderOUT = [None, None, None, '', None, None , None] # [day, month, year, separator, day_digit, month_digits , year_digits]
        for sep in ['/', '-' , ' ' , '\t', '_', ':', ';', '#', "'"] :
            if sep in formatOUT :
                orderOUT[3] = sep
                break
        if 'D' in formatOUT.upper() :
            indexD = formatOUT.upper().index('D')
        else :
            indexD = 2
        if 'M' in formatOUT.upper() :
            indexM = formatOUT.upper().index('M')
        else :
            indexM = 2
        if 'Y' in formatOUT.upper() :
            indexY = formatOUT.upper().index('Y')
        else :
            indexY = 2
        indexDMY = [ indexD , indexM , indexY ]
        for i in range(3) :
            if indexDMY[i] == min(indexDMY):
                orderOUT[i] = 0
            elif indexDMY[i] == max(indexDMY):
                orderOUT[i] = 2
            else :
                orderOUT[i] = 1
        orderOUT[4] = formatOUT.upper().count('D')
        orderOUT[5] = formatOUT.upper().count('M')
        orderOUT[6] = formatOUT.upper().count('Y')


    dateOUT = [ datelist[orderIN.index(orderOUT[0])] , datelist[orderIN.index(orderOUT[1])] , datelist[orderIN.index(orderOUT[2])] ]

    if orderOUT[5] == 0 :
        dateM = ''
    elif orderOUT[5] > 2 and orderIN[5] <= 2 :
        dateM = orderOUT[1]
        for i in range(len(dateOUT[dateM])) :
            dateOUT[dateM][i] = MonthNumber2String[int(dateOUT[dateM][i])]
    elif orderOUT[5] <= 2 and orderIN[5] > 2 :
        dateM = orderOUT[1]
        for i in range(len(dateOUT[dateM])) :
            dateOUT[dateM][i] = MonthString2Number[dateOUT[dateM][i]]

    dateOUTformated = []
    numberformat = [None,None,None] # [year,day,month]
    for i in range(3) :
        numberformat[orderOUT[i]] = orderOUT[i+4]
    for i in range(len(dateOUT[0])) :
        #print(numberformat)
        if numberformat[0] == 0 or numberformat[0] == None:
            dateStr = ''
        elif type(dateOUT[0][i]) == int and numberformat[0] == 2 and dateOUT[0][i] < 10 :
            dateStr = '0' + str(dateOUT[0][i]) + orderOUT[3]
        else :
            dateStr = str(dateOUT[0][i]) + orderOUT[3]
        if numberformat[1] == 0 or numberformat[1] == None :
            dateStr = dateStr + ''
        elif type(dateOUT[1][i]) == int and numberformat[1] == 2 and dateOUT[1][i] < 10 :
            dateStr = dateStr + '0' + str(dateOUT[1][i]) + orderOUT[3]
        else :
            dateStr = dateStr + str(dateOUT[1][i]) + orderOUT[3]
        if numberformat[2] == 0 or numberformat[2] == None:
            dateStr = dateStr + ''
        elif type(dateOUT[2][i]) == int and numberformat[2] == 2 and dateOUT[2][i] < 10 :
            dateStr = dateStr + '0' + str(dateOUT[2][i])
        else :
            dateStr = dateStr + str(dateOUT[2][i])

        dateOUTformated.append( dateStr )

    if output == str :
        return dateOUTformated[0]
    else :
        return dateOUTformated
