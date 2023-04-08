# coding: utf-8
from typing import *

import functools
import itertools

from . import items as _items


class CheckItemGroup(object):

    @property
    def label(self) -> str:
        return self.__label

    def __init__(self, label: str):
        self.__label = label
        self.__items: Dict[str, List[_items.CheckItem]] = {}
        self.__category_orders: Dict[str, int] = {}
        self.__results: Dict[_items.CheckItem, Optional[Sequence[_items.CheckResult]]] = {}

    def append(self, item: _items.CheckItem):
        if item.category not in self.__items:
            self.__items[item.category] = []
        self.__items[item.category].append(item)

    def extend(self, items: Sequence[_items.CheckItem]):
        for item in items:
            self.append(item)

    def categories(self) -> Sequence[str]:
        def _compare(lhs: str, rhs: str):
            # まずcategory_orderで比較
            lhs_id = self.__category_orders.get(lhs, -1)
            rhs_id = self.__category_orders.get(rhs, -1)
            if lhs_id >= 0 and rhs_id >= 0:
                if lhs_id == rhs_id:
                    return 0
                if lhs_id < rhs_id:
                    return -1
                return 1
            if lhs_id >= 0:
                return -1
            if rhs_id >= 0:
                return 1
            # 次に文字列比較
            if lhs == rhs:
                return 0
            if lhs < rhs:
                return -1
            return 1

        return sorted(self.__items.keys(), key=functools.cmp_to_key(_compare))

    def set_category_order(self, categories: Sequence[str]):
        self.__category_orders = {category: i for i, category in enumerate(categories)}

    def items(self, category: str = None) -> Sequence[_items.CheckItem]:
        if category is not None:
            return self.__items[category]

        items = []
        for category in self.categories():
            items.extend(self.__items[category])
        return items

    def clear_results(self):
        self.__results = {}

    def is_executed(self, item: _items.CheckItem) -> bool:
        return item in self.__results

    def execute(self, item: _items.CheckItem) -> Sequence[_items.CheckResult]:
        results = item.execute()
        self.__results[item] = results
        return results

    def execute_all(self):
        self.clear_results()
        for item in self.items():
            self.execute(item)

    def modify(self, error: _items.CheckResult) -> None:
        error.item.modify(error)

    def modify_all(self):
        for result in itertools.chain.from_iterable(self.__results.values()):
            if isinstance(result, _items.CheckResult) and result.is_modifiable:
                self.modify(result)

    def results(self, item: Optional[_items.CheckItem] = None) -> Sequence[_items.CheckResult]:
        if item is not None:
            return self.__results.get(item, [])

        results = []
        for items in self.__items.values():
            results.extend(itertools.chain.from_iterable(self.__results.get(item, []) for item in items))
        return results

    def warnings(self) -> Sequence[_items.CheckResult]:
        return [result for result in self.results() if result.status & _items.CheckResultStatus.WARNING]

    def errors(self) -> Sequence[_items.CheckResult]:
        return [result for result in self.results() if result.status & _items.CheckResultStatus.ERROR]

    def is_success(self) -> bool:
        return all(result.is_success for result in self.results())

    def has_warnings(self) -> bool:
        return any(result.is_warning for result in self.results())

    def has_errors(self) -> bool:
        return any(result.is_error for result in self.results())

    def has_modifiables(self) -> bool:
        return any(result.is_modifiable for result in self.results())