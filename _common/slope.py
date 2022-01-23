# -*- coding: utf-8 -*-
"""
Created on Sun Jan 23 22:38:16 2022

@author: MCARAYA
"""

__version__ = '0.1.2'
__release__ = 220123
__all__ = ['slope']

import numpy as np
import pandas as pd


def slope(df,x=None, y=None, window=None, slope=True, intercept=False):
    """
    Calculates the slope of column Y vs column X or vs index if 'x' is None

    Parameters
    ----------
    df : DataFrame or SimDataFrame
        The DataFrame to work with.
    x : str, optional
        The name of the column to be used as X.
        If None, the index of the DataFrame will be used as X.
        The default is None.
    y : str, optional
        The name of the column to be used as Y.
        If None, the first argument will be considered as Y (not as X).
        The default is None.
    window : int, float or str, optional
        The half-size of the rolling window to calculate the slope.
        if None : the slope will be calculated from the entire dataset.
        if int : window rows before and after of each row will be used to calculate the slope
        if float : the window size will be variable, with window values of X arround each row's X. Not compatible with datetime columns
        if str : the window string will be used as timedelta arround the datetime X
        The default is None.
    slope : bool, optional
        Set it True to return the slope of the linear fit. The default is True.
    intercept : bool, optional
        Set it True to return the intersect of the linear fit. The default is False.
    if both slope and intercept are True, a tuple of both results will be returned

    Returns
    -------
    numpy array
        The array containing the desired output.

    """
    if x is not None and y is None:
        x, y = None, x
    elif x is not None and window is None and y is not None and y not in df.columns:
            x, y, window = None, x, y

    if window is None:  # calculate the slope for the entire dataset
        if x is None:
            if isinstance(df.index,pd.DatetimeIndex):
                s, i = np.polyfit( np.cumsum(np.array([0]+list(np.diff(df.index).astype('timedelta64[s]').astype(float)/60/60/24))), df[y].values, 1, full=False)
            else:
                s, i = np.polyfit( df.index, df[y].values, 1, full=False)
        else:
            if isinstance(df[x],pd.DatetimeIndex):
                s, i = np.polyfit( np.cumsum(np.array([0]+list(np.diff(df[x]).astype('timedelta64[s]').astype(float)/60/60/24))), df[y].values, 1, full=False)
            else:
                s, i = np.polyfit( df[x], df[y].values, 1, full=False)

        # return the results
        if intercept and slope:
            return s, i
        elif intercept:
            return i
        elif slope:
            return s
        else:
            return None

    if type(window) is int:  # calculate slope every N (window) rows
        if x is None:  # use the index as X
            if isinstance(df.index, pd.DatetimeIndex):
                s = [ np.polyfit(np.cumsum(np.array([ (np.diff(df.index[[0,max(0,i-window)]]).astype('timedelta64[s]').astype(float)/60/60/24)[0] ] +
                                                    list(np.diff(df.iloc[max(0,i-window):min(i+window,len(df))].index).astype('timedelta64[s]').astype(float)/60/60/24)
                                                    )
                                           ),
                                 df.iloc[max(0,i-window):min(i+window,len(df))][y].values,
                                 1, full=False) for i in range(len(df)) ]
            else:
                s = [ np.polyfit(df.iloc[max(0,i-window):min(i+window,len(df))].index,
                                 df.iloc[max(0,i-window):min(i+window,len(df))][y].values,
                                 1, full=False) for i in range(len(df)) ]
        else:
            if isinstance(df[x], pd.DatetimeIndex):
                s = [ np.polyfit(np.cumsum(np.array([ (np.diff(df.iloc[[0,max(0,i-window)]][x].values).astype('timedelta64[s]').astype(float)/60/60/24)[0] ] +
                                                    list(np.diff(df.iloc[max(0,i-window):min(i+window,len(df))][x].values).astype('timedelta64[s]').astype(float)/60/60/24)
                                                    )
                                           ),
                                 df.iloc[max(0,i-window):min(i+window,len(df))][y].values,
                                 1, full=False) for i in range(len(df)) ]
            else:
                s = [ np.polyfit(df.iloc[max(0,i-window):min(i+window,len(df))][x].values,
                                 df.iloc[max(0,i-window):min(i+window,len(df))][y].values,
                                 1, full=False) for i in range(len(df)) ]

    elif type(window) is str:  # window is a str representing a timedelta
        if ((x is None and isinstance(df.index,pd.DatetimeIndex)) or (x is not None and 'datetime' in str(df[x].dtype))):
            window = pd.to_timedelta(window)
        else:
            raise ValueError('string window, representing timedelta, only works with datetime index or X column.')

        if x is None:  # use the index as X
            s = [ np.polyfit(np.diff(np.array([df.index[0]] + list(df[(df.index>=(df.index[i]-window)) & (df.index<=(df.index[i]+window))].index))).astype('timedelta64[s]').astype(float)/60/60/24,
                             df[(df.index>=(df.index[i]-window)) & (df.index<=(df.index[i]+window))][y].values,
                             1, full=False) for i in range(len(df)) ]
        else:
            s = [ np.polyfit(np.diff(np.array([df[x].iloc[0]] + list(df[(df[x]>=(df[x].iloc[i]-window)) & (df[x]<=(df[x].iloc[i]+window))][x]))).astype('timedelta64[s]').astype(float)/60/60/24,
                             df[(df[x]>=(df[x].iloc[i]-window)) & (df[x]<=(df[x].iloc[i]+window))][y].values,
                             1, full=False) for i in range(len(df)) ]

    elif type(window) is float:  # windows is a number that should be compared to X
        if x is None:  # use the index as X
            # np.diff(df.index).astype('timedelta64[s]').astype(float)/60/60/24
            s = [ np.polyfit(df[(df.index>=(df.index[i]-window)) & (df.index<=(df.index[i]+window))].index,
                             df[(df.index>=(df.index[i]-window)) & (df.index<=(df.index[i]+window))][y].values,
                             1, full=False) for i in range(len(df)) ]
        else:
            s = [ np.polyfit(df[(df[x]>=(df[x].iloc[i]-window)) & (df[x]<=(df[x].iloc[i]+window))][x].values,
                             df[(df[x]>=(df[x].iloc[i]-window)) & (df[x]<=(df[x].iloc[i]+window))][y].values,
                             1, full=False) for i in range(len(df)) ]
    else:
        raise NotImplemented('window must be int, float, str or None.')

    s = np.array(s)
    s, i = s[:,0], s[:,1]

    if intercept and slope:
        return s, i
    elif intercept:
        return i
    elif slope:
        return s
    else:
        return None
