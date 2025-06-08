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


class _MainWindowBase(QMainWindow, _serializer.SerializableObjectMixin):

    before_setup_ui = Signal()
    after_setup_ui = Signal()
    after_show = Signal()
    before_shutdown_ui = Signal()
    after_shutdown_ui = Signal()
    after_close = Signal()

    @property
    def absolute_name(self) -> str:
        return f'{self.__module__}.{self.__class__.__name__}'

    def __init__(self, parent: QObject|None = None) -> None:
        super(_MainWindowBase, self).__init__(parent)
        self.setObjectName(self.absolute_name)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def setup_ui(self) -> 'MainWindowBase':
        widget = self.centralWidget()
        if widget is not None:
            widget.deleteLater()
        widget = QWidget()

        self.setCentralWidget(widget)

        self.before_setup_ui.emit()
        self._setup_ui(widget)
        self.after_setup_ui.emit()

        return self

    def showEvent(self, _: QShowEvent) -> None:
        self.after_show.emit()

    def closeEvent(self, _: QCloseEvent) -> None:
        self.before_shutdown_ui.emit()
        self._shutdown_ui()
        self.after_shutdown_ui.emit()

        self.after_close.emit()

    def screen(self) -> QScreen:
        return self.window().windowHandle().screen()

    def default_geometry(self) -> QRect:
        return QRect(self.screen().geometry().center(), QSize(0, 0))

    def enable_serialize(self, settings: QSettings) -> None:
        serializer = _serializer.ObjectSerializer()

        def _restore_ui():
            serializer.deserialize(settings, self)

        def _store_ui():
            serializer.serialize(self, settings)
            settings.sync()

        self.after_setup_ui.connect(_restore_ui)
        self.before_shutdown_ui.connect(_store_ui)

    def serialize(self, settings: QSettings) -> None:
        settings.setValue('_geom', self.geometry())
        self._serialize(settings)

    def deserialize(self, settings: QSettings) -> None:
        geom = settings.value('_geom')
        if geom:
            self.setGeometry(geom)
        self._deserialize(settings)

    def _setup_ui(self, central_widget: QWidget) -> None:
        pass

    def _shutdown_ui(self) -> None:
        pass

    def _serialize(self, settings: QSettings) -> None:
        pass

    def _deserialize(self, settings: QSettings) -> None:
        pass


if _MAYA:
    def get_maya_window() -> QWidget:
        maya_main_window_ptr = int(_omui.MQtUtil.mainWindow())
        return wrapInstance(maya_main_window_ptr, QWidget)


    class MainWindowBase(_MainWindowBase, _MayaWidgetBaseMixin):

        def __init__(self, parent: QObject|None = None) -> None:
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
    def execute_and_close_label(self) -> str:
        return u'適用して閉じる'

    @property
    def execute_label(self) -> str:
        return u'適用'

    @property
    def close_label(self) -> str:
        return u'閉じる'

    def __init__(self, parent: QObject|None = None) -> None:
        super(ToolMainWindowBase, self).__init__(parent=parent)

    def setup_ui(self) -> 'ToolMainWindowBase':
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

    def _execute(self) -> bool:
        return True

    def _execute_and_close(self) -> None:
        if self._execute() == False:
            return
        self._close()

    def _close(self) -> None:
        self.close()


class AppBase(object):

    @property
    def window(self) -> QMainWindow:
        return self._window

    def __init__(self) -> None:
        self._app: QApplication|None = None
        self._window: _MainWindowBase|None = None

    def execute(self) -> None:
        self._app = self._setup_application()

        self._initialize(self._app)
        self._window = self._create_window()
        if self._window is not None:
            self._on_before_setup_ui()
            self._window.setup_ui()
            self._on_after_setup_ui()
            self._window.show()

        self._exec_application_main_loop(self._app)

    def _setup_application(self) -> QApplication:
        app = QApplication.instance()
        if not _MAYA:
            if app is None:
                app = QApplication(sys.argv)
        return app

    def _exec_application_main_loop(self, app: QApplication) -> None:
        ret = app.exec_()
        self._finalize()
        if not _MAYA:
            sys.exit(ret)

    def _initialize(self, app: QApplication) -> None:
        pass

    def _create_window(self) -> QMainWindow:
        pass

    def _on_before_setup_ui(self) -> None:
        pass

    def _on_after_setup_ui(self) -> None:
        pass

    def _finalize(self) -> None:
        pass
