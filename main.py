import sys
import random
import pycosat
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors

"""
This program solves graph coloring by reducing to SAT problem. Formulas represent the goal and constraints with
atoms representing pairs (<node>, <color>).
"""


def literal(atom_id, negation=0):
    return int(("-" if negation else "") + str(atom_id))


def main():
    G = nx.Graph()
    cnf = []

    # input ( number of colors followed by pairs representing graph edges )
    colors_number = int(input())
    for line in sys.stdin:
        A, B = line.split()
        G.add_edge(A, B)

    # assign ids to atoms( atoms are represented as pairs (<node>, <color>) )
    atom_id = {}
    atom_id_inv = {}
    free_id = 1
    for node in G.nodes():
        for color in range(colors_number):
            atom_id[(node, color)] = free_id
            atom_id_inv[free_id] = (node, color)
            free_id += 1

    # add the goal clauses ( every node must be colored with exactly one color )
    for node in G.nodes():
        # at least one color for a node ( one clause of #colors literals )
        clause = []
        for color in range(colors_number):
            clause.append(literal(atom_id[(node, color)]))
        cnf.append(clause)

        # max one color for a node ( #node * (#colors * (#colors - 1) / 2) clauses of 2 literals )
        for color1 in range(colors_number):
            for color2 in range(color1 + 1, colors_number):
                cnf.append([literal(atom_id[node, color1], negation=1),
                            literal(atom_id[node, color2], negation=1)])

    # add the restriction clauses ( no two adjacent nodes can be colored with the same color )
    # ( #edges * #colors clauses of two literals )
    for edge in G.edges():
        for color in range(colors_number):
            cnf.append([literal(atom_id[edge[0], color], negation=1),
                        literal(atom_id[edge[1], color], negation=1)])

    # solve the instance of SAT problem
    solution = pycosat.solve(cnf)
    if solution == "UNSAT":
        print("A coloring does not exist.")
        return

    # show the solution and colored graph
    pos = nx.spring_layout(G)
    color_mapping = {}

    for value in solution:
        if value > 0:
            node, color_id = atom_id_inv[value]

            # assign some color from matplotlib colors preset
            if color_id not in color_mapping.keys():
                new_color = random.choice(list(mcolors.cnames.keys()))
                while new_color in color_mapping.values():
                    new_color = random.choice(list(mcolors.cnames.keys()))
                color_mapping[color_id] = new_color
            color = color_mapping[color_id]

            nx.draw_networkx_nodes(G, pos, nodelist=[node],
                                   node_color=color, node_size=500, alpha=0.8)
            print(node + " -> " + color)

    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edge_color='black')
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    main()
