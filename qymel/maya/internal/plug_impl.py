import maya.cmds as _cmds
import maya.api.OpenMaya as _om2


def plug_get_impl(mplug: _om2.MPlug) -> object:
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
        if api_type == _om2.MFn.kTypedAttribute:
            attr_type = _om2.MFnTypedAttribute(mobj).attrType()
            return _typed_attr_table[attr_type](mplug)

        # numeric
        if api_type == _om2.MFn.kNumericAttribute:
            numeric_type = _om2.MFnNumericAttribute(mobj).numericType()
            return _numeric_attr_table[numeric_type](mplug)

        # # generic
        # if api_type == _om2.MFn.kGenericAttribute:
        #     pass

        return _api_type_table[api_type](mplug)

    except:
        # print('not-supported plug data: {}, {}'.format(mplug, mobj.apiTypeStr))
        return _cmds.getAttr(mplug.name())


def _get_component_list_data(mplug: _om2.MPlug) -> tuple[object, ...]:
    mfn = _om2.MFnComponentListData(mplug.asMObject())
    return tuple(mfn.get(i) for i in range(mfn.length()))


_api_type_table = {
    _om2.MFn.kDoubleLinearAttribute: lambda plug: plug.asMDistance().asUnits(_om2.MDistance.uiUnit()),
    _om2.MFn.kFloatLinearAttribute: lambda plug: plug.asMDistance().asUnits(_om2.MDistance.uiUnit()),
    _om2.MFn.kDoubleAngleAttribute: lambda plug: plug.asMAngle().asUnits(_om2.MAngle.uiUnit()),
    _om2.MFn.kFloatAngleAttribute: lambda plug: plug.asMAngle().asUnits(_om2.MAngle.uiUnit()),
    _om2.MFn.kEnumAttribute: lambda plug: plug.asInt(),
    _om2.MFn.kMatrixAttribute: lambda plug: _om2.MFnMatrixData(plug.asMObject()).matrix(),
    _om2.MFn.kFloatMatrixAttribute: lambda plug: _om2.MFnMatrixData(plug.asMObject()).matrix(),
    _om2.MFn.kTimeAttribute: lambda plug: plug.asMTime().asUnits(_om2.MTime.uiUnit()),
}


_typed_attr_table = {
    _om2.MFnData.kInvalid: lambda _: None,
    _om2.MFnData.kString: lambda plug: plug.asString(),
    _om2.MFnData.kStringArray: lambda plug: _om2.MFnStringArrayData(plug.asMObject()).array(),
    _om2.MFnData.kIntArray: lambda plug: _om2.MFnIntArrayData(plug.asMObject()).array(),
    _om2.MFnData.kFloatArray: lambda plug: _om2.MFnDoubleArrayData(plug.asMObject()).array(),
    _om2.MFnData.kDoubleArray: lambda plug: _om2.MFnDoubleArrayData(plug.asMObject()).array(),
    _om2.MFnData.kVectorArray: lambda plug: _om2.MFnVectorArrayData(plug.asMObject()).array(),
    _om2.MFnData.kMatrix: lambda plug: _om2.MFnMatrixData(plug.asMObject()).matrix(),
    _om2.MFnData.kComponentList: _get_component_list_data,
}

_numeric_attr_table = {
    _om2.MFnNumericData.kBoolean: lambda plug: plug.asBool(),
    _om2.MFnNumericData.kInt: lambda plug: plug.asInt(),
    _om2.MFnNumericData.kByte: lambda plug: plug.asInt(),
    _om2.MFnNumericData.kShort: lambda plug: plug.asInt(),
    _om2.MFnNumericData.kLong: lambda plug: plug.asInt(),
    _om2.MFnNumericData.kDouble: lambda plug: plug.asDouble(),
    _om2.MFnNumericData.kFloat: lambda plug: plug.asDouble(),
    _om2.MFnNumericData.kAddr: lambda plug: plug.asDouble(),
}
