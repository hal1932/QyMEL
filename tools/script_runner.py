# coding: utf-8
from typing import *

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui

from qymel.ui.pyside_module import *
from qymel.ui.app import AppBase, MainWindowBase
from qymel.ui import layouts


_TQObject = TypeVar('_TQObject', bound=QObject)


def _get_script_editor_panel() -> Optional[QWidget]:
    label = mel.eval('localizedPanelLabel("Script Editor")')
    for panel in cmds.getPanel(type='scriptedPanel') or []:
        if cmds.scriptedPanel(panel, query=True, label=True) == label:
            ptr = omui.MQtUtil.findControl(panel)
            return wrapInstance(int(ptr), QWidget)
    return None


def _find_children(widget: QWidget, qobject_type: Type[_TQObject]) -> List[_TQObject]:
    results: List[_TQObject] = []
    nodes = [widget]
    while len(nodes) > 0:
        node = nodes.pop(-1)
        if isinstance(node, qobject_type):
            results.append(node)
        nodes.extend(node.children())
    return results


class _ScriptItemWidget(QWidget):

    def __init__(self, label: str, script: str, lang: str):
        super().__init__()
        self.__script = script
        self.__lang = lang
        self.__button = QPushButton(label)
        self.__button.setToolTip(script)
        self.__button.clicked.connect(self.__execute)
        self.setLayout(layouts.hbox(
            self.__button,
            contents_margins=0
        ))

    def __execute(self):
        if self.__lang == 'python':
            exec(self.__script)
        elif self.__lang == 'mel':
            mel.eval(self.__script)


class ScriptRunnerWindow(MainWindowBase):

    def __init__(self):
        super().__init__()
        self.__script_items: List[_ScriptItemWidget] = []

    def _setup_ui(self, central_widget: QWidget) -> None:
        self.setWindowTitle('Script Runner')

        self.__reload_items()

        scroll_proxy = QWidget()
        scroll_proxy.setLayout(layouts.vbox(
            *self.__script_items,
            layouts.stretch(),
            contents_margins=0,
        ))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_proxy)

        central_widget.setLayout(layouts.vbox(
            scroll,
        ))

    def __reload_items(self):
        self.__script_items.clear()

        editor_panel = _get_script_editor_panel()
        for editor in _find_children(editor_panel, QPlainTextEdit):
            script = editor.toPlainText()
            lang = None
            if script.startswith('#'):
                lang = 'python'
            elif script.startswith('//'):
                lang = 'mel'
            else:
                continue

            first_line = script.split('\n')[0]
            if 'scriptrunner' not in first_line:
                continue

            label = first_line.split(' ')[-1]

            item = _ScriptItemWidget(label, script, lang)
            self.__script_items.append(item)


class App(AppBase):

    def _create_window(self) -> QMainWindow:
        return ScriptRunnerWindow()


def main():
    app = App()
    app.execute()


if __name__ == '__main__':
    main()
