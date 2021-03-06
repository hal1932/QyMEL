# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import sys

try:
    import maya.OpenMayaUI as omui
    from maya.app.general.mayaMixin import MayaQWidgetBaseMixin
    _MAYA = True
except ImportError:
    _MAYA = False

from .pyside_module import *
from .layouts import *


class AppBase(object):

    def __init__(self):
        self._app = None  # type: Optional[QApplication]
        self._window = None  # type: Optional[QMainWindow]

    def execute(self):
        self._app = self._setup_application()

        self._initialize(self._app)
        self._window = self._create_window()
        if self._window is not None:
            self._window.setup_ui().show()

        self._exec_application_main_loop(self._app)

    def _setup_application(self):
        # type: () -> QApplication
        app = QApplication.instance()
        if not _MAYA:
            if app is None:
                app = QApplication(sys.argv)
        return app

    def _exec_application_main_loop(self, app):
        # type: (QApplication) -> NoReturn
        if not _MAYA:
            sys.exit(app.exec_())

    def _initialize(self, app):
        # type: (QApplication) -> nore
        pass

    def _create_window(self):
        # type: () -> QMainWindow
        pass


class _MainWindowBase(QMainWindow):

    @property
    def absolute_name(self):
        # type: () -> str
        return '{}.{}'.format(self.__module__, self.__class__.__name__)

    def __init__(self, parent=None):
        # type: (QObject) -> NoReturn
        super(_MainWindowBase, self).__init__(parent)
        self.setObjectName(self.absolute_name)
        self.setAttribute(Qt.WA_DeleteOnClose)

    def setup_ui(self):
        # type: () -> MainWindowBase
        widget = self.centralWidget()
        if widget is not None:
            widget.deleteLater()
        widget = QWidget()

        self.setCentralWidget(widget)
        self._setup_ui(widget)
        return self

    def closeEvent(self, _):
        # type: (QCloseEvent) -> NoReturn
        self._shutdown_ui()

    def _setup_ui(self, central_widget):
        # type: (QWidget) -> NoReturn
        pass

    def _shutdown_ui(self):
        pass


if _MAYA:
    def get_maya_window():
        # type: () -> QWidget
        maya_main_window_ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(long(maya_main_window_ptr), QWidget)


    class MainWindowBase(_MainWindowBase, MayaQWidgetBaseMixin):

        def __init__(self):
            maya_window = get_maya_window()

            for child in maya_window.children():
                # reload でポインタが変わったときのために名前で比較する
                if child.objectName() == self.absolute_name:
                    child.close()

            super(MainWindowBase, self).__init__(parent=maya_window)
else:
    MainWindowBase = _MainWindowBase


class ToolMainWindowBase(MainWindowBase):

    @property
    def execute_label(self):
        # type: () -> str
        return u'実行'

    @property
    def apply_label(self):
        # type: () -> str
        return u'適用'

    @property
    def close_label(self):
        # type: () -> str
        return u'閉じる'

    def __init__(self):
        super(ToolMainWindowBase, self).__init__()

    def setup_ui(self):
        # type: () -> ToolMainWindowBase
        widget = self.centralWidget()
        if widget is not None:
            widget.deleteLater()

        widget = QWidget()
        self.setCentralWidget(widget)

        user_widget = QWidget()
        self._setup_ui(user_widget)

        execute_button = QPushButton(self.execute_label)
        execute_button.clicked.connect(self._execute)

        apply_button = QPushButton(self.apply_label)
        apply_button.clicked.connect(self._apply)

        close_button = QPushButton(self.close_label)
        close_button.clicked.connect(self._close)

        widget.setLayout(vbox(
            user_widget,
            hbox(
                execute_button,
                apply_button,
                close_button,
            )
        ))

        return self

    def _execute(self):
        self._apply()
        self._close()

    def _apply(self):
        pass

    def _close(self):
        self.close()
