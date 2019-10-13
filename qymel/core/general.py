# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.cmds as cmds
import maya.api.OpenMaya as om2

from qymel.internal.graphs import _ls, _eval, _eval_node, _eval_plug, _eval_component
from qymel.internal.plugs import _PlugFactory, _plug_get_impl
from qymel.internal.components import _ComponentFactory


def ls(*args, **kwargs):
    # type: (Any, Any) -> Any
    return _ls(*args, **kwargs)


def eval(obj_name):
    # type: (Union[str, Iterable[str]]) -> Any
    tmp_mfn_comp = om2.MFnComponent()
    tmp_mfn_node = om2.MFnDependencyNode()
    if isinstance(obj_name, (str, unicode)):
        return _eval(obj_name, tmp_mfn_comp, tmp_mfn_node)
    else:
        return [_eval(name, tmp_mfn_comp, tmp_mfn_node) for name in obj_name]


def eval_node(node_name):
    # type: (str) -> Any
    tmp_mfn = om2.MFnDependencyNode()
    return _eval_node(node_name, tmp_mfn)


def eval_plug(plug_name):
    # type: (str) -> Plug
    return _eval_plug(plug_name)


def eval_component(comp_name):
    # type: (str) -> Component
    tmp_mfn = om2.MFnComponent()
    return _eval_component(comp_name, tmp_mfn)


class MayaObject(object):

    @property
    def mobject(self):
        # type: () -> om2.MObject
        return self._mobj_handle.object()

    @property
    def mobject_handle(self):
        # type: () -> om2.MObjectHandle
        return self._mobj_handle

    @property
    def is_null_object(self):
        # type: () -> bool
        return self._mobj_handle.object().isNull()

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        if mobj is not None:
            self._mobj_handle = om2.MObjectHandle(mobj)
        else:
            self._mobj_handle = None

    def __eq__(self, other):
        # type: (object) -> bool
        if other is None:
            return False
        if not isinstance(other, MayaObject):
            return False
        return self._mobj_handle.hashCode() == other._mobj_handle.hashCode()

    def __hash__(self):
        # type: () -> long
        return self._mobj_handle.hashCode()

    def __str__(self):
        # type: () -> str
        return '{} {}'.format(self.__class__, self.mobject)

    def has_fn(self, mfn_type):
        # type: (int) -> bool
        return self.mobject.hasFn(mfn_type)


class Plug(object):

    @property
    def mplug(self):
        # type: () -> om2.MPlug
        return self._mplug

    @property
    def attribute_mobject(self):
        # type: () -> om2.MObject
        return self._mplug.attribute()

    @property
    def is_null_object(self):
        # type: () -> bool
        return self._mplug.isNull

    @property
    def name(self):
        # type: () -> str
        return self._mplug.name()

    @property
    def partial_name(self):
        # type: () -> str
        return self._mplug.partialName()

    @property
    def api_type(self):
        # type: () -> int
        self._mplug.attribute().apiType()

    @property
    def is_source(self):
        # type: () -> bool
        return self._mplug.isSource

    @property
    def is_destination(self):
        # type: () -> bool
        return self._mplug.isDestination

    @property
    def is_array(self):
        # type: () -> bool
        return self._mplug.isArray

    @property
    def is_compound(self):
        # type: () -> bool
        return self._mplug.isCompound

    @property
    def is_locked(self):
        # type: () -> bool
        return self._mplug.isLocked

    @property
    def is_networked(self):
        # type: () -> bool
        return self._mplug.isNetworked

    def __init__(self, mplug):
        # type: (om2.MPlug) -> NoReturn
        self._mplug = mplug
        self._mfn = None

    def __str__(self):
        # type: () -> str
        return '{} {}'.format(self.__class__, self.name)

    def __getitem__(self, item):
        # type: (int) -> Plug
        mplug = self._mplug

        if not mplug.isArray:
            raise RuntimeError('{} is not array'.format(self.name))

        return Plug(mplug.elementByLogicalIndex(item))

    def __getattr__(self, item):
        # type: (str) -> Plug
        mplug = self._mplug

        if not mplug.isCompound:
            raise RuntimeError('{} is not compound'.format(self.name))

        attr_mobj = om2.MFnDependencyNode(mplug.node()).attribute(item)
        child_mplug = mplug.child(attr_mobj)
        return Plug(child_mplug)

    def get(self):
        # type: () -> Any
        mplug = self._mplug

        if mplug.isNetworked:
            raise RuntimeError('{} is networked'.format(self.name))

        return _plug_get_impl(mplug)

    def get_attr(self, **kwargs):
        # type: (Any, Any) -> Any
        return cmds.getAttr(self.name, **kwargs)

    def set_attr(self, *args, **kwargs):
        # type: (Any, Any) -> Any
        return cmds.setAttr(self.name, *args, **kwargs)

    def connect(self, dest_plug, **kwargs):
        # type: (Plug, Any) -> NoReturn
        cmds.connectAttr(self.name, dest_plug.name, **kwargs)

    def disconnect(self, dest_plug, **kwargs):
        # type: (Plug, Any) -> NoReturn
        cmds.disconnectAttr(self.name, dest_plug.name, **kwargs)

    def source(self):
        # type: () -> Plug
        return Plug(self._mplug.source())

    def destinations(self):
        # type: () -> List[Plug]
        return [Plug(mplug) for mplug in self._mplug.destinations()]


