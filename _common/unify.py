# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 18:55:24 2022

@author: MCARAYA
"""

__version__ = '0.1.1'
__release__ = 220127
__author__ = 'Martin Carlos Araya <martinaraya@gmail.com>'
__all__ = ['unify']

import os
import shutil
import glob
from .._common.inout import _extension
from .._Classes.Errors import OverwrittingError


def unify(filepath,overwrite=None,min_input=None):
    """
    Converts multioutput summary files from eclipse .S0001 to unifies output file .UNSMRY

    Parameters
    ----------
    filepath : str
        the path multioutput files to unify
    overwrite : None or bool, optional
        To set behaviour when .UNSMRY file already exists:
            If None will skip these files and return None.
            If False will raise OverwrittingError.
            If True will overwrite the existing file.
            The default is None.
    min_input : int or None, optional
        If int provided, will raise ValueError if there are not enogth input files.

    Raises
    ------
    OverwrittingError
        when the output file already exists.

    Returns
    -------
    None.

    """

    pathS = filepath if _extension(filepath)[0] == '' else _extension(filepath)[2] + _extension(filepath)[1]
    listS = glob.glob(pathS+'.S*')
    listS = [ S for S in listS if _extension(S)[0][2:].isdigit() ]

    if len(listS) == 0:
        print('No multi-output files found.')
        return None

    min_input = -1 if min_input is None else int(min_input)
    if len(listS) < min_input:
        raise ValueError('not enougth input files')

    listS.sort()

    unsmry_path = _extension(filepath)[2] + _extension(filepath)[1] + '.UNSMRY'

    if os.path.isfile(unsmry_path) and overwrite is None:
        print('The .UNSMRY file aready exists:\n ' + str(unsmry_path) + '.\n Set the second argument to True to overwrite.')
        return None
    elif os.path.isfile(unsmry_path) and overwrite is False:
        raise OverwrittingError('The .UNSMRY file aready exists:\n ' + str(unsmry_path) + '.\n Set the second argument to True to overwrite.')
    elif os.path.isfile(unsmry_path) and overwrite is True:
        pass

    unsmry=open(unsmry_path,"wb")
    for S in listS:
        multi=open(S,"rb")
        shutil.copyfileobj(multi, unsmry)
        multi.close()
    unsmry.close()

    print('-> Created: ' + str(unsmry_path))
