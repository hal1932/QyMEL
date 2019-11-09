# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import os

import maya.cmds as cmds
import maya.api.OpenMaya as om2

from . import nodetypes as _nodetypes
from ..internal import graphs as _graphs


class _DictEntry(object):

    @property
    def key(self):
        # type: () -> str
        return self.__key

    @property
    def value(self):
        # type: () -> str
        return self.__value

    def __init__(self, key, value):
        # type: (str, str) -> NoReturn
        self.__key = key
        self.__value = value

    def __repr__(self):
        return "{}('{}', '{}')".format(self.__class__.__name__, self.key, self.value)

    def _update(self, new_value):
        # type: (str) -> NoReturn
        self.__value = new_value

    def _remove(self):
        # type: () -> NoReturn
        self._update(None)


class FileInfo(_DictEntry):

    def __init__(self, key, value):
        # type: (str, str) -> NoReturn
        super(FileInfo, self).__init__(key, value)

    def update(self, new_value):
        # type: (str) -> NoReturn
        cmds.fileInfo(self.key, new_value)
        self._update(new_value)

    def remove(self):
        # type: () -> NoReturn
        cmds.fileInfo(self.key, remove=True)
        self._remove()


class Scene(object):

    @staticmethod
    def name():
        # type: () -> str
        return cmds.file(query=True, sceneName=True)

    @staticmethod
    def normalize_path(file_path):
        # type: (str) -> str
        return file_path.replace(os.sep, '/')

    @staticmethod
    def new_file(force=False):
        # type: (bool) -> str
        return cmds.file(new=True, force=force)

    @staticmethod
    def open_file(file_path, **kwargs):
        # type: (str, Any) -> Union[str, List[_nodetypes.DependNode]]
        file_path = Scene.normalize_path(file_path)
        kwargs['open'] = True
        result = cmds.file(file_path, **kwargs)

        if 'returnNewNodes' in kwargs or 'rnn' in kwargs:
            tmp_mfn = om2.MFnDependencyNode()
            return [_graphs.eval_node(node, tmp_mfn) for node in result]

        return result

    @staticmethod
    def rename_file(new_file_path):
        # type: (str) -> str
        _, ext = os.path.split(new_file_path)
        file_type = FileTranslator.find_by_extension(ext)
        if file_type is not None:
            cmds.file(type=file_type)

        new_file_path = Scene.normalize_path(new_file_path)
        return cmds.file(rename=new_file_path)

    @staticmethod
    def save_file(file_path=None, file_type=None, force=False):
        # type: (str, str, bool) -> str
        if file_path is not None:
            Scene.rename_file(file_path)

        kwargs = {'save': True, 'force': force}
        if file_type is not None:
            kwargs['type'] = file_type

        return cmds.file(**kwargs)

    @staticmethod
    def is_mofieied():
        # type: () -> bool
        return cmds.file(query=True, modified=True)

    @staticmethod
    def import_file(file_path, **kwargs):
        # type: (str, Any) -> Union[str, List[_nodetypes.DependNode]]
        file_path = Scene.normalize_path(file_path)
        kwargs['i'] = True
        result = cmds.file(file_path, **kwargs)

        if 'returnNewNodes' in kwargs or 'rnn' in kwargs:
            tmp_mfn = om2.MFnDependencyNode()
            return [_graphs.eval_node(node, tmp_mfn) for node in result]

        return file_path

    @staticmethod
    def reference_file(file_path, **kwargs):
        # type: (str, Any) -> Union[_nodetypes.FileReference, List[_nodetypes.DependNode]]
        file_path = Scene.normalize_path(file_path)
        kwargs['reference'] = True
        result = cmds.file(file_path, **kwargs)

        if 'returnNewNodes' in kwargs or 'rnn' in kwargs:
            tmp_mfn = om2.MFnDependencyNode()
            return [_graphs.eval_node(node, tmp_mfn) for node in result]

        node = cmds.referenceQuery(result, referenceNode=True)
        return _nodetypes.FileReference(node)

    @staticmethod
    def file_infos():
        # type: () -> List[FileInfo]
        infos = cmds.fileInfo(query=True)
        result = []  # type: List[FileInfo]
        for i in range(len(infos) / 2):
            key = infos[i * 2]
            value = infos[i * 2 + 1]
            result.append(FileInfo(key, value))
        return result

    @staticmethod
    def file_info(key, default_value=None):
        # type: (str, str) -> FileInfo
        value = cmds.fileInfo(key, query=True)
        if len(value) == 0:
            value = default_value
        else:
            value = value[0]
        return FileInfo(key, value)


class FileRule(_DictEntry):

    def __init__(self, key, value):
        # type: (str, str) -> NoReturn
        super(FileRule, self).__init__(key, value)

    def update(self, new_value):
        # type: (str) -> FileRule
        cmds.workspace(fileRule=(self.key, new_value))
        self._update(new_value)

    def remove(self):
        # type: () -> NoReturn
        cmds.workspace(removeFileRuleEntry=self.key)
        self._remove()


class DictVariable(_DictEntry):

    def __init__(self, key, value):
        # type: (str, str) -> NoReturn
        super(DictVariable, self).__init__(key, value)

    def update(self, new_value):
        # type: (str) -> FileRule
        cmds.workspace(variable=(self.key, new_value))
        self._update(new_value)

    def remove(self):
        # type: () -> NoReturn
        cmds.workspace(removeVariableEntry=self.key)
        self._remove()


