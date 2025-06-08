from qymel.ui.app import *
from qymel.ui.layouts import *
from qymel.ui.widgets.models import *
from qymel.ui.widgets.expandable_splitter import *
from qymel.ui.objects.query import *
from qymel.ui.objects.serializer import *


class ListItem(object):
    def __init__(self, index, name, color):
        self.index = index
        self.name = name
        self.color = color


class TableItem(object):
    def __init__(self, index, name, color):
        self.index = index
        self.name = name
        self.color = color


class MyTreeItem(TreeItem):
    def __init__(self, index, name, color):
        super(MyTreeItem, self).__init__()
        self.index = index
        self.name = name
        self.color = color

    def expand(self):
        self.clear_children()
        child = MyTreeItem(self.index + 1, '{}_{}'.format(self.name, self.name.split('_')[0]), self.color)
        self.append_child(child)
        child.append_child(None)


class SerializableWidget(QWidget, SerializableObjectMixin):

    def serialize(self, settings):
        settings.setValue('geom', self.geometry())

    def deserialize(self, settings):
        self.setGeometry(settings.value('geom'))


class MainWindow(MainWindowBase):

    def __init__(self):
        super(MainWindow, self).__init__()

    def _setup_ui(self, central_widget):
        list_view = QListView()
        list_model = ListModel()
        list_view.setModel(list_model)

        list_model.append(ListItem(0, 'aaa', QColor(Qt.red)))
        list_model.append(ListItem(1, 'bbb', QColor(Qt.green)))
        list_model.append(ListItem(2, 'ccc', QColor(Qt.blue)))

        # list_model.insert(1, ListItem(5, 'ddd', None))
        # list_model.insert(2, [ListItem(6, 'eee', None), ListItem(7, 'fff', None)])

        column = ListDefinition(bindings={
            Qt.DisplayRole: 'name',
            Qt.ForegroundRole: 'color',
            Qt.EditRole: 'name'
        })
        list_model.define(column)

        table_view = QTableView()
        table_model = TableModel()
        table_view.setModel(table_model)

        # table_model.append(TableItem(1, 'bbb', QColor(Qt.green)))
        # table_model.append(TableItem(2, 'ccc', QColor(Qt.blue)))
        table_model.extend([
            TableItem(0, 'aaa', QColor(Qt.red)),
            TableItem(1, 'bbb', QColor(Qt.green)),
            TableItem(2, 'ccc', QColor(Qt.blue))
        ])
        # table_model.append(TableItem(0, 'aaa', QColor(Qt.red)))

        header_column = TableHeaderColumnDefinition({Qt.DisplayRole: 'name'})

        column_id = TableColumnDefinition(
            header={
                Qt.DisplayRole: 'id',
                Qt.ForegroundRole: QColor(Qt.red)
            },
            bindings={
                Qt.DisplayRole: 'index',
                Qt.ForegroundRole: 'color'
            }
        )
        column_name = TableColumnDefinition(
            header={
                Qt.DisplayRole: 'name'
            },
            bindings={
                Qt.DisplayRole: 'name',
                Qt.EditRole: 'name',
                Qt.ForegroundRole: 'color'
            }
        )

        table_model.define_header_column(header_column)
        table_model.define_column(0, column_id)
        table_model.define_column(1, column_name)

        tree_view = QTreeView()
        tree_model = TreeModel()
        tree_view.setModel(tree_model)
        tree_view.expanded.connect(lambda index: tree_model.item_from_index(index).expand())

        tree_model.append(MyTreeItem(0, 'aaa', QColor(Qt.red)))
        tree_model.append(MyTreeItem(1, 'bbb', QColor(Qt.green)))
        tree_model.append(MyTreeItem(2, 'ccc', QColor(Qt.blue)))
        tree_model.extend([
            MyTreeItem(0, 'aaa', QColor(Qt.red)),
            MyTreeItem(0, 'aaa', QColor(Qt.red)),
        ])

        tree_model.define_column(0, TreeDefinition(
            header={
                Qt.DisplayRole: 'name',
                Qt.ForegroundRole: QColor(Qt.gray),
            },
            bindings={
                Qt.DisplayRole: 'name',
                Qt.EditRole: 'name',
                Qt.ForegroundRole: 'color'
            }
        ))
        tree_model.define_column(1, TreeDefinition(
            header={
                Qt.DisplayRole: 'color',
            },
            bindings={
                Qt.DisplayRole: 'color',
                Qt.ForegroundRole: 'color'
            }
        ))

        tree_view.expandAll()

        sp1 = ExpandableSplitter()
        sp1.setHandleWidth(10)
        sp1.setOrientation(Qt.Horizontal)

        sp2 = ExpandableSplitter()
        sp2.setHandleWidth(10)
        sp2.setOrientation(Qt.Vertical)

        sp2.addWidget(list_view)
        sp2.addWidget(table_view)

        sp1.addWidget(sp2)
        sp1.addWidget(tree_view)

        central_widget.setLayout(hbox(
            sp1
        ))

        # SerializableWidget
        #   - QVBoxLayout
        #     - QPushButton
        #     - SerializableWidget
        #     - QHBoxLayout
        #       - SerializableWidget
        root = SerializableWidget()
        root_layout = QVBoxLayout()
        root_layout.addWidget(QPushButton())
        root_layout.addWidget(SerializableWidget())
        child_layout = QHBoxLayout()
        child_layout.addWidget(SerializableWidget())
        root_layout.addLayout(child_layout)
        root.setLayout(root_layout)

        serializer = ObjectSerializer()
        settings = QSettings('C:/tmp/test.ini', QSettings.IniFormat)
        serializer.serialize(root, settings)
        settings.sync()

        serializer.deserialize(settings, root)


class App(AppBase):
    def _create_window(self):
        return MainWindow()


def main():
    app = App()
    app.execute()


if __name__ == '__main__':
    main()

