from constants import *

import pygame
import random


class Graph:
    def __init__(self, size: int) -> None:
        self.size = size
        self.grid = [[GraphNode(row, col) for col in range(size)]
                     for row in range(size)]
        self.food = None

    def draw(self, window) -> None:
        for row in self.grid:
            for node in row:
                node.draw(window)

        pygame.display.update()

    def generate_food(self) -> None:
        self.food = random.choice(random.choice(self.grid))
        while not self.food.is_free:
            self.food = random.choice(random.choice(self.grid))

        self.food.color = FOOD_COLOR


class GraphNode:
    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.color = BACKGROUND_COLOR
        self.size = NODE_SIZE

    def draw(self, window, update: bool = False) -> None:
        x = MARGIN + self.col * self.size
        y = MARGIN + self.row * self.size

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

    def is_free(self) -> bool:
        return self.color == BACKGROUND_COLOR

    def is_food(self) -> bool:
        return self.color == FOOD_COLOR

    def is_snake(self) -> bool:
        return not self.is_free() and not self.is_food()

    def reset(self) -> None:
        self.color = BACKGROUND_COLOR
