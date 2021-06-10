# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *

import maya.api.OpenMaya as _om2


_TObj = TypeVar('_TObj', bound='MayaObject')


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
        # type: (Union[_TObj, Any]) -> bool
        if other is None or not isinstance(other, MayaObject):
            return False
        if not other._mobj_handle.isValid():
            return False
        return self._mobj_handle.hashCode() == other._mobj_handle.hashCode()

    def __ne__(self, other):
        # type: (Union[_TObj, Any]) -> bool
        return not self.__eq__(other)

    def __hash__(self):
        # type: () -> integer_types
        return self._mobj_handle.hashCode()

    def __str__(self):
        # type: () -> str
        return '{} {}'.format(self.__class__, self.mobject)

    def has_fn(self, mfn_type):
        # type: (int) -> bool
        return self.mobject.hasFn(mfn_type)
