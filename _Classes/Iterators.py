#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 18 05:32:42 2020

@author: martin
"""

__version__ = '0.1.20-10-18'
__all__ = ['Alternate']

class Alternate(object) :
    def __init__( self,iterable=(1,-1) , **kwargs ) :
        if type(iterable) is int or type(iterable) is float :
            iterable = (iterable,)
        if type(iterable) is not tuple :
            try :
                iterable = tuple(iterable)
            except :
                raise TypeError(" 'iterable' must be an iterable object, like a tuple or list.")
        if len(iterable) == 0 :
            raise ValueError (" 'iterable must not be empty.")
        self.iterable = iterable
        self.i = -1
        self.loops = -1
        self.reverse = False
        if 'loops' in kwargs :
            if type(kwargs['loops']) is not int or kwargs['loops'] < 0 : raise TypeError(" 'loops' must be a positive integer.")
            self.loops = kwargs['loops']
        if 'reverse' in kwargs :
            if type(kwargs['reverse']) is not bool : raise TypeError(" 'reverser' must be True or False.")
            self.reverse = kwargs['reverse']
        if self.reverse :
            self.iterable = tuple( list(self.iterable) + list(self.iterable)[-2:0:-1] )
        self.limit = len(self.iterable)-1
        
    def __repr__(self) :
        return str(next(self))
    @property
    def start(self) :
        self.i = -1
    @property
    def stop(self) :        
        self.i = -2
    @property
    def next(self) :
        if self.loops == 0 : return None
        i = 0 if self.i == self.limit else self.i+1
        return self.iterable[i]
    @property
    def prev(self) :
        i = self.i-1
        return self.iterable[i]
    @property
    def now(self) :
        return self.iterable[self.i]
    def __getitem__(self,index) :
        if type(index) is not int : raise TypeError("'index' must be an integer.")
        return self.iterable[ index % len(self.iterable) ]
    def __next__(self) :
        if self.i >= -1 and self.loops != 0 :
            if self.i+1 == self.limit : self.loops -= 1
            self.i = 0 if self.i == self.limit else self.i+1
            return self.iterable[self.i]
        else :
            raise StopIteration
    def __iter__(self) :
        return self
    def __add__(self,other) :
        return next(self) + other
    def __radd__(self,other) :
        return next(self) + other
    def __sub__(self,other) :
        return next(self) - other
    def __rsub__(self,other) :
        return other - next(self)
    def __mul__(self,other) :
        return next(self) * other
    def __rmul__(self,other) :
        return next(self) * other
    def __mod__(self,other) :
        return next(self) % other
    def __rmod__(self,other) :
        return other % next(self)
    def __truediv____(self,other) :
        return next(self) / other
    def __rtruediv____(self,other) :
        return other / next(self)
    def __floordiv__(self,other) :
        return next(self) // other
    def __rfloordiv__(self,other) :
        return other // next(self)
