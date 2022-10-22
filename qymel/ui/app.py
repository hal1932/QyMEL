# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import sys

try:
    import maya.OpenMayaUI as _omui
    from maya.app.general.mayaMixin import MayaQWidgetBaseMixin as _MayaWidgetBaseMixin
    _MAYA = True
except ImportError:
    _MAYA = False

from .pyside_module import *
from . import layouts as _layouts


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
        # type: (QApplication) -> NoReturn
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
        maya_main_window_ptr = _omui.MQtUtil.mainWindow()
        if sys.version_info.major == 2:
            maya_main_window_ptr = long(maya_main_window_ptr)
        else:
            maya_main_window_ptr = int(maya_main_window_ptr)
        return wrapInstance(maya_main_window_ptr, QWidget)


    class MainWindowBase(_MainWindowBase, _MayaWidgetBaseMixin):

        def __init__(self, parent=None):
            maya_window = get_maya_window()

            for child in maya_window.children():
                # reload でポインタが変わったときのために名前で比較する
                if child.objectName() == self.absolute_name:
                    child.close()

            parent = parent or maya_window
            super(MainWindowBase, self).__init__(parent=parent)
else:
    MainWindowBase = _MainWindowBase


class ToolMainWindowBase(MainWindowBase):

    @property
    def execute_and_close_label(self):
        # type: () -> text_type
        return u'適用して閉じる'

    @property
    def execute_label(self):
        # type: () -> text_type
        return u'適用'

    @property
    def close_label(self):
        # type: () -> text_type
        return u'閉じる'

    def __init__(self, parent=None):
        # type: (QObject) -> NoReturn
        super(ToolMainWindowBase, self).__init__(parent=parent)

    def setup_ui(self):
        # type: () -> ToolMainWindowBase
        widget = self.centralWidget()
        if widget is not None:
            widget.deleteLater()

        widget = QWidget()
        self.setCentralWidget(widget)

        user_widget = QWidget()
        self._setup_ui(user_widget)

        execute_and_close_button = QPushButton(self.execute_and_close_label)
        execute_and_close_button.clicked.connect(self._execute_and_close)

        execute_button = QPushButton(self.execute_label)
        execute_button.clicked.connect(self._execute)

        close_button = QPushButton(self.close_label)
        close_button.clicked.connect(self._close)

        widget.setLayout(_layouts.vbox(
            user_widget,
            _layouts.hbox(
                execute_and_close_button,
                execute_button,
                close_button,
            )
        ))

        return self

    def _execute(self):
        pass

    def _execute_and_close(self):
        self._execute()
        self._close()

    def _close(self):
        self.close()
