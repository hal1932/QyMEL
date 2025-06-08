import typing
import abc

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2
import maya.OpenMaya as _om

from .internal.types import *

if typing.TYPE_CHECKING:
    from . import components as _components
    from . import general as _general

TMItComp = typing.TypeVar('TMItComp', _om2.MItMeshVertex, _om2.MItMeshEdge, _om2.MItMeshPolygon, _om2.MItMeshFaceVertex)
TColorSet = typing.TypeVar('TColorSet', _general.ColorSet, str)
TUvSet = typing.TypeVar('TUvSet', _general.UvSet, str)


class ComponentIter(typing.Generic[TMItComp]):

    @property
    def miter(self) -> TMItComp:
        return self._miter

    @property
    def mobject(self) -> _om2.MObject:
        return self._miter.currentItem()

    @property
    @abc.abstractmethod
    def mel_object(self) -> str:
        raise NotImplementedError()

    def __init__(self, miter: TMItComp, comp: _components.Component) -> None:
        self._miter = miter
        self._comp = comp  # 使う機会はないけど、ループの最中にcompのスコープが切れないように手許で抱えておく
        self.__is_first = True

    def __getattr__(self, item: str) -> object:
        return getattr(self._miter, item)

    def __iter__(self):
        return self

    def next(self):
        return self.__next__()

    def __next__(self):
        if self.__is_first:
            self.__is_first = False
            return self

        self._miter.next()

        if self._miter.isDone():
            raise StopIteration()

        return self


class MeshVertexIter(ComponentIter[_om2.MItMeshVertex]):

    @property
    def mel_object(self) -> str:
        return f'{self._mfn_mesh.fullPathName()}.vtx[{self.index}]'

    @property
    def index(self) -> int:
        return self._miter.index()

    @property
    def connected_edge_indices(self) -> _om2.MIntArray:
        return self._miter.getConnectedEdges()

    @property
    def connected_edge_count(self) -> int:
        return self._miter.numConnectedEdges()

    @property
    def connected_face_indices(self) -> _om2.MIntArray:
        return self._miter.getConnectedFaces()

    @property
    def connected_face_count(self) -> int:
        return self._miter.numConnectedFaces()

    @property
    def connected_vertex_indices(self) -> _om2.MIntArray:
        return self._miter.getConnectedVertices()

    @property
    def on_boundary(self) -> bool:
        return self._miter.onBoundary()

    def __init__(self, miter: _om2.MItMeshVertex, comp: _components.Component, mfn_mesh: _om2.MFnMesh) -> None:
        super(MeshVertexIter, self).__init__(miter, comp)
        self._mfn_mesh = mfn_mesh

    def has_color(self, face_id: int|None = None) -> bool:
        if face_id is not None:
            return self._miter.hasColor(face_id)
        return self._miter.hasColor()

    def color(self, face_id: int|None = None, color_set: TColorSet|None = None) -> _om2.MColor:
        color_set_name = _get_color_set_name(color_set, None)
        if face_id is not None:
            raise RuntimeError('executing this method with face_id cannot used due to Maya\'s problem')
            # このまま実行するとTypeErrorになる
            # > TypeError: function takes at most 1 argument (2 given)
            # return self._miter.getColor(face_id, color_set_name)
        return self._miter.getColor(color_set_name)

    def colors(self, color_set: TColorSet|None = None) -> _om2.MColorArray:
        color_set_name = _get_color_set_name(color_set, None)
        return self._miter.getColors(color_set_name)

    def color_indices(self, color_set: TColorSet|None = None) -> _om2.MIntArray:
        color_set_name = _get_color_set_name(color_set, None)
        return self._miter.getColorIndices(color_set_name)

    def normal(self, face_id: int|None = None, space: int = _om2.MSpace.kObject) -> _om2.MVector:
        if face_id is not None:
            raise RuntimeError('executing this method with face_id cannot used due to Maya\'s problem')
            # このまま実行するとMayaが落ちる
            # return self._miter.getNormals(face_id, space)
        return self._mfn_mesh.getVertexNormal(self.index, True, space)

    def normal_indices(self) -> _om2.MIntArray:
        return self._miter.getNormalIndices()

    def normals(self, space: int = _om2.MSpace.kObject) -> _om2.MVectorArray:
        return self._miter.getNormals(space)

    def uv(self, uv_set: TUvSet|None = None) -> list[float]:
        uv_set_name = _get_uv_set_name(uv_set, None)
        return self._miter.getUV(uv_set_name)

    def uv_indices(self, uv_set: TUvSet|None = None) -> _om2.MIntArray:
        uv_set_name = _get_uv_set_name(uv_set, None)
        return self._miter.getUVIndices(uv_set_name)

    def uvs(self, uv_set: TUvSet|None = None) -> dict[int, tuple[float, float]]:
        uv_set_name = _get_uv_set_name(uv_set, None)
        us, vs, face_ids = self._miter.getUVs(uv_set_name)

        result = {}  # type: dict[int, tuple[float, float]]
        for i, face_id in enumerate(face_ids):
            result[face_id] = us[i], vs[i]

        return result

    def uv_count(self, uv_set: TUvSet|None = None) -> int:
        uv_set_name = _get_uv_set_name(uv_set, None)
        return self._miter.numUVs(uv_set_name)

    def position(self, space: int = _om2.MSpace.kObject) -> _om2.MPoint:
        return self._miter.position(space)


