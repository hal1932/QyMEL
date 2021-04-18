# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import functools
import types
import pstats
import cProfile

import maya.cmds as _cmds


class _Scope(object):

    def __enter__(self):
        self._on_enter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # type: (Type, Exception, types.TracebackType) -> bool
        self._on_exit()
        return False  # 例外伝搬を止めない

    def _on_enter(self):
        pass

    def _on_exit(self):
        pass


class UndoScope(_Scope):

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


class KeepSelectionScope(_Scope):

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


class ViewportPauseScope(_Scope):

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


class ProfileScope(_Scope):

    def __init__(self, callback=None):
        # type: (Callable[[pstats.Stats], None]) -> NoReturn
        self.profile = cProfile.Profile()
        self.callback = callback

    def _on_enter(self):
        self.profile.enable()

    def _on_exit(self):
        self.profile.disable()
        stats = pstats.Stats(self.profile).sort_stats('cumulative')
        if self.callback is not None:
            self.callback(stats)
        else:
            stats.print_stats()


def profile_scope(callback=None):
    def _profile_scope(func):
        @functools.wraps(func)
        def _(*args, **kwargs):
            with ProfileScope(callback):
                func(*args, **kwargs)
        return _
    return _profile_scope
