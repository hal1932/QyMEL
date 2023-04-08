# coding: utf-8
from typing import *

import functools
import itertools

import maya.cmds as _cmds

from qymel.ui.pyside_module import *
from qymel.ui import app as _app
from qymel.ui import layouts as _layouts
from qymel.ui import scopes as _ui_scopes
from qymel.ui.widgets import models as _models
from qymel.ui.objects import serializer as _serializer
from qymel.maya import scopes as _maya_scopes

from .. import checker as _checker
from .. import groups as _groups
from .. import items as _items
from . import icons as _icons


class CheckerWindow(_app.MainWindowBase, _serializer.SerializableObjectMixin):

    @property
    def checker(self) -> _checker.Checker:
        return self._checker

    @property
    def close_on_success(self) -> bool:
        return self.__close_on_success

    @close_on_success.setter
    def close_on_success(self, value: bool):
        self.__close_on_success = value

    def __init__(self, checker: _checker.Checker, parent: QObject = None):
        super().__init__(parent=parent)
        self._checker = checker
        self._groups = _GroupSelectorWidget()
        self._items = _ItemListWidget()
        self._description = _DescriptionWidget()
        self._controls = _ControlWidget()
        self._main_splitter = QSplitter()

        self._groups.selection_changed.connect(self.__reload_group)
        self._items.selection_changed.connect(self.__reload_description)
        self._controls.execute_all_requested.connect(self.execute_all)
        self._controls.modify_all_requested.connect(self.__modify_all)

        self.__close_on_success = False

    def _setup_ui(self, central_widget: QWidget):
        self.setWindowTitle('QyMEL Maya Scene Checker')

        self._main_splitter.addWidget(self._items)
        self._main_splitter.addWidget(self._description)
        for i in range(self._main_splitter.count()):
            self._main_splitter.setStretchFactor(i, 1)
            self._main_splitter.setCollapsible(i, False)

        central_widget.setLayout(_layouts.vbox(
            self._groups,
            self._main_splitter,
            self._controls,
            _layouts.stretch(),
        ))
        self.reload()

    def _shutdown_ui(self):
        pass

    def serialize(self, settings: QSettings):
        settings.setValue('geom', self.geometry())
        settings.setValue('split', self._main_splitter.sizes())

    def deserialize(self, settings: QSettings):
        screen = self.parent().windowHandle().screen()
        self.setGeometry(settings.value('geom') or QRect(screen.geometry().center(), QSize(0, 0)))
        self._main_splitter.setSizes([int(x) for x in (settings.value('split') or [])] or [])

    def reload(self):
        self._groups.load_from(self.checker)
        group = self._groups.selected_group
        if group is not None:
            self._controls.load_from(group.results())

    def __reload_group(self, group: Optional[_groups.CheckItemGroup]):
        self._items.load_from(group)
        self._description.load_from(None, None)

    def __reload_description(self, selection: Optional['_ItemListItem']):
        if not selection:
            self._description.load_from(None, None)
            return

        group = selection.group
        if selection.is_category:
            item = None
            category = selection.label
        else:
            item = selection.items[0]
            category = item.category
        self._description.load_from(category, item, group.results(item) if item else [])

    def select_group(self, group_name: str):
        self._groups.select(group_name)
        return self._groups.selected_group

    @_ui_scopes.wait_cursor_scope
    def execute_all(self):
        group = self._groups.selected_group
        group.execute_all()
        self._items.load_results()
        self._controls.load_from(group.results())
        self.__reload_description(None)

        if self.close_on_success and not group.has_errors():
            self.close()

    @_ui_scopes.wait_cursor_scope
    @_maya_scopes.undo_scope
    def __modify_all(self):
        group = self._groups.selected_group
        group.modify_all()
        self.execute_all()


