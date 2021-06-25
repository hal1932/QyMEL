# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import time
import functools
import types
import pstats
import cProfile


class Scope(object):

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


class ProfileScope(Scope):

    def __init__(self, callback=None):
        # type: (Callable[[pstats.Stats], None]) -> NoReturn
        super(ProfileScope, self).__init__()
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


class TimeScope(Scope):

    def __init__(self, callback=None):
        # type: (Callable[[float], None]) -> NoReturn
        self.callback = callback
        self.begin = 0

    def _on_enter(self):
        self.begin = time.time()

    def _on_exit(self):
        elapsed = time.time() - self.begin
        if self.callback is not None:
            callable(elapsed)
        else:
            print(elapsed)


def time_scope(callback=None):
    def _time_scope(func):
        @functools.wraps(func)
        def _(*args, **kwargs):
            with TimeScope(callback):
                func(*args, **kwargs)
        return _
    return _time_scope
