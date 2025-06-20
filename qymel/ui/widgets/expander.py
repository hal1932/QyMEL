from ..pyside_module import *
from .. import layouts as _layouts

from . import clickable as _clickable


__all__ = ['Expander']


class Expander(QFrame):
    """
    >>> widget = QWidget()
    >>> layout = QVBoxLayout()
    >>> widget.setLayout(layout)
    >>>
    >>> for _ in range(3):
    >>>     expander = Expander()
    >>>     expander.header_layout.setContentsMargins(1, 1, 1, 1)
    >>>     expander.content_layout.setContentsMargins(1, 1, 1, 1)
    >>>     expander.set_header_widget(QLabel('aaa'))
    >>>     expander.set_content_widget(QPushButton('bbb'))
    >>>     layout.addWidget(expander)
    >>> layout.addStretch()
    >>>
    >>> widget.show()
    """

    @property
    def header_layout(self) -> QLayout:
        return self._header_layout

    @property
    def content_layout(self) -> QLayout:
        return self._content_layout

    def __init__(self, parent: QObject|None = None) -> None:
        super(Expander, self).__init__(parent)

        toggle_icon = QApplication.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self._toggle_pix = toggle_icon.pixmap(12)
        self._toggle_image = QLabel()
        self._toggle_image.setPixmap(self._toggle_pix)

        self._header_layout = QHBoxLayout()
        self._content_layout = QHBoxLayout()

        self._header = _clickable.Clickable()
        self._header.setLayout(self._header_layout)
        self._header.clicked.connect(self.toggle)

        self._content = QWidget()
        self._content.setLayout(self._content_layout)
        self._content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._content.setMaximumHeight(0)
        self._content.setMinimumHeight(0)

        self._main_layout = QVBoxLayout()
        self._main_layout.setSpacing(0)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.addWidget(self._header)
        self._main_layout.addWidget(self._content)
        self._main_layout.addStretch()
        self.setLayout(self._main_layout)

        self.setLineWidth(1)
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Plain)

        self._expanded = False

    def set_header_widget(self, header: QWidget) -> None:
        layout = self._header_layout
        _layouts.delete_layout_children(layout)

        layout.addWidget(self._toggle_image)
        layout.addWidget(header)
        layout.addStretch()

        self._update_layout()

    def set_content_widget(self, content: QWidget) -> None:
        layout = self._content_layout
        _layouts.delete_layout_children(layout)

        layout.addWidget(content)
        layout.addStretch()

        self._update_layout()

    def toggle(self) -> None:
        if self._expanded:
            self.collapse()
        else:
            self.expand()

    def expand(self) -> None:
        collapsed_height = self.sizeHint().height() - self._content.maximumHeight()

        content_layout = self._content.layout()
        if content_layout:
            content_height = content_layout.sizeHint().height()
        else:
            content_height = 0

        m = QTransform.rotate(90)
        icon_pix = self._toggle_pix.transformed(m)
        self._toggle_image.setPixmap(icon_pix)

        self._content.setMaximumHeight(content_height)
        self.setMaximumHeight(collapsed_height + content_height)

        self._expanded = True

    def collapse(self) -> None:
        collapsed_height = self.sizeHint().height() - self._content.maximumHeight()

        self._toggle_image.setPixmap(self._toggle_pix)

        self._content.setMaximumHeight(0)
        self.setMaximumHeight(collapsed_height)

        self._expanded = False

    def _update_layout(self) -> None:
        if self._expanded:
            self.expand()
        else:
            self.collapse()
