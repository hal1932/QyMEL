# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import qymel.ui as _ui
from qymel.ui.pyside_module import *


# class MainWindow(_ui.MainWindowBase):
class MainWindow(_ui.ToolMainWindowBase):

    def __init__(self):
        super(MainWindow, self).__init__()

    def _setup_ui(self, central_widget):
        # type: (QWidget) -> NoReturn
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        layout.addWidget(QPushButton('a'))
        layout.addWidget(QPushButton('b'))

    def _shutdown_ui(self):
        print 'aaa'


class App(_ui.AppBase):

    def _create_window(self):
        # type: () -> QMainWindow
        return MainWindow()


def main():
    app = App()
    app.execute()


if __name__ == '__main__':
    main()
