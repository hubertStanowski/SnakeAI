from constants import *

import pygame


class Button:
    def __init__(self, label, x, y, color=BRIGHT_BLUE,  visible=True) -> None:
        self.label = label
        self.x = x
        self.y = y
        self.width, self.height = BUTTON_WIDTH, BUTTON_HEIGHT
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = color
        self.visible = visible

    def draw(self, window) -> None:
        if self.visible:
            pygame.draw.rect(window, self.color, self.rect, border_radius=10)
            current_font = pygame.font.SysFont(FONT, BUTTON_FONT_SIZE)
            label = current_font.render(self.label, True, BUTTON_FONT_COLOR)
            label_rect = label.get_rect(
                center=(self.x + self.width // 2, self.y + self.height // 2))
            window.blit(label, label_rect)


def initialize_buttons() -> None:
    generation_buttons = {}

    x = LEFT_MARGIN + GAME_SIZE + BUTTON_WIDTH*2 + 20
    y = TOP_MARGIN + 120
    x_diff = BUTTON_WIDTH*1.5

    generation_buttons[5] = Button("5", x, y)
    generation_buttons[10] = Button("10", x + x_diff, y)
    generation_buttons[20] = Button("20", x + 2*x_diff, y)
    generation_buttons[30] = Button("30", x + 3*x_diff, y)

    return generation_buttons
