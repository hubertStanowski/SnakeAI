from node_gene import NodeGene
from connection_gene import ConnectionGene
from innovation_history import InnovationHistory
from neat_config import NeatConfig

import random
from collections import defaultdict


class Genome:
    def __init__(self, inputs: int, outputs: int, crossover: bool = False) -> None:
        self.nodes: list[NodeGene] = []
        self.connections: list[ConnectionGene] = []
        self.inputs: int = inputs
        self.outputs: int = outputs
        self.bias_node: int = None
        self.layer_count: int = 2
        self.next_node_id: int = 0
        self.network: list[NodeGene] = []

        if crossover:
            return

        for _ in range(self.inputs):
            self.nodes.append(NodeGene(self.next_node_id, layer=0))
            self.next_node_id += 1

        for _ in range(self.outputs):
            self.nodes.append(NodeGene(self.next_node_id, layer=1))
            self.next_node_id += 1

        self.nodes.append(NodeGene(self.next_node_id, layer=0))
        self.bias_node = self.next_node_id
        self.next_node_id += 1

    def mutate(self, config: NeatConfig, innovation_history: list[InnovationHistory]) -> None:
        if not self.connections:
            self.add_connection(config, innovation_history)

        if random.random() < config.get_weight_mutation_probablility():
            for connection in self.connections:
                connection.mutate_weight(config)

        if random.random() < config.get_add_connection_mutation_probability():
            self.add_connection(config, innovation_history)

        if random.random() < config.get_add_node_mutation_probablility():
            self.add_node(config, innovation_history)

    def add_connection(self, config: NeatConfig, innovation_history: list[InnovationHistory]) -> None:
        if self.fully_connected():
            return

        node1 = random.randrange(0, len(self.nodes))
        node2 = random.randrange(0, len(self.nodes))

        while self.not_useful_connection(node1, node2):
            node1 = random.randrange(0, len(self.nodes))
            node2 = random.randrange(0, len(self.nodes))

        if self.nodes[node1].layer > self.nodes[node2].layer:
            node1, node2 = node2, node1

        connection_innovation_number = self.get_innovation_number(
            config, innovation_history, self.nodes[node1], self.nodes[node2])

        self.connections.append(ConnectionGene(
            self.nodes[node1], self.nodes[node2], random.uniform(-1, 1), connection_innovation_number))

        self.connect_nodes()

    def add_node(self, config: NeatConfig, innovation_history: InnovationHistory) -> None:
        if not self.connections:
            self.add_connection(config, innovation_history)
            return

        chosen_connection = random.randrange(0, len(self.connections))

        # Limit tries to avoid infinite loops
        # Don't know how but it sometimes gets into an infinite loop even though a node can have just 1 connection with bias_node and if there are more than 1 connections
        # it shouldn't be possible to constantly select the one with bias_node, but this limit for tries should fix it regardless
        tries = 0
        while self.connections[chosen_connection].input == self.nodes[self.bias_node] and len(self.connections) != 1 and tries < 3:
            chosen_connection = random.randrange(0, len(self.connections))
            tries += 1

        if tries >= 3:
            self.add_connection(config, innovation_history)
            return

        self.connections[chosen_connection].disable()

        new_node_id = self.next_node_id
        self.next_node_id += 1
        self.nodes.append(NodeGene(new_node_id))

        # Connect with the input node of the selected connection
        current_innovation_number = self.get_innovation_number(
            config, innovation_history, self.connections[chosen_connection].input, self.get_node(new_node_id))
        self.connections.append(ConnectionGene(
            self.connections[chosen_connection].input, self.get_node(new_node_id), 1, current_innovation_number))

        # Connect with the output node of the selected connection
        current_innovation_number = self.get_innovation_number(
            config, innovation_history, self.get_node(new_node_id), self.connections[chosen_connection].output)
        self.connections.append(ConnectionGene(self.get_node(
            new_node_id), self.connections[chosen_connection].output, self.connections[chosen_connection].weight, current_innovation_number))

        self.get_node(
            new_node_id).layer = self.connections[chosen_connection].input.layer + 1

        # Connect with the bias node
        current_innovation_number = self.get_innovation_number(
            config, innovation_history, self.nodes[self.bias_node], self.get_node(new_node_id))
        self.connections.append(ConnectionGene(self.nodes[self.bias_node], self.get_node(
            new_node_id), 0, current_innovation_number))

        if self.get_node(new_node_id).layer == self.connections[chosen_connection].output.layer:
            for i in range(len(self.nodes) - 1):
                if self.nodes[i].layer >= self.get_node(new_node_id).layer:
                    self.nodes[i].layer += 1

            self.layer_count += 1

        self.connect_nodes()

    def crossover(self, config: NeatConfig, parent: 'Genome') -> 'Genome':
        child = Genome(self.inputs, self.outputs, crossover=True)
        child.layer_count = self.layer_count
        child.next_node_id = self.next_node_id
        child.bias_node = self.bias_node

        # First add here and then to child.connections to avoid duplicating complicated code
        new_child_connections: list[ConnectionGene] = []

        for node in self.nodes:
            child.nodes.append(node.clone())

        for connection in self.connections:
            parent_connection = self.get_matching_connection(
                parent, connection.innovation_number)
            child_enable = True

            if parent_connection != -1:
                if not connection.enabled or not parent.connections[parent_connection].enabled:
                    if random.random() < config.get_crossover_connection_disable_probablility():
                        child_enable = False

                if random.random() < 0.5:
                    new_child_connections.append(
                        (connection, child_enable))
                else:
                    new_child_connections.append(
                        (parent.connections[parent_connection], child_enable))

            else:
                new_child_connections.append(
                    (connection, connection.enabled))

        for new_connection, new_enable in new_child_connections:
            child_input = child.get_node(new_connection.input.id)
            child_output = child.get_node(new_connection.output.id)
            child.connections.append(
                new_connection.clone(child_input, child_output))
            child.connections[-1].enabled = new_enable

        child.connect_nodes()

        return child

    def get_innovation_number(self, config: NeatConfig, innovation_history: list[InnovationHistory], input: NodeGene, output: NodeGene) -> int:
        new = True
        current_innovation_number = config.get_next_innovation_number()
        for history in innovation_history:
            if history.matches(self, input, output):
                new = False
                current_innovation_number = history.innovation_number
                break

        if new:
            connected_innovation_numbers = []
            for connection in self.connections:
                connected_innovation_numbers.append(
                    connection.innovation_number)

            innovation_history.append(InnovationHistory(
                input.id, output.id, current_innovation_number, connected_innovation_numbers))

            config.update_next_innovation_number()

        return current_innovation_number

    def not_useful_connection(self, node1: int, node2: int) -> bool:
        if self.nodes[node1].layer == self.nodes[node2].layer:
            return True
        if self.nodes[node1].is_connected_to(self.nodes[node2]):
            return True

        return False

    def fully_connected(self) -> bool:
        possible_connections = 0
        nodes_per_layer = defaultdict(int)

        for node in self.nodes:
            nodes_per_layer[node.layer] += 1

        # possible connections for each layer are (node count of this layer) * (node count of all layers in front of it)
        for i in range(self.layer_count - 1):
            nodes_in_front = 0
            for j in range(i+1, self.layer_count):
                nodes_in_front += nodes_per_layer[j]

            possible_connections += nodes_per_layer[i] * nodes_in_front

        return possible_connections <= len(self.connections)

    def connect_nodes(self) -> None:
        for node in self.nodes:
            node.output_connections = []

        for connection in self.connections:
            connection.input.output_connections.append(connection)

    def get_node(self, target_id: int) -> NodeGene:
        for node in self.nodes:
            if node.id == target_id:
                return node

    def get_matching_connection(self, parent: 'Genome', innovation_number: int) -> int:
        for i in range(len(parent.connections)):
            if parent.connections[i].innovation_number == innovation_number:
                return i

        return -1

    def generate_network(self) -> None:
        self.connect_nodes()
        self.network = []
        for layer in range(self.layer_count):
            for node in self.nodes:
                if node.layer == layer:
                    self.network.append(node)

    def feed_forward(self, input_values: list[float]) -> list[float]:
        for i in range(self.inputs):
            self.nodes[i].output_value = input_values[i]
        self.nodes[self.bias_node].output_value = 1

        for node in self.network:
            node.engage()

        outputs = []

        for i in range(self.outputs):
            # output nodes are initialized after inputs so we start indexing after self.inputs
            outputs.append(self.nodes[self.inputs+i].output_value)

        for node in self.nodes:
            node.input_sum = 0

        return outputs

    def clone(self) -> 'Genome':
        clone = Genome(self.inputs, self.outputs, crossover=True)

        for node in self.nodes:
            clone.nodes.append(node.clone())

        for connection in self.connections:
            clone.connections.append(connection.clone(clone.get_node(
                connection.input.id), clone.get_node(connection.output.id)))

        clone.layer_count = self.layer_count
        clone.next_node_id = self.next_node_id
        clone.bias_node = self.bias_node
        clone.connect_nodes()

        return clone
