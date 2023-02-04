# coding: utf-8
from typing import *

import os
import traceback


class PythonScript(object):

    def __init__(self, file_path):
        self.file_path = os.path.abspath(file_path)

    def execute(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            globals_dic = {
                '__file__': self.file_path,
                '__name__': '__main__',
            }
            try:
                exec(f.read(), globals_dic)
            except:
                traceback.print_exc()
