import random
import pygame
import math


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

        self.x = random.randint(32, 512-32)
        self.y = random.randint(32, 512-32)

    def add_parent(self, parent):
        """Adds a parent to the node."""

        self.parents.append(parent)
        parent.children.append(self)

    def add_child(self, child):
        """Adds a child to the node."""

        self.children.append(child)
        child.parents.append(self)

    def add_spouse(self, spouse):
        """Adds a spouse to the node."""

        self.spouses.append(spouse)
        spouse.spouses.append(self)

    def add_prev_spouse(self, prev_spouse):
        """Moves spouse to previous spouses."""

        self.previous_spouses.append(prev_spouse)
        prev_spouse.previous_spouses.append(self)

    def add_sibling(self, sibling):
        """Adds a sibling to the node."""

        self.siblings.append(sibling)
        sibling.siblings.append(self)

    def to_dict(self):
        """Converts node information to a dictonary for storing in a .json file."""

        return {
            "name": self.name,
            "gender": self.gender,
            "birthdate": self.birthdate,
            "parents": [parent.name for parent in self.parents],
            "children": [child.name for child in self.children],
            "spouses": [spouse.name for spouse in self.spouses],
            "previous_spouses": [prev_spouse.name for prev_spouse in self.previous_spouses],
            "siblings": [sibling.name for sibling in self.siblings],
        }

    def draw(self, surface):
        """Draws node to window."""

        font = pygame.font.SysFont('Arial', 10)
        text_surface = font.render(self.name, True, (59, 53, 113))  # White text
        text_rect = text_surface.get_rect(center=(self.x, self.y+14))

        pygame.draw.circle(surface, (59, 53, 113), (self.x, self.y), 6)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        """
        Function to check if the node has been clicked.

        Args:
            mouse_pos (tuple): The current mouse position.

        Returns:
            bool: True if the node is clicked or False if it isn't.
        """

        # Check if the mouse is clicking on this node.
        distance = math.hypot(mouse_pos[0] - self.x, mouse_pos[1] - self.y)
        return distance <= 30