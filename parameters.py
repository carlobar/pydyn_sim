
import numpy as np


#case = './grid_models/case39.py'
case = 'case39.py'

# number of generators
n_gen = 10

# inertia generators
#H = np.ones(n_gen)*10
H = np.array([500, 30.30, 35.80, 38.60, 26.00, 34.80, 26.40, 24.30, 34.50, 42.0])

t_sim = 20

# to do: Add other parameters of the simulations



current_tol = 0.5
delay_open = .1
delay_close = .1
