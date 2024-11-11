class Node:
    def __init__(self, name, parent = None):
        self.name = name
        self.parent = parent
        self.children = []

        if parent:
            parent.children.append(self)

    def add_child(self, child_name):
        return Node(name=child_name, parent=self)

    def display_tree(self, level = 0):
        print(" " * (level * 3) + self.name)
        for child in self.children:
            child.display_tree(level + 1)

    def to_dict(self):
        return {
            "name": self.name,
            "children": [child.to_dict() for child in self.children]
        }

    @classmethod
    def from_dict(cls, data, parent = None):
        node = cls(name=data['name'], parent=parent)
        for child_data in data.get('children', []):
            cls.from_dict(child_data, parent=node)
        return node

    def traverse_preorder(self, formatted = False):
        nodes = [self.name]
        for child in self.children:
            nodes.extend(child.traverse_preorder())
        return nodes

    def traverse_preorder_formatted(self, prefix = "", is_last = True):
        connector = "┗━ " if is_last else "┣━ "
        lines = [f"{prefix}{connector}{self.name}"]

        if self.children:
            new_prefix = prefix + ("   " if is_last else "┃  ")
            child_count = len(self.children)
            for i, child in enumerate(self.children):
                is_last_child = (i == child_count - 1)
                lines.extend(child.traverse_preorder_formatted(new_prefix, is_last_child))

        return lines
