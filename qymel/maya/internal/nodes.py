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
    _dynamic_cls_cache = {}  # Dict[str, type]

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
    def create_default(mfn, mdagpath=None):
        # type: (_om2.MFnDependencyNode, _om2.MDagPath) -> object
        mobject = mfn.object()  # type: _om2.MObject
        cls = NodeFactory.__create_dynamic_node_type(mfn, mobject)

        if mobject.hasFn(_om2.MFn.kDagNode) and mdagpath is not None:
            return cls(mdagpath)

        return cls(mobject)

    @staticmethod
    def __create_dynamic_node_type(mfn, mobject):
        # type: (_om2.MFnDependencyNode, _om2.MObject) -> type
        type_name = mfn.typeName
        cls = NodeFactory._dynamic_cls_cache.get(type_name, None)
        if cls is not None:
            return cls

        if mobject.hasFn(_om2.MFn.kDagNode):
            base_cls = NodeFactory._default_cls_dict['dag_node']
        else:
            base_cls = NodeFactory._default_cls_dict['node']

        cls_name = type_name[0].upper() + type_name[1:]
        cls = type(cls_name, (base_cls,), {})
        NodeFactory._dynamic_cls_cache[type_name] = cls

        return cls