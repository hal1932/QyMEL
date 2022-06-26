# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *


TItem = TypeVar('_TItem')


def first(sequence, predicate=None):
    # type: (Sequence[TItem], Callable[[TItem], bool]) -> TItem
    for item in sequence:
        if predicate is None or predicate(item):
            return item
    raise StopIteration()


def first_or_default(sequence, predicate=None, default=None):
    # type: (Sequence[TItem], Callable[[TItem], bool], TItem) -> TItem
    for item in sequence:
        if predicate is None or predicate(item):
            return item
    return default


def last(sequence, predicate=None):
    # type: (Sequence[TItem], Callable[[TItem], bool]) -> TItem
    for item in reversed(sequence):
        if predicate is None or predicate(item):
            return item
    raise StopIteration()


def last_or_default(sequence, predicate=None, default=None):
    # type: (Sequence[TItem], Callable[[TItem], bool], TItem) -> TItem
    for item in reversed(sequence):
        if predicate is None or predicate(item):
            return item
    return default
