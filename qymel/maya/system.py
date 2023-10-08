# coding: utf-8
from typing import *
import os

import maya.cmds as _cmds
import maya.api.OpenMaya as _om2

from . import nodetypes as _nodetypes
from .internal import graphs as _graphs


class _DictEntry(object):

    @property
    def key(self) -> str:
        return self.__key

    @property
    def value(self) -> str:
        return self.__value

    def __init__(self, key: str, value: str) -> None:
        self.__key = key
        self.__value = value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.key}', '{self.value}')"

    def _update(self, new_value: Optional[str]) -> None:
        self.__value = new_value

    def _remove(self) -> None:
        self._update(None)


class FileInfo(_DictEntry):

    @staticmethod
    def ls() -> List['FileInfo']:
        infos = []
        flatten_items = _cmds.fileInfo(query=True)
        for i in range(0, len(flatten_items), 2):
            key = flatten_items[i]
            value = flatten_items[i + 1]
            infos.append(FileInfo(key, value))
        return infos

    @staticmethod
    def query(key: str) -> Optional['FileInfo']:
        value = _cmds.fileInfo(key, query=True)
        if len(value) == 0:
            return None
        return FileInfo(key, value[0])

    @staticmethod
    def create(key: str, value: str) -> 'FileInfo':
        info = FileInfo(key, '')
        info.update(value)
        return info

    def __init__(self, key: str, value: str) -> None:
        super(FileInfo, self).__init__(key, value)

    def update(self, new_value: str) -> None:
        _cmds.fileInfo(self.key, new_value)
        self._update(new_value)

    def remove(self) -> None:
        _cmds.fileInfo(remove=self.key)
        self._remove()


class Scene(object):

    @staticmethod
    def name() -> str:
        return _cmds.file(query=True, sceneName=True, shortName=True)

    @staticmethod
    def path() -> str:
        return _cmds.file(query=True, sceneName=True)

    @staticmethod
    def normalize_path(file_path: str) -> str:
        return file_path.replace(os.sep, '/')

    @staticmethod
    def new(force: bool = False) -> str:
        return _cmds.file(new=True, force=force)

    @staticmethod
    def open(file_path: str, **kwargs) -> Union[str, List[_nodetypes.DependNode]]:
        file_path = Scene.normalize_path(file_path)
        kwargs['open'] = True
        result = _cmds.file(file_path, **kwargs)

        if 'returnNewNodes' in kwargs or 'rnn' in kwargs:
            tmp_mfn = _om2.MFnDependencyNode()
            return [_graphs.eval_node(node, tmp_mfn) for node in result]

        return result

    @staticmethod
    def rename(new_name: str) -> str:
        _, ext = Scene.normalize_path(new_name)
        file_type = FileTranslator.find_by_extension(ext)
        if file_type is not None:
            _cmds.file(type=file_type.name)
        return _cmds.file(rename=new_name)

    @staticmethod
    def save(file_path: Optional[str] = None, file_type: Optional[str] = None, force: Optional[bool] = False) -> str:
        file_path = Scene.normalize_path(file_path)

        if file_path is not None:
            Scene.rename(file_path)

        kwargs = {'save': True, 'force': force}
        if file_type is not None:
            kwargs['type'] = file_type

        return _cmds.file(**kwargs)

    @staticmethod
    def is_mofieied() -> bool:
        return _cmds.file(query=True, modified=True)

    @staticmethod
    def set_modified() -> None:
        _cmds.file(modified=True)

    @staticmethod
    def import_file(file_path: str, **kwargs) -> Union[str, List[_nodetypes.DependNode]]:
        file_path = Scene.normalize_path(file_path)
        kwargs['i'] = True
        result = _cmds.file(file_path, **kwargs)

        if 'returnNewNodes' in kwargs or 'rnn' in kwargs:
            tmp_mfn = _om2.MFnDependencyNode()
            return [_graphs.eval_node(node, tmp_mfn) for node in result]

        return file_path

    @staticmethod
    def reference_file(file_path: str, **kwargs) -> Union[_nodetypes.FileReference, List[_nodetypes.DependNode]]:
        file_path = Scene.normalize_path(file_path)
        kwargs['reference'] = True
        result = _cmds.file(file_path, **kwargs)

        if 'returnNewNodes' in kwargs or 'rnn' in kwargs:
            tmp_mfn = _om2.MFnDependencyNode()
            return [_graphs.eval_node(node, tmp_mfn) for node in result]

        node = _cmds.referenceQuery(result, referenceNode=True)
        return _nodetypes.FileReference(node)

    @staticmethod
    def file_infos() -> List[FileInfo]:
        infos = _cmds.fileInfo(query=True)
        result = []  # type: List[FileInfo]
        for i in range(0, len(infos), 2):
            key = infos[i]
            value = infos[i + 1]
            result.append(FileInfo(key, value))
        return result

    @staticmethod
    def file_info(key: str, default_value: Optional[str] = None) -> FileInfo:
        value = _cmds.fileInfo(key, query=True)
        if len(value) == 0:
            value = default_value
        else:
            value = value[0]
        return FileInfo(key, value)


