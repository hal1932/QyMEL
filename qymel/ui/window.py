# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

from .pyside_module import *


class WindowBase(QWidget):

    def setup_ui(self):
        self.setWindowFlags(Qt.Tool)
        self._setup_ui(self)
        return self

    def _setup_ui(self, central_widget):
        # type: (QWidget) -> NoReturn
        pass

    def _show_ui(self):
        pass

    def _shutdown_ui(self):
        pass

    def showEvent(self, event):
        self._show_ui()

    def closeEvent(self, event):
        self._shutdown_ui()
