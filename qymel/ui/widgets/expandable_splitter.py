# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *
from six import *
from six.moves import *

import enum

from ..pyside_module import *


__all__ = ['ExpandableSplitter']


class ExpandableSplitter(QSplitter):

    def createHandle(self):
        # type: () -> QSplitterHandle
        return ExpandableSplitterHandle(self.orientation(), self)


class ExpandableSplitterHandle(QSplitterHandle):

    def __init__(self, orientation, parent=None):
        # type: (Qt.Orientation, QSplitter) -> NoReturn
        super(ExpandableSplitterHandle, self).__init__(orientation, parent)
        self.setMouseTracking(True)

        self.__expanders = []  # type: list[Expander]
        self.__last_pos = None
        self.__range = tuple()  # type: tuple[int, int]

        self.setOrientation(orientation)

    def setOrientation(self, orientation):
        if orientation == Qt.Horizontal:
            self.__expanders = [Expander(ExpandDirection.RIGHT), Expander(ExpandDirection.LEFT)]
        else:
            self.__expanders = [Expander(ExpandDirection.LOWER), Expander(ExpandDirection.UPPER)]
        super(ExpandableSplitterHandle, self).setOrientation(orientation)

    def resizeEvent(self, event):
        # type: (QResizeEvent) -> NoReturn
        for expander in self.__expanders:
            expander.resize(self.rect())

        index = self.splitter().indexOf(self)
        self.__range = self.splitter().getRange(index)

    def paintEvent(self, event):
        # type: (QPaintEvent) -> NoReturn
        painter = QPainter(self)
        for expander in self.__expanders:
            option = QStyleOptionButton()
            option.state = QStyle.State_Enabled
            expander.apply_to(option)
            self.style().drawControl(QStyle.CE_PushButton, option, painter, self)
        painter.end()

    def mouseMoveEvent(self, event):
        # type: (QMouseEvent) -> NoReturn
        QApplication.restoreOverrideCursor()

        need_to_repainted = False
        for expander in self.__expanders:
            activated = expander.contains(event.pos())
            need_to_repainted |= expander.activate(activated)
            if activated:
                QApplication.setOverrideCursor(Qt.ArrowCursor)

        if need_to_repainted:
            self.repaint()

        super(ExpandableSplitterHandle, self).mouseMoveEvent(event)

    def leaveEvent(self, event):
        # type: (QEvent) -> NoReturn
        if any(expander.activate(False) for expander in self.__expanders):
            self.repaint()
        QApplication.restoreOverrideCursor()
        super(ExpandableSplitterHandle, self).leaveEvent(event)

    def mouseReleaseEvent(self, event):
        # type: (QMouseEvent) -> NoReturn
        for expander in self.__expanders:
            expander.enable(True)

            if expander.contains(event.pos()):
                pos = self.pos()

                current_pos = 0
                next_pos = 0
                last_pos = self.__last_pos
                min_pos, max_pos = self.__range

                enabled = True

                if expander.direction == ExpandDirection.RIGHT:
                    current_pos = pos.x()
                    if current_pos == min_pos:
                        next_pos = last_pos
                    else:
                        next_pos = max_pos
                        last_pos = current_pos
                        enabled = False

                elif expander.direction == ExpandDirection.LEFT:
                    current_pos = pos.x()
                    if current_pos == max_pos:
                        next_pos = last_pos
                    else:
                        next_pos = min_pos
                        last_pos = current_pos
                        enabled = False

                elif expander.direction == ExpandDirection.UPPER:
                    current_pos = pos.y()
                    if current_pos == max_pos:
                        next_pos = last_pos
                    else:
                        next_pos = min_pos
                        last_pos = current_pos
                        enabled = False

                elif expander.direction == ExpandDirection.LOWER:
                    current_pos = pos.y()
                    if current_pos == min_pos:
                        next_pos = last_pos
                    else:
                        next_pos = max_pos
                        last_pos = current_pos
                        enabled = False

                if next_pos != current_pos:
                    self.moveSplitter(next_pos)
                    self.__last_pos = last_pos

                expander.enable(enabled)


class ExpandDirection(enum.Enum):

    RIGHT = 1
    LEFT = 2
    UPPER = 3
    LOWER = 4


class Expander(object):

    ARROW_PIXMAP = None  # type: Optional[QPixmap]
    ARROW_SIZE = QSize(16, 16)

    @property
    def direction(self):
        # type: () -> ExpandDirection
        return self.__direction

    def __init__(self, direction):
        # type: (ExpandDirection, QRect) -> NoReturn
        if not Expander.ARROW_PIXMAP:
            Expander.ARROW_PIXMAP = QApplication.style().standardIcon(QStyle.SP_MediaPlay).pixmap(Expander.ARROW_SIZE)

        if direction == ExpandDirection.RIGHT:
            icon_pix = Expander.ARROW_PIXMAP
        elif direction == ExpandDirection.LEFT:
            icon_pix = Expander.ARROW_PIXMAP.transformed(QMatrix().rotate(180))
        elif direction == ExpandDirection.UPPER:
            icon_pix = Expander.ARROW_PIXMAP.transformed(QMatrix().rotate(-90))
        elif direction == ExpandDirection.LOWER:
            icon_pix = Expander.ARROW_PIXMAP.transformed(QMatrix().rotate(90))
        else:
            raise RuntimeError('invalid direction: {}'.format(repr(direction)))

        self.__icon = QIcon(icon_pix)
        self.__icon_size = QSize()
        self.__rect = QRect()
        self.__direction = direction
        self.__enabled = True
        self.__activated = False

    def resize(self, handle_rect):
        # type: (QRect) -> NoReturn
        hw = handle_rect.width()
        hh = handle_rect.height()

        self.__icon_size = QSize(hw, hh)

        if self.__direction == ExpandDirection.RIGHT:
            self.__rect = QRect(QPoint(0, hh / 4 * 1), QSize(hw, hh / 4))
            return

        if self.__direction == ExpandDirection.LEFT:
            self.__rect = QRect(QPoint(0, hh / 4 * 2), QSize(hw, hh / 4))
            return

        if self.__direction == ExpandDirection.UPPER:
            self.__rect = QRect(QPoint(hw / 4 * 1, 0), QSize(hw / 4, hh))
            return

        if self.__direction == ExpandDirection.LOWER:
            self.__rect = QRect(QPoint(hw / 4 * 2, 0), QSize(hw / 4, hh))
            return

    def contains(self, point):
        # type: (QPoint) -> bool
        return self.__rect.contains(point)

    def activate(self, value):
        # type: (bool) -> bool
        updated = value != self.__activated
        self.__activated = value
        return updated

    def enable(self, value):
        # type: (bool) -> bool
        updated = value != self.__enabled
        self.__enabled = value
        return updated

    def apply_to(self, option):
        # type: (QStyleOptionButton) -> NoReturn
        option.rect = self.__rect
        option.icon = self.__icon
        option.iconSize = self.__icon_size

        if self.__activated:
            option.state |= QStyle.State_MouseOver

        if not self.__enabled:
            option.state ^= QStyle.State_Enabled

