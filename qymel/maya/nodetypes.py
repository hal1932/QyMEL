import collections.abc as abc
import typing

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2
import maya.api.OpenMayaAnim as _om2anim

from . import objects as _objects
from . import general as _general
from . import components as _components
from . import iterators as _iterators
from .internal import factory as _factory
from .internal import graphs as _graphs


# 呼び出し回数が極端に多くなる可能性のある静的メソッドをキャッシュ化しておく
_graphs_get_mobject = _graphs.get_mobject
_graphs_eval_node = _graphs.eval_node
_graphs_eval_plug = _graphs.eval_plug
_graphs_to_node_instance = _graphs.to_node_instance
_graphs_to_comp_instance = _graphs.to_comp_instance
_factory_PlugFactory_create = _factory.PlugFactory.create


TFnDependNode = typing.TypeVar('TFnDependNode', bound=_om2.MFnDependencyNode)


class DependNode(_objects.MayaObject, typing.Generic[TFnDependNode]):

    _mfn_type: int = _om2.MFn.kDependencyNode
    _mfn_set: typing.Type[TFnDependNode] = _om2.MFnDependencyNode
    _mel_type: str = None

    @classmethod
    def ls(cls, *args, **kwargs) -> list['DependNode']:
        mel_type = cls._mel_type
        if 'typ' in kwargs:
            del kwargs['type']
        if not mel_type:
            if 'type' in kwargs:
                del kwargs['type']
        else:
            kwargs['type'] = mel_type
        kwargs['noIntermediate'] = True
        return _graphs.ls_nodes(*args, **kwargs)

    @property
    def mel_object(self) -> str:
        return self.full_name

    @property
    def mfn(self) -> TFnDependNode|None:
        mfn_set = self.__class__._mfn_set

        if mfn_set is None:
            return None

        mfn = self._mfn
        if mfn is None:
            mfn = mfn_set(self.mobject)
            self._mfn = mfn

        return mfn

    @property
    def node_type(self) -> str:
        return self.mfn.typeName

    @property
    def is_default_node(self) -> str:
        return self.mfn.isDefaultNode

    @property
    def name(self) -> str:
        return self.mfn.name()

    @property
    def full_name(self) -> str:
        return self.mfn.name()

    @property
    def abs_name(self) -> str:
        return self.mfn.absoluteName()

    @property
    def namespace(self) -> str:
        return self.mfn.namespace

    @property
    def is_locked(self) -> bool:
        return self.mfn.isLocked

    @property
    def is_from_referenced_file(self) -> bool:
        return self.mfn.isFromReferencedFile

    def __init__(self, obj: _om2.MObject|str) -> None:
        if isinstance(obj, str):
            obj, _ = _graphs_get_mobject(obj)

        super(DependNode, self).__init__(obj)
        self._mfn: _om2.MFnDependencyNode|None = None
        self._plugs: dict[str, _general.Plug] = {}

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.full_name}')"

    def __getattr__(self, item: str) -> _general.Plug:
        plug = self._plugs.get(item, None)
        if plug is not None:
            return plug

        try:
            mplug = self.mfn.findPlug(item, False)
        except RuntimeError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

        plug = _factory_PlugFactory_create(mplug)
        self._plugs[item] = plug

        return plug

    def connections(self, **kwargs) -> list['DependNode'|_general.Plug]:
        # 自前でプラグを辿るより listConnections のほうが速い
        others = _cmds.listConnections(self.mel_object, **kwargs) or []

        if 'plugs' in kwargs or 'p' in kwargs:
            return [_graphs_eval_plug(name) for name in others]

        tmp_mfn = _om2.MFnDependencyNode()
        return [_graphs_eval_node(name, tmp_mfn) for name in others]

    def sources(self, **kwargs) -> list['DependNode'|_general.Plug]:
        kwargs.pop('s', None)
        kwargs.pop('d', None)
        kwargs['source'] = True
        kwargs['destination'] = False
        return self.connections(**kwargs)

    def destinations(self, **kwargs) -> list['DependNode'|_general.Plug]:
        kwargs.pop('s', None)
        kwargs.pop('d', None)
        kwargs['source'] = False
        kwargs['destination'] = True
        return self.connections(**kwargs)

    def history(self, **kwargs) -> list['DependNode']:
        nodes = _cmds.listHistory(self.mel_object, **kwargs)
        tmp_mfn = _om2.MFnDependencyNode()
        return [_graphs_eval_node(name, tmp_mfn) for name in nodes]

    def rename(self, new_name: str) -> None:
        _cmds.rename(self.mel_object, new_name)

    def lock(self) -> None:
        _cmds.lockNode(self.mel_object, lock=True)

    def unlock(self) -> None:
        _cmds.lockNode(self.mel_object, lock=False)

    def duplicate(self, **kwargs) -> 'DependNode':
        duplicated_node_name = _cmds.duplicate(self.mel_object, **kwargs)
        return _graphs_eval_node(duplicated_node_name, _om2.MFnDependencyNode())

    def delete(self) -> None:
        _cmds.delete(self.mel_object)


