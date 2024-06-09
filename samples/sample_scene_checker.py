# coding: utf-8
from typing import *

import os

import maya.cmds as cmds
import qymel.maya as qm

from qymel.maya.scene_checker.checker import Checker
from qymel.maya.scene_checker.items import CheckItem, CheckResult
from qymel.maya.scene_checker.ui.checker_window import CheckerWindow

from qymel.ui.pyside_module import QSettings
from qymel.ui.app import AppBase
from qymel.ui.objects.serializer import ObjectSerializer


class CubeExistsAtOrigin(CheckItem):

    _label = 'pCube.t'
    _category = 'layout'
    _description = 'pCubeが原点にあるかどうか？'

    def _execute(self) -> None:
        if not cmds.objExists('pCube1'):
            self.append_error(None, 'pCube1がありません')
            return
        cube: qm.Transform = qm.eval('pCube1')
        if not self.float_seq_equals(cube.t.get(), (0, 0, 0)):
            self.append_error(cube.mel_object, f'tが(0,0,0)ではありません: {cube.t.get()}', True)

    def _modify(self, error: CheckResult) -> None:
        if not cmds.objExists('pCube1'):
            cmds.polyCube()
        for node in error.nodes:
            cmds.setAttr(f'{node}.t', 0, 0, 0, type='double3')


class CubeNotTriangulated(CheckItem):

    _label = 'pCube.e'
    _category = 'modeling'
    _description = 'pCubeは三角化しない'

    def _execute(self) -> None:
        if not cmds.objExists('pCube1'):
            self.append_error(None, 'pCube1がありません')
            return
        cube: qm.Transform = qm.eval('pCube1')
        if not cube.shape().edge_count != 6:
            self.append_error(cube.mel_object, f'三角化されている可能性があります')


class CubeNotRotated(CheckItem):

    _label = 'pCube.r'
    _category = 'layout'
    _description = 'pCubeが回転していない'

    def _execute(self) -> None:
        if not cmds.objExists('pCube1'):
            self.append_error(None, 'pCube1がありません')
            return
        cube: qm.Transform = qm.eval('pCube1')
        if not self.float_seq_equals(cube.r.get(), (0, 0, 0)):
            self.append_error([cube.mel_object], f'rが(0,0,0)ではありません: {cube.r.get()}', True)
            self.append_error([cube.shape().mel_object], 'aaa', False)

    def _modify(self, error: CheckResult) -> None:
        if not cmds.objExists('pCube1'):
            cmds.polyCube()
        for node in error.nodes:
            cmds.setAttr(f'{node}.r', 0, 0, 0, type='double3')


class Dummy1(CheckItem):

    _label = 'dummy1'
    _category = ''
    _description = 'aaa1\nbbb'

    def _execute(self) -> None:
        self.append_warning(None, '警告', True)


class Dummy2(CheckItem):

    _label = 'dummy2'
    _category = ''
    _description = 'aaa2'

    def _execute(self) -> None:
        self.append_warning(None, '警告')


class App(AppBase):

    def __init__(self, checker):
        super().__init__()
        self.checker = checker

    def _create_window(self):  # type: () -> QMainWindow
        window = CheckerWindow(self.checker)

        settings = QSettings(os.path.join(os.environ['TEMP'], window.absolute_name), QSettings.IniFormat)
        serializer = ObjectSerializer()

        def _restore_ui():
            serializer.deserialize(settings, window)

        def _store_ui():
            serializer.serialize(window, settings)
            settings.sync()

        window.after_setup_ui.connect(_restore_ui)
        window.before_shutdown_ui.connect(_store_ui)

        return window


def main():
    checker = Checker()

    group1 = checker.append('group1')
    group1.set_category_order(['', 'layout', 'modeling'])
    group1.append(CubeExistsAtOrigin())
    group1.append(CubeNotTriangulated())
    group1.append(CubeNotRotated())
    group1.append(Dummy1())

    group2 = checker.append('group2')
    group2.set_category_order(['modeling', 'layout', ''])
    group2.append(CubeNotTriangulated())
    group2.append(Dummy1())
    group2.append(Dummy2())

    # GUI
    app = App(checker)
    app.execute()

    # # CUI
    # checker.execute_all()
    # print('=================')
    # for group in checker.groups:
    #     print(group.label)
    #     for result in group.results():
    #         print(result)
    #
    # if checker.has_modifiables():
    #     checker.modify_all()
    #
    # checker.execute_all()
    # print('=================')
    # for group in checker.groups:
    #     print(group.label)
    #     for result in group.results():
    #         print(result)


if __name__ == '__main__':
    main()
