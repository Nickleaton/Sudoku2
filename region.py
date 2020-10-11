from typing import List, Tuple

from pulp import LpVariable, lpSum


class Region:

    def __init__(self, name: str, cells: List[Tuple[int, int]]) -> None:
        self.name = name
        self.cells = cells

    def unique_constraints(self, values: List[int], choices: LpVariable) -> List:
        return [
            (
                lpSum([choices[value][row][column] for row, column in self.cells]) <= 1,
                f"Unique_{self.name}_{value}"
            )
            for value in values
        ]

    def __repr__(self):
        result = self.name + "\n"
        for x, y in self.cells:
            result += f"    {x} {y}\n"
        return result


class Line(Region):

    def __init__(self, r1: int, c1: int, r2: int, c2: int):
        row = range(r1, r2 + 1, 1) if r1 < r2 else range(r1, r2 - 1, -1)
        col = range(c1, c2 + 1, 1) if c1 < c2 else range(c1, c2 - 1, -1)
        cells = [(r, c) for r, c in zip(row, col)]
        super().__init__(f"Line({self.r1},{self.c1},{self.r2},{self.c2}", cells)
        self.r1 = r1
        self.c1 = c1
        self.r2 = r2
        self.c2 = c2

    def __repr__(self):
        return f"({self.r1}.{self.c1}),({self.r2}.{self.c2})"


class Lines:

    def __init__(self, lines: List[Line]):
        self.lines = lines

    def __repr__(self):
        return "[" + ", ".join([str(line) for line in self.lines]) + "]"


class DiagonalLines(Lines):

    def __init__(self):
        super().__init__(
            [
                Line(1, 1, 9, 9),
                Line(9, 1, 1, 9)
            ]
        )


class ArgyleLines(Lines):

    def __init__(self):
        super().__init__(
            [
                Line(1, 5, 5, 1),
                Line(5, 1, 9, 5),
                Line(9, 5, 5, 9),
                Line(5, 9, 1, 5),
                Line(1, 2, 8, 9),
                Line(2, 1, 9, 8),
                Line(1, 8, 8, 1),
                Line(2, 9, 9, 2)
            ]
        )
