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


def delete_layout_children(layout):
    # type: (QLayout) -> QLayout
    if layout.count() == 0:
        return layout

    queue = []
    while layout.count() > 0:
        queue.append(layout.takeAt(0))

    while len(queue) > 0:
        item = queue.pop(0)

        if item.widget() is not None:
            item.widget().deleteLater()

        child_layout = item.layout()
        if child_layout is not None:
            while child_layout.count() > 0:
                queue.append(child_layout.takeAt(0))
            child_layout.deleteLater()

    return layout


def delete_layout_item_by_index(layout, index):
    # type: (QLayout, int) -> bool
    item = layout.takeAt(index)
    if item.widget() is not None:
        item.widget().deleteLater()
    elif item.layout() is not None:
        delete_layout_children(item.layout())
    return True


def delete_layout_item(layout, predicate):
    # type: (QLayout, int) -> bool
    delete_index = -1
    for i in xrange(layout.count()):
        child = layout.itemAt(i)
        if predicate(child):
            delete_index = i
            break
    if delete_index < 0:
        return False
    return delete_layout_item_by_index(layout, delete_index)
