import typing


if typing.TYPE_CHECKING:
    from .. import nodetypes as _nodetypes
    from .. import general as _general
    from .. import components as _components


TDependNode = typing.TypeVar('TDependNode', bound=_nodetypes.DependNode)
TDagNode = typing.TypeVar('TDagNode', bound=_nodetypes.DagNode)
TPlug = typing.TypeVar('TPlug', bound=_general.Plug)
TComponent = typing.TypeVar('TComponent', bound=_components.Component)
