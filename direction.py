from enum import Enum, auto
from typing import Tuple


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    UP_RIGHT = auto()
    UP_LEFT = auto()
    DOWN_RIGHT = auto()
    DOWN_LEFT = auto()

    def arrow(self, size: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        if self == Direction.LEFT:
            return (size, size), (size, -size)
        if self == Direction.DOWN:
            return (-size, -size), (size, -size)
        if self == Direction.UP:
            return (-size, size), (size, size)
        if self == Direction.RIGHT:
            return (-size, -size), (-size, size)
        if self == Direction.DOWN_LEFT:
            return (0, -size), (size, 0)
        if self == Direction.UP_LEFT:
            return (0, size), (size, 0)
        if self == Direction.DOWN_RIGHT:
            return (-size, 0), (0, -size)
        if self == Direction.UP_RIGHT:
            return (0, size), (-size, 0)

    @staticmethod
    def create(r1: int, c1: int, r2: int, c2: int) -> "Direction":
        assert not ((r1 == r2) and (c1 == c2))
        assert (abs(r1-r2) == abs(c1-c2)) or (r1-r2 == 0) or (c1-c2 == 0)
        if r1 < r2:
            # down
            if c1 < c2:
                direction = Direction.DOWN_RIGHT
            elif c1 > c2:
                direction = Direction.UP_RIGHT
            else:
                direction = Direction.RIGHT
        elif r1 > r2:
            # up
            if c1 < c2:
                direction = Direction.DOWN_LEFT
            elif c1 > c2:
                direction = Direction.UP_LEFT
            else:
                direction = Direction.LEFT
        else:
            # left/right
            if c1 < c2:
                direction = Direction.DOWN
            else:
                direction = Direction.UP
        return direction
