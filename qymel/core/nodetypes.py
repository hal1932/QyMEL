# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import maya.api.OpenMayaAnim as om2anim

from qymel.core.general import MayaObject, Plug, Component, MeshVertexComponent, MeshFaceComponent, MeshEdgeComponent, MeshVertexFaceComponent
from qymel.core.iterators import MeshVertexIter, MeshFaceIter, MeshEdgeIter, MeshVertexFaceIter
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
    def node_type(self):
        # type: () -> str
        return cmds.nodeType(self.abs_path)

    @property
    def name(self):
        # type: () -> str
        return self.mfn.name()

    @property
    def abs_name(self):
        # type: () -> str
        return self.mfn.absoluteName()

    @property
    def abs_path(self):
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

    @property
    def exists(self):
        # type: () -> bool
        return not self.mobject.isNull()

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _get_mobject(obj)

        super(DependNode, self).__init__(obj)
        self._mfn = None
        self._plugs = {}  # Dict[str, Plug]

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        return "{}('{}')".format(self.__class__.__name__, self.abs_path)

    def __getattr__(self, item):
        # type: (str) -> Any
        plug = self._plugs.get(item, None)
        if plug is not None:
            return plug

        try:
            mplug = self.mfn.findPlug(item, False)
        except RuntimeError:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, item))

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

    def sources(self, **kwargs):
        # type: (Any) -> Iterable[Any]
        kwargs.pop('s', None)
        kwargs.pop('d', None)
        kwargs['source'] = True
        kwargs['destination'] = False
        return self.connections(**kwargs)

    def destinations(self, **kwargs):
        # type: (Any) -> Iterable[Any]
        kwargs.pop('s', None)
        kwargs.pop('d', None)
        kwargs['source'] = False
        kwargs['destination'] = True
        return self.connections(**kwargs)

    def histories(self, **kwargs):
        nodes = cmds.listHistory(self.abs_path, **kwargs)
        tmp_mfn = om2.MFnDependencyNode()
        return [_eval_node(name, tmp_mfn) for name in nodes]

    def rename(self, new_name):
        # type: (str) -> NoReturn
        cmds.rename(self.abs_path, new_name)

    def lock(self):
        cmds.lockNode(self.abs_path, lock=True)

    def unlock(self):
        cmds.lockNode(self.abs_path, lock=False)

    def duplicate(self, **kwargs):
        # type: (Any) -> DependNode
        duplicated_node_name = cmds.duplicate(self.abs_path, **kwargs)
        return _eval_node(duplicated_node_name, om2.MFnDependencyNode())

    def delete(self):
        cmds.delete(self.abs_path)


class ContainerBase(DependNode):

    _mfn_type = om2.MFn.kContainerBase
    _mfn_set = om2.MFnDependencyNode
    _mel_type = 'containerBase'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ContainerBase._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(ContainerBase, self).__init__(obj)


class AnimCurve(DependNode):

    _mfn_type = om2.MFn.kAnimCurve
    _mfn_set = om2anim.MFnAnimCurve
    _mel_type = 'animCurve'

    _input = float
    _output = float

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurve._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurve._mel_type, **kwargs)

    @property
    def key_count(self):
        # type: () -> long
        return self.mfn.numKeys

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(AnimCurve, self).__init__(obj)

    def key(self, index):
        # type: (int) -> float
        return self.mfn.input(index).asUnits(om2.MTime.uiUnit())

    def value(self, index):
        # type: (int) -> float
        return self.mfn.value(index)

    def keys(self):
        # type: () -> List[float]
        mfn = self.mfn
        return [self._from_input(mfn.input(i)) for i in range(mfn.numKeys)]

    def key_range(self):
        # type: () -> Tuple[float, float]
        mfn = self.mfn
        start = mfn.input(0)
        end = mfn.input(mfn.numKeys - 1)
        return self._from_input(start), self._from_input(end)

    def values(self):
        # type: () -> List[float]
        mfn = self.mfn
        return [self._to_output(mfn.value(i)) for i in range(mfn.numKeys)]

    def evaluate(self, time):
        # type: (float) -> float
        value = self.mfn.evaluate(self._to_input(time))
        return self._to_output(value)

    def add_destination(self, plug):
        # type: (Plug) -> NoReturn
        self.output.connect(plug)

    def set_keyframe(self, **kwargs):
        # type: (Any) -> bool
        outputs = self.output.destinations()
        if len(outputs) == 0:
            return False

        cmds.setKeyframe(outputs[0].name, **kwargs)
        return True

    def _to_input(self, value):
        # type: (float) -> Union[om2.MTime, om2.MAngle, float]
        return value

    def _from_input(self, value):
        # type: (Union[om2.MTime, om2.MAngle, float]) -> float
        return value

    def _to_output(self, value):
        # type: (Union[om2.MTime, om2.MAngle, float]) -> float
        return value


