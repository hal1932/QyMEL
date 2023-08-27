# coding: utf-8
from typing import *
import os
from .pyside_module import *


def get_or_create(project_name: str, settings_name: str) -> QSettings:
    dir = os.path.join(os.environ['APPDATA'], project_name)
    if not os.path.isdir(dir):
        os.makedirs(dir)
    path = os.path.join(dir, settings_name)
    return QSettings(path, QSettings.IniFormat)
