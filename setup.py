# -*- coding: utf-8 -*-
"""
Created on Sun Jul 31 22:21:57 2022

@author: martin
"""

from setuptools import setup, find_packages

setup(
      author="Martin Carlos Araya",
      description="A set of classes and utilities to read different simulation output files, text files and excel file in certain formats.",
      name="datafiletoolbox",
      version='0.52.16',
      packages=find_packages(include=['datafiletoolbox, datafiletoolbox.*']),
      install_requires=['numpy', 'pandas', 'matplotlib'],
      python_requires='>=3.5.0'
      )
