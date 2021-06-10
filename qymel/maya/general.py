# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *

import functools

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2

from .internal import graphs as _graphs
from .internal import plugs as _plugs


def deprecated(message):
    def _deprecated(func):
        @functools.wraps(func)
        def _(*args, **kwargs):
            print(u'[DEPRECATED] {} is deprecated. {}'.format(func.__name__, message))
            return func(*args, **kwargs)
        return _
    return _deprecated


def ls(*args, **kwargs):
    # type: (Any, Any) -> Any
    return _graphs.ls(*args, **kwargs)


def eval(obj_name):
    # type: (Union[str, Iterable[str]]) -> Any
    tmp_mfn_comp = _om2.MFnComponent()
    tmp_mfn_node = _om2.MFnDependencyNode()
    if isinstance(obj_name, (str, text_type)):
        return _graphs.eval(obj_name, tmp_mfn_comp, tmp_mfn_node)
    else:
        return [_graphs.eval(name, tmp_mfn_comp, tmp_mfn_node) for name in obj_name]


def eval_node(node_name):
    # type: (str) -> Any
    tmp_mfn = _om2.MFnDependencyNode()
    return _graphs.eval_node(node_name, tmp_mfn)


def eval_plug(plug_name):
    # type: (str) -> Plug
    return _graphs.eval_plug(plug_name)


def eval_component(comp_name):
    # type: (str) -> _Component
    tmp_mfn = _om2.MFnComponent()
    return _graphs.eval_component(comp_name, tmp_mfn)


class Plug(object):

    @property
    def mel_object(self):
        # type: () -> str
        mfn_node = self.mfn_node
        if isinstance(mfn_node, _om2.MFnDagNode):
            return '{}.{}'.format(mfn_node.fullPathName(), self._mplug.partialName())
        return self._mplug.name()

    @property
    def mplug(self):
        # type: () -> _om2.MPlug
        return self._mplug

    @property
    def attribute_mobject(self):
        # type: () -> _om2.MObject
        return self._mplug.attribute()

    @property
    def mfn_node(self):
        # type: () -> Union[_om2.MFnDependencyNode, _om2.MFnDagNode]
        if self._mfn_node is None:
            node = self._mplug.node()
            if node.hasFn(_om2.MFn.kDagNode):
                mdagpath = _om2.MDagPath.getAPathTo(node)
                self._mfn_node = _om2.MFnDagNode(mdagpath)
            else:
                self._mfn_node = _om2.MFnDependencyNode(node)
        return self._mfn_node

    @property
    def is_null(self):
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
    def exists(self):
        # type: () -> bool
        return _cmds.objExists(self.mel_object)

    def __init__(self, plug):
        # type: (Union[_om2.MPlug, str]) -> NoReturn
        if isinstance(plug, (str, text_type)):
            plug = _graphs.get_mplug(plug)
        self._mplug = _graphs.keep_mplug(plug)
        self._mfn_node = None
        self._node = None  # type: 'DependNode'

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

        attr_mobj = _om2.MFnDependencyNode(mplug.node()).attribute(item)
        child_mplug = mplug.child(attr_mobj)
        return Plug(child_mplug)

    def node(self):
        # type: () -> 'DependNode'
        if self._node is None:
            mfn_node = self.mfn_node
            if isinstance(mfn_node, _om2.MFnDagNode):
                mdagpath = mfn_node.getPath()
                self._node = _graphs.to_node_instance(mfn_node, mdagpath)
            else:
                self._node = _graphs.to_node_instance(mfn_node)
        return self._node

    def get(self):
        # type: () -> Any
        mplug = self._mplug

        if mplug.isNetworked:
            raise RuntimeError('{} is networked'.format(self.name))

        return _plugs.plug_get_impl(mplug)

    def get_attr(self, **kwargs):
        # type: (Any, Any) -> Any
        return _cmds.getAttr(self.mel_object, **kwargs)

    def set_attr(self, *args, **kwargs):
        # type: (Any, Any) -> Any
        return _cmds.setAttr(self.mel_object, *args, **kwargs)

    def connect(self, dest_plug, **kwargs):
        # type: (Plug, Any) -> NoReturn
        _cmds.connectAttr(self.mel_object, dest_plug.mel_object, **kwargs)

    def disconnect(self, dest_plug, **kwargs):
        # type: (Plug, Any) -> NoReturn
        _cmds.disconnectAttr(self.mel_object, dest_plug.mel_object, **kwargs)

    def source(self):
        # type: () -> Plug
        return Plug(self._mplug.source())

    def destinations(self):
        # type: () -> List[Plug]
        return [Plug(mplug) for mplug in self._mplug.destinations()]


_plugs.PlugFactory.register(Plug)


class ColorSet(object):

    @property
    def name(self):
        # type: () -> str
        return self.__name

    @property
    def mel_object(self):
        # type: () -> str
        return self.__name

    @property
    def mesh(self):
        # type: () -> 'Mesh'
        return self.__mesh

    @property
    def channels(self):
        # type: () -> int
        return self.__mfn.getColorRepresentation(self.mel_object)

    @property
    def is_clamped(self):
        # type: () -> bool
        return self.__mfn.isColorClamped(self.mel_object)

    @property
    def is_per_instance(self):
        # type: () -> bool
        return self.__mfn.isColorSetPerInstance(self.mel_object)

    def __init__(self, name, mesh):
        # type: (str, 'Mesh') -> None
        self.__name = name
        self.__mfn = mesh.mfn
        self.__mesh = mesh

    def __repr__(self):
        return "{}('{}', {})".format(self.__class__.__name__, self.mel_object, repr(self.mesh))

    def color(self, index):
        # type: (int) -> _om2.MColor
        return self.__mfn.getColor(index, self.mel_object)

    def colors(self):
        # type: () -> _om2.MColorArray
        return self.__mfn.getColors(self.mel_object)

    def color_index(self, face_id, local_vertex_id):
        # type: (int, int) -> int
        return self.__mfn.getColorIndex(face_id, local_vertex_id, self.mel_object)

    def face_vertex_colors(self):
        # type: () -> _om2.MColorArray
        return self.__mfn.getFaceVertexColors(self.mel_object)

    def vertex_colors(self):
        # type: () -> _om2.MColorArray
        return self.__mfn.getVertexColors(self.mel_object)


class UvSet(object):

    @property
    def name(self):
        # type: () -> str
        return self.__name

    @property
    def mel_object(self):
        # type: () -> str
        return self.__name

    @property
    def mesh(self):
        # type: () -> 'Mesh'
        return self.__mesh

    def __init__(self, name, mesh):
        # type: (str, 'Mesh') -> NoReturn
        self.__name = name
        self.__mesh = mesh
        self.__mfn = mesh.mfn