class ContainerBase(DependNode[TFnDependNode], typing.Generic[TFnDependNode]):

    _mfn_type = _om2.MFn.kContainerBase
    _mel_type = 'containerBase'


class DisplayLayer(DependNode[TFnDependNode], typing.Generic[TFnDependNode]):

    _mfn_type = _om2.MFn.kDisplayLayer
    _mel_type = 'displayLayer'

    DISPLAY_TYPE_NORMAL = 0
    DISPLAY_TYPE_TEMPLATE = 1
    DISPLAY_TYPE_REFERENCE = 2

    @staticmethod
    def create(**kwargs) -> 'DisplayLayer':
        return DisplayLayer(_cmds.createDisplayLayer(**kwargs))

    @property
    def display_type(self) -> int:
        return self.displayType.get()

    def members(self) -> list['DagNode']:
        tmp_mfn = _om2.MFnDependencyNode()
        members = _cmds.editDisplayLayerMembers(self.mel_object, query=True, fullNames=True)
        return [_graphs_eval_node(node, tmp_mfn) for node in members or []]

    def make_current(self) -> None:
        _cmds.editDisplayLayerMembers(currentDisplayLayer=self.mel_object)

    def add(self, node: 'DagNode', no_recurse: bool = True) -> None:
        _cmds.editDisplayLayerMembers(self.mel_object, node.mel_object, noRecurse=no_recurse)

    def extend(self, nodes: abc.Sequence['DagNode'], no_recurse: bool = True) -> None:
        node_paths = [node.mel_object for node in nodes]
        _cmds.editDisplayLayerMembers(self.mel_object, *node_paths, noRecurse=no_recurse)

    def remove(self, node: 'DagNode', no_recurse: bool = True) -> None:
        _cmds.editDisplayLayerMembers('defaultLayer', node.mel_object, noRecurse=no_recurse)

    def clear(self) -> None:
        nodes = _cmds.editDisplayLayerMembers(self.mel_object, query=True, fullNames=True)
        if nodes is not None:
            _cmds.editDisplayLayerMembers('defaultLayer', nodes, noRecurse=True)


class GeometryFilter(DependNode[TFnDependNode], typing.Generic[TFnDependNode]):

    _mfn_type = _om2.MFn.kGeometryFilt
    _mel_type = 'geometryFilter'

    @staticmethod
    def create(**kwargs) -> 'GeometryFilter':
        return _graphs.create_node(GeometryFilter._mel_type, **kwargs)


class SkinCluster(DependNode[_om2anim.MFnSkinCluster]):

    _mfn_type = _om2.MFn.kSkinClusterFilter
    _mfn_set = _om2anim.MFnSkinCluster
    _mel_type = 'skinCluster'

    @staticmethod
    def create(**kwargs) -> 'SkinCluster':
        return SkinCluster(_cmds.skinCluster(**kwargs))

    def influences(self) -> list['Joint']:
        return [Joint(mdagpath) for mdagpath in self.mfn.influenceObjects()]

    def influence_index(self, joint: 'Joint') -> int:
        return self.mfn.indexForInfluenceObject(joint.mdagpath)

    def weights(self,
                mesh: 'Mesh',
                component: _components.MeshVertex|None = None,
                influences: abc.Sequence['Joint']|None = None
    ) -> list[list[float]]:
        mfn: _om2anim.MFnSkinCluster = self.mfn

        if component is None:
            component = mesh.vertex_comp(range(mesh.vertex_count))

        if influences is None:
            flatten_weights, infl_count = mfn.getWeights(mesh.mdagpath, component.mobject)
            influence_mdagpaths = mfn.influenceObjects()
        else:
            influence_mdagpaths = [infl.mdagpath for infl in influences]
            influence_indices = [mfn.indexForInfluenceObject(dagpath) for dagpath in influence_mdagpaths]
            flatten_weights = mfn.getWeights(mesh.mdagpath, component.mobject, _om2.MIntArray(influence_indices))
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


class Entity(ContainerBase[TFnDependNode], typing.Generic[TFnDependNode]):
    pass


