# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import functools

from .pyside_module import *


class _Scope(object):

    def __enter__(self):
        self._on_enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # type: (Type, Exception, TracebackType) -> bool
        self._on_exit()
        return False  # 例外伝搬を止めない

    def _on_enter(self):
        pass

    def _on_exit(self):
        pass


class WaitCursorScope(_Scope):

    def _on_enter(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

    def _on_exit(self):
        QApplication.restoreOverrideCursor()


def wait_cursor_scope(func):
    def _(*args, **kwargs):
        with WaitCursorScope():
            func(*args, **kwargs)
    return _
