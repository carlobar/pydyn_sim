#!python3
#
# Copyright (C) 2014-2015 Julius Susanto. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

# Dynamic model classes
from pydyn.controller import controller
from pydyn.sym_order6a import sym_order6a
from pydyn.sym_order6b import sym_order6b
from pydyn.sym_order4 import sym_order4
from pydyn.ext_grid import ext_grid

# Simulation modules
from pydyn.events import events
from pydyn.recorder import recorder
from pydyn.run_sim import run_sim

# External modules
from pypower.runpf import runpf
from pypower.loadcase import loadcase
import matplotlib.pyplot as plt
import numpy as np
from pdb import set_trace as bp
    
from timeit import default_timer as timer

from parameters import case, t_sim, H



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



if __name__ == '__main__':
    

    # Load PYPOWER case
    ppc = loadcase('../grid_models/'+case)
    
    n = ppc['bus'].shape[0]
    n_gen = ppc['gen'].shape[0]
    n_branch = ppc['branch'].shape[0]


    # define other swing buses
    ppc['bus'][29, BUS_TYPE] = 3
    ppc['bus'][32, BUS_TYPE] = 3

    '''
    # remove losses in the grid's connection
    ppc['branch'][7, 2] = 0.0001
    ppc['branch'][7, 3] = 0.0
    ppc['branch'][7, 4] = 0.0
    '''

    '''
    list_branches = [2, 5, 8]
    for x in list_branches:
        ppc['branch'][x-1, 10] = 0
    
    for x in range(3):
        ppc['bus'][x, 1] = 3
    '''
    
    #bp()
    # Program options
    dynopt = {}
    dynopt['h'] = 0.001                # step length (s)
    dynopt['sample_period'] = 0.01
    dynopt['t_sim'] = t_sim           # simulation time (s)
    dynopt['max_err'] = 1e-8         # Maximum error in network iteration (voltage mismatches)
    dynopt['max_iter'] = 60           # Maximum number of network iterations
    dynopt['verbose'] = False         # option for verbose messages
    dynopt['fn'] = 60                 # Nominal system frequency (Hz)
    dynopt['speed_volt'] = True       # Speed-voltage term option (for current injection calculation)
    
    # Integrator option
    #dynopt['iopt'] = 'mod_euler'
    dynopt['iopt'] = 'runge_kutta'

    # Create dictionary of elements
    elements = {}
    
    


    for i in range(n_gen):
        #G_i = sym_order6b('Generator'+ str(i) +'.mach', dynopt)
        G_i = ext_grid('GEN'+str(i), i, 0.1198, H[i], dynopt)
        elements[G_i.id] = G_i
        
        #Ctrl_i = controller('volt_ctrl'+ str(i) +'.dyn', dynopt)
        #elements[Ctrl_i.id] = Ctrl_i

        #sec_ctrl_i = controller('sec_volt_ctrl'+ str(i) +'.dyn', dynopt)
        #elements[sec_ctrl_i.id] = sec_ctrl_i
        
        
        freq_ctrl_i = controller('freq_ctrl'+ str(i) +'.dyn', dynopt)
        elements[freq_ctrl_i.id] = freq_ctrl_i


    # install protection relays
    '''
    for i in range(n_branch):
        if ppc['branch'][i, 8] == 0:
            overcurrent_relay_i = controller('relay_branch'+ str(i) +'.dyn', dynopt)
            elements[overcurrent_relay_i.id] = overcurrent_relay_i
    '''



    #i=0    
    #Ctrl_i = controller('ctrl'+ str(i) +'.dyn', dynopt)
    #elements[Ctrl_i.id] = Ctrl_i

    
    sync1 = controller('sync.dyn', dynopt)
    elements[sync1.id] = sync1
    
    
    # Create event stack
    oEvents = events('events.evnt')
    
    # Create recorder object
    oRecord = recorder('recorder.rcd')
    
    
    
    
    
    # Run simulation
    start = timer()
    #try:
    oRecord = run_sim(ppc,elements,dynopt,oEvents,oRecord)
    #except:
    #   bp()
    #   oRecord = run_sim(ppc,elements,dynopt,oEvents,oRecord)

    oRecord.results['t_axis'] = oRecord.t_axis
    np.save('results.npy', oRecord.results)
    end = timer()
    print('\n \n')
    print('==============================================')
    print('Total time: ' + str(end-start))
    print('==============================================')
    print('\n \n')
    
