# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import functools

import maya.cmds as _cmds
from ..core import scopes as _scopes


class UndoScope(_scopes.Scope):

    def _on_enter(self):
        _cmds.undoInfo(openChunk=True)

    def _on_exit(self):
        _cmds.undoInfo(closeChunk=True)


def undo_scope(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        with UndoScope():
            func(*args, **kwargs)
    return _


class KeepSelectionScope(_scopes.Scope):

    def __init__(self):
        self.selection = []  # type: List[str]

    def _on_enter(self):
        self.selection = _cmds.ls(sl=True)

    def _on_exit(self):
        _cmds.select(self.selection, replace=True)


def keep_selection_scope(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        with KeepSelectionScope():
            func(*args, **kwargs)
    return _


class ViewportPauseScope(_scopes.Scope):

    def __init__(self):
        self.paused = False

    def _on_enter(self):
        self.paused = _cmds.ogs(query=True, pause=True)
        if not self.paused:
            _cmds.ogs(pause=True)

    def _on_exit(self):
        if _cmds.ogs(query=True, pause=True) != self.paused:
            _cmds.ogs(pause=True)


def viewport_pause_scope(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        with ViewportPauseScope():
            func(*args, **kwargs)
    return _
