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
from . import general as _general


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
            mdagpath, obj = _graphs.get_comp_mobject(obj)
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

    def element_component(self, index):
        # type: (int) -> _TComp
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


#
# iterators
#

class MeshVertexIter(_components.ComponentIter['MeshVertexIter']):

    @property
    def index(self):
        # type: () -> int
        return self._miter.index()

    @property
    def connected_edge_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getConnectedEdges()

    @property
    def connected_edge_count(self):
        # type: () -> int
        return self._miter.numConnectedEdges()

    @property
    def connected_face_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getConnectedFaces()

    @property
    def connected_face_count(self):
        # type: () -> int
        return self._miter.numConnectedFaces()

    @property
    def connected_vertex_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getConnectedVertices()

    @property
    def on_boundary(self):
        # type: () -> bool
        return self._miter.onBoundary()

    def __init__(self, miter, comp, mfn_mesh):
        # type: (_om2.MItMeshVertex, Component, _om2.MFnMesh) -> NoReturn
        super(MeshVertexIter, self).__init__(miter, comp)
        self._mfn_mesh = mfn_mesh

    def has_color(self, face_id=None):
        # type: (int) -> bool
        if face_id is not None:
            return self._miter.hasColor(face_id)
        return self._miter.hasColor()

    def color(self, color_set=None, face_id=None):
        # type: (Union[_general.ColorSet, str], int) -> _om2.MColor
        color_set_name = _get_color_set_name(color_set, None)
        if face_id is not None:
            return self._miter.getColor(color_set_name, face_id)
        return self._miter.getColor(color_set_name)

    def colors(self, color_set=None):
        # type: (Union[_general.ColorSet, str]) -> _om2.MColorArray
        color_set_name = _get_color_set_name(color_set, None)
        return self._miter.getColors(color_set_name)

    def color_indices(self, color_set=None):
        # type: (Union[_general.ColorSet, str]) -> _om2.MIntArray
        color_set_name = _get_color_set_name(color_set, None)
        return self._miter.getColorIndices(color_set_name)

    def normal(self, space=_om2.MSpace.kObject):
        # type: (int) -> _om2.MVector
        # MItMeshVertex.getNormalを引数付きで呼ぶとMayaが落ちる
        return self._mfn_mesh.getVertexNormal(self.index, True, space)

    def normal_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getNormalIndices()

    def normals(self, space=_om2.MSpace.kObject):
        # type: (int) -> _om2.MVectorArray
        return self._miter.getNormals(space)

    def uv(self, uv_set=None):
        # type: (Union[_general.UvSet, str]) -> List[float]
        uv_set_name = _get_uv_set_name(uv_set, None)
        return self._miter.getUV(uv_set_name)

    def uv_indices(self, uv_set=None):
        # type: (Union[_general.UvSet, str]) -> _om2.MIntArray
        uv_set_name = _get_uv_set_name(uv_set, None)
        return self._miter.getUVIndices(uv_set_name)

    def uvs(self, uv_set=None):
        # type: (Union[_general.UvSet, str]) -> Dict[int, Tuple[float, float]]
        uv_set_name = _get_uv_set_name(uv_set, None)
        us, vs, face_ids = self._miter.getUVs(uv_set_name)

        result = {}  # type: Dict[int, Tuple[float, float]]
        for i, face_id in enumerate(face_ids):
            result[face_id] = us[i], vs[i]

        return result

    def uv_count(self, uv_set=None):
        # type: (Union[_general.UvSet, str]) -> int
        uv_set_name = _get_uv_set_name(uv_set, None)
        return self._miter.numUVs(uv_set_name)

    def position(self, space=_om2.MSpace.kObject):
        # type: (int) -> _om2.MPoint
        return self._miter.position(space)


