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
