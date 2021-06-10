# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import sys
import inspect

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2


_TComp = TypeVar('_TComp')


class ComponentIter(Generic[_TComp]):

    @property
    def miter(self):
        return self._miter

    @property
    def mobject(self):
        # type: () -> _om2.MObject
        return self._miter.currentItem()

    def __init__(self, miter, comp):
        self._miter = miter
        self._comp = comp  # 使う機会はないけど、ループの最中にcompのスコープが切れないように手許で抱えておく
        self.__is_first = True

    def __getattr__(self, item):
        # type: (str) -> Any
        return getattr(self._miter, item)

    def __iter__(self):
        # type: () -> _TComp
        return self

    def next(self):
        # type: () -> _TComp
        return self.__next__()

    def __next__(self):
        # type: () -> _TComp
        if self.__is_first:
            self.__is_first = False
            return self

        self._next()

        if self._miter.isDone():
            raise StopIteration()

        return self

    def _next(self):
        # type: () -> NoReturn
        self._miter.next()


class ComponentFactory(object):

    _cls_dict = {}  # type: Dict[_om2.MFn, type]
    _default_cls = None  # type: type

    @staticmethod
    def register(module_name):
        # type: (str) -> NoReturn
        module = sys.modules[module_name]
        for name, symbol in module.__dict__.items():
            if not inspect.isclass(symbol) or not hasattr(symbol, '_comp_type'):
                continue
            comp_type = symbol._comp_type
            ComponentFactory._cls_dict[comp_type] = symbol

    @staticmethod
    def register_default(cls):
        # type: (type) -> NoReturn
        ComponentFactory._default_cls = cls

    @staticmethod
    def create(comp_type, mdagpath, mobject):
        # type: (_om2.MFn, _om2.MDagPath, _om2.MObject) -> object
        if comp_type not in ComponentFactory._cls_dict:
            return None

        cls = ComponentFactory._cls_dict[comp_type]
        return cls(mobject, mdagpath)

    @staticmethod
    def create_default(mdagpath, mobject):
        # type: (_om2.MDagPath, _om2.MObject) -> object
        cls = ComponentFactory._default_cls
        return cls(mdagpath, mobject)

