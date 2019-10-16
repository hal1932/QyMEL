# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.api.OpenMaya as om2


class _Iterator(object):

    @property
    def miter(self):
        return self._miter

    @property
    def mobject(self):
        # type: () -> om2.MObject
        return self._miter.currentItem()

    def __init__(self, miter, comp):
        self._miter = miter
        self._comp = comp  # 使う機会はないけど、ループの最中にcompのスコープが切れないように手許で抱えておく
        self.__is_first = True

    def __getattr__(self, item):
        # type: (str) -> Any
        return getattr(self._miter, item)

    def __iter__(self):
        # type: () -> _Iterator
        return self

    def next(self):
        # type: () -> _Iterator
        return self.__next__()

    def __next__(self):
        # type: () -> _Iterator
        if self.__is_first:
            self.__is_first = False
            return self

        self._next()

        if self._miter.isDone():
            raise StopIteration()

        return self

    def _next(self):
        # type: () -> NoReturn
        self._miter.next()


class MeshVertexIter(_Iterator):

    @property
    def index(self):
        # type: () -> int
        return self._miter.index()

    @property
    def connected_edge_indices(self):
        # type: () -> om2.MIntArray
        return self._miter.getConnectedEdges()

    @property
    def connected_edge_count(self):
        # type: () -> int
        return self._miter.numConnectedEdges()

    @property
    def connected_face_indices(self):
        # type: () -> om2.MIntArray
        return self._miter.getConnectedFaces()

    @property
    def connected_face_count(self):
        # type: () -> int
        return self._miter.numConnectedFaces()

    @property
    def connected_vertex_indices(self):
        # type: () -> om2.MIntArray
        return self._miter.getConnectedVertices()

    @property
    def on_boundary(self):
        # type: () -> bool
        return self._miter.onBoundary()

    def __init__(self, miter, comp, mfn_mesh):
        # type: (om2.MItMeshVertex, Component, om2.MFnMesh) -> NoReturn
        super(MeshVertexIter, self).__init__(miter, comp)
        self._mfn_mesh = mfn_mesh

    def has_color(self, face_id=None):
        # type: (int) -> bool
        if face_id is not None:
            return self._miter.hasColor(face_id)
        return self._miter.hasColor()

    def color(self, color_set=None, face_id=None):
        # type: (Union[ColorSet, str], int) -> om2.MColor
        color_set_name = _get_color_set_name(color_set, None)
        if face_id is not None:
            return self._miter.getColor(color_set_name, face_id)
        return self._miter.getColor(color_set_name)

    def colors(self, color_set=None):
        # type: (Union[ColorSet, str]) -> om2.MColorArray
        color_set_name = _get_color_set_name(color_set, None)
        return self._miter.getColors(color_set_name)

    def color_indices(self, color_set=None):
        # type: (Union[ColorSet, str]) -> om2.MIntArray
        color_set_name = _get_color_set_name(color_set, None)
        return self._miter.getColorIndices(None)

    def normal(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MVector
        # MItMeshVertex.getNormalを引数付きで呼ぶとMayaが落ちる
        return self._mfn_mesh.getVertexNormal(self.index, True, space)

    def normal_indices(self):
        # type: () -> om2.MIntArray
        return self._miter.getNormalIndices()

    def normals(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MVectorArray
        return self._miter.getNormals(space)

    def uv(self, uv_set=None):
        # type: (Union[UvSet, str]) -> List[float]
        uv_set_name = _get_uv_set_name(uv_set, None)
        return self._miter.getUV(uv_set_name)

    def uv_indices(self, uv_set=None):
        # type: (Union[UvSet, str]) -> om2.MIntArray
        uv_set_name = _get_uv_set_name(uv_set, None)
        return self._miter.getUVIndices(uv_set_name)

    def uvs(self, uv_set=None):
        # type: (Union[UvSet, str]) -> Dict[int, Tuple[float]]
        uv_set_name = _get_uv_set_name(uv_set, None)
        us, vs, face_ids = self._miter.getUVs(uv_set_name)

        result = {}  # type: Dict[int, Tuple[float, float]]
        for i, face_id in enumerate(face_ids):
            result[face_id] = us[i], vs[i]

        return result

    def uv_count(self, uv_set=None):
        # type: (Union[UvSet, str]) -> int
        uv_set_name = _get_uv_set_name(uv_set, None)
        return self._miter.numUVs(uv_set_name)

    def position(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MPoint
        return self._miter.position(space)


class MeshFaceIter(_Iterator):

    @property
    def index(self):
        # type: () -> int
        return self._miter.index()

    @property
    def connected_edge_indices(self):
        # type: () -> om2.MIntArray
        return self._miter.getConnectedEdges()

    @property
    def connected_face_indices(self):
        # type: () -> om2.MIntArray
        return self._miter.getConnectedFaces()

    @property
    def connected_vertex_indices(self):
        # type: () -> om2.MIntArray
        return self._miter.getConnectedVertices()

    @property
    def edge_indices(self):
        # type: () -> om2.MIntArray
        return self._miter.getEdges()

    @property
    def vertex_indices(self):
        # type: () -> om2.MIntArray
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
        # type: (om2.MItMeshPolygon, Component) -> NoReturn
        super(MeshFaceIter, self).__init__(miter, comp)

    def _next(self):
        self._miter.next(self._miter)

    def center(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MPoint
        return self._miter.center(space)

    def area(self, space=om2.MSpace.kObject):
        # type: (int) -> float
        return self._miter.getArea(space)

    def normal(self, space=om2.MSpace.kObject, vertex_id=None):
        # type: (int, int) -> om2.MVector
        if vertex_id is not None:
            return self._miter.getNormal(vertex_id, space)
        return self._miter.getNormal(space)

    def normals(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MVectorArray
        return self._miter.getNormals(space)

    def points(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MPointArray
        return self._miter.getPoints(space)

    def triangle(self, index, space=om2.MSpace.kObject):
        # type: (int, int) -> Dict[int, om2.MPoint]
        points, vertices = self._miter.getTriangle(index, space)
        result = {}
        for i, vertex_id in enumerate(vertices):
            result[vertex_id] = points[i]
        return result

    def triangles(self, space=om2.MSpace.kObject):
        # type: (int) -> List[Dict[int, om2.MPoint]]
        data = self._miter.getTriangles(space)
        points = data[0]
        vertices = data[1]

        result = []

        for i in range(len(vertices) / 3):
            result.append({
                vertices[i * 3 + 0]: points[i * 3 + 0],
                vertices[i * 3 + 1]: points[i * 3 + 1],
                vertices[i * 3 + 2]: points[i * 3 + 2],
            })

        return result


class MeshEdgeIter(_Iterator):

    @property
    def index(self):
        # type: () -> int
        return self._miter.index()

    @property
    def connected_edge_indices(self):
        # type: () -> om2.MIntArray
        return self._miter.getConnectedEdges()

    @property
    def connected_face_indices(self):
        # type: () -> om2.MIntArray
        return self._miter.getConnectedFaces()

    @property
    def vertex_indices(self):
        # type: () -> om2.MIntArray
        return om2.MIntArray([self._miter.vertexId(0), self._miter.vertexId(1)])

    @property
    def on_boudary(self):
        # type: () -> bool
        return self._miter.onBoundary()

    @property
    def is_smooth(self):
        # type: () -> bool
        return self._miter.isSmooth

    def __init__(self, miter, comp):
        # type: (om2.MItMeshEdge, Component) -> NoReturn
        super(MeshEdgeIter, self).__init__(miter, comp)

    def center(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MPoint
        return self._miter.center(space)

    def length(self, space=om2.MSpace.kObject):
        # type: (int) -> float
        return self._miter.length(space)

    def points(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MPointArray
        return om2.MPointArray([self._miter.point(0, space), self._miter.point(1, space)])


class MeshVertexFaceIter(_Iterator):

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
        # type: (om2.MItMeshFaceVertex, Component) -> NoReturn
        super(MeshVertexFaceIter, self).__init__(miter, comp)

    def color(self, color_set=None):
        # type: (Union[ColorSet, str]) -> om2.MColor
        color_set_name = _get_color_set_name(color_set, '')
        return self._miter.getColor(color_set_name)

    def color_index(self, color_set=None):
        # type: (Union[ColorSet, str]) -> int
        color_set_name = _get_color_set_name(color_set, '')
        return self._miter.getColorIndex(color_set_name)

    def normal(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MVector
        return self._miter.getNormal(space)

    def tangent(self, space=om2.MSpace.kObject, uv_set=None):
        # type: (int, Union[UvSet, str]) -> om2.MVector
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getTangent(space, uv_set_name)

    def binormal(self, space=om2.MSpace.kObject, uv_set=None):
        # type: (int, Union[UvSet, str]) -> om2.MVector
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getBinormal(space, uv_set_name)

    def normal_index(self):
        # type: () -> int
        return self._miter.normalId()

    def tangent_index(self):
        # type: () -> int
        return self._miter.tangentId()

    def uv(self, uv_set=None):
        # type: (Union[UvSet, str]) -> Tuple[float, float]
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getUV(uv_set_name)

    def uv_index(self, uv_set=None):
        # type: (Union[UvSet, str]) -> int
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getUVIndex(uv_set_name)

    def has_uv(self, uv_set=None):
        # type: (Union[UvSet, str]) -> bool
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.hasUVs(uv_set_name)

    def position(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MPoint
        return self._miter.position(space)


def _get_color_set_name(color_set, default_value):
    # type: (Union[ColorSet, Any]) -> str
    if color_set is None:
        return default_value

    if isinstance(color_set, (str, unicode)):
        return color_set

    return color_set.mel_object


def _get_uv_set_name(uv_set, default_value):
    # type: (Union[UvSet, Any]) -> str
    if uv_set is None:
        return default_value

    if isinstance(uv_set, (str, unicode)):
        return uv_set

    return uv_set.mel_object