class _ControlWidget(QWidget):

    execute_all_requested = Signal()
    modify_all_requested = Signal()

    def __init__(self):
        super().__init__()
        execute_button = QPushButton('すべて実行')
        execute_button.setIcon(_icons.execute())
        execute_button.clicked.connect(self.execute_all_requested.emit)

        self.__modify_button = QPushButton('すべて自動修正')
        self.__modify_button.setIcon(_icons.modify())
        self.__modify_button.clicked.connect(self.modify_all_requested.emit)

        self.setLayout(_layouts.hbox(
            execute_button,
            self.__modify_button,
            contents_margins=0
        ))

    def load_from(self, results: Sequence[_items.CheckResult]):
        self.__modify_button.setEnabled(False)
        for result in results:
            if result.is_modifiable:
                self.__modify_button.setEnabled(True)


class _GroupSelectorWidget(QWidget):

    selection_changed = Signal(_groups.CheckItemGroup)

    @property
    def selected_group(self) -> Optional[_groups.CheckItemGroup]:
        index = self.__combo.currentIndex()
        return self.__groups[index] if index >= 0 else None

    def __init__(self):
        super().__init__()
        self.__combo = QComboBox()
        self.__combo.setCurrentIndex(0)
        self.__groups: List[_groups.CheckItemGroup] = []
        self.setLayout(_layouts.hbox(
            self.__combo,
            contents_margins=0
        ))

        self.__combo.currentIndexChanged.connect(
            lambda _: self.selection_changed.emit(self.selected_group))

    def select(self, name: str):
        self.__combo.setCurrentText(name)

    def load_from(self, checker: _checker.Checker):
        selection = self.__combo.currentIndex()

        self.__groups = checker.groups
        self.__combo.clear()
        self.__combo.addItems(group.label for group in self.__groups)
        if selection >= 0:

            self.__combo.setCurrentIndex(selection)


class _ItemListItem(_models.TreeItem):

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
        results = self.group.results(self.items[0])
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
                self.append_child(_ItemListItem(self.group, None, [item]))


class _ItemListWidget(QWidget):

    selection_changed = Signal(_items.CheckItem)

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

        self.setLayout(_layouts.vbox(
            self.__view,
            contents_margins=0
        ))

    def load_from(self, group: _groups.CheckItemGroup):
        self.__model.clear()

        for category in group.categories():
            items = group.items(category)
            if not category:
                for item in items:
                    self.__model.append(_ItemListItem(group, None, [item]))
            else:
                self.__model.append(_ItemListItem(group, category, items))

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


class _ResultItem(object):

    def __init__(self, label: str, nodes: List[str]):
        self.label = label
        self.nodes = nodes


class _ResultItemWidget(QWidget):

    selection_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.__model = _models.ListModel()
        self.__model.define(_models.ListDefinition(bindings={
            Qt.DisplayRole: 'label'
        }))

        self.__view = QListView()
        self.__view.setModel(self.__model)
        self.__view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__view.selectionModel().selectionChanged.connect(self.__select_nodes)
        self.__view.selectionModel().selectionChanged.connect(lambda _1, _2: self.selection_changed.emit(self.selected_items()))
        self.__view.setEnabled(True)

        self.setLayout(_layouts.vbox(
            self.__view,
            contents_margins=0
        ))

    def clear(self):
        self.__model.clear()

    def append(self, label: str, nodes: List[str]):
        self.__model.append(_ResultItem(label, nodes))

    def items(self) -> List[_ResultItem]:
        return self.__model.items()

    def select(self, items: _ResultItem, replace: bool = False):
        selection = QItemSelection()
        for item in items:
            item_index = self.__model.item_index_of(item)
            index = self.__model.index(item_index, 0)
            selection.merge(QItemSelection(index, index), QItemSelectionModel.Select)

        command = QItemSelectionModel.ClearAndSelect if replace else QItemSelectionModel.Select
        self.__view.selectionModel().select(selection, command)

    def selected_items(self) -> List[_ResultItem]:
        indices = self.__view.selectionModel().selectedIndexes()
        return self.__model.items(indices)

    def __select_nodes(self):
        indices = self.__view.selectionModel().selectedIndexes()
        items = self.__model.items(indices)
        nodes = list(itertools.chain.from_iterable(item.nodes for item in items))
        _cmds.select(nodes, replace=True)


