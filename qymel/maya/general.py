# coding: utf-8
from typing import *
import functools

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2

from .internal import graphs as _graphs
from .internal import factory as _factory
from .internal import plug_impl as _plug_impl

if TYPE_CHECKING:
    from . import components as _components
    from . import nodetypes as _nodetypes


# 呼び出し回数が極端に多くなる可能性のある静的メソッドをキャッシュ化しておく
_om2_MFnComponent = _om2.MFnComponent
_om2_MFnDependencyNode = _om2.MFnDependencyNode
_om2_MFnDagNode = _om2.MFnDagNode
_om2_MDagPath_getAPathTo = _om2.MDagPath.getAPathTo
_om2_MFn_kDagNode = _om2.MFn.kDagNode
_cmds_getAttr = _cmds.getAttr
_cmds_setAttr = _cmds.setAttr
_cmds_connectAttr = _cmds.connectAttr
_cmds_disconnectAttr = _cmds.disconnectAttr
_graphs_eval = _graphs.eval
_graphs_eval_node = _graphs.eval_node
_graphs_eval_plug = _graphs.eval_plug
_graphs_eval_component = _graphs.eval_component


def deprecated(message):
    def _deprecated(func):
        @functools.wraps(func)
        def _(*args, **kwargs):
            print(u'[DEPRECATED] {} is deprecated. {}'.format(func.__name__, message))
            return func(*args, **kwargs)
        return _
    return _deprecated


def ls(*args: str, **kwargs: Any) -> List[Union['Plug', '_components.Component', '_nodetypes.DependNode']]:
    return _graphs.ls(*args, **kwargs)


def eval(obj_name: Union[str, Iterable[str]]) -> Any:
    tmp_mfn_comp = _om2_MFnComponent()
    tmp_mfn_node = _om2_MFnDependencyNode()
    if isinstance(obj_name, str):
        return _graphs_eval(obj_name, tmp_mfn_comp, tmp_mfn_node)
    else:
        return [_graphs_eval(name, tmp_mfn_comp, tmp_mfn_node) for name in obj_name]


def eval_node(node_name: str) -> '_nodetypes.DependNode':
    tmp_mfn = _om2_MFnDependencyNode()
    return _graphs_eval_node(node_name, tmp_mfn)


def eval_plug(plug_name: str) -> 'Plug':
    return _graphs_eval_plug(plug_name)


def eval_component(comp_name: str) -> '_components.Component':
    tmp_mfn = _om2_MFnComponent()
    return _graphs_eval_component(comp_name, tmp_mfn)


