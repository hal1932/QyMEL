# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as om2anim

from qymel.core.general import MayaObject, Plug, MeshVertexComponent, MeshFaceComponent, MeshEdgeComponent, MeshVertexFaceComponent
from qymel.core.iterators import MeshVertexIterator, MeshFaceIter, MeshEdgeIter, MeshVertexFaceIter
from qymel.internal.graphs import _ls_nodes, _create_node, _eval_node, _eval_plug, _to_node_instance, _get_mobject, _get_world_mobject
from qymel.internal.nodes import _NodeFactory


class DependNode(MayaObject):

    _mfn_type = om2.MFn.kDependencyNode
    _mfn_set = om2.MFnDependencyNode
    _mel_type = ''

    @staticmethod
    def ls(*args, **kwargs):
        kwargs.pop('type', None)
        return _ls_nodes(*args, **kwargs)

    @property
    def mfn(self):
        mfn_set = self.__class__._mfn_set

        if mfn_set is None:
            return None

        mfn = self._mfn
        if mfn is None:
            mfn = mfn_set(self.mobject)
            self._mfn = mfn

        return mfn

    @property
    def name(self):
        # type: () -> str
        return self.mfn.name()

    @property
    def abs_name(self):
        # type: () -> str
        return self.mfn.absoluteName()

    @property
    def namespace(self):
        # type: () -> str
        return self.mfn.namespace

    @property
    def is_locked(self):
        # type: () -> bool
        return self.mfn.isLocked

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(DependNode, self).__init__(mobj)
        self._mfn = None
        self._plugs = {}  # Dict[str, Plug]

    def __str__(self):
        # type: () -> str
        return '{} {}'.format(self.__class__, self.abs_path)

    def __getattr__(self, item):
        # type: (str) -> Any
        if item in self.__dict__:
            return self.__dict__[item]

        plug = self._plugs.get(item, None)
        if plug is not None:
            return plug

        mplug = None
        try:
            mplug = self.mfn.findPlug(item, False)
        except RuntimeError:
            pass

        if mplug is None:
            return None

        plug = Plug(mplug)
        self._plugs[item] = plug

        return plug

    def connections(self, **kwargs):
        # type: (Any) -> Iterable[Any]
        # 自前でプラグを辿るより listConnections のほうが速い
        others = cmds.listConnections(self.abs_path, **kwargs) or []

        if 'plugs' in kwargs or 'p' in kwargs:
            return [_eval_plug(name) for name in others]

        tmp_mfn = om2.MFnDependencyNode()
        return [_eval_node(name, tmp_mfn) for name in others]

    def sources(self):
        # type: () -> Iterable[Any]
        return self.connections(source=True, destination=False)

    def destinations(self):
        # type: () -> Iterable[Any]
        return self.connections(source=False, destination=True)

    def rename(self, new_name):
        # type: (str) -> none
        new_name = cmds.rename(self.abs_name, new_name)
        mobj = _get_mobject(new_name)
        self.__init__(mobj)

    def lock(self):
        cmds.lockNode(self.abs_name, lock=True)

    def unlock(self):
        cmds.lockNode(self.abs_name, lock=False)

    def duplicate(self, **kwargs):
        # type: (Any) -> DependNode
        duplicated_node_name = cmds.duplicate(self.abs_name, **kwargs)
        return _eval_node(duplicated_node_name, om2.MFnDependencyNode())

    def delete(self):
        cmds.delete(self.abs_name)


class ContainerBase(DependNode):

    _mfn_type = om2.MFn.kContainerBase
    _mfn_set = om2.MFnDependencyNode
    _mel_type = 'containerBase'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ContainerBase._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(ContainerBase, self).__init__(mobj)


class AnimCurve(DependNode):

    _mfn_type = om2.MFn.kAnimCurve
    _mfn_set = om2anim.MFnAnimCurve
    _mel_type = 'animCurve'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurve._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurve._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(AnimCurve, self).__init__(mobj)


