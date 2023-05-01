# coding: utf-8
from typing import *

import functools

from ..pyside_module import *


class EventProxy(object):
    """
    btn1 = EventProxy.instantiate(QPushButton, 'TEST1')
    btn1.enter.connect(lambda e: print(f'enter1: {e}'))
    btn1.leave.connect(lambda e: print(f'leave1: {e}'))

    btn_cls = EventProxy.create(QPushButton)
    btn2 = btn_cls('TEST2')
    btn2.enter.connect(lambda e: print(f'enter2: {e}'))
    btn2.leave.connect(lambda e: print(f'leave2: {e}'))

    w = QWidget()
    lyt = QVBoxLayout()
    lyt.addWidget(btn1)
    lyt.addWidget(btn2)
    w.setLayout(lyt)
    w.show()
    """

    __cls_indices: Dict[str, int] = {}

    @staticmethod
    def create(cls: type) -> type:
        cls_name = EventProxy.__get_new_cls_name(cls)
        proxy = type(cls_name, tuple([EventProxy, cls]), {})
        setattr(proxy, '__target_cls', cls)
        return proxy

    @staticmethod
    def instantiate(cls: type, *args, **kwargs) -> 'EventProxy':
        proxy = EventProxy.create(cls)
        return proxy(*args, **kwargs)

    @staticmethod
    def __get_new_cls_name(cls: type) -> str:
        name = f'{EventProxy.__name__}_{cls.__name__}'
        index = EventProxy.__cls_indices.get(name, -1)
        index += 1
        EventProxy.__cls_indices[name] = index
        return f'{name}_{index}'

    def __init__(self, *_args, **_kwargs):
        super(EventProxy, self).__init__(*_args, **_kwargs)

    def __getattr__(self, signal_name: str) -> Optional[Signal]:
        if signal_name in self.__dict__:
            return self.__dict__[signal_name]

        event_name = f'{signal_name}Event'
        target_cls = getattr(self.__class__, '__target_cls')

        if event_name not in dir(target_cls):
            raise AttributeError(
                f"'EventProxy<{target_cls.__module__}.{target_cls.__name__}>' object has no attribute '{signal_name}'")

        setattr(self.__class__, signal_name, Signal(object))
        setattr(self, event_name, functools.partial(self.__emit_and_dispatch, signal_name, event_name))

        return getattr(self, signal_name)

    def __emit_and_dispatch(self, signal_to_emit: str, event_to_dispatch: str, event_args: QEvent):
        signal = getattr(self, signal_to_emit)
        signal.emit(event_args)

        event_func = getattr(super(EventProxy, self), event_to_dispatch)
        event_func(event_args)
