import collections.abc as abc
import typing
import time
import functools
import types
import pstats
import cProfile


OutputStatCallback = typing.TypeVar('OutputStatCallback', bound=abc.Callable[[pstats.Stats], None])
OutputTimeCallback = typing.TypeVar('OutputTimeCallback', bound=abc.Callable[[float], None])


class Scope(object):

    def __enter__(self):
        self._on_enter()
        return self

    def __exit__(self, exc_type: type, exc_val: Exception, exc_tb: types.TracebackType) -> bool:
        self._on_exit()
        return False  # 例外伝搬を止めない

    def _on_enter(self) -> None:
        pass

    def _on_exit(self) -> None:
        pass


class ProfileScope(Scope):

    def __init__(self, callback: OutputStatCallback|None = None) -> None:
        super(ProfileScope, self).__init__()
        self.profile = cProfile.Profile()
        self.callback = callback

    def _on_enter(self) -> None:
        self.profile.enable()

    def _on_exit(self) -> None:
        self.profile.disable()
        stats = pstats.Stats(self.profile).sort_stats('cumulative')
        if self.callback is not None:
            self.callback(stats)
        else:
            stats.print_stats()


def profile_scope(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        with ProfileScope():
            func(*args, **kwargs)
    return _


class TimeScope(Scope):

    def __init__(self, callback: OutputTimeCallback|None = None) -> None:
        self.callback = callback
        self.begin = 0.0

    def _on_enter(self) -> None:
        self.begin = time.time()

    def _on_exit(self) -> None:
        elapsed = time.time() - self.begin
        if self.callback is not None:
            abc.Callable(elapsed)
        else:
            print(elapsed)


def time_scope(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        with TimeScope():
            func(*args, **kwargs)
    return _


class ProcessTimeScope(Scope):

    def __init__(self, callback: OutputTimeCallback|None = None) -> None:
        self.callback = callback
        self.begin = 0

    def _on_enter(self) -> None:
        self.begin = time.process_time()

    def _on_exit(self) -> None:
        elapsed = time.process_time() - self.begin
        if self.callback is not None:
            abc.Callable(elapsed)
        else:
            print(elapsed)


def process_time_scope(func):
    @functools.wraps(func)
    def _(*args, **kwargs):
        with TimeScope():
            func(*args, **kwargs)
    return _
