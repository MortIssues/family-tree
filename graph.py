import json
from node import Node


class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name, gender=None, birthdate=None):
        """
        Adds a node to the graph.

        Args:
            name (str): The name of the node
            gender (str): The gender of the node.
            birthdate (str): The birthdate of the node.

        Returns:
            node (Node): The created node.
        """
        # Check if node already exists.
        if name not in self.nodes:
            # Add the node if it doesn't
            self.nodes[name] = Node(name, gender, birthdate)
        else:
            print(f"Person {name} already exists.")
        print(self.nodes)

        # Return it so it can be accessed via variable.
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
        # Find everywhere the node could be and remove reference to it before deleting the node itself.
        if name in self.nodes:
            node = self.nodes[name]
            for parent in node.parents:
                parent.children.remove(node)
            for child in node.children:
                child.parents.remove(node)
            node.spouse.spouse = None
            del self.nodes[name]
        else:
            print(f"Person {name} does not exist.")

    def to_dict(self):
        """
        Begins the dictionary convertion for storing information in a json file.

        Returns:
            Dictionary containing data for all nodes.
        """
        return {name: node.to_dict() for name, node in self.nodes.items()}

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

        # Loop through nodes and set the information for each of the nodes.
        for name, details in data.items():
            node = temp_nodes[name]
            node.gender = details.get("gender")
            node.birthdate = details.get("birthdate")
            node.spouse = temp_nodes.get(details.get("spouse"))
            for parent_name in details.get("parents", []):
                node.parents.append(temp_nodes[parent_name])
            for child_name in details.get("children", []):
                node.children.append(temp_nodes[child_name])

        # Return the graph object.
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