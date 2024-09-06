from constants import *
from graph import *

import pygame


def main() -> None:
    pygame.init()

    window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))

    pygame.display.set_caption("Snake NEAT AI")

    clock = pygame.time.Clock()
    fps = 60
    graph = Graph(GRAPH_SIZE)

    while True:
        clock.tick(fps)

        window.fill(BACKGROUND_COLOR)
        graph.draw(window)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        pygame.display.update()


if __name__ == "__main__":
    main()
