# -*- coding: utf-8 -*-
"""
Created on Wed May 13 00:46:05 2020

@author: MCARAYA
"""

__version__ = '0.4.5'
__release__ = 20230110
__all__ = ['_mainKey', '_itemKey', '_keyType', '_wellFromAttribute', 'tamiz', '_meltDF', '_pivotDF']

import pandas
import numpy
from .._Classes.SimPandas import SimSeries, SimDataFrame


def _is_SimulationResult(obj):
    """
    returns True if the object is a SimulationResults object.
    """
    return 'SimulationResults.' in str(type(obj))


def _mainKey(Key, clean=True, nameSeparator=':'):
    """
    returns the main part (before the name of the item) in the keyword,MAIN:ITEM
    """
    if type(Key) is str:
        if len(Key.strip()) > 0:
            return Key.strip().split(nameSeparator)[0]
        else:
            return ''
    if type(Key) is tuple and len(Key) == 2:
        return _mainKey(str(Key[0]), clean=clean, nameSeparator=nameSeparator)
    if type(Key) is list or type(Key) is tuple:
        results = [_mainKey(K) for K in Key]
        if clean:
            return list(set(results))
        else:
            return list(results)
    if isinstance(Key, (SimSeries, pandas.Series)):
        return _mainKey(Key.name)


def _itemKey(Key, clean=True, nameSeparator=':'):
    """
    returns the item part (after the name of the item) in the keyword, MAIN:ITEM
    """
    if type(Key) is str:
        if len(Key.strip()) > 0:
            if nameSeparator in Key.strip():
                return Key.strip().split(nameSeparator)[-1]
        else:
            return ''
    if type(Key) is tuple and len(Key) == 2:
        return _itemKey(str(Key[0]), clean=clean, nameSeparator=nameSeparator)
    if type(Key) is list or type(Key) is tuple:
        results = [_itemKey(K) for K in Key]
        if clean:
            return list(set(results))
        else:
            return list(results)
    if isinstance(Key, (SimSeries, pandas.Series)):
        return _itemKey(Key.name)


def _keyType(Key):
    """
    returns the type of key for an ECL style key:
        FIELD
        REGION
        WELL
        GROUP
    """
    if type(Key) is str:
        Key = Key.strip()
        if len(Key) > 0:
            if Key[0] == 'F':
                return 'FIELD'
            if Key[0] == 'R':
                return 'REGION'
            if Key[0] == 'W':
                return 'WELL'
            if Key[0] == 'G':
                return 'GROUP'
            return 'OTHER'


def _isECLkey(Key, maxLen=12):
    """
    returns True if the Key is ECL style

    The maximum accepted lenght for the main part of the Key can be changed
    with maxLen parameter. To be compatible with RSM format 12 is a good number.
    """
    if type(maxLen) is not int:
        raise TypeError("maxLen must be an integer")

    if type(Key) is list or type(Key) is tuple:
        results = [_isECLkey(K) for K in Key]
        return results

    if type(Key) is not str:
        return False
    if '-' in _mainKey(Key):
        return False
    if ' ' in _mainKey(Key):
        return False
    if len(_mainKey(Key)) > maxLen:
        return False

    return True


def _wellFromAttribute(listOfAttributes):
    """
    receives a list of attributes, like:
        [ 'WOPR:W1', 'WOPR:W2', 'WOPR:W3', ... ]
    and return a dictionary of the well names only:
        { 'WOPR:W1':'W1', 'WOPR:W2':'W2', 'WOPR:W3':'W3', ... }

    """
    if type(listOfAttributes) is str:
        listOfAttributes = listOfAttributes.split()
    if type(listOfAttributes) is tuple or type(listOfAttributes) is set:
        listOfAttributes = list(listOfAttributes)
    if type(listOfAttributes) is pandas.core.indexes.base.Index:
        listOfAttributes = list(listOfAttributes)
    if type(listOfAttributes) is not list:
        return {}

    newNames = {each: each.split(':')[-1] for each in listOfAttributes}
    return newNames


def _AttributeFromKeys(listOfKeys):
    """
    receives a list of attributes, like:
        [ 'WOPR:W1', 'WOPR:W2', 'WOPR:W3', ... ]
    and return a dictionary of the attribute names only:
        { 'WOPR:W1':'WOPR', 'WWPR:W1':'WWPR', 'WGPR:W1':'WGPR', ... }

    """
    if type(listOfKeys) is str:
        listOfKeys = listOfKeys.split()
    if type(listOfKeys) is tuple or type(listOfKeys) is set:
        listOfKeys = list(listOfKeys)
    if type(listOfKeys) is pandas.core.indexes.base.Index:
        listOfKeys = list(listOfKeys)
    if type(listOfKeys) is not list:
        return {}

    newNames = {each: each.split(':')[0] for each in listOfKeys}
    return newNames


