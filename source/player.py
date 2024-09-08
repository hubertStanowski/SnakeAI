from constants import *
from graph import *
from genome import Genome
from neat_config import NeatConfig


class SnakeNode:
    def __init__(self, graph: Graph, row: int, col: int) -> None:
        self.row = row
        self.col = col
        self.color = SNAKE_COLOR
        self.update_graph(graph)

    def update_graph(self, graph: Graph) -> None:
        graph.grid[self.row][self.col].color = self.color


class Player:
    def __init__(self) -> None:
        self.graph = Graph(GRAPH_SIZE)
        self.body = []
        self.row_vel = 0
        self.col_vel = VELOCITY
        self.alive = True
        self.moving = True
        self.body.append(SnakeNode(self.graph, STARTING_ROW, STARTING_COL))
        self.body.append(SnakeNode(self.graph, STARTING_ROW-1, STARTING_COL))
        self.head = self.body[0]
        self.graph.generate_food()
        # NEAT
        self.fitness: float = 0
        self.lifespan: int = 0
        self.genome_inputs: int = 8
        self.genome_outputs: int = 4
        self.genome: Genome = Genome(self.genome_inputs, self.genome_outputs)
        self.vision: list[float] = []
        self.sensor_view_data: list[float] = []
        self.steps = 0

    def draw(self, window) -> None:
        self.graph.draw(window)

    def update(self) -> None:
        if not self.moving:
            return
        if self.steps >= STEP_LIMIT:
            self.moving = False
            self.alive = False
        self.steps += 1
        self.lifespan += 1
        tail_row, tail_col = self.body[-1].row, self.body[-1].col

        for i in range(len(self.body) - 1, 0, -1):
            self.body[i].row = self.body[i-1].row
            self.body[i].col = self.body[i-1].col
            self.body[i].update_graph(self.graph)

        self.move_head()
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

    # NEAT
    def clone(self) -> 'Player':
        clone = Player()
        clone.genome = self.genome.clone()
        clone.fitness = self.fitness
        clone.genome.generate_network()

        return clone

    def crossover(self, config: NeatConfig, other_parent: 'Player') -> 'Player':
        child = Player()
        child.genome = self.genome.crossover(config, other_parent.genome)
        child.genome.generate_network()

        return child

    def update_fitness(self) -> None:
        survival_bonus = self.lifespan / 40
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
        self.vision.append(int(food_row < self.head.row))
        self.vision.append(int(food_row > self.head.row))
        self.vision.append(int(food_col < self.head.col))
        self.vision.append(int(food_col > self.head.col))

        top_distance = self.head.row
        bottom_distance = self.graph.size - self.head.row - 1
        left_distance = self.head.col
        right_distance = self.graph.size - self.head.col - 1

        # # wall detection
        # self.vision.append(remap(top_distance, 0, self.graph.size - 1, 0, 1))
        # self.vision.append(
        #     remap(bottom_distance, 0, self.graph.size - 1, 0, 1))
        # self.vision.append(remap(left_distance, 0, self.graph.size - 1, 0, 1))
        # self.vision.append(remap(right_distance, 0, self.graph.size - 1, 0, 1))

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

        # self.vision.append(remap(bottom_body, 0, self.graph.size-1, 0, 1))
        # self.vision.append(remap(top_body, 0, self.graph.size-1, 0, 1))
        # self.vision.append(remap(right_body, 0, self.graph.size-1, 0, 1))
        # self.vision.append(remap(left_body, 0, self.graph.size-1, 0, 1))

        # for dr, dc in DIRECTIONS:
        #     try:
        #         current = self.graph.grid[self.head.row+dr][self.head.col+dc]
        #         self.vision.append(int(current.is_snake()))
        #     except:
        #         self.vision.append(0)

        top_obstacle = min(top_body, top_distance)
        bottom_obstacle = min(bottom_body, bottom_distance)
        left_obstacle = min(left_body, left_distance)
        right_obstacle = min(right_body, right_distance)

        self.vision.append(remap(top_obstacle, 0, self.graph.size-1, 0, 1))
        self.vision.append(remap(bottom_obstacle, 0, self.graph.size-1, 0, 1))
        self.vision.append(remap(left_obstacle, 0, self.graph.size-1, 0, 1))
        self.vision.append(remap(right_obstacle, 0, self.graph.size-1, 0, 1))

    def decide(self, show=False) -> None:
        if not self.vision:
            return

        outputs = self.genome.feed_forward(self.vision)
        if show:
            print(outputs)
        decision = max(outputs)
        # each decision into function and if can't do that one randomize
        if outputs[0] == decision:
            if self.row_vel != 1:
                self.row_vel = -1
                self.col_vel = 0
            else:
                self.row_vel = 0
                self.col_vel = random.choice([-1, 1])
        elif outputs[1] == decision:
            if self.row_vel != -1:
                self.row_vel = 1
                self.col_vel = 0
            else:
                self.row_vel = 0
                self.col_vel = random.choice([-1, 1])
        elif outputs[2] == decision:
            if self.col_vel != 1:
                self.row_vel = 0
                self.col_vel = -1
            else:
                self.row_vel = random.choice([-1, 1])
                self.col_vel = 0
        elif outputs[3] == decision:
            if self.col_vel != -1:
                self.row_vel = 0
                self.col_vel = 1
            else:
                self.row_vel = random.choice([-1, 1])
                self.col_vel = 0
