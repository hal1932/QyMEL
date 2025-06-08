import collections.abc as abc

from ..pyside_module import *
from . import query as _query


class SerializableObjectMixin(object):

    def serialize(self, settings: QSettings) -> None:
        pass

    def deserialize(self, settings: QSettings) -> None:
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

    def serialize(self, source: QObject, destination: QSettings) -> None:
        def _serialize(node: QObject, path: str):
            destination.beginGroup(path)
            node.serialize(destination)
            destination.endGroup()
        self._walk_serializables(source, _serialize)

    def deserialize(self, settings: QSettings, destination: QObject) -> None:
        def _deserialize(node: QObject, path: str):
            settings.beginGroup(path)
            node.deserialize(settings)
            settings.endGroup()
        self._walk_serializables(destination, _deserialize)

    def _walk_serializables(self, root: QObject, callback: abc.Callable[[QObject, str], None]) -> None:
        paths = {root: root.__class__.__name__}
        children = {}  # type: dict[QObject, list[QObject]]

        def _is_serializable(node: QObject) -> bool:
            return isinstance(node, SerializableObjectMixin)

        def _fetch_path(node: QObject) -> QObject:
            parent = node.parent()
            parent_path = paths[parent]
            siblings = children.get(parent, _query.ObjectQuery(parent).descendents(_is_serializable))
            node_path = '{}/{}_{}'.format(parent_path, node.__class__.__name__, siblings.index(node))
            paths[node] = node_path
            return node

        if _is_serializable(root):
            callback(root, paths[root])

        query = _query.ObjectQuery(root)
        for child in query.idescendents(predicate=_is_serializable, selector=_fetch_path):
            callback(child, paths[child])
