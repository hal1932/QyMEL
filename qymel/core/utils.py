# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import functools

import maya.cmds as cmds


class UndoChunk(object):

    def __enter__(self):
        cmds.undoInfo(openChunk=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # type: (type, Exception, str) -> NoReturn
        cmds.undoInfo(closeChunk=True)
        raise exc_val


def undo_chunk(func):
    # type: (Callable) -> NoReturn
    @functools.wraps(func)
    def _func(*args, **kwargs):
        with UndoChunk():
            func(*args, **kwargs)
    return _func