class MeshFaceIter(ComponentIter[_om2.MItMeshPolygon]):

    @property
    def mel_object(self) -> str:
        return f'{self._mfn_mesh.fullPathName(())}.f[{self.index}]'

    @property
    def index(self) -> int:
        return self._miter.index()

    @property
    def connected_edge_indices(self) -> _om2.MIntArray:
        return self._miter.getConnectedEdges()

    @property
    def connected_face_indices(self) -> _om2.MIntArray:
        return self._miter.getConnectedFaces()

    @property
    def connected_vertex_indices(self) -> _om2.MIntArray:
        return self._miter.getConnectedVertices()

    @property
    def edge_indices(self) -> _om2.MIntArray:
        return self._miter.getEdges()

    @property
    def vertex_indices(self) -> _om2.MIntArray:
        return self._miter.getVertices()

    @property
    def is_convex(self) -> bool:
        return self._miter.isConvex()

    @property
    def is_lamina(self) -> bool:
        return self._miter.isLamina()

    @property
    def is_planar(self) -> bool:
        return self._miter.isPlanar()

    @property
    def on_boundary(self) -> bool:
        return self._miter.onBoundary()

    @property
    def is_zero_area(self) -> bool:
        return self._miter.zeroArea()

    @property
    def triangle_count(self) -> int:
        return self._miter.numTriangles()

    def __init__(self, miter: _om2.MItMeshPolygon, comp: _components.Component, mfn_mesh: _om2.MFnMesh) -> None:
        super(MeshFaceIter, self).__init__(miter, comp)
        self._mfn_mesh = mfn_mesh

    def _next(self) -> None:
        if _om.MGlobal.apiVersion() >= 20220000:
            self._miter.next()
        else:
            self._miter.next(self._miter)

    def center(self, space: int = _om2.MSpace.kObject) -> _om2.MPoint:
        return self._miter.center(space)

    def area(self, space: int = _om2.MSpace.kObject) -> float:
        return self._miter.getArea(space)

    def normal(self, vertex_id: int|None = None, space: int = _om2.MSpace.kObject) -> _om2.MVector:
        if vertex_id is not None:
            raise RuntimeError('executing this method with face_id cannot used due to Maya\'s problem')
            # このまま実行するとMayaが落ちる
            # return self._miter.getNormal(vertex_id, space)
        return self._miter.getNormal(space)

    def normals(self, space: int = _om2.MSpace.kObject) -> _om2.MVectorArray:
        return self._miter.getNormals(space)

    def points(self, space: int = _om2.MSpace.kObject) -> _om2.MPointArray:
        return self._miter.getPoints(space)

    def triangle(self, index: int, space: int = _om2.MSpace.kObject) -> dict[int, _om2.MPoint]:
        points, vertices = self._miter.getTriangle(index, space)
        result = {}
        for i, vertex_id in enumerate(vertices):
            result[vertex_id] = points[i]
        return result

    def triangles(self, space: int = _om2.MSpace.kObject) -> list[dict[int, _om2.MPoint]]:
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


