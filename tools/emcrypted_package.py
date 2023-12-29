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


class _EncryptedImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):

    def __init__(self, module_script_dict: Dict[str, str], module_abs_paths_dict: Dict[str, str]):
        self.__module_script_dict = module_script_dict
        self.__module_abs_paths_dict = module_abs_paths_dict

    def find_spec(self, fullname: str, path: Optional[str] = None, target: Optional[types.ModuleType] = None) -> Optional[importlib.machinery.ModuleSpec]:
        loader = self
        origin = self.__module_abs_paths_dict.get(fullname)
        if not origin:
            origin = self.__module_abs_paths_dict.get(f'{fullname}.__init__')
        is_package = f'{fullname}.__init__' in self.__module_script_dict.keys()
        # print(f'find_spec: {fullname}, {path}, {target}, is_package={is_package}')
        spec = importlib.machinery.ModuleSpec(fullname, loader, origin=origin, is_package=is_package)
        spec._set_fileattr = True
        return spec

    def create_module(self, spec: importlib.machinery.ModuleSpec) -> Optional[types.ModuleType]:
        # print(f'create_module: {spec.name}')
        return None  # モジュール本体はexec_module内で生成するからここではNoneを返して空のモジュールを作成する

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


@dataclasses.dataclass
class ScriptItem:
    path: str
    source: str


class ScriptEncryptor(object):

    @property
    def encoding(self) -> str:
        return self.__encoding

    def __init__(self, encoding='utf8'):
        self.__encoding = encoding

    @abc.abstractmethod
    def encrypt(self, scripts: Sequence[ScriptItem]) -> bytes:
        raise NotImplementedError()

    @abc.abstractmethod
    def decrypt(self, package: bytes) -> Sequence[ScriptItem]:
        raise NotImplementedError()

    def _encrypt_text(self, text: str) -> bytes:
        return base64.b85encode(text.encode(self.encoding))

    def _decrypt_text(self, data: bytes) -> str:
        return base64.b85decode(data).decode(self.encoding)


class ZipScriptEncryptor(ScriptEncryptor):

    def __init__(self, encoding='utf8'):
        super().__init__(encoding)

    def encrypt(self, scripts: Sequence[ScriptItem]) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as zip:
            for script in scripts:
                source = self._encrypt_text(script.source)
                zip.writestr(script.path, source)
        return buffer.getvalue()

    def decrypt(self, package: bytes) -> Sequence[ScriptItem]:
        scripts: List[ScriptItem] = []
        stream = io.BytesIO(package)
        with zipfile.ZipFile(stream, 'r') as zip:
            for name in zip.namelist():
                with zip.open(name) as f:
                    source = self._decrypt_text(f.read())
                scripts.append(ScriptItem(name, source))
        return scripts


class EncryptedPackage(object):

    def __init__(self, encryptor: ScriptEncryptor):
        self.__encryptor = encryptor

    def save(self, package_dest_path: str, package_root_dir: str) -> bool:
        scripts: List[ScriptItem] = []
        module_abs_paths: Dict[ str, str] = {}

        package_parent_dir = os.path.dirname(package_root_dir)
        for abs_path in glob.glob(f'{package_root_dir}/**/*.py', recursive=True):
            rel_path = os.path.relpath(abs_path, package_parent_dir).replace(os.sep, '/')
            module_name = os.path.splitext(rel_path)[0].replace('/', '.')
            module_abs_paths[module_name] = os.path.abspath(abs_path)
            with open(abs_path, 'r', encoding=self.__encryptor.encoding) as f:
                script = ScriptItem(rel_path, f.read())
                scripts.append(script)

        package_buffer = self.__encryptor.encrypt(scripts)
        package_size = len(package_buffer)
        paths_buffer = self.__encryptor._encrypt_text(json.dumps(module_abs_paths))

        with open(package_dest_path, 'wb') as f:
            f.write(package_size.to_bytes(8, 'little'))
            f.write(package_buffer)
            f.write(paths_buffer)

        return os.path.isfile(package_dest_path)

    def load(self, package_path: str) -> List[str]:
        module_scripts_dict: Dict[str, str] = {}

        with open(package_path, 'rb') as f:
            package_size = int.from_bytes(f.read(8), 'little')
            package_buffer = f.read(package_size)
            paths_buffer = f.read()

        scripts = self.__encryptor.decrypt(package_buffer)
        for script in scripts:
            module_name = os.path.splitext(script.path)[0].replace('/', '.')
            module_scripts_dict[module_name] = script.source

        module_abs_paths = json.loads(self.__encryptor._decrypt_text(paths_buffer))

        finder = _EncryptedImporter(module_scripts_dict, module_abs_paths)
        sys.meta_path.append(finder)

        return list(module_scripts_dict.keys())


if __name__ == '__main__':
    def _test():
        package_root_dir = os.path.join(os.path.dirname(__file__), '..', 'qymel')
        package_dest_path = os.path.join(os.path.dirname(__file__), 'qymel.pkg')

        m = EncryptedPackage(ZipScriptEncryptor())
        if not m.save(package_dest_path, package_root_dir):
            print('failed to save')
            exit(1)

        m = EncryptedPackage(ZipScriptEncryptor())
        module_names = m.load(package_dest_path)
        print(module_names)

        from qymel.core.force_reload import force_reload
        import qymel.core as qm
        force_reload(qm)

    _test()