class ObjectSet(Entity[_om2.MFnSet]):

    _mfn_type = _om2.MFn.kSet
    _mfn_set = _om2.MFnSet
    _mel_type = 'objectSet'

    @staticmethod
    def create(**kwargs) -> 'ObjectSet':
        return ObjectSet(_cmds.sets(**kwargs))

    def members(self, flatten: bool = False) -> list[_objects.MayaObject]:
        result: list[_objects.MayaObject] = []

        mfn: _om2.MFnSet = self.mfn
        selection = mfn.getMembers(flatten)

        tmp_mfn = _om2.MFnDependencyNode()
        tmp_mfn_comp = _om2.MFnComponent()

        for i in range(selection.length()):
            try:
                # component
                mdagpath, mobj = selection.getComponent(i)
                tmp_mfn_comp.setObject(mobj)
                comp = _graphs_to_comp_instance(tmp_mfn_comp, mdagpath, mobj)
                result.append(comp)

            except RuntimeError:
                # node
                mobj = selection.getDependNode(i)
                tmp_mfn.setObject(mobj)

                mdagpath = None
                if mobj.hasFn(_om2.MFn.kDagNode):
                    mdagpath = selection.getDagPath(i)

                node = _graphs_to_node_instance(tmp_mfn, mdagpath)
                result.append(node)

        return result

    def add(self, obj: _objects.MayaObject, force: bool = False) -> None:
        if not force:
            _cmds.sets(obj.mel_object, addElement=self.mel_object)
        else:
            _cmds.sets(obj.mel_object, forceElement=self.mel_object)

    def extend(self, objs: abc.Sequence[_objects.MayaObject], force: bool=False) -> None:
        if not force:
            _cmds.sets(*[o.mel_object for o in objs], addElement=self.mel_object)
        else:
            _cmds.sets(*[o.mel_object for o in objs], forceElement=self.mel_object)

    def remove(self, obj: _objects.MayaObject|abc.Iterable[_objects.MayaObject]) -> None:
        if isinstance(obj, abc.Iterable):
            _cmds.sets(*[o.mel_object for o in obj], remove=self.mel_object)
        else:
            _cmds.sets(obj.mel_object, remove=self.mel_object)

    def clear(self) -> None:
        _cmds.sets(clear=self.mel_object)


class AnimLayer(ObjectSet):

    _mfn_type = _om2.MFn.kAnimLayer
    _mel_type = 'animLayer'

    @staticmethod
    def create(**kwargs) -> 'AnimLayer':
        return AnimLayer(_cmds.animLayer(**kwargs))


class ShadingEngine(ObjectSet):

    _mfn_type = _om2.MFn.kShadingEngine
    _mel_type = 'shadingEngine'

    @staticmethod
    def create(**kwargs) -> 'ShadingEngine':
        kwargs['renderable'] = True
        kwargs.pop('r', None)
        return ShadingEngine(_cmds.sets(**kwargs))

    def materials(self) -> list[DependNode]:
        names = _cmds.ls(_cmds.listHistory(self.mel_object), materials=True)
        tmp_mfn = _om2.MFnDependencyNode()
        return [_graphs_eval_node(name, tmp_mfn) for name in names]


class AnimCurve(DependNode[_om2anim.MFnAnimCurve]):

    _mfn_type = _om2.MFn.kAnimCurve
    _mfn_set = _om2anim.MFnAnimCurve
    _mel_type = 'animCurve'

    _input_type = None
    _output_type = None

    @staticmethod
    def create(**kwargs) -> 'AnimCurve':
        return _graphs.create_node(AnimCurve._mel_type, **kwargs)

    @property
    def key_count(self) -> int:
        return self.mfn.numKeys

    def key(self, index: int) -> float:
        return self.mfn.input(index).asUnits(_om2.MTime.uiUnit())

    def value(self, index: int) -> float:
        return self._to_output(self.mfn.value(index))

    def keys(self) -> list[float]:
        mfn = self.mfn
        return [self._from_input(mfn.input(i)) for i in range(mfn.numKeys)]

    def values(self) -> list[float]:
        mfn = self.mfn
        return [self._to_output(mfn.value(i)) for i in range(mfn.numKeys)]

    def evaluate(self, time: float) -> float:
        value = self.mfn.evaluate(self._to_input(time))
        return self._to_output(value)

    def in_tangent_type(self, index: int) -> int:
        return self.mfn.inTangentType(index)

    def out_tangent_type(self, index: int) -> int:
        return self.mfn.outTangentType(index)

    def set_tangent_type(
            self,
            index: int|tuple[int|int],
            in_type: int|None = None,
            out_type: int|None = None
     ) -> None:
        kwargs = {}
        if isinstance(index, int):
            index = (index, 0)
        kwargs['index'] = index

        if in_type is not None:
            kwargs['inTangentType'] = self._tangent_type_int_to_str(in_type)
        if out_type is not None:
            kwargs['outTangentType'] = self._tangent_type_int_to_str(out_type)

        _cmds.keyTangent(self.mel_object, **kwargs)

    def set_keyframe(self, **kwargs) -> bool:
        outputs = self.output.destinations()
        if len(outputs) == 0:
            return False
        _cmds.setKeyframe(outputs[0].mel_object, **kwargs)
        return True

    def _to_input(self, value: float) -> float:
        input_type = self.__class__._input_type
        if input_type is None:
            return value
        return input_type(value, input_type.uiUnit())

    def _from_input(self, value: _om2.MTime|_om2.MAngle|_om2.MDistance|float) -> float:
        if isinstance(value, float):
            return value
        return value.asUnits(self.__class__._input_type.uiUnit())

    def _to_output(self, value: float) -> float:
        output_type = self.__class__._output_type
        if output_type is None:
            return value
        return output_type(value).asUnits(output_type.uiUnit())

    def _tangent_type_int_to_str(self, i: int) -> str:
        types = {
            _om2anim.MFnAnimCurve.kTangentFixed: 'fixed',
            _om2anim.MFnAnimCurve.kTangentLinear: 'linear',
            _om2anim.MFnAnimCurve.kTangentFlat: 'flat',
            _om2anim.MFnAnimCurve.kTangentStep: 'step',
            _om2anim.MFnAnimCurve.kTangentStepNext: 'stepnext',
            _om2anim.MFnAnimCurve.kTangentClamped: 'clamped',
            _om2anim.MFnAnimCurve.kTangentPlateau: 'plateau',
            _om2anim.MFnAnimCurve.kTangentAuto: 'auto',
        }
        return types[i]


