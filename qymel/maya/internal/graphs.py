import maya.cmds as _cmds
import maya.api.OpenMaya as _om2

from .types import *
from . import factory as _factory


# 呼び出し回数が極端に多くなる可能性のある静的メソッドをキャッシュ化しておく
_om2_MGlobal_getSelectionListByName = _om2.MGlobal.getSelectionListByName
_factory_PlugFactory_create = _factory.PlugFactory.create
_factory_NodeFactory_create = _factory.NodeFactory.create
_factory_NodeFactory_create_default = _factory.NodeFactory.create_default
_factory_ComponentFactory_create = _factory.ComponentFactory.create
_factory_ComponentFactory_create_default = _factory.ComponentFactory.create_default


def ls(*args: str, **kwargs: object) -> list[TDependNode|TPlug|TComponent]:
    if kwargs.get('objectsOnly', False):
        return ls_nodes(*args, **kwargs)

    kwargs['long'] = True
    tmp_mfn_node = _om2.MFnDependencyNode()
    tmp_mfn_comp = _om2.MFnComponent()
    return [eval(name, tmp_mfn_comp, tmp_mfn_node) for name in _cmds.ls(*args, **kwargs)]


def ls_nodes(*args: str, **kwargs: object) -> list[TComponent]:
    result = []

    kwargs['long'] = True
    kwargs['objectsOnly'] = True
    tmp_mfn = _om2.MFnDependencyNode()

    for node_name in _cmds.ls(*args, **kwargs):
        node = eval_node(node_name, tmp_mfn)
        if node is not None:
            result.append(node)

    return result


def eval(
        obj_name: str,
        tmp_mfn_comp: _om2.MFnComponent,
        tmp_mfn_node: _om2.MFnDependencyNode
) -> TDependNode|TPlug|TComponent|None:
    if '.' in obj_name:
        plug = eval_plug(obj_name)
        if plug is not None:
            return plug

        comp = eval_component(obj_name, tmp_mfn_comp)
        if comp is not None:
            return comp

    else:
        node = eval_node(obj_name, tmp_mfn_node)
        if node is not None:
            return node

    raise RuntimeError('unknown object type: {}'.format(obj_name))


def eval_plug(plug_name: str) -> TPlug|None:
    mplug = None
    try:
        mplug = get_mplug(plug_name)
    except TypeError:
        pass

    if mplug is not None:
        plug = _factory_PlugFactory_create(mplug)
        return plug

    return None


def eval_component(comp_name: str, tmp_mfn_comp: _om2.MFnComponent) -> TComponent|None:
    mdagpath = None
    mobj = None
    try:
        mdagpath, mobj = get_comp_mobject(comp_name)
    except TypeError:
        pass

    if mdagpath is not None:
        tmp_mfn_comp.setObject(mobj)
        comp = to_comp_instance(tmp_mfn_comp, mdagpath, mobj)
        return comp

    return None


def eval_node(node_name: str, tmp_mfn_node: _om2.MFnDependencyNode) -> TDependNode|None:
    if '.' in node_name:
        raise TypeError('invalid node: {}'.format(node_name))

    mobj, mdagpath = get_mobject(node_name)

    if mobj.hasFn(_om2.MFn.kDependencyNode):
        tmp_mfn_node.setObject(mobj)
        node = to_node_instance(tmp_mfn_node, mdagpath)
        return node

    return None


def create_node(*args: str, **kwargs: object) -> TDependNode:
    node_name = _cmds.createNode(*args, **kwargs)
    mobj, mdagpath = get_mobject(node_name)
    return to_node_instance(_om2.MFnDependencyNode(mobj), mdagpath)


def to_node_instance(mfn: _om2.MFnDependencyNode, mdagpath: _om2.MDagPath|None = None) -> TDependNode:
    type_name = mfn.typeName
    mobj = mfn.object()

    node = _factory_NodeFactory_create(type_name, mobj, mdagpath)
    if node is not None:
        return node

    return _factory_NodeFactory_create_default(mfn, mdagpath)


def get_mobject(node_name: str) -> tuple[_om2.MObject, _om2.MDagPath|None]:
    sel = _om2_MGlobal_getSelectionListByName(node_name)
    mobj = sel.getDependNode(0)

    if mobj.hasFn(_om2.MFn.kDagNode):
        return mobj, sel.getDagPath(0)

    return mobj, None


def get_world_mobject() -> _om2.MObject:
    ite = _om2.MItDag()
    while not ite.isDone():
        mobj = ite.currentItem()
        if mobj.hasFn(_om2.MFn.kWorld):
            return mobj
    raise RuntimeError('cannot find the MObject of the World')


def _to_plug_instance(mplug: _om2.MPlug) -> TPlug:
    return _factory_PlugFactory_create(mplug)


def to_comp_instance(mfn: _om2.MFnComponent, mdagpath: _om2.MDagPath, mobject: _om2.MObject) -> TComponent:
    comp_type = mfn.componentType

    comp = _factory_ComponentFactory_create(comp_type, mdagpath, mobject)
    if comp is not None:
        return comp

    return _factory_ComponentFactory_create_default(mdagpath, mobject)


def get_mplug(name: str) -> _om2.MPlug:
    sel = _om2_MGlobal_getSelectionListByName(name)
    return sel.getPlug(0)


def keep_mplug(mplug: _om2.MPlug) -> _om2.MPlug:
    u"""
    ネットワークプラグをGC管理下から外すためのメソッド
      ネットワークプラグはメモリ管理がMaya内部で行われるので
      内部でdeleteされないようにノンネットワークプラグに変換しておく
    """
    if not mplug.isNetworked:
        return mplug

    # 新規ノンネットワークプラグをつくって中身を全部移植する
    # https://github.com/ryusas/cymel/blob/05089ea6e34c79723590e9350dc45d5c970fd8f4/python/cymel/core/cyobjects/python/_api2mplug.py#L149
    mattr = mplug.attribute()

    if mplug.isElement:
        index_attrs = [(mplug.logicalIndex(), mattr)]
        mp = mplug.array()
    else:
        index_attrs = []
        mp = mplug

    while mp.isChild:
        mp = mp.parent()
        if mp.isElement:
            index_attrs.append((mp.logicalIndex(), mp.attribute()))
            mp = mp.array()

    mplug = _om2.MPlug(mplug.node(), mattr)
    for index, attr in index_attrs:
        mplug.selectAncestorLogicalIndex(index, attr)

    return mplug


def get_comp_mobject(name: str) -> tuple[_om2.MDagPath, _om2.MObject]:
    sel = _om2_MGlobal_getSelectionListByName(name)
    return sel.getComponent(0)


def connections(mfn: _om2.MFnDependencyNode) -> list[_om2.MObject]:
    result = []

    for i in range(mfn.attributeCount()):
        attr = mfn.attribute(i)
        plug = mfn.findPlug(attr, True)
        for other in plug.connectedTo(True, True):
            result.append(other)

    return result
