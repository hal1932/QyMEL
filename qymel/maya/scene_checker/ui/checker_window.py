# coding: utf-8
from typing import *

from qymel.ui.pyside_module import *
from qymel.ui import app as _app
from qymel.ui import layouts as _layouts
from qymel.ui import scopes as _ui_scopes
from qymel.ui.objects import serializer as _serializer
from qymel.maya import scopes as _maya_scopes

from .. import checker as _checker
from .. import groups as _groups
from . import control_widget as _control
from . import group_selector_widget as _group_selector
from . import item_list_widget as _item_list
from . import description_widget as _description


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
        self._groups = _group_selector.GroupSelectorWidget()
        self._items = _item_list.ItemListWidget()
        self._description = _description.DescriptionWidget()
        self._controls = _control.ControlWidget()
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
