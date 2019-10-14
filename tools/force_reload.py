# coding: utf-8
from __future__ import absolute_import

import sys
import ast
import inspect
import types
import distutils.sysconfig


try:
    from six.moves import reload_module, builtins
except ImportError:
    reload_module = reload
    builtins = __builtin__


STDLIB_ROOT = distutils.sysconfig.get_python_lib(standard_lib=True).lower()
MAYALIB_ROOT = 'C:\\Program Files\\Autodesk\\Maya2018\\bin'


__reloaded_modules = set()


def force_reload(module_obj):
    global __reloaded_modules
    __reloaded_modules.clear()

    __force_reload_rec(module_obj)


def __is_reload_target(module_obj):
    module_file = module_obj.__dict__.get('__file__', None)
    if module_file is None:
        return False

    if module_file.startswith(MAYALIB_ROOT):
        return False

    if module_file.lower().startswith(STDLIB_ROOT):
        return False

    return True


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
