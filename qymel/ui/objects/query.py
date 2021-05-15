# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

from ..pyside_module import *


_ObjectPredicate = Callable[[QObject], bool]
_ObjectSelector = Callable[[QObject], Any]


class ObjectQuery(object):
    """
    >>> # QWidget
    >>> #   - QVBoxLayout
    >>> #     - QPushButton
    >>> #     - QLineEdit
    >>> #     - QHBoxLayout
    >>> #       - QCheckBox
    >>> root = QWidget()
    >>> root_layout = QVBoxLayout()
    >>> root_layout.addWidget(QPushButton())
    >>> root_layout.addWidget(QLineEdit())
    >>> child_layout = QHBoxLayout()
    >>> child_layout.addWidget(QCheckBox())
    >>> root_layout.addLayout(child_layout)
    >>> root.setLayout(root_layout)
    >>>
    >>> query = ObjectQuery(root)
    >>> print(query.child(lambda obj: isinstance(obj, QVBoxLayout)), lambda obj: obj.objectName())
    >>> print(query.children(lambda obj: isinstance(obj, QLayout)))
    >>> print(query.descendent(lambda obj: isinstance(obj, QPushButton)))
    >>> print(query.descendents(lambda obj: isinstance(obj, QLayout)))
    >>>
    >>> query1 = ObjectQuery(child_layout)
    >>> print(query1.parent(lambda obj: isinstance(obj, QVBoxLayout)))
    >>> print(query1.ancestor(lambda obj: isinstance(obj, QWidget)))
    >>> print(query1.ancestors(selector=lambda obj: obj.objectName()))
    """

    @property
    def object(self):
        # type: () -> QObject
        return self.__object

    def __init__(self, obj):
        # type: (QObject) -> NoReturn
        self.__object = obj

    def parent(self, predicate=None, selector=None):
        # type: (Optional[_ObjectPredicate], Optional[_ObjectSelector]) -> Optional[Union[QObject, Any]]
        parent = self.object.parent()
        if not predicate or predicate(parent):
            return selector(parent) if selector else parent
        return None

    def child(self, predicate=None, selector=None):
        # type: (Optional[_ObjectPredicate], Optional[_ObjectPredicate]) -> Optional[Union[QObject, Any]]
        if not predicate:
            return self.object.findChild()
        for child in self.object.children():
            if predicate(child):
                return selector(child) if selector else child
        return None

    def children(self, predicate=None, selector=None):
        # type: (Optional[_ObjectPredicate], Optional[_ObjectSelector]) -> list[Union[QObject, Any]]
        if not predicate:
            return self.object.children()
        children = []
        for child in self.object.children():
            if predicate(child):
                children.append(selector(child) if selector else child)
        return children

    def ichildren(self, predicate=None, selector=None):
        # type: (Optional[_ObjectPredicate], Optional[_ObjectSelector]) -> Iterable[Union[QObject, Any]]
        if not predicate:
            for child in self.object.children():
                yield child
            return

        for child in self.object.children():
            if predicate(child):
                yield selector(child) if selector else child

    def ancestor(self, predicate, selector=None):
        # type: (_ObjectPredicate, Optional[_ObjectSelector]) -> Optional[Union[QObject, Any]]
        parents = [self.object.parent()]
        while parents:
            parent = parents.pop(-1)
            if not parent:
                break
            if predicate(parent):
                return selector(parent) if selector else parent
            parents.append(parent.parent())
        return None

    def ancestors(self, predicate=None, selector=None):
        # type: (Optional[_ObjectPredicate], Optional[_ObjectSelector]) -> list[Union[QObject, Any]]
        ancestors = []
        parents = [self.object.parent()]
        while parents:
            parent = parents.pop(-1)
            if not parent:
                break
            if not predicate or predicate(parent):
                ancestors.append(selector(parent) if selector else parent)
            parents.append(parent.parent())
        return ancestors

    def iancestors(self, predicate=None, selector=None):
        # type: (Optional[_ObjectPredicate], Optional[_ObjectSelector]) -> Iterable[Union[QObject, Any]]
        parents = [self.object.parent()]
        while parents:
            parent = parents.pop(-1)
            if not parent:
                break
            if not predicate or predicate(parent):
                yield selector(parent) if selector else parent
            parents.append(parent.parent())

    def descendent(self, predicate, selector=None):
        # type: (_ObjectPredicate, Optional[_ObjectSelector]) -> Optional[Union[QObject, Any]]
        children = self.object.children()
        while children:
            child = children.pop(-1)
            if predicate(child):
                return selector(child) if selector else child
            children.extend(child.children())
        return None

    def descendents(self, predicate=None, selector=None):
        # type: (Optional[_ObjectPredicate], Optional[_ObjectSelector]) -> list[Union[QObject, Any]]
        descendents = []
        children = self.object.children()
        while children:
            child = children.pop(-1)
            if not predicate or predicate(child):
                descendents.append(selector(child) if selector else child)
            children.extend(child.children())
        return descendents

    def idescendents(self, predicate=None, selector=None):
        # type: (Optional[_ObjectPredicate], Optional[_ObjectSelector]) -> Iterable[Union[QObject, Any]]
        children = self.object.children()
        while children:
            child = children.pop(-1)
            if not predicate or predicate(child):
                yield selector(child) if selector else child
            children.extend(child.children())
