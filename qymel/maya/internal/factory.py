# coding: utf-8
from typing import *
import sys
import inspect

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2


class NodeFactory(object):

    _cls_dict = {}  # type: Dict[str, type]
    _default_cls_dict = {}  # type: Dict[str, type]
    _dynamic_cls_cache = {}  # type: Dict[str, type]

    @staticmethod
    def register(module_name):
        # type: (str) -> NoReturn
        module = sys.modules[module_name]
        for name, symbol in module.__dict__.items():
            if not inspect.isclass(symbol) or not hasattr(symbol, '_mel_type'):
                continue
            mel_type = getattr(symbol, '_mel_type')
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
        # type: (_om2.MFnDependencyNode, Optional[_om2.MDagPath]) -> object
        mobject = mfn.object()  # type: _om2.MObject
        cls = NodeFactory.__create_dynamic_node_type(mfn, mobject, mdagpath)

        if mobject.hasFn(_om2.MFn.kDagNode) and mdagpath is not None:
            return cls(mdagpath)

        return cls(mobject)

    @staticmethod
    def __create_dynamic_node_type(mfn, mobject, mdagpath=None):
        # type: (_om2.MFnDependencyNode, _om2.MObject, Optional[_om2.MDagPath]) -> type
        type_name = mfn.typeName
        cls = NodeFactory._dynamic_cls_cache.get(type_name, None)
        if cls is not None:
            return cls

        if mdagpath:
            node_path = mdagpath.fullPathName()
        else:
            node_path = mfn.absoluteName()

        # 定義済みクラスの中で一番近いクラスを継承して、新しいクラスを動的につくる
        base_cls = None

        base_cls_name_candidates = _cmds.nodeType(node_path, inherited=True)
        for base_cls_name in reversed(base_cls_name_candidates):
            base_cls = NodeFactory._dynamic_cls_cache.get(base_cls_name, None)
            if base_cls is None:
                base_cls = NodeFactory._cls_dict.get(base_cls_name, None)
            if base_cls is not None:
                break

        if not base_cls:
            if mobject.hasFn(_om2.MFn.kDagNode):
                base_cls = NodeFactory._default_cls_dict['dag_node']
            else:
                base_cls = NodeFactory._default_cls_dict['node']

        cls_name = type_name[0].upper() + type_name[1:]
        cls = type(cls_name, (base_cls,), {})
        NodeFactory._dynamic_cls_cache[type_name] = cls

        return cls


class PlugFactory(object):

    _cls = None  # type: type

    @staticmethod
    def register(cls):
        # type: (type) -> NoReturn
        PlugFactory._cls = cls

    @staticmethod
    def create(mplug):
        # type: (_om2.MPlug) -> object
        cls = PlugFactory._cls
        return cls(mplug)


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

