# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.cmds as cmds
import maya.api.OpenMaya as om2


class PlugFactory(object):

    _cls = None  # type: type

    @staticmethod
    def register(cls):
        # type: (type) -> NoReturn
        PlugFactory._cls = cls

    @staticmethod
    def create(mplug):
        # type: (om2.MPlug) -> object
        cls = PlugFactory._cls
        return cls(mplug)


def plug_get_impl(mplug):
    # type: (om2.MPlug) -> Any
    mobj = mplug.attribute()
    api_type = mobj.apiType()

    # array
    if mplug.isArray:
        return [plug_get_impl(mplug.elementByLogicalIndex(i)) for i in range(mplug.numElements())]

    # compound
    if mplug.isCompound:
        return tuple(plug_get_impl(mplug.child(i)) for i in range(mplug.numChildren()))

    try:
        # typed
        if api_type == om2.MFn.kTypedAttribute:
            attr_type = om2.MFnTypedAttribute(mobj).attrType()
            return _typed_attr_table[attr_type](mplug)

        # numeric
        if api_type == om2.MFn.kNumericAttribute:
            numeric_type = om2.MFnNumericAttribute(mobj).numericType()
            return _numeric_attr_table[numeric_type](mplug)

        return _api_type_table[api_type](mplug)

    except KeyError:
        print('not-supported plug data: {}'.format(mplug))
        return cmds.getAttr(mplug.name())


def _get_component_list_data(mplug):
    # type: (om2.MPlug) -> Tuple[int]
    mfn = om2.MFnComponentListData(mplug.asMObject())
    return tuple(mfn.get(i) for i in range(mfn.length()))


_api_type_table = {
    om2.MFn.kDoubleLinearAttribute: lambda plug: plug.asDouble(),
    om2.MFn.kFloatLinearAttribute: lambda plug: plug.asFloat(),
    om2.MFn.kDoubleAngleAttribute: lambda plug: plug.asMAngle().asUnits(om2.MAngle.uiUnit()),
    om2.MFn.kFloatAngleAttribute: lambda plug: plug.asMAngle().asUnits(om2.MAngle.uiUnit()),
    om2.MFn.kEnumAttribute: lambda plug: plug.asInt(),
    om2.MFn.kMatrixAttribute: lambda plug: om2.MFnMatrixAttribute(plug.asMObject()).matrix(),
}


_typed_attr_table = {
    om2.MFnData.kString: lambda plug: plug.asString(),
    om2.MFnData.kMatrix: lambda plug: om2.MFnMatrixData(plug.asMObject()).matrix(),
    om2.MFnData.kComponentList: _get_component_list_data,
}

_numeric_attr_table = {
    om2.MFnNumericData.kBoolean: lambda plug: plug.asBool(),
    om2.MFnNumericData.kInt: lambda plug: plug.asInt(),
    om2.MFnNumericData.kByte: lambda plug: plug.asInt(),
    om2.MFnNumericData.kShort: lambda plug: plug.asInt(),
    om2.MFnNumericData.kLong: lambda plug: plug.asInt(),
    om2.MFnNumericData.kDouble: lambda plug: plug.asDouble(),
    om2.MFnNumericData.kFloat: lambda plug: plug.asDouble(),
    om2.MFnNumericData.kAddr: lambda plug: plug.asDouble(),
}
