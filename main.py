from tree import Tree

def main():
    family_tree = Tree()
    family_tree.load_json("family_tree.json")
    family_tree.display_tree()

if __name__ == "__main__":
    main()