class Workspace(object):

    @staticmethod
    def create(directory_path):
        # type: (str) -> NoReturn
        return cmds.workspace(directory_path, newWorkspace=True)

    @staticmethod
    def root_directory():
        # type: () -> str
        return cmds.workspace(query=True, rootDirectory=True)

    @staticmethod
    def open(directory_path):
        # type: (str) -> NoReturn
        cmds.workspace(directory_path, openWorkspace=True)

    @staticmethod
    def save():
        # type: () -> NoReturn
        cmds.workspace(saveWorkspace=True)

    @staticmethod
    def update():
        # type: () -> NoReturn
        cmds.workspace(update=True)

    @staticmethod
    def file_rules():
        # type: () -> List[FileRule]
        return Workspace.__entries(FileRule, 'fileRule')

    @staticmethod
    def file_rule(key, default_value=None):
        # type: (str, str) -> FileRule
        return Workspace.__entry(FileRule, 'fileRule', key, default_value)

    @staticmethod
    def variables():
        # type: () -> List[DictVariable]
        return Workspace.__entries(DictVariable, 'variable')

    @staticmethod
    def variable(key, default_value=None):
        # type: (str, str) -> DictVariable
        return Workspace.__entry(DictVariable, 'variable', key, default_value)

    @staticmethod
    def expand_name(path):
        # type: (str) -> str
        return cmds.workspace(expandName=path)

    @staticmethod
    def __entries(cls, entry):
        # type: (type, str) -> List[cls]
        kwargs = {'query': True, entry: True}
        entries = cmds.workspace(kwargs)
        result = []  # type: List[cls]
        for i in range(len(entries) / 2):
            key = entries[i * 2]
            value = entries[i * 2 + 1]
            result.append(cls(key, value))
        return result

    @staticmethod
    def __entry(cls, entry, key, default_value):
        # type: (type, str, str, str) -> cls
        kwargs = {'{}Entry'.format(entry): key}
        value = cmds.workspace(kwargs) or default_value
        return cls(key, value)


class FileTranslator(object):

    @staticmethod
    def ls():
        return [FileTranslator(name) for name in cmds.translator(query=True, list=True)]

    @staticmethod
    def find_by_extension(extension):
        # type: (str) -> FileTranslator
        extension = extension.lstrip('.')
        for name in cmds.translator(query=True, list=True):
            ext = cmds.translator(query=True, extension=True)
            if ext == extension:
                return FileTranslator(name)
        return None

    @property
    def name(self):
        # type: () -> str
        return self.__name

    @property
    def extension(self):
        # type: () -> bool
        return cmds.translator(self.name, query=True, extension=True)

    @property
    def can_read(self):
        # type: () -> bool
        return cmds.translator(self.name, query=True, readSupport=True)

    @property
    def can_write(self):
        # type: () -> bool
        return cmds.translator(self.name, query=True, writeSupport=True)

    def __init__(self, name):
        # type: (str) -> NoReturn
        self.__name = name

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        return "{}('{}')".format(self.__class__.__name__, self.name)


class Namespace(object):

    root = None  # type: Namespace

    @staticmethod
    def ls(recurse=False):
        # type: (bool) -> List[Namespace]
        return [Namespace(ns) for ns in om2.MNamespace.getNamespaces(recurse=recurse)]

    @staticmethod
    def create(name, parent=None):
        # type: (str, Namespace) -> Namespace
        kwargs = {'addNamespace': name}
        if parent is not None:
            kwargs['parent'] = parent.mel_object
        ns = cmds.namespace(kwargs)
        return Namespace(ns)

    @staticmethod
    def current():
        # type: () -> Namespace
        ns = cmds.namespace(currentNamespace=True)
        return Namespace(ns)

    @property
    def mel_object(self):
        # type: () -> str
        return self.__abs_name

    @property
    def exists(self):
        # type: () -> bool
        return om2.MNamespace.namespaceExists(self.__abs_name)

    @property
    def name(self):
        # type: () -> str
        return om2.MNamespace.stripNamespaceFromName(self.__abs_name)

    @property
    def abs_name(self):
        # type: () -> str
        return self.__abs_name

    def __init__(self, name):
        # type: (str) -> NoReturn
        self.__abs_name = om2.MNamespace.makeNamepathAbsolute(name)

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        return "{}('{}')".format(self.__class__.__name__, self.name)

    def set_current(self):
        # type: () -> NoReturn
        cmds.namespace(setNamespace=self.mel_object)

    def rename(self, new_name, force=False):
        # type: (str, bool) -> NoReturn
        pass

    def delete(self, delete_contents=False, recursive=False):
        # type: (bool, bool) -> NoReturn
        if recursive:
            for child in self.children():
                child.delete(delete_contents, recursive)
        cmds.namespace(self.mel_object, deleteNamespace=True, deleteContents=delete_contents)
        self.__abs_name = None

    def add(self, node):
        # type: (_nodetypes.DependNode) -> NoReturn
        node.rename('{}:{}'.format(self.name, node.full_name.lstrip('|')))

    def extend(self, nodes):
        # type: (Iterable[_nodetypes.DependNode]) -> NoReturn
        for node in nodes:
            self.add(node)

    def move_contents(self, destination):
        # type: (Namespace) -> NoReturn
        cmds.namespace(moveNamespace=(self.mel_object, destination.mel_object))

    def nodes(self, internal=False):
        # type: (bool) -> List[_nodetypes.DependNode]
        node_names = cmds.namespaceInfo(self.mel_object, listOnlyDependencyNodes=True, internal=internal)
        if node_names is None:
            return []

        tmp_mfn = om2.MFnDependencyNode()
        return [_graphs.eval_node(name, tmp_mfn) for name in node_names]

    def children(self):
        # type: () -> List[Namespace]
        ns_names = cmds.namespaceInfo(self.mel_object, listOnlyNamespaces=True)
        if ns_names is None:
            return []

        return [Namespace(name) for name in ns_names]


Namespace.root = Namespace(om2.MNamespace.rootNamespace())
