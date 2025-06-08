import collections.abc as abc
import typing


_TItem = typing.TypeVar('_TItem')


def any(
        sequence: abc.Sequence[_TItem],
        predicate: abc.Callable[[_TItem], bool]|None = None
) -> bool:
    for item in sequence:
        if predicate is None or predicate(item):
            return True
    return False


def first(
        sequence: abc.Sequence[_TItem],
        predicate: abc.Callable[[_TItem], bool]|None = None
) -> _TItem:
    for item in sequence:
        if predicate is None or predicate(item):
            return item
    raise StopIteration()


def first_or_default(
        sequence: abc.Sequence[_TItem],
        predicate: abc.Callable[[_TItem], bool]|None = None,
        default: _TItem|None = None
) -> _TItem:
    for item in sequence:
        if predicate is None or predicate(item):
            return item
    return default


def last(
        sequence: abc.Sequence[_TItem],
        predicate: abc.Callable[[_TItem], bool]|None = None
) -> _TItem:
    for item in reversed(sequence):
        if predicate is None or predicate(item):
            return item
    raise StopIteration()


def last_or_default(
        sequence: abc.Sequence[_TItem],
        predicate: abc.Callable[[_TItem], bool]|None = None,
        default: _TItem|None = None
) -> _TItem:
    for item in reversed(sequence):
        if predicate is None or predicate(item):
            return item
    return default
