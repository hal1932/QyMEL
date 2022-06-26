# coding: utf-8
try:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtUiTools import *
    PYSIDE_VERSION = 2
except ImportError:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtUiTools import *
    PYSIDE_VERSION = 1

try:
    from shiboken2 import wrapInstance
except ImportError:
    try:
        from shiboken import wrapInstance
    except ImportError:
        try:
            from Shiboken.shiboken import wrapInstance
        except ImportError:
            pass
