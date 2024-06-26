# coding: utf-8
from typing import *

import itertools
import functools

import maya.cmds as _cmds

from qymel.ui.pyside_module import *
from qymel.ui import layouts as _layouts
from qymel.ui.widgets import models as _models

from .. import items as _items
from . import icons as _icons


class DescriptionWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.__category = None
        self.__item = None
        self.__results = []

        self.__icon = QLabel()

        self.__label = QLabel()
        font = self.__label.font()
        font.setBold(True)
        font.setPointSize(10)
        self.__label.setFont(font)

        self.__description = QLabel()
        self.__description.setWordWrap(True)
        self.__description.setMargin(5)

        self.__result_items = _ResultItemWidget()
        self.__result_items.selection_changed.connect(
            lambda items: self.__sync_result_selection(items, True, False)
        )

        self.__result_group_title = 'チェック結果（$COUNT項目）'
        self.__result_group = QGroupBox(self.__result_group_title)
        self.__result_group.setLayout(_layouts.vbox(
            self.__result_items,
        ))

        self.__nodes = _ResultItemWidget()
        self.__nodes.selection_changed.connect(
            lambda items: self.__sync_result_selection(items, False, True)
        )

        self.__nodes_group_title = '対象オブジェクト（$COUNT個）'
        self.__nodes_group = QGroupBox(self.__nodes_group_title)
        self.__nodes_group.setLayout(_layouts.vbox(
            self.__nodes,
        ))

        self.__modify_selected = QPushButton('選択したノードを自動修正')
        self.__modify_all = QPushButton('すべてのノードを自動修正')

        controls = QWidget()
        # controls.setLayout(_layouts.hbox(
        #     self.__modify_selected,
        #     self.__modify_all,
        #     contents_margins=0
        # ))

        self.setLayout(_layouts.vbox(
            _layouts.hbox(
                self.__icon,
                self.__label,
                _layouts.stretch(),
                contents_margins=0
            ),
            self.__description,
            self.__result_group,
            self.__nodes_group,
            controls
        ))

    def clear(self):
        self.__icon.setPixmap(None)
        self.__label.setText('')
        self.__description.setText('')
        self.__result_items.clear()
        self.__nodes.clear()
        self.setEnabled(False)

        self.__result_group.setTitle(self.__result_group_title.replace('$COUNT', '0'))
        self.__nodes_group.setTitle(self.__nodes_group_title.replace('$COUNT', '0'))

    def load_from(self, category: Optional[str], item: Optional[_items.CheckItem], results: Sequence[_items.CheckResult] = []):
        self.clear()

        self.__category = category
        self.__item = item
        self.__results = results

        header = ''
        if category:
            header = f'[{category}]'

        enable_modification = False

        if not item:
            self.__label.setText(header)
        else:
            self.setEnabled(True)
            self.__label.setText(f'{header} {item.label}')
            self.__description.setText(item.description)

            if len(results) == 1 and results[0].status == _items.CheckResultStatus.SUCCESS:
                self.__result_items.append('OK', [], _items.CheckResultStatus.SUCCESS)
            else:
                for result in results:
                    self.__result_items.append(result.message, result.nodes, result.status)
                nodes = set(itertools.chain.from_iterable(result.nodes for result in results))
                for node in sorted(nodes):
                    self.__nodes.append(node, [node], _items.CheckResultStatus.NONE)

            if len(results) > 0:
                if all(r.is_success for r in results):
                    icon = _icons.success()
                elif any(r.is_error for r in results):
                    errors = filter(lambda r: r.is_error, results)
                    is_modifiable = any(e.is_modifiable for e in errors)
                    icon = _icons.error(is_modifiable)
                    enable_modification |= is_modifiable
                else:
                    warnings = filter(lambda r: r.is_warning, results)
                    is_modifiable = any(w.is_modifiable for w in warnings)
                    icon = _icons.warning(is_modifiable)
                    enable_modification |= is_modifiable

                icon_pixmap = icon.pixmap(icon.actualSize(QSize(32, 32)))
                self.__icon.setPixmap(icon_pixmap)

        result_count = len(results)
        self.__result_group.setTitle(self.__result_group_title.replace('$COUNT', str(result_count)))

        nodes_count = sum(len(r.nodes) for r in results)
        self.__nodes_group.setTitle(self.__nodes_group_title.replace('$COUNT', str(nodes_count)))

        self.__modify_selected.setEnabled(enable_modification)
        self.__modify_all.setEnabled(enable_modification)

    def refresh(self):
        self.load_from(self.__category, self.__item, self.__results)

    def __sync_result_selection(self, selection: List['_ResultItem'], from_results: bool, from_nodes: bool):
        if from_results:
            # results -> nodes
            node_items = []
            selected_nodes = list(itertools.chain.from_iterable(item.nodes for item in selection))
            for item in self.__nodes.items():
                if item.nodes[0] in selected_nodes:
                    node_items.append(item)
            self.__nodes.select(node_items, True)

        if from_nodes:
            # nodes -> results
            pass


