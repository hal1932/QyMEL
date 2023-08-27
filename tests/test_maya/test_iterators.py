# coding: utf-8
import unittest

import maya.standalone
maya.standalone.initialize(name='python')

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import qymel.maya as qm


class TestCase(unittest.TestCase):

    def assertFloatSequenceEquals(self, lhs, rhs):
        self.assertEqual(len(lhs), len(rhs))
        for l, r in zip(lhs, rhs):
            self.assertAlmostEqual(l, r, places=4)


class TestMeshVertexIter(TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        cube1, _ = cmds.polyCube()
        self.shape1 = cmds.ls(cmds.listRelatives(cube1, shapes=True), long=True)[0]
        self.dagpath = om2.MGlobal.getSelectionListByName(self.shape1).getDagPath(0)

        cmds.select(cube1, replace=True)
        self.color = cmds.polyColorSet(create=True)[0]
        for i in range(cmds.polyEvaluate(self.shape1, vertex=True)):
            cmds.select(f'{self.shape1}.vtx[{i}]', replace=True)
            cmds.polyColorPerVertex(r=i*0.01, g=i*0.02, b=i*0.05)
            cmds.polyColorPerVertex(a=i*0.1)

    def test_props(self):
        miter = om2.MItMeshVertex(self.dagpath)
        iter = self._get_iter()
        for vtx in iter:
            self.assertEqual(vtx.index, miter.index())
            self.assertSequenceEqual(list(vtx.connected_edge_indices), list(miter.getConnectedEdges()))
            self.assertSequenceEqual(list(vtx.connected_face_indices), list(miter.getConnectedFaces()))
            self.assertSequenceEqual(list(vtx.connected_vertex_indices), list(miter.getConnectedVertices()))
            self.assertEqual(vtx.connected_edge_count, miter.numConnectedEdges())
            self.assertEqual(vtx.connected_face_count, miter.numConnectedEdges())
            self.assertEqual(vtx.on_boundary, miter.onBoundary())
            miter.next()

    def test_color(self):
        miter = om2.MItMeshVertex(self.dagpath)
        iter = self._get_iter()
        for vtx in iter:
            self.assertEqual(vtx.has_color(), miter.hasColor())
            for f in range(miter.numConnectedFaces()):
                self.assertEqual(vtx.has_color(f), miter.hasColor(f))

            self.assertEqual(vtx.color(None, self.color), miter.getColor(self.color))
            # for f in range(miter.numConnectedFaces()):
            #     self.assertEqual(vtx.color(f, self.color), miter.color(f. self.color))

            def _colors(cols):
                return [[c.r, c.g, c.b, c.a] for c in cols]

            self.assertFloatSequenceEquals(_colors(vtx.colors(self.color)), _colors(miter.getColors(self.color)))
            self.assertFloatSequenceEquals(vtx.color_indices(self.color), miter.getColorIndices(self.color))

            miter.next()

    def test_normal(self):
        miter = om2.MItMeshVertex(self.dagpath)
        iter = self._get_iter()
        for vtx in iter:
            self.assertEqual(vtx.normal(), miter.getNormal())
            # for f in range(miter.numConnectedFaces()):
            #     self.assertEqual(vtx.normal(f, om2.MSpace.kObject), miter.getNormal(f, om2.MSpace.kObject))
            self.assertSequenceEqual(list(vtx.normals()), list(miter.getNormals()))
            self.assertSequenceEqual(list(vtx.normal_indices()), list(miter.getNormalIndices()))
            miter.next()

    def test_uv(self):
        miter = om2.MItMeshVertex(self.dagpath)
        iter = self._get_iter()
        uv_set = 'map1'
        for vtx in iter:
            self.assertEqual(vtx.uv(uv_set), miter.getUV(uv_set))
            self.assertSequenceEqual(list(vtx.uv_indices(uv_set)), list(miter.getUVIndices(uv_set)))
            for f, uv in vtx.uvs(uv_set).items():
                self.assertSequenceEqual(uv, miter.getUV(f, uv_set))
            self.assertEqual(vtx.uv_count(uv_set), miter.numUVs(uv_set))
            miter.next()

    def test_position(self):
        miter = om2.MItMeshVertex(self.dagpath)
        iter = self._get_iter()
        for vtx in iter:
            self.assertSequenceEqual(list(vtx.position()), list(miter.position()))
            miter.next()

    def _get_iter(self):
        mcomp = om2.MFnSingleIndexedComponent()
        mobj = mcomp.create(om2.MFn.kMeshVertComponent)
        mcomp.setCompleteData(cmds.polyEvaluate(self.shape1, vertex=True))
        comp = qm.MeshVertex(mobj, self.dagpath)
        return qm.MeshVertexIter(om2.MItMeshVertex(self.dagpath), comp, om2.MFnMesh(self.dagpath))


class TestMeshFaceIter(TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        cube1, _ = cmds.polyCube()
        self.shape1 = cmds.ls(cmds.listRelatives(cube1, shapes=True), long=True)[0]
        self.dagpath = om2.MGlobal.getSelectionListByName(self.shape1).getDagPath(0)

    def test_props(self):
        miter = om2.MItMeshPolygon(self.dagpath)
        iter = self._get_iter()
        for face in iter:
            self.assertEqual(face.index, miter.index())
            self.assertSequenceEqual(list(face.connected_vertex_indices), list(miter.getConnectedVertices()))
            self.assertSequenceEqual(list(face.connected_face_indices), list(miter.getConnectedFaces()))
            self.assertSequenceEqual(list(face.connected_edge_indices), list(miter.getConnectedEdges()))
            self.assertSequenceEqual(list(face.edge_indices), list(miter.getEdges()))
            self.assertSequenceEqual(list(face.vertex_indices), list(miter.getVertices()))
            self.assertEqual(face.is_convex, miter.isConvex())
            self.assertEqual(face.is_lamina, miter.isLamina())
            self.assertEqual(face.is_planar, miter.isPlanar())
            self.assertEqual(face.is_zero_area, miter.zeroArea())
            self.assertEqual(face.on_boundary, miter.onBoundary())
            self.assertEqual(face.triangle_count, miter.numTriangles())
            miter.next()

    def test_geom(self):
        miter = om2.MItMeshPolygon(self.dagpath)
        iter = self._get_iter()
        for face in iter:
            self.assertEqual(face.center(), miter.center())
            self.assertEqual(face.area(), miter.getArea())
            self.assertSequenceEqual(list(face.points()), list(miter.getPoints()))
            miter.next()

    def test_normal(self):
        miter = om2.MItMeshPolygon(self.dagpath)
        iter = self._get_iter()
        for face in iter:
            self.assertEqual(face.normal(), miter.getNormal())
            # for v in miter.getVertices():
            #     self.assertEqual(face.normal(v), miter.getNormal(v))
            self.assertSequenceEqual(list(face.normals()), list(miter.getNormals()))
            miter.next()

    def test_triangle(self):
        miter = om2.MItMeshPolygon(self.dagpath)
        iter = self._get_iter()
        for face in iter:
            for t in range(miter.numTriangles()):
                points, vertices = miter.getTriangle(t)
                for i, (v, p) in enumerate(face.triangle(t).items()):
                    self.assertEqual(v, vertices[i])
                    self.assertEqual(p, points[i])

            vertices = list(miter.getVertices())
            points = miter.getPoints()
            for tri in face.triangles():
                for v, p in tri.items():
                    self.assertIn(v, vertices)
                    self.assertEqual(p, points[vertices.index(v)])

            miter.next()

    def _get_iter(self):
        mcomp = om2.MFnSingleIndexedComponent()
        mobj = mcomp.create(om2.MFn.kMeshPolygonComponent)
        mcomp.setCompleteData(cmds.polyEvaluate(self.shape1, face=True))
        comp = qm.MeshFace(mobj, self.dagpath)
        return qm.MeshFaceIter(om2.MItMeshPolygon(self.dagpath), comp, om2.MFnMesh(self.dagpath))


class TestMeshEdgeIter(TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        cube1, _ = cmds.polyCube()
        self.shape1 = cmds.ls(cmds.listRelatives(cube1, shapes=True), long=True)[0]
        self.dagpath = om2.MGlobal.getSelectionListByName(self.shape1).getDagPath(0)

    def test_props(self):
        miter = om2.MItMeshEdge(self.dagpath)
        iter = self._get_iter()
        for edge in iter:
            self.assertEqual(edge.index, miter.index())
            self.assertSequenceEqual(list(edge.connected_edge_indices), list(miter.getConnectedEdges()))
            self.assertSequenceEqual(list(edge.connected_face_indices), list(miter.getConnectedFaces()))
            self.assertSequenceEqual(list(edge.vertex_indices), [miter.vertexId(0), miter.vertexId(1)])
            self.assertEqual(edge.on_boudary, miter.onBoundary())
            self.assertEqual(edge.is_smooth, miter.isSmooth)
            miter.next()

    def test_geom(self):
        miter = om2.MItMeshEdge(self.dagpath)
        iter = self._get_iter()
        for edge in iter:
            self.assertEqual(edge.center(), miter.center())
            self.assertEqual(edge.length(), miter.length())
            self.assertSequenceEqual(list(edge.points()), [miter.point(0), miter.point(1)])
            miter.next()

    def _get_iter(self):
        mcomp = om2.MFnSingleIndexedComponent()
        mobj = mcomp.create(om2.MFn.kMeshEdgeComponent)
        mcomp.setCompleteData(cmds.polyEvaluate(self.shape1, edge=True))
        comp = qm.MeshEdge(mobj, self.dagpath)
        return qm.MeshEdgeIter(om2.MItMeshEdge(self.dagpath), comp, om2.MFnMesh(self.dagpath))


class TestMeshVertexFaceITer(TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        cube1, _ = cmds.polyCube()
        self.shape1 = cmds.ls(cmds.listRelatives(cube1, shapes=True), long=True)[0]
        self.dagpath = om2.MGlobal.getSelectionListByName(self.shape1).getDagPath(0)

        cmds.select(cube1, replace=True)
        self.color = cmds.polyColorSet(create=True)[0]
        for i in range(cmds.polyEvaluate(self.shape1, vertex=True)):
            cmds.select(f'{self.shape1}.vtx[{i}]', replace=True)
            cmds.polyColorPerVertex(r=i*0.01, g=i*0.02, b=i*0.05)
            cmds.polyColorPerVertex(a=i*0.1)

    def test_props(self):
        miter = om2.MItMeshFaceVertex(self.dagpath)
        iter = self._get_iter()
        for vf in iter:
            self.assertSequenceEqual(list(vf.index), [miter.vertexId(), miter.faceId()])
            self.assertEqual(vf.vertex_index, miter.vertexId())
            self.assertEqual(vf.face_index, miter.faceId())
            self.assertEqual(vf.face_vertex_index, miter.faceVertexId())
            self.assertEqual(vf.has_color, miter.hasColor())
            miter.next()

    def test_color(self):
        miter = om2.MItMeshFaceVertex(self.dagpath)
        iter = self._get_iter()
        for fv in iter:
            self.assertEqual(fv.color(self.color), miter.getColor(self.color))
            self.assertEqual(fv.color_index(self.color), miter.getColorIndex(self.color))

            miter.next()

    def test_normal(self):
        miter = om2.MItMeshFaceVertex(self.dagpath)
        iter = self._get_iter()
        for fv in iter:
            self.assertEqual(fv.normal(), miter.getNormal())
            self.assertEqual(fv.tangent(om2.MSpace.kObject, 'map1'), miter.getTangent(om2.MSpace.kObject, 'map1'))
            self.assertEqual(fv.binormal(om2.MSpace.kObject, 'map1'), miter.getBinormal(om2.MSpace.kObject, 'map1'))
            self.assertEqual(fv.normal_index(), miter.normalId())
            self.assertEqual(fv.tangent_index(), miter.tangentId())
            miter.next()

    def test_uv(self):
        miter = om2.MItMeshFaceVertex(self.dagpath)
        iter = self._get_iter()
        uv_set = 'map1'
        for fv in iter:
            self.assertEqual(fv.has_uv(uv_set), miter.hasUVs(uv_set))
            self.assertEqual(fv.uv(uv_set), miter.getUV(uv_set))
            self.assertEqual(fv.uv_index(), miter.getUVIndex(uv_set))
            miter.next()

    def test_position(self):
        miter = om2.MItMeshFaceVertex(self.dagpath)
        iter = self._get_iter()
        for vf in iter:
            self.assertSequenceEqual(list(vf.position()), list(miter.position()))
            miter.next()

    def _get_iter(self):
        mcomp = om2.MFnDoubleIndexedComponent()
        mobj = mcomp.create(om2.MFn.kMeshVtxFaceComponent)
        mcomp.setCompleteData(cmds.polyEvaluate(self.shape1, vertex=True), cmds.polyEvaluate(self.shape1, face=True))
        comp = qm.MeshVertexFace(mobj, self.dagpath)
        return qm.MeshFaceVertexIter(om2.MItMeshFaceVertex(self.dagpath), comp, om2.MFnMesh(self.dagpath))
