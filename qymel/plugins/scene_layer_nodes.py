# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.api.OpenMaya as om2
import maya.cmds as cmds

import qymel.core as qm


class SceneLayerNode(om2.MPxNode):

    name = 'qmSceneLayer'
    type_id = om2.MTypeId(0x7FF)
    node_type = om2.MPxNode.kDependNode
    classification = 'utility/general'

    filePath = om2.MObject()
    namespace = om2.MObject()
    elements = om2.MObject()
    children = om2.MObject()

    @staticmethod
    def create():
        # type: () -> om2.MPxNode
        return SceneLayerNode()

    @staticmethod
    def initialize():
        # type: () -> NoReturn
        str_attr = om2.MFnTypedAttribute()

        SceneLayerNode.filePath = str_attr.create('filePath', 'f', om2.MFnData.kString)
        str_attr.readable = True
        str_attr.writable = True
        str_attr.storable = True
        str_attr.connectable = False
        SceneLayerNode.addAttribute(SceneLayerNode.filePath)

        SceneLayerNode.namespace = str_attr.create('namespace', 'ns', om2.MFnData.kString)
        str_attr.readable = True
        str_attr.writable = True
        str_attr.storable = True
        str_attr.connectable = False
        SceneLayerNode.addAttribute(SceneLayerNode.namespace)

        msg_attr = om2.MFnMessageAttribute()

        SceneLayerNode.elements = msg_attr.create('elements', 'e')
        msg_attr.array = True
        msg_attr.readable = False
        msg_attr.indexMatters = False
        msg_attr.connectable = True
        SceneLayerNode.addAttribute(SceneLayerNode.elements)

        SceneLayerNode.children = msg_attr.create('children', 'c')
        msg_attr.array = True
        msg_attr.readable = False
        msg_attr.indexMatters = False
        msg_attr.connectable = True
        SceneLayerNode.addAttribute(SceneLayerNode.children)

    def __init__(self):
        super(SceneLayerNode, self).__init__()


qm.setup_plugin(
    globals(),
    [
        qm.NodePluginSetup(SceneLayerNode.name, SceneLayerNode.type_id, SceneLayerNode.create, SceneLayerNode.initialize, SceneLayerNode.node_type, SceneLayerNode.classification),
    ],
    '@hal1932', '0.0.1', 'Any'
)
