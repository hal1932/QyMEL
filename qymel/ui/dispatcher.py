# coding: utf-8
from typing import *

from .pyside_module import *


class _MethodInvokeEvent(QEvent):

    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, func, args, kwargs):
        super(_MethodInvokeEvent, self).__init__(_MethodInvokeEvent.EVENT_TYPE)
        self.func = func
        self.args = args
        self.kwargs = kwargs


class _MethodInvoker(QObject):

    def __init__(self):
        super(_MethodInvoker, self).__init__()

    def event(self, e: _MethodInvokeEvent):
        return e.func(*e.args, **e.kwargs)


class Dispatcher(QObject):

    invoker = _MethodInvoker()

    @staticmethod
    def begin_invoke(func, *args, **kwargs):
        QCoreApplication.postEvent(Dispatcher.invoker, _MethodInvokeEvent(func, args, kwargs))
