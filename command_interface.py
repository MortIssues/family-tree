import cmd2
import argparse
from cmd2 import with_argparser
from graph import Graph
import ci_helper_functions as ci

class CommandInterface(cmd2.Cmd):
    intro = "CLI for the family tree system. Use 'help' or 'help <command>'."
    prompt = "GRAPH> "

    def __init__(self):
        super().__init__()
        self.graph = None
        self.selected_node = None

    select_parser = argparse.ArgumentParser(prog="select")
    select_parser.add_argument("name", type=str,
                               help="The name of the node you wish to select.")

    @ci.requires_graph
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

    @ci.requires_graph
    @ci.requires_selected_node
    def do_remove(self, args):
        """
        Remove the selected node.
        Usage: remove
        Warnings: This will remove all reference to the node and cannot be undone.
        """
        self.graph.remove_node(self.selected_node)
        self.selected_node = None
        print(f"Node {self.selected_node} has been removed.")


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

    @ci.requires_graph
    @ci.requires_selected_node
    def do_set(self, args):
        # Execute relation subcommand.
        if args.subcommand == "relation":
            # Set both parents. Spouse check is done within the .add_parents() function.
            if args.relation_type == 'parents':
                ci.set_relation_parents(self.graph, self.selected_node, args)
            else:
                # If parents wasn't the option they selected then only one target node is necessary for the others.
                target_node = self.graph.get_node(args.nodes[0])

            # Set the child relation.
            if args.relation_type == 'child':
                self.selected_node.add_child(target_node)
                print(f"{args.node} is now a child of {self.selected_node}.")

            # Set the spouse relation.
            elif args.relation_type == 'spouse':
                self.selected_node.spouse = target_node
                print(f"{args.node} is now a spouse of {self.selected_node}.")

        # Info subcommand for setting information pertaining to the selected node.
        elif args.subcommand == "info":
            ci.set_info(self.selected_node, args)

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

    @ci.requires_graph
    @with_argparser(save_parser)
    def do_save(self, args):
        """
        Saves a graph to the given file.
        Usage: save <filename>
        Warnings: filename must be of type JSON.
        """

        self.graph.save_to_json(args.filename)


    # Set up the info parser and subparsers.
    info_parser = argparse.ArgumentParser(prog="info")
    info_subparser = info_parser.add_subparsers(dest="subcommand",
                                                help="Subcommands for info.")

    # Subcommand - All.
    info_all_subcommand = info_subparser.add_parser("all",
                                                    help="Retrieve all information about the selected node.")

    # Subcommand - Relation, and its relation_type argument and optional modifiers flag.
    info_relation_subcommand = info_subparser.add_parser("relation",
                                                         help="Find a relation relative to the selected node.")
    info_relation_subcommand.add_argument("relation_type", type=str,
                                          help="Type of relation.")

    # Subcommand - Birthdays, and its optional sorted flag.
    info_birthdays_subcommand = info_subparser.add_parser("birthdays",
                                                    help="Retrieve all birthdays organised by date order.")
    info_birthdays_subcommand.add_argument("--sorted", action="store_true",
                                    help="Optionally, show birthdays sorted and merged.")

    # Subcommand - Average, and its options: children or age.
    info_average_subcommand = info_subparser.add_parser("average",
                                                        help="Calculate averages for the graph.")
    info_average_subcommand.add_argument("average_type", type=str,
                                         help="Type of average to calculate: children or age.")

    @ci.requires_graph
    @ci.requires_selected_node
    @with_argparser(info_parser)
    def do_info(self, args):
        """
        Retrieve or modify information about the selected node.
        Usage: info <subcommand>
        Subcommands:
            relation <relation_type> --<modifiers>
            all
        """

        # List of possible attributes that may be accessed.
        attribute_list = ["children", "spouse", "parents"]

        # Execute relation subcommand.
        if args.subcommand == "relation" or args.subcommand == "all":
            relation_type = args.relation_type.lower()

            # If the relation type is an explicit one (i.e. in the standard list of attributes.
            if relation_type in attribute_list:
                relatives = getattr(self.selected_node, relation_type)
                print(f"The {relation_type} of {self.selected_node.name} are: {[node.name for node in relatives]}")

            # If the user wanted all info then just output everything.
            elif args.subcommand == "all":
                for attribute in attribute_list:
                    relatives = getattr(self.selected_node, attribute)
                    print(f"The {attribute} of {self.selected_node.name} are: {[node.name for node in relatives]}")

            # Less explicit relations are found here, starting with siblings.
            elif relation_type == "siblings" or args.subcommand == "all":
                siblings = []
                for parent in self.selected_node.parents:
                    siblings.extend(parent.children)
                print(f"The {relation_type} of {self.selected_node.name} are: {siblings}")

            # Cousins are found.
            elif relation_type == "cousins" or args.subcommand == "all":
                ci.info_cousins(self.selected_node)

        # Execute birthdays subcommand with the sorted option as true.
        elif args.subcommand == "birthdays" and args.sorted:
            ci.info_birthdays_sorted(self.graph)

        # Execute birthdays subcommand, no sorting.
        elif args.subcommand == "birthdays":
            ci.info_birthdays_unsorted(self.graph)

        # Execute average subcommand.
        elif args.subcommand == "average":
            average_type = args.average_type.lower()
            total_people = len(self.graph.nodes)

            # Average children option.
            if average_type == "children":
                ci.info_average_children(self.graph, total_people)

            # Average age option.
            elif average_type == "age":
                ci.info_average_age(self.graph, total_people)