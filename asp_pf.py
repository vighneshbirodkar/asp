"""
Path finder for adverserial shortest path
"""

import networkx as nx

def get_most_unique_path(paths):

    if len(paths) == 1:
        return paths[0]

    picked_path = None
    penultimates = {}
    path_penultimate_map = {}

    # Strategy: Pick the least common entry spot into the destination
    for path in paths:

        penultimate = path[-2]

        if penultimate not in path_penultimate_map:
            path_penultimate_map[penultimate] = []

        if penultimate not in penultimates:
            penultimates[penultimate] = 0

        penultimates[penultimate] += 1
        path_penultimate_map[penultimate].append(path)

    # Identify least commonly occuring penultimate node
    penultimate = None
    least_common = 1e10
    for key, value in penultimates.iteritems():
        if value < least_common:
            least_common = value
            penultimate = key

    candidates = path_penultimate_map[penultimate]

    return get_most_unique_path([candidate[:-1] for candidate in candidates])

def get_path(graph, start, end):

    # Get all shortest paths
    paths = nx.algorithms.all_shortest_paths(graph, start, end, weight='weight')
    return get_most_unique_path([path for path in paths])[1]

lines = [line.rstrip('\n') for line in open('advshort.txt')]

# Lines 0, 1, 2 are are not edges
start = int(lines[0].split(':')[1])
end = int(lines[1].split(':')[1])

# Process edges starting from line index 3
edges = lines[3:]
edges = [e for e in edges if len(e) > 1]
edges = [tuple(map(int, e.split(' ')) + [1]) for e in edges]

# Build graph
graph = nx.Graph()
graph.add_node(10000)
graph.add_weighted_edges_from(edges)

print get_path(graph, start, end)