class MeshFaceIter(_components.ComponentIter['MeshFaceIter']):

    @property
    def index(self):
        # type: () -> int
        return self._miter.index()

    @property
    def connected_edge_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getConnectedEdges()

    @property
    def connected_face_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getConnectedFaces()

    @property
    def connected_vertex_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getConnectedVertices()

    @property
    def edge_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getEdges()

    @property
    def vertex_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getVertices()

    @property
    def is_convex(self):
        # type: () -> bool
        return self._miter.isConvex()

    @property
    def is_lamina(self):
        # type: () -> bool
        return self._miter.isLamina()

    @property
    def is_planar(self):
        # type: () -> bool
        return self._miter.isPlanar()

    @property
    def on_boundary(self):
        # type: () -> bool
        return self._miter.onBoundary()

    @property
    def is_zero_area(self):
        # type: () -> bool
        return self._miter.zeroArea()

    @property
    def triangle_count(self):
        # type: () -> int
        return self._miter.numTriangles()

    def __init__(self, miter, comp):
        # type: (_om2.MItMeshPolygon, Component) -> NoReturn
        super(MeshFaceIter, self).__init__(miter, comp)

    def _next(self):
        if _om.MGlobal.apiVersion() >= 20220000:
            self._miter.next()
        else:
            self._miter.next(self._miter)

    def center(self, space=_om2.MSpace.kObject):
        # type: (int) -> _om2.MPoint
        return self._miter.center(space)

    def area(self, space=_om2.MSpace.kObject):
        # type: (int) -> float
        return self._miter.getArea(space)

    def normal(self, space=_om2.MSpace.kObject, vertex_id=None):
        # type: (int, int) -> _om2.MVector
        if vertex_id is not None:
            return self._miter.getNormal(vertex_id, space)
        return self._miter.getNormal(space)

    def normals(self, space=_om2.MSpace.kObject):
        # type: (int) -> _om2.MVectorArray
        return self._miter.getNormals(space)

    def points(self, space=_om2.MSpace.kObject):
        # type: (int) -> _om2.MPointArray
        return self._miter.getPoints(space)

    def triangle(self, index, space=_om2.MSpace.kObject):
        # type: (int, int) -> Dict[int, _om2.MPoint]
        points, vertices = self._miter.getTriangle(index, space)
        result = {}
        for i, vertex_id in enumerate(vertices):
            result[vertex_id] = points[i]
        return result

    def triangles(self, space=_om2.MSpace.kObject):
        # type: (int) -> List[Dict[int, _om2.MPoint]]
        data = self._miter.getTriangles(space)
        points = data[0]
        vertices = data[1]

        result = []

        for i in range(int(len(vertices) / 3)):
            result.append({
                vertices[i * 3 + 0]: points[i * 3 + 0],
                vertices[i * 3 + 1]: points[i * 3 + 1],
                vertices[i * 3 + 2]: points[i * 3 + 2],
            })

        return result


class MeshEdgeIter(_components.ComponentIter['MeshEdgeIter']):

    @property
    def index(self):
        # type: () -> int
        return self._miter.index()

    @property
    def connected_edge_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getConnectedEdges()

    @property
    def connected_face_indices(self):
        # type: () -> _om2.MIntArray
        return self._miter.getConnectedFaces()

    @property
    def vertex_indices(self):
        # type: () -> _om2.MIntArray
        return _om2.MIntArray([self._miter.vertexId(0), self._miter.vertexId(1)])

    @property
    def on_boudary(self):
        # type: () -> bool
        return self._miter.onBoundary()

    @property
    def is_smooth(self):
        # type: () -> bool
        return self._miter.isSmooth

    def __init__(self, miter, comp):
        # type: (_om2.MItMeshEdge, Component) -> NoReturn
        super(MeshEdgeIter, self).__init__(miter, comp)

    def center(self, space=_om2.MSpace.kObject):
        # type: (int) -> _om2.MPoint
        return self._miter.center(space)

    def length(self, space=_om2.MSpace.kObject):
        # type: (int) -> float
        return self._miter.length(space)

    def points(self, space=_om2.MSpace.kObject):
        # type: (int) -> _om2.MPointArray
        return _om2.MPointArray([self._miter.point(0, space), self._miter.point(1, space)])