class DisplayLayer(DependNode):

    _mfn_type = om2.MFn.kDisplayLayer
    _mfn_set = om2.MFnDependencyNode
    _mel_type = 'displayLayer'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = DisplayLayer._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(DisplayLayer._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(DisplayLayer, self).__init__(mobj)


class GeometryFilter(DependNode):

    _mfn_type = om2.MFn.kGeometryFilt
    _mfn_set = om2.MFnDependencyNode
    _mel_type = 'geometryFilter'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = GeometryFilter._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(GeometryFilter._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(GeometryFilter, self).__init__(mobj)


class SkinCluster(GeometryFilter):

    _mfn_type = om2.MFn.kSkin
    _mfn_set = om2anim.MFnSkinCluster
    _mel_type = 'skinCluster'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = SkinCluster._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(SkinCluster._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(SkinCluster, self).__init__(mobj)


class Entity(ContainerBase):

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(Entity, self).__init__(mobj)


class DagNode(Entity):

    _mfn_type = om2.MFn.kDagNode
    _mfn_set = om2.MFnDagNode
    _mel_type = None

    @staticmethod
    def ls(*args, **kwargs):
        kwargs.pop('type', None)
        kwargs['dagObjects'] = True
        return _ls_nodes(*args, **kwargs)

    @property
    def mdagpath(self):
        # type: () -> om2.MDagPath
        return self._mdagpath

    @property
    def abs_path(self):
        # type: () -> str
        return self._mdagpath.fullPathName()

    @property
    def root(self):
        # type: () -> str
        return self.abs_name.split('|')[0]

    @property
    def is_world(self):
        # type:() -> bool
        return self == World

    @property
    def has_parent(self):
        # type: () -> bool
        mfn = self.mfn
        if mfn.parentCount() > 1:
            return True
        parent_mobj = mfn.parent(0)
        return not parent_mobj.hasFn(om2.MFn.kWorld)

    @property
    def has_child(self):
        # type: () -> bool
        return self.mfn.childCount() > 0

    def __init__(self, mobj, mdagpath):
        # type: (om2.MObject, om2.MDagPath) -> NoReturn
        if mobj is None and mdagpath is None:
            # self is World
            mobj = _get_world_mobject()
            mdagpath = om2.MFnDagNode(mobj).getPath()

        super(DagNode, self).__init__(mobj)
        self._mdagpath = mdagpath

    def relatives(self, **kwargs):
        # type: (Any) -> List[DagNode]
        if self.is_world:
            raise NotImplementedError('World.relatives() is not implemented')

        kwargs['path'] = True
        others = cmds.listRelatives(self.abs_path, **kwargs)
        if others is None:
            return []

        tmp_mfn = om2.MFnDependencyNode()
        return [_eval_node(name, tmp_mfn) for name in others]

    def parent(self, index=0):
        # type: (int) -> DagNode
        if self.is_world:
            return None

        parent_mobj = self.mfn.parent(index)
        parent_mfn = om2.MFnDependencyNode(parent_mobj)
        parent_mfn_dag = om2.MFnDagNode(parent_mobj)

        return _to_node_instance(parent_mfn, parent_mfn_dag.getPath())

    def parents(self):
        # type: () -> List[DagNode]
        if self.is_world:
            return []

        result = []

        mfn = self.mfn
        tmp_mfn = om2.MFnDependencyNode()
        tmp_mfn_dag = om2.MFnDagNode()

        for i in range(mfn.parentCount()):
            parent_mobj = mfn.parent(i)

            if parent_mobj.hasFn(om2.MFn.kWorld):
                result.append(World)
                break

            tmp_mfn.setObject(parent_mobj)
            tmp_mfn_dag.setObject(parent_mobj)

            node = _to_node_instance(tmp_mfn, tmp_mfn_dag.getPath())
            result.append(node)

        return result

    def child(self, index=0):
        mfn = self.mfn
        if index >= mfn.childCount():
            return None

        child_mobj = mfn.child(index)
        return _to_node_instance(child_mobj, om2.MFnDagNode(child_mobj).getPath())

    def children(self, type_mfn=om2.MFn.kDagNode):
        # type: () -> List[DagNode]
        result = []

        if self.is_world:
            tmp_mfn = om2.MFnDependencyNode()
            tmp_mfn_dag = om2.MFnDagNode()

            self_hash = self.mobject_handle.hashCode()
            tmp_mobj_handle = om2.MObjectHandle()

            iter = om2.MItDependencyNodes(type_mfn)
            while not iter.isDone():
                mobj = iter.thisNode()
                if mobj.hasFn(om2.MFn.kWorld):
                    iter.next()
                    continue

                tmp_mobj_handle.assign(mobj)
                if tmp_mobj_handle.hashCode() == self_hash:
                    iter.next()
                    continue

                if mobj.hasFn(om2.MFn.kDagNode):
                    tmp_mfn_dag.setObject(mobj)
                    if tmp_mfn_dag.parent(0).hasFn(om2.MFn.kWorld):
                        tmp_mfn.setObject(iter.thisNode())
                        node = _to_node_instance(tmp_mfn, tmp_mfn_dag.getPath())
                        result.append(node)
                else:
                    tmp_mfn.setObject(iter.thisNode())
                    node = _to_node_instance(tmp_mfn, None)
                    result.append(node)

                iter.next()

        else:
            mfn = self.mfn
            tmp_mfn = om2.MFnDependencyNode()
            tmp_mfn_dag = om2.MFnDagNode()

            for i in range(mfn.childCount()):
                child_mobj = mfn.child(i)
                if not child_mobj.hasFn(type_mfn):
                    continue

                tmp_mfn.setObject(child_mobj)
                tmp_mfn_dag.setObject(child_mobj)

                node = _to_node_instance(tmp_mfn, tmp_mfn_dag.getPath())
                result.append(node)

        return result

    def ancestors(self):
        # type: () -> List[DagNode]
        if self.is_world:
            return []

        result = []

        mfn = self.mfn
        tmp_mfn = om2.MFnDependencyNode()
        tmp_mfn_dag = om2.MFnDagNode()

        while mfn.parentCount() > 0:
            parent_mobj = mfn.parent(0)

            if parent_mobj.hasFn(om2.MFn.kWorld):
                break

            tmp_mfn.setObject(parent_mobj)
            tmp_mfn_dag.setObject(parent_mobj)

            node = _to_node_instance(tmp_mfn, tmp_mfn_dag.getPath())
            result.append(node)

            mfn = tmp_mfn_dag

        return result

    def descendents(self):
        # type: () -> List[DagNode]
        return self.relatives(allDescendents=True)

    def siblings(self, type_mfn=om2.MFn.kDagNode):
        # type: () -> List[Any]
        if self.is_world:
            return []

        result = []

        mfn = self.mfn
        parent_mobj = mfn.parent(0)

        if parent_mobj.hasFn(om2.MFn.kWorld):
            result = [node for node in World.children(type_mfn) if node != self]
        else:
            # self と同階層で self に一致しない DAG Node
            tmp_mfn = om2.MFnDependencyNode()
            tmp_mfn_dag = om2.MFnDagNode()

            self_hash = self.mobject_handle.hashCode()
            tmp_mobj_handle = om2.MObjectHandle()

            parent_mfn = om2.MFnDagNode(parent_mobj)
            for i in range(parent_mfn.childCount()):
                mobj = parent_mfn.child(i)
                if not mobj.hasFn(type_mfn):
                    continue

                tmp_mobj_handle.assign(mobj)
                if tmp_mobj_handle.hashCode() == self_hash:
                    continue

                tmp_mfn.setObject(mobj)
                tmp_mfn_dag.setObject(mobj)

                node = _to_node_instance(tmp_mfn, tmp_mfn_dag.getPath())
                result.append(node)

        return result

    def add_child(self, child, **kwargs):
        # type: (DagNode) -> None
        if self.is_world:
            kwargs['world'] = True
            cmds.parent(child.abs_path, **kwargs)
        else:
            cmds.parent(child.abs_path, self.abs_path, **kwargs)
        return child

    def is_parent_of(self, node):
        # type: (DagNode) -> bool
        if self.mfn.isParentOf(node.mobject):
            return True
        return node.mfn.isChildOf(self.mobject)

    def is_child_of(self, node):
        # type: (DagNode) -> bool
        if self.mfn.isChildOf(node.mobject):
            return True
        return node.mfn.isParentOf(self.mobject)


World = DagNode(None, None)


class Transform(DagNode):

    _mfn_type = om2.MFn.kTransform
    _mfn_set = om2.MFnTransform
    _mel_type = 'transform'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Transform._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(Transform._mel_type, **kwargs)

    def __init__(self, mobj, mdagpath):
        # type: (om2.MObject, om2.MDagPath) -> NoReturn
        super(Transform, self).__init__(mobj, mdagpath)

    def shape(self):
        # type: () -> Shape
        mfn = self.mfn
        for i in range(mfn.childCount()):
            child_mobj = mfn.child(i)
            if child_mobj.hasFn(om2.MFn.kShape):
                return _to_node_instance(om2.MFnDependencyNode(child_mobj), om2.MFnDagNode(child_mobj).getPath())
        return None

    def shapes(self):
        # type: () -> List[Shape]
        return self.children(om2.MFn.kShape)

    def add_shape(self, shape):
        # type: (Shape) -> Shape
        cmds.parent(shape.abs_path, self.abs_path, shape=True, addObject=True)
        return shape


class Joint(Transform):

    _mfn_type = om2.MFn.kJoint
    _mfn_set = om2.MFnTransform
    _mel_type = 'joint'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Joint._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(Joint._mel_type, **kwargs)

    def __init__(self, mobj, mdagpath):
        # type: (om2.MObject, om2.MDagPath) -> NoReturn
        super(Joint, self).__init__(mobj, mdagpath)


class ObjectSet(Entity):

    _mfn_type = om2.MFn.kSet
    _mfn_set = om2.MFnSet
    _mel_type = 'objectSet'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ObjectSet._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(ObjectSet._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(ObjectSet, self).__init__(mobj)


class AnimLayer(ObjectSet):

    _mfn_type = om2.MFn.kAnimLayer
    _mfn_set = om2.MFnSet
    _mel_type = 'animLayer'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimLayer._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimLayer._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(AnimLayer, self).__init__(mobj)


class ShadingEngine(ObjectSet):

    _mfn_type = om2.MFn.kShadingEngine
    _mfn_set = om2.MFnDependencyNode
    _mel_type = 'shadingEngine'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ShadingEngine._mel_type
        return _ls_nodes(*args, **kwargs)

    # @staticmethod
    # def create(**kwargs):
    #     return _create_node(ShadingEngine._mel_type, **kwargs)

    def __init__(self, mobj):
        # type: (om2.MObject) -> NoReturn
        super(ShadingEngine, self).__init__(mobj)


class Shape(DagNode):

    _mfn_type = om2.MFn.kShape
    _mfn_set = om2.MFnDagNode
    _mel_type = 'shape'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Shape._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, mobj, mdagpath):
        # type: (om2.MObject, om2.MDagPath) -> NoReturn
        super(Shape, self).__init__(mobj, mdagpath)

    def instantiate(self, **kwargs):
        # type: () -> Transform
        transform = cmds.instance(self.abs_path, **kwargs)
        return _eval_node(transform, om2.MFnDependencyNode())


class Camera(Shape):

    _mfn_type = om2.MFn.kCamera
    _mfn_set = om2.MFnCamera
    _mel_type = 'camera'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Camera._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(Camera._mel_type, **kwargs)

    def __init__(self, mobj, mdagpath):
        # type: (om2.MObject, om2.MDagPath) -> NoReturn
        super(Camera, self).__init__(mobj, mdagpath)


class GeometryShape(Shape):

    _mfn_type = None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'geometryShape'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = GeometryShape._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, mobj, mdagpath):
        # type: (om2.MObject, om2.MDagPath) -> NoReturn
        super(GeometryShape, self).__init__(mobj, mdagpath)


class DeformableShape(GeometryShape):

    _mfn_type = None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'deformableShape'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = DeformableShape._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, mobj, mdagpath):
        # type: (om2.MObject, om2.MDagPath) -> NoReturn
        super(DeformableShape, self).__init__(mobj, mdagpath)


class ControlPoint(DeformableShape):

    _mfn_type = None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'controlPoint'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ControlPoint._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, mobj, mdagpath):
        # type: (om2.MObject, om2.MDagPath) -> NoReturn
        super(ControlPoint, self).__init__(mobj, mdagpath)


