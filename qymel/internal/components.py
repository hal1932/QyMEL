# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import sys
import inspect


class ComponentFactory(object):

    _cls_dict = {}  # type: Dict[str, type]
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
        # type: (om2.MFn, om2.MDagPath, om2.MObject) -> object
        if comp_type not in ComponentFactory._cls_dict:
            return None

        cls = ComponentFactory._cls_dict[comp_type]
        return cls(mdagpath, mobject)

    @staticmethod
    def create_default(mdagpath, mobject):
        # type: (om2.MDagPath, om2.MObject) -> object
        cls = ComponentFactory._default_cls
        return cls(mdagpath, mobject)

