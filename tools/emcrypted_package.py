# coding: utf-8
from typing import *
import sys
import os
import io
import glob
import zipfile
import types
import abc
import dataclasses
import json
import base64
import importlib
import importlib.abc
import importlib.machinery
import importlib.util


class _PackageImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):

    @abc.abstractmethod
    def find_spec(self, fullname: str, path: Optional[str] = None, target: Optional[types.ModuleType] = None) -> Optional[importlib.machinery.ModuleSpec]:
        raise NotImplementedError()

    @abc.abstractmethod    
    def exec_module(self, module: types.ModuleType):
        raise NotImplementedError()

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> Optional[types.ModuleType]:
        # print(f'create_module: {spec.name}')
        return None  # モジュール本体はexec_module内で生成するからここではNoneを返して空のモジュールを作成する


class _EncryptedImporter(_PackageImporter):

    def __init__(self, module_script_dict: Dict[str, str], module_abs_paths_dict: Dict[str, str]):
        self.__module_script_dict = module_script_dict
        self.__module_abs_paths_dict = module_abs_paths_dict

    def find_spec(self, fullname: str, _1, _2) -> Optional[importlib.machinery.ModuleSpec]:
        loader = self
        origin = self.__module_abs_paths_dict.get(fullname)
        if not origin:
            origin = self.__module_abs_paths_dict.get(f'{fullname}.__init__')
        is_package = f'{fullname}.__init__' in self.__module_script_dict.keys()
        # print(f'find_spec: {fullname}, {path}, {target}, is_package={is_package}')
        spec = importlib.machinery.ModuleSpec(fullname, loader, origin=origin, is_package=is_package)
        spec._set_fileattr = True
        return spec

    def exec_module(self, module: types.ModuleType):
        # print(f'exec_module: {module.__name__}')
        module_name = module.__name__

        source = self.__module_script_dict.get(module_name)
        if not source:
            module_name = f'{module_name}.__init__'
            source = self.__module_script_dict.get(module_name)
        if not source:
            return

        exec(source, module.__dict__)


class TextEncrypter(object):

    @property
    def encoding(self) -> str:
        return self.__encoding

    def __init__(self, encoding='utf8'):
        self.__encoding = encoding

    @abc.abstractmethod
    def encrypt(self, text: str) -> bytes:
        raise NotImplementedError()

    @abc.abstractmethod
    def decrypt(self, data: bytes) -> str:
        raise NotImplementedError()


class Base85TextEncrypter(TextEncrypter):

    def __init__(self, encoding='utf8'):
        super().__init__(encoding)

    def encrypt(self, text: str) -> bytes:
        return base64.b85encode(text.encode(self.encoding))

    def decrypt(self, data: bytes) -> str:
        return base64.b85decode(data).decode(self.encoding)


@dataclasses.dataclass
class ScriptItem:
    path: str
    source: bytes


class ScriptPackager(object):

    @abc.abstractmethod
    def compose(self, scripts: Sequence[ScriptItem]) -> bytes:
        raise NotImplementedError()

    @abc.abstractmethod
    def decompose(self, package: bytes) -> Sequence[ScriptItem]:
        raise NotImplementedError()


class ZipScriptPackager(ScriptPackager):

    def compose(self, scripts: Sequence[ScriptItem]) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zip:
            for script in scripts:
                zip.writestr(script.path, script.source)
        return buffer.getvalue()

    def decompose(self, package: bytes) -> Sequence[ScriptItem]:
        scripts: List[ScriptItem] = []
        stream = io.BytesIO(package)
        with zipfile.ZipFile(stream, 'r') as zip:
            for name in zip.namelist():
                with zip.open(name) as f:
                    source = f.read()
                scripts.append(ScriptItem(name, source))
        return scripts


class ScriptSelector(object):

    @abc.abstractmethod
    def select(self, directory: str) -> Sequence[str]:
        raise NotImplementedError()


class PythonScriptSelector(ScriptSelector):

    def select(self, directory: str) -> Sequence[str]:
        return glob.glob(f'{directory}/*.py')


@dataclasses.dataclass
class _PackageData:
    scripts: Sequence[ScriptItem]
    module_abs_paths: Dict[str, str]


