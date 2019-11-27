# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import os
import sys
import glob

import maya.cmds as cmds


class PluginsInfo(object):

    @property
    def root_directory(self):
        # type: () -> str
        return self.__plugins_root

    @property
    def plugin_names(self):
        # type: () -> List[str]
        return self.__plugin_names

    def __init__(self):
        plugins_root = os.path.join(
            os.path.dirname(__file__),
            '..', '..',
            'plugins'
        )
        plugins_root.replace(os.sep, '/')

        plugin_names = []
        for plugin_path in glob.glob(os.path.join(plugins_root, '*.mll')):
            plugin_name = os.path.basename(plugin_path)
            plugin_names.append(plugin_name)

        self.__plugins_root = plugins_root
        self.__plugin_names = plugin_names


def maya_plugin_paths():
    # type: () -> List[str]
    return os.environ.get('MAYA_PLUG_IN_PATH', '').split(os.pathsep)


def add_maya_plugin_path(path):
    # type: (str) -> NoReturn
    path = path.replace(os.sep, '/')
    if path not in maya_plugin_paths():
        os.environ['MAYA_PLUG_IN_PATH'] += ';{}'.format(path)


def load_plugins():
    # type: () -> NoReturn
    plugins = PluginsInfo()
    add_maya_plugin_path(plugins.root_directory)
    for name in plugins.plugin_names:
        cmds.loadPlugin(name, quiet=True)


def unload_plugins(force=False):
    # type: (bool) -> NoReturn
    plugins = PluginsInfo()
    for name in plugins.plugin_names:
        cmds.unloadPlugin(name, force=force)