class _ResultItem(object):

    def __init__(self, label: str, nodes: List[str], status: _items.CheckResultStatus):
        self.label = label
        self.nodes = nodes
        self.status = status


class _ResultItemDelegate(QStyledItemDelegate):

    _pixmaps: Dict[_items.CheckResultStatus, QPixmap] = {}

    def __init__(self):
        super().__init__()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        item = index.model().item(index)

        is_warning = item.status & _items.CheckResultStatus.WARNING == _items.CheckResultStatus.WARNING
        is_error = item.status & _items.CheckResultStatus.ERROR == _items.CheckResultStatus.ERROR
        if not is_warning and not is_error:
            super().paint(painter, option, index)
            return

        is_modifiable = item.status & _items.CheckResultStatus.MODIFIABLE == _items.CheckResultStatus.MODIFIABLE
        icon_creator = functools.partial(_icons.warning if is_warning else _icons.error, is_modifiable)
        status_pix = self.__get_status_pixmap(item.status, icon_creator)

        x = option.rect.left()
        y = option.rect.top()
        w = option.rect.width()
        h = option.rect.height()
        x_offset = status_pix.width() + 2

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
            painter.setPen(option.palette.highlightedText().color())

        painter.drawPixmap(QPoint(x, y), status_pix)
        painter.drawText(QRect(x + x_offset, y, w - x_offset, h), Qt.AlignLeft | Qt.AlignVCenter, item.label)

    def __get_status_pixmap(self, status: _items.CheckResultStatus, creator: Callable[[bool], QIcon]):
        pix = self._pixmaps.get(status)
        if not pix:
            pix = creator().pixmap(QSize(12, 12))
            self._pixmaps[status] = pix
        return pix


class _ResultItemWidget(QWidget):

    selection_changed = Signal(list)

    def __init__(self):
        super().__init__()
        self.__model = _models.ListModel()
        self.__model.define(_models.ListDefinition(bindings={
            Qt.DisplayRole: 'label'
        }))

        self.__view = QListView()
        self.__view.setModel(self.__model)
        self.__view.setItemDelegate(_ResultItemDelegate())
        self.__view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__view.setEnabled(True)

        self.__selection_model = self.__view.selectionModel()
        self.__selection_model.selectionChanged.connect(self.__select_nodes)
        self.__selection_model.selectionChanged.connect(lambda _1, _2: self.selection_changed.emit(self.selected_items()))

        self.setLayout(_layouts.vbox(
            self.__view,
            contents_margins=0
        ))

    def clear(self):
        self.__model.clear()

    def append(self, label: str, nodes: List[str], status: _items.CheckResultStatus):
        self.__model.append(_ResultItem(label, nodes, status))

    def items(self) -> List[_ResultItem]:
        return self.__model.items()

    def select(self, items: Iterable[_ResultItem], replace: bool = False):
        selection = QItemSelection()
        for item in items:
            item_index = self.__model.item_index_of(item)
            index = self.__model.index(item_index, 0)
            selection.merge(QItemSelection(index, index), QItemSelectionModel.Select)

        command = QItemSelectionModel.ClearAndSelect if replace else QItemSelectionModel.Select
        self.__selection_model.select(selection, command)

    def selected_items(self) -> List[_ResultItem]:
        indices = self.__selection_model.selectedIndexes()
        return self.__model.items(indices)

    def __select_nodes(self):
        indices = self.__selection_model.selectedIndexes()
        items = self.__model.items(indices)
        nodes = list(itertools.chain.from_iterable(item.nodes for item in items))
        _cmds.select(nodes, replace=True)
