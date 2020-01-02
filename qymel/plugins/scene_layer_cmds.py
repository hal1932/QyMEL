# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import os
import collections

import maya.api.OpenMaya as om2
# import maya.OpenMaya as om
import maya.cmds as cmds

import qymel.core as qm


class _QmSceneLayerQueryFlags(qm.FlagsDefinition):

    def __init__(self):
        super(_QmSceneLayerQueryFlags, self).__init__()
        self.file_path = qm.SyntaxFlag('f', 'filePath', om2.MSyntax.kBoolean)
        self.elements = qm.SyntaxFlag('e', 'elements', om2.MSyntax.kBoolean)
        self.children = qm.SyntaxFlag('c', 'children', om2.MSyntax.kBoolean)


class QmSceneLayerQuery(om2.MPxCommand):

    name = 'qmSceneLayerQuery'

    @staticmethod
    def creator():
        return QmSceneLayerQuery()

    @staticmethod
    def syntax_creator():
        syntax = om2.MSyntax()

        syntax.enableQuery = True
        syntax.enableEdit = False

        syntax.setObjectType(om2.MSyntax.kStringObjects)

        flags = _QmSceneLayerQueryFlags()
        flags.apply_to(syntax)

        return syntax

    def __init__(self):
        super(QmSceneLayerQuery, self).__init__()

    def doIt(self, args):
        # type: (om2.MArgList) -> NoReturn
        parser = qm.ArgDatabase(self.syntax(), args)
        flags = parser.parse_flags(_QmSceneLayerQueryFlags)  # type: _QmSceneLayerQueryFlags

        node_names = parser.getObjectStrings()
        for name in node_names:
            if not cmds.objExists(name):
                cmds.error('node "{}" is not exists'.format(name))

        if flags.file_path.is_true:
            results = []
            for node_name in node_names:
                file_path = cmds.getAttr('{}.filePath'.format(node_name)) or ''
                results.append(file_path)
            self.setResult(results)
            return

        if flags.elements.is_true:
            elements = []
            for name in node_names:
                elements.extend(cmds.listConnections('{}.elements'.format(name)) or [])
            self.setResult(elements)
            return

        if flags.children.is_true:
            children = []
            for name in node_names:
                children.extend(cmds.listConnections('{}.children'.format(name)) or [])
            self.setResult(children)
            return

        self.setResult(cmds.ls(type='qmSceneLayer'))


class _QmSceneLayerEditFlags(qm.FlagsDefinition):

    def __init__(self):
        super(_QmSceneLayerEditFlags, self).__init__()
        self.new_layer = qm.SyntaxFlag('new', 'newLayer', om2.MSyntax.kBoolean)
        self.unload = qm.SyntaxFlag('u', 'unload', om2.MSyntax.kBoolean)
        self.reload = qm.SyntaxFlag('r', 'reload', om2.MSyntax.kBoolean)

        self.file_path = qm.SyntaxFlag('f', 'filePath', om2.MSyntax.kString)
        self.name = qm.SyntaxFlag('n', 'name', om2.MSyntax.kString)
        self.parent_layer = qm.SyntaxFlag('p', 'parent', om2.MSyntax.kString)
        self.namespace = qm.SyntaxFlag('ns', 'namespace', om2.MSyntax.kString)

        self.recursive = qm.SyntaxFlag('rec', 'recursive', om2.MSyntax.kBoolean)


class QmSceneLayerEdit(om2.MPxCommand):

    name = 'qmSceneLayerEdit'

    @staticmethod
    def creator():
        return QmSceneLayerEdit()

    @staticmethod
    def syntax_creator():
        syntax = om2.MSyntax()

        syntax.enableQuery = False
        syntax.enableEdit = True

        syntax.setObjectType(om2.MSyntax.kStringObjects)
        syntax.setMaxObjects(1)

        flags = _QmSceneLayerEditFlags()
        flags.apply_to(syntax)

        return syntax

    def __init__(self):
        super(QmSceneLayerEdit, self).__init__()

    def doIt(self, args):
        # type: (om2.MArgList) -> NoReturn
        parser = qm.ArgDatabase(self.syntax(), args)

        layer_names = parser.getObjectStrings()
        for name in layer_names:
            if not cmds.objExists(name):
                cmds.error('node "{}" is not exists'.format(name))
            if cmds.nodeType(name) != 'qmSceneLayer':
                cmds.error('node "{}" is not qmSceneLayer'.format(name))

        flags = parser.parse_flags(_QmSceneLayerEditFlags)  # type: _QmSceneLayerEditFlags
        options = _EditOptions(flags)

        editor = _LayerEditor()

        if flags.unload.is_true:
            if len(layer_names) != 1:
                cmds.error('one qmSceneLayer node name must be specified')

            editor.layer_name = layer_names[0]
            editor.unload(flags.recursive.is_true)

            self.setResult(editor.layer_name)
            return

        elif flags.reload.is_true:
            if len(layer_names) != 1:
                cmds.error('one qmSceneLayer node name must be specified')

            editor.layer_name = layer_names[0]
            editor.reload(flags.recursive.is_true)

            self.setResult(editor.layer_name)
            return

        elif flags.new_layer.is_true:
            editor.create(options.layer_name or 'qmSceneLayer1')

            if options.file_path is not None:
                editor.load_file(options.file_path, options.namespace)

            if options.parent_layer is not None:
                editor.set_parent_layer(options.parent_layer)

            self.setResult(editor.layer_name)
            return

        else:
            if len(layer_names) != 1:
                cmds.error('one qmSceneLayer node name must be specified')

            editor.layer_name = layer_names[0]

            if flags.name.is_set:
                editor.rename(options.layer_name)

            if flags.namespace.is_set:
                editor.set_namespace(options.namespace)

            if flags.parent_layer.is_set:
                editor.set_parent_layer(options.parent_layer)

            if flags.file_path.is_set:
                editor.load_file(options.file_path, options.namespace)

        self.setResult(editor.layer_name)
        return


