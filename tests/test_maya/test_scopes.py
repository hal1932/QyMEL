# coding: utf-8
from __future__ import absolute_import, print_function
from six import *
from six.moves import *
from typing import *

import unittest
import functools
import operator

import maya.standalone
maya.standalone.initialize(name='python')

import maya.cmds as cmds
import maya.api.OpenMaya as om2
import qymel.maya as qm


class TestUndoScope(unittest.TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)

    def test_class(self):
        nodes = cmds.ls()
        with qm.UndoScope():
            cmds.polyCube()
        cmds.undo()
        self.assertSequenceEqual(nodes, cmds.ls())


class TestKeepSelectionScope(unittest.TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)

    def test_class(self):
        cmds.polyCube()
        nodes = cmds.ls(sl=True)
        with qm.KeepSelectionScope():
            cmds.select(clear=True)
        self.assertSequenceEqual(nodes, cmds.ls(sl=True))


'''
ViewPauseScopeは単体テストが書けないから何もしない
'''
# class TestViewportPauseScope(unittest.TestCase):
#     pass
