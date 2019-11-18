# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import sys
import os
import ast
import inspect
import types
import collections
import distutils.sysconfig


try:
    from six.moves import reload_module, builtins
except ImportError:
    reload_module = reload
    builtins = __builtin__


STDLIB_ROOT = distutils.sysconfig.get_python_lib(standard_lib=True).lower()
MAYALIB_ROOT = os.environ.get('MAYA_LOCATION', None).replace('/', os.sep)


_reloaded_modules = set()


def force_reload(module_obj):
    global _reloaded_modules
    _reloaded_modules.clear()

    items = _get_import_items(module_obj)
    _reload_modules(items)
    _apply_updates(items)


class _ImportSymbolItem(object):

    def __init__(self, name):
        # type: (Union[str, ast.alias]) -> NoReturn
        if isinstance(name, (str, unicode)):
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
        # type: (types.ModuleType, str, List[_ImportSymbolItem]) -> NoReturn
        self.module = module
        self.alias = alias
        self.symbols = symbols

    def __repr__(self):
        if self.alias is not None:
            return '{} as {}, {}'.format(self.module.__name__, self.alias, self.symbols)
        return '{} {}'.format(self.module.__name__, self.symbols)


def _get_import_items(root_module):
    # type: (types.ModuleType) -> collections.OrderedDict[types.ModuleType, List[_ImportItem]]
    result = collections.OrderedDict()

    modules = [root_module]
    while len(modules) > 0:
        module = modules.pop(-1)
        if module in result or not _is_reload_target(module):
            continue

        tree = _parse_module_source(module)
        if tree is None:
            continue

        children = _walk_ast_tree(tree, module)
        for child in children:
            if child.module in result:
                continue
            modules.append(child.module)

        result[module] = children

    return result


def _reload_modules(items):
    # type: (Dict[types.ModuleType, List[_ImportItem]]) -> NoReturn
    for module in items.keys():
        print 'reload: {}'.format(module.__name__)
        reload_module(module)


def _apply_updates(updated_items):
    # type: (Dict[types.ModuleType, List[_ImportItem]]) -> NoReturn
    for module, items in updated_items.items():
        if len(items) > 0:
            print module.__name__
        for item in items:
            if item.symbols is None:
                continue

            for symbol in item.symbols:
                symbol_name = symbol.alias if symbol.alias is not None else symbol.name

                if symbol.is_module:
                    new_symbol_obj = item.module
                else:
                    new_symbol_obj = item.module.__dict__[symbol.name]

                if id(module.__dict__[symbol_name]) == id(new_symbol_obj):
                    continue

                print '  {}: {} -> {}'.format(module.__dict__[symbol_name], id(module.__dict__[symbol_name]), id(new_symbol_obj))
                module.__dict__[symbol_name] = new_symbol_obj


def _walk_ast_tree(tree, module):
    # type: (ast.Module, types.ModuleType) -> List[_ImportItem]
    result = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                module_obj = _find_from_sys_modules(module, module_name)
                if module_obj is None or not _is_reload_target(module_obj):
                    continue
                result.append(_ImportItem(module_obj, alias.asname, None))

        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                if node.names[0].name == '*':
                    module_obj = _find_from_sys_modules(module, node.module)
                else:
                    if node.module is None:
                        submodule_name = node.names[0].name
                    else:
                        submodule_name = '{}.{}'.format(node.module, node.names[0].name)
                    module_obj = _find_from_sys_modules(module, submodule_name, node.level)
            else:
                module_obj = _find_from_sys_modules(module, node.module)

            if module_obj is None or not _is_reload_target(module_obj):
                continue

            symbols = []
            for alias in node.names:
                if alias.name == '*':
                    if '__all__' in module_obj.__dict__:
                        symbols.extend([_ImportSymbolItem(name) for name in module_obj.__dict__['__all__']])
                    else:
                        symbols.extend([_ImportSymbolItem(name) for name in module_obj.__dict__ if not name.startswith('_')])
                else:
                    symbol = _ImportSymbolItem(alias)
                    symbol.is_module = module_obj.__name__.split('.')[-1] == alias.name
                    symbols.append(symbol)

            result.append(_ImportItem(module_obj, None, symbols))

    # print module
    # for item in result:
    #     print '    {} as {}'.format(item.module.__name__, item.alias)
    #     for symbol in item.symbols:
    #         print '        {} as {}, {}'.format(symbol.name, symbol.alias, symbol.is_module)

    return result


def _parse_module_source(module):
    # type: (types.ModuleType) -> ast.Module
    try:
        # inspect.getsource() は内部でキャッシュが効いてるから、必ず最新のソースを取得するために自前で read() する
        # source = inspect.getsource(module)
        source_file = inspect.getsourcefile(module)
        with open(source_file, 'r') as f:
            source = f.read()
    except TypeError:
        return None
    except IOError:
        return None

    return ast.parse(source)


def _is_reload_target(module):
    # type: (types.ModuleType) -> bool
    module_file = module.__dict__.get('__file__', None)
    if module_file is None:
        return False

    if module_file == __file__:
        return False

    if MAYALIB_ROOT is not None and module_file.startswith(MAYALIB_ROOT):
        return False

    if module_file.lower().startswith(STDLIB_ROOT):
        return False

    return True