class _EditOptions(object):

    def __init__(self, flags):
        # type: (_QmSceneLayerEditFlags) -> NoReturn
        file_path = flags.file_path.value
        if file_path is not None:
            file_path, exists = om2.MFileObject.getResolvedFullNameAndExistsStatus(file_path, om2.MFileObject.kInputFile)
            if not exists:
                cmds.error('file not found: {}'.format(file_path))
            scenes_root_path = qm.Workspace.path_by_file_rule('scene') or ''
            if file_path.startswith(scenes_root_path):
                file_path = os.path.relpath(file_path, scenes_root_path).replace(os.sep, '/')

        parent_layer = flags.parent_layer.value
        if parent_layer is not None:
            if not cmds.objExists(parent_layer):
                cmds.error('node "{}" is not found'.format(parent_layer))
            if cmds.nodeType(parent_layer) != 'qmSceneLayer':
                cmds.error('node "{}" is not qnSceneLayer'.format(parent_layer))

        default_namespace = ':'
        if file_path is not None:
            file_name, _ = os.path.splitext(os.path.basename(file_path))
            layer_name = flags.name.value or file_name + 'Layer'
            default_namespace = file_name
        else:
            layer_name = flags.name.value

        namespace = flags.namespace.value or default_namespace

        self.file_path = file_path
        self.layer_name = layer_name
        self.parent_layer = parent_layer
        self.namespace = namespace


class _LayerEditor(object):

    def __init__(self, layer_name=None):
        # type: (str) -> NoReturn
        self.layer_name = layer_name

    def create(self, layer_name):
        self.layer_name = cmds.createNode('qmSceneLayer', name=layer_name)

    def rename(self, layer_name):
        if self.layer_name != layer_name:
            self.layer_name = cmds.rename(self.layer_name, layer_name)

    def load_file(self, file_path, namespace):
        # type: (str, str) -> NoReturn
        current_elements = cmds.listConnections('{}.elements'.format(self.layer_name)) or []

        new_nodes = cmds.file(
            file_path,
            i=True,
            loadReferenceDepth='all',
            removeDuplicateNetworks=True,
            returnNewNodes=True,
            namespace=namespace
        )

        for node in new_nodes:
            cmds.lockNode(node, lock=True)
            cmds.connectAttr('{}.message'.format(node), '{}.elements'.format(self.layer_name), nextAvailable=True)

        cmds.setAttr('{}.filePath'.format(self.layer_name), file_path, type='string')
        cmds.setAttr('{}.namespace'.format(self.layer_name), namespace, type='string')

        if len(current_elements) > 0:
            cmds.lockNode(current_elements, lock=False)
            cmds.lockNode(cmds.listRelatives(current_elements, allDescendents=True, fullPath=True) or [], lock=False)
            cmds.delete(current_elements)

    def unload(self, recursive):
        # type: (bool) -> NoReturn
        children = cmds.listConnections('{}.children'.format(self.layer_name)) or []
        for child in children:
            cmds.disconnectAttr('{}.message'.format(child), '{}.children'.format(self.layer_name), nextAvailable=True)

        if recursive:
            for child in children:
                editor = _LayerEditor(child)
                editor.unload(True)

        current_elements = cmds.listConnections('{}.elements'.format(self.layer_name)) or []
        if len(current_elements) > 0:
            cmds.lockNode(current_elements, lock=False)
            cmds.lockNode(cmds.listRelatives(current_elements, allDescendents=True, fullPath=True) or [], lock=False)
            cmds.delete(current_elements)

        if cmds.objExists(self.layer_name):
            cmds.delete(self.layer_name)

    def reload(self, recursive):
        # type: (bool) -> NoReturn
        if recursive:
            for child in cmds.listConnections('{}.children'.format(self.layer_name)) or []:
                editor = _LayerEditor(child)
                editor.reload(True)

        file_path = cmds.getAttr('{}.filePath'.format(self.layer_name))
        if file_path is not None:
            namespace = cmds.getAttr('{}.namespace'.format(self.layer_name))
            self.load_file(file_path, namespace)

    def set_parent_layer(self, parent_layer):
        # type: (str) -> NoReturn
        current_parent = cmds.listConnections('{}.message'.format(self.layer_name)) or []
        if len(current_parent) > 0:
            cmds.disconnectAttr('{}.message'.format(self.layer_name), '{}.children'.format(current_parent[0]), nextAvailable=True)

        if parent_layer is not None:
            cmds.connectAttr('{}.message'.format(self.layer_name), '{}.children'.format(parent_layer), nextAvailable=True)

    def set_namespace(self, namespace):
        # type: (str) -> NoReturn
        current_namespace = cmds.getAttr('{}.namespace'.format(self.layer_name))
        if namespace != current_namespace:
            cmds.namespace(rename=(current_namespace, namespace))
            cmds.setAttr('{}.namespace'.format(self.layer_name), namespace, type='string')


qm.setup_plugin(
    globals(),
    [
        qm.CommandPluginSetup(QmSceneLayerQuery.name, QmSceneLayerQuery.creator, QmSceneLayerQuery.syntax_creator),
        qm.CommandPluginSetup(QmSceneLayerEdit.name, QmSceneLayerEdit.creator, QmSceneLayerEdit.syntax_creator),
    ],
    '@hal1932', '0.0.1', 'Any'
)
