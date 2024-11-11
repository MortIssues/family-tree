import json

from node import Node

class Tree(Node):
    def __init__(self, name = None, parent = None):
        super().__init__(name, parent)

    def save_json(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)
        print(f"Family tree saved to {file_path}")

    @classmethod
    def load_json(cls, filename):
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            print(f"Family tree loaded from {filename}")
            return cls.from_dict(data)
        except FileNotFoundError:
            print(f"No file found at {filename}, starting with an empty tree.")
            return None
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {filename}")
            return None

    def display_tree(self):
        print("\n".join(self.traverse_preorder_formatted()))