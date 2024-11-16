import json

from node import Node

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_node(self, name, gender=None, birthdate=None):
        if name not in self.nodes:
            self.nodes[name] = Node(name, gender, birthdate)
        else:
            print(f"Person {name} already exists.")
        return self.nodes[name]

    def get_node(self, name):
        return self.nodes.get(name)

    def remove_node(self, name):
        if name in self.nodes:
            person = self.nodes[name]
            # Remove relationships
            for parent in person.parents:
                parent.children.remove(person)
            for child in person.children:
                child.parents.remove(person)
            for spouse in person.spouses:
                spouse.spouses.remove(person)
            for sibling in person.siblings:
                sibling.siblings.remove(person)
            # Remove the node
            del self.nodes[name]
        else:
            print(f"Person {name} does not exist.")

    def to_dict(self):
        return {name: person.to_dict() for name, person in self.nodes.items()}

    @classmethod
    def from_dict(cls, data):
        graph = cls()
        temp_nodes = {name: Node(name) for name in data.keys()}

        # Populate nodes with attributes
        for name, details in data.items():
            node = temp_nodes[name]
            node.gender = details.get("gender")
            node.birthdate = details.get("birthdate")

        # Establish relationships
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
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)
        print(f"Family graph saved to {file_path}")

    @classmethod
    def load_from_json(cls, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            print(f"Family graph loaded from {file_path}")
            return cls.from_dict(data)
        except FileNotFoundError:
            print(f"No file found at {file_path}, starting with an empty graph.")
            return cls()
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}.")
            return cls()

    def display_graph(self):
        for name, node in self.nodes.items():
            print(f"{name}: {node.to_dict()}")

    def traverse_graph(self, start_name):
        visited = []

        def dfs(node):
            if node.name in visited:
                return
            visited.append(node.name)
            print(f"Visiting: {node.name}")
            for child in node.children:
                dfs(child)
            for spouse in node.spouses:
                dfs(spouse)
            for sibling in node.siblings:
                dfs(sibling)

        start_node = self.get_node(start_name)
        if start_node:
            dfs(start_node)
        else:
            print(f"Person {start_name} not found in the graph.")