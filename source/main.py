from constants import *
from graph import *
from player import *
from buttons import *
from population import Population
from neat_config import NeatConfig
from user_config import *

import pygame


def main() -> None:
    pygame.init()

    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Snake NEAT AI")

    clock = pygame.time.Clock()
    fps_idx = 1

    human_playing = HUMAN_PLAYING
    population_size = POPULATION_SIZE
    config = NeatConfig()
    population = Population(config, size=population_size)
    score = 0

    human_player = Player()
    buttons = initialize_buttons()
    node_id_renders = prerender_node_ids()
    ai_player = Player()
    ai_player.alive = False
    pause = False
    target_generation = 10

    show_previous = False
    simulation_done = False

    animation_snake = initialize_animation_snake()
    animation_step = [0]  # in a list to pass as pointer

    while True:
        fps = FPS[fps_idx] if ai_player.alive or human_playing else 0
        clock.tick(fps)
        animation_step[0] += 1

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
                if (population.generation-1 >= target_generation or show_previous):
                    if show_previous:
                        ai_player = population.prev_best_player.clone()
                        show_previous = False
                    else:
                        ai_player = population.gen_best_players[target_generation-1].clone(
                        )
                    simulation_done = True
                else:
                    if not population.finished():
                        population.update_survivors()
                    else:
                        print(
                            f"Gen: {population.generation}, Score: {population.curr_best_player.get_score()} / {population.best_ever_player.get_score()}")
                        population.natural_selection()
                    animate_evolving_progress(
                        window, animation_snake, animation_step, clock.get_fps())
                    display_training_info(
                        window, population, target_generation)

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
                    if event.key == pygame.K_RETURN:
                        if not ai_player or not ai_player.alive:
                            show_previous = True
                    elif event.key == pygame.K_SPACE:
                        if simulation_done:
                            pause = not pause
                    elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                        population = Population(
                            config, size=population_size)
                        ai_player.alive = False
                        simulation_done = False
                        display_reset(window)
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
                            if label != "best":
                                target_generation = label
                            else:
                                ai_player = population.best_ever_player.clone()
                                simulation_done = True
                            button.select()
                            for other in buttons.values():
                                if other is not button:
                                    other.unselect()

            current_generation = ai_player.generation if simulation_done else population.generation
            display_generation(window, current_generation)
            display_button_info(window)
            draw_ui_lines(window)
            if pause:
                display_paused(window)
            for button in buttons.values():
                button.draw(window)
        if simulation_done or human_playing or ai_player.alive:
            display_curr_score(window, score)
        else:
            display_best_score(window, population.curr_best_player.get_score(
            ), population.best_ever_player.get_score())
            population.curr_best_player.draw_network(
                window, node_id_renders)
        pygame.display.update()


def display_button_info(window: pygame.Surface) -> None:
    font = pygame.font.SysFont(FONT, BUTTON_INFO_FONT_SIZE)
    label = font.render("Simulate generation", True, BRIGHT_BLUE)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 160))

    window.blit(label, label_rect)


def display_curr_score(window: pygame.Surface, score: int) -> None:
    font = pygame.font.SysFont(FONT, SCORE_FONT_SIZE)
    label = font.render(f"Score: {score}", True, RUBY)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 95))

    window.blit(label, label_rect)


def display_best_score(window: pygame.Surface, score: int, best_ever: int) -> None:
    font = pygame.font.SysFont(FONT, SCORE_FONT_SIZE)
    label = font.render(f"Best score: {score} / {best_ever}", True, RUBY)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 95))

    window.blit(label, label_rect)


def display_generation(window: pygame.Surface, generation: int) -> None:
    font = pygame.font.SysFont(FONT, GENERATION_FONT_SIZE)
    label = font.render(f"Gen: {generation}", True, BRIGHT_BLUE)
    label_rect = label.get_rect(
        center=(LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//2), 40))

    window.blit(label, label_rect)


def display_paused(window: pygame.Surface) -> None:
    font = pygame.font.SysFont(FONT, RESET_FONT_SIZE)
    label = font.render("PAUSED", True, ORANGE)
    label_rect = label.get_rect(
        center=((2*LEFT_MARGIN + GAME_SIZE) // 2, WINDOW_HEIGHT // 2.3))

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
                      ((LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//5.5)), 130), ((LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//1.2)), 130)])
    pygame.draw.lines(window, BRIGHT_BLUE, True, [
                      ((LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//5.5)), 320), ((LEFT_MARGIN+GAME_SIZE+(RIGHT_MARGIN//1.2)), 320)])


def display_training_info(window: pygame.Surface, population: Population, target_generation: int) -> None:
    alive = len([player for player in population.players if player.alive])
    font = pygame.font.SysFont(FONT, EVOL_INFO_FONT_SIZE)

    progress_label = font.render(
        f"Training generation: {population.generation} / {target_generation}", True, BRIGHT_BLUE)
    progress_label_rect = progress_label.get_rect(
        center=((LEFT_MARGIN+GAME_SIZE)//2, 160))

    alive_label = font.render(
        f"Alive: {alive} / {population.size}", True, BRIGHT_BLUE)
    alive_label_rect = alive_label.get_rect(
        center=((LEFT_MARGIN+GAME_SIZE)//2, 195))

    # window.blit(size_label, size_label_rect)
    window.blit(progress_label, progress_label_rect)
    window.blit(alive_label, alive_label_rect)


def animate_evolving_progress(window: pygame.Surface, animation_snake: Player, animation_step: list[int], real_fps: float) -> None:
    if animation_step[0] > real_fps/20:
        if animation_snake.head.pos() in [(10, 14), (10, 10), (14, 14), (14, 10)]:
            animation_snake.turn_right()
        animation_snake.update(animation=True)
        animation_step[0] = 0

    animation_snake.draw(window, gridlines=False)


def initialize_animation_snake() -> Player:
    animation_snake = Player()
    animation_snake.graph = Graph(GRAPH_SIZE)
    animation_snake.body = []
    row = 10
    for col in range(14, 9, -1):
        animation_snake.body.append(
            SnakeNode(animation_snake.graph, row, col))

    animation_snake.head = animation_snake.body[0]

    animation_snake.graph.grid[12][12].color = RUBY
    animation_snake.graph.food = animation_snake.graph.grid[12][12]

    return animation_snake


# Optimization for drawing neural network
def prerender_node_ids() -> list:
    renders = []
    font = pygame.font.Font(FONT, NODE_ID_FONT_SIZE)
    for id in range(20):
        renders.append(font.render(str(id), True, BRIGHT_BLUE))

    return renders


if __name__ == "__main__":
    main()