class AnimCurveTA(AnimCurve):

    _mel_type = 'animCurveTA'

    _input_type = _om2.MTime
    _output_type = _om2.MAngle

    @staticmethod
    def create(**kwargs) -> 'AnimCurveTA':
        return _graphs.create_node(AnimCurveTA._mel_type, **kwargs)


class AnimCurveTL(AnimCurve):

    _mel_type = 'animCurveTL'

    _input_type = _om2.MTime
    _output_type = _om2.MDistance

    @staticmethod
    def create(**kwargs) -> 'AnimCurveTL':
        return _graphs.create_node(AnimCurveTL._mel_type, **kwargs)


class AnimCurveTT(AnimCurve):

    _mel_type = 'animCurveTT'

    _input_type = _om2.MTime
    _output_type = _om2.MTime

    @staticmethod
    def create(**kwargs) -> 'AnimCurveTT':
        return _graphs.create_node(AnimCurveTT._mel_type, **kwargs)


class AnimCurveTU(AnimCurve):

    _mel_type = 'animCurveTU'

    _input_type = _om2.MTime
    _output_type = None

    @staticmethod
    def create(**kwargs) -> 'AnimCurveTT':
        return _graphs.create_node(AnimCurveTU._mel_type, **kwargs)

    def _to_input(self, value: float) -> _om2.MTime:
        return _om2.MTime(value)


class AnimCurveUA(AnimCurve):

    _mel_type = 'animCurveUA'

    _in_type = None
    _out_type = _om2.MAngle

    @staticmethod
    def create(**kwargs) -> 'AnimCurveUA':
        return _graphs.create_node(AnimCurveUA._mel_type, **kwargs)


class AnimCurveUL(AnimCurve):

    _mel_type = 'animCurveUL'

    _input_type = None
    _output_type = _om2.MDistance

    @staticmethod
    def create(**kwargs) -> 'AnimCurveUL':
        return _graphs.create_node(AnimCurveUL._mel_type, **kwargs)


class AnimCurveUT(AnimCurve):

    _mel_type = 'animCurveUT'

    _input_type = None
    _output_type = _om2.MTime

    @staticmethod
    def create(**kwargs) -> 'AnimCurveUT':
        return _graphs.create_node(AnimCurveUT._mel_type, **kwargs)


class AnimCurveUU(AnimCurve):

    _mel_type = 'animCurveUU'

    _input_type = None
    _output_type = None

    @staticmethod
    def create(**kwargs) -> 'AnimCurveUU':
        return _graphs.create_node(AnimCurveUU._mel_type, **kwargs)


TFnDagNode = typing.TypeVar('TFnDagNode', bound=_om2.MFnDagNode)


class DagNode(Entity[TFnDagNode], typing.Generic[TFnDagNode]):

    _mfn_type = _om2.MFn.kDagNode
    _mfn_set = _om2.MFnDagNode
    _mel_type = None

    @classmethod
    def ls(cls, *args, **kwargs) -> list['DagNode']:
        kwargs['dagObjects'] = True
        return super().ls(*args, **kwargs)

    @property
    def mdagpath(self) -> _om2.MDagPath:
        return self._mdagpath

    @property
    def full_name(self) -> str:
        return self._mdagpath.fullPathName()

    @property
    def root_node(self) -> 'DagNode':
        mdagpath = _om2.MDagPath(self.mdagpath)
        root_path = mdagpath.pop(mdagpath.length() - 1)
        return _graphs_to_node_instance(_om2.MFnDagNode(root_path), root_path)

    @property
    def is_world(self) -> bool:
        return self == world

    @property
    def has_parent(self) -> bool:
        mfn = self.mfn
        if mfn.parentCount() > 1:
            return True
        parent_mobj = mfn.parent(0)
        return not parent_mobj.hasFn(_om2.MFn.kWorld)

    @property
    def has_child(self) -> bool:
        return self.mfn.childCount() > 0

    @property
    def is_instanced(self) -> bool:
        return self.mfn.isInstanced()

    @property
    def instance_number(self) -> int:
        return self.mdagpath.instanceNumber()

    @property
    def instance_count(self) -> int:
        return self.mfn.instanceCount(False)

    @property
    def indirect_instance_count(self) -> int:
        return self.mfn.instanceCount(True)

    @property
    def is_intermediate(self) -> bool:
        return self.mfn.isIntermediateObject

    @property
    def local_bounding_box(self) -> _om2.MBoundingBox:
        return self.mfn.boundingBox

    def __init__(self, obj: str|_om2.MObject|None) -> None:
        if isinstance(obj, str):
            _, obj = _graphs_get_mobject(obj)

        if obj is None:
            # self is World
            obj = _graphs.get_world_mobject()

        if isinstance(obj, _om2.MObject):
            obj = _om2.MDagPath.getAPathTo(obj)

        super(DagNode, self).__init__(obj.node())
        self._mdagpath = obj

    def __repr__(self) -> str:
        if self.is_world:
            return f'{self.__class__.__name__}(world)'
        return super().__repr__()

    def relatives(self, **kwargs) -> list['DagNode']:
        if self.is_world:
            raise NotImplementedError('World.relatives() is not implemented')

        kwargs['path'] = True
        others = _cmds.listRelatives(self.mel_object, **kwargs)
        if others is None:
            return []

        tmp_mfn = _om2.MFnDependencyNode()
        return [_graphs_eval_node(name, tmp_mfn) for name in others]

    def parent(self, index: int = 0) -> typing['DagNode', None]:
        if self.is_world:
            return None

        parent_mobj = self.mfn.parent(index)
        parent_mfn = _om2.MFnDependencyNode(parent_mobj)
        parent_mfn_dag = _om2.MFnDagNode(parent_mobj)

        return _graphs_to_node_instance(parent_mfn, parent_mfn_dag.getPath())

    def parents(self, **kwargs) -> list['DagNode']:
        if self.is_world:
            return []
        kwargs['allParents'] = True
        return self.relatives(**kwargs)

    def child(self, index: int = 0) -> typing.Optional['DagNode']:
        if self.is_world:
            return self.children()[index]

        mfn = self.mfn
        if index >= mfn.childCount():
            return None

        child_mobj = mfn.child(index)
        child_mfn = _om2.MFnDagNode(child_mobj)
        return _graphs_to_node_instance(child_mfn, _om2.MFnDagNode(child_mobj).getPath())

    def first_child(self, **kwargs) -> typing.Optional['DagNode']:
        if 'name' not in kwargs:
            return self.child(0)

        kwargs['children'] = True
        children = self.children(**kwargs)
        if len(children) == 0:
            return None

        name = kwargs.pop('name', children[0].name)
        for child in children:
            if child.name == name:
                return child

        return None

    def last_child(self, **kwargs) -> typing.Optional['DagNode']:
        if 'name' not in kwargs:
            return self.child(0)

        kwargs['children'] = True
        children = self.children(**kwargs)
        if len(children) == 0:
            return None

        children.reverse()

        name = kwargs.pop('name', children[0].name)
        for child in children:
            if child.name == name:
                return child

        return None

    def children(self, **kwargs) -> list['DagNode']:
        if self.is_world:
            kwargs['assemblies'] = True
            return _graphs.ls_nodes(**kwargs)

        kwargs['children'] = True
        return self.relatives(**kwargs)

    def ancestors(self, **kwargs) -> list['DagNode']:
        if self.is_world:
            return []

        result = []

        mfn = self.mfn
        tmp_mfn = _om2.MFnDependencyNode()
        tmp_mfn_dag = _om2.MFnDagNode()

        no_intermediate = kwargs.get('noIntermediate', False)
        type_name = kwargs.get('type', None)

        while mfn.parentCount() > 0:
            parent_mobj = mfn.parent(0)

            if parent_mobj.hasFn(_om2.MFn.kWorld):
                break

            tmp_mfn_dag.setObject(parent_mobj)
            if no_intermediate and tmp_mfn_dag.isIntermediateObject:
                continue
            if type_name is not None and tmp_mfn_dag.typeName != type_name:
                continue

            tmp_mfn.setObject(parent_mobj)
            node = _graphs_to_node_instance(tmp_mfn, tmp_mfn_dag.getPath())
            result.append(node)

            mfn = tmp_mfn_dag

        return result

    def descendents(self, **kwargs) -> list['DagNode']:
        if self.is_world:
            kwargs['dagObjects'] = True
            return _graphs.ls_nodes(**kwargs)

        kwargs['allDescendents'] = True
        return self.relatives(**kwargs)

    def siblings(self, **kwargs) -> list['DagNode']:
        if self.is_world:
            return []

        result = []

        mfn = self.mfn
        parent_mobj = mfn.parent(0)

        if parent_mobj.hasFn(_om2.MFn.kWorld):
            result = [node for node in world.children(**kwargs) if node != self]
        else:
            # self と同階層で self に一致しない DAG Node
            tmp_mfn = _om2.MFnDependencyNode()
            tmp_mfn_dag = _om2.MFnDagNode()

            self_hash = self.mobject_handle.hashCode()
            tmp_mobj_handle = _om2.MObjectHandle()

            no_intermediate = kwargs.get('noIntermediate', False)
            type_name = kwargs.get('type', None)

            parent_mfn = _om2.MFnDagNode(parent_mobj)
            for i in range(parent_mfn.childCount()):
                mobj = parent_mfn.child(i)

                tmp_mobj_handle.assign(mobj)
                if tmp_mobj_handle.hashCode() == self_hash:
                    continue

                tmp_mfn_dag.setObject(mobj)

                if no_intermediate and tmp_mfn_dag.isIntermediateObject:
                    continue
                if type_name is not None and tmp_mfn_dag.typeName != type_name:
                    continue

                tmp_mfn.setObject(mobj)
                node = _graphs_to_node_instance(tmp_mfn, tmp_mfn_dag.getPath())
                result.append(node)

        return result

    def add_child(self, child: 'DagNode', **kwargs) -> 'DagNode':
        if self.is_world:
            kwargs['world'] = True
            new_child_name = _cmds.parent(child.mel_object, **kwargs)[0]
        else:
            new_child_name = _cmds.parent(child.mel_object, self.mel_object, **kwargs)[0]

        if 'addObject' in kwargs or 'add' in kwargs:
            return _graphs_eval_node(new_child_name, _om2.MFnDependencyNode())
        return child

    def is_parent_of(self, node: 'DagNode') -> bool:
        if self.is_world:
            children = _cmds.ls(assemblies=True, long=True)
        else:
            children = _cmds.listRelatives(self.mel_object, children=True, fullPath=True) or []
        return node.mel_object in children

    def is_child_of(self, node: 'DagNode') -> bool:
        return node.is_parent_of(self)

    def is_ancestor_of(self, node: 'DagNode') -> bool:
        if self.is_world:
            return True
        ancestors = _cmds.listRelatives(node.mel_object, allParents=True, fullPath=True) or []
        return self.mel_object in ancestors

    def is_descendent_of(self, node: 'DagNode') -> bool:
        return node.is_ancestor_of(self)

    def is_instance_of(self, node: 'DagNode') -> bool:
        return self.mobject == node.mobject

    def instances(self) -> list['DagNode']:
        if not self.is_instanced:
            return []

        instances = []  # type: list[DagNode]

        tmp_mfn = _om2.MFnDagNode()
        mdagpath = self.mdagpath
        for other_mdagpath in _om2.MDagPath.getAllPathsTo(self.mobject):
            if other_mdagpath == mdagpath:
                continue
            tmp_mfn.setObject(other_mdagpath.node())
            node = _graphs_to_node_instance(tmp_mfn, _om2.MDagPath(other_mdagpath))
            instances.append(node)

        return instances


