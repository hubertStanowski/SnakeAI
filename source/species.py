from player import Player
from genome import Genome
from innovation_history import InnovationHistory
from neat_config import NeatConfig

import random
import math


class Species:
    def __init__(self, representative: Player) -> None:
        self.players: list[Player] = [representative]
        self.representative: Player = representative
        self.best_fitness: float = 0
        self.average_fitness: float = self.best_fitness
        self.staleness: int = 0

    def reproduce(self, config: NeatConfig, innovation_history: list[InnovationHistory]) -> Player:
        if len(self.players) < 1:
            return

        if random.random() < config.get_no_crossover_probability():
            child = self.select_player().clone()
        else:
            if len(self.players) < 2:
                return
            parent1 = self.select_player()
            parent2 = self.select_player()

            if parent1.fitness > parent2.fitness:
                child = parent1.crossover(config, parent2)
            else:
                child = parent2.crossover(config, parent1)

        child.genome.mutate(config, innovation_history)

        return child

    def is_this_species(self, config: NeatConfig, tested_genome: Genome) -> bool:
        """
            Compare a tested_genome to species representative and returns whether it is close enough to it to be considered the same species,
            based on compatibility coefficients and compatibility threshold defined beforehand by the user.
        """
        # Formula for large_genome_normalizer given in the article by creators of NEAT
        large_genome_normalizer = max(len(tested_genome.connections) - 20, 1)

        average_weight_difference = self.get_average_weight_difference(
            tested_genome, self.representative.genome)
        excess_disjoint_count = self.get_excess_disjoint_count(
            tested_genome, self.representative.genome)

        # Formula for compatibility given in the article by creators of NEAT
        compatibility = (config.get_excess_disjoint_coefficient() * excess_disjoint_count /
                         large_genome_normalizer) + (config.get_weight_difference_coefficient() * average_weight_difference)

        return compatibility < config.get_compatibility_threshold()

    def sort(self) -> None:
        if not self.players:
            self.staleness = math.inf
            return

        self.players.sort(key=lambda player: player.fitness, reverse=True)

        if self.players[0].fitness > self.best_fitness:
            self.staleness = 0
            self.best_fitness = self.players[0].fitness
            self.representative = self.players[0]
        else:
            self.staleness += 1

    def remove_low_performers(self) -> None:
        """
            Removes the bottom half of players.
            !ONLY USE AFTER SORTING!
        """
        if len(self.players) <= 2:
            return

        for _ in range(len(self.players) // 2):
            self.players.pop()

    def get_average_weight_difference(self, genome1: Genome, genome2: Genome) -> float:
        """
            Return the average weight difference of matching connections in genome1 and genome2 
        """
        if not genome1.connections or not genome2.connections:
            return 0

        match_count = 0
        diff_sum = 0

        for i in range(len(genome1.connections)):
            for j in range(len(genome2.connections)):
                if genome1.connections[i].innovation_number == genome2.connections[j].innovation_number:
                    match_count += 1
                    diff_sum += abs(genome1.connections[i].weight -
                                    genome2.connections[j].weight)
                    break

        if match_count == 0:
            return math.inf

        return diff_sum / match_count

    def get_excess_disjoint_count(self, genome1: Genome, genome2: Genome) -> int:
        """
            Returns the number of genes that don't match between genome1 and genome2
        """
        match_count = 0
        for i in range(len(genome1.connections)):
            for j in range(len(genome2.connections)):
                if genome1.connections[i].innovation_number == genome2.connections[j].innovation_number:
                    match_count += 1
                    break

        return len(genome1.connections) + len(genome2.connections) - 2 * match_count

    def select_player(self) -> Player:
        """
            Select a player for reproduction
        """
        fitness_sum = sum([player.fitness for player in self.players])
        random_threshold = random.uniform(0, fitness_sum)

        running_sum = 0
        for player in self.players:
            running_sum += player.fitness
            if running_sum >= random_threshold:
                return player

    def update_average_fitness(self) -> None:
        if not self.players:
            return

        self.average_fitness = sum(
            [player.fitness for player in self.players]) / len(self.players)

    def share_fitness(self) -> None:
        for player in self.players:
            player.fitness /= len(self.players)

    def add(self, new: Player) -> None:
        self.players.append(new)
