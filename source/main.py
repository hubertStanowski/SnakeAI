from constants import *
from graph import *
from snake import *

import pygame


def main() -> None:
    pygame.init()

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Snake NEAT AI")

    clock = pygame.time.Clock()
    fps = 10
    human_playing = True
    human_player = Snake()
    score = 0

    while True:
        clock.tick(fps)

        window.fill(BACKGROUND_COLOR)
        human_player.update()
        human_player.draw(window)

        if human_playing:
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
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        human_player = Snake()
                        display_reset(window)
            score = human_player.get_score()

        display_score(window, score)

        pygame.display.update()


def display_score(window: pygame.Surface, score: int) -> None:
    font = pygame.font.SysFont(FONT, SCORE_FONT_SIZE)
    label = font.render("Score: " + str(score), True, WHITE)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 50))

    window.blit(label, label_rect)


def display_reset(window: pygame.Surface) -> None:
    font = pygame.font.SysFont(FONT, RESET_FONT_SIZE)
    label = font.render("RESET", True, RED)
    label_rect = label.get_rect(
        center=((2*LEFT_MARGIN + GAME_SIZE) // 2, WINDOW_HEIGHT // 2.3))

    window.blit(label, label_rect)
    pygame.display.update()
    pygame.time.delay(1000)


if __name__ == "__main__":
    main()
