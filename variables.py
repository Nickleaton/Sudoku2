from typing import List, Dict

from pulp import LpVariable

from region import Region


class Variables:

    def __init__(self):
        self._choices = LpVariable.dicts("Choice", (self.VALUES, self.ROWS, self.COLUMNS), cat='Binary')
        self._values = LpVariable.dicts("Values", (self.ROWS, self.COLUMNS), min(self.ALL), max(self.ALL),
                                        cat='Integer')

    # noinspection PyPep8Naming
    @property
    def ALL(self) -> List[int]:
        return [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # noinspection PyPep8Naming
    @property
    def VALUES(self) -> List[int]:
        return self.ALL

    # noinspection PyPep8Naming
    @property
    def ROWS(self) -> List[int]:
        return self.ALL

    # noinspection PyPep8Naming
    @property
    def COLUMNS(self) -> List[int]:
        return self.ALL

    @property
    def choices(self) -> Dict[str, LpVariable]:
        return self._choices

    @property
    def values(self) -> Dict[str, LpVariable]:
        return self._values

    def valid(self, n: int) -> bool:
        return n in self.VALUES

    def column_regions(self):
        for column in self.COLUMNS:
            yield Region(f"Column_{column}", [[column, row] for row in self.ROWS])

    def row_regions(self):
        for row in self.ROWS:
            yield Region(f"Row_{row}", [[column, row] for column in self.COLUMNS])

    def box_regions(self):
        for i in range(3):
            for j in range(3):
                yield Region(f"Box_{i + 1}_{j + 1}",
                             [[3 * i + a + 1, 3 * j + b + 1] for a in range(3) for b in range(3)])