class EncryptedPackage(object):

    def __init__(self, packager: ScriptPackager, encrypter: TextEncrypter):
        self.__packager = packager
        self.__encrypter = encrypter

    def save(self, package_dest_path: str, package_root_dir: str, selector: ScriptSelector) -> bool:
        script_paths = self.__enumerate_scripts(package_root_dir, selector)
        package = self.__create_package(script_paths, package_root_dir)
        package_buffer = self.__compose_package(package)

        with open(package_dest_path, 'wb') as f:
            f.write(package_buffer)
        return os.path.isfile(package_dest_path)

    def load(self, package_path: str) -> List[str]:
        with open(package_path, 'rb') as f:
            package_buffer = f.read()
        package = self.__decompose_package(package_buffer)

        importer = self.__create_importer(package)
        sys.meta_path.append(importer)

        return list(package.module_abs_paths.keys())
    
    def __enumerate_scripts(self, package_root_dir: str, selector: ScriptSelector) -> List[str]:
        script_dirs = [package_root_dir]
        for root, dirs, _ in os.walk(package_root_dir):
            script_dirs.extend(os.path.join(root, dir) for dir in dirs)

        script_paths: Set[str] = set()
        for script_dir in script_dirs:
            for script_path in selector.select(script_dir):
                script_paths.add(os.path.normpath(script_path))
        
        return list(script_paths)
    
    def __create_package(self, script_paths: List[str], package_root_dir: str) -> _PackageData:
        scripts: List[ScriptItem] = []
        module_abs_paths: Dict[str, str] = {}

        package_parent_dir = os.path.dirname(package_root_dir)
        for abs_path in script_paths:
            rel_path = os.path.relpath(abs_path, package_parent_dir).replace(os.sep, '/')
            module_name = os.path.splitext(rel_path)[0].replace('/', '.')
            module_abs_paths[module_name] = os.path.abspath(abs_path)
            with open(abs_path, 'r', encoding=self.__encrypter.encoding) as f:
                source = self.__encrypter.encrypt(f.read())
                script = ScriptItem(rel_path, source)
                scripts.append(script)
        
        return _PackageData(scripts, module_abs_paths)
    
    def __compose_package(self, package: _PackageData) -> bytes:
        package_buffer = self.__packager.compose(package.scripts)
        package_size = len(package_buffer)
        paths_buffer = self.__encrypter.encrypt(json.dumps(package.module_abs_paths))

        stream = io.BytesIO()
        stream.write(package_size.to_bytes(8, 'little'))
        stream.write(package_buffer)
        stream.write(paths_buffer)

        return stream.getvalue()

    def __decompose_package(self, package_buffer: bytes) -> _PackageData:
        stream = io.BytesIO(package_buffer)
        package_size = int.from_bytes(stream.read(8), 'little')
        package_buffer = stream.read(package_size)
        paths_buffer = stream.read()

        scripts = self.__packager.decompose(package_buffer)
        module_abs_paths = json.loads(self.__encrypter.decrypt(paths_buffer))

        return _PackageData(scripts, module_abs_paths)

    def __create_importer(self, package: _PackageData) -> _PackageImporter:
        module_scripts_dict: Dict[str, str] = {}
        for script in package.scripts:
            module_name = os.path.splitext(script.path)[0].replace('/', '.')
            module_scripts_dict[module_name] = self.__encrypter.decrypt(script.source)
        return _EncryptedImporter(module_scripts_dict, package.module_abs_paths)


if __name__ == '__main__':
    def _test():
        package_root_dir = os.path.join(os.path.dirname(__file__), '..', 'qymel')
        package_dest_path = os.path.join(os.path.dirname(__file__), 'qymel.pkg')

        m = EncryptedPackage(ZipScriptPackager(), Base85TextEncrypter())
        if not m.save(package_dest_path, package_root_dir, PythonScriptSelector()):
            print('failed to save')
            return -1

        m = EncryptedPackage(ZipScriptPackager(), Base85TextEncrypter())
        modules = m.load(package_dest_path)
        print(modules)

        from qymel.core.force_reload import force_reload
        import qymel.core as qm
        force_reload(qm)

        return 0

    sys.exit(_test())