class AnimCurveTA(AnimCurve):

    _mel_type = 'animCurveTA'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurveTA._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurveTA._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(AnimCurveTA, self).__init__(obj)

    def _to_input(self, value):
        # type: (float) -> Union[om2.MTime, om2.MAngle, float]
        return om2.MTime(value)

    def _from_input(self, value):
        # type: (Union[om2.MTime, om2.MAngle, float]) -> float
        return value.asUnits(om2.MTime.asUnits())

    def _to_output(self, value):
        # type: (Union[om2.MTime, om2.MAngle, float]) -> float
        return value.asUnits(om2.MAngle.uiUnit())


class AnimCurveTL(AnimCurve):

    _mel_type = 'animCurveTL'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurveTL._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurveTL._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(AnimCurveTL, self).__init__(obj)

    def _to_input(self, value):
        # type: (float) -> Union[om2.MTime, om2.MAngle, float]
        return om2.MTime(value)

    def _from_input(self, value):
        # type: (Union[om2.MTime, om2.MAngle, float]) -> float
        return value.asUnits(om2.MTime.uiUnit())


class AnimCurveTT(AnimCurve):

    _mel_type = 'animCurveTT'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurveTT._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurveTT._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(AnimCurveTT, self).__init__(obj)

    def _to_input(self, value):
        # type: (float) -> Union[om2.MTime, om2.MAngle, float]
        return om2.MTime(value)

    def _from_input(self, value):
        # type: (Union[om2.MTime, om2.MAngle, float]) -> float
        return value.asUnits(om2.MTime.uiUnit())

    def _to_output(self, value):
        # type: (Union[om2.MTime, om2.MAngle, float]) -> float
        return value.asUnits(om2.MTime.uiUnit())


class AnimCurveTU(AnimCurve):

    _mel_type = 'animCurveTU'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurveTU._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurveTU._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(AnimCurveTU, self).__init__(obj)

    def _to_input(self, value):
        # type: (float) -> Union[om2.MTime, om2.MAngle, float]
        return om2.MTime(value)


class AnimCurveUA(AnimCurve):

    _mel_type = 'animCurveUA'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurveUA._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurveUA._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(AnimCurveUA, self).__init__(obj)

    def _to_output(self, value):
        # type: (Union[om2.MTime, om2.MAngle, float]) -> float
        return value.asUnits(om2.MAngle.uiUnit())


class AnimCurveUL(AnimCurve):

    _mel_type = 'animCurveUL'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurveUL._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurveUL._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(AnimCurveUL, self).__init__(obj)


class AnimCurveUT(AnimCurve):

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurveUT._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurveUT._mel_type, **kwargs)

    _mel_type = 'animCurveUT'

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(AnimCurveUT, self).__init__(obj)

    def _to_output(self, value):
        # type: (Union[om2.MTime, om2.MAngle, float]) -> float
        return value.asUnits(om2.MTime.uiUnit())


