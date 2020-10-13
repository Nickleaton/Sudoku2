from abc import ABC, abstractmethod
from typing import Optional, Dict, List

from pulp import lpSum

from board import Board
from render import RenderGrid
from variables import Variables


class Rule(ABC):
    subclasses = {}

    def __init__(self, variables: Variables):
        self.variables = variables

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.subclasses[cls.__name__] = cls

    @property
    def name(self):
        return f"{self.__class__.__name__}"

    @property
    def objective(self):
        return None

    @property
    def description(self) -> Optional[str]:
        return None

    def render(self, drawing: RenderGrid) -> None:
        return None

    @abstractmethod
    def constraints(self) -> List:
        raise NotImplemented


class ComposedRule(Rule):

    def __init__(self, variables: Variables, children: List[Rule] = None):
        self.variables = variables
        self.children = [] if children is None else children

    def add(self, child: Rule) -> None:
        self.children.append(child)

    @property
    def name(self):
        return " | ".join([child.name for child in self.children])

    @property
    def objective(self):
        return lpSum([child.objective for child in self.children if child is not None])

    @property
    def description(self) -> Optional[str]:
        return "\n".join([child.description for child in self.children if child.description is not None])

    def render(self, drawing: RenderGrid) -> None:
        return "\n".join([child.render(drawing) for child in self.children if child.render(drawing) is not None])

    @property
    def constraints(self) -> List:
        results = []
        for child in self.children:
            if constraints := child.constraints:
                results.extend(constraints)
        return results


class ParameterRule (Rule):

    def __init__(self, variables: Variables, parameters: Optional[Dict]):
        super().__init__(variables)
        self.parameters = parameters


class MagicSquare(ParameterRule):

    def __init__(self, variables: Variables, parameters: Optional[Dict]):
        super().__init__(variables, parameters)
        self.row = parameters['row']
        self.col = parameters['col']
        self.step = parameters['step']
        self.rows = [self.row - self.step, self.row, self.row + self.step]
        self.cols = [self.col - self.step, self.col, self.col + self.step]

    @property
    def name(self):
        return f"{self.__class__.__name__}({self.row},{self.col},{self.step})"

    @property
    def constraints(self) -> List:

        result = []
        for col in self.cols:
            result.append(
                (
                    lpSum([self.variables.values[row][col] for row in self.rows]) == 15,
                    f"Magic_Square_Column_{col}"
                )
            )
        for row in self.rows:
            result.append(
                (
                    lpSum([self.variables.values[row][col] for col in self.cols]) == 15,
                    f"Magic_Square_Row_{row}"
                )
            )
        result.append(
            (
                lpSum([self.variables.values[row][col] for row, col in zip(self.rows, self.cols)]) == 15,
                "Magic_Square_Diagonal_1"
            )
        )
        result.append(
            (
                lpSum([self.variables.values[row][col] for row, col in zip(self.rows[::-1], self.cols)]) == 15,
                "Magic_Square_Diagonal_2"
            )
        )
        return result

    @property
    def description(self) -> Optional[str]:
        return None

    def render(self, drawing):
        for row in self.rows:
            for col in self.cols:
                drawing.shade_cell(row, col, 'lightskyblue')


class Thermometer(ParameterRule):

    def __init__(self, variables: Variables, parameters: Optional[Dict]):
        super().__init__(variables, parameters)
        self.points = parameters

    @property
    def constraints(self) -> List:
        result = []
        for start, end in zip(self.points[:-1], self.points[1:]):
            r1, c1 = start
            r2, c2 = end
            result.append(
                (
                    self.variables.values[r1][c1] + 1 <= self.variables.values[r2][c2],
                    f"Thermometer_{r1}_{c1}_{r2}_{c2}"
                )
            )
        return result

    @property
    def description(self) -> Optional[str]:
        return "Along each 'Thermometer', digits must increase starting from the 'bulb'"

    def render(self, drawing: RenderGrid) -> None:
        for start, end in zip(self.points[:-1], self.points[1:]):
            r1, c1 = start
            r2, c2 = end
            drawing.draw_line(r1, c1, r2, c2, 'thermometer_line')
        r, c = self.points[0]
        drawing.draw_circle(r, c, 'thermometer_bulb')


