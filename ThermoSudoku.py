from collections import OrderedDict
from typing import Tuple, List

from pulp import LpProblem, LpMinimize, LpVariable, LpInteger, lpSum, LpStatus


class ThermoSudoku(object):

    def __init__(self):
        self.name = self.__class__.__name__
        self.problem = LpProblem(self.name, LpMinimize)
        self.problem += self.objective
        self.variables = LpVariable.dicts("Choice", (self.VALUES, self.ROWS, self.COLUMNS), 0, 1, LpInteger)
        self.add_cell_constraints()
        self.add_box_contraints()
        self.add_column_constraints()
        self.add_row_constraints()
        self.thermometers = OrderedDict()

    @property
    def objective(self) -> Tuple:
        return lpSum([self.variables[value][row][column] for value in self.VALUES for row in self.ROWS for column in self.COLUMNS]), "Objective"

    def add_cell_constraints(self) -> None:
        for row in self.ROWS:
            for column in self.COLUMNS:
                condition = lpSum([self.variables[value][row][column] for value in self.VALUES]) == 1
                name = f"cell_{column}_{row}"
                self.problem += condition, name

    def add_column_constraints(self) -> None:
        for column in self.COLUMNS:
            for value in self.VALUES:
                condition = lpSum([self.variables[value][row][column] for row in self.ROWS]) == 1
                name = f"column_{value}_{column}"
                self.problem += condition, name

    def add_row_constraints(self) -> None:
        for row in self.ROWS:
            for value in self.VALUES:
                condition = lpSum([self.variables[value][row][column] for column in self.COLUMNS]) == 1
                name = f"row_{value}_{row}"
                self.problem += condition, name

    def add_box_contraints(self) -> None:
        for b in self.BOXES:
            for value in self.VALUES:
                condition = lpSum([self.variables[value][row][column] for (row, column) in b]) == 1
                name = f"box_{value}_{b[0][0]}_{b[0][1]}"
                self.problem += condition, name

    @property
    def ALL(self) -> List[str]:
        return ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    @property
    def ROWS(self) -> List[int]:
        return self.ALL

    @property
    def COLUMNS(self) -> List[int]:
        return self.ALL

    @property
    def VALUES(self) -> List[int]:
        return self.ALL

    @property
    def BOXES(self) -> List[Tuple[int, int]]:
        result = []
        for i in range(3):
            for j in range(3):
                result += [[(self.ROWS[3 * i + k], self.COLUMNS[3 * j + l]) for k in range(3) for l in range(3)]]
        return result

    def set_values(self, text: str) -> None:
        row = 0
        for line in text.split('\n'):
            if line.strip(" ") == '':
                continue
            for column, num_str in enumerate(line.ljust(9)):
                if num_str == '.':
                    continue
                condition = self.variables[num_str][f"{row + 2}"][f"{column + 1}"] == 1
                name = f"set_{num_str}_{row + 2}_{column + 1}"
                self.problem += condition, name
            row += 1

    def add_thermometer(self, points: List[Tuple[int, int]]) -> None:
        self.thermometers[chr(ord('A') + len(self.thermometers))] = points
        for start, finish in zip(points[:-1], points[1:]):
            start_column = str(start[0])
            start_row = str(start[1])
            finish_column = str(finish[0])
            finish_row = str(finish[1])
            start_value  = lpSum([int(value) * self.variables[value][start_row ][start_column ] for value in self.VALUES])
            finish_value = lpSum([int(value) * self.variables[value][finish_row][finish_column] for value in self.VALUES])
            condition = finish_value - start_value >= 1
            name = f"thermo_{start_column}_{start_row}_{finish_column}_{finish_row}"
            self.problem += condition, name

    def solve(self):
        self.problem.writeLP(self.__class__.__name__ + ".lp")
        self.problem.solve()

    def __str__(self) -> str:
        result = self.name + "\n"
        result += LpStatus[self.problem.status] + "\n"
        for row in self.ROWS:
            for column in self.COLUMNS:
                for value in self.VALUES:
                    if self.variables[value][row][column].varValue == 1.0:
                        result += value + " "
                result += " "
            result += "\n"
        for column in self.COLUMNS:
            for row in self.ROWS:
                for value in self.VALUES:
                    print (f"{value} {row} {column}   = {self.variables[value][row][column].varValue}")
        return result


problem = """
.........
.........
.........
.........
......9..
....8.7..
.........
.........
.........
"""

s = ThermoSudoku()
s.add_thermometer([(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8)])
s.add_thermometer([(9, 8), (9, 7), (9, 6), (9, 5), (9, 4), (9, 3), (9, 2)])
s.add_thermometer([(8, 1), (7, 1), (6, 1), (5, 1), (4, 1), (3, 1), (2, 1)])
s.add_thermometer([(2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9)])

s.add_thermometer([(2, 4), (2, 3), (3, 3), (3, 2)])
s.add_thermometer([(3, 8), (2, 7), (2, 6)])

s.add_thermometer([(7, 2), (7, 3), (8, 3), (8, 4)])

s.add_thermometer([(4, 3), (4, 4), (3, 5)])
s.add_thermometer([(7, 5), (6, 4), (6, 3)])
s.add_thermometer([(6,7),(5,6),(4,7)])
s.add_thermometer([(8, 6), (8, 7), (7, 8)])

s.set_values(problem)

s.solve()
print(s)
