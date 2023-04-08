# coding: utf-8
from typing import *

from qymel.ui.pyside_module import *
from qymel.ui import layouts as _layouts

from .. import items as _items
from . import icons as _icons


class ControlWidget(QWidget):

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
