#!/bin/python3


################################################
# file to generate the frequency controllers

import sys
import numpy as np
from pypower.loadcase import loadcase
from parameters import case, H


# load power system and extract information
ppc = loadcase('./grid_models/'+case)

n = ppc['bus'].shape[0]
n_gen = ppc['gen'].shape[0]

node_id = [str(int(x-1)) for x in ppc['bus'][:, 0]]
gen_id = [str(int(x-1)) for x in ppc['gen'][:, 0]]



#print(sys.argv)

if len(sys.argv) >= 2:
	dest_dir = sys.argv[1]
else:
	dest_dir = '.'

#alpha = [.12 for x in H]
alpha = [1.0 for x in H]
k_consensus = [1/.16 for x in H]
d_droop = [.05 for x in H]


file_name_i = 'freq_ctrlith.dyn'

header = '''
##########################
# define the signals


'''

signals_ctrl_gen = '''

Pm_ref = REF()
omega_ref = REF()

# used for initialization
Pm0 = INPUT(Pm,GENx)

Pm_droop = REF()
Omega = REF()
'''

ctrl_dyn = '''

call_func = INT_FUNC(update_ctrl.freq)
Omega_nom = INT(Omega_dot, K, 1)
Omega = MULT(Omega_nom, 1)
u = SUM(Pm_droop, Omega)
Pm_tot = SUM(Pm_ref, u) 
Pm = OUTPUT(Pm_tot, GENx)

'''


initialization = '''
##################
# Initialisation #
##################

INIT
SIGNAL = D = CONST(d_droop)
SIGNAL = Alpha = CONST(alpha)
SIGNAL = K = CONST(k_consensus)

SIGNAL = Pm_ref = MULT(Pm0, 1)
SIGNAL = omega_ref = CONST(1.0)

'''




input_ctrl = '''

# frequency in the generator
gen = INPUT(gen, sys_matrices)
omega = INPUT(omega,GENx)
omega_error = SUM(omega_ref, -omega)

# Control variables

'''

for i in range(n_gen):
    input_ctrl += "Omega_x = INPUT(Omega, freq_ctrlx)\n".replace('x', str(i))



for i in range(n_gen):
	id_label = 'ID = freq_ctrl' + str(i) + '\n'

	input_ctrl_i = input_ctrl.replace('x', str(i))

	
	init = initialization.replace('d_droop', str(d_droop[i]))
	init = init.replace('alpha', str(alpha[i]))
	init = init.replace('k_consensus', str(k_consensus[i]))

	sec_ctrl_i = signals_ctrl_gen.replace('x', str(i)) + input_ctrl_i + ctrl_dyn.replace('GENx', 'GEN'+str(i))
	file_name = dest_dir + '/' + file_name_i.replace('ith', str(i))
	#print(dest_dir)
	#print(file_name)
	with open(file_name, 'w') as f:
		f.write(id_label)
		f.write(header)
		f.write(sec_ctrl_i)

		f.write(init)




