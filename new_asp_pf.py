"""
Path finder for adverserial shortest path
"""
import socket
import sys
import networkx as nx
import copy

computation_limit = 8 ** 8

def get_best_next_node(candidate, weights, memo):

    c_hash = ''
    for i in range(len(candidate)):
        c_hash += str(candidate[i]) + '-' + str(weights[i]) + ','

    if c_hash in memo:
        return memo[c_hash]

    if len(candidate) <= 2:
        return weights[1]

    # Get next node
    next = candidate[1]

    min_value = 1e10

    for i in range(1, len(candidate)):

        # Clone weights
        w = copy.deepcopy(weights)

        # Double the weight from (i - 1) to i
        w[i] *= 2

        # Recurse
        value = w[1] + get_best_next_node(candidate[1:], w, memo)

        if value > min_value:
            min_value = value

    # Memoize
    memo[c_hash] = min_value

    return min_value


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

    # Don't go deeper if the candidate length is two
    if len(candidates[0]) == 2:
        return candidates[0][1]

    return get_most_unique_path([candidate[:-1] for candidate in candidates])

def get_path(graph, start, end):

    # Get all shortest paths
    paths = nx.algorithms.all_shortest_paths(graph, start, end, weight='weight')
    paths = [path for path in paths]

    # Count all possible paths
    computations = 0
    for path in paths:
        computations += len(path) ** len(path)

    if computations < computation_limit:
        print('Computations required: ', computations, ' is less than', computation_limit)
        min_cost = 1e10
        next_best = paths[0][1]
        for path in paths:
            # Construct weights
            weights = []
            weights.append(0)
            for i in range(1, len(path)):
                 weights.append(graph[path[ i - 1]][path[ i ]]['weight'])

            # Get min cost of this path
            cost = get_best_next_node([node for node in path], weights, {})
            if cost < min_cost:
                min_cost = cost
                next_best = path[1]
        
        return next_best
    else:
        return get_most_unique_path([path for path in paths])[1]

HOST = 'localhost'
PORT = 5000

if len(sys.argv) > 1:
    PORT = int(sys.argv[1])

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

recv_data = ''
data = ''

while '#' not in recv_data:
    recv_data = sock.recv(1024)
    data += recv_data

lines = data.split('\n')

# lines = [line.rstrip('\n') for line in open('advshort.txt')]

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

# Communicate via socket
recv_data = ''
player_pos = start

while '$' not in recv_data:

    # Send our move
    move = get_path(graph, player_pos, end)

    print("Moving from", player_pos, "to", move)

    sock.sendall('%d\n' % (move))

    # Update our position
    player_pos = move

    recv_data = sock.recv(65536)
    if '$' in recv_data:
        break

    # Read edge doubled by the adversary
    n1, n2, weight = [int(x) for x in recv_data.split(' ')]

    print("Adversary has set edge (", n1, "->", n2, ") as", weight)

    if n1 == -1 or n2 == -1:
        print("Ignoring adversary's move")
    else:
        # Update graph
        graph[n1][n2]['weight'] = weight
        graph[n2][n1]['weight'] = weight
