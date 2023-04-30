# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

from ..pyside_module import *


def hline(parent=None):
    # type: (QObject) -> QFrame
    frame = QFrame(parent)
    frame.setFrameShape(QFrame.HLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def vline(parent=None):
    # type: (QObject) -> QFrame
    frame = QFrame(parent)
    frame.setFrameShape(QFrame.VLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def hseparator(parent=None):
    # type: (QObject) -> QFrame
    frame = QFrame(parent)
    frame.setFrameShape(QFrame.HLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def vseparator(parent=None):
    # type: (QObject) -> QFrame
    frame = QFrame(parent)
    frame.setFrameShape(QFrame.VLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def groupbox(title, layout, parent=None):
    # type: (text_type, QLayout, QObject) -> QGroupBox
    box = QGroupBox(title, parent)
    box.setLayout(layout)
    return box


def scroll_area(layout, parent=None):
    # type: (QLayout, QObject) -> QScrollArea
    area = QScrollArea(parent)
    widget = QWidget(area)
    widget.setLayout(layout)
    area.setWidget(widget)
    area.setWidgetResizable(True)
    return area


def image(pixmap_or_filepath, parent=None):
    # type: (Union[QPixmap, text_type], QObject) -> QLabel
    label = QLabel(parent)
    pix = pixmap_or_filepath if isinstance(pixmap_or_filepath, QPixmap) else QPixmap(pixmap_or_filepath)
    label.setPixmap(pix)
    return label


def image_button(pixmap_or_filepath, parent=None):
    # type: (Union[QPixmap, text_type], QObject) -> QPushButton
    button = QPushButton(parent)
    pix = pixmap_or_filepath if isinstance(pixmap_or_filepath, QPixmap) else QPixmap(pixmap_or_filepath)
    icon = QIcon(pix)
    button.setIcon(icon)
    button.setIconSize(pix.size())
    button.setFixedSize(pix.size())
    return button


def desktop():
    # type: () -> QDesktopWidget
    app = QApplication.instance()
    return app.desktop()


from .clickable import *
from .event_proxy import *
from .expandable_splitter import *
from .expander import *
from .file_selector import *
from .log_viewer import *
from .models import *
