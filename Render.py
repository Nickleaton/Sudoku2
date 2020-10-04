from typing import List, Tuple

import svgwrite
from enum import Enum, auto
import yaml

from Direction import Direction


class Side(Enum):
    TOP = auto()
    BOTTOM = auto()
    LEFT = auto()
    RIGHT = auto()


class RenderGrid:

    def __init__(self, settings_filename: str):
        with open(settings_filename) as file:
            self.settings = yaml.full_load(file)

        self.drawing = svgwrite.Drawing(size=tuple(self.settings['board_size']))
        # self.drawing.add(self.drawing.rect(size=('100%', '100%'),background={'fill':'pink'}))
        self.count = self.settings['size']
        self.spacing = self.settings['spacing']
        self.offset = self.settings['offset']
        self.x_text_offset = self.settings['x_text_offset']
        self.y_text_offset = self.settings['y_text_offset']
        self.circle_radius = self.settings['circle_radius']

    def center (self, row: int, column: int) -> Tuple[int, int]:
        x = self.offset + int((row - 0.5) * self.spacing)
        y = self.offset + int((column - 0.5) * self.spacing)
        return x, y


    def draw_cells(self):
        for i in range(self.count + 1):
            self.drawing.add(
                self.drawing.line(
                    (self.offset + i * self.spacing, self.offset),
                    (self.offset + i * self.spacing, self.offset + self.spacing * 9),
                    **self.settings['cell_line']
                )
            )
            self.drawing.add(
                self.drawing.line(
                    (self.offset, self.offset + i * self.spacing),
                    (self.offset + self.spacing * 9, self.offset + i * self.spacing),
                    **self.settings['cell_line']
                )
            )

    def draw_border(self):
        self.drawing.add(
            self.drawing.line(
                (self.offset, self.offset),
                (self.offset, self.offset + self.spacing * self.count),
                **self.settings['border_line']
            )
        )
        self.drawing.add(
            self.drawing.line(
                (self.offset, self.offset),
                (self.offset + self.spacing * self.count, self.offset),
                **self.settings['border_line']
            )
        )
        self.drawing.add(
            self.drawing.line(
                (self.offset + self.spacing * self.count, self.offset),
                (self.offset + self.spacing * self.count, self.offset + self.spacing * self.count),
                **self.settings['border_line']
            )
        )
        self.drawing.add(
            self.drawing.line(
                (self.offset, self.offset + self.spacing * self.count),
                (self.offset + self.spacing * self.count, self.offset + self.spacing * self.count),
                **self.settings['border_line']
            )
        )

    def draw_boxes(self):
        for i in range(3, self.count, 3):
            self.drawing.add(
                self.drawing.line(
                    (self.offset + i * self.spacing, self.offset),
                    (self.offset + i * self.spacing, self.offset + self.spacing * 9),
                    **self.settings['box_line']
                )
            )
            self.drawing.add(
                self.drawing.line(
                    (self.offset, self.offset + i * self.spacing),
                    (self.offset + self.spacing * 9, self.offset + i * self.spacing),
                    **self.settings['box_line']
                )
            )

    def draw_diagonals(self):
        self.drawing.add(
            self.drawing.line(
                (self.offset, self.offset),
                (self.offset + self.spacing * self.count, self.offset + self.spacing * self.count),
                **self.settings['diagonal_line']
            )
        )
        self.drawing.add(
            self.drawing.line(
                (self.offset, self.offset + self.spacing * self.count),
                (self.offset + self.spacing * self.count, self.offset),
                **self.settings['diagonal_line']
            )
        )

    def draw_number(self, row: int, column: int, value: int):
        x = self.offset + int((row - 1) * self.spacing) + self.x_text_offset
        y = self.offset + int((column) * self.spacing) + self.y_text_offset
        self.drawing.add(
            self.drawing.text(text=str(value), insert=(x, y), **self.settings['number_text'])
        )

    def draw_circle(self, row: int, column: int) -> None:
        x,y = self.center(row, column)
        self.drawing.add(
            self.drawing.circle(center=(x, y), r=self.circle_radius, **(self.settings['circle']))
        )



    def draw_arrow(self, r1: int, c1: int, r2: int, c2: int) -> None:
        direction = Direction.create(r1, c1, r2, c2)
        print (direction.name)
        x1,y1 = self.center(r1, c1)
        x2,y2 = self.center(r2, c2)
        self.drawing.add(self.drawing.line((x1,y1),(x2,y2),**self.settings['arrow_line']))
        self.draw_circle(r1,c1)
        (dx1, dy1), (dx2, dy2) = direction.arrow(20)
        self.drawing.add(self.drawing.line((x2,y2),(x2+dx1,y2+dy1),**self.settings['arrow_line']))
        self.drawing.add(self.drawing.line((x2,y2),(x2+dx2,y2+dy2),**self.settings['arrow_line']))

    def draw_outside_number(self, row: int, column: int, value: int) -> None:
        pass

    def draw_thermometer(self, cells: List) -> None:
        pass

    def draw_shaded_cell(self, row: int, column: int, colour) -> None:
        pass

    def draw_region_outline(self, cells: List[Tuple[int, int]]) -> None:
        pass

    def draw_small_total(self, row: int, column: int, value: int) -> None:
        pass

    def draw_x(self, r1: int, c1: int, r2: int, c2: int) -> None:
        pass

    def draw_v(self, r1: int, c1: int, r2: int, c2: int) -> None:
        pass

    def draw_node_circle(r1: int, c1: int, r2: int, c2: int, values: List[int]) -> None:
        pass

    def draw_dot(r1: int, c1: int, r2: int, c2: int, black: bool) -> None:
        pass

    def write(self):
        return self.drawing.save(pretty=True)

#
# rg = RenderGrid("drawing.yaml")
# rg.draw_cells()
# rg.draw_boxes()
# rg.draw_border()
# rg.draw_diagonals()
# rg.draw_number(5, 5, 5)
# rg.draw_circle(1, 1)
# rg.draw_arrow(5,5,3,3)
# rg.draw_arrow(5,5,7,3)
# rg.draw_arrow(5,5,3,7)
# rg.draw_arrow(5,5,7,7)
# rg.draw_arrow(5,5,5,3)
# rg.draw_arrow(5,5,7,5)
# rg.draw_arrow(5,5,5,7)
# rg.draw_arrow(5,5,3,5)
# rg.write()
