# coding: utf-8
from typing import *

from ..pyside_module import *


def hline(parent: Optional[QObject] = None) -> QFrame:
    frame = QFrame(parent)
    frame.setFrameShape(QFrame.HLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def vline(parent: Optional[QObject] = None) -> QFrame:
    frame = QFrame(parent)
    frame.setFrameShape(QFrame.VLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def hseparator(parent: Optional[QObject] = None) -> QFrame:
    frame = QFrame(parent)
    frame.setFrameShape(QFrame.HLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def vseparator(parent: Optional[QObject] = None) -> QFrame:
    frame = QFrame(parent)
    frame.setFrameShape(QFrame.VLine)
    frame.setFrameShadow(QFrame.Sunken)
    return frame


def groupbox(title: str, layout: QLayout, parent: Optional[QObject] = None) -> QGroupBox:
    box = QGroupBox(title, parent)
    box.setLayout(layout)
    return box


def scroll_area(layout: QLayout, parent: Optional[QObject] = None) -> QScrollArea:
    area = QScrollArea(parent)
    widget = QWidget(area)
    widget.setLayout(layout)
    area.setWidget(widget)
    area.setWidgetResizable(True)
    return area


def image(pixmap_or_filepath: Union[QPixmap, str], parent: Optional[QObject] = None) -> QLabel:
    label = QLabel(parent)
    pix = pixmap_or_filepath if isinstance(pixmap_or_filepath, QPixmap) else QPixmap(pixmap_or_filepath)
    label.setPixmap(pix)
    return label


def image_button(pixmap_or_filepath: Union[QPixmap, str], parent: Optional[QObject] = None) -> QPushButton:
    button = QPushButton(parent)
    pix = pixmap_or_filepath if isinstance(pixmap_or_filepath, QPixmap) else QPixmap(pixmap_or_filepath)
    icon = QIcon(pix)
    button.setIcon(icon)
    button.setIconSize(pix.size())
    button.setFixedSize(pix.size())
    return button


def desktop() -> QScreen:
    return QGuiApplication.primaryScreen()


from .clickable import *
from .event_proxy import *
from .expandable_splitter import *
from .expander import *
from .file_selector import *
from .log_viewer import *
from .models import *
