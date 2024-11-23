from ci_helper_functions import requires_selected_node


class Node:
    def __init__(self, name, gender=None, birthdate=None):
        self.name = name
        self.gender = gender
        self.birthdate = birthdate
        self.parents = []
        self.children = []
        self.spouse = None

    def set_parents(self, parent1, parent2):
        """Adds a parent to the node."""

        if parent1 == parent2.spouse and parent2 == parent1.spouse:
            self.parents.extend([parent1,parent2])
            parent1.children.append(self)
            parent2.children.append(self)

    def add_child(self, child):
        """Adds a child to the node."""

        self.children.append(child)
        child.parents.append(self)

    def set_spouse(self, spouse):
        """Adds a spouse to the node."""

        self.spouse = spouse
        spouse.spouse = self

    def to_dict(self):
        """Converts node information to a dictonary for storing in a .json file."""

        return {
            "name": self.name,
            "gender": self.gender,
            "birthdate": self.birthdate,
            "parents": [parent.name for parent in self.parents],
            "children": [child.name for child in self.children],
            "spouse": self.spouse.name if self.spouse else None
        }

    def get_all_related(self):
        related_members = []

        def collect_related(node):
            if node not in related_members:
                if node != self:
                    related_members.append(node)

                if self.parents:
                    for parent in self.parents:
                        collect_related(parent)

                if self.children:
                    for child in self.children:
                        collect_related(child)

                if self.spouse:
                    collect_related(self.spouse)

        collect_related(self)

        return related_members