world = DagNode(None)


class Transform(DagNode[_om2.MFnTransform]):

    _mfn_type = _om2.MFn.kTransform
    _mfn_set = _om2.MFnTransform
    _mel_type = 'transform'

    @staticmethod
    def create(**kwargs) -> 'Transform':
        return _graphs.create_node(Transform._mel_type, **kwargs)

    @property
    def transformation(self) -> _om2.MTransformationMatrix:
        return self.mfn.transformation()

    def has_shape(self) -> bool:
        mfn = self.mfn
        for i in range(mfn.childCount()):
            child = mfn.child(i)
            if child.hasFn(_om2.MFn.kShape):
                return True
        return False

    def shape_count(self) -> int:
        count = 0
        mfn = self.mfn
        for i in range(mfn.childCount()):
            child = mfn.child(i)
            if child.hasFn(_om2.MFn.kShape):
                count += 1
        return count

    def shape(self) -> typing.Optional['Shape']:
        mdagpath = _om2.MDagPath(self.mdagpath)
        try:
            mdagpath.extendToShape()
        except RuntimeError:
            return None
        return _graphs_to_node_instance(_om2.MFnDependencyNode(mdagpath.node()), mdagpath)

    def shapes(self) -> list['Shape']:
        return self.relatives(shapes=True)

    def add_shape(self, shape: 'Shape') -> 'Shape':
        _cmds.parent(shape.mel_object, self.mel_object, shape=True, addObject=True)
        return shape

    def instantiate(self, **kwargs) -> 'Transform':
        transform = _cmds.instance(self.mel_object, **kwargs)[0]
        return _graphs_eval_node(transform, _om2.MFnDependencyNode())

    def world_bounding_box(self) -> _om2.MBoundingBox:
        bbox = _cmds.xform(self.mel_object, query=True, boundingBox=True)
        return _om2.MBoundingBox(
            _om2.MPoint(bbox[0], bbox[1], bbox[2]),
            _om2.MPoint(bbox[3], bbox[4], bbox[5])
        )


class Joint(Transform):

    _mfn_type = _om2.MFn.kJoint
    _mel_type = 'joint'

    @staticmethod
    def create(**kwargs) -> 'Joint':
        return Joint(_cmds.joint(**kwargs))


TFnShape = typing.TypeVar('TFnShape', bound=_om2.MFnDagNode)


