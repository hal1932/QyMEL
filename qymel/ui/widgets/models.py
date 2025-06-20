import typing
import collections.abc as abc
from ..pyside_module import *


__all__ = [
    'Binding',
    'ListDefinition',
    'ListModel',
    'TableDefinition',
    'TableColumnDefinition',
    'TableHeaderColumnDefinition',
    'TableModel',
    'TreeDefinition',
    'TreeItem',
    'TreeModel'
]


#
# data binding
#

class Binding(object):

    def __init__(self, path: str) -> None:
        self.path = path

    def value(self, obj: object) -> object:
        return getattr(obj, self.path)

    def set_value(self, obj: object, value: object) -> None:
        setattr(obj, self.path, value)


class BindDefinition(object):

    def __init__(self, bindings: dict[Qt.ItemDataRole, Binding|str]|None = None) -> None:
        self.bindings: dict[Qt.ItemDataRole, Binding] = {}
        if bindings:
            for role, path in bindings.items():
                self.bind(role, path)

    def bind(self, role: Qt.ItemDataRole, binding: Binding|str) -> None:
        if not isinstance(binding, Binding):
            binding = Binding(binding)
        self.bindings[role] = binding


TItem = typing.TypeVar('TItem')
TBindDef = typing.TypeVar('TBindDef', bound=BindDefinition)


class Binder(typing.Generic[TItem, TBindDef]):

    @property
    def is_enabled(self) -> bool:
        return len(self._columns) > 0

    @property
    def count(self) -> int:
        return len(self._columns)

    def __init__(self) -> None:
        self._columns: list[TBindDef] = []

    def column(self, index: int) -> TBindDef:
        return self._columns[index]

    def set_binding(self, index: int, column: BindDefinition) -> None:
        self._columns.insert(index, column)

    def binding(self, index: QModelIndex, role: Qt.ItemDataRole) -> Binding|None:
        if index.isValid() and self._columns and 0 <= index.column() < len(self._columns):
            return self._columns[index.column()].bindings.get(role)
        return None

    def is_bound(self, index: QModelIndex, role: Qt.ItemDataRole) -> bool:
        return self.binding(index, role) is not None


#
# common items model
#

TItemIndex = typing.TypeVar('TItemIndex', int, QModelIndex)


