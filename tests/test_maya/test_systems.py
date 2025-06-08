import unittest
import os

import maya.standalone
maya.standalone.initialize(name='python')

import maya.cmds as cmds
import qymel.maya as qm


class TestFileInfo(unittest.TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        cmds.fileInfo('key1', 'value1')
        cmds.fileInfo('key2', 'value2')

    def test_static(self):
        infos = qm.FileInfo.ls()
        self.assertEqual(len(infos), 2)
        self.assertEqual(infos[0].key, 'key1')
        self.assertEqual(infos[0].value, 'value1')
        self.assertEqual(infos[1].key, 'key2')
        self.assertEqual(infos[1].value, 'value2')

        info = qm.FileInfo.query('key1')
        self.assertEqual(info.key, 'key1')
        self.assertEqual(info.value, 'value1')

        info = qm.FileInfo.query('aaa')
        self.assertIsNone(info)

        info = qm.FileInfo.create('111', '222')
        self.assertEqual(info.key, '111')
        self.assertEqual(info.value, '222')
        self.assertEqual(info.value, cmds.fileInfo('111', query=True)[0])

    def test_update(self):
        info = qm.FileInfo('key1', 'value1')
        self.assertEqual(info.value, cmds.fileInfo('key1', query=True)[0])
        info.update('aaa')
        self.assertEqual(info.value, 'aaa')
        self.assertEqual(info.value, cmds.fileInfo('key1', query=True)[0])

    def test_remove(self):
        info = qm.FileInfo('key1', 'value1')
        self.assertEqual('value1', cmds.fileInfo('key1', query=True)[0])
        info.remove()
        self.assertEqual([], cmds.fileInfo('key1', query=True))


class TestScene(unittest.TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)

    def test_path(self):
        scene_path = cmds.file(rename='aaa.ma')
        self.assertEqual(qm.Scene.name(), os.path.basename(scene_path))
        self.assertEqual(qm.Scene.path(), scene_path)

        path = scene_path.replace('/', os.sep)
        self.assertEqual(qm.Scene.normalize_path(path), scene_path)

    def test_new(self):
        nodes = cmds.ls()
        cmds.polyCube()
        qm.Scene.new(True)
        self.assertSequenceEqual(nodes, cmds.ls())

    def test_rename(self):
        scene_path = cmds.file(rename='aaa.ma')
        cmds.file(new=True, force=True)
        qm.Scene.rename('aaa.ma')
        self.assertEqual(scene_path, cmds.file(query=True, sceneName=True))

    def test_open_rename_save(self):
        tmp_scene_path = 'C:/tmp/test.ma'
        cmds.file(new=True, force=True)
        cmds.polyCube()
        cmds.file(rename=tmp_scene_path)
        cmds.file(save=True, force=True)

        cmds.file(new=True, force=True)
        cmds.file(tmp_scene_path, open=True)
        tmp_scene_nodes = cmds.ls()

        cmds.file(new=True, force=True)
        qm.Scene.open(tmp_scene_path)
        self.assertSequenceEqual(tmp_scene_nodes, cmds.ls())

        tmp_scene_path_1 = 'C:/tmp/test1.ma'
        cmds.file(tmp_scene_path, open=True)
        qm.Scene.rename(tmp_scene_path_1)
        self.assertEqual(tmp_scene_path_1, cmds.file(query=True, sceneName=True))

        cmds.file(new=True, force=True)
        cmds.polyCube()
        cmds.file(rename=tmp_scene_path)
        cmds.file(save=True, force=True)
        qm.Scene.save(tmp_scene_path_1)
        self.assertEqual(tmp_scene_path_1, cmds.file(query=True, sceneName=True))

        cmds.file(tmp_scene_path, open=True)
        nodes = cmds.ls()
        cmds.file(tmp_scene_path_1, open=True)
        self.assertSequenceEqual(nodes, cmds.ls())

        os.remove(tmp_scene_path)
        os.remove(tmp_scene_path_1)

    def test_modify(self):
        self.assertFalse(qm.Scene.is_mofieied())
        cmds.polyCube()
        self.assertTrue(qm.Scene.is_mofieied())

    def test_import(self):
        tmp_scene_path = 'C:/tmp/test.ma'
        cmds.polyCube()
        cmds.file(rename=tmp_scene_path)
        cmds.file(save=True, force=True)

        cmds.file(new=True, force=True)
        cmds.file(tmp_scene_path, i=True)
        nodes = cmds.ls()

        cmds.file(new=True, force=True)
        qm.Scene.import_file(tmp_scene_path)
        self.assertSequenceEqual(nodes, cmds.ls())

    def test_reference(self):
        tmp_scene_path = 'C:/tmp/test.ma'
        cmds.polyCube()
        cmds.file(rename=tmp_scene_path)
        cmds.file(save=True, force=True)

        cmds.file(new=True, force=True)
        cmds.file(tmp_scene_path, reference=True)
        nodes = cmds.ls()

        cmds.file(new=True, force=True)
        qm.Scene.reference_file(tmp_scene_path)
        self.assertSequenceEqual(nodes, cmds.ls())

    def test_file_info(self):
        cmds.fileInfo('key1', 'value1')
        cmds.fileInfo('key2', 'value2')

        infos = qm.Scene.file_infos()
        self.assertEqual(len(infos), 2)
        self.assertEqual(infos[0].key, 'key1')
        self.assertEqual(infos[0].value, 'value1')
        self.assertEqual(infos[1].key, 'key2')
        self.assertEqual(infos[1].value, 'value2')

        info = qm.Scene.file_info('key1')
        self.assertEqual(info.key, 'key1')
        self.assertEqual(info.value, 'value1')


class TestFileRule(unittest.TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        self.rules = {}
        rules = cmds.workspace(query=True, fileRule=True)
        for i in range(0, len(rules), 2):
            self.rules[rules[i]] = rules[i + 1]

    def test_static(self):
        rules = qm.FileRule.ls()
        self.assertEqual(len(rules), len(self.rules))
        for rule in rules:
            self.assertIn(rule.key, self.rules)
            self.assertEqual(rule.value, self.rules[rule.key])

        rule = qm.FileRule.query('scene')
        self.assertEqual(rule.key, 'scene')
        self.assertEqual(rule.value, cmds.workspace(fileRuleEntry='scene'))

        rule = qm.FileRule.query('aaa')
        self.assertIsNone(rule)

        rule = qm.FileRule.create('111', '222')
        self.assertEqual(rule.key, '111')
        self.assertEqual(rule.value, '222')
        self.assertEqual(rule.value, cmds.workspace(fileRuleEntry='111'))
        cmds.workspace(removeFileRuleEntry='111')  # revert

    def test_update(self):
        value = cmds.workspace(fileRuleEntry='scene')[0]
        rule = qm.FileRule('scene', value)
        self.assertEqual(rule.value, value)
        rule.update('aaa')
        self.assertEqual(rule.value, 'aaa')
        cmds.workspace(fileRule=(rule.key, value))  # revert

    def test_remove(self):
        cmds.workspace(fileRule=('111', '222'))
        self.assertEqual(cmds.workspace(fileRuleEntry='111'), '222')
        rule = qm.FileRule('111', '222')
        rule.remove()
        self.assertEqual(cmds.workspace(fileRuleEntry='111'), '')


class TestWorkspaceVariable(unittest.TestCase):

    def setUp(self) -> None:
        cmds.file(new=True, force=True)
        cmds.workspace(variable=('key1', 'value1'))
        cmds.workspace(variable=('key2', 'value2'))

    def tearDown(self) -> None:
        cmds.workspace(removeVariableEntry='key1')
        cmds.workspace(removeVariableEntry='key2')

    def test_static(self):
        variables = qm.WorkspaceVariable.ls()
        self.assertEqual(len(variables), 2)
        self.assertEqual(variables[0].key, 'key1')
        self.assertEqual(variables[0].value, 'value1')
        self.assertEqual(variables[1].key, 'key2')
        self.assertEqual(variables[1].value, 'value2')

        variable = qm.WorkspaceVariable.query('key1')
        self.assertEqual(variable.key, 'key1')
        self.assertEqual(variable.value, cmds.workspace(variableEntry='key1'))

        variable = qm.WorkspaceVariable.query('aaa')
        self.assertIsNone(variable)

        variable = qm.WorkspaceVariable.create('111', '222')
        self.assertEqual(variable.key, '111')
        self.assertEqual(variable.value, '222')
        self.assertEqual(variable.value, cmds.workspace(variableEntry='111'))
        cmds.workspace(removeVariableEntry='111')  # revert

    def test_update(self):
        variable = qm.WorkspaceVariable('key1', 'value1')
        self.assertEqual(variable.value, cmds.workspace(variableEntry='key1'))
        variable.update('aaa')
        self.assertEqual(variable.value, 'aaa')
        self.assertEqual(variable.value, cmds.workspace(variableEntry='key1'))

    def test_remove(self):
        cmds.workspace(variable=('111', '222'))
        variable = qm.WorkspaceVariable('111', '222')
        self.assertEqual('222', cmds.workspace(variableEntry='111'))
        variable.remove()
        self.assertEqual('', cmds.workspace(variableEntry='111'))


class TestWorkspace(unittest.TestCase):
    pass


class TestFileTranslator(unittest.TestCase):
    pass


class TestNamespace(unittest.TestCase):
    pass
