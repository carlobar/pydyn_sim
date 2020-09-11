import numpy as np
import matplotlib.pyplot as plt
from pypower.loadcase import loadcase
from pypower.idx_bus import BUS_I, BUS_TYPE, PD, QD, GS, BS, BUS_AREA, \
    VM, VA, BASE_KV, ZONE, VMAX, VMIN

from parameters import case, H

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



# load power system and extract information
ppc = loadcase('../grid_models/' + case)

n = ppc['bus'].shape[0]
n_gen = ppc['gen'].shape[0]

node_id = [str(int(x-1)) for x in ppc['bus'][:, 0]]
gen_id = [str(int(x-1)) for x in ppc['gen'][:, 0]]

att = 'scale'
#att = 'bias'

freq_error = []
consensus_error = []

for i in range(0, 6):
    #folder = '../results_droop/case_8/'
    #folder = '../simulations/'
    folder = '../resiliency_'+att+'_att/case_'+ str(i) +'/'

    results = np.load(folder + 'results.npy', allow_pickle=True).item()

    t = np.array(results['t_axis'])

    n = 10

    P = []
    Q = []

    omega = []
    E = []
    Vang = []

    Vfd = []
    Pm = []

    omega_error = []
    w = []

    P_droop = []
    Omega = []
    u = []

    Q_droop = []
    E_i = []
    e = []
    Q_error = []
    Vt_error = []
    Q0 = []
    V_error = []
    Vt = []


    u_p = []
    u_i = []
    u_i_b = []

    for i in range(n):
	    omega.append( np.array(results['GEN'+str(i)+':omega']) )
	    E.append( np.array(results['GEN'+str(i)+':Vt']) )
	    #Vang.append( np.array(results['GEN'+str(i)+':Vang']) )
	    #Pm.append( np.array(results['GEN'+str(i)+':Pm']) )

	    P.append( np.array(results['GEN'+str(i)+':P']) )
	    Pm.append( np.array(results['GEN'+str(i)+':Pm']) )
	    #Q.append( np.array(results['GEN'+str(i)+':Q']) )

	    #Vfd.append( np.array(results['GEN'+str(i)+':Vfd']) )

	    omega_error.append( np.array(results['omega_error'+str(i)]) )
	    #w.append( np.array(results['w'+str(i)]) )


	    P_droop.append( np.array(results['Pm_droop'+str(i)]) )
	    Omega.append( np.array(results['Omega_local'+str(i)]) )
	    u.append( np.array(results['u'+str(i)]) )



    omega_avg = np.zeros( len(omega[0]) )
    for i in range(n):
        omega_avg += omega[i]*H[i]/sum(H)

    freq_error.append( np.square(omega_avg*60-60).mean() )

    def integrate(x, t):
        h = t[1]-t[0]
        T = len(t)
        total = np.zeros(T)
        for t in range(1, T):
            total[t] = total[t-1] + (x[t] + x[t-1])*h/2
        return total


    u = []
    for i in range(n):
        u.append(integrate(omega_error[i], t))
        

    u_avg = u[0]
    for i in range(1, len(u) ):
        u_avg += u[i]
    u_avg *= 1/len(u)

    # average error of the consensus variables
    #error_consensus = sum(Omega)/len(Omega) - u_avg 

    consensus_error.append( np.square( sum(Omega)/len(Omega) - u_avg ).mean() )




plt.figure(1)
plt.clf()
plt.plot(range(0, 6), freq_error, '-o', label='$\Delta \omega$')
#plt.ylim([59.8, 60.2])
plt.xlabel('F')
plt.ylabel('Freq error [Hz]')
plt.legend()
plt.show()

plt.savefig('./images/freq_impact_'+att+'.pgf', bbox_inches='tight')



plt.figure(2)
plt.clf()
plt.plot(range(0,6), consensus_error, '-o', label='$\Delta \Omega$')
#plt.ylim([59.8, 60.2])
plt.xlabel('F')
plt.ylabel('Consensus error ')
plt.legend()
plt.show()

plt.savefig('./images/Omega_impact_'+att+'.pgf', bbox_inches='tight')






'''
plt.figure(1)
plt.clf()
plt.plot(t, omega_avg*60, label='$\omega$')
#plt.ylim([59.8, 60.2])
plt.xlabel('Time (s)')
plt.ylabel('Freq [Hz]')
plt.legend()
plt.show()
'''

'''
plt.figure(2)
plt.clf()
for i in range(n):
	plt.plot(t, P[i], label='$P_'+str(i)+'$')
plt.xlabel('Time (s)')
plt.ylabel('Active power in generators (P) MW')
plt.legend()
plt.show()


plt.figure(3)
plt.clf()
for i in range(n):
	plt.plot(t, P_droop[i], label='$P_'+str(i)+'^d$')
#plt.ylim([59.8, 60.2])
plt.xlabel('Time (s)')
plt.ylabel('Droop ctrl')
plt.legend()
plt.show()
'''


'''
plt.figure(4)
plt.clf()
for i in range(n):
	plt.plot(t, Omega[i], label='$\Omega_'+str(i)+'$')
#plt.ylim([59.8, 60.2])
plt.xlabel('Time (s)')
plt.ylabel('Secondary ctrl')
plt.legend()
plt.show()


plt.figure(5)
plt.clf()
for i in range(n):
	plt.plot(t, u[i], label='$u_'+str(i)+'$')
#plt.ylim([59.8, 60.2])
plt.xlabel('Time (s)')
plt.ylabel('Generator ctrl signal')
plt.legend()
plt.show()
'''


'''
plt.figure(6)
plt.clf()
for i in range(n):
	plt.plot(t, E[i], label='$E_'+str(i)+'$')
#plt.ylim([59.8, 60.2])
plt.xlabel('Time (s)')
plt.ylabel('E_i')
plt.legend()
plt.show()
'''






'''

plt.figure(7)
plt.clf()
for i in range(n):
	plt.plot(t, u[i], label='$\int \Delta \omega_'+str(i)+'$')
#plt.ylim([59.8, 60.2])
plt.xlabel('Time (s)')
plt.ylabel('')
plt.legend()
plt.show()



plt.figure(8)
plt.clf()
#plt.plot(t, total/.16, label='$u_{avg}$')
plt.plot(t, u_avg, label='$u_{avg}$')
#plt.ylim([59.8, 60.2])
plt.xlabel('Time (s)')
plt.ylabel('energy Droop ctrl')
plt.legend()
plt.show()




plt.figure(9)
plt.clf()
plt.plot(t, error_consensus, label='error consensus')
#plt.ylim([59.8, 60.2])
plt.xlabel('Time (s)')
plt.ylabel('')
plt.legend()
plt.show()
'''




'''
# sync element
sync1_2 = np.array( results['SYNC1:sync'] )
sync_Vm_error = np.array( results['SYNC1:Vm_error'] )
sync_Vang_error = np.array( results['SYNC1:Vang_error'] )
sync_omega_error = np.array( results['SYNC1:omega_error'] )
'''




'''
plt.figure(12)
plt.clf()
plt.plot(t, sync_Vm_error, '-')
plt.xlabel('Time (s)')
plt.ylabel('sync Vm_error')
plt.show()   

plt.figure(13)
plt.clf()
plt.plot(t, sync_Vang_error*180/np.pi, '-')
plt.xlabel('Time (s)')
plt.ylabel('sync Vang_error')
plt.show()   

'''

