# coding: utf-8
from typing import *
import sys
import os
import ast
import inspect
import types
import codecs
import importlib
import sysconfig


IGNORED_MODULE_FILE_PATHS = [
    sysconfig.get_path('stdlib').lower(),
    os.environ.get('MAYA_LOCATION', '').replace('/', os.sep).lower(),
    __file__.lower(),
]
IGNORED_MODULE_NAMES = []


def force_reload(module_obj):
    items = _get_import_items(module_obj)
    _reload_modules(items)
    _apply_updates(items)


class _ImportSymbol(object):

    def __init__(self, name: Union[str, ast.alias]) -> None:
        if isinstance(name, str):
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

    def __init__(self,
                 module: types.ModuleType,
                 alias: Optional[str],
                 symbols: Optional[List[_ImportSymbol]] = None
     ) -> None:
        self.module = module
        self.alias = alias
        self.symbols = [s for s in symbols or [] if not s.name.startswith('Q')]

    def __repr__(self):
        if self.alias is not None:
            return '{} as {}, {}'.format(self.module.__name__, self.alias, self.symbols)
        return '{} {}'.format(self.module.__name__, self.symbols)


class _ModuleItem(object):

    def __init__(self, module: types.ModuleType, items: List[_ImportItem]) -> None:
        self.module = module
        self.items = items


def _get_import_items(root_module: types.ModuleType) -> List[_ModuleItem]:
    return _get_import_items_rec(root_module, set())


def _get_import_items_rec(module: types.ModuleType, found_modules: Set[types.ModuleType]) -> List[_ModuleItem]:
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


def _reload_modules(items: List[_ModuleItem]) -> None:
    for item in items:
        print('reload: {}'.format(item.module.__name__))
        importlib.reload(item.module)


def _apply_updates(updated_items: List[_ModuleItem]) -> None:
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


def _walk_ast_tree(tree: ast.Module, module: types.ModuleType) -> List[_ImportItem]:
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
                        symbols = [_ImportSymbol(name) for name in module_obj.__dict__['__all__']]
                    else:
                        symbols = [_ImportSymbol(name) for name in module_obj.__dict__ if not name.startswith('_')]

                    result.append(_ImportItem(module_obj, None, symbols))
                    break

                else:
                    module_obj = _find_from_sys_modules(module, f'{node_module_name}.{alias.name}', node.level)
                    module_obj = module_obj or _find_from_sys_modules(module, node_module_name, node.level)
                    if not _is_reload_target_module(module_obj):
                        continue

                    symbol = _ImportSymbol(alias)
                    symbol.is_module = module_obj.__name__.split('.')[-1] == alias.name

                    result.append(_ImportItem(module_obj, None, [symbol]))

    return result


def _parse_module_source(module: types.ModuleType) -> Optional[ast.Module]:
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


def _is_reload_target_module(module: types.ModuleType) -> bool:
    if module is None:
        return False

    if module.__name__ in sys.builtin_module_names:
        return False

    if module.__name__ in IGNORED_MODULE_NAMES:
        return False

    module_file = module.__dict__.get('__file__', None)
    if module_file is None:
        return False

    module_file = module_file.lower()

    for ignored_path in IGNORED_MODULE_FILE_PATHS:
        if ignored_path and module_file.startswith(ignored_path):
            return False

    return True


def _find_from_sys_modules(
        module: types.ModuleType,
        node_name: str,
        relative_ref_level: int = 0
) -> Optional[types.ModuleType]:
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