class FileRule(_DictEntry):

    @staticmethod
    def ls() -> List['FileRule']:
        rules = []
        flatten_items = _cmds.workspace(query=True, fileRule=True)
        for i in range(0, len(flatten_items), 2):
            key = flatten_items[i]
            value = flatten_items[i + 1]
            rules.append(FileRule(key, value))
        return rules

    @staticmethod
    def query(key: str) -> Optional['FileRule']:
        value = _cmds.workspace(fileRuleEntry=key)
        if len(value) == 0:
            return None
        return FileRule(key, value)

    @staticmethod
    def create(key: str, value: str) -> 'FileRule':
        rule = FileRule(key, '')
        rule.update(value)
        return rule

    def __init__(self, key: str, value: str) -> None:
        super(FileRule, self).__init__(key, value)

    def update(self, new_value: str) -> None:
        _cmds.workspace(fileRule=(self.key, new_value))
        self._update(new_value)

    def remove(self) -> None:
        _cmds.workspace(removeFileRuleEntry=self.key)
        self._remove()


class WorkspaceVariable(_DictEntry):

    @staticmethod
    def ls() -> List['WorkspaceVariable']:
        rules = []
        flatten_items = _cmds.workspace(query=True, variable=True)
        for i in range(0, len(flatten_items), 2):
            key = flatten_items[i]
            value = flatten_items[i + 1]
            rules.append(WorkspaceVariable(key, value))
        return rules

    @staticmethod
    def query(key: str) -> Optional['WorkspaceVariable']:
        value = _cmds.workspace(variableEntry=key)
        if len(value) == 0:
            return None
        return WorkspaceVariable(key, value)

    @staticmethod
    def create(key: str, value: str) -> 'WorkspaceVariable':
        rule = WorkspaceVariable(key, '')
        rule.update(value)
        return rule

    def __init__(self, key: str, value: str) -> None:
        super(WorkspaceVariable, self).__init__(key, value)

    def update(self, new_value: str) -> None:
        _cmds.workspace(variable=(self.key, new_value))
        self._update(new_value)

    def remove(self) -> None:
        _cmds.workspace(removeVariableEntry=self.key)
        self._remove()


class Workspace(object):

    @staticmethod
    def create(directory_path: str) -> str:
        return _cmds.workspace(directory_path, newWorkspace=True)

    @staticmethod
    def root_directory() -> str:
        return _cmds.workspace(query=True, rootDirectory=True)

    @staticmethod
    def open(directory_path: str) -> None:
        _cmds.workspace(directory_path, openWorkspace=True)

    @staticmethod
    def save() -> None:
        _cmds.workspace(saveWorkspace=True)

    @staticmethod
    def update() -> None:
        _cmds.workspace(update=True)

    @staticmethod
    def file_rules() -> List[FileRule]:
        return Workspace.__entries(FileRule, 'fileRule')

    @staticmethod
    def file_rule(key: str, default_value: Optional[str] = None) -> FileRule:
        return Workspace.__entry(FileRule, 'fileRule', key, default_value)

    @staticmethod
    def variables() -> List[WorkspaceVariable]:
        return Workspace.__entries(WorkspaceVariable, 'variable')

    @staticmethod
    def variable(key: str, default_value: Optional[str] = None) -> WorkspaceVariable:
        return Workspace.__entry(WorkspaceVariable, 'variable', key, default_value)

    @staticmethod
    def expand_name(path: str) -> str:
        return _cmds.workspace(expandName=path)

    @staticmethod
    def path_by_file_rule(rule_key: str) -> Optional[str]:
        rule = Workspace.file_rule(rule_key)
        if rule is None:
            return None
        return os.path.join(
            Workspace.root_directory(),
            rule.value
        ).replace(os.sep, '/')

    @staticmethod
    def __entries(cls: Type[_DictEntry], entry: str) -> List[Any]:
        kwargs = {'query': True, entry: True}
        entries = _cmds.workspace(**kwargs)
        result = []
        for i in range(0, len(entries), 2):
            key = entries[i]
            value = entries[i + 1]
            result.append(cls(key, value))
        return result

    @staticmethod
    def __entry(cls: Type[_DictEntry], entry: str, key: str, default_value: Optional[str]):
        kwargs = {'{}Entry'.format(entry): key}
        value = _cmds.workspace(**kwargs) or default_value
        return cls(key, value)


