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


class Player:
    def __init__(self) -> None:
        self.graph = Graph(GRAPH_SIZE)
        self.body = []
        self.row_vel = 0
        self.col_vel = VELOCITY
        self.alive = True
        self.moving = True
        self.body.append(SnakeNode(self.graph, STARTING_ROW, STARTING_COL))
        self.body.append(SnakeNode(self.graph, STARTING_ROW-1, STARTING_COL))
        self.head = self.body[0]

        self.graph.generate_food()

    def draw(self, window) -> None:
        self.graph.draw(window)

    def update(self) -> None:
        if not self.moving:
            return

        tail_row, tail_col = self.body[-1].row, self.body[-1].col

        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].row = self.body[i-1].row
            self.body[i].col = self.body[i-1].col
            self.body[i].update_graph(self.graph)

        self.move_head()
        self.graph.grid[tail_row][tail_col].reset()

        self.check_collisions()
        if not self.moving:
            return

        self.head.update_graph(self.graph)

        if (self.head.row, self.head.col) == (self.graph.food.row, self.graph.food.col):
            self.body.append(SnakeNode(self.graph, tail_row, tail_col))
            self.graph.generate_food()

    def check_collisions(self) -> None:
        collides_top_bottom = not (0 <= self.head.col < self.graph.size)
        collides_left_right = not (0 <= self.head.row < self.graph.size)

        if collides_top_bottom or collides_left_right:
            self.alive = False
            self.moving = False
        elif self.graph.grid[self.head.row][self.head.col].is_snake():
            self.alive = False
            self.moving = False

    def move_head(self) -> None:
        self.head.row += self.row_vel
        self.head.col += self.col_vel

    def get_score(self) -> int:
        return len(self.body) - 2
