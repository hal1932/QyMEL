# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

from ..pyside_module import *


TTableItem = TypeVar('TTableItem')


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


class TableDefinition(object):

    def __init__(self, bindings=None):
        # type: (Optional[dict[Qt.ItemDataRole, str]]) -> NoReturn
        self.bindings = {}  # type: dict[Qt.ItemDataRole, Binding]
        if bindings:
            for role, path in bindings.items():
                self.bind(role, path)

    def bind(self, role, binding):
        # type: (Qt.ItemDataRole, Union[Binding, str]) -> NoReturn
        if not isinstance(binding, Binding):
            binding = Binding(binding)
        self.bindings[role] = binding


class TableColumn(TableDefinition):

    def __init__(self, header=None, bindings=None):
        # type: (Optional[str], Optional[dict[Qt.ItemDataRole, str]]) -> NoReturn
        super(TableColumn, self).__init__(bindings)
        self.header = header


class TableHeaderColumn(TableDefinition):

    def __init__(self, bindings=None):
        # type: (Optional[dict[Qt.ItemDataRole, str]]) -> NoReturn
        super(TableHeaderColumn, self).__init__(bindings)


class TableModel(QStandardItemModel, Generic[TTableItem]):
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
    >>> column_id = TableColumn('id', bindings={
    >>>     Qt.DisplayRole: 'index',
    >>>     Qt.ForegroundRole: 'color'
    >>> })
    >>>
    >>> column_name = TableColumn('name', bindings={
    >>>     Qt.DisplayRole: 'name',
    >>>     Qt.EditRole: 'name'
    >>> })
    >>>
    >>> model.define_header_column(header_column)
    >>> model.define_column(0, column_id)
    >>> model.define_column(1, column_name)
    >>>
    >>> view.show()
    """

    def __init__(self, parent=None):
        super(TableModel, self).__init__(parent)
        self._columns = []  # type: list[TableColumn]
        self._header_column = None  # type: Optional[TableHeaderColumn]
        self._items = []  # type: list[TTableItem]

    def define_column(self, index, column):
        # type: (int, TableColumn) -> NoReturn
        self._columns.insert(index, column)

    def define_header_column(self, header_column):
        # type: (TableHeaderColumn) -> NoReturn
        self._header_column = header_column

    def append(self, item):
        # type: (TTableItem) -> NoReturn
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items))
        self._items.append(item)
        self.endInsertRows()

    def extend(self, items):
        # type: (Sequence[TTableItem]) -> NoReturn
        self.beginInsertRows(QModelIndex(), len(self._items), len(self._items) + len(items))
        self._items.extend(items)
        self.endInsertRows()

    def replace(self, items):
        # type: (Sequence[TTableItem]) -> NoReturn
        self.beginResetModel()
        self._items = items
        self.endResetModel()

    def clear(self):
        self.replace([])

    def index(self, row, column, parent=QModelIndex()):
        # type: (int, int, QModelIndex) -> QModelIndex
        if self._columns:
            return self.createIndex(row, column, 0) if self.hasIndex(row, column, parent) else QModelIndex()
        return super(TableModel, self).index(row, column, parent)

    def rowCount(self, parent=QModelIndex()):
        # type: (QModelIndex) -> int
        if self._items:
            return len(self._items)
        return super(TableModel, self).rowCount()

    def columnCount(self, parent=QModelIndex()):
        # type: (QModelIndex) -> int
        if self._columns:
            return len(self._columns)
        return super(TableModel, self).columnCount()

    def headerData(self, section, orientation, role):
        # type: (int, Qt.Orientation, Qt.ItemDataRole) -> Optional[str]
        if self._columns and orientation == Qt.Horizontal:
            if role == Qt.DisplayRole and section < len(self._columns):
                column = self._columns[section]
                if column:
                    return column.header

        if self._header_column and orientation == Qt.Vertical:
            binding = self._header_column.bindings.get(role)
            if binding:
                return binding.value(self._items[section])

        return super(TableModel, self).headerData(section, orientation, role)

    def data(self, index, role=Qt.DisplayRole):
        # type: (QModelIndex, Qt.ItemDataRole) -> Any
        if not self._is_index_valid(index):
            return None

        if self._columns and self._items:
            column = self._columns[index.column()]
            if column:
                binding = column.bindings.get(role)
                if binding:
                    return binding.value(self._items[index.row()])

        return super(TableModel, self).data(index, role)

    def setData(self, index, value, role=Qt.EditRole):
        # type: (QModelIndex, TTableItem, Qt.ItemDataRole) -> bool
        print(role)
        if not self._is_index_valid(index):
            return False

        if self._columns and self._items:
            column = self._columns[index.column()]
            if column:
                binding = column.bindings.get(role)
                if binding:
                    binding.set_value(self._items[index.row()], value)
                    return True

        return super(TableModel, self).setData(index, value, role)

    def _is_index_valid(self, index):
        # type: (QModelIndex) -> bool
        if not index.isValid():
            return False
        if self._items:
            return 0 <= index.row() < len(self._items)
        return True