class FileTranslator(object):

    @staticmethod
    def ls() -> List['FileTranslator']:
        return [FileTranslator(name) for name in _cmds.translator(query=True, list=True)]

    @staticmethod
    def find_by_extension(extension: str) -> Optional['FileTranslator']:
        extension = extension.lstrip('.')
        for name in _cmds.translator(query=True, list=True):
            ext = _cmds.translator(name, query=True, extension=True)
            if ext == extension:
                return FileTranslator(name)
        return None

    @property
    def name(self) -> str:
        return self.__name

    @property
    def extension(self) -> str:
        return _cmds.translator(self.name, query=True, extension=True)

    @property
    def can_read(self) -> bool:
        return _cmds.translator(self.name, query=True, readSupport=True)

    @property
    def can_write(self) -> bool:
        return _cmds.translator(self.name, query=True, writeSupport=True)

    def __init__(self, name: str) -> None:
        self.__name = name

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self.name}')"


class Namespace(object):

    root: 'Namespace' = None

    @staticmethod
    def ls(recurse: bool = False) -> List['Namespace']:
        return [Namespace(ns) for ns in _om2.MNamespace.getNamespaces(recurse=recurse)]

    @staticmethod
    def create(name: str, parent: Optional['Namespace'] = None) -> 'Namespace':
        kwargs = {'addNamespace': name}
        if parent is not None:
            kwargs['parent'] = parent.mel_object
        else:
            kwargs['parent'] = Namespace.root.mel_object
        ns = _cmds.namespace(**kwargs)
        return Namespace(ns)

    @staticmethod
    def current() -> 'Namespace':
        ns = _cmds.namespace(currentNamespace=True)
        return Namespace(ns)

    @property
    def mel_object(self) -> str:
        return self.__abs_name

    @property
    def exists(self) -> bool:
        return _om2.MNamespace.namespaceExists(self.__abs_name)

    @property
    def name(self) -> str:
        return _om2.MNamespace.stripNamespaceFromName(self.__abs_name)

    @property
    def abs_name(self) -> str:
        return self.__abs_name

    def __init__(self, name: str) -> None:
       self.__abs_name = _om2.MNamespace.makeNamepathAbsolute(name)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return "{}('{}')".format(self.__class__.__name__, self.name)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            if not _om2.MNamespace.namespaceExists(other):
                return False
            other = Namespace(other)
        if isinstance(other, Namespace):
            return self.mel_object == other.mel_object
        return False

    def set_current(self) -> None:
        _cmds.namespace(setNamespace=self.mel_object)

    def rename(self, new_name: str) -> None:
        _cmds.namespace(rename=[self.mel_object, new_name])

    def delete(self, delete_contents: bool = False, recursive: bool = False) -> None:
        if recursive:
            for child in self.children():
                child.delete(delete_contents, recursive)
        _cmds.namespace(removeNamespace=self.mel_object, deleteNamespaceContent=delete_contents)
        self.__abs_name = None

    def add(self, node: _nodetypes.DependNode) -> None:
        node.rename('{}:{}'.format(self.name, node.full_name.lstrip('|')))

    def extend(self, nodes: Iterable[_nodetypes.DependNode]) -> None:
        for node in nodes:
            self.add(node)

    def move_contents(self, destination: 'Namespace') -> None:
        _cmds.namespace(moveNamespace=(self.mel_object, destination.mel_object))

    def nodes(self, internal: bool = False) -> List[_nodetypes.DependNode]:
        node_names = _cmds.namespaceInfo(self.mel_object, listOnlyDependencyNodes=True, internal=internal)
        if node_names is None:
            return []

        tmp_mfn = _om2.MFnDependencyNode()
        return [_graphs.eval_node(name, tmp_mfn) for name in node_names]

    def children(self) -> List['Namespace']:
        ns_names = _cmds.namespaceInfo(self.mel_object, listOnlyNamespaces=True)
        if ns_names is None:
            return []

        return [Namespace(name) for name in ns_names]


Namespace.root = Namespace(_om2.MNamespace.rootNamespace())
