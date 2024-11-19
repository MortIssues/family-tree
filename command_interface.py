import cmd2
import argparse
from cmd2 import with_argparser
from graph import Graph


class CommandInterface(cmd2.Cmd):
    intro = "CLI for the family tree system. Use 'help' or 'help <command>'."
    prompt = "GRAPH> "

    def __init__(self):
        super().__init__()
        self.graph = None
        self.selected_node = None


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

        self.selected_node = self.graph.get_node(args.name)
        print(f"{args.name} is now the selected node.")


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

    @with_argparser(create_parser)
    def do_create(self, args):
        """
        Create a new object based on the given subcommand.
        Usage: create <subcommand>
        Subcommands:
            graph
            node <name> Optionally: --gender <gender> --birthdate <birthdate>
        Warnings: Creating a new graph will discard the one currently being worked on.
        """

        # Create a new blank graph.
        if args.subcommand == "graph":
            self.graph = Graph()
            print("New graph created.")

        # Create a new node.
        elif args.subcommand == "node":
            self.selected_node = self.graph.add_node(args.name,
                                                     args.gender if args.gender else None,
                                                     args.birthdate if args.birthdate else None)
            print(f"New node {args.name} created.")


    # Set up the set parser
    set_parser = argparse.ArgumentParser(prog="set")
    set_subparsers = set_parser.add_subparsers(dest="subcommand")

    # Subcommand - relation
    set_relation_parser = set_subparsers.add_parser('relation',
                                                    help="Create a new relationship relative to the current selected node.")
    set_relation_parser.add_argument("relation_type", type=str, choices=['child', 'spouse', 'parents'],
                                     help="The relation type: parent, child, spouse, parents.")
    set_relation_parser.add_argument("nodes", type=str, nargs='+',
                                     help="The relation's identity. For 'parents', specify two nodes.")

    #Subcommand - info
    set_info_subcommand = set_subparsers.add_parser("info", help="Set an attribute of the selected node.")
    set_info_subcommand.add_argument("attribute", type=str, help="Attribute to modify.")
    set_info_subcommand.add_argument("value", type=str, help="New value for the attribute.")

    def do_set(self, args):
        if args.subcommand == "relation":
            if args.relation_type == 'parents':
                parent1 = self.graph.get_node(args.nodes[0])
                parent2 = self.graph.get_node(args.nodes[1])
                self.selected_node.add_parents(parent1, parent2)
                print(f"{args.nodes[0]} and {args.nodes[1]} are now parents of {self.selected_node}.")
            else:
                target_node = self.graph.get_node(args.nodes[0])

            if args.relation_type == 'child':
                self.selected_node.add_child(target_node)
                print(f"{args.node} is now a child of {self.selected_node}.")
            elif args.relation_type == 'spouse':
                self.selected_node.spouse = target_node
                print(f"{args.node} is now a spouse of {self.selected_node}.")

        elif args.subcommand == "info":
            attribute = args.attribute.lower()
            value = args.value

            if hasattr(self.selected_node, attribute):
                setattr(self.selected_node, attribute, value)
                print(f"Updated {self.selected_node.name} {attribute} to {value}.")
            else:
                print(f"Invalid attribute: {attribute}.")


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

        self.graph.save_to_json(args.filename)


    info_parser = argparse.ArgumentParser(prog="info")
    info_subparser = info_parser.add_subparsers(dest="subcommand",
                                                help="Subcommands for info.")

    # Subcommand - All
    info_all_subcommand = info_subparser.add_parser("all",
                                                    help="Retrieve all information about the selected node.")

    # Subcommand - Relation and its relation_type argument and optional modifiers flag.
    info_relation_subcommand = info_subparser.add_parser("relation",
                                                         help="Find a relation relative to the selected node.")
    info_relation_subcommand.add_argument("relation_type", type=str,
                                          help="Type of relation.")

    # Subcommand - Birthdays and its optional sorted flag.
    info_birthdays_subcommand = info_subparser.add_parser("birthdays",
                                                    help="Retrieve all birthdays organised by date order.")
    info_birthdays_subcommand.add_argument("--sorted", action="store_true",
                                    help="Optionally, show birthdays sorted and merged.")

    @with_argparser(info_parser)
    def do_info(self, args):
        """
        Retrieve or modify information about the selected node.
        Usage: info <subcommand>
        Subcommands:
            relation <relation_type> --<modifiers>
            all
        """

        attribute_list = ["children", "spouse", "parents"]

        if args.subcommand == "relation" or args.subcommand == "all":
            relation_type = args.relation_type.lower()

            if relation_type in attribute_list:
                relatives = getattr(self.selected_node, relation_type)
                print(f"The {relation_type} of {self.selected_node.name} are: {[node.name for node in relatives]}")

            elif args.subcommand == "all":
                for attribute in attribute_list:
                    relatives = getattr(self.selected_node, attribute)
                    print(f"The {attribute} of {self.selected_node.name} are: {[node.name for node in relatives]}")

            elif relation_type == "siblings" or args.subcommand == "all":
                siblings = []
                for parent in self.selected_node.parents:
                    siblings.extend(parent.children)
                print(f"The {relation_type} of {self.selected_node.name} are: {siblings}")

            elif relation_type == "cousins" or args.subcommand == "all":
                cousins = []
                for parent in self.selected_node.parents:
                    if not parent.parents:
                        continue
                    for grandparent in parent.parents:
                        if not grandparent.children:
                            continue
                        for pibling in grandparent.children:
                            if pibling == parent:
                                continue
                            for child in pibling.children:
                                if child.name not in cousins:
                                    cousins.append(child.name)

        elif args.subcommand == "birthdays" and args.sorted:
            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            birthdays = {}

            for node in self.graph.nodes.values():
                if node.birthdate:
                    day, month, year = node.birthdate.split('-')
                    key = f"{day}-{month}"

                    if key not in birthdays:
                        birthdays[key] = []

                    birthdays[key].append(node.name)

            sorted_birthdays = sorted(birthdays.items(), key=lambda x: int(x[0].split('-')[1]) * 31 + int(x[0].split('-')[0]))
            for date, names in sorted_birthdays:
                f_day = date.split("-")[0]
                f_day += "st" if f_day[-1] == "1" else "nd" if f_day[-1] == "2" else "rd" if f_day[-1] == "3" else "th"
                f_month = months[int(date.split("-")[1]) - 1]
                print(f"{' and '.join(names)}: {f_day} {f_month}")

        elif args.subcommand == "birthdays":
            birthdays = []

            for node in self.graph.nodes.values():
                if node.birthdate:
                    birthdays.append([node.name, node.birthdate])

            for birthday in birthdays:
                print(f"{birthday[0]}: {birthday[1]}")