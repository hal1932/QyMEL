# coding: utf-8
from typing import *

import maya.cmds as cmds
import qymel.maya as qm

from qymel.maya.scene_checker.checker import Checker
from qymel.maya.scene_checker.items import CheckItem, CheckResult


class CubeExistsAtOrigin(CheckItem):

    _label = 'pCube.t'
    _category = 'layout'
    _description = 'pCubeが原点にあるかどうか？'

    def _execute(self) -> Optional[Sequence['CheckResult']]:
        if not cmds.objExists('pCube1'):
            return [CheckResult.error(self, 'pCube1がありません', False)]
        cube: qm.Transform = qm.eval('pCube1')
        if not self.float_seq_equals(cube.t.get(), (0, 0, 0)):
            return [CheckResult.error(self, f'tが(0,0,0)ではありません: {cube.t.get()}', True, [cube.mel_object])]
        return None

    def _modify(self, error: CheckResult) -> Optional[CheckResult]:
        if not cmds.objExists('pCube1'):
            cmds.polyCube()
        for node in error.nodes:
            cmds.setAttr(f'{node}.t', 0, 0, 0, type='double3')
        return None


class CubeNotTriangulated(CheckItem):

    _label = 'pCube.e'
    _category = 'modeling'
    _description = 'pCubeは三角化しない'

    def _execute(self) -> Optional[Sequence['CheckResult']]:
        if not cmds.objExists('pCube1'):
            return [CheckResult.error(self, 'pCube1がありません', False)]
        cube: qm.Transform = qm.eval('pCube1')
        if not cube.shape().edge_count != 6:
            return [CheckResult.error(self, f'三角化されている可能性があります', False, [cube.mel_object])]
        return None


class CubeNotRotated(CheckItem):

    _label = 'pCube.r'
    _category = 'layout'
    _description = 'pCubeが回転していない'

    def _execute(self) -> Optional[Sequence['CheckResult']]:
        if not cmds.objExists('pCube1'):
            return [CheckResult.error(self, 'pCube1がありません', False)]
        cube: qm.Transform = qm.eval('pCube1')
        if not self.float_seq_equals(cube.r.get(), (0, 0, 0)):
            return [CheckResult.error(self, f'rが(0,0,0)ではありません: {cube.r.get()}', True, [cube.mel_object])]
        return None

    def _modify(self, error: CheckResult) -> Optional[CheckResult]:
        if not cmds.objExists('pCube1'):
            cmds.polyCube()
        for node in error.nodes:
            cmds.setAttr(f'{node}.r', 0, 0, 0, type='double3')
        return None


class Empty(CheckItem):

    _label = 'empty'
    _category = ''
    _description = 'aaa'

    def _execute(self) -> Optional[Sequence['CheckResult']]:
        pass


def main():
    checker = Checker()
    checker.set_category_order(['layout', '', 'modeling'])
    checker.append(CubeExistsAtOrigin())
    checker.append(CubeNotTriangulated())
    checker.append(CubeNotRotated())
    checker.append(Empty())

    checker.execute_all()
    for result in checker.results():
        print(result)

    if checker.has_modifiables:
        checker.modify_all()

    checker.execute_all()
    for result in checker.results():
        print(result)


if __name__ == '__main__':
    main()
