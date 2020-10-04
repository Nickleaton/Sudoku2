from string import Template
from typing import Tuple, List

import yaml
from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpStatus

from Board import Board
from Render import RenderGrid
from Sud import solver, HTML_TEMPLATE
from Region import Region
from Rule import Rule, ValueRule


class Sudoku:

    def __init__(self):
        self.name = self.__class__.__name__
        self.problem = LpProblem(self.name, LpMinimize)
        self.problem += self.objective
        self.choices = LpVariable.dicts("Choice", (self.VALUES, self.ROWS, self.COLUMNS), cat='Binary')
        self.values = LpVariable.dicts("Values", (self.ROWS, self.COLUMNS), 1, 9, cat='Integer')
        self.rules = {}
        self.board = Board(self.ROWS, self.COLUMNS)
        self.result = Board(self.ROWS, self.COLUMNS)

    def add_rule(self, rule: "Rule") -> None:
        self.rules[rule.name] = rule
        for constraint in rule.constraints():
            self.problem += constraint[0], constraint[1]

    def write(self, filename):
        self.problem.writeLP(filename)

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
                             [[3 * i + k + 1, 3 * j + l + 1] for k in range(3) for l in range(3)])

    @property
    def objective(self) -> Tuple:
        return 0, "Objective"

    @property
    def ALL(self) -> List[int]:
        return [1, 2, 3, 4, 5, 6, 7, 8, 9]

    @property
    def ROWS(self) -> List[int]:
        return self.ALL

    @property
    def COLUMNS(self) -> List[int]:
        return self.ALL

    @property
    def VALUES(self) -> List[int]:
        return self.ALL

    def valid(self, n: int) -> bool:
        return n >= 1 and n <= 9

    @property
    def BOXES(self) -> List[Tuple[int, int]]:
        result = []
        for i in range(3):
            for j in range(3):
                result += [[(self.ROWS[3 * i + k], self.COLUMNS[3 * j + l]) for k in range(3) for l in range(3)]]
        return result

    def add_values(self) -> None:
        for row in self.ROWS:
            for column in self.COLUMNS:
                self.problem += lpSum([value * self.choices[value][row][column] for value in self.VALUES]) - \
                                self.values[row][column] == 0, f"Value_{row}_{column}"
        self.unique_cells = True

    def add_magic_square(self, x: int, y: int) -> None:
        rows = [y - 1, y, y + 1]
        columns = [x - 1, x, x + 1]
        for column in columns:
            self.problem += lpSum(
                [self.values[row][column] for row in rows]) == 15, f"Magic_Square_Column_{column}"
        for row in rows:
            self.problem += lpSum(
                [self.values[row][column] for column in columns]) == 15, f"Magic_Square_Row_{row}"

        self.problem += lpSum([self.values[x][y] for x, y in zip(rows, columns)]) == 15, \
                        "Magic_Square_Diagonal_1"
        self.problem += lpSum([self.values[x][y] for x, y in zip(rows[::-1], columns)]) == 15, \
                        "Magic_Square_Diagonal_2"

    def add_thermometer(self, n: int, thermometer) -> None:
        for i in range(1, len(thermometer)):
            c1 = thermometer[i - 1][0]
            r1 = thermometer[i - 1][1]
            c2 = thermometer[i][0]
            r2 = thermometer[i][1]
            self.problem += self.values[r2][c2] - self.values[r1][
                c1] >= 1, f"Thermometer_{n + 1:02d}_{r1}_{c1}_{r2}_{c2}"

    def add_arrow(self, n: int, x1: int, y1: int, x2: int, y2: int) -> None:
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))

        pass

    def add_x_positional(self) -> None:
        for column in self.COLUMNS:
            for row in self.ROWS:
                for value in self.VALUES:
                    self.problem += self.choices[value][row][1] == self.choices[1][row][value], \
                                    f"x_positional_row_{value}_{row}_{column}"
                    self.problem += self.choices[value][1][column] == self.choices[1][value][column], \
                                    f"x_positional_col_{value}_{row}_{column}"

    def solve(self):
        self.problem.writeLP(self.__class__.__name__ + ".lp")
        self.problem.solve(solver)

        while True:
            self.problem.solve(solver)
            # The status of the solution is printed to the screen
            if LpStatus[self.problem.status] == "Optimal":
                # The rule is added that the same solution cannot be returned again
                # self.problem += lpSum([self.choices[v][r][c] for v in self.VALUES
                # If a new optimal solution cannot be found, we end the program
                for row in self.ROWS:
                    for col in self.COLUMNS:
                        self.board.add(row, col, int(self.values[row][col].varValue))
                break
            else:
                break

    def rule_text(self):
        result = ""
        for rule in self.rules.values():
            if rule.description is None:
                continue
            result += f"<p>{rule.description}.</p>"
        return result

    def svg(self) -> str:
        rg = RenderGrid("drawing.yaml")
        rg.draw_cells()
        rg.draw_boxes()
        rg.draw_border()
        if "Knowns" in self.rules:
            rule = self.rules['Knowns']
            for row in self.ROWS:
                for col in self.COLUMNS:
                    if rule.board.knowns[row - 1][col - 1] is None:
                        continue
                    rg.draw_number(row, col, rule.board.knowns[row - 1][col - 1])
        return rg.drawing.tostring()

    def solution(self) -> str:
        rg = RenderGrid("drawing.yaml")
        rg.draw_cells()
        rg.draw_boxes()
        rg.draw_border()
        for row in self.ROWS:
            for col in self.COLUMNS:
                if self.board.knowns[row - 1][col - 1] is None:
                    continue
                rg.draw_number(row, col, self.board.knowns[row - 1][col - 1])
        return rg.drawing.tostring()

    def html(self, filename):
        template = Template(HTML_TEMPLATE)
        with open(filename, "w")  as f:
            f.write(template.substitute(rules=self.rule_text(), svg=self.svg(), solution=self.solution()))

    @staticmethod
    def load(filename: str) -> 'Sudoku':
        sudoku = Sudoku()
        problem = yaml.load(open(filename, "r"), Loader=yaml.FullLoader)
        sudoku.add_rule(ValueRule(sudoku, None))
        for rule_config in problem['Constraints']:
            if type(rule_config) == str:
                rule = Rule.subclasses[rule_config](sudoku, None)
                sudoku.add_rule(rule)
            elif type(rule_config) == dict:
                for key, parameters in rule_config.items():
                    clz = Rule.subclasses[key]
                    rule = Rule.subclasses[key](sudoku, parameters)
                    sudoku.add_rule(rule)
        return sudoku