class _DescriptionWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.__icon = QLabel()

        self.__label = QLabel()
        font = self.__label.font()
        font.setBold(True)
        font.setPointSize(10)
        self.__label.setFont(font)

        self.__description = QLabel()
        self.__description.setWordWrap(True)
        self.__description.setMargin(5)

        self.__results = _ResultItemWidget()
        self.__results.selection_changed.connect(
            lambda items: self.__sync_result_selection(items, True, False)
        )

        self.__result_group_title = 'チェック結果（$COUNT項目）'
        self.__result_group = QGroupBox(self.__result_group_title)
        self.__result_group.setLayout(_layouts.vbox(
            self.__results,
        ))

        self.__nodes = _ResultItemWidget()
        self.__nodes.selection_changed.connect(
            lambda items: self.__sync_result_selection(items, False, True)
        )

        self.__nodes_group_title = '対象オブジェクト（$COUNT個）'
        self.__nodes_group = QGroupBox(self.__nodes_group_title)
        self.__nodes_group.setLayout(_layouts.vbox(
            self.__nodes,
        ))

        self.__modify_selected = QPushButton('選択したノードを自動修正')
        self.__modify_all = QPushButton('すべてのノードを自動修正')

        controls = QWidget()
        controls.setLayout(_layouts.hbox(
            self.__modify_selected,
            self.__modify_all,
            contents_margins=0
        ))

        self.setLayout(_layouts.vbox(
            _layouts.hbox(
                self.__icon,
                self.__label,
                _layouts.stretch(),
                contents_margins=0
            ),
            self.__description,
            self.__result_group,
            self.__nodes_group,
            controls
        ))

    def clear(self):
        self.__icon.setPixmap(None)
        self.__label.setText('')
        self.__description.setText('')
        self.__results.clear()
        self.__nodes.clear()
        self.setEnabled(False)

        self.__result_group.setTitle(self.__result_group_title.replace('$COUNT', '0'))
        self.__nodes_group.setTitle(self.__nodes_group_title.replace('$COUNT', '0'))

    def load_from(self, category: Optional[str], item: Optional[_items.CheckItem], results: Sequence[_items.CheckResult] = []):
        self.clear()

        header = ''
        if category:
            header = f'[{category}]'

        enable_modification = False

        if not item:
            self.__label.setText(header)
        else:
            self.setEnabled(True)
            self.__label.setText(f'{header} {item.label}')
            self.__description.setText(item.description)

            if len(results) == 1 and results[0].status == _items.CheckResultStatus.SUCCESS:
                self.__results.append('OK', [])
            else:
                for result in results:
                    self.__results.append(result.message, result.nodes)
                    for node in result.nodes:
                        self.__nodes.append(node, [node])

            if len(results) > 0:
                if all(r.is_success for r in results):
                    icon = _icons.success()
                elif any(r.is_error for r in results):
                    errors = filter(lambda r: r.is_error, results)
                    is_modifiable = any(e.is_modifiable for e in errors)
                    icon = _icons.error(is_modifiable)
                    enable_modification |= is_modifiable
                else:
                    warnings = filter(lambda r: r.is_warning, results)
                    is_modifiable = any(w.is_modifiable for w in warnings)
                    icon = _icons.warning(is_modifiable)
                    enable_modification |= is_modifiable

                icon_pixmap = icon.pixmap(icon.actualSize(QSize(32, 32)))
                self.__icon.setPixmap(icon_pixmap)

        result_count = len(results)
        self.__result_group.setTitle(self.__result_group_title.replace('$COUNT', str(result_count)))

        nodes_count = sum(len(r.nodes) for r in results)
        self.__nodes_group.setTitle(self.__nodes_group_title.replace('$COUNT', str(nodes_count)))

        self.__modify_selected.setEnabled(enable_modification)
        self.__modify_all.setEnabled(enable_modification)

    def __sync_result_selection(self, selection: List[_ResultItem], from_results: bool, from_nodes: bool):
        if from_results:
            # results -> nodes
            node_items = []
            selected_nodes = list(itertools.chain.from_iterable(item.nodes for item in selection))
            for item in self.__nodes.items():
                if item.nodes[0] in selected_nodes:
                    node_items.append(item)
            self.__nodes.select(node_items, True)

        if from_nodes:
            # nodes -> results
            pass
