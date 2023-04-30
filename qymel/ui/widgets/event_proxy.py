# coding: utf-8
from typing import *

import functools

from ..pyside_module import *


class EventProxy(object):
    """
    btn = EventProxy.create(QPushButton)
    btn.enter.connect(lambda e: print(f'enter: {e}'))
    btn.leave.connect(lambda e: print(f'leave: {e}'))
    btn.show()
    """

    @staticmethod
    def create(cls, *args, **kwargs):
        # type: (type, List[Any], Dict[str, Any]) -> EventProxy
        proxy = type(f'{EventProxy.__name__}_{cls.__name__}', tuple([EventProxy, cls]), {})
        return proxy(cls, *args, **kwargs)

    def __init__(self, cls, *_args, **_kwargs):
        # type: (type, List[Any], Dict[str, Any]) -> NoReturn
        self.__target_cls = cls
        super(EventProxy, self).__init__(*_args, **_kwargs)

    def __getattr__(self, signal_name):
        # type: (str) -> Optional[Signal]
        if signal_name in self.__dict__:
            return self.__dict__[signal_name]

        event_name = f'{signal_name}Event'
        if event_name not in dir(self.__target_cls):
            raise AttributeError(
                f"'EventProxy<{self.__target_cls.__module__}.{self.__target_cls.__name__}>' object has no attribute '{signal_name}'")

        cls = self.__class__
        self.__class__ = type(cls.__name__, cls.__bases__, {
            **cls.__dict__,
            signal_name: Signal(object),
        })

        setattr(self, event_name, functools.partial(self.__call_event, event_name, signal_name))

        return getattr(self, signal_name)

    def __call_event(self, event_name, signal_name, event):
        # type: (str, str, QEvent) -> NoReturn
        signal = getattr(self, signal_name)
        signal.emit(event)

        event_func = getattr(super(EventProxy, self), event_name)
        event_func(event)
