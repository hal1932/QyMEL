# coding: utf-8
from typing import *

import os

from qymel.ui.pyside_module import *


_icons: Dict[str, QIcon] = {}


def execute() -> QIcon:
    return icon('execute')


def modify() -> QIcon:
    return icon('modify')


def success() -> QIcon:
    return icon('success')


def invalid() -> QIcon:
    return icon('invalid')


def warning(is_modifiable: bool) -> QIcon:
    if is_modifiable:
        return icon('warning-modifiable')
    return icon('warning')


def error(is_modifiable: bool) -> QIcon:
    if is_modifiable:
        return icon('error-modifiable')
    return icon('error')


def icon(name: str) -> QIcon:
    global _icons
    if name not in _icons:
        _icons[name] = QIcon(_file_path(name))
    return _icons[name]


def _file_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), f'{name}.png')
