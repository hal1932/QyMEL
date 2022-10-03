# coding: utf-8
import unittest

import maya.standalone
maya.standalone.initialize(name='python')

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import qymel.maya as qm


class _TestComponent(unittest.TestCase):

    def _setUp(self) -> None:
        cmds.file(new=True, force=True)
        self.cube1, _ = cmds.polyCube()
        self.shape1 = cmds.ls(cmds.listRelatives(self.cube1, shapes=True), long=True)[0]
        self.elements = self.indices(self.shape1)
        self.comp = cmds.ls(f'|{self.cube1}.{self.repr}[*]', flatten=True)

        self.mcomp = self.mfncomp()
        self.mobj = self.mcomp.create(self.mfn)
        self.mcomp.setCompleteData(*self.count(self.shape1))

        self.dagpath = om2.MGlobal.getSelectionListByName(self.shape1).getDagPath(0)

    def _test_props(self):
        comp = self.cls(self.mobj, self.dagpath)
        self.assertSequenceEqual(cmds.ls(comp.mel_object, flatten=True), self.comp)
        self.assertEqual(comp.exists, True)
        self.assertEqual(comp.mdagpath, self.dagpath)
        self.assertEqual(comp.mfn.__class__, self.mcomp.__class__)
        self.assertEqual(list(comp.elements), self.elements)
        self.assertEqual(len(comp), len(self.elements))

    def _test_elements(self):
        comp = self.cls(self.mobj, self.dagpath)
        for i, elem in enumerate(self.elements):
            self.assertEqual(comp[i], elem)
            self.assertEqual(comp.element(i), elem)

        for i, elem in enumerate(comp):
            self.assertEqual(elem, self.elements[i])

    def _test_clone(self):
        comp = self.cls(self.mobj, self.dagpath)

        clone = comp.clone()
        self.assertEqual(clone.api_type, comp.api_type)
        self.assertEqual(list(clone.elements), list(comp.elements))

        clone = comp.clone_empty()
        self.assertEqual(clone.api_type, comp.api_type)
        self.assertEqual(list(clone.elements), [])

    def _test_resize_1d(self):
        mcomp = self.mfncomp()
        mobj = mcomp.create(self.mfn)
        comp = self.cls(mobj, self.dagpath)

        comp.append(0)
        self.assertEqual(len(comp), 1)
        self.assertEqual(comp[0], 0)

        comp.append(1)
        self.assertEqual(len(comp), 2)
        self.assertEqual(comp[1], 1)

        comp.extend([3, 4])
        self.assertEqual(len(comp), 4)
        self.assertEqual(comp[2], 3)
        self.assertEqual(comp[3], 4)

    def _test_resize_2d(self):
        mcomp = self.mfncomp()
        mobj = mcomp.create(self.mfn)
        comp = self.cls(mobj, self.dagpath)

        comp.append([0, 1])
        self.assertEqual(len(comp), 1)
        self.assertSequenceEqual(comp[0], [0, 1])

        comp.append([2, 3])
        self.assertEqual(len(comp), 2)
        self.assertSequenceEqual(comp[1], [2, 3])

        comp.extend([[4, 5], [6, 7]])
        self.assertEqual(len(comp), 4)
        self.assertSequenceEqual(comp[2], [4, 5])
        self.assertSequenceEqual(comp[3], [6, 7])


class TestMeshVertex(_TestComponent):

    def setUp(self) -> None:
        self.cls = qm.MeshVertex
        self.count = lambda shape: [cmds.polyEvaluate(shape, vertex=True)]
        self.indices = lambda shape: list(range(self.count(shape)[0]))
        self.repr = 'vtx'
        self.mfn = om2.MFn.kMeshVertComponent
        self.mfncomp = om2.MFnSingleIndexedComponent
        super()._setUp()

    def test_props(self):
        super()._test_props()

    def test_elements(self):
        super()._test_elements()

    def test_clone(self):
        super()._test_clone()

    def test_resize(self):
        super()._test_resize_1d()


class TestMeshFace(_TestComponent):

    def setUp(self) -> None:
        self.cls = qm.MeshFace
        self.count = lambda shape: [cmds.polyEvaluate(shape, face=True)]
        self.indices = lambda shape: list(range(self.count(shape)[0]))
        self.repr = 'f'
        self.mfn = om2.MFn.kMeshPolygonComponent
        self.mfncomp = om2.MFnSingleIndexedComponent
        super()._setUp()

    def test_props(self):
        super()._test_props()

    def test_elements(self):
        super()._test_elements()

    def test_clone(self):
        super()._test_clone()

    def test_resize(self):
        super()._test_resize_1d()


class TestMeshEdge(_TestComponent):

    def setUp(self) -> None:
        self.cls = qm.MeshEdge
        self.count = lambda shape: [cmds.polyEvaluate(shape, edge=True)]
        self.indices = lambda shape: list(range(self.count(shape)[0]))
        self.repr = 'e'
        self.mfn = om2.MFn.kMeshEdgeComponent
        self.mfncomp = om2.MFnSingleIndexedComponent
        super()._setUp()

    def test_props(self):
        super()._test_props()

    def test_elements(self):
        super()._test_elements()

    def test_clone(self):
        super()._test_clone()

    def test_resize(self):
        super()._test_resize_1d()


class TestVertexFace(_TestComponent):

    def _get_indices(self, shape):
        indices = []
        dagpath = om2.MGlobal.getSelectionListByName(shape).getDagPath(0)
        iter = om2.MItMeshFaceVertex(dagpath)
        while not iter.isDone():
            indices.append((iter.faceId(), iter.faceVertexId()))
            iter.next()
        return indices

    def setUp(self) -> None:
        self.cls = qm.MeshVertexFace
        self.count = lambda shape: [cmds.polyEvaluate(shape, face=True), 4]
        self.indices = lambda shape: self._get_indices(shape)
        self.repr = 'vtxFace'
        self.mfn = om2.MFn.kMeshVtxFaceComponent
        self.mfncomp = om2.MFnDoubleIndexedComponent
        super()._setUp()

    def test_props(self):
        super()._test_props()

    def test_elements(self):
        super()._test_elements()

    def test_clone(self):
        super()._test_clone()

    def test_resize(self):
        super()._test_resize_2d()