class MeshEdgeIter(ComponentIter[_om2.MItMeshEdge]):

    @property
    def mel_object(self) -> str:
        return f'{self._mfn_mesh.fullPathName()}.e[{self.index}]'

    @property
    def index(self) -> int:
        return self._miter.index()

    @property
    def connected_edge_indices(self) -> _om2.MIntArray:
        return self._miter.getConnectedEdges()

    @property
    def connected_face_indices(self) -> _om2.MIntArray:
        return self._miter.getConnectedFaces()

    @property
    def vertex_indices(self) -> _om2.MIntArray:
        return _om2.MIntArray([self._miter.vertexId(0), self._miter.vertexId(1)])

    @property
    def on_boundary(self) -> bool:
        return self._miter.onBoundary()

    @property
    def is_smooth(self) -> bool:
        return self._miter.isSmooth

    def __init__(self, miter: _om2.MItMeshEdge, comp: _components.Component, mfn_mesh: _om2.MFnMesh) -> None:
        super(MeshEdgeIter, self).__init__(miter, comp)
        self._mfn_mesh = mfn_mesh

    def center(self, space: int = _om2.MSpace.kObject) -> _om2.MPoint:
        return self._miter.center(space)

    def length(self, space: int = _om2.MSpace.kObject) -> float:
        return self._miter.length(space)

    def points(self, space: int = _om2.MSpace.kObject) -> _om2.MPointArray:
        return _om2.MPointArray([self._miter.point(0, space), self._miter.point(1, space)])


class MeshFaceVertexIter(ComponentIter[_om2.MItMeshFaceVertex]):

    @property
    def mel_object(self) -> str:
        vtx_id, face_id = self.index
        return f'{self._mfn_mesh.fullPathName()}.f[{vtx_id}][{face_id}]'

    @property
    def index(self) -> tuple[int, int]:
        miter = self._miter
        return miter.vertexId(), miter.faceId()

    @property
    def face_index(self) -> int:
        return self._miter.faceId()

    @property
    def vertex_index(self) -> int:
        return self._miter.vertexId()

    @property
    def face_vertex_index(self) -> int:
        return self._miter.faceVertexId()

    @property
    def has_color(self) -> bool:
        return self._miter.hasColor()

    def __init__(self, miter: _om2.MItMeshFaceVertex, comp: _components.Component, mfn_mesh: _om2.MFnMesh) -> None:
        super(MeshFaceVertexIter, self).__init__(miter, comp)
        self._mfn_mesh = mfn_mesh

    def color(self, color_set: TColorSet|None = None) -> _om2.MColor:
        color_set_name = _get_color_set_name(color_set, '')
        return self._miter.getColor(color_set_name)

    def color_index(self, color_set: TColorSet|None = None) -> int:
        color_set_name = _get_color_set_name(color_set, '')
        return self._miter.getColorIndex(color_set_name)

    def normal(self, space: int = _om2.MSpace.kObject) -> _om2.MVector:
        return self._miter.getNormal(space)

    def tangent(self, space: int = _om2.MSpace.kObject, uv_set=None) -> _om2.MVector:
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getTangent(space, uv_set_name)

    def binormal(self, space: int = _om2.MSpace.kObject, uv_set: TUvSet|None = None) -> _om2.MVector:
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getBinormal(space, uv_set_name)

    def normal_index(self):
        # type: () -> int
        return self._miter.normalId()

    def tangent_index(self):
        # type: () -> int
        return self._miter.tangentId()

    def uv(self, uv_set: TUvSet|None = None) -> tuple[float, float]:
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getUV(uv_set_name)

    def uv_index(self, uv_set: TUvSet|None = None) -> int:
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.getUVIndex(uv_set_name)

    def has_uv(self, uv_set: TUvSet|None = None) -> bool:
        uv_set_name = _get_uv_set_name(uv_set, 'map1')
        return self._miter.hasUVs(uv_set_name)

    def position(self, space: int = _om2.MSpace.kObject) -> _om2.MPoint:
        return self._miter.position(space)


def _get_color_set_name(color_set: TColorSet|None, default_value: str|None) -> str:
    if color_set is None:
        return default_value

    if isinstance(color_set, str):
        return color_set

    return color_set.mel_object


def _get_uv_set_name(uv_set: TUvSet|None, default_value: str|None) -> str:
    if uv_set is None:
        return default_value

    if isinstance(uv_set, str):
        return uv_set

    return uv_set.mel_object
