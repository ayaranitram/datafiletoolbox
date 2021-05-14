"""
Created on Wed May 13 15:14:35 2020

@author: MCARAYA
"""

__version__ = 0.0
__release = 210514
__all__ = []


class OverwrittingError(Exception):
    pass


class UndefinedDateFormat(Exception):
    pass


# PrototypeError class to recognize the class from cwrap
try :
    from cwrap import PrototypeError
except ModuleNotFoundError :
    print("\n WARNING: missing 'cwrap' module, will be able to load eclipse style simulation outputs.\n         Please intall it using pip command:\n           pip install cwrap\n\n       or upgrade:\n\n          pip install cwrap --upgrade\n        or intall libecl using pip command:\n           pip install libecl\n\n       or upgrade:\n\n          pip install libecl --upgrade" )


class MissingDependence(Exception):
    pass


class InvalidKeyError(Exception):
    pass