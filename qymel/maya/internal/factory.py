# coding: utf-8
from __future__ import annotations
from typing import *
import sys
import inspect

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2

from .types import *


class NodeFactory(object):

    _cls_dict: Dict[str, Type[TDependNode]] = {}
    _default_cls_dict: Dict[str, Type[TDependNode]] = {}
    _dynamic_cls_cache: Dict[str, Type[TDependNode]] = {}

    @staticmethod
    def register(module_name: str) -> None:
        module = sys.modules[module_name]
        for name, symbol in module.__dict__.items():
            if not inspect.isclass(symbol) or not hasattr(symbol, '_mel_type'):
                continue
            mel_type = getattr(symbol, '_mel_type')
            if mel_type is None or len(mel_type) == 0:
                continue
            NodeFactory._cls_dict[mel_type] = symbol

    @staticmethod
    def register_default(node_cls: Type[TDependNode], dag_node_cls: Type[TDependNode]) -> None:
        NodeFactory._default_cls_dict['node'] = node_cls
        NodeFactory._default_cls_dict['dag_node'] = dag_node_cls

    @staticmethod
    def create(mel_type: str, mobject: _om2.MObject, mdagpath: Optional[_om2.MDagPath] = None) -> Optional[TDependNode]:
        if mel_type not in NodeFactory._cls_dict:
            return None

        cls = NodeFactory._cls_dict[mel_type]
        if mdagpath is not None:
            return cls(mdagpath)
        return cls(mobject)

    @staticmethod
    def create_default(mfn: _om2.MFnDependencyNode, mdagpath: Optional[_om2.MDagPath] = None) -> TDependNode:
        mobject = mfn.object()
        cls = NodeFactory.__create_dynamic_node_type(mfn, mobject, mdagpath)

        if mobject.hasFn(_om2.MFn.kDagNode) and mdagpath is not None:
            return cls(mdagpath)

        return cls(mobject)

    @staticmethod
    def __create_dynamic_node_type(
            mfn: _om2.MFnDependencyNode,
            mobject: _om2.MObject,
            mdagpath: Optional[_om2.MDagPath] = None
    ) -> Type[TDependNode]:
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

    _cls: Optional[Type[TPlug]] = None

    @staticmethod
    def register(cls: Type[TPlug]) -> None:
        PlugFactory._cls = cls

    @staticmethod
    def create(mplug: _om2.MPlug) -> TPlug:
        return PlugFactory._cls(mplug)


class ComponentFactory(object):

    _cls_dict: Dict[_om2.MFn, Type[TComponent]] = {}
    _default_cls: Optional[Type[TComponent]] = None

    @staticmethod
    def register(module_name: str) -> None:
        module = sys.modules[module_name]
        for name, symbol in module.__dict__.items():
            if not inspect.isclass(symbol) or not hasattr(symbol, '_comp_type'):
                continue
            comp_type = symbol._comp_type
            ComponentFactory._cls_dict[comp_type] = symbol

    @staticmethod
    def register_default(cls: Type[TComponent]) -> None:
        ComponentFactory._default_cls = cls

    @staticmethod
    def create(comp_type: _om2.MFn, mdagpath: _om2.MDagPath, mobject: _om2.MObject) -> Optional[TComponent]:
        if comp_type not in ComponentFactory._cls_dict:
            return None

        cls = ComponentFactory._cls_dict[comp_type]
        return cls(mobject, mdagpath)

    @staticmethod
    def create_default(mdagpath: _om2.MDagPath, mobject: _om2.MObject) -> TComponent:
        cls = ComponentFactory._default_cls
        return cls(mdagpath, mobject)

