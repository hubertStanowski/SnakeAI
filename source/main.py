from constants import *
from graph import *
from player import Player

from population import Population
from neat_config import NeatConfig

import pygame


def main() -> None:
    pygame.init()

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Snake NEAT AI")

    clock = pygame.time.Clock()
    fps = 10

    human_player = Player()
    config = NeatConfig()
    score = 0

    population = Population(config, size=500)
    ai_player = None
    generation_target = 200
    human_playing = False

    while True:
        fps = 10 if ai_player else 0
        clock.tick(fps)

        window.fill(BACKGROUND_COLOR)
        if human_playing:
            human_player.update()
            human_player.draw(window)
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
                        human_player = Player()
                        display_reset(window)
            score = human_player.get_score()
        else:
            if not population.finished():
                population.update_survivors(window)
            elif population.generation == generation_target:
                if not ai_player:
                    ai_player = population.prev_best_player.clone()
                elif ai_player.alive:
                    ai_player.look()
                    ai_player.decide(show=True)
                    ai_player.update()
                    ai_player.draw(window)
                    score = ai_player.get_score()
            else:
                print(population.generation,
                      population.curr_best_player.get_score())
                population.natural_selection()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

        display_score(window, score)
        if ai_player or human_playing:
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
