from constants import *
from graph import *
from snake import *

import pygame


def main() -> None:
    pygame.init()

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Snake NEAT AI")

    clock = pygame.time.Clock()
    fps = 15
    graph = Graph(GRAPH_SIZE)
    human_playing = True
    human_player = Snake(graph)
    graph.generate_food()
    score = 0

    while True:
        clock.tick(fps)

        window.fill(BACKGROUND_COLOR)
        human_player.update(graph)
        graph.draw(window)

        if human_playing:
            score = human_player.get_score()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and human_player.row_vel != 1:
                        human_player.row_vel = -1
                        human_player.col_vel = 0
                    elif event.key == pygame.K_DOWN and human_player.row_vel != -1:
                        human_player.row_vel = 1
                        human_player.col_vel = 0
                    elif event.key == pygame.K_LEFT and human_player.col_vel != 1:
                        human_player.row_vel = 0
                        human_player.col_vel = -1
                    elif event.key == pygame.K_RIGHT and human_player.col_vel != -1:
                        human_player.row_vel = 0
                        human_player.col_vel = 1

        display_score(window, score)

        pygame.display.update()


def display_score(window: pygame.Surface, score: int) -> None:
    font = pygame.font.SysFont(FONT, SCORE_FONT_SIZE)
    label = font.render("Score: " + str(score), True, FONT_COLOR)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 50))

    window.blit(label, label_rect)


if __name__ == "__main__":
    main()
