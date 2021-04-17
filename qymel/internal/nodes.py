# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import sys
import inspect

import maya.api.OpenMaya as _om2


class NodeFactory(object):

    _cls_dict = {}  # Dict[str, type]
    _default_cls_dict = {}  # Dict[str, type]

    @staticmethod
    def register(module_name):
        # type: (str) -> NoReturn
        module = sys.modules[module_name]
        for name, symbol in module.__dict__.items():
            if not inspect.isclass(symbol) or not hasattr(symbol, '_mel_type'):
                continue
            mel_type = symbol._mel_type
            if mel_type is None or len(mel_type) == 0:
                continue
            NodeFactory._cls_dict[mel_type] = symbol

    @staticmethod
    def register_default(node_cls, dag_node_cls):
        # type: (type, type) -> NoReturn
        NodeFactory._default_cls_dict['node'] = node_cls
        NodeFactory._default_cls_dict['dag_node'] = dag_node_cls

    @staticmethod
    def create(mel_type, mobject, mdagpath=None):
        # type: (str, _om2.MObject, _om2.MDagPath) -> Any
        if mel_type not in NodeFactory._cls_dict:
            return None

        cls = NodeFactory._cls_dict[mel_type]
        if mdagpath is not None:
            return cls(mdagpath)
        return cls(mobject)

    @staticmethod
    def create_default(mobject, mdagpath=None):
        # type: (_om2.MObject, _om2.MDagPath) -> object
        cls = NodeFactory._default_cls_dict['node']
        if mdagpath is not None:
            # TODO: 例外処理を使いたくない
            try:
                return cls(mdagpath)
            except:
                pass
        return cls(mobject)
