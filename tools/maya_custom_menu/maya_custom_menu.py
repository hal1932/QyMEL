import dataclasses
import abc
import json
import functools
import os

import maya.cmds as _cmds
import maya.mel as _mel


@dataclasses.dataclass
class _MenuItem:
    label: str = ''
    directory_path: str = ''
    recursive: bool = False
    menu: str = ''


@dataclasses.dataclass
class _Script:
    path: str = ''

    @staticmethod
    @abc.abstractmethod
    def extension() -> str:
        pass

    @abc.abstractmethod
    def create_menu(self, label: str, parent: _MenuItem) -> None:
        pass

    @abc.abstractmethod
    def create_option(self, label: str, parent: _MenuItem, item: _MenuItem) -> None:
        pass

    @staticmethod
    def create(file_path: str) -> '_Script':
        _, ext = os.path.splitext(file_path)
        for subcls in _Script.__subclasses__():
            if subcls.extension() == ext:
                return subcls(file_path)


class _PythonScript(_Script):

    @staticmethod
    def extension() -> str:
        return '.py'

    def create_menu(self, label: str, parent: _MenuItem) -> str:
        command = f'import qymel.core.python_script; qymel.core.python_script.PythonScript(\'{self.path}\').execute()'
        return _cmds.menuItem(parent=parent.menu, label=label, command=command, echoCommand=True)

    def create_option(self, label: str, parent: _MenuItem, item: _MenuItem) -> None:
        command = f'import qymel.core.python_script; qymel.core.python_script.PythonScript(\'{self.path}\').execute()'
        return _cmds.menuItem(item.menu, parent=parent.menu, optionBox=True, command=command, echoCommand=True)


class _MelScript(_Script):

    @staticmethod
    def extension() -> str:
        return '.mel'

    def create_menu(self, label: str, parent: _MenuItem) -> str:
        command = f'source \\"{self.path}\\"'
        return _mel.eval(f'menuItem -parent "{parent.menu}" -label "{label}" -command "{command}" -echoCommand 1')

    def create_option(self, label: str, parent: _MenuItem, item: _MenuItem) -> None:
        command = f'source \\"{self.path}\\"'
        return _mel.eval(f'menuItem -parent "{parent.menu}" -optionBox true -command "{command}" -echoCommand 1 {item.menu}')


def _create_child_menu(item: _MenuItem, *_):
    _cmds.menu(item.menu, edit=True, deleteAllItems=True)

    for child in os.listdir(item.directory_path):
        child_path = os.path.join(item.directory_path, child).replace(os.sep, '/')

        if item.recursive and os.path.isdir(child_path):
            child_item = _MenuItem(label=child, directory_path=child_path, recursive=item.recursive)
            child_item.menu = _cmds.menuItem(parent=item.menu, label=child, subMenu=True, tearOff=True)
            _cmds.menu(child_item.menu, edit=True, postMenuCommand=functools.partial(_create_child_menu, child_item))

        elif os.path.isfile(child_path):
            child_name, child_ext = os.path.splitext(child)
            if child_name.endswith('_option'):
                continue

            child_item = _MenuItem(label=child_name, directory_path=child_path, recursive=item.recursive)
            child_item.menu = _Script.create(child_path).create_menu(child, item)

            option_path = os.path.join(item.directory_path, child_name + '_option' + child_ext).replace(os.sep, '/')
            if os.path.isfile(option_path):
                _Script.create(option_path).create_option(child, item, child_item)


def _load_settings(settings_path: str) -> list[_MenuItem]:
    try:
        with open(settings_path, 'r') as f:
            items = [_MenuItem(**setting) for setting in json.load(f)]
    except Exception as e:
        _cmds.error(f'failed to load settings: {e}')
        return []

    for item in items:
        item.directory_path = os.path.expandvars(item.directory_path)
        item.directory_path = os.path.expanduser(item.directory_path)

    errors_notfound: list[str] = []

    settings_root = os.path.dirname(settings_path)
    for item in items:
        if os.path.isdir(item.directory_path):
            continue
        abs_path = os.path.join(settings_root, item.directory_path)
        if os.path.isdir(abs_path):
            item.directory_path = abs_path
        else:
            errors_notfound.append(item.directory_path)

    if errors_notfound:
        _cmds.error(f'script directory not found: {",".join(errors_notfound)}')
        return []

    return items


def create_custom_menu(settings_path: str, parent_menu: str) -> None:
    if not os.path.isfile(settings_path):
        return

    items = _load_settings(settings_path)
    if not items:
        return

    for item in items:
        item.menu = _cmds.menu(parent=parent_menu, label=item.label, tearOff=True)
        _cmds.menu(item.menu, edit=True, postMenuCommand=functools.partial(_create_child_menu, item))
