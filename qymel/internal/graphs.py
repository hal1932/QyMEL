# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.cmds as cmds
import maya.api.OpenMaya as om2

from qymel.internal.nodes import _NodeFactory
from qymel.internal.plugs import _PlugFactory
from qymel.internal.components import _ComponentFactory


def _ls(*args, **kwargs):
    # type: (Any, Any) -> Any
    result = []

    kwargs['long'] = True
    tmp_mfn_node = om2.MFnDependencyNode()
    tmp_mfn_comp = om2.MFnComponent()

    # 自前でノードを辿るより ls のほうが速い
    for obj_name in cmds.ls(*args, **kwargs):
        obj = _eval(obj_name, tmp_mfn_comp, tmp_mfn_node)
        result.append(obj)

    return result


def _ls_nodes(*args, **kwargs):
    result = []

    kwargs['long'] = True
    kwargs['objectsOnly'] = True
    tmp_mfn = om2.MFnDependencyNode()

    for node_name in cmds.ls(*args, **kwargs):
        node = _eval_node(node_name, tmp_mfn)
        if node is not None:
            result.append(node)

    return result


def _eval(obj_name, tmp_mfn_comp, tmp_mfn_node):
    # type: (str, om2.MFnComponent, om2.MFnDependencyNode) -> Any
    if '.' in obj_name:
        plug = _eval_plug(obj_name)
        if plug is not None:
            return plug

        comp = _eval_component(obj_name, tmp_mfn_comp)
        if comp is not None:
            return comp

    else:
        node = _eval_node(obj_name, tmp_mfn_node)
        if node is not None:
            return node

    raise RuntimeError('unknown object type: {}'.format(obj_name))


def _eval_plug(plug_name):
    # type: (str) -> Any
    mplug = None
    try:
        mplug = _get_mplug(plug_name)
    except TypeError:
        pass

    if mplug is not None:
        plug = _PlugFactory.create(mplug)
        return plug

    return None


def _eval_component(comp_name, tmp_mfn_comp):
    # type: (str, om2.MFnComponent) -> Any
    mdagpath = None
    mobj = None
    try:
        mdagpath, mobj = _get_comp_mobject(comp_name)
    except TypeError:
        pass

    if mdagpath is not None:
        tmp_mfn_comp.setObject(mobj)
        comp = _to_comp_instance(tmp_mfn_comp, mdagpath, mobj)
        return comp

    return None


def _eval_node(node_name, tmp_mfn_node):
    # type: (str, om2.MFnDependencyNode) -> Any
    mobj, mdagpath = _get_mobject(node_name)

    if mobj.hasFn(om2.MFn.kDependencyNode):
        tmp_mfn_node.setObject(mobj)
        node = _to_node_instance(tmp_mfn_node, mdagpath)
        return node

    return None


def _create_node(*args, **kwargs):
    node_name = cmds.createNode(*args, **kwargs)
    mobj, mdagpath = _get_mobject(node_name)
    return _to_node_instance(om2.MFnDependencyNode(mobj), mdagpath)


def _to_node_instance(mfn, mdagpath):
    # type: (om2.MFnDependencyNode, om2.MDagPath) -> object
    type_name = mfn.typeName
    mobj = mfn.object()

    node = _NodeFactory.create(type_name, mobj, mdagpath)
    if node is not None:
        return node

    return _NodeFactory.create_default(mobj)


def _to_plug_instance(mplug):
    # type: (om2.MPlug) -> object
    return _PlugFactory.create(mplug)


def _to_comp_instance(mfn, mdagpath, mobject):
    # type: (om2.MFnComponent, om2.MDagPath, om2.MObject) -> object
    comp_type = mfn.componentType

    comp = _ComponentFactory.create(comp_type, mdagpath, mobject)
    if comp is not None:
        return comp

    return _ComponentFactory.create_default(mdagpath, mobject)


def _get_mobject(node_name):
    # type: (str) -> (om2.MObject, om2.MDagPath)
    sel = om2.MSelectionList()
    sel.add(node_name)
    mobj = sel.getDependNode(0)

    if mobj.hasFn(om2.MFn.kDagNode):
        return mobj, sel.getDagPath(0)

    return mobj, None


def _get_world_mobject():
    # type: () -> om2.MObject
    iter = om2.MItDag()
    while not iter.isDone():
        mobj = iter.currentItem()
        if mobj.hasFn(om2.MFn.kWorld):
            return mobj
    raise RuntimeError('cannot find the MObject of the World')


def _get_mplug(name):
    # type: (str) -> om2.MPlug
    sel = om2.MSelectionList()
    sel.add(name)
    return sel.getPlug(0)


def _get_comp_mobject(name):
    # type: (str) -> (om2.MDagPath, om2.MObject)
    sel = om2.MSelectionList()
    sel.add(name)
    return sel.getComponent(0)
