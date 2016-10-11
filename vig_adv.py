import socket
import sys
import networkx as nx
import numpy as np

np.set_printoptions(precision=2)


HOST = 'localhost'
PORT = 5000


def softmax(x, w):
    x = x*w
    x = np.exp(x)
    x = x/x.sum()
    return x


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

print('Start = %d' % start)
print('End = %d' % end)

edges = lines[3:]
edges = [e for e in edges if len(e) > 1]
edges = [tuple(map(int, e.split(' ')) + [1]) for e in edges]
graph = nx.Graph()
graph.add_node(10000)

graph.add_weighted_edges_from(edges)
print('Graph Nodes = %d' % graph.number_of_nodes())
print('Graph Edges = %d' % graph.number_of_edges())

recv_data = ''
player_pos = start
softmax_weight = 1.0

while '$' not in recv_data:
    recv_data = sock.recv(1024)
    if '$' in recv_data:
        break

    player_pos = int(recv_data)
    print('Player Position = %d' % player_pos)

    nbrs = graph.neighbors(end)
    print('Neighbors of target = %r' % nbrs)
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
    print('Neighbour Weights = %s' % str(nbr_weights))
    nbr_weights = softmax(nbr_weights, softmax_weight)
    print('Annealed Weights = %s' % str(nbr_weights))
    print('Chosen Neighbour = %d' % chosen_nbr)
    print('Doubling Edge (%d %d)' % (chosen_nbr, end))

    sock.sendall('%d %d\n' % (chosen_nbr, end))
    softmax_weight += 1.0

sock.close()
