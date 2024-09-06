from constants import *
from graph import *


class SnakeNode:
    def __init__(self, graph: Graph, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.color = SNAKE_COLOR
        self.update_graph(graph)

    def update_graph(self, graph: Graph) -> None:
        graph.grid[self.row][self.col].color = self.color


class Snake:
    def __init__(self, graph: Graph) -> None:
        self.body = []
        self.row_vel = 0
        self.col_vel = VELOCITY
        self.alive = True
        self.moving = True

        self.body.append(SnakeNode(graph, STARTING_ROW, STARTING_COL))
        self.body.append(SnakeNode(graph, STARTING_ROW-1, STARTING_COL))

    def move_head(self) -> None:
        self.body[0].row += self.row_vel
        self.body[0].col += self.col_vel

    def update(self, graph: Graph) -> None:
        if not self.moving:
            return

        tail_row, tail_col = self.body[-1].row, self.body[-1].col
        for i in range(1, len(self.body)):
            self.body[i].row = self.body[i-1].row
            self.body[i].col = self.body[i-1].col
            self.body[i].update_graph(graph)

        self.move_head()
        self.check_collisions(graph)
        if not self.moving:
            return
        self.body[0].update_graph(graph)
        graph.grid[tail_row][tail_col].reset()

    def check_collisions(self, graph: Graph) -> None:
        head = self.body[0]
        collides_top_bottom = not (0 <= head.col < graph.size)
        collides_left_right = not (0 <= head.row < graph.size)

        if collides_top_bottom or collides_left_right:
            self.alive = False
            self.moving = False
