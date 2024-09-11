from constants import *

import pygame
import random


class Graph:
    def __init__(self, size: int) -> None:
        self.size = size
        self.grid = [[GraphNode(row, col) for col in range(size)]
                     for row in range(size)]
        self.food = None

    def draw(self, window, update=False) -> None:
        for row in self.grid:
            for node in row:
                node.draw(window)
        if update:
            pygame.display.update()

    def generate_food(self) -> None:
        self.food = random.choice(random.choice(self.grid))
        while not self.food.is_free():
            self.food = random.choice(random.choice(self.grid))

        self.food.color = FOOD_COLOR

    def generate_obstacles(self) -> None:
        for row in self.grid:
            for node in row:
                if node.is_free():
                    if random.random() > 0.99:
                        node.color = LIGHT_GREEN


class GraphNode:
    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.color = BACKGROUND_COLOR
        self.size = NODE_SIZE

    def draw(self, window, gridlines: bool = True, update: bool = False) -> None:
        x = LEFT_MARGIN + self.col * self.size
        y = TOP_MARGIN + self.row * self.size

        # if self.row == 12 and self.col == 12:
        #     self.color = BLACK

        pygame.draw.rect(window, self.color, (x, y, self.size, self.size))
        if gridlines:
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

    def is_free(self) -> bool:
        return self.color == BACKGROUND_COLOR

    def is_food(self) -> bool:
        return self.color == FOOD_COLOR

    def is_snake(self) -> bool:
        return not self.is_free() and not self.is_food()

    def reset(self) -> None:
        self.color = BACKGROUND_COLOR