def tamiz(ListOrTuple):
    """
    receives a list or tuple of strings and other types mixed
    returns a tuple where:
        the item 0 is a list of the strings
        the item 1 is a list of the other types

    list and tuples inside are recursevely processed
    """
    strings = []
    others = []

    if type(ListOrTuple) is str:
        strings += [ListOrTuple]
    elif type(ListOrTuple) is list or type(ListOrTuple) is tuple:
        for each in ListOrTuple:
            if type(each) is list or type(each) is tuple:
                expanded = tamiz(each)
                strings += expanded[0]
                others += expanded[1]
            elif type(each) is str:
                strings += [each]
            else:
                others += [each]
    else:
        others += [ListOrTuple]
    return strings, others


def _meltDF(df, hue='--auto', label='--auto', SimObject=None, FullOutput=False, **kwargs):
    """
        common procedure to melt and rename the dataframe
        """
    if type(df) in [SimSeries, SimDataFrame]:
        SimDF = True
        unitsdict = df.get_units().copy()
        units = lambda col: unitsdict[col] if col in unitsdict else None
        df = df.DF
    else:
        SimDF = False

    for key in ['hue', 'label', 'SimObject', 'FullOutput']:
        kwargs.pop(key, None)
    if 'var_name' in kwargs:
        var_name = kwargs['var_name']
    else:
        var_name = 'SDFvariable'
    if 'value_name' in kwargs:
        value_name = kwargs['value_name']
    else:
        value_name = 'value'

    df = df.melt(var_name=var_name, value_name=value_name, ignore_index=False)
    df['attribute'] = _mainKey(list(df[var_name]), False)
    df['item'] = _itemKey(list(df[var_name]), False)

    if hue == 'main':
        hue = 'attribute'
    if label == 'main':
        label = 'attribute'

    itemLabel = 'item'
    values = value_name  # 'value' before

    if len(set([i[0] for i in _mainKey(list(df[var_name]))])) == 1:
        itemLabel = list(set(_mainKey(list(df[var_name]))))[0][0].upper()
        if itemLabel == 'W':
            itemLabel = 'well'
        elif itemLabel == 'R':
            itemLabel = 'region'
        elif itemLabel == 'G':
            itemLabel = 'group'
        else:
            itemLabel = 'item'

    if _is_SimulationResult(SimObject):
        unitsLabel = ' [' + SimObject.get_plotUnits(_mainKey(list(df[var_name]))[0]) + ']'
    else:
        unitsLabel = ''

    if hue == '--auto' and label == '--auto':
        if len(_mainKey(list(df[var_name]))) == 1 and len(_itemKey(list(df[var_name]))) == 1:
            hue = None
            label = itemLabel
            newLabel = _mainKey(list(df[var_name]))[0] + unitsLabel
            df = df.rename(columns={value_name: newLabel})  # value_name was 'value' before
            values = newLabel
        elif len(_mainKey(list(df[var_name]))) == 1 and len(_itemKey(list(df[var_name]))) > 1:
            hue = None
            label = itemLabel
            newLabel = _mainKey(list(df[var_name]))[0] + unitsLabel
            df = df.rename(columns={value_name: newLabel})  # value_name was 'value' before
            values = newLabel
        elif len(_mainKey(list(df[var_name]))) > 1 and len(_itemKey(list(df[var_name]))) == 1:
            hue = itemLabel  # None
            label = 'attribute'
            # values = _itemKey( list(df[var_name]) )[0]
            # df = df.rename(columns={'value':values})
        elif len(_mainKey(list(df[var_name]))) > len(_itemKey(list(df[var_name]))):
            hue = itemLabel  # 'item'
            label = 'attribute'
        elif len(_mainKey(list(df[var_name]))) < len(_itemKey(list(df[var_name]))):
            hue = 'attribute'
            label = itemLabel  # 'item'
        else:
            hue = 'attribute'
            label = itemLabel  # 'item'

    else:
        if hue == '--auto':
            if len(_mainKey(list(df[var_name]))) == 1 and len(_itemKey(list(df[var_name]))) == 1:
                hue = None
                # newLabel = _mainKey( list(df[var_name]) )[0] + ' [' + self.get_plotUnits(_mainKey( list(df[var_name]) )[0]) + ']'
                # df = df.rename(columns={'value':newLabel})
                # values = newLabel
            elif len(_mainKey(list(df[var_name]))) == 1 and len(_itemKey(list(df[var_name]))) > 1:
                hue = None
                # newLabel = _mainKey( list(df[var_name]) )[0] + ' [' + self.get_plotUnits(_mainKey( list(df[var_name]) )[0]) + ']'
                # df = df.rename(columns={'value':newLabel})
                # values = newLabel
            elif len(_mainKey(list(df[var_name]))) > 1 and len(_itemKey(list(df[var_name]))) == 1:
                hue = None
            elif len(_mainKey(list(df[var_name]))) > len(_itemKey(list(df[var_name]))):
                hue = itemLabel if label != itemLabel else 'attribute'
            elif len(_mainKey(list(df[var_name]))) < len(_itemKey(list(df[var_name]))):
                hue = 'attribute' if label != 'attribute' else itemLabel
            else:
                hue = 'attribute' if label != 'attribute' else itemLabel
        else:
            if hue == 'item':
                hue = itemLabel
            elif hue == 'main':
                hue = 'attribute'

        if label == '--auto':
            if len(_mainKey(list(df[var_name]))) == 1 and len(_itemKey(list(df[var_name]))) == 1:
                label = None
                # newLabel = _mainKey( list(df[var_name]) )[0] + ' [' + self.get_plotUnits(_mainKey( list(df[var_name]) )[0]) + ']'
                # df = df.rename(columns={'value':newLabel})
                # values = newLabel
            elif len(_mainKey(list(df[var_name]))) == 1 and len(_itemKey(list(df[var_name]))) > 1:
                label = itemLabel
                # newLabel = _mainKey( list(df[var_name]) )[0] + ' [' + self.get_plotUnits(_mainKey( list(df[var_name]) )[0]) + ']'
                # df = df.rename(columns={'value':newLabel})
                # values = newLabel
            elif len(_mainKey(list(df[var_name]))) > 1 and len(_itemKey(list(df[var_name]))) == 1:
                label = 'attribute' if hue != 'attribute' else itemLabel
            elif len(_mainKey(list(df[var_name]))) > len(_itemKey(list(df[var_name]))):
                label = 'attribute' if hue != 'attribute' else itemLabel
            elif len(_mainKey(list(df[var_name]))) < len(_itemKey(list(df[var_name]))):
                label = itemLabel if hue != itemLabel else 'attribute'
            else:
                label = itemLabel if hue != itemLabel else 'attribute'
        else:
            if label == 'item':
                label = itemLabel
            elif label == 'main':
                label = 'attribute'

    # generate values for units columns
    if SimDF:
        unitsCol = [units(df[var_name].iloc[i]) for i in range(len(df))]

    if var_name == 'SDFvariable':
        df = df.drop(columns=var_name)
    df = df.rename(columns={'item': itemLabel})

    if FullOutput:
        return hue, label, itemLabel, values, df
    elif SimDF:
        df['units'] = unitsCol
        return df
    else:
        return df


