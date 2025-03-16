# coding: utf-8
import pkg_resources

try:
    PYSIDE_VERSION = next(tuple(int(v) for v in dist.version.split('.')) for dist in pkg_resources.working_set if dist.key.startswith('pyside'))
except:
    raise RuntimeError('PySide is not installed')

if PYSIDE_VERSION[0] == 6:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
    from PySide6.QtUiTools import *
    from shiboken6 import wrapInstance
elif PYSIDE_VERSION[0] == 2:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2.QtUiTools import *
    from shiboken2 import wrapInstance
elif PYSIDE_VERSION[0] == 1:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide.QtUiTools import *
    from shiboken import wrapInstance
else:
    raise ImportError('Unsupported PySide version: %s' % PYSIDE_VERSION)
