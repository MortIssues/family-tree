import argparse
import cmd2
from cmd2 import with_argparser

from graph import Graph


class CommandInterface(cmd2.Cmd):
    intro = "CLI for the family tree system. Use 'help' or 'help <command>'."
    prompt = "TREE> "

    def __init__(self):
        super().__init__()
        self.graph = None
        self.selected_node = None

    create_parser = argparse.ArgumentParser(prog="add")
    create_subparsers = create_parser.add_subparsers(dest="subcommand")

    create_graph_parser = create_subparsers.add_parser('graph',
                                                       help="Create a new graph.")

    create_node_parser = create_subparsers.add_parser('node',
                                                      help="Create a new node.")
    create_node_parser.add_argument("name", type=str,
                                    help="The name of the node to be created.")
    create_node_parser.add_argument("gender", action='store_true',
                                    help="The gender of the node's identity.")
    create_node_parser.add_argument("birthdate", action='store_true',
                                    help="The birthdate of the node's identity.")

    create_relation_parser = create_subparsers.add_parser('relation',
                                                          help="Create a new relationship relative to the current selected node.")
    create_relation_parser.add_argument("relation_type", type=str,
                                        help="The relation type: Parent, child, sibling, spouse.")
    create_relation_parser.add_argument("node", type=str,
                                        help="The relation's identity.")

    @with_argparser(create_parser)
    def do_create(self, args):
        if args.subcommand == "graph":
            self.graph = Graph()
            print("New graph created.")

        elif args.subcommand == "node":
            self.graph.add_node(args.name, args.gender if args.gender else None, args.birthdate if args.birthdate else None)
            print("New node created.")

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

    divorce_parser = argparse.ArgumentParser(prog="divorce")
    divorce_parser.add_argument("node", type=str,
                             help="The name of the node currently a spouse of the selected node, to be divorced.")

    @with_argparser(divorce_parser)
    def do_divorce(self, args):
        self.selected_node.divorce_spouse(self.graph.get_node(args.node))

    load_parser = argparse.ArgumentParser(prog="load")
    load_parser.add_argument("filename", type=str,
                             help="The name of the file you wish to load a node graph from.")

    @with_argparser(load_parser)
    def do_load(self, args):
        self.graph = Graph().load_from_json(args.filename)
        print(f"Graph loaded from {args.filename}.")

    save_parser = argparse.ArgumentParser(prog="save")
    save_parser.add_argument("filename", type=str,
                             help="The name of the file you wish to save the current node graph as.")

    @with_argparser(save_parser)
    def do_save(self, args):
        self.graph.save_to_json(args.filename)
        print(f"Graph saved to {args.filename}.")

    select_parser = argparse.ArgumentParser(prog="select")
    select_parser.add_argument("name", type=str,
                             help="The name of the node you wish to select.")

    @with_argparser(select_parser)
    def do_select(self, args):
        self.selected_node = self.graph.get_node(args.name)
        print(f"{args.name} is now the selected node.")

    def do_remove(self, args):
        self.graph.remove_node(self.selected_node)
        print(f"{args.name} has been removed.")

    def do_info(self, args):
        print(self.selected_node.to_dict())