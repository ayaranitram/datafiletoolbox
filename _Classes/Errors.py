"""
Created on Wed May 13 15:14:35 2020

@author: MCARAYA
"""

__version__ = 0.0
__release = 210308
__all__ = []


class OverwrittingError(Exception):
    pass


class UndefinedDateFormat(Exception):
    pass


# PrototypeError class to recognize the class from crwap
from cwrap import PrototypeError


class MissingDependence(Exception):
    pass