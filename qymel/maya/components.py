# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2
import maya.OpenMaya as _om

from .internal import components as _components
from .internal import graphs as _graphs
from . import objects as _objects
from . import iterators as _iterators


# 呼び出し回数が極端に多くなる可能性のある静的メソッドをキャッシュ化しておく
_graphs_get_comp_mobject = _graphs.get_comp_mobject


_TCompFn = TypeVar('_TCompFn', bound=_om2.MFnComponent)
_TCompElem = TypeVar('_TCompElem')
_TCompIter = TypeVar('_TCompIter', bound='ComponentIter')
_TComp = TypeVar('_TComp')


class Component(_objects.MayaObject, Generic[_TCompFn, _TCompElem, _TCompIter, _TComp]):

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
            mdagpath, obj = _graphs_get_comp_mobject(obj)
        super(Component, self).__init__(obj)
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

    def node(self):
        # type: () -> 'DagNode'
        mfn = _om2.MFnDagNode(self.mdagpath)
        return _graphs.to_node_instance(mfn, self.mdagpath)

    def clone(self):
        # type: () -> _TComp
        clone = self.clone_empty()
        clone.extend(self.elements)
        return clone

    def clone_empty(self):
        # type: () -> _TComp
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

    def set_complete(self, count):
        # type: (int) -> NoReturn
        self.mfn.setCompleteData(count)

    @classmethod
    def _create_api_comp(cls, elements=None):
        # type: (type, Sequence[_TCompElem]) -> _TCompFn
        comp = cls._comp_mfn()
        comp.create(cls._comp_type)
        if elements:
            comp.addElements(elements)
        return comp


#
# components
#

class SingleIndexedComponent(Component[_om2.MFnSingleIndexedComponent, int, _TCompIter, _TComp]):

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


class DoubleIndexedComponent(Component[_om2.MFnDoubleIndexedComponent, Tuple[int, int], _TCompIter, _TComp]):

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
        # type: () -> MeshVertexIter
        ite = _om2.MItMeshVertex(self.mdagpath, self.mobject)
        return _iterators.MeshVertexIter(ite, self, _om2.MFnMesh(self.mdagpath))


class MeshFace(SingleIndexedComponent[_iterators.MeshFaceIter, 'MeshFace']):

    _comp_type = _om2.MFn.kMeshPolygonComponent
    _comp_repr = 'f'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshFace, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> MeshFaceIter
        ite = _om2.MItMeshPolygon(self.mdagpath, self.mobject)
        return _iterators.MeshFaceIter(ite, self, _om2.MFnMesh(self.mdagpath))


class MeshEdge(SingleIndexedComponent[_iterators.MeshEdgeIter, 'MeshEdge']):

    _comp_type = _om2.MFn.kMeshEdgeComponent
    _comp_repr = 'e'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshEdge, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> MeshEdgeIter
        ite = _om2.MItMeshEdge(self.mdagpath, self.mobject)
        return _iterators.MeshEdgeIter(ite, self, _om2.MFnMesh(self.mdagpath))


class MeshVertexFace(DoubleIndexedComponent[_iterators.MeshFaceVertexIter, 'MeshVertexFace']):

    _comp_type = _om2.MFn.kMeshVtxFaceComponent
    _comp_repr = 'vtxface'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshVertexFace, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> MeshVertexFaceIter
        ite = _om2.MItMeshFaceVertex(self.mdagpath, self.mobject)
        return _iterators.MeshFaceVertexIter(ite, self, _om2.MFnMesh(self.mdagpath))


_components.ComponentFactory.register(__name__)