class Shape(DagNode[TFnShape], typing.Generic[TFnShape]):

    _mfn_type = _om2.MFn.kShape
    _mel_type = 'shape'

    def transform(self) -> Transform|None:
        parent = self.parent()
        return parent if isinstance(parent, Transform) else None

    def shading_groups(self) -> list[ShadingEngine]:
        names = _cmds.ls(_cmds.listHistory(self.mel_object, future=True), type='shadingEngine')
        tmp_mfn = _om2.MFnDependencyNode()
        return [_graphs_eval_node(name, tmp_mfn) for name in names]

    def instantiate(self, **kwargs) -> 'Transform':
        transform = _cmds.instance(self.mel_object, **kwargs)
        return _graphs_eval_node(transform, _om2.MFnDependencyNode())

    def skin_cluster(self) -> typing.Optional['SkinCluster']:
        names = _cmds.ls(_cmds.listHistory(self.mel_object), type='skinCluster')
        if len(names) == 0:
            return None
        return SkinCluster(names[0])


class Locator(Shape[TFnShape]):

    _mfn_type = _om2.MFn.kLocator
    _mel_type = 'locator'


class Camera(Shape[_om2.MFnCamera]):

    _mfn_type = _om2.MFn.kCamera
    _mfn_set = _om2.MFnCamera
    _mel_type = 'camera'

    @staticmethod
    def create(**kwargs) -> 'Camera':
        return Camera(_cmds.camera(**kwargs))

    def is_startup_camera(self) -> bool:
        return _cmds.camera(self.mel_object, query=True, startupCamera=True)


class GeometryShape(Shape[TFnShape], typing.Generic[TFnShape]):

    _mel_type = 'geometryShape'


class DeformableShape(GeometryShape[TFnShape], typing.Generic[TFnShape]):

    _mel_type = 'deformableShape'


class ControlPoint(DeformableShape[TFnShape], typing.Generic[TFnShape]):

    _mel_type = 'controlPoint'


class SurfaceShape(ControlPoint[TFnShape], typing.Generic[TFnShape]):

    _mel_type = 'surfaceShape'


class CurveShape(ControlPoint[TFnShape], typing.Generic[TFnShape]):

    _mel_type = 'curveShape'


class NurbsCurve(CurveShape[_om2.MFnNurbsCurve]):

    _mfn_type = _om2.MFn.kNurbsCurveGeom
    _mfn_set = _om2.MFnNurbsCurve
    _mel_type = 'nurbsCurve'


class Mesh(SurfaceShape[_om2.MFnMesh]):

    _mfn_type = _om2.MFn.kMesh
    _mfn_set = _om2.MFnMesh
    _mel_type = 'mesh'

    @staticmethod
    def create(**kwargs) -> 'Mesh':
        return _graphs.create_node(Mesh._mel_type, **kwargs)

    @property
    def face_count(self) -> int:
        return self.mfn.numPolygons

    @property
    def vertex_count(self) -> int:
        return self.mfn.numVertices

    @property
    def edge_count(self) -> int:
        return self.mfn.numEdges

    @property
    def face_vertex_count(self) -> int:
        return self.mfn.numFaceVertices

    @property
    def uv_set_count(self) -> int:
        return self.mfn.numUVSets

    @property
    def color_set_count(self) -> int:
        return self.mfn.numColorSets

    def points(self, space: int =_om2.MSpace.kObject) -> _om2.MFloatPointArray:
        return self.mfn.getFloatPoints(space)

    def connected_shaders(self) -> dict['ShadingEngine', list[int]]:
        mobjs, face_ids = self.mfn.getConnectedShaders(self.instance_number)

        shaders = {index: ShadingEngine(mobj) for index, mobj in enumerate(mobjs)}

        result = {shader: [] for shader in shaders.values()}
        for face_id, shader_id in enumerate(face_ids):
            shader = shaders[shader_id]
            result[shader].append(face_id)

        return result

    def current_color_set(self) -> _general.ColorSet:
        mfn = self.mfn
        name = mfn.currentColorSetName(self.instance_number)
        return _general.ColorSet(name, self)

    def color_sets(self) -> list[_general.ColorSet]:
        mfn = self.mfn
        names = mfn.getColorSetNames()
        return [_general.ColorSet(name, self) for name in names]

    def current_uv_set(self) -> _general.UvSet:
        mfn = self.mfn
        name = mfn.currentUVSetName()
        return _general.UvSet(name, self)

    def uv_sets(self) -> list[_general.UvSet]:
        mfn = self.mfn
        names = mfn.getUVSetNames()
        return [_general.UvSet(name, self) for name in names]

    def add_color_set(self, name: str = '') -> _general.ColorSet:
        _cmds.select(self.mel_object, replace=True)
        name = _cmds.polyColorSet(create=True, colorSet=name)
        return _general.ColorSet(name, self)

    def face_comp(self, indices: abc.Sequence[int]|None = None) -> _components.MeshFace:
        return self.__create_component(_components.MeshFace, indices, self.face_count)

    def vertex_comp(self, indices: abc.Sequence[int]|None = None) -> _components.MeshVertex:
        return self.__create_component(_components.MeshVertex, indices, self.vertex_count)

    def edge_comp(self, indices: abc.Sequence[int]|None = None) -> _components.MeshEdge:
        return self.__create_component(_components.MeshEdge, indices, self.edge_count)

    def vertex_face_comp(self, indices: abc.Sequence[tuple[int, int]]|None = None) -> _components.MeshVertexFace:
        return self.__create_component(_components.MeshVertexFace, indices, [self.vertex_count, self.face_count])

    def faces(self, comp: _components.MeshFace|None = None) -> _iterators.MeshFaceIter:
        if comp is None:
            comp = self.face_comp()
        return comp.iterator()

    def vertices(self, comp: _components.MeshVertex|None = None) -> _iterators.MeshVertexIter:
        if comp is None:
            comp = self.vertex_comp()
        return comp.iterator()

    def edges(self, comp: _components.MeshEdge|None = None) -> _iterators.MeshEdgeIter:
        if comp is None:
            comp = self.edge_comp()
        return comp.iterator()

    def face_vertices(self, comp: _components.MeshVertexFace|None = None) -> _iterators.MeshFaceVertexIter:
        if comp is None:
            comp = self.vertex_face_comp()
        return comp.iterator()

    def __create_component(
            self,
            cls: type,
            indices: abc.Sequence[object]|None = None,
            complete_length: int|list[int]|None = None
    ) -> _components.Component:
        comp = cls._comp_mfn()
        mobj = comp.create(cls._comp_type)
        if indices is not None:
            comp.addElements(indices)
        else:
            if isinstance(complete_length, int):
                comp.setCompleteData(complete_length)
            else:
                comp.setCompleteData(*complete_length)
        return cls(mobj, self.mdagpath)


