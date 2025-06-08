import collections.abc
import abc
import enum
import math


class CheckItem(object):

    _label = ''
    _category = ''
    _description = ''
    _eps = 1e-4

    @staticmethod
    def find_from_module(module) -> collections.abc.Sequence['CheckItem']:
        items: list[CheckItem] = []
        for key in dir(module):
            value = getattr(module, key)
            if isinstance(value, type) and issubclass(value, CheckItem) and value != CheckItem:
                items.append(value())
        return items

    @property
    def label(self) -> str:
        return self.__class__._label

    @property
    def category(self) -> str:
        return self.__class__._category

    @property
    def description(self) -> str:
        return self.__class__._description

    def __str__(self) -> str:
        return f'[{self.category}][{self.label}] {self.description}'

    def execute(self) -> collections.abc.Sequence['CheckResult']:
        self.__results: list[CheckResult] = []
        self._execute()
        return self.__results or [CheckResult.success(self)]

    def modify(self, error: 'CheckResult') -> None:
        self._modify(error)

    @abc.abstractmethod
    def _execute(self) -> None:
        raise NotImplementedError()

    def _modify(self, error: 'CheckResult') -> None:
        pass

    def append_warning(self, nodes: str | list[str] | None, message: str, modifiable: bool = False):
        if nodes is not None:
            nodes = [nodes] if isinstance(nodes, str) else nodes
        self.__results.append(CheckResult.warning(self, message, modifiable, nodes))

    def append_error(self, nodes: str | list[str] | None, message: str, modifiable: bool = False):
        if nodes is not None:
            nodes = [nodes] if isinstance(nodes, str) else nodes
        self.__results.append(CheckResult.error(self, message, modifiable, nodes))

    def float_equals(self, lhs: float, rhs: float) -> bool:
        return math.fabs(lhs - rhs) < self.__class__._eps

    def float_seq_equals(self, lhs: collections.abc.Sequence[float], rhs: collections.abc.Sequence[float]) -> bool:
        if len(lhs) != len(lhs):
            return False
        return all(self.float_equals(l, r) for l, r in zip(lhs, rhs))


class CheckResultStatus(enum.Flag):
    NONE = enum.auto()
    SUCCESS = enum.auto()
    MODIFIABLE = enum.auto()
    WARNING = enum.auto()
    ERROR = enum.auto()

    def __str__(self) -> str:
        return super().__str__().split('.')[-1]


class CheckResult(object):

    @staticmethod
    def success(item: CheckItem) -> 'CheckResult':
        return CheckResult(item, CheckResultStatus.SUCCESS, '', [])

    @staticmethod
    def warning(item: CheckItem, message: str, modifiable: bool, nodes: list[str] | None = None) -> 'CheckResult':
        status = CheckResultStatus.WARNING
        if modifiable:
            status |= CheckResultStatus.MODIFIABLE
        return CheckResult(item, status, message, nodes or [])

    @staticmethod
    def error(item: CheckItem, message: str, modifiable: bool, nodes: list[str] | None = None) -> 'CheckResult':
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
    def nodes(self) -> list[str]:
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

    def __init__(self, item: CheckItem, status: CheckResultStatus, message: str, nodes: list[str]):
        self.__item = item
        self.__status = status
        self.__message = message
        self.__nodes = nodes

    def __str__(self) -> str:
        return f'[{self.item.category}][{self.item.label}] {self.status} {self.message}'
