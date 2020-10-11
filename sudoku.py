from string import Template
from typing import Tuple

import yaml
from pulp import LpProblem, LpMinimize, LpStatus, COIN_CMD

from board import Board
from render import RenderGrid
from rule import ComposedRule, ValueRule, Rule
from variables import Variables

config = yaml.safe_load(open('config.yaml', 'r'))
solver = COIN_CMD(**config)

with open('html_template.txt', 'r') as f:
    HTML_TEMPLATE = f.read()

class Sudoku:

    def __init__(self):
        self.name = self.__class__.__name__
        self.problem = LpProblem(self.name, LpMinimize)
        self.problem += self.objective
        self.variables = Variables()
        self.rules = ComposedRule(self.variables)
        self.board = Board(self.variables.ROWS, self.variables.COLUMNS)
        self.result = Board(self.variables.ROWS, self.variables.COLUMNS)

    def write(self, filename):
        self.problem.writeLP(filename)

    @property
    def objective(self) -> Tuple:
        return 0, "Objective"

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
                for row in self.variables.ROWS:
                    for col in self.variables.COLUMNS:
                        self.board.add(row, col, int(self.variables.values[row][col].varValue))
                break
            else:
                break

    def rule_text(self):
        result = ""
        for rule in self.rules.children:
            if rule.description is None:
                continue
            result += f"<p>{rule.description}.</p>"
        return result

    def svg(self) -> str:
        rg = RenderGrid("drawing.yaml")
        for rule in self.rules.children:
            rule.render(rg)
        rg.draw_cells()
        rg.draw_boxes()
        rg.draw_border()
        return rg.drawing.tostring()

    def solution(self) -> str:
        rg = RenderGrid("drawing.yaml")
        rg.draw_cells()
        rg.draw_boxes()
        rg.draw_border()
        return rg.drawing.tostring()

    def html(self, filename):
        template = Template(HTML_TEMPLATE)
        with open(filename, "w") as f:
            f.write(template.substitute(rules=self.rule_text(), svg=self.svg(), solution=self.solution()))

    @staticmethod
    def load(filename: str) -> 'Sudoku':
        sudoku = Sudoku()
        problem = yaml.load(open(filename, "r"), Loader=yaml.FullLoader)
        sudoku.rules.add(ValueRule(sudoku.variables))
        for rule_config in problem['Constraints']:
            if type(rule_config) == str:
                rule = Rule.subclasses[rule_config](sudoku.variables)
                sudoku.rules.add(rule)
            elif type(rule_config) == dict:
                key = next(iter(rule_config))
                rule = Rule.subclasses[key](sudoku.variables, rule_config[key])
                sudoku.rules.add(rule)
        for constraint in sudoku.rules.constraints:
            sudoku.problem += constraint
        return sudoku