class MeshVertexFaceIter(_components.ComponentIter['MeshVertexFaceIter']):

    @property
    def index(self):
        # type: () -> Tuple[int, int]
        miter = self._miter
        return miter.vertexId(), miter.faceId()

    @property
    def face_index(self):
        # type: () -> int
        return self._miter.faceId()

    @property
    def vertex_index(self):
        # type: () -> int
        return self._miter.vertexId()

    @property
    def face_vertex_index(self):
        # type: () -> int
        return self._miter.faceVertexId()

    @property
    def has_color(self):
        # type: () -> bool
        return self._miter.hasColor()

    def __init__(self, miter, comp):
        # type: (_om2.MItMeshFaceVertex, Component) -> NoReturn
        super(MeshVertexFaceIter, self).__init__(miter, comp)

    def color(self, color_set=None):
        # type: (Union[_general.ColorSet, str]) -> _om2.MColor
        color_set_name = _get_color_set_name(color_set, '')
        return self._miter.getColor(color_set_name)

    def color_index(self, color_set=None):
        # type: (Union[_general.ColorSet, str]) -> int
        color_set_name = _get_color_set_name(color_set, '')
        return self._miter.getColorIndex(color_set_name)

    def normal(self, space=_om2.MSpace.kObject):
        # type: (int) -> _om2.MVector
        return self._miter.getNormal(space)

    def tangent(self, space=_om2.MSpace.kObject, uv_set=None):
        # type: (int, Union[_general.UvSet, str]) -> _om2.MVector
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getTangent(space, uv_set_name)

    def binormal(self, space=_om2.MSpace.kObject, uv_set=None):
        # type: (int, Union[_general.UvSet, str]) -> _om2.MVector
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getBinormal(space, uv_set_name)

    def normal_index(self):
        # type: () -> int
        return self._miter.normalId()

    def tangent_index(self):
        # type: () -> int
        return self._miter.tangentId()

    def uv(self, uv_set=None):
        # type: (Union[_general.UvSet, str]) -> Tuple[float, float]
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getUV(uv_set_name)

    def uv_index(self, uv_set=None):
        # type: (Union[_general.UvSet, str]) -> int
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getUVIndex(uv_set_name)

    def has_uv(self, uv_set=None):
        # type: (Union[_general.UvSet, str]) -> bool
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.hasUVs(uv_set_name)

    def position(self, space=_om2.MSpace.kObject):
        # type: (int) -> _om2.MPoint
        return self._miter.position(space)


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


class MeshVertex(SingleIndexedComponent[MeshVertexIter, 'MeshVertex']):

    _comp_type = _om2.MFn.kMeshVertComponent
    _comp_repr = 'vtx'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshVertex, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> MeshVertexIter
        ite = _om2.MItMeshVertex(self.mdagpath, self.mobject)
        return MeshVertexIter(ite, self, _om2.MFnMesh(self.mdagpath))

    def f(self): pass


class MeshFace(SingleIndexedComponent[MeshFaceIter, 'MeshFace']):

    _comp_type = _om2.MFn.kMeshPolygonComponent
    _comp_repr = 'f'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshFace, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> MeshFaceIter
        ite = _om2.MItMeshPolygon(self.mdagpath, self.mobject)
        return MeshFaceIter(ite, self)


class MeshEdge(SingleIndexedComponent[MeshEdgeIter, 'MeshEdge']):

    _comp_type = _om2.MFn.kMeshEdgeComponent
    _comp_repr = 'e'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshEdge, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> MeshEdgeIter
        ite = _om2.MItMeshEdge(self.mdagpath, self.mobject)
        return MeshEdgeIter(ite, self)


class MeshVertexFace(DoubleIndexedComponent[MeshVertexFaceIter, 'MeshVertexFace']):

    _comp_type = _om2.MFn.kMeshVtxFaceComponent
    _comp_repr = 'vtxface'

    def __init__(self, obj, mdagpath=None):
        # type: (Union[_om2.MObject, str], _om2.MDagPath) -> NoReturn
        super(MeshVertexFace, self).__init__(obj, mdagpath)

    def iterator(self):
        # type: () -> MeshVertexFaceIter
        ite = _om2.MItMeshFaceVertex(self.mdagpath, self.mobject)
        return MeshVertexFaceIter(ite, self)


def _get_color_set_name(color_set, default_value):
    # type: (Union[_general.ColorSet, Any], Optional[str]) -> str
    if color_set is None:
        return default_value

    if isinstance(color_set, (str, text_type)):
        return color_set

    return color_set.mel_object


def _get_uv_set_name(uv_set, default_value):
    # type: (Union[_general.UvSet, Any], Optional[str]) -> str
    if uv_set is None:
        return default_value

    if isinstance(uv_set, (str, text_type)):
        return uv_set

    return uv_set.mel_object


_components.ComponentFactory.register(__name__)
