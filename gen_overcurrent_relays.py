#!/bin/python3


################################################
# file to generate the frequency controllers

import sys
import numpy as np
from pypower.loadcase import loadcase
from parameters import case, H, current_tol, delay_open, delay_close



# load power system and extract information
ppc = loadcase('./grid_models/'+case)

n = ppc['branch'].shape[0]




if len(sys.argv) >= 2:
	dest_dir = sys.argv[1]
else:
	dest_dir = '.'


file_name_i = 'relay_branchith.dyn'

inputs = '''

bus = INPUT(bus, sys_matrices)
branch = INPUT(branch, sys_matrices)
Ybus = INPUT(Ybus, sys_matrices)

'''

relay_dyn = '''


call_func = INT_FUNC(relay.overcurrent)

event_off = EVENT(switch_off, DISABLE_BRANCH, b*)
event_on = EVENT(switch_on, ENABLE_BRANCH, b*)

t = INT(k, 1, 1)


'''


initialization = '''
##################
# Initialisation #
##################

INIT
SIGNAL = k = CONST(1.0)

SIGNAL = node_a = CONST(x*)
SIGNAL = node_b = CONST(y*)

SIGNAL = breaker_state = CONST(1)

SIGNAL = I_nom = CONST(1)
SIGNAL = tolerance = CONST(tol*)

SIGNAL = switch_off = CONST(0)
SIGNAL = switch_on = CONST(0)

SIGNAL = t_event = CONST(0)
SIGNAL = delay_open = CONST(t_open)
SIGNAL = delay_reclose = CONST(t_close)

SIGNAL = reclose_attempts = CONST(0)

SIGNAL = debug = CONST(0)


'''



for i in range(n):
	# check if the branch isn't a trnasformer
	if ppc['branch'][i, 8] == 0:
		
		node_a = ppc['branch'][i, 0]
		node_b = ppc['branch'][i, 1]

		id_label = 'ID = relay_branch' + str(i) + '\n'
	
		dyn = relay_dyn.replace('b*', str(i))

		init = initialization.replace('x*', str(node_a))
		init = init.replace('y*', str(node_b))
		init = init.replace('tol*', str(current_tol))
		init = init.replace('t_open', str(delay_open))
		init = init.replace('t_close', str(delay_close))

		file_name = dest_dir + '/' + file_name_i.replace('ith', str(i))

		with open(file_name, 'w') as f:
			f.write(id_label)
			f.write(inputs)
			f.write(dyn)
			f.write(init)




