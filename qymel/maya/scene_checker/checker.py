import collections.abc as abc
from . import groups as _groups


class Checker(object):

    @property
    def groups(self) -> abc.Sequence[_groups.CheckItemGroup]:
        return self.__groups

    def __init__(self):
        self.__groups: list[_groups.CheckItemGroup] = []

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

    def execute_group(self, group_name: str) -> _groups.CheckItemGroup|None:
        for group in self.__groups:
            if group == group_name:
                group.execute_all()
                return group
        return None

    def has_results(self) -> bool:
        for group in self.__groups:
            if len(group.results()) > 0:
                return True
        return False

    def has_modifiables(self) -> bool:
        for group in self.__groups:
            if group.has_modifiables:
                return True
        return False

    def modify_all(self):
        for group in self.__groups:
            group.modify_all()
