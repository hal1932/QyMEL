# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

from ..pyside_module import *


class Binding(object):

    def __init__(self, path):
        # type: (str) -> NoReturn
        self.path = path

    def value(self, obj):
        # type: (Any) -> Any
        return getattr(obj, self.path)

    def set_value(self, obj, value):
        # type: (Any, Any) -> NoReturn
        setattr(obj, self.path, value)


class _BindDefinition(object):

    def __init__(self, bindings=None):
        # type: (Optional[dict[Qt.ItemDataRole, Union[Binding, str]]]) -> NoReturn
        self.bindings = {}  # type: dict[Qt.ItemDataRole, Binding]
        if bindings:
            for role, path in bindings.items():
                self.bind(role, path)

    def bind(self, role, binding):
        # type: (Qt.ItemDataRole, Union[Binding, str]) -> NoReturn
        if not isinstance(binding, Binding):
            binding = Binding(binding)
        self.bindings[role] = binding


_TItem = TypeVar('_TItem', bound=QStandardItemModel)
_TBindDef = TypeVar('_TBindDef', bound=_BindDefinition)


class _Binder(Generic[_TItem, _TBindDef]):

    @property
    def is_enabled(self):
        # type: () -> bool
        return len(self._columns) > 0

    @property
    def count(self):
        # type: () -> int
        return len(self._columns)

    def __init__(self):
        self._columns = []  # type: list[_TBindDef]

    def column(self, index):
        # type: (int) -> _TBindDef
        return self._columns[index]

    def set_binding(self, index, column):
        # type: (int, _BindDefinition) -> NoReturn
        self._columns.insert(index, column)

    def binding(self, index, role):
        # type: (QModelIndex, Qt.ItemDataRole) -> Optional[Binding]
        if self._columns and 0 <= index.column() < len(self._columns):
            return self._columns[index.column()].bindings.get(role)
        return None


class _ItemsModel(QStandardItemModel, Generic[_TItem, _TBindDef]):

    def __init__(self, parent=None):
        # type: (QObject) -> NoReturn
        super(_ItemsModel, self).__init__(parent)
        self._binder = _Binder()
        self._items = []  # type: list[_TItem]

    def append(self, item):
        # type: (_TItem) -> NoReturn
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
        self._items.append(item)
        self.endInsertRows()

    def extend(self, items):
        # type: (Sequence[_TItem]) -> NoReturn
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items) + len(items))
        self._items.extend(items)
        self.endInsertRows()

    def replace(self, items):
        # type: (Sequence[_TItem]) -> NoReturn
        self._items = []
        self.extend(items)

    def clear(self):
        self.replace([])

    def item(self, index):
        # type: (Union[QModelIndex, int]) -> _TItem
        if self._binder.is_enabled:
            if isinstance(index, QModelIndex):
                index = index.row()
            return self._items[index]

        if isinstance(index, int):
            index = self.index(index, 0, QModelIndex())
        return super(_ItemsModel, self).itemFromIndex(index)

    def flags(self, index):
        # type: (QModelIndex) -> Qt.ItemFlags
        flags = super(_ItemsModel, self).flags(index)
        if self._binder.is_enabled:
            if self._binder.binding(index, Qt.EditRole):
                flags |= Qt.ItemIsEditable
            else:
                flags &= not Qt.ItemIsEditable
        return flags

    def index(self, row, column, parent=QModelIndex()):
        # type: (int, int, QModelIndex) -> QModelIndex
        if self._binder.is_enabled:
            return self.createIndex(row, column, 0) if self.hasIndex(row, column, parent) else QModelIndex()
        return super(_ItemsModel, self).index(row, column, parent)

    def rowCount(self, parent=QModelIndex()):
        # type: (QModelIndex) -> int
        if self._binder.is_enabled:
            return len(self._items)
        return super(_ItemsModel, self).rowCount()

    def columnCount(self, parent=QModelIndex()):
        # type: (QModelIndex) -> int
        if self._binder.is_enabled:
            return self._binder.count
        return super(_ItemsModel, self).columnCount(parent)

    def data(self, index, role=Qt.DisplayRole):
        # type: (QModelIndex, Qt.ItemDataRole) -> Any
        if not index.isValid():
            return None

        if self._binder.is_enabled:
            binding = self._binder.binding(index, role)
            if binding:
                return binding.value(self._items[index.row()])

        return super(_ItemsModel, self).data(index, role)

    def setData(self, index, value, role=Qt.EditRole):
        # type: (QModelIndex, _TItem, Qt.ItemDataRole) -> bool
        if not index.isValid():
            return False

        if self._binder.is_enabled:
            binding = self._binder.binding(index, role)
            if binding:
                binding.set_value(self._items[index.row()], value)
                return True

        return super(_ItemsModel, self).setData(index, value, role)

    def _define_column(self, index, definition):
        # type: (int, _TBindDef) -> NoReturn
        self._binder.set_binding(index, definition)


