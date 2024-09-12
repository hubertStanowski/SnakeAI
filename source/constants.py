# Window dimensions
TOP_MARGIN = 50
BOTTOM_MARGIN = 50
LEFT_MARGIN = 50
RIGHT_MARGIN = 500
GAME_SIZE = 800
WINDOW_WIDTH = GAME_SIZE + LEFT_MARGIN + RIGHT_MARGIN
WINDOW_HEIGHT = GAME_SIZE + BOTTOM_MARGIN + TOP_MARGIN
BUTTON_WIDTH = 50
BUTTON_HEIGHT = 50

GRAPH_SIZE = 25
NODE_SIZE = GAME_SIZE // GRAPH_SIZE

VELOCITY = 1
STARTING_ROW = GRAPH_SIZE // 2
STARTING_COL = 2
STEP_LIMIT = 250  # was 500 change back if worse performance

FPS = [7, 10, 20]


# Font
FONT = None
SCORE_FONT_SIZE = 70
RESET_FONT_SIZE = 150
NODE_ID_FONT_SIZE = 24
BUTTON_FONT_SIZE = 40
BUTTON_INFO_FONT_SIZE = BUTTON_FONT_SIZE + 10
EVOL_INFO_FONT_SIZE = BUTTON_FONT_SIZE
GENERATION_FONT_SIZE = SCORE_FONT_SIZE
PAUSED_FONT_SIZE = 100

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RUBY = (224, 17, 95)
ORANGE = (223, 120, 17)
DARK_GREEN = (37, 165, 97)
BRIGHT_BLUE = (51, 255, 255)
LIGHT_GREEN = (5, 179, 86)

BACKGROUND_COLOR = (31, 59, 77)
GRID_COLOR = (78, 130, 163)
FOOD_COLOR = RUBY
BUTTON_FONT_COLOR = BACKGROUND_COLOR
