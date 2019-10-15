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
        return self.miter.currentItem()

    @property
    def index(self):
        # type: () -> int
        return self._miter.index()

    def __init__(self, miter, comp):
        self._miter = miter
        self._comp = comp  # 使う機会はないんだけど、ループの最中にcompのスコープが切れないように手許で保持しておく
        self.__is_first = True

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
    def connected_edge_indices(self):
        # type: () -> om2.MIntArray
        return self.miter.getConnectedEdges()

    @property
    def connected_edge_count(self):
        # type: () -> int
        return self.miter.numConnectedEdges()

    @property
    def connected_face_indices(self):
        # type: () -> om2.MIntArray
        return self.miter.getConnectedFaces()

    @property
    def connected_face_count(self):
        # type: () -> int
        return self.miter.numConnectedFaces()

    @property
    def connected_vertex_indices(self):
        # type: () -> om2.MIntArray
        return self.miter.getConnectedVertices()

    @property
    def on_boundary(self):
        # type: () -> bool
        return self.miter.onBoundary()

    def __init__(self, miter, comp):
        # type: (om2.MItMeshVertex, Component) -> NoReturn
        super(MeshVertexIter, self).__init__(miter, comp)

    def has_color(self, face_id=None):
        # type: (int) -> bool
        if face_id is not None:
            return self.miter.hasColor(face_id)
        return self.miter.hasColor()

    def color(self, color_set=None, face_id=None):
        # type: (Union[ColorSet, str], int) -> om2.MColor
        color_set_name = _get_color_set_name(color_set)
        if face_id is not None:
            return self.miter.getColor(color_set_name, face_id)
        return self.miter.getColor(color_set_name)

    def colors(self, color_set=None):
        # type: (Union[ColorSet, str]) -> om2.MColorArray
        color_set_name = _get_color_set_name(color_set)
        return self.miter.getColors(color_set_name)

    def color_indices(self, color_set=None):
        # type: (Union[ColorSet, str]) -> om2.MIntArray
        color_set_name = _get_color_set_name(color_set)
        return self.miter.getColorIndices(color_set_name)

    def normal(self, space=om2.MSpace.kObject, face_id=None):
        # type: (int, int) -> om2.MVector
        if face_id is not None:
            return self.miter.getNormal(space, face_id)
        return self.miter.getNormal(space)

    def normal_indices(self):
        # type: () -> om2.MIntArray
        return self.miter.getNormalIndices()

    def normals(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MVectorArray
        return self.miter.getNormals(space)

    def uv(self, uv_set=None):
        # type: (Union[UvSet, str]) -> List[float]
        uv_set_name = _get_uv_set_name(uv_set)
        return self.miter.getUV(uv_set_name)

    def uv_indices(self, uv_set=None):
        # type: (Union[UvSet, str]) -> om2.MIntArray
        uv_set_name = _get_uv_set_name(uv_set)
        return self.miter.getUVIndices(uv_set_name)

    def uvs(self, uv_set=None):
        # type: (Union[UvSet, str]) -> Dict[int, Tuple[float]]
        uv_set_name = _get_uv_set_name(uv_set)
        us, vs, face_ids = self.miter.getUVs(uv_set_name)

        result = {}  # type: Dict[int, Tuple[float]]
        for i, face_id in enumerate(face_ids):
            result[face_id] = us[i], vs[i]

        return result

    def uv_count(self, uv_set=None):
        # type: (Union[UvSet, str]) -> int
        uv_set_name = _get_uv_set_name(uv_set)
        return self.miter.numUVs(uv_set_name)

    def position(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MPoint
        return self.miter.position(space)


class MeshFaceIter(_Iterator):

    @property
    def connected_edge_indices(self):
        # type: () -> om2.MIntArray
        return self.miter.getConnectedEdges()

    @property
    def connected_face_indices(self):
        # type: () -> om2.MIntArray
        return self.miter.getConnectedFaces()

    @property
    def connected_vertex_indices(self):
        # type: () -> om2.MIntArray
        return self.miter.getConnectedVertices()

    @property
    def edge_indices(self):
        # type: () -> om2.MIntArray
        return self.miter.getEdges()

    def __init__(self, miter, comp):
        # type: (om2.MItMeshPolygon, Component) -> NoReturn
        super(MeshFaceIter, self).__init__(miter, comp)

    def _next(self):
        self._miter.next(self._miter)

    def center(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MPoint
        return self.miter.center(space)

    def area(self, space=om2.MSpace.kObject):
        # type: (int) -> float
        return self.miter.getArea(space)

    def color(self, color_set=None, vertex_id=None):
        # type: (Union[ColorSet, str], int) -> om2.MColor
        if color_set is not None:
            color_set_name = _get_color_set_name(color_set)
            return self.miter.getColor(color_set_name)
        return self.miter.getColor(vertex_id)

    def color_index(self, vertex_id, color_set=None):
        # type: (int, Union[ColorSet, str]) -> int
        color_set_name = _get_color_set_name(color_set)
        return self.miter.getColorIndex(vertex_id, color_set_name)

    def color_indices(self, color_set=None):
        # type: (Union[ColorSet, str]) -> om2.MIntArray
        color_set_name = _get_color_set_name(color_set)
        return self.miter.getColorIndices(color_set_name)

    def colors(self, color_set=None):
        # type: (Union[ColorSet, str]) -> om2.MColorArray
        color_set_name = _get_color_set_name(color_set)
        return self.miter.getColors(color_set_name)

    def normal(self, space=om2.MSpace.kObject, vertex_id=None):
        # type: (int, int) -> om2.MVector
        if vertex_id is not None:
            return self.miter.getNormal(vertex_id, space)
        return self.miter.getNormal(space)

    def normals(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MVectorArray
        return self.miter.getNormals(space)

    def points(self, space=om2.MSpace.kObject):
        # type: (int) -> om2.MPointArray
        return self.miter.getPoints(space)

    def triangle(self, index, space=om2.MSpace.kObject):
        # type: (int, int) -> Dict[int, om2.MPoint]
        points, vertices = self.miter.getTriangle(index, space)
        result = {}
        for i, vertex_id in enumerate(vertices):
            result[vertex_id] = points[i]
        return result

    def triangles(self, space=om2.MSpace.kObject):
        # type: (int) -> List[Dict[int, om2.MPoint]]
        data = self.miter.getTriangles(space)
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

    def __init__(self, miter, comp):
        # type: (om2.MItMeshEdge, Component) -> NoReturn
        super(MeshEdgeIter, self).__init__(miter, comp)


class MeshVertexFaceIter(_Iterator):

    @property
    def face_index(self):
        # type: () -> int
        return self._miter.faceId()

    @property
    def vertex_index(self):
        # type: () -> int
        return self._miter.vertexId()

    def __init__(self, miter, comp):
        # type: (om2.MItMeshFaceVertex, Component) -> NoReturn
        super(MeshVertexFaceIter, self).__init__(miter, comp)


def _get_color_set_name(color_set):
    # type: (Union[ColorSet, str]) -> str
    if color_set is None:
        return None

    if isinstance(color_set, (str, unicode)):
        return color_set

    return color_set.mel_object


def _get_uv_set_name(uv_set):
    # type: (Union[UvSet, str]) -> str
    if uv_set is None:
        return None

    if isinstance(uv_set, (str, unicode)):
        return uv_set

    return uv_set.mel_object
