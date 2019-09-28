# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.api.OpenMaya as om2

from qymel.internal.graphs import _ls, _ls_nodes, _create_node
from qymel.internal.objects import _PlugFactory, _ComponentFactory


def ls(*args, **kwargs):
    return _ls(*args, **kwargs)


class MayaObject(object):

    @property
    def mobject(self):
        # type: () -> om2.MObject
        return self._mobj_handle.object()

    @property
    def mobj_handle(self):
        # type: () -> om2.MObjectHandle
        return self._mobj_handle

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        self._mobj_handle = om2.MObjectHandle(mobj)

    def __eq__(self, other):
        # type: (object) -> bool
        if other is None:
            return False
        if not isinstance(other, MayaObject):
            return False
        return self.mobject == other.mobject

    def __hash__(self):
        # type: () -> long
        return self.mobj_handle.hashCode()

    def __str__(self):
        # type: () -> str
        return '{} {}'.format(self.__class__, self.mobject)


class Plug(object):

    @property
    def mplug(self):
        # type: () -> om2.MPlug
        return self._mplug

    @property
    def name(self):
        # type: () -> str
        return self.mplug.name()

    @property
    def partial_name(self):
        # type: () -> str
        return self.mplug.partialName()

    def __init__(self, mplug):
        # type: (om2.MPlug) -> NoReturn
        self._mplug = mplug

    def __str__(self):
        # type: () -> str
        return '{} {}'.format(self.__class__, self.name)


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

    def __init__(self, mdagpath, mobj):
        # type: (om2.MDagPath, om2.MObject) -> NoReturn
        super(Component, self).__init__(mobj)
        self._mdagpath = mdagpath
        self._mfn = None

    def __str__(self):
        # type: () -> str
        return '{} {} (count: {})'.format(self.__class__, self.mdagpath.fullPathName(), self.mfn.elementCount)

    def __len__(self):
        # type: () -> int
        return self.mfn.elementCount


class MeshVertexComponent(Component):

    _comp_mfn = om2.MFnSingleIndexedComponent
    _comp_type = om2.MFn.kMeshVertComponent

    def __init__(self, mdagpath, mobj):
        # type: (om2.MDagPath, om2.MObject) -> NoReturn
        super(MeshVertexComponent, self).__init__(mdagpath, mobj)


_PlugFactory.register(Plug)
_ComponentFactory.register(__name__)
