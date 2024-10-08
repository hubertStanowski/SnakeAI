from constants import *
from graph import *
from genome import Genome
from neat_config import NeatConfig

from collections import defaultdict
import math


class SnakeNode:
    def __init__(self, graph: Graph, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.color = WHITE
        self.update_graph(graph)

    def update_graph(self, graph: Graph) -> None:
        graph.grid[self.row][self.col].color = self.color

    def set_color(self, index: int, total: int, step: int) -> None:
        # Calculate the hue based on the position in the snake body
        hue = index / total
        # Calculate the brightness to create a pulsing effect
        brightness = (1 + 0.5 * math.sin((step+index) / 2.5)) / 1.5
        # Saturation between 80-90%
        saturation = 0.85 + 0.05 * math.sin((5*step + index) / 2.5)
        r, g, b = self.hsv_to_rgb(hue, saturation, brightness)

        # Apply a metallic effect by adjusting the RGB values
        metallic_factor = 0.5
        r = r * (1 - metallic_factor) + metallic_factor
        g = g * (1 - metallic_factor) + metallic_factor
        b = b * (1 - metallic_factor) + metallic_factor

        self.color = (int(r * 255), int(g * 255), int(b * 255))

    @staticmethod
    def hsv_to_rgb(h, s, v) -> tuple[float, float, float]:
        if s == 0.0:
            return v, v, v
        i = int(h * 6.0)  # Assume hue < 1
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0:
            return v, t, p
        if i == 1:
            return q, v, p
        if i == 2:
            return p, v, t
        if i == 3:
            return p, q, v
        if i == 4:
            return t, p, v
        if i == 5:
            return v, p, q
        # Fallback to white in case of an error
        return WHITE

    def pos(self) -> tuple[int, int]:
        return self.row, self.col


class Player:
    def __init__(self) -> None:
        self.graph = Graph(GRAPH_SIZE)
        self.body = []
        self.row_vel = 0
        self.col_vel = VELOCITY
        self.alive = True
        self.moving = True
        self.body.append(SnakeNode(self.graph, STARTING_ROW, STARTING_COL))
        self.body.append(SnakeNode(self.graph, STARTING_ROW, STARTING_COL-1))
        self.head = self.body[0]
        self.graph.generate_food()
        # NEAT
        self.fitness: float = 0
        self.lifespan: int = 0
        self.genome_inputs: int = 12
        self.genome_outputs: int = 3
        self.genome: Genome = Genome(self.genome_inputs, self.genome_outputs)
        self.vision: list[float] = []
        self.sensor_view_data: list[float] = []
        self.steps = 0
        self.generation = 1

    def draw(self, window, gridlines: bool = True) -> None:
        self.graph.draw(window, gridlines)
        if not self.alive:
            return

        # Draw eyes on the head
        eye_radius = 4
        eye_offset = 6

        # Calculate positions for the eyes based on the head's position and velocity direction
        x = LEFT_MARGIN + self.head.col * NODE_SIZE
        y = TOP_MARGIN + self.head.row * NODE_SIZE

        if self.row_vel == -VELOCITY:  # Moving up
            eye1_pos = (x + NODE_SIZE // 2 - eye_offset,
                        y + NODE_SIZE // 2 - eye_offset // 2)
            eye2_pos = (x + NODE_SIZE // 2 + eye_offset,
                        y + NODE_SIZE // 2 - eye_offset // 2)
        elif self.row_vel == VELOCITY:  # Moving down
            eye1_pos = (x + NODE_SIZE // 2 - eye_offset,
                        y + NODE_SIZE // 2 + eye_offset // 2)
            eye2_pos = (x + NODE_SIZE // 2 + eye_offset,
                        y + NODE_SIZE // 2 + eye_offset // 2)
        elif self.col_vel == -VELOCITY:  # Moving left
            eye1_pos = (x + NODE_SIZE // 2 - eye_offset // 2,
                        y + NODE_SIZE // 2 - eye_offset)
            eye2_pos = (x + NODE_SIZE // 2 - eye_offset // 2,
                        y + NODE_SIZE // 2 + eye_offset)
        elif self.col_vel == VELOCITY:  # Moving right
            eye1_pos = (x + NODE_SIZE // 2 + eye_offset // 2,
                        y + NODE_SIZE // 2 - eye_offset)
            eye2_pos = (x + NODE_SIZE // 2 + eye_offset // 2,
                        y + NODE_SIZE // 2 + eye_offset)

        pygame.draw.circle(window, BLACK, eye1_pos, eye_radius)
        pygame.draw.circle(window, BLACK, eye2_pos, eye_radius)

    def update(self, animation=False) -> None:
        if not self.moving:
            return
        if self.steps >= STEP_LIMIT and not animation:
            self.moving = False
            self.alive = False
        self.steps += 1
        self.lifespan += 1
        tail_row, tail_col = self.body[-1].row, self.body[-1].col

        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].row = self.body[i-1].row
            self.body[i].col = self.body[i-1].col
            self.body[i].set_color(i, len(self.body), self.lifespan)
            self.body[i].update_graph(self.graph)

        self.move_head()
        self.head.set_color(0, len(self.body), self.lifespan)
        self.graph.grid[tail_row][tail_col].reset()

        self.check_collisions()
        if not self.moving:
            return

        self.head.update_graph(self.graph)

        if (self.head.row, self.head.col) == (self.graph.food.row, self.graph.food.col):
            self.body.append(SnakeNode(self.graph, tail_row, tail_col))
            self.graph.generate_food()
            self.steps = 0

    def check_collisions(self) -> None:
        collides_top_bottom = not (0 <= self.head.col < self.graph.size)
        collides_left_right = not (0 <= self.head.row < self.graph.size)

        if collides_top_bottom or collides_left_right:
            self.alive = False
            self.moving = False
        elif self.graph.grid[self.head.row][self.head.col].is_snake():
            self.alive = False
            self.moving = False

    def move_head(self) -> None:
        self.head.row += self.row_vel
        self.head.col += self.col_vel

    def get_score(self) -> int:
        return len(self.body) - 2

# Direction change for AI (for human they are relative to the user view not head)
    def turn_left(self) -> None:
        if self.row_vel != 0:
            self.col_vel = self.row_vel
            self.row_vel = 0
        else:
            self.row_vel = -self.col_vel
            self.col_vel = 0

    def turn_right(self) -> None:
        if self.row_vel != 0:
            self.col_vel = -self.row_vel
            self.row_vel = 0
        else:
            self.row_vel = self.col_vel
            self.col_vel = 0

    # NEAT
    def clone(self) -> 'Player':
        clone = Player()
        clone.genome = self.genome.clone()
        clone.fitness = self.fitness
        clone.generation = self.generation
        clone.genome.generate_network()

        return clone

    def crossover(self, config: NeatConfig, other_parent: 'Player') -> 'Player':
        child = Player()
        child.genome = self.genome.crossover(config, other_parent.genome)
        child.genome.generate_network()

        return child

    def update_fitness(self) -> None:
        survival_bonus = 0  # self.lifespan / 100
        food_bonus = self.get_score() ** 3
        collision_penalty = 1 if self.alive else 0.8
        self.fitness = (1 + food_bonus + survival_bonus) * collision_penalty

    def look(self) -> None:
        def remap(value: float, start1: float, stop1: float, start2: float, stop2: float) -> float:
            # Remaps a value in range(start1, stop1) proportionately to range(start2, stop2) and returns it
            return (value - start1) / (stop1 - start1) * (stop2 - start2) + start2

        self.vision = []

        # food detection
        food_row = self.graph.food.row
        food_col = self.graph.food.col

        top_food = int(food_row < self.head.row)
        bottom_food = int(food_row > self.head.row)
        left_food = int(food_col < self.head.col)
        right_food = int(food_col > self.head.col)

        # wall detection
        top_wall = self.head.row
        bottom_wall = self.graph.size - self.head.row - 1
        left_wall = self.head.col
        right_wall = self.graph.size - self.head.col - 1

        top_wall = remap(top_wall, 0, self.graph.size-1, 0, 1)
        bottom_wall = remap(bottom_wall, 0, self.graph.size-1, 0, 1)
        left_wall = remap(left_wall, 0, self.graph.size-1, 0, 1)
        right_wall = remap(right_wall, 0, self.graph.size-1, 0, 1)

        # body detection
        bottom_body = self.graph.size - 1
        for i in range(self.head.row+1, self.graph.size):
            if self.graph.grid[i][self.head.col].is_snake():
                bottom_body = i
                break

        top_body = self.graph.size - 1
        for i in range(self.head.row-1, -1, -1):
            if self.graph.grid[i][self.head.col].is_snake():
                top_body = i
                break

        right_body = self.graph.size - 1
        for j in range(self.head.col+1, self.graph.size):
            if self.graph.grid[self.head.row][j].is_snake():
                right_body = j
                break

        left_body = self.graph.size - 1
        for j in range(self.head.col-1, -1, -1):
            if self.graph.grid[self.head.row][j].is_snake():
                left_body = j
                break

        top_body = remap(top_body, 0, self.graph.size-1, 0, 1)
        bottom_body = remap(bottom_body, 0, self.graph.size-1, 0, 1)
        left_body = remap(left_body, 0, self.graph.size-1, 0, 1)
        right_body = remap(right_body, 0, self.graph.size-1, 0, 1)

        # going up
        if self.row_vel == -VELOCITY:
            self.vision.append(top_food)
            self.vision.append(bottom_food)
            self.vision.append(left_food)
            self.vision.append(right_food)

            self.vision.append(top_body)
            self.vision.append(bottom_body)
            self.vision.append(left_body)
            self.vision.append(right_body)

            self.vision.append(top_wall)
            self.vision.append(bottom_wall)
            self.vision.append(left_wall)
            self.vision.append(right_wall)
        # going down
        elif self.row_vel == VELOCITY:
            self.vision.append(bottom_food)
            self.vision.append(top_food)
            self.vision.append(right_food)
            self.vision.append(left_food)

            self.vision.append(bottom_body)
            self.vision.append(top_body)
            self.vision.append(right_body)
            self.vision.append(left_body)

            self.vision.append(bottom_wall)
            self.vision.append(top_wall)
            self.vision.append(right_wall)
            self.vision.append(left_wall)
        # going left
        elif self.col_vel == -VELOCITY:
            self.vision.append(left_food)
            self.vision.append(right_food)
            self.vision.append(bottom_food)
            self.vision.append(top_food)

            self.vision.append(left_body)
            self.vision.append(right_body)
            self.vision.append(bottom_body)
            self.vision.append(top_body)

            self.vision.append(left_wall)
            self.vision.append(right_wall)
            self.vision.append(bottom_wall)
            self.vision.append(top_wall)
        # going right
        elif self.col_vel == VELOCITY:
            self.vision.append(right_food)
            self.vision.append(left_food)
            self.vision.append(top_food)
            self.vision.append(bottom_food)

            self.vision.append(right_body)
            self.vision.append(left_body)
            self.vision.append(top_body)
            self.vision.append(bottom_body)

            self.vision.append(right_wall)
            self.vision.append(left_wall)
            self.vision.append(top_wall)
            self.vision.append(bottom_wall)

    def decide(self, show=False) -> None:
        if not self.vision:
            return

        outputs = self.genome.feed_forward(self.vision)
        if show:
            print(outputs)
        decision = max(outputs)

        if outputs[0] == decision:
            self.turn_left()
        elif outputs[1] == decision:
            self.turn_right()


# Here and not in genome.py as that file is meant to be reusable and this function is not

    def draw_network(self, window: pygame.Surface, node_id_renders: list[pygame.Surface]) -> None:
        if not self.genome.network:
            return

        radius = 14
        x = WINDOW_WIDTH - radius*5 + 15
        y = WINDOW_HEIGHT - BOTTOM_MARGIN + 10
        layer_count = self.genome.layer_count - 1
        y_diff = radius * 3
        x_diff = radius * 25 // layer_count

        layers = defaultdict(list)
        for node in self.genome.network:
            layers[node.layer].append(node)

        node_pos = {}

        for layer, nodes in layers.items():
            """
            Hardcoding as there have never been >13 nodes in a layer
            and don't want to overcomplicate it for nodes to look good 
            and add new ones symetrically
            """
            y_positions = [y - 6*y_diff, y - 5*y_diff, y - 7*y_diff, y - 4*y_diff, y - 8*y_diff,
                           y - 3*y_diff, y - 9*y_diff, y - 2*y_diff, y - 10*y_diff, y - y_diff,
                           y - 11*y_diff, y, y - 12*y_diff]
            for i, node in enumerate(nodes):
                node_pos[node] = (x-(layer_count-layer)*x_diff, y_positions[i])

        for connection in self.genome.connections:
            input_pos = node_pos[connection.input]
            output_pos = node_pos[connection.output]
            pygame.draw.line(window, BRIGHT_BLUE, input_pos,
                             output_pos, max(int(5 * abs(connection.weight)), 1))

        # Seperate loop and not when assigning positions so that the connection line doesn't overlay the id
        for node, pos in node_pos.items():
            text = node_id_renders[node.id]
            text_rect = text.get_rect(center=node_pos[node])

            pygame.draw.circle(window, BRIGHT_BLUE, node_pos[node], radius+2)
            pygame.draw.circle(window, RUBY, node_pos[node], radius)
            window.blit(text, text_rect)

        # Node adding order id | *y_diff
        """
        12  12
        11  10
        10  8
        9   6
        8   4
        7   2
        6   1
        5   3
        4   5
        3   7
        2   9
        1   11
        0   13
        """