def _pivotDF(df, item=None, index=None, values=None, nameSeparator=':'):
    """
    Procedure to convert a long table to wide table (pivot) integrating the data from
    the item column into the column names.

    Parameters
    ----------
    df : DataFrame
        DESCRIPTION.
    item : str, optional
        The column name that contains the item (i.e. wells) names.
        If not will try to guess from the object columns in the dataframe
    index : str, optional
        The column to be used as index in the pivoted table.
        If None will use the first datetime column or column labeled 'time'.
    values : str or list of str, optional
        The columns to be pivoted.
        The default is all the columns but index and item columns.
    nameSeparator : str, optional
        The string to be used separator in the new concatenated column names.
        New column names will be:
            original_column_name:item_name
        The default is ':'.

    Raises
    ------
    TypeError
        If not able to guess item or index columns.

    Returns
    -------
    newdf : DataFrame
        The pivoted DataFrame.

    """
    resetIndex = False
    if index is None:
        resetIndex = True
        for col in df:
            if 'date' in str(df[col].dtype):
                index = col
                break
    if index is None:
        for col in df:
            if str(col).upper().strip() == 'TIME' and ('int' in str(df[col].dtype) or 'float' in str(df[col].dtype)):
                index = col
                break
    if index is None:
        raise TypeError("Not able to find a column to be used as index, please provide 'index' parameter.")
    else:
        print(" >>> Identified column '" + str(index) + "' as index to pivot. <<<")
        newindex = pandas.Index(numpy.sort(df[index].squeeze().unique()))
    if item is None:
        candidate = None
        for col in df:
            if 'object' == str(df[col].dtype):
                if candidate is None:
                    candidate = (col, len(df[col].squeeze().unique()))
                elif len(df[col].squeeze().unique()) < candidate[1]:
                    candidate = (col, len(df[col].squeeze().unique()))
        if candidate is not None:
            item = candidate[0]
            print(" >>> Identified column '" + str(item) + "' as item to pivot. <<<")
        else:
            raise TypeError("Not able to find a column to be used as item, please provide 'item' parameter.")

    names = {col[0] if type(col) is tuple else col: col for col in df.columns}
    if item not in names:
        names[item] = item
    if index not in names:
        names[index] = index
    if values is None:
        values = [cols for cols in df.columns if cols != names[item]] if index is None else [cols for cols in df.columns
                                                                                             if cols != names[
                                                                                                 item] and cols !=
                                                                                             names[index]]

    newdf = pandas.DataFrame(index=newindex)
    for ite in df[item].squeeze().unique():
        for col in values:
            newdf[(str(col[0]) + ':' + str(ite),) + col[1:] if type(col) is tuple else str(col) + ':' + str(ite)] = \
            df[df[names[item]] == ite].set_index(names[index])[col]

    if resetIndex:
        newdf = newdf.reset_index()
    return newdf