class AnimCurveUU(AnimCurve):

    _mel_type = 'animCurveUU'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = AnimCurveUU._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        return _create_node(AnimCurveUU._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(AnimCurveUU, self).__init__(obj)


class DisplayLayer(DependNode):

    _mfn_type = om2.MFn.kDisplayLayer
    _mfn_set = om2.MFnDependencyNode
    _mel_type = 'displayLayer'

    kNormalType = 0
    kTemplateType = 1
    kReferenceType = 2

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = DisplayLayer._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        node = cmds.createDisplayLayer(**kwargs)
        return _eval_node(node, om2.MFnDependencyNode())

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(DisplayLayer, self).__init__(obj)

    def members(self):
        # type: () -> List[DagNode]
        tmp_mfn = om2.MFnDependencyNode()
        return [_eval_node(node, tmp_mfn) for node in cmds.editDisplayLayerMembers(self.abs_path, query=True, fullNames=True) or []]

    def make_current(self):
        # type: () -> NoReturn
        cmds.editDisplayLayerMembers(currentDisplayLayer=self.abs_path)

    def add(self, node, no_recurse=True):
        # type: (DagNode, bool) -> NoReturn
        cmds.editDisplayLayerMembers(self.abs_path, node.abs_path, noRecurse=no_recurse)

    def extend(self, nodes, no_recurse=True):
        # type: (Iterable[DagNode], bool) -> NoReturn
        node_paths = [node.abs_path for node in nodes]
        cmds.editDisplayLayerMembers(self.abs_path, *node_paths, noRecurse=no_recurse)

    def remove(self, node, no_recurse=True):
        # type: (DagNode, bool) -> NoReturn
        cmds.editDisplayLayerMembers('defaultLayer', node.abs_path, noRecurse=no_recurse)

    def clear(self):
        # type: () -> NoReturn
        nodes = cmds.editDisplayLayerMembers(self.abs_path, query=True, fullNames=True)
        if nodes is not None:
            cmds.editDisplayLayerMembers('defaultLayer', nodes, noRecurse=True)

    # def set_visible(self, value):
    #     # type: (bool) -> NoReturn
    #     self.visibility.set(value)
    #
    # def set_hide_on_playback(self, value):
    #     # type: (bool) -> NoReturn
    #     self.hideOnPlayback.set(value)

    def set_display_type(self, type):
        # type: (int) -> NoReturn
        self.displayType.set(type)


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

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(GeometryFilter, self).__init__(obj)


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

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(SkinCluster, self).__init__(obj)

    def influences(self):
        # type: () -> List[Joint]
        tmp_mfn = om2.MFnDependencyNode()
        return [_eval_node(name, tmp_mfn) for name in self.mfn.influenceObjects()]

    def weights(self, mesh, component=None, influences=None):
        # type: (Mesh, MeshVertexComponent, Iterable[Joint]) -> List[List[float]]
        mfn = self.mfn

        if component is None:
            component = mesh.vertex_comp(range(mesh.vertex_count))

        if influences is None:
            flatten_weights, infl_count = mfn.getWeights(mesh.mdagpath, component.mobject)
            influence_mdagpaths = mfn.influenceObjects()
        else:
            influence_mdagpaths = [i.mdagpath for i in influences]
            influence_indices = [mfn.indexForInfluenceObject(dagpath) for dagpath in influence_mdagpaths]
            flatten_weights = mfn.getWeights(mesh.mdagpath, component.mobject, om2.MIntArray(influence_indices))
            infl_count = len(influence_mdagpaths)

        weight_count = len(flatten_weights) / infl_count

        result = [None] * infl_count
        for i in range(infl_count):
            infl_index = mfn.indexForInfluenceObject(influence_mdagpaths[i])
            weights = [0.0] * weight_count
            for w in range(weight_count):
                weights[w] = flatten_weights[w * infl_count + infl_index]
            result[infl_index] = weights

        return result


class Entity(ContainerBase):

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(Entity, self).__init__(obj)


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
        return self.abs_path.split('|')[0]

    @property
    def is_world(self):
        # type:() -> bool
        return self == world

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

    @property
    def is_instanced(self):
        # type: () -> bool
        return self.mfn.isInstanced()

    @property
    def instance_number(self):
        # type: () -> int
        return self.mdagpath.instanceNumber()

    @property
    def instance_count(self):
        # type: () -> int
        return self.mfn.instanceCount(False)

    @property
    def indirect_instance_count(self):
        # type: () -> int
        return self.mfn.instanceCount(True)

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, mdagpath = _get_mobject(obj)

        if obj is None and mdagpath is None:
            # self is World
            obj = _get_world_mobject()
            mdagpath = om2.MFnDagNode(obj).getPath()

        super(DagNode, self).__init__(obj)
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
        return self.relatives(allParents=True)

    def child(self, index=0):
        # type: (int) -> DagNode
        mfn = self.mfn
        if index >= mfn.childCount():
            return None

        child_mobj = mfn.child(index)
        return _to_node_instance(child_mobj, om2.MFnDagNode(child_mobj).getPath())

    def children(self):
        # type: () -> List[DagNode]
        if not self.is_world:
            return self.relatives(children=True)

        result = []

        tmp_mfn = om2.MFnDependencyNode()
        tmp_mfn_dag = om2.MFnDagNode()

        self_hash = self.mobject_handle.hashCode()
        tmp_mobj_handle = om2.MObjectHandle()

        iter = om2.MItDependencyNodes()
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
        if self.is_world:
            return _ls_nodes()
        return self.relatives(allDescendents=True)

    def siblings(self, type_mfn=om2.MFn.kDagNode):
        # type: (int) -> List[Any]
        if self.is_world:
            return []

        result = []

        mfn = self.mfn
        parent_mobj = mfn.parent(0)

        if parent_mobj.hasFn(om2.MFn.kWorld):
            result = [node for node in world.children(type_mfn) if node != self]
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
        # type: (DagNode, Any) -> None
        if self.is_world:
            kwargs['world'] = True
            new_child_name = cmds.parent(child.abs_path, **kwargs)[0]
        else:
            new_child_name = cmds.parent(child.abs_path, self.abs_path, **kwargs)[0]

        if 'addObject' in kwargs or 'add' in kwargs:
            return _eval_node(new_child_name, om2.MFnDependencyNode())
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

    def is_instance_of(self, node):
        # type: (DagNode) -> bool
        return self.mobject == node.mobject

    def instances(self):
        # type: (bool) -> List[DagNode]
        tmp_mfn = om2.MFnDependencyNode()
        return [_eval_node(mdagpath.fullPathName(), tmp_mfn) for mdagpath in self.mfn.getAllPaths()]

    def other_instances(self):
        # type: (bool) -> List[DagNode]
        mfn = self.mfn
        self_path = mfn.fullPathName()
        tmp_mfn = om2.MFnDependencyNode()
        return [_eval_node(mdagpath.fullPathName(), tmp_mfn) for mdagpath in mfn.getAllPaths() if mdagpath.fullPathName() != self_path]


world = DagNode(None, None)


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

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(Transform, self).__init__(obj, mdagpath)

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
        return self.relatives(shapes=True)

    def add_shape(self, shape):
        # type: (Shape) -> Shape
        cmds.parent(shape.abs_path, self.abs_path, shape=True, addObject=True)
        return shape

    def instantiate(self, **kwargs):
        # type: (Any) -> Transform
        transform = cmds.instance(self.abs_path, **kwargs)
        return _eval_node(transform, om2.MFnDependencyNode())


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

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(Joint, self).__init__(obj, mdagpath)


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

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(ObjectSet, self).__init__(obj)

    def members(self, flatten=False):
        # type: (bool) -> List[DependNode]
        result = []  # type: List[DependNode]

        selection = self.mfn.getMembers(flatten)
        tmp_mfn = om2.MFnDependencyNode()

        for i in range(selection.length()):
            mobj = selection.getDependNode(i)
            tmp_mfn.setObject(mobj)

            mdagpath = None
            if mobj.hasFn(om2.MFn.kDagNode):
                mdagpath = selection.getDagPath(i)

            node = _to_node_instance(tmp_mfn, mdagpath)
            result.append(node)

        return result

    def add(self, obj, force=False):
        # type: (Union[DependNode, Component], bool) -> NoReturn
        if not force:
            cmds.sets(obj.abs_path, addElement=self.abs_path)
        else:
            cmds.sets(obj.abs_path, forceElement=self.abs_path)

    def extend(self, objs, force=False):
        # type: (Iterable[Union[DependNode, Component]], bool) -> NoReturn
        for obj in objs:
            self.add(obj, force)

    def remove(self, obj):
        # type: (Union[DependNode, Component]) -> NoReturn
        cmds.sets(obj.abs_path, remove=self.abs_path)

    def clear(self):
        # type: () -> NoReturn
        cmds.sets(clear=self.abs_path)


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

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(AnimLayer, self).__init__(obj)


class ShadingEngine(ObjectSet):

    _mfn_type = om2.MFn.kShadingEngine
    _mfn_set = om2.MFnSet
    _mel_type = 'shadingEngine'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ShadingEngine._mel_type
        return _ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        kwargs['renderable'] = True
        kwargs.pop('r', None)
        name = cmds.sets(**kwargs)
        return _eval_node(name, om2.MFnDependencyNode())

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        super(ShadingEngine, self).__init__(obj)

    def materials(self):
        # type: () -> [DependNode]
        names = cmds.ls(cmds.listHistory(self.abs_path), materials=True)
        tmp_mfn = om2.MFnDependencyNode()
        return [_eval_node(name, tmp_mfn) for name in names]


class Shape(DagNode):

    _mfn_type = om2.MFn.kShape
    _mfn_set = om2.MFnDagNode
    _mel_type = 'shape'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = Shape._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(Shape, self).__init__(obj, mdagpath)

    def shading_groups(self):
        # type: () -> [ShadingEngine]
        names = cmds.ls(cmds.listHistory(self.abs_path, future=True), type='shadingEngine')
        tmp_mfn = om2.MFnDependencyNode()
        return [_eval_node(name, tmp_mfn) for name in names]

    def instantiate(self, **kwargs):
        # type: (Any) -> Transform
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

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(Camera, self).__init__(obj, mdagpath)


class GeometryShape(Shape):

    _mfn_type = None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'geometryShape'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = GeometryShape._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(GeometryShape, self).__init__(obj, mdagpath)


class DeformableShape(GeometryShape):

    _mfn_type = None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'deformableShape'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = DeformableShape._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(DeformableShape, self).__init__(obj, mdagpath)


class ControlPoint(DeformableShape):

    _mfn_type = None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'controlPoint'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = ControlPoint._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(ControlPoint, self).__init__(obj, mdagpath)


class SurfaceShape(ControlPoint):

    _mfn_type = None
    _mfn_set = om2.MFnDagNode
    _mel_type = 'surfaceShape'

    @staticmethod
    def ls(*args, **kwargs):
        kwargs['type'] = SurfaceShape._mel_type
        return _ls_nodes(*args, **kwargs)

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(SurfaceShape, self).__init__(obj, mdagpath)


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

    @property
    def vertex_count(self):
        # type: () -> int
        return self.mfn.numVertices

    def __init__(self, obj, mdagpath=None):
        # type: (Union[om2.MObject, str], om2.MDagPath) -> NoReturn
        super(Mesh, self).__init__(obj, mdagpath)

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
        return MeshVertexIter(miter)

    def edges(self, comp=None):
        # type: (MeshEdgeComponent) -> MeshEdgeIter
        if comp is None:
            miter = om2.MItMeshEdge(self.mobject)
        else:
            miter = om2.MItMeshEdge(self.mdagpath, comp.mobject)
        return MeshEdgeIter(miter)

    def vertex_faces(self, comp=None):
        # type: (MeshVertexFaceComponent) -> MeshVertexFaceIter
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
