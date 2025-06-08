import unittest

import maya.standalone
maya.standalone.initialize(name='python')

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import qymel.maya as qm


class TestPlugPlug(unittest.TestCase):

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
        # type: (str) -> tuple[qm.Plug, str, om2.MPlug, om2.MObject]
        full_name = cmds.ls(name, long=True)[0]
        plug = qm.Plug(full_name)
        mplug = om2.MGlobal.getSelectionListByName(name).getPlug(0)  # type: om2.MPlug
        mattr = mplug.attribute()  # type: om2.MObject
        return plug, full_name, mplug, mattr
