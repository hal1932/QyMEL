import logging
import datetime

from ..pyside_module import *
from ...core import scopes as _scopes


__all__ = ['LoggingContext', 'LogAutoFlushScope', 'LogViewer']


class LoggingContext(object):
    """
    >>> logger = logging.getLogger(__name__)
    >>> LoggingContext.auto_flush = True
    >>> logger.info('info')
    >>> logger.warning('warning')
    >>> LoggingContext.auto_flush = False
    """

    auto_flush = False


class LogAutoFlushScope(_scopes.Scope):
    """
    >>> logger = logging.getLogger(__name__)
    >>> with LogAutoFlushScope():
    >>>     logger.info('info')
    >>>     logger.warning('warning')
    """

    def __init__(self, enable_auto_flush: bool = True) -> None:
        super(LogAutoFlushScope, self).__init__()
        self.__scoped_value = enable_auto_flush
        self.__current_value = LoggingContext.auto_flush

    def _on_enter(self) -> None:
        LoggingContext.auto_flush = self.__scoped_value

    def _on_exit(self) -> None:
        LoggingContext.auto_flush = self.__current_value


class LogViewer(QWidget):
    """
    >>> logger = logging.getLogger(__name__)
    >>> viewer = LogViewer()
    >>> logger.handlers.append(viewer.create_handler())
    >>> viewer.show()
    """

    def __init__(self, max_blocks: int = 1000, parent: QObject | None = None) -> None:
        super(LogViewer, self).__init__(parent)

        self.debug_format = QTextCharFormat()
        self.debug_format.setForeground(QBrush(QColor(119, 119, 119)))

        self.info_format = QTextCharFormat()
        self.info_format.setForeground(QBrush(QColor(20, 235, 20)))

        self.warning_format = QTextCharFormat()
        self.warning_format.setForeground(QBrush(QColor(235, 135, 20)))

        self.error_format = QTextCharFormat()
        self.error_format.setForeground(QBrush(QColor(235, 20, 20)))

        self.critical_format = QTextCharFormat()
        self.critical_format.setForeground(QBrush(QColor(235, 20, 20)))
        self.critical_format.setBackground(QBrush(QColor(235, 235, 235)))

        self.auto_flush = True
        self.timestamp_format = '%H:%M:%S'

        self._editor = LogTextEdit(max_blocks=max_blocks)

        editor_layout = QVBoxLayout()
        editor_layout.setContentsMargins(1, 1, 1, 1)
        editor_layout.setSpacing(0)
        editor_layout.addWidget(self._editor)
        self.setLayout(editor_layout)

    def create_handler(self, level: int = logging.NOTSET) -> logging.Handler:
        return LogHandler(self, level)

    def clear(self) -> None:
        self._editor.clear()

    def flush(self) -> None:
        cursor = self._editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        QApplication.processEvents()

    def append_debug_line(self, text: str) -> None:
        self._append(u'{}\n'.format(text), self.debug_format)

    def append_info_line(self, text: str) -> None:
        self._append(u'{}\n'.format(text), self.info_format)

    def append_warning_line(self, text: str) -> None:
        self._append(u'{}\n'.format(text), self.warning_format)

    def append_error_line(self, text: str) -> None:
        self._append(u'{}\n'.format(text), self.error_format)

    def append_critical_line(self, text: str) -> None:
        self._append(u'{}\n'.format(text), self.critical_format)

    def _append(self, text: str, char_format: str) -> None:
        if len(text) == 0:
            return

        if len(self.timestamp_format or '') > 0:
            ts = datetime.datetime.now().strftime(self.timestamp_format)
            text = u'[{}] {}'.format(ts, text)

        cursor = self._editor.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.setCharFormat(char_format)

        cursor.insertText(text)

        if self.auto_flush or LoggingContext.auto_flush:
            self.flush()


class LogTextEdit(QTextEdit):

    def __init__(self, max_blocks: int = 0, parent: QObject | None = None) -> None:
        super(LogTextEdit, self).__init__(parent)
        self.setReadOnly(True)
        self.textChanged.connect(self.__scroll_to_end)

        if max_blocks > 0:
            self.document().setMaximumBlockCount(max_blocks + 1)

    def contextMenuEvent(self, e: QContextMenuEvent) -> None:
        menu = self.createStandardContextMenu()  # type: QMenu
        menu.addSeparator()
        clear_action = menu.addAction('Clear')

        action = menu.exec_(e.globalPos())
        if action == clear_action:
            self.clear()

    def __scroll_to_end(self) -> None:
        scroll_bar = self.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())


class LogHandler(logging.Handler):

    def __init__(self, view: LogViewer, level: int) -> None:
        super(LogHandler, self).__init__(level)
        self.__view = view

    def emit(self, record: logging.LogRecord) -> None:
        try:
            if record.levelno == logging.DEBUG:
                self.__view.append_debug_line(record.getMessage())

            elif record.levelno == logging.INFO:
                self.__view.append_info_line(record.getMessage())

            elif record.levelno == logging.WARNING:
                self.__view.append_warning_line(record.getMessage())

            elif record.levelno == logging.ERROR:
                self.__view.append_error_line(record.getMessage())

            elif record.levelno == logging.CRITICAL:
                self.__view.append_critical_line(record.getMessage())

        except:
            self.handleError(record)
