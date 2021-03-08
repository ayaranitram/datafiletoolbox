# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 08:56:44 2021

@author: martin
"""

__version__ = 0.1
__release__ = 210308

from .._Classes.Errors import PrototypeError, MissingDependence
from .._common.inout import _extension
import os
from warnings import warn


class EclSumLoader():
    _EclSum = None
    def __init__(self):
        self._EclSum = None
        if EclSumLoader._EclSum:
            self._EclSum = EclSumLoader._EclSum
        else:
            try :
                # try to use libecl instalation from pypi.org
                from ecl.summary import EclSum
                from ecl.version import version as libecl_version
                print('\n using libecl version ' + str(libecl_version))
                self._EclSum = EclSum
                EclSumLoader._EclSum = EclSum
            except ModuleNotFoundError:
                # try to use my compiled version of libecl from https://github.com/equinor/libecl
                eclPath = _extension(str(os.getcwd()))[3] + '/datafiletoolbox/equinor/libecl/win10/lib/python'
                os.environ['PYTHONPATH'] = eclPath + ';' + os.environ['PYTHONPATH']
                eclPath = eclPath + ';' + _extension(str(os.getcwd()))[3] + '/datafiletoolbox/equinor/libecl/win10/lib'
                eclPath = eclPath + ';' + _extension(str(os.getcwd()))[3] + '/datafiletoolbox/equinor/libecl/win10/bin'
                os.environ['PATH'] = eclPath + ';' + os.environ['PATH']
                
                #from datafiletoolbox.equinor.libecl.win10.lib.python import ecl
                try :
                    from datafiletoolbox.equinor.libecl.win10.lib.python.ecl.summary import EclSum
                    print('\n using ecl from https://github.com/equinor/libecl compiled for Windows10')
                    self._EclSum = EclSum
                    EclSumLoader._EclSum = EclSum
                except ModuleNotFoundError :
                    print("\n ERROR: missing 'cwrap', please intall it using pip command:\n           pip install crwap\n\n       or upgrade:\n\n          pip install crwap --upgrade\n        or intall libecl using pip command:\n           pip install libecl\n\n       or upgrade:\n\n          pip install libecl --upgrade" )
                    raise ModuleNotFoundError()
                except PrototypeError :
                    # the class is already registered in crwap from a previos load, no need to register again
                    warn("PrototypeError: Type: 'ecl_type_enum' already registered!")
                    # return self._EclSum
                except:
                    raise MissingDependence("EclSum failed to load")
    

    def __call__(self,SummaryFilePath) :
        if self._EclSum:
            return self._EclSum(SummaryFilePath)
        else :
            raise MissingDependence("failed to load "+str(SummaryFilePath))
