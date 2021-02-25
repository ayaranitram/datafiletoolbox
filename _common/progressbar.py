# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 20:39:44 2020

@author: MCARAYA
"""

__version__ = 0.5
__release__ = 210225
__all__ = ['progressbar']

import time

def progressbar(percentage_or_counter) :
    endline = '\r'
    if type(percentage_or_counter) is float :
        if round(percentage_or_counter,2) == 100.0 :
            endline = '\n'
        partial = '  ░░▒▒▓▓██'[ int(percentage_or_counter%2.5) ] #* (int(percentage_or_counter%5)>0) + ''  # '█▀▄▌▐' ' ░▒▓█'
        completed = '█'*int(percentage_or_counter/2.5)
        # partial = '0123456789'[ int((percentage_or_counter%5)*2) ] # '█▀▄▌▐'
        # completed = '9'*int(percentage_or_counter/5)
        empty = ' '*(40 - len(completed) -1)
        percentage = '  '*(round(percentage_or_counter, 2)<100.0) + str(round(percentage_or_counter, 2)) +'%'
        progress = completed + partial + empty + percentage
    elif type(percentage_or_counter) is int :
        if percentage_or_counter == 0 :
            progress = ' '*40
        elif percentage_or_counter < 40 :
            partial =  ' ░▒▓█     ' *8 + ' ░▒▓█'[-percentage_or_counter%5:]
            emtpy = ' '*(40-percentage_or_counter)
            progress = partial + emtpy
            progress = progress[-40:]
        else :
            partial =  ' ░▒▓█     ' *8 + ' ░▒▓█'[-percentage_or_counter%5:]
            progress = partial[-40:]
    print(progress, end=endline)

for i in range(101) :
    progressbar(float(i))
    time.sleep(0.01)

# time.sleep(1)

# for i in range(400) :
#     progressbar(i)
#     time.sleep(0.01)