# coding: utf-8
from typing import *

from . import groups as _groups


class Checker(object):

    @property
    def groups(self) -> Sequence[_groups.CheckItemGroup]:
        return self.__groups

    def __init__(self):
        self.__groups: List[_groups.CheckItemGroup] = []

    def append(self, label: str) -> _groups.CheckItemGroup:
        group = _groups.CheckItemGroup(label)
        self.__groups.append(group)
        return group

    def clear_results(self):
        for group in self.__groups:
            group.clear_results()

    def execute_all(self):
        for group in self.__groups:
            group.execute_all()

    def execute_group(self, group_name: str) -> Optional[_groups.CheckItemGroup]:
        for group in self.__groups:
            if group == group_name:
                group.execute_all()
                return group
        return None

    def has_modifiables(self) -> bool:
        for group in self.__groups:
            if group.has_modifiables:
                return True
        return False

    def modify_all(self):
        for group in self.__groups:
            group.modify_all()