class FileReference(DependNode[_om2.MFnReference]):

    _mfn_type = _om2.MFn.kReference
    _mfn_set = _om2.MFnReference
    _mel_type = 'reference'

    @property
    def file_path(self) -> str:
        return self.mfn.fileName(True, False, False)

    @property
    def file_path_with_copy_number(self) -> str:
        return self.mfn.fileName(True, False, True)

    @property
    def unresolved_file_path(self) -> str:
        return self.mfn.fileName(False, False, False)

    @property
    def unresolved_file_path_with_copy_number(self) -> str:
        return self.mfn.fileName(False, False, True)

    @property
    def is_loaded(self) -> bool:
        return self.mfn.isLoaded()

    @property
    def associated_namespace(self) -> str:
        return ':' + self.mfn.associatedNamespace(False)

    def load(self, depth: str|None = None, return_new_nodes: bool = False) -> list[DependNode|None]:
        return self.replace(None, depth, return_new_nodes)

    def replace(
            self,
            file_path: str|None,
            depth: str|None = None,
            return_new_nodes: bool = False
    ) -> list[DependNode|None]:
        args = []
        if file_path is not None:
            args.append(file_path)

        kwargs = {
            'loadReference': self.mel_object,
            'returnNewNodes': return_new_nodes,
        }
        if depth is not None:
            kwargs['loadReferenceDepth'] = depth

        result = _cmds.file(*args, **kwargs)

        if return_new_nodes:
            tmp_mfn = _om2.MFnDependencyNode()
            return [_graphs_eval_node(name, tmp_mfn) for name in result]

        return None

    def unload(self, force: bool =False) -> None:
        _cmds.file(unloadReference=self.mel_object, force=force)

    def import_to_scene(self, strict: bool = False) -> None:
        _cmds.file(self.file_path, importReference=True, strict=strict)

    def remove(self, force: bool = False) -> None:
        _cmds.file(self.file_path, removeReference=True, force=force)

    def nodes(self) -> list[DependNode]:
        nodes = self.mfn.nodes()
        if len(nodes) == 0:
            return []

        mfn = _om2.MFnDependencyNode()
        mfn_dag = _om2.MFnDagNode()

        result = []
        for node in nodes:
            mfn.setObject(node)
            mdagpath = None
            if node.hasFn(_om2.MFn.kDagNode):
                mfn_dag.setObject(node)
                mdagpath = mfn_dag.getPath()
            result.append(_graphs_to_node_instance(mfn, mdagpath))

        return result


class FileTexture(DependNode):

    _mfn_type = _om2.MFn.kFileTexture
    _mel_type = 'file'


class Place2dTexture(DependNode):

    _mfn_type = _om2.MFn.kPlace2dTexture
    _mel_type = 'place2dTexture'


class Lambert(DependNode):

    _mfn_type = _om2.MFn.kLambert
    _mel_type = 'lambert'

    @classmethod
    def create(cls) -> 'Lambert':
        name = _cmds.shadingNode(cls._mel_type, asShader=True)
        sg = _cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='{}.SG'.format(name))
        _cmds.connectAttr('{}.outColor'.format(name), '{}.surfaceShader'.format(sg))
        return cls(name)


class Reflect(Lambert):

    _mfn_type = _om2.MFn.kReflect
    _mel_type = 'reflect'


class Phong(Reflect):

    _mfn_type = _om2.MFn.kPhong
    _mel_type = 'phong'


class PhongE(Reflect):

    _mfn_type = _om2.MFn.kPhongExplorer
    _mel_type = 'phongE'


class Blinn(Reflect):

    _mfn_type = _om2.MFn.kBlinn
    _mel_type = 'blinn'


_factory.NodeFactory.register(__name__)
_factory.NodeFactory.register_default(DependNode, DagNode)
