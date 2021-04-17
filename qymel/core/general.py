# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import maya.cmds as cmds
import maya.api.OpenMaya as om2

from ..internal import graphs as _graphs
from ..internal import plugs as _plugs
from ..internal import components as _components


def ls(*args, **kwargs):
    # type: (Any, Any) -> Any
    return _graphs.ls(*args, **kwargs)


def eval(obj_name):
    # type: (Union[str, Iterable[str]]) -> Any
    tmp_mfn_comp = om2.MFnComponent()
    tmp_mfn_node = om2.MFnDependencyNode()
    if isinstance(obj_name, (str, text_type)):
        return _graphs.eval(obj_name, tmp_mfn_comp, tmp_mfn_node)
    else:
        return [_graphs.eval(name, tmp_mfn_comp, tmp_mfn_node) for name in obj_name]


def eval_node(node_name):
    # type: (str) -> Any
    tmp_mfn = om2.MFnDependencyNode()
    return _graphs.eval_node(node_name, tmp_mfn)


def eval_plug(plug_name):
    # type: (str) -> Plug
    return _graphs.eval_plug(plug_name)


def eval_component(comp_name):
    # type: (str) -> Component
    tmp_mfn = om2.MFnComponent()
    return _graphs.eval_component(comp_name, tmp_mfn)


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
    def is_null(self):
        # type: () -> bool
        return self._mobj_handle.object().isNull()

    @property
    def mel_object(self):
        # type: () -> Union[str, Tuple[str]]
        pass

    @property
    def exists(self):
        # type: () -> bool
        mobj = self.mobject
        if mobj is None:
            return False
        if mobj.isNull():
            return False
        return True

    @property
    def api_type(self):
        # type: () -> int
        return self.mobject.apiType()

    @property
    def api_type_str(self):
        # type: () -> str
        return self.mobject.apiTypeStr

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        if mobj is not None:
            self._mobj_handle = om2.MObjectHandle(mobj)
        else:
            self._mobj_handle = None

    def __eq__(self, other):
        # type: (object) -> bool
        if other is None or not other._mobj_handle.isValid():
            return False
        if not isinstance(other, MayaObject):
            return False
        return self._mobj_handle.hashCode() == other._mobj_handle.hashCode()

    def __ne__(self, other):
        # type: (object) -> bool
        return not self.__eq__(other)

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
    def mel_object(self):
        # type: () -> str
        mfn_node = self.mfn_node
        if isinstance(mfn_node, om2.MFnDagNode):
            return '{}.{}'.format(mfn_node.fullPathName(), self._mplug.partialName())
        return self._mplug.name()

    @property
    def mplug(self):
        # type: () -> om2.MPlug
        return self._mplug

    @property
    def attribute_mobject(self):
        # type: () -> om2.MObject
        return self._mplug.attribute()

    @property
    def mfn_node(self):
        # type: () -> Union[om2.MFnDependencyNode, om2.MFnDagNode]
        if self._mfn_node is None:
            node = self._mplug.node()
            if node.hasFn(om2.MFn.kDagNode):
                self._mfn_node = om2.MFnDagNode(node)
            else:
                self._mfn_node = om2.MFnDependencyNode(node)
        return self._mfn_node

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
        return self._mplug.attribute().apiType()

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

    @property
    def exists(self):
        # type: () -> bool
        return cmds.objExists(self.mel_object)

    def __init__(self, plug):
        # type: (Union[om2.MPlug, str]) -> NoReturn
        if isinstance(plug, (str, text_type)):
            plug = _graphs.get_mplug(plug)
        self._mplug = plug
        self._mfn_node = None

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        return "{}('{}')".format(self.__class__.__name__, self.name)

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

        return _plugs.plug_get_impl(mplug)

    def get_attr(self, **kwargs):
        # type: (Any, Any) -> Any
        return cmds.getAttr(self.mel_object, **kwargs)

    def set_attr(self, *args, **kwargs):
        # type: (Any, Any) -> Any
        return cmds.setAttr(self.mel_object, *args, **kwargs)

    def connect(self, dest_plug, **kwargs):
        # type: (Plug, Any) -> NoReturn
        cmds.connectAttr(self.mel_object, dest_plug.mel_object, **kwargs)

    def disconnect(self, dest_plug, **kwargs):
        # type: (Plug, Any) -> NoReturn
        cmds.disconnectAttr(self.mel_object, dest_plug.mel_object, **kwargs)

    def source(self):
        # type: () -> Plug
        return Plug(self._mplug.source())

    def destinations(self):
        # type: () -> List[Plug]
        return [Plug(mplug) for mplug in self._mplug.destinations()]


class Component(MayaObject):

    _comp_mfn = None
    _comp_type = om2.MFn.kComponent
    _comp_repr = ''

    @property
    def mel_object(self):
        # type: () -> Tuple[str]
        sel_list = om2.MSelectionList()
        sel_list.add((self.mdagpath, self.mobject), False)
        return cmds.ls(sel_list.getSelectionStrings(0), long=True)

    @property
    def exists(self):
        # type: () -> bool
        for mel_obj in self.mel_object:
            if not cmds.objExists(mel_obj):
                return False
        return True

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

    def __init__(self, obj, mdagpath):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        if isinstance(obj, (str, text_type)):
            mdagpath, obj = _graphs.get_comp_mobject(obj)
        super(Component, self).__init__(obj)
        self._mdagpath = mdagpath
        self._mfn = None  # type: om2.MFnComponent
        self.__cursor = 0

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        return ', '.join(["{}('{}')".format(self.__class__.__name__, name) for name in self.mel_object])

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

    def __init__(self, obj, mdagpath):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(_SingleIndexedComponent, self).__init__(obj, mdagpath)

    def _get_element(self, index):
        # type: (int) -> Any
        return self.mfn.element(index)


class _DoubleIndexedComponent(Component):

    def __init__(self, obj, mdagpath):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(_DoubleIndexedComponent, self).__init__(obj, mdagpath)

    def _get_element(self, index):
        # type: (int) -> Any
        return self.mfn.getElement(index)


class MeshVertex(_SingleIndexedComponent):

    _comp_mfn = om2.MFnSingleIndexedComponent
    _comp_type = om2.MFn.kMeshVertComponent
    _comp_repr = 'vtx'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(MeshVertex, self).__init__(obj, mdagpath)


class MeshFace(_SingleIndexedComponent):

    _comp_mfn = om2.MFnSingleIndexedComponent
    _comp_type = om2.MFn.kMeshPolygonComponent
    _comp_repr = 'f'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(MeshFace, self).__init__(obj, mdagpath)


class MeshEdge(_SingleIndexedComponent):

    _comp_mfn = om2.MFnSingleIndexedComponent
    _comp_type = om2.MFn.kMeshEdgeComponent
    _comp_repr = 'e'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(MeshEdge, self).__init__(obj, mdagpath)


class MeshVertexFace(_DoubleIndexedComponent):

    _comp_mfn = om2.MFnDoubleIndexedComponent
    _comp_type = om2.MFn.kMeshVtxFaceComponent
    _comp_repr = 'vtxface'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(MeshVertexFace, self).__init__(obj, mdagpath)


_plugs.PlugFactory.register(Plug)
_components.ComponentFactory.register(__name__)
