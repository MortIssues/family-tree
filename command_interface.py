import argparse
import cmd2
from cmd2 import with_argparser
import sys
from graph import Graph


class CommandInterface(cmd2.Cmd):
    intro = "CLI for the family tree system. Use 'help' or 'help <command>'."
    prompt = "TREE> "

    def __init__(self, lock):
        super().__init__()
        self.graph = None
        self.selected_node = None
        self.lock = lock

    def do_quit(self, args = 0):
        """Exits the program."""

        sys.exit(args)

    # Set up the create parser.
    create_parser = argparse.ArgumentParser(prog="add")
    create_subparsers = create_parser.add_subparsers(dest="subcommand")

    # Subcommand - Graph
    create_graph_parser = create_subparsers.add_parser('graph',
                                                       help="Create a new graph.")

    # Subcommand - Node and its arguments: name, --gender, --birthdate
    create_node_parser = create_subparsers.add_parser('node',
                                                      help="Create a new node.")
    create_node_parser.add_argument("name", type=str,
                                    help="The name of the node to be created.")
    create_node_parser.add_argument("--gender", type=str,
                                    help="Optionally, the gender of the node's identity.")
    create_node_parser.add_argument("--birthdate", type=str,
                                    help="Optionally, the birthdate of the node's identity.")

    # Subcommand - Relation and its arguments: relation_type, node
    create_relation_parser = create_subparsers.add_parser('relation',
                                                          help="Create a new relationship relative to the current selected node.")
    create_relation_parser.add_argument("relation_type", type=str,
                                        help="The relation type: Parent, child, sibling, spouse.")
    create_relation_parser.add_argument("node", type=str,
                                        help="The relation's identity.")

    @with_argparser(create_parser)
    def do_create(self, args):
        """
        Create a new object based on the given subcommand.
        Usage: create <subcommand>
        Subcommands:
            graph
            node <name>
                Optionally: --gender <gender> --birthdate <birthdate>
            relation <relation_type> <node>
        Warnings: Creating a new graph will discard the one currently being worked on.
        """

        with self.lock:
            # Create a new blank graph.
            if args.subcommand == "graph":
                self.graph = Graph()
                print("New graph created.")

            # Create a new node.
            elif args.subcommand == "node":
                print(args.gender, args.birthdate)
                self.selected_node = self.graph.add_node(args.name,
                                                         args.gender if args.gender else None,
                                                         args.birthdate if args.birthdate else None)
                print("New node created.")

            # Establish a specified relationship between the selected node and a specified node.
            elif args.subcommand == "relation":
                target_node = self.graph.get_node(args.node)
                if args.relation_type == 'parent':
                    self.selected_node.add_parent(target_node)
                    print(f"{args.node} is now a parent of {self.selected_node}.")
                elif args.relation_type == 'child':
                    self.selected_node.add_child(target_node)
                    print(f"{args.node} is now a child of {self.selected_node}.")
                elif args.relation_type == 'sibling':
                    self.selected_node.add_sibling(target_node)
                    print(f"{args.node} is now a sibling of {self.selected_node}.")
                elif args.relation_type == 'spouse':
                    self.selected_node.add_spouse(target_node)
                    print(f"{args.node} is now a spouse of {self.selected_node}.")

    # Set up the divorce parser and its node argument.
    # This could be achieved without the argparser but I felt it was beneficial for the sake of consistency and also clarity when it comes to the help command.
    divorce_parser = argparse.ArgumentParser(prog="divorce")
    divorce_parser.add_argument("node", type=str,
                             help="The name of the node currently a spouse of the selected node, to be divorced.")

    @with_argparser(divorce_parser)
    def do_divorce(self, args):
        """
        Divorces a node from the current selected node.
        Usage: divorce <node>
        Warnings: The node to be divorced must be in the spouse of the selected node.
        """

        with self.lock:
            self.selected_node.divorce_spouse(self.graph.get_node(args.node))

    # Set up the load parser and its filename argument.
    load_parser = argparse.ArgumentParser(prog="load")
    load_parser.add_argument("filename", type=str,
                             help="The name of the file you wish to load a node graph from.")

    @with_argparser(load_parser)
    def do_load(self, args):
        """
        Loads a graph from the given file.
        Usage: load <filename>
        Warnings:
            The file must be valid and must be of type JSON.
            Loading a new graph will discard the one currently being worked on.
        """

        with self.lock:
            self.graph = Graph().load_from_json(args.filename)

    # Set up the save parser and its filename argument.
    save_parser = argparse.ArgumentParser(prog="save")
    save_parser.add_argument("filename", type=str,
                             help="The name of the file you wish to save the current node graph as.")

    @with_argparser(save_parser)
    def do_save(self, args):
        """
        Saves a graph to the given file.
        Usage: save <filename>
        Warnings: filename must be of type JSON.
        """

        with self.lock:
            self.graph.save_to_json(args.filename)

    # Set up the select parser and its name argument.
    select_parser = argparse.ArgumentParser(prog="select")
    select_parser.add_argument("name", type=str,
                             help="The name of the node you wish to select.")

    @with_argparser(select_parser)
    def do_select(self, args):
        """
        Selects a node.
        Usage: select <name>
        """

        with self.lock:
            self.selected_node = self.graph.get_node(args.name)
            print(f"{args.name} is now the selected node.")

    def do_remove(self, args):
        """
        Removes a node.
        Usage: remove <name>
        Warnings: This cannot be undone.
        """

        with self.lock:
            self.graph.remove_node(self.selected_node)
            print(f"{args.name} has been removed.")

    def do_info(self, args):
        """
        Outputs information about the selected node.
        Usage: info
        Notes: this still needs some work as I would like to be able to retrieve certain data from a node including
        relations. For example typing in 'info uncle' should return the selected nodes uncle. I would like to try
        implement a modular way of doing this so the term 'great' can be stacked to shift layers. For example 'great
        great grandmother' should return a list of the selected nodes great great grandmothers.
        """

        print(self.selected_node.to_dict())