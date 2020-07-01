# control function

import numpy as np
from network import com_net
from pdb import set_trace as bp

def freq(id_ctrl, signals):
    gen_id = int(id_ctrl.replace('freq_ctrl', ''))
    
    # primary ctrl
    freq_error = signals['omega_ref'] - signals['omega']

    #signals['S'] = signals['Pm_droop']

    signals['Pm_droop'] = signals['D']*freq_error


    # secondary control
    n_gen = signals['gen'].shape[0]

    #gamma = 1.0

    Omega = np.zeros(n_gen)
    for i in range(n_gen):
        Omega[i] = signals['Omega_'+str(i)] 

    d_ij = np.ones(n_gen)
    for j in range(n_gen):
        d_ij[j] = Omega[gen_id] - Omega[j]

    w = np.zeros(n_gen)
    for j in range(n_gen):
        w[j] = com_net[gen_id, j] * d_ij[j]

    signals['Omega_dot'] = freq_error * signals['Alpha'] - sum(w)

    return signals





def volt(id_ctrl, signals):
    gen_id = int(id_ctrl.replace('sec_volt_ctrl', ''))
    
    # primary ctrl
    signals['Vt_error'] = signals['Vt_ref'] - signals['Vt']
    signals['Q_error'] = signals['Q_ref'] - signals['Q']

    signals['Q_droop'] = signals['D']*signals['Q_error']

    # secondary control
    n_gen = signals['gen'].shape[0]

    gamma = 0.0

    Q = np.zeros(n_gen)
    for i in range(n_gen):
        Q[i] = signals['Q'+str(i)] 

    d_ij = np.ones(n_gen)
    for j in range(n_gen):
        d_ij[j] = Q[gen_id] - Q[j]

    w = np.zeros(n_gen)
    for j in range(n_gen):
        w[j] = com_net[gen_id, j] * d_ij[j] * gamma

    signals['e_dot'] = signals['beta']*signals['Vt_error'] - sum(w)

    signals['E_i'] = signals['Vt_ref'] + signals['Q_droop'] + signals['e']

    return signals

