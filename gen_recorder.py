#!/bin/python3

# create the recorder for the simulations


import sys
import numpy as np
from pypower.loadcase import loadcase
from parameters import case, n_gen

# example output
#AVR3:Vdf, AVR3, Vfd, STATE

def record(element, var, type='SIGNAL', name=None):
    rec_name = ''
    if name == None:
        rec_name = element + ':' + var
    else:
        rec_name = name

    return ','.join([rec_name, element, var, type])+'\n'



if len(sys.argv) >= 2:
	file_name = sys.argv[1]
else:
	file_name = 'recorder.rcd'

'''
# load power system and extract information
ppc = loadcase(case)

n = ppc['bus'].shape[0]
n_gen = ppc['gen'].shape[0]

node_id = [str(int(x-1)) for x in ppc['bus'][:, 0]]
gen_id = [str(int(x-1)) for x in ppc['gen'][:, 0]]
'''

records = ''
for i in range(n_gen):
    element = 'GEN'+str(i)
    records += record( element, 'omega', 'STATE' )
    records += record( element, 'Vt' )
    records += record( element, 'delta' )
    records += record( element, 'P' )
    records += record( element, 'Pm' )
    #records += record( element, 'Q' )
    #records += record( element, 'Vfd' )
    records += '\n'


vars = ['Pm_droop', 'u', 'Omega', 'omega_error']
for i in range(n_gen):
    element = 'freq_ctrl'+str(i)
    for var in vars:
        name = var+str(i)
        records += record( element, var, 'SIGNAL', name)
    records += '\n'

'''
vars = ['Q_droop', 'e', 'E_i', 'Q_error', 'Vt_error', 'Q_ref']
for i in range(n_gen):
    element = 'sec_volt_ctrl'+str(i)
    for var in vars:
        name = var+str(i)
        records += record( element, var, 'SIGNAL', name)
    records += '\n'



vars = ['V_error', 'Vt']#, 'u_p', 'u_i']
for i in range(n_gen):
    #element = 'AVR'+str(i)
    element = 'sec_volt_ctrl'+str(i)
    for var in vars:
        name = var+str(i)
        records += record( element, var, 'SIGNAL', name)
    records += '\n'
'''


vars = ['P', 'Q', 'Vm', 'Va']
nodes = [19, 33]
element = 'bus'
for i in nodes:
    for var in vars:
        name = var + str(i)
        records += record( element, name, 'SIGNAL', name)
    records += '\n'


with open(file_name, 'w') as f:
    f.write(records)

