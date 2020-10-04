from abc import ABC, abstractmethod
from typing import Optional, Dict, List

from pulp import lpSum

from Board import Board
from Sudoku import Sudoku


class Rule(ABC):
    subclasses = {}

    def __init__(self, sudoku: Sudoku, parameters: Optional[Dict]):
        self.sudoku = sudoku
        self.parameters = parameters

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.subclasses[cls.__name__] = cls

    @property
    def name(self):
        return self.__class__.__name__

    @abstractmethod
    def constraints(self) -> List["Rule"]:
        raise NotImplemented

    @property
    def objective(self):
        return None

    @property
    def description(self) -> str:
        return None

    @property
    def render(self, drawing) -> None:
        return None


class ConsecutiveDots(Rule):

    def __init__(self, sudoku: Sudoku, parameters: Optional[Dict]):
        super().__init__(sudoku, parameters)
        self.dots = [param.split(',') for param in parameters]

    def constraints(self) -> List[Rule]:
        result = []
        for dot in self.dots:
            r1, c1, r2, c2 = map(int, dot)
            result.append(
                (self.sudoku.values[r1][c1] - self.sudoku.values[r2][c2] >= -1, f"ConsecutiveDot_{r1}_{c1}_{r2}_{c2}_a")
            )
            result.append(
                (self.sudoku.values[r1][c1] - self.sudoku.values[r2][c2] <= +1, f"ConsecutiveDot_{r1}_{c1}_{r2}_{c2}_b")
            )

        return result


    @property
    def description(self) -> str:
        return "Cells surrounding a black dot must contain consecutive digits"


    @property
    def render(self, drawing) -> None:
        return None


class ValueRule(Rule):

    def constraints(self) -> List[Rule]:
        result = []
        for row in self.sudoku.ROWS:
            for col in self.sudoku.COLUMNS:
                result.append(
                    (
                        lpSum([value * self.sudoku.choices[value][row][col] for value in self.sudoku.VALUES])
                        == self.sudoku.values[row][col],
                        f"Value_{row}_{col}"
                    )
                )
        return result


class Knowns(Rule):

    def __init__(self, sudoku: Sudoku, parameters: Optional[Dict]):
        super().__init__(sudoku, parameters)
        self.board = Board.load(parameters, sudoku.ROWS, sudoku.COLUMNS)

    def constraints(self) -> List[Rule]:
        result = []
        for row in self.sudoku.ROWS:
            for col in self.sudoku.COLUMNS:
                if self.board.knowns[row - 1, col - 1] is None:
                    continue
                value = self.board.knowns[row - 1, col - 1]
                result.append((self.sudoku.values[row][col] == value, f"Known_{row + 1}_{col + 1}_{value}"))
        return result


class UniqueCells(Rule):

    def constraints(self) -> List[Rule]:
        return [
            (
                lpSum([self.sudoku.choices[value][row][col] for value in self.sudoku.VALUES]) == 1,
                f"Unique_in_cell_{row}_{col}"
            )
            for row in self.sudoku.ROWS
            for col in self.sudoku.COLUMNS
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

    def constraints(self) -> List[Rule]:
        result = []
        for region in self.region():
            result.extend(region.unique_constraints(self.sudoku.VALUES, self.sudoku.choices))
        return result

    @property
    def description(self) -> str:
        return f"Each number can only appear once in each {self.region_name()}"


class UniqueColumns(RegionRule):

    def region(self):
        return self.sudoku.column_regions()

    def region_name(self) -> str:
        return "column"


class UniqueRows(RegionRule):

    def region(self):
        return self.sudoku.row_regions()

    def region_name(self) -> str:
        return "row"


class UniqueBoxes(RegionRule):

    def region(self):
        return self.sudoku.box_regions()

    def region_name(self) -> str:
        return "box"


class ChessMove(Rule):

    def add_chess_move(self, offsets, name: str) -> List[Rule]:
        result = []
        for value in self.sudoku.VALUES:
            for row1 in self.sudoku.ROWS:
                for col1 in self.sudoku.COLUMNS:
                    for x, y in offsets:
                        row2 = row1 + y
                        col2 = col1 + x
                        if not self.sudoku.valid(row2):
                            continue
                        if not self.sudoku.valid(col2):
                            continue
                        cname = f"{name}_move_{value}_{row1}_{col1}_{row2}_{col2}"
                        result.append(
                            (
                                self.sudoku.choices[value][row1][col1] + self.sudoku.choices[value][row2][col2] <= 1,
                                cname
                            )
                        )
        return result


class AntiKnightsMove(ChessMove):

    def constraints(self) -> List[Rule]:
        offsets = [(-1, -2), (1, -2), (-2, -1), (-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1)]
        return self.add_chess_move(offsets, 'AntiKnightsMove')

    @property
    def description(self):
        return "AntiKnightsMove"


class KingsMove(ChessMove):

    def constraints(self) -> List[Rule]:
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        return self.add_chess_move(offsets, 'AntiKnightsMove')

    @property
    def description(self):
        return "Kings"


class OrthogonalConsecutive(Rule):

    def constraints(self) -> List[Rule]:
        results = []
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for value in self.sudoku.VALUES:
            for row in self.sudoku.ROWS:
                for column in self.sudoku.COLUMNS:
                    for x, y in offsets:
                        row2 = row + y
                        column2 = column + x
                        if not self.sudoku.valid(row2):
                            continue
                        if not self.sudoku.valid(column2):
                            continue
                        if self.sudoku.valid(value - 1):
                            name = f"Orthogonal_{value}_{value - 1}_{row}_{column}_{row2}_{column2}"
                            results.append(
                                (
                                    self.sudoku.choices[value - 1][row2][column2]
                                    + self.sudoku.choices[value][row][column] <= 1,
                                    name
                                )
                            )
                        if self.sudoku.valid(value + 1):
                            name = f"Orthogonal_{value}_{value + 1}_{row}_{column}_{row2}_{column2}"
                            results.append(
                                (
                                    self.sudoku.choices[value + 1][row2][column2]
                                    + self.sudoku.choices[value][row][column] <= 1,
                                    name
                                )
                            )
        return results