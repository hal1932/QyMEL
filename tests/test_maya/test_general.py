# coding: utf-8
from __future__ import absolute_import, print_function
from six import *
from six.moves import *
from typing import *

import unittest

import maya.standalone
maya.standalone.initialize(name='python')

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import qymel.maya as qm


class TestGeneral(unittest.TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        cube1, _ = cmds.polyCube()
        cube2, _ = cmds.polyCube()
        cmds.parent(cube2, cube1)
        self.cube1 = cmds.ls(cube1, long=True)[0]
        self.shape1 = cmds.ls(cmds.listRelatives(self.cube1, shapes=True), long=True)[0]
        self.cube2 = cmds.ls(cube2, long=True)[0]
        self.cubes = [self.cube1, self.cube2]

    def tearDown(self) -> None:
        pass

    def test_ls(self):
        cmds_ls = cmds.ls()
        qm_ls = qm.ls()
        self.assertEqual(len(cmds_ls), len(qm_ls))
        self.assertSequenceEqual([node.mel_object for node in qm_ls], cmds.ls(cmds_ls, long=True))

    def test_eval(self):
        for name in self.cubes:
            node = qm.eval(name)
            self.assertEqual(node.mel_object, cmds.ls(name, long=True)[0])

    def test_eval_node(self):
        for name in self.cubes:
            node = qm.eval_node(name)
            self.assertEqual(node.mel_object, cmds.ls(name, long=True)[0])

        with self.assertRaises(TypeError):
            qm.eval_node(f'{self.cube1}.t')

        with self.assertRaises(TypeError):
            self.assertIsNone(qm.eval_node(f'{self.shape1}.vtx[0]'))

    def test_eval_plug(self):
        for name in self.cubes:
            self.assertIsNone(qm.eval_plug(name))

        plug = qm.eval_plug(f'{self.cube1}.t')
        self.assertEqual(plug.mel_object, f'{self.cube1}.t')

        self.assertIsNone(qm.eval_plug(f'{self.shape1}.vtx[0]'))

    def test_eval_component(self):
        for name in self.cubes:
            with self.assertRaises(RuntimeError):
                qm.eval_component(name)

        self.assertIsNone(qm.eval_component(f'{self.cube1}.t'))

        comp = qm.eval_component(f'{self.shape1}.vtx[0]')
        self.assertEqual(len(comp.mel_object), 1)
        self.assertEqual(comp.mel_object[0], f'{self.shape1}.vtx[0]')

        comp = qm.eval_component(f'{self.shape1}.vtx[0:1]')
        self.assertEqual(comp.mel_object[0], f'{self.shape1}.vtx[0:1]')


class TestGeneralPlug(unittest.TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        cube1, _ = cmds.polyCube()
        cube2, _ = cmds.polyCube()
        cmds.parent(cube2, cube1)
        self.cube1 = cmds.ls(cube1, long=True)[0]
        cmds.setAttr(f'{self.cube1}.t', 1, 2, 3, type='double3')
        self.t = f'{self.cube1}.t'
        self.tx = f'{self.cube1}.tx'
        self.ty = f'{self.cube1}.ty'
        self.tz = f'{self.cube1}.tz'
        self.names = [self.t, self.tx, self.ty, self.tz]
        self.t2 = f'{cube2}.t'

    def test_props(self):
        for name in self.names:
            plug, full_name, mplug, mattr = self.__get_plug(name)
            self.assertEqual(plug.mel_object, name)
            self.assertEqual(plug.mplug, mplug)
            self.assertEqual(plug.attribute_mobject, mattr)
            self.assertEqual(plug.mfn_node.fullPathName(), om2.MFnDagNode(mplug.node()).fullPathName())
            self.assertFalse(plug.is_null)
            self.assertEqual(plug.name, full_name.strip('|'))
            self.assertEqual(plug.partial_name, name.split('.')[-1])
            self.assertEqual(plug.api_type, mattr.apiType())
            self.assertEqual(plug.is_source, mplug.isSource)
            self.assertEqual(plug.is_destination, mplug.isDestination)
            self.assertEqual(plug.is_array, mplug.isArray)
            self.assertEqual(plug.is_compound, mplug.isCompound)
            self.assertEqual(plug.is_networked, mplug.isNetworked)
            self.assertEqual(plug.is_locked, mplug.isLocked)
            self.assertEqual(plug.exists, not mplug.isNull)

    def test_node(self):
        for name in self.names:
            plug, full_name, mplug, mattr = self.__get_plug(name)
            self.assertEqual(plug.node().mel_object, om2.MFnDagNode(mplug.node()).fullPathName())

    def test_get(self):
        plug, full_name, mplug, mattr = self.__get_plug(self.t)
        self.assertEqual(plug.get(), cmds.getAttr(full_name)[0])

        for name in [self.tx, self.ty, self.tz]:
            plug, full_name, mplug, mattr = self.__get_plug(name)
            self.assertEqual(plug.get(), cmds.getAttr(full_name))

    def test_get_attr(self):
        for name in self.names:
            plug, full_name, mplug, mattr = self.__get_plug(name)
            self.assertEqual(plug.get_attr(), cmds.getAttr(full_name))

    def test_set_attr(self):
        plug, full_name, mplug, mattr = self.__get_plug(self.t)

        cmds.setAttr(full_name, 0, 0, 0, type='double3')
        plug.set_attr(1, 2, 3, type='double3')
        got = cmds.getAttr(full_name)

        cmds.setAttr(full_name, 0, 0, 0, type='double3')
        cmds.setAttr(full_name, 1, 2, 3, type='double3')
        expected = cmds.getAttr(full_name)

        self.assertEqual(got, expected)

    def test_connect(self):
        plug, full_name, mplug, mattr = self.__get_plug(self.t)
        plug2, full_name2, _, _ = self.__get_plug(self.t2)

        destinations = cmds.ls(cmds.listConnections(full_name, plugs=True, source=False), long=True)
        self.assertNotIn(full_name2, destinations)

        plug.connect(plug2)
        destinations = cmds.ls(cmds.listConnections(full_name, plugs=True, source=False), long=True)
        self.assertIn(full_name2, destinations)

        plug.disconnect(plug2)
        destinations = cmds.ls(cmds.listConnections(full_name, plugs=True, source=False), long=True)
        self.assertNotIn(full_name2, destinations)

    def test_connection(self):
        plug, full_name, mplug, mattr = self.__get_plug(self.t)
        plug2, full_name2, _, _ = self.__get_plug(self.t2)
        cmds.connectAttr(full_name, full_name2)

        self.assertEqual(plug2.source().full_name, full_name)
        self.assertEqual(len(plug.destinations()), 1)
        self.assertEqual(plug.destinations()[0].full_name, full_name2)

    def __get_plug(self, name):
        # type: (str) -> Tuple[qm.Plug, str, om2.MPlug, om2.MAttributeIndex]
        full_name = cmds.ls(name, long=True)[0]
        plug = qm.Plug(full_name)
        mplug = om2.MGlobal.getSelectionListByName(name).getPlug(0)  # type: om2.MPlug
        mattr = mplug.attribute()  # type: om2.MObject
        return plug, full_name, mplug, mattr


class TestGeneralColorSet(unittest.TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        self.cube1, _ = cmds.polyCube()
        self.shape1 = cmds.ls(cmds.listRelatives(self.cube1, shapes=True), long=True)[0]
        cmds.select(self.cube1, replace=True)
        self.color = cmds.polyColorSet(create=True)[0]
        for i in range(cmds.polyEvaluate(self.shape1, vertex=True)):
            cmds.select(f'{self.shape1}.vtx[{i}]', replace=True)
            cmds.polyColorPerVertex(r=i*0.01, g=i*0.02, b=i*0.05)
            cmds.polyColorPerVertex(a=i*0.1)

    def test_props(self):
        color_set = qm.ColorSet(self.color, qm.Mesh(self.shape1))
        cmds.polyColorSet(currentColorSet=True, colorSet=self.color)
        self.assertEqual(color_set.name, self.color)
        self.assertEqual(color_set.mel_object, self.color)
        self.assertEqual(color_set.mesh.mel_object, self.shape1)
        self.assertEqual(color_set.channels, len(cmds.polyColorSet(query=True, currentColorSet=True, representation=True)))
        self.assertEqual(color_set.is_clamped, cmds.polyColorSet(query=True, currentColorSet=True, clamped=True))

    def test_color(self):
        color_set = qm.ColorSet(self.color, qm.Mesh(self.shape1))
        colors = color_set.colors()
        vtx_faces = cmds.ls(cmds.polyListComponentConversion('pCubeShape1', toVertexFace=True), flatten=True)
        for i, vf in enumerate(sorted(vtx_faces)):  # V→Fの順にソート vtxFace[0][0], vtxFace[0][3], vtxFace[0][5], ...
            cmds.select(vf, replace=True)
            color = color_set.color(i)
            self.assertEqual([color[0], color[1], color[2]], cmds.polyColorPerVertex(query=True, colorRGB=True))
            self.assertEqual(color[3], cmds.polyColorPerVertex(query=True, alpha=True)[0])
            self.assertEqual(color, colors[i])

    def test_face_vertex_colors(self):
        color_set = qm.ColorSet(self.color, qm.Mesh(self.shape1))
        vtxface_colors = []
        for vf in cmds.ls(cmds.polyListComponentConversion('pCubeShape1', toVertexFace=True), flatten=True):
            cmds.select(vf, replace=True)
            color = cmds.polyColorPerVertex(query=True, colorRGB=True)
            color.append(cmds.polyColorPerVertex(query=True, alpha=True)[0])
            vtxface_colors.append(color)
        for got, expected in zip(color_set.face_vertex_colors(), vtxface_colors):
            self.assertEqual(got.getColor(), expected)

    def test_vertex_colors(self):
        color_set = qm.ColorSet(self.color, qm.Mesh(self.shape1))
        vertex_colors = []
        for v in cmds.ls(cmds.polyListComponentConversion('pCubeShape1', toVertex=True), flatten=True):
            cmds.select(v, replace=True)
            color = cmds.polyColorPerVertex(query=True, colorRGB=True)
            color.append(cmds.polyColorPerVertex(query=True, alpha=True)[0])
            vertex_colors.append(color)
        for got, expected in zip(color_set.vertex_colors(), vertex_colors):
            self.assertEqual(got.getColor(), expected)


class TestGeneralUvSet(unittest.TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        cube1, _ = cmds.polyCube()
        self.shape1 = cmds.ls(cmds.listRelatives(cube1, shapes=True), long=True)[0]
        self.uvset = cmds.polyUVSet(query=True, currentUVSet=True)[0]

    def test_props(self):
        uvset = qm.UvSet(self.uvset, qm.Mesh(self.shape1))
        self.assertEqual(uvset.name, self.uvset)
        self.assertEqual(uvset.mel_object, self.uvset)
        self.assertEqual(uvset.mesh.mel_object, self.shape1)
