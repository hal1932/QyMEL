# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

from ..pyside_module import *
from . import query as _query


class SerializableObjectMixin(object):

    def serialize(self, settings):
        # type: (QSettings) -> NoReturn
        pass

    def deserialize(self, settings):
        # type: (QSettings) -> NoReturn
        pass


class ObjectSerializer(object):
    """
    >>> class SerializableWidget(QWidget, SerializableObjectMixin):
    >>>     def serialize(self, settings):
    >>>         # type: (QSettings) -> NoReturn
    >>>         settings.setValue('geom', self.geometry())
    >>>
    >>>     def deserialize(self, settings):
    >>>         # type: (QSettings) -> NoReturn
    >>>         self.setGeometry(settings.value('geom'))
    >>>
    >>> # SerializableWidget
    >>> #   - QVBoxLayout
    >>> #     - QPushButton
    >>> #     - SerializableWidget
    >>> #     - QHBoxLayout
    >>> #       - SerializableWidget
    >>> root = SerializableWidget()
    >>> root_layout = QVBoxLayout()
    >>> root_layout.addWidget(QPushButton())
    >>> root_layout.addWidget(SerializableWidget())
    >>> child_layout = QHBoxLayout()
    >>> child_layout.addWidget(SerializableWidget())
    >>> root_layout.addLayout(child_layout)
    >>> root.setLayout(root_layout)
    >>>
    >>> serializer = ObjectSerializer()
    >>> settings = QSettings('path_to_file', QSettings.IniFormat)
    >>> serializer.serialize(root, settings)
    >>> settings.sync()
    >>>
    >>> serializer.deserialize(settings, root)
    """

    def serialize(self, source, destination):
        # type: (QObject, QSettings) -> NoReturn
        def _serialize(node, path):
            # type: (QObject, text_type) -> NoReturn
            destination.beginGroup(path)
            node.serialize(destination)
            destination.endGroup()
        self._walk_serializables(source, _serialize)

    def deserialize(self, settings, destination):
        # type: (QSettings, QObject) -> NoReturn
        def _deserialize(node, path):
            # type: (QObject, text_type) -> NoReturn
            settings.beginGroup(path)
            node.deserialize(settings)
            settings.endGroup()
        self._walk_serializables(destination, _deserialize)

    def _walk_serializables(self, node, callback):
        # type: (QObject, Callable[[SerializableObjectMixin, text_type]]) -> NoReturn
        paths = {node: node.__class__.__name__}
        children = {}  # type: dict[QObject, list[QObject]]

        def _is_serializable(node):
            # type: (QObject) -> bool
            return isinstance(node, SerializableObjectMixin)

        def _fetch_path(node):
            # type: (QObject) -> QObject
            parent = node.parent()
            parent_path = paths[parent]
            siblings = children.get(parent, _query.ObjectQuery(parent).descendents(_is_serializable))
            node_path = '{}/{}_{}'.format(parent_path, node.__class__.__name__, siblings.index(node))
            paths[node] = node_path
            return node

        if _is_serializable(node):
            callback(node, paths[node])

        query = _query.ObjectQuery(node)
        for child in query.idescendents(predicate=_is_serializable, selector=_fetch_path):
            callback(child, paths[child])
