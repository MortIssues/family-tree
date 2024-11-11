from tree import Tree

def main():
    root = Tree().load_json("family_tree.json")
    parent = root.find_node_by_name("child2b")
    parent.add_child("child2b2")
    root.save_json("family_tree.json")
    root.display_tree()

if __name__ == "__main__":
    main()