#
# ListModel
#

TListItem = TypeVar('TListItem', bound=QStandardItem)


class ListDefinition(_BindDefinition):
    pass


class ListModel(_ItemsModel[TListItem, ListDefinition]):
    """
    >>>class ListItem(object):
    >>> def __init__(self, index, name, color):
    >>>     self.index = index
    >>>     self.name = name
    >>>     self.color = color
    >>>
    >>> view = QListView()
    >>> model = ListModel()
    >>> view.setModel(model)
    >>>
    >>> model.append(ListItem(0, 'aaa', QColor(Qt.red)))
    >>> model.append(ListItem(1, 'bbb', QColor(Qt.green)))
    >>> model.append(ListItem(2, 'ccc', QColor(Qt.blue)))
    >>>
    >>> column = ListDefinition(bindings={
    >>>     Qt.DisplayRole: 'name',
    >>>     Qt.ForegroundRole: 'color',
    >>>     Qt.EditRole: 'name'
    >>> })
    >>> model.define(column)
    >>>
    >>> view.show()
    """

    def define(self, definition):
        # type: (ListDefinition) -> NoReturn
        self._define_column(0, definition)


#
# TableModel
#

TTableItem = TypeVar('TTableItem', bound=_TItem)


class TableDefinition(_BindDefinition):
    pass


class TableColumn(TableDefinition):

    def __init__(self, header=None, bindings=None):
        # type: (Optional[dict[Qt.ItemDataRole, Any]], Optional[dict[Qt.ItemDataRole, Union[Binding, str]]]) -> NoReturn
        super(TableColumn, self).__init__(bindings)
        self.header = header


class TableHeaderColumn(TableDefinition):

    def __init__(self, bindings=None):
        # type: (Optional[dict[Qt.ItemDataRole, Union[Binding, str]]]) -> NoReturn
        super(TableHeaderColumn, self).__init__(bindings)


class TableModel(_ItemsModel[TTableItem, TableColumn]):
    """
    >>> class TableItem(object):
    >>>     def __init__(self, index, name, color):
    >>>         self.index = index
    >>>         self.name = name
    >>>         self.color = color
    >>>
    >>> view = QTableView()
    >>> model = TableModel()
    >>> view.setModel(model)
    >>>
    >>> model.append(TableItem(0, 'aaa', QColor(Qt.red)))
    >>> model.append(TableItem(1, 'bbb', QColor(Qt.green)))
    >>> model.append(TableItem(2, 'ccc', QColor(Qt.blue)))
    >>>
    >>> header_column = TableHeaderColumn({Qt.DisplayRole: 'color'})
    >>>
    >>> column_id = TableColumn(
    >>>     header={
    >>>         Qt.DisplayRole: 'id',
    >>>         Qt.ForegroundRole: QColor(Qt.red)
    >>>     },
    >>>     bindings={
    >>>         Qt.DisplayRole: 'index',
    >>>         Qt.ForegroundRole: 'color'
    >>>     }
    >>> )
    >>> column_name = TableColumn(
    >>>     header={
    >>>         Qt.DisplayRole: 'name'
    >>>     },
    >>>     bindings={
    >>>         Qt.DisplayRole: 'name',
    >>>         Qt.EditRole: 'name'
    >>>     }
    >>> )
    >>>
    >>> model.define_header_column(header_column)
    >>> model.define_column(0, column_id)
    >>> model.define_column(1, column_name)
    >>>
    >>> view.show()
    """

    def __init__(self, parent=None):
        super(TableModel, self).__init__(parent)
        self._header_column = None  # type: Optional[TableHeaderColumn]

    def define_header_column(self, header_column):
        # type: (TableHeaderColumn) -> NoReturn
        self._header_column = header_column

    def define_column(self, index, column):
        # type: (int, TableColumn) -> NoReturn
        self._define_column(index, column)

    def headerData(self, section, orientation, role):
        # type: (int, Qt.Orientation, Qt.ItemDataRole) -> Optional[str]
        if self._binder.is_enabled:
            if orientation == Qt.Horizontal:
                header = self._binder.column(section).header
                return header.get(role)

            if self._header_column and orientation == Qt.Vertical:
                binding = self._header_column.bindings.get(role)
                if binding:
                    return binding.value(self._items[section])

        return super(TableModel, self).headerData(section, orientation, role)


