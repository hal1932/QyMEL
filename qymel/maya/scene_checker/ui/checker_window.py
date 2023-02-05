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
        self._controls.execute_all_requested.connect(self.__execute_all)
        self._controls.modify_all_requested.connect(self.__modify_all)

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
        self._main_splitter.setSizes([int(x) for x in settings.value('split')] or [])

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

    @_ui_scopes.wait_cursor_scope
    def __execute_all(self):
        group = self._groups.selected_group
        group.execute_all()
        self._items.load_results()
        self._controls.load_from(group.results())
        self.__reload_description(None)

    @_ui_scopes.wait_cursor_scope
    @_maya_scopes.undo_scope
    def __modify_all(self):
        group = self._groups.selected_group
        group.modify_all()
        self.__execute_all()


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

        def _select_nodes(nodes):
            _cmds.select(clear=True)
            for node in nodes:
                if _cmds.objExists(node):
                    _cmds.select(node)

        self.__results = QListWidget()
        self.__results.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__results.itemSelectionChanged.connect(functools.partial(self.__sync_result_selection, True, False))
        self.__results.itemSelectionChanged.connect(
            lambda: _select_nodes(self.__results.currentItem().data(Qt.UserRole) if self.__results.currentItem() else [])
        )
        result_group = QGroupBox('チェック結果')
        result_group.setLayout(_layouts.vbox(
            self.__results,
        ))

        self.__nodes = QListWidget()
        self.__nodes.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__nodes.itemSelectionChanged.connect(functools.partial(self.__sync_result_selection, False, True))
        self.__nodes.itemSelectionChanged.connect(
            lambda: _select_nodes([self.__nodes.currentItem().text()] if self.__nodes.currentItem() else [])
        )
        nodes_group = QGroupBox('対象ノード')
        nodes_group.setLayout(_layouts.vbox(
            self.__nodes,
        ))

        self.__fix_selected = QPushButton('選択したノードを自動修正')
        self.__fix_all = QPushButton('すべてのノードを自動修正')

        controls = QWidget()
        controls.setLayout(_layouts.hbox(
            self.__fix_selected,
            self.__fix_all,
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
            result_group,
            nodes_group,
            controls
        ))

    def clear(self):
        self.__icon.setPixmap(None)
        self.__label.setText('')
        self.__description.setText('')
        self.__results.clear()
        self.__nodes.clear()
        self.setEnabled(False)

    def load_from(self, category: Optional[str], item: Optional[_items.CheckItem], results: Sequence[_items.CheckResult] = []):
        self.clear()

        header = ''
        if category:
            header = f'[{category}]'

        if not item:
            self.__label.setText(header)
        else:
            self.setEnabled(True)
            self.__label.setText(f'{header} {item.label}')
            self.__description.setText(item.description)

            if len(results) == 1 and results[0].status == _items.CheckResultStatus.SUCCESS:
                item = QListWidgetItem()
                item.setText('OK')
                item.setData(Qt.UserRole, [])
                self.__results.addItem(item)
            else:
                for result in results:
                    item = QListWidgetItem()
                    item.setText(result.message)
                    item.setData(Qt.UserRole, result.nodes)
                    self.__results.addItem(item)
                    self.__nodes.addItems(result.nodes)

            if len(results) > 0:
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

                icon_pixmap = icon.pixmap(icon.actualSize(QSize(32, 32)))
                self.__icon.setPixmap(icon_pixmap)

    def __sync_result_selection(self, from_results: bool, from_nodes: bool):
        if from_results:
            # results -> nodes
            nodes = list(itertools.chain.from_iterable(item.data(Qt.UserRole) for item in self.__results.selectedItems()))
            for i in range(self.__nodes.count()):
                item = self.__nodes.item(i)
                self.__nodes.setItemSelected(item, item.text() in nodes)
        if from_nodes:
            # nodes -> results
            pass

