from constants import *
from graph import *
from snake import *

import pygame


def main() -> None:
    pygame.init()

    window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))

    pygame.display.set_caption("Snake NEAT AI")

    clock = pygame.time.Clock()
    fps = 10
    graph = Graph(GRAPH_SIZE)
    human_playing = True
    human_player = Snake(graph)

    while True:
        clock.tick(fps)

        window.fill(BACKGROUND_COLOR)
        human_player.update(graph)
        graph.draw(window)
        if human_playing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        human_player.row_vel = -1
                        human_player.col_vel = 0
                    elif event.key == pygame.K_DOWN:
                        human_player.row_vel = 1
                        human_player.col_vel = 0
                    elif event.key == pygame.K_LEFT:
                        human_player.row_vel = 0
                        human_player.col_vel = -1
                    elif event.key == pygame.K_RIGHT:
                        human_player.row_vel = 0
                        human_player.col_vel = 1

        pygame.display.update()


if __name__ == "__main__":
    main()
