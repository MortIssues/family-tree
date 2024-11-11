class Node:
    def __init__(self, name, parent = None):
        self.name = name
        self.parent = parent
        self.children = []

        if parent:
            parent.children.append(self)

    def add_child(self, child_name):
        return Node(name=child_name, parent=self)

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

    def find_node_by_name(self, name):
        if self.name == name:
            return self

        for child in self.children:
            found_node = child.find_node_by_name(name)
            if found_node is not None:
                return found_node

        return None

    def delete_node_by_name(self, name):
        for i, child in enumerate(self.children):
            if child.name == name:
                del self.children[i]
