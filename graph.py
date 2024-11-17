import json
import pygame
import math
from node import Node


def draw_dashed_line(surface, color, start_pos, end_pos, dash_length=10, gap_length=5, thickness=2):
    """
    Function for drawing a custom dashed line.

    Args:
        surface (pygame.Surface): Surface to draw the line.
        color (tuple): Color of the line.
        start_pos (tuple): Start position of the line.
        end_pos (tuple): End position of the line.
        dash_length (int): Length of the dashed line. Defaults to 10.
        gap_length (int): Length of the gap between dashes. Defaults to 5.
        thickness (int): Thickness of the dashed line. Defaults to 2.
    """

    total_length = math.hypot(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
    num_dashes = int(total_length / (dash_length + gap_length))

    dx = (end_pos[0] - start_pos[0]) / total_length
    dy = (end_pos[1] - start_pos[1]) / total_length

    for i in range(num_dashes):
        dash_start = (start_pos[0] + i * (dash_length + gap_length) * dx,
                      start_pos[1] + i * (dash_length + gap_length) * dy)
        dash_end = (dash_start[0] + dash_length * dx, dash_start[1] + dash_length * dy)
        pygame.draw.line(surface, color, dash_start, dash_end, thickness)

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name, gender=None, birthdate=None):
        """
        Adds a node to the graph.

        Args:
            gender (str): The gender of the node.
            birthdate (str): The birthdate of the node.

        Returns:
            node (Node): The created node.
        """

        if name not in self.nodes:
            self.nodes[name] = Node(name, gender, birthdate)
        else:
            print(f"Person {name} already exists.")
        print(self.nodes)
        return self.nodes[name]

    def get_node(self, name):
        """
        Finds and returns a node based on its name.

        Args:
            name (str): The name of the node.

        Returns:
            node (Node): The node.
        """

        return self.nodes.get(name)

    def remove_node(self, name):
        """
        Removes a node, including all references to it.

        Args:
            name (str): The name of the node to be removed.
        """

        if name in self.nodes:
            person = self.nodes[name]
            for parent in person.parents:
                parent.children.remove(person)
            for child in person.children:
                child.parents.remove(person)
            for spouse in person.spouses:
                spouse.spouses.remove(person)
            for sibling in person.siblings:
                sibling.siblings.remove(person)
            del self.nodes[name]
        else:
            print(f"Person {name} does not exist.")

    def to_dict(self):
        """
        Begins the dictionary convertion for storing information in a json file.

        Returns:
            Dictionary containing data for all nodes.
        """

        return {name: person.to_dict() for name, person in self.nodes.items()}

    @classmethod
    def from_dict(cls, data):
        """
        Creates a graph object from a dictionary representation of nodes and their relationships.

        Args:
            data (dict): A dictionary where the keys are node names and the values are dictionaries.

        Returns:
            graph (Graph): A new Graph object populated with nodes and their relationships as defined in data.
        """

        graph = cls()
        temp_nodes = {name: Node(name) for name in data.keys()}

        for name, details in data.items():
            node = temp_nodes[name]
            node.gender = details.get("gender")
            node.birthdate = details.get("birthdate")

        for name, details in data.items():
            node = temp_nodes[name]
            for parent_name in details.get("parents", []):
                node.add_parent(temp_nodes[parent_name])
            for child_name in details.get("children", []):
                node.add_child(temp_nodes[child_name])
            for spouse_name in details.get("spouses", []):
                node.add_spouse(temp_nodes[spouse_name])
            for sibling_name in details.get("siblings", []):
                node.add_sibling(temp_nodes[sibling_name])

        graph.nodes = temp_nodes
        return graph

    def save_to_json(self, file_path):
        """
        Saves the graph to a json file.
        Args:
            file_path (str): The path to the json file for the graph to be saved to.
        """

        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)
        print(f"Family graph saved to {file_path}")

    @classmethod
    def load_from_json(cls, file_path):
        """
        Loads graph information from a json file and converts it into a Graph object.

        Args:
            file_path (str): The path to the json file that contains the graph data.

        Returns:
            graph (Graph): A new Graph object created from the data in the json file, or an empty graph if an error is
            thrown.
        """

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f"Graph loaded from {file_path}.")
            return cls.from_dict(data)
        except FileNotFoundError:
            print(f"No file found at {file_path}, starting with an empty graph.")
            return cls()
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}.")
            return cls()

    def display_graph(self):
        """
        Redundant function to display unformatted node information.
        Keeping around for bug testing.
        """

        for name, node in self.nodes.items():
            print(f"{name}: {node.to_dict()}")

    def draw(self, surface):
        """
        Function to draw all nodes to the surface.

        Args:
            surface (pygame.Surface): Surface to draw the nodes.
        """

        for node in self.nodes.values():
            node.draw(surface)

    def draw_connections(self, surface):
        """
        Function to draw connections between nodes.

        Args:
            surface (pygame.Surface): Surface to draw the connections.
        """

        drawn_pairs = []
        for node in self.nodes.values():
            # Loop through the nodes children and draw lines between them
            for child in node.children:
                pygame.draw.line(surface, (40, 28, 73), (node.x, node.y), (child.x, child.y), 2)

                # Draw arrow to indicate direction of descendency.
                dx = node.x - child.x
                dy = node.y - child.y

                # Find angle in radians given the delta x and y
                angle = math.atan2(dy, dx)

                # Find the middle of the line.
                mid_x = (node.x + child.x) / 2
                mid_y = (node.y + child.y) / 2

                # Fine each point on the arrow.
                arrow_tip = (mid_x, mid_y)
                arrow_left = (mid_x + 8 * math.cos(angle - math.pi / 6), mid_y + 8 * math.sin(angle - math.pi / 6))
                arrow_right = (mid_x + 8 * math.cos(angle + math.pi / 6), mid_y + 8 * math.sin(angle + math.pi / 6))

                # Draw the arrow.
                pygame.draw.polygon(surface, (40, 28, 73), [arrow_tip, arrow_left, arrow_right])

            for spouse in node.spouses:
                # Draw lines between spouse and append them to drawn_pairs.
                pair = tuple(sorted([node.name, spouse.name]))
                if pair not in drawn_pairs:
                    draw_dashed_line(surface, (40, 28, 73), (node.x, node.y), (spouse.x, spouse.y))
                    drawn_pairs.append(pair)