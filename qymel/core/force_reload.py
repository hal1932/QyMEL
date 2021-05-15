# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import sys
import os
import ast
import inspect
import types
import codecs
import distutils.sysconfig


try:
    from six.moves import reload_module, builtins
except ImportError:
    reload_module = reload
    builtins = __builtin__


IGNORED_MODULE_FILE_PATHS = [
    distutils.sysconfig.get_python_lib(standard_lib=True),
    os.environ.get('MAYA_LOCATION', '').replace('/', os.sep),
]
IGNORED_MODULE_NAMES = []


def force_reload(module_obj):
    items = _get_import_items(module_obj)
    _reload_modules(items)
    _apply_updates(items)


class _ImportSymbolItem(object):

    def __init__(self, name):
        # type: (Union[str, ast.alias]) -> NoReturn
        if isinstance(name, (str, text_type)):
            self.name = name
            self.alias = None
        elif isinstance(name, ast.alias):
            self.name = name.name
            self.alias = name.asname
        self.is_module = False

    def __repr__(self):
        if self.alias is not None:
            return '{} as {}'.format(self.name, self.alias)
        return self.name


class _ImportItem(object):

    def __init__(self, module, alias, symbols=None):
        # type: (types.ModuleType, Optional[text_type], Optional[List[_ImportSymbolItem]]) -> NoReturn
        self.module = module
        self.alias = alias
        self.symbols = [s for s in symbols or [] if not s.name.startswith('Q')]

    def __repr__(self):
        if self.alias is not None:
            return '{} as {}, {}'.format(self.module.__name__, self.alias, self.symbols)
        return '{} {}'.format(self.module.__name__, self.symbols)


class _ModuleItem(object):

    def __init__(self, module, items):
        # type: (types.ModuleType, List[_ImportItem]) -> NoReturn
        self.module = module
        self.items = items


def _get_import_items(root_module):
    # type: (types.ModuleType) -> List[_ModuleItem]
    return _get_import_items_rec(root_module, set())


def _get_import_items_rec(module, found_modules):
    # type: (types.ModuleType, Set[types.ModuleType]) -> List[_ModuleItem]
    if not _is_reload_target_module(module) or module in found_modules:
        return []

    found_modules.add(module)

    tree = _parse_module_source(module)
    if tree is None:
        return []

    result = []  # type: List[_ModuleItem]

    children = _walk_ast_tree(tree, module)

    child_item = _ModuleItem(module, children)

    for child in children:
        result.extend(_get_import_items_rec(child.module, found_modules))

    result.append(child_item)

    return result


def _reload_modules(items):
    # type: (List[_ModuleItem]) -> NoReturn
    for item in items:
        print('reload: {}'.format(item.module.__name__))
        reload_module(item.module)


def _apply_updates(updated_items):
    # type: (List[_ModuleItem]) -> NoReturn
    for item in updated_items:
        module = item.module
        items = item.items

        # print(module.__name__)

        for sub_item in items:
            if sub_item.symbols is None:
                continue

            # print('  {}'.format(sub_item.module.__name__))

            for symbol in sub_item.symbols:
                symbol_name = symbol.alias if symbol.alias is not None else symbol.name

                if symbol.is_module:
                    new_symbol_obj = sys.modules[sub_item.module.__name__]
                else:
                    new_symbol_obj = sys.modules[sub_item.module.__name__].__dict__[symbol.name]

                if id(module.__dict__[symbol_name]) == id(new_symbol_obj):
                    continue

                # print('    {}, {}: {} -> {}'.format(symbol_name, module.__dict__[symbol_name], id(module.__dict__[symbol_name]), id(new_symbol_obj)))
                module.__dict__[symbol_name] = new_symbol_obj


def _walk_ast_tree(tree, module):
    # type: (ast.Module, types.ModuleType) -> List[_ImportItem]
    result = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                module_obj = _find_from_sys_modules(module, module_name)
                if module_obj is None or not _is_reload_target_module(module_obj):
                    continue
                result.append(_ImportItem(module_obj, alias.asname))

        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                node_module_name = node.module
            else:
                node_module_name = node.names[0].name

            for alias in node.names:
                if alias.name == '*':
                    module_obj = _find_from_sys_modules(module, node_module_name, node.level)
                    if not _is_reload_target_module(module_obj):
                        continue

                    if '__all__' in module_obj.__dict__:
                        symbols = [_ImportSymbolItem(name) for name in module_obj.__dict__['__all__']]
                    else:
                        symbols = [_ImportSymbolItem(name) for name in module_obj.__dict__ if not name.startswith('_')]

                    result.append(_ImportItem(module_obj, None, symbols))
                    break

                else:
                    module_obj = _find_from_sys_modules(module, '{}.{}'.format(node_module_name, alias.name), node.level)
                    module_obj = module_obj or _find_from_sys_modules(module, node_module_name, node.level)
                    if not _is_reload_target_module(module_obj):
                        continue

                    symbol = _ImportSymbolItem(alias)
                    symbol.is_module = module_obj.__name__.split('.')[-1] == alias.name

                    result.append(_ImportItem(module_obj, None, [symbol]))

    return result


def _parse_module_source(module):
    # type: (types.ModuleType) -> Optional[ast.Module]
    try:
        # inspect.getsource() は内部でキャッシュが効いてるから、必ず最新のソースを取得するために自前で read() する
        # source = inspect.getsource(module)
        source_file = inspect.getsourcefile(module)
        with codecs.open(source_file, 'r', 'utf-8') as f:
            source = f.read()
    except TypeError:
        return None
    except IOError:
        return None

    return ast.parse(source)


def _is_reload_target_module(module):
    # type: (types.ModuleType) -> bool
    if module is None:
        return False

    if module.__name__ in IGNORED_MODULE_NAMES:
        return False

    module_file = module.__dict__.get('__file__', None)
    if module_file is None:
        return False

    if module_file == __file__:
        return False

    for ignored_path in IGNORED_MODULE_FILE_PATHS:
        if module_file.startswith(ignored_path):
            return False

    return True


def _find_from_sys_modules(module, node_name, relative_ref_level=0):
    # type: (types.ModuleType, str, int) -> Optional[types.ModuleType]
    # absolute import?
    if node_name in sys.modules:
        return sys.modules[node_name]

    # relative import?
    if relative_ref_level == 0:
        module_name = '{}.{}'.format(module.__name__, node_name)
    else:
        module_origin_name = '.'.join(module.__name__.split('.')[:-relative_ref_level])
        module_name = '{}.{}'.format(module_origin_name, node_name)
        if module_name not in sys.modules and module.__package__ is not None:
            module_name = '{}.{}'.format(module.__package__, node_name)

    return sys.modules.get(module_name, None)
