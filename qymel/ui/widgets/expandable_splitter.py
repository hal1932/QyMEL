# coding: utf-8
from __future__ import absolute_import, print_function, division
from typing import *

import enum

from ..pyside_module import *


__all__ = ['ExpandableSplitter']


class ExpandableSplitter(QSplitter):
    """
    >>> splitter = ExpandableSplitter()
    >>> splitter.addWidget(QPushButton('aaa'))
    >>> splitter.addWidget(QPushButton('bbb'))
    >>> splitter.show()
    """

    def __init__(self, *args, **kwargs):
        super(ExpandableSplitter, self).__init__(*args, **kwargs)

        def _splitter_moved(pos, index):
            handle = self.handle(index)
            if isinstance(handle, ExpandableSplitterHandle):
                handle.on_splitter_moved(pos)

        self.splitterMoved.connect(_splitter_moved)

    def createHandle(self):
        # type: () -> QSplitterHandle
        return ExpandableSplitterHandle(self.orientation(), self)


class ExpandableSplitterHandle(QSplitterHandle):

    def __init__(self, orientation, parent=None):
        # type: (Qt.Orientation, QSplitter) -> NoReturn
        super(ExpandableSplitterHandle, self).__init__(orientation, parent)
        self.setMouseTracking(True)

        self.__expanders = []  # type: List[Expander]
        self.__last_pos = None
        self.__range = tuple()  # type: Tuple[int, int]

        self.setOrientation(orientation)

    def on_splitter_moved(self, pos):
        # type: (int) -> NoReturn
        if pos == 0:
            for expander in self.__expanders:
                disabled = expander.direction == ExpandDirection.LEFT or expander.direction == ExpandDirection.UPPER
                expander.enable(not disabled)
        elif pos == self.__range[1]:
            for expander in self.__expanders:
                disabled = expander.direction == ExpandDirection.RIGHT or expander.direction == ExpandDirection.LOWER
                expander.enable(not disabled)
        else:
            for expander in self.__expanders:
                expander.enable(True)

    def setOrientation(self, orientation):
        super(ExpandableSplitterHandle, self).setOrientation(orientation)

        if orientation == Qt.Horizontal:
            self.__expanders = [Expander(ExpandDirection.RIGHT), Expander(ExpandDirection.LEFT)]
        else:
            self.__expanders = [Expander(ExpandDirection.LOWER), Expander(ExpandDirection.UPPER)]

    def resizeEvent(self, event):
        # type: (QResizeEvent) -> NoReturn
        super(ExpandableSplitterHandle, self).resizeEvent(event)

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
        super(ExpandableSplitterHandle, self).mouseMoveEvent(event)

        QApplication.restoreOverrideCursor()

        need_to_repainted = False
        for expander in self.__expanders:
            activated = expander.contains(event.pos())
            need_to_repainted |= expander.activate(activated)
            if activated:
                QApplication.setOverrideCursor(Qt.ArrowCursor)

        if need_to_repainted:
            self.repaint()

    def leaveEvent(self, event):
        # type: (QEvent) -> NoReturn
        super(ExpandableSplitterHandle, self).leaveEvent(event)

        if any(expander.activate(False) for expander in self.__expanders):
            self.repaint()
        QApplication.restoreOverrideCursor()

    def mousePressEvent(self, event):
        # type: (QMouseEvent) -> NoReturn
        super(ExpandableSplitterHandle, self).mousePressEvent(event)

        pos = self.__current_position()
        if self.__range[0] < pos < self.__range[1]:
            self.__last_pos = pos

    def mouseReleaseEvent(self, event):
        # type: (QMouseEvent) -> NoReturn
        super(ExpandableSplitterHandle, self).mouseReleaseEvent(event)

        current_pos = self.__current_position()

        for expander in self.__expanders:
            if not expander.is_enabled:
                continue

            if expander.contains(event.pos()):
                next_pos = 0
                last_pos = self.__last_pos
                min_pos, max_pos = self.__range

                enabled = True

                if expander.direction == ExpandDirection.RIGHT:
                    if current_pos == min_pos:
                        next_pos = last_pos
                    else:
                        next_pos = max_pos
                        last_pos = current_pos
                        enabled = False

                elif expander.direction == ExpandDirection.LEFT:
                    if current_pos == max_pos:
                        next_pos = last_pos
                    else:
                        next_pos = min_pos
                        last_pos = current_pos
                        enabled = False

                elif expander.direction == ExpandDirection.UPPER:
                    if current_pos == max_pos:
                        next_pos = last_pos
                    else:
                        next_pos = min_pos
                        last_pos = current_pos
                        enabled = False

                elif expander.direction == ExpandDirection.LOWER:
                    if current_pos == min_pos:
                        next_pos = last_pos
                    else:
                        next_pos = max_pos
                        last_pos = current_pos
                        enabled = False

                if next_pos != current_pos and last_pos:
                    self.moveSplitter(next_pos)
                    self.__last_pos = last_pos

                expander.enable(enabled)

    def __current_position(self):
        # type: () -> int
        pos = self.pos()
        if self.orientation() == Qt.Horizontal:
            return pos.x()
        return pos.y()


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

    @property
    def is_enabled(self):
        # type: () -> bool
        return self.__enabled

    def __init__(self, direction):
        # type: (ExpandDirection) -> NoReturn
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