class ConsecutiveDots(ParameterRule):

    def __init__(self, variables: Variables, parameters: Optional[Dict]):
        super().__init__(variables, parameters)
        self.dots = [param.split(',') for param in parameters]

    def constraints(self) -> List:
        result = []
        for dot in self.dots:
            r1, c1, r2, c2 = map(int, dot)
            result.append(
                (self.variables.values[r1][c1] - self.variables.values[r2][c2] >= -1,
                 f"ConsecutiveDot_{r1}_{c1}_{r2}_{c2}_a")
            )
            result.append(
                (self.variables.values[r1][c1] - self.variables.values[r2][c2] <= +1,
                 f"ConsecutiveDot_{r1}_{c1}_{r2}_{c2}_b")
            )

        return result

    @property
    def description(self) -> Optional[str]:
        return "Cells surrounding a black dot must contain consecutive digits"

    def render(self, drawing: RenderGrid) -> None:
        return


class ValueRule(Rule):

    @property
    def constraints(self) -> List:
        result = []
        for row in self.variables.ROWS:
            for col in self.variables.COLUMNS:
                result.append(
                    (
                        lpSum([value * self.variables.choices[value][row][col] for value in self.variables.VALUES]) ==
                        self.variables.values[row][col],
                        f"Value_{row}_{col}"
                    )
                )
        return result


class Knowns(ParameterRule):

    def __init__(self, variables: Variables, parameters: Optional[Dict]):
        super().__init__(variables, parameters)
        self.board = Board.load(parameters, variables.ROWS, variables.COLUMNS)

    @property
    def constraints(self) -> List:
        result = []
        for row in self.variables.ROWS:
            for col in self.variables.COLUMNS:
                if self.board.knowns[row - 1, col - 1] is None:
                    continue
                value = self.board.knowns[row - 1, col - 1]
                result.append((self.variables.values[row][col] == value, f"Known_{row + 1}_{col + 1}_{value}"))
        return result

    def render(self, drawing: RenderGrid) -> None:
        for row in self.variables.ROWS:
            for col in self.variables.COLUMNS:
                if self.board.knowns[row - 1][col - 1] is None:
                    continue
                known = self.board.knowns[row - 1][col - 1] is not None
                drawing.draw_number(row, col, self.board.knowns[row - 1][col - 1], known)


class UniqueCells(Rule):

    @property
    def constraints(self) -> List:
        return [
            (
                lpSum([self.variables.choices[value][row][col] for value in self.variables.VALUES]) == 1,
                f"Unique_in_cell_{row}_{col}"
            )
            for row in self.variables.ROWS
            for col in self.variables.COLUMNS
        ]

    @property
    def description(self) -> str:
        return "Each cell can only contain a unique value"


class RegionRule(Rule):

    @abstractmethod
    def region(self):
        raise NotImplementedError

    @abstractmethod
    def region_name(self) -> str:
        raise NotImplementedError

    @property
    def constraints(self) -> List:
        result = []
        for region in self.region():
            result.extend(region.unique_constraints(self.variables.VALUES, self.variables.choices))
        return result

    @property
    def description(self) -> Optional[str]:
        return f"Each number can only appear once in each {self.region_name()}"


class UniqueColumns(RegionRule):

    def region(self):
        return self.variables.column_regions()

    def region_name(self) -> str:
        return "column"


class UniqueRows(RegionRule):

    def region(self):
        return self.variables.row_regions()

    def region_name(self) -> str:
        return "row"


class UniqueBoxes(RegionRule):

    def region(self):
        return self.variables.box_regions()

    def region_name(self) -> str:
        return "box"


