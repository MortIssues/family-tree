"""Helper functions for the command_interface class."""

from datetime import datetime

# Check for a graph.
def requires_graph(func):
    def wrapper(self, *args, **kwargs):
        if not self.graph:
            print("This command requires a graph. Either load one with the 'load' command or make one with the 'create graph' command.")
            return
        return func(self, *args, **kwargs)
    return wrapper


#Check for a selected node.
def requires_selected_node(func):
    def wrapper(self, *args, **kwargs):
        if not self.selected_node:
            print("This command requires a node to be selected. Please use the 'select' command.")
            return
        return func(self, *args, **kwargs)
    return wrapper


# Set the parent relationships.
def set_relation_parents(graph, node, args):
    parent1 = graph.get_node(args.nodes[0])
    parent2 = graph.get_node(args.nodes[1])
    node.add_parents(parent1, parent2)
    print(f"{args.nodes[0]} and {args.nodes[1]} are now parents of {node}.")


# Set node attribute to value.
def set_info(node, args):
    attribute = args.attribute.lower()
    value = args.value

    # Check if the node has the attrivute and if so update it to the specified value.
    if hasattr(node, attribute):
        setattr(node, attribute, value)
        print(f"Updated {node.name} {attribute} to {value}.")
    else:
        print(f"Invalid attribute: {attribute}.")


# Find cousins for the 'info' command.
def info_cousins(node):
    cousins = []

    # Loop through parents of the selected node.
    for parent in node.parents:
        # If statements here were reversed to prevent excessive indentation.
        if not parent.parents:
            continue

        # Loop through grandparents of selected node
        for grandparent in parent.parents:
            if not grandparent.children:
                continue

            # Loop through aunts/uncles (A.K.A. Piblings - Yes it is a word.)
            for pibling in grandparent.children:
                # Ignore the pibling if they're actually a parent of a selected node.
                if pibling == parent:
                    continue

                # If not loop through their children and append them.
                for child in pibling.children:
                    if child.name not in cousins:
                        cousins.append(child.name)

    print(f"The cousins of {node} are: {cousins}")


# Find and sort birthdays for the 'info birthdays --sorted' command.
def info_birthdays_sorted(graph):
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    birthdays = {}

    # Go through nodes and append their names and birthdays to a dictionary.
    # Dictionary makes merging later easier.
    for node in graph.nodes.values():
        if node.birthdate:
            day, month, year = node.birthdate.split('-')
            key = f"{day}-{month}"

            # If the date isn't already in the dictionary add it.
            if key not in birthdays:
                birthdays[key] = []

            # Regardless, add the person's name, this'll either add it to someone with the existing birthday or
            # just add themselves if they're the only one with that birthday.
            birthdays[key].append(node.name)

    # Sort the birthdays by their birthday, formatted into something more sortable.
    sorted_birthdays = sorted(birthdays.items(), key=lambda x: int(x[0].split('-')[1]) * 31 + int(x[0].split('-')[0]))

    # Output the result with some extra formatting to make it a bit more human-readable.
    for date, names in sorted_birthdays:
        f_day = date.split("-")[0]
        f_day += "st" if f_day[-1] == "1" else "nd" if f_day[-1] == "2" else "rd" if f_day[-1] == "3" else "th"
        f_month = months[int(date.split("-")[1]) - 1]
        print(f"{' and '.join(names)}: {f_day} {f_month}")


# Find birthdays and output them unsorted for the 'info birthdays' command.
def info_birthdays_unsorted(graph):
    birthdays = []

    # Go through nodes and add a tuple containing the name and their birthday then output it.
    for node in graph.nodes.values():
        if node.birthdate:
            birthdays.append((node.name, node.birthdate))

    for birthday in birthdays:
        print(f"{birthday[0]}: {birthday[1]}")

def info_average_children(graph, total_people):
    total_children = 0

    # Loop through nodes adding the length of their children array to the total_children.
    for node in graph.nodes.values():
        total_children += len(node.children)

    # Divide total children by the number of nodes for the average and output.
    average_children = total_children / total_people
    print(f"Average number of children per person: {average_children}")

def info_average_age(graph, total_people):
    total_age = 0
    # Loop through nodes.
    for node in graph.nodes.values():
        if node.birthdate:
            # Datetime can be used to convert their birthdate as a string to a datetime object with which
            # arithmatic can be done more easily.
            day, month, year = map(int, node.birthdate.split('-'))
            birthdate = datetime(year, month, day)
            age = (datetime.now() - birthdate).days // 365
            total_age += age

    # Calculate the average and output.
    average_age = total_age / total_people
    print(f"Average age: {average_age}")