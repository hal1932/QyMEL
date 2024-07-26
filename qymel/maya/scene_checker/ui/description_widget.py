# coding: utf-8
from typing import *

import itertools
import functools
import dataclasses

import maya.cmds as _cmds

from qymel.ui.pyside_module import *
from qymel.ui import layouts as _layouts
from qymel.ui.widgets import models as _models

from .. import items as _items
from . import icons as _icons


class DescriptionWidget(QWidget):

    modify_requested = Signal(list)

    def __init__(self):
        super().__init__()

        self.__category = None
        self.__item = None
        self.__results = []

        self.__icon = QLabel()

        self.__label = QLabel()
        self.__label.setStyleSheet('font-weight: bold; font-size: 10pt;')

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

        self.__node_items = _ResultItemWidget()
        self.__node_items.selection_changed.connect(
            lambda items: self.__sync_result_selection(items, False, True)
        )

        self.__nodes_group_title = '対象オブジェクト（$COUNT個）'
        self.__nodes_group = QGroupBox(self.__nodes_group_title)
        self.__nodes_group.setLayout(_layouts.vbox(
            self.__node_items,
        ))

        self.__modify_selected = QPushButton('選択した項目を自動修正')
        self.__modify_selected.clicked.connect(self.__modify_selected_items)

        self.__modify_all = QPushButton('すべての項目を自動修正')
        self.__modify_all.clicked.connect(self.__modify_all_items)

        controls = QWidget()
        controls.setLayout(_layouts.hbox(
            self.__modify_selected,
            self.__modify_all,
            contents_margins=0
        ))

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
        self.__node_items.clear()
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

            if len(results) == 1 and results[0].is_success:
                self.__result_items.append(results[0], 'OK', [], _items.CheckResultStatus.SUCCESS)
            else:
                for result in results:
                    self.__result_items.append(result)
                nodes = set(itertools.chain.from_iterable(result.nodes for result in results))
                for node in sorted(nodes):
                    self.__node_items.append(None, node, [node], _items.CheckResultStatus.NONE)

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

        self.__modify_all.setEnabled(enable_modification)

        enable_modification = any(r.is_modifiable for r in self.__result_items.selected_items())
        self.__modify_selected.setEnabled(enable_modification)

    def refresh(self):
        self.load_from(self.__category, self.__item, self.__results)

    def __sync_result_selection(self, selection: List['_ResultItem'], from_results: bool, from_nodes: bool):
        if from_results:
            # results -> nodes
            node_items = []
            selected_nodes = list(itertools.chain.from_iterable(item.nodes for item in selection))
            for item in self.__node_items.items():
                if item.nodes[0] in selected_nodes:
                    node_items.append(item)
            self.__node_items.select(node_items, True)

        if from_nodes:
            # nodes -> results
            pass

        selected_results = self.__result_items.selected_items()
        has_modifiables = any(r.result.is_modifiable for r in selected_results)
        self.__modify_selected.setEnabled(has_modifiables)

        has_modifiables = any(r.result.is_modifiable for r in self.__result_items.items())
        self.__modify_all.setEnabled(has_modifiables)

    def __modify_selected_items(self):
        selected_results = self.__result_items.selected_items()
        modifiable_results = [r.result for r in selected_results if r.result.is_modifiable]
        self.modify_requested.emit(modifiable_results)

    def __modify_all_items(self):
        results = self.__result_items.items()
        modifiable_results = [r.result for r in results if r.result.is_modifiable]
        self.modify_requested.emit(modifiable_results)


@dataclasses.dataclass(frozen=True)
class _ResultItem:
    label: str
    nodes: List[str]
    status: _items.CheckResultStatus
    result: _items.CheckResult


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

    def append(self,
               result: _items.CheckResult,
               label: Optional[str] = None,
               nodes: Optional[List[str]] = None,
               status: Optional[_items.CheckResultStatus] = None
               ):
        label = label or result.message
        nodes = nodes or result.nodes
        status = status or result.status
        self.__model.append(_ResultItem(label, nodes, status, result))

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
