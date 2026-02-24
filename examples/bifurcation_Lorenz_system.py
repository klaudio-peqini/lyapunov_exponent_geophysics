#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 00:25:08 2023

@author: klaudio
"""

import numpy as np
import matplotlib.pyplot as plt


def lorenz_system(x, y, z, r, b=10, s=6):
    x_dot = b * (y - x)
    y_dot = r * x - y - x * z
    z_dot = x * y - s * z
    return x_dot, y_dot, z_dot


dr = 0.1  # parameter step size
r = np.arange(40, 200, dr)  # parameter range
dt = 0.001  # time step
t = np.arange(0, 10, dt)  # time range

# initialize solution arrays
xs = np.empty(len(t) + 1)
ys = np.empty(len(t) + 1)
zs = np.empty(len(t) + 1)

# initial values x0,y0,z0 for the system
xs[0], ys[0], zs[0] = (1, 1, 1)


# Save the plot points coordinates and plot the with a single call to plt.plot
# instead of plotting them one at a time, as it's much more efficient
r_maxes = []
z_maxes = []
r_mins = []
z_mins = []


for R in r:
    # Print something to show everything is running
    # print(f"{R=:.2f}")
    for i in range(len(t)):
        # approximate numerical solutions to system
        x_dot, y_dot, z_dot = lorenz_system(xs[i], ys[i], zs[i], R)
        xs[i + 1] = xs[i] + (x_dot * dt)
        ys[i + 1] = ys[i] + (y_dot * dt)
        zs[i + 1] = zs[i] + (z_dot * dt)
    # calculate and save the peak values of the z solution
    for i in range(1, len(zs) - 1):
        # save the local maxima
        if zs[i - 1] < zs[i] and zs[i] > zs[i + 1]:
            r_maxes.append(R)
            z_maxes.append(zs[i])
        # save the local minima
        elif zs[i - 1] > zs[i] and zs[i] < zs[i + 1]:
            r_mins.append(R)
            z_mins.append(zs[i])

    # "use final values from one run as initial conditions for the next to stay near the attractor"
    xs[0], ys[0], zs[0] = xs[i], ys[i], zs[i]


plt.scatter(r_maxes, z_maxes, color="black", s=0.5, alpha=0.2)
plt.scatter(r_mins, z_mins, color="red", s=0.5, alpha=0.2)

plt.xlim(0, 200)
plt.ylim(0, 400)
plt.show()


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

import numpy as np
from scipy.integrate import solve_ivp

# ODE system
def func(t, v, sigma, r, b):
    x, y, z = v
    return [ sigma * (y - x), r * x - y - x * z, x * y - b * z ]

# Jacobian matrix
def JM(t, v, sigma, r, b):
    x, y, z = v
    return np.array([[-sigma, sigma, 0], [r - z, -1, -x], [y, x, -b]])

# parameters
sigma = 10
r = 28
b = 8/3

# dimension of the system (to keep things general)
n = 3

# number of Lyapunov exponents
n_lyap = 3

# (dis)assemble state and tangent vectors (or their derivatives)
# into one vector for integrator:
assemble = lambda v,U: np.hstack((v,U.flatten()))
disassemble = lambda state: (state[:n], state[n:].reshape(n,n_lyap))

def func_with_lyaps(t, state, *pars):
    v, U = disassemble(state)
    dv = func(t, v, *pars)
    dU = JM(t, v, *pars) @ U
    return assemble(dv, dU)

# initial states:
v = np.random.random(n)
U = np.random.random((n_lyap,n))

lyaps = [] # local Lyapunov exponents

dt = 1
iters = 1000

for _ in range(iters):
    sol = solve_ivp(
            func_with_lyaps,
            [0, dt],
            assemble(v,U),
            t_eval=[dt],
            args=(sigma, r, b),
            max_step=dt,
        )
    v,U = disassemble(sol.y.flatten())
    U,R = np.linalg.qr(U)
    lyaps.append(np.log(abs(R.diagonal()))/dt)

transient_steps = 100
# result:
print(*np.average(lyaps[transient_steps:],axis=0))


###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################

import scipy.integrate as sc

def diff_Lorenz(u):
    x,y,z = u
    f = [sigma * (y - x), r * x - y - x * z, x * y - b * z]
    Df = [[-sigma, sigma, 0], [r - z, -1, -x], [y, x, -b]]
    return np.array(f), np.array(Df)

def LEC_system(u):
    #x,y,z = u[:3]             # n=3
    U = u[3:12].reshape([3,3]) # size n square matrix, sub-array from n to n+n*n=n*(n+1)
    L = u[12:15]               # vector, sub-array from n*(n+1) to n*(n+1)+n=n*(n+2)
    f,Df = diff_Lorenz(u[:3])
    A = U.T.dot(Df.dot(U))
    dL = np.diag(A).copy();
    for i in range(3):
        A[i,i] = 0
        for j in range(i+1,3): A[i,j] = -A[j,i]
    dU = U.dot(A)
    return np.concatenate([f,dU.flatten(),dL])

u0 = np.ones(3)
U0 = np.identity(3)
L0 = np.zeros(3)
u0 = np.concatenate([u0, U0.flatten(), L0])
t = np.linspace(0,200,501)
u = sc.odeint(lambda u,t:LEC_system(u),u0,t, hmax=0.05)
L = u[5:,12:15].T/t[5:]

plt.figure()
plt.plot(t[5:],L.T)

