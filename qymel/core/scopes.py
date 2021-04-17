# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import functools

import maya.cmds as cmds


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


class UndoScope(_Scope):

    def _on_enter(self):
        cmds.undoInfo(openChunk=True)

    def _on_exit(self):
        cmds.undoInfo(closeChunk=True)


def undo_scope(func):
    def _(*args, **kwargs):
        with UndoScope():
            func(*args, **kwargs)

    return _


class KeepSelectionScope(_Scope):

    def __init__(self):
        self.selection = []  # type: List[str]

    def _on_enter(self):
        self.selection = cmds.ls(sl=True)

    def _on_exit(self):
        cmds.select(self.selection, replace=True)


def keep_selection_scope(func):
    def _(*args, **kwargs):
        with KeepSelectionScope():
            func(*args, **kwargs)

    return _
