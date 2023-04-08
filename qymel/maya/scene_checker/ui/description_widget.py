# coding: utf-8
from typing import *

import itertools

import maya.cmds as _cmds

from qymel.ui.pyside_module import *
from qymel.ui import layouts as _layouts
from qymel.ui.widgets import models as _models

from .. import items as _items
from . import icons as _icons


class DescriptionWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.__icon = QLabel()

        self.__label = QLabel()
        font = self.__label.font()
        font.setBold(True)
        font.setPointSize(10)
        self.__label.setFont(font)

        self.__description = QLabel()
        self.__description.setWordWrap(True)
        self.__description.setMargin(5)

        self.__results = _ResultItemWidget()
        self.__results.selection_changed.connect(
            lambda items: self.__sync_result_selection(items, True, False)
        )

        self.__result_group_title = 'チェック結果（$COUNT項目）'
        self.__result_group = QGroupBox(self.__result_group_title)
        self.__result_group.setLayout(_layouts.vbox(
            self.__results,
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
        self.__results.clear()
        self.__nodes.clear()
        self.setEnabled(False)

        self.__result_group.setTitle(self.__result_group_title.replace('$COUNT', '0'))
        self.__nodes_group.setTitle(self.__nodes_group_title.replace('$COUNT', '0'))

    def load_from(self, category: Optional[str], item: Optional[_items.CheckItem], results: Sequence[_items.CheckResult] = []):
        self.clear()

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
                self.__results.append('OK', [])
            else:
                for result in results:
                    self.__results.append(result.message, result.nodes)
                    for node in result.nodes:
                        self.__nodes.append(node, [node])

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

    def __init__(self, label: str, nodes: List[str]):
        self.label = label
        self.nodes = nodes


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
        self.__view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.__view.selectionModel().selectionChanged.connect(self.__select_nodes)
        self.__view.selectionModel().selectionChanged.connect(lambda _1, _2: self.selection_changed.emit(self.selected_items()))
        self.__view.setEnabled(True)

        self.setLayout(_layouts.vbox(
            self.__view,
            contents_margins=0
        ))

    def clear(self):
        self.__model.clear()

    def append(self, label: str, nodes: List[str]):
        self.__model.append(_ResultItem(label, nodes))

    def items(self) -> List[_ResultItem]:
        return self.__model.items()

    def select(self, items: Iterable[_ResultItem], replace: bool = False):
        selection = QItemSelection()
        for item in items:
            item_index = self.__model.item_index_of(item)
            index = self.__model.index(item_index, 0)
            selection.merge(QItemSelection(index, index), QItemSelectionModel.Select)

        command = QItemSelectionModel.ClearAndSelect if replace else QItemSelectionModel.Select
        self.__view.selectionModel().select(selection, command)

    def selected_items(self) -> List[_ResultItem]:
        indices = self.__view.selectionModel().selectedIndexes()
        return self.__model.items(indices)

    def __select_nodes(self):
        indices = self.__view.selectionModel().selectedIndexes()
        items = self.__model.items(indices)
        nodes = list(itertools.chain.from_iterable(item.nodes for item in items))
        _cmds.select(nodes, replace=True)
