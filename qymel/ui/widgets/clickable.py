# coding: utf-8
from typing import *

from ..pyside_module import *


class Clickable(QWidget):

    clicked = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super(Clickable, self).__init__(parent)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        self.clicked.emit()
