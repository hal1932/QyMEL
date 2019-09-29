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
    result = []

    kwargs['long'] = True
    tmp_mfn_node = om2.MFnDependencyNode()
    tmp_mfn_comp = om2.MFnComponent()

    for obj_name in cmds.ls(*args, **kwargs):
        if '.' in obj_name:
            mplug = None
            try:
                mplug = _get_mplug(obj_name)
            except TypeError:
                pass

            if mplug is not None:
                plug = _PlugFactory.create(mplug)
                result.append(plug)
                continue

            mdagpath = None
            mobj = None
            try:
                mdagpath, mobj = _get_comp_mobject(obj_name)
            except TypeError:
                pass

            if mdagpath is not None:
                tmp_mfn_comp.setObject(mobj)
                comp = _to_comp_instance(tmp_mfn_comp, mdagpath, mobj)
                result.append(comp)
                continue

        else:
            mobj = _get_mobject(obj_name)
            if mobj.hasFn(om2.MFn.kDependencyNode):
                tmp_mfn_node.setObject(mobj)
                node = _to_node_instance(tmp_mfn_node)
                result.append(node)
                continue

        raise RuntimeError('unknown object type: {}'.format(obj_name))

    return result


def _ls_nodes(*args, **kwargs):
    result = []

    kwargs['long'] = True
    kwargs['objectsOnly'] = True
    tmp_mfn = om2.MFnDependencyNode()

    for node_name in cmds.ls(*args, **kwargs):
        mobj = _get_mobject(node_name)
        if not mobj.hasFn(om2.MFn.kDependencyNode):
            return None

        tmp_mfn.setObject(mobj)

        node = _to_node_instance(tmp_mfn)
        if node is not None:
            result.append(node)

    return result


def _create_node(*args, **kwargs):
    node_name = cmds.createNode(*args, **kwargs)
    mobj = _get_mobject(node_name)
    return _to_node_instance(om2.MFnDependencyNode(mobj))


def _to_node_instance(mfn):
    # type: (om2.MFnDependencyNode) -> object
    type_name = mfn.typeName
    mobj = mfn.object()

    node = _NodeFactory.create(type_name, mobj)
    if node is not None:
        return node

    if mobj.hasFn(om2.MFn.kDagNode):
        return _NodeFactory.create_default_dag(mobj)

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
    # type: (str) -> om2.MObject
    sel = om2.MSelectionList()
    sel.add(node_name)
    return sel.getDependNode(0)


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
