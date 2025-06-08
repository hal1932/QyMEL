import collections.abc as abc
import functools

from ..core import scopes as _scopes
from .pyside_module import *


class WaitCursorScope(_scopes.Scope):

    def _on_enter(self) -> None:
        QApplication.setOverrideCursor(Qt.WaitCursor)

    def _on_exit(self) -> None:
        QApplication.restoreOverrideCursor()


def wait_cursor_scope(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        with WaitCursorScope():
            func(*args, **kwargs)
    return _


class KeepRowSelectionScope(_scopes.Scope):

    def __init__(self, view: QAbstractItemView) -> None:
        super().__init__()
        self.__view = view
        self.__selection: list[QModelIndex]|None = None

    def _on_enter(self) -> None:
        indices = self.__view.selectedIndexes()

        model = self.__view.model()
        if isinstance(model, QSortFilterProxyModel):
            indices = [model.mapToSource(index) for index in indices]

        self.__selection = indices

    def _on_exit(self) -> None:
        if self.__selection is None:
            return

        view = self.__view

        mode = view.selectionMode()
        view.setSelectionMode(QAbstractItemView.MultiSelection)

        indices = self.__selection

        model = self.__view.model()
        if isinstance(model, QSortFilterProxyModel):
            indices = [model.mapFromSource(index) for index in indices]

        for index in indices:
            view.selectRow(index.row())

        view.setSelectionMode(mode)


class SignalConnectionScope(_scopes.Scope):

    def __init__(self, signal: Signal, slot: abc.Callable) -> None:
        super().__init__()
        self.__signal = signal
        self.__slot = slot

    def _on_enter(self) -> None:
        self.__signal.connect(self.__slot)

    def _on_exit(self) -> None:
        self.__signal.disconnect(self.__slot)


class SignalDisconnectionScope(_scopes.Scope):

    def __init__(self, signal: Signal, slot: abc.Callable) -> None:
        super().__init__()
        self.__signal = signal
        self.__slot = slot

    def _on_enter(self) -> None:
        self.__signal.disconnect(self.__slot)

    def _on_exit(self) -> None:
        self.__signal.connect(self.__slot)