def _find_from_sys_modules(module, node_name, relative_ref_level=0):
    # type: (types.ModuleType, str, int) -> types.ModuleType
    # absolute import
    module_name = node_name
    if module_name not in sys.modules:
        # relative import
        module_origin_name = '.'.join(module.__name__.split('.')[:-relative_ref_level])
        module_name = '{}.{}'.format(module_origin_name, node_name)
        if module_name not in sys.modules:
            if module.__package__ is None:
                return None
            module_name = '{}.{}'.format(module.__package__, node_name)

    if module_name not in sys.modules:
        return None

    return sys.modules[module_name]


if __name__ == '__main__':
    import reload_test as rt
    force_reload(rt)

'''
def __force_reload_rec(module_obj, indent=0):
    if not isinstance(module_obj, types.ModuleType):
        return

    global __reloaded_modules
    if module_obj in __reloaded_modules:
        return False

    if not __is_reload_target(module_obj):
        return

    print('{}reload {}, {}'.format('  ' * indent, module_obj.__name__, module_obj.__file__))
    module_obj = reload_module(module_obj)

    for submodule in __find_submodules(module_obj):
        if not __is_reload_target(submodule.module_obj):
            continue

        __force_reload_rec(submodule.module_obj, indent + 1)

        module_obj = reload_module(module_obj)
        __reloaded_modules.add(module_obj)

        if submodule.from_import:
            for symbol in submodule.symbols:
                name = symbol.name

                as_name = symbol.as_name
                if as_name is None:
                    as_name = name

                # if as_name[0] != 'Q':
                #     if as_name == name:
                #         print('{} - ({}) {} {} {} -> {}'.format(
                #             '  ' * (indent + 1),
                #             module_obj.__name__,
                #             name, module_obj.__dict__[as_name],
                #             id(module_obj.__dict__[as_name]), id(submodule.module_obj.__dict__[name])))
                #     else:
                #         print('{} - ({}) {} as {} {} {} -> {}'.format(
                #             '  ' * (indent + 1),
                #             module_obj.__name__,
                #             name, as_name, module_obj.__dict__[as_name],
                #             id(module_obj.__dict__[as_name]), id(submodule.module_obj.__dict__[name])))

                if submodule.module_obj.__name__.split('.')[-1] == name:
                    module_obj.__dict__[as_name] = submodule.module_obj
                else:
                    module_obj.__dict__[as_name] = submodule.module_obj.__dict__[name]


class __ModuleInfo(object):

    def __init__(self):
        self.name = None
        self.module_obj = None
        self.from_import = False
        self.symbols = []

    def __repr__(self):
        return '{}, {}, {}, {}'.format(self.name, self.module_obj, self.from_import, ', '.join(self.symbols))


class __SymbolInfo(object):

    def __init__(self, name):
        if isinstance(name, ast.alias):
            self.name = name.name
            self.as_name = name.asname
        else:
            self.name = name
            self.as_name = None

    def __repr__(self):
        if self.as_name is not None:
            return '{} as {}'.format(self.name, self.as_name)
        else:
            return self.name


def __find_submodules(module_obj):
    try:
        source = inspect.getsource(module_obj)
    except TypeError:
        return []
    except IOError:
        return []

    tree = ast.parse(source)

    modules = []

    for node in tree.body:
        if isinstance(node, ast.Import):
            target_module = __get_sys_module(module_obj, node.names[0].name)
            if target_module is None:
                continue

            module = __ModuleInfo()
            module.module_obj = target_module
            modules.append(module)

        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:
                if node.names[0].name == '*':
                    target_module = __get_sys_module(module_obj, node.module)
                else:
                    if node.module is None:
                        submodule_name = node.names[0].name
                    else:
                        submodule_name = '{}.{}'.format(node.module, node.names[0].name)
                    target_module = __get_sys_module(module_obj, submodule_name, node.level)
            else:
                target_module = __get_sys_module(module_obj, node.module)
            if target_module is None:
                continue

            if node.names[0].name == '*':
                if '__all__' in target_module.__dict__:
                    symbols = [__SymbolInfo(x) for x in target_module.__dict__['__all__']]
                else:
                    symbols = [__SymbolInfo(x) for x in target_module.__dict__ if not x.startswith('__')]
            else:
                symbols = [__SymbolInfo(x) for x in node.names]

            module = __ModuleInfo()
            module.name = node.module
            module.module_obj = target_module
            module.from_import = True
            module.symbols = symbols

            modules.append(module)

    return modules


def __get_sys_module(module_obj, node_name, relative_ref_level=0):
    # absolute import
    module_name = node_name
    if module_name not in sys.modules:
        # relative import
        module_origin_name = '.'.join(module_obj.__name__.split('.')[:-relative_ref_level])
        module_name = '{}.{}'.format(module_origin_name, node_name)
        if module_name not in sys.modules:
            if module_obj.__package__ is None:
                return None
            module_name = '{}.{}'.format(module_obj.__package__, node_name)

    if module_name not in sys.modules:
        return None

    return sys.modules[module_name]
'''
