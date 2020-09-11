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

for i in range(n_gen):
    G.add_node( gen_id[i] )


# select the type of communication graph between the generators
graph=1

if graph == 0:
    # connected graph
    com_net = np.ones((n_gen, n_gen))

elif graph == 1:
    # simple graph
    com_net = np.zeros((n_gen, n_gen))
    for i in range(n_gen-1):
        j = i+1
        com_net[i, j] = 1
    com_net[0, n_gen-1] = 1
    com_net = com_net + com_net.T




for i in range(n_gen):
    for j in range(n_gen):
        if com_net[i, j] == 1:
            n_from = gen_id[i]
            n_to = gen_id[j]
            G.add_edge( str(n_from), str(n_to) )






plt.figure(19)
plt.clf()
G_i = copy.deepcopy(G)

# define colors
color_nodes = []
for node in G_i:
	node_f = str(int(node))
	color_nodes.append( 'powderblue' )

pos = nx.spectral_layout(G_i)

nx.draw_networkx_nodes(G_i, pos, node_color=color_nodes)
nx.draw_networkx_labels(G_i, pos)
nx.draw_networkx_edges(G_i, pos, arrows = False)

plt.draw()
plt.show()



plt.savefig('./images/comm_net_'+str(graph)+'.pgf', bbox_inches='tight')






G = nx.DiGraph()

for i in range(n_gen):
    G.add_node( gen_id[i] )



graph = 0

if graph == 0:
    # connected graph
    com_net = np.ones((n_gen, n_gen))

elif graph == 1:
    # simple graph
    com_net = np.zeros((n_gen, n_gen))
    for i in range(n_gen-1):
        j = i+1
        com_net[i, j] = 1
    com_net[0, n_gen-1] = 1
    com_net = com_net + com_net.T


for i in range(n_gen):
    for j in range(n_gen):
        if com_net[i, j] == 1:
            n_from = gen_id[i]
            n_to = gen_id[j]
            G.add_edge( str(n_from), str(n_to) )


plt.figure(20)
plt.clf()
G_i = copy.deepcopy(G)

nx.draw_networkx_nodes(G_i, pos, node_color=color_nodes)
nx.draw_networkx_labels(G_i, pos)
nx.draw_networkx_edges(G_i, pos, arrows = False)

plt.draw()
plt.show()

plt.savefig('./images/comm_net_'+str(graph)+'.pgf', bbox_inches='tight')