#
# TreeView
#

TTreeItem = TypeVar('TTreeItem', bound=_TItem)


class TreeDefinition(_BindDefinition):

    def __init__(self, header=None, bindings=None):
        # type: (Optional[dict[Qt.ItemDataRole, Any]], Optional[dict[Qt.ItemDataRole, Union[Binding, str]]]) -> NoReturn
        super(TreeDefinition, self).__init__(bindings)
        self.header = header


class TreeItem(object):
    """
    see `<TestClass>`
    >>> class MyTreeItem(TreeItem):
    >>>     def __init__(self, index, name, color):
    >>>         super(MyTreeItem, self).__init__()
    >>>         self.index = index
    >>>         self.name = name
    >>>         self.color = color
    >>>
    >>>     def expand(self):
    >>>         self.clear_children()
    >>>         child = MyTreeItem(...)
    >>>         child.set_expandable(True)
    >>>         self.append_child(child)
    """

    @property
    def child_count(self):
        return len(self.children)

    @property
    def parent(self):
        # type: () -> Optional[TTreeItem]
        return self._parent

    @property
    def children(self):
        # type: () -> Sequence[TTreeItem]
        return self._children

    def __init__(self, parent=None):
        # type: (Optional[TreeItem]) -> NoReturn
        self._parent = parent
        self._children = []  # type: list[TreeItem]
        self._model = None  # type: QAbstractItemModel

    def set_expandable(self, value):
        if value:
            self._children.append(None)
        else:
            self._children = []

    def child(self, index):
        # type: (int) -> Optional[TTreeItem]
        if 0 <= index < len(self.children):
            return self._children[index]
        return None

    def child_index_of(self, child):
        # type: (TTreeItem) -> int
        return self._children.index(child)

    def append_child(self, child):
        # type: (TTreeItem) -> NoReturn
        model = self._model

        model.beginInsertRows(model.index_from_item(self), self.child_count, self.child_count)
        self._children.append(child)
        model.endInsertRows()

        if child:
            child._parent = self
            child._model = model

    def extend_children(self, children):
        # type: (Sequence[TreeItem]) -> NoReturn
        model = self._model

        model.beginInsertRows(model.index_from_item(self), self.child_count, self.child_count + len(children) - 1)
        self._children.extend(children)
        model.endInsertRows()

        for child in children:
            if child:
                child._parent = self
                child._model = model

    def clear_children(self):
        # type: () -> NoReturn
        model = self._model

        model.beginRemoveRows(model.index_from_item(self), 0, self.child_count)
        self._children = []
        model.endRemoveRows()


TTreeItem = TypeVar('TTreeItem', bound=TreeItem)


