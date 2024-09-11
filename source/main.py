from constants import *
from graph import *
from player import Player
from buttons import initialize_buttons, Button
from population import Population
from neat_config import NeatConfig

import pygame


# TODO training progress bar curr_gen/target_gen


def main() -> None:
    pygame.init()

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Snake NEAT AI")

    clock = pygame.time.Clock()
    fps_idx = 1

    buttons = initialize_buttons()
    config = NeatConfig()
    human_player = Player()

    score = 0

    population_size = 500
    population = Population(config, size=population_size)
    node_id_renders = prerender_node_ids()
    ai_player = Player()
    ai_player.alive = False
    pause = False
    target_generation = 10
    human_playing = False
    show_current = False
    simulation_done = False

    while True:
        fps = FPS[fps_idx] if ai_player.alive or human_playing else 0
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
            if not simulation_done:
                if (population.generation-1 >= target_generation or show_current):
                    if show_current:
                        ai_player = population.prev_best_player.clone()
                        show_current = False
                    else:
                        ai_player = population.gen_best_players[target_generation-1].clone(
                        )
                    simulation_done = True
                else:
                    display_best_score(window, population.curr_best_player.get_score(
                    ), population.best_ever_player.get_score())
                    population.curr_best_player.draw_network(
                        window, node_id_renders)

                    if not population.finished():
                        population.update_survivors()
                    else:
                        print(
                            f"Gen: {population.generation}, Score: {population.curr_best_player.get_score()} / {population.best_ever_player.get_score()}")
                        population.natural_selection()

            if simulation_done:
                if ai_player.alive and not pause:
                    ai_player.look()
                    ai_player.decide(show=False)
                    ai_player.update()

                ai_player.draw(window)
                score = ai_player.get_score()
                ai_player.draw_network(window, node_id_renders)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if not ai_player or not ai_player.alive:
                            show_current = True
                    elif event.key == pygame.K_RETURN:
                        pause = not pause
                    elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                        population = Population(config, size=population_size)
                        ai_player.alive = False
                        simulation_done = False
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        fps_idx = min(fps_idx+1, len(FPS)-1)
                    elif event.key == pygame.K_MINUS:
                        fps_idx = max(fps_idx-1, 0)
                elif pygame.mouse.get_pressed()[0]:
                    pos = pygame.mouse.get_pos()
                    for label, button in buttons.items():
                        if button.clicked(pos):
                            simulation_done = False
                            ai_player.alive = False
                            target_generation = label
                            button.select()
                            for other in buttons.values():
                                if other is not button:
                                    other.unselect()

            current_generation = ai_player.generation if simulation_done else population.generation
            display_generation(window, current_generation, simulation_done)
            display_button_info(window)
            draw_ui_lines(window)
            for button in buttons.values():
                button.draw(window)
        if simulation_done or human_playing or ai_player.alive:
            display_curr_score(
                window, score, population.best_ever_player.get_score())

        pygame.display.update()


def display_button_info(window: pygame.Surface) -> None:
    font = pygame.font.SysFont(FONT, BUTTON_INFO_FONT_SIZE)
    label = font.render("Simulate generation", True, BRIGHT_BLUE)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 195))

    window.blit(label, label_rect)


def display_curr_score(window: pygame.Surface, score: int, best_ever: int) -> None:
    font = pygame.font.SysFont(FONT, SCORE_FONT_SIZE)
    label = font.render(f"Score: {score}", True, RUBY)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 110))

    window.blit(label, label_rect)


def display_best_score(window: pygame.Surface, score: int, best_ever: int) -> None:
    font = pygame.font.SysFont(FONT, SCORE_FONT_SIZE)
    label = font.render(f"Best score: {score} / {best_ever}", True, ORANGE)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 110))

    window.blit(label, label_rect)


def display_generation(window: pygame.Surface, generation: int, simulating: bool) -> None:
    font = pygame.font.SysFont(FONT, GENERATION_FONT_SIZE)
    label = font.render("Gen: " + str(generation), True,
                        SNAKE_COLOR if not simulating else BRIGHT_BLUE)
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


def draw_ui_lines(window: pygame.Surface) -> None:
    # pygame.draw.lines(window, BRIGHT_BLUE, True, [
    #                   (LEFT_MARGIN+GAME_SIZE+30, 30), (LEFT_MARGIN+GAME_SIZE+30, WINDOW_HEIGHT-30)])
    pygame.draw.lines(window, BRIGHT_BLUE, True, [
                      ((LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//5.5)), 150), ((LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//1.2)), 150)])
    pygame.draw.lines(window, BRIGHT_BLUE, True, [
                      ((LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//5.5)), 300), ((LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//1.2)), 300)])


# Optimization for drawing neural network
def prerender_node_ids() -> list:
    renders = []
    font = pygame.font.Font(FONT, NODE_ID_FONT_SIZE)
    for id in range(20):
        renders.append(font.render(str(id), True, WHITE))

    return renders


if __name__ == "__main__":
    main()
