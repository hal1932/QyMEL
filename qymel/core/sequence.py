# coding: utf-8
from typing import *


_TItem = TypeVar('_TItem')


def any(
        sequence: Sequence[_TItem],
        predicate: Optional[Callable[[_TItem], bool]] = None
) -> bool:
    for item in sequence:
        if predicate is None or predicate(item):
            return True
    return False


def first(
        sequence: Sequence[_TItem],
        predicate: Optional[Callable[[_TItem], bool]] = None
) -> _TItem:
    for item in sequence:
        if predicate is None or predicate(item):
            return item
    raise StopIteration()


def first_or_default(
        sequence: Sequence[_TItem],
        predicate: Optional[Callable[[_TItem], bool]] = None,
        default: Optional[_TItem] = None
) -> _TItem:
    for item in sequence:
        if predicate is None or predicate(item):
            return item
    return default


def last(
        sequence: Sequence[_TItem],
        predicate: Optional[Callable[[_TItem], bool]] = None
) -> _TItem:
    for item in reversed(sequence):
        if predicate is None or predicate(item):
            return item
    raise StopIteration()


def last_or_default(
        sequence: Sequence[_TItem],
        predicate: Optional[Callable[[_TItem], bool]] = None,
        default: Optional[_TItem] = None
) -> _TItem:
    for item in reversed(sequence):
        if predicate is None or predicate(item):
            return item
    return default
