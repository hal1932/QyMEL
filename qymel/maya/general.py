# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *

import functools

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2

from .internal import components as _components
from .internal import graphs as _graphs
from .internal import plugs as _plugs
from . import iterators as _iterators


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


class MayaObject(object):

    @property
    def mobject(self):
        # type: () -> _om2.MObject
        return self._mobj_handle.object()

    @property
    def mobject_handle(self):
        # type: () -> _om2.MObjectHandle
        return self._mobj_handle

    @property
    def is_null(self):
        # type: () -> bool
        return self.mobject.isNull()

    @property
    def mel_object(self):
        # type: () -> Union[str, Tuple[str]]
        raise NotImplementedError()

    @property
    def exists(self):
        # type: () -> bool
        return not self.is_null

    @property
    def api_type(self):
        # type: () -> int
        return self.mobject.apiType()

    @property
    def api_type_str(self):
        # type: () -> str
        return self.mobject.apiTypeStr

    def __init__(self, mobj):
        # type: (_om2.MObject) -> NoReturn
        if mobj is not None:
            self._mobj_handle = _om2.MObjectHandle(mobj)
        else:
            self._mobj_handle = None

    def __eq__(self, other):
        # type: (Union[MayaObject, Any]) -> bool
        if other is None or not isinstance(other, MayaObject):
            return False
        if not other._mobj_handle.isValid():
            return False
        return self._mobj_handle.hashCode() == other._mobj_handle.hashCode()

    def __ne__(self, other):
        # type: (Union[MayaObject, Any]) -> bool
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
        self._node = None  # type: DependNode

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
        # type: () -> DependNode
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


_TCompFn = TypeVar('_TCompFn', bound=_om2.MFnComponent)
_TCompElem = TypeVar('_TCompElem')
_TCompIter = TypeVar('_TCompIter', bound=_iterators._Iterator)
_TCompType = TypeVar('_TCompType')


class _Component(MayaObject, Generic[_TCompFn, _TCompElem, _TCompIter, _TCompType]):

    _comp_mfn = None
    _comp_type = _om2.MFn.kComponent
    _comp_repr = ''

    @property
    def mel_object(self):
        # type: () -> Tuple[str]
        sel_list = _om2.MSelectionList()
        sel_list.add((self.mdagpath, self.mobject), False)
        return _cmds.ls(sel_list.getSelectionStrings(0), long=True)

    @property
    def exists(self):
        # type: () -> bool
        for mel_obj in self.mel_object:
            if not _cmds.objExists(mel_obj):
                return False
        return True

    @property
    def mdagpath(self):
        # type: () -> _om2.MDagPath
        return self._mdagpath

    @property
    def mfn(self):
        # type: () -> _TCompFn
        if self._mfn is None:
            self._mfn = self.__class__._comp_mfn(self.mobject)
        return self._mfn

    @property
    def elements(self):
        # type: () -> Iterable[_TCompElem]
        return self.mfn.getElements()

    def __init__(self, obj, mdagpath):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        if isinstance(obj, (str, text_type)):
            mdagpath, obj = _graphs.get_comp_mobject(obj)
        super(_Component, self).__init__(obj)
        self._mdagpath = mdagpath
        self._mfn = None  # type: _TCompFn
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

    def __getitem__(self, item):
        # type: (int) -> _TCompElem
        return self.element(item)

    def __iter__(self):
        self.__cursor = 0
        return self

    def next(self):
        # type: () -> _TCompElem
        return self.__next__()

    def __next__(self):
        # type: () -> _TCompElem
        if self.__cursor >= len(self):
            raise StopIteration()
        value = self.element(self.__cursor)
        self.__cursor += 1
        return value

    def clone_empty(self):
        # type: () -> _TCompType
        comp = self._create_api_comp()
        return self.__class__(comp.object(), self.mdagpath)

    def element(self, index):
        # type: (int) -> _TCompElem
        raise NotImplementedError()

    def iterator(self):
        # type: () -> _TCompIter
        raise NotImplementedError()

    def append(self, element):
        # type: (_TCompElem) -> NoReturn
        self.mfn.addElement(element)

    def extend(self, elements):
        # type: (Sequence[_TCompElem]) -> NoReturn
        self.mfn.addElements(elements)

    def element_component(self, index):
        # type: (int) -> _TCompType
        comp = self.clone_empty()
        comp.append(self.element(index))
        return comp

    @classmethod
    def _create_api_comp(cls, elements=None):
        # type: (type, Sequence[_TCompElem]) -> _TCompFn
        comp = cls._comp_mfn()
        comp.create(cls._comp_type)
        if elements:
            comp.addElements(elements)
        return comp


class SingleIndexedComponent(_Component[_om2.MFnSingleIndexedComponent, int, _TCompIter, _TCompType]):

    _comp_mfn = _om2.MFnSingleIndexedComponent

    def __init__(self, obj, mdagpath):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(SingleIndexedComponent, self).__init__(obj, mdagpath)

    def element(self, index):
        # type: (int) -> int
        return self.mfn.element(index)

    def iterator(self):
        # type: () -> _TCompIter
        raise NotImplementedError()


class DoubleIndexedComponent(_Component[_om2.MFnDoubleIndexedComponent, Tuple[int, int], _TCompIter, _TCompType]):

    _comp_mfn = _om2.MFnDoubleIndexedComponent

    def __init__(self, obj, mdagpath):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(DoubleIndexedComponent, self).__init__(obj, mdagpath)

    def element(self, index):
        # type: (int) -> Tuple[int, int]
        return self.mfn.getElement(index)

    def iterator(self):
        # type: () -> _TCompIter
        raise NotImplementedError()


class MeshVertex(SingleIndexedComponent[_iterators.MeshVertexIter, 'MeshVertex']):

    _comp_type = _om2.MFn.kMeshVertComponent
    _comp_repr = 'vtx'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshVertex, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> _iterators.MeshVertexIter
        iter = _om2.MItMeshVertex(self.mdagpath, self.mobject)
        return _iterators.MeshVertexIter(iter, self, _om2.MFnMesh(self.mdagpath))

    def f(self): pass


class MeshFace(SingleIndexedComponent[_iterators.MeshFaceIter, 'MeshFace']):

    _comp_type = _om2.MFn.kMeshPolygonComponent
    _comp_repr = 'f'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshFace, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> _iterators.MeshFaceIter
        iter = _om2.MItMeshPolygon(self.mdagpath, self.mobject)
        return _iterators.MeshFaceIter(iter, self)


class MeshEdge(SingleIndexedComponent[_iterators.MeshEdgeIter, 'MeshEdge']):

    _comp_type = _om2.MFn.kMeshEdgeComponent
    _comp_repr = 'e'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshEdge, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> _iterators.MeshEdgeIter
        iter = _om2.MItMeshEdge(self.mdagpath, self.mobject)
        return _iterators.MeshEdgeIter(iter, self)


class MeshVertexFace(DoubleIndexedComponent[_iterators.MeshVertexFaceIter, 'MeshVertexFace']):

    _comp_type = _om2.MFn.kMeshVtxFaceComponent
    _comp_repr = 'vtxface'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshVertexFace, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> _iterators.MeshVertexFaceIter
        iter = _om2.MItMeshFaceVertex(self.mdagpath, self.mobject)
        return _iterators.MeshVertexFaceIter(iter, self)


_plugs.PlugFactory.register(Plug)
_components.ComponentFactory.register(__name__)
