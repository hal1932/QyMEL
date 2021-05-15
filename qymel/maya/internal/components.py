# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import sys
import inspect

import maya.api.OpenMaya as _om2


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

