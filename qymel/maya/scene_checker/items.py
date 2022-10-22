# coding: utf-8
from typing import *
from enum import Flag, auto
from abc import abstractmethod
import math


class CheckItem(object):

    _label = ''
    _category = ''
    _description = ''
    _eps = 1e-4

    @property
    def label(self) -> str:
        return self.__class__._label

    @property
    def category(self) -> str:
        return self.__class__._category

    @property
    def description(self) -> str:
        return self.__class__._description

    def __init__(self):
        pass

    def __str__(self) -> str:
        return f'[{self.category}][{self.label}] {self.description}'

    def execute(self) -> Sequence['CheckResult']:
        return self._execute() or [CheckResult.success(self)]

    def modify(self, error: 'CheckResult') -> 'CheckResult':
        return self._modify(error) or CheckResult.success(self)

    @abstractmethod
    def _execute(self) -> Optional[Sequence['CheckResult']]:
        raise NotImplementedError()

    def _modify(self, error: 'CheckResult') -> Optional['CheckResult']:
        pass

    def float_equals(self, lhs: float, rhs: float) -> bool:
        return math.fabs(lhs - rhs) < self.__class__._eps

    def float_seq_equals(self, lhs: Sequence[float], rhs: Sequence[float]) -> bool:
        if len(lhs) != len(lhs):
            return False
        return all(self.float_equals(l, r) for l, r in zip(lhs, rhs))


class CheckResultStatus(Flag):
    NONE = auto()
    SUCCESS = auto()
    MODIFIABLE = auto()
    WARNING = auto()
    ERROR = auto()

    def __str__(self) -> str:
        return super().__str__().split('.')[-1]


class CheckResult(object):

    @staticmethod
    def success(item: CheckItem) -> 'CheckResult':
        return CheckResult(item, CheckResultStatus.SUCCESS, '', [])

    @staticmethod
    def warning(item: CheckItem, message: str, modifiable: bool, nodes: Optional[List[str]] = None) -> 'CheckResult':
        status = CheckResultStatus.WARNING
        if modifiable:
            status |= CheckResultStatus.MODIFIABLE
        return CheckResult(item, status, message, nodes or [])

    @staticmethod
    def error(item: CheckItem, message: str, modifiable: bool, nodes: Optional[List[str]] = None) -> 'CheckResult':
        status = CheckResultStatus.ERROR
        if modifiable:
            status |= CheckResultStatus.MODIFIABLE
        return CheckResult(item, status, message, nodes or [])

    @property
    def item(self) -> CheckItem:
        return self.__item

    @property
    def status(self) -> CheckResultStatus:
        return self.__status

    @property
    def message(self) -> str:
        return self.__message

    @property
    def nodes(self) -> List[str]:
        return self.__nodes

    @property
    def is_success(self) -> bool:
        return self.status == CheckResultStatus.SUCCESS

    @property
    def is_warning(self) -> bool:
        return self.status & CheckResultStatus.WARNING == CheckResultStatus.WARNING

    @property
    def is_error(self) -> bool:
        return self.status & CheckResultStatus.ERROR == CheckResultStatus.ERROR

    @property
    def is_modifiable(self) -> bool:
        return self.status & CheckResultStatus.MODIFIABLE == CheckResultStatus.MODIFIABLE

    def __init__(self, item: CheckItem, status: CheckResultStatus, message: str, nodes: List[str]):
        self.__item = item
        self.__status = status
        self.__message = message
        self.__nodes = nodes

    def __str__(self) -> str:
        return f'[{self.item.category}][{self.item.label}] {self.status} {self.message}'
