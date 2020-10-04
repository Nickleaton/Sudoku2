from typing import Tuple, List

from pulp import LpProblem, LpMinimize, LpVariable, LpInteger, lpSum, LpStatus


class SchismaticNonominoes(object):

    def __init__(self):
        self.name = self.__class__.__name__
        self.problem = LpProblem(self.name, LpMinimize)
        self.problem += self.objective
        self.variables = LpVariable.dicts("Choice", (self.VALUES, self.ROWS, self.COLUMNS), 0, 1, LpInteger)
        self.add_cell_constraints()
        self.add_column_constraints()
        self.add_row_constraints()
        self.regions = []

    @property
    def objective(self) -> Tuple:
        return 0, "Objective"

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
                condition = self.variables[num_str][f"{row + 1}"][f"{column + 1}"] == 1
                name = f"set_{num_str}_{row + 2}_{column + 1}"
                self.problem += condition, name
            row += 1

    def set_region(self, text: str) -> None:
        regions = [[] for value in self.VALUES]
        row = 0
        for line in text.split('\n'):
            if line.strip(" ") == '':
                continue
            for column, num_str in enumerate(line.ljust(9)):
                regions[int(num_str)-1].append((row+1,column+1))
            row += 1
        for i, region in enumerate(regions):
            for value in self.VALUES:
                condition = lpSum([self.variables[value][str(row)][str(column)] for row, column in region]) == 1
                name = f"unique_region_{i}_{value}"
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
        return result


problem = """
1.2...7.9
....8....
.6.....1.
.........
.1..6..3.
.........
.5.....9.
....4.1..
3....7...
"""

regions = """
111111222
133333244
136333244
156722244
556727444
556777889
566778889
556788889
566999999
"""

s = SchismaticNonominoes()
s.set_values(problem)
s.set_region(regions)
s.solve()
print(s)
