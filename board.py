import numpy as np


class Board:

    def __init__(self, rows, columns):
        self.rows = max(rows)
        self.columns = max(columns)
        self.knowns = np.full(shape=(self.rows, self.columns), fill_value=None)

    def add(self, row: int, col: int, value: int):
        self.knowns[row - 1, col - 1] = value

    def __repr__(self) -> str:
        result = ""
        for row in range(self.rows):
            for col in range(self.columns):
                if self.knowns[row, col] is None:
                    result += " "
                else:
                    result += f"{self.knowns[row, col]}"
            result += "\n"
        return result

    def __eq__(self, other):
        for row in range(self.rows):
            for col in range(self.columns):
                if self.knowns[row, col] != other.knowns[row, col]:
                    return False
        return True

    @staticmethod
    def load(parameters, rows, columns) -> "Board":
        board = Board(rows, columns)
        row = 0
        for line in parameters:
            if line.strip(" ") == '':
                continue
            for col, num_str in enumerate(line.ljust(9)):
                if num_str == '.':
                    continue
                value = int(num_str)
                board.add(row + 1, col + 1, value)
            row += 1
        return board
