# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

from ..pyside_module import *


class _Stretch(object): pass


_stretch_instance = _Stretch()


def stretch():
    global _stretch_instance
    return _stretch_instance


def hbox(*items, **kwargs):
    return _box(QHBoxLayout, items, kwargs)


def vbox(*items, **kwargs):
    return _box(QVBoxLayout, items, kwargs)


def _box(cls, items, kwargs):
    # type: (Type, List[Union[QWidget, QLayout, _Stretch]], Dict[str, Any]) -> NoReturn
    box = cls()
    for item in items:
        if isinstance(item, QWidget):
            box.addWidget(item)
        elif isinstance(item, QLayout):
            box.addLayout(item)
        elif isinstance(item, _Stretch):
            box.addStretch()

    for k, v in kwargs.items():
        if k == 'contents_margins':
            if isinstance(v, int):
                box.setContentsMargins(v, v, v, v)
            else:
                box.setContentsMargins(v)
        elif k == 'spacing':
            box.setSpacing(v)

    return box