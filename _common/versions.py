# -*- coding: utf-8 -*-
"""
Created on Sat May 16 14: 44: 06 2020

@author: martin
"""

__version__ = '0.0.0'
__release__ = 210225

import pprint


def versions(modules):
    if modules is not list:
        modules = [modules]
    vers = {}
    for module in modules:
        vers[module] = [module.version.split('.')]
    pprint(vers)
