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
    fps_idx = 1

    human_player = Player()
    config = NeatConfig()
    score = 0

    population_size = 500
    population = Population(config, size=population_size)
    node_id_renders = prerender_node_ids()
    ai_player = None
    generation_target = 50
    human_playing = False
    show_current = False

    while True:
        fps = FPS[fps_idx] if ai_player or human_playing else 0
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
            if not ai_player:
                display_best_score(
                    window, population.curr_best_player.get_score())
                population.curr_best_player.draw_network(
                    window, node_id_renders)

            if not population.finished():
                population.update_survivors()
            elif not ai_player and (population.generation == generation_target or show_current):
                show_current = False
                ai_player = population.prev_best_player.clone()
            elif ai_player:
                if ai_player.alive:
                    ai_player.look()
                    ai_player.decide(show=False)
                    ai_player.update()
                    ai_player.draw(window)
                    score = ai_player.get_score()
                    ai_player.draw_network(window, node_id_renders)
                else:
                    ai_player = None
                    pygame.time.delay(1000)
            else:
                print("Gen:", population.generation, "Score:",
                      population.curr_best_player.get_score())
                population.natural_selection()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not ai_player or not ai_player.alive:
                            show_current = True
                    elif event.key == pygame.K_RETURN:
                        ai_player = None
                        pygame.time.delay(1000)
                    elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                        population = Population(config, size=population_size)
                        ai_player = None
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        fps_idx = min(fps_idx+1, len(FPS)-1)
                    elif event.key == pygame.K_MINUS:
                        fps_idx = max(fps_idx-1, 0)

            display_generation(window, population.generation)

        if ai_player or human_playing:
            display_curr_score(window, score)

        pygame.display.update()


def display_curr_score(window: pygame.Surface, score: int) -> None:
    font = pygame.font.SysFont(FONT, SCORE_FONT_SIZE)
    label = font.render("Score: " + str(score), True, RUBY)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 110))

    window.blit(label, label_rect)


def display_best_score(window: pygame.Surface, score: int) -> None:
    font = pygame.font.SysFont(FONT, SCORE_FONT_SIZE)
    label = font.render("Best score: " + str(score), True, ORANGE)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 110))

    window.blit(label, label_rect)


def display_generation(window: pygame.Surface, generation: int) -> None:
    font = pygame.font.SysFont(FONT, SCORE_FONT_SIZE)
    label = font.render("Gen: " + str(generation), True, SNAKE_COLOR)
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


# Optimization for drawing neural network
def prerender_node_ids() -> list:
    renders = []
    font = pygame.font.Font(FONT, NODE_ID_FONT_SIZE)
    for id in range(20):
        renders.append(font.render(str(id), True, WHITE))

    return renders


if __name__ == "__main__":
    main()
