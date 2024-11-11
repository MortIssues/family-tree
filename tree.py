import json
from node import Node

class Tree:
    def __init__(self):
        self.root = None

    def set_root(self, name):
        self.root = Node(name=name)
        return self.root

    def save_json(self, file_path):
        if not self.root:
            print("No root node to save.")
            return

        with open(file_path, 'w') as f:
            json.dump(self.root.to_dict(), f, indent=4)
        print(f"Family tree saved to {file_path}")

    def load_json(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.root = Node.from_dict(data)
            print(f"Family tree loaded from {file_path}")
        except FileNotFoundError:
            print(f"No file found at {file_path}, starting with an empty tree.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from {file_path}")

    def display_tree(self):
        if not self.root:
            print("No root node set.")
        else:
            print("\n".join(self.root.traverse_preorder_formatted()))

    def traverse_preorder(self):
        if not self.root:
            print("No root node set.")
            return []
        return self.root.traverse_preorder()