import argparse
import cmd2
from cmd2 import with_argparser
import sys
from r_graph import Graph


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
    create_parser = argparse.ArgumentParser(prog="create")
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
            if args.node in self.selected_node.spouses:
                self.selected_node.spouses.remove(args.node)
                self.selected_node.previous_spouses.add(args.node)
                args.node.spouses.remove(self.selected_node)
                args.node.previous_spouses.add(self.selected_node)
            else:
                self.selected_node.add_prev_spouse(self.graph.get_node(args.node))


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
            print(self.graph.nodes)

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

    info_parser = argparse.ArgumentParser(prog="info")
    info_subparser = info_parser.add_subparsers(dest="subcommand",
                                                help="Subcommands for info.")

    # Subcommand - All
    info_all_subcommand = info_subparser.add_parser("all", help="Retrieve all information about the selected node.")

    # Subcommand - Relation and its relation_type argument and optional modifiers flag.
    info_relation_subcommand = info_subparser.add_parser("relation",
                                                         help="Find a relation relative to the selected node.")
    info_relation_subcommand.add_argument("relation_type", type=str,
                                          help="Type of relation (e.g., parents, siblings, cousins).")
    info_relation_subcommand.add_argument("--modifiers", nargs="*", default=[],
                                          help="Optional modifiers.")

    # Subcommand - Set and its arguments: Attribute and value
    info_set_subcommand = info_subparser.add_parser("set", help="Set an attribute of the selected node.")
    info_set_subcommand.add_argument("attribute", type=str, help="Attribute to modify (e.g., name, gender, birthdate).")
    info_set_subcommand.add_argument("value", type=str, help="New value for the attribute.")

    @with_argparser(info_parser)
    def do_info(self, args):
        """
        Retrieve or modify information about the selected node.
        Usage: info <subcommand>
        Subcommands:
            relation <relation_type> --<modifiers>
            set <attribute> <value>
            all
        """

        with self.lock:
            attribute_list = ["parents", "children", "siblings", "spouses", "previous_spouses"]

            if args.subcommand == "all":
                for relation in attribute_list:
                    relatives = getattr(self.selected_node, relation)
                    print(f"The {relation} of {self.selected_node} are: {[node.name for node in relatives]}")

            elif args.subcommand == "relation":

                relation_type = args.relation_type.lower()
                modifiers = args.modifiers
                generations = sum(1 for mod in modifiers if mod == "great")

                if relation_type in attribute_list:
                    relatives = getattr(self.selected_node, relation_type)
                    print(f"The {relation_type} of {self.selected_node.name} are: {[node.name for node in relatives]}")

                elif relation_type in ["grandparents", "grandchildren"] and generations > 0:
                    current_generation = self.selected_node.parents if relation_type == "grandparents" else self.selected_node.children
                    for _ in range(generations - 1):
                        next_generation = []
                        for node in current_generation:
                            if relation_type == "grandparents":
                                next_generation.extend(node.parents)
                            elif relation_type == "grandchildren":
                                next_generation.extend(node.children)
                        current_generation = next_generation

                    print(
                        f"{'Great ' * generations}{relation_type.capitalize()} of {self.selected_node.name}: {[n.name for n in current_generation]}")

                elif relation_type == "grandparents" or args.subcommand == "all":
                    grandparents = []
                    for parent in self.selected_node.parents:
                        grandparents.extend(parent.parents)
                    print(f"The grandparents of {self.selected_node.name} are: {[gp.name for gp in grandparents]}")

                elif relation_type == "cousins" or args.subcommand == "all":
                    cousins = []
                    for parent in self.selected_node.parents:
                        for sibling in parent.siblings:
                            cousins.extend(sibling.children)
                    print(f"The cousins of {self.selected_node.name} are: {[c.name for c in cousins]}")

                else:
                    print(f"Unknown or unsupported relation type: {relation_type}.")

            elif args.subcommand == "set":
                attribute = args.attribute.lower()
                value = args.value

                if hasattr(self.selected_node, attribute):
                    setattr(self.selected_node, attribute, value)
                    print(f"Updated {self.selected_node.name} {attribute} to {value}.")
                else:
                    print(f"Invalid attribute: {attribute}.")