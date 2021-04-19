# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import functools

from ..core import scopes as _scopes
from .pyside_module import *


class WaitCursorScope(_scopes.Scope):

    def _on_enter(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

    def _on_exit(self):
        QApplication.restoreOverrideCursor()


def wait_cursor_scope(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        with WaitCursorScope():
            func(*args, **kwargs)
    return _


class KeepRowSelectionScope(_scopes.Scope):

    def __init__(self, view):
        # type: (Union[QAbstractItemView]) -> NoReturn
        self.__view = view
        self.__selection = None  # type: List[QModelIndex]

    def _on_enter(self):
        indices = self.__view.selectedIndexes()

        model = self.__view.model()
        if isinstance(model, QSortFilterProxyModel):
            indices = [model.mapToSource(index) for index in indices]

        self.__selection = indices

    def _on_exit(self):
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
