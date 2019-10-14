# coding: utf-8
from __future__ import absolute_import
from typing import *
from six.moves import *

import os
import sys


TEMPLATE = '''
class ${ClassName}(${BaseClassName}):

    _mfn_type = om2.MFn.${TypeName}
    _mfn_set = om2.${MFnSetName}
    _mel_type = '${MelTypeName}'

    @staticmethod
    def ls(*args, **kwargs):
        # type: (Any, Any) -> List[${ClassName}]
        kwargs['type'] = ${ClassName}._mel_type
        return _graphs.ls_nodes(*args, **kwargs)

    @staticmethod
    def create(**kwargs):
        # type: (Any) -> ${ClassName}
        return _graphs.create_node(${ClassName}._mel_type, **kwargs)

    def __init__(self, obj):
        # type: (Union[om2.MObject, str]) -> NoReturn
        if isinstance(obj, (str, unicode)):
            obj, _ = _graphs.get_mobject(obj)
        super(${ClassName}, self).__init__(obj)

'''

source_file = sys.argv[1]
dest_file = os.path.join(os.path.dirname(__file__), 'nodetypes_gen.py')

with open(dest_file, 'w') as wf:
    with open(source_file, 'r') as rf:
        rf.readline()
        for line in rf:
            name, parent, mfn_type, mfn_set, mel_type = line.strip().split(',')
            print name
            source = TEMPLATE
            source = source.replace('${ClassName}', name)
            source = source.replace('${BaseClassName}', parent)
            source = source.replace('${TypeName}', mfn_type)
            source = source.replace('${MFnSetName}', mfn_set)
            source = source.replace('${MelTypeName}', mel_type)
            wf.write(source)

