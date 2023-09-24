# coding: utf-8
from typing import *

if TYPE_CHECKING:
    from .. import nodetypes as _nodetypes
    from .. import general as _general
    from .. import components as _components

    TDependNode = TypeVar('TDependNode', bound=_nodetypes.DependNode)
    TPlug = TypeVar('TPlug', bound=_general.Plug)
    TComponent = TypeVar('TComponent', bound=_components.Component)
