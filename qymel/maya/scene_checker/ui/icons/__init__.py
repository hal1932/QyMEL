
import os

from qymel.ui.pyside_module import *


_icons: dict[str, QIcon] = {}


class IconType(object):

    EXECUTE = 'execute'
    MODIFY = 'modify'
    SUCCESS = 'success'
    INVALID = 'invalid'
    WARNING = 'warning'
    WARNING_MODIFIABLE = 'warning-modifiable'
    ERROR = 'error'
    ERROR_MODIFIABLE = 'error-modifiable'


# region icon()のショートカット
def execute() -> QIcon:
    return icon(IconType.EXECUTE)


def modify() -> QIcon:
    return icon(IconType.MODIFY)


def success() -> QIcon:
    return icon(IconType.SUCCESS)


def invalid() -> QIcon:
    return icon(IconType.INVALID)


def warning(is_modifiable: bool) -> QIcon:
    if is_modifiable:
        return icon(IconType.WARNING_MODIFIABLE)
    return icon(IconType.WARNING)


def error(is_modifiable: bool) -> QIcon:
    if is_modifiable:
        return icon(IconType.ERROR_MODIFIABLE)
    return icon(IconType.ERROR)
# endregion


def icon(name: str) -> QIcon:
    global _icons
    if name not in _icons:
        _icons[name] = QIcon(_file_path(name))
    return _icons[name]


def _file_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), f'{name}.png')