class TreeModel(QAbstractItemModel, Generic[TTreeItem]):
    """
    see `<TreeItem>`
    >>> tree_view = QTreeView()
    >>> tree_model = TreeModel()
    >>> tree_view.setModel(tree_model)
    >>> tree_view.expanded.connect(lambda index: tree_model.item_from_index(index).expand())
    >>>
    >>> tree_model.append(MyTreeItem(0, 'aaa', QColor(Qt.red)))
    >>> tree_model.append(MyTreeItem(1, 'bbb', QColor(Qt.green)))
    >>> tree_model.append(MyTreeItem(2, 'ccc', QColor(Qt.blue)))
    >>>
    >>> tree_model.define_column(0, TreeDefinition(
    >>>     header={
    >>>         Qt.DisplayRole: 'name',
    >>>         Qt.ForegroundRole: QColor(Qt.gray),
    >>>     },
    >>>     bindings={
    >>>         Qt.DisplayRole: 'name',
    >>>         Qt.EditRole: 'name',
    >>>         Qt.ForegroundRole: 'color'
    >>>     }
    >>> ))
    >>> tree_model.define_column(1, TreeDefinition(
    >>>     header={
    >>>         Qt.DisplayRole: 'color',
    >>>     },
    >>>     bindings={
    >>>         Qt.DisplayRole: 'color',
    >>>         Qt.ForegroundRole: 'color'
    >>>     }
    >>> ))
    >>>
    >>> tree_view.expandAll()
    >>>
    >>> tree_view.show()
    """

    @property
    def root(self):
        # type: () -> TTreeItem
        return self._root

    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)
        self._binder = _Binder()
        self._root = TreeItem()
        self._root._model = self

    def define_column(self, index, definition):
        # type: (int, TreeDefinition) -> NoReturn
        self._binder.set_binding(index, definition)

    def append(self, item):
        # type: (TTreeItem) -> NoReturn
        self._root.append_child(item)

    def extend(self, items):
        # type: (Sequence[TTreeItem]) -> NoReturn
        self._root.extend_children(items)

    def clear(self):
        self._root.clear_children()

    def item_from_index(self, index):
        # type: (QModelIndex) -> Optional[TTreeItem]
        if not index.isValid():
            return None
        return index.internalPointer()

    def index_from_item(self, item):
        # type: (TTreeItem) -> QModelIndex
        if item.parent:
            parent = item.parent
        else:
            parent = self._root

        if item == parent:
            return QModelIndex()

        return self.createIndex(parent.children.index(item), 0, item)

    def flags(self, index):
        # type: (QModelIndex) -> Qt.ItemFlags
        flags = Qt.ItemIsEnabled
        if self._binder.binding(index, Qt.EditRole):
            flags |= Qt.ItemIsEditable
        else:
            flags &= not Qt.ItemIsEditable
        return flags

    def rowCount(self, parent=QModelIndex()):
        # type: (QModelIndex) -> int
        if not parent.isValid():
            return self._root.child_count
        parent_item = parent.internalPointer()
        if not parent_item:
            return 0
        return parent_item.child_count

    def columnCount(self, parent=QModelIndex()):
        # type: (QModelIndex) -> int
        return self._binder.count

    def parent(self, index):
        # type: (QModelIndex) -> QModelIndex
        if not index.isValid():
            return QModelIndex()
        item = index.internalPointer()
        if not item:
            return QModelIndex()
        parent = item.parent
        if parent == self._root:
            return QModelIndex()
        return self.createIndex(parent.parent.child_index_of(parent), 0, parent)

    def index(self, row, column, parent=QModelIndex()):
        # type: (QModelIndex) -> QModelIndex
        if not parent.isValid():
            parent_item = self._root
        else:
            parent_item = parent.internalPointer()
        child_item = parent_item.child(row)
        return self.createIndex(row, column, child_item)

    def data(self, index, role=Qt.DisplayRole):
        # type: (QModelIndex, Qt.ItemDataRole) -> Any
        if not index.isValid():
            return None

        binding = self._binder.binding(index, role)
        if not binding:
            return None

        item = index.internalPointer()
        if not item:
            return None

        return binding.value(item)

    def setData(self, index, value, role=Qt.EditRole):
        # type: (QModelIndex, _TItem, Qt.ItemDataRole) -> bool
        if not index.isValid():
            return False

        binding = self._binder.binding(index, role)
        if not binding:
            return False

        item = index.internalPointer()
        if not item:
            return False

        binding.set_value(item, value)
        return True
