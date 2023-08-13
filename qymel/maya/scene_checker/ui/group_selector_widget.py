# coding: utf-8
from typing import *

from qymel.ui.pyside_module import *
from qymel.ui import layouts as _layouts

from .. import checker as _checker
from .. import groups as _groups


class GroupSelectorWidget(QWidget):

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
