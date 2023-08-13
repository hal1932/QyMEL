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
from .objects import serializer as _serializer


class AppBase(object):

    @property
    def window(self):
        # type: () -> QMainWindow
        return self._window

    def __init__(self):
        self._app = None  # type: Optional[QApplication]
        self._window = None  # type: Optional[QMainWindow]

    def execute(self):
        self._app = self._setup_application()

        self._initialize(self._app)
        self._window = self._create_window()
        if self._window is not None:
            self._on_before_setup_ui()
            self._window.setup_ui()
            self._on_after_setup_ui()
            self._window.show()

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
        ret = app.exec_()
        self._finalize()
        if not _MAYA:
            sys.exit(ret)

    def _initialize(self, app):
        # type: (QApplication) -> NoReturn
        pass

    def _create_window(self):
        # type: () -> QMainWindow
        pass

    def _on_before_setup_ui(self):
        pass

    def _on_after_setup_ui(self):
        pass

    def _finalize(self):
        pass


class _MainWindowBase(QMainWindow, _serializer.SerializableObjectMixin):

    before_setup_ui = Signal()
    after_setup_ui = Signal()
    after_show = Signal()
    before_shutdown_ui = Signal()
    after_shutdown_ui = Signal()
    after_close = Signal()

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

        self.before_setup_ui.emit()
        self._setup_ui(widget)
        self.after_setup_ui.emit()

        return self

    def showEvent(self, _):
        # type: (QShowEvent) -> NoReturn
        self.after_show.emit()

    def closeEvent(self, _):
        # type: (QCloseEvent) -> NoReturn
        self.before_shutdown_ui.emit()
        self._shutdown_ui()
        self.after_shutdown_ui.emit()

        self.after_close.emit()

    def screen(self):
        # type: () -> QScreen
        return self.window().windowHandle().screen()

    def default_geometry(self):
        # type: () -> QRect
        return QRect(self.screen().geometry().center(), QSize(0, 0))

    def enable_serialzie(self, settings=None):
        # type: (QSettings) -> NoReturn
        serializer = _serializer.ObjectSerializer()

        def _restore_ui():
            serializer.deserialize(settings, self)

        def _store_ui():
            serializer.serialize(self, settings)
            settings.sync()

        self.after_setup_ui.connect(_restore_ui)
        self.before_shutdown_ui.connect(_store_ui)

    def serialize(self, settings):
        # type: (QSettings) -> NoReturn
        settings.setValue('_geom', self.geometry())
        self._serialize(settings)

    def deserialize(self, settings):
        # type: (QSettings) -> NoReturn
        geom = settings.value('_geom')
        if geom:
            self.setGeometry(geom)
        self._deserialize(settings)

    def screen(self):
        # type: () -> QScreen
        return self.parent().windowHandle().screen()

    def _setup_ui(self, central_widget):
        # type: (QWidget) -> NoReturn
        pass

    def _shutdown_ui(self):
        pass

    def _serialize(self, settings):
        # type: (QSettings) -> None
        pass

    def _deserialize(self, settings):
        # type: (QSettings) -> None
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

        self.before_setup_ui.emit()
        self._setup_ui(user_widget)
        self.after_setup_ui.emit()

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
        # type: () -> bool
        return True

    def _execute_and_close(self):
        if self._execute() == False:
            return
        self._close()

    def _close(self):
        self.close()
