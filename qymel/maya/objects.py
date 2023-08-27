# coding: utf-8
from typing import *

import maya.api.OpenMaya as _om2


# 呼び出し回数が極端に多くなる可能性のある静的メソッドをキャッシュ化しておく
_om2_MObjectHandle = _om2.MObjectHandle


_TObj = TypeVar('_TObj', bound='MayaObject')


class MayaObject(object):

    @property
    def mobject(self) -> _om2.MObject:
        return self._mobj_handle.object()

    @property
    def mobject_handle(self) -> _om2.MObjectHandle:
        return self._mobj_handle

    @property
    def is_null(self) -> bool:
        return self.mobject.isNull()

    @property
    def mel_object(self) -> Union[str, Tuple[str]]:
        raise NotImplementedError()

    @property
    def exists(self) -> bool:
        return not self.is_null

    @property
    def api_type(self) -> int:
        return self.mobject.apiType()

    @property
    def api_type_str(self) -> str:
        return self.mobject.apiTypeStr

    def __init__(self, mobj: _om2.MObject) -> None:
        if mobj is not None:
            self._mobj_handle = _om2_MObjectHandle(mobj)
        else:
            self._mobj_handle = None

    def __eq__(self, other: Union[_TObj, Any]) -> bool:
        if other is None or not isinstance(other, MayaObject):
            return False
        if not other._mobj_handle.isValid():
            return False
        return self._mobj_handle.hashCode() == other._mobj_handle.hashCode()

    def __ne__(self, other: Union[_TObj, Any]) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return self._mobj_handle.hashCode()

    def __str__(self) -> str:
        return f'{self.__class__} {self.mobject}'

    def has_fn(self, mfn_type: int) -> bool:
        return self.mobject.hasFn(mfn_type)
