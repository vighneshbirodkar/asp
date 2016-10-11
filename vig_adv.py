import socket
import sys
import networkx as nx
from termcolor import cprint
import numpy as np

np.set_printoptions(precision=2)


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

start = int(lines[0].split()[-1])
end = int(lines[1].split()[-1])

cprint('Start = %d' % start, 'cyan')
cprint('End = %d' % end, 'cyan')

edges = lines[3:]
edges = [e for e in edges if len(e) > 1]
edges = [tuple(map(int, e.split(' ')) + [1]) for e in edges]
graph = nx.Graph()
graph.add_node(10000)

graph.add_weighted_edges_from(edges)
cprint('Graph Nodes = %d' % graph.number_of_nodes(), 'cyan')
cprint('Graph Edges = %d' % graph.number_of_edges(), 'cyan')

recv_data = ''
player_pos = start

while '$' not in recv_data:
    recv_data = sock.recv(1024)
    if '$' in recv_data:
        break

    player_pos = int(recv_data)
    cprint('Player Position = %d' % player_pos, 'red')

    nbrs = graph.neighbors(end)
    cprint('Neighbors of target = %r' % nbrs, 'cyan')
    nbr_weights = np.zeros(len(nbrs), dtype=np.float)

    for (i, nbr) in enumerate(nbrs):
        try:
            l = nx.algorithms.shortest_path_length(graph, player_pos, nbr,
                                                   weight='weight')
        except nx.exception.NetworkXNoPath:
            l = np.inf

        l = float(l)
        l = max(l, 0.001)
        nbr_weights[i] = 1.0/l

    nbr_weights = nbr_weights/nbr_weights.sum()
    chosen_nbr = np.random.choice(nbrs, p=nbr_weights)
    cprint('Neighbour Weights = %s' % str(nbr_weights), 'cyan')
    cprint('Chosen Neighbour = %d' % chosen_nbr, 'green')
    cprint('Doubling Edge (%d %d)' % (chosen_nbr, end), 'green')

    sock.sendall('%d %d\n' % (chosen_nbr, end))

sock.close()
