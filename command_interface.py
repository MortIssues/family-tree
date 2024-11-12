import argparse
import cmd2
from cmd2 import with_argparser

from tree import Tree


class CommandInterface(cmd2.Cmd):
    intro = "CLI for the family tree system. Use 'help' or 'help <command>'."
    prompt = "TREE> "

    def __init__(self):
        super().__init__()
        self.tree = None

    create_parser = argparse.ArgumentParser(prog="create")
    create_subparsers = create_parser.add_subparsers(dest="subcommand")

    tree_parser = create_subparsers.add_parser('tree', help="Create a new tree.")
    tree_parser.add_argument("name", type=str, help="The name of the root node of the tree.")

    create_child_parser = create_subparsers.add_parser('child', help="Create a new child node.")
    create_child_parser.add_argument("name", type=str, help="The name of the child node to be created.")
    create_child_parser.add_argument("parent", type=str, help="The name of the parent node.")

    @with_argparser(create_parser)
    def do_create(self, args):
        """
        Creates a new object based on subcommand.
        Usage: create <subcommand>
        Subcommands:
            - Tree <name>
            - Child <name> <parent>
        Caution: Creating a new tree will result in the current one being discarded.
        """

        if args.subcommand == "tree":
            self.tree = Tree(name=args.name)
        elif args.subcommand == "child":
            parent = self.tree.find_node_by_name(args.parent)
            if not parent:
                print(f"Error Occurred - No node found called {parent}")
                return
            parent.add_child(args.name)

    remove_parser = argparse.ArgumentParser(prog="remove")
    remove_subparsers = remove_parser.add_subparsers(dest="subcommand")

    remove_child_parser = remove_subparsers.add_parser('child', help="Remove a child node.")
    remove_child_parser.add_argument("name", type=str, help="The name of the child node to be removed.")

    @with_argparser(remove_parser)
    def do_remove(self, args):
        """
        Removes a child node from a node in the tree.
        Usage: remove child <name>
        Caution: Children of the removed child node will also be removed.
        """

        if args.subcommand == "child":
            if self.tree.name == args.name:
                self.tree = None
            else:
                self.tree.remove_node_by_name(args.name)


    def do_display(self, args):
        """
        Displays the current tree structure.
        """

        self.tree.display_tree()

    def do_save(self, args):
        """
        Saves a tree to a .json file.
        Usage: save tree <filename>
        """

        self.tree.save_json(args)

    def do_load(self, args):
        """
        Loads a tree from a .json file.
        Usage: load <filename.json>
        Caution: Loading a new tree will result in the current one being discarded.
        """

        self.tree = Tree()
        self.tree = Tree.load_json(args)