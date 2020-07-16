# relay function

import numpy as np
import cmath

from network import com_net
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


# np.degrees(cmath.phase(Va))


def get_volt(node, bus):
    Vm = bus[node, VM]
    Va = bus[node, VA]
    V = Vm * np.exp(1j * Va)
    return V

def overcurrent(id_element, signals):
    branch_id = int(id_element.replace('relay_branch', ''))

    # calculate the current on the branch
    node_a = int(signals['branch'][branch_id, 0])-1
    node_b = int(signals['branch'][branch_id, 1])-1

    Va = get_volt(node_a, signals['bus'])
    Vb = get_volt(node_b, signals['bus'])
    Yab = signals['Ybus'][node_a, node_b]

    Iab = (Va - Vb) * Yab

    if signals['t'] < 0.1:
        signals['I_nom'] = abs(Iab)
        signals['t_event'] = -1
        #if branch_id == 43:
        #    bp()

    I_max = signals['I_nom'] * (1 + signals['tolerance'])

    breaker_state = int(signals['branch'][branch_id, 10])

    switch_on = 0
    switch_off = 0
    
    if (abs(Iab) > I_max) and (breaker_state == 1):
        if signals['t_event'] <= 0:
            signals['t_event'] = signals['t']
        elif signals['t'] - signals['t_event'] >= signals['delay_open']:
            switch_off = 1
            #signals['t_event'] = -1
            #signals['breaker_state'] = 0
            #print('****loop disable')
            #print('branch = ', branch_id)             
    elif (breaker_state == 0) and (signals['reclose_attempts'] < 0):
        if signals['t_event'] <= 0:
            signals['t_event'] = signals['t']
        elif signals['t'] - signals['t_event'] >= signals['delay_reclose']:
            switch_on = 1
            #signals['t_event'] = -1
            #signals['breaker_state'] = 1
            signals['reclose_attempts'] += 1
            #print('****loop enable')
            #print('branch = ', branch_id, ', attempets: ', signals['reclose_attempts'])
    if signals['breaker_state'] != breaker_state:
        signals['t_event'] = -1

    signals['switch_on'] = switch_on
    signals['switch_off'] = switch_off

    signals['breaker_state'] = breaker_state

    '''
    if branch_id == 3:
        print(signals['debug'])
        signals['debug'] += 1
    '''

    return signals




# Eq * np.exp(1j * delta) / np.complex(0,Xdp)
