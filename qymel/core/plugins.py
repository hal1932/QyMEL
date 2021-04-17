# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import sys
import os
import glob

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2


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
            '..',
            'plugins',
            'bin',
            sys.platform,
            _cmds.about(version=True)
        )
        plugins_root.replace(os.sep, '/')

        plugin_names = []

        for plugin_path in glob.glob(os.path.join(plugins_root, '*.mll')):
            plugin_name = os.path.basename(plugin_path)
            plugin_names.append(plugin_name)

        for plugin_path in glob.glob(os.path.join(plugins_root, '*.py')):
            plugin_name = os.path.basename(plugin_path)
            if plugin_name == '__init__.py':
                continue
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
        _cmds.loadPlugin(name, quiet=True)


def unload_plugins(force=False):
    # type: (bool) -> NoReturn
    plugins = PluginsInfo()
    for name in plugins.plugin_names:
        _cmds.unloadPlugin(name, force=force)


class PluginSetup(object):
    pass


class CommandPluginSetup(PluginSetup):

    def __init__(self, name, creator=None, syntax_creator=None):
        # type: (str, Callable[[], _om2.MPxCommand], Callable[[], _om2.MSyntax]) -> NoReturn
        self.name = name
        self.creator = creator
        self.syntax_creator = syntax_creator


class NodePluginSetup(PluginSetup):

    def __init__(self, name, type_id, creator=None, initializer=None, node_type=_om2.MPxNode.kDependNode, classification='utility/general'):
        # type: (str, _om2.MTypeId, Callable[[], _om2.MPxNode], Callable[[], None], int, str) -> NoReturn
        self.name = name
        self.type_id = type_id
        self.creator = creator
        self.node_type = node_type
        self.classification = classification

        if initializer is None:
            def _(): pass
            self.initializer = _
        else:
            self.initializer = initializer


def setup_plugin(plugin_globals, setups, vendor='Unknown', version='Unknown', api_version='Any'):
    # type: (Dict[str, Any], Iterable[PluginSetup], str, str, str) -> NoReturn
    def _maya_use_new_api():
        pass

    def _initialize_plugin(mobj):
        # type: (_om2.MObject) -> NoReturn
        mplugin = _om2.MFnPlugin(mobj, vendor, version, api_version)

        for setup in setups:
            if isinstance(setup, CommandPluginSetup):
                if setup.syntax_creator is None:
                    mplugin.registerCommand(setup.name, setup.creator)
                else:
                    mplugin.registerCommand(setup.name, setup.creator, setup.syntax_creator)

            elif isinstance(setup, NodePluginSetup):
                mplugin.registerNode(setup.name, setup.type_id, setup.creator, setup.initializer, setup.node_type, setup.classification)

    def _uninitialize_plugin(mobj):
        # type: (_om2.MObject) -> NoReturn
        mplugin = _om2.MFnPlugin(mobj)
        for setup in setups:
            if isinstance(setup, CommandPluginSetup):
                mplugin.deregisterCommand(setup.name)
            elif isinstance(setup, NodePluginSetup):
                mplugin.deregisterNode(setup.type_id)

    plugin_globals['maya_useNewAPI'] = _maya_use_new_api
    plugin_globals['initializePlugin'] = _initialize_plugin
    plugin_globals['uninitializePlugin'] = _uninitialize_plugin


class SyntaxFlag(object):

    @property
    def is_set(self):
        # type: () -> bool
        return self._is_set

    @property
    def value(self):
        # type: () -> Any
        return self._value if self.is_set else None

    @property
    def is_true(self):
        # type: () -> bool
        return self.is_set and self.value

    def __init__(self, short_name, long_name, value_type, multi_use=False, help=None):
        # type: (str, str, int, bool, str) -> NoReturn
        self.short_name = short_name
        self.long_name = long_name
        self.value_type = value_type
        self.is_multi_use = multi_use
        self.help = help

        self._value = None
        self._is_set = False

    def get(self, default_value=None):
        # type: (Any) -> Any
        if self._is_set:
            return self.value
        return default_value


class FlagsDefinition(object):

    def __init__(self):
        pass

    def flags(self):
        # type: () -> Iterable[SyntaxFlag]
        return self.__dict__.values()

    def apply_to(self, syntax):
        # type: (_om2.MSyntax) -> NoReturn
        for flag in self.flags():
            syntax.addFlag(flag.short_name, flag.long_name, flag.value_type)
            if flag.is_multi_use:
                syntax.makeFlagMultiUse(flag.short_name)


class ArgDatabase(_om2.MArgDatabase):

    def __init__(self, syntax, args):
        # type: (_om2.MSyntax, _om2.MArgList) -> NoReturn
        super(ArgDatabase, self).__init__(syntax, args)

    def parse_flags(self, flags_definition_cls):
        # type: (type) -> FlagsDefinition
        definition = flags_definition_cls()

        for flag in definition.flags():
            flag._is_set = self.isFlagSet(flag.short_name)
            if flag._is_set:
                if flag.is_multi_use:
                    for i in range(self.numberOfFlagUses(flag.short_name)):
                        args = self.getFlagArgumentList(flag.short_name, i)
                        flag._value = self.__get_flag_values(flag, args)
                else:
                    flag._value = self.__get_flag_value(flag)

        return definition

    def is_flag_true(self, flag, index=0):
        # type: (str, int) -> bool
        if not self.isFlagSet(flag):
            return False
        return self.flagArgumentBool(flag, index)

    def flag_string(self, flag, index=0, default_value=None):
        # type: (str, int, str) -> str
        if not self.isFlagSet(flag):
            return default_value

        # multi-useのときだけじゃなく、Noneが与えられたときもRuntimeErrorになる
        try:
            return self.flagArgumentString(flag, index)
        except RuntimeError:
            return None

    def __get_flag_value(self, flag):
        # type: (SyntaxFlag) -> Any
        try:
            if flag.value_type == _om2.MSyntax.kBoolean:
                return self.flagArgumentBool(flag.short_name, 0)
            if flag.value_type == _om2.MSyntax.kString:
                return self.flagArgumentString(flag.short_name, 0)

        except RuntimeError:
            return None

    def __get_flag_values(self, flag, args):
        # type: (SyntaxFlag, _om2.MArgList) -> List[Any]
        try:
            if flag.value_type == _om2.MSyntax.kBoolean:
                return [args.asBool(i) for i in range(len(args))]
            if flag.value_type == _om2.MSyntax.kString:
                return [args.asString(i) for i in range(len(args))]

        except RuntimeError:
            return None