class NormalSudukoRules(ComposedRule):

    def __init__(self, variables: Variables):
        super().__init__(
            variables,
            [
                UniqueRows(variables),
                UniqueBoxes(variables),
                UniqueColumns(variables),
                UniqueCells(variables)
            ]
        )

    @property
    def description(self) -> Optional[str]:
        return f"Normal Sudoku rules apply"

class ChessMove(Rule):

    def add_chess_move(self, offsets, name: str) -> List:
        result = []
        for value in self.variables.VALUES:
            for row1 in self.variables.ROWS:
                for col1 in self.variables.COLUMNS:
                    for x, y in offsets:
                        row2 = row1 + y
                        col2 = col1 + x
                        if not self.variables.valid(row2):
                            continue
                        if not self.variables.valid(col2):
                            continue
                        cname = f"{name}_move_{value}_{row1}_{col1}_{row2}_{col2}"
                        result.append(
                            (
                                self.variables.choices[value][row1][col1] + self.variables.choices[value][row2][
                                    col2] <= 1,
                                cname
                            )
                        )
        return result


class AntiKnightsMove(ChessMove):

    @property
    def constraints(self) -> List:
        offsets = [(-1, -2), (1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1)]
        return self.add_chess_move(offsets, 'AntiKnightsMove')

    @property
    def description(self) -> Optional[str]:
        return "Cells that are knight's move away from each other cannot contain the same digit"


class AntiKingsMove(ChessMove):

    @property
    def constraints(self) -> List:
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        return self.add_chess_move(offsets, 'AntiKingsMove')

    @property
    def description(self) -> Optional[str]:
        return "Kings"

class MoveQueenMove(ChessMove):

    def constraints(self) -> List:
        offsets = [(-1, -2), (1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1)]
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        self.add_chess_move(sudoku, offsets, 'Quuens')

    def description(self):
        return "QueensMove"

    def add_queen_move(sudoku, offsets, value) -> None:
        for row in sudoku.ROWS:
            for column in sudoku.COLUMNS:
                for x, y in offsets:
                    row2 = row + y
                    column2 = column + x
                    if not sudoku.valid(row2):
                        continue
                    if not sudoku.valid(column2):
                        continue
                    cname = f"Queens_move_{value}_{row}_{column}_{row2}_{column2}"
                    sudoku.problem += sudoku.choices[value][row2][column2] \
                                      + sudoku.choices[value][row][column] <= 1, \
                                      cname

    def add_queens_move(self, values: List[int]) -> None:
        offsets = []
        for v in self.VALUES:
            offsets.append((v, v))
            offsets.append((v, -v))
            offsets.append((-v, v))
            offsets.append((-v, -v))
        for value in values:
            self.add_queen_move(offsets, value)

class OrthogonalConsecutive(Rule):

    @property
    def constraints(self) -> List:
        results = []
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for value in self.variables.VALUES:
            for row in self.variables.ROWS:
                for column in self.variables.COLUMNS:
                    for x, y in offsets:
                        row2 = row + y
                        column2 = column + x
                        if not self.variables.valid(row2):
                            continue
                        if not self.variables.valid(column2):
                            continue
                        if self.variables.valid(value - 1):
                            name = f"Orthogonal_{value}_{value - 1}_{row}_{column}_{row2}_{column2}"
                            results.append(
                                (
                                    self.variables.choices[value - 1][row2][column2]
                                    + self.variables.choices[value][row][column] <= 1,
                                    name
                                )
                            )
                        if self.variables.valid(value + 1):
                            name = f"Orthogonal_{value}_{value + 1}_{row}_{column}_{row2}_{column2}"
                            results.append(
                                (
                                    self.variables.choices[value + 1][row2][column2]
                                    + self.variables.choices[value][row][column] <= 1,
                                    name
                                )
                            )
        return results