class Component(MayaObject):

    _comp_mfn = None
    _comp_type = om2.MFn.kComponent

    @property
    def mdagpath(self):
        # type: () -> om2.MDagPath
        return self._mdagpath

    @property
    def mfn(self):
        # type: () -> om2.MFnComponent
        if self._mfn is None:
            self._mfn = self.__class__._comp_mfn(self.mobject)
        return self._mfn

    @property
    def elements(self):
        # type: () -> Iterable[Any]
        return self.mfn.getElements()

    def __init__(self, mdagpath, mobj):
        # type: (om2.MDagPath, om2.MObject) -> NoReturn
        super(Component, self).__init__(mobj)
        self._mdagpath = mdagpath
        self._mfn = None
        self.__cursor = 0

    def __str__(self):
        # type: () -> str
        return '{} {} (count: {})'.format(self.__class__, self.mdagpath.fullPathName(), self.mfn.elementCount)

    def __len__(self):
        # type: () -> int
        return self.mfn.elementCount

    def __iter__(self):
        self.__cursor = 0
        return self

    def next(self):
        # type: () -> Any
        return self.__next__()

    def _get_element(self, index):
        # type: (int) -> Any
        return None

    def __next__(self):
        # type: () -> Any
        if self.__cursor >= len(self):
            raise StopIteration()
        value = self._get_element(self.__cursor)
        self.__cursor += 1
        return value


class _SingleIndexedComponent(Component):

    def __init__(self, mdagpath, mobj):
        # type: (om2.MDagPath, om2.MObject) -> NoReturn
        super(_SingleIndexedComponent, self).__init__(mdagpath, mobj)

    def _get_element(self, index):
        # type: (int) -> Any
        return self.mfn.element(index)


class _DoubleIndexedComponent(Component):

    def __init__(self, mdagpath, mobj):
        # type: (om2.MDagPath, om2.MObject) -> NoReturn
        super(_SingleIndexedComponent, self).__init__(mdagpath, mobj)

    def _get_element(self, index):
        # type: (int) -> Any
        return self.mfn.getElement(index)


class MeshVertexComponent(_SingleIndexedComponent):

    _comp_mfn = om2.MFnSingleIndexedComponent
    _comp_type = om2.MFn.kMeshVertComponent

    def __init__(self, mdagpath, mobj):
        # type: (om2.MDagPath, om2.MObject) -> NoReturn
        super(MeshVertexComponent, self).__init__(mdagpath, mobj)


class MeshFaceComponent(_SingleIndexedComponent):

    _comp_mfn = om2.MFnSingleIndexedComponent
    _comp_type = om2.MFn.kMeshPolygonComponent

    def __init__(self, mdagpath, mobj):
        # type: (om2.MDagPath, om2.MObject) -> NoReturn
        super(MeshFaceComponent, self).__init__(mdagpath, mobj)


class MeshEdgeComponent(_SingleIndexedComponent):

    _comp_mfn = om2.MFnSingleIndexedComponent
    _comp_type = om2.MFn.kMeshEdgeComponent

    def __init__(self, mdagpath, mobj):
        # type: (om2.MDagPath, om2.MObject) -> NoReturn
        super(MeshEdgeComponent, self).__init__(mdagpath, mobj)


class MeshVertexFaceComponent(_DoubleIndexedComponent):

    _comp_mfn = om2.MFnDoubleIndexedComponent
    _comp_type = om2.MFn.kMeshVtxFaceComponent

    def __init__(self, mdagpath, mobj):
        # type: (om2.MDagPath, om2.MObject) -> NoReturn
        super(MeshVertexFaceComponent, self).__init__(mdagpath, mobj)


_PlugFactory.register(Plug)
_ComponentFactory.register(__name__)