class Plug(object):

    @property
    def mel_object(self) -> str:
        mfn_node = self.mfn_node
        if isinstance(mfn_node, _om2_MFnDagNode):
            return '{}.{}'.format(mfn_node.fullPathName(), self._mplug.partialName())
        return self._mplug.name()

    @property
    def mplug(self) -> _om2.MPlug:
        return self._mplug

    @property
    def attribute_mobject(self) -> _om2.MObject:
        return self._mplug.attribute()

    @property
    def mfn_node(self) -> Union[_om2.MFnDependencyNode, _om2.MFnDagNode]:
        if self._mfn_node is None:
            node = self._mplug.node()
            if node.hasFn(_om2_MFn_kDagNode):
                mdagpath = _om2_MDagPath_getAPathTo(node)
                self._mfn_node = _om2_MFnDagNode(mdagpath)
            else:
                self._mfn_node = _om2_MFnDependencyNode(node)
        return self._mfn_node

    @property
    def is_null(self) -> bool:
        return self._mplug.isNull

    @property
    def name(self) -> str:
        return self._mplug.name()

    @property
    def partial_name(self) -> str:
        return self._mplug.partialName()

    @property
    def full_name(self) -> str:
        return _cmds.ls(self.mel_object, long=True)[0]

    @property
    def api_type(self) -> int:
        return self._mplug.attribute().apiType()

    @property
    def is_source(self) -> bool:
        return self._mplug.isSource

    @property
    def is_destination(self) -> bool:
        return self._mplug.isDestination

    @property
    def is_array(self) -> bool:
        return self._mplug.isArray

    @property
    def is_compound(self) -> bool:
        return self._mplug.isCompound

    @property
    def is_networked(self) -> bool:
        return self._mplug.isNetworked

    @property
    def is_locked(self) -> bool:
        return self._mplug.isLocked

    @property
    def exists(self) -> bool:
        return _cmds.objExists(self.mel_object)

    def __init__(self, plug: Union[_om2.MPlug, str]) -> None:
        if isinstance(plug, str):
            plug = _graphs.get_mplug(plug)
        self._mplug = _graphs.keep_mplug(plug)
        self._mfn_node: Optional[_om2.MFnDependencyNode] = None
        self._node: Optional[_nodetypes.DependNode] = None

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return "{}('{}')".format(self.__class__.__name__, self.name)

    def __getitem__(self, item: int) -> 'Plug':
        mplug = self._mplug

        if not mplug.isArray:
            raise RuntimeError('{} is not array'.format(self.name))

        return Plug(mplug.elementByLogicalIndex(item))

    def node(self) -> '_nodetypes.DependNode':
        if self._node is None:
            mfn_node = self.mfn_node
            if isinstance(mfn_node, _om2_MFnDagNode):
                mdagpath = mfn_node.getPath()
                self._node = _graphs.to_node_instance(mfn_node, mdagpath)
            else:
                self._node = _graphs.to_node_instance(mfn_node)
        return self._node

    def get(self) -> Any:
        mplug = self._mplug

        if mplug.isNetworked:
            raise RuntimeError('{} is networked'.format(self.name))

        return _plug_impl.plug_get_impl(mplug)

    def get_attr(self, **kwargs) -> Any:
        return _cmds_getAttr(self.mel_object, **kwargs)

    def set_attr(self, *args, **kwargs) -> Any:
        return _cmds_setAttr(self.mel_object, *args, **kwargs)

    def connect(self, dest_plug, **kwargs) -> None:
        _cmds_connectAttr(self.mel_object, dest_plug.mel_object, **kwargs)

    def disconnect(self, dest_plug: 'Plug', **kwargs) -> None:
        _cmds_disconnectAttr(self.mel_object, dest_plug.mel_object, **kwargs)

    def source(self) -> 'Plug':
        return Plug(self._mplug.source())

    def destinations(self) -> List['Plug']:
        return [Plug(mplug) for mplug in self._mplug.destinations()]


_factory.PlugFactory.register(Plug)


class ColorSet(object):

    @property
    def name(self) -> str:
        return self.__name

    @property
    def mel_object(self) -> str:
        return self.__name

    @property
    def mesh(self) -> '_nodetypes.Mesh':
        return self.__mesh

    @property
    def channels(self) -> int:
        return self.__mfn.getColorRepresentation(self.mel_object)

    @property
    def is_clamped(self) -> bool:
        return self.__mfn.isColorClamped(self.mel_object)

    @property
    def is_per_instance(self) -> bool:
        return self.__mfn.isColorSetPerInstance(self.mel_object)

    def __init__(self, name: str, mesh: '_nodetypes.Mesh') -> None:
        self.__name = name
        self.__mfn = mesh.mfn
        self.__mesh = mesh

    def __repr__(self) -> str:
        return "{}('{}', {})".format(self.__class__.__name__, self.mel_object, repr(self.mesh))

    def color(self, index: int) -> _om2.MColor:
        return self.__mfn.getColor(index, self.mel_object)

    def colors(self) -> _om2.MColorArray:
        return self.__mfn.getColors(self.mel_object)

    def color_index(self, face_id: int, local_vertex_id:int) -> int:
        return self.__mfn.getColorIndex(face_id, local_vertex_id, self.mel_object)

    def face_vertex_colors(self) -> _om2.MColorArray:
        return self.__mfn.getFaceVertexColors(self.mel_object)

    def vertex_colors(self) -> _om2.MColorArray:
        return self.__mfn.getVertexColors(self.mel_object)


class UvSet(object):

    @property
    def name(self) -> str:
        return self.__name

    @property
    def mel_object(self) -> str:
        return self.__name

    @property
    def mesh(self) -> '_nodetypes.Mesh':
        return self.__mesh

    def __init__(self, name: str, mesh: '_nodetypes.Mesh') -> None:
        self.__name = name
        self.__mesh = mesh
        self.__mfn = mesh.mfn
