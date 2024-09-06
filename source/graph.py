from constants import *

import pygame


class Graph:
    def __init__(self, size) -> None:
        self.size = size
        self.grid = [[GraphNode(row, col) for col in range(size)]
                     for row in range(size)]

    def draw(self, window) -> None:
        for row in self.grid:
            for node in row:
                node.draw(window)

        pygame.display.update()


class GraphNode:
    def __init__(self, row, col) -> None:
        self.row = row
        self.col = col
        self.color = BACKGROUND_COLOR
        self.size = NODE_SIZE

    def draw(self, window, update=False) -> None:
        x = MARGIN + self.row * self.size
        y = MARGIN + self.col * self.size

        pygame.draw.rect(window, self.color, (x, y, self.size, self.size))
        # pygame.draw.rect(window, WHITE, (x, y, self.size, self.size), 1) # worse than lines (uneven lines)
        pygame.draw.line(window, GRID_COLOR, (x, y),
                         (x + self.size, y))

        pygame.draw.line(window, GRID_COLOR, (x, y),
                         (x, y + self.size))

        pygame.draw.line(window, GRID_COLOR, (x + self.size, y),
                         (x + self.size, y + self.size))

        pygame.draw.line(window, GRID_COLOR, (x, y + self.size),
                         (x + self.size, y + self.size))

        if update:
            pygame.display.update()
