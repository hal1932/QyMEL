# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import collections

import maya.cmds as cmds

from qymel.ui.pyside_module import *
import qymel.core as qm
import qymel.ui as qu


class _LayerItem(object):

    @property
    def name(self):
        # type: () -> str
        return self.node.name

    def __init__(self, node, parent):
        # type: (qm.DependNode, _LayerItem) -> NoReturn
        self.node = node
        self.parent = parent

        self.children = []

        for child_name in cmds.qmSceneLayerQuery(node.mel_object, children=True) or []:
            child = _LayerItem(qm.eval_node(child_name), self)
            self.children.append(child)


class _LayerTreeModel(QAbstractItemModel):

    def __init__(self, parent=None):
        super(_LayerTreeModel, self).__init__(parent)

        nodes = [qm.eval_node(name) for name in cmds.qmSceneLayerQuery(rootNodes=True) or []]
        self.__root_items = [_LayerItem(node, None) for node in nodes]

    def rowCount(self, parent):
        # type: (QModelIndex) -> int
        if parent is None or not parent.isValid():
            return len(self.__root_items)

        children = parent.internalPointer().children
        return len(children)

    def columnCount(self, parent):
        # type: (QModelIndex) -> int
        return 2

    def headerData(self, section, orientation, role):
        # type: (int, Qt.Orientation, int) -> str
        if role == Qt.DisplayRole:
            if section == 0:
                return 'name'
            if section == 1:
                return 'aaa'
        return None

    def data(self, index, role):
        # type: (QModelIndex, int) -> Any
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            item = index.internalPointer()
            if index.column() == 0:
                return item.name
            if index.column() == 1:
                return 'x'

        return None

    def index(self, row, column, parent):
        # type: (int, int, QModelIndex) -> QModelIndex
        if parent is None or not parent.isValid():
            return self.createIndex(row, column, self.__root_items[row])

        item = parent.internalPointer()
        if row < len(item.children):
            return self.createIndex(row, column, item.children[row])

        return QModelIndex()

    def parent(self, index):
        # type: (QModelIndex) -> QModelIndex
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if item.parent is None:
            return QModelIndex()

        parent_item = item.parent
        if parent_item.parent is None:
            row = self.__root_items.index(parent_item)
        else:
            row = parent_item.parent.children.index(parent_item)

        return self.createIndex(row, 0, parent_item)

    def traverse(self, predicate=None):
        # type: (Callable[[QModelIndex], bool]) -> Iterable[QModelIndex]
        result = []

        def _dfs(index):
            if predicate is not None and not predicate(index):
                return
            result.append(index)
            for i in range(self.rowCount(index)):
                child = self.index(i, 0, index)
                _dfs(child)

        for i in range(self.rowCount(None)):
            index = self.index(i, 0, None)
            _dfs(index)

        return result


class ButtonDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(ButtonDelegate, self).__init__(parent)
        self.__mouse_pos = None  # type: QPoint
        self.__is_pressed = False

    def editorEvent(self, event, model, option, index):
        # type: (QEvent, QAbstractItemModel, QStyleOptionViewItem, QModelIndex) -> bool
        self.__mouse_pos = event.pos()
        if event.type() in (QEvent.Enter, QEvent.MouseMove):
            # self.__mouse_pos = event.pos()
            print 'enter/move'
            option.widget.update(index)

        elif event.type() == QEvent.Leave:
            print 'leave'
            self.__mouse_pos = None
            option.widget.update(index)

        elif event.type() in (QEvent.MouseButtonPress, QEvent.MouseButtonDblClick) and event.button() == Qt.LeftButton:
            print 'click'
            button_opt = self.__get_option(option)
            self.__is_pressed = button_opt.rect.contains(event.pos())
            option.widget.update(index)

            if event.type() == QEvent.MouseButtonDblClick:
                return True
        
        elif event.type() == QEvent.MouseButtonRelease:
            print 'release'
            self.__is_pressed = False
            option.widget.update(index)

        return super(ButtonDelegate, self).editorEvent(event, model, option, index)

    def paint(self, painter, option, index):
        # type: (QPainter, QStyleOptionViewItem, QModelIndex) -> NoReturn
        super(ButtonDelegate, self).paint(painter, option, index)

        button_opt = self.__get_option(option)

        # button_opt.state &= ~QStyle.State_HasFocus
        if self.__mouse_pos is not None and button_opt.rect.contains(self.__mouse_pos):
            button_opt.state |= QStyle.State_HasFocus
            if self.__is_pressed:
                button_opt.state |= QStyle.State_On
            else:
                button_opt.state |= QStyle.State_MouseOver
        else:
            button_opt.state &= ~QStyle.State_MouseOver

        option.widget.style().drawControl(QStyle.CE_PushButton, button_opt, painter)

    def __get_option(self, option):
        # type: (QStyleOptionViewItem) -> QStyleOptionButton
        button_opt = QStyleOptionButton()
        button_opt.initFrom(option.widget)
        button_opt.text = 'xxxx'
        button_opt.rect = QRect(option.rect)
        button_opt.rect.setLeft(option.rect.right() - 32)

        style = option.widget.style()
        text_rect = style.subElementRect(QStyle.SE_PushButtonContents, button_opt)
        margin = style.pixelMetric(QStyle.PM_ButtonMargin, button_opt) * 2
        text_width = button_opt.fontMetrics.width(button_opt.text)
        if text_rect.width() < text_width + margin:
            button_opt.rect.setLeft(button_opt.rect.left() - (text_width - text_rect.width() + margin))

        return button_opt


class RowPaddingDelegate(QItemDelegate):

    def sizeHint(self, option, index):
        # type: (QStyleOptionViewItem, QModelIndex) -> QSize
        size = super(RowPaddingDelegate, self).sizeHint(option, index)
        if index.column() == 0:
            size.setWidth(size.width() + 10)
        return size


class _LayerTreeView(QTreeView):

    def __init__(self, parent=None):
        super(_LayerTreeView, self).__init__(parent)
        self.setModel(_LayerTreeModel())
        self.d = ButtonDelegate()
        self.setItemDelegateForColumn(1, self.d)

    def setup_ui(self):
        pass


class MainWindow(qu.MainWindowBase):

    def __init__(self):
        super(MainWindow, self).__init__()
        qm.load_plugins()
        self.__layer_tree = _LayerTreeView()

    def _setup_ui(self, central_widget):
        # type: (QWidget) -> NoReturn
        self.setWindowTitle(u'qmSceneLayer Editor')

        self.__layer_tree.setup_ui()
        self.__layer_tree.expandAll()

        def test():
            model = self.__layer_tree.model()
            print '====='
            def p(idx):
                parent = model.parent(idx)
                return not parent.isValid() or self.__layer_tree.isExpanded(parent)
            for index in model.traverse(p):
                item = index.internalPointer()
                print item.name, self.__layer_tree.isExpanded(index)
        btn = QPushButton('aaa')
        btn.clicked.connect(test)

        central_widget.setLayout(qu.vbox(
            self.__layer_tree,
            btn,
            contents_margins=0
        ))

    def _shutdown_ui(self):
        try:
            # qm.unload_plugins()
            pass
        except RuntimeError:
            pass


def main():
    class App(qu.AppBase):
        def __init__(self):
            super(App, self).__init__()

        def _create_window(self):
            # type: () -> QMainWindow
            return MainWindow()

    app = App()
    app.execute()


if __name__ == '__main__':
    main()
