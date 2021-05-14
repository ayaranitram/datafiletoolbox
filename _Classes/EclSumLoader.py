# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 08:56:44 2021

@author: martin
"""

__version__ = 0.11
__release__ = 210315
__all__ = ['EclSumLoader']

from .._Classes.Errors import PrototypeError, MissingDependence
from .._common.inout import _extension
import os
from warnings import warn
from .._common.sharedVariables import _loadingECLfile

class _EclSumLoader(object):
    _EclSum = None
    _AlreadyLoaded = {}
    
    def __init__(self):
        self._EclSum = None
        if _EclSumLoader._EclSum:
            self._EclSum = _EclSumLoader._EclSum
        else:
            try :
                # try to use libecl instalation from pypi.org
                from ecl.summary import EclSum
                from ecl.version import version as libecl_version
                print('\n using libecl version ' + str(libecl_version))
                self._EclSum = EclSum
                _EclSumLoader._EclSum = EclSum
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
                    _EclSumLoader._EclSum = EclSum
                except ModuleNotFoundError :
                    print("\n ERROR: missing 'cwrap' module, please intall it using pip command:\n           pip install cwrap\n\n       or upgrade:\n\n          pip install cwrap --upgrade\n        or intall libecl using pip command:\n           pip install libecl\n\n       or upgrade:\n\n          pip install libecl --upgrade" )
                    raise ModuleNotFoundError()
                except PrototypeError :
                    # the class is already registered in cwrap from a previos load, no need to register again
                    warn("PrototypeError: Type: 'ecl_type_enum' already registered!")
                    # return self._EclSum
                except:
                    if _loadingECLfile[0] :
                        raise MissingDependence("EclSum failed to load")
                    else:
                        print("WARNING: EclSum failed to load, you will not be able to load results in eclipse binary format.")
            except:
                if _loadingECLfile[0]:
                    raise MissingDependence("EclSum failed to load")
                else:
                    print("WARNING: EclSum failed to load, you will not be able to load results in eclipse binary format.")

    def __call__(self,SummaryFilePath,reload=False,unload=False) :
        reload = bool(reload)
        unload = bool(unload)
        if unload:
            if SummaryFilePath in _EclSumLoader._AlreadyLoaded:
                _EclSumLoader._AlreadyLoaded[SummaryFilePath] = None
                del _EclSumLoader._AlreadyLoaded[SummaryFilePath]
                print("\n<EclSumLoader> unloaded file and removed data from memory.")
            else:
                print("\n<EclSumLoader> file was not loaded.")
        if SummaryFilePath is None:
            return None
        if not os.path.isfile(SummaryFilePath):
            raise FileNotFoundError(SummaryFilePath)
        elif SummaryFilePath in _EclSumLoader._AlreadyLoaded and reload is False:
            print("\n<EclSumLoader> file already loaded.\n               To reload please set parameter reload=True\n")
            return _EclSumLoader._AlreadyLoaded[SummaryFilePath]
        if self._EclSum:
            _EclSumLoader._AlreadyLoaded[SummaryFilePath] = self._EclSum(SummaryFilePath)
            return _EclSumLoader._AlreadyLoaded[SummaryFilePath]  # self._EclSum(SummaryFilePath)
        else :
            raise MissingDependence("failed to load "+str(SummaryFilePath))

EclSumLoader = _EclSumLoader
