import collections.abc as abc
from ..pyside_module import *


_ObjectPredicate = abc.Callable[[QObject], bool] | None
_ObjectSelector = abc.Callable[[QObject], object]  | None
_QueryResult = QObject | object | None


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
    >>> print(query.descendant(lambda obj: isinstance(obj, QPushButton)))
    >>> print(query.descendents(lambda obj: isinstance(obj, QLayout)))
    >>>
    >>> query1 = ObjectQuery(child_layout)
    >>> print(query1.parent(lambda obj: isinstance(obj, QVBoxLayout)))
    >>> print(query1.ancestor(lambda obj: isinstance(obj, QWidget)))
    >>> print(query1.ancestors(selector=lambda obj: obj.objectName()))
    """

    @property
    def object(self) -> QObject:
        return self.__object

    def __init__(self, obj: QObject) -> None:
        self.__object = obj

    def parent(self, predicate: _ObjectPredicate = None, selector: _ObjectSelector = None) -> _QueryResult:
        parent = self.object.parent()
        if not predicate or (parent and predicate(parent)):
            return selector(parent) if selector else parent
        return None

    def child(self, predicate: _ObjectPredicate = None, selector: _ObjectSelector = None) -> _QueryResult:
        if not predicate:
            return self.object.findChild(QObject)
        for child in self.object.children():
            if not predicate or predicate(child):
                return selector(child) if selector else child
        return None

    def children(self, predicate: _ObjectPredicate = None, selector: _ObjectSelector = None) -> _QueryResult:
        if not predicate:
            return self.object.children()
        children = []
        for child in self.object.children():
            if not predicate or predicate(child):
                children.append(selector(child) if selector else child)
        return children

    def ichildren(self, predicate: _ObjectPredicate = None, selector: _ObjectSelector = None) -> abc.Iterable[_QueryResult]:
        if not predicate:
            for child in self.object.children():
                yield child
            return

        for child in self.object.children():
            if not predicate or predicate(child):
                yield selector(child) if selector else child

    def ancestor(self, predicate: _ObjectPredicate = None, selector: _ObjectSelector = None) -> _QueryResult:
        parents = [self.object.parent()]
        while parents:
            parent = parents.pop(-1)
            if not parent:
                break
            if not predicate or predicate(parent):
                return selector(parent) if selector else parent
            parents.append(parent.parent())
        return None

    def ancestors(self, predicate: _ObjectPredicate = None, selector: _ObjectSelector = None) -> list[_QueryResult]:
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

    def iancestors(self, predicate: _ObjectPredicate = None, selector: _ObjectSelector = None) -> abc.Iterable[_QueryResult]:
        parents = [self.object.parent()]
        while parents:
            parent = parents.pop(-1)
            if not parent:
                break
            if not predicate or predicate(parent):
                yield selector(parent) if selector else parent
            parents.append(parent.parent())

    def descendant(self, predicate: _ObjectPredicate = None, selector: _ObjectSelector = None) -> _QueryResult:
        children = self.object.children()
        while children:
            child = children.pop(-1)
            if not predicate or predicate(child):
                return selector(child) if selector else child
            children.extend(child.children())
        return None

    def descendents(self, predicate: _ObjectPredicate = None, selector: _ObjectSelector = None) -> list[_QueryResult]:
        descendents = []
        children = self.object.children()
        while children:
            child = children.pop(-1)
            if not predicate or predicate(child):
                descendents.append(selector(child) if selector else child)
            children.extend(child.children())
        return descendents

    def idescendents(self, predicate: _ObjectPredicate = None, selector: _ObjectSelector = None) -> abc.Iterable[_QueryResult]:
        children = self.object.children()
        while children:
            child = children.pop(-1)
            if not predicate or predicate(child):
                yield selector(child) if selector else child
            children.extend(child.children())
