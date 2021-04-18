# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

from ui.pyside_module import *


def hline():
    # type: () -> QFrame
    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def vline():
    # type: () -> QFrame
    frame = QFrame()
    frame.setFrameShape(QFrame.VLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def hseparator():
    # type: () -> QFrame
    frame = QFrame()
    frame.setFrameShape(QFrame.HLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def vseparator():
    # type: () -> QFrame
    frame = QFrame()
    frame.setFrameShape(QFrame.VLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame
