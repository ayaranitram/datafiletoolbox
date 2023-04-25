# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:31:52 2020

@author: MCARAYA
"""

__version__ = '0.4.5'
__release__ = 20220420
__all__ = ['Plot']

import time
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import is_color_like
from matplotlib.figure import Figure
from math import log
from .._common.functions import _is_SimulationResult
from .._common.inout import _verbose
from .._common.functions import _mainKey
from .._common.units import convertUnit

timeout = 0.1


def savePlot(figure, FileName=''):
    figure.savefig(FileName)


def Plot(SimResultObjects=[], Y_Keys=[], X_Key='TIME', X_Units=[], Y_Units=[], ObjectsColors=[], SeriesColors=[],
         graphName='', Y_Axis=[], Y_Scales=[], legendLocation='best', X_Scale=[], Labels={}, linewidth=[], linestyle=[],
         markers=[], markersize=[], do_not_repeat_colors=True, ColorBySimulation=None, ColorBySeries=None,
         DropZeros=False, minlinewidth=0.1, minmarkersize=0.5, Xgrid=0, Ygrid=0, fig=None, num=None, show=True,
         hline=None, figsize=(6, 4), dpi=150, singleYaxis=False, legend=True, xlim=(None, None), ylim=(None, None),
         tight_layout=True, **kwargs):
    """
    uses matplot lib to create graphs of the selected vectors
    for the selected SimResult objects.
    """
    
    # validate common keyword parameters:
    for kw in ['xMin', 'xMax', 'yMin', 'yMax', 'Xmin', 'Xmax', 'Ymin', 'Ymax']:
        if kw in kwargs:
            kwargs[kw.lower()] = kwargs[kw]
            kwargs.pop(kw, None)

    if 'xmin' in kwargs and 'xmax' in kwargs:
        if xlim == (None, None):
            xlim = (kwargs['xmin'], kwargs['xmax'])
            kwargs.pop('xmin', None)
            kwargs.pop('xmax', None)
    elif 'xmin' in kwargs:
        if xlim == (None, None):
            xlim = (kwargs['xmin'], None)
            kwargs.pop('xmin', None)
    elif 'xmax' in kwargs:
        if xlim == (None, None):
            xlim = (None, kwargs['xmax'])
            kwargs.pop('xmax', None)

    if 'ymin' in kwargs and 'ymax' in kwargs:
        if ylim == (None, None):
            ylim = (kwargs['ymin'], kwargs['ymax'])
            kwargs.pop('ymin', None)
            kwargs.pop('ymax', None)
    elif 'ymin' in kwargs:
        if ylim == (None, None):
            ylim = (kwargs['ymin'], None)
            kwargs.pop('ymin', None)
    elif 'ymax' in kwargs:
        if ylim == (None, None):
            ylim = (None, kwargs['ymax'])
            kwargs.pop('ymax', None)

    # validate plt.tight_layout() argument
    tight_layout = bool(tight_layout)

    # validate pyplot figure parameters
    if fig is None and num is None:
        pass
    elif not isinstance(fig, Figure) and num is None:
        raise TypeError('fig must be a matplotlib.Figure instance')
    elif fig is None and not isinstance(num, (str, int, Figure)):
        raise TypeError('num must be int, str or matplotlib.Figure')

    if dpi is not None and not isinstance(dpi, (int, float)):
        raise TypeError('dpi must be int or float')

    if figsize is None:
        pass
    elif type(figsize) is tuple:
        if len(figsize) != 2:
            raise ValueError('figsize must be a tuple of two floats or integers')
        if not isinstance(figsize[0], (int, float)):
            raise TypeError('figsize must be a tuple of floats (float,float)')
        if not isinstance(figsize[1], (int, float)):
            raise TypeError('figsize must be a tuple of floats (float,float)')

    # ensure SimResultObjects is not empty and is OK
    if len(SimResultObjects) == 0:
        raise TypeError('<Plot> at least one SimResult object is required (first argument).')
    if not _is_SimulationResult(SimResultObjects) and type(SimResultObjects) is not list and type(
            SimResultObjects) is not tuple:
        raise TypeError('<Plot> SimResultObjects must be a SimResult object or a list of SimResult objects.')
    if type(SimResultObjects) is not list:
        SimResultObjects = [SimResultObjects]
    if type(SimResultObjects) is tuple:
        SimResultObjects = list(SimResultObjects)

    CheckedList = []
    for each in range(len(SimResultObjects)):
        if _is_SimulationResult(SimResultObjects[each]):
            CheckedList.append(SimResultObjects[each])
        else:
            if each == 0:
                print('<Plot> the 1st simulation object (python index 0 of list) is not a SimulationResult object.')
            elif each == 1:
                print('<Plot> the 2nd simulation object (python index 1 of list) is not a SimulationResult object.')
            else:
                print('<Plot> the ' + str(each + 1) + 'th simulation object (python index ' + str(
                    each) + ' of list) is not a SimulationResult object.')
    SimResultObjects = CheckedList[:]
    CheckedList = None

    # ensure Y_Keys is not empty and is OK
    if type(Y_Keys) is str:
        Y_Keys = [Y_Keys]
    if type(Y_Keys) is tuple:
        Y_Keys = list(Y_Keys)
    if type(Y_Keys) is not list:
        raise TypeError('<Plot> Y_Keys must be a string, or a list of strings.')
    if len(Y_Keys) == 0:
        raise TypeError('<Plot> at least one Key to plot is required (second argument).')

    # put X Key in a list, if not already a list
    if type(X_Key) is str:
        X_Key = [X_Key]
    if type(X_Key) is tuple:
        X_Key = list(X_Key)
    if type(X_Key) is not list:
        raise TypeError('<Plot> X_Key must be a string, or a list of strings.')
    # if more than 1 X key is received
    if len(X_Key) > 1:
        if len(X_Key) == len(Y_Keys):
            pass  # it is OK, they are pairs of X & Y
        else:
            X_Key = X_Key[:1]  # keep only the first one

    # put X Units in a list, if not already
    if type(X_Units) is str:
        X_Units = [X_Units]
    if type(X_Units) is tuple:
        X_Units = list(X_Units)
    if type(X_Units) is not list:
        raise TypeError('<Plot> X_Units must be a string, or a list of strings.')
    # if is an empty list, take the units from the X of the first object
    elif len(X_Units) == 0:
        if len(X_Key) == 1:
            X_Units = [SimResultObjects[-1].get_plotUnit(X_Key[0])]
        else:
            X_Units = [SimResultObjects[-1].get_plotUnit(X_Key[i]) for i in range(len(X_Key))]
    # if more than 1 X Units are in the list
    elif len(X_Units) > 1:
        if len(X_Units) == len(X_Key):
            pass  # it is OK, one unit per key
        else:
            X_Units = X_Units[:1] * len(X_Key)  # keep only the first one repeated as many times as len(X_Key)

    # put Y Units in a list, if not already
    if type(Y_Units) is str:
        Y_Units = [Y_Units]
    if type(Y_Units) is tuple:
        Y_Units = list(Y_Units)
    if type(Y_Units) is not list:
        raise TypeError('<Plot> Y_Units must be a string, or a list of strings.')
    if len(Y_Units) == 0:
        Y_Units = [SimResultObjects[-1].get_plotUnit(Y_Keys[0])]
    if len(Y_Units) < len(Y_Keys):
        for y in range(len(Y_Units), len(Y_Keys)):
            Y_Units.append(SimResultObjects[-1].get_plotUnit(Y_Keys[y]))
        time.sleep(timeout)

    # check matplotlib.pyplot.plot color argument is provided
    if 'c' in kwargs and (ObjectsColors is None or len(ObjectsColors) == 0):
        SeriesColors = kwargs['c']
    if 'color' in kwargs and (ObjectsColors is None or len(ObjectsColors) == 0):
        SeriesColors = kwargs['color']
    # check ObjectsColors is OK or empty
    if type(ObjectsColors) is str:
        ObjectsColors = [ObjectsColors]
    elif type(ObjectsColors) is tuple and len(ObjectsColors) == 3 and (
            type(ObjectsColors[0]) is float or type(ObjectsColors[0]) is int) and (
            type(ObjectsColors[1]) is float or type(ObjectsColors[1]) is int) and (
            type(ObjectsColors[2]) is float or type(ObjectsColors[2]) is int):
        ObjectsColors = [ObjectsColors]
    elif type(ObjectsColors) is tuple:
        ObjectsColors = list(ObjectsColors)
    if type(ObjectsColors) is not list:
        raise TypeError(
            '<Plot> ObjectsColors must be a matplotlib color string, a single RGB tuple, or a list of strings or RGB tuples.')

    # check matplotlib.pyplot.plot color argument is provided
    if 'c' in kwargs and (SeriesColors is None or len(SeriesColors) == 0):
        SeriesColors = kwargs['c']
    if 'color' in kwargs and (SeriesColors is None or len(SeriesColors) == 0):
        SeriesColors = kwargs['color']
    # check SeriesColors is OK or empty
    if type(SeriesColors) is str:
        SeriesColors = [SeriesColors]
    elif type(SeriesColors) is tuple and len(SeriesColors) == 3 and (
            type(SeriesColors[0]) is float or type(SeriesColors[0]) is int) and (
            type(SeriesColors[1]) is float or type(SeriesColors[1]) is int) and (
            type(SeriesColors[2]) is float or type(SeriesColors[2]) is int):
        SeriesColors = [SeriesColors]
    elif type(SeriesColors) is tuple:
        SeriesColors = list(SeriesColors)
    if type(SeriesColors) is not list:
        raise TypeError(
            '<Plot> SeriesColors must be a matplotlib color string, a single RGB tuple, or a list of strings or RGB tuples.')

    # check optial parameters
    if ColorBySimulation is not None and type(ColorBySimulation) is not bool:
        print('<Plot>  ColorBySimulation must be None, True or False')
    if ColorBySeries is not None and type(ColorBySeries) is not bool:
        print('<Plot>  ColorBySeries must be None, True or False')
    if ColorBySimulation is None:
        if len(SimResultObjects) == 1:
            ColorBySimulation = False
        elif len(SimResultObjects) < len(Y_Keys):
            ColorBySimulation = False
        else:
            ColorBySimulation = True
    if ColorBySeries is None:
        if len(SimResultObjects) == 1:
            ColorBySeries = True
        elif len(SimResultObjects) >= len(Y_Keys):
            ColorBySeries = False
        else:
            ColorBySeries = True

    # remove color argument from kwargs
    if 'c' in kwargs:
        del kwargs['c']
    if 'color' in kwargs:
        del kwargs['color']

    # remove show legeng argument from kwargs
    if 'legend' in kwargs:
        del kwargs['legend']

    # remove user limits from kwargs
    if 'xlim' in kwargs:
        del kwargs['xlim']
    if 'ylim' in kwargs:
        del kwargs['ylim']

    # define the figure name if not provided
    assert type(graphName) in (str, int)
    if type(graphName) is str and len(graphName.split()) == 0:
        graphName = str(Y_Keys) + ' vs ' + str(X_Key) + ' from ' + str(SimResultObjects)
    if num is None:
        num = graphName

    # put Y_Axis in a list, if not already
    if type(Y_Axis) is str:
        try:
            Y_Axis = int(Y_Axis)
        except:
            raise TypeError('<Plot> Y_Axis must be integer')
    if type(Y_Axis) is int:
        Y_Axis = [Y_Axis]
    if type(Y_Axis) is tuple:
        Y_Axis = list(Y_Axis)
    if type(Y_Axis) is not list:
        raise TypeError('<Plot> Y_Units must be a string, or a list of strings.')
    if Y_Axis == []:
        Y_Names = {}
        Y_Counter = 0
        Y_Axis = [0] * len(Y_Keys)
        for i in range(len(Y_Keys)):
            if Y_Keys[i].split(':')[0] in Y_Names:
                Y_Axis[i] = Y_Names[Y_Keys[i].split(':')[0]]
                _verbose(SimResultObjects[-1].get_Verbosity(), 1,
                         "<Plot> Axis for '" + Y_Keys[i] + "' is " + str(Y_Names[Y_Keys[i].split(':')[0]]))
            else:
                Y_Names[Y_Keys[i].split(':')[0]] = Y_Counter % 2
                Y_Axis[i] = Y_Counter % 2
                Y_Counter += 1
                _verbose(SimResultObjects[-1].get_Verbosity(), 1,
                         "<Plot> Axis for '" + Y_Keys[i] + "' is " + str(Y_Names[Y_Keys[i].split(':')[0]]))
            time.sleep(timeout)
    if len(Y_Axis) != len(Y_Keys):
        print('<Plot> found ' + str(len(Y_Axis)) + ' Y_Axis but ' + str(len(Y_Keys)) + ' Y_Keys.', Y_Axis, Y_Keys)

    if singleYaxis:
        Y_Axis = [0] * len(Y_Axis)

    # check Y_Scales is OK
    if Y_Scales == []:
        Y_Scales = [None] * len(Y_Keys)
    assert len(Y_Scales) == len(Y_Keys)

    # locationDict = { 'best' : 0,
    # 'upper right' : 1,
    # 'upper left' : 2,
    # 'lower left' : 3,
    # 'lower right' : 4,
    # 'right' : 5,
    # 'center left' : 6,
    # 'center right' : 7,
    # 'lower center' : 8,
    # 'upper center' : 9,
    # 'center' : 10 }

    if len(X_Key) == 1:
        # define the X label as the 1s X Key + its units
        Xlabel = X_Key[0] + ' [ ' + str(X_Units[0]) + ' ]'
    else:
        Xlabel = True
        for each in X_Key:
            if X_Key[0].split(':')[0] not in each:
                Xlabel = False
                break
            # time.sleep(timeout)
        if Xlabel:
            Xlabel = X_Key[0].split(':')[0] + ' [ ' + str(X_Units[0]) + ' ]'
        else:
            Xlabel = ', '.join(X_Key) + ' [ ' + ', '.join(list(set(X_Units))) + ' ]'

    # check markers parameter
    if type(markers) in [int, str, tuple]:
        markers = [markers]
    assert type(markers) is list
    if len(markers) == 0:
        if len(SimResultObjects) > 1:
            markers = ['None'] * len(SimResultObjects)
        elif len(Y_Keys) > 1:
            markers = ['None'] * len(Y_Keys)
        else:
            markers = ['None']
    # overwrite the default marker
    # by model first
    if len(SimResultObjects) > 1:
        for i in range(len(SimResultObjects)):
            if SimResultObjects[i].get_Marker() is not None:
                markers[i] = SimResultObjects[i].get_Marker()
    # by specific keys if single
    elif len(Y_Keys) > 0:
        for i in range(len(Y_Keys)):
            if SimResultObjects[-1].get_Marker(Y_Keys[i]) is not None:
                markers[i] = SimResultObjects[-1].get_Marker(Y_Keys[i])

    # check markersize parameter
    if type(markersize) is int or type(markersize) is float:
        markersize = [markersize]
    assert type(markersize) is list
    if len(markersize) == 0:
        if len(SimResultObjects) > 1:
            markersize = 2.0 / round((log(len(SimResultObjects)) + 1), 2)
            if markersize < minmarkersize:
                markersize = minmarkersize
            markersize = [markersize] * len(SimResultObjects)
        elif len(Y_Keys) > 1:
            markersize = 2.0 / round((log(len(Y_Keys)) + 1), 2)
            if markersize < minmarkersize:
                markersize = minmarkersize
            markersize = [markersize] * len(Y_Keys)
        else:
            markersize = [2.0]
    # overwrite the default markersize
    # by model first
    if len(SimResultObjects) > 1:
        markersize = markersize * len(SimResultObjects)
        for i in range(len(SimResultObjects)):
            if SimResultObjects[i].get_MarkerSize() is not None:
                markersize[i] = SimResultObjects[i].get_MarkerSize()
    # by specific keys if single
    elif len(Y_Keys) > 0:
        markersize = markersize * len(Y_Keys)
        for i in range(len(Y_Keys)):
            if SimResultObjects[-1].get_MarkerSize(Y_Keys[i]) is not None:
                markersize[i] = SimResultObjects[-1].get_MarkerSize(Y_Keys[i])

    # check linestyle parameter
    if type(linestyle) in [str]:
        linestyle = [linestyle]
    assert type(linestyle) is list
    if len(linestyle) == 0:
        if len(SimResultObjects) > 1:
            linestyle = ['-'] * len(SimResultObjects)
        elif len(Y_Keys) > 1:
            linestyle = ['-'] * len(Y_Keys)
        else:
            linestyle = ['-']
    # overwrite the default marker
    # by model first
    if len(SimResultObjects) > 1:
        for i in range(len(SimResultObjects)):
            if SimResultObjects[i].get_Style() is not None:
                linestyle[i] = SimResultObjects[i].get_Style()
    # by specific keys if single
    elif len(Y_Keys) > 0:
        for i in range(len(Y_Keys)):
            if SimResultObjects[-1].get_Style(Y_Keys[i]) is not None:
                linestyle[i] = SimResultObjects[-1].get_Style(Y_Keys[i])

    # check linewidth parameter
    if type(linewidth) is int or type(linewidth) is float:
        linewidth = [linewidth]
    assert type(linewidth) is list
    if len(linewidth) == 0:
        if len(SimResultObjects) > 1:
            linewidth = 2.0 / round((log(len(SimResultObjects)) + 1), 2)
            if linewidth < minlinewidth:
                linewidth = minlinewidth
            linewidth = [linewidth] * len(SimResultObjects)
        elif len(Y_Keys) > 1:
            linewidth = 2.0 / round((log(len(Y_Keys)) + 1), 2)
            if linewidth < minlinewidth:
                linewidth = minlinewidth
            linewidth = [linewidth] * len(Y_Keys)
        else:
            linewidth = [2.0]
    # overwrite the default linewidth
    # by model first
    if len(SimResultObjects) > 1:
        # if single Y_Key
        if len(Y_Keys) == 1:
            linewidth = linewidth * len(SimResultObjects)
            markersize = markersize * len(SimResultObjects)
            for i in range(len(SimResultObjects)):
                if SimResultObjects[i].get_Width() is not None:
                    linewidth[i] = SimResultObjects[i].get_Width()
                if SimResultObjects[i].get_MarkerSize() is not None:
                    markersize[i] = SimResultObjects[i].get_MarkerSize()
        elif len(linewidth) == len(Y_Keys):  # several Y_Keys and SimResultObjects
            linewidth = linewidth * len(SimResultObjects)
            markersize = markersize * len(SimResultObjects)
            for i in range(len(SimResultObjects)):
                for j in range(len(Y_Keys)):
                    if SimResultObjects[i].get_Width() is not None:
                        linewidth[i * len(Y_Keys) + j] = SimResultObjects[i].get_Width(Y_Keys[j])
                    if SimResultObjects[i].get_MarkerSize(Y_Keys[j]) is not None:
                        markersize[i * len(Y_Keys) + j] = SimResultObjects[i].get_MarkerSize(Y_Keys[j])
        elif len(linewidth) == len(SimResultObjects):  # several Y_Keys and SimResultObjects
            linewidth = linewidth * len(Y_Keys)
            markersize = markersize * len(Y_Keys)
            for i in range(len(SimResultObjects)):
                for j in range(len(Y_Keys)):
                    if SimResultObjects[i].get_Width() is not None:
                        linewidth[i * len(Y_Keys) + j] = SimResultObjects[i].get_Width(Y_Keys[j])
                    if SimResultObjects[i].get_MarkerSize(Y_Keys[j]) is not None:
                        markersize[i * len(Y_Keys) + j] = SimResultObjects[i].get_MarkerSize(Y_Keys[j])
        elif len(linewidth) == 1:  # several Y_Keys and SimResultObjects
            linewidth = [linewidth] * len(SimResultObjects) * len(Y_Keys)
            markersize = [markersize] * len(SimResultObjects) * len(Y_Keys)
            for i in range(len(SimResultObjects)):
                for j in range(len(Y_Keys)):
                    if SimResultObjects[i].get_Width() is not None:
                        linewidth[i * len(Y_Keys) + j] = SimResultObjects[i].get_Width(Y_Keys[j])
                    if SimResultObjects[i].get_MarkerSize(Y_Keys[j]) is not None:
                        markersize[i * len(Y_Keys) + j] = SimResultObjects[i].get_MarkerSize(Y_Keys[j])
        else:  # several Y_Keys and SimResultObjects
            linewidth = [linewidth] * len(SimResultObjects) * len(Y_Keys)
            markersize = [markersize] * len(SimResultObjects) * len(Y_Keys)
            for i in range(len(SimResultObjects)):
                for j in range(len(Y_Keys)):
                    if SimResultObjects[i].get_Width() is not None:
                        linewidth[i * len(Y_Keys) + j] = SimResultObjects[i].get_Width(Y_Keys[j])
                    if SimResultObjects[i].get_MarkerSize(Y_Keys[j]) is not None:
                        markersize[i * len(Y_Keys) + j] = SimResultObjects[i].get_MarkerSize(Y_Keys[j])


    # by specific keys if single
    elif len(Y_Keys) > 0:
        linewidth = linewidth * len(Y_Keys)
        for i in range(len(Y_Keys)):
            if SimResultObjects[-1].get_Width(Y_Keys[i]) is not None:
                linewidth[i] = SimResultObjects[-1].get_Width(Y_Keys[i])

    # set line colors and style:
    if len(SimResultObjects) == 1:  # only one simulation object to plot
        NColors = len(SeriesColors)
        SeriesColors = SeriesColors + [None] * (len(Y_Keys) - NColors)
        for c in range(NColors, len(Y_Keys)):
            if is_color_like(SimResultObjects[-1].get_Color(Y_Keys[c])):
                SeriesColors[c] = SimResultObjects[-1].get_Color(Y_Keys[c])
            elif 'THP' in Y_Keys[c]:
                SeriesColors[c] = ('lightgray')
            elif 'BHP' in Y_Keys[c]:
                SeriesColors[c] = ('darkgray')
            elif 'BP' in Y_Keys[c]:
                SeriesColors[c] = ('black')
            elif 'QOIL' in Y_Keys[c]:
                SeriesColors[c] = ((0, 1, 0))
            elif 'OP' in Y_Keys[c] or 'OIL' in Y_Keys[c]:
                SeriesColors[c] = ('g')
            elif 'NGL' in Y_Keys[c]:
                SeriesColors[c] = ((1, 1, 0))
            elif 'LPG' in Y_Keys[c]:
                SeriesColors[c] = ('orange')
            elif 'GP' in Y_Keys[c] or 'GAS' in Y_Keys[c]:
                SeriesColors[c] = ('r')
            elif 'GI' in Y_Keys[c]:
                SeriesColors[c] = ('m')
            elif 'WP' in Y_Keys[c]:
                SeriesColors[c] = ('b')
            elif 'WI' in Y_Keys[c]:
                SeriesColors[c] = ('c')
            elif 'GOR' in Y_Keys[c]:
                SeriesColors[c] = ('gold')
            elif 'WC' in Y_Keys[c]:
                SeriesColors[c] = ('steelblue')
            else:
                SeriesColors[c] = (random.random(), random.random(), random.random())
            # time.sleep(timeout)

        # plot history keywords as dots
        if SimResultObjects[-1].historyAsDots:
            for y in range(len(Y_Keys)):
                if _mainKey(Y_Keys[y]).endswith('H'):
                    if SimResultObjects[-1].get_Marker(Y_Keys[y]) is not None and SimResultObjects[-1].get_Marker(
                            Y_Keys[y]).lower().strip() not in ['none', '', ' ']:
                        markers[y] = SimResultObjects[-1].get_Marker(Y_Keys[y])
                    else:
                        markers[y] = '.'
                    if type(SimResultObjects[-1].get_MarkerSize(Y_Keys[y])) in (int, float):
                        markersize[y] = SimResultObjects[-1].get_MarkerSize(Y_Keys[y])
                    else:
                        markersize[y] = 1.0
                    linestyle[y] = 'None'

        if do_not_repeat_colors:  # repeated colors not-allowrd
            for c in range(NColors, len(SeriesColors)):
                while SeriesColors.count(SeriesColors[c]) > 1:
                    SeriesColors[c] = (random.random(), random.random(), random.random())
        else:  # repeated colors allowed
            Clean = list(set(SeriesColors))
            CleanCount = []
            CleanSorted = {}
            for each in Clean:
                CleanSorted[each] = SeriesColors.count(each)
                CleanCount.append(SeriesColors.count(each))
            CleanCount.sort()
            New_Y_Keys = [None] * sum(CleanCount)
            New_Y_Colors = [None] * sum(CleanCount)
            NY = 0
            # sort the colors by number of repetition
            SortedColors = [None] * len(CleanSorted)
            for CC in CleanCount[::-1]:
                for color in CleanSorted:
                    if CleanSorted[color] == CC and color not in SortedColors:
                        SortedColors[NY] = color
                        NY += 1

            NY = 0
            for color in SortedColors:
                for SC in range(len(SeriesColors)):
                    if SeriesColors[SC] == color:
                        New_Y_Colors[NY] = color
                        New_Y_Keys[NY] = Y_Keys[SC]
                        NY += 1
            SeriesColors = New_Y_Colors[:]
            Y_Keys = New_Y_Keys[:]
            New_Y_Colors = None
            New_Y_Keys = None

    elif len(Y_Keys) == 1:  # several simulation objects but a single key
        if SeriesColors == []:
            SeriesColors = ['solid']
        if len(ObjectsColors) < len(SimResultObjects):
            NObjects = len(ObjectsColors)
            ObjectsColors = ObjectsColors + [None] * (len(SimResultObjects) - NObjects)
            for c in range(NObjects, len(SimResultObjects)):
                ObjectsColors[c] = SimResultObjects[c].get_Color()

    else:  # several objects and keys
        if ColorBySimulation and not ColorBySeries:
            if len(ObjectsColors) < len(SimResultObjects):
                for c in range(len(ObjectsColors), len(SimResultObjects)):
                    NObjects = len(ObjectsColors)
                    ObjectsColors = ObjectsColors + [None] * (len(SimResultObjects) - NObjects)
                    for c in range(NObjects, len(SimResultObjects)):
                        ObjectsColors[c] = SimResultObjects[c].get_Color()

            # SeriesColors used to set style
            SeriesColors = [None] * len(Y_Keys)
            for c in range(len(Y_Keys)):

                if 'BHP' in Y_Keys[c]:
                    SeriesColors[c] = (0, (5, 10))
                elif 'BP' in Y_Keys[c]:
                    SeriesColors[c] = (0, (7, 8))
                elif 'OP' in Y_Keys[c] or 'OIL' in Y_Keys[c]:
                    SeriesColors[c] = 'solid'
                elif 'NGL' in Y_Keys[c]:
                    SeriesColors[c] = 'dashed'
                elif 'LPG' in Y_Keys[c]:
                    SeriesColors[c] = 'dashdot'
                elif 'GP' in Y_Keys[c] or 'GAS' in Y_Keys[c]:
                    SeriesColors[c] = 'dotted'
                elif 'GI' in Y_Keys[c]:
                    SeriesColors[c] = (0, (3, 5, 1, 5, 1, 5))
                elif 'WP' in Y_Keys[c]:
                    SeriesColors[c] = (0, (3, 5, 1, 5, 1, 5))
                elif 'WI' in Y_Keys[c]:
                    SeriesColors[c] = (0, (3, 5, 1, 5))
                else:
                    SeriesColors[c] = '--'

            # plot history keywords as dots
            if SimResultObjects[-1].historyAsDots:
                for y in range(len(Y_Keys)):
                    if _mainKey(Y_Keys[y]).endswith('H'):
                        if type(SimResultObjects[-1].get_Marker(Y_Keys[y])) is not None:
                            markers[y] = SimResultObjects[-1].get_Marker(Y_Keys[y])
                        else:
                            markers[y] = 'o'
                        if type(SimResultObjects[-1].get_MarkerSize(Y_Keys[y])) is float:
                            markersize[y] = SimResultObjects[-1].get_MarkerSize(Y_Keys[y])
                        else:
                            markersize[y] = 1.0
                        linestyle[y] = 'None'

            if do_not_repeat_colors:  # repeated colors not-allowrd
                if len(set(SeriesColors)) == 1:
                    SeriesColors = ['solid'] * len(Y_Keys)
            else:  # repeated colors allowrd
                pass
                # SeriesColors = []
                # for c in range ( len( Y_Keys ) ) :
                #     SeriesColors.append('solid')
                # time.sleep(timeout)

        if not ColorBySimulation and ColorBySeries:
            if len(ObjectsColors) < len(SimResultObjects):
                for c in range(len(ObjectsColors), len(SimResultObjects)):
                    NObjects = len(ObjectsColors)
                    ObjectsColors = ObjectsColors + [None] * (len(SimResultObjects) - NObjects)
                    for c in range(NObjects, len(SimResultObjects)):
                        ObjectsColors[c] = SimResultObjects[c].get_Style()

            # # SeriesColors used to set style
            SeriesColors = [None] * len(Y_Keys)
            for c in range(len(Y_Keys)):
                if is_color_like(SimResultObjects[-1].get_Color(Y_Keys[c])):
                    SeriesColors[c] = SimResultObjects[-1].get_Color(Y_Keys[c])
                elif 'THP' in Y_Keys[c]:
                    SeriesColors[c] = ('lightgray')
                elif 'BHP' in Y_Keys[c]:
                    SeriesColors[c] = ('darkgray')
                elif 'BP' in Y_Keys[c]:
                    SeriesColors[c] = ('black')
                elif 'QOIL' in Y_Keys[c]:
                    SeriesColors[c] = ((0, 1, 0))
                elif 'OP' in Y_Keys[c] or 'OIL' in Y_Keys[c]:
                    SeriesColors[c] = ('g')
                elif 'NGL' in Y_Keys[c]:
                    SeriesColors[c] = ((1, 1, 0))
                elif 'LPG' in Y_Keys[c]:
                    SeriesColors[c] = ('orange')
                elif 'GP' in Y_Keys[c] or 'GAS' in Y_Keys[c]:
                    SeriesColors[c] = ('r')
                elif 'GI' in Y_Keys[c]:
                    SeriesColors[c] = ('m')
                elif 'WP' in Y_Keys[c]:
                    SeriesColors[c] = ('b')
                elif 'WI' in Y_Keys[c]:
                    SeriesColors[c] = ('c')
                elif 'GOR' in Y_Keys[c]:
                    SeriesColors[c] = ('gold')
                elif 'WC' in Y_Keys[c]:
                    SeriesColors[c] = ('steelblue')
                else:
                    SeriesColors[c] = (random.random(), random.random(), random.random())

            # plot history keywords as dots
            if SimResultObjects[-1].historyAsDots:
                for y in range(len(Y_Keys)):
                    if _mainKey(Y_Keys[y]).endswith('H'):
                        if type(SimResultObjects[-1].get_Marker(Y_Keys[y])) is not None:
                            markers[y] = SimResultObjects[-1].get_Marker(Y_Keys[y])
                        else:
                            markers[y] = 'o'
                        if type(SimResultObjects[-1].get_MarkerSize(Y_Keys[y])) is float:
                            markersize[y] = SimResultObjects[-1].get_MarkerSize(Y_Keys[y])
                        else:
                            markersize[y] = 1.0
                        linestyle[y] = 'None'

            if do_not_repeat_colors:  # repeated colors not-allowrd
                if len(set(SeriesColors)) == 1:
                    SeriesColors = ['solid'] * len(Y_Keys)
            else:  # repeated colors allowrd
                pass
                # SeriesColors = []
                # for c in range ( len( Y_Keys ) ) :
                #     SeriesColors.append('solid')
                # time.sleep(timeout)

    if Y_Scales == []:
        Y_Scales = [None] * len(Y_Keys)

    Ylabel = str(Y_Keys[0]) + ' ' + str(Y_Units[0])
    Title = ''
    if len(Y_Keys) == 1:
        Title = Y_Keys[0] + ' vs ' + X_Key[0]
    if len(SimResultObjects) == 1:
        if len(Title) > 0:
            Title = Title + ' for ' + str(SimResultObjects[-1].get_Name())
        else:
            Title = str(SimResultObjects[-1].get_Name())

    if fig is None:
        fig = plt.figure(num=num, figsize=figsize, dpi=dpi)
    elif not isinstance(fig, Figure):
        raise TypeError('fig must be a matplotlib.pyplot Figure instance')

    Axis = [fig.add_subplot()]

    _ = plt.title(Title)

    # display grid if required
    if Xgrid > 0:
        if Xgrid == 1:
            plt.grid(True, 'both', 'x', color='k', alpha=0.25, linestyle='-', linewidth=0.25)
        elif Xgrid == 2:
            plt.grid(True, 'major', 'x', color='k', alpha=0.25, linestyle='-', linewidth=0.25)
        elif Xgrid == 3:
            plt.grid(True, 'minor', 'x', color='k', alpha=0.25, linestyle='-', linewidth=0.25)
            plt.grid(True, 'major', 'x', color='k', alpha=0.50, linestyle='-', linewidth=0.50)

    if Ygrid > 0:
        if Ygrid == 1:
            plt.grid(True, 'both', 'y', color='k', alpha=0.25, linestyle='-', linewidth=0.25)
        elif Ygrid == 2:
            plt.grid(True, 'major', 'y', color='k', alpha=0.25, linestyle='-', linewidth=0.25)
        elif Ygrid == 3:
            plt.grid(True, 'minor', 'y', color='k', alpha=0.25, linestyle='-', linewidth=0.25)
            plt.grid(True, 'major', 'y', color='k', alpha=0.50, linestyle='-', linewidth=0.50)

    Axis[0].set_xlabel(Xlabel)
    Axis[0].set_ylabel(Ylabel)

    if max(Y_Axis) > 0:
        for i in range(1, max(Y_Axis) + 1):
            Axis.append(Axis[0].twinx())
            Axis[i].set_ylabel('')
            time.sleep(timeout)

    AxLabels = {}
    AxUnits = {}
    for i in range(max(Y_Axis) + 1):
        AxLabels[i] = []
        AxUnits[i] = []
        time.sleep(timeout)

    Xdate = False
    if X_Key[0] in ('DATE', 'DATES'):
        Xdate = True
        ToU = SimResultObjects[-1].get_plotUnit(X_Key[0])
        FromU = SimResultObjects[-1].get_Unit(X_Key[0])
        X0 = SimResultObjects[-1](X_Key[0])
        X = convertUnit(X0, FromU, ToU, PrintConversionPath=(SimResultObjects[-1].get_Verbosity() == 1))
        time.sleep(timeout * 5)
        datemin = np.datetime64(X[0], 'Y')
        datemax = np.datetime64(X[-1], 'Y') + np.timedelta64(1, 'Y')
        # print('using dates')# format the ticks
        years = mdates.YearLocator()  # every year
        months = mdates.MonthLocator()  # every month
        years_fmt = mdates.DateFormatter('%Y')
        X = X.astype('O')
        Axis[0].xaxis.set_major_locator(years)
        Axis[0].xaxis.set_major_formatter(years_fmt)
        Axis[0].xaxis.set_minor_locator(months)

    plotLines = []
    for s in range(len(SimResultObjects)):

        FromU = SimResultObjects[s].get_Unit(X_Key[0])
        ToU = X_Units[0]
        X0 = SimResultObjects[s](X_Key[0])
        time.sleep(timeout)
        X = convertUnit(X0, FromU, ToU, PrintConversionPath=(SimResultObjects[s].get_Verbosity() == 1))
        time.sleep(timeout * 5)

        if Xdate is False and type(X) != np.ndarray:
            if type(X) is list or type(X) is tuple:
                try:
                    X = np.array(X, dtype='float')
                except:
                    print('<Plot> the X key ' + X_Key[0] + ' from simulation ' + SimResultObjects[
                        s].get_Name() + ' is not numpy array.')
        elif Xdate:
            X = X.astype('datetime64[D]').astype('O')  # convert numpy date array to array of datetime objects

            if xlim != (None, None):
                xlim = list(xlim)
                for xl in range(2):  # try to convert date as string to datetime object
                    if type(xlim[xl]) is str:
                        try:
                            xlim[xl] = pd.to_datetime(xlim[xl]).to_numpy().astype('datetime64[D]').astype('O')
                        except:
                            pass
                xlim = tuple(xlim)

        for y in range(len(Y_Keys)):
            time.sleep(timeout)
            # check if the key exists in the object:
            if not SimResultObjects[s].is_Key(Y_Keys[y]):
                continue
            Y0 = SimResultObjects[s](Y_Keys[y])

            if len(Y_Keys) == len(X_Key):
                FromU = SimResultObjects[s].get_Unit(X_Key[y])
                ToU = X_Units[y]
                X0 = SimResultObjects[s](X_Key[y])
                time.sleep(timeout)
                X = convertUnit(X0, FromU, ToU, PrintConversionPath=(SimResultObjects[s].get_Verbosity() == 1))
                time.sleep(timeout * 5)

                if Xdate == False and type(X) != np.ndarray:
                    if type(X) == list or type(X) == tuple:
                        try:
                            X = np.array(X, dtype='float')
                        except:
                            print('<Plot> the X key ' + X_Key[y] + ' from simulation ' + SimResultObjects[
                                s].get_Name() + ' is not numpy array ')
                elif Xdate:
                    X = X.astype('datetime64[D]').astype('O')  # X = X.astype('O')

            if Y0 is None:
                pass
            else:

                if len(SimResultObjects) == 1:
                    # ThisLabel = str(Y_Keys[y])
                    if str(Y_Keys[y]) in Labels:
                        ThisLabel = str(Labels[Y_Keys[y]])
                    else:
                        ThisLabel = str(Y_Keys[y])

                elif len(Y_Keys) == 1:
                    # ThisLabel = str( SimResultObjects[s].get_Name() + ' ' + Y_Keys[0] )
                    if str(SimResultObjects[s]) in Labels:
                        ThisLabel = str(Labels[SimResultObjects[s]])
                    elif str(SimResultObjects[s].get_Name()) in Labels:
                        ThisLabel = str(Labels[SimResultObjects[s].get_Name()])
                    else:
                        ThisLabel = str(SimResultObjects[s].get_Name())  # + ' ' + Y_Keys[0] )
                else:
                    # ThisLabel = str( SimResultObjects[s].get_Name() + ' ' + Y_Keys[y] )
                    if str(SimResultObjects[s]) in Labels:
                        ThisLabel = str(Labels[SimResultObjects[s]])
                    elif str(SimResultObjects[s].get_Name()) in Labels:
                        ThisLabel = str(Labels[SimResultObjects[s].get_Name()])
                    else:
                        ThisLabel = str(SimResultObjects[s].get_Name())

                    if str(Y_Keys[y]) in Labels:
                        ThisLabel = ThisLabel + ' ' + str(Labels[Y_Keys[y]])
                    else:
                        ThisLabel = ThisLabel + ' ' + str(Y_Keys[y])

                # convertUnit(value, fromUnit, toUnit, PrintConversionPath=True):
                FromU = SimResultObjects[s].get_Unit(Y_Keys[y])
                ToU = Y_Units[y]

                Y = convertUnit(Y0, FromU, ToU, PrintConversionPath=(SimResultObjects[s].get_Verbosity() == 1))
                time.sleep(timeout * 5)
                if type(Y) != np.ndarray:
                    if type(X) == list or type(X) == tuple:
                        try:
                            Y = np.array(Y, dtype='float')
                        except:
                            print('<Plot> the Y key ' + Y_Keys[y] + ' from simulation ' + SimResultObjects[
                                s].get_Name() + ' is not numpy array.')

                if type(Y) == np.ndarray:
                    if DropZeros and Y.min() == 0 and Y.max() == 0:
                        print('<Plot> skipping the Y key ' + Y_Keys[y] + ' from simulation ' + SimResultObjects[
                            s].get_Name() + ' because it is all zeroes.')
                        continue
                    if len(Y) != len(X):
                        print('<Plot> the Y vector ' + str(Y_Keys[y]) + ' from the model ' + str(
                            SimResultObjects[s]) + ' contains less than tha its X vector ' + str(
                            X_Key[0]) + '\n       len(Y):' + str(len(Y)) + ' != len(X):' + str(len(X)))
                    else:
                        Yax = Y_Axis[y]
                        # print('\n\ndebuging:','\nlen(sims)',len(SimResultObjects),'\nlen(Y_Keys)',len(Y_Keys),'\ns',s,'\ny',y,'\nObjectsColors',ObjectsColors,'\nSeriesColors',SeriesColors,'\nlinewidth',linewidth,'\nlinestyle',linestyle,'\nmarkers',markers,'\nmarkersize',markersize)
                        if len(SimResultObjects) == 1:
                            Lc = SeriesColors[y]
                            Lw = linewidth[y]
                            Ls = linestyle[y]
                            Mk = markers[y]
                            Ms = markersize[y]
                        elif len(Y_Keys) == 1:
                            Lc = ObjectsColors[s]
                            Lw = linewidth[s]
                            Ls = linestyle[s]
                            Mk = markers[s]
                            Ms = markersize[s]
                        elif not ColorBySimulation and ColorBySeries:
                            Ls = ObjectsColors[s]
                            Lw = linewidth[s * len(Y_Keys) + y]
                            Lc = SeriesColors[y]  # linestyle[y]  # linestyle[s]
                            Mk = markers[s]
                            Ms = markersize[s * len(Y_Keys) + y]
                        elif ColorBySimulation and not ColorBySeries:  # else:  # elif len(SimResultObjects) > len(Y_Keys)
                            Lc = ObjectsColors[s]
                            Lw = linewidth[s * len(Y_Keys) + y]
                            Ls = linestyle[y]  # linestyle[s]
                            Mk = markers[s]
                            Ms = markersize[s * len(Y_Keys) + y]
                        if len(Y_Keys) == 1:
                            Yax = 0
                        # if len(SimResultObjects) > 1 and len(Y_Keys) > 1:
                        #     # if len( SimResultObjects ) > len( Y_Keys ):
                        #     #     Ls = SimResultObjects[s].style
                        #     # else:
                        #     #     Ls = SeriesColors[s]
                        #     Ls = SeriesColors[s]

                        plotLines += Axis[Yax].plot(X, Y, linestyle=Ls, linewidth=Lw, color=Lc, marker=Mk,
                                                    markersize=Ms, label=ThisLabel, **kwargs)

                        if Xdate:
                            # round to nearest years.
                            if np.datetime64(X[0], 'Y') < datemin:
                                datemin = np.datetime64(X[0], 'Y')
                            if np.datetime64(X[-1], 'Y') + np.timedelta64(1, 'Y') > datemax:
                                datemax = np.datetime64(X[-1], 'Y') + np.timedelta64(1, 'Y')

                        AxLabels[Y_Axis[y]].append(Y_Keys[y].split(':')[0])
                        AxUnits[Y_Axis[y]].append(Y_Units[y])

        if Xdate:
            Axis[0].set_xlim(datemin, datemax)
            fig.autofmt_xdate()
            Axis[0].fmt_xdata = mdates.DateFormatter('%Y-%b')

    for i in range(max(Y_Axis) + 1):  # for i in range( max(Y_Axis) +1) :
        time.sleep(timeout)
        textA = ', '.join(list(set(AxLabels[i])))
        textB = ' [ ' + ', '.join(list(set(AxUnits[i]))) + ' ]'
        Axis[i].set_ylabel(textA + textB)
        if len(Y_Scales) < i and Y_Scales[i] is not None:
            Axis[i].set(ylim=(Y_Scales[i]))

    if X_Scale != []:
        Axis[0].set_xlim(X_Scale[0], X_Scale[1])
    # Axis[0].set_xlim(0, 50)
    if do_not_repeat_colors:
        plotLabels = [l.get_label() for l in plotLines]
        LegendLines = plotLines
    else:
        plotLabels = []
        LegendLines = []
        labeled = []
        for l in plotLines:
            N = SeriesColors.count(SeriesColors[Y_Keys.index(l.get_label())])
            if N < 10:
                plotLabels += [l.get_label()]
                LegendLines += [l]
            elif _mainKey(l.get_label()) not in labeled:
                plotLabels += [_mainKey(l.get_label())]
                LegendLines += [l]
                labeled.append(_mainKey(l.get_label()))
            else:
                plotLabels += [None]
                LegendLines += [None]

    # display the legend
    if bool(legend):
        Axis[0].legend(LegendLines, plotLabels,
                       loc=legendLocation)  # LegendLines contains selected plotLines for the leggend

    # display horizontal line if required
    if type(hline) is dict and len(hline) > 0:
        plt.hlines(hline['y'], xmin=hline['xmin'] if 'xmin' in hline else None,
                   xmax=hline['xmax'] if 'xmax' in hline else None,
                   colors=hline['colors'] if 'colors' in hline else None,
                   linestyles=hline['linestyle'] if 'linestyle' in hline else None,
                   label=hline['label'] if 'label' in hline else None)
    elif type(hline) in (int, float):
        xMin, xMax = plt.xlim()
        print('limites x de la figura', xMin, xMax)
        plt.hlines(hline, xmin=xMin, xmax=xMax, colors='darkgray', linestyles='--', label='')

    # set the user limits
    plt.xlim(xlim)
    plt.ylim(ylim)

    if tight_layout:
        plt.tight_layout()

    return fig
