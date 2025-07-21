import typing
import collections.abc as abc

from ..pyside_module import *


class _Stretch(object):
    pass


TLayoutItem = typing.TypeVar('TLayoutItem', bound=(QWidget, QLayout, _Stretch))
TBoxLayout = typing.TypeVar('TBoxLayout', bound=QBoxLayout)

_stretch_instance = _Stretch()


def stretch():
    global _stretch_instance
    return _stretch_instance


def hbox(*items: TLayoutItem, **kwargs) -> QHBoxLayout:
    return _box(QHBoxLayout, items, kwargs)


def vbox(*items: TLayoutItem, **kwargs) -> QVBoxLayout:
    return _box(QVBoxLayout, items, kwargs)


def _box(cls: typing.Type[TBoxLayout], items: abc.Iterable[TLayoutItem], kwargs: dict[str, object]) -> TBoxLayout:
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


def delete_layout_children(layout: QLayout) -> QLayout:
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


def delete_layout_item_by_index(layout: QLayout, index: int) -> bool:
    item = layout.takeAt(index)
    if item.widget() is not None:
        item.widget().deleteLater()
    elif item.layout() is not None:
        delete_layout_children(item.layout())
    return True


def delete_layout_item(layout: QLayout, predicate: abc.Callable[[QObject], bool]) -> bool:
    delete_index = -1
    for i in range(layout.count()):
        child = layout.itemAt(i)
        if predicate(child):
            delete_index = i
            break
    if delete_index < 0:
        return False
    return delete_layout_item_by_index(layout, delete_index)