class ItemsModel(QAbstractItemModel, typing.Generic[TItem, TBindDef]):

    def __init__(self, parent: QObject|None = None) -> None:
        super(ItemsModel, self).__init__(parent)
        self._binder = Binder()
        self._items: list[TItem] = []

    def append(self, item: TItem) -> None:
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
        self._items.append(item)
        self.endInsertRows()

    def extend(self, items: abc.Sequence[TItem]) -> None:
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items) + len(items) - 1)
        self._items.extend(items)
        self.endInsertRows()

    def insert(self, index: TItemIndex, items: TItem|abc.Sequence[TItem]) -> None:
        if isinstance(index, QModelIndex):
            index = index.row()
        if not isinstance(items, abc.Sequence):
            items = [items]

        self.beginInsertRows(QModelIndex(), index, index + len(items) - 1)
        for item in items:
            self._items.insert(index, item)
            index += 1
        self.endInsertRows()

    def replace(self, items: abc.Sequence[TItem]) -> None:
        self.beginResetModel()
        self._items = []
        self._items.extend(items)
        self.endResetModel()

    def clear(self) -> None:
        self.beginResetModel()
        self._items = []
        self.endResetModel()

    def item(self, index: TItemIndex) -> TItem:
        if isinstance(index, QModelIndex):
            index = index.row()
        return self._items[index]

    def items(self, indices: abc.Sequence[TItemIndex]|None = None) -> list[TItem]:
        if indices is None:
            return self._items
        return [self.item(index) for index in indices]

    def item_index_of(self, item: TItem) -> TItemIndex:
        return self._items.index(item)

    def flags(self, index: TItemIndex) -> Qt.ItemFlag:
        if isinstance(index, int):
            index = self.index(index, 0)

        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        if self._binder.is_bound(index, Qt.ItemDataRole.EditRole):
            flags |= Qt.ItemFlag.ItemIsEditable
        else:
            flags &= ~Qt.ItemFlag.ItemIsEditable

        return flags

    def index(self, row: int, column: int, parent: QModelIndex|None = None) -> QModelIndex:
        parent = parent or QModelIndex()
        if 0 <= row < self.rowCount(parent):
            return self.createIndex(row, column, self.item(row))
        return QModelIndex()

    def parent(self, index: QModelIndex|None = None) -> QModelIndex:
        return QModelIndex()

    def hasChildren(self, parent: QModelIndex|None = None) -> bool:
        return False

    def rowCount(self, parent: QModelIndex|None = None) -> int:
        return len(self._items)

    def columnCount(self, parent: QModelIndex|None = None) -> int:
        return self._binder.count

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> object:
        binding = self._binder.binding(index, role)
        if binding:
            return binding.value(self._items[index.row()])
        return None

    def setData(self, index: QModelIndex, value: TItem, role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole) -> bool:
        binding = self._binder.binding(index, role)
        if binding:
            binding.set_value(self._items[index.row()], value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def _define_column(self, index: int, definition: TBindDef) -> None:
        self._binder.set_binding(index, definition)


#
# ListModel
#

TListItem = typing.TypeVar('TListItem')


class ListDefinition(BindDefinition):
    pass


class ListModel(ItemsModel[TListItem, ListDefinition]):
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

    def define(self, definition: ListDefinition) -> None:
        self._define_column(0, definition)


#
# TableModel
#

TTableItem = typing.TypeVar('TTableItem')


class TableDefinition(BindDefinition):
    pass


class TableColumnDefinition(TableDefinition):

    def __init__(self,
                 header: dict[Qt.ItemDataRole, object]|None = None,
                 bindings: dict[Qt.ItemDataRole, Binding|str]|None = None
     ) -> None:
        super(TableColumnDefinition, self).__init__(bindings)
        self.header = header


class TableHeaderColumnDefinition(TableDefinition):

    def __init__(self, bindings: dict[Qt.ItemDataRole, Binding|str]|None = None) -> None:
        super(TableHeaderColumnDefinition, self).__init__(bindings)


class TableModel(ItemsModel[TTableItem, TableColumnDefinition]):
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
    >>> header_column = TableHeaderColumnDefinition({Qt.DisplayRole: 'color'})
    >>>
    >>> column_id = TableColumnDefinition(
    >>>     header={
    >>>         Qt.DisplayRole: 'id',
    >>>         Qt.ForegroundRole: QColor(Qt.red)
    >>>     },
    >>>     bindings={
    >>>         Qt.DisplayRole: 'index',
    >>>         Qt.ForegroundRole: 'color'
    >>>     }
    >>> )
    >>> column_name = TableColumnDefinition(
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

    def __init__(self, parent: QObject|None = None) -> None:
        super(TableModel, self).__init__(parent)
        self._header_column: TableHeaderColumnDefinition|None = None

    def define_header_column(self, header_column: TableHeaderColumnDefinition) -> None:
        self._header_column = header_column

    def define_column(self, index: int, column: TableColumnDefinition) -> None:
        self._define_column(index, column)

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole) -> str|None:
        if self._binder.is_enabled:
            if orientation == Qt.Orientation.Horizontal:
                header = self._binder.column(section).header
                return header.get(role)

            if self._header_column and orientation == Qt.Orientation.Vertical:
                binding = self._header_column.bindings.get(role)
                if binding:
                    return binding.value(self._items[section])

        return super(TableModel, self).headerData(section, orientation, role)


#
# TreeView
#

TTreeItem = typing.TypeVar('TTreeItem')


class TreeDefinition(BindDefinition):

    def __init__(self,
                 header: dict[Qt.ItemDataRole, object]|None = None,
                 bindings: dict[Qt.ItemDataRole, Binding|str]|None = None
     ) -> None:
        super(TreeDefinition, self).__init__(bindings)
        self.header = header


class TreeItem(object):
    """
    see `<TreeModel>`
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
    >>>         self.append_child(child)
    >>>         child.append_child(None)  # appending a dummy child to be able to expanding
    """

    @property
    def child_count(self) -> int:
        return len(self.children)

    @property
    def has_children(self) -> bool:
        return self.child_count > 0

    @property
    def parent(self) -> TTreeItem|None:
        return self._parent

    @property
    def children(self) -> list[TTreeItem]:
        return self._children

    def __init__(self) -> None:
        self._parent: TTreeItem|None = None
        self._children: list[TTreeItem] = []
        self._model: TreeModel|None = None

    def child(self, index: int) -> TTreeItem|None:
        if 0 <= index < len(self.children):
            return self._children[index]
        return None

    def child_index_of(self, child: TTreeItem) -> int:
        return self._children.index(child)

    def append_child(self, child: TTreeItem|None) -> None:
        self.insert_children(self.child_count, [child])

    def extend_children(self, children: abc.Sequence[TTreeItem|None]) -> None:
        self.insert_children(self.child_count, children)

    def insert_children(self, index: int, children: abc.Sequence[TTreeItem|None]) -> None:
        if not self._model:
            raise RuntimeError('cannot edit children before the node is inserted to the parent')

        model = self._model

        model.beginInsertRows(model.index_from_item(self), index, index + len(children) - 1)
        for child in children:
            self._children.insert(index, child)
            if child:
                child._parent = self
                child._model = model
            index += 1
        model.endInsertRows()

    def clear_children(self) -> None:
        if not self._model:
            raise RuntimeError('cannot edit children before the node is inserted to the parent')

        model = self._model

        model.beginRemoveRows(model.index_from_item(self), 0, self.child_count)
        self._children = []
        model.endRemoveRows()


class TreeModel(QAbstractItemModel, typing.Generic[TTreeItem]):
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
    def root(self) -> TTreeItem:
        return self._root

    def __init__(self, parent: QObject|None = None) -> None:
        super(TreeModel, self).__init__(parent)
        self._binder = Binder()
        self._root = TreeItem()
        self._root._model = self

    def define_column(self, index: int, definition: TreeDefinition) -> None:
        self._binder.set_binding(index, definition)

    def append(self, item: TTreeItem) -> None:
        self._root.append_child(item)

    def extend(self, items: abc.Sequence[TTreeItem]) -> None:
        self._root.extend_children(items)

    def clear(self) -> None:
        self._root.clear_children()

    def replace(self, items: abc.Sequence[TTreeItem]) -> None:
        self.clear()
        self.extend(items)

    def item_from_index(self, index: QModelIndex) -> TTreeItem|None:
        if not index.isValid():
            return None
        return index.internalPointer()

    def index_from_item(self, item: TTreeItem) -> QModelIndex:
        if item.parent:
            parent = item.parent
        else:
            parent = self._root

        if item == parent:
            return QModelIndex()

        return self.createIndex(parent.children.index(item), 0, item)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = Qt.ItemFlag.ItemIsEnabled
        if self._binder.binding(index, Qt.ItemDataRole.EditRole):
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def rowCount(self, parent: QModelIndex|None = None):
        parent = parent or QModelIndex()
        if not parent.isValid():
            return self._root.child_count
        parent_item = parent.internalPointer()
        if not parent_item:
            return 0
        return parent_item.child_count

    def columnCount(self, parent: QModelIndex|None = None):
        return self._binder.count

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()
        item = index.internalPointer()
        if not item:
            return QModelIndex()
        parent = item.parent
        if parent == self._root:
            return QModelIndex()
        return self.createIndex(parent.parent.child_index_of(parent), 0, parent)

    def index(self, row: int, column: int, parent: QModelIndex|None = None) -> QModelIndex:
        parent = parent or QModelIndex()
        if not parent.isValid():
            parent_item = self._root
        else:
            parent_item = parent.internalPointer()
        child_item = parent_item.child(row)
        return self.createIndex(row, column, child_item)

    def hasChildren(self, parent: QModelIndex|None = None) -> bool:
        parent = parent or QModelIndex()
        item = self.item_from_index(parent) if parent.isValid() else self._root
        if item:
            return item.has_children
        return False

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> object:
        if not index.isValid():
            return None

        binding = self._binder.binding(index, role)
        if not binding:
            return None

        item = index.internalPointer()
        if not item:
            return None

        return binding.value(item)

    def setData(self, index: QModelIndex, value: TItem, role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole) -> bool:
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