class SurfaceShape(ControlPoint):

    _mfn_type = None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'surfaceShape'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = SurfaceShape._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, mobj, mdagpath):
        # type: (om2.MObject, om2.MDagPath) -> NoReturn
        super(SurfaceShape, self).__init__(mobj, mdagpath)


class Mesh(SurfaceShape):

    _mfn_type = om2.MFn.kMesh
    _mfn_set = om2.MFnMesh
    _mel_type = 'mesh'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Mesh._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(Mesh._mel_type, **kwargs)

    def __init__(self, mobj, mdagpath):
        # type: (om2.MObject, om2.MDagPath) -> NoReturn
        super(Mesh, self).__init__(mobj, mdagpath)

    def face_comp(self, indices):
        # type: (Iterable[int]) -> MeshFaceComponent
        return self.__create_component(MeshFaceComponent, indices)

    def vertex_comp(self, indices):
        # type: (Iterable[int]) -> MeshVertexComponent
        return self.__create_component(MeshVertexComponent, indices)

    def edge_comp(self, indices):
        # type: (Iterable[int]) -> MeshEdgeComponent
        return self.__create_component(MeshEdgeComponent, indices)

    def vertex_face_comp(self, indices):
        # type: (Iterable[Iterable[int, int]]) -> MeshVertexFaceComponent
        return self.__create_component(MeshVertexFaceComponent, indices)

    def faces(self, comp=None):
        # type: (MeshFaceComponent) -> MeshFaceIter
        if comp is None:
            miter = om2.MItMeshPolygon(self.mobject)
        else:
            miter = om2.MItMeshPolygon(self.mdagpath, comp.mobject)
        return MeshFaceIter(miter)

    def vertices(self, comp=None):
        # type: (MeshVertexComponent) -> MeshVertexIter
        if comp is None:
            miter = om2.MItMeshVertex(self.mobject)
        else:
            miter = om2.MItMeshVertex(self.mdagpath, comp.mobject)
        return MeshVertexIterator(miter)

    def edges(self, comp=None):
        # type: (MeshEdgeComponent) -> MeshEdgeIter
        if comp is None:
            miter = om2.MItMeshEdge(self.mobject)
        else:
            miter = om2.MItMeshEdge(self.mdagpath, comp.mobject)
        return MeshEdgeIter(miter)

    def vertex_faces(self, comp=None):
        # type: (MeshFaceVertexComponent) -> MeshFaceVertexIter
        if comp is None:
            miter = om2.MItMeshFaceVertex(self.mobject)
        else:
            miter = om2.MItMeshFaceVertex(self.mdagpath, comp.mobject)
        return MeshVertexFaceIter(miter)

    def __create_component(self, cls, indices):
        comp = cls._comp_mfn()
        mobj = comp.create(cls._comp_type)
        comp.addElements(indices)
        return cls(self.mdagpath, mobj)



_NodeFactory.register(__name__)
_NodeFactory.register_default(DependNode, DagNode)
