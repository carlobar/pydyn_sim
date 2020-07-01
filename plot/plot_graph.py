#!python3

import networkx as nx
import copy
import pylab

from parameters import case

# External modules
from pypower.loadcase import loadcase
import matplotlib.pyplot as plt
import numpy as np
from pdb import set_trace as bp

from pypower.idx_bus import BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, \
    VM, VA, BASE_KV, ZONE, VMAX, VMIN

'''
columns 0-12 must be included in input matrix (in case file)
    0.  C{BUS_I}       bus number (1 to 29997)
    1.  C{BUS_TYPE}    bus type (1 = PQ, 2 = PV, 3 = ref, 4 = isolated)
    2.  C{PD}          real power demand (MW)
    3.  C{QD}          reactive power demand (MVAr)
    4.  C{GS}          shunt conductance (MW at V = 1.0 p.u.)
    5.  C{BS}          shunt susceptance (MVAr at V = 1.0 p.u.)
    6.  C{BUS_AREA}    area number, 1-100
    7.  C{VM}          voltage magnitude (p.u.)
    8.  C{VA}          voltage angle (degrees)
    9.  C{BASE_KV}     base voltage (kV)
    10. C{ZONE}        loss zone (1-999)
    11. C{VMAX}        maximum voltage magnitude (p.u.)
    12. C{VMIN}        minimum voltage magnitude (p.u.)
'''


ppc = loadcase('../grid_models/'+case)




n = ppc['bus'].shape[0]
n_gen = ppc['gen'].shape[0]

node_id = [str(int(x)) for x in ppc['bus'][:, 0]]
gen_id = [str(int(x)) for x in ppc['gen'][:, 0]]
conn_id = []
load_id = []

for i in range(n):
    node = node_id[i]
    if node not in gen_id:
        P, Q = ppc['bus'][i, 2:4]
        if P==Q and P == 0:
            conn_id.append(node)
        else:
            load_id.append(node)

G = nx.DiGraph()

for i in range(n):
    node = node_id[i]
    G.add_node( node )

m = ppc['branch'].shape[0]
for k in range(m):
    n_from = int(ppc['branch'][k, 0])
    n_to = int(ppc['branch'][k, 1])
    status = int(ppc['branch'][k, 10])
    if status == 1:
        G.add_edge( str(n_from), str(n_to) )
        G.add_edge( str(n_to), str(n_from) )






# Get the set of nodes that are connected
def update_frontier(i, frontier, graph):
    #print(i)
    if i not in frontier:
        frontier.add( i )
        neighbors = G.adj[ i ].keys()
        for j in neighbors:
            frontier.update( update_frontier(j, frontier, graph) )
    return frontier






connected_nodes = []
V = set(node_id)
node = node_id[0]
finished = False

while not finished:
    frontier = set()
    frontier = update_frontier(node, frontier, G)
    connected_nodes.append(frontier)
    V.difference_update(frontier)

    if len(V) == 0:
        finished = True
    else:
        node = list(V)[0]


'''
# get the nodes in the same zone
nodes_area = []
areas = set(ppc['bus'][:, BUS_AREA])
for area in areas:
	nodes_area_i = []
	for i in range(n):
		if ppc['bus'][i, BUS_AREA] == area:
			nodes_area_i.append( node_id[i] )
	nodes_area.append( set(nodes_area_i) )

connected_nodes = nodes_area
'''

# number of graphs
m = len(connected_nodes)

for i in range(m):
	plt.figure(i+10)
	plt.clf()
	G_i = copy.deepcopy(G)
	nodes_i = connected_nodes[i]
	for j in node_id:
		if j not in nodes_i:
			G_i.remove_node(j)
	load_i = list(set(load_id).intersection(nodes_i))
	conn_i = list(set(conn_id).intersection(nodes_i))
	gen_i = list(set(gen_id).intersection(nodes_i))


	# define colors
	color_nodes = []
	for node in G_i:
		node_f = str(int(node))
		if node_f in gen_i:
			color_nodes.append( 'powderblue' )
		elif node_f in conn_i:
			color_nodes.append( 'silver' )
		else:
			color_nodes.append( 'yellowgreen' )



	pos = nx.shell_layout(G_i, nlist=[load_i, conn_i, gen_i])
	#pos = nx.spring_layout(G_i)


	nx.draw_networkx_nodes(G_i, pos, node_color=color_nodes)
	nx.draw_networkx_labels(G_i, pos)
	nx.draw_networkx_edges(G_i, pos, arrows = False)

	plt.draw()
	plt.show()


# get the communication network
com_net = np.zeros((n_gen, n_gen))
n_subnets = len(connected_nodes)

map_id_pos = dict()
for i in range(n_gen):
	map_id_pos[ gen_id[i] ] = i

for k in range(n_subnets):
	nodes_k = connected_nodes[k]
	gen_k = list(set(gen_id).intersection(nodes_k))
	for i in gen_k:
		pos_i = map_id_pos[i]
		for j in gen_k:
			pos_j = map_id_pos[j]
			com_net[pos_i, pos_j] = 1


#plt.savefig('graph_case39.pgf', bbox_inches='tight')




