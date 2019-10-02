# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.api.OpenMaya as om2


class _Iterator(object):

    @property
    def index(self):
        # type: () -> int
        return self._miter.index()

    def __init__(self, miter):
        self._miter = miter
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


class MeshVertexIterator(_Iterator):

    def __init__(self, miter):
        # type: (om2.MItMeshVertex) -> NoReturn
        super(MeshVertexIterator, self).__init__(miter)


class MeshFaceIter(_Iterator):

    def __init__(self, miter):
        # type: (om2.MItMeshPolygon) -> NoReturn
        super(MeshFaceIter, self).__init__(miter)

    def _next(self):
        self._miter.next(self._miter)


class MeshEdgeIter(_Iterator):

    def __init__(self, miter):
        # type: (om2.MItMeshEdge) -> NoReturn
        super(MeshEdgeIter, self).__init__(miter)


class MeshVertexFaceIter(_Iterator):

    @property
    def face_index(self):
        # type: () -> int
        return self._miter.faceId()

    @property
    def vertex_index(self):
        # type: () -> int
        return self._miter.vertexId()

    def __init__(self, miter):
        # type: (om2.MItMeshFaceVertex) -> NoReturn
        super(MeshVertexFaceIter, self).__init__(miter)
