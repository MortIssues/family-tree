class Node:
    def __init__(self, name, gender=None, birthdate=None):
        self.name = name
        self.gender = gender
        self.birthdate = birthdate
        self.parents = []
        self.children = []
        self.spouses = []
        self.previous_spouses = []
        self.siblings = []

    def add_parent(self, parent):
        self.parents.append(parent)
        parent.children.append(self)

    def add_child(self, child):
        self.children.append(child)
        child.parents.append(self)

    def add_spouse(self, spouse):
        self.spouses.append(spouse)
        spouse.spouses.append(self)

    def divorce_spouse(self, spouse):
        if spouse in self.spouses:
            self.spouses.remove(spouse)
            self.previous_spouses.append(spouse)
            spouse.spouses.remove(self)
            spouse.previous_spouses.append(self)

    def add_sibling(self, sibling):
        self.siblings.append(sibling)
        sibling.siblings.append(self)

    def to_dict(self):
        return {
            "name": self.name,
            "gender": self.gender,
            "birthdate": self.birthdate,
            "parents": [parent.name for parent in self.parents],
            "children": [child.name for child in self.children],
            "spouses": [spouse.name for spouse in self.spouses],
            "previous_spouses": [spouse.name for spouse in self.previous_spouses],
            "siblings": [sibling.name for sibling in self.siblings],
        }
