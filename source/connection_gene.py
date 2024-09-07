from node_gene import NodeGene
from neat_config import NeatConfig

import random


class ConnectionGene:
    def __init__(self, input: NodeGene, output: NodeGene, weight: float, innovation_number: int, enabled: bool = True) -> None:
        self.input: NodeGene = input
        self.output: NodeGene = output
        self.weight: float = weight
        self.innovation_number: int = innovation_number
        self.enabled: bool = enabled

    def disable(self) -> None:
        self.enabled = False

    def mutate_weight(self, config: NeatConfig) -> None:
        if random.random() < config.get_big_weight_mutation_probablility():
            self.weight = random.uniform(-1, 1)
        else:
            self.weight += (random.gauss() / 50)

            self.weight = min(self.weight, 1)
            self.weight = max(self.weight, -1)

    def clone(self, input: NodeGene, output: NodeGene) -> 'ConnectionGene':
        return ConnectionGene(input, output, self.weight, self.innovation_number, enabled=self.enabled)
