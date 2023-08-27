# coding: utf-8
from typing import *

from qymel.ui.pyside_module import *
from qymel.ui import layouts as _layouts
from qymel.ui.widgets import models as _models

from .. import groups as _groups
from .. import items as _items
from . import icons as _icons


class ItemListItem(_models.TreeItem):

    def __init__(self, group: _groups.CheckItemGroup, category: Optional[str], items: List[_items.CheckItem]):
        super().__init__()
        self.group = group
        if category is None:
            self.label = items[0].label
            self.is_category = False
        else:
            self.label = category
            self.is_category = True
        self.items = items
        self.icon: QPixmap = None
        self.load_results()

    def load_results(self):
        results: List[_items.CheckResult] = []
        for item in self.items:
            if not self.group.is_executed(item):
                results.clear()
                break
            results.extend(self.group.results(item))

        if len(results) == 0:
            icon = _icons.invalid()
            self.icon = icon.pixmap(icon.actualSize(QSize(12, 12)))
        else:
            if all(r.is_success for r in results):
                icon = _icons.success()
            elif any(r.is_error for r in results):
                errors = filter(lambda r: r.is_error, results)
                is_modifiable = any(e.is_modifiable for e in errors)
                icon = _icons.error(is_modifiable)
            else:
                warnings = filter(lambda r: r.is_warning, results)
                is_modifiable = any(w.is_modifiable for w in warnings)
                icon = _icons.warning(is_modifiable)
            self.icon = icon.pixmap(icon.actualSize(QSize(12, 12)))

    def expand(self):
        self.clear_children()
        if self.is_category:
            for item in self.items:
                self.append_child(ItemListItem(self.group, None, [item]))


class ItemListWidget(QWidget):

    selection_changed = Signal(_items.CheckItem)
    execute_requested = Signal(list)

    def __init__(self):
        super().__init__()
        self.__model = _models.TreeModel()
        self.__model.define_column(0, _models.TreeDefinition(
            bindings={
                Qt.DisplayRole: 'label',
                Qt.DecorationRole: 'icon',
            }
        ))

        self.__view = QTreeView()
        self.__view.setModel(self.__model)
        self.__view.setHeaderHidden(True)
        self.__view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.__view.expanded.connect(lambda index: self.__model.item_from_index(index).expand())
        self.__view.clicked.connect(lambda index: self.selection_changed.emit(self.__model.item_from_index(index)))
        self.__view.expandAll()

        self.__view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__view.customContextMenuRequested.connect(self.__show_context_menu)

        self.setLayout(_layouts.vbox(
            self.__view,
            contents_margins=0
        ))

    def refresh(self):
        self.load_results()
        self.__model.dataChanged.emit(QModelIndex(), QModelIndex())

    def load_from(self, group: _groups.CheckItemGroup):
        self.__model.clear()

        for category in group.categories():
            items = group.items(category)
            if not category:
                for item in items:
                    self.__model.append(ItemListItem(group, None, [item]))
            else:
                self.__model.append(ItemListItem(group, category, items))

        self.__view.expandAll()

    def load_results(self):
        nodes = self.__model.root.children[:]
        while len(nodes) > 0:
            node = nodes.pop(-1)
            node.load_results()
            for child in node.children:
                nodes.append(child)
        self.__model.layoutChanged.emit()

        self.__view.clearFocus()
        self.__view.clearSelection()

    def __show_context_menu(self, pos: QPoint):
        index = self.__view.indexAt(pos)
        if not index.isValid():
            return

        item: ItemListItem = self.__model.item_from_index(index)

        menu = QMenu()
        exec_act = QAction('実行')
        exec_act.triggered.connect(lambda: self.execute_requested.emit(item.items))
        menu.addAction(exec_act)
        menu.exec_(self.__view.mapToGlobal(pos))
